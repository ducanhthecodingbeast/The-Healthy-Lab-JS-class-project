from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import ORDER_STATUSES, Order, OrderItem, Product, User
from schemas import OrderCreate, OrderItemRead, OrderRead
from services.food_lab import build_food_lab_item, parse_custom_data


ORDER_STATUS_TRANSITIONS = {
    "customer": {("pending", "cancelled")},
    "chef": {("pending", "preparing"), ("preparing", "ready")},
    "delivery": {("ready", "delivering"), ("delivering", "delivered")},
}
CUSTOM_ITEM_PRICE_ROLES = {"admin", "cashier", "staff"}


def money(value: float) -> float:
    return round(float(value), 2)


def prices_match(left: float, right: float) -> bool:
    return money(left) == money(right)


def can_update_order_status(order: Order, next_status: str, current_user: User) -> bool:
    if next_status not in ORDER_STATUSES:
        return False
    if current_user.role == "admin":
        return True
    return (order.status, next_status) in ORDER_STATUS_TRANSITIONS.get(current_user.role, set()) and (
        current_user.role != "customer" or order.customer_id == current_user.id
    )


def build_order_read(order: Order, session: Session) -> OrderRead:
    items = session.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return OrderRead(
        id=order.id,
        customer_id=order.customer_id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        delivery_address=order.delivery_address,
        status=order.status,
        total_price=order.total_price,
        note=order.note,
        items=[
            OrderItemRead(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                custom_details=item.custom_details,
                custom_data=parse_custom_data(item.custom_data),
            )
            for item in items
        ],
    )


def build_order(data: OrderCreate, session: Session, current_user: User) -> Order:
    if not data.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    delivery_address = data.delivery_address or current_user.address
    if not delivery_address:
        raise HTTPException(status_code=400, detail="Delivery address is required")

    total_price = 0.0
    order_items = []
    for item_data in data.items:
        if item_data.product_id and item_data.custom_food_lab:
            raise HTTPException(status_code=400, detail="Order item cannot combine product_id and Food Lab custom selections")
        if item_data.product_id:
            product = session.get(Product, item_data.product_id)
            if not product or not product.is_available:
                raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
            product_name = product.name
            unit_price = money(product.price)
            item_total = money(unit_price * item_data.quantity)
            if item_total <= 0:
                raise HTTPException(status_code=400, detail="Product item total_price must be positive")
            if item_data.unit_price is not None and not prices_match(item_data.unit_price, unit_price):
                raise HTTPException(status_code=400, detail="Product item unit_price does not match catalog price")
            if item_data.total_price is not None and not prices_match(item_data.total_price, item_total):
                raise HTTPException(status_code=400, detail="Product item total_price does not match catalog price")
            product_id = product.id
            custom_details = item_data.custom_details
            custom_data = None
        elif item_data.custom_food_lab:
            built_item = build_food_lab_item(item_data.custom_food_lab, item_data.quantity)
            if item_data.product_name is not None and item_data.product_name != built_item.product_name:
                raise HTTPException(status_code=400, detail="Food Lab item product_name is server-generated")
            if item_data.custom_details is not None and item_data.custom_details != built_item.custom_details:
                raise HTTPException(status_code=400, detail="Food Lab item custom_details is server-generated")
            if item_data.unit_price is not None and not prices_match(item_data.unit_price, built_item.unit_price):
                raise HTTPException(status_code=400, detail="Food Lab item unit_price does not match server price")
            if item_data.total_price is not None and not prices_match(item_data.total_price, built_item.total_price):
                raise HTTPException(status_code=400, detail="Food Lab item total_price does not match server price")
            product_id = None
            product_name = built_item.product_name
            unit_price = built_item.unit_price
            item_total = built_item.total_price
            custom_details = built_item.custom_details
            custom_data = built_item.custom_data_json
        else:
            if current_user.role not in CUSTOM_ITEM_PRICE_ROLES:
                raise HTTPException(
                    status_code=403,
                    detail="Customers cannot create custom-priced items yet",
                )
            if not item_data.product_name or item_data.unit_price is None:
                raise HTTPException(status_code=400, detail="Custom order items need product_name and unit_price")
            product_name = item_data.product_name
            unit_price = money(item_data.unit_price)
            item_total = money(unit_price * item_data.quantity)
            if item_total <= 0:
                raise HTTPException(status_code=400, detail="Custom item total_price must be positive")
            if item_data.total_price is not None and not prices_match(item_data.total_price, item_total):
                raise HTTPException(status_code=400, detail="Custom item total_price must match unit_price and quantity")
            product_id = None
            custom_details = item_data.custom_details
            custom_data = None

        total_price += item_total
        order_items.append(
            {
                "product_id": product_id,
                "product_name": product_name,
                "quantity": item_data.quantity,
                "unit_price": unit_price,
                "total_price": item_total,
                "custom_details": custom_details,
                "custom_data": custom_data,
            }
        )

    if money(total_price) <= 0:
        raise HTTPException(status_code=400, detail="Order total_price must be positive")

    order = Order(
        customer_id=current_user.id,
        customer_name=data.customer_name or current_user.name,
        customer_phone=data.customer_phone or current_user.phone,
        delivery_address=delivery_address,
        status="pending",
        total_price=money(total_price),
        note=data.note,
    )
    session.add(order)
    session.flush()

    for item in order_items:
        session.add(OrderItem(order_id=order.id, **item))

    return order
