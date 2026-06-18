from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from database import Base


ROLES = ["customer", "chef", "delivery", "cashier", "staff", "admin"]
ORDER_STATUSES = ["pending", "preparing", "ready", "delivering", "delivered", "cancelled"]
RESERVATION_STATUSES = ["booked", "seated", "cancelled", "completed"]
QUEUE_STATUSES = ["waiting", "called", "seated", "cancelled"]
PAYMENT_STATUSES = ["pending", "paid", "failed", "refunded"]


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="customer", index=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    calories = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True, index=True, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    delivery_address = Column(String, nullable=False)
    status = Column(String, default="pending", index=True, nullable=False)
    total_price = Column(Float, default=0, nullable=False)
    note = Column(Text, nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=True)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    custom_details = Column(Text, nullable=True)


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    tier = Column(String, default="bronze", index=True, nullable=False)


class Voucher(Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    discount_percent = Column(Float, default=0, nullable=False)
    min_order_total = Column(Float, default=0, nullable=False)
    status = Column(String, default="active", index=True, nullable=False)


class StaffProfile(Base):
    __tablename__ = "staff_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    role = Column(String, index=True, nullable=False)
    shift = Column(String, nullable=True)
    status = Column(String, default="Standby", index=True, nullable=False)


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    item = Column(String, nullable=True)


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    unit = Column(String, nullable=False)
    low_stock_threshold = Column(Float, default=0, nullable=False)


class RecipeItem(Base):
    __tablename__ = "recipe_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), index=True, nullable=False)
    quantity = Column(Float, nullable=False)


class InventoryLot(Base):
    __tablename__ = "inventory_lots"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    quantity = Column(Float, nullable=False)
    remaining_quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0, nullable=False)
    imported_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)


class OrderStockDeduction(Base):
    __tablename__ = "order_stock_deductions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, index=True, nullable=False)
    deducted_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RestaurantTable(Base):
    __tablename__ = "restaurant_tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String, default="available", index=True, nullable=False)


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    table_id = Column(Integer, ForeignKey("restaurant_tables.id"), nullable=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    party_size = Column(Integer, nullable=False)
    reservation_time = Column(DateTime, index=True, nullable=False)
    status = Column(String, default="booked", index=True, nullable=False)
    note = Column(Text, nullable=True)


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    party_size = Column(Integer, nullable=False)
    status = Column(String, default="waiting", index=True, nullable=False)
    wait_minutes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, default="cash", nullable=False)
    status = Column(String, default="pending", index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    level = Column(String, default="info", index=True, nullable=False)
    is_read = Column(Boolean, default=False, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
