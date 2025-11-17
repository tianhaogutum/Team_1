"""
Database seeding script to populate initial data for development and demo.
"""
import asyncio
from datetime import datetime

from sqlalchemy import select

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


async def seed_data():
    """Seed the database with sample routes, breakpoints, and related data."""
    settings = get_settings()
    init_db(settings)
    
    async with get_db_session() as session:
        # Check if data already exists
        result = await session.execute(select(Route).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping...")
            return
        
        # Create sample routes
        routes_data = [
            {
                "id": 1001,
                "title": "Salzburg Old Town City Walk",
                "category_name": "cityTour",
                "length_meters": 3500.0,
                "duration_min": 45,
                "difficulty": 1,
                "short_description": "Explore the charming old town of Salzburg, passing by Mozart's birthplace and historic squares.",
                "xp_required": 0,
                "story_prologue_title": "The Mozart City Adventure",
                "story_prologue_body": "You begin your journey in the heart of Salzburg, where music and history intertwine. The cobblestone streets whisper tales of Mozart and the Salzach River flows gently beside you.",
                "story_epilogue_body": "As you complete your walk through Salzburg's old town, you've discovered the soul of this musical city. The memories of baroque architecture and cultural heritage will stay with you.",
            },
            {
                "id": 1002,
                "title": "Alpine Meadow Trail",
                "category_name": "hikingTourTrail",
                "length_meters": 8500.0,
                "duration_min": 180,
                "difficulty": 3,
                "short_description": "A moderate hike through alpine meadows with stunning mountain views.",
                "xp_required": 50,
                "story_prologue_title": "Mountain Explorer's Quest",
                "story_prologue_body": "The alpine meadows call to you. Today's challenge takes you through wildflower fields and up gentle slopes, where each step brings you closer to panoramic mountain vistas.",
                "story_epilogue_body": "You've conquered the alpine trail! The fresh mountain air and breathtaking views have rewarded your efforts. You're ready for even greater challenges.",
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
                "story_prologue_title": "Riverside Adventure",
                "story_prologue_body": "Your wheels are ready, and the river path stretches ahead. This leisurely ride offers perfect views of the water and surrounding countryside.",
                "story_epilogue_body": "The riverside path has shown you the beauty of cycling. You've enjoyed the gentle breeze and peaceful scenery along the way.",
            },
            {
                "id": 1004,
                "title": "Forest Trail Running Loop",
                "category_name": "trailRunning",
                "length_meters": 6000.0,
                "duration_min": 40,
                "difficulty": 2,
                "short_description": "A challenging trail run through dense forest with varied terrain.",
                "xp_required": 30,
                "story_prologue_title": "Forest Runner's Challenge",
                "story_prologue_body": "The forest trail awaits your footsteps. Today you'll push your limits through winding paths, over roots and rocks, testing both speed and endurance.",
                "story_epilogue_body": "You've completed the forest loop! Your legs are strong, your breath is steady, and you've proven your trail running prowess.",
            },
            {
                "id": 1005,
                "title": "Historic Castle Hill Climb",
                "category_name": "hikingTourTrail",
                "length_meters": 2500.0,
                "duration_min": 90,
                "difficulty": 2,
                "short_description": "Climb to an ancient castle with panoramic city views and rich history.",
                "xp_required": 0,
                "story_prologue_title": "Castle Guardian's Ascent",
                "story_prologue_body": "The ancient castle stands above the city, a sentinel of history. Your mission: ascend the hill and discover the secrets held within its walls.",
                "story_epilogue_body": "From the castle heights, you've seen the city spread below like a map. The history and views have made this climb unforgettable.",
            },
            {
                "id": 1006,
                "title": "Lakeside Sunset Walk",
                "category_name": "hikingTourTrail",
                "length_meters": 4000.0,
                "duration_min": 60,
                "difficulty": 1,
                "short_description": "A peaceful evening walk along the lake, perfect for watching the sunset.",
                "xp_required": 0,
                "story_prologue_title": "Sunset Serenity",
                "story_prologue_body": "The lake glimmers in the afternoon light. This gentle walk offers tranquility and the promise of a beautiful sunset over the water.",
                "story_epilogue_body": "As the sun sets over the lake, you've found peace and beauty in this simple walk. The colors of the sky reflect on the water, creating a perfect end to your day.",
            },
            {
                "id": 1007,
                "title": "Mountain Peak Challenge",
                "category_name": "mountaineering",
                "length_meters": 15000.0,
                "duration_min": 360,
                "difficulty": 5,
                "short_description": "An advanced mountaineering route to a challenging peak with technical sections.",
                "xp_required": 200,
                "story_prologue_title": "Peak Conqueror's Journey",
                "story_prologue_body": "The peak looms ahead, a true test of skill and determination. This is not for the faint of heart—steep ascents, rocky terrain, and breathtaking heights await.",
                "story_epilogue_body": "You've reached the summit! The world spreads below you, and you've proven yourself as a true mountaineer. This achievement will be remembered.",
            },
            {
                "id": 1008,
                "title": "Village Heritage Trail",
                "category_name": "themeTrail",
                "length_meters": 5000.0,
                "duration_min": 120,
                "difficulty": 1,
                "short_description": "Discover the cultural heritage of traditional villages along this themed trail.",
                "xp_required": 0,
                "story_prologue_title": "Heritage Explorer",
                "story_prologue_body": "Step back in time as you walk through historic villages. Each building tells a story, and each corner reveals a piece of local culture and tradition.",
                "story_epilogue_body": "You've journeyed through history, learning about the people and places that shaped this region. The heritage trail has enriched your understanding.",
            },
            {
                "id": 1009,
                "title": "Coastal Cliff Path",
                "category_name": "hikingTourTrail",
                "length_meters": 7000.0,
                "duration_min": 150,
                "difficulty": 3,
                "short_description": "A dramatic coastal walk along cliffs with ocean views and sea breeze.",
                "xp_required": 80,
                "story_prologue_title": "Coastal Wanderer",
                "story_prologue_body": "The ocean stretches to the horizon, and the cliff path offers stunning views at every turn. The sound of waves accompanies your journey.",
                "story_epilogue_body": "You've walked the coastal cliffs, feeling the power of the ocean and the beauty of the coastline. This adventure has been both challenging and rewarding.",
            },
            {
                "id": 1010,
                "title": "Urban Art Discovery Walk",
                "category_name": "cityTour",
                "length_meters": 3000.0,
                "duration_min": 50,
                "difficulty": 1,
                "short_description": "Explore street art, murals, and creative installations throughout the city.",
                "xp_required": 0,
                "story_prologue_title": "Art Seeker's Quest",
                "story_prologue_body": "The city is a canvas, and you're the explorer. Hidden murals, street art, and creative installations await your discovery around every corner.",
                "story_epilogue_body": "You've uncovered the artistic soul of the city. Each piece of art tells a story, and you've become part of that narrative.",
            },
        ]
        
        routes = []
        for route_data in routes_data:
            route = Route(**route_data)
            routes.append(route)
            session.add(route)
        
        await session.flush()
        
        # Create breakpoints for each route
        breakpoints_data = [
            # Route 1001: Salzburg Old Town
            {"route_id": 1001, "order_index": 0, "poi_name": "Mozartplatz", "poi_type": "square", "latitude": 47.7989, "longitude": 13.0485, "main_quest_snippet": "Start at Mozartplatz, the heart of Salzburg's old town."},
            {"route_id": 1001, "order_index": 1, "poi_name": "Mozart's Birthplace", "poi_type": "museum", "latitude": 47.8000, "longitude": 13.0500, "main_quest_snippet": "Visit the birthplace of Wolfgang Amadeus Mozart."},
            {"route_id": 1001, "order_index": 2, "poi_name": "Getreidegasse", "poi_type": "street", "latitude": 47.8010, "longitude": 13.0510, "main_quest_snippet": "Walk through the famous shopping street Getreidegasse."},
            {"route_id": 1001, "order_index": 3, "poi_name": "Salzach River Bridge", "poi_type": "bridge", "latitude": 47.8020, "longitude": 13.0520, "main_quest_snippet": "Cross the Salzach River and enjoy the view of the old town."},
            
            # Route 1002: Alpine Meadow
            {"route_id": 1002, "order_index": 0, "poi_name": "Trailhead", "poi_type": "trailhead", "latitude": 47.5000, "longitude": 13.2000, "main_quest_snippet": "Begin your alpine adventure at the trailhead."},
            {"route_id": 1002, "order_index": 1, "poi_name": "Wildflower Meadow", "poi_type": "natural", "latitude": 47.5100, "longitude": 13.2100, "main_quest_snippet": "Pass through a meadow filled with alpine wildflowers."},
            {"route_id": 1002, "order_index": 2, "poi_name": "Mountain Viewpoint", "poi_type": "viewpoint", "latitude": 47.5200, "longitude": 13.2200, "main_quest_snippet": "Reach a viewpoint with panoramic mountain vistas."},
            
            # Route 1003: Riverside Cycling
            {"route_id": 1003, "order_index": 0, "poi_name": "Cycle Path Start", "poi_type": "trailhead", "latitude": 47.6000, "longitude": 13.1000, "main_quest_snippet": "Start your riverside cycling adventure."},
            {"route_id": 1003, "order_index": 1, "poi_name": "Riverside Park", "poi_type": "park", "latitude": 47.6100, "longitude": 13.1100, "main_quest_snippet": "Pass through a peaceful riverside park."},
            {"route_id": 1003, "order_index": 2, "poi_name": "Picnic Area", "poi_type": "facility", "latitude": 47.6200, "longitude": 13.1200, "main_quest_snippet": "Reach a scenic picnic area by the river."},
            
            # Route 1004: Forest Trail Running
            {"route_id": 1004, "order_index": 0, "poi_name": "Forest Entrance", "poi_type": "trailhead", "latitude": 47.7000, "longitude": 13.3000, "main_quest_snippet": "Enter the forest trail and begin your run."},
            {"route_id": 1004, "order_index": 1, "poi_name": "Ancient Tree", "poi_type": "natural", "latitude": 47.7100, "longitude": 13.3100, "main_quest_snippet": "Pass by an ancient, towering tree."},
            {"route_id": 1004, "order_index": 2, "poi_name": "Forest Clearing", "poi_type": "natural", "latitude": 47.7200, "longitude": 13.3200, "main_quest_snippet": "Reach a peaceful forest clearing."},
            
            # Route 1005: Castle Hill
            {"route_id": 1005, "order_index": 0, "poi_name": "Castle Hill Base", "poi_type": "trailhead", "latitude": 47.7950, "longitude": 13.0450, "main_quest_snippet": "Begin your ascent to the castle."},
            {"route_id": 1005, "order_index": 1, "poi_name": "Historic Gate", "poi_type": "monument", "latitude": 47.7960, "longitude": 13.0460, "main_quest_snippet": "Pass through the historic castle gate."},
            {"route_id": 1005, "order_index": 2, "poi_name": "Castle Courtyard", "poi_type": "monument", "latitude": 47.7970, "longitude": 13.0470, "main_quest_snippet": "Enter the castle courtyard."},
            {"route_id": 1005, "order_index": 3, "poi_name": "Castle Tower", "poi_type": "viewpoint", "latitude": 47.7980, "longitude": 13.0480, "main_quest_snippet": "Reach the castle tower for panoramic views."},
        ]
        
        breakpoints = []
        for bp_data in breakpoints_data:
            bp = Breakpoint(**bp_data)
            breakpoints.append(bp)
            session.add(bp)
        
        await session.flush()
        
        # Create mini quests for some breakpoints
        mini_quests_data = [
            {"breakpoint_id": breakpoints[1].id, "task_description": "Take a photo of Mozart's Birthplace facade", "xp_reward": 10},
            {"breakpoint_id": breakpoints[2].id, "task_description": "Find and count the decorative signs on Getreidegasse", "xp_reward": 15},
            {"breakpoint_id": breakpoints[5].id, "task_description": "Identify 3 different types of wildflowers in the meadow", "xp_reward": 20},
            {"breakpoint_id": breakpoints[6].id, "task_description": "Take a panoramic photo from the mountain viewpoint", "xp_reward": 25},
            {"breakpoint_id": breakpoints[9].id, "task_description": "Spot at least 2 different bird species in the park", "xp_reward": 15},
            {"breakpoint_id": breakpoints[11].id, "task_description": "Touch the ancient tree and estimate its age", "xp_reward": 20},
            {"breakpoint_id": breakpoints[13].id, "task_description": "Read the inscription on the historic gate", "xp_reward": 10},
            {"breakpoint_id": breakpoints[15].id, "task_description": "Count the number of windows visible from the castle tower", "xp_reward": 30},
        ]
        
        for mq_data in mini_quests_data:
            mini_quest = MiniQuest(**mq_data)
            session.add(mini_quest)
        
        # Create a demo profile
        demo_profile = DemoProfile(
            total_xp=0,
            level=1,
            user_vector_json='{"fitness": 2, "preference": "city"}',
            genai_welcome_summary="Welcome, City Explorer! You're ready to discover urban adventures.",
        )
        session.add(demo_profile)
        await session.flush()
        
        # Create a few sample feedback entries
        feedback_data = [
            {"demo_profile_id": demo_profile.id, "route_id": 1007, "reason": "too_difficult"},
            {"demo_profile_id": demo_profile.id, "route_id": 1009, "reason": "too_far"},
        ]
        
        for fb_data in feedback_data:
            feedback = ProfileFeedback(**fb_data)
            session.add(feedback)
        
        # Create a sample souvenir (completed route)
        souvenir = Souvenir(
            demo_profile_id=demo_profile.id,
            route_id=1001,
            completed_at=datetime.now(),
            total_xp_gained=150,
            genai_summary="You've successfully completed the Salzburg Old Town walk! Your exploration of Mozart's city was both educational and inspiring.",
            xp_breakdown_json='{"base": 100, "distance": 30, "quests": 20}',
        )
        session.add(souvenir)
        
        await session.commit()
        print(f"✅ Seeded database with {len(routes)} routes, {len(breakpoints)} breakpoints, {len(mini_quests_data)} mini quests, 1 demo profile, and sample data.")


if __name__ == "__main__":
    asyncio.run(seed_data())

