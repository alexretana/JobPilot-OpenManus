"""
User Profiles API
FastAPI router for user profile management operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr

from app.data.models import UserProfile, JobType, RemoteType
from app.data.database import get_user_repository
from app.logger import logger

router = APIRouter(prefix="/api/users", tags=["User Profiles"])


class UserProfileCreate(BaseModel):
    """Request model for creating a user profile."""
    first_name: Optional[str] = None
    last_name: str  # Required field
    email: EmailStr  # Required field
    phone: Optional[str] = None
    current_title: Optional[str] = None
    experience_years: Optional[int] = None
    skills: List[str]  # Required field (must be non-empty list)
    education: Optional[str] = None
    bio: Optional[str] = None
    preferred_locations: List[str] = []
    preferred_job_types: List[JobType]  # Required field (must be non-empty list)
    preferred_remote_types: List[RemoteType]  # Required field (must be non-empty list)
    desired_salary_min: Optional[float] = None
    desired_salary_max: Optional[float] = None


class UserProfileUpdate(BaseModel):
    """Request model for updating a user profile."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    current_title: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[List[str]] = None
    education: Optional[str] = None
    bio: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[JobType]] = None
    preferred_remote_types: Optional[List[RemoteType]] = None
    desired_salary_min: Optional[float] = None
    desired_salary_max: Optional[float] = None


class UserProfileResponse(BaseModel):
    """Response model for user profile data."""
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    current_title: Optional[str] = None
    experience_years: Optional[int] = None
    skills: List[str] = []
    education: Optional[str] = None
    bio: Optional[str] = None
    preferred_locations: List[str] = []
    preferred_job_types: List[JobType] = []
    preferred_remote_types: List[RemoteType] = []
    desired_salary_min: Optional[float] = None
    desired_salary_max: Optional[float] = None
    created_at: datetime
    updated_at: datetime


@router.post("", response_model=UserProfileResponse, status_code=201)
async def create_user_profile(user_data: UserProfileCreate):
    """Create a new user profile."""
    try:
        user_repo = get_user_repository()
        
        # Convert to UserProfile model
        user_profile = UserProfile(**user_data.model_dump())
        
        # Create the user
        created_user = user_repo.create_user(user_profile)
        
        return UserProfileResponse(
            id=str(created_user.id),
            first_name=created_user.first_name,
            last_name=created_user.last_name,
            email=created_user.email,
            phone=created_user.phone,
            current_title=created_user.current_title,
            experience_years=created_user.experience_years,
            skills=created_user.skills,
            education=created_user.education,
            bio=created_user.bio,
            preferred_locations=created_user.preferred_locations,
            preferred_job_types=created_user.preferred_job_types,
            preferred_remote_types=created_user.preferred_remote_types,
            desired_salary_min=created_user.desired_salary_min,
            desired_salary_max=created_user.desired_salary_max,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error creating user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[UserProfileResponse])
async def list_user_profiles(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
):
    """List all user profiles with pagination."""
    try:
        user_repo = get_user_repository()
        users, total = user_repo.list_users(limit=limit, offset=offset)
        
        response_users = []
        for user in users:
            response_users.append(UserProfileResponse(
                id=str(user.id),
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone,
                current_title=user.current_title,
                experience_years=user.experience_years,
                skills=user.skills,
                education=user.education,
                bio=user.bio,
                preferred_locations=user.preferred_locations,
                preferred_job_types=user.preferred_job_types,
                preferred_remote_types=user.preferred_remote_types,
                desired_salary_min=user.desired_salary_min,
                desired_salary_max=user.desired_salary_max,
                created_at=user.created_at,
                updated_at=user.updated_at
            ))
        
        return response_users
        
    except Exception as e:
        logger.error(f"Error listing user profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """Get a specific user profile by ID."""
    try:
        user_repo = get_user_repository()
        user = user_repo.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserProfileResponse(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            current_title=user.current_title,
            experience_years=user.experience_years,
            skills=user.skills,
            education=user.education,
            bio=user.bio,
            preferred_locations=user.preferred_locations,
            preferred_job_types=user.preferred_job_types,
            preferred_remote_types=user.preferred_remote_types,
            desired_salary_min=user.desired_salary_min,
            desired_salary_max=user.desired_salary_max,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, user_data: UserProfileUpdate):
    """Update an existing user profile."""
    try:
        user_repo = get_user_repository()
        
        # Convert to dict and remove None values
        update_dict = {k: v for k, v in user_data.model_dump().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_user = user_repo.update_user(user_id, update_dict)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserProfileResponse(
            id=str(updated_user.id),
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            email=updated_user.email,
            phone=updated_user.phone,
            current_title=updated_user.current_title,
            experience_years=updated_user.experience_years,
            skills=updated_user.skills,
            education=updated_user.education,
            bio=updated_user.bio,
            preferred_locations=updated_user.preferred_locations,
            preferred_job_types=updated_user.preferred_job_types,
            preferred_remote_types=updated_user.preferred_remote_types,
            desired_salary_min=updated_user.desired_salary_min,
            desired_salary_max=updated_user.desired_salary_max,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user_profile(user_id: str):
    """Delete a user profile."""
    try:
        user_repo = get_user_repository()
        success = user_repo.delete_user(user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return None  # 204 No Content response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user profile {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/by-email", response_model=UserProfileResponse)
async def get_user_by_email(email: EmailStr = Query(..., description="Email address to search for")):
    """Get a user profile by email address."""
    try:
        user_repo = get_user_repository()
        user = user_repo.get_user_by_email(email)
        
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserProfileResponse(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            current_title=user.current_title,
            experience_years=user.experience_years,
            skills=user.skills,
            education=user.education,
            bio=user.bio,
            preferred_locations=user.preferred_locations,
            preferred_job_types=user.preferred_job_types,
            preferred_remote_types=user.preferred_remote_types,
            desired_salary_min=user.desired_salary_min,
            desired_salary_max=user.desired_salary_max,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile by email {email}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
