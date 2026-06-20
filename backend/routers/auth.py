from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import create_token, get_current_user, hash_password, verify_password
from database import get_session
from models import Membership, User
from schemas import LoginRequest, LoginResponse, UserCreate, UserRead


router = APIRouter()


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


@router.post("/auth/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
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


@router.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email == data.email.strip().lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return build_login_response(user)


@router.get("/auth/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
