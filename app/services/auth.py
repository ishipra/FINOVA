from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User, RoleEnum
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
import uuid

class AuthService:

    async def register(self, data: UserCreate, db: AsyncSession) -> User:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

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

    async def login(self, data: LoginRequest, db: AsyncSession) -> TokenResponse:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        token = create_access_token({"sub": user.id, "role": user.role})

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        )

auth_service = AuthService()