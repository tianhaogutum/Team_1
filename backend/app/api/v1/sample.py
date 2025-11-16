from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db

router = APIRouter(prefix="/sample", tags=["sample"])


class SampleResponse(BaseModel):
    message: str
    status: str = "success"
    db_connected: bool = True


@router.get("/", response_model=SampleResponse)
async def sample_endpoint(
    db: AsyncSession = Depends(get_db),
) -> SampleResponse:
    """
    A simple sample endpoint to demonstrate the API structure with database connection.
    """
    # Test database connection
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        db_connected = True
    except Exception:
        db_connected = False
    
    return SampleResponse(
        message="Hello from FastAPI with SQLAlchemy!",
        db_connected=db_connected,
    )

