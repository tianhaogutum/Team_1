"""
Routes API endpoints for route story generation and retrieval.

This module provides endpoints for:
- Generating complete stories for routes (US-06, US-07)
- Retrieving existing story content
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.entities import Route, Breakpoint
from app.services.story_generator import generate_story_for_route
from app.api.schemas import StoryGenerateRequest, StoryGenerateResponse

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/{route_id}/generate-story", response_model=StoryGenerateResponse)
async def generate_route_story(
    route_id: int,
    request: StoryGenerateRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Generate complete story for specified route and save to database.
    
    This endpoint implements the Two-Step Global Generation approach:
    1. If story exists and force_regenerate=False, return existing (0 delay)
    2. Otherwise, generate new story using TinyLlama (10-15s)
    3. Save to database for future use
    
    Args:
        route_id: ID of the route to generate story for
        request: Story generation parameters
        db: Database session
    
    Returns:
        Complete story with title, outline, prologue, epilogue, and breakpoint content
        
    Raises:
        HTTPException: 404 if route not found, 400 if no breakpoints
    """
    # 1. Fetch route with breakpoints
    result = await db.execute(
        select(Route)
        .where(Route.id == route_id)
        .options(selectinload(Route.breakpoints))
    )
    route = result.scalar_one_or_none()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with id {route_id} not found"
        )
    
    if not route.breakpoints:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Route has no breakpoints. Cannot generate story."
        )
    
    # 2. Check if story already exists
    if route.story_prologue_body and not request.force_regenerate:
        # Return existing story (0 delay)
        return _assemble_existing_story(route)
    
    # 3. Generate new story
    story_data = await generate_story_for_route(
        route=route,
        breakpoints=route.breakpoints,
        narrative_style=request.narrative_style
    )
    
    # 4. Save to database
    await _save_story_to_db(route, story_data, db)
    
    # 5. Return result
    return StoryGenerateResponse(**story_data)


@router.get("/{route_id}/story", response_model=StoryGenerateResponse)
async def get_route_story(
    route_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Retrieve existing story for a route.
    
    Args:
        route_id: ID of the route
        db: Database session
    
    Returns:
        Existing story content
        
    Raises:
        HTTPException: 404 if route not found or no story exists
    """
    result = await db.execute(
        select(Route)
        .where(Route.id == route_id)
        .options(selectinload(Route.breakpoints))
    )
    route = result.scalar_one_or_none()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with id {route_id} not found"
        )
    
    if not route.story_prologue_body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No story generated for this route yet"
        )
    
    return _assemble_existing_story(route)


async def _save_story_to_db(
    route: Route,
    story_data: dict,
    db: AsyncSession
):
    """
    Save generated story to database.
    
    Updates Route table with prologue and epilogue,
    and Breakpoint table with main_quest and side_plot for each breakpoint.
    
    Args:
        route: Route entity to update
        story_data: Generated story data
        db: Database session
    """
    # Update Route table
    route.story_prologue_title = story_data["title"]
    route.story_prologue_body = story_data["prologue"]
    route.story_epilogue_body = story_data["epilogue"]
    
    # Update Breakpoint table
    for bp_data in story_data["breakpoints"]:
        idx = bp_data["index"]
        if idx < len(route.breakpoints):
            bp = route.breakpoints[idx]
            bp.main_quest_snippet = bp_data["main_quest"]
            bp.side_plot_snippet = bp_data["side_plot"]
    
    await db.commit()
    await db.refresh(route)


def _assemble_existing_story(route: Route) -> dict:
    """
    Assemble existing story data from database.
    
    Args:
        route: Route entity with story data
    
    Returns:
        dict matching StoryGenerateResponse format
    """
    return {
        "title": route.story_prologue_title or "Untitled Adventure",
        "outline": "Existing story outline",  # Could be stored separately if needed
        "prologue": route.story_prologue_body or "",
        "epilogue": route.story_epilogue_body or "",
        "breakpoints": [
            {
                "index": bp.order_index,
                "main_quest": bp.main_quest_snippet or "",
                "side_plot": bp.side_plot_snippet or ""
            }
            for bp in sorted(route.breakpoints, key=lambda x: x.order_index)
        ]
    }

