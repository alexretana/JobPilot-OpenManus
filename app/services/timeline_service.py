"""
Timeline Service for Job Application Tracking

This service handles timeline events for job applications including:
- Creating events for job saves, applications, interviews, etc.
- Retrieving timeline data for display
- Managing event data and milestones
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.data.models import (
    TimelineEvent,
    TimelineEventDB,
    TimelineEventType,
    pydantic_to_sqlalchemy,
    sqlalchemy_to_pydantic,
)

logger = logging.getLogger(__name__)


class TimelineService:
    """Service for managing timeline events in job applications."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_event(
        self,
        user_profile_id: str,
        event_type: TimelineEventType,
        title: str,
        description: Optional[str] = None,
        job_id: Optional[str] = None,
        application_id: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        event_date: Optional[datetime] = None,
        is_milestone: bool = False,
    ) -> TimelineEvent:
        """Create a new timeline event."""

        try:
            # Create the event
            event = TimelineEvent(
                user_profile_id=user_profile_id,
                event_type=event_type,
                title=title,
                description=description,
                job_id=job_id,
                application_id=application_id,
                event_data=event_data or {},
                event_date=event_date or datetime.utcnow(),
                is_milestone=is_milestone,
            )

            # Convert to SQLAlchemy and save
            event_db = pydantic_to_sqlalchemy(event, TimelineEventDB)
            self.db.add(event_db)
            self.db.commit()
            self.db.refresh(event_db)

            # Convert back to Pydantic
            return sqlalchemy_to_pydantic(event_db, TimelineEvent)

        except Exception as e:
            logger.error(f"Error creating timeline event: {e}")
            self.db.rollback()
            raise

    def get_user_timeline(
        self,
        user_profile_id: str,
        limit: int = 50,
        offset: int = 0,
        job_id: Optional[str] = None,
        event_types: Optional[List[TimelineEventType]] = None,
        days_back: Optional[int] = None,
    ) -> List[TimelineEvent]:
        """Get timeline events for a user, with optional filtering."""

        try:
            query = self.db.query(TimelineEventDB).filter(
                TimelineEventDB.user_profile_id == user_profile_id
            )

            # Filter by job if specified
            if job_id:
                query = query.filter(TimelineEventDB.job_id == job_id)

            # Filter by event types if specified
            if event_types:
                query = query.filter(TimelineEventDB.event_type.in_(event_types))

            # Filter by time range if specified
            if days_back:
                cutoff_date = datetime.utcnow() - timedelta(days=days_back)
                query = query.filter(TimelineEventDB.event_date >= cutoff_date)

            # Order by event date (most recent first)
            query = query.order_by(desc(TimelineEventDB.event_date))

            # Apply pagination
            events_db = query.offset(offset).limit(limit).all()

            # Convert to Pydantic models
            return [
                sqlalchemy_to_pydantic(event_db, TimelineEvent)
                for event_db in events_db
            ]

        except Exception as e:
            logger.error(f"Error retrieving user timeline: {e}")
            raise

    def get_job_timeline(
        self, job_id: str, user_profile_id: Optional[str] = None, limit: int = 50
    ) -> List[TimelineEvent]:
        """Get timeline events for a specific job."""

        try:
            query = self.db.query(TimelineEventDB).filter(
                TimelineEventDB.job_id == job_id
            )

            # Filter by user if specified
            if user_profile_id:
                query = query.filter(TimelineEventDB.user_profile_id == user_profile_id)

            # Order by event date (most recent first)
            events_db = (
                query.order_by(desc(TimelineEventDB.event_date)).limit(limit).all()
            )

            # Convert to Pydantic models
            return [
                sqlalchemy_to_pydantic(event_db, TimelineEvent)
                for event_db in events_db
            ]

        except Exception as e:
            logger.error(f"Error retrieving job timeline: {e}")
            raise

    def get_application_timeline(
        self, application_id: str, limit: int = 50
    ) -> List[TimelineEvent]:
        """Get timeline events for a specific application ID.

        Note: With the new job_user_interactions structure, this method
        now simply filters timeline events by the application_id field.
        """

        try:
            query = self.db.query(TimelineEventDB).filter(
                TimelineEventDB.application_id == application_id
            )

            # Order by event date (chronological order for application timeline)
            events_db = query.order_by(TimelineEventDB.event_date).limit(limit).all()

            # Convert to Pydantic models
            return [
                sqlalchemy_to_pydantic(event_db, TimelineEvent)
                for event_db in events_db
            ]

        except Exception as e:
            logger.error(f"Error retrieving application timeline: {e}")
            raise

    def update_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        event_date: Optional[datetime] = None,
        is_milestone: Optional[bool] = None,
    ) -> Optional[TimelineEvent]:
        """Update an existing timeline event."""

        try:
            event_db = (
                self.db.query(TimelineEventDB)
                .filter(TimelineEventDB.id == event_id)
                .first()
            )

            if not event_db:
                return None

            # Update fields if provided
            if title is not None:
                event_db.title = title
            if description is not None:
                event_db.description = description
            if event_data is not None:
                event_db.event_data = event_data
            if event_date is not None:
                event_db.event_date = event_date
            if is_milestone is not None:
                event_db.is_milestone = is_milestone

            # Update timestamp
            event_db.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(event_db)

            # Convert back to Pydantic
            return sqlalchemy_to_pydantic(event_db, TimelineEvent)

        except Exception as e:
            logger.error(f"Error updating timeline event: {e}")
            self.db.rollback()
            raise

    def delete_event(self, event_id: str) -> bool:
        """Delete a timeline event."""

        try:
            event_db = (
                self.db.query(TimelineEventDB)
                .filter(TimelineEventDB.id == event_id)
                .first()
            )

            if not event_db:
                return False

            self.db.delete(event_db)
            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error deleting timeline event: {e}")
            self.db.rollback()
            raise

    # Convenience methods for creating specific types of events

    def log_job_saved(
        self,
        user_profile_id: str,
        job_id: str,
        job_title: str,
        company_name: str,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> TimelineEvent:
        """Log when a user saves a job."""

        event_data = {"job_title": job_title, "company_name": company_name}
        if notes:
            event_data["notes"] = notes
        if tags:
            event_data["tags"] = tags

        return self.create_event(
            user_profile_id=user_profile_id,
            event_type=TimelineEventType.JOB_SAVED,
            title=f"Saved job: {job_title} at {company_name}",
            description=notes,
            job_id=job_id,
            event_data=event_data,
        )

    def log_application_submitted(
        self,
        user_profile_id: str,
        job_id: str,
        application_id: str,
        job_title: str,
        company_name: str,
        application_method: Optional[str] = None,
    ) -> TimelineEvent:
        """Log when a user submits an application."""

        event_data = {"job_title": job_title, "company_name": company_name}
        if application_method:
            event_data["application_method"] = application_method

        return self.create_event(
            user_profile_id=user_profile_id,
            event_type=TimelineEventType.APPLICATION_SUBMITTED,
            title=f"Applied to {job_title} at {company_name}",
            description=f"Application submitted{' via ' + application_method if application_method else ''}",
            job_id=job_id,
            application_id=application_id,
            event_data=event_data,
            is_milestone=True,
        )

    def log_interview_scheduled(
        self,
        user_profile_id: str,
        job_id: str,
        application_id: str,
        job_title: str,
        company_name: str,
        interview_date: datetime,
        interview_type: Optional[str] = None,
        interviewer: Optional[str] = None,
    ) -> TimelineEvent:
        """Log when an interview is scheduled."""

        event_data = {
            "job_title": job_title,
            "company_name": company_name,
            "interview_date": interview_date.isoformat(),
        }
        if interview_type:
            event_data["interview_type"] = interview_type
        if interviewer:
            event_data["interviewer"] = interviewer

        return self.create_event(
            user_profile_id=user_profile_id,
            event_type=TimelineEventType.INTERVIEW_SCHEDULED,
            title=f"Interview scheduled for {job_title} at {company_name}",
            description=f"Interview on {interview_date.strftime('%Y-%m-%d %H:%M')}{' (' + interview_type + ')' if interview_type else ''}",
            job_id=job_id,
            application_id=application_id,
            event_data=event_data,
            event_date=interview_date,
            is_milestone=True,
        )

    def log_status_change(
        self,
        user_profile_id: str,
        job_id: str,
        application_id: str,
        job_title: str,
        company_name: str,
        old_status: str,
        new_status: str,
        notes: Optional[str] = None,
    ) -> TimelineEvent:
        """Log when an application status changes."""

        event_data = {
            "job_title": job_title,
            "company_name": company_name,
            "old_status": old_status,
            "new_status": new_status,
        }
        if notes:
            event_data["notes"] = notes

        # Determine if this is a milestone
        milestone_statuses = ["interviewing", "offered", "accepted", "rejected"]
        is_milestone = new_status.lower() in milestone_statuses

        return self.create_event(
            user_profile_id=user_profile_id,
            event_type=TimelineEventType.STATUS_CHANGED,
            title=f"Status changed for {job_title} at {company_name}: {new_status.title()}",
            description=f"Status updated from '{old_status}' to '{new_status}'{': ' + notes if notes else ''}",
            job_id=job_id,
            application_id=application_id,
            event_data=event_data,
            is_milestone=is_milestone,
        )

    def log_custom_event(
        self,
        user_profile_id: str,
        title: str,
        description: Optional[str] = None,
        job_id: Optional[str] = None,
        application_id: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        event_date: Optional[datetime] = None,
        is_milestone: bool = False,
    ) -> TimelineEvent:
        """Log a custom user-defined event."""

        return self.create_event(
            user_profile_id=user_profile_id,
            event_type=TimelineEventType.CUSTOM_EVENT,
            title=title,
            description=description,
            job_id=job_id,
            application_id=application_id,
            event_data=event_data,
            event_date=event_date,
            is_milestone=is_milestone,
        )

    def get_milestones(
        self, user_profile_id: str, limit: int = 20, days_back: Optional[int] = 30
    ) -> List[TimelineEvent]:
        """Get milestone events for a user."""

        return self.get_user_timeline(
            user_profile_id=user_profile_id, limit=limit, days_back=days_back
        )

    def get_upcoming_events(
        self, user_profile_id: str, days_ahead: int = 7, limit: int = 10
    ) -> List[TimelineEvent]:
        """Get upcoming timeline events (like scheduled interviews)."""

        try:
            future_date = datetime.utcnow() + timedelta(days=days_ahead)

            events_db = (
                self.db.query(TimelineEventDB)
                .filter(
                    and_(
                        TimelineEventDB.user_profile_id == user_profile_id,
                        TimelineEventDB.event_date > datetime.utcnow(),
                        TimelineEventDB.event_date <= future_date,
                    )
                )
                .order_by(TimelineEventDB.event_date)
                .limit(limit)
                .all()
            )

            return [
                sqlalchemy_to_pydantic(event_db, TimelineEvent)
                for event_db in events_db
            ]

        except Exception as e:
            logger.error(f"Error retrieving upcoming events: {e}")
            raise
