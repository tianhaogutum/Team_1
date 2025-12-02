"""
Story generation service for creating Harry Potter themed adventure narratives.

This module implements direct story generation (no LLM calls):
- Step A: Generate story skeleton (Outline + Prologue + Epilogue)
- Step B: Generate all breakpoint content (Main Quest chapters, ~1000 words each)
- Step C: Generate mini quests for each breakpoint

All generated content is in English as per project requirements.
"""
import json
import random
import os
from pathlib import Path
from typing import Any, Optional

from app.models.entities import Route, Breakpoint


# Path to historical context data
HISTORICAL_CONTEXT_DIR = Path(__file__).parent.parent.parent / "data" / "historical_context"


def _load_historical_context(route_id: int) -> Optional[dict[int, dict[str, Any]]]:
    """
    Load historical context for a specific route.
    
    Args:
        route_id: Route ID to load context for
    
    Returns:
        Dictionary mapping order_index to historical context, or None if not found
    """
    context_file = HISTORICAL_CONTEXT_DIR / f"route_{route_id}.json"
    if not context_file.exists():
        return None
    
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert to dict indexed by order_index
            context_map = {}
            for bp in data.get('breakpoints', []):
                context_map[bp['order_index']] = bp.get('historical_context', '')
            return context_map
    except Exception as e:
        print(f"⚠️ Failed to load historical context: {e}")
        return None


def _generate_harry_potter_skeleton(route_context: dict) -> dict:
    """
    Generate Harry Potter themed story skeleton.
    
    Args:
        route_context: Formatted route information
    
    Returns:
        dict with title, outline, prologue, epilogue
    """
    route_name = route_context.get('name', 'Unknown Location')
    location = route_context.get('location', 'a mysterious place')
    
    # Generate title
    title = f"The Magical Quest of {route_name}"
    
    # Generate outline
    outline = f"A young wizard embarks on a dangerous quest to uncover ancient magical secrets hidden within {route_name}, facing challenges and mysteries at every turn."
    
    # Generate prologue
    prologue = f"""You sit in the Great Hall of Hogwarts, the morning post arriving with a flurry of owls. Among the usual letters and packages, a peculiar envelope catches your eye. It's sealed with dark green wax bearing the symbol of a wand crossed with a key.

Your hands tremble slightly as you break the seal. The letter is written in elegant, looping script:

"Dear {route_context.get('name', 'Student')},

You have been selected for a mission of utmost importance. Ancient magical artifacts have been discovered in {location}, specifically at a location known as {route_name}. These artifacts hold power that could either protect or endanger the wizarding world.

You must journey to this place and uncover the secrets hidden there. Trust no one completely, and beware—dark forces may also be seeking these artifacts.

The journey begins at dawn tomorrow. Pack your wand, your courage, and your wits.

Yours in magic,
The Order of the Phoenix"

Your heart races with excitement and apprehension. This is it—your chance to prove yourself, to become a true wizard of legend. As you fold the letter carefully, you notice a small map has been included, showing the route you must follow. Each marked point seems to pulse with magical energy.

Tomorrow, your adventure begins."""
    
    # Generate epilogue
    epilogue = f"""As you stand at the final location, the magical artifacts safely secured, you reflect on the incredible journey you've undertaken. The challenges you faced, the mysteries you solved, and the magic you witnessed have transformed you.

The letter from the Order of Phoenix was just the beginning. Through {route_name}, you've discovered not just ancient artifacts, but also your own strength, courage, and the true meaning of being a wizard.

You've learned that magic isn't just about spells and potions—it's about the connections between places, people, and history. The real world and the magical world are intertwined in ways you never imagined.

As you prepare to return to Hogwarts, you know this adventure has changed you forever. You're no longer just a student; you're a true wizard, ready to face whatever challenges lie ahead.

The journey may be over, but your magical story has only just begun."""
    
    return {
        "title": title,
        "outline": outline,
        "prologue": prologue,
        "epilogue": epilogue
    }


def _generate_harry_potter_chapter(
    chapter_num: int,
    total_chapters: int,
    poi_name: str,
    poi_type: str,
    historical_context: Optional[str],
    previous_chapter_summary: str = "",
    next_location_hint: str = "",
    is_wiesn_route: bool = False
) -> str:
    """
    Generate a ~1000 word Harry Potter themed chapter for a breakpoint.
    
    Args:
        chapter_num: Chapter number (0-indexed)
        total_chapters: Total number of chapters
        poi_name: Name of the POI/breakpoint
        poi_type: Type of the POI
        historical_context: Historical context for this location (if available)
        previous_chapter_summary: Brief summary of previous chapter for continuity
        next_location_hint: Hint about next location
        is_wiesn_route: Whether this is the Wiesn route (for detailed generation)
    
    Returns:
        Full chapter text (~1000 words for Wiesn, shorter for others)
    """
    # Base chapter structure
    chapter_intro = f"""Chapter {chapter_num + 1}: The Mystery of {poi_name}

"""
    
    # For non-Wiesn routes, use simple mock data
    if not is_wiesn_route:
        return _generate_simple_mock_chapter(
            chapter_num, poi_name, poi_type, previous_chapter_summary, next_location_hint
        )
    
    # For Wiesn route, generate detailed content with historical context
    # Opening paragraph - arrival and atmosphere
    if historical_context:
        # Extract key historical facts for richer storytelling
        opening = f"""You arrive at {poi_name}, and immediately you sense something extraordinary. The air itself seems to shimmer with residual magic, as if centuries of magical events have left their mark on this place. 

According to the historical records you've studied, {historical_context}. This knowledge makes the location even more significant. You can almost feel the weight of history pressing down on you, mingling with the magical energy that permeates the area. The Muggles who visit this place see only the surface—the celebrations, the architecture, the traditions. But you, as a wizard, can perceive the deeper magical currents that flow beneath.

Your wand feels warm in your hand, reacting to the magical presence. You whisper "Lumos," and the tip of your wand glows brighter than usual, illuminating details that would be invisible to Muggles. The very stones beneath your feet seem to pulse with ancient power, and you realize that this location has been a nexus of magical energy for far longer than the Muggles have been celebrating here.

"""
    else:
        opening = f"""You arrive at {poi_name}, and immediately you sense something extraordinary. The air itself seems to shimmer with residual magic, as if centuries of magical events have left their mark on this place.

Your wand feels warm in your hand, reacting to the magical presence. You whisper "Lumos," and the tip of your wand glows brighter than usual, illuminating details that would be invisible to Muggles.

"""
    
    # Middle section - action and discovery (enhanced for Wiesn with historical context)
    if historical_context:
        middle = f"""{previous_chapter_summary if previous_chapter_summary else "Following the map from the Order of Phoenix,"} you carefully examine the area. Your training at Hogwarts has prepared you for this moment, but nothing could have prepared you for the depth of magical history embedded in this place.

As you explore, you notice something peculiar. There's a pattern in the way the magical energy flows—it's not random, but deliberate, as if the very history of this location has been woven into a magical tapestry. The celebrations that Muggles see are merely the surface manifestation of something far deeper and more ancient.

You pull out your wand and cast a revealing charm. "Revelio!" The spell reveals hidden magical markers, glowing runes that only appear to those with magical sight. They form a path, leading you deeper into the mystery of this location. The runes seem to tell a story that connects the Muggle history you've learned about with the hidden magical history that has been kept secret for generations.

The historical significance of this place—{historical_context[:150]}...—takes on new meaning when viewed through magical eyes. You realize that the events that happened here in the Muggle world were not coincidences, but were influenced by the magical community working behind the scenes.

The runes tell a story—ancient, powerful magic that has been dormant for years, waiting for the right moment, the right wizard, to awaken it. You realize that this isn't just a quest; it's a test. The Order of Phoenix wants to see if you're worthy of the power that lies hidden here, power that has been protected by generations of wizards who understood the importance of this location.

"""
    else:
        middle = f"""{previous_chapter_summary if previous_chapter_summary else "Following the map from the Order of Phoenix,"} you carefully examine the area. Your training at Hogwarts has prepared you for this moment. You know how to look for magical traces, how to sense hidden enchantments, and how to protect yourself from potential dangers.

As you explore, you notice something peculiar. There's a pattern in the way the magical energy flows—it's not random, but deliberate. Someone, or something, has been here recently. The magical signature is fresh, which means you're not alone in this quest.

You pull out your wand and cast a revealing charm. "Revelio!" The spell reveals hidden magical markers, glowing runes that only appear to those with magical sight. They form a path, leading you deeper into the mystery of this location.

The runes tell a story—ancient, powerful magic that has been dormant for years, waiting for the right moment, the right wizard, to awaken it. You realize that this isn't just a quest; it's a test. The Order of Phoenix wants to see if you're worthy of the power that lies hidden here.

"""
    
    # Discovery and challenge
    discovery = f"""Suddenly, you hear a sound—the rustle of fabric, the snap of a twig. You spin around, wand raised, ready to defend yourself. But instead of an enemy, you see a figure emerging from the shadows.

"Who's there?" you call out, your voice steady despite the adrenaline coursing through your veins.

A voice responds, calm and measured: "A friend. Or at least, someone who shares your goal."

The figure steps into the light, and you see another wizard—older, with a weathered face and eyes that have seen too much. They're wearing robes that mark them as a member of a different magical organization, but their wand is lowered, showing no hostile intent.

"I've been tracking the same magical signatures," they explain. "The artifacts you seek are real, and they're more powerful than the Order of Phoenix may have told you. But there are others—dark wizards—who also want them."

Your heart pounds. This is more dangerous than you anticipated. "What do you want?" you ask, keeping your wand ready.

"To help you," they say. "But first, you must prove yourself. This location holds a test. Pass it, and you'll gain access to the next clue. Fail, and..." They don't finish the sentence, but the implication is clear.

"""
    
    # The test/challenge (enhanced for Wiesn)
    if historical_context:
        challenge = f"""The mysterious wizard gestures, and the magical runes you saw earlier begin to glow brighter, forming a complex pattern on the ground. You recognize it as an ancient magical test—a trial that wizards of old used to determine worthiness.

"You must solve this puzzle," the wizard explains. "The answer lies in understanding the history of this place, in seeing beyond what Muggles see, in recognizing the magic that binds everything together. The history you've learned about {poi_name} is not just Muggle history—it's intertwined with our magical world in ways you're about to discover."

You study the pattern, your mind racing. The historical context you learned about this location suddenly becomes crucial. The runes aren't just random symbols—they're connected to the real history of {poi_name}, to the events that happened here, to the people who once walked these grounds. You think about {historical_context[:100]}... and how these events might have been influenced by or influenced the magical world.

You think back to everything you know about this place, combining your magical knowledge with the historical facts. The solution begins to form in your mind, piece by piece, like a complex spell coming together. You realize that the answer requires understanding both the Muggle history and the hidden magical significance of this location.

"""
    else:
        challenge = f"""The mysterious wizard gestures, and the magical runes you saw earlier begin to glow brighter, forming a complex pattern on the ground. You recognize it as an ancient magical test—a trial that wizards of old used to determine worthiness.

"You must solve this puzzle," the wizard explains. "The answer lies in understanding the history of this place, in seeing beyond what Muggles see, in recognizing the magic that binds everything together."

You study the pattern, your mind racing. The historical context you learned about this location suddenly becomes crucial. The runes aren't just random symbols—they're connected to the real history of {poi_name}, to the events that happened here, to the people who once walked these grounds.

You think back to everything you know about this place, combining your magical knowledge with the historical facts. The solution begins to form in your mind, piece by piece, like a complex spell coming together.

"""
    
    # Resolution and cliffhanger
    resolution = f"""With a deep breath, you step forward and trace the correct pattern with your wand. The runes respond immediately, glowing brighter and brighter until they form a path of light leading away from this location.

"You've passed the test," the mysterious wizard says, a hint of approval in their voice. "But this is only the beginning. The next location holds even greater challenges, and the dark wizards are closing in. You must move quickly."

They hand you a small, enchanted object—a compass that points not to north, but to the next location on your quest. "Use this wisely," they warn. "And remember: not everything is as it seems. Trust your instincts, but verify everything."

As they disappear into the shadows, you look at the compass. It's pointing toward {next_location_hint if next_location_hint else "your next destination"}. The magical path you've created glows invitingly, but you know that danger awaits.

You've uncovered the first secret, passed the first test, but you're only at the beginning of your journey. The real challenges lie ahead, and you must be ready for whatever comes next.

The adventure continues..."""
    
    # Combine all parts
    full_chapter = chapter_intro + opening + middle + discovery + challenge + resolution
    
    # Ensure it's approximately 1000 words (rough estimate: ~150 words per section)
    # The current structure should be close to 1000 words
    return full_chapter


def _generate_simple_mock_chapter(
    chapter_num: int,
    poi_name: str,
    poi_type: str,
    previous_chapter_summary: str = "",
    next_location_hint: str = ""
) -> str:
    """
    Generate a simple mock chapter for non-Wiesn routes.
    
    Args:
        chapter_num: Chapter number (0-indexed)
        poi_name: Name of the POI/breakpoint
        poi_type: Type of the POI
        previous_chapter_summary: Brief summary of previous chapter
        next_location_hint: Hint about next location
    
    Returns:
        Simple chapter text (~200-300 words)
    """
    chapter_intro = f"""Chapter {chapter_num + 1}: {poi_name}

"""
    
    content = f"""{previous_chapter_summary if previous_chapter_summary else "Following your magical quest,"} you arrive at {poi_name}. 

As a wizard exploring this {poi_type}, you immediately sense the magical energy that flows through this place. Your wand responds to the ancient magic that has been woven into the very fabric of this location over the centuries.

You take a moment to observe your surroundings. The magical signature here is strong, indicating that this place has been touched by powerful wizarding events in the past. You can feel the presence of ancient spells and enchantments that have been layered upon this location.

Following the guidance from the Order of Phoenix, you search for clues and magical markers. Your training at Hogwarts has prepared you well for this moment. You know how to recognize the signs of hidden magic, how to read the magical traces left behind by previous wizards.

After a thorough investigation, you discover a small magical artifact—a token that will guide you to your next destination. The artifact glows softly in your hand, pointing toward {next_location_hint if next_location_hint else "the next location on your quest"}.

You've made progress, but the journey continues. The real challenges and mysteries lie ahead, waiting to be uncovered by a worthy wizard.

The adventure continues..."""
    
    return chapter_intro + content


def _generate_mini_quests(
    chapter_num: int,
    total_chapters: int,
    poi_name: str,
    poi_type: str
) -> list[dict[str, Any]]:
    """
    Generate 1-2 mini quests for a breakpoint.
    
    Args:
        chapter_num: Chapter number (0-indexed)
        total_chapters: Total number of chapters
        poi_name: Name of the POI/breakpoint
        poi_type: Type of the POI
    
    Returns:
        List of mini quest dicts with task_description and xp_reward
    """
    # Quest types with Harry Potter themed descriptions
    quest_templates = {
        "photo": {
            "descriptions": [
                f"Use your enchanted camera to capture the magical essence of {poi_name}. The photograph will reveal hidden magical properties invisible to Muggles.",
                f"Take a magical photograph of {poi_name} using the special camera provided by the Order of Phoenix. The image will help document your quest.",
                f"Capture the mystical aura of {poi_name} with your enchanted camera. This magical photograph will be added to your collection of evidence."
            ],
            "base_xp": 15,
            "type": "photo"
        },
        "observation": {
            "descriptions": [
                f"Carefully observe {poi_name} and identify any magical signatures or hidden enchantments. Use your magical sight to see what Muggles cannot.",
                f"Examine {poi_name} closely for signs of ancient magic. Look for runes, magical symbols, or traces of spellwork that might reveal secrets.",
                f"Study the magical properties of {poi_name}. Your trained eye can spot details that will be crucial to solving the mystery."
            ],
            "base_xp": 20
        },
        "collection": {
            "descriptions": [
                f"Collect magical evidence from {poi_name}. Look for enchanted objects, magical traces, or clues left behind by previous wizards.",
                f"Gather magical artifacts or clues hidden at {poi_name}. These items will help you piece together the puzzle of your quest.",
                f"Search for and collect any magical items or traces at {poi_name}. Each piece of evidence brings you closer to the truth."
            ],
            "base_xp": 25
        },
        "puzzle": {
            "descriptions": [
                f"Solve the magical puzzle hidden at {poi_name}. The solution requires combining your knowledge of magic with the history of this location.",
                f"Decipher the ancient riddle or puzzle at {poi_name}. Your wizarding education has prepared you for this challenge.",
                f"Unlock the magical mystery at {poi_name} by solving the puzzle. The answer lies in understanding both magic and history."
            ],
            "base_xp": 30,
            "generate_quiz": True  # Flag to generate actual quiz
        }
    }
    
    # Determine number of quests (1-2, with higher chance of 2 quests for later chapters)
    num_quests = 2 if random.random() < (0.3 + chapter_num * 0.1) else 1
    num_quests = min(num_quests, 2)  # Max 2 quests
    
    # Select quest types (avoid duplicates)
    available_types = list(quest_templates.keys())
    selected_types = random.sample(available_types, num_quests)
    
    # Generate quests
    quests = []
    for quest_type in selected_types:
        template = quest_templates[quest_type]
        description = random.choice(template["descriptions"])
        
        # XP increases with chapter number (later chapters = harder quests = more XP)
        xp_multiplier = 1.0 + (chapter_num / total_chapters) * 0.5
        xp_reward = int(template["base_xp"] * xp_multiplier)
        
        quest_data = {
            "task_description": description,
            "xp_reward": xp_reward
        }
        
        # For puzzle quests, generate actual quiz question and answers
        if quest_type == "puzzle" and template.get("generate_quiz", False):
            quiz_data = _generate_quiz_question(poi_name, poi_type, chapter_num)
            # Store quiz data as JSON in task_description
            quest_data["task_description"] = json.dumps({
                "type": "quiz",
                "description": description,
                "question": quiz_data["question"],
                "choices": quiz_data["choices"],
                "correct_answer": quiz_data["correct_answer"]
            })
        # For photo quests, store type in JSON for easier parsing
        elif quest_type == "photo" and template.get("type") == "photo":
            quest_data["task_description"] = json.dumps({
                "type": "photo",
                "description": description
            })
        
        quests.append(quest_data)
    
    return quests


def _generate_quiz_question(
    poi_name: str,
    poi_type: str,
    chapter_num: int
) -> dict[str, Any]:
    """
    Generate a Harry Potter themed quiz question for puzzle quests.
    
    Args:
        poi_name: Name of the POI
        poi_type: Type of the POI
        chapter_num: Chapter number
    
    Returns:
        dict with question, choices, and correct_answer
    """
    # Quiz question templates
    quiz_templates = [
        {
            "question": f"What magical property makes {poi_name} significant to wizards?",
            "choices": [
                "It's a convergence point of ancient magical energy",
                "It's where the first wand was created",
                "It's a portal to another dimension",
                "It's where dragons once nested"
            ],
            "correct_answer": 0
        },
        {
            "question": f"Which spell would be most effective for revealing hidden magic at {poi_name}?",
            "choices": [
                "Revelio",
                "Lumos",
                "Accio",
                "Expelliarmus"
            ],
            "correct_answer": 0
        },
        {
            "question": f"What does the magical signature at {poi_name} indicate?",
            "choices": [
                "Ancient wizarding activity",
                "Recent dark magic",
                "A magical creature's presence",
                "A broken enchantment"
            ],
            "correct_answer": 0
        },
        {
            "question": f"Which Hogwarts house would be most interested in the history of {poi_name}?",
            "choices": [
                "Ravenclaw",
                "Gryffindor",
                "Slytherin",
                "Hufflepuff"
            ],
            "correct_answer": 0
        },
        {
            "question": f"What type of magical protection would be most appropriate for {poi_name}?",
            "choices": [
                "Concealment charms",
                "Fiendfyre",
                "Unforgivable Curses",
                "Love potions"
            ],
            "correct_answer": 0
        },
        {
            "question": f"According to magical theory, what makes {poi_type} locations particularly magical?",
            "choices": [
                "They accumulate magical energy over centuries",
                "They're built on ley lines",
                "They're protected by ancient guardians",
                "All of the above"
            ],
            "correct_answer": 3
        }
    ]
    
    # Select a random quiz template
    selected_quiz = random.choice(quiz_templates)
    
    return {
        "question": selected_quiz["question"],
        "choices": selected_quiz["choices"],
        "correct_answer": selected_quiz["correct_answer"]
    }


async def generate_story_for_route(
    route: Route,
    breakpoints: list[Breakpoint],
    narrative_style: str = "adventure"
) -> dict[str, Any]:
    """
    Generate complete Harry Potter themed story for a route.
    
    This function orchestrates the story generation process:
    1. Generates story skeleton (outline, prologue, epilogue)
    2. Generates content for all breakpoints (1000-word chapters)
    3. Generates mini quests for each breakpoint (1-2 quests per breakpoint)
    4. Returns assembled story data
    
    Args:
        route: Route entity with basic information
        breakpoints: List of breakpoint entities in order
        narrative_style: Story style (not used in direct generation, kept for API compatibility)
    
    Returns:
        dict containing:
            - title: Story title
            - outline: Mission summary
            - prologue: Opening chapter
            - epilogue: Closing chapter
            - breakpoints: List of breakpoint content dicts with:
                - index: Breakpoint index
                - main_quest: Chapter text (~1000 words)
                - mini_quests: List of mini quest dicts with task_description and xp_reward
    """
    # 1. Prepare context
    route_context = _format_route_info(route)
    
    # 2. Load historical context if available (for Wiesn route)
    historical_context_map = None
    if route.id == 1362610:  # Wiesn route
        historical_context_map = _load_historical_context(route.id)
    
    # 3. Generate skeleton
    skeleton = _generate_harry_potter_skeleton(route_context)
    
    # 4. Generate story chapters for each breakpoint
    story_points = []
    previous_summary = ""
    
    for i, bp in enumerate(sorted(breakpoints, key=lambda x: x.order_index)):
        # Get historical context for this breakpoint
        hist_context = None
        if historical_context_map:
            hist_context = historical_context_map.get(bp.order_index)
        
        # Get hint about next location
        next_hint = ""
        if i + 1 < len(breakpoints):
            next_bp = sorted(breakpoints, key=lambda x: x.order_index)[i + 1]
            next_hint = next_bp.poi_name or f"the next location"
        
        # Generate chapter (detailed for Wiesn route, simple mock for others)
        is_wiesn = route.id == 1362610
        chapter_text = _generate_harry_potter_chapter(
            chapter_num=i,
            total_chapters=len(breakpoints),
            poi_name=bp.poi_name or f"Location {i + 1}",
            poi_type=bp.poi_type or "location",
            historical_context=hist_context,
            previous_chapter_summary=previous_summary,
            next_location_hint=next_hint,
            is_wiesn_route=is_wiesn
        )
        
        # Generate mini quests for this breakpoint
        mini_quests = _generate_mini_quests(
            chapter_num=i,
            total_chapters=len(breakpoints),
            poi_name=bp.poi_name or f"Location {i + 1}",
            poi_type=bp.poi_type or "location"
        )
        
        # Create summary for next chapter
        previous_summary = f"After uncovering the secrets of {bp.poi_name or f'Location {i + 1}'},"
        
        story_points.append({
            "index": i,
            "main_quest": chapter_text,
            "mini_quests": mini_quests
        })
    
    # 5. Log generation
    print("\n" + "="*80)
    print("✨ HARRY POTTER STORY GENERATED")
    print("="*80)
    print(f"🗺️ Route: {route_context.get('name', 'Unknown')}")
    print(f"📖 Title: {skeleton.get('title', 'N/A')}")
    print(f"📊 Generated {len(story_points)} chapters")
    print("="*80 + "\n")
    
    # Log to UI
    from app.llm_logger import log_llm_output
    log_llm_output(
        message_type="skeleton",
        title=f"📖 Story Generated: {skeleton.get('title', 'Adventure')}",
        content=f"**Outline:** {skeleton.get('outline', 'N/A')}\n\n**Prologue:** {skeleton.get('prologue', 'N/A')[:200]}...\n\n**Epilogue:** {skeleton.get('epilogue', 'N/A')[:200]}...",
        metadata={
            "route_name": route_context.get('name', 'Unknown'),
            "narrative_style": "harry_potter",
            "title": skeleton.get('title', 'N/A')
        }
    )
    
    # 6. Assemble and return
    return {
        **skeleton,
        "breakpoints": story_points
    }


def _format_route_info(route: Route) -> dict:
    """
    Format route information for context.
    
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
