from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from routers.admin import router as admin_router
from routers.auth import router as auth_router
from routers.inventory import router as inventory_router
from routers.notifications import router as notifications_router
from routers.orders import router as orders_router
from routers.payments import router as payments_router
from routers.products import router as products_router
from routers.restaurant import router as restaurant_router

# Compatibility re-exports for scripts/tests that still import handlers/helpers from main.py.
from database import get_session
from routers.admin import admin_summary, create_staff_profile, list_staff, list_users, list_vouchers, my_membership
from routers.auth import build_login_response, login, me, register
from routers.inventory import (
    create_ingredient,
    create_inventory_lot,
    create_recipe_item,
    create_supplier,
    list_ingredients,
    list_inventory,
    list_inventory_lots,
    list_recipe_items,
    list_suppliers,
)
from routers.notifications import list_notifications
from routers.orders import create_order, get_order, list_food_lab_options, list_orders, my_orders, preview_food_lab_item, update_order_status
from routers.payments import create_payment, list_payments, update_payment_status
from routers.products import create_product, get_product, list_products, update_product
from routers.restaurant import (
    call_next_queue_entry,
    complete_reservation,
    create_queue_entry,
    create_reservation,
    create_table,
    list_queue_entries,
    list_reservations,
    list_tables,
    seat_queue_entry,
    update_queue_status,
    update_reservation_status,
)
from services.inventory import deduct_order_stock, inventory_rows, refresh_inventory_alerts
from services.memberships import get_or_create_membership, membership_tier
from services.notifications import create_notification_once
from services.orders import (
    CUSTOM_ITEM_PRICE_ROLES,
    ORDER_STATUS_TRANSITIONS,
    build_order,
    build_order_read,
    can_update_order_status,
    money,
    prices_match,
)
from services.payments import PAYMENT_RECONCILE_ROLES, validate_payment, validate_payment_status_update
from services.reservations import find_table_for_reservation


app = FastAPI(title="The Healthy Lab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def health_check():
    return {"message": "The Healthy Lab API is running", "docs": "/docs"}

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(admin_router)
app.include_router(inventory_router)
app.include_router(restaurant_router)
app.include_router(payments_router)
app.include_router(notifications_router)
