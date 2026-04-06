from sqlalchemy import Column, String, Boolean, Enum, DateTime
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum
from datetime import datetime, timezone

class RoleEnum(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.viewer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    transactions = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")