"""
Import route details (elevation, duration) from JSON file into the routes table.

Usage:
    python backend/scripts/import_route_details.py \
        --json-file backend/data/outdooractive/route_details.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.insert(0, ROOT_DIR)

from app.database import get_db_session, init_db
from app.models.entities import Route
from app.settings import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-file",
        type=str,
        default=os.path.join(ROOT_DIR, "data/outdooractive/route_details.json"),
        help="Path to the JSON file containing route details.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and show stats without touching the database.",
    )
    return parser.parse_args()


def load_route_details(json_path: str) -> dict[int, dict[str, int | None]]:
    """
    Load route details from JSON file.
    
    Returns:
        Dictionary mapping route_id -> {elevation, duration}
    """
    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    
    details: dict[int, dict[str, int | None]] = {}
    
    for route in data.get("routes", []):
        route_id = route.get("id")
        if route_id is None:
            continue
        
        try:
            route_id = int(route_id)
        except (ValueError, TypeError):
            continue
        
        details[route_id] = {
            "elevation": route.get("elevation"),
            "duration": route.get("duration"),
        }
    
    return details


async def update_route_details(
    details: dict[int, dict[str, int | None]],
    *,
    dry_run: bool,
) -> None:
    """
    Update route elevation and duration_min in the database.
    """
    print(f"Loaded {len(details)} route details from JSON.")
    
    if dry_run:
        sample_items = list(details.items())[:5]
        print("Dry run enabled. Sample updates:")
        for route_id, detail in sample_items:
            print(f"  Route {route_id}: elevation={detail['elevation']}, duration={detail['duration']}")
        return

    settings = get_settings()
    init_db(settings)

    session = await get_db_session()
    try:
        updated = 0
        not_found = 0
        
        for route_id, detail in details.items():
            route = await session.get(Route, route_id)
            if route is None:
                print(f"Warning: Route {route_id} not found in database, skipping.")
                not_found += 1
                continue
            
            # Update elevation
            if detail["elevation"] is not None:
                route.elevation = detail["elevation"]
            
            # Update duration_min (using existing field)
            if detail["duration"] is not None:
                route.duration_min = detail["duration"]
            
            updated += 1
        
        await session.commit()
        print(f"Updated {updated} routes with elevation and duration data.")
        if not_found > 0:
            print(f"Warning: {not_found} route IDs from JSON were not found in database.")
    finally:
        await session.close()


async def async_main() -> None:
    args = parse_args()
    details = load_route_details(args.json_file)
    await update_route_details(details, dry_run=args.dry_run)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

