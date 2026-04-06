from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.user import UserCreate, UserOut, UserUpdateRole, UserUpdateStatus
from app.services.user_service import user_service
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[UserOut])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await user_service.get_all_users(db)

@router.post("/", response_model=UserOut, status_code=201)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await user_service.create_user(data, db)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await user_service.get_user_by_id(user_id, db)

@router.patch("/{user_id}/role", response_model=UserOut)
async def update_role(
    user_id: str,
    data: UserUpdateRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await user_service.update_role(user_id, data, db)

@router.patch("/{user_id}/status", response_model=UserOut)
async def update_status(
    user_id: str,
    data: UserUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await user_service.update_status(user_id, data, db)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await user_service.delete_user(user_id, db)