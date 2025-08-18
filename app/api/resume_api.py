"""
Resume API Endpoints
FastAPI routes for resume management with database integration.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Path, Query
from pydantic import BaseModel, Field

from app.data.database import get_resume_repository
from app.data.resume_models import (
    Certification as CertificationModel,
)
from app.data.resume_models import (
    ContactInfo as ContactInfoModel,
)
from app.data.resume_models import (
    Education as EducationModel,
)
from app.data.resume_models import (
    Project as ProjectModel,
)
from app.data.resume_models import (
    Resume as ResumeModel,
)
from app.data.resume_models import (
    ResumeStatus,
    ResumeType,
)
from app.data.resume_models import (
    Skill as SkillModel,
)
from app.data.resume_models import (
    WorkExperience as WorkExperienceModel,
)
from app.logger import logger

# Create router
router = APIRouter(prefix="/api/resumes", tags=["resumes"])

# =====================================
# Request/Response Models
# =====================================


class ContactInfo(BaseModel):
    """Contact information model."""

    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None


class WorkExperience(BaseModel):
    """Work experience model."""

    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None


class Education(BaseModel):
    """Education model."""

    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None


class Skill(BaseModel):
    """Skill model."""

    name: str
    category: Optional[str] = None
    proficiency_level: Optional[str] = None


class Project(BaseModel):
    """Project model."""

    name: str
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    url: Optional[str] = None


class Certification(BaseModel):
    """Certification model."""

    name: str
    issuer: Optional[str] = None
    date_earned: Optional[str] = None
    expiry_date: Optional[str] = None


class CreateResumeRequest(BaseModel):
    """Request model for creating a new resume."""

    title: str
    contact_info: ContactInfo
    summary: Optional[str] = None
    work_experience: Optional[List[WorkExperience]] = None
    education: Optional[List[Education]] = None
    skills: Optional[List[Skill]] = None
    projects: Optional[List[Project]] = None
    certifications: Optional[List[Certification]] = None
    template_id: Optional[str] = None


class UpdateResumeRequest(BaseModel):
    """Request model for updating a resume."""

    title: Optional[str] = None
    contact_info: Optional[ContactInfo] = None
    summary: Optional[str] = None
    work_experience: Optional[List[WorkExperience]] = None
    education: Optional[List[Education]] = None
    skills: Optional[List[Skill]] = None
    projects: Optional[List[Project]] = None
    certifications: Optional[List[Certification]] = None
    template_id: Optional[str] = None


class ExportResumeRequest(BaseModel):
    """Request model for exporting resume."""

    export_format: str = Field(..., description="Format: pdf, json, yaml, txt")
    template_name: str = Field("moderncv", description="Template for PDF export")
    filename: Optional[str] = Field(None, description="Custom filename")
    theme_options: Optional[Dict[str, Any]] = Field(
        None, description="Theme customization"
    )


class ResumeResponse(BaseModel):
    """Response model for resume data."""

    id: str
    user_id: str
    title: str
    status: str
    resume_type: str = "base"
    created_at: str
    updated_at: str
    version: int = 1
    completeness_score: Optional[float] = None


class ResumeListResponse(BaseModel):
    """Response model for list of resumes."""

    resumes: List[ResumeResponse]
    total: int
    page: int = 1
    per_page: int = 10


# =====================================
# Helper Functions
# =====================================


def calculate_completeness(resume_data: dict) -> float:
    """Calculate resume completeness score."""
    score = 0.0
    total_weight = 0.0

    # Contact info (weight: 0.2)
    if resume_data.get("contact_info", {}).get("full_name"):
        score += 0.1
    if resume_data.get("contact_info", {}).get("email"):
        score += 0.1
    total_weight += 0.2

    # Summary (weight: 0.1)
    if resume_data.get("summary"):
        score += 0.1
    total_weight += 0.1

    # Work experience (weight: 0.3)
    work_exp = resume_data.get("work_experience", [])
    if work_exp:
        score += 0.3
    total_weight += 0.3

    # Education (weight: 0.15)
    education = resume_data.get("education", [])
    if education:
        score += 0.15
    total_weight += 0.15

    # Skills (weight: 0.15)
    skills = resume_data.get("skills", [])
    if skills:
        score += 0.15
    total_weight += 0.15

    # Projects (weight: 0.1)
    projects = resume_data.get("projects", [])
    if projects:
        score += 0.1
    total_weight += 0.1

    return min(score / total_weight if total_weight > 0 else 0.0, 1.0)


# =====================================
# Resume CRUD Endpoints
# =====================================


@router.get("/", response_model=ResumeListResponse)
async def get_user_resumes(
    user_id: str = Query(..., description="User ID to get resumes for"),
    status: Optional[str] = Query(None, description="Filter by resume status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Items per page"),
):
    """Get all resumes for a user with optional filtering and pagination."""
    try:
        # Get resume repository
        resume_repo = get_resume_repository()

        # Get resumes from database with pagination
        offset = (page - 1) * per_page
        resumes, total = resume_repo.get_user_resumes(
            user_id=user_id, status=status, limit=per_page, offset=offset
        )

        # Convert to response format
        resume_responses = []
        for resume in resumes:
            # Convert Resume model to dict for completeness calculation
            resume_dict = (
                resume.dict()
                if hasattr(resume, "dict")
                else {
                    "contact_info": resume.contact_info,
                    "summary": resume.summary,
                    "work_experience": resume.work_experience,
                    "education": resume.education,
                    "skills": resume.skills,
                    "projects": resume.projects,
                }
            )

            completeness = calculate_completeness(resume_dict)
            resume_responses.append(
                ResumeResponse(
                    id=str(resume.id) if resume.id else "",
                    user_id=resume.user_id,
                    title=resume.title,
                    status=resume.status,
                    resume_type=resume.resume_type or "base",
                    created_at=(
                        resume.created_at.isoformat()
                        if resume.created_at
                        else datetime.utcnow().isoformat()
                    ),
                    updated_at=(
                        resume.updated_at.isoformat()
                        if resume.updated_at
                        else datetime.utcnow().isoformat()
                    ),
                    version=resume.version or 1,
                    completeness_score=completeness,
                )
            )

        return ResumeListResponse(
            resumes=resume_responses,
            total=total,
            page=page,
            per_page=per_page,
        )

    except Exception as e:
        logger.error(f"Error getting user resumes: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving resumes: {str(e)}"
        )


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
):
    """Get a specific resume by ID."""
    try:
        resume_repo = get_resume_repository()
        resume = resume_repo.get_resume(resume_id=resume_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Check authorization
        if resume.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return resume

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resume {resume_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving resume: {str(e)}"
        )


@router.post("/")
async def create_resume(
    request: CreateResumeRequest,
    user_id: str = Query(..., description="User ID"),
):
    """Create a new resume."""
    try:
        resume_repo = get_resume_repository()
        now = datetime.utcnow()

        # Create resume data
        resume_data = ResumeModel(
            user_id=user_id,
            title=request.title,
            contact_info=ContactInfoModel(**request.contact_info.dict()),
            summary=request.summary,
            work_experience=[
                WorkExperienceModel(**exp.dict())
                for exp in (request.work_experience or [])
            ],
            education=[
                EducationModel(**edu.dict()) for edu in (request.education or [])
            ],
            skills=[SkillModel(**skill.dict()) for skill in (request.skills or [])],
            projects=[ProjectModel(**proj.dict()) for proj in (request.projects or [])],
            certifications=[
                CertificationModel(**cert.dict())
                for cert in (request.certifications or [])
            ],
            template_id=request.template_id,
            resume_type=ResumeType.BASE,
            status=ResumeStatus.DRAFT,
            created_at=now,
            updated_at=now,
            version=1,
        )

        # Store the resume
        created_resume = resume_repo.create_resume(resume_data)

        logger.info(f"Created new resume: {created_resume.id} for user: {user_id}")
        return {
            "message": "Resume created successfully",
            "resume_id": created_resume.id,
            "id": created_resume.id,  # Also return as 'id' for compatibility
        }

    except Exception as e:
        logger.error(f"Error creating resume: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating resume: {str(e)}")


@router.put("/{resume_id}")
async def update_resume(
    resume_id: str = Path(..., description="Resume ID"),
    request: UpdateResumeRequest = Body(...),
    user_id: str = Query(..., description="User ID for authorization"),
):
    """Update an existing resume."""
    try:
        resume_repo = get_resume_repository()
        resume = resume_repo.get_resume(resume_id=resume_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Check authorization
        if resume.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update resume data with provided fields
        update_data = request.dict(exclude_unset=True)

        if update_data:
            updated_resume = resume_repo.update_resume(
                resume_id=resume_id, update_data=update_data
            )
            if updated_resume:
                logger.info(f"Updated resume: {resume_id}")
                return {
                    "message": "Resume updated successfully",
                    "version": updated_resume.version,
                }
            else:
                raise HTTPException(status_code=404, detail="Resume not found")
        else:
            return {"message": "No changes to update"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating resume: {str(e)}")


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
):
    """Delete a resume."""
    try:
        resume_repo = get_resume_repository()

        # First check if resume exists and belongs to user
        resume = resume_repo.get_resume(resume_id=resume_id)
        if not resume or resume.user_id != user_id:
            raise HTTPException(
                status_code=404, detail="Resume not found or access denied"
            )

        success = resume_repo.delete_resume(resume_id=resume_id)

        if not success:
            raise HTTPException(status_code=404, detail="Resume not found")

        logger.info(f"Deleted resume: {resume_id}")
        return {"message": "Resume deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {str(e)}")


# =====================================
# Resume Templates
# =====================================


@router.get("/templates")
async def get_resume_templates():
    """Get available resume templates."""
    try:
        # Mock template data for now
        templates = [
            {
                "id": "modern",
                "name": "Modern",
                "description": "A clean, modern resume template",
                "preview_url": "/templates/modern/preview.png",
            },
            {
                "id": "classic",
                "name": "Classic",
                "description": "A traditional, professional resume template",
                "preview_url": "/templates/classic/preview.png",
            },
            {
                "id": "creative",
                "name": "Creative",
                "description": "A creative template for design-focused roles",
                "preview_url": "/templates/creative/preview.png",
            },
        ]

        return {"templates": templates}

    except Exception as e:
        logger.error(f"Error getting resume templates: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting templates: {str(e)}"
        )


# =====================================
# Export Endpoints
# =====================================


@router.post("/{resume_id}/export")
async def export_resume(
    resume_id: str = Path(..., description="Resume ID"),
    request: ExportResumeRequest = Body(...),
    user_id: str = Query(..., description="User ID for authorization"),
):
    """Export an existing resume in various formats."""
    try:
        resume_repo = get_resume_repository()
        resume = resume_repo.get_resume(resume_id=resume_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Check authorization
        if resume.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # For now, we'll return a mock response since we don't have the full PDF service
        if request.export_format.lower() == "pdf":
            # In a real implementation, this would generate a PDF
            return {
                "message": "Resume exported as PDF successfully",
                "export_format": request.export_format,
                "template_name": request.template_name,
                "download_url": f"/api/resumes/{resume_id}/download/pdf",
                "note": "PDF generation not implemented in demo - this is a mock response",
            }
        elif request.export_format.lower() == "json":
            return {
                "message": "Resume exported as JSON successfully",
                "data": resume.dict(),
            }
        else:
            return {
                "message": f"Resume exported as {request.export_format} successfully",
                "export_format": request.export_format,
                "note": f"{request.export_format.upper()} export not fully implemented in demo",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting resume: {e}")
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.get("/export/templates")
async def get_export_templates():
    """Get available export templates and formats."""
    try:
        return {
            "export_formats": ["pdf", "json", "yaml", "txt"],
            "pdf_templates": [
                {"name": "moderncv", "description": "Modern CV template"},
                {"name": "classic", "description": "Classic professional template"},
                {"name": "creative", "description": "Creative design template"},
            ],
            "supported_themes": [
                {"name": "blue", "description": "Professional blue theme"},
                {"name": "green", "description": "Modern green theme"},
                {"name": "red", "description": "Bold red theme"},
                {"name": "black", "description": "Classic black and white"},
            ],
        }

    except Exception as e:
        logger.error(f"Error getting export templates: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting export templates: {str(e)}"
        )


# =====================================
# Analytics and Utility Endpoints
# =====================================


@router.get("/{resume_id}/analytics")
async def get_resume_analytics(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
):
    """Get comprehensive analytics for a resume."""
    try:
        resume_repo = get_resume_repository()
        resume = resume_repo.get_resume(resume_id=resume_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Check authorization
        if resume.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Calculate basic analytics
        completeness = calculate_completeness(resume.dict())
        work_experience = resume.work_experience or []
        education = resume.education or []
        skills = resume.skills or []
        projects = resume.projects or []
        certifications = resume.certifications or []

        recommendations = []
        if not any(
            exp.achievements for exp in work_experience if hasattr(exp, "achievements")
        ):
            recommendations.append("Add more specific achievements to work experience")
        if len(skills) < 8:
            recommendations.append(
                f"Consider adding more skills (currently {len(skills)})"
            )
        if len(projects) == 0:
            recommendations.append("Add projects to showcase practical experience")

        analytics = {
            "resume_id": resume_id,
            "completeness_score": completeness,
            "sections": {
                "work_experience_count": len(work_experience),
                "education_count": len(education),
                "skills_count": len(skills),
                "projects_count": len(projects),
                "certifications_count": len(certifications),
            },
            "recommendations": recommendations,
        }

        return {"analytics": analytics}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resume analytics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting analytics: {str(e)}"
        )


# =====================================
# Health Check
# =====================================


@router.get("/health")
async def resume_api_health():
    """Health check for resume API."""
    try:
        resume_repo = get_resume_repository()
        total_resumes = await resume_repo.get_total_resumes_count()
        return {
            "status": "healthy",
            "service": "Resume API",
            "resumes_count": total_resumes,
            "timestamp": datetime.utcnow().isoformat(),
            "features": ["resume_crud", "templates", "export", "analytics"],
        }
    except Exception as e:
        logger.error(f"Error in resume API health check: {e}")
        return {
            "status": "unhealthy",
            "service": "Resume API",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
