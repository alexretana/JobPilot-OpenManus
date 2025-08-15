"""
Timeline API endpoints for job application tracking.

This module provides REST API endpoints for:
- Getting user timeline events
- Creating custom timeline events
- Getting job-specific timelines
- Managing timeline milestones
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.data.database import get_database_manager
from app.data.models import TimelineEventType
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


# Request/Response models for timeline API
class CreateTimelineEventRequest(BaseModel):
    """Request model for creating a timeline event."""

    event_type: TimelineEventType
    title: str
    description: Optional[str] = None
    job_id: Optional[str] = None
    application_id: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    event_date: Optional[datetime] = None
    is_milestone: bool = False


class UpdateTimelineEventRequest(BaseModel):
    """Request model for updating a timeline event."""

    title: Optional[str] = None
    description: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    event_date: Optional[datetime] = None
    is_milestone: Optional[bool] = None


class TimelineEventResponse(BaseModel):
    """Response model for timeline events."""

    id: str
    job_id: Optional[str]
    application_id: Optional[str]
    user_profile_id: str
    event_type: TimelineEventType
    title: str
    description: Optional[str]
    event_data: Dict[str, Any]
    event_date: datetime
    is_milestone: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateCustomEventRequest(BaseModel):
    """Request model for creating custom timeline events."""

    title: str
    description: Optional[str] = None
    job_id: Optional[str] = None
    application_id: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    event_date: Optional[datetime] = None
    is_milestone: bool = False


# Database session dependency
def get_database_session():
    """Get database session for timeline operations."""
    db_manager = get_database_manager()
    with db_manager.get_session() as session:
        yield session


# Timeline API endpoints
@router.get("/user/{user_profile_id}", response_model=List[TimelineEventResponse])
def get_user_timeline(
    user_profile_id: str,
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of events to return"
    ),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    event_types: Optional[List[TimelineEventType]] = Query(
        None, description="Filter by event types"
    ),
    days_back: Optional[int] = Query(
        None, ge=1, description="Only include events from the last N days"
    ),
    db: Session = Depends(get_database_session),
):
    """Get timeline events for a specific user."""

    try:
        timeline_service = TimelineService(db)
        events = timeline_service.get_user_timeline(
            user_profile_id=user_profile_id,
            limit=limit,
            offset=offset,
            job_id=job_id,
            event_types=event_types,
            days_back=days_back,
        )

        return [TimelineEventResponse.from_orm(event) for event in events]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving timeline: {str(e)}"
        )


@router.get("/job/{job_id}", response_model=List[TimelineEventResponse])
def get_job_timeline(
    job_id: str,
    user_profile_id: Optional[str] = Query(
        None, description="Filter by user profile ID"
    ),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of events to return"
    ),
    db: Session = Depends(get_database_session),
):
    """Get timeline events for a specific job."""

    try:
        timeline_service = TimelineService(db)
        events = timeline_service.get_job_timeline(
            job_id=job_id, user_profile_id=user_profile_id, limit=limit
        )

        return [TimelineEventResponse.from_orm(event) for event in events]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving job timeline: {str(e)}"
        )


@router.get("/application/{application_id}", response_model=List[TimelineEventResponse])
def get_application_timeline(
    application_id: str,
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of events to return"
    ),
    db: Session = Depends(get_database_session),
):
    """Get timeline events for a specific application."""

    try:
        timeline_service = TimelineService(db)
        events = timeline_service.get_application_timeline(
            application_id=application_id, limit=limit
        )

        return [TimelineEventResponse.from_orm(event) for event in events]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving application timeline: {str(e)}"
        )


@router.get(
    "/user/{user_profile_id}/milestones", response_model=List[TimelineEventResponse]
)
def get_user_milestones(
    user_profile_id: str,
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of milestones to return"
    ),
    days_back: Optional[int] = Query(
        30, ge=1, description="Only include milestones from the last N days"
    ),
    db: Session = Depends(get_database_session),
):
    """Get milestone events for a specific user."""

    try:
        timeline_service = TimelineService(db)
        milestones = timeline_service.get_milestones(
            user_profile_id=user_profile_id, limit=limit, days_back=days_back
        )

        return [TimelineEventResponse.from_orm(milestone) for milestone in milestones]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving milestones: {str(e)}"
        )


@router.get(
    "/user/{user_profile_id}/upcoming", response_model=List[TimelineEventResponse]
)
def get_upcoming_events(
    user_profile_id: str,
    days_ahead: int = Query(7, ge=1, le=30, description="Look ahead this many days"),
    limit: int = Query(
        10, ge=1, le=50, description="Maximum number of events to return"
    ),
    db: Session = Depends(get_database_session),
):
    """Get upcoming timeline events for a specific user (like scheduled interviews)."""

    try:
        timeline_service = TimelineService(db)
        events = timeline_service.get_upcoming_events(
            user_profile_id=user_profile_id, days_ahead=days_ahead, limit=limit
        )

        return [TimelineEventResponse.from_orm(event) for event in events]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving upcoming events: {str(e)}"
        )


@router.post("/user/{user_profile_id}/event", response_model=TimelineEventResponse)
def create_timeline_event(
    user_profile_id: str,
    request: CreateTimelineEventRequest,
    db: Session = Depends(get_database_session),
):
    """Create a new timeline event."""

    try:
        timeline_service = TimelineService(db)
        event = timeline_service.create_event(
            user_profile_id=user_profile_id,
            event_type=request.event_type,
            title=request.title,
            description=request.description,
            job_id=request.job_id,
            application_id=request.application_id,
            event_data=request.event_data,
            event_date=request.event_date,
            is_milestone=request.is_milestone,
        )

        return TimelineEventResponse.from_orm(event)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating timeline event: {str(e)}"
        )


@router.post(
    "/user/{user_profile_id}/custom-event", response_model=TimelineEventResponse
)
def create_custom_event(
    user_profile_id: str,
    request: CreateCustomEventRequest,
    db: Session = Depends(get_database_session),
):
    """Create a custom timeline event."""

    try:
        timeline_service = TimelineService(db)
        event = timeline_service.log_custom_event(
            user_profile_id=user_profile_id,
            title=request.title,
            description=request.description,
            job_id=request.job_id,
            application_id=request.application_id,
            event_data=request.event_data,
            event_date=request.event_date,
            is_milestone=request.is_milestone,
        )

        return TimelineEventResponse.from_orm(event)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating custom event: {str(e)}"
        )


@router.put("/event/{event_id}", response_model=TimelineEventResponse)
def update_timeline_event(
    event_id: str,
    request: UpdateTimelineEventRequest,
    db: Session = Depends(get_database_session),
):
    """Update an existing timeline event."""

    try:
        timeline_service = TimelineService(db)
        event = timeline_service.update_event(
            event_id=event_id,
            title=request.title,
            description=request.description,
            event_data=request.event_data,
            event_date=request.event_date,
            is_milestone=request.is_milestone,
        )

        if not event:
            raise HTTPException(status_code=404, detail="Timeline event not found")

        return TimelineEventResponse.from_orm(event)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating timeline event: {str(e)}"
        )


@router.delete("/event/{event_id}")
def delete_timeline_event(event_id: str, db: Session = Depends(get_database_session)):
    """Delete a timeline event."""

    try:
        timeline_service = TimelineService(db)
        success = timeline_service.delete_event(event_id)

        if not success:
            raise HTTPException(status_code=404, detail="Timeline event not found")

        return {"message": "Timeline event deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting timeline event: {str(e)}"
        )


# Convenience endpoints for specific event types
@router.post(
    "/user/{user_profile_id}/job/{job_id}/saved", response_model=TimelineEventResponse
)
def log_job_saved(
    user_profile_id: str,
    job_id: str,
    job_title: str = Query(..., description="Job title"),
    company_name: str = Query(..., description="Company name"),
    notes: Optional[str] = Query(None, description="Optional notes"),
    tags: Optional[List[str]] = Query(None, description="Optional tags"),
    db: Session = Depends(get_database_session),
):
    """Log when a user saves a job."""

    try:
        timeline_service = TimelineService(db)
        event = timeline_service.log_job_saved(
            user_profile_id=user_profile_id,
            job_id=job_id,
            job_title=job_title,
            company_name=company_name,
            notes=notes,
            tags=tags,
        )

        return TimelineEventResponse.from_orm(event)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error logging job saved event: {str(e)}"
        )


@router.post(
    "/user/{user_profile_id}/application/{application_id}/submitted",
    response_model=TimelineEventResponse,
)
def log_application_submitted(
    user_profile_id: str,
    application_id: str,
    job_id: str = Query(..., description="Job ID"),
    job_title: str = Query(..., description="Job title"),
    company_name: str = Query(..., description="Company name"),
    application_method: Optional[str] = Query(
        None, description="How the application was submitted"
    ),
    db: Session = Depends(get_database_session),
):
    """Log when a user submits an application."""

    try:
        timeline_service = TimelineService(db)
        event = timeline_service.log_application_submitted(
            user_profile_id=user_profile_id,
            job_id=job_id,
            application_id=application_id,
            job_title=job_title,
            company_name=company_name,
            application_method=application_method,
        )

        return TimelineEventResponse.from_orm(event)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error logging application submitted event: {str(e)}",
        )


@router.post(
    "/user/{user_profile_id}/application/{application_id}/interview-scheduled",
    response_model=TimelineEventResponse,
)
def log_interview_scheduled(
    user_profile_id: str,
    application_id: str,
    job_id: str = Query(..., description="Job ID"),
    job_title: str = Query(..., description="Job title"),
    company_name: str = Query(..., description="Company name"),
    interview_date: datetime = Query(..., description="Interview date and time"),
    interview_type: Optional[str] = Query(
        None, description="Type of interview (phone, video, in-person, etc.)"
    ),
    interviewer: Optional[str] = Query(None, description="Interviewer name"),
    db: Session = Depends(get_database_session),
):
    """Log when an interview is scheduled."""

    try:
        timeline_service = TimelineService(db)
        event = timeline_service.log_interview_scheduled(
            user_profile_id=user_profile_id,
            job_id=job_id,
            application_id=application_id,
            job_title=job_title,
            company_name=company_name,
            interview_date=interview_date,
            interview_type=interview_type,
            interviewer=interviewer,
        )

        return TimelineEventResponse.from_orm(event)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error logging interview scheduled event: {str(e)}"
        )


@router.post(
    "/user/{user_profile_id}/application/{application_id}/status-changed",
    response_model=TimelineEventResponse,
)
def log_status_change(
    user_profile_id: str,
    application_id: str,
    job_id: str = Query(..., description="Job ID"),
    job_title: str = Query(..., description="Job title"),
    company_name: str = Query(..., description="Company name"),
    old_status: str = Query(..., description="Previous application status"),
    new_status: str = Query(..., description="New application status"),
    notes: Optional[str] = Query(
        None, description="Optional notes about the status change"
    ),
    db: Session = Depends(get_database_session),
):
    """Log when an application status changes."""

    try:
        timeline_service = TimelineService(db)
        event = timeline_service.log_status_change(
            user_profile_id=user_profile_id,
            job_id=job_id,
            application_id=application_id,
            job_title=job_title,
            company_name=company_name,
            old_status=old_status,
            new_status=new_status,
            notes=notes,
        )

        return TimelineEventResponse.from_orm(event)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error logging status change event: {str(e)}"
        )


@router.get("/event-types", response_model=List[str])
def get_event_types():
    """Get all available timeline event types."""
    return [event_type.value for event_type in TimelineEventType]
