# Rec Lab Scaffold

This repository provides a starter scaffold for the Rec Lab project with FastAPI backend and SQLAlchemy ORM.

## Structure

- `backend/`: FastAPI application with SQLAlchemy ORM connecting to Supabase PostgreSQL.
- `frontend/`: Placeholder for future React or Next.js application.
- `docs/`: Documentation and design notes.
- `scripts/`: Utility scripts for local development and automation.

## Backend Setup

The backend uses [FastAPI](https://fastapi.tiangolo.com/) with SQLAlchemy ORM for database operations, connecting to Supabase (PostgreSQL).

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

Create a `.env` file in `backend/` with the following keys:

```env
# Database Configuration (Supabase PostgreSQL)
# Get this from your Supabase project: Settings -> Database -> Connection string
# Format: postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.your_project.supabase.co:5432/postgres
```

**How to get your Supabase DATABASE_URL:**

1. Go to your Supabase project dashboard
2. Navigate to Settings → Database
3. Find the "Connection string" section
4. Select "URI" format
5. Replace `[YOUR-PASSWORD]` with your database password
6. The format should be: `postgresql+asyncpg://postgres:[password]@[host]:5432/postgres`

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

The backend uses SQLAlchemy ORM with async support for database operations. Database models are defined in `app/models/`, and database sessions are managed through dependency injection in FastAPI routes.

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

1. Configure environment variables in `backend/.env` (especially `DATABASE_URL`).
2. Create a virtual environment and install dependencies with pip.
3. Run database migrations: `alembic upgrade head`
4. Run `uvicorn` to start the API server.
5. Add frontend implementation under `frontend/`.
6. Create new database models in `app/models/` and generate migrations as needed.
