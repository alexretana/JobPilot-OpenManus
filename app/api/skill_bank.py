"""
Skill Bank API
FastAPI router for skill bank management operations.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

from app.data.database import get_database_manager
from app.data.skill_bank_models import (
    Certification,
    ContentFocusType,
    ContentSource,
    EducationContentVariation,
    EducationEntry,
    EnhancedSkill,
    ExperienceContentVariation,
    ExperienceEntry,
    ExperienceType,
    ProjectContentVariation,
    ProjectEntry,
    SkillCategory,
    SkillLevel,
    SummaryVariation,
)
from app.data.skill_bank_repository import SkillBankRepository
from app.logger import logger

router = APIRouter(prefix="/api/skill-bank", tags=["Skill Bank"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class SkillBankResponse(BaseModel):
    """Response model for skill bank data."""

    id: str
    user_id: str
    skills: Dict[str, List[EnhancedSkill]]
    skill_categories: List[str]
    default_summary: Optional[str] = None
    summary_variations: List[SummaryVariation]
    work_experiences: List[ExperienceEntry]
    education_entries: List[EducationEntry]
    projects: List[ProjectEntry]
    certifications: List[Certification]
    experience_content_variations: Dict[str, List[ExperienceContentVariation]]
    education_content_variations: Dict[str, List[EducationContentVariation]]
    project_content_variations: Dict[str, List[ProjectContentVariation]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillBankUpdateRequest(BaseModel):
    """Request model for updating skill bank."""

    default_summary: Optional[str] = None
    skill_categories: Optional[List[str]] = None


class EnhancedSkillRequest(BaseModel):
    """Request model for creating/updating enhanced skills."""

    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE
    category: SkillCategory = SkillCategory.TECHNICAL
    subcategory: Optional[str] = None
    years_experience: Optional[int] = None
    proficiency_score: Optional[float] = None
    description: Optional[str] = None
    keywords: List[str] = []
    is_featured: bool = False
    display_order: int = 0
    source: ContentSource = ContentSource.MANUAL


class SkillUpdateRequest(BaseModel):
    """Request model for updating a skill."""

    name: Optional[str] = None
    level: Optional[SkillLevel] = None
    category: Optional[SkillCategory] = None
    subcategory: Optional[str] = None
    years_experience: Optional[int] = None
    proficiency_score: Optional[float] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None


class SummaryVariationRequest(BaseModel):
    """Request model for creating summary variations."""

    title: str
    content: str
    tone: str = "professional"
    length: str = "standard"
    focus: ContentFocusType = ContentFocusType.GENERAL
    target_industries: List[str] = []
    target_roles: List[str] = []
    keywords_emphasized: List[str] = []


class ExperienceEntryRequest(BaseModel):
    """Request model for creating experience entries."""

    company: str
    position: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    experience_type: ExperienceType = ExperienceType.FULL_TIME
    default_description: Optional[str] = None
    default_achievements: List[str] = []
    skills_used: List[str] = []
    technologies: List[str] = []


class ExperienceContentVariationRequest(BaseModel):
    """Request model for creating experience content variations."""

    experience_id: str
    title: str
    content: str
    focus: ContentFocusType = ContentFocusType.GENERAL
    achievements: List[str] = []
    skills_highlighted: List[str] = []
    target_industries: List[str] = []
    target_roles: List[str] = []
    keywords_emphasized: List[str] = []


class EducationEntryRequest(BaseModel):
    """Request model for creating education entries."""

    institution: str
    degree: str
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    honors: List[str] = []
    relevant_coursework: List[str] = []
    default_description: Optional[str] = None


class ProjectEntryRequest(BaseModel):
    """Request model for creating project entries."""

    name: str
    url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    default_description: Optional[str] = None
    default_achievements: List[str] = []
    technologies: List[str] = []


class CertificationRequest(BaseModel):
    """Request model for creating certification entries."""

    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


# =============================================================================
# MAIN SKILL BANK ENDPOINTS
# =============================================================================


@router.get("/{user_id}", response_model=SkillBankResponse)
async def get_skill_bank(user_id: str = Path(..., description="User ID")):
    """Get user's complete skill bank."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        skill_bank = await skill_bank_repo.get_skill_bank(user_id)
        if not skill_bank:
            # Create default skill bank if it doesn't exist
            skill_bank = await skill_bank_repo.create_skill_bank(user_id)

        return SkillBankResponse(**skill_bank.dict())

    except Exception as e:
        logger.error(f"Error getting skill bank for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=SkillBankResponse)
async def update_skill_bank(
    update_request: SkillBankUpdateRequest,
    user_id: str = Path(..., description="User ID"),
):
    """Update skill bank basic information."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        updates = {}
        if update_request.default_summary is not None:
            updates["default_summary"] = update_request.default_summary
        if update_request.skill_categories is not None:
            updates["skill_categories"] = update_request.skill_categories

        skill_bank = await skill_bank_repo.update_skill_bank(user_id, updates)
        return SkillBankResponse(**skill_bank.dict())

    except Exception as e:
        logger.error(f"Error updating skill bank for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SKILLS MANAGEMENT ENDPOINTS
# =============================================================================


@router.post("/{user_id}/skills", response_model=EnhancedSkill, status_code=201)
async def add_skill(
    skill_request: EnhancedSkillRequest, user_id: str = Path(..., description="User ID")
):
    """Add a new skill to the skill bank."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        skill = EnhancedSkill(**skill_request.dict())
        added_skill = await skill_bank_repo.add_skill(user_id, skill)

        return added_skill

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding skill for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/skills", response_model=List[EnhancedSkill])
async def get_skills(
    user_id: str = Path(..., description="User ID"),
    category: Optional[str] = Query(None, description="Filter by skill category"),
):
    """Get all skills for a user, optionally filtered by category."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        skills = await skill_bank_repo.get_skills(user_id, category)
        return skills

    except Exception as e:
        logger.error(f"Error getting skills for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/skills/{skill_id}", response_model=EnhancedSkill)
async def update_skill(
    skill_update: SkillUpdateRequest,
    user_id: str = Path(..., description="User ID"),
    skill_id: str = Path(..., description="Skill ID"),
):
    """Update an existing skill."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        updates = {}
        for field, value in skill_update.dict(exclude_unset=True).items():
            if value is not None:
                updates[field] = value

        updated_skill = await skill_bank_repo.update_skill(user_id, skill_id, updates)
        return updated_skill

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating skill {skill_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/skills/{skill_id}", status_code=204)
async def delete_skill(
    user_id: str = Path(..., description="User ID"),
    skill_id: str = Path(..., description="Skill ID"),
):
    """Delete a skill from the skill bank."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        success = await skill_bank_repo.delete_skill(user_id, skill_id)
        if not success:
            raise HTTPException(status_code=404, detail="Skill not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting skill {skill_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SUMMARY VARIATIONS ENDPOINTS
# =============================================================================


@router.post("/{user_id}/summaries", response_model=SummaryVariation, status_code=201)
async def add_summary_variation(
    summary_request: SummaryVariationRequest,
    user_id: str = Path(..., description="User ID"),
):
    """Add a new summary variation."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        variation = SummaryVariation(**summary_request.dict())
        added_variation = await skill_bank_repo.add_summary_variation(
            user_id, variation
        )

        return added_variation

    except Exception as e:
        logger.error(f"Error adding summary variation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/summaries/{variation_id}", response_model=SummaryVariation)
async def update_summary_variation(
    summary_request: SummaryVariationRequest,
    user_id: str = Path(..., description="User ID"),
    variation_id: str = Path(..., description="Variation ID"),
):
    """Update a summary variation."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        updates = summary_request.dict(exclude_unset=True)
        updated_variation = await skill_bank_repo.update_summary_variation(
            user_id, variation_id, updates
        )

        return updated_variation

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error updating summary variation {variation_id} for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/summaries/{variation_id}", status_code=204)
async def delete_summary_variation(
    user_id: str = Path(..., description="User ID"),
    variation_id: str = Path(..., description="Variation ID"),
):
    """Delete a summary variation."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        success = await skill_bank_repo.delete_summary_variation(user_id, variation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Summary variation not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting summary variation {variation_id} for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# EXPERIENCE MANAGEMENT ENDPOINTS
# =============================================================================


@router.post("/{user_id}/experience", response_model=ExperienceEntry, status_code=201)
async def add_experience(
    experience_request: ExperienceEntryRequest,
    user_id: str = Path(..., description="User ID"),
):
    """Add a new work experience entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        experience = ExperienceEntry(**experience_request.dict())
        added_experience = await skill_bank_repo.add_experience(user_id, experience)

        return added_experience

    except Exception as e:
        logger.error(f"Error adding experience for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/experience/{experience_id}", response_model=ExperienceEntry)
async def update_experience(
    experience_request: ExperienceEntryRequest,
    user_id: str = Path(..., description="User ID"),
    experience_id: str = Path(..., description="Experience ID"),
):
    """Update a work experience entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        updates = experience_request.dict(exclude_unset=True)
        updated_experience = await skill_bank_repo.update_experience(
            user_id, experience_id, updates
        )

        return updated_experience

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error updating experience {experience_id} for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/experience/{experience_id}", status_code=204)
async def delete_experience(
    user_id: str = Path(..., description="User ID"),
    experience_id: str = Path(..., description="Experience ID"),
):
    """Delete a work experience entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        success = await skill_bank_repo.delete_experience(user_id, experience_id)
        if not success:
            raise HTTPException(status_code=404, detail="Experience not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting experience {experience_id} for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{user_id}/experience/{experience_id}/content",
    response_model=ExperienceContentVariation,
    status_code=201,
)
async def add_experience_content_variation(
    variation_request: ExperienceContentVariationRequest,
    user_id: str = Path(..., description="User ID"),
    experience_id: str = Path(..., description="Experience ID"),
):
    """Add a content variation to a work experience entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        # Ensure the experience_id in the request matches the path parameter
        variation_request.experience_id = experience_id

        variation = ExperienceContentVariation(**variation_request.dict())
        added_variation = await skill_bank_repo.add_experience_variation(
            user_id, variation
        )

        return added_variation

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error adding experience content variation for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# EDUCATION MANAGEMENT ENDPOINTS
# =============================================================================


@router.post("/{user_id}/education", response_model=EducationEntry, status_code=201)
async def add_education(
    education_request: EducationEntryRequest,
    user_id: str = Path(..., description="User ID"),
):
    """Add a new education entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        education = EducationEntry(**education_request.dict())
        added_education = await skill_bank_repo.add_education(user_id, education)

        return added_education

    except Exception as e:
        logger.error(f"Error adding education for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/education/{education_id}", response_model=EducationEntry)
async def update_education(
    education_request: EducationEntryRequest,
    user_id: str = Path(..., description="User ID"),
    education_id: str = Path(..., description="Education ID"),
):
    """Update an education entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        updates = education_request.dict(exclude_unset=True)
        updated_education = await skill_bank_repo.update_education(
            user_id, education_id, updates
        )

        return updated_education

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating education {education_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/education/{education_id}", status_code=204)
async def delete_education(
    user_id: str = Path(..., description="User ID"),
    education_id: str = Path(..., description="Education ID"),
):
    """Delete an education entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        success = await skill_bank_repo.delete_education(user_id, education_id)
        if not success:
            raise HTTPException(status_code=404, detail="Education not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting education {education_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PROJECTS MANAGEMENT ENDPOINTS
# =============================================================================


@router.post("/{user_id}/projects", response_model=ProjectEntry, status_code=201)
async def add_project(
    project_request: ProjectEntryRequest,
    user_id: str = Path(..., description="User ID"),
):
    """Add a new project entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        project = ProjectEntry(**project_request.dict())
        added_project = await skill_bank_repo.add_project(user_id, project)

        return added_project

    except Exception as e:
        logger.error(f"Error adding project for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/projects/{project_id}", response_model=ProjectEntry)
async def update_project(
    project_request: ProjectEntryRequest,
    user_id: str = Path(..., description="User ID"),
    project_id: str = Path(..., description="Project ID"),
):
    """Update a project entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        updates = project_request.dict(exclude_unset=True)
        updated_project = await skill_bank_repo.update_project(
            user_id, project_id, updates
        )

        return updated_project

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating project {project_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/projects/{project_id}", status_code=204)
async def delete_project(
    user_id: str = Path(..., description="User ID"),
    project_id: str = Path(..., description="Project ID"),
):
    """Delete a project entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        success = await skill_bank_repo.delete_project(user_id, project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CERTIFICATIONS MANAGEMENT ENDPOINTS
# =============================================================================


@router.post("/{user_id}/certifications", response_model=Certification, status_code=201)
async def add_certification(
    cert_request: CertificationRequest,
    user_id: str = Path(..., description="User ID"),
):
    """Add a new certification entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        certification = Certification(**cert_request.dict())
        added_certification = await skill_bank_repo.add_certification(
            user_id, certification
        )

        return added_certification

    except Exception as e:
        logger.error(f"Error adding certification for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{user_id}/certifications/{certification_id}", response_model=Certification
)
async def update_certification(
    cert_request: CertificationRequest,
    user_id: str = Path(..., description="User ID"),
    certification_id: str = Path(..., description="Certification ID"),
):
    """Update a certification entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        updates = cert_request.dict(exclude_unset=True)
        updated_certification = await skill_bank_repo.update_certification(
            user_id, certification_id, updates
        )

        return updated_certification

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error updating certification {certification_id} for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/certifications/{certification_id}", status_code=204)
async def delete_certification(
    user_id: str = Path(..., description="User ID"),
    certification_id: str = Path(..., description="Certification ID"),
):
    """Delete a certification entry."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        success = await skill_bank_repo.delete_certification(user_id, certification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Certification not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting certification {certification_id} for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# DATA MIGRATION ENDPOINTS
# =============================================================================


@router.post("/{user_id}/migrate", response_model=SkillBankResponse)
async def migrate_from_user_profile(user_id: str = Path(..., description="User ID")):
    """Migrate skills data from UserProfile to SkillBank."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        migrated_bank = await skill_bank_repo.migrate_from_user_profile(user_id)
        return SkillBankResponse(**migrated_bank.dict())

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error migrating data for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================


@router.get("/{user_id}/categories", response_model=List[str])
async def get_skill_categories(user_id: str = Path(..., description="User ID")):
    """Get all skill categories for a user."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        skill_bank = await skill_bank_repo.get_or_create_skill_bank(user_id)
        return skill_bank.skill_categories

    except Exception as e:
        logger.error(f"Error getting skill categories for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/stats", response_model=Dict[str, Any])
async def get_skill_bank_stats(user_id: str = Path(..., description="User ID")):
    """Get skill bank statistics."""
    try:
        db_manager = get_database_manager()
        skill_bank_repo = SkillBankRepository(db_manager)

        skill_bank = await skill_bank_repo.get_or_create_skill_bank(user_id)

        # Calculate statistics
        total_skills = sum(len(skills) for skills in skill_bank.skills.values())
        skills_by_category = {
            category: len(skills) for category, skills in skill_bank.skills.items()
        }

        stats = {
            "total_skills": total_skills,
            "skills_by_category": skills_by_category,
            "total_summary_variations": len(skill_bank.summary_variations),
            "total_work_experiences": len(skill_bank.work_experiences),
            "total_education_entries": len(skill_bank.education_entries),
            "total_projects": len(skill_bank.projects),
            "total_certifications": len(skill_bank.certifications),
            "last_updated": skill_bank.updated_at,
            "created_at": skill_bank.created_at,
        }

        return stats

    except Exception as e:
        logger.error(f"Error getting stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
