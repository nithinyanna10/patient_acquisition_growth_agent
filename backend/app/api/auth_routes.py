from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.auth.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import UserORM
from app.schemas import TokenResponse, UserCreate, UserResponse
from app.services.audit_service import write_audit_log

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)


@router.post("/users", response_model=UserResponse)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: UserORM = Depends(require_roles({"admin"})),
):
    existing = db.query(UserORM).filter(UserORM.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = UserORM(
        id=payload.id,
        email=str(payload.email),
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def me(current_user: UserORM = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    users = db.query(UserORM).all()
    write_audit_log(db, current_user, "LIST_USERS", "users", None)
    return users
