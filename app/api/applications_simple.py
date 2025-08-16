"""
Simple Applications API for JobPilot
Basic CRUD operations for job applications
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..data.database import get_application_repository, get_job_repository
from ..data.models import ApplicationStatus, JobApplication

router = APIRouter(prefix="/api/applications", tags=["applications"])

# =====================================
# Request/Response Models
# =====================================

# Default user ID (same as in web_server.py)
DEFAULT_USER_ID = "00000000-0000-4000-8000-000000000001"


class CreateApplicationRequest(BaseModel):
    """Request model for creating a new job application."""

    job_id: str
    user_profile_id: str = DEFAULT_USER_ID  # Default to demo user
    status: ApplicationStatus = ApplicationStatus.NOT_APPLIED
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Response model for job application data."""

    id: str
    job_id: str
    user_profile_id: str
    status: ApplicationStatus
    applied_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Job info
    job_title: Optional[str] = None
    company: Optional[str] = None


# =====================================
# API Endpoints
# =====================================


@router.post("/")
def create_application(request: CreateApplicationRequest):
    """Create a new job application."""
    try:
        app_repo = get_application_repository()
        job_repo = get_job_repository()

        # Verify job exists
        job = job_repo.get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Check if application already exists
        existing_app = app_repo.get_application_by_job_and_user(
            request.job_id, request.user_profile_id
        )
        if existing_app:
            raise HTTPException(
                status_code=400, detail="Application already exists for this job"
            )

        # Create application
        app_data = JobApplication(
            id=uuid4(),
            job_id=UUID(request.job_id),
            user_profile_id=UUID(request.user_profile_id),
            status=request.status,
            applied_date=(
                datetime.utcnow()
                if request.status == ApplicationStatus.APPLIED
                else None
            ),
            notes=request.notes,
        )

        application = app_repo.create_application(app_data)

        return ApplicationResponse(
            id=str(application.id),
            job_id=str(application.job_id),
            user_profile_id=str(application.user_profile_id),
            status=application.status,
            applied_date=application.applied_date,
            notes=application.notes,
            created_at=application.created_at,
            updated_at=application.updated_at,
            job_title=job.title,
            company=job.company,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_applications(
    user_profile_id: str = Query(DEFAULT_USER_ID, description="User profile ID"),
    status: Optional[ApplicationStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Limit"),
):
    """Get user's job applications."""
    try:
        app_repo = get_application_repository()
        job_repo = get_job_repository()

        applications, total = app_repo.get_applications(
            user_profile_id=user_profile_id, status=status, limit=limit, offset=0
        )

        # Enrich with job data
        app_responses = []
        for app in applications:
            job = job_repo.get_job(app.job_id)
            app_response = ApplicationResponse(
                id=str(app.id),
                job_id=str(app.job_id),
                user_profile_id=str(app.user_profile_id),
                status=app.status,
                applied_date=app.applied_date,
                notes=app.notes,
                created_at=app.created_at,
                updated_at=app.updated_at,
                job_title=job.title if job else "Unknown Job",
                company=job.company if job else "Unknown Company",
            )
            app_responses.append(app_response)

        return {"applications": app_responses, "total": total}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{application_id}")
def get_application(application_id: str):
    """Get a specific job application."""
    try:
        app_repo = get_application_repository()
        job_repo = get_job_repository()

        application = app_repo.get_application(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        job = job_repo.get_job(application.job_id)

        return ApplicationResponse(
            id=str(application.id),
            job_id=str(application.job_id),
            user_profile_id=str(application.user_profile_id),
            status=application.status,
            applied_date=application.applied_date,
            notes=application.notes,
            created_at=application.created_at,
            updated_at=application.updated_at,
            job_title=job.title if job else "Unknown Job",
            company=job.company if job else "Unknown Company",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{application_id}")
def update_application(
    application_id: str,
    status: Optional[ApplicationStatus] = None,
    notes: Optional[str] = None,
):
    """Update a job application."""
    try:
        app_repo = get_application_repository()
        job_repo = get_job_repository()

        # Prepare update data
        update_data = {}
        if status is not None:
            update_data["status"] = status
            if (
                status == ApplicationStatus.APPLIED
                and "applied_date" not in update_data
            ):
                update_data["applied_date"] = datetime.utcnow()
        if notes is not None:
            update_data["notes"] = notes

        # Update application
        updated_app = app_repo.update_application(application_id, update_data)
        if not updated_app:
            raise HTTPException(status_code=404, detail="Application not found")

        job = job_repo.get_job(updated_app.job_id)

        return ApplicationResponse(
            id=str(updated_app.id),
            job_id=str(updated_app.job_id),
            user_profile_id=str(updated_app.user_profile_id),
            status=updated_app.status,
            applied_date=updated_app.applied_date,
            notes=updated_app.notes,
            created_at=updated_app.created_at,
            updated_at=updated_app.updated_at,
            job_title=job.title if job else "Unknown Job",
            company=job.company if job else "Unknown Company",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{application_id}")
def delete_application(application_id: str):
    """Delete a job application."""
    try:
        app_repo = get_application_repository()

        success = app_repo.delete_application(application_id)
        if not success:
            raise HTTPException(status_code=404, detail="Application not found")

        return {"message": "Application deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
