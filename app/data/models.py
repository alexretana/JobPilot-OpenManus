"""
JobPilot Data Models
Core data structures for job hunting functionality, migrated from original JobPilot.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, sessionmaker

from .base import Base

# Import enhanced skill bank models
try:
    from .skill_bank_models import EnhancedSkillBankDB
except ImportError:
    # Fallback for development - create a placeholder
    class EnhancedSkillBankDB:
        pass


# NOTE: The following models need cascade delete rules but are defined in separate files:
# - ResumeDB (should have):
#   - user_id = Column(String, ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False)
#   - parent_resume_id = Column(String, ForeignKey('resumes.id', ondelete='SET NULL'))
#   - target_job_id = Column(String, ForeignKey('job_listings.id', ondelete='SET NULL'))
#   - template_id = Column(String, ForeignKey('resume_templates.id', ondelete='SET NULL'))
# - EnhancedSkillBankDB (should have):
#   - user_id = Column(String, ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False)


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


class InteractionType(str, Enum):
    """Types of user interactions with jobs."""

    VIEWED = "viewed"
    SAVED = "saved"
    APPLIED = "applied"
    HIDDEN = "hidden"
    REJECTED_BY_USER = "rejected_by_user"


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
    # company field removed - now handled via company relationship
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
    # REMOVE: company_size - now in company relationship
    # REMOVE: industry - now in company relationship

    # URLs and external references
    job_url: Optional[str] = None
    # REMOVE: company_url - now in company relationship as 'website'
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

    # Company relationship fields
    company_id: Optional[UUID] = None
    company_name: Optional[str] = (
        None  # For display purposes, populated from relationship
    )

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

    # Location information
    city: Optional[str] = None
    state: Optional[str] = None

    # Professional links
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Professional information
    current_title: Optional[str] = None
    experience_years: Optional[int] = None
    # skills: List[str] = Field(default_factory=list)  # DELETE - use skill_bank relationship only
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
# SQLAlchemy Database Models
# =====================================


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
    source_listings = relationship(
        "JobSourceListingDB", back_populates="source", cascade="all, delete-orphan"
    )


class JobSourceListingDB(Base):
    """SQLAlchemy model for job source listings."""

    __tablename__ = "job_source_listings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    # UPDATE: Add cascade rules
    job_id = Column(
        String, ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False
    )
    source_id = Column(
        String, ForeignKey("job_sources.id", ondelete="CASCADE"), nullable=False
    )
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
    # UPDATE: Add cascade rules
    job_id = Column(
        String, ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False
    )
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

    # ADD: Foreign key to companies table
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)

    # Basic information
    title = Column(String, nullable=False)
    # REMOVE: company = Column(String, nullable=False)  # DELETE - now in company table
    location = Column(String)  # Job location (can differ from company HQ)
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
    # REMOVE: company_size = Column(String)  # DELETE - now in company table
    # REMOVE: industry = Column(String)  # DELETE - now in company table

    # URLs and external references
    job_url = Column(String)
    # REMOVE: company_url = Column(String)  # DELETE - now in company table as 'website'
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
    company = relationship("CompanyInfoDB", back_populates="job_listings")
    # applications = relationship("JobApplicationDB", back_populates="job")  # DELETE - replaced by user_interactions
    user_interactions = relationship(
        "JobUserInteractionDB", back_populates="job", cascade="all, delete-orphan"
    )  # NEW: consolidated interactions
    source_listings = relationship(
        "JobSourceListingDB", back_populates="job", cascade="all, delete-orphan"
    )
    embeddings = relationship(
        "JobEmbeddingDB", back_populates="job", cascade="all, delete-orphan"
    )
    canonical_job = relationship("JobListingDB", remote_side=[id])
    # ADD: Back reference to tailored resumes
    tailored_resumes = relationship("ResumeDB", back_populates="target_job")

    # ADD: Performance indexes and data validation constraints
    __table_args__ = (
        Index("idx_job_company_status", "company_id", "status"),
        Index("idx_job_location_type", "location", "job_type"),
        Index("idx_job_posted_date", "posted_date"),
        Index("idx_job_salary_range", "salary_min", "salary_max"),
        Index("idx_job_experience_level", "experience_level"),
        Index("idx_job_remote_type", "remote_type"),
        Index("idx_job_created_status", "created_at", "status"),
        # ADD: Data validation constraints
        CheckConstraint("salary_min >= 0", name="salary_min_positive"),
        CheckConstraint("salary_max >= salary_min", name="salary_range_valid"),
        CheckConstraint(
            "job_url LIKE 'http%://%' OR job_url IS NULL", name="job_url_format"
        ),
        CheckConstraint(
            "application_url LIKE 'http%://%' OR application_url IS NULL",
            name="app_url_format",
        ),
        CheckConstraint("LENGTH(title) >= 3", name="title_min_length"),
        CheckConstraint("LENGTH(title) <= 200", name="title_max_length"),
    )


class UserProfileDB(Base):
    """SQLAlchemy model for user profiles."""

    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Personal information
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)

    # Location information
    city = Column(String)
    state = Column(String)

    # Professional links
    linkedin_url = Column(String)
    portfolio_url = Column(String)

    # Professional information
    current_title = Column(String)
    experience_years = Column(Integer)
    # skills = Column(JSON)  # DELETE - use skill_bank relationship only
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
    # applications = relationship("JobApplicationDB", back_populates="user_profile")  # DELETE - replaced by job_interactions
    job_interactions = relationship(
        "JobUserInteractionDB", back_populates="user", cascade="all, delete-orphan"
    )  # NEW: consolidated interactions
    resumes = relationship(
        "ResumeDB", back_populates="user", cascade="all, delete-orphan"
    )
    skill_bank = relationship(
        "EnhancedSkillBankDB", back_populates="user", uselist=False
    )

    # ADD: Performance indexes and data validation constraints
    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_location", "city", "state"),
        Index("idx_user_created", "created_at"),
        # ADD: Data validation constraints
        CheckConstraint("email LIKE '%@%.%' OR email IS NULL", name="email_format"),
        CheckConstraint(
            "linkedin_url LIKE 'http%://linkedin.com%' OR linkedin_url LIKE 'http%://%.linkedin.com%' OR linkedin_url IS NULL",
            name="linkedin_url_format",
        ),
        CheckConstraint(
            "experience_years >= 0 OR experience_years IS NULL",
            name="experience_positive",
        ),
        CheckConstraint(
            "desired_salary_min >= 0 OR desired_salary_min IS NULL",
            name="desired_salary_min_positive",
        ),
        CheckConstraint(
            "desired_salary_max >= desired_salary_min OR desired_salary_max IS NULL OR desired_salary_min IS NULL",
            name="desired_salary_range_valid",
        ),
    )


class JobUserInteractionDB(Base):
    """Consolidated user-job interactions (replaces JobApplicationDB + SavedJobDB)."""

    __tablename__ = "job_user_interactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    # UPDATE: Add cascade rules
    user_id = Column(
        String,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        String,
        ForeignKey("job_listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Interaction classification
    interaction_type = Column(SQLEnum(InteractionType), nullable=False, index=True)

    # Application-specific fields (used when interaction_type = APPLIED)
    application_status = Column(SQLEnum(ApplicationStatus))
    applied_date = Column(DateTime)
    response_date = Column(DateTime)
    resume_version = Column(String)  # Which resume was used
    cover_letter = Column(Text)
    follow_up_date = Column(DateTime)
    interview_scheduled = Column(DateTime)

    # Saved job specific fields (used when interaction_type = SAVED)
    saved_date = Column(DateTime)
    tags = Column(JSON, default=list)  # User organization tags

    # Common fields
    notes = Column(Text)  # User notes about this job/application
    interaction_data = Column(
        JSON, default=dict
    )  # Flexible storage for interaction-specific data

    # Tracking
    first_interaction = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    interaction_count = Column(Integer, default=1)  # How many times user interacted

    # Job snapshot (preserve job details at time of key interactions)
    job_snapshot = Column(JSON)  # Store job details when applied/saved

    # Relationships
    user = relationship("UserProfileDB", back_populates="job_interactions")
    job = relationship("JobListingDB", back_populates="user_interactions")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id", "job_id", "interaction_type", name="unique_user_job_interaction"
        ),
        Index(
            "idx_user_interaction_type_date",
            "user_id",
            "interaction_type",
            "last_interaction",
        ),
        Index("idx_job_interaction_type", "job_id", "interaction_type"),
        # Business logic constraints
        CheckConstraint(
            "interaction_type != 'applied' OR application_status IS NOT NULL",
            name="applied_interactions_need_status",
        ),
        CheckConstraint(
            "interaction_type != 'saved' OR saved_date IS NOT NULL",
            name="saved_interactions_need_date",
        ),
        CheckConstraint(
            "interaction_type != 'applied' OR application_status != 'not_applied'",
            name="applied_interactions_cannot_be_not_applied",
        ),
    )


class CompanyInfoDB(Base):
    """SQLAlchemy model for company information."""

    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, index=True)
    normalized_name = Column(
        String, nullable=False, index=True
    )  # ADD: For fuzzy matching
    domain = Column(String, unique=True, index=True)  # ADD: Company domain for matching
    industry = Column(String, index=True)
    size = Column(String)
    size_category = Column(
        SQLEnum(CompanySizeCategory), index=True
    )  # ADD: Enum version
    location = Column(String)
    headquarters_location = Column(String)  # ADD: More specific
    founded_year = Column(Integer)  # ADD: Company age
    website = Column(String)
    description = Column(Text)
    logo_url = Column(String)  # ADD: Company logo

    # Additional details (keep existing)
    culture = Column(Text)
    values = Column(JSON, default=list)
    benefits = Column(JSON, default=list)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # NEW RELATIONSHIP: Back reference to jobs
    job_listings = relationship("JobListingDB", back_populates="company")

    # ADD: Unique constraint on normalized name + domain and validation constraints
    __table_args__ = (
        UniqueConstraint("normalized_name", "domain", name="unique_company_identity"),
        Index("idx_company_name_domain", "name", "domain"),
        # ADD: Data validation constraints
        CheckConstraint("LENGTH(name) >= 1", name="company_name_not_empty"),
        CheckConstraint("LENGTH(name) <= 200", name="company_name_max_length"),
        CheckConstraint(
            "website LIKE 'http%://%' OR website IS NULL", name="website_url_format"
        ),
        CheckConstraint(
            "founded_year >= 1800 OR founded_year IS NULL",
            name="founded_year_reasonable",
        ),
        # Note: Cannot use strftime in SQLite CHECK constraints - handled in application logic
        # CheckConstraint('founded_year <= strftime("%Y", "now") OR founded_year IS NULL', name='founded_year_not_future'),
    )


class TimelineEventDB(Base):
    """SQLAlchemy model for timeline events."""

    __tablename__ = "timeline_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    job_id = Column(
        String, ForeignKey("job_listings.id"), nullable=True
    )  # Can be None for general events
    interaction_id = Column(
        String, ForeignKey("job_user_interactions.id"), nullable=True
    )  # Link to specific user-job interaction
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
    interaction = relationship("JobUserInteractionDB")
    user_profile = relationship("UserProfileDB")


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
    # No special mappings needed after ETL removal

    return sqlalchemy_class(**data)


def sqlalchemy_to_pydantic(sqlalchemy_obj, pydantic_class):
    """Convert SQLAlchemy model to Pydantic model."""
    data = {}
    for column in sqlalchemy_obj.__table__.columns:
        value = getattr(sqlalchemy_obj, column.name)
        column_name = column.name

        # Handle field name mappings for renamed fields
        # No special mappings needed after ETL removal

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
        ]:
            value = {}
        # Skip None values for required fields - let Pydantic handle defaults
        elif value is None and column_name in ["id", "created_at", "updated_at"]:
            continue

        data[column_name] = value
    return pydantic_class(**data)
