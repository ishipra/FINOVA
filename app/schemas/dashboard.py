from pydantic import BaseModel
from typing import List

class CategorySummary(BaseModel):
    category: str
    total: float

class MonthlyTrend(BaseModel):
    month: str
    income: float
    expense: float

class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    total_transactions: int
    category_breakdown: List[CategorySummary]
    recent_transactions: list