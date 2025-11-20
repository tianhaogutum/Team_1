"""
Import route locations from CSV file into the routes table.

Usage:
    python backend/scripts/import_route_locations.py \
        --csv-file /path/to/route_locations_with_countries.csv
"""

from __future__ import annotations

import argparse
import asyncio
import csv
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
        "--csv-file",
        type=str,
        required=True,
        help="Path to the CSV file containing route locations (id,location).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and show stats without touching the database.",
    )
    return parser.parse_args()


def load_locations_from_csv(csv_path: str) -> dict[int, str]:
    """
    Load route locations from CSV file.
    
    Returns:
        Dictionary mapping route_id -> location string
    """
    locations: dict[int, str] = {}
    
    with open(csv_path, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            route_id_str = row.get("id", "").strip()
            location = row.get("location", "").strip()
            
            if not route_id_str or not location:
                continue
                
            try:
                route_id = int(route_id_str)
                locations[route_id] = location
            except ValueError:
                print(f"Warning: Invalid route ID '{route_id_str}', skipping.")
                continue
    
    return locations


async def update_route_locations(
    locations: dict[int, str],
    *,
    dry_run: bool,
) -> None:
    """
    Update route locations in the database.
    """
    print(f"Loaded {len(locations)} route locations from CSV.")
    
    if dry_run:
        sample_items = list(locations.items())[:5]
        print("Dry run enabled. Sample updates:")
        for route_id, location in sample_items:
            print(f"  Route {route_id}: {location}")
        return

    settings = get_settings()
    init_db(settings)

    session = await get_db_session()
    try:
        updated = 0
        not_found = 0
        
        for route_id, location in locations.items():
            route = await session.get(Route, route_id)
            if route is None:
                print(f"Warning: Route {route_id} not found in database, skipping.")
                not_found += 1
                continue
            
            route.location = location
            updated += 1
        
        await session.commit()
        print(f"Updated {updated} routes with location data.")
        if not_found > 0:
            print(f"Warning: {not_found} route IDs from CSV were not found in database.")
    finally:
        await session.close()


async def async_main() -> None:
    args = parse_args()
    locations = load_locations_from_csv(args.csv_file)
    await update_route_locations(locations, dry_run=args.dry_run)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

