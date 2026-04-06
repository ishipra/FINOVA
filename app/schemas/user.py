from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import RoleEnum

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: RoleEnum = RoleEnum.viewer

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class UserUpdateRole(BaseModel):
    role: RoleEnum

class UserUpdateStatus(BaseModel):
    is_active: bool