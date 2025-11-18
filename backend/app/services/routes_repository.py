# Route Data Operations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Route


class RouteRepository:
    """
    Data access layer for Route entities.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Upsert from Outdooractive
    # ------------------------------------------------------------------

    async def upsert_from_outdooractive(self, items: List[Dict[str, Any]]) -> int:
        """
        Insert or update routes based on Outdooractive payloads.
    
        """
        count = 0

        for item in items:
            # Adjusted according to Outdooractive's actual parameters
            external_id_raw = item.get("id")
            if external_id_raw is None:
                continue

            route_id = int(external_id_raw)

            title = item.get("title") or item.get("name") or "Untitled route"
            category_name = item.get("category_name")  
            length_meters = item.get("length_m") or item.get("distance")  
            duration_min = item.get("duration_min") or item.get("duration")
            difficulty = item.get("difficulty")  
            short_description = item.get("summary") or item.get("description")
            gpx_data_raw = item.get("gpx")  

            stmt = select(Route).where(Route.id == route_id)
            result = await self.db.execute(stmt)
            route: Optional[Route] = result.scalar_one_or_none()

            if route is None:
                route = Route(
                    id=route_id,
                    title=title,
                    category_name=category_name,
                    length_meters=length_meters,
                    duration_min=duration_min,
                    difficulty=difficulty,
                    short_description=short_description,
                    gpx_data_raw=gpx_data_raw,
                    xp_required=0,  
                )
                self.db.add(route)
            else:
                route.title = title
                route.category_name = category_name
                route.length_meters = length_meters
                route.duration_min = duration_min
                route.difficulty = difficulty
                route.short_description = short_description
                route.gpx_data_raw = gpx_data_raw

            count += 1

        return count

    # ------------------------------------------------------------------
    # Query routes for recommendation
    # ------------------------------------------------------------------

    async def list_routes_for_recommendation(
        self,
        activity_type: str | None = None,
        limit: int = 50,
    ) -> List[Route]:
        """
        Fetch candidate routes from the local DB.
        """
        stmt = select(Route)

        if activity_type:
            stmt = stmt.where(Route.category_name == activity_type)

        stmt = stmt.order_by(Route.id.asc()).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
