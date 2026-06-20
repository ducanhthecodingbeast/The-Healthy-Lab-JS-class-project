from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from auth import get_current_user, require_role
from database import get_session
from models import QUEUE_STATUSES, RESERVATION_STATUSES, QueueEntry, Reservation, RestaurantTable, User
from pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, apply_pagination
from schemas import (
    QueueEntryCreate,
    QueueEntryRead,
    QueueStatusUpdate,
    ReservationCreate,
    ReservationRead,
    ReservationStatusUpdate,
    RestaurantTableCreate,
    RestaurantTableRead,
)
from services.reservations import find_table_for_reservation


router = APIRouter()


def validate_reservation_status_filter(status_filter: str | None) -> None:
    if status_filter is not None and status_filter not in RESERVATION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid reservation status filter")


def validate_queue_status_filter(status_filter: str | None) -> None:
    if status_filter is not None and status_filter not in QUEUE_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid queue status filter")


QUEUE_STATUS_TRANSITIONS = {
    "waiting": ["called", "cancelled"],
    "called": ["seated", "cancelled"],
    "seated": [],
    "cancelled": [],
}

RESERVATION_STATUS_TRANSITIONS = {
    "booked": ["seated", "cancelled", "completed"],
    "seated": ["completed", "cancelled"],
    "completed": [],
    "cancelled": [],
}


def ensure_queue_transition(current_status: str, next_status: str) -> None:
    if next_status not in QUEUE_STATUS_TRANSITIONS.get(current_status, []):
        raise HTTPException(status_code=400, detail="Invalid queue status flow")


def ensure_reservation_transition(current_status: str, next_status: str) -> None:
    if next_status not in RESERVATION_STATUS_TRANSITIONS.get(current_status, []):
        raise HTTPException(status_code=400, detail="Invalid reservation status flow")


@router.get("/tables", response_model=list[RestaurantTableRead])
def list_tables(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "cashier", "staff"])
    return session.query(RestaurantTable).order_by(RestaurantTable.capacity, RestaurantTable.name).all()


@router.post("/tables", response_model=RestaurantTableRead, status_code=status.HTTP_201_CREATED)
def create_table(
    data: RestaurantTableCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    table = RestaurantTable(**data.model_dump())
    session.add(table)
    session.commit()
    session.refresh(table)
    return table


@router.get("/reservations", response_model=list[ReservationRead])
def list_reservations(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    status: str | None = None,
    from_time: Annotated[datetime | None, Query(alias="from")] = None,
    to_time: Annotated[datetime | None, Query(alias="to")] = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
):
    validate_reservation_status_filter(status)
    if from_time and to_time and from_time > to_time:
        raise HTTPException(status_code=400, detail="from must be before or equal to to")

    query = session.query(Reservation)
    if current_user.role not in ["admin", "cashier", "staff"]:
        query = query.filter(Reservation.user_id == current_user.id)
    if status:
        query = query.filter(Reservation.status == status)
    if from_time:
        query = query.filter(Reservation.reservation_time >= from_time)
    if to_time:
        query = query.filter(Reservation.reservation_time <= to_time)
    return apply_pagination(query.order_by(Reservation.reservation_time.desc()), limit, offset).all()


@router.post("/reservations", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "cashier", "staff"] and data.status != "booked":
        raise HTTPException(status_code=403, detail="Customers can only create booked reservations")
    if data.status not in RESERVATION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid reservation status")

    table = find_table_for_reservation(data, session)
    reservation = Reservation(
        user_id=current_user.id,
        table_id=table.id,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        party_size=data.party_size,
        reservation_time=data.reservation_time,
        status=data.status,
        note=data.note,
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.put("/reservations/{reservation_id}/status", response_model=ReservationRead)
def update_reservation_status(
    reservation_id: int,
    data: ReservationStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if data.status not in RESERVATION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid reservation status")
    if current_user.role not in ["admin", "cashier", "staff"] and reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own reservation")
    if current_user.role == "customer" and data.status != "cancelled":
        raise HTTPException(status_code=403, detail="Customers can only cancel reservations")
    ensure_reservation_transition(reservation.status, data.status)
    reservation.status = data.status
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.post("/reservations/{reservation_id}/complete", response_model=ReservationRead)
def complete_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "cashier", "staff"])
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    ensure_reservation_transition(reservation.status, "completed")
    reservation.status = "completed"
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.get("/queue", response_model=list[QueueEntryRead])
def list_queue_entries(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    status: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
):
    validate_queue_status_filter(status)
    query = session.query(QueueEntry)
    if current_user.role not in ["admin", "cashier", "staff"]:
        query = query.filter(QueueEntry.user_id == current_user.id)
    if status:
        query = query.filter(QueueEntry.status == status)
    return apply_pagination(query.order_by(QueueEntry.created_at.desc()), limit, offset).all()


@router.post("/queue", response_model=QueueEntryRead, status_code=status.HTTP_201_CREATED)
def create_queue_entry(
    data: QueueEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "cashier", "staff"] and data.status != "waiting":
        raise HTTPException(status_code=403, detail="Customers can only join the waiting queue")
    if data.status not in QUEUE_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid queue status")
    open_entry = (
        session.query(QueueEntry)
        .filter(QueueEntry.user_id == current_user.id, QueueEntry.status.in_(["waiting", "called"]))
        .first()
    )
    if open_entry and current_user.role == "customer":
        raise HTTPException(status_code=400, detail="You already have an active queue entry")
    entry = QueueEntry(user_id=current_user.id, **data.model_dump())
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.post("/queue/next/call", response_model=QueueEntryRead)
def call_next_queue_entry(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "cashier", "staff"])
    entry = (
        session.query(QueueEntry)
        .filter(QueueEntry.status == "waiting")
        .order_by(QueueEntry.created_at.asc(), QueueEntry.id.asc())
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="No waiting queue entries")
    ensure_queue_transition(entry.status, "called")
    entry.status = "called"
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.post("/queue/{entry_id}/seat", response_model=QueueEntryRead)
def seat_queue_entry(
    entry_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "cashier", "staff"])
    entry = session.get(QueueEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    ensure_queue_transition(entry.status, "seated")
    entry.status = "seated"
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/queue/{entry_id}/status", response_model=QueueEntryRead)
def update_queue_status(
    entry_id: int,
    data: QueueStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "cashier", "staff"])
    entry = session.get(QueueEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    ensure_queue_transition(entry.status, data.status)
    entry.status = data.status
    if data.wait_minutes is not None:
        entry.wait_minutes = data.wait_minutes
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry
