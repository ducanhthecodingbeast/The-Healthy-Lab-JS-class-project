from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Role = Literal["customer", "chef", "delivery", "admin"]
OrderStatus = Literal["pending", "preparing", "ready", "delivering", "delivered", "cancelled"]


class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=6)
    phone: str | None = None
    address: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: Role
    phone: str | None = None
    address: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    id: int
    name: str
    email: str
    role: Role


class ProductCreate(BaseModel):
    name: str
    category: str
    description: str
    price: float = Field(gt=0)
    calories: int = Field(ge=0)
    image_url: str | None = None
    is_available: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    calories: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    is_available: bool | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    description: str
    price: float
    calories: int
    image_url: str | None = None
    is_available: bool


class OrderItemCreate(BaseModel):
    product_id: int | None = None
    product_name: str | None = None
    quantity: int = Field(gt=0)
    unit_price: float | None = Field(default=None, gt=0)
    total_price: float | None = Field(default=None, ge=0)
    custom_details: str | None = None


class OrderCreate(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    delivery_address: str | None = None
    note: str | None = None
    items: list[OrderItemCreate]


class OrderItemRead(BaseModel):
    id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    custom_details: str | None = None


class OrderRead(BaseModel):
    id: int
    customer_id: int
    customer_name: str
    customer_phone: str | None = None
    delivery_address: str
    status: OrderStatus
    total_price: float
    note: str | None = None
    items: list[OrderItemRead]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class AdminSummary(BaseModel):
    total_orders: int
    pending_orders: int
    delivered_orders: int
    total_revenue: float
    total_customers: int
