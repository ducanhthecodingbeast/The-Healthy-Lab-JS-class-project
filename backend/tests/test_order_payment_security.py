from pathlib import Path
from datetime import datetime, timedelta
import os
import tempfile


db_path = Path(tempfile.gettempdir()) / f"healthy_lab_pytest_{os.getpid()}.db"
db_path.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

import pytest  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from auth import hash_password  # noqa: E402
from database import engine  # noqa: E402
from main import (  # noqa: E402
    call_next_queue_entry,
    complete_reservation,
    create_order,
    create_payment,
    list_notifications,
    list_orders,
    list_payments,
    preview_food_lab_item,
    seat_queue_entry,
    list_products,
    list_queue_entries,
    list_reservations,
    my_orders,
    update_payment_status,
    update_order_status,
)
from models import Ingredient, InventoryLot, Membership, Notification, OrderMembershipAward, Product, QueueEntry, Reservation, User  # noqa: E402
from schemas import (  # noqa: E402
    FoodLabCustomPreviewCreate,
    FoodLabCustomSelection,
    OrderCreate,
    OrderItemCreate,
    OrderStatusUpdate,
    PaymentCreate,
    PaymentStatusUpdate,
)
from seed import seed  # noqa: E402


@pytest.fixture()
def session():
    engine.dispose()
    db_path.unlink(missing_ok=True)
    seed()
    with Session(engine) as db_session:
        yield db_session
    engine.dispose()
    db_path.unlink(missing_ok=True)


def get_user(session: Session, email: str) -> User:
    return session.query(User).filter(User.email == email).one()


def get_product(session: Session) -> Product:
    return session.query(Product).filter(Product.is_available.is_(True)).first()


def add_customer(session: Session, email: str) -> User:
    user = User(
        name="Second Customer",
        email=email,
        password_hash=hash_password("password123"),
        role="customer",
        phone="0902222000",
        address="456 Green Street",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def product_order(session: Session, customer: User):
    product = get_product(session)
    return create_order(
        OrderCreate(
            customer_name=customer.name,
            customer_phone=customer.phone,
            delivery_address=customer.address,
            items=[OrderItemCreate(product_id=product.id, quantity=2)],
        ),
        session,
        customer,
    )


def assert_http_error(status_code: int, callback):
    with pytest.raises(HTTPException) as exc_info:
        callback()
    assert exc_info.value.status_code == status_code


def test_product_item_price_tampering_is_rejected_and_server_price_is_used(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    product = get_product(session)

    assert_http_error(
        400,
        lambda: create_order(
            OrderCreate(
                delivery_address=customer.address,
                items=[OrderItemCreate(product_id=product.id, quantity=2, unit_price=0.01)],
            ),
            session,
            customer,
        ),
    )
    assert_http_error(
        400,
        lambda: create_order(
            OrderCreate(
                delivery_address=customer.address,
                items=[OrderItemCreate(product_id=product.id, quantity=2, total_price=0.02)],
            ),
            session,
            customer,
        ),
    )

    order = create_order(
        OrderCreate(
            delivery_address=customer.address,
            items=[OrderItemCreate(product_id=product.id, quantity=3)],
        ),
        session,
        customer,
    )
    assert order.items[0].unit_price == product.price
    assert order.items[0].total_price == round(product.price * 3, 2)
    assert order.total_price == round(product.price * 3, 2)


def test_customer_custom_item_arbitrary_price_is_rejected(session: Session):
    customer = get_user(session, "customer@healthylab.test")

    assert_http_error(
        403,
        lambda: create_order(
            OrderCreate(
                delivery_address=customer.address,
                items=[OrderItemCreate(product_name="Custom Bowl", quantity=1, unit_price=12.5)],
            ),
            session,
            customer,
        ),
    )


def test_admin_cashier_and_staff_can_create_custom_priced_items(session: Session):
    staff = User(
        name="Staff User",
        email="staff@healthylab.test",
        password_hash=hash_password("password123"),
        role="staff",
        phone="0903333000",
        address="The Healthy Lab Floor",
    )
    session.add(staff)
    session.commit()
    session.refresh(staff)

    for user in [get_user(session, "admin@healthylab.test"), get_user(session, "cashier@healthylab.test"), staff]:
        order = create_order(
            OrderCreate(
                customer_name="Counter guest",
                customer_phone="0909999000",
                delivery_address=user.address,
                items=[
                    OrderItemCreate(
                        product_name="Custom Food Lab Bowl",
                        quantity=2,
                        unit_price=12.5,
                        total_price=25.0,
                    )
                ],
            ),
            session,
            user,
        )
        assert order.items[0].product_id is None
        assert order.items[0].total_price == 25.0


def test_forbidden_order_status_transitions_are_rejected(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    order = product_order(session, customer)

    assert_http_error(
        403,
        lambda: update_order_status(order.id, OrderStatusUpdate(status="ready"), session, get_user(session, "chef@healthylab.test")),
    )
    assert_http_error(
        403,
        lambda: update_order_status(
            order.id,
            OrderStatusUpdate(status="delivering"),
            session,
            get_user(session, "delivery@healthylab.test"),
        ),
    )

    other_customer = add_customer(session, "other@healthylab.test")
    assert_http_error(
        403,
        lambda: update_order_status(order.id, OrderStatusUpdate(status="cancelled"), session, other_customer),
    )


def test_customer_payment_authorization_and_amount_validation(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    order = product_order(session, customer)

    assert_http_error(
        400,
        lambda: create_payment(
            PaymentCreate(order_id=order.id, amount=order.total_price - 0.01, method="card", status="pending"),
            session,
            customer,
        ),
    )
    assert_http_error(
        400,
        lambda: create_payment(
            PaymentCreate(order_id=order.id, amount=order.total_price + 0.01, method="card", status="pending"),
            session,
            customer,
        ),
    )
    assert_http_error(
        403,
        lambda: create_payment(
            PaymentCreate(order_id=order.id, amount=order.total_price, method="card", status="paid"),
            session,
            customer,
        ),
    )

    other_customer = add_customer(session, "payer@healthylab.test")
    assert_http_error(
        403,
        lambda: create_payment(
            PaymentCreate(order_id=order.id, amount=order.total_price, method="card", status="pending"),
            session,
            other_customer,
        ),
    )

    cancelled = update_order_status(order.id, OrderStatusUpdate(status="cancelled"), session, customer)
    assert cancelled.status == "cancelled"
    assert_http_error(
        400,
        lambda: create_payment(
            PaymentCreate(order_id=order.id, amount=order.total_price, method="card", status="pending"),
            session,
            customer,
        ),
    )


def test_admin_and_cashier_can_reconcile_payments_for_active_orders(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    cashier = get_user(session, "cashier@healthylab.test")

    admin_order = product_order(session, customer)
    admin_payment = create_payment(
        PaymentCreate(order_id=admin_order.id, amount=1.0, method="cash", status="paid"),
        session,
        admin,
    )
    assert admin_payment.status == "paid"

    cashier_order = product_order(session, customer)
    cashier_payment = create_payment(
        PaymentCreate(order_id=cashier_order.id, amount=cashier_order.total_price + 1, method="cash", status="refunded"),
        session,
        cashier,
    )
    assert cashier_payment.status == "refunded"


def test_delivered_unpaid_order_does_not_award_membership_points(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    order = product_order(session, customer)
    before_points = membership_points(session, customer)

    update_order_status(order.id, OrderStatusUpdate(status="delivered"), session, admin)

    assert membership_points(session, customer) == before_points
    assert session.query(OrderMembershipAward).filter(OrderMembershipAward.order_id == order.id).first() is None


def test_paid_before_delivered_order_awards_membership_points_once(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    order = product_order(session, customer)
    before_points = membership_points(session, customer)

    create_payment(PaymentCreate(order_id=order.id, amount=order.total_price, method="cash", status="paid"), session, admin)
    update_order_status(order.id, OrderStatusUpdate(status="delivered"), session, admin)
    expected_points = before_points + int(order.total_price)
    assert membership_points(session, customer) == expected_points

    update_order_status(order.id, OrderStatusUpdate(status="delivered"), session, admin)
    assert membership_points(session, customer) == expected_points
    assert session.query(OrderMembershipAward).filter(OrderMembershipAward.order_id == order.id).count() == 1


def test_paid_after_delivered_order_awards_membership_points_once(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    order = product_order(session, customer)
    before_points = membership_points(session, customer)

    update_order_status(order.id, OrderStatusUpdate(status="delivered"), session, admin)
    assert membership_points(session, customer) == before_points

    pending = create_payment(
        PaymentCreate(order_id=order.id, amount=order.total_price, method="card", status="pending"),
        session,
        customer,
    )
    update_payment_status(pending.id, PaymentStatusUpdate(status="paid"), session, admin)
    expected_points = before_points + int(order.total_price)
    assert membership_points(session, customer) == expected_points

    update_payment_status(pending.id, PaymentStatusUpdate(status="paid"), session, admin)
    assert membership_points(session, customer) == expected_points
    assert session.query(OrderMembershipAward).filter(OrderMembershipAward.order_id == order.id).count() == 1


def test_product_pagination_caps_and_category_filter(session: Session):
    old_style_products = list_products(False, session)
    bowls = list_products(category="BOWLS", limit=2, offset=1, session=session)

    assert old_style_products
    assert len(bowls) == 2
    assert all(product.category == "bowls" for product in bowls)
    assert_http_error(400, lambda: list_products(limit=201, session=session))
    assert_http_error(400, lambda: list_products(offset=-1, session=session))


def test_order_filters_preserve_role_scopes(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    other_customer = add_customer(session, "order-filter@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    chef = get_user(session, "chef@healthylab.test")

    own_order = product_order(session, customer)
    other_order = product_order(session, other_customer)

    own_pending = my_orders(session, customer, status="pending", limit=20)
    assert own_order.id in {order.id for order in own_pending}
    assert other_order.id not in {order.id for order in own_pending}
    assert all(order.customer_id == customer.id and order.status == "pending" for order in own_pending)

    admin_filtered = list_orders(session, admin, status="pending", customer_id=other_customer.id, limit=20)
    assert other_order.id in {order.id for order in admin_filtered}
    assert all(order.customer_id == other_customer.id and order.status == "pending" for order in admin_filtered)

    chef_delivered = list_orders(session, chef, status="delivered")
    assert chef_delivered == []
    assert_http_error(403, lambda: list_orders(session, chef, customer_id=customer.id))
    assert_http_error(400, lambda: list_orders(session, admin, status="not-real"))


def test_structured_food_lab_builder_prices_and_rejects_invalid_selection(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    selection = FoodLabCustomSelection(
        base="quinoa-bowl",
        protein="chicken",
        extras=["avocado"],
        dressing="lemon-herb",
    )

    preview = preview_food_lab_item(FoodLabCustomPreviewCreate(selection=selection, quantity=2))
    assert preview.product_name == "Food Lab Herbed Chicken Quinoa Bowl"
    assert preview.unit_price == 10.5
    assert preview.total_price == 21.0
    assert preview.inventory_needs["Quinoa"] == 0.36

    order = create_order(
        OrderCreate(
            delivery_address=customer.address,
            items=[OrderItemCreate(quantity=2, custom_food_lab=selection)],
        ),
        session,
        customer,
    )
    assert order.items[0].product_id is None
    assert order.items[0].product_name == preview.product_name
    assert order.items[0].custom_details == preview.custom_details
    assert order.items[0].custom_data["builder"] == "food_lab"
    quinoa_need = next(need for need in order.items[0].custom_data["inventory_needs"] if need["ingredient"] == "Quinoa")
    assert quinoa_need["quantity"] == 0.18
    assert order.total_price == preview.total_price

    assert_http_error(
        400,
        lambda: create_order(
            OrderCreate(
                delivery_address=customer.address,
                items=[
                    OrderItemCreate(
                        quantity=1,
                        custom_food_lab=FoodLabCustomSelection(
                            base="not-real",
                            protein="chicken",
                            extras=[],
                            dressing="lemon-herb",
                        ),
                    )
                ],
            ),
            session,
            customer,
        ),
    )

    assert_http_error(
        400,
        lambda: create_order(
            OrderCreate(
                delivery_address=customer.address,
                items=[OrderItemCreate(quantity=1, custom_food_lab=selection, unit_price=0.01)],
            ),
            session,
            customer,
        ),
    )


def test_structured_food_lab_inventory_deduction_is_deterministic(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    selection = FoodLabCustomSelection(
        base="quinoa-bowl",
        protein="chicken",
        extras=["avocado"],
        dressing="lemon-herb",
    )

    before_quinoa = ingredient_stock(session, "Quinoa")
    before_chicken = ingredient_stock(session, "Chicken")
    before_avocado = ingredient_stock(session, "Avocado")

    order = create_order(
        OrderCreate(
            delivery_address=customer.address,
            items=[OrderItemCreate(quantity=2, custom_food_lab=selection)],
        ),
        session,
        customer,
    )
    update_order_status(order.id, OrderStatusUpdate(status="delivered"), session, admin)

    assert round(before_quinoa - ingredient_stock(session, "Quinoa"), 2) == 0.36
    assert round(before_chicken - ingredient_stock(session, "Chicken"), 2) == 0.32
    assert round(before_avocado - ingredient_stock(session, "Avocado"), 2) == 1.0


def test_reservation_and_queue_filters_are_scoped_and_paginated(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    other_customer = add_customer(session, "restaurant-filter@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    now = datetime.utcnow()
    session.add(
        Reservation(
            user_id=other_customer.id,
            table_id=None,
            customer_name="Other Guest",
            customer_phone="0904444999",
            party_size=2,
            reservation_time=now + timedelta(days=3),
            status="cancelled",
        )
    )
    session.add(
        QueueEntry(
            user_id=other_customer.id,
            customer_name="Other Queue",
            customer_phone="0904444888",
            party_size=2,
            status="called",
            wait_minutes=5,
        )
    )
    session.commit()

    customer_reservations = list_reservations(session, customer, status="booked", limit=20)
    assert customer_reservations
    assert all(reservation.user_id == customer.id and reservation.status == "booked" for reservation in customer_reservations)

    cancelled_reservations = list_reservations(session, admin, status="cancelled", from_time=now, limit=1)
    assert len(cancelled_reservations) == 1
    assert cancelled_reservations[0].user_id == other_customer.id

    called_queue = list_queue_entries(session, admin, status="called")
    assert called_queue
    assert all(entry.status == "called" for entry in called_queue)
    assert list_queue_entries(session, customer, status="called") == []
    assert_http_error(400, lambda: list_reservations(session, admin, status="not-real"))
    assert_http_error(400, lambda: list_queue_entries(session, admin, status="not-real"))


def test_queue_and_reservation_operational_endpoints(session: Session):
    admin = get_user(session, "admin@healthylab.test")
    customer = get_user(session, "customer@healthylab.test")
    reservation = session.query(Reservation).filter(Reservation.user_id == customer.id, Reservation.status == "booked").first()

    called_entry = call_next_queue_entry(session, admin)
    assert called_entry.status == "called"

    seated_entry = seat_queue_entry(called_entry.id, session, admin)
    assert seated_entry.status == "seated"
    assert_http_error(400, lambda: seat_queue_entry(called_entry.id, session, admin))

    completed = complete_reservation(reservation.id, session, admin)
    assert completed.status == "completed"
    assert_http_error(400, lambda: complete_reservation(reservation.id, session, admin))


def test_payment_and_notification_filters(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    order = product_order(session, customer)
    payment = create_payment(
        PaymentCreate(order_id=order.id, amount=1.0, method="cash", status="paid"),
        session,
        admin,
    )

    paid_payments = list_payments(session, admin, status="paid", order_id=order.id, limit=5)
    assert [item.id for item in paid_payments] == [payment.id]
    assert_http_error(400, lambda: list_payments(session, admin, status="not-real"))
    assert_http_error(400, lambda: list_payments(session, admin, order_id=0))

    session.add(Notification(title="Read warning", message="Already read", level="warning", is_read=True))
    session.add(Notification(title="Unread warning", message="Needs attention", level="warning", is_read=False))
    session.commit()

    unread_warnings = list_notifications(session, admin, unread_only=True, level="warning", limit=20)
    assert unread_warnings
    assert all(notification.level == "warning" and not notification.is_read for notification in unread_warnings)
    assert_http_error(400, lambda: list_notifications(session, admin, limit=0))


def test_payment_lifecycle_prevents_duplicate_paid_payments(session: Session):
    customer = get_user(session, "customer@healthylab.test")
    admin = get_user(session, "admin@healthylab.test")
    order = product_order(session, customer)

    pending = create_payment(
        PaymentCreate(order_id=order.id, amount=order.total_price, method="card", status="pending"),
        session,
        customer,
    )
    paid = update_payment_status(pending.id, PaymentStatusUpdate(status="paid"), session, admin)
    assert paid.status == "paid"

    assert_http_error(
        400,
        lambda: create_payment(
            PaymentCreate(order_id=order.id, amount=order.total_price, method="cash", status="paid"),
            session,
            admin,
        ),
    )

    second_pending = create_payment(
        PaymentCreate(order_id=order.id, amount=order.total_price, method="card", status="pending"),
        session,
        customer,
    )
    assert_http_error(400, lambda: update_payment_status(second_pending.id, PaymentStatusUpdate(status="paid"), session, admin))


def ingredient_stock(session: Session, ingredient_name: str) -> float:
    ingredient = session.query(Ingredient).filter(Ingredient.name == ingredient_name).one()
    lots = session.query(InventoryLot).filter(InventoryLot.ingredient_id == ingredient.id).all()
    return round(sum(lot.remaining_quantity for lot in lots), 4)


def membership_points(session: Session, customer: User) -> int:
    membership = session.query(Membership).filter(Membership.user_id == customer.id).one()
    return membership.points
