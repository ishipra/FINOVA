from sqlalchemy import Column, String, Float, Enum, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum
from datetime import datetime, timezone

class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(String(100), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)  # soft delete
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user_id = Column(TEXT, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="transactions")