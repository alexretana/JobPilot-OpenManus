"""
JobPilot Database Management
Database operations and repository pattern for job hunting data.
"""

import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, create_engine, desc, or_, text
from sqlalchemy.orm import sessionmaker

from app.data.company_matcher import (
    extract_domain_from_url,
    find_existing_company,
    validate_company_data,
)
from app.data.models import (
    Base,
    CompanyInfoDB,
    CompanySizeCategory,
    ExperienceLevel,
    JobListing,
    JobListingDB,
    JobStatus,
    JobType,
    RemoteType,
    UserProfile,
    UserProfileDB,
    pydantic_to_sqlalchemy,
    sqlalchemy_to_pydantic,
)
from app.data.resume_models import Resume, ResumeDB
from app.logger import logger
from app.utils.retry import retry_db_critical, retry_db_write


class DatabaseManager:
    """Manages database connections and provides basic operations."""

    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        if database_url is None:
            # Default to SQLite in the data directory
            data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
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

    def create_all_tables(self):
        """Create all database tables (alias for create_tables)."""
        return self.create_tables()

    def drop_all_tables(self):
        """Drop all database tables (DANGEROUS - for development only)."""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("All database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            raise

    @retry_db_critical(max_retries=5, base_delay=2.0)
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
                stats["job_listings"] = session.query(JobListingDB).count()
                stats["user_profiles"] = session.query(UserProfileDB).count()
                stats["companies"] = session.query(CompanyInfoDB).count()
                # Note: Legacy applications and saved_jobs tables removed
        except Exception as e:
            logger.error(f"Error getting table stats: {e}")
            stats = {"error": str(e)}

        return stats


class JobRepository:
    """Repository for job listing operations."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize job repository."""
        self.db_manager = db_manager

    @retry_db_write()
    def create_job(self, job_data: JobListing) -> JobListing:
        """Create a new job listing."""
        try:
            with self.db_manager.get_session() as session:
                job_db = pydantic_to_sqlalchemy(job_data, JobListingDB)
                session.add(job_db)
                session.flush()  # Get the ID

                # Convert back to Pydantic model
                result = sqlalchemy_to_pydantic(job_db, JobListing)
                logger.info(
                    f"Created job: {result.title} with company_id: {result.company_id}"
                )
                return result

        except Exception as e:
            logger.error(f"Error creating job: {e}")
            raise

    def get_job(self, job_id: str) -> Optional[JobListing]:
        """Get job by ID."""
        try:
            with self.db_manager.get_session() as session:
                job_db = (
                    session.query(JobListingDB)
                    .filter(JobListingDB.id == job_id)
                    .first()
                )
                if job_db:
                    return sqlalchemy_to_pydantic(job_db, JobListing)
                return None
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {e}")
            return None

    @retry_db_write()
    def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Optional[JobListing]:
        """Update job listing."""
        try:
            with self.db_manager.get_session() as session:
                job_db = (
                    session.query(JobListingDB)
                    .filter(JobListingDB.id == job_id)
                    .first()
                )
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
                job_db = (
                    session.query(JobListingDB)
                    .filter(JobListingDB.id == job_id)
                    .first()
                )
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
        offset: int = 0,
    ) -> Tuple[List[JobListing], int]:
        """Search jobs with filters using company relationship."""
        try:
            with self.db_manager.get_session() as session:
                # Join with CompanyInfoDB to get company information
                query_obj = (
                    session.query(JobListingDB)
                    .join(CompanyInfoDB)
                    .filter(JobListingDB.status == JobStatus.ACTIVE)
                )

                # Text search across title, company name, and description
                if query:
                    search_filter = or_(
                        JobListingDB.title.ilike(f"%{query}%"),
                        CompanyInfoDB.name.ilike(
                            f"%{query}%"
                        ),  # Search company name from relationship
                        JobListingDB.description.ilike(f"%{query}%"),
                        JobListingDB.requirements.ilike(f"%{query}%"),
                    )
                    query_obj = query_obj.filter(search_filter)

                # Filter by job types
                if job_types:
                    query_obj = query_obj.filter(JobListingDB.job_type.in_(job_types))

                # Filter by remote types
                if remote_types:
                    query_obj = query_obj.filter(
                        JobListingDB.remote_type.in_(remote_types)
                    )

                # Filter by experience levels
                if experience_levels:
                    query_obj = query_obj.filter(
                        JobListingDB.experience_level.in_(experience_levels)
                    )

                # Filter by locations
                if locations:
                    location_filters = [
                        JobListingDB.location.ilike(f"%{loc}%") for loc in locations
                    ]
                    query_obj = query_obj.filter(or_(*location_filters))

                # Filter by companies using company name from relationship
                if companies:
                    query_obj = query_obj.filter(CompanyInfoDB.name.in_(companies))

                # Salary filters
                if min_salary is not None:
                    query_obj = query_obj.filter(
                        or_(
                            JobListingDB.salary_min >= min_salary,
                            JobListingDB.salary_max >= min_salary,
                        )
                    )

                if max_salary is not None:
                    query_obj = query_obj.filter(
                        or_(
                            JobListingDB.salary_max <= max_salary,
                            JobListingDB.salary_min <= max_salary,
                        )
                    )

                # Age filter
                if max_age_days is not None:
                    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
                    query_obj = query_obj.filter(JobListingDB.created_at >= cutoff_date)

                # Get total count
                total_count = query_obj.count()

                # Apply pagination and ordering
                jobs_db = (
                    query_obj.order_by(desc(JobListingDB.created_at))
                    .offset(offset)
                    .limit(limit)
                    .all()
                )

                # Convert to Pydantic models with company name populated
                jobs = []
                for job_db in jobs_db:
                    job_dict = sqlalchemy_to_pydantic(job_db, JobListing).dict()
                    # Populate company name from relationship
                    job_dict["company_name"] = job_db.company.name
                    jobs.append(JobListing(**job_dict))

                logger.info(
                    f"Search returned {len(jobs)} jobs out of {total_count} total"
                )
                return jobs, total_count

        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return [], 0

    def get_recent_jobs(self, limit: int = 20) -> List[JobListing]:
        """Get most recent job listings."""
        try:
            with self.db_manager.get_session() as session:
                jobs_db = (
                    session.query(JobListingDB)
                    .filter(JobListingDB.status == JobStatus.ACTIVE)
                    .order_by(desc(JobListingDB.created_at))
                    .limit(limit)
                    .all()
                )

                jobs = [
                    sqlalchemy_to_pydantic(job_db, JobListing) for job_db in jobs_db
                ]
                logger.info(f"Retrieved {len(jobs)} recent jobs")
                return jobs

        except Exception as e:
            logger.error(f"Error getting recent jobs: {e}")
            return []

    def get_jobs_by_company(self, company: str, limit: int = 20) -> List[JobListing]:
        """Get jobs by company name using company relationship."""
        try:
            with self.db_manager.get_session() as session:
                jobs_db = (
                    session.query(JobListingDB)
                    .join(CompanyInfoDB)
                    .filter(
                        and_(
                            CompanyInfoDB.name.ilike(f"%{company}%"),
                            JobListingDB.status == JobStatus.ACTIVE,
                        )
                    )
                    .order_by(desc(JobListingDB.created_at))
                    .limit(limit)
                    .all()
                )

                # Convert to Pydantic models with company name populated
                jobs = []
                for job_db in jobs_db:
                    job_dict = sqlalchemy_to_pydantic(job_db, JobListing).dict()
                    # Populate company name from relationship
                    job_dict["company_name"] = job_db.company.name
                    jobs.append(JobListing(**job_dict))

                logger.info(f"Retrieved {len(jobs)} jobs for company: {company}")
                return jobs

        except Exception as e:
            logger.error(f"Error getting jobs for company {company}: {e}")
            return []

    @retry_db_write(max_retries=2, base_delay=1.5)
    def bulk_create_jobs(self, jobs_data: List[JobListing]) -> int:
        """Create multiple job listings efficiently."""
        try:
            with self.db_manager.get_session() as session:
                jobs_db = [
                    pydantic_to_sqlalchemy(job_data, JobListingDB)
                    for job_data in jobs_data
                ]
                session.add_all(jobs_db)
                session.flush()

                count = len(jobs_db)
                logger.info(f"Bulk created {count} jobs")
                return count

        except Exception as e:
            logger.error(f"Error bulk creating jobs: {e}")
            raise

    def get_or_create_company(
        self, name: str, domain: str = None, **kwargs
    ) -> CompanyInfoDB:
        """Get existing company or create new one with matching."""
        try:
            with self.db_manager.get_session() as session:
                # Extract domain from website if provided in kwargs
                website = kwargs.get("website")
                if website and not domain:
                    domain = extract_domain_from_url(website)

                # Validate company data
                normalized_name, validated_domain, errors = validate_company_data(
                    name=name, domain=domain, website=website
                )

                if errors:
                    raise ValueError(f"Invalid company data: {', '.join(errors)}")

                # Try to find existing company
                existing_id = find_existing_company(session, name, validated_domain)
                if existing_id:
                    existing = (
                        session.query(CompanyInfoDB)
                        .filter(CompanyInfoDB.id == existing_id)
                        .first()
                    )
                    if existing:
                        logger.info(f"Found existing company: {existing.name}")
                        # Create detached copy with all attributes loaded
                        session.expunge(existing)
                        return existing

                # Create new company
                company_data = {
                    "name": name.strip(),
                    "normalized_name": normalized_name,
                    "domain": validated_domain,
                    **kwargs,
                }

                # Handle size_category conversion if size is provided
                if "size" in kwargs and "size_category" not in kwargs:
                    from app.data.company_matcher import (
                        get_company_size_category_from_string,
                    )

                    size_category = get_company_size_category_from_string(
                        kwargs["size"]
                    )
                    if size_category:
                        company_data["size_category"] = CompanySizeCategory(
                            size_category
                        )

                company = CompanyInfoDB(**company_data)
                session.add(company)
                session.flush()
                session.refresh(company)

                logger.info(f"Created new company: {company.name} (ID: {company.id})")
                # Create detached copy with all attributes loaded
                session.expunge(company)
                return company

        except Exception as e:
            logger.error(f"Error getting/creating company {name}: {e}")
            raise

    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """Update job status."""
        try:
            with self.db_manager.get_session() as session:
                job_db = (
                    session.query(JobListingDB)
                    .filter(JobListingDB.id == job_id)
                    .first()
                )
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
                user_db = (
                    session.query(UserProfileDB)
                    .filter(UserProfileDB.id == user_id)
                    .first()
                )
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
                user_db = (
                    session.query(UserProfileDB)
                    .filter(UserProfileDB.email == email)
                    .first()
                )
                if user_db:
                    return sqlalchemy_to_pydantic(user_db, UserProfile)
                return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    def update_user(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> Optional[UserProfile]:
        """Update user profile."""
        try:
            with self.db_manager.get_session() as session:
                user_db = (
                    session.query(UserProfileDB)
                    .filter(UserProfileDB.id == user_id)
                    .first()
                )
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
                user_db = (
                    session.query(UserProfileDB)
                    .filter(UserProfileDB.id == user_id)
                    .first()
                )
                if user_db:
                    session.delete(user_db)
                    logger.info(f"Deleted user profile: {user_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    def list_users(
        self, limit: int = 50, offset: int = 0
    ) -> Tuple[List[UserProfile], int]:
        """List all user profiles with pagination."""
        try:
            with self.db_manager.get_session() as session:
                query_obj = session.query(UserProfileDB)

                # Get total count
                total_count = query_obj.count()

                # Apply pagination and ordering
                users_db = (
                    query_obj.order_by(desc(UserProfileDB.created_at))
                    .offset(offset)
                    .limit(limit)
                    .all()
                )

                # Convert to Pydantic models
                users = [
                    sqlalchemy_to_pydantic(user_db, UserProfile) for user_db in users_db
                ]

                logger.info(f"Listed {len(users)} users out of {total_count} total")
                return users, total_count

        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return [], 0


class ResumeRepository:
    """Repository for resume operations."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize resume repository."""
        self.db_manager = db_manager

    @retry_db_write()
    def create_resume(self, resume_data: Resume) -> Resume:
        """Create a new resume."""
        try:
            with self.db_manager.get_session() as session:
                resume_db = pydantic_to_sqlalchemy(resume_data, ResumeDB)
                session.add(resume_db)
                session.flush()  # Get the ID

                result = sqlalchemy_to_pydantic(resume_db, Resume)
                logger.info(f"Created resume: {result.title} for user {result.user_id}")
                return result

        except Exception as e:
            logger.error(f"Error creating resume: {e}")
            raise

    def get_resume(self, resume_id: str) -> Optional[Resume]:
        """Get resume by ID."""
        try:
            with self.db_manager.get_session() as session:
                resume_db = (
                    session.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                )
                if resume_db:
                    return sqlalchemy_to_pydantic(resume_db, Resume)
                return None
        except Exception as e:
            logger.error(f"Error getting resume {resume_id}: {e}")
            return None

    def get_user_resumes(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Resume], int]:
        """Get resumes for a user with filtering and pagination."""
        try:
            with self.db_manager.get_session() as session:
                query_obj = session.query(ResumeDB).filter(ResumeDB.user_id == user_id)

                # Filter by status if provided
                if status:
                    query_obj = query_obj.filter(ResumeDB.status == status)

                # Get total count
                total_count = query_obj.count()

                # Apply pagination and ordering
                resumes_db = (
                    query_obj.order_by(desc(ResumeDB.updated_at))
                    .offset(offset)
                    .limit(limit)
                    .all()
                )

                # Convert to Pydantic models
                resumes = [
                    sqlalchemy_to_pydantic(resume_db, Resume)
                    for resume_db in resumes_db
                ]

                logger.info(
                    f"Retrieved {len(resumes)} resumes out of {total_count} total for user {user_id}"
                )
                return resumes, total_count

        except Exception as e:
            logger.error(f"Error getting resumes for user {user_id}: {e}")
            return [], 0

    @retry_db_write()
    def update_resume(
        self, resume_id: str, update_data: Dict[str, Any]
    ) -> Optional[Resume]:
        """Update resume."""
        try:
            with self.db_manager.get_session() as session:
                resume_db = (
                    session.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                )
                if not resume_db:
                    return None

                # Update fields
                for field, value in update_data.items():
                    if hasattr(resume_db, field):
                        setattr(resume_db, field, value)

                resume_db.updated_at = datetime.utcnow()
                session.flush()

                result = sqlalchemy_to_pydantic(resume_db, Resume)
                logger.info(f"Updated resume: {resume_id}")
                return result

        except Exception as e:
            logger.error(f"Error updating resume {resume_id}: {e}")
            raise

    def delete_resume(self, resume_id: str) -> bool:
        """Delete resume."""
        try:
            with self.db_manager.get_session() as session:
                resume_db = (
                    session.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                )
                if resume_db:
                    session.delete(resume_db)
                    logger.info(f"Deleted resume: {resume_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting resume {resume_id}: {e}")
            return False

    def get_resumes_by_type(
        self, user_id: str, resume_type: str, limit: int = 20
    ) -> List[Resume]:
        """Get resumes by type for a user."""
        try:
            with self.db_manager.get_session() as session:
                resumes_db = (
                    session.query(ResumeDB)
                    .filter(
                        and_(
                            ResumeDB.user_id == user_id,
                            ResumeDB.resume_type == resume_type,
                        )
                    )
                    .order_by(desc(ResumeDB.updated_at))
                    .limit(limit)
                    .all()
                )

                resumes = [
                    sqlalchemy_to_pydantic(resume_db, Resume)
                    for resume_db in resumes_db
                ]
                logger.info(
                    f"Retrieved {len(resumes)} {resume_type} resumes for user {user_id}"
                )
                return resumes

        except Exception as e:
            logger.error(f"Error getting {resume_type} resumes for user {user_id}: {e}")
            return []

    async def get_total_resumes_count(self) -> int:
        """Get total count of all resumes in the database."""
        try:
            with self.db_manager.get_session() as session:
                count = session.query(ResumeDB).count()
                logger.info(f"Total resumes count: {count}")
                return count
        except Exception as e:
            logger.error(f"Error getting total resumes count: {e}")
            return 0


# Global instances (initialized when needed)
db_manager = None
job_repo = None
user_repo = None
resume_repo = None
interaction_repo = None
company_repo = None


def initialize_database(database_url: str = None):
    """Initialize global database instances."""
    global db_manager, job_repo, user_repo, resume_repo, interaction_repo, company_repo

    # Import here to avoid circular imports
    from app.data.company_repository import CompanyRepository
    from app.data.interaction_repository import JobUserInteractionRepository

    db_manager = DatabaseManager(database_url)
    job_repo = JobRepository(db_manager)
    user_repo = UserRepository(db_manager)
    resume_repo = ResumeRepository(db_manager)
    interaction_repo = JobUserInteractionRepository(db_manager)
    company_repo = CompanyRepository(db_manager)

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


def get_resume_repository() -> ResumeRepository:
    """Get or create resume repository."""
    global resume_repo
    if resume_repo is None:
        initialize_database()
    return resume_repo


def get_interaction_repository():
    """Get or create interaction repository."""
    global interaction_repo
    if interaction_repo is None:
        initialize_database()
    return interaction_repo


def get_company_repository():
    """Get or create company repository."""
    global company_repo
    if company_repo is None:
        initialize_database()
    return company_repo


def get_application_repository():
    """Get or create application repository (legacy compatibility - uses interaction repository)."""
    # Legacy compatibility: applications are now handled by the interaction repository
    return get_interaction_repository()
