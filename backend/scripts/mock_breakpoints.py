"""
Create mock breakpoints for a handful of routes so the simulator can unlock US-07 / US-09 flows.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy import delete, select

# Allow running the script directly via `python scripts/mock_breakpoints.py`
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db_session, init_db
from app.models.entities import Breakpoint, Route
from app.settings import get_settings


ROUTE_BREAKPOINTS: dict[int, list[dict[str, object]]] = {
    1362328: [
        {
            "order_index": 0,
            "poi_name": "Domplatz Start",
            "poi_type": "historic_square",
            "latitude": 49.8919,
            "longitude": 10.8864,
            "main_quest_snippet": "Kick off the world-heritage run under the spires of Bamberg Cathedral.",
            "side_plot_snippet": "Choir voices echo behind the cathedral doors as you stretch.",
        },
        {
            "order_index": 1,
            "poi_name": "Regnitz Riverside Stride",
            "poi_type": "river_walk",
            "latitude": 49.895,
            "longitude": 10.881,
            "main_quest_snippet": "Follow the Regnitz and keep tempo with the gentle current.",
            "side_plot_snippet": "Spot rowers slicing through the morning mist.",
        },
        {
            "order_index": 2,
            "poi_name": "Altenburg Vista",
            "poi_type": "viewpoint",
            "latitude": 49.8853,
            "longitude": 10.8782,
            "main_quest_snippet": "Climb toward Altenburg Castle for the signature hill repeat.",
            "side_plot_snippet": "A falcon circles overhead, watching your ascent.",
        },
        {
            "order_index": 3,
            "poi_name": "Little Venice Boardwalk",
            "poi_type": "canal",
            "latitude": 49.8922,
            "longitude": 10.8805,
            "main_quest_snippet": "Drop back to the canals and weave between the fishermen’s houses.",
            "side_plot_snippet": "Windowsills overflow with red geraniums.",
        },
        {
            "order_index": 4,
            "poi_name": "Maxplatz Sprint Finish",
            "poi_type": "city_square",
            "latitude": 49.8928,
            "longitude": 10.8879,
            "main_quest_snippet": "Push through the final cobblestone sprint into Maxplatz.",
            "side_plot_snippet": "Crowds clap wooden clappers to cheer you home.",
        },
    ],
    1362610: [
        {
            "order_index": 0,
            "poi_name": "Theresienwiese Gate",
            "poi_type": "trailhead",
            "latitude": 48.1319,
            "longitude": 11.5494,
            "main_quest_snippet": "Start beneath the Wiesn arch and feel the festival grounds wake up.",
            "side_plot_snippet": "Vendors set out gingerbread hearts still warm from the oven.",
        },
        {
            "order_index": 1,
            "poi_name": "Bavaria Statue Steps",
            "poi_type": "landmark",
            "latitude": 48.131,
            "longitude": 11.548,
            "main_quest_snippet": "Climb to the foot of the Bavaria statue for the first elevation pop.",
            "side_plot_snippet": "Tap the bronze lions for good luck on the descent.",
        },
        {
            "order_index": 2,
            "poi_name": "Oktoberfest Midway",
            "poi_type": "festival_lane",
            "latitude": 48.1328,
            "longitude": 11.5552,
            "main_quest_snippet": "Thread through colorful tents and listen for accordion riffs.",
            "side_plot_snippet": "Guess how many pretzels are stacked at the baker’s stall.",
        },
        {
            "order_index": 3,
            "poi_name": "Craft Market Lane",
            "poi_type": "market",
            "latitude": 48.1341,
            "longitude": 11.5586,
            "main_quest_snippet": "Glide past artisans carving steins while the course bends back west.",
            "side_plot_snippet": "A brewer offers you a whiff of freshly toasted malt.",
        },
        {
            "order_index": 4,
            "poi_name": "Festzelt Finish Arch",
            "poi_type": "finish_line",
            "latitude": 48.1322,
            "longitude": 11.5509,
            "main_quest_snippet": "Charge through the illuminated fest tent arch to complete the Wiesn loop.",
            "side_plot_snippet": "Bandleader raises his baton just as you cross the line.",
        },
    ],
    1367672: [
        {
            "order_index": 0,
            "poi_name": "Annaberg Trailhead",
            "poi_type": "trailhead",
            "latitude": 50.5805,
            "longitude": 13.0012,
            "main_quest_snippet": "Hit the pine-lined start chute pointing toward Fichtelberg.",
            "side_plot_snippet": "Cowbells echo from the valley farms below.",
        },
        {
            "order_index": 1,
            "poi_name": "Pöhlberg Forest Cut",
            "poi_type": "forest",
            "latitude": 50.5739,
            "longitude": 12.9991,
            "main_quest_snippet": "Duck into the spruce forest and tackle the rooty switchbacks.",
            "side_plot_snippet": "A dusting of moss makes the boulders look enchanted.",
        },
        {
            "order_index": 2,
            "poi_name": "Granite Crest Ridge",
            "poi_type": "ridge",
            "latitude": 50.569,
            "longitude": 12.994,
            "main_quest_snippet": "Steady your breathing on the exposed ridge with 360° Ore Mountain views.",
            "side_plot_snippet": "Look for the old border marker standing beside the trail.",
        },
        {
            "order_index": 3,
            "poi_name": "Fichtelberg Saddle",
            "poi_type": "saddle",
            "latitude": 50.5662,
            "longitude": 12.9835,
            "main_quest_snippet": "Refuel at the saddle before the final kilometer grind.",
            "side_plot_snippet": "Volunteers hand out blueberry tea steaming in enamel cups.",
        },
        {
            "order_index": 4,
            "poi_name": "Summit Panorama Deck",
            "poi_type": "summit",
            "latitude": 50.564,
            "longitude": 12.951,
            "main_quest_snippet": "Tag the summit deck—highest point in Saxony—and soak up the Salomon Cup finish vibe.",
            "side_plot_snippet": "Paragliders launch just as you raise your arms in victory.",
        },
    ],
}


async def main() -> None:
    settings = get_settings()
    init_db(settings)

    async with await get_db_session() as session:
        for route_id, breakpoint_rows in ROUTE_BREAKPOINTS.items():
            route_result = await session.execute(select(Route).where(Route.id == route_id))
            route = route_result.scalar_one_or_none()
            if not route:
                print(f"⚠️  Route {route_id} not found in database. Skipping.")
                continue

            # Clear any existing mock breakpoints
            await session.execute(delete(Breakpoint).where(Breakpoint.route_id == route_id))

            for row in breakpoint_rows:
                session.add(Breakpoint(route_id=route_id, **row))

        await session.commit()
        print(f"✅ Inserted breakpoints for {len(ROUTE_BREAKPOINTS)} routes.")


if __name__ == "__main__":
    asyncio.run(main())

