"""
JobPilot Skill Bank Repository
Repository implementation for skill bank operations with enhanced content variation management
"""

import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional


# Custom JSON encoder for handling date and datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


from sqlalchemy.orm import Session

from app.data.database import DatabaseManager
from app.data.models import UserProfileDB
from app.data.skill_bank_models import (
    Certification,
    EducationEntry,
    EnhancedSkill,
    EnhancedSkillBankDB,
    ExperienceContentVariation,
    ExperienceEntry,
    ProjectEntry,
    SkillBank,
    SummaryVariation,
    convert_skill_list_to_enhanced,
    create_default_skill_bank,
)


class SkillBankRepository:
    """Repository for skill bank operations."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _get_session(self) -> Session:
        """Get database session."""
        return self.db_manager.get_session()

    # ===========================================
    # MAIN SKILL BANK OPERATIONS
    # ===========================================

    async def get_skill_bank(self, user_id: str) -> Optional[SkillBank]:
        """Get user's skill bank."""
        with self._get_session() as session:
            skill_bank_db = (
                session.query(EnhancedSkillBankDB)
                .filter(EnhancedSkillBankDB.user_id == user_id)
                .first()
            )

            if not skill_bank_db:
                return None

            return self._db_to_pydantic(skill_bank_db)

    async def create_skill_bank(self, user_id: str) -> SkillBank:
        """Create a new skill bank for user."""
        with self._get_session() as session:
            # Check if skill bank already exists
            existing = (
                session.query(EnhancedSkillBankDB)
                .filter(EnhancedSkillBankDB.user_id == user_id)
                .first()
            )

            if existing:
                return self._db_to_pydantic(existing)

            # Create default skill bank
            skill_bank = create_default_skill_bank(user_id)

            # Convert to database model
            skill_bank_db = self._pydantic_to_db(skill_bank)

            session.add(skill_bank_db)
            session.commit()
            session.refresh(skill_bank_db)

            return self._db_to_pydantic(skill_bank_db)

    async def get_or_create_skill_bank(self, user_id: str) -> SkillBank:
        """Get existing skill bank or create a new one."""
        skill_bank = await self.get_skill_bank(user_id)
        if skill_bank:
            return skill_bank
        return await self.create_skill_bank(user_id)

    async def update_skill_bank(
        self, user_id: str, updates: Dict[str, Any]
    ) -> SkillBank:
        """Update skill bank fields."""
        with self._get_session() as session:
            skill_bank_db = (
                session.query(EnhancedSkillBankDB)
                .filter(EnhancedSkillBankDB.user_id == user_id)
                .first()
            )

            if not skill_bank_db:
                # Create new skill bank if it doesn't exist
                return await self.create_skill_bank(user_id)

            # Update fields
            for field, value in updates.items():
                if hasattr(skill_bank_db, field):
                    if isinstance(value, (dict, list)):
                        setattr(
                            skill_bank_db,
                            field,
                            (
                                json.dumps(value, cls=DateTimeEncoder)
                                if value
                                else ([] if field.endswith("s") else {})
                            ),
                        )
                    else:
                        setattr(skill_bank_db, field, value)

            skill_bank_db.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(skill_bank_db)

            return self._db_to_pydantic(skill_bank_db)

    # ===========================================
    # SKILLS MANAGEMENT
    # ===========================================

    async def add_skill(self, user_id: str, skill: EnhancedSkill) -> EnhancedSkill:
        """Add a new skill to the skill bank."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        # Add skill to appropriate category
        if skill.category.value not in skill_bank.skills:
            skill_bank.skills[skill.category.value] = []

        # Check for duplicates by name
        existing_skills = skill_bank.skills[skill.category.value]
        if any(
            existing.name.lower() == skill.name.lower() for existing in existing_skills
        ):
            raise ValueError(
                f"Skill '{skill.name}' already exists in category '{skill.category.value}'"
            )

        skill_bank.skills[skill.category.value].append(skill)

        # Update in database
        await self._update_skills_in_db(user_id, skill_bank.skills)

        return skill

    async def update_skill(
        self, user_id: str, skill_id: str, updates: Dict[str, Any]
    ) -> EnhancedSkill:
        """Update an existing skill."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        # Find skill across all categories
        for category_name, skills in skill_bank.skills.items():
            for i, skill in enumerate(skills):
                if skill.id == skill_id:
                    # Update skill fields
                    for field, value in updates.items():
                        if hasattr(skill, field):
                            setattr(skill, field, value)

                    # Update in database
                    await self._update_skills_in_db(user_id, skill_bank.skills)

                    return skill

        raise ValueError(f"Skill with ID '{skill_id}' not found")

    async def delete_skill(self, user_id: str, skill_id: str) -> bool:
        """Delete a skill from the skill bank."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        # Find and remove skill
        for category_name, skills in skill_bank.skills.items():
            for i, skill in enumerate(skills):
                if skill.id == skill_id:
                    del skills[i]

                    # Update in database
                    await self._update_skills_in_db(user_id, skill_bank.skills)

                    return True

        return False

    async def get_skills(
        self, user_id: str, category: Optional[str] = None
    ) -> List[EnhancedSkill]:
        """Get all skills, optionally filtered by category."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        if category:
            return skill_bank.skills.get(category, [])

        # Return all skills from all categories
        all_skills = []
        for skills in skill_bank.skills.values():
            all_skills.extend(skills)

        return sorted(
            all_skills, key=lambda s: (s.category.value, s.display_order, s.name)
        )

    # ===========================================
    # SUMMARY VARIATIONS
    # ===========================================

    async def add_summary_variation(
        self, user_id: str, variation: SummaryVariation
    ) -> SummaryVariation:
        """Add a summary variation."""
        skill_bank = await self.get_or_create_skill_bank(user_id)
        skill_bank.summary_variations.append(variation)

        await self._update_summary_variations_in_db(
            user_id, skill_bank.summary_variations
        )
        return variation

    async def update_summary_variation(
        self, user_id: str, variation_id: str, updates: Dict[str, Any]
    ) -> SummaryVariation:
        """Update a summary variation."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for variation in skill_bank.summary_variations:
            if variation.id == variation_id:
                for field, value in updates.items():
                    if hasattr(variation, field):
                        setattr(variation, field, value)

                await self._update_summary_variations_in_db(
                    user_id, skill_bank.summary_variations
                )
                return variation

        raise ValueError(f"Summary variation with ID '{variation_id}' not found")

    async def delete_summary_variation(self, user_id: str, variation_id: str) -> bool:
        """Delete a summary variation."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for i, variation in enumerate(skill_bank.summary_variations):
            if variation.id == variation_id:
                del skill_bank.summary_variations[i]

                await self._update_summary_variations_in_db(
                    user_id, skill_bank.summary_variations
                )
                return True

        return False

    # ===========================================
    # EXPERIENCE MANAGEMENT
    # ===========================================

    async def add_experience(
        self, user_id: str, experience: ExperienceEntry
    ) -> ExperienceEntry:
        """Add a work experience entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)
        skill_bank.work_experiences.append(experience)

        await self._update_experiences_in_db(user_id, skill_bank.work_experiences)
        return experience

    async def update_experience(
        self, user_id: str, experience_id: str, updates: Dict[str, Any]
    ) -> ExperienceEntry:
        """Update a work experience entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for experience in skill_bank.work_experiences:
            if experience.id == experience_id:
                for field, value in updates.items():
                    if hasattr(experience, field):
                        setattr(experience, field, value)

                await self._update_experiences_in_db(
                    user_id, skill_bank.work_experiences
                )
                return experience

        raise ValueError(f"Experience with ID '{experience_id}' not found")

    async def delete_experience(self, user_id: str, experience_id: str) -> bool:
        """Delete a work experience entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for i, experience in enumerate(skill_bank.work_experiences):
            if experience.id == experience_id:
                del skill_bank.work_experiences[i]

                # Also remove any content variations for this experience
                if experience_id in skill_bank.experience_content_variations:
                    del skill_bank.experience_content_variations[experience_id]

                await self._update_experiences_in_db(
                    user_id, skill_bank.work_experiences
                )
                await self._update_experience_variations_in_db(
                    user_id, skill_bank.experience_content_variations
                )
                return True

        return False

    async def add_experience_content_variation(
        self, user_id: str, experience_id: str, variation: ExperienceContentVariation
    ) -> ExperienceContentVariation:
        """Add a content variation to a work experience entry."""
        return await self.add_experience_variation(user_id, variation)

    async def add_experience_variation(
        self, user_id: str, variation: ExperienceContentVariation
    ) -> ExperienceContentVariation:
        """Add a variation to a work experience entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        # Ensure the experience exists
        experience_exists = any(
            exp.id == variation.experience_id for exp in skill_bank.work_experiences
        )
        if not experience_exists:
            raise ValueError(
                f"Experience with ID '{variation.experience_id}' not found"
            )

        # Add variation
        if variation.experience_id not in skill_bank.experience_content_variations:
            skill_bank.experience_content_variations[variation.experience_id] = []

        skill_bank.experience_content_variations[variation.experience_id].append(
            variation
        )

        await self._update_experience_variations_in_db(
            user_id, skill_bank.experience_content_variations
        )
        return variation

    # ===========================================
    # EDUCATION MANAGEMENT
    # ===========================================

    async def add_education(
        self, user_id: str, education: EducationEntry
    ) -> EducationEntry:
        """Add an education entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)
        skill_bank.education_entries.append(education)

        await self._update_education_in_db(user_id, skill_bank.education_entries)
        return education

    async def update_education(
        self, user_id: str, education_id: str, updates: Dict[str, Any]
    ) -> EducationEntry:
        """Update an education entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for education in skill_bank.education_entries:
            if education.id == education_id:
                for field, value in updates.items():
                    if hasattr(education, field):
                        setattr(education, field, value)

                await self._update_education_in_db(
                    user_id, skill_bank.education_entries
                )
                return education

        raise ValueError(f"Education with ID '{education_id}' not found")

    async def delete_education(self, user_id: str, education_id: str) -> bool:
        """Delete an education entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for i, education in enumerate(skill_bank.education_entries):
            if education.id == education_id:
                del skill_bank.education_entries[i]

                # Also remove any content variations for this education
                if education_id in skill_bank.education_content_variations:
                    del skill_bank.education_content_variations[education_id]

                await self._update_education_in_db(
                    user_id, skill_bank.education_entries
                )
                return True

        return False

    # ===========================================
    # PROJECT MANAGEMENT
    # ===========================================

    async def add_project(self, user_id: str, project: ProjectEntry) -> ProjectEntry:
        """Add a project entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)
        skill_bank.projects.append(project)

        await self._update_projects_in_db(user_id, skill_bank.projects)
        return project

    async def update_project(
        self, user_id: str, project_id: str, updates: Dict[str, Any]
    ) -> ProjectEntry:
        """Update a project entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for project in skill_bank.projects:
            if project.id == project_id:
                for field, value in updates.items():
                    if hasattr(project, field):
                        setattr(project, field, value)

                await self._update_projects_in_db(user_id, skill_bank.projects)
                return project

        raise ValueError(f"Project with ID '{project_id}' not found")

    async def delete_project(self, user_id: str, project_id: str) -> bool:
        """Delete a project entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for i, project in enumerate(skill_bank.projects):
            if project.id == project_id:
                del skill_bank.projects[i]

                # Also remove any content variations for this project
                if project_id in skill_bank.project_content_variations:
                    del skill_bank.project_content_variations[project_id]

                await self._update_projects_in_db(user_id, skill_bank.projects)
                return True

        return False

    # ===========================================
    # CERTIFICATION MANAGEMENT
    # ===========================================

    async def add_certification(
        self, user_id: str, certification: Certification
    ) -> Certification:
        """Add a certification entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)
        skill_bank.certifications.append(certification)

        await self._update_certifications_in_db(user_id, skill_bank.certifications)
        return certification

    async def update_certification(
        self, user_id: str, certification_id: str, updates: Dict[str, Any]
    ) -> Certification:
        """Update a certification entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for certification in skill_bank.certifications:
            if certification.id == certification_id:
                for field, value in updates.items():
                    if hasattr(certification, field):
                        setattr(certification, field, value)

                await self._update_certifications_in_db(
                    user_id, skill_bank.certifications
                )
                return certification

        raise ValueError(f"Certification with ID '{certification_id}' not found")

    async def delete_certification(self, user_id: str, certification_id: str) -> bool:
        """Delete a certification entry."""
        skill_bank = await self.get_or_create_skill_bank(user_id)

        for i, certification in enumerate(skill_bank.certifications):
            if certification.id == certification_id:
                del skill_bank.certifications[i]

                await self._update_certifications_in_db(
                    user_id, skill_bank.certifications
                )
                return True

        return False

    # ===========================================
    # DATA MIGRATION
    # ===========================================

    async def migrate_from_user_profile(self, user_id: str) -> SkillBank:
        """Migrate skills data from UserProfile to SkillBank."""
        with self._get_session() as session:
            user_profile = (
                session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
            )
            if not user_profile:
                raise ValueError(f"User profile with ID '{user_id}' not found")

            # Get or create skill bank
            skill_bank = await self.get_or_create_skill_bank(user_id)

            # Migrate basic skills from user profile
            if user_profile.skills:
                # Convert simple skill names to enhanced skills
                enhanced_skills = convert_skill_list_to_enhanced(user_profile.skills)

                # Add to technical skills category
                if "Technical Skills" not in skill_bank.skills:
                    skill_bank.skills["Technical Skills"] = []

                # Only add skills that don't already exist
                existing_names = {
                    skill.name.lower()
                    for skill in skill_bank.skills["Technical Skills"]
                }
                new_skills = [
                    skill
                    for skill in enhanced_skills
                    if skill.name.lower() not in existing_names
                ]

                skill_bank.skills["Technical Skills"].extend(new_skills)

            # Migrate bio as default summary if no summary exists
            if user_profile.bio and not skill_bank.default_summary:
                skill_bank.default_summary = user_profile.bio

            # Update skill bank in database
            await self._update_full_skill_bank(user_id, skill_bank)

            return skill_bank

    # ===========================================
    # HELPER METHODS
    # ===========================================

    def _db_to_pydantic(self, skill_bank_db: EnhancedSkillBankDB) -> SkillBank:
        """Convert database model to Pydantic model."""

        # Convert JSON fields back to proper types
        skills = {}
        if skill_bank_db.skills:
            skills_data = (
                skill_bank_db.skills
                if isinstance(skill_bank_db.skills, dict)
                else json.loads(skill_bank_db.skills)
            )
            for category, skill_list in skills_data.items():
                skills[category] = [
                    EnhancedSkill(**skill_dict) for skill_dict in skill_list
                ]

        summary_variations = []
        if skill_bank_db.summary_variations:
            variations_data = (
                skill_bank_db.summary_variations
                if isinstance(skill_bank_db.summary_variations, list)
                else json.loads(skill_bank_db.summary_variations)
            )
            summary_variations = [
                SummaryVariation(**var_dict) for var_dict in variations_data
            ]

        work_experiences = []
        if skill_bank_db.work_experiences:
            exp_data = (
                skill_bank_db.work_experiences
                if isinstance(skill_bank_db.work_experiences, list)
                else json.loads(skill_bank_db.work_experiences)
            )
            work_experiences = [ExperienceEntry(**exp_dict) for exp_dict in exp_data]

        education_entries = []
        if skill_bank_db.education_entries:
            edu_data = (
                skill_bank_db.education_entries
                if isinstance(skill_bank_db.education_entries, list)
                else json.loads(skill_bank_db.education_entries)
            )
            education_entries = [EducationEntry(**edu_dict) for edu_dict in edu_data]

        projects = []
        if skill_bank_db.projects:
            proj_data = (
                skill_bank_db.projects
                if isinstance(skill_bank_db.projects, list)
                else json.loads(skill_bank_db.projects)
            )
            projects = [ProjectEntry(**proj_dict) for proj_dict in proj_data]

        certifications = []
        if skill_bank_db.certifications:
            cert_data = (
                skill_bank_db.certifications
                if isinstance(skill_bank_db.certifications, list)
                else json.loads(skill_bank_db.certifications)
            )
            certifications = [Certification(**cert_dict) for cert_dict in cert_data]

        # Handle content variations
        experience_content_variations = {}
        if skill_bank_db.experience_content_variations:
            exp_var_data = (
                skill_bank_db.experience_content_variations
                if isinstance(skill_bank_db.experience_content_variations, dict)
                else json.loads(skill_bank_db.experience_content_variations)
            )
            for exp_id, variations in exp_var_data.items():
                experience_content_variations[exp_id] = [
                    ExperienceContentVariation(**var_dict) for var_dict in variations
                ]

        return SkillBank(
            id=skill_bank_db.id,
            user_id=skill_bank_db.user_id,
            skills=skills,
            skill_categories=skill_bank_db.skill_categories or [],
            default_summary=skill_bank_db.default_summary,
            summary_variations=summary_variations,
            work_experiences=work_experiences,
            education_entries=education_entries,
            projects=projects,
            certifications=certifications,
            experience_content_variations=experience_content_variations,
            education_content_variations=skill_bank_db.education_content_variations
            or {},
            project_content_variations=skill_bank_db.project_content_variations or {},
            # REMOVED: Legacy field references no longer exist in SkillBank Pydantic model
            # experience_keywords, industry_keywords, technical_keywords, soft_skills,
            # auto_extracted_skills, skill_confidence - functionality moved to enhanced skills
            created_at=skill_bank_db.created_at,
            updated_at=skill_bank_db.updated_at,
        )

    def _pydantic_to_db(self, skill_bank: SkillBank) -> EnhancedSkillBankDB:
        """Convert Pydantic model to database model."""

        # Convert skills to JSON serializable format
        skills_json = {}
        for category, skill_list in skill_bank.skills.items():
            skills_json[category] = [skill.model_dump() for skill in skill_list]

        return EnhancedSkillBankDB(
            id=skill_bank.id,
            user_id=skill_bank.user_id,
            skills=json.dumps(skills_json, cls=DateTimeEncoder),
            skill_categories=skill_bank.skill_categories,
            default_summary=skill_bank.default_summary,
            summary_variations=json.dumps(
                [var.model_dump() for var in skill_bank.summary_variations],
                cls=DateTimeEncoder,
            ),
            work_experiences=json.dumps(
                [exp.model_dump() for exp in skill_bank.work_experiences],
                cls=DateTimeEncoder,
            ),
            education_entries=json.dumps(
                [edu.model_dump() for edu in skill_bank.education_entries],
                cls=DateTimeEncoder,
            ),
            projects=json.dumps(
                [proj.model_dump() for proj in skill_bank.projects], cls=DateTimeEncoder
            ),
            certifications=json.dumps(
                [cert.model_dump() for cert in skill_bank.certifications],
                cls=DateTimeEncoder,
            ),
            experience_content_variations=json.dumps(
                {
                    exp_id: [var.model_dump() for var in variations]
                    for exp_id, variations in skill_bank.experience_content_variations.items()
                },
                cls=DateTimeEncoder,
            ),
            education_content_variations=skill_bank.education_content_variations,
            project_content_variations=skill_bank.project_content_variations,
            created_at=skill_bank.created_at,
            updated_at=skill_bank.updated_at,
        )

    async def _update_skills_in_db(
        self, user_id: str, skills: Dict[str, List[EnhancedSkill]]
    ):
        """Update skills in database."""
        skills_json = {
            category: [skill.dict() for skill in skill_list]
            for category, skill_list in skills.items()
        }
        await self.update_skill_bank(user_id, {"skills": skills_json})

    async def _update_summary_variations_in_db(
        self, user_id: str, variations: List[SummaryVariation]
    ):
        """Update summary variations in database."""
        variations_json = [var.dict() for var in variations]
        await self.update_skill_bank(user_id, {"summary_variations": variations_json})

    async def _update_experiences_in_db(
        self, user_id: str, experiences: List[ExperienceEntry]
    ):
        """Update work experiences in database."""
        experiences_json = [exp.dict() for exp in experiences]
        await self.update_skill_bank(user_id, {"work_experiences": experiences_json})

    async def _update_experience_variations_in_db(
        self, user_id: str, variations: Dict[str, List[ExperienceContentVariation]]
    ):
        """Update experience content variations in database."""
        variations_json = {
            exp_id: [var.dict() for var in var_list]
            for exp_id, var_list in variations.items()
        }
        await self.update_skill_bank(
            user_id, {"experience_content_variations": variations_json}
        )

    async def _update_full_skill_bank(self, user_id: str, skill_bank: SkillBank):
        """Update complete skill bank in database."""
        updates = {
            "skills": {
                category: [skill.dict() for skill in skill_list]
                for category, skill_list in skill_bank.skills.items()
            },
            "default_summary": skill_bank.default_summary,
            "summary_variations": [var.dict() for var in skill_bank.summary_variations],
            "work_experiences": [exp.dict() for exp in skill_bank.work_experiences],
            "education_entries": [edu.dict() for edu in skill_bank.education_entries],
            "projects": [proj.dict() for proj in skill_bank.projects],
            "certifications": [cert.dict() for cert in skill_bank.certifications],
        }
        await self.update_skill_bank(user_id, updates)

    async def _update_education_in_db(
        self, user_id: str, education_entries: List[EducationEntry]
    ):
        """Update education entries in database."""
        education_json = [edu.dict() for edu in education_entries]
        await self.update_skill_bank(user_id, {"education_entries": education_json})

    async def _update_projects_in_db(self, user_id: str, projects: List[ProjectEntry]):
        """Update project entries in database."""
        projects_json = [proj.dict() for proj in projects]
        await self.update_skill_bank(user_id, {"projects": projects_json})

    async def _update_certifications_in_db(
        self, user_id: str, certifications: List[Certification]
    ):
        """Update certifications in database."""
        certifications_json = [cert.dict() for cert in certifications]
        await self.update_skill_bank(user_id, {"certifications": certifications_json})
