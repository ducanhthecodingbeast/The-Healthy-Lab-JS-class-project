from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Reservation, RestaurantTable
from schemas import ReservationCreate


def find_table_for_reservation(data: ReservationCreate, session: Session) -> RestaurantTable:
    start = data.reservation_time - timedelta(minutes=90)
    end = data.reservation_time + timedelta(minutes=90)

    if data.table_id:
        table = session.get(RestaurantTable, data.table_id)
        tables = [table] if table else []
    else:
        tables = (
            session.query(RestaurantTable)
            .filter(RestaurantTable.capacity >= data.party_size, RestaurantTable.status == "available")
            .order_by(RestaurantTable.capacity)
            .all()
        )

    for table in tables:
        if not table or table.capacity < data.party_size:
            continue
        conflict = (
            session.query(Reservation)
            .filter(
                Reservation.table_id == table.id,
                Reservation.status.in_(["booked", "seated"]),
                Reservation.reservation_time >= start,
                Reservation.reservation_time <= end,
            )
            .first()
        )
        if not conflict:
            return table

    raise HTTPException(status_code=400, detail="No available table for that party size and time")
