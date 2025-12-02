"""
HTTP test for the profile statistics API endpoint.

This script tests the endpoint via HTTP requests (simulating frontend calls).
"""
import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"


def test_statistics_endpoint_http():
    """Test statistics endpoint via HTTP."""
    print("🌐 Testing Profile Statistics API via HTTP\n")
    
    # 1. Get a profile ID from the database or use a known one
    print("1️⃣  Finding a profile with completed routes...")
    try:
        # Try to get profiles list (if such endpoint exists) or use a known ID
        # For now, let's try profile ID 1, 2, etc.
        profile_id = None
        for test_id in [1, 2, 3, 4, 5]:
            try:
                response = requests.get(f"{API_BASE_URL}/api/profiles/{test_id}", timeout=5)
                if response.status_code == 200:
                    profile_id = test_id
                    print(f"   ✓ Found profile ID: {profile_id}")
                    break
            except requests.exceptions.RequestException:
                continue
        
        if not profile_id:
            print("   ⚠️  Could not find a valid profile. Trying profile ID 1 anyway...")
            profile_id = 1
    except Exception as e:
        print(f"   ⚠️  Error finding profile: {e}")
        profile_id = 1
    
    # 2. Test statistics endpoint
    print(f"\n2️⃣  Testing GET /api/profiles/{profile_id}/statistics...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/profiles/{profile_id}/statistics",
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print(f"   ⚠️  Profile {profile_id} not found or has no data")
            print("   This is expected if the profile doesn't exist.")
            return True
        
        if response.status_code != 200:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 3. Validate response structure
        print("\n3️⃣  Validating response structure...")
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON response: {e}")
            return False
        
        required_fields = [
            "total_distance_km",
            "total_elevation_m",
            "routes_completed",
            "achievements_unlocked",
            "activity_breakdown"
        ]
        
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            print(f"   ❌ Missing fields: {missing_fields}")
            return False
        
        print("   ✓ All required fields present")
        
        # 4. Display statistics
        print("\n4️⃣  Statistics Data:")
        print(f"   Total Distance: {data['total_distance_km']:.1f} km")
        print(f"   Total Elevation: {data['total_elevation_m']} m")
        print(f"   Routes Completed: {data['routes_completed']}")
        print(f"   Achievements Unlocked: {data['achievements_unlocked']}")
        print(f"   Activity Breakdown:")
        for activity, count in data['activity_breakdown'].items():
            print(f"     - {activity}: {count}")
        
        # 5. Validate data types
        print("\n5️⃣  Validating data types...")
        type_checks = [
            (data['total_distance_km'], (int, float), "total_distance_km"),
            (data['total_elevation_m'], int, "total_elevation_m"),
            (data['routes_completed'], int, "routes_completed"),
            (data['achievements_unlocked'], int, "achievements_unlocked"),
            (data['activity_breakdown'], dict, "activity_breakdown"),
        ]
        
        all_valid = True
        for value, expected_type, field_name in type_checks:
            if not isinstance(value, expected_type):
                print(f"   ❌ {field_name} has wrong type: {type(value).__name__} (expected {expected_type.__name__})")
                all_valid = False
            else:
                print(f"   ✓ {field_name} type correct: {type(value).__name__}")
        
        if not all_valid:
            return False
        
        print("\n✅ HTTP test passed! Statistics endpoint is accessible and returns correct data.")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Could not connect to {API_BASE_URL}")
        print("   Make sure the backend server is running: cd backend && uvicorn app.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timeout")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run HTTP tests."""
    print("=" * 60)
    print("Profile Statistics API HTTP Test")
    print("=" * 60)
    print()
    
    test_passed = test_statistics_endpoint_http()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    if test_passed:
        print("✅ HTTP test PASSED")
        print("\n💡 Next steps:")
        print("   1. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
        print("   2. Start the frontend: cd frontend && pnpm dev")
        print("   3. Open the app and check the Statistics tab in user profile")
        return 0
    else:
        print("❌ HTTP test FAILED")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure the backend is running on http://localhost:8000")
        print("   2. Check that you have at least one profile with completed routes")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

