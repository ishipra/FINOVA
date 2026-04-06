from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.dashboard_service import dashboard_service
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_analyst_or_admin
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await dashboard_service.get_summary(db)

@router.get("/trends")
async def get_monthly_trends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)
):
    return await dashboard_service.get_monthly_trends(db)

@router.get("/categories")
async def get_category_totals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await dashboard_service.get_category_totals(db)