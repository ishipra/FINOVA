from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from typing import Optional
from datetime import datetime
import uuid

class TransactionService:

    async def create(self, data: TransactionCreate, user_id: str, db: AsyncSession):
        transaction = Transaction(
            id=str(uuid.uuid4()),
            amount=data.amount,
            type=data.type,
            category=data.category,
            date=data.date,
            notes=data.notes,
            user_id=user_id
        )
        db.add(transaction)
        await db.flush()
        return transaction

    async def get_all(
        self,
        db: AsyncSession,
        type: Optional[TransactionType] = None,
        category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ):
        filters = [Transaction.is_deleted == False]

        if type:
            filters.append(Transaction.type == type)
        if category:
            filters.append(Transaction.category.ilike(f"%{category}%"))
        if date_from:
            filters.append(Transaction.date >= date_from)
        if date_to:
            filters.append(Transaction.date <= date_to)

        result = await db.execute(
            select(Transaction)
            .where(and_(*filters))
            .order_by(Transaction.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_id(self, transaction_id: str, db: AsyncSession):
        result = await db.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.is_deleted == False
            )
        )
        transaction = result.scalar_one_or_none()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction

    async def update(self, transaction_id: str, data: TransactionUpdate, db: AsyncSession):
        transaction = await self.get_by_id(transaction_id, db)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)
        await db.flush()
        return transaction

    async def soft_delete(self, transaction_id: str, db: AsyncSession):
        transaction = await self.get_by_id(transaction_id, db)
        transaction.is_deleted = True
        await db.flush()
        return {"message": "Transaction deleted successfully"}

transaction_service = TransactionService()