from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import create_token, get_current_user, get_optional_current_user, hash_password, require_role, verify_password
from database import create_db_and_tables, get_session
from models import (
    ORDER_STATUSES,
    QUEUE_STATUSES,
    RESERVATION_STATUSES,
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
from schemas import (
    AdminSummary,
    IngredientCreate,
    IngredientRead,
    InventoryItemRead,
    InventoryLotCreate,
    InventoryLotRead,
    LoginRequest,
    LoginResponse,
    MembershipRead,
    NotificationRead,
    OrderCreate,
    OrderItemRead,
    OrderRead,
    OrderStatusUpdate,
    PaymentCreate,
    PaymentRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    QueueEntryCreate,
    QueueEntryRead,
    QueueStatusUpdate,
    RecipeItemCreate,
    RecipeItemRead,
    ReservationCreate,
    ReservationRead,
    ReservationStatusUpdate,
    RestaurantTableCreate,
    RestaurantTableRead,
    StaffProfileCreate,
    StaffProfileRead,
    SupplierCreate,
    SupplierRead,
    UserCreate,
    UserRead,
    VoucherRead,
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


def membership_tier(points: int) -> str:
    if points >= 250:
        return "gold"
    if points >= 100:
        return "silver"
    return "bronze"


def get_or_create_membership(user: User, session: Session) -> Membership:
    membership = session.query(Membership).filter(Membership.user_id == user.id).first()
    if membership:
        return membership

    membership = Membership(user_id=user.id, points=0, tier="bronze")
    session.add(membership)
    session.flush()
    return membership


def create_notification_once(session: Session, title: str, message: str, level: str = "info"):
    existing = (
        session.query(Notification)
        .filter(Notification.title == title, Notification.message == message, Notification.is_read.is_(False))
        .first()
    )
    if existing:
        return existing

    notification = Notification(title=title, message=message, level=level)
    session.add(notification)
    return notification


def inventory_rows(session: Session) -> list[InventoryItemRead]:
    rows = []
    ingredients = session.query(Ingredient).order_by(Ingredient.name).all()
    for ingredient in ingredients:
        lots = (
            session.query(InventoryLot)
            .filter(InventoryLot.ingredient_id == ingredient.id, InventoryLot.remaining_quantity > 0)
            .order_by(InventoryLot.expires_at.is_(None), InventoryLot.expires_at, InventoryLot.imported_at)
            .all()
        )
        stock = round(sum(lot.remaining_quantity for lot in lots), 2)
        expires_at = lots[0].expires_at if lots else None
        rows.append(
            InventoryItemRead(
                id=ingredient.id,
                name=ingredient.name,
                unit=ingredient.unit,
                stock=stock,
                low_stock_threshold=ingredient.low_stock_threshold,
                expires_at=expires_at,
            )
        )
    return rows


def refresh_inventory_alerts(session: Session):
    soon = datetime.utcnow() + timedelta(days=7)
    for item in inventory_rows(session):
        if item.stock <= item.low_stock_threshold:
            create_notification_once(
                session,
                "Low stock",
                f"{item.name} is below threshold ({item.stock:g} {item.unit} left).",
                "warning",
            )
        if item.expires_at and item.expires_at <= soon:
            create_notification_once(
                session,
                "Expiry watch",
                f"{item.name} has stock expiring on {item.expires_at.date().isoformat()}.",
                "info",
            )


def deduct_order_stock(order: Order, session: Session):
    existing = session.query(OrderStockDeduction).filter(OrderStockDeduction.order_id == order.id).first()
    if existing:
        return

    needs: dict[int, float] = {}
    items = session.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    ingredients = session.query(Ingredient).all()
    ingredient_by_name = {ingredient.name.lower(): ingredient for ingredient in ingredients}

    for item in items:
        if item.product_id:
            recipe_items = session.query(RecipeItem).filter(RecipeItem.product_id == item.product_id).all()
            for recipe_item in recipe_items:
                needs[recipe_item.ingredient_id] = needs.get(recipe_item.ingredient_id, 0) + recipe_item.quantity * item.quantity
        elif item.custom_details:
            details = item.custom_details.lower()
            for ingredient_name, ingredient in ingredient_by_name.items():
                if ingredient_name in details:
                    needs[ingredient.id] = needs.get(ingredient.id, 0) + 0.1 * item.quantity

    for ingredient_id, needed in needs.items():
        remaining_need = needed
        lots = (
            session.query(InventoryLot)
            .filter(InventoryLot.ingredient_id == ingredient_id, InventoryLot.remaining_quantity > 0)
            .order_by(InventoryLot.expires_at.is_(None), InventoryLot.expires_at, InventoryLot.imported_at)
            .all()
        )
        for lot in lots:
            used = min(lot.remaining_quantity, remaining_need)
            lot.remaining_quantity = round(lot.remaining_quantity - used, 4)
            remaining_need = round(remaining_need - used, 4)
            session.add(lot)
            if remaining_need <= 0:
                break

        if remaining_need > 0:
            ingredient = session.get(Ingredient, ingredient_id)
            create_notification_once(
                session,
                "Inventory shortage",
                f"Order #{order.id} needed {needed:g} {ingredient.unit} of {ingredient.name}, but stock was short by {remaining_need:g}.",
                "warning",
            )

    session.add(OrderStockDeduction(order_id=order.id))
    membership = session.query(Membership).filter(Membership.user_id == order.customer_id).first()
    if membership:
        membership.points += int(order.total_price)
        membership.tier = membership_tier(membership.points)
        session.add(membership)
    refresh_inventory_alerts(session)


def find_table_for_reservation(data: ReservationCreate, session: Session) -> RestaurantTable:
    start = data.reservation_time - timedelta(minutes=90)
    end = data.reservation_time + timedelta(minutes=90)

    if data.table_id:
        table = session.get(RestaurantTable, data.table_id)
        tables = [table] if table else []
    else:
        tables = (
            session.query(RestaurantTable)
            .filter(RestaurantTable.capacity >= data.party_size, RestaurantTable.status == "available")
            .order_by(RestaurantTable.capacity)
            .all()
        )

    for table in tables:
        if not table or table.capacity < data.party_size:
            continue
        conflict = (
            session.query(Reservation)
            .filter(
                Reservation.table_id == table.id,
                Reservation.status.in_(["booked", "seated"]),
                Reservation.reservation_time >= start,
                Reservation.reservation_time <= end,
            )
            .first()
        )
        if not conflict:
            return table

    raise HTTPException(status_code=400, detail="No available table for that party size and time")


@app.get("/")
def health_check():
    return {"message": "The Healthy Lab API is running", "docs": "/docs"}


@app.post("/auth/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: Session = Depends(get_session)):
    email = data.email.strip().lower()
    existing_user = session.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(data.password),
        role="customer",
        phone=data.phone,
        address=data.address,
    )
    session.add(user)
    session.flush()
    session.add(Membership(user_id=user.id, points=0, tier="bronze"))
    session.commit()
    session.refresh(user)

    return build_login_response(user)


@app.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email == data.email.strip().lower()).first()
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
    if data.status == "delivered":
        customer = session.get(User, order.customer_id)
        if customer:
            get_or_create_membership(customer, session)
        deduct_order_stock(order, session)
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
    items = inventory_rows(session)
    low_stock_items = len([item for item in items if item.stock <= item.low_stock_threshold])
    soon = datetime.utcnow() + timedelta(days=7)
    expiring_lots = (
        session.query(func.count(InventoryLot.id))
        .filter(InventoryLot.remaining_quantity > 0, InventoryLot.expires_at.isnot(None), InventoryLot.expires_at <= soon)
        .scalar()
    )
    active_reservations = session.query(func.count(Reservation.id)).filter(Reservation.status.in_(["booked", "seated"])).scalar()
    waiting_queue = session.query(func.count(QueueEntry.id)).filter(QueueEntry.status == "waiting").scalar()
    paid_orders = session.query(func.count(Payment.id)).filter(Payment.status == "paid").scalar()

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
        low_stock_items=low_stock_items,
        expiring_lots=expiring_lots,
        active_reservations=active_reservations,
        waiting_queue=waiting_queue,
        paid_orders=paid_orders,
    )


@app.get("/memberships/me", response_model=MembershipRead)
def my_membership(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    membership = get_or_create_membership(current_user, session)
    session.commit()
    session.refresh(membership)
    return membership


@app.get("/vouchers", response_model=list[VoucherRead])
def list_vouchers(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = session.query(Voucher)
    if current_user.role != "admin":
        query = query.filter(Voucher.status == "active")
    return query.order_by(Voucher.code).all()


@app.get("/staff", response_model=list[StaffProfileRead])
def list_staff(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    return session.query(StaffProfile).order_by(StaffProfile.id).all()


@app.post("/staff", response_model=StaffProfileRead, status_code=status.HTTP_201_CREATED)
def create_staff_profile(
    data: StaffProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    profile = StaffProfile(**data.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@app.get("/suppliers", response_model=list[SupplierRead])
def list_suppliers(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "staff"])
    return session.query(Supplier).order_by(Supplier.name).all()


@app.post("/suppliers", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(
    data: SupplierCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "staff"])
    supplier = Supplier(**data.model_dump())
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier


@app.get("/ingredients", response_model=list[IngredientRead])
def list_ingredients(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "chef", "staff"])
    return session.query(Ingredient).order_by(Ingredient.name).all()


@app.post("/ingredients", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    data: IngredientCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "staff"])
    existing = session.query(Ingredient).filter(Ingredient.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ingredient already exists")
    ingredient = Ingredient(**data.model_dump())
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)
    return ingredient


@app.get("/recipes", response_model=list[RecipeItemRead])
def list_recipe_items(
    product_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "chef", "staff"])
    query = session.query(RecipeItem)
    if product_id is not None:
        query = query.filter(RecipeItem.product_id == product_id)
    return query.order_by(RecipeItem.product_id, RecipeItem.id).all()


@app.post("/recipes", response_model=RecipeItemRead, status_code=status.HTTP_201_CREATED)
def create_recipe_item(
    data: RecipeItemCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "chef"])
    if not session.get(Product, data.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    if not session.get(Ingredient, data.ingredient_id):
        raise HTTPException(status_code=404, detail="Ingredient not found")
    recipe_item = RecipeItem(**data.model_dump())
    session.add(recipe_item)
    session.commit()
    session.refresh(recipe_item)
    return recipe_item


@app.get("/inventory", response_model=list[InventoryItemRead])
def list_inventory(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "chef", "staff"])
    refresh_inventory_alerts(session)
    session.commit()
    return inventory_rows(session)


@app.get("/inventory/lots", response_model=list[InventoryLotRead])
def list_inventory_lots(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "staff"])
    return session.query(InventoryLot).order_by(InventoryLot.expires_at.is_(None), InventoryLot.expires_at, InventoryLot.imported_at).all()


@app.post("/inventory/lots", response_model=InventoryLotRead, status_code=status.HTTP_201_CREATED)
def create_inventory_lot(
    data: InventoryLotCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "staff"])
    if not session.get(Ingredient, data.ingredient_id):
        raise HTTPException(status_code=404, detail="Ingredient not found")
    if data.supplier_id and not session.get(Supplier, data.supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    lot = InventoryLot(**data.model_dump(), remaining_quantity=data.quantity)
    session.add(lot)
    refresh_inventory_alerts(session)
    session.commit()
    session.refresh(lot)
    return lot


@app.get("/tables", response_model=list[RestaurantTableRead])
def list_tables(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "cashier", "staff"])
    return session.query(RestaurantTable).order_by(RestaurantTable.capacity, RestaurantTable.name).all()


@app.post("/tables", response_model=RestaurantTableRead, status_code=status.HTTP_201_CREATED)
def create_table(
    data: RestaurantTableCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin"])
    table = RestaurantTable(**data.model_dump())
    session.add(table)
    session.commit()
    session.refresh(table)
    return table


@app.get("/reservations", response_model=list[ReservationRead])
def list_reservations(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = session.query(Reservation)
    if current_user.role not in ["admin", "cashier", "staff"]:
        query = query.filter(Reservation.user_id == current_user.id)
    return query.order_by(Reservation.reservation_time.desc()).all()


@app.post("/reservations", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "cashier", "staff"] and data.status != "booked":
        raise HTTPException(status_code=403, detail="Customers can only create booked reservations")
    if data.status not in RESERVATION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid reservation status")

    table = find_table_for_reservation(data, session)
    reservation = Reservation(
        user_id=current_user.id,
        table_id=table.id,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        party_size=data.party_size,
        reservation_time=data.reservation_time,
        status=data.status,
        note=data.note,
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@app.put("/reservations/{reservation_id}/status", response_model=ReservationRead)
def update_reservation_status(
    reservation_id: int,
    data: ReservationStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if current_user.role not in ["admin", "cashier", "staff"] and reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own reservation")
    if current_user.role == "customer" and data.status != "cancelled":
        raise HTTPException(status_code=403, detail="Customers can only cancel reservations")
    reservation.status = data.status
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@app.get("/queue", response_model=list[QueueEntryRead])
def list_queue_entries(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = session.query(QueueEntry)
    if current_user.role not in ["admin", "cashier", "staff"]:
        query = query.filter(QueueEntry.user_id == current_user.id)
    return query.order_by(QueueEntry.created_at.desc()).all()


@app.post("/queue", response_model=QueueEntryRead, status_code=status.HTTP_201_CREATED)
def create_queue_entry(
    data: QueueEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "cashier", "staff"] and data.status != "waiting":
        raise HTTPException(status_code=403, detail="Customers can only join the waiting queue")
    if data.status not in QUEUE_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid queue status")
    open_entry = (
        session.query(QueueEntry)
        .filter(QueueEntry.user_id == current_user.id, QueueEntry.status.in_(["waiting", "called"]))
        .first()
    )
    if open_entry and current_user.role == "customer":
        raise HTTPException(status_code=400, detail="You already have an active queue entry")
    entry = QueueEntry(user_id=current_user.id, **data.model_dump())
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@app.put("/queue/{entry_id}/status", response_model=QueueEntryRead)
def update_queue_status(
    entry_id: int,
    data: QueueStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "cashier", "staff"])
    entry = session.get(QueueEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    allowed_transitions = {
        "waiting": ["called", "cancelled"],
        "called": ["seated", "cancelled"],
        "seated": [],
        "cancelled": [],
    }
    if data.status not in allowed_transitions.get(entry.status, []):
        raise HTTPException(status_code=400, detail="Invalid queue status flow")
    entry.status = data.status
    if data.wait_minutes is not None:
        entry.wait_minutes = data.wait_minutes
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@app.get("/payments", response_model=list[PaymentRead])
def list_payments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "cashier"])
    return session.query(Payment).order_by(Payment.created_at.desc()).all()


@app.post("/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    data: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order = session.get(Order, data.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only pay your own orders")
    if current_user.role not in ["customer", "admin", "cashier"]:
        raise HTTPException(status_code=403, detail="This role cannot create payments")
    payment = Payment(**data.model_dump())
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@app.get("/notifications", response_model=list[NotificationRead])
def list_notifications(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "staff", "chef"])
    refresh_inventory_alerts(session)
    session.commit()
    return session.query(Notification).order_by(Notification.created_at.desc()).limit(50).all()
