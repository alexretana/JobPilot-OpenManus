"""
JobPilot Data Models
Core data structures for job hunting functionality, migrated from original JobPilot.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# =====================================
# Enums for Job-Related Classifications
# =====================================


class JobType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    FREELANCE = "Freelance"
    INTERNSHIP = "Internship"
    TEMPORARY = "Temporary"


class RemoteType(str, Enum):
    ON_SITE = "On-site"
    REMOTE = "Remote"
    HYBRID = "Hybrid"


class ExperienceLevel(str, Enum):
    ENTRY_LEVEL = "entry_level"
    ASSOCIATE = "associate"
    MID_LEVEL = "mid_level"
    SENIOR_LEVEL = "senior_level"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


class JobStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FILLED = "filled"
    EXPIRED = "expired"


class ApplicationStatus(str, Enum):
    NOT_APPLIED = "not_applied"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class SavedJobStatus(str, Enum):
    SAVED = "saved"
    ARCHIVED = "archived"


class TimelineEventType(str, Enum):
    """Types of timeline events for job applications."""

    JOB_POSTED = "job_posted"
    JOB_SAVED = "job_saved"
    APPLICATION_SUBMITTED = "application_submitted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    FOLLOW_UP_SENT = "follow_up_sent"
    RESPONSE_RECEIVED = "response_received"
    STATUS_CHANGED = "status_changed"
    NOTE_ADDED = "note_added"
    CUSTOM_EVENT = "custom_event"


class ETLProcessingStatus(str, Enum):
    """ETL processing status for raw data collections."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class ETLOperationType(str, Enum):
    """Types of ETL operations."""

    COLLECTION = "collection"
    PROCESSING = "processing"
    LOADING = "loading"
    RETRY = "retry"
    CLEANUP = "cleanup"


class VerificationStatus(str, Enum):
    """Job verification status."""

    UNVERIFIED = "unverified"
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"
    REMOVED = "removed"


class CompanySizeCategory(str, Enum):
    """Company size categories."""

    STARTUP = "startup"  # 1-50 employees
    SMALL = "small"  # 51-200 employees
    MEDIUM = "medium"  # 201-1000 employees
    LARGE = "large"  # 1001-5000 employees
    ENTERPRISE = "enterprise"  # 5000+ employees


class SeniorityLevel(str, Enum):
    """Job seniority levels."""

    INDIVIDUAL_CONTRIBUTOR = "individual_contributor"
    TEAM_LEAD = "team_lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"


# =====================================
# Pydantic Models for API/Data Transfer
# =====================================

# =====================================
# NEW: Phase 2 Models for Real Job Board Integration
# =====================================


class JobSource(BaseModel):
    """Track job board sources and their metadata."""

    id: UUID = Field(default_factory=uuid4)
    name: str  # "linkedin", "indeed", "glassdoor"
    display_name: str  # "LinkedIn Jobs", "Indeed", "Glassdoor"
    base_url: str
    api_available: bool = False
    scraping_rules: Optional[Dict[str, Any]] = None
    rate_limit_config: Optional[Dict[str, Any]] = None
    last_scraped: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class JobSourceListing(BaseModel):
    """Link jobs to their sources with source-specific metadata."""

    id: UUID = Field(default_factory=uuid4)
    job_id: UUID
    source_id: UUID
    source_job_id: str  # Original ID from source platform
    source_url: str
    source_metadata: Optional[Dict[str, Any]] = None  # Platform-specific fields
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class JobEmbedding(BaseModel):
    """Store vector embeddings for semantic search."""

    id: UUID = Field(default_factory=uuid4)
    job_id: UUID
    embedding_model: str  # e.g., "sentence-transformers/all-MiniLM-L6-v2"
    content_hash: str  # Hash of the content that was embedded
    embedding_vector: List[float]  # The actual embedding
    embedding_dimension: int
    content_type: str = "job_description"  # job_description, requirements, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class JobDeduplication(BaseModel):
    """Track duplicate jobs across platforms."""

    id: UUID = Field(default_factory=uuid4)
    canonical_job_id: UUID  # The "main" job record
    duplicate_job_id: UUID  # The duplicate job record
    confidence_score: float  # 0.0 to 1.0 confidence it's a duplicate
    matching_fields: List[str]  # Which fields matched (title, company, etc.)
    merge_strategy: str = "keep_canonical"  # merge_both, keep_canonical, manual_review
    reviewed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class JobListingBase(BaseModel):
    """Base job listing data structure."""

    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None

    # Job details
    job_type: Optional[JobType] = None
    remote_type: Optional[RemoteType] = None
    experience_level: Optional[ExperienceLevel] = None

    # Salary information
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"

    # Skills and qualifications
    skills_required: Optional[List[str]] = []
    skills_preferred: Optional[List[str]] = []
    education_required: Optional[str] = None

    # Additional information
    benefits: Optional[List[str]] = []
    company_size: Optional[str] = None
    industry: Optional[str] = None

    # URLs and external references
    job_url: Optional[str] = None
    company_url: Optional[str] = None
    application_url: Optional[str] = None

    # Metadata
    posted_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    source: Optional[str] = None  # Where the job was scraped from

    # NEW: Multi-source tracking
    canonical_id: Optional[UUID] = None  # If this is a duplicate, points to canonical
    source_count: int = 1  # How many sources have this job
    data_quality_score: Optional[float] = None  # 0.0-1.0 quality assessment

    # NEW: Enhanced metadata
    scraped_at: Optional[datetime] = None
    last_verified: Optional[datetime] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # NEW: Enriched data
    company_size_category: Optional[CompanySizeCategory] = None
    seniority_level: Optional[SeniorityLevel] = None
    tech_stack: Optional[List[str]] = []
    benefits_parsed: Optional[Dict[str, Any]] = None  # structured benefits data

    @validator(
        "skills_required", "skills_preferred", "benefits", "tech_stack", pre=True
    )
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


class JobListing(JobListingBase):
    """Complete job listing with metadata."""

    id: UUID = Field(default_factory=uuid4)
    status: JobStatus = JobStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile for job matching."""

    id: UUID = Field(default_factory=uuid4)

    # Personal information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    # Professional information
    current_title: Optional[str] = None
    experience_years: Optional[int] = None
    skills: List[str] = Field(default_factory=list)
    education: Optional[str] = None
    bio: Optional[str] = None

    # Job preferences
    preferred_locations: List[str] = Field(default_factory=list)
    preferred_job_types: List[JobType] = Field(default_factory=list)
    preferred_remote_types: List[RemoteType] = Field(default_factory=list)
    desired_salary_min: Optional[float] = None
    desired_salary_max: Optional[float] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class JobApplication(BaseModel):
    """Job application tracking."""

    id: UUID = Field(default_factory=uuid4)
    job_id: UUID
    user_profile_id: UUID

    # Application details
    status: ApplicationStatus = ApplicationStatus.NOT_APPLIED
    applied_date: Optional[datetime] = None
    response_date: Optional[datetime] = None

    # Application materials
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None

    # Follow-up tracking
    follow_up_date: Optional[datetime] = None
    interview_scheduled: Optional[datetime] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class CompanyInfo(BaseModel):
    """Company information."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    # Additional details
    culture: Optional[str] = None
    values: List[str] = []
    benefits: List[str] = []

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class SavedJob(BaseModel):
    """Saved job tracking."""

    id: UUID = Field(default_factory=uuid4)
    job_id: UUID
    user_profile_id: UUID

    # Saved job details
    status: SavedJobStatus = SavedJobStatus.SAVED
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)  # User-defined tags for organization

    # Metadata
    saved_date: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class JobMatch(BaseModel):
    """Job matching result with AI analysis."""

    job_id: UUID
    user_profile_id: UUID

    # Matching scores (0.0 to 1.0)
    overall_score: float
    skills_match_score: float
    experience_match_score: float
    location_match_score: float
    salary_match_score: float

    # AI-generated explanations
    match_reasons: List[str] = []
    skill_gaps: List[str] = []
    recommendations: Optional[str] = None

    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    """Timeline event for job application tracking."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: Optional[str] = None  # Can be None for general events
    application_id: Optional[str] = None  # Link to specific application
    user_profile_id: str

    # Event details
    event_type: TimelineEventType
    title: str
    description: Optional[str] = None

    # Event data (flexible JSON for event-specific data)
    event_data: Dict[str, Any] = Field(default_factory=dict)

    # Event scheduling/timing
    event_date: datetime = Field(default_factory=datetime.utcnow)
    is_milestone: bool = False  # Mark important events

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


# =====================================
# ETL Pipeline Models
# =====================================


class RawJobCollection(BaseModel):
    """Raw job collection from external APIs."""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    api_provider: str  # "jsearch", "indeed", etc.
    query_params: Dict[str, Any]  # Search parameters used
    raw_response: Dict[str, Any]  # Complete API response
    metadata: Optional[Dict[str, Any]] = None  # Response metadata
    processing_status: ETLProcessingStatus = ETLProcessingStatus.PENDING
    error_info: Optional[Dict[str, Any]] = None  # Error details if failed
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class JobProcessingLog(BaseModel):
    """Log of job processing operations."""

    id: UUID = Field(default_factory=uuid4)
    collection_id: UUID  # Reference to raw collection
    operation_type: ETLOperationType
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: ETLProcessingStatus
    jobs_processed: int = 0
    jobs_failed: int = 0
    errors: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ProcessedJobData(BaseModel):
    """Processed job data ready for loading."""

    processing_id: UUID  # Reference to processing log
    job_index: int  # Index in the processing batch
    processed_data: Dict[str, Any]  # Transformed job data
    embedding_vector: Optional[List[float]] = None  # Generated embeddings
    duplicate_of: Optional[UUID] = None  # If duplicate, reference to canonical
    load_status: ETLProcessingStatus = ETLProcessingStatus.PENDING
    quality_score: Optional[float] = None  # Data quality assessment
    validation_errors: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ETLOperationLog(BaseModel):
    """Comprehensive ETL operation logging."""

    id: UUID = Field(default_factory=uuid4)
    operation_type: ETLOperationType
    operation_name: str  # Specific operation (e.g., "jsearch_collection", "embedding_generation")
    status: ETLProcessingStatus
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    input_data: Optional[Dict[str, Any]] = None  # Operation parameters
    output_data: Optional[Dict[str, Any]] = None  # Operation results
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    operation_metadata: Optional[Dict[str, Any]] = None  # Renamed from metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


# =====================================
# SQLAlchemy Database Models
# =====================================

Base = declarative_base()


# =====================================
# NEW: Phase 2 SQLAlchemy Models
# =====================================


class JobSourceDB(Base):
    """SQLAlchemy model for job sources."""

    __tablename__ = "job_sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    api_available = Column(Boolean, default=False)
    scraping_rules = Column(JSON)
    rate_limit_config = Column(JSON)
    last_scraped = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source_listings = relationship("JobSourceListingDB", back_populates="source")


class JobSourceListingDB(Base):
    """SQLAlchemy model for job source listings."""

    __tablename__ = "job_source_listings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)
    source_id = Column(String, ForeignKey("job_sources.id"), nullable=False)
    source_job_id = Column(String, nullable=False)  # Original ID from source platform
    source_url = Column(String, nullable=False)
    source_metadata = Column(JSON)  # Platform-specific fields
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("JobListingDB", back_populates="source_listings")
    source = relationship("JobSourceDB", back_populates="source_listings")


class JobEmbeddingDB(Base):
    """SQLAlchemy model for job embeddings."""

    __tablename__ = "job_embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)
    embedding_model = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    embedding_vector = Column(JSON, nullable=False)  # Store as JSON array
    embedding_dimension = Column(Integer, nullable=False)
    content_type = Column(String, default="job_description")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("JobListingDB", back_populates="embeddings")


class JobDeduplicationDB(Base):
    """SQLAlchemy model for job deduplication."""

    __tablename__ = "job_duplications"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    canonical_job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)
    duplicate_job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)
    confidence_score = Column(Float, nullable=False)
    matching_fields = Column(JSON, nullable=False)  # Store as JSON array
    merge_strategy = Column(String, default="keep_canonical")
    reviewed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    canonical_job = relationship("JobListingDB", foreign_keys=[canonical_job_id])
    duplicate_job = relationship("JobListingDB", foreign_keys=[duplicate_job_id])


class JobListingDB(Base):
    """SQLAlchemy model for job listings."""

    __tablename__ = "job_listings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Basic information
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    responsibilities = Column(Text)

    # Job details
    job_type = Column(SQLEnum(JobType))
    remote_type = Column(SQLEnum(RemoteType))
    experience_level = Column(SQLEnum(ExperienceLevel))

    # Salary information
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String, default="USD")

    # Skills and qualifications (stored as JSON)
    skills_required = Column(JSON)
    skills_preferred = Column(JSON)
    education_required = Column(String)

    # Additional information
    benefits = Column(JSON)
    company_size = Column(String)
    industry = Column(String)

    # URLs and external references
    job_url = Column(String)
    company_url = Column(String)
    application_url = Column(String)

    # Dates
    posted_date = Column(DateTime)
    application_deadline = Column(DateTime)

    # Metadata
    source = Column(String)
    status = Column(SQLEnum(JobStatus), default=JobStatus.ACTIVE)

    # NEW: Multi-source tracking
    canonical_id = Column(String, ForeignKey("job_listings.id"), nullable=True)
    source_count = Column(Integer, default=1)
    data_quality_score = Column(Float)

    # NEW: Enhanced metadata
    scraped_at = Column(DateTime)
    last_verified = Column(DateTime)
    verification_status = Column(
        SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED
    )

    # NEW: Enriched data
    company_size_category = Column(SQLEnum(CompanySizeCategory))
    seniority_level = Column(SQLEnum(SeniorityLevel))
    tech_stack = Column(JSON)
    benefits_parsed = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = relationship("JobApplicationDB", back_populates="job")
    source_listings = relationship("JobSourceListingDB", back_populates="job")
    embeddings = relationship("JobEmbeddingDB", back_populates="job")
    canonical_job = relationship("JobListingDB", remote_side=[id])


class UserProfileDB(Base):
    """SQLAlchemy model for user profiles."""

    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Personal information
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)

    # Professional information
    current_title = Column(String)
    experience_years = Column(Integer)
    skills = Column(JSON)
    education = Column(String)
    bio = Column(Text)

    # Job preferences (stored as JSON)
    preferred_locations = Column(JSON)
    preferred_job_types = Column(JSON)
    preferred_remote_types = Column(JSON)
    desired_salary_min = Column(Float)
    desired_salary_max = Column(Float)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = relationship("JobApplicationDB", back_populates="user_profile")
    # TODO: Add resume and skill bank relationships after resolving circular import


class JobApplicationDB(Base):
    """SQLAlchemy model for job applications."""

    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)

    # Application details
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.NOT_APPLIED)
    applied_date = Column(DateTime)
    response_date = Column(DateTime)

    # Application materials
    resume_version = Column(String)
    cover_letter = Column(Text)
    notes = Column(Text)

    # Follow-up tracking
    follow_up_date = Column(DateTime)
    interview_scheduled = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("JobListingDB", back_populates="applications")
    user_profile = relationship("UserProfileDB", back_populates="applications")


class SavedJobDB(Base):
    """SQLAlchemy model for saved jobs."""

    __tablename__ = "saved_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)

    # Saved job details
    status = Column(SQLEnum(SavedJobStatus), default=SavedJobStatus.SAVED)
    notes = Column(Text)
    tags = Column(JSON)  # User-defined tags for organization

    # Metadata
    saved_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("JobListingDB")
    user_profile = relationship("UserProfileDB")


class CompanyInfoDB(Base):
    """SQLAlchemy model for company information."""

    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, unique=True)
    industry = Column(String)
    size = Column(String)
    location = Column(String)
    website = Column(String)
    description = Column(Text)

    # Additional details (stored as JSON)
    culture = Column(Text)
    values = Column(JSON)
    benefits = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TimelineEventDB(Base):
    """SQLAlchemy model for timeline events."""

    __tablename__ = "timeline_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    job_id = Column(
        String, ForeignKey("job_listings.id"), nullable=True
    )  # Can be None for general events
    application_id = Column(
        String, ForeignKey("applications.id"), nullable=True
    )  # Link to specific application
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)

    # Event details
    event_type = Column(SQLEnum(TimelineEventType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)

    # Event data (flexible JSON for event-specific data)
    event_data = Column(JSON)

    # Event scheduling/timing
    event_date = Column(DateTime, default=datetime.utcnow)
    is_milestone = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("JobListingDB")
    application = relationship("JobApplicationDB")
    user_profile = relationship("UserProfileDB")


# =====================================
# ETL Pipeline SQLAlchemy Models
# =====================================


class RawJobCollectionDB(Base):
    """SQLAlchemy model for raw job collections from external APIs."""

    __tablename__ = "raw_job_collections"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    api_provider = Column(String, nullable=False)  # "jsearch", "indeed", etc.
    query_params = Column(JSON, nullable=False)  # Search parameters used
    raw_response = Column(JSON, nullable=False)  # Complete API response
    response_metadata = Column(JSON)  # Response metadata (renamed from metadata)
    processing_status = Column(
        SQLEnum(ETLProcessingStatus), default=ETLProcessingStatus.PENDING
    )
    error_info = Column(JSON)  # Error details if failed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    processing_logs = relationship(
        "JobProcessingLogDB", back_populates="raw_collection"
    )


class JobProcessingLogDB(Base):
    """SQLAlchemy model for job processing operations."""

    __tablename__ = "job_processing_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    collection_id = Column(String, ForeignKey("raw_job_collections.id"), nullable=False)
    operation_type = Column(SQLEnum(ETLOperationType), nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(SQLEnum(ETLProcessingStatus), nullable=False)
    jobs_processed = Column(Integer, default=0)
    jobs_failed = Column(Integer, default=0)
    errors = Column(JSON)  # List of error dictionaries
    metrics = Column(JSON)  # Processing metrics
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    raw_collection = relationship(
        "RawJobCollectionDB", back_populates="processing_logs"
    )
    processed_data = relationship("ProcessedJobDataDB", back_populates="processing_log")


class ProcessedJobDataDB(Base):
    """SQLAlchemy model for processed job data ready for loading."""

    __tablename__ = "processed_job_data"

    processing_id = Column(
        String, ForeignKey("job_processing_logs.id"), primary_key=True
    )
    job_index = Column(Integer, primary_key=True)  # Index in the processing batch
    processed_data = Column(JSON, nullable=False)  # Transformed job data
    embedding_vector = Column(JSON)  # Generated embeddings as JSON array
    duplicate_of = Column(String)  # If duplicate, reference to canonical job UUID
    load_status = Column(
        SQLEnum(ETLProcessingStatus), default=ETLProcessingStatus.PENDING
    )
    quality_score = Column(Float)  # Data quality assessment
    validation_errors = Column(JSON)  # List of validation error strings
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    processing_log = relationship("JobProcessingLogDB", back_populates="processed_data")


class ETLOperationLogDB(Base):
    """SQLAlchemy model for comprehensive ETL operation logging."""

    __tablename__ = "etl_operation_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    operation_type = Column(SQLEnum(ETLOperationType), nullable=False)
    operation_name = Column(String, nullable=False)  # Specific operation name
    status = Column(SQLEnum(ETLProcessingStatus), nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)  # Operation duration in milliseconds
    input_data = Column(JSON)  # Operation parameters
    output_data = Column(JSON)  # Operation results
    error_message = Column(Text)  # Human-readable error message
    error_details = Column(JSON)  # Structured error details
    operation_metadata = Column(
        JSON
    )  # Additional operation metadata (renamed from metadata)
    created_at = Column(DateTime, default=datetime.utcnow)


# =====================================
# Utility Functions
# =====================================


def create_database_engine(database_url: str = "sqlite:///jobpilot.db"):
    """Create SQLAlchemy engine for database operations."""
    return create_engine(database_url, echo=False)


def create_tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(engine)


def get_session_factory(engine):
    """Get SQLAlchemy session factory."""
    return sessionmaker(bind=engine)


# =====================================
# Data Conversion Functions
# =====================================


def pydantic_to_sqlalchemy(pydantic_obj: BaseModel, sqlalchemy_class):
    """Convert Pydantic model to SQLAlchemy model."""
    data = pydantic_obj.dict(exclude_unset=True)
    # Convert all UUID fields to strings for SQLAlchemy (required for SQLite)
    for key, value in data.items():
        if isinstance(value, UUID):
            data[key] = str(value)

    # Handle field name mappings for renamed fields
    if sqlalchemy_class.__name__ == "RawJobCollectionDB":
        if "metadata" in data:
            data["response_metadata"] = data.pop("metadata")
    elif sqlalchemy_class.__name__ == "ETLOperationLogDB":
        if "metadata" in data:
            data["operation_metadata"] = data.pop("metadata")
        elif "operation_metadata" in data:
            # Handle both naming conventions
            pass

    return sqlalchemy_class(**data)


def sqlalchemy_to_pydantic(sqlalchemy_obj, pydantic_class):
    """Convert SQLAlchemy model to Pydantic model."""
    data = {}
    for column in sqlalchemy_obj.__table__.columns:
        value = getattr(sqlalchemy_obj, column.name)
        column_name = column.name

        # Handle field name mappings for renamed fields
        if (
            sqlalchemy_obj.__class__.__name__ == "RawJobCollectionDB"
            and column_name == "response_metadata"
        ):
            column_name = "metadata"
        elif (
            sqlalchemy_obj.__class__.__name__ == "ETLOperationLogDB"
            and column_name == "operation_metadata"
        ):
            column_name = "metadata"

        # Handle None values for list fields
        if value is None and column_name in [
            "skills",
            "preferred_locations",
            "preferred_job_types",
            "preferred_remote_types",
            "skills_required",
            "skills_preferred",
            "benefits",
            "values",
            "tags",
            "tech_stack",
            "matching_fields",
        ]:
            value = []
        # Handle None values for event_data dict field
        elif value is None and column_name == "event_data":
            value = {}
        # Handle None values for metadata dict fields
        elif value is None and column_name in [
            "scraping_rules",
            "rate_limit_config",
            "source_metadata",
            "benefits_parsed",
            "metadata",
            "operation_metadata",
            "response_metadata",
        ]:
            value = {}
        # Skip None values for required fields - let Pydantic handle defaults
        elif value is None and column_name in ["id", "created_at", "updated_at"]:
            continue

        data[column_name] = value
    return pydantic_class(**data)
