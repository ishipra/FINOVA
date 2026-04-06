from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from app.services.transaction_service import transaction_service
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_analyst_or_admin, require_admin
from app.models.user import User
from app.models.transaction import TransactionType

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/", response_model=List[TransactionOut])
async def get_transactions(
    type: Optional[TransactionType] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await transaction_service.get_all(db, type, category, date_from, date_to, skip, limit)

@router.post("/", response_model=TransactionOut, status_code=201)
async def create_transaction(
    data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)
):
    return await transaction_service.create(data, current_user.id, db)

@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await transaction_service.get_by_id(transaction_id, db)

@router.patch("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)
):
    return await transaction_service.update(transaction_id, data, db)

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await transaction_service.soft_delete(transaction_id, db)