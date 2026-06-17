from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import create_token, get_current_user, get_optional_current_user, hash_password, require_role, verify_password
from database import create_db_and_tables, get_session
from models import ORDER_STATUSES, Order, OrderItem, Product, User
from schemas import (
    AdminSummary,
    LoginRequest,
    LoginResponse,
    OrderCreate,
    OrderItemRead,
    OrderRead,
    OrderStatusUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    UserCreate,
    UserRead,
)


app = FastAPI(title="The Healthy Lab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_login_response(user: User) -> LoginResponse:
    return LoginResponse(
        token=create_token(user),
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        phone=user.phone,
        address=user.address,
    )


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


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
            )
            for item in items
        ],
    )


@app.get("/")
def health_check():
    return {"message": "The Healthy Lab API is running", "docs": "/docs"}


@app.post("/auth/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role="customer",
        phone=data.phone,
        address=data.address,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return build_login_response(user)


@app.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return build_login_response(user)


@app.get("/auth/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/products", response_model=list[ProductRead])
def list_products(
    include_disabled: bool = False,
    session: Session = Depends(get_session),
    current_user: User | None = Depends(get_optional_current_user),
):
    if include_disabled:
        require_role(current_user, ["admin"])
        return session.query(Product).all()
    return session.query(Product).filter(Product.is_available.is_(True)).all()


@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product or not product.is_available:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    product = Product(**data.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    data: ProductUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["customer", "admin"])
    if not data.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    delivery_address = data.delivery_address or current_user.address
    if not delivery_address:
        raise HTTPException(status_code=400, detail="Delivery address is required")

    total_price = 0.0
    order_items = []
    for item_data in data.items:
        if item_data.product_id:
            product = session.get(Product, item_data.product_id)
            if not product or not product.is_available:
                raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
            product_name = product.name
            unit_price = product.price
            product_id = product.id
        else:
            if not item_data.product_name or item_data.unit_price is None:
                raise HTTPException(status_code=400, detail="Custom order items need product_name and unit_price")
            product_name = item_data.product_name
            unit_price = item_data.unit_price
            product_id = None

        item_total = round(item_data.total_price if item_data.total_price is not None else unit_price * item_data.quantity, 2)
        total_price += item_total
        order_items.append(
            {
                "product_id": product_id,
                "product_name": product_name,
                "quantity": item_data.quantity,
                "unit_price": unit_price,
                "total_price": item_total,
                "custom_details": item_data.custom_details,
            }
        )

    order = Order(
        customer_id=current_user.id,
        customer_name=data.customer_name or current_user.name,
        customer_phone=data.customer_phone or current_user.phone,
        delivery_address=delivery_address,
        status="pending",
        total_price=round(total_price, 2),
        note=data.note,
    )
    session.add(order)
    session.flush()

    for item in order_items:
        session.add(OrderItem(order_id=order.id, **item))

    session.commit()
    session.refresh(order)
    return build_order_read(order, session)


@app.get("/orders/my", response_model=list[OrderRead])
def my_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    orders = session.query(Order).filter(Order.customer_id == current_user.id).all()
    return [build_order_read(order, session) for order in orders]


@app.get("/orders", response_model=list[OrderRead])
def list_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        orders = session.query(Order).all()
    elif current_user.role == "chef":
        orders = session.query(Order).filter(Order.status.in_(["pending", "preparing"])).all()
    elif current_user.role == "delivery":
        orders = session.query(Order).filter(Order.status.in_(["ready", "delivering"])).all()
    else:
        raise HTTPException(status_code=403, detail="Customers should use /orders/my")

    return [build_order_read(order, session) for order in orders]


@app.get("/orders/{order_id}", response_model=OrderRead)
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


@app.put("/orders/{order_id}/status", response_model=OrderRead)
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

    allowed = False
    if current_user.role == "admin":
        allowed = True
    elif current_user.role == "customer":
        allowed = order.customer_id == current_user.id and order.status == "pending" and data.status == "cancelled"
    elif current_user.role == "chef":
        allowed = (order.status, data.status) in [("pending", "preparing"), ("preparing", "ready")]
    elif current_user.role == "delivery":
        allowed = (order.status, data.status) in [("ready", "delivering"), ("delivering", "delivered")]

    if not allowed:
        raise HTTPException(status_code=403, detail="This role cannot make that status change")

    order.status = data.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return build_order_read(order, session)


@app.get("/users", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    return session.query(User).all()


@app.get("/admin/summary", response_model=AdminSummary)
def admin_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    total_orders = session.query(func.count(Order.id)).scalar()
    pending_orders = session.query(func.count(Order.id)).filter(Order.status == "pending").scalar()
    delivered_orders = session.query(func.count(Order.id)).filter(Order.status == "delivered").scalar()
    total_revenue = session.query(func.coalesce(func.sum(Order.total_price), 0)).filter(Order.status == "delivered").scalar()
    total_customers = session.query(func.count(User.id)).filter(User.role == "customer").scalar()
    total_products = session.query(func.count(Product.id)).scalar()
    active_products = session.query(func.count(Product.id)).filter(Product.is_available.is_(True)).scalar()
    kitchen_orders = session.query(func.count(Order.id)).filter(Order.status.in_(["pending", "preparing"])).scalar()
    delivery_orders = session.query(func.count(Order.id)).filter(Order.status.in_(["ready", "delivering"])).scalar()

    return AdminSummary(
        total_orders=total_orders,
        pending_orders=pending_orders,
        delivered_orders=delivered_orders,
        total_revenue=round(float(total_revenue), 2),
        total_customers=total_customers,
        total_products=total_products,
        active_products=active_products,
        kitchen_orders=kitchen_orders,
        delivery_orders=delivery_orders,
    )
