"""
Test script for achievement system.
Run with: python scripts/test_achievements.py
"""
from __future__ import annotations

import asyncio
from pathlib import Path

# Allow running the script directly
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db_session, init_db
from app.models.entities import DemoProfile, Route, Souvenir, Achievement, ProfileAchievement
from app.services.achievement_service import (
    seed_achievements,
    check_and_unlock_achievements,
    get_all_achievements,
    get_user_achievements,
)
from app.settings import get_settings
from sqlalchemy import select


async def test_achievements() -> None:
    """Test achievement system."""
    settings = get_settings()
    init_db(settings)

    async with await get_db_session() as session:
        print("🧪 Testing Achievement System\n")

        # 1. Seed achievements
        print("1. Seeding achievements...")
        await seed_achievements(session)
        all_achievements = await get_all_achievements(session)
        print(f"   ✅ Seeded {len(all_achievements)} achievements")
        for a in all_achievements:
            print(f"      - {a.icon} {a.name}: {a.description}")

        # 2. Get or create a test profile
        print("\n2. Getting test profile...")
        result = await session.execute(select(DemoProfile).limit(1))
        profile = result.scalar_one_or_none()
        
        if not profile:
            print("   ⚠️  No profile found. Creating test profile...")
            profile = DemoProfile(total_xp=0, level=1)
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
        
        print(f"   ✅ Using profile ID: {profile.id} (Level: {profile.level}, XP: {profile.total_xp})")

        # 3. Check initial achievements (should be none unlocked)
        print("\n3. Checking initial achievements...")
        user_achievements = await get_user_achievements(profile.id, session)
        print(f"   ✅ User has {len(user_achievements)} unlocked achievements")

        # 4. Test achievement unlocking
        print("\n4. Testing achievement unlocking...")
        
        # Get user's completed routes
        souvenirs_result = await session.execute(
            select(Souvenir).where(Souvenir.demo_profile_id == profile.id)
        )
        souvenirs = list(souvenirs_result.scalars().all())
        print(f"   📊 User has completed {len(souvenirs)} routes")
        
        # Check and unlock
        newly_unlocked = await check_and_unlock_achievements(profile.id, session)
        print(f"   ✅ Unlocked {len(newly_unlocked)} new achievements:")
        for a in newly_unlocked:
            print(f"      - {a.icon} {a.name}")

        # 5. Get all achievements with status
        print("\n5. Getting all achievements with status...")
        all_achievements = await get_all_achievements(session)
        user_achievements = await get_user_achievements(profile.id, session)
        unlocked_ids = {ua.achievement_id for ua in user_achievements}
        
        unlocked_count = 0
        for a in all_achievements:
            is_unlocked = a.id in unlocked_ids
            status = "✅ UNLOCKED" if is_unlocked else "🔒 LOCKED"
            print(f"   {status} - {a.icon} {a.name}: {a.description}")
            if is_unlocked:
                unlocked_count += 1
        
        print(f"\n   📊 Summary: {unlocked_count}/{len(all_achievements)} achievements unlocked")

        # 6. Test specific conditions
        print("\n6. Testing specific achievement conditions...")
        
        # Test First Steps (should unlock if user has 1+ routes)
        if len(souvenirs) >= 1:
            print("   ✅ First Steps condition met (1+ routes completed)")
        else:
            print("   🔒 First Steps condition not met (need 1+ routes)")
        
        # Test Explorer (should unlock if user has 3+ routes)
        if len(souvenirs) >= 3:
            print("   ✅ Explorer condition met (3+ routes completed)")
        else:
            print(f"   🔒 Explorer condition not met (need 3 routes, have {len(souvenirs)})")
        
        # Test Rising Star (should unlock if level >= 5)
        if profile.level >= 5:
            print(f"   ✅ Rising Star condition met (Level {profile.level} >= 5)")
        else:
            print(f"   🔒 Rising Star condition not met (Level {profile.level} < 5)")
        
        # Test XP Collector (should unlock if total_xp >= 1000)
        if profile.total_xp >= 1000:
            print(f"   ✅ XP Collector condition met ({profile.total_xp} XP >= 1000)")
        else:
            print(f"   🔒 XP Collector condition not met ({profile.total_xp} XP < 1000)")

        print("\n✅ Achievement system test completed!")


if __name__ == "__main__":
    asyncio.run(test_achievements())

