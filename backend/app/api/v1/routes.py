"""
Routes API endpoints for route story generation and retrieval.

This module provides endpoints for:
- Generating complete stories for routes (US-06, US-07)
- Retrieving existing story content
"""
import time
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.entities import Route, Breakpoint, DemoProfile
from app.services.story_generator import generate_story_for_route
from app.services.recommendation_service import get_recommended_routes
from app.api.schemas import (
    StoryGenerateRequest,
    StoryGenerateResponse,
    RecommendationResponse,
    RouteResponse,
)
from app.logger import get_logger, log_request, log_business_logic

logger = get_logger(__name__)

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_route_recommendations(
    profile_id: Optional[int] = None,
    category: Optional[str] = None,
    limit: int = 20,
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
):
    """
    Get route recommendations using Content-Based Filtering (CBF).
    
    This endpoint implements US-02 (personalized recommendations) and US-01 (random recommendations).
    
    Query Parameters:
    - profile_id: Optional user profile ID for personalized recommendations
    - category: Optional activity category filter (running/hiking/cycling)
    - limit: Maximum number of routes to return (default: 20)
    
    Behavior:
    - If profile_id provided: Returns routes ranked by CBF similarity score
    - If no profile_id: Returns random routes
    - If category provided: Filters results by mapped category_name values
    
    Returns:
        RecommendationResponse with routes list and metadata
    """
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info(f"🗺️ 获取路线推荐: profile_id={profile_id}, category={category}, limit={limit}")
    
    # Validate profile_id if provided and fetch profile once
    profile = None
    if profile_id is not None:
        logger.debug(f"🔍 验证用户档案: profile_id={profile_id}")
        profile = await db.get(DemoProfile, profile_id)
        if not profile:
            logger.warning(f"❌ 用户档案未找到: profile_id={profile_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile with id {profile_id} not found"
            )
        logger.debug(f"✅ 用户档案验证成功: profile_id={profile_id}")
    
    # Get recommended routes
    logger.debug("🔄 开始计算推荐路线...")
    routes = await get_recommended_routes(
        db=db,
        profile_id=profile_id,
        category=category,
        limit=limit
    )
    logger.info(f"✅ 推荐路线计算完成: 返回 {len(routes)} 条路线")
    
    # Convert to response models
    route_responses = []
    for route in routes:
        route_dict = RouteResponse.model_validate(route).model_dump()
        # Add is_locked field based on user XP (if profile exists)
        if profile:
            route_dict["is_locked"] = profile.total_xp < route.xp_required
        else:
            route_dict["is_locked"] = False
        
        # Add recommendation score if available (set by recommendation_service)
        if hasattr(route, 'recommendation_score'):
            route_dict["recommendation_score"] = route.recommendation_score
            logger.debug(f"📊 路线 {route.id} 推荐分数: {route.recommendation_score:.4f}")
        if hasattr(route, 'recommendation_score_breakdown'):
            route_dict["recommendation_score_breakdown"] = route.recommendation_score_breakdown
        
        route_responses.append(RouteResponse(**route_dict))
    
    duration_ms = (time.time() - start_time) * 1000
    is_personalized = profile_id is not None
    
    log_request(
        logger,
        "GET",
        "/api/routes/recommendations",
        status_code=200,
        duration_ms=duration_ms,
        user_id=profile_id,
        category=category,
        routes_count=len(route_responses),
        is_personalized=is_personalized
    )
    
    logger.info(f"✅ 推荐路线返回成功: {len(route_responses)} 条路线, 个性化={is_personalized}, 耗时={duration_ms:.2f}ms")
    logger.info("=" * 80)
    
    return RecommendationResponse(
        routes=route_responses,
        total=len(route_responses),
        is_personalized=is_personalized
    )


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
    2. Otherwise, generate new story using Llama3.1:8b via Ollama (10-15s)
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
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info(f"📖 生成路线故事: route_id={route_id}, narrative_style={request.narrative_style}, force_regenerate={request.force_regenerate}")
    
    # 1. Fetch route with breakpoints and mini_quests
    logger.debug(f"🔍 查询路线信息: route_id={route_id}")
    result = await db.execute(
        select(Route)
        .where(Route.id == route_id)
        .options(
            selectinload(Route.breakpoints).selectinload(Breakpoint.mini_quests)
        )
    )
    route = result.scalar_one_or_none()
    
    if not route:
        logger.error(f"❌ 路线未找到: route_id={route_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with id {route_id} not found"
        )
    
    logger.debug(f"✅ 路线查询成功: route_id={route_id}, breakpoints_count={len(route.breakpoints) if route.breakpoints else 0}")
    
    if not route.breakpoints:
        logger.error(f"❌ 路线没有断点: route_id={route_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Route has no breakpoints. Cannot generate story."
        )
    
    # 2. Check if story already exists
    if route.story_prologue_body and not request.force_regenerate:
        logger.info("📚 使用已存在的故事（跳过生成）")
        duration_ms = (time.time() - start_time) * 1000
        log_request(
            logger,
            "POST",
            f"/api/routes/{route_id}/generate-story",
            status_code=200,
            duration_ms=duration_ms,
            cached=True
        )
        logger.info(f"✅ 故事返回成功（缓存）: 耗时={duration_ms:.2f}ms")
        logger.info("=" * 80)
        return _assemble_existing_story(route)
    
    # 3. Generate new story
    logger.info("🤖 开始生成新故事...")
    story_data = await generate_story_for_route(
        route=route,
        breakpoints=route.breakpoints,
        narrative_style=request.narrative_style
    )
    logger.info("✅ 故事生成完成")
    
    # 4. Save to database
    logger.debug("💾 保存故事到数据库...")
    await _save_story_to_db(route, story_data, db)
    logger.info("✅ 故事已保存到数据库")
    
    duration_ms = (time.time() - start_time) * 1000
    log_business_logic(
        logger,
        "生成",
        "路线故事",
        entity_id=route_id,
        narrative_style=request.narrative_style,
        breakpoints_count=len(route.breakpoints)
    )
    
    log_request(
        logger,
        "POST",
        f"/api/routes/{route_id}/generate-story",
        status_code=200,
        duration_ms=duration_ms,
        cached=False
    )
    
    logger.info(f"✅ 故事生成并返回成功: 耗时={duration_ms:.2f}ms")
    logger.info("=" * 80)
    
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
        .options(
            selectinload(Route.breakpoints).selectinload(Breakpoint.mini_quests)
        )
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
    Breakpoint table with main_quest for each breakpoint,
    and MiniQuest table with generated mini quests.
    
    Args:
        route: Route entity to update
        story_data: Generated story data
        db: Database session
    """
    from app.models.entities import MiniQuest
    
    # Update Route table
    route.story_prologue_title = story_data["title"]
    route.story_prologue_body = story_data["prologue"]
    route.story_epilogue_body = story_data["epilogue"]
    
    # Update Breakpoint table and create MiniQuests
    for bp_data in story_data["breakpoints"]:
        idx = bp_data["index"]
        if idx < len(route.breakpoints):
            bp = route.breakpoints[idx]
            bp.main_quest_snippet = bp_data["main_quest"]
            
            # Clear existing mini quests for this breakpoint
            for existing_quest in bp.mini_quests:
                await db.delete(existing_quest)
            
            # Create new mini quests
            mini_quests_data = bp_data.get("mini_quests", [])
            for quest_data in mini_quests_data:
                mini_quest = MiniQuest(
                    breakpoint_id=bp.id,
                    task_description=quest_data["task_description"],
                    xp_reward=quest_data["xp_reward"]
                )
                db.add(mini_quest)
    
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
                "mini_quests": [
                    {
                        "task_description": quest.task_description,
                        "xp_reward": quest.xp_reward
                    }
                    for quest in bp.mini_quests
                ]
            }
            for bp in sorted(route.breakpoints, key=lambda x: x.order_index)
        ]
    }

