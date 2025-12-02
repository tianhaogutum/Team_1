"""
Test achievement unlocking with a real scenario.
Run with: python scripts/test_achievement_unlock.py
"""
from __future__ import annotations

import asyncio
from pathlib import Path

# Allow running the script directly
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db_session, init_db
from app.models.entities import DemoProfile, Route, Souvenir
from app.services.achievement_service import (
    seed_achievements,
    check_and_unlock_achievements,
    get_user_achievements,
)
from app.settings import get_settings
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def test_achievement_unlock() -> None:
    """Test unlocking achievements with a real scenario."""
    settings = get_settings()
    init_db(settings)

    async with await get_db_session() as session:
        print("🧪 Testing Achievement Unlocking\n")

        # 1. Seed achievements
        await seed_achievements(session)
        print("✅ Achievements seeded\n")

        # 2. Get or create test profile
        result = await session.execute(select(DemoProfile).limit(1))
        profile = result.scalar_one_or_none()
        
        if not profile:
            print("⚠️  No profile found. Please create a profile first.")
            return
        
        print(f"📊 Profile: ID={profile.id}, Level={profile.level}, XP={profile.total_xp}\n")

        # 3. Get completed routes
        souvenirs_result = await session.execute(
            select(Souvenir)
            .where(Souvenir.demo_profile_id == profile.id)
            .options(selectinload(Souvenir.route))
        )
        souvenirs = list(souvenirs_result.scalars().all())
        completed_routes = [s.route for s in souvenirs if s.route]
        
        print(f"📊 Completed Routes: {len(completed_routes)}")
        for i, route in enumerate(completed_routes, 1):
            route_type = "hiking"  # Default
            if route.category_name:
                lower = route.category_name.lower()
                if "run" in lower or "jogging" in lower:
                    route_type = "running"
                elif "cycling" in lower or "bike" in lower:
                    route_type = "cycling"
            print(f"   {i}. {route.title} ({route_type})")
        
        # Calculate total distance
        total_distance_km = sum((r.length_meters or 0) / 1000.0 for r in completed_routes)
        print(f"📊 Total Distance: {total_distance_km:.1f} km\n")

        # 4. Check and unlock achievements
        print("🔍 Checking achievements...")
        newly_unlocked = await check_and_unlock_achievements(profile.id, session)
        
        if newly_unlocked:
            print(f"🎉 Unlocked {len(newly_unlocked)} new achievements:")
            for a in newly_unlocked:
                print(f"   ✅ {a.icon} {a.name}")
        else:
            print("   No new achievements unlocked")

        # 5. Show all achievements status
        print("\n📋 All Achievements Status:")
        from app.services.achievement_service import get_all_achievements
        all_achievements = await get_all_achievements(session)
        user_achievements = await get_user_achievements(profile.id, session)
        unlocked_ids = {ua.achievement_id for ua in user_achievements}
        
        unlocked_count = 0
        for a in all_achievements:
            is_unlocked = a.id in unlocked_ids
            status = "✅" if is_unlocked else "🔒"
            print(f"   {status} {a.icon} {a.name}")
            if is_unlocked:
                unlocked_count += 1
        
        print(f"\n📊 Summary: {unlocked_count}/{len(all_achievements)} achievements unlocked")
        print(f"   Level: {profile.level}")
        print(f"   Total XP: {profile.total_xp}")
        print(f"   Routes Completed: {len(completed_routes)}")
        print(f"   Total Distance: {total_distance_km:.1f} km")


if __name__ == "__main__":
    asyncio.run(test_achievement_unlock())

