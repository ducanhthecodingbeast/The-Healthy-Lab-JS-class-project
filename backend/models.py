from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text

from database import Base


ROLES = ["customer", "chef", "delivery", "admin"]
ORDER_STATUSES = ["pending", "preparing", "ready", "delivering", "delivered", "cancelled"]


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
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    custom_details = Column(Text, nullable=True)
