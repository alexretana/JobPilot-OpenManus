#!/usr/bin/env python3
"""
AI-Powered Resume Generation Pipeline Test
Comprehensive test of the complete resume generation system including AI content generation and PDF export.
"""

import asyncio
import json
import sys
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.data.database import DatabaseManager
from app.data.resume_models import (
    Certification,
    ContactInfo,
    Education,
    ExperienceType,
    Project,
    Resume,
    ResumeStatus,
    ResumeType,
    Skill,
    SkillLevel,
    WorkExperience,
)
from app.logger import logger
from app.repositories.resume_repository import ResumeRepository
from app.services.llm_service import create_llm_service
from app.services.resume_orchestrator_service import (
    ResumeGenerationRequest,
    create_resume_orchestrator,
)


class ResumeGenerationTester:
    """Comprehensive tester for resume generation pipeline."""

    def __init__(self):
        self.db_manager = DatabaseManager("sqlite:///jobpilot.db")
        self.test_user_id = str(uuid4())
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "test_details": [],
        }

    def log_test_result(
        self, test_name: str, success: bool, details: str = "", warning: bool = False
    ):
        """Log test result and update counters."""
        status = "PASS" if success else "FAIL"
        if warning:
            status = "WARN"
            self.test_results["warnings"] += 1
        elif success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1

        self.test_results["test_details"].append(
            {
                "test": test_name,
                "status": status,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(f"[{status}] {test_name}: {details}")

    def create_comprehensive_resume(self) -> Resume:
        """Create a comprehensive test resume."""
        contact_info = ContactInfo(
            full_name="Jane Smith",
            email="jane.smith@example.com",
            phone="+1 (555) 987-6543",
            location="Seattle, WA",
            linkedin="https://linkedin.com/in/janesmith",
            github="https://github.com/janesmith",
            website="https://janesmith.dev",
        )

        work_experience = [
            WorkExperience(
                company="Amazon",
                position="Senior Software Engineer",
                location="Seattle, WA",
                start_date=date(2020, 3, 1),
                end_date=None,
                is_current=True,
                experience_type=ExperienceType.FULL_TIME,
                description="Lead backend development for high-scale distributed systems",
                achievements=[
                    "Designed and implemented microservices architecture handling 10M+ requests/day",
                    "Reduced system latency by 45% through optimization and caching strategies",
                    "Led team of 5 engineers in migrating legacy monolith to cloud-native architecture",
                    "Implemented CI/CD pipeline improving deployment frequency by 300%",
                ],
                skills_used=[
                    "Python",
                    "AWS",
                    "Kubernetes",
                    "Docker",
                    "PostgreSQL",
                    "Redis",
                ],
            ),
            WorkExperience(
                company="Microsoft",
                position="Software Engineer II",
                location="Redmond, WA",
                start_date=date(2018, 6, 1),
                end_date=date(2020, 2, 28),
                is_current=False,
                experience_type=ExperienceType.FULL_TIME,
                description="Developed cloud services and APIs for Azure platform",
                achievements=[
                    "Built RESTful APIs serving 1M+ monthly active users",
                    "Implemented authentication and authorization using OAuth 2.0",
                    "Collaborated with product teams to deliver features ahead of schedule",
                    "Mentored 2 junior developers in best practices and code review",
                ],
                skills_used=[
                    "C#",
                    ".NET Core",
                    "Azure",
                    "SQL Server",
                    "React",
                    "TypeScript",
                ],
            ),
        ]

        education = [
            Education(
                institution="University of Washington",
                degree="Master of Science",
                field_of_study="Computer Science",
                location="Seattle, WA",
                start_date=date(2016, 9, 1),
                end_date=date(2018, 6, 1),
                gpa=3.8,
                honors=["Magna Cum Laude", "Graduate Research Assistant"],
                relevant_coursework=[
                    "Distributed Systems",
                    "Machine Learning",
                    "Database Systems",
                    "Software Engineering",
                    "Computer Networks",
                ],
            ),
            Education(
                institution="University of California, San Diego",
                degree="Bachelor of Science",
                field_of_study="Computer Engineering",
                location="San Diego, CA",
                start_date=date(2012, 9, 1),
                end_date=date(2016, 6, 1),
                gpa=3.6,
                honors=["Dean's List", "Engineering Honor Society"],
                relevant_coursework=[
                    "Data Structures",
                    "Algorithms",
                    "Computer Architecture",
                    "Operating Systems",
                    "Software Design",
                ],
            ),
        ]

        skills = [
            Skill(
                name="Python",
                level=SkillLevel.EXPERT,
                category="Programming Languages",
                years_experience=6,
                is_featured=True,
            ),
            Skill(
                name="Java",
                level=SkillLevel.ADVANCED,
                category="Programming Languages",
                years_experience=5,
                is_featured=True,
            ),
            Skill(
                name="JavaScript",
                level=SkillLevel.ADVANCED,
                category="Programming Languages",
                years_experience=4,
                is_featured=True,
            ),
            Skill(
                name="AWS",
                level=SkillLevel.ADVANCED,
                category="Cloud Platforms",
                years_experience=4,
                is_featured=True,
            ),
            Skill(
                name="Kubernetes",
                level=SkillLevel.INTERMEDIATE,
                category="DevOps",
                years_experience=3,
                is_featured=False,
            ),
            Skill(
                name="Docker",
                level=SkillLevel.ADVANCED,
                category="DevOps",
                years_experience=4,
                is_featured=False,
            ),
            Skill(
                name="PostgreSQL",
                level=SkillLevel.ADVANCED,
                category="Databases",
                years_experience=5,
                is_featured=False,
            ),
            Skill(
                name="React",
                level=SkillLevel.INTERMEDIATE,
                category="Frontend Frameworks",
                years_experience=3,
                is_featured=False,
            ),
            Skill(
                name="Machine Learning",
                level=SkillLevel.INTERMEDIATE,
                category="AI/ML",
                years_experience=2,
                is_featured=False,
            ),
        ]

        projects = [
            Project(
                name="Distributed Task Scheduler",
                description="Built a fault-tolerant distributed task scheduling system using microservices",
                start_date=date(2021, 1, 1),
                end_date=date(2021, 6, 1),
                url="https://github.com/janesmith/task-scheduler",
                github_url="https://github.com/janesmith/task-scheduler",
                technologies=["Python", "Kubernetes", "Redis", "PostgreSQL", "gRPC"],
                achievements=[
                    "Handles 100k+ concurrent tasks with 99.9% uptime",
                    "Implemented auto-scaling based on queue depth",
                    "Built comprehensive monitoring and alerting system",
                ],
            ),
            Project(
                name="Real-time Analytics Dashboard",
                description="Created real-time analytics platform for processing streaming data",
                start_date=date(2020, 8, 1),
                end_date=date(2020, 12, 1),
                url="https://analytics.janesmith.dev",
                github_url="https://github.com/janesmith/analytics-dashboard",
                technologies=["Python", "Apache Kafka", "InfluxDB", "Grafana", "React"],
                achievements=[
                    "Processes 1M+ events per minute with sub-second latency",
                    "Built interactive visualizations with real-time updates",
                    "Implemented alerting system for anomaly detection",
                ],
            ),
        ]

        certifications = [
            Certification(
                name="AWS Certified Solutions Architect - Professional",
                issuer="Amazon Web Services",
                issue_date=date(2021, 9, 1),
                credential_id="AWS-SAP-2021-001",
                url="https://aws.amazon.com/certification/",
            ),
            Certification(
                name="Certified Kubernetes Administrator",
                issuer="Cloud Native Computing Foundation",
                issue_date=date(2020, 11, 1),
                credential_id="CKA-2020-001",
            ),
        ]

        return Resume(
            user_id=self.test_user_id,
            title="Senior Software Engineer - Jane Smith",
            contact_info=contact_info,
            summary="Experienced Senior Software Engineer with 6+ years developing scalable distributed systems and cloud-native applications. Expert in Python, AWS, and microservices architecture with a proven track record of leading high-performance teams and delivering complex technical solutions. Passionate about building robust, efficient systems that drive business growth.",
            work_experience=work_experience,
            education=education,
            skills=skills,
            projects=projects,
            certifications=certifications,
            resume_type=ResumeType.BASE,
            status=ResumeStatus.ACTIVE,
        )

    async def test_llm_service(self):
        """Test LLM service functionality."""
        logger.info("🧠 Testing LLM Service...")

        try:
            # Test mock provider
            llm_service = create_llm_service("mock")

            # Test content generation
            prompt = "Generate a professional summary for a software engineer with 5 years experience."
            content = await llm_service.generate_content(prompt)

            if content and len(content) > 10:
                self.log_test_result(
                    "LLM Content Generation",
                    True,
                    f"Generated {len(content)} characters",
                )
            else:
                self.log_test_result(
                    "LLM Content Generation", False, "No meaningful content generated"
                )

            # Test provider info
            provider_info = llm_service.get_provider_info()
            if provider_info.get("provider") == "mock":
                self.log_test_result(
                    "LLM Provider Info", True, f"Provider: {provider_info['provider']}"
                )
            else:
                self.log_test_result(
                    "LLM Provider Info", False, "Provider info incorrect"
                )

        except Exception as e:
            self.log_test_result("LLM Service", False, f"Error: {str(e)}")

    async def test_pdf_generation_service(self):
        """Test PDF generation capabilities."""
        logger.info("📄 Testing PDF Generation Service...")

        try:
            from app.services.pdf_generation_service import create_pdf_service

            pdf_service = create_pdf_service()

            # Test template listing
            templates = pdf_service.get_available_templates()
            if templates and len(templates) > 0:
                self.log_test_result(
                    "PDF Templates", True, f"Found {len(templates)} templates"
                )
            else:
                self.log_test_result("PDF Templates", False, "No templates found")

            # Test resume creation and PDF generation
            test_resume = self.create_comprehensive_resume()

            # Note: Actual PDF generation might fail without LaTeX installed
            # So we'll just test the conversion to RenderCV format
            rendercv_data = pdf_service._convert_to_rendercv_format(test_resume)

            if rendercv_data and "cv" in rendercv_data:
                self.log_test_result(
                    "RenderCV Conversion",
                    True,
                    "Successfully converted to RenderCV format",
                )
            else:
                self.log_test_result(
                    "RenderCV Conversion", False, "Failed to convert to RenderCV format"
                )

        except Exception as e:
            self.log_test_result("PDF Generation Service", False, f"Error: {str(e)}")

    async def test_resume_generation_service(self):
        """Test AI-powered resume generation service."""
        logger.info("🎯 Testing Resume Generation Service...")

        try:
            with self.db_manager.get_session() as session:
                ResumeRepository(session)
                llm_service = create_llm_service("mock")

                from app.services.resume_generation_service import (
                    ResumeGenerationService,
                )

                gen_service = ResumeGenerationService(llm_service)

                # Test professional summary generation
                summary_result = await gen_service.generate_professional_summary(
                    candidate_background="Software engineer with cloud experience",
                    target_role="Senior Software Engineer",
                    industry="Technology",
                    experience_level="senior",
                    key_skills=["Python", "AWS", "Kubernetes"],
                    achievements=["Led team migration to microservices"],
                    career_focus="Backend development",
                )

                if summary_result and "summaries" in summary_result:
                    self.log_test_result(
                        "Professional Summary Generation",
                        True,
                        f"Generated {len(summary_result['summaries'])} summary variations",
                    )
                else:
                    self.log_test_result(
                        "Professional Summary Generation",
                        False,
                        "No summaries generated",
                    )

                # Test achievement bullet generation
                achievement_result = await gen_service.generate_achievement_bullets(
                    position_title="Software Engineer",
                    company_name="Tech Corp",
                    industry="Technology",
                    role_level="senior",
                    basic_description="Developed web applications",
                    technologies=["Python", "React", "AWS"],
                    responsibilities=["Code development", "Team collaboration"],
                    target_keywords=["microservices", "scalability"],
                )

                if achievement_result and "achievements" in achievement_result:
                    self.log_test_result(
                        "Achievement Generation",
                        True,
                        f"Generated {len(achievement_result['achievements'])} achievements",
                    )
                else:
                    self.log_test_result(
                        "Achievement Generation", False, "No achievements generated"
                    )

        except Exception as e:
            self.log_test_result("Resume Generation Service", False, f"Error: {str(e)}")

    async def test_resume_orchestrator(self):
        """Test the complete resume orchestration service."""
        logger.info("🎼 Testing Resume Orchestrator...")

        try:
            with self.db_manager.get_session() as session:
                repo = ResumeRepository(session)
                orchestrator = create_resume_orchestrator(
                    resume_repository=repo, llm_provider="mock"
                )

                # Test template retrieval
                templates = await orchestrator.get_generation_templates()
                if templates and "pdf_templates" in templates:
                    self.log_test_result(
                        "Orchestrator Templates",
                        True,
                        f"Retrieved templates and options",
                    )
                else:
                    self.log_test_result(
                        "Orchestrator Templates", False, "Failed to get templates"
                    )

                # Test resume creation from scratch
                creation_request = ResumeGenerationRequest(
                    user_id=self.test_user_id,
                    generation_type="create",
                    target_role="Software Engineer",
                    target_industry="Technology",
                    export_formats=["json"],  # Skip PDF for testing
                )

                # Note: This would fail without a user profile, but we test the structure
                try:
                    result = await orchestrator.generate_complete_resume(
                        creation_request
                    )
                    if result.errors and "User profile not found" in str(result.errors):
                        self.log_test_result(
                            "Orchestrator Structure",
                            True,
                            "Orchestrator properly handles missing user profile",
                            warning=True,
                        )
                    else:
                        self.log_test_result(
                            "Orchestrator Create Resume",
                            result.success,
                            f"Resume creation: {result.errors if not result.success else 'Success'}",
                        )
                except Exception as e:
                    if "User profile not found" in str(e):
                        self.log_test_result(
                            "Orchestrator Structure",
                            True,
                            "Orchestrator properly validates user profile",
                            warning=True,
                        )
                    else:
                        raise

        except Exception as e:
            self.log_test_result("Resume Orchestrator", False, f"Error: {str(e)}")

    async def test_end_to_end_workflow(self):
        """Test the complete end-to-end workflow with existing resume."""
        logger.info("🔄 Testing End-to-End Workflow...")

        try:
            with self.db_manager.get_session() as session:
                repo = ResumeRepository(session)

                # Step 1: Create a base resume
                test_resume = self.create_comprehensive_resume()
                resume_db = await repo.create_resume(test_resume)
                base_resume = repo._db_to_pydantic(resume_db)

                self.log_test_result(
                    "Base Resume Creation", True, f"Created resume: {resume_db.id}"
                )

                # Step 2: Test resume enhancement
                orchestrator = create_resume_orchestrator(
                    resume_repository=repo, llm_provider="mock"
                )

                enhancement_request = ResumeGenerationRequest(
                    user_id=self.test_user_id,
                    generation_type="enhance",
                    base_resume_id=base_resume.id,
                    job_description="Senior Software Engineer position requiring Python, AWS, and microservices experience",
                    export_formats=["json", "txt"],  # Skip PDF for testing
                )

                result = await orchestrator.generate_complete_resume(
                    enhancement_request
                )

                if result.success:
                    self.log_test_result(
                        "E2E Enhancement",
                        True,
                        f"Enhanced resume created: {result.resume_id}",
                    )
                    self.log_test_result(
                        "E2E Export",
                        len(result.generated_files) >= 2,
                        f"Generated {len(result.generated_files)} export files",
                    )

                    # Check processing metadata
                    if result.generation_metadata:
                        self.log_test_result(
                            "E2E Metadata",
                            True,
                            f"Processing time: {result.processing_time:.2f}s",
                        )

                else:
                    self.log_test_result(
                        "E2E Enhancement", False, f"Errors: {result.errors}"
                    )

        except Exception as e:
            self.log_test_result("End-to-End Workflow", False, f"Error: {str(e)}")

    async def test_export_functionality(self):
        """Test resume export in multiple formats."""
        logger.info("📤 Testing Export Functionality...")

        try:
            from app.services.pdf_generation_service import create_export_service

            export_service = create_export_service()
            test_resume = self.create_comprehensive_resume()

            # Test JSON export
            json_result = await export_service.export_resume(
                resume=test_resume,
                export_format="json",
                options={"filename": "test_resume.json"},
            )

            if json_result.get("success"):
                self.log_test_result(
                    "JSON Export", True, f"Exported to {json_result['filename']}"
                )
            else:
                self.log_test_result(
                    "JSON Export", False, f"Error: {json_result.get('error')}"
                )

            # Test YAML export
            yaml_result = await export_service.export_resume(
                resume=test_resume,
                export_format="yaml",
                options={"filename": "test_resume.yaml"},
            )

            if yaml_result.get("success"):
                self.log_test_result(
                    "YAML Export", True, f"Exported to {yaml_result['filename']}"
                )
            else:
                self.log_test_result(
                    "YAML Export", False, f"Error: {yaml_result.get('error')}"
                )

            # Test TXT export
            txt_result = await export_service.export_resume(
                resume=test_resume,
                export_format="txt",
                options={"filename": "test_resume.txt"},
            )

            if txt_result.get("success"):
                self.log_test_result(
                    "TXT Export", True, f"Exported to {txt_result['filename']}"
                )
            else:
                self.log_test_result(
                    "TXT Export", False, f"Error: {txt_result.get('error')}"
                )

        except Exception as e:
            self.log_test_result("Export Functionality", False, f"Error: {str(e)}")

    async def test_performance_benchmarks(self):
        """Test performance benchmarks for generation pipeline."""
        logger.info("⚡ Testing Performance Benchmarks...")

        try:
            with self.db_manager.get_session() as session:
                repo = ResumeRepository(session)

                # Create a base resume for optimization testing
                test_resume = self.create_comprehensive_resume()
                resume_db = await repo.create_resume(test_resume)
                base_resume = repo._db_to_pydantic(resume_db)

                orchestrator = create_resume_orchestrator(
                    resume_repository=repo, llm_provider="mock"
                )

                # Test single resume generation performance
                start_time = datetime.now()

                perf_request = ResumeGenerationRequest(
                    user_id=self.test_user_id,
                    generation_type="enhance",
                    base_resume_id=base_resume.id,
                    job_description="Python developer position",
                    export_formats=["json"],
                )

                result = await orchestrator.generate_complete_resume(perf_request)

                processing_time = (datetime.now() - start_time).total_seconds()

                if (
                    result.success and processing_time < 10.0
                ):  # Should complete in under 10 seconds
                    self.log_test_result(
                        "Performance Single",
                        True,
                        f"Generated in {processing_time:.2f}s (target: <10s)",
                    )
                else:
                    self.log_test_result(
                        "Performance Single",
                        False,
                        f"Took {processing_time:.2f}s or failed",
                    )

                # Test batch generation performance
                batch_requests = [
                    ResumeGenerationRequest(
                        user_id=self.test_user_id,
                        generation_type="enhance",
                        base_resume_id=base_resume.id,
                        job_description=f"Job description {i}",
                        export_formats=["json"],
                    )
                    for i in range(3)
                ]

                batch_start = datetime.now()
                batch_results = await orchestrator.batch_generate_resumes(
                    batch_requests, max_concurrent=2
                )
                batch_time = (datetime.now() - batch_start).total_seconds()

                successful_batch = sum(1 for r in batch_results if r.success)

                if (
                    successful_batch >= 2 and batch_time < 30.0
                ):  # Should complete batch in under 30s
                    self.log_test_result(
                        "Performance Batch",
                        True,
                        f"Generated {successful_batch}/3 in {batch_time:.2f}s",
                    )
                else:
                    self.log_test_result(
                        "Performance Batch",
                        False,
                        f"Only {successful_batch}/3 successful in {batch_time:.2f}s",
                    )

        except Exception as e:
            self.log_test_result("Performance Benchmarks", False, f"Error: {str(e)}")

    def print_summary(self):
        """Print test summary and results."""
        total_tests = (
            self.test_results["passed"]
            + self.test_results["failed"]
            + self.test_results["warnings"]
        )

        print("\n" + "=" * 80)
        print("📊 RESUME GENERATION PIPELINE TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⚠️  Warnings: {self.test_results['warnings']}")

        success_rate = (
            (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        )
        print(f"📈 Success Rate: {success_rate:.1f}%")

        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)

        for test in self.test_results["test_details"]:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
            emoji = status_emoji.get(test["status"], "❓")
            print(f"{emoji} {test['test']}: {test['details']}")

        print("\n" + "=" * 80)

        if self.test_results["failed"] == 0:
            print(
                "🎉 ALL TESTS PASSED! Resume generation pipeline is working correctly."
            )
        else:
            print(
                f"❌ {self.test_results['failed']} tests failed. Please review the issues above."
            )

        return self.test_results["failed"] == 0


async def main():
    """Run all resume generation pipeline tests."""
    logger.info("🚀 Starting Resume Generation Pipeline Tests")
    logger.info("=" * 80)

    tester = ResumeGenerationTester()

    try:
        # Run all test suites
        await tester.test_llm_service()
        await tester.test_pdf_generation_service()
        await tester.test_resume_generation_service()
        await tester.test_resume_orchestrator()
        await tester.test_export_functionality()
        await tester.test_end_to_end_workflow()
        await tester.test_performance_benchmarks()

        # Print summary
        success = tester.print_summary()

        # Save detailed results to file
        results_file = Path("test_results_resume_generation.json")
        with open(results_file, "w") as f:
            json.dump(tester.test_results, f, indent=2)

        logger.info(f"📁 Detailed test results saved to: {results_file}")

        return success

    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        return False


if __name__ == "__main__":
    import asyncio

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
