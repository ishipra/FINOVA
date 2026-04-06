from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.user import User, RoleEnum
from app.schemas.user import UserCreate, UserUpdateRole, UserUpdateStatus
from app.core.security import hash_password
import uuid

class UserService:

    async def get_all_users(self, db: AsyncSession):
        result = await db.execute(select(User))
        return result.scalars().all()

    async def get_user_by_id(self, user_id: str, db: AsyncSession):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def create_user(self, data: UserCreate, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=data.role
        )
        db.add(user)
        await db.flush()
        return user

    async def update_role(self, user_id: str, data: UserUpdateRole, db: AsyncSession):
        user = await self.get_user_by_id(user_id, db)
        user.role = data.role
        await db.flush()
        return user

    async def update_status(self, user_id: str, data: UserUpdateStatus, db: AsyncSession):
        user = await self.get_user_by_id(user_id, db)
        user.is_active = data.is_active
        await db.flush()
        return user

    async def delete_user(self, user_id: str, db: AsyncSession):
        user = await self.get_user_by_id(user_id, db)
        await db.delete(user)
        await db.flush()
        return {"message": "User deleted successfully"}

user_service = UserService()