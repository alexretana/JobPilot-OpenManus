"""
Resume Generation Service
AI-powered content generation and optimization for resumes using external prompt templates.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.data.models import JobListingDB, UserProfileDB
from app.data.resume_models import (
    ContactInfo,
    Project,
    Resume,
    ResumeStatus,
    ResumeType,
    Skill,
    SkillLevel,
    WorkExperience,
)
from app.logger import logger
from app.services.llm_service import LLMService


class ResumeGenerationService:
    """Service for AI-powered resume content generation and optimization."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.prompts_dir = Path(__file__).parent.parent / "prompts" / "resume"

    def _load_prompt_template(self, template_name: str) -> str:
        """Load a prompt template from external file."""
        template_path = self.prompts_dir / f"{template_name}.md"
        try:
            with open(template_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt template not found: {template_path}")
            raise ValueError(f"Prompt template '{template_name}' not found")

    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with provided variables."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Missing required template variable: {e}")

    async def generate_professional_summary(
        self,
        candidate_background: str,
        target_role: str,
        industry: str,
        experience_level: str,
        key_skills: List[str],
        achievements: List[str],
        career_focus: str,
        company_type: str = "enterprise",
    ) -> Dict[str, Any]:
        """Generate multiple variations of professional summary."""
        try:
            template = self._load_prompt_template("generate_summary")
            prompt = self._format_prompt(
                template,
                candidate_background=candidate_background,
                target_role=target_role,
                industry=industry,
                experience_level=experience_level,
                key_skills=", ".join(key_skills),
                achievements="; ".join(achievements),
                career_focus=career_focus,
                company_type=company_type,
            )

            response = await self.llm_service.generate_content(prompt)

            # Parse JSON response
            try:
                result = json.loads(response)
                logger.info(
                    f"Generated {len(result.get('summaries', []))} summary variations"
                )
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                # Return a fallback summary
                return self._generate_fallback_summary(
                    target_role, key_skills, experience_level
                )

        except Exception as e:
            logger.error(f"Error generating professional summary: {e}")
            return self._generate_fallback_summary(
                target_role, key_skills, experience_level
            )

    async def generate_achievement_bullets(
        self,
        position_title: str,
        company_name: str,
        industry: str,
        role_level: str,
        basic_description: str,
        technologies: List[str],
        responsibilities: List[str],
        target_keywords: List[str],
    ) -> Dict[str, Any]:
        """Generate impactful achievement bullet points for a work experience."""
        try:
            template = self._load_prompt_template("generate_achievements")
            prompt = self._format_prompt(
                template,
                position_title=position_title,
                company_name=company_name,
                industry=industry,
                role_level=role_level,
                basic_description=basic_description,
                technologies=", ".join(technologies),
                responsibilities="; ".join(responsibilities),
                target_keywords=", ".join(target_keywords),
            )

            response = await self.llm_service.generate_content(prompt)

            try:
                result = json.loads(response)
                logger.info(
                    f"Generated {len(result.get('achievements', []))} achievement bullets"
                )
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                return self._generate_fallback_achievements(
                    position_title, technologies
                )

        except Exception as e:
            logger.error(f"Error generating achievement bullets: {e}")
            return self._generate_fallback_achievements(position_title, technologies)

    async def optimize_resume_for_job(
        self,
        base_resume: Resume,
        job_listing: JobListingDB,
        optimization_level: str = "moderate",
    ) -> Dict[str, Any]:
        """Optimize an existing resume for a specific job posting."""
        try:
            template = self._load_prompt_template("optimize_resume_content")

            # Prepare job data
            job_requirements = getattr(job_listing, "requirements", "") or ""
            preferred_skills = []
            if (
                hasattr(job_listing, "skills_preferred")
                and job_listing.skills_preferred
            ):
                preferred_skills = job_listing.skills_preferred

            # Convert resume to JSON for context
            base_resume_json = json.dumps(base_resume.dict(), indent=2, default=str)

            prompt = self._format_prompt(
                template,
                base_resume_json=base_resume_json,
                job_title=job_listing.title,
                company_name=job_listing.company,
                job_description=job_listing.description or "",
                job_requirements=job_requirements,
                preferred_skills=", ".join(preferred_skills),
                industry=getattr(job_listing, "industry", "") or "Technology",
            )

            response = await self.llm_service.generate_content(prompt)

            try:
                result = json.loads(response)
                logger.info(
                    f"Optimized resume for {job_listing.title} at {job_listing.company}"
                )
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse optimization response: {e}")
                return self._generate_fallback_optimization(base_resume)

        except Exception as e:
            logger.error(f"Error optimizing resume for job: {e}")
            return self._generate_fallback_optimization(base_resume)

    def create_optimized_resume(
        self, base_resume: Resume, optimization_result: Dict[str, Any], job_id: str
    ) -> Resume:
        """Create a new resume object with optimized content."""
        try:
            # Create new resume based on optimization
            optimized_resume = Resume(
                user_id=base_resume.user_id,
                title=f"{base_resume.title} - Optimized",
                resume_type=ResumeType.TAILORED,
                status=ResumeStatus.DRAFT,
                contact_info=base_resume.contact_info,
                summary=optimization_result.get(
                    "optimized_summary", base_resume.summary
                ),
                based_on_resume_id=base_resume.id,
                job_id=job_id,
                version=1,
            )

            # Process optimized work experience
            if "optimized_experience" in optimization_result:
                optimized_resume.work_experience = []
                for exp_data in optimization_result["optimized_experience"]:
                    experience = WorkExperience(**exp_data)
                    optimized_resume.work_experience.append(experience)
            else:
                optimized_resume.work_experience = base_resume.work_experience

            # Process optimized skills
            if "optimized_skills" in optimization_result:
                optimized_resume.skills = []
                for skill_data in optimization_result["optimized_skills"]:
                    skill = Skill(**skill_data)
                    optimized_resume.skills.append(skill)
            else:
                optimized_resume.skills = base_resume.skills

            # Process optimized projects
            if "optimized_projects" in optimization_result:
                optimized_resume.projects = []
                for proj_data in optimization_result["optimized_projects"]:
                    project = Project(**proj_data)
                    optimized_resume.projects.append(project)
            else:
                optimized_resume.projects = base_resume.projects

            # Keep other sections unchanged
            optimized_resume.education = base_resume.education
            optimized_resume.certifications = base_resume.certifications
            optimized_resume.custom_sections = base_resume.custom_sections
            optimized_resume.template_id = base_resume.template_id

            logger.info(
                f"Created optimized resume with {len(optimized_resume.work_experience)} experiences"
            )
            return optimized_resume

        except Exception as e:
            logger.error(f"Error creating optimized resume: {e}")
            # Return a copy of the base resume as fallback
            fallback = base_resume.copy()
            fallback.id = None
            fallback.title = f"{base_resume.title} - Optimized"
            fallback.resume_type = ResumeType.TAILORED
            fallback.job_id = job_id
            return fallback

    async def enhance_work_experience(
        self,
        experience: WorkExperience,
        target_keywords: List[str],
        industry: str = "Technology",
    ) -> WorkExperience:
        """Enhance a single work experience entry with better achievements."""
        try:
            result = await self.generate_achievement_bullets(
                position_title=experience.position,
                company_name=experience.company,
                industry=industry,
                role_level="mid",  # Could be inferred from experience
                basic_description=experience.description or "",
                technologies=experience.skills_used,
                responsibilities=experience.achievements,
                target_keywords=target_keywords,
            )

            if "achievements" in result and result["achievements"]:
                # Update achievements with generated bullets
                enhanced_achievements = [
                    achievement["bullet_point"]
                    for achievement in result["achievements"]
                ]

                enhanced_experience = experience.copy()
                enhanced_experience.achievements = enhanced_achievements

                # Extract additional skills mentioned in achievements
                all_keywords = []
                for achievement in result["achievements"]:
                    all_keywords.extend(achievement.get("keywords_used", []))

                # Add unique keywords to skills_used
                current_skills = set(enhanced_experience.skills_used)
                current_skills.update(all_keywords)
                enhanced_experience.skills_used = list(current_skills)

                return enhanced_experience
            else:
                return experience

        except Exception as e:
            logger.error(f"Error enhancing work experience: {e}")
            return experience

    def _generate_fallback_summary(
        self, target_role: str, key_skills: List[str], experience_level: str
    ) -> Dict[str, Any]:
        """Generate a basic fallback summary when LLM fails."""
        skills_text = ", ".join(key_skills[:5])  # Top 5 skills
        summary = f"Experienced {target_role} with strong background in {skills_text}. Proven track record of delivering high-quality solutions and collaborating effectively with cross-functional teams. Seeking to leverage technical expertise and {experience_level}-level experience in a challenging new role."

        return {
            "summaries": [
                {
                    "version": "fallback",
                    "summary": summary,
                    "word_count": len(summary.split()),
                    "key_strengths": key_skills[:3],
                    "target_roles": [target_role],
                }
            ],
            "customization_notes": [
                "Fallback summary - recommend manual customization"
            ],
            "ats_optimization": {
                "primary_keywords": key_skills[:3],
                "secondary_keywords": key_skills[3:6],
                "keyword_density": "standard",
            },
        }

    def _generate_fallback_achievements(
        self, position_title: str, technologies: List[str]
    ) -> Dict[str, Any]:
        """Generate basic fallback achievements when LLM fails."""
        tech_text = ", ".join(technologies[:3])
        achievements = [
            f"Developed and maintained applications using {tech_text}",
            "Collaborated with team members to deliver high-quality software solutions",
            f"Participated in code reviews and followed best practices for {position_title} role",
        ]

        return {
            "achievements": [
                {
                    "bullet_point": achievement,
                    "category": "general",
                    "impact_type": "collaboration",
                    "quantified_metrics": [],
                    "keywords_used": technologies[:2],
                }
                for achievement in achievements
            ],
            "suggested_variations": [],
            "missing_quantification_opportunities": [
                "Add specific metrics and numbers to quantify impact"
            ],
        }

    def _generate_fallback_optimization(self, base_resume: Resume) -> Dict[str, Any]:
        """Generate basic fallback optimization when LLM fails."""
        return {
            "optimized_summary": base_resume.summary,
            "optimized_experience": [exp.dict() for exp in base_resume.work_experience],
            "optimized_skills": [skill.dict() for skill in base_resume.skills],
            "optimized_projects": [proj.dict() for proj in base_resume.projects],
            "keyword_analysis": {
                "keywords_added": [],
                "keywords_emphasized": [],
                "missing_keywords": [],
                "ats_score_prediction": 75,
            },
            "optimization_notes": [
                "Fallback optimization applied - manual review recommended"
            ],
        }


class ResumeContentBuilder:
    """Builder class for constructing resumes from user profile data."""

    def __init__(self, generation_service: ResumeGenerationService):
        self.generation_service = generation_service

    async def build_from_profile(
        self,
        user_profile: UserProfileDB,
        target_role: Optional[str] = None,
        target_industry: Optional[str] = None,
    ) -> Resume:
        """Build a comprehensive resume from user profile data."""
        try:
            # Extract basic information
            contact_info = ContactInfo(
                full_name=f"{user_profile.first_name} {user_profile.last_name}",
                email=user_profile.email,
                phone=user_profile.phone,
                location=getattr(user_profile, "location", None),
            )

            # Determine role and industry
            role = target_role or user_profile.current_title or "Professional"
            industry = target_industry or "Technology"

            # Generate professional summary
            key_skills = user_profile.skills or []
            experience_level = self._determine_experience_level(user_profile)

            summary_result = (
                await self.generation_service.generate_professional_summary(
                    candidate_background=user_profile.bio or "",
                    target_role=role,
                    industry=industry,
                    experience_level=experience_level,
                    key_skills=key_skills,
                    achievements=[],
                    career_focus=role,
                )
            )

            # Use the first generated summary
            summary = ""
            if summary_result.get("summaries"):
                summary = summary_result["summaries"][0]["summary"]

            # Create skills objects
            skills = []
            for skill_name in key_skills:
                skill = Skill(
                    name=skill_name,
                    level=SkillLevel.INTERMEDIATE,
                    category="Technical Skills",
                    is_featured=True,
                )
                skills.append(skill)

            # Create basic resume
            resume = Resume(
                user_id=user_profile.id,
                title=f"{role} Resume",
                resume_type=ResumeType.BASE,
                status=ResumeStatus.DRAFT,
                contact_info=contact_info,
                summary=summary,
                work_experience=[],
                education=[],
                skills=skills,
                projects=[],
                certifications=[],
            )

            logger.info(
                f"Built base resume for {user_profile.first_name} {user_profile.last_name}"
            )
            return resume

        except Exception as e:
            logger.error(f"Error building resume from profile: {e}")
            raise

    def _determine_experience_level(self, user_profile: UserProfileDB) -> str:
        """Determine experience level from user profile."""
        # This could be enhanced with more sophisticated logic
        # For now, return a default
        return "mid-level"
