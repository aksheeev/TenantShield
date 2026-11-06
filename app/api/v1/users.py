import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_scoped_db, require_role
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_scoped_db),
    admin: CurrentUser = Depends(require_role("admin")),
):
    """Admin adds a user to their OWN tenant. Tenant comes from the JWT, never from the request."""
    user = User(
        id=uuid.uuid4(),
        tenant_id=uuid.UUID(admin.tenant_id),
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Generic message on purpose: don't reveal which emails already exist.
        raise HTTPException(status_code=400, detail="Could not create user") from None
    return user


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_scoped_db),
    _: CurrentUser = Depends(require_role("admin")),
):
    # No tenant filter on purpose: RLS scopes this query.
    return db.execute(select(User)).scalars().all()