from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user, require_role
from database import get_session
from models import PAYMENT_STATUSES, Order, Payment, User
from pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, apply_pagination
from schemas import PaymentCreate, PaymentRead, PaymentStatusUpdate
from services.memberships import award_order_membership_points
from services.payments import validate_payment, validate_payment_status_update


router = APIRouter()


def validate_payment_status_filter(status_filter: str | None) -> None:
    if status_filter is not None and status_filter not in PAYMENT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid payment status filter")


@router.get("/payments", response_model=list[PaymentRead])
def list_payments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    status: str | None = None,
    order_id: int | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
):
    require_role(current_user, ["admin", "cashier"])
    validate_payment_status_filter(status)
    if order_id is not None and order_id < 1:
        raise HTTPException(status_code=400, detail="order_id must be greater than 0")

    query = session.query(Payment)
    if status:
        query = query.filter(Payment.status == status)
    if order_id is not None:
        query = query.filter(Payment.order_id == order_id)
    return apply_pagination(query.order_by(Payment.created_at.desc()), limit, offset).all()


@router.post("/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    data: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order = session.get(Order, data.order_id)
    validate_payment(data, order, current_user, session)
    payment = Payment(**data.model_dump())
    session.add(payment)
    session.flush()
    if payment.status == "paid":
        award_order_membership_points(order, session)
    session.commit()
    session.refresh(payment)
    return payment


@router.put("/payments/{payment_id}/status", response_model=PaymentRead)
def update_payment_status(
    payment_id: int,
    data: PaymentStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    payment = session.get(Payment, payment_id)
    order = session.get(Order, payment.order_id) if payment else None
    validate_payment_status_update(payment, order, data, current_user, session)
    payment.status = data.status
    session.add(payment)
    if payment.status == "paid":
        award_order_membership_points(order, session)
    session.commit()
    session.refresh(payment)
    return payment
