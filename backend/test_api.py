#!/usr/bin/env python3
"""Quick test script to check backend API connectivity"""
import httpx
import json
import sys

def test_backend():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Backend API...")
    print(f"Base URL: {base_url}\n")
    
    # Test 1: Health check with explicit IPv4
    print("1. Testing /healthz endpoint...")
    print("   (Note: /healthz is a standard health check endpoint name)")
    try:
        # Use sync client with longer timeout (30 seconds)
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{base_url}/healthz")
            print(f"   ✅ Status: {response.status_code}")
            print(f"   Response: {response.json()}\n")
    except httpx.TimeoutException:
        print(f"   ❌ Timeout: Backend is not responding within 30 seconds")
        print(f"   💡 Try: Check if backend is running and not stuck")
        print(f"   💡 Check backend terminal for error messages")
        return
    except httpx.ConnectError as e:
        print(f"   ❌ Connection Error: {e}")
        print(f"   💡 Try: Make sure backend is running on port 8000")
        return
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}\n")
        return
    
    # Test 2: Create profile
    print("2. Testing POST /api/profiles endpoint...")
    test_data = {
        "fitness": "beginner",
        "type": ["history-culture"],
        "narrative": "adventure"
    }
    try:
        # Use longer timeout for GenAI calls (60 seconds)
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{base_url}/api/profiles",
                json=test_data
            )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print(f"   ✅ Success!")
            data = response.json()
            print(f"   Profile ID: {data.get('id')}")
            print(f"   Welcome Summary (first 100 chars): {data.get('welcome_summary', '')[:100]}...")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
    except httpx.TimeoutException:
        print(f"   ⚠️  Timeout (GenAI might be slow)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_backend()

