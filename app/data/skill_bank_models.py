"""
JobPilot Skill Bank Data Models
Enhanced skill bank models for comprehensive content variation management
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base
from .resume_models import ExperienceType, SkillLevel

# =============================================================================
# CONTENT VARIATION ENUMS
# =============================================================================


class ContentFocusType(str, Enum):
    """Type of focus for content variations."""

    TECHNICAL = "technical"
    LEADERSHIP = "leadership"
    RESULTS = "results"
    GENERAL = "general"
    CREATIVE = "creative"
    CONCISE = "concise"
    DETAILED = "detailed"


class SkillCategory(str, Enum):
    """Categories of skills."""

    TECHNICAL = "technical"
    SOFT = "soft"
    TRANSFERABLE = "transferable"
    INDUSTRY = "industry"
    TOOL = "tool"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    PLATFORM = "platform"
    METHODOLOGY = "methodology"
    DOMAIN = "domain"
    OTHER = "other"


class ContentSource(str, Enum):
    """Source of content or skill."""

    MANUAL = "manual"  # User-entered
    EXTRACTED = "extracted"  # Auto-extracted from job/resume
    GENERATED = "generated"  # AI-generated
    IMPORTED = "imported"  # Imported from external source


# =============================================================================
# CONTENT VARIATION MODELS (Pydantic)
# =============================================================================


class ContentVariation(BaseModel):
    """Base model for all content variations."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str  # "Technical Focus", "Leadership Focus", etc.
    content: str  # The actual content variation

    # Context & Usage
    target_industries: List[str] = Field(default_factory=list)
    target_roles: List[str] = Field(default_factory=list)
    keywords_emphasized: List[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    source: ContentSource = ContentSource.MANUAL


class SummaryVariation(ContentVariation):
    """Professional summary variations."""

    tone: str = "professional"  # professional, creative, technical
    length: str = "standard"  # concise, standard, detailed
    focus: ContentFocusType = ContentFocusType.GENERAL


class ExperienceContentVariation(ContentVariation):
    """Work experience content variations."""

    experience_id: str  # Links to specific work experience
    focus: ContentFocusType = ContentFocusType.GENERAL
    achievements: List[str] = Field(default_factory=list)
    skills_highlighted: List[str] = Field(default_factory=list)


class EducationContentVariation(ContentVariation):
    """Education content variations."""

    education_id: str  # Links to specific education entry
    focus: ContentFocusType = ContentFocusType.GENERAL
    highlights: List[str] = Field(default_factory=list)
    relevant_coursework: List[str] = Field(default_factory=list)


class ProjectContentVariation(ContentVariation):
    """Project content variations."""

    project_id: str  # Links to specific project
    focus: ContentFocusType = ContentFocusType.GENERAL
    achievements: List[str] = Field(default_factory=list)
    technologies_highlighted: List[str] = Field(default_factory=list)


# =============================================================================
# MASTER ENTRY MODELS (Pydantic)
# =============================================================================


class ExperienceEntry(BaseModel):
    """Master work experience record."""

    id: str = Field(default_factory=lambda: str(uuid4()))

    # Basic Info (Stable)
    company: str
    position: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    experience_type: ExperienceType = ExperienceType.FULL_TIME

    # Default Content
    default_description: Optional[str] = None
    default_achievements: List[str] = Field(default_factory=list)

    # Skills & Technologies Used
    skills_used: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

    # Content Variations (References to SkillBank.experience_content_variations[this.id])
    has_variations: bool = False
    default_variation_id: Optional[str] = None

    @validator("end_date")
    def validate_end_date(cls, v, values):
        if v and "start_date" in values and v < values["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class EducationEntry(BaseModel):
    """Master education record."""

    id: str = Field(default_factory=lambda: str(uuid4()))

    # Basic Info (Stable)
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None

    # Default Content
    honors: List[str] = Field(default_factory=list)
    relevant_coursework: List[str] = Field(default_factory=list)
    default_description: Optional[str] = None

    # Content Variations (References to SkillBank.education_content_variations[this.id])
    has_variations: bool = False
    default_variation_id: Optional[str] = None

    @validator("end_date")
    def validate_end_date(cls, v, values):
        if (
            v
            and "start_date" in values
            and values["start_date"]
            and v < values["start_date"]
        ):
            raise ValueError("End date must be after start date")
        return v


class ProjectEntry(BaseModel):
    """Master project record."""

    id: str = Field(default_factory=lambda: str(uuid4()))

    # Basic Info (Stable)
    name: str
    url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # Default Content
    default_description: Optional[str] = None
    default_achievements: List[str] = Field(default_factory=list)

    # Technologies
    technologies: List[str] = Field(default_factory=list)

    # Content Variations (References to SkillBank.project_content_variations[this.id])
    has_variations: bool = False
    default_variation_id: Optional[str] = None

    @validator("end_date")
    def validate_end_date(cls, v, values):
        if (
            v
            and "start_date" in values
            and values["start_date"]
            and v < values["start_date"]
        ):
            raise ValueError("End date must be after start date")
        return v


class EnhancedSkill(BaseModel):
    """Enhanced skill with detailed metadata."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE

    # Categorization
    category: SkillCategory = SkillCategory.TECHNICAL
    subcategory: Optional[str] = None  # "Programming Languages", "Frameworks", etc.

    # Experience & Proficiency
    years_experience: Optional[int] = None
    proficiency_score: Optional[float] = Field(None, ge=0, le=1)  # 0.0-1.0

    # Context & Usage
    description: Optional[str] = None  # User-written description
    keywords: List[str] = Field(default_factory=list)  # Related terms

    # Display & Organization
    is_featured: bool = False  # Should be prominently displayed
    display_order: int = 0

    # Metadata
    source: ContentSource = ContentSource.MANUAL
    confidence: float = Field(1.0, ge=0, le=1)  # AI confidence if auto-extracted
    last_used: Optional[datetime] = None
    usage_count: int = 0


class Certification(BaseModel):
    """Certification entry with simplified structure."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

    # Simple validation
    @validator("expiry_date")
    def validate_expiry_date(cls, v, values):
        if (
            v
            and "issue_date" in values
            and values["issue_date"]
            and v < values["issue_date"]
        ):
            raise ValueError("Expiry date must be after issue date")
        return v


# =============================================================================
# COMPLETE SKILL BANK MODEL (Pydantic)
# =============================================================================


class SkillBank(BaseModel):
    """Enhanced skill bank with content variations."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str

    # SKILLS MANAGEMENT (Enhanced)
    skills: Dict[str, List[EnhancedSkill]] = Field(default_factory=dict)
    skill_categories: List[str] = Field(default_factory=list)

    # SUMMARY VARIATIONS
    default_summary: Optional[str] = None
    summary_variations: List[SummaryVariation] = Field(default_factory=list)

    # EXPERIENCE ENTRIES (Master Records)
    work_experiences: List[ExperienceEntry] = Field(default_factory=list)

    # EDUCATION ENTRIES (Master Records)
    education_entries: List[EducationEntry] = Field(default_factory=list)

    # PROJECT ENTRIES (Master Records)
    projects: List[ProjectEntry] = Field(default_factory=list)

    # CERTIFICATIONS (Simple - no variations needed)
    certifications: List[Certification] = Field(default_factory=list)

    # CONTENT VARIATIONS (Related to experiences/education/projects)
    experience_content_variations: Dict[str, List[ExperienceContentVariation]] = Field(
        default_factory=dict
    )
    education_content_variations: Dict[str, List[EducationContentVariation]] = Field(
        default_factory=dict
    )
    project_content_variations: Dict[str, List[ProjectContentVariation]] = Field(
        default_factory=dict
    )

    # LEGACY FIELDS (For backward compatibility)
    experience_keywords: List[str] = Field(default_factory=list)
    industry_keywords: List[str] = Field(default_factory=list)
    technical_keywords: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)

    # AI EXTRACTION & SUGGESTION
    auto_extracted_skills: List[str] = Field(default_factory=list)
    skill_confidence: Dict[str, float] = Field(default_factory=dict)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user-123",
                "skills": {
                    "Technical Skills": [
                        {
                            "name": "Python",
                            "level": "expert",
                            "category": "technical",
                            "subcategory": "Programming Languages",
                            "years_experience": 5,
                            "description": "Expert in Python development with focus on data analysis and API development",
                            "is_featured": True,
                        }
                    ]
                },
                "default_summary": "Experienced software engineer with expertise in...",
                "summary_variations": [
                    {
                        "title": "Technical Focus",
                        "content": "Technical software engineer with deep expertise in...",
                        "tone": "technical",
                        "length": "standard",
                        "focus": "technical",
                    }
                ],
                "work_experiences": [
                    {
                        "company": "Tech Corp",
                        "position": "Senior Developer",
                        "start_date": "2020-01-01",
                        "is_current": True,
                        "default_description": "Led development of...",
                    }
                ],
            }
        }


# =============================================================================
# SQLALCHEMY MODELS (Database Layer)
# =============================================================================


class EnhancedSkillBankDB(Base):
    """Enhanced skills bank database model."""

    __tablename__ = "skill_banks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)

    # SKILLS MANAGEMENT (Enhanced)
    skills = Column(JSON, default=dict)  # Dict[category, List[EnhancedSkill]]
    skill_categories = Column(
        JSON, default=list
    )  # ["Technical", "Soft Skills", "Transferable"]

    # SUMMARY VARIATIONS
    default_summary = Column(Text)
    summary_variations = Column(JSON, default=list)  # List[SummaryVariation]

    # EXPERIENCE ENTRIES (Master Records)
    work_experiences = Column(JSON, default=list)  # List[ExperienceEntry]

    # EDUCATION ENTRIES (Master Records)
    education_entries = Column(JSON, default=list)  # List[EducationEntry]

    # PROJECT ENTRIES (Master Records)
    projects = Column(JSON, default=list)  # List[ProjectEntry]

    # CERTIFICATIONS (Simple - no variations needed)
    certifications = Column(JSON, default=list)  # List[Certification]

    # CONTENT VARIATIONS (Related to experiences/education/projects)
    experience_content_variations = Column(
        JSON, default=dict
    )  # Dict[experience_id, List[ContentVariation]]
    education_content_variations = Column(
        JSON, default=dict
    )  # Dict[education_id, List[ContentVariation]]
    project_content_variations = Column(
        JSON, default=dict
    )  # Dict[project_id, List[ContentVariation]]

    # LEGACY FIELDS (For backward compatibility)
    experience_keywords = Column(JSON, default=list)
    industry_keywords = Column(JSON, default=list)
    technical_keywords = Column(JSON, default=list)
    soft_skills = Column(JSON, default=list)
    auto_extracted_skills = Column(JSON, default=list)
    skill_confidence = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserProfileDB", back_populates="skill_bank")


# =============================================================================
# REPOSITORY INTERFACE
# =============================================================================


class SkillBankRepository:
    """Repository interface for skill bank operations."""

    async def get_skill_bank(self, user_id: str) -> Optional[SkillBank]:
        """Get user's skill bank."""

    async def create_skill_bank(self, user_id: str) -> SkillBank:
        """Create a new skill bank for user."""

    async def update_skill_bank(
        self, user_id: str, updates: Dict[str, Any]
    ) -> SkillBank:
        """Update skill bank fields."""

    # === SKILLS MANAGEMENT ===
    async def add_skill(self, user_id: str, skill: EnhancedSkill) -> EnhancedSkill:
        """Add a new skill to the skill bank."""

    async def update_skill(
        self, user_id: str, skill_id: str, updates: Dict[str, Any]
    ) -> EnhancedSkill:
        """Update an existing skill."""

    async def delete_skill(self, user_id: str, skill_id: str) -> bool:
        """Delete a skill from the skill bank."""

    async def get_skills(
        self, user_id: str, category: Optional[str] = None
    ) -> List[EnhancedSkill]:
        """Get all skills, optionally filtered by category."""

    # === SUMMARY VARIATIONS ===
    async def add_summary_variation(
        self, user_id: str, variation: SummaryVariation
    ) -> SummaryVariation:
        """Add a summary variation."""

    async def update_summary_variation(
        self, user_id: str, variation_id: str, updates: Dict[str, Any]
    ) -> SummaryVariation:
        """Update a summary variation."""

    async def delete_summary_variation(self, user_id: str, variation_id: str) -> bool:
        """Delete a summary variation."""

    # === EXPERIENCE MANAGEMENT ===
    async def add_experience(
        self, user_id: str, experience: ExperienceEntry
    ) -> ExperienceEntry:
        """Add a work experience entry."""

    async def update_experience(
        self, user_id: str, experience_id: str, updates: Dict[str, Any]
    ) -> ExperienceEntry:
        """Update a work experience entry."""

    async def delete_experience(self, user_id: str, experience_id: str) -> bool:
        """Delete a work experience entry."""

    async def add_experience_variation(
        self, user_id: str, variation: ExperienceContentVariation
    ) -> ExperienceContentVariation:
        """Add a variation to a work experience entry."""

    # === DATA MIGRATION ===
    async def migrate_from_user_profile(self, user_id: str) -> SkillBank:
        """Migrate skills data from UserProfile to SkillBank."""

    async def migrate_from_resumes(self, user_id: str) -> SkillBank:
        """Migrate content from user's resumes to SkillBank."""


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_default_skill_bank(user_id: str) -> SkillBank:
    """Create a default skill bank for a new user."""

    return SkillBank(
        user_id=user_id,
        skill_categories=[
            "Technical Skills",
            "Soft Skills",
            "Tools & Technologies",
            "Languages",
            "Frameworks",
            "Methodologies",
            "Domain Knowledge",
        ],
        skills={"Technical Skills": [], "Soft Skills": [], "Tools & Technologies": []},
        default_summary="",
        summary_variations=[],
    )


def get_contact_info_from_user_profile(profile) -> Dict[str, Any]:
    """Extract contact info from UserProfileDB."""

    location = None
    if profile.city and profile.state:
        location = f"{profile.city}, {profile.state}"
    elif profile.city:
        location = profile.city
    elif profile.state:
        location = profile.state

    return {
        "full_name": f"{profile.first_name or ''} {profile.last_name or ''}".strip(),
        "email": profile.email,
        "phone": profile.phone,
        "location": location,
        "linkedin_url": profile.linkedin_url,
        "portfolio_url": profile.portfolio_url,
    }


def convert_skill_list_to_enhanced(skills: List[str]) -> List[EnhancedSkill]:
    """Convert a simple list of skill names to EnhancedSkill objects."""

    return [
        EnhancedSkill(
            name=skill,
            level=SkillLevel.INTERMEDIATE,
            category=SkillCategory.TECHNICAL,
            source=ContentSource.IMPORTED,
        )
        for skill in skills
    ]
