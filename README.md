# Rec Lab Scaffold

This repository provides a starter scaffold for the Rec Lab project with FastAPI backend and SQLAlchemy ORM.

## Structure

- `backend/`: FastAPI application with SQLAlchemy ORM backed by a local SQLite database.
- `frontend/`: Placeholder for future React or Next.js application.
- `docs/`: Documentation and design notes.
- `scripts/`: Utility scripts for local development and automation.

## Backend Setup

The backend uses [FastAPI](https://fastapi.tiangolo.com/) with SQLAlchemy ORM for database operations, persisting data locally via SQLite (the Outdooractive data is stored in `backend/data/app.db` by default).

### Prerequisites

- Python 3.11+

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

For development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Running the API

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Environment Variables

The API works out-of-the-box with SQLite — no configuration required. A database file is automatically created at `backend/data/app.db`.

If you want to change the database location (or point to PostgreSQL/another engine), copy `backend/env.template` to `backend/.env` and update the connection string:

```env
DATABASE_URL=sqlite+aiosqlite:///absolute/path/to/backend/data/app.db
```

Any SQLAlchemy-compatible async URL (e.g., `postgresql+asyncpg://...`) is supported if the corresponding driver is installed.

### Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Frontend Placeholder

The frontend stack is yet to be finalized. Use the `frontend/` directory to experiment with React or Next.js. Add a framework-specific README or setup script once the choice is confirmed.

## Database Integration

The backend uses SQLAlchemy ORM with async support for database operations. Database models are defined in `app/models/`, and database sessions are managed through dependency injection in FastAPI routes. Outdooractive data (or any other upstream source) should be ingested into the local SQLite database before serving via the API.

**Example usage in a route:**

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    # Use db session here
    result = await db.execute(text("SELECT * FROM items"))
    return result.fetchall()
```

## Development Workflow

1. (Optional) Configure environment variables in `backend/.env` if you need a custom `DATABASE_URL`.
2. Create a virtual environment and install dependencies with pip.
3. Run database migrations: `alembic upgrade head`
4. Run `uvicorn` to start the API server.
5. Add frontend implementation under `frontend/`.
6. Create new database models in `app/models/` and generate migrations as needed.
