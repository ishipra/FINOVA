from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_service.register(data, db)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(data, db)