# Rec Lab Project

A full-stack application with FastAPI backend and Next.js frontend, featuring outdoor route recommendations with gamification and story generation.

## Tech Stack

**Backend:**

- FastAPI (Python 3.11+)
- SQLAlchemy with async SQLite
- Alembic for database migrations

**Frontend:**

- Next.js 16 with React 19
- TypeScript
- Tailwind CSS

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (pnpm or npm)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

### 2. Frontend Setup

```bash
cd frontend
pnpm install  # or npm install
pnpm run build  # or npm run build
```

### 3. Run the Application

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Access the application at:

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz

Or use the dev script:

```bash
./scripts/dev.sh
```

## Development Workflow

1. **Set up environment** (first time only)

   ```bash
   # Backend
   cd backend && python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   alembic upgrade head

   # Frontend
   cd ../frontend && pnpm install
   ```

2. **Develop backend**

   - Edit code in `backend/app/`
   - Create migrations: `alembic revision --autogenerate -m "description"`
   - Apply migrations: `alembic upgrade head`

3. **Develop frontend**

   ```bash
   cd frontend
   pnpm run dev  # Runs on http://localhost:3000
   ```

4. **Build and serve together**

   ```bash
   # Build frontend
   cd frontend && pnpm run build

   # Run backend (serves both API and frontend)
   cd ../backend && source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/     # API endpoints
│   │   ├── models/     # Database models
│   │   ├── services/   # Business logic
│   │   ├── database.py # DB connection
│   │   └── main.py     # FastAPI app
│   ├── alembic/        # Database migrations
│   ├── data/           # SQLite database
│   ├── scripts/        # Utility scripts
│   └── requirements.txt
├── frontend/
│   ├── app/            # Next.js app directory
│   ├── components/     # React components
│   └── out/            # Build output (generated)
└── scripts/
    └── dev.sh          # Development server script
```

## Database

- **Default location**: `backend/data/app.db`
- **Migrations**: Managed with Alembic
  ```bash
  alembic revision --autogenerate -m "description"
  alembic upgrade head
  alembic downgrade -1
  ```
- **Environment**: Copy `backend/env.example` to `backend/.env` to customize `DATABASE_URL`

## Scripts

- `backend/scripts/seed_db.py` - Seed database with demo data
- `backend/scripts/test_models.py` - Test database models
- `scripts/dev.sh` - Start development server

## Environment Variables

See `backend/env.example` for available configuration options. Create `backend/.env` to override defaults.
