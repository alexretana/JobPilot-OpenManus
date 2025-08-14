# JobPilot Resume Management Data Models
# Adapted from resume-lm with JobPilot-specific enhancements

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.data.models import Base

# =============================================================================
# ENUMS AND TYPES
# =============================================================================

class ResumeStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    TEMPLATE = "template"

class ResumeType(str, Enum):
    BASE = "base"            # Master resume with all experience
    TAILORED = "tailored"    # Job-specific tailored version
    TEMPLATE = "template"    # Reusable template

class SectionType(str, Enum):
    CONTACT = "contact"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    PUBLICATIONS = "publications"
    VOLUNTEER = "volunteer"
    LANGUAGES = "languages"
    INTERESTS = "interests"
    CUSTOM = "custom"

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ExperienceType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    VOLUNTEER = "volunteer"
    FREELANCE = "freelance"

# =============================================================================
# PYDANTIC MODELS (API/Validation Layer)
# =============================================================================

class ContactInfo(BaseModel):
    """Contact information section"""
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    portfolio: Optional[str] = None

class WorkExperience(BaseModel):
    """Single work experience entry"""
    company: str
    position: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    experience_type: ExperienceType = ExperienceType.FULL_TIME
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class Education(BaseModel):
    """Education entry"""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    honors: List[str] = Field(default_factory=list)
    relevant_coursework: List[str] = Field(default_factory=list)

class Skill(BaseModel):
    """Individual skill with metadata"""
    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE
    category: Optional[str] = None  # e.g., "Programming Languages", "Frameworks"
    years_experience: Optional[int] = None
    is_featured: bool = False  # Should this skill be prominently displayed?

class Project(BaseModel):
    """Project entry"""
    name: str
    description: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    url: Optional[str] = None
    github_url: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)

class Certification(BaseModel):
    """Certification entry"""
    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None

class ResumeSection(BaseModel):
    """Generic resume section"""
    section_type: SectionType
    title: str
    content: Dict[str, Any]  # Flexible content storage
    is_visible: bool = True
    order: int = 0

class ResumeTemplate(BaseModel):
    """Resume template configuration"""
    name: str
    description: Optional[str] = None
    sections: List[SectionType]
    section_order: List[SectionType]
    styling: Dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False

class ATSScore(BaseModel):
    """ATS compatibility score"""
    overall_score: float = Field(ge=0, le=100)
    keyword_score: float = Field(ge=0, le=100)
    formatting_score: float = Field(ge=0, le=100)
    section_score: float = Field(ge=0, le=100)
    length_score: float = Field(ge=0, le=100)
    suggestions: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    
class JobTailoringAnalysis(BaseModel):
    """Analysis of how well resume matches a job"""
    job_id: Optional[str] = None
    match_score: float = Field(ge=0, le=100)
    skill_match: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    recommended_additions: List[str] = Field(default_factory=list)
    sections_to_emphasize: List[SectionType] = Field(default_factory=list)

class Resume(BaseModel):
    """Complete resume model"""
    id: Optional[str] = None
    user_id: str
    title: str
    resume_type: ResumeType = ResumeType.BASE
    status: ResumeStatus = ResumeStatus.DRAFT
    
    # Resume content
    contact_info: ContactInfo
    summary: Optional[str] = None
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    custom_sections: List[ResumeSection] = Field(default_factory=list)
    
    # Metadata and configuration
    template_id: Optional[str] = None
    based_on_resume_id: Optional[str] = None  # For tailored resumes
    job_id: Optional[str] = None  # If tailored for specific job
    
    # Analysis and scoring
    ats_score: Optional[ATSScore] = None
    tailoring_analysis: Optional[JobTailoringAnalysis] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_generated_at: Optional[datetime] = None
    
    # Version control
    version: int = 1
    parent_version_id: Optional[str] = None

# =============================================================================
# SKILLS BANK MODELS
# =============================================================================

class SkillBank(BaseModel):
    """Centralized skill repository for resume building"""
    user_id: str
    skills: Dict[str, List[Skill]]  # Categorized skills
    experience_keywords: List[str] = Field(default_factory=list)
    industry_keywords: List[str] = Field(default_factory=list)
    technical_keywords: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    
    # Auto-extracted from job applications and experiences
    auto_extracted_skills: List[str] = Field(default_factory=list)
    skill_confidence: Dict[str, float] = Field(default_factory=dict)
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SkillSuggestion(BaseModel):
    """AI-generated skill suggestions"""
    skill_name: str
    category: str
    confidence: float = Field(ge=0, le=1)
    reason: str  # Why this skill was suggested
    source: str  # Job posting, experience, etc.

# =============================================================================
# SQLALCHEMY MODELS (Database Layer)
# =============================================================================

class ResumeDB(Base):
    """Resume database model"""
    __tablename__ = "resumes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    title = Column(String, nullable=False)
    resume_type = Column(String, nullable=False, default="base")
    status = Column(String, nullable=False, default="draft")
    
    # JSON content fields
    contact_info = Column(JSON, nullable=False)
    summary = Column(Text)
    work_experience = Column(JSON, default=list)
    education = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    custom_sections = Column(JSON, default=list)
    
    # Configuration
    template_id = Column(String, ForeignKey("resume_templates.id"))
    based_on_resume_id = Column(String, ForeignKey("resumes.id"))
    job_id = Column(String, ForeignKey("job_listings.id"))
    
    # Analysis results
    ats_score_data = Column(JSON)
    tailoring_analysis = Column(JSON)
    
    # Metadata
    version = Column(Integer, default=1)
    parent_version_id = Column(String, ForeignKey("resumes.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_generated_at = Column(DateTime)
    
    # Relationships
    user = relationship("UserProfileDB", back_populates="resumes")
    template = relationship("ResumeTemplateDB")
    job = relationship("JobListingDB")
    versions = relationship("ResumeDB", remote_side=[id])

class ResumeTemplateDB(Base):
    """Resume template database model"""
    __tablename__ = "resume_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    sections = Column(JSON, nullable=False)
    section_order = Column(JSON, nullable=False)
    styling = Column(JSON, default=dict)
    is_default = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)  # System vs user templates
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SkillBankDB(Base):
    """Skills bank database model"""
    __tablename__ = "skill_banks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Skill data
    skills = Column(JSON, default=dict)
    experience_keywords = Column(JSON, default=list)
    industry_keywords = Column(JSON, default=list)
    technical_keywords = Column(JSON, default=list)
    soft_skills = Column(JSON, default=list)
    auto_extracted_skills = Column(JSON, default=list)
    skill_confidence = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserProfileDB", back_populates="skill_bank")

class ResumeVersionDB(Base):
    """Resume version tracking"""
    __tablename__ = "resume_versions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    changes_summary = Column(Text)
    content_snapshot = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)  # User action vs AI action

# =============================================================================
# RESUME BUILDER AGENT MODELS
# =============================================================================

class ResumeGenerationRequest(BaseModel):
    """Request for AI resume generation/optimization"""
    user_id: str
    base_resume_id: Optional[str] = None
    job_id: Optional[str] = None
    job_description: Optional[str] = None
    template_id: Optional[str] = None
    
    # Generation parameters
    tone: str = "professional"  # professional, creative, technical
    length: str = "standard"    # concise, standard, detailed
    focus_areas: List[str] = Field(default_factory=list)
    include_sections: List[SectionType] = Field(default_factory=list)
    
    # AI model preferences
    ai_provider: str = "openai"
    model: str = "gpt-4"

class ResumeGenerationResult(BaseModel):
    """Result of AI resume generation"""
    resume: Resume
    generation_metadata: Dict[str, Any]
    suggestions: List[str]
    confidence_score: float
    processing_time: float
    tokens_used: Optional[int] = None

# =============================================================================
# RESUME REPOSITORY INTERFACE
# =============================================================================

class ResumeRepository:
    """Repository interface for resume operations"""
    
    async def create_resume(self, resume_data: Resume) -> ResumeDB:
        """Create new resume"""
        pass
    
    async def get_resume(self, resume_id: str, user_id: str) -> Optional[Resume]:
        """Get resume by ID"""
        pass
    
    async def update_resume(self, resume_id: str, updates: Dict[str, Any]) -> Optional[Resume]:
        """Update resume"""
        pass
    
    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """Delete resume"""
        pass
    
    async def get_user_resumes(self, user_id: str, status: Optional[ResumeStatus] = None) -> List[Resume]:
        """Get all resumes for user"""
        pass
    
    async def create_tailored_resume(self, base_resume_id: str, job_id: str) -> Resume:
        """Create job-tailored resume version"""
        pass
    
    async def get_resume_versions(self, resume_id: str) -> List[ResumeVersionDB]:
        """Get all versions of a resume"""
        pass
    
    async def calculate_ats_score(self, resume: Resume, job_description: Optional[str] = None) -> ATSScore:
        """Calculate ATS compatibility score"""
        pass
