from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import get_current_user, require_role
from database import get_session
from models import InventoryLot, Order, Payment, Product, QueueEntry, Reservation, StaffProfile, User, Voucher
from schemas import AdminSummary, MembershipRead, StaffProfileCreate, StaffProfileRead, UserRead, VoucherRead
from services.inventory import inventory_rows
from services.memberships import get_or_create_membership


router = APIRouter()


@router.get("/users", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    return session.query(User).all()


@router.get("/admin/summary", response_model=AdminSummary)
def admin_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    total_orders = session.query(func.count(Order.id)).scalar()
    pending_orders = session.query(func.count(Order.id)).filter(Order.status == "pending").scalar()
    delivered_orders = session.query(func.count(Order.id)).filter(Order.status == "delivered").scalar()
    total_revenue = session.query(func.coalesce(func.sum(Order.total_price), 0)).filter(Order.status == "delivered").scalar()
    total_customers = session.query(func.count(User.id)).filter(User.role == "customer").scalar()
    total_products = session.query(func.count(Product.id)).scalar()
    active_products = session.query(func.count(Product.id)).filter(Product.is_available.is_(True)).scalar()
    kitchen_orders = session.query(func.count(Order.id)).filter(Order.status.in_(["pending", "preparing"])).scalar()
    delivery_orders = session.query(func.count(Order.id)).filter(Order.status.in_(["ready", "delivering"])).scalar()
    items = inventory_rows(session)
    low_stock_items = len([item for item in items if item.stock <= item.low_stock_threshold])
    soon = datetime.utcnow() + timedelta(days=7)
    expiring_lots = (
        session.query(func.count(InventoryLot.id))
        .filter(InventoryLot.remaining_quantity > 0, InventoryLot.expires_at.isnot(None), InventoryLot.expires_at <= soon)
        .scalar()
    )
    active_reservations = session.query(func.count(Reservation.id)).filter(Reservation.status.in_(["booked", "seated"])).scalar()
    waiting_queue = session.query(func.count(QueueEntry.id)).filter(QueueEntry.status == "waiting").scalar()
    paid_orders = session.query(func.count(Payment.id)).filter(Payment.status == "paid").scalar()

    return AdminSummary(
        total_orders=total_orders,
        pending_orders=pending_orders,
        delivered_orders=delivered_orders,
        total_revenue=round(float(total_revenue), 2),
        total_customers=total_customers,
        total_products=total_products,
        active_products=active_products,
        kitchen_orders=kitchen_orders,
        delivery_orders=delivery_orders,
        low_stock_items=low_stock_items,
        expiring_lots=expiring_lots,
        active_reservations=active_reservations,
        waiting_queue=waiting_queue,
        paid_orders=paid_orders,
    )


@router.get("/memberships/me", response_model=MembershipRead)
def my_membership(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    membership = get_or_create_membership(current_user, session)
    session.commit()
    session.refresh(membership)
    return membership


@router.get("/vouchers", response_model=list[VoucherRead])
def list_vouchers(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = session.query(Voucher)
    if current_user.role != "admin":
        query = query.filter(Voucher.status == "active")
    return query.order_by(Voucher.code).all()


@router.get("/staff", response_model=list[StaffProfileRead])
def list_staff(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    return session.query(StaffProfile).order_by(StaffProfile.id).all()


@router.post("/staff", response_model=StaffProfileRead, status_code=status.HTTP_201_CREATED)
def create_staff_profile(
    data: StaffProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    profile = StaffProfile(**data.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
