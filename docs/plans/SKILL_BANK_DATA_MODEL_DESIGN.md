# 🏗️ Skill Bank Data Model Design

## 📊 Current Data Model Analysis

### **Existing Models Overview**
After reviewing both `app/data/models.py` and `app/data/resume_models.py`, here's the current data structure:

#### **UserProfileDB** (models.py:712-754)
```python
# Contact & Professional Info
first_name, last_name, email, phone
city, state, linkedin_url, portfolio_url
current_title, experience_years, skills (JSON), education, bio

# Job Preferences 
preferred_locations, preferred_job_types, preferred_remote_types
desired_salary_min, desired_salary_max
```

#### **SkillBankDB** (resume_models.py:345-367)  
```python
# Basic skill categorization
skills (JSON Dict[str, List[Skill]])
experience_keywords, industry_keywords, technical_keywords, soft_skills
auto_extracted_skills, skill_confidence
```

#### **Resume Models** (resume_models.py:79-241)
```python
ContactInfo, WorkExperience, Education, Skill, Project, Certification
ResumeSection, Resume (with all content sections)
```

## 🎯 Design Goals

1. **Eliminate Redundancy** - Single source of truth for each data type
2. **Maintain Compatibility** - Don't break existing resume system
3. **Enable Content Variations** - Support multiple versions of descriptions/content
4. **Preserve Data Integrity** - Maintain relationships between models
5. **Minimize Breaking Changes** - Extend existing models where possible

## 🔧 Enhanced Skill Bank Architecture

### **Core Design Principles**

1. **UserProfile = Contact Info Master** - Keep contact info in UserProfile, reference from Skill Bank
2. **SkillBank = Content & Skills Master** - All professional content and skills management
3. **Resume = Assembly Layer** - Assembles content from UserProfile + SkillBank
4. **Content Variations Pattern** - Reusable system for different versions of content

### **Data Flow Architecture**
```
UserProfile (Contact + Preferences) ←→ SkillBank (Content + Skills) → Resume (Assembly)
                ↓                                    ↓                        ↓
         [Contact Fields]                    [Content Variations]      [Final Output]
```

## 📋 Enhanced Models Design

### **1. Extended SkillBankDB** (Primary Enhancement)
```python
class SkillBankDB(Base):
    __tablename__ = "skill_banks"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # SKILLS MANAGEMENT (Enhanced)
    skills = Column(JSON)  # Dict[category, List[EnhancedSkill]]
    skill_categories = Column(JSON)  # ["Technical", "Soft Skills", "Transferable"]
    
    # SUMMARY VARIATIONS
    default_summary = Column(Text)
    summary_variations = Column(JSON)  # List[SummaryVariation]
    
    # EXPERIENCE ENTRIES (Master Records)
    work_experiences = Column(JSON)  # List[ExperienceEntry]
    
    # EDUCATION ENTRIES (Master Records)  
    education_entries = Column(JSON)  # List[EducationEntry]
    
    # PROJECT ENTRIES (Master Records)
    projects = Column(JSON)  # List[ProjectEntry]
    
    # CERTIFICATIONS (Simple - no variations needed)
    certifications = Column(JSON)  # List[Certification]
    
    # CONTENT VARIATIONS (Related to experiences/education/projects)
    experience_content_variations = Column(JSON)  # Dict[experience_id, List[ContentVariation]]
    education_content_variations = Column(JSON)   # Dict[education_id, List[ContentVariation]]
    project_content_variations = Column(JSON)     # Dict[project_id, List[ContentVariation]]
    
    # AUTO-EXTRACTION & AI
    auto_extracted_skills = Column(JSON)
    skill_confidence = Column(JSON)  # Dict[skill_name, confidence_score]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserProfileDB", back_populates="skill_bank")
```

### **2. Content Variation Models** (New Pattern)

#### **Base ContentVariation Model**
```python
class ContentVariation(BaseModel):
    """Reusable content variation pattern"""
    
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
```

#### **Specific Content Models**
```python
class SummaryVariation(ContentVariation):
    """Professional summary variations"""
    tone: str = "professional"  # professional, creative, technical
    length: str = "standard"     # concise, standard, detailed

class ExperienceContentVariation(ContentVariation):
    """Work experience content variations"""
    experience_id: str  # Links to specific work experience
    focus_area: str     # "technical", "leadership", "results"
    achievements: List[str] = Field(default_factory=list)
    skills_highlighted: List[str] = Field(default_factory=list)
```

### **3. Enhanced Master Entry Models**

#### **ExperienceEntry** (Master Record)
```python
class ExperienceEntry(BaseModel):
    """Master work experience record"""
    
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
```

#### **EducationEntry** (Master Record)
```python
class EducationEntry(BaseModel):
    """Master education record"""
    
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
```

### **4. Enhanced Skill Model**
```python
class EnhancedSkill(BaseModel):
    """Enhanced skill with detailed metadata"""
    
    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE
    
    # Categorization
    category: str  # "Technical Skills", "Soft Skills", "Transferable Skills"
    subcategory: Optional[str] = None  # "Programming Languages", "Frameworks", etc.
    
    # Experience & Proficiency
    years_experience: Optional[int] = None
    proficiency_score: Optional[float] = None  # 0.0-1.0
    
    # Context & Usage
    description: Optional[str] = None  # User-written description
    keywords: List[str] = Field(default_factory=list)  # Related terms
    
    # Display & Organization
    is_featured: bool = False  # Should be prominently displayed
    display_order: int = 0
    
    # Metadata
    source: str = "manual"  # "manual", "extracted", "suggested"
    confidence: float = 1.0  # AI confidence if auto-extracted
    last_used: Optional[datetime] = None
    usage_count: int = 0
```

## 🔄 Data Migration Strategy

### **Phase 1: Extend Existing Tables** (Non-breaking)
1. Add new JSON columns to `SkillBankDB`
2. Keep existing columns for backward compatibility
3. Migrate data from `UserProfileDB.skills` to enhanced format

### **Phase 2: Populate Content Variations** (New functionality)
1. Create default content variations from existing resume data
2. Allow users to create additional variations
3. Link variations to master entries

### **Phase 3: Clean Up** (Future - after UI is stable)
1. Remove redundant fields once data is fully migrated
2. Optimize database queries and indexes
3. Archive old format fields

## 📊 Contact Info Consolidation Strategy

### **Single Source of Truth: UserProfileDB**
Keep all contact information in `UserProfileDB`:
```python
# UserProfileDB remains the master for:
first_name, last_name, email, phone
city, state, linkedin_url, portfolio_url
```

### **SkillBank References Contact**
```python
# SkillBank.get_contact_info() -> References UserProfile
def get_contact_info(self) -> ContactInfo:
    profile = self.user  # SQLAlchemy relationship
    return ContactInfo(
        full_name=f"{profile.first_name} {profile.last_name}".strip(),
        email=profile.email,
        phone=profile.phone,
        location=f"{profile.city}, {profile.state}" if profile.city else None,
        linkedin_url=profile.linkedin_url,
        portfolio_url=profile.portfolio_url,
    )
```

### **Resume Assembly**
```python
# Resume creation pulls from both sources
def create_resume_from_skill_bank(skill_bank: SkillBank, profile: UserProfile) -> Resume:
    return Resume(
        # Contact from UserProfile
        contact_info=skill_bank.get_contact_info(),
        
        # Content from SkillBank
        summary=skill_bank.get_summary_variation("default"),
        work_experience=skill_bank.get_experience_entries(),
        skills=skill_bank.get_skills(),
        # ... etc
    )
```

## 🔗 API Design Implications

### **Endpoint Structure**
```python
# Single comprehensive endpoint
GET  /api/skill-bank/{user_id}           # Get complete skill bank
PUT  /api/skill-bank/{user_id}           # Update skill bank

# Content variation management
POST /api/skill-bank/{user_id}/summaries/{variation_id}
POST /api/skill-bank/{user_id}/experience/{exp_id}/variations
POST /api/skill-bank/{user_id}/education/{edu_id}/variations

# Skills management
PUT  /api/skill-bank/{user_id}/skills    # Bulk update skills
POST /api/skill-bank/{user_id}/skills    # Add single skill

# Contact info remains in user profile
GET  /api/users/{user_id}                # Includes contact info
PUT  /api/users/{user_id}                # Updates contact info
```

## 💡 Key Benefits of This Design

1. **No Redundancy** - Contact info stays in UserProfile, content in SkillBank
2. **Flexible Content** - Multiple variations for different job types
3. **Backward Compatible** - Existing Resume system still works
4. **Scalable** - Can add new content types easily
5. **Performance Optimized** - Single JSON operations instead of multiple tables
6. **AI-Friendly** - Easy to extract and suggest content variations

## 🎯 Implementation Priority

1. **Week 1-2**: Extend SkillBankDB model with new JSON fields
2. **Week 2**: Create Pydantic models and validation
3. **Week 3**: Build API endpoints for content management
4. **Week 4**: Create data migration scripts
5. **Week 5**: Update frontend interfaces

This design maintains all existing functionality while adding powerful new content variation capabilities without creating redundant database tables or models.
