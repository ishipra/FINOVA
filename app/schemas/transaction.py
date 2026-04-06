from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionType

class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: datetime
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("category")
    @classmethod
    def category_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Category cannot be empty")
        return v.strip()

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

class TransactionOut(BaseModel):
    id: str
    amount: float
    type: TransactionType
    category: str
    date: datetime
    notes: Optional[str]
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}