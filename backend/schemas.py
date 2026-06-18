from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Role = Literal["customer", "chef", "delivery", "cashier", "staff", "admin"]
OrderStatus = Literal["pending", "preparing", "ready", "delivering", "delivered", "cancelled"]
ReservationStatus = Literal["booked", "seated", "cancelled", "completed"]
QueueStatus = Literal["waiting", "called", "seated", "cancelled"]
PaymentStatus = Literal["pending", "paid", "failed", "refunded"]


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
    phone: str | None = None
    address: str | None = None


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
    product_id: int | None = None
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
    total_products: int
    active_products: int
    kitchen_orders: int
    delivery_orders: int
    low_stock_items: int = 0
    expiring_lots: int = 0
    active_reservations: int = 0
    waiting_queue: int = 0
    paid_orders: int = 0


class MembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    points: int
    tier: str


class VoucherRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    description: str
    discount_percent: float
    min_order_total: float
    status: str


class StaffProfileCreate(BaseModel):
    user_id: int | None = None
    name: str
    role: str
    shift: str | None = None
    status: str = "Standby"


class StaffProfileRead(StaffProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SupplierCreate(BaseModel):
    name: str
    contact_name: str | None = None
    phone: str | None = None
    item: str | None = None


class SupplierRead(SupplierCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class IngredientCreate(BaseModel):
    name: str
    unit: str
    low_stock_threshold: float = Field(default=0, ge=0)


class IngredientRead(IngredientCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RecipeItemCreate(BaseModel):
    product_id: int
    ingredient_id: int
    quantity: float = Field(gt=0)


class RecipeItemRead(RecipeItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class InventoryLotCreate(BaseModel):
    ingredient_id: int
    supplier_id: int | None = None
    quantity: float = Field(gt=0)
    unit_cost: float = Field(default=0, ge=0)
    expires_at: datetime | None = None


class InventoryLotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingredient_id: int
    supplier_id: int | None = None
    quantity: float
    remaining_quantity: float
    unit_cost: float
    imported_at: datetime
    expires_at: datetime | None = None


class InventoryItemRead(BaseModel):
    id: int
    name: str
    unit: str
    stock: float
    low_stock_threshold: float
    expires_at: datetime | None = None


class RestaurantTableCreate(BaseModel):
    name: str
    capacity: int = Field(gt=0)
    status: str = "available"


class RestaurantTableRead(RestaurantTableCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ReservationCreate(BaseModel):
    table_id: int | None = None
    customer_name: str
    customer_phone: str
    party_size: int = Field(gt=0, le=12)
    reservation_time: datetime
    note: str | None = None
    status: ReservationStatus = "booked"


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    table_id: int | None = None
    customer_name: str
    customer_phone: str
    party_size: int
    reservation_time: datetime
    status: ReservationStatus
    note: str | None = None


class ReservationStatusUpdate(BaseModel):
    status: ReservationStatus


class QueueEntryCreate(BaseModel):
    customer_name: str
    customer_phone: str | None = None
    party_size: int = Field(gt=0, le=12)
    status: QueueStatus = "waiting"
    wait_minutes: int = Field(default=0, ge=0)


class QueueEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    customer_name: str
    customer_phone: str | None = None
    party_size: int
    status: QueueStatus
    wait_minutes: int
    created_at: datetime


class QueueStatusUpdate(BaseModel):
    status: QueueStatus
    wait_minutes: int | None = Field(default=None, ge=0)


class PaymentCreate(BaseModel):
    order_id: int
    amount: float = Field(gt=0)
    method: str = "cash"
    status: PaymentStatus = "pending"


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: float
    method: str
    status: PaymentStatus
    created_at: datetime


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    message: str
    level: str
    is_read: bool
    created_at: datetime
