#!/usr/bin/env python3
"""
Test script for improved SVG generation with few-shot learning.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.genai_service import generate_pixel_art_svg


async def test_svg_generation():
    """Test the improved SVG generation function."""
    print("🎨 Testing Improved SVG Generation with Few-Shot Learning\n")
    print("="*80)
    
    # Test data
    route_title = "Alpine Adventure Trail"
    route_location = "Bavarian Alps, Germany"
    completed_at = datetime.now()
    xp_gained = 250
    distance_km = 8.5
    difficulty = 2  # Difficult
    
    print(f"📋 Test Parameters:")
    print(f"   Route: {route_title}")
    print(f"   Location: {route_location}")
    print(f"   XP: {xp_gained}")
    print(f"   Distance: {distance_km} km")
    print(f"   Difficulty: {difficulty}")
    print("="*80)
    print("\n🤖 Calling LLM to generate SVG...\n")
    
    try:
        svg_result = await generate_pixel_art_svg(
            route_title=route_title,
            route_location=route_location,
            completed_at=completed_at,
            xp_gained=xp_gained,
            distance_km=distance_km,
            difficulty=difficulty
        )
        
        print("\n" + "="*80)
        print("✅ SVG Generation Successful!")
        print("="*80)
        print(f"\n📏 SVG Length: {len(svg_result)} characters")
        print(f"📄 First 500 characters:")
        print("-"*80)
        print(svg_result[:500])
        print("...")
        print("-"*80)
        
        # Save to file
        output_file = Path(__file__).parent.parent.parent / "llm-generated-souvenir.svg"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(svg_result)
        
        print(f"\n💾 SVG saved to: {output_file}")
        print("="*80)
        
        return svg_result
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(test_svg_generation())

