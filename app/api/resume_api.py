"""
Resume API Endpoints
FastAPI routes for resume management, ATS scoring, and job integration.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.data.database import get_db
from app.data.resume_models import (
    Certification,
    ContactInfo,
    Education,
    Project,
    Resume,
    ResumeStatus,
    ResumeType,
    Skill,
    WorkExperience,
)
from app.logger import logger
from app.repositories.resume_repository import ResumeRepository
from app.services.resume_orchestrator_service import (
    ResumeGenerationRequest,
    create_resume_orchestrator,
)


# Create router
router = APIRouter(prefix="/api/resumes", tags=["resumes"])

# =====================================
# Request/Response Models
# =====================================


class CreateResumeRequest(BaseModel):
    """Request model for creating a new resume."""

    title: str
    contact_info: ContactInfo
    summary: Optional[str] = None
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    template_id: Optional[str] = None
    resume_type: ResumeType = ResumeType.BASE


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
    status: Optional[ResumeStatus] = None
    template_id: Optional[str] = None


class CreateFromProfileRequest(BaseModel):
    """Request model for creating resume from user profile."""

    title: str
    user_id: str


class TailorResumeRequest(BaseModel):
    """Request model for creating tailored resume."""

    base_resume_id: str
    job_id: str
    title: Optional[str] = None


class AIGenerateResumeRequest(BaseModel):
    """Request model for AI-powered resume generation."""

    generation_type: str = Field(
        ..., description="Type: 'create', 'optimize', or 'enhance'"
    )
    base_resume_id: Optional[str] = Field(
        None, description="Required for optimize/enhance"
    )
    job_id: Optional[str] = Field(None, description="Job ID for optimization")
    job_description: Optional[str] = Field(None, description="Job description text")
    target_role: Optional[str] = Field(None, description="Target job role")
    target_industry: Optional[str] = Field(None, description="Target industry")
    optimization_level: str = Field(
        "moderate", description="light, moderate, or aggressive"
    )
    export_formats: List[str] = Field(
        ["pdf"], description="Export formats: pdf, json, yaml, txt"
    )
    pdf_template: str = Field("moderncv", description="PDF template name")
    theme_options: Optional[Dict[str, Any]] = Field(
        None, description="Custom theme options"
    )
    custom_instructions: Optional[str] = Field(
        None, description="Custom generation instructions"
    )


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
    resume_type: str
    created_at: str
    updated_at: str
    version: int
    completeness_score: Optional[float] = None


class ResumeListResponse(BaseModel):
    """Response model for list of resumes."""

    resumes: List[ResumeResponse]
    total: int
    page: int = 1
    per_page: int = 10


# =====================================
# Resume CRUD Endpoints
# =====================================


@router.get("/", response_model=ResumeListResponse)
async def get_user_resumes(
    user_id: str = Query(..., description="User ID to get resumes for"),
    status: Optional[ResumeStatus] = Query(None, description="Filter by resume status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Get all resumes for a user with optional filtering and pagination."""
    try:
        repo = ResumeRepository(db)
        resumes = await repo.get_user_resumes(user_id, status)

        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_resumes = resumes[start_idx:end_idx]

        # Convert to response format
        resume_responses = []
        for resume in paginated_resumes:
            from app.data.resume_models import calculate_resume_completeness

            completeness = calculate_resume_completeness(resume)

            resume_responses.append(
                ResumeResponse(
                    id=resume.id,
                    user_id=resume.user_id,
                    title=resume.title,
                    status=resume.status,
                    resume_type=resume.resume_type,
                    created_at=resume.created_at.isoformat()
                    if resume.created_at
                    else "",
                    updated_at=resume.updated_at.isoformat()
                    if resume.updated_at
                    else "",
                    version=resume.version,
                    completeness_score=completeness,
                )
            )

        return ResumeListResponse(
            resumes=resume_responses, total=len(resumes), page=page, per_page=per_page
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
    db: Session = Depends(get_db),
):
    """Get a specific resume by ID."""
    try:
        repo = ResumeRepository(db)
        resume = await repo.get_resume(resume_id, user_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        return resume.dict()

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
    db: Session = Depends(get_db),
):
    """Create a new resume."""
    try:
        repo = ResumeRepository(db)

        # Create resume object
        resume_data = Resume(
            user_id=user_id,
            title=request.title,
            contact_info=request.contact_info,
            summary=request.summary,
            work_experience=request.work_experience,
            education=request.education,
            skills=request.skills,
            projects=request.projects,
            certifications=request.certifications,
            template_id=request.template_id,
            resume_type=request.resume_type,
        )

        # Save resume
        resume_db = await repo.create_resume(resume_data)
        resume = repo._db_to_pydantic(resume_db)

        # Update skill bank
        await repo.update_skill_bank_from_resume(user_id, resume)

        logger.info(f"Created new resume: {resume_db.id}")
        return {"message": "Resume created successfully", "resume_id": resume_db.id}

    except Exception as e:
        logger.error(f"Error creating resume: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating resume: {str(e)}")


@router.put("/{resume_id}")
async def update_resume(
    resume_id: str = Path(..., description="Resume ID"),
    request: UpdateResumeRequest = Body(...),
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
):
    """Update an existing resume."""
    try:
        repo = ResumeRepository(db)

        # Prepare update data
        updates = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                updates[field] = value

        if not updates:
            return {"message": "No updates provided"}

        # Update resume
        updated_resume = await repo.update_resume(resume_id, user_id, updates)

        if not updated_resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Update skill bank if skills were updated
        if "skills" in updates:
            await repo.update_skill_bank_from_resume(user_id, updated_resume)

        logger.info(f"Updated resume: {resume_id}")
        return {
            "message": "Resume updated successfully",
            "version": updated_resume.version,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating resume: {str(e)}")


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
):
    """Delete a resume."""
    try:
        repo = ResumeRepository(db)
        success = await repo.delete_resume(resume_id, user_id)

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
# Resume Creation from Profile
# =====================================


@router.post("/from-profile")
async def create_resume_from_profile(
    request: CreateFromProfileRequest, db: Session = Depends(get_db)
):
    """Create a resume from user profile data."""
    try:
        repo = ResumeRepository(db)
        resume = await repo.create_resume_from_user_profile(
            request.user_id, request.title
        )

        if not resume:
            raise HTTPException(status_code=404, detail="User profile not found")

        logger.info(f"Created resume from profile for user: {request.user_id}")
        return {
            "message": "Resume created from profile successfully",
            "resume_id": resume.id,
            "title": resume.title,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating resume from profile: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error creating resume from profile: {str(e)}"
        )


# =====================================
# Resume Templates
# =====================================


@router.get("/templates")
async def get_resume_templates(db: Session = Depends(get_db)):
    """Get available resume templates."""
    try:
        repo = ResumeRepository(db)
        templates = await repo.get_resume_templates()

        return {"templates": templates}

    except Exception as e:
        logger.error(f"Error getting resume templates: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting templates: {str(e)}"
        )


@router.post("/templates/initialize")
async def initialize_default_templates(db: Session = Depends(get_db)):
    """Initialize default system resume templates."""
    try:
        repo = ResumeRepository(db)
        await repo.create_default_templates()

        return {"message": "Default templates initialized successfully"}

    except Exception as e:
        logger.error(f"Error initializing templates: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error initializing templates: {str(e)}"
        )


# =====================================
# Resume Tailoring and Job Integration
# =====================================


@router.post("/tailor")
async def create_tailored_resume(
    request: TailorResumeRequest,
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
):
    """Create a tailored resume for a specific job."""
    try:
        repo = ResumeRepository(db)
        tailored_resume = await repo.create_tailored_resume(
            request.base_resume_id, request.job_id, user_id
        )

        if not tailored_resume:
            raise HTTPException(status_code=404, detail="Base resume or job not found")

        logger.info(f"Created tailored resume: {tailored_resume.id}")
        return {
            "message": "Tailored resume created successfully",
            "resume_id": tailored_resume.id,
            "title": tailored_resume.title,
            "job_id": request.job_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tailored resume: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error creating tailored resume: {str(e)}"
        )


@router.get("/{resume_id}/ats-score")
async def get_ats_score(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
    job_description: Optional[str] = Query(
        None, description="Job description for targeted scoring"
    ),
    db: Session = Depends(get_db),
):
    """Get ATS compatibility score for a resume."""
    try:
        repo = ResumeRepository(db)
        resume = await repo.get_resume(resume_id, user_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        ats_score = await repo.calculate_ats_score(resume, job_description)

        return {
            "resume_id": resume_id,
            "ats_score": ats_score.dict(),
            "analyzed_at": ats_score.dict().get("analyzed_at", ""),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating ATS score: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error calculating ATS score: {str(e)}"
        )


@router.post("/{resume_id}/optimize-for-job/{job_id}")
async def optimize_resume_for_job(
    resume_id: str = Path(..., description="Resume ID"),
    job_id: str = Path(..., description="Job ID"),
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
):
    """Analyze and provide optimization recommendations for a resume against a job."""
    try:
        repo = ResumeRepository(db)
        optimization = await repo.optimize_resume_for_job(resume_id, job_id, user_id)

        if not optimization:
            raise HTTPException(status_code=404, detail="Resume or job not found")

        return {"resume_id": resume_id, "job_id": job_id, "optimization": optimization}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing resume for job: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error optimizing resume: {str(e)}"
        )


# =====================================
# Skills Bank Integration
# =====================================


@router.get("/skills-bank/{user_id}")
async def get_user_skill_bank(
    user_id: str = Path(..., description="User ID"), db: Session = Depends(get_db)
):
    """Get user's skill bank for resume building."""
    try:
        repo = ResumeRepository(db)
        skill_bank = await repo.get_user_skill_bank(user_id)

        if not skill_bank:
            return {"message": "No skill bank found for user", "skills": {}}

        return {"skill_bank": skill_bank}

    except Exception as e:
        logger.error(f"Error getting skill bank: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting skill bank: {str(e)}"
        )


# =====================================
# Resume Analytics
# =====================================


@router.get("/{resume_id}/analytics")
async def get_resume_analytics(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
):
    """Get comprehensive analytics for a resume."""
    try:
        repo = ResumeRepository(db)
        resume = await repo.get_resume(resume_id, user_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        from app.data.resume_models import (
            calculate_resume_completeness,
            extract_resume_keywords,
        )

        # Calculate various metrics
        completeness = calculate_resume_completeness(resume)
        keywords = extract_resume_keywords(resume)
        ats_score = await repo.calculate_ats_score(resume)

        # Basic analytics
        analytics = {
            "resume_id": resume_id,
            "completeness_score": completeness,
            "total_keywords": len(keywords),
            "keyword_list": keywords,
            "ats_score": ats_score.dict(),
            "sections": {
                "work_experience_count": len(resume.work_experience),
                "education_count": len(resume.education),
                "skills_count": len(resume.skills),
                "projects_count": len(resume.projects),
                "certifications_count": len(resume.certifications),
            },
            "recommendations": [
                "Add more specific achievements to work experience"
                if not any(exp.achievements for exp in resume.work_experience)
                else None,
                f"Consider adding more skills (currently {len(resume.skills)})"
                if len(resume.skills) < 8
                else None,
                "Add projects to showcase practical experience"
                if len(resume.projects) == 0
                else None,
            ],
        }

        # Filter out None recommendations
        analytics["recommendations"] = [
            r for r in analytics["recommendations"] if r is not None
        ]

        return {"analytics": analytics}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resume analytics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting analytics: {str(e)}"
        )


# =====================================
# Utility Endpoints
# =====================================


@router.get("/{resume_id}/versions")
async def get_resume_versions(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
):
    """Get version history for a resume."""
    try:
        # For now, return basic version info
        # In a full implementation, this would query resume_versions table
        repo = ResumeRepository(db)
        resume = await repo.get_resume(resume_id, user_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        return {
            "resume_id": resume_id,
            "current_version": resume.version,
            "versions": [
                {
                    "version": resume.version,
                    "created_at": resume.updated_at.isoformat()
                    if resume.updated_at
                    else "",
                    "is_current": True,
                }
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resume versions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting versions: {str(e)}")


@router.post("/{resume_id}/duplicate")
async def duplicate_resume(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
    new_title: str = Query(..., description="Title for the duplicated resume"),
    db: Session = Depends(get_db),
):
    """Create a duplicate of an existing resume."""
    try:
        repo = ResumeRepository(db)
        original_resume = await repo.get_resume(resume_id, user_id)

        if not original_resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Create duplicate
        duplicate_resume = Resume(**original_resume.dict())
        duplicate_resume.id = None  # Will generate new ID
        duplicate_resume.title = new_title
        duplicate_resume.based_on_resume_id = resume_id
        duplicate_resume.created_at = None
        duplicate_resume.updated_at = None
        duplicate_resume.version = 1

        # Save duplicate
        duplicate_db = await repo.create_resume(duplicate_resume)

        logger.info(f"Duplicated resume {resume_id} to {duplicate_db.id}")
        return {
            "message": "Resume duplicated successfully",
            "original_id": resume_id,
            "duplicate_id": duplicate_db.id,
            "title": new_title,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating resume: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error duplicating resume: {str(e)}"
        )


# =====================================
# AI-Powered Resume Generation
# =====================================


@router.post("/ai/generate")
async def generate_resume_with_ai(
    request: AIGenerateResumeRequest,
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
    llm_provider: str = Query(
        "mock", description="LLM provider: openai, anthropic, mock"
    ),
):
    """Generate a complete resume using AI with content optimization and export."""
    try:
        # Create orchestrator service
        repo = ResumeRepository(db)
        orchestrator = create_resume_orchestrator(
            resume_repository=repo, llm_provider=llm_provider
        )

        # Create generation request
        generation_request = ResumeGenerationRequest(
            user_id=user_id,
            generation_type=request.generation_type,
            base_resume_id=request.base_resume_id,
            job_id=request.job_id,
            job_description=request.job_description,
            target_role=request.target_role,
            target_industry=request.target_industry,
            optimization_level=request.optimization_level,
            export_formats=request.export_formats,
            pdf_template=request.pdf_template,
            theme_options=request.theme_options,
            custom_instructions=request.custom_instructions,
        )

        # Generate resume
        result = await orchestrator.generate_complete_resume(generation_request)

        if result.success:
            response = {
                "success": True,
                "message": "Resume generated successfully",
                "resume_id": result.resume_id,
                "processing_time": result.processing_time,
                "generation_metadata": result.generation_metadata,
                "generated_files": result.generated_files,
                "optimization_analysis": result.optimization_analysis,
            }

            if result.warnings:
                response["warnings"] = result.warnings

            logger.info(f"AI resume generation completed for user {user_id}")
            return response
        else:
            logger.error(f"AI resume generation failed: {result.errors}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Resume generation failed",
                    "errors": result.errors,
                    "processing_time": result.processing_time,
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI resume generation: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")


@router.post("/ai/batch-generate")
async def batch_generate_resumes(
    requests: List[AIGenerateResumeRequest],
    user_id: str = Query(..., description="User ID for authorization"),
    max_concurrent: int = Query(
        3, ge=1, le=5, description="Max concurrent generations"
    ),
    db: Session = Depends(get_db),
    llm_provider: str = Query(
        "mock", description="LLM provider: openai, anthropic, mock"
    ),
):
    """Generate multiple resumes concurrently."""
    try:
        if len(requests) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 resumes per batch")

        # Create orchestrator service
        repo = ResumeRepository(db)
        orchestrator = create_resume_orchestrator(
            resume_repository=repo, llm_provider=llm_provider
        )

        # Convert to generation requests
        generation_requests = []
        for req in requests:
            generation_requests.append(
                ResumeGenerationRequest(
                    user_id=user_id,
                    generation_type=req.generation_type,
                    base_resume_id=req.base_resume_id,
                    job_id=req.job_id,
                    job_description=req.job_description,
                    target_role=req.target_role,
                    target_industry=req.target_industry,
                    optimization_level=req.optimization_level,
                    export_formats=req.export_formats,
                    pdf_template=req.pdf_template,
                    theme_options=req.theme_options,
                    custom_instructions=req.custom_instructions,
                )
            )

        # Generate resumes in batch
        results = await orchestrator.batch_generate_resumes(
            generation_requests, max_concurrent=max_concurrent
        )

        # Prepare response
        successful_count = sum(1 for r in results if r.success)
        failed_count = len(results) - successful_count

        response_data = {
            "batch_results": [
                {
                    "success": result.success,
                    "resume_id": result.resume_id,
                    "processing_time": result.processing_time,
                    "errors": result.errors,
                    "warnings": result.warnings,
                }
                for result in results
            ],
            "summary": {
                "total_requested": len(requests),
                "successful": successful_count,
                "failed": failed_count,
                "total_processing_time": sum(r.processing_time for r in results),
            },
        }

        logger.info(
            f"Batch generation completed: {successful_count}/{len(requests)} successful"
        )
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch resume generation: {e}")
        raise HTTPException(status_code=500, detail=f"Batch generation error: {str(e)}")


@router.get("/ai/templates")
async def get_generation_templates(
    db: Session = Depends(get_db),
    llm_provider: str = Query("mock", description="LLM provider for capabilities"),
):
    """Get available templates and options for AI resume generation."""
    try:
        # Create orchestrator service
        repo = ResumeRepository(db)
        orchestrator = create_resume_orchestrator(
            resume_repository=repo, llm_provider=llm_provider
        )

        templates = await orchestrator.get_generation_templates()

        return {
            "message": "Generation templates retrieved successfully",
            "templates": templates,
        }

    except Exception as e:
        logger.error(f"Error getting generation templates: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting templates: {str(e)}"
        )


# =====================================
# Resume Export Endpoints
# =====================================


@router.post("/{resume_id}/export")
async def export_resume(
    resume_id: str = Path(..., description="Resume ID"),
    request: ExportResumeRequest = Body(...),
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
):
    """Export an existing resume in various formats."""
    try:
        # Get resume
        repo = ResumeRepository(db)
        resume = await repo.get_resume(resume_id, user_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Create export service
        from app.services.pdf_generation_service import create_export_service

        export_service = create_export_service()

        # Export resume
        export_result = await export_service.export_resume(
            resume=resume,
            export_format=request.export_format,
            template_name=request.template_name,
            options={
                "filename": request.filename,
                "theme_options": request.theme_options,
            },
        )

        if export_result.get("success"):
            logger.info(f"Exported resume {resume_id} as {request.export_format}")
            return {
                "message": f"Resume exported as {request.export_format} successfully",
                "export_result": export_result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Export failed: {export_result.get('error', 'Unknown error')}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting resume: {e}")
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.get("/export/templates")
async def get_export_templates():
    """Get available export templates and formats."""
    try:
        from app.services.pdf_generation_service import create_pdf_service

        pdf_service = create_pdf_service()

        templates = pdf_service.get_available_templates()

        return {
            "export_formats": ["pdf", "json", "yaml", "txt"],
            "pdf_templates": templates,
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


@router.post("/{resume_id}/preview")
async def generate_resume_preview(
    resume_id: str = Path(..., description="Resume ID"),
    user_id: str = Query(..., description="User ID for authorization"),
    template_name: str = Query("moderncv", description="Template for preview"),
    db: Session = Depends(get_db),
):
    """Generate a preview image of the resume."""
    try:
        # Get resume
        repo = ResumeRepository(db)
        resume = await repo.get_resume(resume_id, user_id)

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Create PDF service for preview
        from app.services.pdf_generation_service import create_pdf_service

        pdf_service = create_pdf_service()

        # Generate preview
        preview_result = await pdf_service.generate_preview_image(
            resume=resume, template_name=template_name
        )

        if preview_result.get("success"):
            return {
                "message": "Preview generated successfully",
                "preview": preview_result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Preview generation failed: {preview_result.get('error', 'Unknown error')}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail=f"Preview error: {str(e)}")
