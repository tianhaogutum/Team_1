"""
Profile API endpoints for user questionnaire submission and profile management.

This module implements:
- POST /api/profiles - Submit questionnaire and create profile (US-03 & US-04)
- GET /api/profiles/{id} - Retrieve profile details
- PATCH /api/profiles/{id} - Update profile
"""
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    ProfileCreate,
    ProfileCreateResponse,
    ProfileResponse,
    ProfileUpdate,
)
from app.database import get_db
from app.models.entities import DemoProfile
from app.services.genai_service import generate_welcome_summary
from app.services.user_profile_service import (
    generate_fallback_welcome,
    translate_questionnaire_to_vector,
)

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_questionnaire(
    questionnaire: ProfileCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileCreateResponse:
    """
    Submit cold-start questionnaire and create user profile (US-03 & US-04).
    
    This endpoint:
    1. Translates questionnaire answers to a structured user_vector
    2. Generates a personalized welcome summary using GenAI
    3. Stores the profile in the database
    4. Returns the profile ID and welcome summary
    
    Parameters
    ----------
    questionnaire : ProfileCreate
        User's answers to the onboarding questionnaire
    db : AsyncSession
        Database session
    
    Returns
    -------
    ProfileCreateResponse
        Created profile with welcome summary and user_vector
    """
    # 1. Translate questionnaire to user_vector
    user_vector = translate_questionnaire_to_vector(questionnaire)
    
    # 2. Generate welcome summary with GenAI (with fallback)
    try:
        welcome_summary = await generate_welcome_summary(questionnaire)
    except HTTPException as e:
        # Log HTTP errors from Ollama (e.g., 503 Service Unavailable)
        logger.warning(
            f"GenAI service unavailable (status {e.status_code}), using fallback: {e.detail}",
            exc_info=True
        )
        welcome_summary = generate_fallback_welcome(questionnaire)
    except Exception as e:
        # Log other unexpected errors
        logger.warning(
            f"GenAI generation failed, using fallback: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        welcome_summary = generate_fallback_welcome(questionnaire)
    
    # 3. Create database record
    new_profile = DemoProfile(
        user_vector_json=json.dumps(user_vector, ensure_ascii=False),
        genai_welcome_summary=welcome_summary,
        total_xp=0,
        level=1,
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    
    # 4. Return response
    return ProfileCreateResponse(
        id=new_profile.id,
        welcome_summary=welcome_summary,
        user_vector=user_vector,
    )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileResponse:
    """
    Retrieve profile details by ID.
    
    Parameters
    ----------
    profile_id : int
        Profile ID
    db : AsyncSession
        Database session
    
    Returns
    -------
    ProfileResponse
        Profile details
    
    Raises
    ------
    HTTPException
        404 if profile not found
    """
    profile = await db.get(DemoProfile, profile_id)
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )
    
    return ProfileResponse.model_validate(profile)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_update: ProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileResponse:
    """
    Update profile details (partial update).
    
    Parameters
    ----------
    profile_id : int
        Profile ID
    profile_update : ProfileUpdate
        Fields to update
    db : AsyncSession
        Database session
    
    Returns
    -------
    ProfileResponse
        Updated profile
    
    Raises
    ------
    HTTPException
        404 if profile not found
    """
    profile = await db.get(DemoProfile, profile_id)
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )
    
    # Update only provided fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return ProfileResponse.model_validate(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a user profile from the database.
    
    Parameters
    ----------
    profile_id : int
        Profile ID to delete
    db : AsyncSession
        Database session
    
    Raises
    ------
    HTTPException
        404 if profile not found
    """
    profile = await db.get(DemoProfile, profile_id)
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )
    
    await db.delete(profile)
    await db.flush()  # Flush to ensure deletion is processed
    
    return None

