# Return recommended results

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import RecommendationRequest, RecommendationResponse, RouteResponse
from app.models.entities import Route
from app.services.outdooractive_client import OutdooractiveClient
from app.services.routes_repository import RouteRepository
from app.services.recommend_routes import recommend_routes


class RoutesService:
    """
    Orchestrates Outdooractive sync + local DB recommendation.
    """

    def __init__(
        self,
        db: AsyncSession,
        client: OutdooractiveClient | None = None,
    ) -> None:
        self.db = db
        self.client = client or OutdooractiveClient()
        self.repo = RouteRepository(db)

    # ------------------------------------------------------------------
    # Sync from Outdooractive into local DB
    # ------------------------------------------------------------------

    async def sync_routes_from_outdooractive(
        self,
        region: Optional[str] = None,
        activity_type: Optional[str] = None,
        limit: int = 200,
    ) -> int:
        """
        Fetch routes from Outdooractive and upsert into our local DB.
        """
        items = await self.client.fetch_routes(
            region=region,
            activity_type=activity_type,
            limit=limit,
        )
        count = await self.repo.upsert_from_outdooractive(items)
        return count

    # ------------------------------------------------------------------
    # Recommend from local DB
    # ------------------------------------------------------------------

    async def recommend_routes(
        self,
        req: RecommendationRequest,
        limit: int = 50,
    ) -> RecommendationResponse:
        """
        Only talks to our own database, uses the recommendation algorithm.
        """
        candidates: list[Route] = await self.repo.list_routes_for_recommendation(
            activity_type=req.activity_type,
            limit=limit,
        )

        ranked: list[Route] = recommend_routes(
            routes=candidates,
            activity_type=req.activity_type,
        )

        route_schemas = [RouteResponse.model_validate(r) for r in ranked]

        return RecommendationResponse(
            routes=route_schemas,
            total=len(route_schemas),
        )
