"""
Applications API
Job application management endpoints for JobPilot
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..data.database import (
    get_application_repository,
    get_database_manager,
    get_job_repository,
    get_user_repository,
)
from ..data.models import (
    ApplicationStatus,
    JobApplication,
    JobApplicationDB,
    JobListingDB,
    TimelineEvent,
    TimelineEventType,
)

router = APIRouter(prefix="/applications", tags=["applications"])

# =====================================
# Request/Response Models
# =====================================


class CreateApplicationRequest(BaseModel):
    """Request model for creating a new job application."""

    job_id: str
    user_profile_id: str
    status: ApplicationStatus = ApplicationStatus.NOT_APPLIED
    applied_date: Optional[datetime] = None
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None


class UpdateApplicationRequest(BaseModel):
    """Request model for updating a job application."""

    status: Optional[ApplicationStatus] = None
    applied_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    interview_scheduled: Optional[datetime] = None


class ApplicationResponse(BaseModel):
    """Response model for job application data."""

    id: str
    job_id: str
    user_profile_id: str
    status: ApplicationStatus
    applied_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    interview_scheduled: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Related data
    job: Optional[Dict[str, Any]] = None
    user_profile: Optional[Dict[str, Any]] = None


class ApplicationsListResponse(BaseModel):
    """Response model for applications list."""

    applications: List[ApplicationResponse]
    total: int
    page: int
    page_size: int


# =====================================
# API Endpoints
# =====================================


@router.post("/", response_model=ApplicationResponse)
async def create_application(request: CreateApplicationRequest):
    """Create a new job application."""
    try:
        app_repo = get_application_repository()
        job_repo = get_job_repository()

        # Verify job exists
        job = job_repo.get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Check if application already exists for this job/user combination
        existing_app = app_repo.get_application_by_job_and_user(
            request.job_id, request.user_profile_id
        )
        if existing_app:
            raise HTTPException(
                status_code=400, detail="Application already exists for this job"
            )

        # Create application
        app_data = JobApplication(
            id=str(uuid4()),
            job_id=request.job_id,
            user_profile_id=request.user_profile_id,
            status=request.status,
            applied_date=request.applied_date
            or (
                datetime.utcnow()
                if request.status != ApplicationStatus.NOT_APPLIED
                else None
            ),
            resume_version=request.resume_version,
            cover_letter=request.cover_letter,
            notes=request.notes,
        )

        application = app_repo.create_application(app_data)

        # TODO: Create timeline event (implement when timeline service is ready)

        # Get full application data with job info
        app_response = get_application_response(application.id)
        return app_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ApplicationsListResponse)
async def get_applications(
    user_profile_id: str = Query(..., description="User profile ID"),
    status: Optional[ApplicationStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db=Depends(get_database_manager),
):
    """Get user's job applications with filtering and pagination."""
    try:
        offset = (page - 1) * page_size

        applications, total = await db.get_applications(
            user_profile_id=user_profile_id,
            status=status,
            limit=page_size,
            offset=offset,
        )

        app_responses = []
        for app in applications:
            app_response = await get_application_response(app.id, db)
            app_responses.append(app_response)

        return ApplicationsListResponse(
            applications=app_responses, total=total, page=page, page_size=page_size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: str, db=Depends(get_database_manager)):
    """Get a specific job application."""
    try:
        app_response = await get_application_response(application_id, db)
        if not app_response:
            raise HTTPException(status_code=404, detail="Application not found")
        return app_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    request: UpdateApplicationRequest,
    db=Depends(get_database_manager),
):
    """Update a job application."""
    try:
        # Get existing application
        existing_app = await db.get_application(application_id)
        if not existing_app:
            raise HTTPException(status_code=404, detail="Application not found")

        # Prepare update data
        update_data = {}
        if request.status is not None:
            update_data["status"] = request.status
        if request.applied_date is not None:
            update_data["applied_date"] = request.applied_date
        if request.response_date is not None:
            update_data["response_date"] = request.response_date
        if request.resume_version is not None:
            update_data["resume_version"] = request.resume_version
        if request.cover_letter is not None:
            update_data["cover_letter"] = request.cover_letter
        if request.notes is not None:
            update_data["notes"] = request.notes
        if request.follow_up_date is not None:
            update_data["follow_up_date"] = request.follow_up_date
        if request.interview_scheduled is not None:
            update_data["interview_scheduled"] = request.interview_scheduled

        # Update application
        await db.update_application(application_id, update_data)

        # Create timeline event for status changes
        if request.status and request.status != existing_app.status:
            job = await db.get_job(existing_app.job_id)
            timeline_event = await create_status_change_timeline_event(
                existing_app, request.status, job, db
            )
            if timeline_event:
                await db.create_timeline_event(timeline_event)

        # Get updated application data
        app_response = await get_application_response(application_id, db)
        return app_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{application_id}")
async def delete_application(application_id: str, db=Depends(get_database_manager)):
    """Delete a job application."""
    try:
        # Get existing application
        existing_app = await db.get_application(application_id)
        if not existing_app:
            raise HTTPException(status_code=404, detail="Application not found")

        # Delete related timeline events
        await db.delete_timeline_events_by_application(application_id)

        # Delete application
        await db.delete_application(application_id)

        return {"message": "Application deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{application_id}/timeline")
async def get_application_timeline(
    application_id: str, db=Depends(get_database_manager)
):
    """Get timeline events for a specific application."""
    try:
        # Verify application exists
        application = await db.get_application(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # Get timeline events
        timeline_events = await db.get_application_timeline(application_id)

        return {"application_id": application_id, "events": timeline_events}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================
# Helper Functions
# =====================================


def get_application_response(application_id: str) -> Optional[ApplicationResponse]:
    """Get full application data with related job and user profile info."""
    app_repo = get_application_repository()
    job_repo = get_job_repository()
    user_repo = get_user_repository()

    application = app_repo.get_application(application_id)
    if not application:
        return None

    # Get related job data
    job = job_repo.get_job(application.job_id)
    job_data = (
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "remote_type": job.remote_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "posted_date": job.posted_date,
            "job_url": job.job_url,
        }
        if job
        else None
    )

    # Get user profile data (basic info only)
    user_profile = user_repo.get_user(application.user_profile_id)
    profile_data = (
        {
            "id": user_profile.id,
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "email": user_profile.email,
            "current_title": user_profile.current_title,
        }
        if user_profile
        else None
    )

    return ApplicationResponse(
        id=application.id,
        job_id=application.job_id,
        user_profile_id=application.user_profile_id,
        status=application.status,
        applied_date=application.applied_date,
        response_date=application.response_date,
        resume_version=application.resume_version,
        cover_letter=application.cover_letter,
        notes=application.notes,
        follow_up_date=application.follow_up_date,
        interview_scheduled=application.interview_scheduled,
        created_at=application.created_at,
        updated_at=application.updated_at,
        job=job_data,
        user_profile=profile_data,
    )


async def create_status_change_timeline_event(
    application: JobApplicationDB,
    new_status: ApplicationStatus,
    job: Optional[JobListingDB],
    db,
) -> Optional[TimelineEvent]:
    """Create a timeline event for application status changes."""
    if not job:
        return None

    # Map status to event type and details
    event_mapping = {
        ApplicationStatus.APPLIED: {
            "type": TimelineEventType.APPLICATION_SUBMITTED,
            "title": f"Applied to {job.title}",
            "description": f"Submitted application to {job.company}",
            "is_milestone": True,
        },
        ApplicationStatus.INTERVIEWING: {
            "type": TimelineEventType.INTERVIEW_SCHEDULED,
            "title": f"Interview scheduled for {job.title}",
            "description": f"Interview process started with {job.company}",
            "is_milestone": True,
        },
        ApplicationStatus.ACCEPTED: {
            "type": TimelineEventType.OFFER_RECEIVED,
            "title": f"Offer received from {job.company}",
            "description": f"Job offer received for {job.title}",
            "is_milestone": True,
        },
        ApplicationStatus.REJECTED: {
            "type": TimelineEventType.STATUS_CHANGED,
            "title": f"Application rejected - {job.title}",
            "description": f"Application was not selected by {job.company}",
            "is_milestone": False,
        },
        ApplicationStatus.WITHDRAWN: {
            "type": TimelineEventType.STATUS_CHANGED,
            "title": f"Application withdrawn - {job.title}",
            "description": f"Withdrew application from {job.company}",
            "is_milestone": False,
        },
    }

    event_info = event_mapping.get(new_status)
    if not event_info:
        return None

    return TimelineEvent(
        job_id=application.job_id,
        application_id=application.id,
        user_profile_id=application.user_profile_id,
        event_type=event_info["type"],
        title=event_info["title"],
        description=event_info["description"],
        event_data={
            "job_title": job.title,
            "company": job.company,
            "old_status": application.status.value,
            "new_status": new_status.value,
        },
        is_milestone=event_info["is_milestone"],
    )
