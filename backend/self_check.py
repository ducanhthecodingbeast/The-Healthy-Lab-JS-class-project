from pathlib import Path
import os
import tempfile


db_path = Path(tempfile.gettempdir()) / "healthy_lab_self_check.db"
db_path.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

from sqlalchemy.orm import Session  # noqa: E402

from database import engine  # noqa: E402
from main import admin_summary, create_order, login, my_orders, update_order_status  # noqa: E402
from models import Product, User  # noqa: E402
from schemas import LoginRequest, OrderCreate, OrderItemCreate, OrderStatusUpdate  # noqa: E402
from seed import seed  # noqa: E402


def main():
    seed()

    with Session(engine) as session:
        customer_login = login(LoginRequest(email="customer@healthylab.test", password="password123"), session)
        assert customer_login.phone == "0900000004"
        assert customer_login.address == "123 Green Street"

        customer = session.query(User).filter(User.email == "customer@healthylab.test").first()
        product = session.query(Product).filter(Product.is_available.is_(True)).first()
        order = create_order(
            OrderCreate(
                customer_name=customer.name,
                customer_phone=customer.phone,
                delivery_address=customer.address,
                note="Self-check order",
                items=[
                    OrderItemCreate(product_id=product.id, quantity=2),
                    OrderItemCreate(
                        product_name="Custom Food Lab Bowl",
                        quantity=1,
                        unit_price=12.5,
                        custom_details="Quinoa, Salmon, Avocado",
                    ),
                ],
            ),
            session,
            customer,
        )

        assert order.items[0].product_id == product.id
        assert order.items[1].product_id is None
        assert order.total_price == round(product.price * 2 + 12.5, 2)
        assert any(item.custom_details for item in order.items)

        own_orders = my_orders(session, customer)
        assert any(existing.id == order.id for existing in own_orders)

        cancelled = update_order_status(order.id, OrderStatusUpdate(status="cancelled"), session, customer)
        assert cancelled.status == "cancelled"

        admin = session.query(User).filter(User.email == "admin@healthylab.test").first()
        summary = admin_summary(session, admin)
        assert summary.total_orders >= 1
        assert summary.total_products >= summary.active_products >= 1

    print("self_check passed")


if __name__ == "__main__":
    main()
