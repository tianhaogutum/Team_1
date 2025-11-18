# Retrieve route data via the Outdooractive API
from typing import Any, Dict, List

import httpx

from app.settings import get_settings

settings = get_settings()

# Map human-readable activity names to numeric IDs used by external APIs,should be adjusted according to Outdooractive's actual codes
ACTIVITY_CODE_MAP: Dict[str, str] = {
    "hiking": "1001",
    "cycling": "1002",
    "city-walk": "1003",
    "trail-running": "1004",
}

class OutdooractiveClient:
    """
    Thin HTTP client for the Outdooractive routes API.
    Only responsible for external HTTP calls, no DB logic here.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.outdooractive_api_key
        self.base_url = base_url or settings.outdooractive_base_url

    async def fetch_routes(
        self,
        region: str | None = None,
        activity_type: str | int | None = None,  
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        #######parameters need to be adjusted according to the Outdooractive API 
        params: Dict[str, Any] = {
            "key": self.api_key,
            "lang": "en",
            "limit": limit,
        }

        if region:
            params["where"] = region  

        if activity_type is not None:
            if isinstance(activity_type, int) or (isinstance(activity_type, str) and activity_type.isdigit()):
                activity_code = str(activity_type)
            else:
                activity_code = ACTIVITY_CODE_MAP.get(str(activity_type).lower(), None)

            if activity_code:
                params["activity"] = activity_code
            else:
                params["activity"] = activity_type

        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            resp = await client.get("/some/routes/endpoint", params=params)
            resp.raise_for_status()
            data = resp.json()
        # endpoint and response structure need to be adjusted according to the Outdooractive API
        return data.get("results", [])

