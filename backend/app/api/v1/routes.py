# routes api

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import RecommendationRequest, RecommendationResponse
from app.database import get_db
from app.services.routes_service import RoutesService

router = APIRouter(tags=["routes"])


# ---------------------------------------------------------------------------
# Sync request/response schemas (For internal use only)
# ---------------------------------------------------------------------------

class SyncRoutesRequest(BaseModel):
    """
    Synchronise route data from Outdooractive to the local database
    """
    region: Optional[str] = None
    activity_type: Optional[str] = None  
    limit: int = Field(default=200, le=1000)


class SyncRoutesResponse(BaseModel):
    synced: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/routes/sync", response_model=SyncRoutesResponse)
async def sync_routes(
    payload: SyncRoutesRequest,
    db: AsyncSession = Depends(get_db),
) -> SyncRoutesResponse:
    """
    Management:Synchronise route data from Outdooractive to the local database
    """
    service = RoutesService(db)
    count = await service.sync_routes_from_outdooractive(
        region=payload.region,
        activity_type=payload.activity_type,
        limit=payload.limit,
    )
    return SyncRoutesResponse(synced=count)


@router.post("/routes/recommend", response_model=RecommendationResponse)
async def recommend_routes_endpoint(
    payload: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """
    Query the local database
    """
    service = RoutesService(db)
    return await service.recommend_routes(req=payload, limit=50)
