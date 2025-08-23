"""
Resume Repository
CRUD operations for resume management with database integration.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session

from app.data.models import JobListingDB, UserProfileDB
from app.data.resume_models import (
    ATSScore,
    Certification,
    ContactInfo,
    Education,
    Project,
    Resume,
    ResumeDB,
    ResumeOptimizationDB,
    ResumeStatus,
    ResumeTemplateDB,
    ResumeType,
    SectionType,
    Skill,
    WorkExperience,
    calculate_resume_completeness,
    create_resume_from_profile,
    generate_ats_score,
)
from app.data.skill_bank_models import EnhancedSkillBankDB
from app.logger import logger


class ResumeRepository:
    """Repository for resume CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    # =====================================
    # Resume CRUD Operations
    # =====================================

    async def create_resume(self, resume_data: Resume) -> ResumeDB:
        """Create a new resume in the database."""
        try:
            # Convert Pydantic model to dict for storage
            resume_dict = resume_data.dict()

            # Serialize dates in JSON fields
            serialized_work_experience = self._serialize_dates_in_dict(
                resume_dict.get("work_experience", [])
            )
            serialized_education = self._serialize_dates_in_dict(
                resume_dict.get("education", [])
            )
            serialized_skills = self._serialize_dates_in_dict(
                resume_dict.get("skills", [])
            )
            serialized_projects = self._serialize_dates_in_dict(
                resume_dict.get("projects", [])
            )
            serialized_certifications = self._serialize_dates_in_dict(
                resume_dict.get("certifications", [])
            )
            serialized_custom_sections = self._serialize_dates_in_dict(
                resume_dict.get("custom_sections", [])
            )

            # Create new resume DB record
            resume_db = ResumeDB(
                id=resume_dict.get("id") or str(uuid4()),
                user_id=resume_dict["user_id"],
                title=resume_dict["title"],
                resume_type=resume_dict.get("resume_type", "base"),
                status=resume_dict.get("status", "draft"),
                contact_info=resume_dict["contact_info"],
                summary=resume_dict.get("summary"),
                work_experience=serialized_work_experience,
                education=serialized_education,
                skills=serialized_skills,
                projects=serialized_projects,
                certifications=serialized_certifications,
                custom_sections=serialized_custom_sections,
                template_id=resume_dict.get("template_id"),
                based_on_resume_id=resume_dict.get("based_on_resume_id"),
                job_id=resume_dict.get("job_id"),
                version=resume_dict.get("version", 1),
            )

            self.session.add(resume_db)
            self.session.commit()

            logger.info(f"Created new resume: {resume_db.id}")
            return resume_db

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating resume: {e}")
            raise

    async def get_resume(self, resume_id: str, user_id: str) -> Optional[Resume]:
        """Get a resume by ID for a specific user."""
        try:
            resume_db = (
                self.session.query(ResumeDB)
                .filter(and_(ResumeDB.id == resume_id, ResumeDB.user_id == user_id))
                .first()
            )

            if not resume_db:
                return None

            return self._db_to_pydantic(resume_db)

        except Exception as e:
            logger.error(f"Error getting resume {resume_id}: {e}")
            return None

    async def update_resume(
        self, resume_id: str, user_id: str, updates: Dict[str, Any]
    ) -> Optional[Resume]:
        """Update a resume with provided data."""
        try:
            resume_db = (
                self.session.query(ResumeDB)
                .filter(and_(ResumeDB.id == resume_id, ResumeDB.user_id == user_id))
                .first()
            )

            if not resume_db:
                return None

            # Update fields
            for field, value in updates.items():
                if hasattr(resume_db, field):
                    setattr(resume_db, field, value)

            resume_db.updated_at = datetime.utcnow()
            resume_db.version += 1  # Increment version

            self.session.commit()

            logger.info(f"Updated resume: {resume_id}")
            return self._db_to_pydantic(resume_db)

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating resume {resume_id}: {e}")
            return None

    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """Delete a resume."""
        try:
            resume_db = (
                self.session.query(ResumeDB)
                .filter(and_(ResumeDB.id == resume_id, ResumeDB.user_id == user_id))
                .first()
            )

            if not resume_db:
                return False

            self.session.delete(resume_db)
            self.session.commit()

            logger.info(f"Deleted resume: {resume_id}")
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting resume {resume_id}: {e}")
            return False

    async def get_user_resumes(
        self, user_id: str, status: Optional[ResumeStatus] = None
    ) -> List[Resume]:
        """Get all resumes for a user, optionally filtered by status."""
        try:
            query = self.session.query(ResumeDB).filter(ResumeDB.user_id == user_id)

            if status:
                query = query.filter(ResumeDB.status == status.value)

            resume_dbs = query.order_by(desc(ResumeDB.updated_at)).all()

            return [self._db_to_pydantic(resume_db) for resume_db in resume_dbs]

        except Exception as e:
            logger.error(f"Error getting user resumes for {user_id}: {e}")
            return []

    # =====================================
    # Resume Creation from Profile
    # =====================================

    async def create_resume_from_user_profile(
        self, user_id: str, title: str = None
    ) -> Optional[Resume]:
        """Create a basic resume from user profile data."""
        try:
            # Get user profile
            user_profile = (
                self.session.query(UserProfileDB)
                .filter(UserProfileDB.id == user_id)
                .first()
            )
            if not user_profile:
                logger.error(f"User profile not found: {user_id}")
                return None

            # Convert to dict for processing
            profile_data = {
                "id": user_profile.id,
                "first_name": user_profile.first_name,
                "last_name": user_profile.last_name,
                "email": user_profile.email,
                "phone": user_profile.phone,
                "current_title": user_profile.current_title,
                "bio": user_profile.bio,
                "skills": user_profile.skills or [],
                "education": user_profile.education,
            }

            # Create resume using utility function
            resume = create_resume_from_profile(profile_data)
            if title:
                resume.title = title

            # Save to database
            resume_db = await self.create_resume(resume)
            return self._db_to_pydantic(resume_db)

        except Exception as e:
            logger.error(f"Error creating resume from profile for {user_id}: {e}")
            return None

    # =====================================
    # Resume Tailoring and Job Integration
    # =====================================

    async def create_tailored_resume(
        self, base_resume_id: str, job_id: str, user_id: str
    ) -> Optional[Resume]:
        """Create a tailored resume for a specific job."""
        try:
            # Get base resume
            base_resume = await self.get_resume(base_resume_id, user_id)
            if not base_resume:
                return None

            # Get job details
            job_db = (
                self.session.query(JobListingDB)
                .filter(JobListingDB.id == job_id)
                .first()
            )
            if not job_db:
                logger.error(f"Job not found: {job_id}")
                return None

            # Create tailored copy
            tailored_resume = Resume(**base_resume.dict())
            tailored_resume.id = None  # Will generate new ID
            tailored_resume.title = f"{base_resume.title} - {job_db.company}"
            tailored_resume.resume_type = ResumeType.TAILORED
            tailored_resume.based_on_resume_id = base_resume_id
            tailored_resume.job_id = job_id
            tailored_resume.version = 1
            tailored_resume.created_at = None  # Will be set by create_resume
            tailored_resume.updated_at = None

            # Basic optimization: add job-relevant skills if missing
            job_skills = set()
            if job_db.skills_required:
                job_skills.update(skill.lower() for skill in job_db.skills_required)
            if job_db.skills_preferred:
                job_skills.update(skill.lower() for skill in job_db.skills_preferred)

            resume_skills = {skill.name.lower() for skill in tailored_resume.skills}
            missing_skills = job_skills - resume_skills

            # Add missing skills (up to 5) from job requirements
            for skill in list(missing_skills)[:5]:
                tailored_resume.skills.append(
                    Skill(
                        name=skill.title(),
                        level="intermediate",
                        category="Job-Relevant Skills",
                    )
                )

            # Create and save
            resume_db = await self.create_resume(tailored_resume)
            return self._db_to_pydantic(resume_db)

        except Exception as e:
            logger.error(f"Error creating tailored resume: {e}")
            return None

    # =====================================
    # ATS Scoring and Optimization
    # =====================================

    async def calculate_ats_score(
        self, resume: Resume, job_description: Optional[str] = None
    ) -> ATSScore:
        """Calculate ATS compatibility score for a resume."""
        try:
            return generate_ats_score(resume, job_description)
        except Exception as e:
            logger.error(f"Error calculating ATS score: {e}")
            # Return default score
            return ATSScore(
                overall_score=50.0,
                keyword_score=50.0,
                formatting_score=50.0,
                section_score=50.0,
                length_score=50.0,
                suggestions=["Unable to calculate detailed score"],
                missing_keywords=[],
            )

    async def optimize_resume_for_job(
        self, resume_id: str, job_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze and provide optimization recommendations for a resume against a job."""
        try:
            # Get resume and job
            resume = await self.get_resume(resume_id, user_id)
            if not resume:
                return None

            job_db = (
                self.session.query(JobListingDB)
                .filter(JobListingDB.id == job_id)
                .first()
            )
            if not job_db:
                return None

            # Calculate ATS score
            job_description = (
                f"{job_db.title} {job_db.description or ''} {job_db.requirements or ''}"
            )
            ats_score = await self.calculate_ats_score(resume, job_description)

            # Calculate completeness
            completeness = calculate_resume_completeness(resume)

            # Job-specific analysis
            job_skills = set()
            if job_db.skills_required:
                job_skills.update(skill.lower() for skill in job_db.skills_required)
            if job_db.skills_preferred:
                job_skills.update(skill.lower() for skill in job_db.skills_preferred)

            resume_skills = {skill.name.lower() for skill in resume.skills}
            skill_matches = list(job_skills.intersection(resume_skills))
            missing_skills = list(job_skills - resume_skills)

            # Store optimization results
            optimization_db = ResumeOptimizationDB(
                resume_id=resume_id,
                job_id=job_id,
                match_score=ats_score.overall_score,
                keyword_matches=ats_score.missing_keywords,  # TODO: implement proper keyword matching
                missing_keywords=ats_score.missing_keywords,
                skill_matches=skill_matches,
                missing_skills=missing_skills,
                recommendations=ats_score.suggestions,
                sections_to_emphasize=[
                    SectionType.SKILLS.value,
                    SectionType.EXPERIENCE.value,
                ],
                content_suggestions=[
                    f"Consider adding these skills: {', '.join(missing_skills[:5])}",
                    f"Emphasize experience with: {', '.join(skill_matches[:3])}",
                ],
            )

            self.session.add(optimization_db)
            self.session.commit()

            return {
                "ats_score": ats_score.dict(),
                "completeness_score": completeness,
                "skill_matches": skill_matches,
                "missing_skills": missing_skills[:10],  # Top 10
                "recommendations": ats_score.suggestions,
                "job_match_score": ats_score.overall_score,
            }

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error optimizing resume for job: {e}")
            return None

    # =====================================
    # Resume Templates
    # =====================================

    async def get_resume_templates(self) -> List[Dict[str, Any]]:
        """Get available resume templates."""
        try:
            templates = (
                self.session.query(ResumeTemplateDB)
                .filter(
                    or_(
                        ResumeTemplateDB.is_system is True,
                        ResumeTemplateDB.is_default is True,
                    )
                )
                .all()
            )

            return [
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "sections": template.sections,
                    "is_default": template.is_default,
                    "styling": template.styling,
                }
                for template in templates
            ]

        except Exception as e:
            logger.error(f"Error getting resume templates: {e}")
            return []

    async def create_default_templates(self):
        """Create default system resume templates."""
        try:
            default_templates = [
                {
                    "name": "Modern Professional",
                    "description": "Clean, modern design perfect for tech and professional roles",
                    "sections": [
                        "contact",
                        "summary",
                        "experience",
                        "education",
                        "skills",
                        "projects",
                    ],
                    "section_order": [
                        "contact",
                        "summary",
                        "experience",
                        "skills",
                        "education",
                        "projects",
                    ],
                    "styling": {
                        "color_scheme": "blue",
                        "font_family": "Arial",
                        "layout": "single_column",
                    },
                    "is_default": True,
                    "is_system": True,
                },
                {
                    "name": "ATS-Friendly",
                    "description": "Optimized for Applicant Tracking Systems with simple formatting",
                    "sections": [
                        "contact",
                        "summary",
                        "experience",
                        "education",
                        "skills",
                    ],
                    "section_order": [
                        "contact",
                        "summary",
                        "experience",
                        "education",
                        "skills",
                    ],
                    "styling": {
                        "color_scheme": "black",
                        "font_family": "Times New Roman",
                        "layout": "simple",
                    },
                    "is_default": False,
                    "is_system": True,
                },
                {
                    "name": "Creative Portfolio",
                    "description": "Showcase creativity with projects and portfolio sections",
                    "sections": [
                        "contact",
                        "summary",
                        "projects",
                        "experience",
                        "skills",
                        "education",
                    ],
                    "section_order": [
                        "contact",
                        "summary",
                        "projects",
                        "experience",
                        "skills",
                        "education",
                    ],
                    "styling": {
                        "color_scheme": "purple",
                        "font_family": "Helvetica",
                        "layout": "two_column",
                    },
                    "is_default": False,
                    "is_system": True,
                },
            ]

            for template_data in default_templates:
                existing = (
                    self.session.query(ResumeTemplateDB)
                    .filter(ResumeTemplateDB.name == template_data["name"])
                    .first()
                )

                if not existing:
                    template_db = ResumeTemplateDB(**template_data)
                    self.session.add(template_db)

            self.session.commit()
            logger.info("Created default resume templates")

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating default templates: {e}")

    # =====================================
    # Skills Bank Integration
    # =====================================

    async def get_user_skill_bank(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's skill bank for resume building."""
        try:
            skill_bank = (
                self.session.query(EnhancedSkillBankDB)
                .filter(EnhancedSkillBankDB.user_id == user_id)
                .first()
            )

            if not skill_bank:
                return None

            # Extract enhanced skills from new format
            all_skills = {}
            if skill_bank.skills:
                skills_data = skill_bank.skills
                if isinstance(skills_data, str):
                    import json

                    skills_data = json.loads(skills_data)
                all_skills = skills_data

            return {
                "skills": all_skills,
                "work_experiences": skill_bank.work_experiences or [],
                "education_entries": skill_bank.education_entries or [],
                "projects": skill_bank.projects or [],
                "certifications": skill_bank.certifications or [],
                "summary_variations": skill_bank.summary_variations or [],
            }

        except Exception as e:
            logger.error(f"Error getting skill bank for {user_id}: {e}")
            return None

    async def update_skill_bank_from_resume(self, user_id: str, resume: Resume):
        """Update user's skill bank based on resume content (deprecated - use SkillBankRepository)."""
        try:
            # This method is deprecated in favor of the new SkillBankRepository
            # For now, we'll just log that skills should be managed via the new system
            logger.info(
                f"Resume skills update requested for user {user_id} - use SkillBankRepository for skill management"
            )

            # Extract skills from resume for backwards compatibility
            resume_skills = [skill.name for skill in resume.skills]
            logger.info(
                f"Resume contains {len(resume_skills)} skills: {', '.join(resume_skills[:5])}{'...' if len(resume_skills) > 5 else ''}"
            )

        except Exception as e:
            logger.error(f"Error processing resume skills: {e}")

    # =====================================
    # Utility Methods
    # =====================================

    def _serialize_dates_in_dict(self, data: Any) -> Any:
        """Recursively convert date objects to ISO format strings for JSON serialization."""
        if isinstance(data, dict):
            return {
                key: self._serialize_dates_in_dict(value) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._serialize_dates_in_dict(item) for item in data]
        elif isinstance(data, date):
            return data.isoformat()
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data

    def _deserialize_dates_in_dict(self, data: Any) -> Any:
        """Recursively convert ISO format date strings back to date objects."""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key in [
                    "start_date",
                    "end_date",
                    "issue_date",
                    "expiry_date",
                ] and isinstance(value, str):
                    try:
                        # Parse ISO format date string
                        if "T" in value:  # datetime
                            result[key] = datetime.fromisoformat(
                                value.replace("Z", "+00:00")
                            )
                        else:  # date
                            result[key] = datetime.strptime(value, "%Y-%m-%d").date()
                    except (ValueError, TypeError):
                        result[key] = value
                else:
                    result[key] = self._deserialize_dates_in_dict(value)
            return result
        elif isinstance(data, list):
            return [self._deserialize_dates_in_dict(item) for item in data]
        else:
            return data

    def _db_to_pydantic(self, resume_db: ResumeDB) -> Resume:
        """Convert database model to Pydantic model."""
        try:
            # Convert contact_info JSON to ContactInfo object
            contact_info = ContactInfo(**resume_db.contact_info)

            # Convert work_experience JSON to WorkExperience objects
            work_experience = []
            if resume_db.work_experience:
                for exp_data in resume_db.work_experience:
                    deserialized_exp = self._deserialize_dates_in_dict(exp_data)
                    work_experience.append(WorkExperience(**deserialized_exp))

            # Convert education JSON to Education objects
            education = []
            if resume_db.education:
                for edu_data in resume_db.education:
                    deserialized_edu = self._deserialize_dates_in_dict(edu_data)
                    education.append(Education(**deserialized_edu))

            # Convert skills JSON to Skill objects
            skills = []
            if resume_db.skills:
                for skill_data in resume_db.skills:
                    deserialized_skill = self._deserialize_dates_in_dict(skill_data)
                    skills.append(Skill(**deserialized_skill))

            # Convert projects JSON to Project objects
            projects = []
            if resume_db.projects:
                for proj_data in resume_db.projects:
                    deserialized_proj = self._deserialize_dates_in_dict(proj_data)
                    projects.append(Project(**deserialized_proj))

            # Convert certifications JSON to Certification objects
            certifications = []
            if resume_db.certifications:
                for cert_data in resume_db.certifications:
                    deserialized_cert = self._deserialize_dates_in_dict(cert_data)
                    certifications.append(Certification(**deserialized_cert))

            return Resume(
                id=resume_db.id,
                user_id=resume_db.user_id,
                title=resume_db.title,
                resume_type=resume_db.resume_type,
                status=resume_db.status,
                contact_info=contact_info,
                summary=resume_db.summary,
                work_experience=work_experience,
                education=education,
                skills=skills,
                projects=projects,
                certifications=certifications,
                custom_sections=resume_db.custom_sections or [],
                template_id=resume_db.template_id,
                based_on_resume_id=resume_db.based_on_resume_id,
                job_id=resume_db.job_id,
                version=resume_db.version,
                created_at=resume_db.created_at,
                updated_at=resume_db.updated_at,
                last_generated_at=resume_db.last_generated_at,
            )

        except Exception as e:
            logger.error(f"Error converting resume DB to Pydantic: {e}")
            raise
