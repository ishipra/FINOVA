import asyncio
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User, RoleEnum
from app.models.transaction import Transaction, TransactionType
from app.core.security import hash_password
import uuid
from datetime import datetime

async def seed():
    async with engine.begin() as conn:
        import app.models
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "admin@finance.com"))
        if result.scalar_one_or_none():
            print("Already seeded. Skipping.")
            return

        # Create users
        admin = User(id=str(uuid.uuid4()), email="admin@finance.com", full_name="Admin User", hashed_password=hash_password("admin123"), role=RoleEnum.admin)
        analyst = User(id=str(uuid.uuid4()), email="analyst@finance.com", full_name="Analyst User", hashed_password=hash_password("analyst123"), role=RoleEnum.analyst)
        viewer = User(id=str(uuid.uuid4()), email="viewer@finance.com", full_name="Viewer User", hashed_password=hash_password("viewer123"), role=RoleEnum.viewer)
        db.add_all([admin, analyst, viewer])
        await db.flush()

        # Create transactions
        transactions = [
            Transaction(id=str(uuid.uuid4()), amount=75000, type=TransactionType.income, category="Salary", date=datetime(2024, 1, 1), notes="January salary", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=25000, type=TransactionType.income, category="Freelance", date=datetime(2024, 1, 10), notes="Web project", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=12000, type=TransactionType.expense, category="Rent", date=datetime(2024, 1, 5), notes="Monthly rent", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=4500, type=TransactionType.expense, category="Food", date=datetime(2024, 1, 15), notes="Groceries", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=2000, type=TransactionType.expense, category="Transport", date=datetime(2024, 1, 20), notes="Commute", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=75000, type=TransactionType.income, category="Salary", date=datetime(2024, 2, 1), notes="February salary", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=8000, type=TransactionType.income, category="Freelance", date=datetime(2024, 2, 14), notes="Logo design", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=12000, type=TransactionType.expense, category="Rent", date=datetime(2024, 2, 5), notes="Monthly rent", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=3200, type=TransactionType.expense, category="Food", date=datetime(2024, 2, 18), notes="Dining out", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=15000, type=TransactionType.expense, category="Shopping", date=datetime(2024, 2, 22), notes="Electronics", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=75000, type=TransactionType.income, category="Salary", date=datetime(2024, 3, 1), notes="March salary", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=5000, type=TransactionType.expense, category="Utilities", date=datetime(2024, 3, 10), notes="Electricity and water", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=12000, type=TransactionType.expense, category="Rent", date=datetime(2024, 3, 5), notes="Monthly rent", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=30000, type=TransactionType.income, category="Bonus", date=datetime(2024, 3, 25), notes="Performance bonus", user_id=admin.id),
            Transaction(id=str(uuid.uuid4()), amount=9500, type=TransactionType.expense, category="Healthcare", date=datetime(2024, 3, 18), notes="Medical checkup", user_id=admin.id),
        ]
        db.add_all(transactions)
        await db.commit()
        print("Seeded successfully!")
        print("Admin:    admin@finance.com / admin123")
        print("Analyst:  analyst@finance.com / analyst123")
        print("Viewer:   viewer@finance.com / viewer123")

asyncio.run(seed())