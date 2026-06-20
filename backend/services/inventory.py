from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models import Ingredient, InventoryLot, Order, OrderItem, OrderStockDeduction, RecipeItem
from schemas import InventoryItemRead
from services.notifications import create_notification_once
from services.food_lab import parse_custom_data


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
            continue
        if item.custom_data:
            handled_custom_data = False
            custom_data = parse_custom_data(item.custom_data)
            if custom_data and custom_data.get("builder") == "food_lab":
                handled_custom_data = True
                for need in custom_data.get("inventory_needs", []):
                    ingredient_name = str(need.get("ingredient", "")).lower()
                    ingredient = ingredient_by_name.get(ingredient_name)
                    if not ingredient:
                        continue
                    quantity = float(need.get("quantity", 0))
                    if quantity > 0:
                        needs[ingredient.id] = needs.get(ingredient.id, 0) + quantity * item.quantity
            if handled_custom_data:
                continue
        if item.custom_details:
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
    refresh_inventory_alerts(session)
