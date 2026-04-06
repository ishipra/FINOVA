from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_
from app.models.transaction import Transaction, TransactionType
from app.schemas.dashboard import DashboardSummary, CategorySummary, MonthlyTrend
from datetime import datetime, timezone

class DashboardService:

    async def get_summary(self, db: AsyncSession) -> DashboardSummary:

        # Total income, total expense, count — all in one query
        result = await db.execute(
            select(
                func.coalesce(
                    func.sum(
                        case((Transaction.type == TransactionType.income, Transaction.amount), else_=0)
                    ), 0
                ).label("total_income"),
                func.coalesce(
                    func.sum(
                        case((Transaction.type == TransactionType.expense, Transaction.amount), else_=0)
                    ), 0
                ).label("total_expense"),
                func.count(Transaction.id).label("total_transactions")
            ).where(Transaction.is_deleted == False)
        )
        row = result.one()
        total_income = float(row.total_income)
        total_expense = float(row.total_expense)
        total_transactions = row.total_transactions
        net_balance = total_income - total_expense

        # Category breakdown
        cat_result = await db.execute(
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total")
            )
            .where(Transaction.is_deleted == False)
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
        )
        category_breakdown = [
            CategorySummary(category=row.category, total=float(row.total))
            for row in cat_result.all()
        ]

        # Recent 5 transactions
        recent_result = await db.execute(
            select(Transaction)
            .where(Transaction.is_deleted == False)
            .order_by(Transaction.date.desc())
            .limit(5)
        )
        recent = recent_result.scalars().all()
        recent_transactions = [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.type,
                "category": t.category,
                "date": t.date.isoformat(),
                "notes": t.notes
            }
            for t in recent
        ]

        return DashboardSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_balance=net_balance,
            total_transactions=total_transactions,
            category_breakdown=category_breakdown,
            recent_transactions=recent_transactions
        )

    async def get_monthly_trends(self, db: AsyncSession):
        # Get all non-deleted transactions
        result = await db.execute(
            select(Transaction)
            .where(Transaction.is_deleted == False)
            .order_by(Transaction.date.asc())
        )
        transactions = result.scalars().all()

        # Group by month manually (SQLite doesn't support date_trunc)
        monthly = {}
        for t in transactions:
            month_key = t.date.strftime("%Y-%m")
            if month_key not in monthly:
                monthly[month_key] = {"income": 0.0, "expense": 0.0}
            if t.type == TransactionType.income:
                monthly[month_key]["income"] += t.amount
            else:
                monthly[month_key]["expense"] += t.amount

        return [
            MonthlyTrend(
                month=month,
                income=round(data["income"], 2),
                expense=round(data["expense"], 2)
            )
            for month, data in sorted(monthly.items())
        ]

    async def get_category_totals(self, db: AsyncSession):
        result = await db.execute(
            select(
                Transaction.category,
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
                func.count(Transaction.id).label("count")
            )
            .where(Transaction.is_deleted == False)
            .group_by(Transaction.category, Transaction.type)
            .order_by(func.sum(Transaction.amount).desc())
        )
        return [
            {
                "category": row.category,
                "type": row.type,
                "total": round(float(row.total), 2),
                "count": row.count
            }
            for row in result.all()
        ]

dashboard_service = DashboardService()