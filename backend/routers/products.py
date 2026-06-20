from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import get_current_user, get_optional_current_user, require_role
from database import get_session
from models import Product, User
from pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, apply_pagination
from schemas import ProductCreate, ProductRead, ProductUpdate


router = APIRouter()


@router.get("/products", response_model=list[ProductRead])
def list_products(
    include_disabled: bool = False,
    session: Session = Depends(get_session),
    current_user: User | None = Depends(get_optional_current_user),
    category: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
):
    query = session.query(Product)
    if include_disabled:
        require_role(current_user, ["admin"])
    else:
        query = query.filter(Product.is_available.is_(True))
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())
    return apply_pagination(query.order_by(Product.id), limit, offset).all()


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product or not product.is_available:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
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


@router.put("/products/{product_id}", response_model=ProductRead)
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
