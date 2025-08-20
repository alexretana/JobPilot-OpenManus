"""
Resume Orchestrator Service
Orchestrates the complete resume generation pipeline combining AI content generation and PDF export.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.data.models import JobListingDB, UserProfileDB
from app.data.resume_models import Resume
from app.data.resume_repository import ResumeRepository
from app.logger import logger
from app.services.llm_service import LLMService, create_llm_service
from app.services.pdf_generation_service import (
    PDFGenerationService,
    ResumeExportService,
)
from app.services.resume_generation_service import (
    ResumeContentBuilder,
    ResumeGenerationService,
)


class ResumeGenerationRequest:
    """Request model for complete resume generation."""

    def __init__(
        self,
        user_id: str,
        generation_type: str = "optimize",  # "optimize", "create", "enhance"
        base_resume_id: Optional[str] = None,
        job_id: Optional[str] = None,
        job_description: Optional[str] = None,
        target_role: Optional[str] = None,
        target_industry: Optional[str] = None,
        optimization_level: str = "moderate",  # "light", "moderate", "aggressive"
        export_formats: List[str] = None,  # ["pdf", "json", "yaml", "txt"]
        pdf_template: str = "moderncv",
        theme_options: Optional[Dict[str, Any]] = None,
        custom_instructions: Optional[str] = None,
    ):
        self.user_id = user_id
        self.generation_type = generation_type
        self.base_resume_id = base_resume_id
        self.job_id = job_id
        self.job_description = job_description
        self.target_role = target_role
        self.target_industry = target_industry
        self.optimization_level = optimization_level
        self.export_formats = export_formats or ["pdf"]
        self.pdf_template = pdf_template
        self.theme_options = theme_options or {}
        self.custom_instructions = custom_instructions


class ResumeGenerationResult:
    """Result model for complete resume generation."""

    def __init__(self):
        self.success = False
        self.resume: Optional[Resume] = None
        self.resume_id: Optional[str] = None
        self.optimization_analysis: Optional[Dict[str, Any]] = None
        self.generated_files: Dict[str, Dict[str, Any]] = {}
        self.generation_metadata: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.processing_time: float = 0.0
        self.generation_timestamp: str = datetime.now().isoformat()


class ResumeOrchestratorService:
    """Orchestrates the complete resume generation and export pipeline."""

    def __init__(
        self,
        resume_repository: ResumeRepository,
        llm_service: Optional[LLMService] = None,
        output_dir: Optional[str] = None,
    ):
        self.resume_repository = resume_repository
        self.llm_service = llm_service or create_llm_service()

        # Initialize sub-services
        self.generation_service = ResumeGenerationService(self.llm_service)
        self.content_builder = ResumeContentBuilder(self.generation_service)
        self.pdf_service = PDFGenerationService(output_dir)
        self.export_service = ResumeExportService(self.pdf_service)

        logger.info("Resume orchestrator service initialized")

    async def generate_complete_resume(
        self, request: ResumeGenerationRequest
    ) -> ResumeGenerationResult:
        """Generate a complete resume with content optimization and export."""

        start_time = datetime.now()
        result = ResumeGenerationResult()

        try:
            logger.info(
                f"Starting complete resume generation for user {request.user_id}"
            )

            # Step 1: Generate or optimize resume content
            if request.generation_type == "create":
                resume, analysis = await self._create_new_resume(request)
            elif request.generation_type == "optimize":
                resume, analysis = await self._optimize_existing_resume(request)
            elif request.generation_type == "enhance":
                resume, analysis = await self._enhance_resume_content(request)
            else:
                raise ValueError(f"Unknown generation type: {request.generation_type}")

            if not resume:
                result.errors.append("Failed to generate resume content")
                return result

            result.resume = resume
            result.optimization_analysis = analysis

            # Step 2: Save resume to database
            resume_db = await self.resume_repository.create_resume(resume)
            result.resume_id = resume_db.id

            logger.info(f"Resume content generated and saved: {resume_db.id}")

            # Step 3: Export in requested formats
            export_tasks = []
            for export_format in request.export_formats:
                task = self._export_resume_format(
                    resume=resume,
                    export_format=export_format,
                    template_name=request.pdf_template,
                    options=request.theme_options,
                )
                export_tasks.append((export_format, task))

            # Execute export tasks concurrently
            for export_format, task in export_tasks:
                try:
                    export_result = await task
                    result.generated_files[export_format] = export_result

                    if export_result.get("success"):
                        logger.info(f"Successfully exported resume as {export_format}")
                    else:
                        result.warnings.append(
                            f"Export to {export_format} failed: {export_result.get('error', 'Unknown error')}"
                        )

                except Exception as e:
                    result.warnings.append(
                        f"Export to {export_format} failed: {str(e)}"
                    )

            # Step 4: Update skill bank if resume was created/optimized
            if request.generation_type in ["create", "optimize"]:
                try:
                    await self.resume_repository.update_skill_bank_from_resume(
                        request.user_id, resume
                    )
                    logger.info("Updated skill bank from generated resume")
                except Exception as e:
                    result.warnings.append(f"Failed to update skill bank: {str(e)}")

            # Step 5: Generate metadata
            result.generation_metadata = {
                "generation_type": request.generation_type,
                "optimization_level": request.optimization_level,
                "export_formats": request.export_formats,
                "pdf_template": request.pdf_template,
                "llm_provider": self.llm_service.get_provider_info(),
                "total_sections": len(
                    [
                        s
                        for s in [
                            resume.work_experience,
                            resume.education,
                            resume.skills,
                            resume.projects,
                            resume.certifications,
                        ]
                        if s
                    ]
                ),
                "content_stats": self._analyze_resume_content(resume),
            }

            result.success = True
            result.processing_time = (datetime.now() - start_time).total_seconds()

            logger.info(
                f"Complete resume generation finished in {result.processing_time:.2f}s"
            )
            return result

        except Exception as e:
            result.errors.append(f"Resume generation failed: {str(e)}")
            result.processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Resume generation failed: {e}")
            return result

    async def _create_new_resume(
        self, request: ResumeGenerationRequest
    ) -> Tuple[Optional[Resume], Optional[Dict[str, Any]]]:
        """Create a new resume from user profile."""
        try:
            # Get user profile
            user_profile = (
                self.resume_repository.session.query(UserProfileDB)
                .filter(UserProfileDB.id == request.user_id)
                .first()
            )

            if not user_profile:
                raise ValueError(f"User profile not found: {request.user_id}")

            # Build base resume from profile
            resume = await self.content_builder.build_from_profile(
                user_profile=user_profile,
                target_role=request.target_role,
                target_industry=request.target_industry,
            )

            # Generate analysis
            analysis = {
                "creation_method": "profile_based",
                "generated_sections": ["contact_info", "summary", "skills"],
                "completeness_score": 65.0,  # Basic resume from profile
                "recommendations": [
                    "Add work experience entries",
                    "Include education details",
                    "Add projects and certifications",
                ],
            }

            return resume, analysis

        except Exception as e:
            logger.error(f"Error creating new resume: {e}")
            return None, None

    async def _optimize_existing_resume(
        self, request: ResumeGenerationRequest
    ) -> Tuple[Optional[Resume], Optional[Dict[str, Any]]]:
        """Optimize an existing resume for a specific job."""
        try:
            # Get base resume
            if not request.base_resume_id:
                raise ValueError("Base resume ID required for optimization")

            base_resume = await self.resume_repository.get_resume(
                request.base_resume_id, request.user_id
            )

            if not base_resume:
                raise ValueError(f"Base resume not found: {request.base_resume_id}")

            # Get job listing if job_id provided
            job_listing = None
            if request.job_id:
                job_listing = (
                    self.resume_repository.session.query(JobListingDB)
                    .filter(JobListingDB.id == request.job_id)
                    .first()
                )

                if not job_listing:
                    logger.warning(f"Job listing not found: {request.job_id}")

            # Optimize resume content
            if job_listing:
                optimization_result = (
                    await self.generation_service.optimize_resume_for_job(
                        base_resume=base_resume,
                        job_listing=job_listing,
                        optimization_level=request.optimization_level,
                    )
                )
            else:
                # Create a mock job listing from job description
                if request.job_description:
                    optimization_result = await self._optimize_with_description(
                        base_resume,
                        request.job_description,
                        request.target_role or "Software Engineer",
                    )
                else:
                    raise ValueError(
                        "Either job_id or job_description required for optimization"
                    )

            # Create optimized resume
            optimized_resume = self.generation_service.create_optimized_resume(
                base_resume=base_resume,
                optimization_result=optimization_result,
                job_id=request.job_id or "custom",
            )

            return optimized_resume, optimization_result

        except Exception as e:
            logger.error(f"Error optimizing resume: {e}")
            return None, None

    async def _optimize_with_description(
        self, base_resume: Resume, job_description: str, job_title: str
    ) -> Dict[str, Any]:
        """Optimize resume using job description text."""

        # Create a mock job listing object
        class MockJobListing:
            def __init__(self, title: str, description: str):
                self.title = title
                self.company = "Target Company"
                self.description = description
                self.requirements = ""
                self.skills_preferred = []

        mock_job = MockJobListing(job_title, job_description)

        return await self.generation_service.optimize_resume_for_job(
            base_resume=base_resume, job_listing=mock_job
        )

    async def _enhance_resume_content(
        self, request: ResumeGenerationRequest
    ) -> Tuple[Optional[Resume], Optional[Dict[str, Any]]]:
        """Enhance existing resume content with better achievements."""
        try:
            # Get base resume
            if not request.base_resume_id:
                raise ValueError("Base resume ID required for enhancement")

            base_resume = await self.resume_repository.get_resume(
                request.base_resume_id, request.user_id
            )

            if not base_resume:
                raise ValueError(f"Base resume not found: {request.base_resume_id}")

            # Enhance work experiences
            enhanced_resume = base_resume.copy()
            enhanced_resume.id = None  # Will get new ID when saved
            enhanced_resume.title = f"{base_resume.title} - Enhanced"

            target_keywords = []
            if request.job_description:
                # Extract keywords from job description
                # This is a simple implementation - could be enhanced with NLP
                common_keywords = [
                    "python",
                    "javascript",
                    "react",
                    "aws",
                    "docker",
                    "kubernetes",
                    "leadership",
                    "agile",
                    "scrum",
                    "ci/cd",
                    "api",
                    "microservices",
                ]
                target_keywords = [
                    kw
                    for kw in common_keywords
                    if kw.lower() in request.job_description.lower()
                ]

            # Enhance each work experience
            enhanced_experiences = []
            for exp in enhanced_resume.work_experience:
                try:
                    enhanced_exp = (
                        await self.generation_service.enhance_work_experience(
                            experience=exp,
                            target_keywords=target_keywords,
                            industry=request.target_industry or "Technology",
                        )
                    )
                    enhanced_experiences.append(enhanced_exp)
                except Exception as e:
                    logger.warning(
                        f"Failed to enhance experience at {exp.company}: {e}"
                    )
                    enhanced_experiences.append(
                        exp
                    )  # Use original if enhancement fails

            enhanced_resume.work_experience = enhanced_experiences

            # Generate analysis
            analysis = {
                "enhancement_method": "ai_powered",
                "enhanced_sections": ["work_experience"],
                "experiences_enhanced": len(enhanced_experiences),
                "target_keywords_used": target_keywords,
                "recommendations": [
                    "Review enhanced achievements for accuracy",
                    "Consider adding quantified metrics where possible",
                ],
            }

            return enhanced_resume, analysis

        except Exception as e:
            logger.error(f"Error enhancing resume: {e}")
            return None, None

    async def _export_resume_format(
        self,
        resume: Resume,
        export_format: str,
        template_name: str,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Export resume in a specific format."""
        try:
            return await self.export_service.export_resume(
                resume=resume,
                export_format=export_format,
                template_name=template_name,
                options=options,
            )
        except Exception as e:
            logger.error(f"Error exporting resume as {export_format}: {e}")
            return {"success": False, "error": str(e), "format": export_format}

    def _analyze_resume_content(self, resume: Resume) -> Dict[str, Any]:
        """Analyze resume content for metadata."""
        try:
            total_experience_years = 0
            for exp in resume.work_experience:
                if exp.start_date and exp.end_date:
                    years = (exp.end_date - exp.start_date).days / 365.25
                    total_experience_years += years
                elif exp.start_date and exp.is_current:
                    years = (datetime.now().date() - exp.start_date).days / 365.25
                    total_experience_years += years

            skill_categories = {}
            for skill in resume.skills:
                category = skill.category or "Other"
                skill_categories[category] = skill_categories.get(category, 0) + 1

            return {
                "total_work_experiences": len(resume.work_experience),
                "total_experience_years": round(total_experience_years, 1),
                "total_education_entries": len(resume.education),
                "total_skills": len(resume.skills),
                "skill_categories": skill_categories,
                "total_projects": len(resume.projects),
                "total_certifications": len(resume.certifications),
                "has_summary": bool(resume.summary),
                "summary_word_count": (
                    len(resume.summary.split()) if resume.summary else 0
                ),
                "featured_skills": len([s for s in resume.skills if s.is_featured]),
            }

        except Exception as e:
            logger.error(f"Error analyzing resume content: {e}")
            return {"error": "Content analysis failed"}

    async def batch_generate_resumes(
        self, requests: List[ResumeGenerationRequest], max_concurrent: int = 3
    ) -> List[ResumeGenerationResult]:
        """Generate multiple resumes concurrently with rate limiting."""

        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_single(
            request: ResumeGenerationRequest,
        ) -> ResumeGenerationResult:
            async with semaphore:
                return await self.generate_complete_resume(request)

        tasks = [generate_single(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions in results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ResumeGenerationResult()
                error_result.errors.append(f"Batch generation failed: {str(result)}")
                final_results.append(error_result)
                logger.error(f"Batch generation failed for request {i}: {result}")
            else:
                final_results.append(result)

        logger.info(
            f"Batch generation completed: {len(final_results)} resumes processed"
        )
        return final_results

    async def get_generation_templates(self) -> Dict[str, Any]:
        """Get available templates and options for resume generation."""
        try:
            pdf_templates = self.pdf_service.get_available_templates()

            return {
                "pdf_templates": pdf_templates,
                "export_formats": ["pdf", "json", "yaml", "txt"],
                "optimization_levels": [
                    {"value": "light", "description": "Minor keyword optimization"},
                    {
                        "value": "moderate",
                        "description": "Balanced content and keyword optimization",
                    },
                    {
                        "value": "aggressive",
                        "description": "Comprehensive content rewriting",
                    },
                ],
                "generation_types": [
                    {
                        "value": "create",
                        "description": "Create new resume from profile",
                    },
                    {
                        "value": "optimize",
                        "description": "Optimize existing resume for job",
                    },
                    {"value": "enhance", "description": "Enhance resume achievements"},
                ],
                "llm_provider": self.llm_service.get_provider_info(),
            }

        except Exception as e:
            logger.error(f"Error getting generation templates: {e}")
            return {
                "error": "Failed to load templates",
                "pdf_templates": [
                    {"name": "moderncv", "description": "Default template"}
                ],
                "export_formats": ["pdf"],
            }


# Factory function
def create_resume_orchestrator(
    resume_repository: ResumeRepository,
    llm_provider: str = "mock",
    output_dir: Optional[str] = None,
    **llm_kwargs,
) -> ResumeOrchestratorService:
    """Create a resume orchestrator service with specified configuration."""

    llm_service = create_llm_service(provider=llm_provider, **llm_kwargs)

    return ResumeOrchestratorService(
        resume_repository=resume_repository,
        llm_service=llm_service,
        output_dir=output_dir,
    )
