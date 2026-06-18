from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from auth import hash_password
from database import create_db_and_tables, engine
from models import (
    Ingredient,
    InventoryLot,
    Membership,
    Notification,
    Order,
    OrderItem,
    OrderStockDeduction,
    Payment,
    Product,
    QueueEntry,
    RecipeItem,
    Reservation,
    RestaurantTable,
    StaffProfile,
    Supplier,
    User,
    Voucher,
)


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
        "name": "Cashier",
        "email": "cashier@healthylab.test",
        "password": "password123",
        "role": "cashier",
        "phone": "0900000005",
        "address": "The Healthy Lab Front Desk",
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


SUPPLIERS = [
    ("Green Farm Co.", "Hoa", "0903333000", "Vegetables"),
    ("Fresh Grain Supply", "Bao", "0904444000", "Quinoa, rice"),
    ("Daily Dairy & Drinks", "Lan", "0905555000", "Almond milk, juices"),
]


INGREDIENTS = [
    ("Quinoa", "kg", 5),
    ("Avocado", "pcs", 20),
    ("Almond Milk", "liters", 6),
    ("Salmon", "kg", 2),
    ("Chicken", "kg", 3),
    ("Mixed Greens", "kg", 4),
    ("Whole Wheat Wrap", "pcs", 15),
    ("Orange Juice", "liters", 5),
]


VOUCHERS = [
    ("GREEN10", "10% off healthy bowls", 10, 8, "active"),
    ("SMOOTHIE5", "$5 smoothie combo discount", 0, 12, "draft"),
    ("JUICELOVE", "5% off juices and smoothies", 5, 5, "active"),
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
        session.query(Notification).delete()
        session.query(Payment).delete()
        session.query(QueueEntry).delete()
        session.query(Reservation).delete()
        session.query(RestaurantTable).delete()
        session.query(OrderStockDeduction).delete()
        session.query(OrderItem).delete()
        session.query(Order).delete()
        session.query(InventoryLot).delete()
        session.query(RecipeItem).delete()
        session.query(Ingredient).delete()
        session.query(Supplier).delete()
        session.query(StaffProfile).delete()
        session.query(Voucher).delete()
        session.query(Membership).delete()
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
            if user.role == "customer":
                session.add(Membership(user_id=user.id, points=0, tier="bronze"))
                session.commit()

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

        suppliers_by_name = {}
        for name, contact_name, phone, item in SUPPLIERS:
            supplier = Supplier(name=name, contact_name=contact_name, phone=phone, item=item)
            session.add(supplier)
            session.commit()
            session.refresh(supplier)
            suppliers_by_name[supplier.name] = supplier

        ingredients_by_name = {}
        for name, unit, low_stock_threshold in INGREDIENTS:
            ingredient = Ingredient(name=name, unit=unit, low_stock_threshold=low_stock_threshold)
            session.add(ingredient)
            session.commit()
            session.refresh(ingredient)
            ingredients_by_name[ingredient.name] = ingredient

        today = datetime.utcnow()
        lot_data = [
            ("Quinoa", "Fresh Grain Supply", 8.5, 3.2, today + timedelta(days=20)),
            ("Avocado", "Green Farm Co.", 18, 0.8, today + timedelta(days=2)),
            ("Almond Milk", "Daily Dairy & Drinks", 12, 1.5, today + timedelta(days=14)),
            ("Salmon", "Green Farm Co.", 4, 12, today + timedelta(days=5)),
            ("Chicken", "Green Farm Co.", 5, 8, today + timedelta(days=6)),
            ("Mixed Greens", "Green Farm Co.", 3.5, 2.4, today + timedelta(days=3)),
            ("Whole Wheat Wrap", "Fresh Grain Supply", 24, 0.4, today + timedelta(days=30)),
            ("Orange Juice", "Daily Dairy & Drinks", 9, 1.1, today + timedelta(days=7)),
        ]
        for ingredient_name, supplier_name, quantity, unit_cost, expires_at in lot_data:
            session.add(
                InventoryLot(
                    ingredient_id=ingredients_by_name[ingredient_name].id,
                    supplier_id=suppliers_by_name[supplier_name].id,
                    quantity=quantity,
                    remaining_quantity=quantity,
                    unit_cost=unit_cost,
                    expires_at=expires_at,
                )
            )
        session.commit()

        recipe_data = {
            "Avocado Quinoa Bowl": [("Quinoa", 0.18), ("Avocado", 1), ("Mixed Greens", 0.08)],
            "Salmon Power Bowl": [("Salmon", 0.18), ("Quinoa", 0.12), ("Mixed Greens", 0.06)],
            "Chicken Protein Bowl": [("Chicken", 0.2), ("Quinoa", 0.12), ("Mixed Greens", 0.06)],
            "Garden Wrap": [("Whole Wheat Wrap", 1), ("Mixed Greens", 0.08), ("Avocado", 0.5)],
            "Turkey Avocado Wrap": [("Whole Wheat Wrap", 1), ("Mixed Greens", 0.06), ("Avocado", 0.5)],
            "Rainbow Salad": [("Mixed Greens", 0.18), ("Avocado", 0.5)],
            "Greek Chickpea Salad": [("Mixed Greens", 0.18)],
            "Berry Protein Smoothie": [("Almond Milk", 0.25)],
            "Green Detox Smoothie": [("Almond Milk", 0.2), ("Mixed Greens", 0.06)],
            "Cold Pressed Orange Juice": [("Orange Juice", 0.35)],
        }
        for product_name, items in recipe_data.items():
            product = products_by_name[product_name]
            for ingredient_name, quantity in items:
                session.add(
                    RecipeItem(
                        product_id=product.id,
                        ingredient_id=ingredients_by_name[ingredient_name].id,
                        quantity=quantity,
                    )
                )
        session.commit()

        for code, description, discount_percent, min_order_total, voucher_status in VOUCHERS:
            session.add(
                Voucher(
                    code=code,
                    description=description,
                    discount_percent=discount_percent,
                    min_order_total=min_order_total,
                    status=voucher_status,
                )
            )
        session.commit()

        table_a = RestaurantTable(name="Table A1", capacity=2, status="available")
        table_b = RestaurantTable(name="Table B1", capacity=4, status="available")
        table_c = RestaurantTable(name="Table C1", capacity=6, status="available")
        session.add_all([table_a, table_b, table_c])
        session.commit()
        session.refresh(table_b)

        staff_profiles = [
            StaffProfile(user_id=users_by_email["chef@healthylab.test"].id, name="Chef", role="chef", shift="Morning", status="On duty"),
            StaffProfile(user_id=users_by_email["delivery@healthylab.test"].id, name="Delivery", role="delivery", shift="Evening", status="On duty"),
            StaffProfile(user_id=users_by_email["cashier@healthylab.test"].id, name="Cashier", role="cashier", shift="Lunch rush", status="Standby"),
        ]
        session.add_all(staff_profiles)
        session.commit()

        customer = users_by_email["customer@healthylab.test"]
        session.add(
            Reservation(
                user_id=customer.id,
                table_id=table_b.id,
                customer_name="Linh Tran",
                customer_phone="0901111000",
                party_size=4,
                reservation_time=today + timedelta(days=1, hours=18),
                status="booked",
                note="Window seat if possible",
            )
        )
        session.add(
            QueueEntry(
                user_id=customer.id,
                customer_name="Walk-in A12",
                customer_phone="0901111000",
                party_size=3,
                status="waiting",
                wait_minutes=12,
            )
        )
        session.add(
            Notification(
                title="Low stock",
                message="Avocado is below threshold.",
                level="warning",
            )
        )
        session.add(
            Notification(
                title="Expiry watch",
                message="Avocado batch expires soon.",
                level="info",
            )
        )
        session.commit()

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
                        product_id=product.id,
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
            if status == "delivered":
                session.add(Payment(order_id=order.id, amount=order.total_price, method="cash", status="paid"))
                membership = session.query(Membership).filter(Membership.user_id == customer.id).first()
                membership.points += int(order.total_price)
                membership.tier = "bronze"
                session.add(membership)
                session.commit()

        print(
            "Seed complete: "
            f"{session.query(User).count()} users, "
            f"{session.query(Product).count()} products, "
            f"{session.query(Order).count()} orders"
        )


if __name__ == "__main__":
    seed()
