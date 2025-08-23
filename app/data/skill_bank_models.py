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

    # LEGACY FIELDS - REMOVED: Now handled by enhanced skills system
    # experience_keywords: List[str] = Field(default_factory=list)  # DELETE - use enhanced skills with keywords
    # industry_keywords: List[str] = Field(default_factory=list)    # DELETE - use enhanced skills with keywords
    # technical_keywords: List[str] = Field(default_factory=list)   # DELETE - use enhanced skills with keywords
    # soft_skills: List[str] = Field(default_factory=list)          # DELETE - use enhanced skills with category

    # AI EXTRACTION & SUGGESTION - REMOVED: Now handled by individual skill metadata
    # auto_extracted_skills: List[str] = Field(default_factory=list)  # DELETE - use skill.source = EXTRACTED
    # skill_confidence: Dict[str, float] = Field(default_factory=dict)  # DELETE - use skill.confidence field

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Task 3.3 SKIPPED: No computed properties needed in development mode
    # Legacy compatibility properties were not implemented since we're working with fresh mock data

    def get_skills_by_category(self, category: SkillCategory) -> List[EnhancedSkill]:
        """Get all skills for a specific category."""
        all_skills = []
        for skill_list in self.skills.values():
            all_skills.extend(
                [skill for skill in skill_list if skill.category == category]
            )
        return sorted(
            all_skills, key=lambda s: (s.is_featured, s.display_order), reverse=True
        )

    def get_featured_skills(self) -> List[EnhancedSkill]:
        """Get all featured skills across all categories."""
        featured = []
        for skill_list in self.skills.values():
            featured.extend([skill for skill in skill_list if skill.is_featured])
        return sorted(featured, key=lambda s: s.display_order)

    def get_all_skill_names(self) -> List[str]:
        """Get all skill names as a flat list."""
        all_names = []
        for skill_list in self.skills.values():
            all_names.extend([skill.name for skill in skill_list])
        return sorted(all_names)

    def get_skills_for_resume_section(
        self, max_skills: int = 10, prefer_featured: bool = True
    ) -> List[str]:
        """Get skills formatted for resume sections."""
        if prefer_featured:
            # Start with featured skills
            skills = self.get_featured_skills()
            if len(skills) >= max_skills:
                return [skill.name for skill in skills[:max_skills]]

            # Fill remaining with non-featured skills by proficiency
            remaining_count = max_skills - len(skills)
            all_skills = []
            for skill_list in self.skills.values():
                all_skills.extend([s for s in skill_list if not s.is_featured])

            # Sort by proficiency score (highest first)
            all_skills.sort(key=lambda s: s.proficiency_score or 0, reverse=True)
            skills.extend(all_skills[:remaining_count])
        else:
            # Get all skills and sort by proficiency
            all_skills = []
            for skill_list in self.skills.values():
                all_skills.extend(skill_list)
            all_skills.sort(key=lambda s: s.proficiency_score or 0, reverse=True)
            skills = all_skills[:max_skills]

        return [skill.name for skill in skills]

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

    # Legacy fields removed - functionality migrated to enhanced skills system
    # All legacy keyword and skill fields have been replaced by the EnhancedSkill system
    # which provides more structured and flexible skill management

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
    """Create a default skill bank for a new user with comprehensive mock data."""
    from datetime import date

    # Create sample enhanced skills
    technical_skills = [
        EnhancedSkill(
            name="Python",
            level=SkillLevel.EXPERT,
            category=SkillCategory.TECHNICAL,
            subcategory="Programming Languages",
            years_experience=5,
            proficiency_score=0.9,
            description="Expert in Python development with focus on web applications, data analysis, and automation",
            keywords=["Django", "FastAPI", "NumPy", "Pandas", "Automation"],
            is_featured=True,
            display_order=1,
        ),
        EnhancedSkill(
            name="JavaScript",
            level=SkillLevel.EXPERT,
            category=SkillCategory.TECHNICAL,
            subcategory="Programming Languages",
            years_experience=4,
            proficiency_score=0.85,
            description="Full-stack JavaScript development including modern ES6+, Node.js, and frontend frameworks",
            keywords=["ES6+", "Node.js", "React", "Vue", "TypeScript"],
            is_featured=True,
            display_order=2,
        ),
        EnhancedSkill(
            name="React",
            level=SkillLevel.EXPERT,
            category=SkillCategory.FRAMEWORK,
            subcategory="Frontend Frameworks",
            years_experience=3,
            proficiency_score=0.8,
            description="Advanced React development including hooks, context, state management, and modern patterns",
            keywords=["Hooks", "Redux", "Context API", "JSX", "Components"],
            is_featured=True,
            display_order=3,
        ),
        EnhancedSkill(
            name="SQL",
            level=SkillLevel.ADVANCED,
            category=SkillCategory.TECHNICAL,
            subcategory="Database",
            years_experience=4,
            proficiency_score=0.75,
            description="Database design, complex queries, performance optimization, and data modeling",
            keywords=["PostgreSQL", "MySQL", "Query Optimization", "Database Design"],
            is_featured=False,
            display_order=4,
        ),
    ]

    interpersonal_skills = [
        EnhancedSkill(
            name="Project Management",
            level=SkillLevel.ADVANCED,
            category=SkillCategory.SOFT,
            subcategory="Leadership",
            years_experience=3,
            proficiency_score=0.8,
            description="Leading cross-functional teams, agile methodologies, and project delivery",
            keywords=["Agile", "Scrum", "Team Leadership", "Planning"],
            is_featured=True,
            display_order=1,
        ),
        EnhancedSkill(
            name="Communication",
            level=SkillLevel.EXPERT,
            category=SkillCategory.SOFT,
            subcategory="Interpersonal",
            years_experience=5,
            proficiency_score=0.9,
            description="Excellent written and verbal communication, presentation skills, and stakeholder management",
            keywords=["Presentations", "Technical Writing", "Stakeholder Management"],
            is_featured=True,
            display_order=2,
        ),
    ]

    tools_skills = [
        EnhancedSkill(
            name="Git",
            level=SkillLevel.EXPERT,
            category=SkillCategory.TOOL,
            subcategory="Version Control",
            years_experience=5,
            proficiency_score=0.9,
            description="Advanced Git workflows, branching strategies, and collaboration practices",
            keywords=["GitHub", "GitLab", "Branching", "Merge Conflicts"],
            is_featured=False,
            display_order=1,
        ),
        EnhancedSkill(
            name="Docker",
            level=SkillLevel.ADVANCED,
            category=SkillCategory.TOOL,
            subcategory="DevOps",
            years_experience=2,
            proficiency_score=0.7,
            description="Containerization, Docker Compose, and deployment strategies",
            keywords=["Containerization", "Docker Compose", "Deployment"],
            is_featured=False,
            display_order=2,
        ),
    ]

    # Create sample summary variations
    summary_variations = [
        SummaryVariation(
            title="Technical Leadership Focus",
            content="Experienced software engineer with 5+ years developing scalable web applications using Python, JavaScript, and modern frameworks. Proven track record of leading development teams and delivering high-quality solutions. Passionate about clean code, best practices, and mentoring junior developers.",
            tone="professional",
            length="standard",
            focus=ContentFocusType.TECHNICAL,
            target_industries=["Technology", "Software", "Startups"],
            target_roles=["Senior Developer", "Tech Lead", "Engineering Manager"],
            keywords_emphasized=[
                "Python",
                "JavaScript",
                "Leadership",
                "Scalable Applications",
            ],
        ),
        SummaryVariation(
            title="Full-Stack Developer Focus",
            content="Full-stack developer specializing in modern web technologies including React, Python, and cloud platforms. Strong background in both frontend user experience and backend architecture. Experienced in agile development and cross-functional collaboration.",
            tone="professional",
            length="concise",
            focus=ContentFocusType.GENERAL,
            target_industries=["Technology", "E-commerce", "SaaS"],
            target_roles=["Full Stack Developer", "Software Engineer", "Web Developer"],
            keywords_emphasized=["React", "Python", "Full-Stack", "Agile"],
        ),
        SummaryVariation(
            title="Results-Oriented Focus",
            content="Results-driven software engineer with expertise in building high-performance applications that serve millions of users. Led projects that increased system efficiency by 40% and reduced deployment time by 60%. Strong focus on scalability, performance optimization, and user experience.",
            tone="professional",
            length="standard",
            focus=ContentFocusType.RESULTS,
            target_industries=["Technology", "Enterprise Software", "SaaS"],
            target_roles=[
                "Senior Engineer",
                "Principal Developer",
                "Technical Architect",
            ],
            keywords_emphasized=[
                "Performance",
                "Scalability",
                "Results",
                "Optimization",
            ],
        ),
    ]

    # Create sample work experiences
    work_experiences = [
        ExperienceEntry(
            company="TechCorp Solutions",
            position="Senior Software Engineer",
            location="San Francisco, CA",
            start_date=date(2022, 1, 15),
            end_date=None,
            is_current=True,
            experience_type=ExperienceType.FULL_TIME,
            default_description="Lead development of microservices architecture serving 2M+ daily active users. Architect and implement scalable solutions using Python, React, and cloud technologies.",
            default_achievements=[
                "Improved system performance by 40% through database optimization and caching strategies",
                "Led a team of 5 developers in migrating legacy monolith to microservices architecture",
                "Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes",
                "Mentored 3 junior developers, with 2 receiving promotions within 18 months",
            ],
            skills_used=["Python", "React", "PostgreSQL", "Docker", "AWS"],
            technologies=["FastAPI", "Redux", "Redis", "Kubernetes", "GitLab CI"],
        ),
        ExperienceEntry(
            company="DataFlow Analytics",
            position="Software Developer",
            location="Austin, TX",
            start_date=date(2020, 3, 1),
            end_date=date(2022, 1, 10),
            is_current=False,
            experience_type=ExperienceType.FULL_TIME,
            default_description="Full-stack development of data analytics platform processing 10TB+ daily. Built responsive web interfaces and robust API services.",
            default_achievements=[
                "Developed real-time dashboard displaying analytics for 500+ enterprise clients",
                "Optimized data processing pipeline, reducing analysis time from hours to minutes",
                "Built REST APIs handling 100K+ requests per day with 99.9% uptime",
                "Collaborated with data science team to implement machine learning model integration",
            ],
            skills_used=["JavaScript", "Python", "SQL", "React", "Node.js"],
            technologies=["Express.js", "MongoDB", "D3.js", "Pandas", "Scikit-learn"],
        ),
        ExperienceEntry(
            company="WebSolutions Inc",
            position="Junior Developer",
            location="Remote",
            start_date=date(2019, 6, 1),
            end_date=date(2020, 2, 28),
            is_current=False,
            experience_type=ExperienceType.FULL_TIME,
            default_description="Frontend development for e-commerce platform with focus on user experience and responsive design. Collaborated closely with design and backend teams.",
            default_achievements=[
                "Implemented responsive design improving mobile conversion rate by 25%",
                "Built reusable component library adopted across 3 product teams",
                "Reduced page load time by 30% through code optimization and lazy loading",
            ],
            skills_used=["JavaScript", "HTML", "CSS", "React", "Git"],
            technologies=["Webpack", "Sass", "Jest", "Figma", "GitHub"],
        ),
    ]

    # Create sample projects
    projects = [
        ProjectEntry(
            name="Task Management SaaS Platform",
            url="https://github.com/user/task-manager",
            github_url="https://github.com/user/task-manager",
            start_date=date(2023, 6, 1),
            end_date=date(2023, 9, 15),
            default_description="Full-stack SaaS application for team task management with real-time collaboration features",
            default_achievements=[
                "Built with React frontend and FastAPI backend serving 1000+ registered users",
                "Implemented real-time updates using WebSockets and Redis pub/sub",
                "Achieved 99.5% uptime with automated deployment and monitoring",
            ],
            technologies=["React", "FastAPI", "PostgreSQL", "Redis", "Docker", "AWS"],
        ),
        ProjectEntry(
            name="AI-Powered Content Analyzer",
            url="https://content-analyzer.demo.com",
            github_url="https://github.com/user/content-analyzer",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 3, 31),
            default_description="Machine learning application that analyzes content sentiment and provides optimization suggestions",
            default_achievements=[
                "Integrated OpenAI GPT API for advanced content analysis",
                "Achieved 85% accuracy in sentiment classification",
                "Processed 10,000+ articles with average analysis time under 2 seconds",
            ],
            technologies=["Python", "Scikit-learn", "Flask", "OpenAI API", "React"],
        ),
    ]

    # Create sample certifications
    certifications = [
        Certification(
            name="AWS Solutions Architect Associate",
            issuer="Amazon Web Services",
            issue_date=date(2023, 5, 15),
            expiry_date=date(2026, 5, 15),
            credential_id="AWS-SAA-2023-051567",
            url="https://aws.amazon.com/certification/",
            description="Demonstrates expertise in designing distributed systems on AWS",
        ),
        Certification(
            name="Professional Scrum Master I",
            issuer="Scrum.org",
            issue_date=date(2022, 11, 8),
            expiry_date=None,
            credential_id="PSM-I-2022-110834",
            url="https://scrum.org/",
            description="Validates knowledge of Scrum framework and agile principles",
        ),
    ]

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
        skills={
            "Technical Skills": technical_skills,
            "Soft Skills": interpersonal_skills,
            "Tools & Technologies": tools_skills,
        },
        default_summary="Experienced software engineer with 5+ years developing scalable web applications. Strong background in Python, JavaScript, and modern development practices with a focus on clean code and team collaboration.",
        summary_variations=summary_variations,
        work_experiences=work_experiences,
        projects=projects,
        certifications=certifications,
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
