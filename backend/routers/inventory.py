from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user, require_role
from database import get_session
from models import Ingredient, InventoryLot, Product, RecipeItem, Supplier, User
from schemas import (
    IngredientCreate,
    IngredientRead,
    InventoryItemRead,
    InventoryLotCreate,
    InventoryLotRead,
    RecipeItemCreate,
    RecipeItemRead,
    SupplierCreate,
    SupplierRead,
)
from services.inventory import inventory_rows, refresh_inventory_alerts


router = APIRouter()


@router.get("/suppliers", response_model=list[SupplierRead])
def list_suppliers(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "staff"])
    return session.query(Supplier).order_by(Supplier.name).all()


@router.post("/suppliers", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/ingredients", response_model=list[IngredientRead])
def list_ingredients(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "chef", "staff"])
    return session.query(Ingredient).order_by(Ingredient.name).all()


@router.post("/ingredients", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/recipes", response_model=list[RecipeItemRead])
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


@router.post("/recipes", response_model=RecipeItemRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/inventory", response_model=list[InventoryItemRead])
def list_inventory(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "chef", "staff"])
    refresh_inventory_alerts(session)
    session.commit()
    return inventory_rows(session)


@router.get("/inventory/lots", response_model=list[InventoryLotRead])
def list_inventory_lots(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, ["admin", "staff"])
    return session.query(InventoryLot).order_by(InventoryLot.expires_at.is_(None), InventoryLot.expires_at, InventoryLot.imported_at).all()


@router.post("/inventory/lots", response_model=InventoryLotRead, status_code=status.HTTP_201_CREATED)
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
