from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user, require_role
from database import get_session
from models import ORDER_STATUSES, Order, User
from pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, apply_pagination
from schemas import FoodLabCustomPreviewCreate, FoodLabCustomPreviewRead, FoodLabOptionsRead, OrderCreate, OrderRead, OrderStatusUpdate
from services.food_lab import food_lab_options, preview_food_lab
from services.inventory import deduct_order_stock
from services.memberships import award_order_membership_points
from services.orders import build_order, build_order_read, can_update_order_status


router = APIRouter()


def validate_order_status_filter(status_filter: str | None) -> None:
    if status_filter is not None and status_filter not in ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid order status filter")


@router.get("/food-lab/options", response_model=FoodLabOptionsRead)
def list_food_lab_options():
    return food_lab_options()


@router.post("/food-lab/preview", response_model=FoodLabCustomPreviewRead)
def preview_food_lab_item(data: FoodLabCustomPreviewCreate):
    return preview_food_lab(data.selection, data.quantity)


@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["customer", "admin", "cashier", "staff"])
    order = build_order(data, session, current_user)
    session.commit()
    session.refresh(order)
    return build_order_read(order, session)


@router.get("/orders/my", response_model=list[OrderRead])
def my_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    status: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
):
    validate_order_status_filter(status)
    query = session.query(Order).filter(Order.customer_id == current_user.id)
    if status:
        query = query.filter(Order.status == status)
    orders = apply_pagination(query.order_by(Order.id.desc()), limit, offset).all()
    return [build_order_read(order, session) for order in orders]


@router.get("/orders", response_model=list[OrderRead])
def list_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    status: str | None = None,
    customer_id: int | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
):
    validate_order_status_filter(status)
    if customer_id is not None and customer_id < 1:
        raise HTTPException(status_code=400, detail="customer_id must be greater than 0")

    if current_user.role == "admin":
        query = session.query(Order)
        if customer_id is not None:
            query = query.filter(Order.customer_id == customer_id)
    elif current_user.role == "chef":
        if customer_id is not None:
            raise HTTPException(status_code=403, detail="Only admins can filter orders by customer_id")
        query = session.query(Order).filter(Order.status.in_(["pending", "preparing"]))
    elif current_user.role == "delivery":
        if customer_id is not None:
            raise HTTPException(status_code=403, detail="Only admins can filter orders by customer_id")
        query = session.query(Order).filter(Order.status.in_(["ready", "delivering"]))
    else:
        raise HTTPException(status_code=403, detail="Customers should use /orders/my")

    if status:
        query = query.filter(Order.status == status)
    orders = apply_pagination(query.order_by(Order.id.desc()), limit, offset).all()
    return [build_order_read(order, session) for order in orders]


@router.get("/orders/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own orders")
    if current_user.role == "chef" and order.status not in ["pending", "preparing"]:
        raise HTTPException(status_code=403, detail="Chef can only view kitchen orders")
    if current_user.role == "delivery" and order.status not in ["ready", "delivering"]:
        raise HTTPException(status_code=403, detail="Delivery can only view delivery orders")

    return build_order_read(order, session)


@router.put("/orders/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if data.status not in ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid order status")

    if not can_update_order_status(order, data.status, current_user):
        raise HTTPException(status_code=403, detail="This role cannot make that status change")

    order.status = data.status
    session.add(order)
    if data.status == "delivered":
        deduct_order_stock(order, session)
        award_order_membership_points(order, session)
    session.commit()
    session.refresh(order)
    return build_order_read(order, session)
