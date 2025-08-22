"""
Job User Interaction Repository
Manages all user-job interactions (saved, applied, viewed, etc.)

This repository replaces separate JobApplication and SavedJob repositories
by using the consolidated JobUserInteractionDB model to handle all types
of user interactions with jobs.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.data.models import (
    ApplicationStatus,
    InteractionType,
    JobUserInteractionDB,
    sqlalchemy_to_pydantic,
)
from app.logger import logger
from app.utils.retry import retry_db_write


class JobUserInteractionRepository:
    """Repository for managing all user-job interactions."""

    def __init__(self, db_manager):
        """Initialize interaction repository."""
        self.db_manager = db_manager

    @retry_db_write()
    def save_job(
        self,
        user_id: str,
        job_id: str,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        interaction_data: Optional[Dict[str, Any]] = None,
    ) -> JobUserInteractionDB:
        """Save a job for later viewing.

        Args:
            user_id: ID of the user saving the job
            job_id: ID of the job being saved
            notes: Optional notes about why the job was saved
            tags: Optional tags for organizing saved jobs
            interaction_data: Optional flexible data storage

        Returns:
            JobUserInteractionDB: The saved job interaction record
        """
        try:
            with self.db_manager.get_session() as session:
                # Check if user has already saved this job
                existing = self._get_existing_interaction(
                    session, user_id, job_id, InteractionType.SAVED
                )

                current_time = datetime.utcnow()

                if existing:
                    # Update existing saved job
                    existing.notes = notes
                    existing.tags = tags or []
                    existing.interaction_data = interaction_data or {}
                    existing.last_interaction = current_time
                    existing.interaction_count = existing.interaction_count + 1
                    session.flush()
                    session.refresh(existing)

                    result = sqlalchemy_to_pydantic(existing, JobUserInteractionDB)
                    logger.info(f"Updated saved job: {job_id} for user: {user_id}")
                    return result
                else:
                    # Create new saved job interaction
                    interaction = JobUserInteractionDB(
                        id=str(uuid4()),
                        user_id=user_id,
                        job_id=job_id,
                        interaction_type=InteractionType.SAVED,
                        notes=notes,
                        tags=tags or [],
                        saved_date=current_time,
                        first_interaction=current_time,
                        last_interaction=current_time,
                        interaction_count=1,
                        interaction_data=interaction_data or {},
                    )
                    session.add(interaction)
                    session.flush()
                    session.refresh(interaction)

                    result = sqlalchemy_to_pydantic(interaction, JobUserInteractionDB)
                    logger.info(f"Saved job: {job_id} for user: {user_id}")
                    return result

        except Exception as e:
            logger.error(f"Error saving job {job_id} for user {user_id}: {e}")
            raise

    @retry_db_write()
    def apply_to_job(
        self,
        user_id: str,
        job_id: str,
        resume_version: Optional[str] = None,
        cover_letter: Optional[str] = None,
        interaction_data: Optional[Dict[str, Any]] = None,
    ) -> JobUserInteractionDB:
        """Apply to a job.

        Args:
            user_id: ID of the user applying to the job
            job_id: ID of the job being applied to
            resume_version: Version/name of resume used
            cover_letter: Cover letter text
            interaction_data: Optional flexible data storage

        Returns:
            JobUserInteractionDB: The job application interaction record
        """
        try:
            with self.db_manager.get_session() as session:
                # Check if user has already applied to this job
                existing = self._get_existing_interaction(
                    session, user_id, job_id, InteractionType.APPLIED
                )

                current_time = datetime.utcnow()

                if existing:
                    # Update existing application
                    existing.resume_version = resume_version
                    existing.cover_letter = cover_letter
                    existing.interaction_data = interaction_data or {}
                    existing.last_interaction = current_time
                    existing.interaction_count = existing.interaction_count + 1
                    session.flush()
                    session.refresh(existing)

                    result = sqlalchemy_to_pydantic(existing, JobUserInteractionDB)
                    logger.info(f"Updated application: {job_id} for user: {user_id}")
                    return result
                else:
                    # Create new job application interaction
                    interaction = JobUserInteractionDB(
                        id=str(uuid4()),
                        user_id=user_id,
                        job_id=job_id,
                        interaction_type=InteractionType.APPLIED,
                        application_status=ApplicationStatus.APPLIED,
                        applied_date=current_time,
                        resume_version=resume_version,
                        cover_letter=cover_letter,
                        first_interaction=current_time,
                        last_interaction=current_time,
                        interaction_count=1,
                        interaction_data=interaction_data or {},
                    )
                    session.add(interaction)
                    session.flush()
                    session.refresh(interaction)

                    result = sqlalchemy_to_pydantic(interaction, JobUserInteractionDB)
                    logger.info(f"Applied to job: {job_id} for user: {user_id}")
                    return result

        except Exception as e:
            logger.error(f"Error applying to job {job_id} for user {user_id}: {e}")
            raise

    def get_user_interactions(
        self,
        user_id: str,
        interaction_type: Optional[InteractionType] = None,
        limit: Optional[int] = None,
    ) -> List[JobUserInteractionDB]:
        """Get all interactions for a user.

        Args:
            user_id: ID of the user
            interaction_type: Optional filter by interaction type
            limit: Optional limit on number of results

        Returns:
            List[JobUserInteractionDB]: List of user interactions
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(JobUserInteractionDB).filter(
                    JobUserInteractionDB.user_id == user_id
                )

                if interaction_type:
                    query = query.filter(
                        JobUserInteractionDB.interaction_type == interaction_type
                    )

                # Order by last interaction date (newest first)
                query = query.order_by(JobUserInteractionDB.last_interaction.desc())

                if limit:
                    query = query.limit(limit)

                interactions_db = query.all()

                # Convert to Pydantic models
                interactions = [
                    sqlalchemy_to_pydantic(interaction_db, JobUserInteractionDB)
                    for interaction_db in interactions_db
                ]

                logger.info(
                    f"Retrieved {len(interactions)} interactions for user: {user_id}"
                    + (f" of type: {interaction_type}" if interaction_type else "")
                )
                return interactions

        except Exception as e:
            logger.error(f"Error getting interactions for user {user_id}: {e}")
            return []

    def get_saved_jobs(
        self, user_id: str, limit: Optional[int] = None
    ) -> List[JobUserInteractionDB]:
        """Get user's saved jobs.

        Args:
            user_id: ID of the user
            limit: Optional limit on number of results

        Returns:
            List[JobUserInteractionDB]: List of saved job interactions
        """
        return self.get_user_interactions(
            user_id, interaction_type=InteractionType.SAVED, limit=limit
        )

    def get_applications(
        self,
        user_id: str,
        status: Optional[ApplicationStatus] = None,
        limit: Optional[int] = None,
    ) -> List[JobUserInteractionDB]:
        """Get user's job applications.

        Args:
            user_id: ID of the user
            status: Optional filter by application status
            limit: Optional limit on number of results

        Returns:
            List[JobUserInteractionDB]: List of job application interactions
        """
        interactions = self.get_user_interactions(
            user_id, interaction_type=InteractionType.APPLIED, limit=limit
        )

        if status:
            interactions = [
                interaction
                for interaction in interactions
                if interaction.application_status == status
            ]

        return interactions

    @retry_db_write()
    def record_job_view(
        self,
        user_id: str,
        job_id: str,
        interaction_data: Optional[Dict[str, Any]] = None,
    ) -> JobUserInteractionDB:
        """Record that a user viewed a job.

        Args:
            user_id: ID of the user viewing the job
            job_id: ID of the job being viewed
            interaction_data: Optional flexible data storage

        Returns:
            JobUserInteractionDB: The job view interaction record
        """
        try:
            with self.db_manager.get_session() as session:
                # Check if user has already viewed this job
                existing = self._get_existing_interaction(
                    session, user_id, job_id, InteractionType.VIEWED
                )

                current_time = datetime.utcnow()

                if existing:
                    # Update existing view record
                    existing.last_interaction = current_time
                    existing.interaction_count = existing.interaction_count + 1
                    if interaction_data:
                        existing.interaction_data.update(interaction_data)
                    session.flush()
                    session.refresh(existing)

                    result = sqlalchemy_to_pydantic(existing, JobUserInteractionDB)
                    logger.debug(
                        f"Updated job view: {job_id} for user: {user_id} (count: {existing.interaction_count})"
                    )
                    return result
                else:
                    # Create new job view interaction
                    interaction = JobUserInteractionDB(
                        id=str(uuid4()),
                        user_id=user_id,
                        job_id=job_id,
                        interaction_type=InteractionType.VIEWED,
                        first_interaction=current_time,
                        last_interaction=current_time,
                        interaction_count=1,
                        interaction_data=interaction_data or {},
                    )
                    session.add(interaction)
                    session.flush()
                    session.refresh(interaction)

                    result = sqlalchemy_to_pydantic(interaction, JobUserInteractionDB)
                    logger.debug(f"Recorded job view: {job_id} for user: {user_id}")
                    return result

        except Exception as e:
            logger.error(f"Error recording job view {job_id} for user {user_id}: {e}")
            raise

    @retry_db_write()
    def hide_job(
        self,
        user_id: str,
        job_id: str,
        reason: Optional[str] = None,
        interaction_data: Optional[Dict[str, Any]] = None,
    ) -> JobUserInteractionDB:
        """Hide a job from user's view.

        Args:
            user_id: ID of the user hiding the job
            job_id: ID of the job being hidden
            reason: Optional reason for hiding
            interaction_data: Optional flexible data storage

        Returns:
            JobUserInteractionDB: The job hide interaction record
        """
        try:
            with self.db_manager.get_session() as session:
                # Check if user has already hidden this job
                existing = self._get_existing_interaction(
                    session, user_id, job_id, InteractionType.HIDDEN
                )

                current_time = datetime.utcnow()

                if existing:
                    # Update existing hide record
                    existing.notes = reason
                    existing.interaction_data = interaction_data or {}
                    existing.last_interaction = current_time
                    session.flush()
                    session.refresh(existing)

                    result = sqlalchemy_to_pydantic(existing, JobUserInteractionDB)
                    logger.info(f"Updated hidden job: {job_id} for user: {user_id}")
                    return result
                else:
                    # Create new job hide interaction
                    interaction = JobUserInteractionDB(
                        id=str(uuid4()),
                        user_id=user_id,
                        job_id=job_id,
                        interaction_type=InteractionType.HIDDEN,
                        notes=reason,
                        first_interaction=current_time,
                        last_interaction=current_time,
                        interaction_count=1,
                        interaction_data=interaction_data or {},
                    )
                    session.add(interaction)
                    session.flush()
                    session.refresh(interaction)

                    result = sqlalchemy_to_pydantic(interaction, JobUserInteractionDB)
                    logger.info(f"Hid job: {job_id} for user: {user_id}")
                    return result

        except Exception as e:
            logger.error(f"Error hiding job {job_id} for user {user_id}: {e}")
            raise

    @retry_db_write()
    def update_application_status(
        self, interaction_id: str, status: ApplicationStatus
    ) -> bool:
        """Update application status.

        Args:
            interaction_id: ID of the interaction to update
            status: New application status

        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            with self.db_manager.get_session() as session:
                interaction_db = (
                    session.query(JobUserInteractionDB)
                    .filter(
                        JobUserInteractionDB.id == interaction_id,
                        JobUserInteractionDB.interaction_type
                        == InteractionType.APPLIED,
                    )
                    .first()
                )

                if not interaction_db:
                    logger.warning(
                        f"Application interaction not found: {interaction_id}"
                    )
                    return False

                old_status = interaction_db.application_status
                interaction_db.application_status = status
                interaction_db.last_interaction = datetime.utcnow()

                # Set response date if status indicates a response from employer
                if status in [
                    ApplicationStatus.INTERVIEWING,
                    ApplicationStatus.REJECTED,
                    ApplicationStatus.ACCEPTED,
                ]:
                    if not interaction_db.response_date:
                        interaction_db.response_date = datetime.utcnow()

                session.flush()

                logger.info(
                    f"Updated application status: {interaction_id} from {old_status} to {status}"
                )
                return True

        except Exception as e:
            logger.error(f"Error updating application status {interaction_id}: {e}")
            return False

    def _get_existing_interaction(
        self, session, user_id: str, job_id: str, interaction_type: InteractionType
    ) -> Optional[JobUserInteractionDB]:
        """Get existing interaction of specific type between user and job.

        Args:
            session: Database session
            user_id: ID of the user
            job_id: ID of the job
            interaction_type: Type of interaction to look for

        Returns:
            Optional[JobUserInteractionDB]: Existing interaction or None
        """
        return (
            session.query(JobUserInteractionDB)
            .filter(
                JobUserInteractionDB.user_id == user_id,
                JobUserInteractionDB.job_id == job_id,
                JobUserInteractionDB.interaction_type == interaction_type,
            )
            .first()
        )
