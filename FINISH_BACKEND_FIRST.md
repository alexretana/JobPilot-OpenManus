# FINISH_BACKEND_FIRST.md

## Database Refactoring & Normalization Checklist

This document outlines the detailed steps to refactor the JobPilot-OpenManus database schema to eliminate redundancies,
improve relationships, and create a more normalized structure.

---

## Phase 1: Company Data Normalization

### Task 1.1: Update CompanyInfoDB Model

**File**: `app/data/models.py`

**Changes Required**:

```python
class CompanyInfoDB(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, index=True)
    normalized_name = Column(String, nullable=False, index=True)  # ADD: For fuzzy matching
    domain = Column(String, unique=True, index=True)  # ADD: Company domain for matching
    industry = Column(String, index=True)
    size = Column(String)
    size_category = Column(SQLEnum(CompanySizeCategory), index=True)  # ADD: Enum version
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

    # ADD: Unique constraint on normalized name + domain
    __table_args__ = (
        UniqueConstraint('normalized_name', 'domain', name='unique_company_identity'),
        Index('idx_company_name_domain', 'name', 'domain'),
    )
```

### Task 1.2: Update JobListingDB Model

**File**: `app/data/models.py`

**Changes Required**:

1. **Add company_id foreign key**:

```python
class JobListingDB(Base):
    # ADD: Foreign key to companies table
    company_id = Column(String, ForeignKey('companies.id'), nullable=False, index=True)

    # REMOVE these redundant fields:
    # company = Column(String, nullable=False)  # DELETE
    # company_size = Column(String)  # DELETE - now in company table
    # industry = Column(String)  # DELETE - now in company table
    # company_url = Column(String)  # DELETE - now in company table as 'website'

    # ADD: Relationship to company
    company = relationship("CompanyInfoDB", back_populates="job_listings")
```

2. **Update existing fields**:

```python
    # Keep all other existing fields unchanged
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    location = Column(String)  # Job location (can differ from company HQ)
    # ... rest of fields remain the same
```

### Task 1.3: Create Company Matching Utility

**File**: `app/data/company_matcher.py` (NEW FILE)

**Purpose**: Helper functions to match and normalize company data

**Content**:

```python
"""
Company Matching and Normalization Utilities
"""
import re
from typing import Optional, Tuple
from difflib import SequenceMatcher

def normalize_company_name(name: str) -> str:
    """Normalize company name for matching"""
    # Remove common suffixes/prefixes
    name = re.sub(r'\b(Inc|LLC|Corp|Corporation|Ltd|Limited|Co)\b\.?', '', name, flags=re.IGNORECASE)
    # Remove extra whitespace and convert to lowercase
    return ' '.join(name.split()).lower().strip()

def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from company website URL"""
    if not url:
        return None
    # Implementation to extract domain
    pass

def find_existing_company(name: str, domain: str = None) -> Optional[str]:
    """Find existing company ID by name/domain matching"""
    # Implementation to search existing companies
    pass

def similarity_score(str1: str, str2: str) -> float:
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, str1, str2).ratio()
```

### Task 1.4: Update JobListing Pydantic Model

**File**: `app/data/models.py`

**Changes**:

```python
class JobListing(JobListingBase):
    # ADD: Company relationship field
    company_id: Optional[UUID] = None
    company_name: Optional[str] = None  # For display purposes, populated from relationship

    # REMOVE from JobListingBase:
    # company_size: Optional[str] = None  # DELETE - now in company
    # industry: Optional[str] = None  # DELETE - now in company
    # company_url: Optional[str] = None  # DELETE - now in company as website

    # Keep existing company field for backward compatibility during migration
    company: str  # Will be populated from company.name
```

---

## Phase 2: User-Job Interaction Consolidation

### Task 2.1: Create New JobUserInteractionDB Model

**File**: `app/data/models.py`

**Add new enum**:

```python
class InteractionType(str, Enum):
    VIEWED = "viewed"
    SAVED = "saved"
    APPLIED = "applied"
    HIDDEN = "hidden"
    REJECTED_BY_USER = "rejected_by_user"
```

**Add new model**:

```python
class JobUserInteractionDB(Base):
    """Consolidated user-job interactions (replaces JobApplicationDB + SavedJobDB)"""
    __tablename__ = "job_user_interactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey('user_profiles.id'), nullable=False, index=True)
    job_id = Column(String, ForeignKey('job_listings.id'), nullable=False, index=True)

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
    interaction_data = Column(JSON, default=dict)  # Flexible storage for interaction-specific data

    # Tracking
    first_interaction = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    interaction_count = Column(Integer, default=1)  # How many times user interacted

    # Job snapshot (preserve job details at time of key interactions)
    job_snapshot = Column(JSON)  # Store job details when applied/saved

    # Relationships
    user = relationship("UserProfileDB", back_populates="job_interactions")
    job = relationship("JobListingDB", back_populates="user_interactions")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'job_id', 'interaction_type', name='unique_user_job_interaction'),
        Index('idx_user_interaction_type_date', 'user_id', 'interaction_type', 'last_interaction'),
        Index('idx_job_interaction_type', 'job_id', 'interaction_type'),
        # Ensure application fields are set when interaction_type is APPLIED
        CheckConstraint(
            "interaction_type != 'applied' OR application_status IS NOT NULL",
            name="applied_interactions_need_status"
        ),
        # Ensure saved_date is set when interaction_type is SAVED
        CheckConstraint(
            "interaction_type != 'saved' OR saved_date IS NOT NULL",
            name="saved_interactions_need_date"
        ),
    )
```

### Task 2.2: Update UserProfileDB Relationships

**File**: `app/data/models.py`

**Changes**:

```python
class UserProfileDB(Base):
    # UPDATE: Replace applications relationship
    # applications = relationship("JobApplicationDB", back_populates="user_profile")  # DELETE

    # ADD: New consolidated relationship
    job_interactions = relationship("JobUserInteractionDB", back_populates="user")

    # Keep other relationships unchanged
    resumes = relationship("ResumeDB", back_populates="user")
    skill_bank = relationship("EnhancedSkillBankDB", back_populates="user", uselist=False)
```

### Task 2.3: Update JobListingDB Relationships

**File**: `app/data/models.py`

**Changes**:

```python
class JobListingDB(Base):
    # UPDATE: Replace applications relationship
    # applications = relationship("JobApplicationDB", back_populates="job")  # DELETE

    # ADD: New consolidated relationship
    user_interactions = relationship("JobUserInteractionDB", back_populates="job")

    # Keep other relationships unchanged
    source_listings = relationship("JobSourceListingDB", back_populates="job")
    embeddings = relationship("JobEmbeddingDB", back_populates="job")
```

### Task 2.4: Create Migration for Existing Data

**File**: `app/data/migrations/consolidate_interactions.py` (NEW FILE)

**Purpose**: Migrate existing JobApplicationDB and SavedJobDB data to new structure

**Content**:

```python
"""
Migration script to consolidate job applications and saved jobs
"""
from sqlalchemy.orm import Session
from app.data.models import JobApplicationDB, SavedJobDB, JobUserInteractionDB, InteractionType, ApplicationStatus

def migrate_applications(session: Session):
    """Migrate existing applications to new interaction model"""
    applications = session.query(JobApplicationDB).all()

    for app in applications:
        interaction = JobUserInteractionDB(
            user_id=app.user_profile_id,
            job_id=app.job_id,
            interaction_type=InteractionType.APPLIED,
            application_status=app.status,
            applied_date=app.applied_date,
            response_date=app.response_date,
            resume_version=app.resume_version,
            cover_letter=app.cover_letter,
            notes=app.notes,
            follow_up_date=app.follow_up_date,
            interview_scheduled=app.interview_scheduled,
            first_interaction=app.created_at,
            last_interaction=app.updated_at,
        )
        session.add(interaction)

    session.commit()

def migrate_saved_jobs(session: Session):
    """Migrate existing saved jobs to new interaction model"""
    saved_jobs = session.query(SavedJobDB).all()

    for saved in saved_jobs:
        # Check if user also applied to this job
        existing_interaction = session.query(JobUserInteractionDB).filter(
            JobUserInteractionDB.user_id == saved.user_profile_id,
            JobUserInteractionDB.job_id == saved.job_id,
            JobUserInteractionDB.interaction_type == InteractionType.APPLIED
        ).first()

        if existing_interaction:
            # User both saved and applied - update existing record
            existing_interaction.saved_date = saved.saved_date
            existing_interaction.tags = saved.tags
            if saved.notes and not existing_interaction.notes:
                existing_interaction.notes = saved.notes
        else:
            # Create new saved interaction
            interaction = JobUserInteractionDB(
                user_id=saved.user_profile_id,
                job_id=saved.job_id,
                interaction_type=InteractionType.SAVED,
                saved_date=saved.saved_date,
                tags=saved.tags,
                notes=saved.notes,
                first_interaction=saved.saved_date,
                last_interaction=saved.updated_at,
            )
            session.add(interaction)

    session.commit()
```

---

## Phase 3: Skills Data Cleanup

### Task 3.1: Remove Redundant Skills Fields from UserProfileDB

**File**: `app/data/models.py`

**Changes**:

```python
class UserProfileDB(Base):
    # REMOVE: Redundant skills field
    # skills = Column(JSON)  # DELETE - use skill_bank relationship only

    # Keep all other fields unchanged
    # Personal information, location, professional links, job preferences
    # Only remove the skills field
```

### Task 3.2: Clean Up EnhancedSkillBankDB Redundancies

**File**: `app/data/skill_bank_models.py`

**Changes**:

```python
class EnhancedSkillBankDB(Base):
    __tablename__ = "skill_banks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)

    # KEEP: Core skill management
    skills = Column(JSON, default=dict)  # Dict[category, List[EnhancedSkill]]
    skill_categories = Column(JSON, default=list)

    # KEEP: Summary variations
    default_summary = Column(Text)
    summary_variations = Column(JSON, default=list)

    # KEEP: Master records
    work_experiences = Column(JSON, default=list)
    education_entries = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    certifications = Column(JSON, default=list)

    # KEEP: Content variations
    experience_content_variations = Column(JSON, default=dict)
    education_content_variations = Column(JSON, default=dict)
    project_content_variations = Column(JSON, default=dict)

    # REMOVE: Redundant legacy fields
    # experience_keywords = Column(JSON, default=list)  # DELETE - overlaps with skills
    # industry_keywords = Column(JSON, default=list)    # DELETE - overlaps with skills
    # technical_keywords = Column(JSON, default=list)   # DELETE - overlaps with skills
    # soft_skills = Column(JSON, default=list)          # DELETE - overlaps with skills
    # auto_extracted_skills = Column(JSON, default=list) # DELETE - use skills with source=EXTRACTED
    # skill_confidence = Column(JSON, default=dict)     # DELETE - use confidence field in EnhancedSkill

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserProfileDB", back_populates="skill_bank")
```

### Task 3.3: Add Computed Properties for Legacy Compatibility

**STATUS: SKIPPED**

**Reason**: Not needed in development mode with only mock data. No existing production systems require backward
compatibility. We'll implement the enhanced skills system directly without legacy property bridges.

**Note**: If needed later, computed properties can be added for API backward compatibility, but currently unnecessary.

### Task 3.4: Update Skill Migration Utilities

**File**: `app/data/skill_bank_models.py`

**Update the migration functions**:

```python
# REMOVE: convert_skill_list_to_enhanced function (if exists)
# UPDATE: create_default_skill_bank to not use redundant fields

def create_default_skill_bank(user_id: str) -> SkillBank:
    """Create a default skill bank for a new user"""
    return SkillBank(
        user_id=user_id,
        skills={
            "Technical Skills": [],
            "Soft Skills": [],
            "Tools & Platforms": [],
        },
        skill_categories=["Technical Skills", "Soft Skills", "Tools & Platforms"],
        summary_variations=[],
        work_experiences=[],
        education_entries=[],
        projects=[],
        certifications=[],
        experience_content_variations={},
        education_content_variations={},
        project_content_variations={},
        # REMOVE: All the legacy keyword fields
    )
```

---

## Phase 4: Resume Relationship Simplification

### Task 4.1: Simplify ResumeDB Foreign Key Relationships

**File**: `app/data/resume_models.py`

**Changes**:

```python
class ResumeDB(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    title = Column(String, nullable=False)
    resume_type = Column(String, nullable=False, default="base")
    status = Column(String, nullable=False, default="draft")

    # ... keep all content fields unchanged ...

    # SIMPLIFY: Foreign key relationships
    template_id = Column(String, ForeignKey("resume_templates.id"))
    parent_resume_id = Column(String, ForeignKey("resumes.id"))  # For versions/tailoring
    target_job_id = Column(String, ForeignKey("job_listings.id"))  # If tailored for specific job

    # REMOVE: Redundant fields
    # based_on_resume_id = Column(String, ForeignKey("resumes.id"))  # DELETE - redundant with parent_resume_id
    # job_id = Column(String, ForeignKey("job_listings.id"))  # DELETE - redundant with target_job_id

    # ... keep analysis and version control fields ...

    # IMPROVE: Relationships with better back_populates
    user = relationship("UserProfileDB", back_populates="resumes")
    template = relationship("ResumeTemplateDB", back_populates="resumes")
    parent_resume = relationship("ResumeDB", remote_side=[id], back_populates="child_resumes")
    child_resumes = relationship("ResumeDB", back_populates="parent_resume")
    target_job = relationship("JobListingDB", back_populates="tailored_resumes")
    generations = relationship("ResumeGenerationDB", back_populates="resume")
```

### Task 4.2: Add Missing Back References

**File**: `app/data/models.py`

**Add to JobListingDB**:

```python
class JobListingDB(Base):
    # ADD: Back reference to tailored resumes
    tailored_resumes = relationship("ResumeDB", back_populates="target_job")
```

**File**: `app/data/resume_models.py`

**Add to ResumeTemplateDB**:

```python
class ResumeTemplateDB(Base):
    # ADD: Back reference to resumes using this template
    resumes = relationship("ResumeDB", back_populates="template")
```

### Task 4.3: Update Resume Pydantic Model

**File**: `app/data/resume_models.py`

**Changes**:

```python
class Resume(BaseModel):
    # ... existing fields ...

    # RENAME: For clarity
    parent_resume_id: Optional[str] = None  # RENAME from based_on_resume_id
    target_job_id: Optional[str] = None     # RENAME from job_id

    # REMOVE: Redundant field
    # based_on_resume_id: Optional[str] = None  # DELETE
    # job_id: Optional[str] = None              # DELETE
```

### Task 4.4: Add Resume Relationship Validation

**File**: `app/data/resume_models.py`

**Add validation**:

```python
class ResumeDB(Base):
    # ... existing model ...

    # ADD: Table constraints for data integrity
    __table_args__ = (
        # Prevent circular parent relationships
        CheckConstraint('parent_resume_id != id', name='no_self_parent'),
        # Ensure tailored resumes have a parent or are base types
        CheckConstraint(
            "resume_type = 'base' OR parent_resume_id IS NOT NULL",
            name='tailored_resumes_need_parent'
        ),
        # Ensure template resumes don't have parents or targets
        CheckConstraint(
            "resume_type != 'template' OR (parent_resume_id IS NULL AND target_job_id IS NULL)",
            name='templates_are_standalone'
        ),
        # Index for common queries
        Index('idx_user_resume_type_status', 'user_id', 'resume_type', 'status'),
        Index('idx_parent_resume', 'parent_resume_id'),
        Index('idx_target_job', 'target_job_id'),
    )
```

---

## Phase 5: Database Constraints & Integrity

### Task 5.1: Add Missing Indexes for Performance

**File**: `app/data/models.py`

**Add to each model**:

```python
class JobListingDB(Base):
    # ADD: Performance indexes
    __table_args__ = (
        Index('idx_job_company_status', 'company_id', 'status'),
        Index('idx_job_location_type', 'location', 'job_type'),
        Index('idx_job_posted_date', 'posted_date'),
        Index('idx_job_salary_range', 'salary_min', 'salary_max'),
        Index('idx_job_experience_level', 'experience_level'),
        Index('idx_job_remote_type', 'remote_type'),
        Index('idx_job_created_status', 'created_at', 'status'),
    )

class JobUserInteractionDB(Base):
    # Indexes already defined in Task 2.1
    pass

class UserProfileDB(Base):
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_location', 'city', 'state'),
        Index('idx_user_created', 'created_at'),
    )

class EnhancedSkillBankDB(Base):
    __table_args__ = (
        Index('idx_skillbank_user', 'user_id'),
        Index('idx_skillbank_updated', 'updated_at'),
    )
```

### Task 5.2: Add Data Validation Constraints

**File**: `app/data/models.py`

**Add validation**:

```python
# ADD: Validation constraints across models

class JobListingDB(Base):
    __table_args__ = (
        # ... existing indexes ...

        # ADD: Data validation constraints
        CheckConstraint('salary_min >= 0', name='salary_min_positive'),
        CheckConstraint('salary_max >= salary_min', name='salary_range_valid'),
        CheckConstraint("job_url ~ '^https?://' OR job_url IS NULL", name='job_url_format'),
        CheckConstraint("application_url ~ '^https?://' OR application_url IS NULL", name='app_url_format'),
        CheckConstraint('LENGTH(title) >= 3', name='title_min_length'),
        CheckConstraint('LENGTH(title) <= 200', name='title_max_length'),
    )

class UserProfileDB(Base):
    __table_args__ = (
        # ... existing indexes ...

        # ADD: Data validation
        CheckConstraint("email ~ '^[^@]+@[^@]+\.[^@]+$' OR email IS NULL", name='email_format'),
        CheckConstraint("linkedin_url ~ '^https?://.*linkedin\.com' OR linkedin_url IS NULL", name='linkedin_url_format'),
        CheckConstraint('experience_years >= 0 OR experience_years IS NULL', name='experience_positive'),
        CheckConstraint('desired_salary_min >= 0 OR desired_salary_min IS NULL', name='desired_salary_min_positive'),
        CheckConstraint('desired_salary_max >= desired_salary_min OR desired_salary_max IS NULL OR desired_salary_min IS NULL', name='desired_salary_range_valid'),
    )

class CompanyInfoDB(Base):
    __table_args__ = (
        # ... existing constraints ...

        # ADD: More validation
        CheckConstraint('LENGTH(name) >= 1', name='company_name_not_empty'),
        CheckConstraint('LENGTH(name) <= 200', name='company_name_max_length'),
        CheckConstraint("website ~ '^https?://' OR website IS NULL", name='website_url_format'),
        CheckConstraint('founded_year >= 1800 OR founded_year IS NULL', name='founded_year_reasonable'),
        CheckConstraint('founded_year <= EXTRACT(YEAR FROM NOW()) OR founded_year IS NULL', name='founded_year_not_future'),
    )
```

### Task 5.3: Add Cascade Delete Rules

**File**: `app/data/models.py`

**Update foreign key relationships**:

```python
class JobUserInteractionDB(Base):
    # UPDATE: Add cascade rules
    user_id = Column(String, ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False)
    job_id = Column(String, ForeignKey('job_listings.id', ondelete='CASCADE'), nullable=False)

class JobSourceListingDB(Base):
    # UPDATE: Add cascade rules
    job_id = Column(String, ForeignKey('job_listings.id', ondelete='CASCADE'), nullable=False)
    source_id = Column(String, ForeignKey('job_sources.id', ondelete='CASCADE'), nullable=False)

class JobEmbeddingDB(Base):
    # UPDATE: Add cascade rules
    job_id = Column(String, ForeignKey('job_listings.id', ondelete='CASCADE'), nullable=False)

class ResumeDB(Base):
    # UPDATE: Add appropriate cascade rules
    user_id = Column(String, ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False)
    parent_resume_id = Column(String, ForeignKey('resumes.id', ondelete='SET NULL'))
    target_job_id = Column(String, ForeignKey('job_listings.id', ondelete='SET NULL'))
    template_id = Column(String, ForeignKey('resume_templates.id', ondelete='SET NULL'))

class EnhancedSkillBankDB(Base):
    # UPDATE: Add cascade rule
    user_id = Column(String, ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False)
```

---

## Phase 6: Repository Layer Updates

### Task 6.1: Update JobRepository Methods

**File**: `app/data/database.py`

**Changes Required**:

```python
class JobRepository:
    # UPDATE: search_jobs method to use company relationship
    def search_jobs(self, ...):
        # CHANGE: Join with CompanyInfoDB instead of filtering by company string
        query_obj = session.query(JobListingDB).join(CompanyInfoDB).filter(...)

        # UPDATE: Company filter
        if companies:
            query_obj = query_obj.filter(CompanyInfoDB.name.in_(companies))

    # UPDATE: get_jobs_by_company method
    def get_jobs_by_company(self, company: str, limit: int = 20):
        # CHANGE: Use company relationship
        jobs_db = (
            session.query(JobListingDB)
            .join(CompanyInfoDB)
            .filter(CompanyInfoDB.name.ilike(f"%{company}%"))
            .filter(JobListingDB.status == JobStatus.ACTIVE)
            .order_by(desc(JobListingDB.created_at))
            .limit(limit)
            .all()
        )

    # ADD: New method for company management
    def get_or_create_company(self, name: str, domain: str = None) -> CompanyInfoDB:
        """Get existing company or create new one"""
        pass
```

### Task 6.2: Create JobUserInteractionRepository

**File**: `app/data/interaction_repository.py` (NEW FILE)

**Purpose**: Replace separate JobApplication and SavedJob repositories

**Content**:

```python
"""
Job User Interaction Repository
Manages all user-job interactions (saved, applied, viewed, etc.)
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.data.models import JobUserInteractionDB, InteractionType, ApplicationStatus

class JobUserInteractionRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_job(self, user_id: str, job_id: str, notes: str = None, tags: List[str] = None) -> JobUserInteractionDB:
        """Save a job for later"""
        pass

    def apply_to_job(self, user_id: str, job_id: str, resume_version: str = None, cover_letter: str = None) -> JobUserInteractionDB:
        """Record job application"""
        pass

    def get_user_interactions(self, user_id: str, interaction_type: InteractionType = None) -> List[JobUserInteractionDB]:
        """Get user's job interactions"""
        pass

    def get_saved_jobs(self, user_id: str) -> List[JobUserInteractionDB]:
        """Get user's saved jobs"""
        return self.get_user_interactions(user_id, InteractionType.SAVED)

    def get_applications(self, user_id: str, status: ApplicationStatus = None) -> List[JobUserInteractionDB]:
        """Get user's job applications"""
        interactions = self.get_user_interactions(user_id, InteractionType.APPLIED)
        if status:
            interactions = [i for i in interactions if i.application_status == status]
        return interactions

    def update_application_status(self, interaction_id: str, status: ApplicationStatus) -> bool:
        """Update application status"""
        pass

    def record_job_view(self, user_id: str, job_id: str) -> JobUserInteractionDB:
        """Record that user viewed a job"""
        pass

    def hide_job(self, user_id: str, job_id: str, reason: str = None) -> JobUserInteractionDB:
        """Hide job from user's view"""
        pass
```

### Task 6.3: Update get_database_manager Function

**File**: `app/data/database.py`

**Add new repository getters**:

```python
# ADD: New global repository instances
interaction_repo = None
company_repo = None

def initialize_database(database_url: str = None):
    global db_manager, job_repo, user_repo, interaction_repo, company_repo, resume_repo

    db_manager = DatabaseManager(database_url)
    job_repo = JobRepository(db_manager)
    user_repo = UserRepository(db_manager)
    interaction_repo = JobUserInteractionRepository(db_manager)  # NEW
    company_repo = CompanyRepository(db_manager)  # NEW
    resume_repo = ResumeRepository(db_manager)

# ADD: New getter functions
def get_interaction_repository() -> JobUserInteractionRepository:
    global interaction_repo
    if interaction_repo is None:
        initialize_database()
    return interaction_repo

def get_company_repository() -> CompanyRepository:
    global company_repo
    if company_repo is None:
        initialize_database()
    return company_repo
```

### Task 6.4: Create CompanyRepository

**File**: `app/data/company_repository.py` (NEW FILE)

**Content**:

```python
"""
Company Repository
Manages company data and matching
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.data.models import CompanyInfoDB
from app.data.company_matcher import normalize_company_name, extract_domain_from_url

class CompanyRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_or_create_company(self, name: str, website: str = None, **kwargs) -> CompanyInfoDB:
        """Get existing company or create new one with matching"""
        with self.db_manager.get_session() as session:
            normalized_name = normalize_company_name(name)
            domain = extract_domain_from_url(website) if website else None

            # Try to find existing company
            existing = self._find_matching_company(session, normalized_name, domain)
            if existing:
                return existing

            # Create new company
            company = CompanyInfoDB(
                name=name,
                normalized_name=normalized_name,
                domain=domain,
                website=website,
                **kwargs
            )
            session.add(company)
            session.commit()
            session.refresh(company)
            return company

    def _find_matching_company(self, session: Session, normalized_name: str, domain: str = None) -> Optional[CompanyInfoDB]:
        """Find matching company by name and domain"""
        pass

    def search_companies(self, query: str, limit: int = 10) -> List[CompanyInfoDB]:
        """Search companies by name"""
        pass
```

---

## Phase 7: Update Mock Data Generator

### Task 7.1: Update MockDataGenerator Class

**File**: `app/data/mock_data_generator.py`

**Major changes required**:

1. **Remove redundant skill generation**:

```python
class MockDataGenerator:
    # UPDATE: Remove methods that create redundant data
    # REMOVE: Any code that sets UserProfile.skills
    # REMOVE: Any code that sets legacy skill bank fields

    def create_user_profile(self, user_data: Dict[str, Any]) -> str:
        # UPDATE: Remove skills field assignment
        user_profile = UserProfileDB(
            # ... other fields ...
            # skills=[],  # DELETE - don't set this field
        )
```

2. **Update company creation**:

```python
    async def create_comprehensive_skill_bank(self, user_id: str, role: str = "developer") -> SkillBank:
        # UPDATE: Don't set redundant legacy fields
        skill_bank = await self.skill_bank_repo.get_or_create_skill_bank(user_id)

        # Only add skills to the main skills dict
        # Don't set experience_keywords, technical_keywords, etc.
```

3. **Add company data generation**:

```python
    def create_companies(self) -> List[str]:
        """Create sample companies with proper normalization"""
        companies_data = [
            {
                "name": "TechFlow Solutions",
                "normalized_name": "techflow solutions",  # ADD
                "domain": "techflowsolutions.com",  # ADD
                "industry": "Software Development",
                "size": "201-500 employees",
                "size_category": CompanySizeCategory.MEDIUM,  # ADD
                "location": "San Francisco, CA",
                "website": "https://techflowsolutions.com",
                "founded_year": 2015,  # ADD
                # ... rest of company data
            },
            # ... more companies
        ]

        company_ids = []
        with self._get_session() as session:
            for company_data in companies_data:
                company = CompanyInfoDB(**company_data)
                session.add(company)
                session.flush()
                company_ids.append(company.id)
            session.commit()

        return company_ids
```

4. **Update job creation to use company_id**:

```python
    def create_jobs(self, company_ids: List[str]) -> List[str]:
        """Create sample jobs linked to companies"""
        # UPDATE: Use company_id instead of company name string
        job_data = {
            "title": "Senior Software Engineer",
            "company_id": random.choice(company_ids),  # ADD
            # "company": "TechFlow Solutions",  # REMOVE
            # ... rest of job data
        }
```

5. **Update interaction creation**:

```python
    def create_job_interactions(self, user_ids: List[str], job_ids: List[str]) -> List[str]:
        """Create sample job interactions (saved/applied)"""
        interactions = []

        for user_id in user_ids:
            # Create some saved jobs
            saved_jobs = random.sample(job_ids, random.randint(2, 5))
            for job_id in saved_jobs:
                interaction = JobUserInteractionDB(
                    user_id=user_id,
                    job_id=job_id,
                    interaction_type=InteractionType.SAVED,
                    saved_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    notes=random.choice(["Interesting opportunity", "Good benefits", "Remote friendly"]),
                    tags=random.sample(["remote", "startup", "growth", "benefits"], random.randint(1, 3)),
                )
                interactions.append(interaction)

            # Create some applications
            applied_jobs = random.sample([j for j in job_ids if j not in saved_jobs], random.randint(1, 3))
            for job_id in applied_jobs:
                interaction = JobUserInteractionDB(
                    user_id=user_id,
                    job_id=job_id,
                    interaction_type=InteractionType.APPLIED,
                    application_status=random.choice(list(ApplicationStatus)),
                    applied_date=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                    resume_version="v1.0",
                )
                interactions.append(interaction)

        with self._get_session() as session:
            session.add_all(interactions)
            session.commit()

        return [i.id for i in interactions]
```

---

## Phase 8: Testing & Validation

### Task 8.1: Create Database Schema Validation Tests

**File**: `tests/test_database_schema.py` (NEW FILE)

**Purpose**: Validate all database changes work correctly

**Content Structure**:

```python
"""
Database Schema Validation Tests
Tests to ensure all database refactoring changes work correctly
"""
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.data.models import Base, JobListingDB, CompanyInfoDB, JobUserInteractionDB
from app.data.database import DatabaseManager

class TestDatabaseSchema:
    """Test database schema and relationships"""

    @pytest.fixture
    def db_manager(self):
        """Create test database"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return DatabaseManager("sqlite:///:memory:")

    def test_company_job_relationship(self, db_manager):
        """Test company-job relationship works"""
        # Create company
        # Create job with company_id
        # Verify relationship works both ways
        pass

    def test_job_user_interaction_constraints(self, db_manager):
        """Test interaction table constraints"""
        # Test unique constraint on user_id + job_id + interaction_type
        # Test application interactions require status
        # Test saved interactions require saved_date
        pass

    def test_skill_bank_cleanup(self, db_manager):
        """Test skill bank no longer has redundant fields"""
        # Verify legacy fields are removed
        # Test skill bank operations still work
        pass

    def test_resume_relationship_simplification(self, db_manager):
        """Test resume relationships are simplified"""
        # Test parent_resume_id works
        # Test target_job_id works
        # Verify redundant fields are removed
        pass

    def test_cascade_deletes(self, db_manager):
        """Test cascade delete rules work correctly"""
        # Test user deletion cascades properly
        # Test job deletion handles applications correctly
        pass

class TestDataIntegrity:
    """Test data validation constraints"""

    def test_job_listing_constraints(self, db_manager):
        """Test job listing validation"""
        # Test salary constraints
        # Test URL format validation
        # Test required field validation
        pass

    def test_company_constraints(self, db_manager):
        """Test company validation"""
        # Test name length constraints
        # Test URL format validation
        # Test unique constraints
        pass

    def test_interaction_constraints(self, db_manager):
        """Test interaction validation"""
        # Test interaction type requirements
        # Test unique constraints
        pass

class TestRepositoryOperations:
    """Test repository methods work with new schema"""

    def test_job_repository_company_integration(self, db_manager):
        """Test job repository works with company relationships"""
        # Test job creation with company
        # Test job search by company
        # Test company matching
        pass

    def test_interaction_repository_operations(self, db_manager):
        """Test new interaction repository"""
        # Test saving jobs
        # Test applying to jobs
        # Test getting user interactions
        pass

    def test_skill_bank_repository_cleanup(self, db_manager):
        """Test skill bank repository with cleaned up fields"""
        # Test skill operations work
        # Test legacy field access fails gracefully
        pass
```

### Task 8.2: Create Migration Validation Tests

**File**: `tests/test_data_migration.py` (NEW FILE)

**Purpose**: Test data migration from old to new structure

**Content Structure**:

```python
"""
Data Migration Validation Tests
"""
class TestDataMigration:
    def test_application_to_interaction_migration(self):
        """Test migrating applications to interactions"""
        # Create old-style application data
        # Run migration
        # Verify data is correctly migrated
        pass

    def test_saved_job_to_interaction_migration(self):
        """Test migrating saved jobs to interactions"""
        pass

    def test_company_data_migration(self):
        """Test migrating job company strings to company relationships"""
        pass

    def test_skill_data_migration(self):
        """Test skill data cleanup doesn't lose information"""
        pass
```

### Task 8.3: Create Integration Tests

**File**: `tests/test_database_integration.py` (NEW FILE)

**Purpose**: End-to-end testing of database operations

**Content Structure**:

```python
"""
Database Integration Tests
End-to-end testing of all database operations
"""
class TestDatabaseIntegration:
    def test_complete_user_workflow(self, db_manager):
        """Test complete user workflow with new schema"""
        # Create user
        # Create skill bank
        # Save jobs
        # Apply to jobs
        # Create resumes
        # Verify all relationships work
        pass

    def test_job_lifecycle_with_company(self, db_manager):
        """Test job lifecycle with company relationships"""
        # Create company
        # Create job
        # User interactions
        # Job updates
        # Company updates
        pass

    def test_performance_with_indexes(self, db_manager):
        """Test query performance with new indexes"""
        # Create large dataset
        # Run common queries
        # Measure performance
        pass
```

---

## Phase 9: Create Comprehensive Mock Data Generator

### Task 9.1: Create New generate_mock_data.py Script

**File**: `generate_mock_data.py` (NEW FILE in root directory)

**Purpose**: Generate comprehensive test data for all tables respecting relationships

**Content Structure**:

```python
"""
Comprehensive Mock Data Generator
Generates realistic test data for all JobPilot tables with proper relationships
"""
import random
import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from uuid import uuid4

from app.data.database import initialize_database, get_database_manager
from app.data.models import *
from app.data.skill_bank_models import *
from app.data.resume_models import *
from app.data.skill_bank_repository import SkillBankRepository

class ComprehensiveMockDataGenerator:
    """Generate comprehensive mock data with proper relationships"""

    def __init__(self):
        initialize_database()
        self.db_manager = get_database_manager()
        self.skill_bank_repo = SkillBankRepository(self.db_manager)

        # Storage for created IDs to maintain relationships
        self.company_ids = []
        self.user_ids = []
        self.job_ids = []
        self.resume_ids = []
        self.interaction_ids = []

    async def generate_all_data(self, num_users: int = 10, num_companies: int = 20, num_jobs: int = 100):
        """Generate complete dataset"""
        print("🏢 Creating companies...")
        await self.create_companies(num_companies)

        print("👥 Creating users...")
        await self.create_users(num_users)

        print("🏦 Creating skill banks...")
        await self.create_skill_banks()

        print("💼 Creating jobs...")
        await self.create_jobs(num_jobs)

        print("📄 Creating resumes...")
        await self.create_resumes()

        print("❤️ Creating job interactions...")
        await self.create_job_interactions()

        print("📊 Creating timeline events...")
        await self.create_timeline_events()

        print("🔗 Creating job sources and embeddings...")
        await self.create_job_metadata()

        print("✅ Mock data generation complete!")
        print(f"Created: {len(self.company_ids)} companies, {len(self.user_ids)} users, {len(self.job_ids)} jobs")

    async def create_companies(self, num_companies: int):
        """Create realistic company data"""
        company_templates = [
            {
                "name": "TechFlow Solutions",
                "industry": "Software Development",
                "size_category": CompanySizeCategory.MEDIUM,
                "founded_year": 2015,
                "description": "Leading provider of enterprise software solutions...",
            },
            # ... more company templates
        ]

        with self.db_manager.get_session() as session:
            for i in range(num_companies):
                template = random.choice(company_templates)
                company = CompanyInfoDB(
                    id=str(uuid4()),
                    name=f"{template['name']} {i}" if i > 0 else template['name'],
                    normalized_name=template['name'].lower(),
                    domain=f"{template['name'].lower().replace(' ', '')}.com",
                    industry=template['industry'],
                    size_category=template['size_category'],
                    founded_year=template['founded_year'] + random.randint(-10, 10),
                    description=template['description'],
                    website=f"https://{template['name'].lower().replace(' ', '')}.com",
                )
                session.add(company)
                self.company_ids.append(company.id)

            session.commit()

    async def create_users(self, num_users: int):
        """Create realistic user profiles"""
        # Implementation details...
        pass

    async def create_skill_banks(self):
        """Create skill banks for all users"""
        # Implementation details...
        pass

    async def create_jobs(self, num_jobs: int):
        """Create jobs linked to companies"""
        # Implementation details...
        pass

    async def create_resumes(self):
        """Create resumes for users"""
        # Implementation details...
        pass

    async def create_job_interactions(self):
        """Create job interactions (saved/applied)"""
        # Implementation details...
        pass

    async def create_timeline_events(self):
        """Create timeline events for interactions"""
        # Implementation details...
        pass

    async def create_job_metadata(self):
        """Create job sources, embeddings, etc."""
        # Implementation details...
        pass

async def main():
    """Run mock data generation"""
    generator = ComprehensiveMockDataGenerator()
    await generator.generate_all_data(
        num_users=20,
        num_companies=30,
        num_jobs=150
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Task 9.2: Implement Detailed Mock Data Methods

**Each method in the above class needs detailed implementation**

**Companies** (create realistic tech companies):

- Use industry-appropriate company names
- Generate realistic domains and websites
- Vary company sizes and industries
- Create proper founding years and descriptions

**Users** (create diverse user profiles):

- Generate realistic names and contact info
- Vary experience levels and locations
- Create appropriate job preferences
- Don't set skills field (use skill bank only)

**Skill Banks** (create role-appropriate skills):

- Generate skills based on user "role" (developer, designer, PM, etc.)
- Create summary variations
- Add work experience entries
- Add education and certifications
- Don't use legacy keyword fields

**Jobs** (create realistic job postings):

- Link to created companies via company_id
- Generate appropriate titles for company industries
- Create realistic requirements and descriptions
- Vary salary ranges, locations, and types
- Include skills requirements that match user skills

**Resumes** (create resume variations):

- Create base resumes for each user
- Create some tailored versions for specific jobs
- Link to skill bank data appropriately
- Use simplified relationships (parent_resume_id, target_job_id)

**Interactions** (create realistic user behavior):

- Users save 3-8 jobs each
- Users apply to 1-4 jobs each
- Some users both save and apply to same job
- Generate realistic application statuses and dates
- Add appropriate notes and tags

**Timeline Events** (create interaction history):

- Create events for each job interaction
- Add some interview events for applications
- Include follow-up events
- Generate realistic event dates and descriptions

**Job Metadata** (create supporting data):

- Create job sources (LinkedIn, Indeed, etc.)
- Link jobs to sources via JobSourceListingDB
- Generate some job embeddings
- Create deduplication records for some jobs

### Task 9.3: Add Data Validation and Reporting

**Add to generate_mock_data.py**:

```python
def validate_generated_data(self):
    """Validate all generated data is consistent"""
    with self.db_manager.get_session() as session:
        # Check all foreign key relationships
        # Verify no orphaned records
        # Check constraint compliance
        # Generate summary report
        pass

def generate_data_report(self):
    """Generate report of created data"""
    with self.db_manager.get_session() as session:
        stats = {
            'companies': session.query(CompanyInfoDB).count(),
            'users': session.query(UserProfileDB).count(),
            'jobs': session.query(JobListingDB).count(),
            'resumes': session.query(ResumeDB).count(),
            'interactions': session.query(JobUserInteractionDB).count(),
            'timeline_events': session.query(TimelineEventDB).count(),
            # ... more stats
        }

        print("\n📊 Data Generation Report:")
        for table, count in stats.items():
            print(f"  {table}: {count} records")

        return stats
```

---

## Phase 10: Final Validation & Documentation

### Task 10.1: Create Database Migration Script

**File**: `scripts/migrate_database_schema.py` (NEW FILE)

**Purpose**: Production-ready migration script

**Content Structure**:

```python
"""
Database Schema Migration Script
Migrates production database from old to new schema
"""
import logging
from sqlalchemy import create_engine
from app.data.database import DatabaseManager
from app.data.migrations.consolidate_interactions import migrate_applications, migrate_saved_jobs

def run_migration(database_url: str, dry_run: bool = True):
    """Run complete database migration"""
    # Step 1: Backup existing data
    # Step 2: Create new tables
    # Step 3: Migrate existing data
    # Step 4: Verify migration
    # Step 5: Drop old tables (if not dry_run)
    pass

if __name__ == "__main__":
    # Command line interface for migration
    pass
```

### Task 10.2: Update Documentation

**File**: `docs/database_schema.md` (NEW FILE)

**Purpose**: Document the new database schema

**Content**:

- Updated entity-relationship diagrams
- Table descriptions with all changes
- Relationship explanations
- Index documentation
- Constraint explanations

### Task 10.3: Create Performance Benchmark Tests

**File**: `tests/test_performance.py` (NEW FILE)

**Purpose**: Ensure new schema performs well

**Content**:

```python
"""
Performance Tests for New Database Schema
"""
def test_job_search_performance():
    """Test job search with company joins"""
    pass

def test_user_interaction_queries():
    """Test consolidated interaction queries"""
    pass

def test_skill_bank_operations():
    """Test skill bank operations performance"""
    pass
```

---

## Implementation Order & Checklist

### Phase 1: Company Normalization ✅

- [x] Task 1.1: Update CompanyInfoDB Model
- [x] Task 1.2: Update JobListingDB Model
- [x] Task 1.3: Create Company Matching Utility
- [x] Task 1.4: Update JobListing Pydantic Model

### Phase 2: User-Job Interaction Consolidation ✅

- [x] Task 2.1: Create New JobUserInteractionDB Model
- [x] Task 2.2: Update UserProfileDB Relationships
- [x] Task 2.3: Update JobListingDB Relationships
- [x] ~~Task 2.4: Create Migration for Existing Data~~ (Skipped - working with fresh mock data)

### Phase 3: Skills Data Cleanup ✅

- [x] Task 3.1: Remove Redundant Skills Fields from UserProfileDB
- [x] Task 3.2: Clean Up EnhancedSkillBankDB Redundancies
- [x] ~~Task 3.3: Add Computed Properties for Legacy Compatibility~~ (Skipped - working with fresh mock data)
- [x] Task 3.4: Update Skill Migration Utilities

### Phase 4: Resume Relationship Simplification ✅

- [x] Task 4.1: Simplify ResumeDB Foreign Key Relationships
- [x] Task 4.2: Add Missing Back References
- [x] Task 4.3: Update Resume Pydantic Model
- [x] Task 4.4: Add Resume Relationship Validation

### Phase 5: Database Constraints & Integrity ✅

- [x] Task 5.1: Add Missing Indexes for Performance
- [x] Task 5.2: Add Data Validation Constraints
- [x] Task 5.3: Add Cascade Delete Rules

### Phase 6: Repository Layer Updates ✅

- [ ] Task 6.1: Update JobRepository Methods
- [ ] Task 6.2: Create JobUserInteractionRepository
- [ ] Task 6.3: Update get_database_manager Function
- [ ] Task 6.4: Create CompanyRepository

### Phase 7: Update Mock Data Generator ✅

- [ ] Task 7.1: Update MockDataGenerator Class

### Phase 8: Testing & Validation ✅

- [ ] Task 8.1: Create Database Schema Validation Tests
- [ ] Task 8.2: Create Migration Validation Tests
- [ ] Task 8.3: Create Integration Tests

### Phase 9: Create Comprehensive Mock Data Generator ✅

- [ ] Task 9.1: Create New generate_mock_data.py Script
- [ ] Task 9.2: Implement Detailed Mock Data Methods
- [ ] Task 9.3: Add Data Validation and Reporting

### Phase 10: Final Validation & Documentation ✅

- [ ] Task 10.1: Create Database Migration Script
- [ ] Task 10.2: Update Documentation
- [ ] Task 10.3: Create Performance Benchmark Tests

---

## Success Criteria

Upon completion, the database should have:

1. **✅ Normalized Company Data**: No company information duplication
2. **✅ Consolidated Interactions**: Single table for all user-job interactions
3. **✅ Clean Skills Management**: No redundant skill fields
4. **✅ Simplified Resume Relationships**: Clear, non-redundant foreign keys
5. **✅ Proper Constraints**: Data validation and integrity constraints
6. **✅ Performance Indexes**: Strategic indexes for common queries
7. **✅ Working Repositories**: Updated repository methods for new schema
8. **✅ Comprehensive Tests**: Full test coverage for all changes
9. **✅ Mock Data Generation**: Script that creates realistic test data
10. **✅ Documentation**: Clear documentation of all changes

Each phase should be completed and tested before moving to the next phase to ensure no breaking changes are introduced.
