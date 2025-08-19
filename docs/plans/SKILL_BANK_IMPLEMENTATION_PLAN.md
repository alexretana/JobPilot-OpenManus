# 🏗️ Skill Bank Implementation Plan

## 📋 Overview

The **Skill Bank** is a comprehensive skill and content management system that will serve as the single source of truth for all user profile data. It will integrate seamlessly with the Resume Builder, allowing users to create and manage variations of their professional content.

## 🎯 Core Objectives

1. **Centralized Content Management** - Single source for all professional information
2. **Content Variations** - Support "main/variation/history" pattern for dynamic content
3. **Skill Categorization** - Enhanced skill management with types and experience levels
4. **Resume Integration** - Seamless data flow to Resume Builder sections
5. **Data Consolidation** - Eliminate duplication between UserProfile and Resume data

---

## 🗃️ **Backend Data Model Design**

### **Current State Analysis**

**Existing Models:**
- `UserProfileDB` - Basic profile info (name, email, phone, skills, preferences)
- `SkillBankDB` - Skills repository (skills, keywords, confidence)
- `ResumeDB` - Resume content (sections, projects, education, experience)

**Key Issues to Address:**
- Contact info scattered across UserProfile and Resume models
- Skills stored in multiple places (UserProfile.skills, SkillBankDB.skills, ResumeDB content)
- No content variation system for dynamic resume content
- Resume sections rebuild the same data repeatedly

### **Enhanced Data Model Architecture**

#### **1. Contact Information Consolidation**

```python
class ContactInfoDB(Base):
    """Centralized contact information"""
    __tablename__ = "contact_info"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Basic contact
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    
    # NEW: Location information
    city = Column(String)
    state = Column(String)
    country = Column(String, default="United States")
    
    # NEW: Professional links
    linkedin_url = Column(String)
    portfolio_url = Column(String)
    github_url = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_profile = relationship("UserProfileDB", back_populates="contact_info")
```

#### **2. Content Variation System**

**Base Content Variation Model:**
```python
class ContentVariationDB(Base):
    """Base model for content variations"""
    __tablename__ = "content_variations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Content details
    content_type = Column(String, nullable=False)  # summary, experience, education, project
    parent_id = Column(String, nullable=True)  # References parent entity (experience_id, etc.)
    
    # Variation metadata
    title = Column(String)  # User-defined title for the variation
    content = Column(Text, nullable=False)
    is_main = Column(Boolean, default=False)  # Is this the main/default version?
    usage_count = Column(Integer, default=0)  # Track how often it's used
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)
    
    # Relationships
    user_profile = relationship("UserProfileDB")
```

#### **3. Professional Experience Model**

```python
class ExperienceEntryDB(Base):
    """Professional experience entries"""
    __tablename__ = "experience_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Basic job information (single source of truth)
    job_title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    location = Column(String)
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)  # Null for current jobs
    is_current = Column(Boolean, default=False)
    
    # Order for display
    display_order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_profile = relationship("UserProfileDB")
    content_variations = relationship(
        "ContentVariationDB", 
        primaryjoin="and_(ExperienceEntryDB.id==foreign(ContentVariationDB.parent_id), ContentVariationDB.content_type=='experience')"
    )
```

#### **4. Education Model**

```python
class EducationEntryDB(Base):
    """Education entries"""
    __tablename__ = "education_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Basic education information
    institution_name = Column(String, nullable=False)
    degree_type = Column(String)  # Bachelor's, Master's, PhD, Certificate, etc.
    field_of_study = Column(String)
    location = Column(String)
    
    # Dates
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    graduation_date = Column(DateTime)
    is_current = Column(Boolean, default=False)
    
    # Additional details
    gpa = Column(String)
    honors = Column(String)
    
    # Order for display
    display_order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_profile = relationship("UserProfileDB")
    content_variations = relationship(
        "ContentVariationDB",
        primaryjoin="and_(EducationEntryDB.id==foreign(ContentVariationDB.parent_id), ContentVariationDB.content_type=='education')"
    )
```

#### **5. Projects Model**

```python
class ProjectEntryDB(Base):
    """Project entries"""
    __tablename__ = "project_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Project information
    project_name = Column(String, nullable=False)
    project_url = Column(String)
    repository_url = Column(String)
    
    # Dates
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_ongoing = Column(Boolean, default=False)
    
    # Technologies/Skills used (JSON array)
    technologies_used = Column(JSON, default=list)
    
    # Order for display
    display_order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_profile = relationship("UserProfileDB")
    content_variations = relationship(
        "ContentVariationDB",
        primaryjoin="and_(ProjectEntryDB.id==foreign(ContentVariationDB.parent_id), ContentVariationDB.content_type=='project')"
    )
```

#### **6. Enhanced Skills Model**

```python
class SkillType(str, Enum):
    HARD_SKILL = "hard_skill"
    SOFT_SKILL = "soft_skill"
    TRANSFERABLE_SKILL = "transferable_skill"

class SkillEntryDB(Base):
    """Enhanced skill entries"""
    __tablename__ = "skill_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Skill information
    skill_name = Column(String, nullable=False)
    skill_type = Column(SQLEnum(SkillType), nullable=False)
    
    # Experience details (optional)
    years_experience = Column(Integer)
    proficiency_level = Column(String)  # Beginner, Intermediate, Advanced, Expert
    
    # Description
    description = Column(Text)  # How it was used, context, achievements
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    # Display order
    display_order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_profile = relationship("UserProfileDB")
```

#### **7. Certificates Model**

```python
class CertificateEntryDB(Base):
    """Certificate entries"""
    __tablename__ = "certificate_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Certificate information
    certificate_name = Column(String, nullable=False)
    issuing_organization = Column(String, nullable=False)
    credential_id = Column(String)
    credential_url = Column(String)
    
    # Dates
    date_obtained = Column(DateTime)
    expiration_date = Column(DateTime)  # Null for non-expiring certificates
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Display order
    display_order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_profile = relationship("UserProfileDB")
```

#### **8. Enhanced SkillBankDB Model**

```python
class SkillBankDB(Base):
    """Enhanced Skills bank - aggregated view"""
    __tablename__ = "skill_banks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    # Summary variations (main summary is just is_main=True)
    # Individual skills are in SkillEntryDB
    
    # Auto-generated insights
    skill_summary = Column(JSON, default=dict)  # Aggregated skill metrics
    experience_summary = Column(JSON, default=dict)  # Years by category, etc.
    
    # AI-generated suggestions
    suggested_skills = Column(JSON, default=list)
    skill_gaps = Column(JSON, default=list)
    
    # Metadata
    last_analyzed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_profile = relationship("UserProfileDB", back_populates="skill_bank")
    summary_variations = relationship(
        "ContentVariationDB",
        primaryjoin="and_(SkillBankDB.user_profile_id==foreign(ContentVariationDB.user_profile_id), ContentVariationDB.content_type=='summary')"
    )
```

### **Updated UserProfileDB Model**

```python
class UserProfileDB(Base):
    """Updated user profile - focused on preferences and metadata"""
    __tablename__ = "user_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    
    # REMOVED: contact info (moved to ContactInfoDB)
    # REMOVED: skills (moved to SkillBankDB system)
    
    # Professional preferences only
    current_title = Column(String)  # This might move to ContactInfoDB too
    experience_years = Column(Integer)
    bio = Column(Text)  # Main professional bio
    
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
    contact_info = relationship("ContactInfoDB", back_populates="user_profile", uselist=False)
    skill_bank = relationship("SkillBankDB", back_populates="user_profile", uselist=False)
    experience_entries = relationship("ExperienceEntryDB", back_populates="user_profile")
    education_entries = relationship("EducationEntryDB", back_populates="user_profile")
    project_entries = relationship("ProjectEntryDB", back_populates="user_profile")
    skill_entries = relationship("SkillEntryDB", back_populates="user_profile")
    certificate_entries = relationship("CertificateEntryDB", back_populates="user_profile")
    applications = relationship("JobApplicationDB", back_populates="user_profile")
    resumes = relationship("ResumeDB", back_populates="user")
```

---

## 🔧 **Backend API Design**

### **API Endpoint Structure**

#### **1. Skill Bank Overview**
```
GET    /api/skill-bank/{user_id}           # Get complete skill bank
PUT    /api/skill-bank/{user_id}           # Update skill bank metadata
DELETE /api/skill-bank/{user_id}/reset     # Reset all skill bank data
```

#### **2. Contact Information**
```
GET    /api/skill-bank/{user_id}/contact           # Get contact info
PUT    /api/skill-bank/{user_id}/contact           # Update contact info
```

#### **3. Summary Management**
```
GET    /api/skill-bank/{user_id}/summaries         # Get all summary variations
POST   /api/skill-bank/{user_id}/summaries         # Create new summary variation
PUT    /api/skill-bank/{user_id}/summaries/{id}    # Update summary variation
DELETE /api/skill-bank/{user_id}/summaries/{id}    # Delete summary variation
POST   /api/skill-bank/{user_id}/summaries/{id}/set-main  # Set as main summary
```

#### **4. Experience Management**
```
GET    /api/skill-bank/{user_id}/experience                    # Get all experience entries
POST   /api/skill-bank/{user_id}/experience                    # Create experience entry
PUT    /api/skill-bank/{user_id}/experience/{id}               # Update experience entry
DELETE /api/skill-bank/{user_id}/experience/{id}               # Delete experience entry

# Experience content variations
GET    /api/skill-bank/{user_id}/experience/{id}/content       # Get content variations
POST   /api/skill-bank/{user_id}/experience/{id}/content       # Create content variation
PUT    /api/skill-bank/{user_id}/experience/{id}/content/{cid} # Update content variation
DELETE /api/skill-bank/{user_id}/experience/{id}/content/{cid} # Delete content variation
```

#### **5. Education Management**
```
GET    /api/skill-bank/{user_id}/education                     # Get all education entries
POST   /api/skill-bank/{user_id}/education                     # Create education entry
PUT    /api/skill-bank/{user_id}/education/{id}                # Update education entry
DELETE /api/skill-bank/{user_id}/education/{id}                # Delete education entry

# Education content variations
GET    /api/skill-bank/{user_id}/education/{id}/content        # Get content variations
POST   /api/skill-bank/{user_id}/education/{id}/content        # Create content variation
PUT    /api/skill-bank/{user_id}/education/{id}/content/{cid}  # Update content variation
DELETE /api/skill-bank/{user_id}/education/{id}/content/{cid}  # Delete content variation
```

#### **6. Projects Management**
```
GET    /api/skill-bank/{user_id}/projects                      # Get all project entries
POST   /api/skill-bank/{user_id}/projects                      # Create project entry
PUT    /api/skill-bank/{user_id}/projects/{id}                 # Update project entry
DELETE /api/skill-bank/{user_id}/projects/{id}                 # Delete project entry

# Project content variations
GET    /api/skill-bank/{user_id}/projects/{id}/content         # Get content variations
POST   /api/skill-bank/{user_id}/projects/{id}/content         # Create content variation
PUT    /api/skill-bank/{user_id}/projects/{id}/content/{cid}   # Update content variation
DELETE /api/skill-bank/{user_id}/projects/{id}/content/{cid}   # Delete content variation
```

#### **7. Skills Management**
```
GET    /api/skill-bank/{user_id}/skills                        # Get all skills
POST   /api/skill-bank/{user_id}/skills                        # Create skill entry
PUT    /api/skill-bank/{user_id}/skills/{id}                   # Update skill entry
DELETE /api/skill-bank/{user_id}/skills/{id}                   # Delete skill entry
POST   /api/skill-bank/{user_id}/skills/reorder                # Reorder skills
GET    /api/skill-bank/{user_id}/skills/by-type/{type}         # Get skills by type
```

#### **8. Certificates Management**
```
GET    /api/skill-bank/{user_id}/certificates                  # Get all certificates
POST   /api/skill-bank/{user_id}/certificates                  # Create certificate
PUT    /api/skill-bank/{user_id}/certificates/{id}             # Update certificate
DELETE /api/skill-bank/{user_id}/certificates/{id}             # Delete certificate
```

### **Repository Layer Implementation**

```python
class SkillBankRepository:
    """Repository for Skill Bank operations"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    # Contact Info
    async def get_contact_info(self, user_id: str) -> Optional[ContactInfo]:
        """Get user contact information"""
        
    async def update_contact_info(self, user_id: str, contact_data: ContactInfoUpdate) -> ContactInfo:
        """Update contact information"""
    
    # Summary Management
    async def get_summaries(self, user_id: str) -> List[ContentVariation]:
        """Get all summary variations"""
        
    async def create_summary_variation(self, user_id: str, content: str, title: str = None) -> ContentVariation:
        """Create new summary variation"""
        
    async def set_main_summary(self, user_id: str, variation_id: str) -> ContentVariation:
        """Set summary as main/default"""
    
    # Experience Management
    async def get_experience_entries(self, user_id: str) -> List[ExperienceEntry]:
        """Get all experience entries with main content"""
        
    async def create_experience_entry(self, user_id: str, experience_data: ExperienceEntryCreate) -> ExperienceEntry:
        """Create new experience entry"""
        
    async def get_experience_content_variations(self, user_id: str, experience_id: str) -> List[ContentVariation]:
        """Get content variations for experience entry"""
        
    # Skills Management
    async def get_skills_by_type(self, user_id: str, skill_type: SkillType = None) -> List[SkillEntry]:
        """Get skills, optionally filtered by type"""
        
    async def create_skill_entry(self, user_id: str, skill_data: SkillEntryCreate) -> SkillEntry:
        """Create new skill entry"""
        
    # Certificates Management
    async def get_certificates(self, user_id: str, include_expired: bool = True) -> List[CertificateEntry]:
        """Get certificates, optionally excluding expired ones"""
        
    # Utility Methods
    async def get_complete_skill_bank(self, user_id: str) -> SkillBank:
        """Get complete skill bank with all sections"""
        
    async def export_for_resume(self, user_id: str, sections: List[str] = None) -> Dict[str, Any]:
        """Export skill bank data formatted for resume creation"""
```

---

## 🖥️ **Frontend Architecture**

### **Service Layer (skillBankApi.ts)**

```typescript
// Types
interface ContactInfo {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  city?: string;
  state?: string;
  linkedinUrl?: string;
  portfolioUrl?: string;
  githubUrl?: string;
}

interface ContentVariation {
  id: string;
  title?: string;
  content: string;
  isMain: boolean;
  usageCount: number;
  createdAt: string;
  lastUsedAt?: string;
}

interface ExperienceEntry {
  id: string;
  jobTitle: string;
  companyName: string;
  location?: string;
  startDate: string;
  endDate?: string;
  isCurrent: boolean;
  displayOrder: number;
  mainContent?: string;  // The main content variation
  variations: ContentVariation[];
}

interface SkillEntry {
  id: string;
  skillName: string;
  skillType: 'hard_skill' | 'soft_skill' | 'transferable_skill';
  yearsExperience?: number;
  proficiencyLevel?: string;
  description?: string;
  displayOrder: number;
}

interface SkillBank {
  contactInfo: ContactInfo;
  summaries: ContentVariation[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  skills: SkillEntry[];
  certificates: CertificateEntry[];
}

class SkillBankApiService {
  private baseUrl = '/api/skill-bank';
  
  // Contact Info
  async getContactInfo(userId: string): Promise<ContactInfo> { /* ... */ }
  async updateContactInfo(userId: string, data: Partial<ContactInfo>): Promise<ContactInfo> { /* ... */ }
  
  // Summary Management
  async getSummaries(userId: string): Promise<ContentVariation[]> { /* ... */ }
  async createSummaryVariation(userId: string, content: string, title?: string): Promise<ContentVariation> { /* ... */ }
  async updateSummaryVariation(userId: string, variationId: string, updates: Partial<ContentVariation>): Promise<ContentVariation> { /* ... */ }
  async setMainSummary(userId: string, variationId: string): Promise<ContentVariation> { /* ... */ }
  
  // Experience Management
  async getExperienceEntries(userId: string): Promise<ExperienceEntry[]> { /* ... */ }
  async createExperienceEntry(userId: string, data: Omit<ExperienceEntry, 'id' | 'variations'>): Promise<ExperienceEntry> { /* ... */ }
  async getExperienceContentVariations(userId: string, experienceId: string): Promise<ContentVariation[]> { /* ... */ }
  async createExperienceContentVariation(userId: string, experienceId: string, content: string, title?: string): Promise<ContentVariation> { /* ... */ }
  
  // Skills Management
  async getSkills(userId: string, type?: string): Promise<SkillEntry[]> { /* ... */ }
  async createSkill(userId: string, skill: Omit<SkillEntry, 'id'>): Promise<SkillEntry> { /* ... */ }
  async updateSkill(userId: string, skillId: string, updates: Partial<SkillEntry>): Promise<SkillEntry> { /* ... */ }
  async deleteSkill(userId: string, skillId: string): Promise<void> { /* ... */ }
  
  // Certificates Management
  async getCertificates(userId: string): Promise<CertificateEntry[]> { /* ... */ }
  async createCertificate(userId: string, cert: Omit<CertificateEntry, 'id'>): Promise<CertificateEntry> { /* ... */ }
  
  // Complete Skill Bank
  async getCompleteSkillBank(userId: string): Promise<SkillBank> { /* ... */ }
  
  // Resume Integration
  async exportForResume(userId: string, sections?: string[]): Promise<Record<string, any>> { /* ... */ }
}

export const skillBankApi = new SkillBankApiService();
```

### **Component Architecture**

#### **Main Skill Bank Component**
```typescript
// SkillBank.tsx
const SkillBank: Component<{ userId: string }> = ({ userId }) => {
  const [activeTab, setActiveTab] = createSignal<SkillBankSection>('contact');
  const [skillBank, { refetch }] = createResource(() => skillBankApi.getCompleteSkillBank(userId));
  
  return (
    <div class="container mx-auto p-4">
      {/* Tabbed Navigation */}
      <div class="tabs tabs-boxed mb-6">
        <button class={`tab ${activeTab() === 'contact' ? 'tab-active' : ''}`} 
                onClick={() => setActiveTab('contact')}>
          Contact Info
        </button>
        <button class={`tab ${activeTab() === 'summaries' ? 'tab-active' : ''}`} 
                onClick={() => setActiveTab('summaries')}>
          Professional Summaries
        </button>
        <button class={`tab ${activeTab() === 'experience' ? 'tab-active' : ''}`} 
                onClick={() => setActiveTab('experience')}>
          Experience
        </button>
        <button class={`tab ${activeTab() === 'education' ? 'tab-active' : ''}`} 
                onClick={() => setActiveTab('education')}>
          Education
        </button>
        <button class={`tab ${activeTab() === 'projects' ? 'tab-active' : ''}`} 
                onClick={() => setActiveTab('projects')}>
          Projects
        </button>
        <button class={`tab ${activeTab() === 'skills' ? 'tab-active' : ''}`} 
                onClick={() => setActiveTab('skills')}>
          Skills
        </button>
        <button class={`tab ${activeTab() === 'certificates' ? 'tab-active' : ''}`} 
                onClick={() => setActiveTab('certificates')}>
          Certificates
        </button>
      </div>
      
      {/* Content Sections */}
      <Show when={activeTab() === 'contact'}>
        <ContactInfoSection userId={userId} contactInfo={skillBank()?.contactInfo} onUpdate={refetch} />
      </Show>
      
      <Show when={activeTab() === 'summaries'}>
        <SummariesSection userId={userId} summaries={skillBank()?.summaries} onUpdate={refetch} />
      </Show>
      
      <Show when={activeTab() === 'experience'}>
        <ExperienceSection userId={userId} experiences={skillBank()?.experience} onUpdate={refetch} />
      </Show>
      
      {/* Additional sections... */}
    </div>
  );
};
```

---

## 🧩 **Integration with Resume Builder**

### **Resume Builder Tab Integration**

Update `ResumeBuilderPage.tsx` to include Skill Bank:

```typescript
// ResumeBuilderPage.tsx
const tabs = [
  { id: 'profile', label: 'User Profile', icon: UserIcon },
  { id: 'skill-bank', label: 'Skill Bank', icon: DatabaseIcon },  // NEW
  { id: 'resume', label: 'Resume Builder', icon: DocumentIcon }
];
```

### **Resume Section Data Integration**

Each resume section will have "Use from Skill Bank" options:

```typescript
// Example: Experience section in resume builder
const ExperienceResumeSection: Component = () => {
  const [useSkillBank, setUseSkillBank] = createSignal(false);
  const [skillBankExperience] = createResource(() => 
    skillBankApi.getExperienceEntries(userId)
  );
  
  return (
    <div class="experience-section">
      <div class="flex items-center justify-between mb-4">
        <h3>Experience</h3>
        <label class="label cursor-pointer">
          <input type="checkbox" class="toggle" 
                 checked={useSkillBank()} 
                 onChange={(e) => setUseSkillBank(e.target.checked)} />
          <span class="label-text ml-2">Use from Skill Bank</span>
        </label>
      </div>
      
      <Show when={useSkillBank()} fallback={<ManualExperienceEntry />}>
        <SkillBankExperienceSelector 
          experiences={skillBankExperience()} 
          onSelect={handleExperienceSelect}
        />
      </Show>
    </div>
  );
};
```

---

## 📋 **Data Migration Strategy**

### **Phase 1: Create New Models**
1. Create new database tables without affecting existing ones
2. Update models.py with new schemas
3. Run database migrations

### **Phase 2: Data Migration Script**
```python
async def migrate_user_profile_data():
    """Migrate existing UserProfile data to new Skill Bank structure"""
    
    users = session.query(UserProfileDB).all()
    
    for user in users:
        # 1. Migrate contact info
        contact_info = ContactInfoDB(
            user_profile_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone
        )
        session.add(contact_info)
        
        # 2. Migrate skills
        if user.skills:
            for skill_name in user.skills:
                skill_entry = SkillEntryDB(
                    user_profile_id=user.id,
                    skill_name=skill_name,
                    skill_type=SkillType.HARD_SKILL  # Default, user can change later
                )
                session.add(skill_entry)
        
        # 3. Create main summary from bio
        if user.bio:
            summary_variation = ContentVariationDB(
                user_profile_id=user.id,
                content_type='summary',
                title='Main Summary',
                content=user.bio,
                is_main=True
            )
            session.add(summary_variation)
    
    session.commit()
```

### **Phase 3: Gradual Cutover**
1. Update frontend to use new Skill Bank APIs
2. Maintain backwards compatibility during transition
3. Remove old fields after successful migration

---

## ✅ **Testing Strategy**

### **Backend Testing**
- Unit tests for all new models
- API endpoint testing with various data scenarios
- Data migration testing with sample data
- Performance testing for complex queries

### **Frontend Testing**
- Component testing for all Skill Bank sections
- Integration testing with Resume Builder
- User journey testing (create skill bank → create resume)
- Cross-browser compatibility testing

### **End-to-End Testing**
- Complete skill bank creation workflow
- Resume generation using skill bank data
- Data synchronization between systems
- Performance under load

---

## 📅 **Implementation Timeline**

### **Week 1-2: Backend Foundation**
- Create new database models
- Implement repository layer
- Build API endpoints
- Create migration scripts

### **Week 3-4: Frontend Components**  
- Build all Skill Bank UI sections
- Implement service layer
- Create variation management UI
- Integration testing

### **Week 5: Resume Builder Integration**
- Update Resume Builder with Skill Bank tab
- Implement "use from skill bank" features
- Test data flow between systems

### **Week 6: Testing & Deployment**
- Comprehensive testing
- Performance optimization
- Data migration execution
- Production deployment

---

**Plan Created**: 2025-01-19  
**Estimated Completion**: 2025-02-16 (4 weeks)  
**Complexity**: High  
**Impact**: Major feature addition with data model changes
