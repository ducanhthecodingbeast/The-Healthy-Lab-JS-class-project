from sqlalchemy.orm import Session

from auth import hash_password
from database import create_db_and_tables, engine
from models import Order, OrderItem, Product, User


USERS = [
    {
        "name": "Admin",
        "email": "admin@healthylab.test",
        "password": "password123",
        "role": "admin",
        "phone": "0900000001",
        "address": "The Healthy Lab Office",
    },
    {
        "name": "Chef",
        "email": "chef@healthylab.test",
        "password": "password123",
        "role": "chef",
        "phone": "0900000002",
        "address": "The Healthy Lab Kitchen",
    },
    {
        "name": "Delivery",
        "email": "delivery@healthylab.test",
        "password": "password123",
        "role": "delivery",
        "phone": "0900000003",
        "address": "The Healthy Lab Delivery Desk",
    },
    {
        "name": "Customer",
        "email": "customer@healthylab.test",
        "password": "password123",
        "role": "customer",
        "phone": "0900000004",
        "address": "123 Green Street",
    },
]


PRODUCTS = [
    ("Avocado Quinoa Bowl", "bowls", "Quinoa, avocado, chickpeas, greens, and lemon tahini.", 8.50, 520, "assets/images/food-menu-1.png"),
    ("Salmon Power Bowl", "bowls", "Grilled salmon, brown rice, edamame, cucumber, and sesame.", 10.90, 610, "assets/images/food-menu-2.png"),
    ("Chicken Protein Bowl", "bowls", "Grilled chicken, sweet potato, broccoli, and herb sauce.", 9.50, 580, "assets/images/food-menu-3.png"),
    ("Garden Wrap", "wraps", "Whole-grain wrap with hummus, cucumber, carrot, and greens.", 6.80, 390, "assets/images/food-menu-4.png"),
    ("Turkey Avocado Wrap", "wraps", "Turkey breast, avocado, tomato, greens, and yogurt sauce.", 7.90, 430, "assets/images/food-menu-5.png"),
    ("Rainbow Salad", "salads", "Mixed greens, beetroot, tomato, cucumber, radish, and seeds.", 6.50, 310, "assets/images/food-menu-6.png"),
    ("Greek Chickpea Salad", "salads", "Chickpeas, cucumber, tomato, olives, feta, and herbs.", 7.20, 360, "assets/images/promo-4.png"),
    ("Berry Protein Smoothie", "smoothies", "Berries, banana, almond milk, and plant protein.", 5.90, 280, "assets/images/promo-2.png"),
    ("Green Detox Smoothie", "smoothies", "Spinach, apple, cucumber, lemon, and ginger.", 5.50, 220, "assets/images/promo-3.png"),
    ("Cold Pressed Orange Juice", "juices", "Fresh orange juice pressed daily.", 4.20, 160, "assets/images/promo-1.png"),
]


MOCK_ORDERS = [
    ("pending", [("Avocado Quinoa Bowl", 1), ("Green Detox Smoothie", 1)], "No onion please."),
    ("preparing", [("Garden Wrap", 2)], "Cut wraps in half."),
    ("ready", [("Salmon Power Bowl", 1)], "Extra sesame sauce."),
    ("delivering", [("Rainbow Salad", 1), ("Cold Pressed Orange Juice", 2)], "Call before arriving."),
    ("delivered", [("Chicken Protein Bowl", 1), ("Berry Protein Smoothie", 1)], "Completed order."),
]


def seed():
    create_db_and_tables()

    with Session(engine) as session:
        session.query(OrderItem).delete()
        session.query(Order).delete()
        session.query(Product).delete()
        session.query(User).delete()
        session.commit()

        users_by_email = {}
        for user_data in USERS:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                phone=user_data["phone"],
                address=user_data["address"],
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            users_by_email[user.email] = user

        products_by_name = {}
        for name, category, description, price, calories, image_url in PRODUCTS:
            product = Product(
                name=name,
                category=category,
                description=description,
                price=price,
                calories=calories,
                image_url=image_url,
                is_available=True,
            )
            session.add(product)
            session.commit()
            session.refresh(product)
            products_by_name[product.name] = product

        customer = users_by_email["customer@healthylab.test"]
        for status, items, note in MOCK_ORDERS:
            order = Order(
                customer_id=customer.id,
                customer_name=customer.name,
                customer_phone=customer.phone,
                delivery_address=customer.address,
                status=status,
                note=note,
            )
            session.add(order)
            session.commit()
            session.refresh(order)

            total_price = 0
            for product_name, quantity in items:
                product = products_by_name[product_name]
                item_total = round(product.price * quantity, 2)
                total_price += item_total
                session.add(
                    OrderItem(
                        order_id=order.id,
                        product_name=product.name,
                        quantity=quantity,
                        unit_price=product.price,
                        total_price=item_total,
                        custom_details=None,
                    )
                )

            order.total_price = round(total_price, 2)
            session.add(order)
            session.commit()

        print(
            "Seed complete: "
            f"{session.query(User).count()} users, "
            f"{session.query(Product).count()} products, "
            f"{session.query(Order).count()} orders"
        )


if __name__ == "__main__":
    seed()
