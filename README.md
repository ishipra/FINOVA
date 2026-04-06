# Finance Dashboard API

A production-structured REST API backend for a finance dashboard system, built with FastAPI and SQLite. Supports role-based access control, financial record management, and aggregated dashboard analytics.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | SQLite (via aiosqlite) |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | JWT (python-jose) |
| Password Hashing | bcrypt (passlib) |
| Validation | Pydantic v2 |
| Server | Uvicorn |

---

## Project Structure

---

## Setup Instructions

### 1. Clone and create virtual environment
```bash
git clone <your-repo-url>
cd finance_dashboard
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install fastapi uvicorn[standard] sqlalchemy alembic pydantic pydantic-settings "python-jose[cryptography]" "passlib[bcrypt]" python-multipart aiosqlite email-validator bcrypt==4.0.1 greenlet
```

### 3. Create `.env` file
```env
DATABASE_URL=sqlite+aiosqlite:///./finance.db
SECRET_KEY=supersecretkey123changethistosomethinglong
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```

The database and tables are created automatically on first startup.

### 5. Open API docs

---

## Roles and Permissions

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| Login / Register | yes | yes | yes |
| View transactions | yes | yes | yes |
| View dashboard summary | yes | yes | yes |
| View monthly trends | no | yes | yes |
| Create transactions | no | yes | yes |
| Update transactions | no | yes | yes |
| Delete transactions (soft) | no | no | yes |
| Manage users | no | no | yes |
| Assign roles | no | no | yes |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Register a new user |
| POST | /auth/login | Login and receive JWT token |

### Users (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | /users/me | Get current logged in user |
| GET | /users/ | List all users |
| POST | /users/ | Create a user |
| GET | /users/{id} | Get user by ID |
| PATCH | /users/{id}/role | Update user role |
| PATCH | /users/{id}/status | Activate or deactivate user |
| DELETE | /users/{id} | Delete a user |

### Transactions
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | /transactions/ | All roles | List with filters |
| POST | /transactions/ | Analyst, Admin | Create a record |
| GET | /transactions/{id} | All roles | Get by ID |
| PATCH | /transactions/{id} | Analyst, Admin | Update a record |
| DELETE | /transactions/{id} | Admin only | Soft delete |

### Dashboard
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | /dashboard/summary | All roles | Total income, expense, balance |
| GET | /dashboard/trends | Analyst, Admin | Monthly income vs expense |
| GET | /dashboard/categories | All roles | Per-category breakdown |

---

## Sample Test Users
```json
{ "email": "admin@finance.com", "password": "admin123", "role": "admin" }
{ "email": "analyst@finance.com", "password": "analyst123", "role": "analyst" }
{ "email": "viewer@finance.com", "password": "viewer123", "role": "viewer" }
```

---

## Assumptions and Design Decisions

- **SQLite over PostgreSQL** — Used SQLite with aiosqlite for zero-configuration local development. The `DATABASE_URL` in `.env` can be swapped to a PostgreSQL URL with no code changes required.
- **Soft deletes** — Transactions are never physically deleted. A `is_deleted` flag is set to `true`, preserving data integrity and audit history.
- **UUID primary keys** — All records use UUIDs instead of auto-increment integers for better security and future scalability.
- **JWT authentication** — Stateless token-based auth. Tokens expire after 30 minutes by default, configurable via `.env`.
- **Role hierarchy** — Three roles: viewer (read only), analyst (read and write), admin (full access including user management).
- **Pagination** — Transaction listing supports `skip` and `limit` query parameters for pagination.
- **Input validation** — All inputs are validated via Pydantic v2. Amounts must be positive, categories cannot be empty, emails must be valid format.

---

## Key Design Patterns

- **Service layer pattern** — Business logic lives in `services/`, not in route handlers. Routes only call services.
- **Dependency injection** — FastAPI's `Depends()` system is used for auth, RBAC, and DB sessions throughout.
- **Async throughout** — All database operations are fully async using SQLAlchemy's async engine for better performance.