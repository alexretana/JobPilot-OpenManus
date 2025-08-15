"""
JobPilot Database Management
Database operations and repository pattern for job hunting data.
"""

import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import create_engine, text, and_, or_, func, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from app.data.models import (
    Base, JobListingDB, UserProfileDB, JobApplicationDB, CompanyInfoDB, SavedJobDB,
    JobListing, UserProfile, JobApplication, CompanyInfo, SavedJob,
    JobStatus, ApplicationStatus, JobType, RemoteType, ExperienceLevel, SavedJobStatus,
    pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
)
from app.logger import logger


class DatabaseManager:
    """Manages database connections and provides basic operations."""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        if database_url is None:
            # Default to SQLite in the data directory
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            database_url = f"sqlite:///{data_dir}/jobpilot.db"
        
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionFactory = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        self.create_tables()
        
        logger.info(f"Database manager initialized with URL: {database_url}")
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup."""
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_table_stats(self) -> Dict[str, int]:
        """Get statistics about table row counts."""
        stats = {}
        try:
            with self.get_session() as session:
                stats['job_listings'] = session.query(JobListingDB).count()
                stats['user_profiles'] = session.query(UserProfileDB).count()
                stats['applications'] = session.query(JobApplicationDB).count()
                stats['companies'] = session.query(CompanyInfoDB).count()
        except Exception as e:
            logger.error(f"Error getting table stats: {e}")
            stats = {'error': str(e)}
        
        return stats


class JobRepository:
    """Repository for job listing operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize job repository."""
        self.db_manager = db_manager
    
    def create_job(self, job_data: JobListing) -> JobListing:
        """Create a new job listing."""
        try:
            with self.db_manager.get_session() as session:
                job_db = pydantic_to_sqlalchemy(job_data, JobListingDB)
                session.add(job_db)
                session.flush()  # Get the ID
                
                # Convert back to Pydantic model
                result = sqlalchemy_to_pydantic(job_db, JobListing)
                logger.info(f"Created job: {result.title} at {result.company}")
                return result
                
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            raise
    
    def get_job(self, job_id: str) -> Optional[JobListing]:
        """Get job by ID."""
        try:
            with self.db_manager.get_session() as session:
                job_db = session.query(JobListingDB).filter(JobListingDB.id == job_id).first()
                if job_db:
                    return sqlalchemy_to_pydantic(job_db, JobListing)
                return None
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {e}")
            return None
    
    def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Optional[JobListing]:
        """Update job listing."""
        try:
            with self.db_manager.get_session() as session:
                job_db = session.query(JobListingDB).filter(JobListingDB.id == job_id).first()
                if not job_db:
                    return None
                
                # Update fields
                for field, value in job_data.items():
                    if hasattr(job_db, field):
                        setattr(job_db, field, value)
                
                job_db.updated_at = datetime.utcnow()
                session.flush()
                
                result = sqlalchemy_to_pydantic(job_db, JobListing)
                logger.info(f"Updated job: {job_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            raise
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job listing."""
        try:
            with self.db_manager.get_session() as session:
                job_db = session.query(JobListingDB).filter(JobListingDB.id == job_id).first()
                if job_db:
                    session.delete(job_db)
                    logger.info(f"Deleted job: {job_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}")
            return False
    
    def search_jobs(
        self,
        query: Optional[str] = None,
        job_types: Optional[List[JobType]] = None,
        remote_types: Optional[List[RemoteType]] = None,
        experience_levels: Optional[List[ExperienceLevel]] = None,
        locations: Optional[List[str]] = None,
        companies: Optional[List[str]] = None,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        max_age_days: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[JobListing], int]:
        """Search jobs with filters."""
        try:
            with self.db_manager.get_session() as session:
                query_obj = session.query(JobListingDB).filter(
                    JobListingDB.status == JobStatus.ACTIVE
                )
                
                # Text search across title, company, and description
                if query:
                    search_filter = or_(
                        JobListingDB.title.ilike(f"%{query}%"),
                        JobListingDB.company.ilike(f"%{query}%"),
                        JobListingDB.description.ilike(f"%{query}%"),
                        JobListingDB.requirements.ilike(f"%{query}%")
                    )
                    query_obj = query_obj.filter(search_filter)
                
                # Filter by job types
                if job_types:
                    query_obj = query_obj.filter(JobListingDB.job_type.in_(job_types))
                
                # Filter by remote types
                if remote_types:
                    query_obj = query_obj.filter(JobListingDB.remote_type.in_(remote_types))
                
                # Filter by experience levels
                if experience_levels:
                    query_obj = query_obj.filter(JobListingDB.experience_level.in_(experience_levels))
                
                # Filter by locations
                if locations:
                    location_filters = [JobListingDB.location.ilike(f"%{loc}%") for loc in locations]
                    query_obj = query_obj.filter(or_(*location_filters))
                
                # Filter by companies
                if companies:
                    query_obj = query_obj.filter(JobListingDB.company.in_(companies))
                
                # Salary filters
                if min_salary is not None:
                    query_obj = query_obj.filter(
                        or_(
                            JobListingDB.salary_min >= min_salary,
                            JobListingDB.salary_max >= min_salary
                        )
                    )
                
                if max_salary is not None:
                    query_obj = query_obj.filter(
                        or_(
                            JobListingDB.salary_max <= max_salary,
                            JobListingDB.salary_min <= max_salary
                        )
                    )
                
                # Age filter
                if max_age_days is not None:
                    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
                    query_obj = query_obj.filter(JobListingDB.created_at >= cutoff_date)
                
                # Get total count
                total_count = query_obj.count()
                
                # Apply pagination and ordering
                jobs_db = (query_obj
                          .order_by(desc(JobListingDB.created_at))
                          .offset(offset)
                          .limit(limit)
                          .all())
                
                # Convert to Pydantic models
                jobs = [sqlalchemy_to_pydantic(job_db, JobListing) for job_db in jobs_db]
                
                logger.info(f"Search returned {len(jobs)} jobs out of {total_count} total")
                return jobs, total_count
                
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return [], 0
    
    def get_recent_jobs(self, limit: int = 20) -> List[JobListing]:
        """Get most recent job listings."""
        try:
            with self.db_manager.get_session() as session:
                jobs_db = (session.query(JobListingDB)
                          .filter(JobListingDB.status == JobStatus.ACTIVE)
                          .order_by(desc(JobListingDB.created_at))
                          .limit(limit)
                          .all())
                
                jobs = [sqlalchemy_to_pydantic(job_db, JobListing) for job_db in jobs_db]
                logger.info(f"Retrieved {len(jobs)} recent jobs")
                return jobs
                
        except Exception as e:
            logger.error(f"Error getting recent jobs: {e}")
            return []
    
    def get_jobs_by_company(self, company: str, limit: int = 20) -> List[JobListing]:
        """Get jobs by company name."""
        try:
            with self.db_manager.get_session() as session:
                jobs_db = (session.query(JobListingDB)
                          .filter(
                              and_(
                                  JobListingDB.company.ilike(f"%{company}%"),
                                  JobListingDB.status == JobStatus.ACTIVE
                              )
                          )
                          .order_by(desc(JobListingDB.created_at))
                          .limit(limit)
                          .all())
                
                jobs = [sqlalchemy_to_pydantic(job_db, JobListing) for job_db in jobs_db]
                logger.info(f"Retrieved {len(jobs)} jobs for company: {company}")
                return jobs
                
        except Exception as e:
            logger.error(f"Error getting jobs for company {company}: {e}")
            return []
    
    def bulk_create_jobs(self, jobs_data: List[JobListing]) -> int:
        """Create multiple job listings efficiently."""
        try:
            with self.db_manager.get_session() as session:
                jobs_db = [pydantic_to_sqlalchemy(job_data, JobListingDB) for job_data in jobs_data]
                session.add_all(jobs_db)
                session.flush()
                
                count = len(jobs_db)
                logger.info(f"Bulk created {count} jobs")
                return count
                
        except Exception as e:
            logger.error(f"Error bulk creating jobs: {e}")
            raise
    
    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """Update job status."""
        try:
            with self.db_manager.get_session() as session:
                job_db = session.query(JobListingDB).filter(JobListingDB.id == job_id).first()
                if job_db:
                    job_db.status = status
                    job_db.updated_at = datetime.utcnow()
                    logger.info(f"Updated job {job_id} status to {status}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating job status {job_id}: {e}")
            return False


class UserRepository:
    """Repository for user profile operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize user repository."""
        self.db_manager = db_manager
    
    def create_user(self, user_data: UserProfile) -> UserProfile:
        """Create a new user profile."""
        try:
            with self.db_manager.get_session() as session:
                user_db = pydantic_to_sqlalchemy(user_data, UserProfileDB)
                session.add(user_db)
                session.flush()
                
                result = sqlalchemy_to_pydantic(user_db, UserProfile)
                logger.info(f"Created user profile: {result.email}")
                return result
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID."""
        try:
            with self.db_manager.get_session() as session:
                user_db = session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
                if user_db:
                    return sqlalchemy_to_pydantic(user_db, UserProfile)
                return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email."""
        try:
            with self.db_manager.get_session() as session:
                user_db = session.query(UserProfileDB).filter(UserProfileDB.email == email).first()
                if user_db:
                    return sqlalchemy_to_pydantic(user_db, UserProfile)
                return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile."""
        try:
            with self.db_manager.get_session() as session:
                user_db = session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
                if not user_db:
                    return None
                
                # Update fields
                for field, value in user_data.items():
                    if hasattr(user_db, field):
                        setattr(user_db, field, value)
                
                user_db.updated_at = datetime.utcnow()
                session.flush()
                
                result = sqlalchemy_to_pydantic(user_db, UserProfile)
                logger.info(f"Updated user profile: {user_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user profile."""
        try:
            with self.db_manager.get_session() as session:
                user_db = session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
                if user_db:
                    session.delete(user_db)
                    logger.info(f"Deleted user profile: {user_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    def list_users(self, limit: int = 50, offset: int = 0) -> Tuple[List[UserProfile], int]:
        """List all user profiles with pagination."""
        try:
            with self.db_manager.get_session() as session:
                query_obj = session.query(UserProfileDB)
                
                # Get total count
                total_count = query_obj.count()
                
                # Apply pagination and ordering
                users_db = (query_obj
                           .order_by(desc(UserProfileDB.created_at))
                           .offset(offset)
                           .limit(limit)
                           .all())
                
                # Convert to Pydantic models
                users = [sqlalchemy_to_pydantic(user_db, UserProfile) for user_db in users_db]
                
                logger.info(f"Listed {len(users)} users out of {total_count} total")
                return users, total_count
                
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return [], 0


class SavedJobRepository:
    """Repository for saved job operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize saved job repository."""
        self.db_manager = db_manager
    
    def save_job(self, job_id: str, user_profile_id: str, notes: Optional[str] = None, tags: Optional[List[str]] = None) -> SavedJob:
        """Save a job for a user."""
        try:
            with self.db_manager.get_session() as session:
                # Check if job is already saved
                existing = session.query(SavedJobDB).filter(
                    and_(
                        SavedJobDB.job_id == job_id,
                        SavedJobDB.user_profile_id == user_profile_id,
                        SavedJobDB.status == SavedJobStatus.SAVED
                    )
                ).first()
                
                if existing:
                    # Update existing saved job
                    existing.notes = notes
                    existing.tags = tags or []
                    existing.updated_at = datetime.utcnow()
                    result = sqlalchemy_to_pydantic(existing, SavedJob)
                    logger.info(f"Updated saved job: {job_id} for user: {user_profile_id}")
                else:
                    # Create new saved job
                    saved_job_data = SavedJob(
                        job_id=UUID(job_id),
                        user_profile_id=UUID(user_profile_id),
                        notes=notes,
                        tags=tags or []
                    )
                    saved_job_db = pydantic_to_sqlalchemy(saved_job_data, SavedJobDB)
                    session.add(saved_job_db)
                    session.flush()
                    
                    result = sqlalchemy_to_pydantic(saved_job_db, SavedJob)
                    logger.info(f"Saved job: {job_id} for user: {user_profile_id}")
                
                return result
                
        except Exception as e:
            logger.error(f"Error saving job {job_id}: {e}")
            raise
    
    def unsave_job(self, job_id: str, user_profile_id: str) -> bool:
        """Remove a job from saved jobs."""
        try:
            with self.db_manager.get_session() as session:
                saved_job_db = session.query(SavedJobDB).filter(
                    and_(
                        SavedJobDB.job_id == job_id,
                        SavedJobDB.user_profile_id == user_profile_id,
                        SavedJobDB.status == SavedJobStatus.SAVED
                    )
                ).first()
                
                if saved_job_db:
                    session.delete(saved_job_db)
                    logger.info(f"Unsaved job: {job_id} for user: {user_profile_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error unsaving job {job_id}: {e}")
            return False
    
    def get_saved_jobs(self, user_profile_id: str, status: SavedJobStatus = SavedJobStatus.SAVED, limit: int = 50) -> List[Dict[str, Any]]:
        """Get saved jobs for a user with job details."""
        try:
            with self.db_manager.get_session() as session:
                # Join SavedJobDB with JobListingDB to get complete job information
                saved_jobs = (session.query(SavedJobDB, JobListingDB)
                             .join(JobListingDB, SavedJobDB.job_id == JobListingDB.id)
                             .filter(
                                 and_(
                                     SavedJobDB.user_profile_id == user_profile_id,
                                     SavedJobDB.status == status
                                 )
                             )
                             .order_by(desc(SavedJobDB.saved_date))
                             .limit(limit)
                             .all())
                
                result = []
                for saved_job_db, job_db in saved_jobs:
                    job_data = sqlalchemy_to_pydantic(job_db, JobListing)
                    saved_job_data = sqlalchemy_to_pydantic(saved_job_db, SavedJob)
                    
                    result.append({
                        "saved_job": saved_job_data.dict(),
                        "job": job_data.dict()
                    })
                
                logger.info(f"Retrieved {len(result)} saved jobs for user: {user_profile_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error getting saved jobs for user {user_profile_id}: {e}")
            return []
    
    def is_job_saved(self, job_id: str, user_profile_id: str) -> bool:
        """Check if a job is saved by a user."""
        try:
            with self.db_manager.get_session() as session:
                saved_job = session.query(SavedJobDB).filter(
                    and_(
                        SavedJobDB.job_id == job_id,
                        SavedJobDB.user_profile_id == user_profile_id,
                        SavedJobDB.status == SavedJobStatus.SAVED
                    )
                ).first()
                
                return saved_job is not None
                
        except Exception as e:
            logger.error(f"Error checking if job {job_id} is saved: {e}")
            return False
    
    def archive_saved_job(self, job_id: str, user_profile_id: str) -> bool:
        """Archive a saved job (change status to archived)."""
        try:
            with self.db_manager.get_session() as session:
                saved_job_db = session.query(SavedJobDB).filter(
                    and_(
                        SavedJobDB.job_id == job_id,
                        SavedJobDB.user_profile_id == user_profile_id,
                        SavedJobDB.status == SavedJobStatus.SAVED
                    )
                ).first()
                
                if saved_job_db:
                    saved_job_db.status = SavedJobStatus.ARCHIVED
                    saved_job_db.updated_at = datetime.utcnow()
                    logger.info(f"Archived saved job: {job_id} for user: {user_profile_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error archiving saved job {job_id}: {e}")
            return False
    
    def update_saved_job(self, job_id: str, user_profile_id: str, notes: Optional[str] = None, tags: Optional[List[str]] = None) -> Optional[SavedJob]:
        """Update notes and tags for a saved job."""
        try:
            with self.db_manager.get_session() as session:
                saved_job_db = session.query(SavedJobDB).filter(
                    and_(
                        SavedJobDB.job_id == job_id,
                        SavedJobDB.user_profile_id == user_profile_id,
                        SavedJobDB.status == SavedJobStatus.SAVED
                    )
                ).first()
                
                if saved_job_db:
                    if notes is not None:
                        saved_job_db.notes = notes
                    if tags is not None:
                        saved_job_db.tags = tags
                    saved_job_db.updated_at = datetime.utcnow()
                    
                    result = sqlalchemy_to_pydantic(saved_job_db, SavedJob)
                    logger.info(f"Updated saved job: {job_id} for user: {user_profile_id}")
                    return result
                return None
                
        except Exception as e:
            logger.error(f"Error updating saved job {job_id}: {e}")
            return None


class ApplicationRepository:
    """Repository for job application operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize application repository."""
        self.db_manager = db_manager
    
    def create_application(self, app_data: JobApplication) -> JobApplication:
        """Create a new job application."""
        try:
            with self.db_manager.get_session() as session:
                app_db = pydantic_to_sqlalchemy(app_data, JobApplicationDB)
                session.add(app_db)
                session.flush()  # Get the ID
                
                result = sqlalchemy_to_pydantic(app_db, JobApplication)
                logger.info(f"Created application: {result.id} for job {result.job_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error creating application: {e}")
            raise
    
    def get_application(self, application_id: str) -> Optional[JobApplication]:
        """Get application by ID."""
        try:
            with self.db_manager.get_session() as session:
                app_db = session.query(JobApplicationDB).filter(
                    JobApplicationDB.id == application_id
                ).first()
                if app_db:
                    return sqlalchemy_to_pydantic(app_db, JobApplication)
                return None
        except Exception as e:
            logger.error(f"Error getting application {application_id}: {e}")
            return None
    
    def get_application_by_job_and_user(self, job_id: str, user_profile_id: str) -> Optional[JobApplication]:
        """Get application by job and user combination."""
        try:
            with self.db_manager.get_session() as session:
                app_db = session.query(JobApplicationDB).filter(
                    and_(
                        JobApplicationDB.job_id == job_id,
                        JobApplicationDB.user_profile_id == user_profile_id
                    )
                ).first()
                if app_db:
                    return sqlalchemy_to_pydantic(app_db, JobApplication)
                return None
        except Exception as e:
            logger.error(f"Error getting application for job {job_id} and user {user_profile_id}: {e}")
            return None
    
    def get_applications(
        self,
        user_profile_id: str,
        status: Optional[ApplicationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[JobApplication], int]:
        """Get user's applications with filtering."""
        try:
            with self.db_manager.get_session() as session:
                query_obj = session.query(JobApplicationDB).filter(
                    JobApplicationDB.user_profile_id == user_profile_id
                )
                
                # Filter by status
                if status:
                    query_obj = query_obj.filter(JobApplicationDB.status == status)
                
                # Get total count
                total = query_obj.count()
                
                # Apply pagination and ordering
                apps_db = query_obj.order_by(
                    desc(JobApplicationDB.created_at)
                ).offset(offset).limit(limit).all()
                
                applications = [
                    sqlalchemy_to_pydantic(app_db, JobApplication) 
                    for app_db in apps_db
                ]
                
                logger.info(f"Retrieved {len(applications)} applications for user {user_profile_id}")
                return applications, total
                
        except Exception as e:
            logger.error(f"Error getting applications for user {user_profile_id}: {e}")
            return [], 0
    
    def update_application(self, application_id: str, update_data: Dict[str, Any]) -> Optional[JobApplication]:
        """Update application."""
        try:
            with self.db_manager.get_session() as session:
                app_db = session.query(JobApplicationDB).filter(
                    JobApplicationDB.id == application_id
                ).first()
                if not app_db:
                    return None
                
                # Update fields
                for field, value in update_data.items():
                    if hasattr(app_db, field):
                        setattr(app_db, field, value)
                
                app_db.updated_at = datetime.utcnow()
                session.flush()
                
                result = sqlalchemy_to_pydantic(app_db, JobApplication)
                logger.info(f"Updated application: {application_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error updating application {application_id}: {e}")
            raise
    
    def delete_application(self, application_id: str) -> bool:
        """Delete application."""
        try:
            with self.db_manager.get_session() as session:
                app_db = session.query(JobApplicationDB).filter(
                    JobApplicationDB.id == application_id
                ).first()
                if app_db:
                    session.delete(app_db)
                    logger.info(f"Deleted application: {application_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting application {application_id}: {e}")
            return False
    
    def get_applications_by_job(self, job_id: str) -> List[JobApplication]:
        """Get all applications for a specific job."""
        try:
            with self.db_manager.get_session() as session:
                apps_db = session.query(JobApplicationDB).filter(
                    JobApplicationDB.job_id == job_id
                ).order_by(desc(JobApplicationDB.created_at)).all()
                
                return [
                    sqlalchemy_to_pydantic(app_db, JobApplication) 
                    for app_db in apps_db
                ]
                
        except Exception as e:
            logger.error(f"Error getting applications for job {job_id}: {e}")
            return []


# Global instances (initialized when needed)
db_manager = None
job_repo = None
user_repo = None
saved_job_repo = None
application_repo = None


def initialize_database(database_url: str = None):
    """Initialize global database instances."""
    global db_manager, job_repo, user_repo, saved_job_repo, application_repo
    
    db_manager = DatabaseManager(database_url)
    job_repo = JobRepository(db_manager)
    user_repo = UserRepository(db_manager)
    saved_job_repo = SavedJobRepository(db_manager)
    application_repo = ApplicationRepository(db_manager)
    
    logger.info("Database repositories initialized")


def get_database_manager() -> DatabaseManager:
    """Get or create database manager."""
    global db_manager
    if db_manager is None:
        initialize_database()
    return db_manager


def get_job_repository() -> JobRepository:
    """Get or create job repository."""
    global job_repo
    if job_repo is None:
        initialize_database()
    return job_repo


def get_user_repository() -> UserRepository:
    """Get or create user repository."""
    global user_repo
    if user_repo is None:
        initialize_database()
    return user_repo


def get_saved_job_repository() -> SavedJobRepository:
    """Get or create saved job repository."""
    global saved_job_repo
    if saved_job_repo is None:
        initialize_database()
    return saved_job_repo


def get_application_repository() -> ApplicationRepository:
    """Get or create application repository."""
    global application_repo
    if application_repo is None:
        initialize_database()
    return application_repo
