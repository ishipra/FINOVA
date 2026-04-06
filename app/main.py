from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.routers import auth, users, transactions, dashboard
from app.core.exceptions import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    global_exception_handler
)

app = FastAPI(
    title="Finance Dashboard API",
    description="A role-based finance management backend built with FastAPI and SQLite",
    version="1.0.0",
    contact={
        "name": "Finance Dashboard",
    },
    license_info={
        "name": "MIT"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.on_event("startup")
async def startup():
    from app.database import engine, Base
    import app.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)

@app.get("/", tags=["Health"])
async def root():
    return {"message": "Finance Dashboard API is running"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}