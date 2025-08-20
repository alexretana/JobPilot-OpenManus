"""
JobPilot Mock Data Generator
Generator for creating comprehensive mock data for UserProfile and SkillBank testing
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.data.database import DatabaseManager
from app.data.models import UserProfileDB
from app.data.skill_bank_models import (
    ContentFocusType,
    ContentSource,
    EnhancedSkill,
    SkillCategory,
    SummaryVariation,
)
from app.repositories.skill_bank_repository import SkillBankRepository


class DataMigrationManager:
    """Manager for data migration operations between UserProfile and SkillBank."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.skill_bank_repo = SkillBankRepository(db_manager)

    def _get_session(self) -> Session:
        """Get database session."""
        return self.db_manager.get_session()

    # =========================================================================
    # CONTACT INFO CONSOLIDATION
    # =========================================================================

    async def migrate_contact_info_to_skillbank(self, user_id: str) -> Dict[str, Any]:
        """
        Migrate contact information from UserProfile to SkillBank.
        Creates a single source of truth for contact data.
        """
        with self._get_session() as session:
            # Get user profile data
            user_profile = (
                session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
            )

            if not user_profile:
                raise ValueError(f"User profile not found for user_id: {user_id}")

            # Extract contact info from UserProfile
            contact_info = {
                "first_name": user_profile.first_name,
                "last_name": user_profile.last_name,
                "email": user_profile.email,
                "phone": user_profile.phone,
                "city": user_profile.city,
                "state": user_profile.state,
                "linkedin_url": user_profile.linkedin_url,
                "portfolio_url": user_profile.portfolio_url,
            }

            # Get or create skill bank
            skill_bank = await self.skill_bank_repo.get_or_create_skill_bank(user_id)

            # Update skill bank with contact info (store in skill_bank model if needed)
            # For now, contact info remains in UserProfile as the canonical source
            # but SkillBank can reference it

            return {
                "status": "success",
                "user_id": user_id,
                "contact_info": contact_info,
                "message": "Contact info available to both UserProfile and SkillBank",
            }

    # =========================================================================
    # SKILLS DATA MIGRATION
    # =========================================================================

    async def migrate_skills_to_enhanced_format(self, user_id: str) -> Dict[str, Any]:
        """
        Migrate UserProfile.skills JSON to EnhancedSkill format in SkillBank.
        """
        with self._get_session() as session:
            # Get user profile data
            user_profile = (
                session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
            )

            if not user_profile:
                raise ValueError(f"User profile not found for user_id: {user_id}")

            # Get existing skills from UserProfile
            existing_skills = user_profile.skills or []
            if isinstance(existing_skills, str):
                try:
                    existing_skills = json.loads(existing_skills)
                except json.JSONDecodeError:
                    existing_skills = []

            # Get or create skill bank
            skill_bank = await self.skill_bank_repo.get_or_create_skill_bank(user_id)

            # Convert legacy skills to enhanced format
            migrated_skills = []
            for skill_data in existing_skills:
                if isinstance(skill_data, str):
                    # Simple string skill
                    enhanced_skill = EnhancedSkill(
                        id=str(uuid4()),
                        name=skill_data,
                        category=SkillCategory.TECHNICAL,  # Default category
                        source=ContentSource.MANUAL,
                        created_at=datetime.utcnow(),
                    )
                elif isinstance(skill_data, dict):
                    # Structured skill data
                    enhanced_skill = EnhancedSkill(
                        id=str(uuid4()),
                        name=skill_data.get("name", "Unknown Skill"),
                        level=skill_data.get("level", "intermediate"),
                        category=self._map_skill_category(skill_data.get("category")),
                        subcategory=skill_data.get("category"),
                        years_experience=skill_data.get("years_experience"),
                        description=skill_data.get("description"),
                        is_featured=skill_data.get("is_featured", False),
                        source=ContentSource.IMPORTED,
                        created_at=datetime.utcnow(),
                    )
                else:
                    continue  # Skip invalid skill data

                migrated_skills.append(enhanced_skill)

            # Add migrated skills to skill bank
            for skill in migrated_skills:
                try:
                    await self.skill_bank_repo.add_skill(user_id, skill)
                except ValueError as e:
                    # Skip duplicate skills
                    if "already exists" not in str(e):
                        raise e

            return {
                "status": "success",
                "user_id": user_id,
                "migrated_skills_count": len(migrated_skills),
                "skills": [skill.dict() for skill in migrated_skills],
                "message": f"Successfully migrated {len(migrated_skills)} skills to enhanced format",
            }

    def _map_skill_category(self, old_category: Optional[str]) -> SkillCategory:
        """Map legacy skill categories to new SkillCategory enum."""
        if not old_category:
            return SkillCategory.TECHNICAL

        old_category_lower = old_category.lower()

        # Mapping common categories
        if any(
            term in old_category_lower
            for term in ["programming", "technical", "tech", "software", "development"]
        ):
            return SkillCategory.TECHNICAL
        elif any(
            term in old_category_lower
            for term in ["soft", "communication", "leadership", "management"]
        ):
            return SkillCategory.SOFT
        elif any(
            term in old_category_lower for term in ["language", "framework", "library"]
        ):
            return SkillCategory.FRAMEWORK
        elif any(term in old_category_lower for term in ["tool", "platform", "system"]):
            return SkillCategory.PLATFORM
        elif any(
            term in old_category_lower for term in ["domain", "industry", "business"]
        ):
            return SkillCategory.DOMAIN
        else:
            return SkillCategory.TECHNICAL  # Default fallback

    # =========================================================================
    # BIO TO SUMMARY MIGRATION
    # =========================================================================

    async def migrate_bio_to_summary_variations(self, user_id: str) -> Dict[str, Any]:
        """
        Migrate UserProfile.bio to SkillBank summary variations.
        """
        with self._get_session() as session:
            # Get user profile data
            user_profile = (
                session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
            )

            if not user_profile:
                raise ValueError(f"User profile not found for user_id: {user_id}")

            bio = user_profile.bio
            if not bio:
                return {
                    "status": "skipped",
                    "user_id": user_id,
                    "message": "No bio found in UserProfile",
                }

            # Get or create skill bank
            skill_bank = await self.skill_bank_repo.get_or_create_skill_bank(user_id)

            # Create summary variation from bio
            main_summary = SummaryVariation(
                id=str(uuid4()),
                title="Professional Summary",
                content=bio,
                tone="professional",
                length="standard",
                focus=ContentFocusType.GENERAL,
                source=ContentSource.IMPORTED,
                created_at=datetime.utcnow(),
            )

            # Set as default summary and add as variation
            await self.skill_bank_repo.update_skill_bank(
                user_id, {"default_summary": bio}
            )

            await self.skill_bank_repo.add_summary_variation(user_id, main_summary)

            return {
                "status": "success",
                "user_id": user_id,
                "bio_content": bio,
                "summary_variation": main_summary.dict(),
                "message": "Successfully migrated bio to summary variations",
            }

    # =========================================================================
    # COMPREHENSIVE MIGRATION
    # =========================================================================

    async def migrate_user_data_comprehensive(self, user_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive migration of all UserProfile data to SkillBank format.
        """
        results = {
            "user_id": user_id,
            "migration_timestamp": datetime.utcnow().isoformat(),
            "results": {},
        }

        try:
            # Migrate contact info
            contact_result = await self.migrate_contact_info_to_skillbank(user_id)
            results["results"]["contact_info"] = contact_result
        except Exception as e:
            results["results"]["contact_info"] = {"status": "error", "message": str(e)}

        try:
            # Migrate skills
            skills_result = await self.migrate_skills_to_enhanced_format(user_id)
            results["results"]["skills"] = skills_result
        except Exception as e:
            results["results"]["skills"] = {"status": "error", "message": str(e)}

        try:
            # Migrate bio to summaries
            bio_result = await self.migrate_bio_to_summary_variations(user_id)
            results["results"]["bio_to_summaries"] = bio_result
        except Exception as e:
            results["results"]["bio_to_summaries"] = {
                "status": "error",
                "message": str(e),
            }

        # Calculate overall success
        successful_migrations = sum(
            1
            for result in results["results"].values()
            if result.get("status") == "success"
        )
        total_migrations = len(results["results"])

        results["overall_status"] = (
            "success" if successful_migrations == total_migrations else "partial"
        )
        results["success_rate"] = f"{successful_migrations}/{total_migrations}"

        return results

    # =========================================================================
    # VALIDATION AND VERIFICATION
    # =========================================================================

    async def validate_migration_integrity(self, user_id: str) -> Dict[str, Any]:
        """
        Validate that data migration completed successfully and no data was lost.
        """
        with self._get_session() as session:
            # Get original UserProfile data
            user_profile = (
                session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
            )

            if not user_profile:
                return {"status": "error", "message": "User profile not found"}

            # Get migrated SkillBank data
            skill_bank = await self.skill_bank_repo.get_skill_bank(user_id)

            validation_results = {
                "user_id": user_id,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "checks": {},
            }

            # Check contact info accessibility
            validation_results["checks"]["contact_info"] = {
                "user_profile_has_contact": bool(
                    user_profile.first_name and user_profile.email
                ),
                "contact_fields_count": sum(
                    [
                        bool(user_profile.first_name),
                        bool(user_profile.last_name),
                        bool(user_profile.email),
                        bool(user_profile.phone),
                        bool(user_profile.city),
                        bool(user_profile.state),
                        bool(user_profile.linkedin_url),
                        bool(user_profile.portfolio_url),
                    ]
                ),
                "status": "accessible via UserProfile",
            }

            # Check skills migration
            original_skills_count = len(user_profile.skills or [])
            migrated_skills_count = (
                sum(len(skills) for skills in skill_bank.skills.values())
                if skill_bank
                else 0
            )

            validation_results["checks"]["skills_migration"] = {
                "original_skills_count": original_skills_count,
                "migrated_skills_count": migrated_skills_count,
                "migration_complete": migrated_skills_count >= original_skills_count,
                "status": (
                    "success"
                    if migrated_skills_count >= original_skills_count
                    else "incomplete"
                ),
            }

            # Check bio to summary migration
            has_bio = bool(user_profile.bio)
            has_summary = bool(
                skill_bank
                and (skill_bank.default_summary or skill_bank.summary_variations)
            )

            validation_results["checks"]["bio_to_summary"] = {
                "original_has_bio": has_bio,
                "skillbank_has_summary": has_summary,
                "migration_needed": has_bio,
                "migration_complete": not has_bio or has_summary,
                "status": "success" if (not has_bio or has_summary) else "incomplete",
            }

            # Overall validation status
            all_checks = [
                check["status"] for check in validation_results["checks"].values()
            ]
            validation_results["overall_status"] = (
                "success"
                if all(
                    status in ["success", "accessible via UserProfile"]
                    for status in all_checks
                )
                else "needs_attention"
            )

            return validation_results

    # =========================================================================
    # BATCH MIGRATION UTILITIES
    # =========================================================================

    async def migrate_all_users(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Migrate data for all users in the system.
        """
        with self._get_session() as session:
            query = session.query(UserProfileDB)
            if limit:
                query = query.limit(limit)

            users = query.all()

            batch_results = {
                "batch_timestamp": datetime.utcnow().isoformat(),
                "total_users": len(users),
                "processed_users": 0,
                "successful_migrations": 0,
                "failed_migrations": 0,
                "results": [],
            }

            for user in users:
                try:
                    user_result = await self.migrate_user_data_comprehensive(user.id)
                    batch_results["results"].append(user_result)
                    batch_results["processed_users"] += 1

                    if user_result["overall_status"] == "success":
                        batch_results["successful_migrations"] += 1
                    else:
                        batch_results["failed_migrations"] += 1

                except Exception as e:
                    batch_results["results"].append(
                        {"user_id": user.id, "status": "error", "message": str(e)}
                    )
                    batch_results["failed_migrations"] += 1
                    batch_results["processed_users"] += 1

            batch_results["success_rate"] = (
                batch_results["successful_migrations"]
                / batch_results["processed_users"]
                if batch_results["processed_users"] > 0
                else 0
            )

            return batch_results
