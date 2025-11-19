"""
Story generation service for creating coherent route narratives.

This module implements the Two-Step Global Generation approach:
- Step A: Generate story skeleton (Outline + Prologue + Epilogue)
- Step B: Batch generate all breakpoint content (Main Quest + Side Plot)

All generated content is in English as per project requirements.
"""
import json
from typing import Any

from app.models.entities import Route, Breakpoint
from app.services.genai_service import call_ollama, NARRATIVE_STYLE_PROMPTS


async def generate_story_for_route(
    route: Route,
    breakpoints: list[Breakpoint],
    narrative_style: str = "adventure"
) -> dict[str, Any]:
    """
    Generate complete coherent story for a route using two-step method.
    
    This function orchestrates the story generation process:
    1. Generates story skeleton (outline, prologue, epilogue)
    2. Batch generates content for all breakpoints
    3. Returns assembled story data
    
    Args:
        route: Route entity with basic information
        breakpoints: List of breakpoint entities in order
        narrative_style: Story style (adventure/mystery/playful)
    
    Returns:
        dict containing:
            - title: Story title
            - outline: Mission summary
            - prologue: Opening chapter
            - epilogue: Closing chapter
            - breakpoints: List of breakpoint content dicts
    """
    # 1. Prepare context
    route_context = _format_route_info(route)
    poi_list = _format_poi_list(breakpoints)
    
    # 2. Step A: Generate skeleton
    skeleton = await _generate_skeleton(
        route_context=route_context,
        narrative_style=narrative_style
    )
    
    # 3. Step B: Batch generate story points
    story_points = await _generate_story_points(
        skeleton=skeleton,
        poi_list=poi_list,
        num_points=len(breakpoints),
        narrative_style=narrative_style  # Pass narrative style through
    )
    
    # 4. Assemble and return
    return {
        **skeleton,
        "breakpoints": story_points
    }


def _format_route_info(route: Route) -> dict:
    """
    Format route information for prompt context.
    
    Args:
        route: Route entity
    
    Returns:
        dict with formatted route information
    """
    return {
        "name": route.title,
        "location": route.category_name or "Unknown",
        "distance_km": round(route.length_meters / 1000, 1) if route.length_meters else 0,
        "difficulty": route.difficulty or 0,
        "tags": json.loads(route.tags_json) if route.tags_json else [],
        "description": route.short_description or ""
    }


def _format_poi_list(breakpoints: list[Breakpoint]) -> str:
    """
    Format POI list as numbered list for prompt.
    
    Args:
        breakpoints: List of breakpoint entities
    
    Returns:
        Formatted string with numbered POI list
    """
    poi_lines = []
    for bp in breakpoints:
        poi_name = bp.poi_name or f"Point {bp.order_index + 1}"
        poi_type = bp.poi_type or "location"
        poi_lines.append(f"{bp.order_index}. {poi_name} (Type: {poi_type})")
    return "\n".join(poi_lines)


async def _generate_skeleton(route_context: dict, narrative_style: str) -> dict:
    """
    Generate story skeleton (Outline + Prologue + Epilogue).
    
    Args:
        route_context: Formatted route information
        narrative_style: Desired story style
    
    Returns:
        dict with title, outline, prologue, epilogue
    """
    # Get detailed narrative style instructions from centralized prompts
    narrative_hint = NARRATIVE_STYLE_PROMPTS.get(
        narrative_style,
        NARRATIVE_STYLE_PROMPTS["adventure"]  # Default to adventure
    )
    
    # Extract tags as string
    tags_str = ', '.join(str(t.get('text', t)) if isinstance(t, dict) else str(t) 
                         for t in route_context['tags'][:5]) if route_context['tags'] else "outdoor adventure"
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a master storyteller for outdoor adventures. Create a story framework for this route.

The narrative style must follow this description: "{narrative_hint}"

You must respond with ONLY valid JSON in this exact format:
{{
  "title": "Story title (max 10 words)",
  "outline": "One sentence describing the hero's mission or goal",
  "prologue": "Opening scene that sets the mood and introduces the quest (100-120 words)",
  "epilogue": "Closing reflection on the completed journey (100-120 words)"
}}

All content must be in English.<|eot_id|><|start_header_id|>user<|end_header_id|>

Route Name: {route_context['name']}
Location: {route_context['location']}
Distance: {route_context['distance_km']} km
Difficulty: {route_context['difficulty']}/6
Tags: {tags_str}

Generate the story framework in JSON format.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    try:
        response = await call_ollama(
            prompt=prompt,
            max_tokens=500,
            temperature=0.5
        )
        
        # Ollama returns complete JSON, no need to add opening brace
        full_response = response
        
        # Extract JSON from response (handle potential markdown code blocks)
        json_str = full_response
        if "```json" in full_response:
            json_str = full_response.split("```json")[1].split("```")[0].strip()
        elif "```" in full_response:
            json_str = full_response.split("```")[1].split("```")[0].strip()
        
        # Find JSON object boundaries
        json_start = json_str.find('{')
        json_end = json_str.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = json_str[json_start:json_end]
        
        # Parse JSON
        result = json.loads(json_str)
        
        # Validate required fields
        if not all(key in result for key in ['title', 'outline', 'prologue', 'epilogue']):
            raise ValueError("Missing required fields in response")
        
        return result
            
    except Exception as e:
        # Fallback skeleton if parsing fails
        print(f"⚠️ Skeleton generation failed: {str(e)}, using fallback")
        return {
            "title": f"Adventure at {route_context['name']}",
            "outline": "Embark on a journey to discover the beauty of nature.",
            "prologue": "Your adventure begins here. The path ahead is full of wonder and challenge. Each step brings you closer to understanding the magic of this place.",
            "epilogue": "As your journey ends, you carry these memories forward. The trail has taught you something valuable about yourself and the world."
        }


async def _generate_story_points(
    skeleton: dict,
    poi_list: str,
    num_points: int,
    narrative_style: str = "adventure"
) -> list[dict]:
    """
    Batch generate story content for ALL breakpoints.
    
    Args:
        skeleton: Generated story skeleton
        poi_list: Formatted POI list
        num_points: Number of breakpoints to generate
        narrative_style: Narrative style to maintain consistency
    
    Returns:
        list of dicts with index, main_quest, side_plot
    """
    # Get detailed narrative style instructions
    narrative_hint = NARRATIVE_STYLE_PROMPTS.get(
        narrative_style,
        NARRATIVE_STYLE_PROMPTS["adventure"]
    )
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a game master creating checkpoint narratives for a story.

The narrative style must follow this description: "{narrative_hint}"

For EACH checkpoint, write TWO distinct snippets:

1. MAIN_QUEST (40-60 words): Advance the main plot. This continues the story from prologue through each point to epilogue. Must be narrative progression.
2. SIDE_PLOT (30-40 words): Describe ONLY this location's visual/historical details. DO NOT advance the plot. Focus on atmosphere and POI characteristics.

You must respond with ONLY valid JSON array format:
[
  {{
    "index": 0,
    "main_quest": "Main quest narrative text here",
    "side_plot": "Side plot description here"
  }},
  {{
    "index": 1,
    "main_quest": "...",
    "side_plot": "..."
  }}
]

All content must be in English.<|eot_id|><|start_header_id|>user<|end_header_id|>

Story Framework:
- Title: {skeleton.get('title', 'Adventure')}
- Mission: {skeleton.get('outline', 'Explore the route')}
- Prologue: {skeleton.get('prologue', '')[:200]}
- Epilogue: {skeleton.get('epilogue', '')[:200]}

Generate narratives for these {num_points} checkpoints in order:
{poi_list}

The main_quest must flow smoothly: Prologue → Point 0 → Point 1 → ... → Point {num_points-1} → Epilogue<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    try:
        response = await call_ollama(
            prompt=prompt,
            max_tokens=num_points * 180,  # ~180 tokens per point for JSON format
            temperature=0.6
        )
        
        # Ollama returns complete JSON array, no need to add opening bracket
        full_response = response
        
        # Extract JSON from response (handle potential markdown code blocks)
        json_str = full_response
        if "```json" in full_response:
            json_str = full_response.split("```json")[1].split("```")[0].strip()
        elif "```" in full_response:
            json_str = full_response.split("```")[1].split("```")[0].strip()
        
        # Find JSON array boundaries
        json_start = json_str.find('[')
        json_end = json_str.rfind(']') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = json_str[json_start:json_end]
        
        # Parse JSON
        story_points = json.loads(json_str)
        
        # Validate structure
        if not isinstance(story_points, list):
            raise ValueError("Response is not a JSON array")
        
        for point in story_points:
            if not all(key in point for key in ['index', 'main_quest', 'side_plot']):
                raise ValueError("Missing required fields in story point")
            
    except Exception as e:
        # Fallback: generate template points
        print(f"⚠️ Story points generation failed: {str(e)}, using fallback")
        story_points = []
    
    # Ensure we have enough points with contextualized fallbacks
    if len(story_points) < num_points:
        # Try to get POI names from the list
        poi_lines = poi_list.split('\n')
        for i in range(len(story_points), num_points):
            poi_name = f"checkpoint {i}"
            if i < len(poi_lines):
                # Extract POI name from formatted list
                parts = poi_lines[i].split('. ', 1)
                if len(parts) > 1:
                    poi_name = parts[1].split(' (')[0]
            
            story_points.append({
                "index": i,
                "main_quest": f"You press forward on your quest, each step bringing you closer to understanding this place's true nature. At {poi_name}, you pause to reflect on how far you've come and how much further there is to go.",
                "side_plot": f"The area surrounding {poi_name} has its own distinct character. The landscape tells a story of time and nature working together to create something beautiful and unique."
            })
    
    # Ensure correct indices and return only needed points
    for i, point in enumerate(story_points[:num_points]):
        point["index"] = i
    
    return story_points[:num_points]

