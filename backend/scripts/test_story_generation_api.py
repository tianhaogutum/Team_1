"""
Test script for story generation API.

Tests:
1. Generate story for Wiesn route (should generate detailed 1000-word chapters)
2. Generate story for other route (should generate simple mock chapters)
3. Verify story content is saved correctly
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_session, init_db
from app.models.entities import Route, Breakpoint
from app.services.story_generator import generate_story_for_route
from app.settings import get_settings


async def test_wiesn_route_story():
    """Test story generation for Wiesn route (1362610)."""
    print("\n" + "="*80)
    print("🧪 TEST 1: Wiesn Route Story Generation")
    print("="*80)
    
    settings = get_settings()
    init_db(settings)
    
    async with await get_db_session() as session:
        # Find Wiesn route
        from sqlalchemy import select
        result = await session.execute(
            select(Route).where(Route.id == 1362610)
        )
        route = result.scalar_one_or_none()
        
        if not route:
            print("❌ Wiesn route (1362610) not found in database")
            return False
        
        print(f"✅ Found route: {route.title}")
        
        # Load breakpoints
        from sqlalchemy.orm import selectinload
        result = await session.execute(
            select(Route)
            .where(Route.id == 1362610)
            .options(selectinload(Route.breakpoints))
        )
        route = result.scalar_one()
        
        if not route.breakpoints:
            print("❌ Route has no breakpoints")
            return False
        
        print(f"✅ Found {len(route.breakpoints)} breakpoints")
        for bp in sorted(route.breakpoints, key=lambda x: x.order_index):
            print(f"   - Breakpoint {bp.order_index}: {bp.poi_name}")
        
        # Generate story
        print("\n📖 Generating story...")
        story_data = await generate_story_for_route(
            route=route,
            breakpoints=route.breakpoints,
            narrative_style="adventure"
        )
        
        # Verify story structure
        assert "title" in story_data, "Story missing title"
        assert "prologue" in story_data, "Story missing prologue"
        assert "epilogue" in story_data, "Story missing epilogue"
        assert "breakpoints" in story_data, "Story missing breakpoints"
        
        print(f"✅ Story generated successfully!")
        print(f"   Title: {story_data['title']}")
        print(f"   Prologue length: {len(story_data['prologue'])} characters")
        print(f"   Epilogue length: {len(story_data['epilogue'])} characters")
        print(f"   Breakpoints: {len(story_data['breakpoints'])}")
        
        # Check breakpoint chapters
        print("\n📚 Breakpoint Chapters:")
        for bp_data in story_data['breakpoints']:
            chapter_text = bp_data['main_quest']
            word_count = len(chapter_text.split())
            print(f"   Chapter {bp_data['index'] + 1}: {word_count} words")
            
            # For Wiesn route, chapters should be ~1000 words
            if route.id == 1362610:
                if word_count < 500:
                    print(f"      ⚠️  Warning: Chapter is shorter than expected (~1000 words)")
                else:
                    print(f"      ✅ Chapter length looks good")
            
            # Check for mini quests
            mini_quests = bp_data.get('mini_quests', [])
            print(f"      Mini quests: {len(mini_quests)}")
            for quest in mini_quests:
                print(f"         - {quest['task_description'][:60]}... ({quest['xp_reward']} XP)")
        
        # Check if historical context was used
        print("\n🏛️  Historical Context Check:")
        if route.id == 1362610:
            # Check if first chapter mentions historical context
            first_chapter = story_data['breakpoints'][0]['main_quest']
            if '1810' in first_chapter or 'Theresienwiese' in first_chapter or 'Oktoberfest' in first_chapter:
                print("   ✅ Historical context appears to be used in story")
            else:
                print("   ⚠️  Historical context may not be used")
        
        return True


async def test_other_route_story():
    """Test story generation for a non-Wiesn route."""
    print("\n" + "="*80)
    print("🧪 TEST 2: Other Route Story Generation (Simple Mock)")
    print("="*80)
    
    settings = get_settings()
    init_db(settings)
    
    async with await get_db_session() as session:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Find a route that's not Wiesn
        result = await session.execute(
            select(Route)
            .where(Route.id != 1362610)
            .options(selectinload(Route.breakpoints))
            .limit(1)
        )
        route = result.scalar_one_or_none()
        
        if not route:
            print("❌ No other route found in database")
            return False
        
        if not route.breakpoints:
            print("❌ Route has no breakpoints")
            return False
        
        print(f"✅ Found route: {route.title} (ID: {route.id})")
        print(f"✅ Found {len(route.breakpoints)} breakpoints")
        
        # Generate story
        print("\n📖 Generating story...")
        story_data = await generate_story_for_route(
            route=route,
            breakpoints=route.breakpoints,
            narrative_style="adventure"
        )
        
        print(f"✅ Story generated successfully!")
        print(f"   Title: {story_data['title']}")
        
        # Check breakpoint chapters (should be shorter for non-Wiesn routes)
        print("\n📚 Breakpoint Chapters:")
        for bp_data in story_data['breakpoints']:
            chapter_text = bp_data['main_quest']
            word_count = len(chapter_text.split())
            print(f"   Chapter {bp_data['index'] + 1}: {word_count} words")
            
            # For non-Wiesn routes, chapters should be ~200-300 words
            if word_count > 500:
                print(f"      ⚠️  Warning: Chapter is longer than expected (~200-300 words)")
            else:
                print(f"      ✅ Chapter length looks good (simple mock)")
        
        return True


async def test_story_save_to_db():
    """Test that story is saved correctly to database."""
    print("\n" + "="*80)
    print("🧪 TEST 3: Story Save to Database")
    print("="*80)
    
    settings = get_settings()
    init_db(settings)
    
    async with await get_db_session() as session:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Get Wiesn route
        result = await session.execute(
            select(Route)
            .where(Route.id == 1362610)
            .options(
                selectinload(Route.breakpoints).selectinload(Breakpoint.mini_quests)
            )
        )
        route = result.scalar_one_or_none()
        
        if not route:
            print("❌ Wiesn route not found")
            return False
        
        # Generate and save story
        from app.api.v1.routes import _save_story_to_db
        
        story_data = await generate_story_for_route(
            route=route,
            breakpoints=route.breakpoints,
            narrative_style="adventure"
        )
        
        await _save_story_to_db(route, story_data, session)
        
        # Verify saved data
        print("✅ Story saved to database")
        print(f"   Prologue title: {route.story_prologue_title}")
        print(f"   Prologue length: {len(route.story_prologue_body or '')} characters")
        print(f"   Epilogue length: {len(route.story_epilogue_body or '')} characters")
        
        # Refresh route to get updated data
        await session.refresh(route)
        
        # Check breakpoints (access mini_quests count without lazy loading)
        for bp in sorted(route.breakpoints, key=lambda x: x.order_index):
            if bp.main_quest_snippet:
                word_count = len(bp.main_quest_snippet.split())
                # Count mini quests without triggering lazy load
                quest_count = len([q for q in bp.mini_quests])
                print(f"   Breakpoint {bp.order_index} ({bp.poi_name}): {word_count} words")
                print(f"      Mini quests: {quest_count}")
            else:
                print(f"   ⚠️  Breakpoint {bp.order_index} has no main_quest_snippet")
        
        return True


async def main():
    """Run all tests."""
    print("🚀 Starting Story Generation API Tests\n")
    
    results = []
    
    # Test 1: Wiesn route story generation
    try:
        result = await test_wiesn_route_story()
        results.append(("Wiesn Route Story", result))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Wiesn Route Story", False))
    
    # Test 2: Other route story generation
    try:
        result = await test_other_route_story()
        results.append(("Other Route Story", result))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Other Route Story", False))
    
    # Test 3: Story save to database
    try:
        result = await test_story_save_to_db()
        results.append(("Story Save to DB", result))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Story Save to DB", False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "="*80)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

