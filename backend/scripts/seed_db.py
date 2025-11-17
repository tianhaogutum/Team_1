"""
Database seeding script to populate initial data for development and demo.
Creates ~10 routes with breakpoints, mini-quests, and other related data.
"""
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import select

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_session, init_db
from app.models.entities import (
    Breakpoint,
    DemoProfile,
    MiniQuest,
    ProfileFeedback,
    Route,
    Souvenir,
)
from app.settings import get_settings


async def seed_database() -> None:
    """Seed the database with initial demo data."""
    settings = get_settings()
    init_db(settings)

    async with get_db_session() as session:
        # Check if data already exists
        result = await session.execute(select(Route).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping...")
            return

        # Create 10 routes with varying characteristics
        routes_data = [
            {
                "id": 1001,
                "title": "Salzburg Old Town City Walk",
                "category_name": "cityTour",
                "length_meters": 3500.0,
                "duration_min": 45,
                "difficulty": 1,
                "short_description": "A charming walk through Salzburg's historic old town, passing Mozart's birthplace and the Hohensalzburg Fortress.",
                "xp_required": 0,
                "story_prologue_title": "The Mozart Trail",
                "story_prologue_body": "Begin your journey in the heart of Salzburg, where music and history intertwine. Follow the footsteps of Wolfgang Amadeus Mozart through cobblestone streets.",
                "story_epilogue_body": "You've completed the Mozart Trail! The melodies of Salzburg will echo in your memories forever.",
            },
            {
                "id": 1002,
                "title": "Alpine Meadow Hiking Trail",
                "category_name": "hikingTourTrail",
                "length_meters": 8500.0,
                "duration_min": 180,
                "difficulty": 3,
                "short_description": "A moderate mountain hike through alpine meadows with stunning views of the surrounding peaks.",
                "xp_required": 50,
                "story_prologue_title": "Mountain Explorer's Quest",
                "story_prologue_body": "The mountains call to you. Today, you'll ascend through wildflower meadows and breathe the crisp alpine air.",
                "story_epilogue_body": "You've conquered the alpine trail! The summit views were worth every step.",
            },
            {
                "id": 1003,
                "title": "Riverside Cycling Path",
                "category_name": "cycling",
                "length_meters": 12000.0,
                "duration_min": 60,
                "difficulty": 2,
                "short_description": "A scenic bike ride along the river, perfect for families and casual cyclists.",
                "xp_required": 0,
                "story_prologue_title": "River Adventure",
                "story_prologue_body": "Hop on your bike and follow the gentle river as it winds through the countryside. Each turn reveals new beauty.",
                "story_epilogue_body": "What a ride! The river has shown you its secrets today.",
            },
            {
                "id": 1004,
                "title": "Forest Trail Running Loop",
                "category_name": "trailRunning",
                "length_meters": 5000.0,
                "duration_min": 35,
                "difficulty": 2,
                "short_description": "A fast-paced trail run through dense forest with natural obstacles.",
                "xp_required": 25,
                "story_prologue_title": "Forest Sprinter",
                "story_prologue_body": "The forest path awaits. Feel the earth beneath your feet as you sprint through nature's obstacle course.",
                "story_epilogue_body": "You've mastered the forest trail! Your speed and agility have been tested.",
            },
            {
                "id": 1005,
                "title": "Historic Castle Route",
                "category_name": "hikingTourTrail",
                "length_meters": 6000.0,
                "duration_min": 120,
                "difficulty": 2,
                "short_description": "Walk through history to a medieval castle perched on a hilltop.",
                "xp_required": 0,
                "story_prologue_title": "Castle Quest",
                "story_prologue_body": "Legends speak of an ancient castle. Today, you'll discover if the stories are true.",
                "story_epilogue_body": "The castle stands before you, a testament to history. Your quest is complete.",
            },
            {
                "id": 1006,
                "title": "Lakeside Stroll",
                "category_name": "hikingTourTrail",
                "length_meters": 4000.0,
                "duration_min": 50,
                "difficulty": 1,
                "short_description": "A peaceful walk around a beautiful alpine lake with picnic spots.",
                "xp_required": 0,
                "story_prologue_title": "Lake Serenity",
                "story_prologue_body": "The lake's calm waters invite you to slow down and appreciate the moment. Nature's tranquility awaits.",
                "story_epilogue_body": "You've found peace by the lake. The water's reflection mirrors your inner calm.",
            },
            {
                "id": 1007,
                "title": "Mountain Peak Challenge",
                "category_name": "mountaineering",
                "length_meters": 15000.0,
                "duration_min": 360,
                "difficulty": 5,
                "short_description": "A challenging ascent to a mountain peak for experienced hikers only.",
                "xp_required": 200,
                "story_prologue_title": "Peak Conqueror",
                "story_prologue_body": "The summit calls. This is no ordinary hike—it's a test of will, strength, and determination.",
                "story_epilogue_body": "You've reached the peak! The world spreads below you, and you've earned this view.",
            },
            {
                "id": 1008,
                "title": "Village Heritage Walk",
                "category_name": "cityTour",
                "length_meters": 2500.0,
                "duration_min": 40,
                "difficulty": 1,
                "short_description": "Explore a charming alpine village with traditional architecture and local culture.",
                "xp_required": 0,
                "story_prologue_title": "Village Stories",
                "story_prologue_body": "Every corner of this village tells a story. Walk slowly and listen to the whispers of the past.",
                "story_epilogue_body": "You've uncovered the village's secrets. Its stories are now part of your own.",
            },
            {
                "id": 1009,
                "title": "Waterfall Discovery Trail",
                "category_name": "hikingTourTrail",
                "length_meters": 7000.0,
                "duration_min": 150,
                "difficulty": 3,
                "short_description": "Hike to a spectacular waterfall hidden in the mountains.",
                "xp_required": 75,
                "story_prologue_title": "Waterfall Seeker",
                "story_prologue_body": "Rumors of a hidden waterfall have reached you. Follow the sound of rushing water to find this natural wonder.",
                "story_epilogue_body": "The waterfall reveals itself! The mist and roar are a reward for your journey.",
            },
            {
                "id": 1010,
                "title": "Sunset Ridge Walk",
                "category_name": "hikingTourTrail",
                "length_meters": 5500.0,
                "duration_min": 90,
                "difficulty": 2,
                "short_description": "A moderate hike along a ridge with panoramic sunset views.",
                "xp_required": 30,
                "story_prologue_title": "Golden Hour Quest",
                "story_prologue_body": "Time your journey to reach the ridge as the sun begins its descent. The golden hour awaits.",
                "story_epilogue_body": "The sunset painted the sky in colors you'll never forget. This moment is yours forever.",
            },
        ]

        # Create routes
        routes = []
        for route_data in routes_data:
            route = Route(**route_data)
            session.add(route)
            routes.append(route)

        await session.flush()

        # Create breakpoints and mini-quests for each route
        breakpoints_data = [
            # Route 1001: Salzburg City Walk (5 breakpoints)
            {
                "route_id": 1001,
                "order_index": 0,
                "poi_name": "Mozart's Birthplace",
                "poi_type": "landmark",
                "latitude": 47.7989,
                "longitude": 13.0436,
                "main_quest_snippet": "You stand before the house where Mozart was born. The music of genius echoes here.",
                "side_plot_snippet": "A street musician plays Eine kleine Nachtmusik nearby.",
            },
            {
                "route_id": 1001,
                "order_index": 1,
                "poi_name": "Getreidegasse",
                "poi_type": "street",
                "latitude": 47.7995,
                "longitude": 13.0442,
                "main_quest_snippet": "The famous shopping street stretches before you, each sign a work of art.",
                "side_plot_snippet": None,
            },
            {
                "route_id": 1001,
                "order_index": 2,
                "poi_name": "Hohensalzburg Fortress",
                "poi_type": "castle",
                "latitude": 47.7944,
                "longitude": 13.0447,
                "main_quest_snippet": "The fortress looms above. History and power resonate from these ancient walls.",
                "side_plot_snippet": "You can see the entire city from here.",
            },
            {
                "route_id": 1001,
                "order_index": 3,
                "poi_name": "Mirabell Palace",
                "poi_type": "palace",
                "latitude": 47.8056,
                "longitude": 13.0433,
                "main_quest_snippet": "The palace gardens are a masterpiece of baroque design.",
                "side_plot_snippet": None,
            },
            {
                "route_id": 1001,
                "order_index": 4,
                "poi_name": "Salzach River Bridge",
                "poi_type": "bridge",
                "latitude": 47.8006,
                "longitude": 13.0450,
                "main_quest_snippet": "Cross the river and reflect on your journey through Salzburg.",
                "side_plot_snippet": "The river flows gently, carrying stories downstream.",
            },
            # Route 1002: Alpine Meadow (4 breakpoints)
            {
                "route_id": 1002,
                "order_index": 0,
                "poi_name": "Trailhead",
                "poi_type": "trailhead",
                "latitude": 47.4567,
                "longitude": 13.2024,
                "main_quest_snippet": "The trail begins here. Take a deep breath of mountain air.",
                "side_plot_snippet": None,
            },
            {
                "route_id": 1002,
                "order_index": 1,
                "poi_name": "Alpine Meadow",
                "poi_type": "meadow",
                "latitude": 47.4500,
                "longitude": 13.2100,
                "main_quest_snippet": "Wildflowers carpet the meadow. The beauty is overwhelming.",
                "side_plot_snippet": "Butterflies dance among the flowers.",
            },
            {
                "route_id": 1002,
                "order_index": 2,
                "poi_name": "Mountain Viewpoint",
                "poi_type": "viewpoint",
                "latitude": 47.4450,
                "longitude": 13.2150,
                "main_quest_snippet": "The view opens before you. Peaks stretch to the horizon.",
                "side_plot_snippet": None,
            },
            {
                "route_id": 1002,
                "order_index": 3,
                "poi_name": "Summit",
                "poi_type": "summit",
                "latitude": 47.4400,
                "longitude": 13.2200,
                "main_quest_snippet": "You've reached the summit! The world is at your feet.",
                "side_plot_snippet": "An eagle soars overhead, celebrating your achievement.",
            },
            # Route 1003: Riverside Cycling (3 breakpoints)
            {
                "route_id": 1003,
                "order_index": 0,
                "poi_name": "Cycling Start Point",
                "poi_type": "trailhead",
                "latitude": 47.5000,
                "longitude": 13.1000,
                "main_quest_snippet": "Your cycling adventure begins. The river awaits.",
                "side_plot_snippet": None,
            },
            {
                "route_id": 1003,
                "order_index": 1,
                "poi_name": "Riverside Picnic Area",
                "poi_type": "picnic_area",
                "latitude": 47.5100,
                "longitude": 13.1100,
                "main_quest_snippet": "A perfect spot to rest. The river flows peacefully.",
                "side_plot_snippet": "Ducks swim by, unbothered by your presence.",
            },
            {
                "route_id": 1003,
                "order_index": 2,
                "poi_name": "Cycling End Point",
                "poi_type": "trailhead",
                "latitude": 47.5200,
                "longitude": 13.1200,
                "main_quest_snippet": "You've completed the cycling route. Well done!",
                "side_plot_snippet": None,
            },
            # Add a few more breakpoints for other routes (simplified)
            {
                "route_id": 1004,
                "order_index": 0,
                "poi_name": "Forest Trail Start",
                "poi_type": "trailhead",
                "latitude": 47.4000,
                "longitude": 13.3000,
                "main_quest_snippet": "The forest trail begins. Ready to run?",
                "side_plot_snippet": None,
            },
            {
                "route_id": 1004,
                "order_index": 1,
                "poi_name": "Forest Clearing",
                "poi_type": "clearing",
                "latitude": 47.4050,
                "longitude": 13.3050,
                "main_quest_snippet": "A clearing opens in the forest. Catch your breath.",
                "side_plot_snippet": None,
            },
            {
                "route_id": 1004,
                "order_index": 2,
                "poi_name": "Trail End",
                "poi_type": "trailhead",
                "latitude": 47.4100,
                "longitude": 13.3100,
                "main_quest_snippet": "You've completed the trail run! Your speed was impressive.",
                "side_plot_snippet": None,
            },
        ]

        breakpoints = []
        for bp_data in breakpoints_data:
            breakpoint = Breakpoint(**bp_data)
            session.add(breakpoint)
            breakpoints.append(breakpoint)

        await session.flush()

        # Create mini-quests for some breakpoints
        mini_quests_data = [
            {
                "breakpoint_id": breakpoints[0].id,  # Mozart's Birthplace
                "task_description": "Take a photo of Mozart's Birthplace and share a fun fact about the composer.",
                "xp_reward": 20,
            },
            {
                "breakpoint_id": breakpoints[2].id,  # Hohensalzburg Fortress
                "task_description": "Count the number of towers you can see from the fortress viewpoint.",
                "xp_reward": 15,
            },
            {
                "breakpoint_id": breakpoints[4].id,  # Salzach River Bridge
                "task_description": "Find the love lock on the bridge and make a wish.",
                "xp_reward": 10,
            },
            {
                "breakpoint_id": breakpoints[5].id,  # Alpine Meadow
                "task_description": "Identify three different types of wildflowers in the meadow.",
                "xp_reward": 25,
            },
            {
                "breakpoint_id": breakpoints[7].id,  # Summit
                "task_description": "Take a panoramic photo from the summit and name three peaks you can see.",
                "xp_reward": 30,
            },
            {
                "breakpoint_id": breakpoints[9].id,  # Riverside Picnic Area
                "task_description": "Spot at least two different bird species near the river.",
                "xp_reward": 15,
            },
        ]

        for mq_data in mini_quests_data:
            mini_quest = MiniQuest(**mq_data)
            session.add(mini_quest)

        # Create 2 demo profiles
        profiles_data = [
            {
                "total_xp": 150,
                "level": 2,
                "user_vector_json": json.dumps({"fitness": 3, "preference": "hiking", "story_style": "adventure"}),
                "genai_welcome_summary": "You are an Adventure Seeker! You love challenging hikes and epic stories.",
            },
            {
                "total_xp": 50,
                "level": 1,
                "user_vector_json": json.dumps({"fitness": 2, "preference": "city_walk", "story_style": "cultural"}),
                "genai_welcome_summary": "You are a Cultural Explorer! You enjoy discovering history and local stories.",
            },
        ]

        profiles = []
        for profile_data in profiles_data:
            profile = DemoProfile(**profile_data)
            session.add(profile)
            profiles.append(profile)

        await session.flush()

        # Create 2 souvenirs (completed routes)
        souvenirs_data = [
            {
                "demo_profile_id": profiles[0].id,
                "route_id": 1002,
                "total_xp_gained": 120,
                "genai_summary": "You conquered the alpine trail! The mountain views were breathtaking, and your determination shone through.",
                "xp_breakdown_json": json.dumps({"base": 80, "difficulty": 30, "quests": 10}),
            },
            {
                "demo_profile_id": profiles[1].id,
                "route_id": 1001,
                "total_xp_gained": 75,
                "genai_summary": "You've explored Salzburg's old town beautifully! The Mozart trail has enriched your cultural journey.",
                "xp_breakdown_json": json.dumps({"base": 50, "quests": 25}),
            },
        ]

        for souvenir_data in souvenirs_data:
            souvenir = Souvenir(**souvenir_data)
            session.add(souvenir)

        # Create 3 feedback entries
        feedback_data = [
            {
                "demo_profile_id": profiles[0].id,
                "route_id": 1007,
                "reason": "too_difficult",
            },
            {
                "demo_profile_id": profiles[1].id,
                "route_id": 1004,
                "reason": "not_interested",
            },
            {
                "demo_profile_id": profiles[0].id,
                "route_id": 1003,
                "reason": "too_far",
            },
        ]

        for feedback_entry in feedback_data:
            feedback = ProfileFeedback(**feedback_entry)
            session.add(feedback)

        await session.commit()
        print(f"✅ Seeded database successfully!")
        print(f"   - {len(routes)} routes created")
        print(f"   - {len(breakpoints)} breakpoints created")
        print(f"   - {len(mini_quests_data)} mini-quests created")
        print(f"   - {len(profiles)} demo profiles created")
        print(f"   - {len(souvenirs_data)} souvenirs created")
        print(f"   - {len(feedback_data)} feedback entries created")


if __name__ == "__main__":
    asyncio.run(seed_database())

