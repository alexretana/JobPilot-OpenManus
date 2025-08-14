"""
JobPilot Data Models
Core data structures for job hunting functionality, migrated from original JobPilot.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, EmailStr
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, Text, JSON,
    ForeignKey, Enum as SQLEnum, create_engine, MetaData
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import sqlalchemy as sa


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


# =====================================
# Pydantic Models for API/Data Transfer
# =====================================

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
    
    @validator('skills_required', 'skills_preferred', 'benefits', pre=True)
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
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
# SQLAlchemy Database Models
# =====================================

Base = declarative_base()


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship("JobApplicationDB", back_populates="job")


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
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=True)  # Can be None for general events
    application_id = Column(String, ForeignKey("applications.id"), nullable=True)  # Link to specific application
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
    return sqlalchemy_class(**data)


def sqlalchemy_to_pydantic(sqlalchemy_obj, pydantic_class):
    """Convert SQLAlchemy model to Pydantic model."""
    data = {}
    for column in sqlalchemy_obj.__table__.columns:
        value = getattr(sqlalchemy_obj, column.name)
        # Handle None values for list fields
        if value is None and column.name in ['skills', 'preferred_locations', 'preferred_job_types', 'preferred_remote_types', 'skills_required', 'skills_preferred', 'benefits', 'values', 'tags']:
            value = []
        # Handle None values for event_data dict field
        elif value is None and column.name == 'event_data':
            value = {}
        data[column.name] = value
    return pydantic_class(**data)
