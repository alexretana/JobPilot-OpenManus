# JobPilot Resume Management Data Models
# Adapted from resume-lm with JobPilot-specific enhancements

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
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
)
from sqlalchemy.orm import relationship

from .base import Base

# =============================================================================
# ENUMS AND TYPES
# =============================================================================


class ResumeStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    TEMPLATE = "template"


class ResumeType(str, Enum):
    BASE = "base"  # Master resume with all experience
    TAILORED = "tailored"  # Job-specific tailored version
    TEMPLATE = "template"  # Reusable template


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
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
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

    @validator("end_date")
    def validate_end_date(cls, v, values):
        if v and "start_date" in values and v < values["start_date"]:
            raise ValueError("End date must be after start date")
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
    parent_resume_id: Optional[str] = (
        None  # RENAME from based_on_resume_id - For versions/tailoring
    )
    target_job_id: Optional[str] = (
        None  # RENAME from job_id - If tailored for specific job
    )

    # REMOVED: Redundant fields
    # based_on_resume_id: Optional[str] = None  # DELETED - renamed to parent_resume_id
    # job_id: Optional[str] = None              # DELETED - renamed to target_job_id
    # parent_version_id: Optional[str] = None   # DELETED - redundant with parent_resume_id

    # Analysis and scoring
    ats_score: Optional[ATSScore] = None
    tailoring_analysis: Optional[JobTailoringAnalysis] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_generated_at: Optional[datetime] = None

    # Version control
    version: int = 1


# =============================================================================
# SKILLS BANK MODELS - MOVED
# =============================================================================

# SkillBank and related models have been moved to skill_bank_models.py
# to provide enhanced functionality with content variations and structured data management.
# Use the EnhancedSkillBankDB and SkillBank models from skill_bank_models.py instead.

# =============================================================================
# SQLALCHEMY MODELS (Database Layer)
# =============================================================================


class ResumeDB(Base):
    """Resume database model"""

    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, nullable=False)
    resume_type = Column(String, nullable=False, default="base")
    status = Column(String, nullable=False, default="draft")

    # JSON content fields (keep all content fields unchanged)
    contact_info = Column(JSON, nullable=False)
    summary = Column(Text)
    work_experience = Column(JSON, default=list)
    education = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    custom_sections = Column(JSON, default=list)

    # SIMPLIFIED: Foreign key relationships with proper cascade rules
    template_id = Column(String, ForeignKey("resume_templates.id", ondelete="SET NULL"))
    parent_resume_id = Column(
        String, ForeignKey("resumes.id", ondelete="SET NULL")
    )  # For versions/tailoring
    target_job_id = Column(
        String, ForeignKey("job_listings.id", ondelete="SET NULL")
    )  # If tailored for specific job

    # REMOVED: Redundant fields
    # based_on_resume_id = Column(String, ForeignKey("resumes.id"))  # DELETED - redundant with parent_resume_id
    # job_id = Column(String, ForeignKey("job_listings.id"))  # DELETED - redundant with target_job_id
    # parent_version_id = Column(String, ForeignKey("resumes.id"))  # DELETED - redundant with parent_resume_id

    # Analysis results (keep analysis and version control fields)
    ats_score_data = Column(JSON)
    tailoring_analysis = Column(JSON)

    # Metadata
    version = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_generated_at = Column(DateTime)

    # IMPROVED: Relationships with better back_populates
    user = relationship("UserProfileDB", back_populates="resumes")
    template = relationship("ResumeTemplateDB", back_populates="resumes")
    parent_resume = relationship(
        "ResumeDB", remote_side=[id], back_populates="child_resumes"
    )
    child_resumes = relationship("ResumeDB", back_populates="parent_resume")
    target_job = relationship("JobListingDB", back_populates="tailored_resumes")
    generations = relationship("ResumeGenerationDB", back_populates="resume")

    # ADD: Table constraints for data integrity
    __table_args__ = (
        # Prevent circular parent relationships
        CheckConstraint("parent_resume_id != id", name="no_self_parent"),
        # Ensure tailored resumes have a parent or are base types
        CheckConstraint(
            "resume_type = 'base' OR parent_resume_id IS NOT NULL",
            name="tailored_resumes_need_parent",
        ),
        # Ensure template resumes don't have parents or targets
        CheckConstraint(
            "resume_type != 'template' OR (parent_resume_id IS NULL AND target_job_id IS NULL)",
            name="templates_are_standalone",
        ),
        # Index for common queries
        Index("idx_user_resume_type_status", "user_id", "resume_type", "status"),
        Index("idx_parent_resume", "parent_resume_id"),
        Index("idx_target_job", "target_job_id"),
    )


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

    # ADD: Back reference to resumes using this template
    resumes = relationship("ResumeDB", back_populates="template")


# NOTE: SkillBankDB has been replaced by EnhancedSkillBankDB in skill_bank_models.py
# This class is kept for backward compatibility during migration


# Legacy SkillBankDB model removed - replaced by EnhancedSkillBankDB in skill_bank_models.py
# All legacy skill bank functionality has been migrated to the enhanced system


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
    length: str = "standard"  # concise, standard, detailed
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

    async def get_resume(self, resume_id: str, user_id: str) -> Optional[Resume]:
        """Get resume by ID"""

    async def update_resume(
        self, resume_id: str, updates: Dict[str, Any]
    ) -> Optional[Resume]:
        """Update resume"""

    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """Delete resume"""

    async def get_user_resumes(
        self, user_id: str, status: Optional[ResumeStatus] = None
    ) -> List[Resume]:
        """Get all resumes for user"""

    async def create_tailored_resume(self, base_resume_id: str, job_id: str) -> Resume:
        """Create job-tailored resume version"""

    async def get_resume_versions(self, resume_id: str) -> List[ResumeVersionDB]:
        """Get all versions of a resume"""

    async def calculate_ats_score(
        self, resume: Resume, job_description: Optional[str] = None
    ) -> ATSScore:
        """Calculate ATS compatibility score"""


# =============================================================================
# RESUME GENERATION AND FILE OUTPUT
# =============================================================================


class ResumeFormat(str, Enum):
    """Resume output formats"""

    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"
    TXT = "txt"


class ResumeGenerationDB(Base):
    """Resume generation tracking database model"""

    __tablename__ = "resume_generations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False)

    # Generation details
    format = Column(String, nullable=False)  # PDF, DOCX, HTML, etc.
    template_name = Column(String, nullable=False)
    file_path = Column(String)
    file_size = Column(Integer)
    generation_params = Column(JSON, default=dict)

    # Generation status
    status = Column(String, default="pending")  # pending, completed, failed
    error_message = Column(Text)

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resume = relationship("ResumeDB", back_populates="generations")


class ResumeOptimizationDB(Base):
    """Resume optimization tracking for specific jobs"""

    __tablename__ = "resume_optimizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)

    # Optimization results
    match_score = Column(Float, nullable=False)
    keyword_matches = Column(JSON, default=list)
    missing_keywords = Column(JSON, default=list)
    skill_matches = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)

    # Recommendations
    recommendations = Column(JSON, default=list)
    sections_to_emphasize = Column(JSON, default=list)
    content_suggestions = Column(JSON, default=list)

    # Analysis metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    analysis_version = Column(String, default="v1.0")

    # Relationships
    resume = relationship("ResumeDB")
    job = relationship("JobListingDB")


# =============================================================================
# UTILITY FUNCTIONS FOR RESUME OPERATIONS
# =============================================================================


def create_resume_from_profile(user_profile_data: Dict[str, Any]) -> Resume:
    """Create a basic resume from user profile data"""
    contact_info = ContactInfo(
        full_name=f"{user_profile_data.get('first_name', '')} {user_profile_data.get('last_name', '')}".strip(),
        email=user_profile_data.get("email", ""),
        phone=user_profile_data.get("phone"),
        linkedin_url=user_profile_data.get("linkedin_url"),
        github_url=user_profile_data.get("github_url"),
        website_url=user_profile_data.get("website_url"),
    )

    # Convert profile skills to resume skills
    skills = []
    if user_profile_data.get("skills"):
        for skill_name in user_profile_data["skills"]:
            skills.append(
                Skill(
                    name=skill_name,
                    level=SkillLevel.INTERMEDIATE,
                    category="Technical Skills",
                )
            )

    resume = Resume(
        user_id=user_profile_data["id"],
        title=f"{user_profile_data.get('current_title', 'Professional')} Resume",
        contact_info=contact_info,
        summary=user_profile_data.get("bio"),
        skills=skills,
    )

    return resume


def calculate_resume_completeness(resume: Resume) -> float:
    """Calculate resume completeness score (0.0 to 100.0)"""
    score = 0
    total_sections = 8

    # Essential sections
    if resume.contact_info.full_name and resume.contact_info.email:
        score += 1
    if resume.summary and len(resume.summary.strip()) > 30:
        score += 1
    if len(resume.work_experience) > 0:
        score += 1
    if len(resume.education) > 0:
        score += 1
    if len(resume.skills) >= 3:
        score += 1
    if len(resume.projects) > 0 or len(resume.certifications) > 0:
        score += 1
    if resume.contact_info.linkedin_url or resume.contact_info.github_url:
        score += 1
    if any(exp.achievements for exp in resume.work_experience):
        score += 1

    return (score / total_sections) * 100


def extract_resume_keywords(resume: Resume) -> List[str]:
    """Extract all keywords from resume content"""
    keywords = set()

    # From skills
    for skill in resume.skills:
        keywords.add(skill.name.lower())
        if skill.category:
            keywords.add(skill.category.lower())

    # From work experience
    for exp in resume.work_experience:
        keywords.update(skill.lower() for skill in exp.skills_used)
        keywords.add(exp.position.lower())
        keywords.add(exp.company.lower())

    # From projects
    for project in resume.projects:
        keywords.update(tech.lower() for tech in project.technologies)

    # From education
    for edu in resume.education:
        if edu.field_of_study:
            keywords.add(edu.field_of_study.lower())
        keywords.add(edu.degree.lower())

    # From certifications
    for cert in resume.certifications:
        keywords.add(cert.name.lower())
        keywords.add(cert.issuer.lower())

    return list(keywords)


def generate_ats_score(
    resume: Resume, job_description: Optional[str] = None
) -> ATSScore:
    """Generate ATS compatibility score for resume"""
    # Basic scoring algorithm
    format_score = 85.0  # Assume good format

    # Section scoring
    has_contact = bool(resume.contact_info.full_name and resume.contact_info.email)
    has_experience = len(resume.work_experience) > 0
    has_skills = len(resume.skills) > 0
    has_education = len(resume.education) > 0

    section_score = (
        (25 if has_contact else 0)
        + (35 if has_experience else 0)
        + (25 if has_skills else 0)
        + (15 if has_education else 0)
    )

    # Length scoring (assume good length)
    length_score = 90.0

    # Keyword scoring
    resume_keywords = set(extract_resume_keywords(resume))
    if job_description:
        # Simple keyword matching - in production this would be more sophisticated
        job_keywords = set(job_description.lower().split())
        common_keywords = resume_keywords.intersection(job_keywords)
        keyword_score = min(len(common_keywords) * 5, 100.0)
        missing_keywords = list(job_keywords - resume_keywords)[:10]  # Top 10 missing
    else:
        keyword_score = 75.0  # Default score without job description
        missing_keywords = []

    overall_score = (format_score + section_score + length_score + keyword_score) / 4

    suggestions = []
    if not has_contact:
        suggestions.append("Add complete contact information")
    if not has_experience:
        suggestions.append("Add work experience section")
    if not has_skills:
        suggestions.append("Add skills section")
    if len(resume.skills) < 5:
        suggestions.append("Add more relevant skills")
    if not any(exp.achievements for exp in resume.work_experience):
        suggestions.append("Add specific achievements to work experience")

    return ATSScore(
        overall_score=overall_score,
        keyword_score=keyword_score,
        formatting_score=format_score,
        section_score=section_score,
        length_score=length_score,
        suggestions=suggestions,
        missing_keywords=missing_keywords,
    )
