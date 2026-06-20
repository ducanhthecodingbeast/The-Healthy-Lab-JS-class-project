from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import PAYMENT_STATUSES, Order, Payment, User
from schemas import PaymentCreate, PaymentStatusUpdate
from services.orders import prices_match


PAYMENT_RECONCILE_ROLES = {"admin", "cashier"}


def validate_payment(data: PaymentCreate, order: Order | None, current_user: User, session: Session | None = None) -> Order:
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot create payment for a cancelled order")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")
    if data.status not in PAYMENT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid payment status")
    if current_user.role == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only pay your own orders")
    if current_user.role not in ["customer", "admin", "cashier"]:
        raise HTTPException(status_code=403, detail="This role cannot create payments")
    if current_user.role not in PAYMENT_RECONCILE_ROLES:
        if data.status != "pending":
            raise HTTPException(status_code=403, detail="Customers can only create pending payments")
        if not prices_match(data.amount, order.total_price):
            raise HTTPException(status_code=400, detail="Payment amount must match order total")
    if data.status == "paid" and session:
        ensure_no_duplicate_paid_payment(session, order.id)
    return order


def validate_payment_status_update(
    payment: Payment | None,
    order: Order | None,
    data: PaymentStatusUpdate,
    current_user: User,
    session: Session,
) -> Payment:
    if current_user.role not in PAYMENT_RECONCILE_ROLES:
        raise HTTPException(status_code=403, detail="Only admin and cashier can reconcile payments")
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if data.status not in PAYMENT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid payment status")
    if order.status == "cancelled" and data.status == "paid":
        raise HTTPException(status_code=400, detail="Cannot mark payment paid for a cancelled order")
    if data.status == "paid":
        ensure_no_duplicate_paid_payment(session, order.id, exclude_payment_id=payment.id)
    return payment


def ensure_no_duplicate_paid_payment(session: Session, order_id: int, exclude_payment_id: int | None = None) -> None:
    query = session.query(Payment).filter(Payment.order_id == order_id, Payment.status == "paid")
    if exclude_payment_id is not None:
        query = query.filter(Payment.id != exclude_payment_id)
    if query.first():
        raise HTTPException(status_code=400, detail="Order already has a paid payment")
