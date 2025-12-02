"""
Test script for the profile statistics API endpoint.

This script tests:
1. GET /api/profiles/{profile_id}/statistics endpoint
2. Validates response structure
3. Checks calculation accuracy
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models.entities import DemoProfile, Souvenir, Route, ProfileAchievement
from app.api.v1.profiles import get_profile_statistics


async def test_statistics_endpoint():
    """Test the statistics endpoint with real database data."""
    print("🧪 Testing Profile Statistics API Endpoint\n")
    
    async with await get_db_session() as db:
        # 1. Find a profile with souvenirs
        print("1️⃣  Finding a profile with completed routes...")
        result = await db.execute(
            select(DemoProfile)
            .where(DemoProfile.id.in_(
                select(Souvenir.demo_profile_id).distinct()
            ))
            .limit(1)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            print("❌ No profile with souvenirs found. Please complete at least one route first.")
            return False
        
        print(f"   ✓ Found profile ID: {profile.id}")
        print(f"   - Total XP: {profile.total_xp}")
        print(f"   - Level: {profile.level}\n")
        
        # 2. Get actual souvenirs data for manual verification
        print("2️⃣  Fetching souvenirs data for verification...")
        souvenirs_result = await db.execute(
            select(Souvenir)
            .where(Souvenir.demo_profile_id == profile.id)
            .options(selectinload(Souvenir.route))
        )
        souvenirs = souvenirs_result.scalars().all()
        
        print(f"   ✓ Found {len(souvenirs)} souvenirs\n")
        
        # 3. Calculate expected values manually
        print("3️⃣  Calculating expected statistics manually...")
        expected_distance = 0.0
        expected_elevation = 0
        expected_activity_breakdown = {"running": 0, "hiking": 0, "cycling": 0}
        
        for souvenir in souvenirs:
            if souvenir.route:
                if souvenir.route.length_meters:
                    expected_distance += souvenir.route.length_meters / 1000.0
                if souvenir.route.elevation:
                    expected_elevation += souvenir.route.elevation
                
                if souvenir.route.category_name:
                    category_lower = souvenir.route.category_name.lower()
                    if "run" in category_lower or "jogging" in category_lower:
                        expected_activity_breakdown["running"] += 1
                    elif "cycling" in category_lower or "mountain" in category_lower or "bike" in category_lower:
                        expected_activity_breakdown["cycling"] += 1
                    else:
                        expected_activity_breakdown["hiking"] += 1
        
        # Count achievements
        achievements_result = await db.execute(
            select(func.count(ProfileAchievement.id))
            .where(ProfileAchievement.demo_profile_id == profile.id)
        )
        expected_achievements = achievements_result.scalar() or 0
        
        print(f"   Expected values:")
        print(f"   - Total Distance: {expected_distance:.1f} km")
        print(f"   - Total Elevation: {expected_elevation} m")
        print(f"   - Routes Completed: {len(souvenirs)}")
        print(f"   - Achievements Unlocked: {expected_achievements}")
        print(f"   - Activity Breakdown: {expected_activity_breakdown}\n")
        
        # 4. Call the statistics endpoint
        print("4️⃣  Calling statistics endpoint...")
        try:
            stats_response = await get_profile_statistics(profile.id, db)
            print("   ✓ Endpoint call successful\n")
        except Exception as e:
            print(f"   ❌ Endpoint call failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 5. Validate response structure
        print("5️⃣  Validating response structure...")
        required_fields = [
            "total_distance_km",
            "total_elevation_m",
            "routes_completed",
            "achievements_unlocked",
            "activity_breakdown"
        ]
        
        stats_dict = stats_response.model_dump()
        missing_fields = [f for f in required_fields if f not in stats_dict]
        
        if missing_fields:
            print(f"   ❌ Missing fields: {missing_fields}")
            return False
        
        print("   ✓ All required fields present\n")
        
        # 6. Validate values
        print("6️⃣  Validating calculated values...")
        all_correct = True
        
        # Distance (allow small floating point differences)
        if abs(stats_response.total_distance_km - expected_distance) > 0.1:
            print(f"   ❌ Distance mismatch: got {stats_response.total_distance_km:.1f}, expected {expected_distance:.1f}")
            all_correct = False
        else:
            print(f"   ✓ Distance correct: {stats_response.total_distance_km:.1f} km")
        
        # Elevation
        if stats_response.total_elevation_m != expected_elevation:
            print(f"   ❌ Elevation mismatch: got {stats_response.total_elevation_m}, expected {expected_elevation}")
            all_correct = False
        else:
            print(f"   ✓ Elevation correct: {stats_response.total_elevation_m} m")
        
        # Routes completed
        if stats_response.routes_completed != len(souvenirs):
            print(f"   ❌ Routes count mismatch: got {stats_response.routes_completed}, expected {len(souvenirs)}")
            all_correct = False
        else:
            print(f"   ✓ Routes count correct: {stats_response.routes_completed}")
        
        # Achievements
        if stats_response.achievements_unlocked != expected_achievements:
            print(f"   ❌ Achievements mismatch: got {stats_response.achievements_unlocked}, expected {expected_achievements}")
            all_correct = False
        else:
            print(f"   ✓ Achievements correct: {stats_response.achievements_unlocked}")
        
        # Activity breakdown
        for activity_type in ["running", "hiking", "cycling"]:
            expected_count = expected_activity_breakdown.get(activity_type, 0)
            actual_count = stats_response.activity_breakdown.get(activity_type, 0)
            if actual_count != expected_count:
                print(f"   ❌ {activity_type} count mismatch: got {actual_count}, expected {expected_count}")
                all_correct = False
            else:
                print(f"   ✓ {activity_type} count correct: {actual_count}")
        
        print()
        
        if all_correct:
            print("✅ All tests passed! Statistics endpoint is working correctly.")
            return True
        else:
            print("❌ Some validations failed. Please check the implementation.")
            return False


async def test_statistics_endpoint_not_found():
    """Test 404 handling for non-existent profile."""
    print("\n🧪 Testing 404 handling for non-existent profile...\n")
    
    async with await get_db_session() as db:
        # Find a non-existent profile ID (use a very large number)
        result = await db.execute(
            select(func.max(DemoProfile.id))
        )
        max_id = result.scalar() or 0
        non_existent_id = max_id + 9999
        
        try:
            from app.api.v1.profiles import get_profile_statistics
            from fastapi import HTTPException
            
            await get_profile_statistics(non_existent_id, db)
            print(f"   ❌ Should have raised 404 for profile ID {non_existent_id}")
            return False
        except HTTPException as e:
            if e.status_code == 404:
                print(f"   ✓ Correctly raised 404 for non-existent profile")
                return True
            else:
                print(f"   ❌ Raised wrong status code: {e.status_code} (expected 404)")
                return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Profile Statistics API Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Normal statistics endpoint
    test1_passed = await test_statistics_endpoint()
    
    # Test 2: 404 handling
    test2_passed = await test_statistics_endpoint_not_found()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Test 1 (Statistics calculation): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (404 handling): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

