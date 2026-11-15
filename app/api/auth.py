from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, issue_access_token, verify_password
from app.dependencies import CurrentUser, DbSession
from app.models import User
from app.schemas import LoginIn, ProfilePatch, RegisterIn, TokenOut, UserOut

router = APIRouter(tags=["Auth & Users"])


@router.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: DbSession):
    email = str(payload.email).strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=email, password_hash=hash_password(payload.password), full_name=payload.full_name, phone=payload.phone)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from None
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: DbSession):
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token, lifetime = issue_access_token(user.id)
    return TokenOut(access_token=token, expires_in=lifetime)


@router.get("/users/me", response_model=UserOut)
def get_profile(user: CurrentUser):
    return user


@router.patch("/users/me", response_model=UserOut)
def update_profile(payload: ProfilePatch, user: CurrentUser, db: DbSession):
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "full_name" and value is None:
            raise HTTPException(status_code=422, detail="full_name cannot be null")
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
