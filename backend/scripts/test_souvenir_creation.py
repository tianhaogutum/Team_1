#!/usr/bin/env python3
"""
Test script for creating a souvenir via API.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db_session, init_db
from app.models.entities import DemoProfile, Route, Souvenir
from app.api.schemas import RouteCompleteRequest
from app.api.v1.souvenirs import create_souvenir
from app.settings import get_settings


async def test_souvenir_creation():
    """Test creating a souvenir."""
    print("🧪 Testing Souvenir Creation\n")
    print("="*80)
    
    settings = get_settings()
    init_db(settings)
    
    session = await get_db_session()
    try:
        # Get first profile
        result = await session.execute(select(DemoProfile).limit(1))
        profile = result.scalar_one_or_none()
        
        if not profile:
            print("❌ No profile found. Please create a profile first.")
            return
        
        print(f"✅ Found profile: id={profile.id}, level={profile.level}, xp={profile.total_xp}")
        
        # Get first route
        result = await session.execute(
            select(Route)
            .limit(1)
            .options(selectinload(Route.breakpoints))
        )
        route = result.scalar_one_or_none()
        
        if not route:
            print("❌ No route found. Please seed the database first.")
            return
        
        print(f"✅ Found route: id={route.id}, title={route.title}")
        
        # Create request
        request = RouteCompleteRequest(
            route_id=route.id,
            completed_quest_ids=[]  # No quests completed for this test
        )
        
        print(f"\n📋 Test Request:")
        print(f"   Profile ID: {profile.id}")
        print(f"   Route ID: {request.route_id}")
        print(f"   Completed Quests: {len(request.completed_quest_ids)}")
        print("="*80)
        
        try:
            # Call the create_souvenir function
            response = await create_souvenir(
                profile_id=profile.id,
                request=request,
                db=session
            )
            
            print("\n✅ Souvenir Creation Successful!")
            print("="*80)
            print(f"📊 Souvenir ID: {response.souvenir.id}")
            print(f"⭐ XP Gained: {response.total_xp_gained}")
            print(f"📈 New Total XP: {response.new_total_xp}")
            print(f"🎯 New Level: {response.new_level}")
            print(f"🎨 SVG Generated: {'Yes' if response.souvenir.pixel_image_svg else 'No'}")
            if response.souvenir.pixel_image_svg:
                print(f"   SVG Length: {len(response.souvenir.pixel_image_svg)} characters")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(test_souvenir_creation())

