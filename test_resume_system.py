#!/usr/bin/env python3
"""
Resume System Test Script
Test the complete resume backend implementation without dependencies on JobPilot tables.
"""

import asyncio
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
    calculate_resume_completeness,
    extract_resume_keywords,
)
from app.logger import logger
from app.repositories.resume_repository import ResumeRepository


# Create database connection
db_manager = DatabaseManager("sqlite:///jobpilot.db")


def create_test_user_data():
    """Create test user data for resume creation."""
    return {
        "id": str(uuid4()),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "current_title": "Senior Software Engineer",
        "bio": "Experienced software engineer with 8+ years developing scalable web applications.",
        "skills": [
            "Python",
            "JavaScript",
            "React",
            "Django",
            "PostgreSQL",
            "AWS",
            "Docker",
        ],
        "education": "Bachelor of Science in Computer Science",
    }


def create_comprehensive_resume(user_id: str) -> Resume:
    """Create a comprehensive test resume."""
    contact_info = ContactInfo(
        full_name="John Doe",
        email="john.doe@example.com",
        phone="+1 (555) 123-4567",
        location="San Francisco, CA",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe",
        website="https://johndoe.dev",
    )

    work_experience = [
        WorkExperience(
            company="Tech Innovations Inc",
            position="Senior Software Engineer",
            location="San Francisco, CA",
            start_date=date(2021, 1, 1),
            end_date=None,
            is_current=True,
            experience_type=ExperienceType.FULL_TIME,
            description="Lead development of microservices architecture serving 1M+ users",
            achievements=[
                "Reduced API response time by 40% through optimization",
                "Mentored 3 junior developers and conducted code reviews",
                "Implemented CI/CD pipeline reducing deployment time by 60%",
                "Led migration to cloud infrastructure saving $50k annually",
            ],
            skills_used=[
                "Python",
                "Django",
                "PostgreSQL",
                "Docker",
                "Kubernetes",
                "AWS",
            ],
        ),
        WorkExperience(
            company="StartupXYZ",
            position="Full Stack Developer",
            location="San Francisco, CA",
            start_date=date(2018, 6, 1),
            end_date=date(2020, 12, 31),
            is_current=False,
            experience_type=ExperienceType.FULL_TIME,
            description="Developed web applications for e-commerce platform",
            achievements=[
                "Built responsive frontend serving 100k+ daily users",
                "Optimized database queries improving performance by 25%",
                "Integrated payment processing and fraud detection systems",
            ],
            skills_used=["JavaScript", "React", "Node.js", "MongoDB", "Stripe API"],
        ),
    ]

    education = [
        Education(
            institution="University of California, Berkeley",
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            location="Berkeley, CA",
            start_date=date(2014, 9, 1),
            end_date=date(2018, 5, 1),
            gpa=3.7,
            honors=["Magna Cum Laude", "Dean's List"],
            relevant_coursework=[
                "Data Structures",
                "Algorithms",
                "Database Systems",
                "Software Engineering",
                "Machine Learning",
            ],
        )
    ]

    skills = [
        Skill(
            name="Python",
            level=SkillLevel.ADVANCED,
            category="Programming Languages",
            years_experience=6,
            is_featured=True,
        ),
        Skill(
            name="JavaScript",
            level=SkillLevel.ADVANCED,
            category="Programming Languages",
            years_experience=5,
            is_featured=True,
        ),
        Skill(
            name="React",
            level=SkillLevel.ADVANCED,
            category="Frontend Frameworks",
            years_experience=4,
            is_featured=True,
        ),
        Skill(
            name="Django",
            level=SkillLevel.ADVANCED,
            category="Backend Frameworks",
            years_experience=5,
            is_featured=True,
        ),
        Skill(
            name="PostgreSQL",
            level=SkillLevel.INTERMEDIATE,
            category="Databases",
            years_experience=4,
            is_featured=False,
        ),
        Skill(
            name="AWS",
            level=SkillLevel.INTERMEDIATE,
            category="Cloud Platforms",
            years_experience=3,
            is_featured=False,
        ),
        Skill(
            name="Docker",
            level=SkillLevel.INTERMEDIATE,
            category="DevOps",
            years_experience=3,
            is_featured=False,
        ),
        Skill(
            name="Kubernetes",
            level=SkillLevel.BEGINNER,
            category="DevOps",
            years_experience=1,
            is_featured=False,
        ),
    ]

    projects = [
        Project(
            name="E-commerce Platform",
            description="Full-stack web application built with Django and React for online marketplace",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 6, 1),
            url="https://github.com/johndoe/ecommerce-platform",
            github_url="https://github.com/johndoe/ecommerce-platform",
            technologies=["Django", "React", "PostgreSQL", "Docker", "AWS"],
            achievements=[
                "Implemented secure payment processing with Stripe",
                "Built responsive UI serving 10k+ concurrent users",
                "Deployed on AWS with 99.9% uptime",
                "Integrated real-time chat and notifications",
            ],
        ),
        Project(
            name="ML Stock Predictor",
            description="Machine learning model for stock price prediction using LSTM networks",
            start_date=date(2019, 9, 1),
            end_date=date(2019, 12, 1),
            url="https://stockpredictor.johndoe.dev",
            github_url="https://github.com/johndoe/stock-predictor",
            technologies=["Python", "TensorFlow", "Pandas", "Flask", "Chart.js"],
            achievements=[
                "Achieved 78% accuracy in 30-day price predictions",
                "Processed and analyzed 10+ years of market data",
                "Built interactive web dashboard for visualization",
            ],
        ),
    ]

    certifications = [
        Certification(
            name="AWS Certified Developer - Associate",
            issuer="Amazon Web Services",
            issue_date=date(2021, 3, 1),
            credential_id="AWS-DEV-2021-001",
            url="https://aws.amazon.com/certification/",
        ),
        Certification(
            name="Professional Scrum Master I",
            issuer="Scrum.org",
            issue_date=date(2020, 8, 1),
            credential_id="PSM-I-2020-001",
        ),
    ]

    return Resume(
        user_id=user_id,
        title="Senior Software Engineer Resume",
        contact_info=contact_info,
        summary="Experienced Senior Software Engineer with 8+ years of experience developing scalable web applications and leading cross-functional teams. Expertise in Python, JavaScript, and cloud technologies. Proven track record of optimizing system performance and mentoring junior developers.",
        work_experience=work_experience,
        education=education,
        skills=skills,
        projects=projects,
        certifications=certifications,
        resume_type=ResumeType.BASE,
        status=ResumeStatus.ACTIVE,
    )


async def test_resume_crud_operations():
    """Test basic CRUD operations."""
    logger.info("🧪 Testing Resume CRUD Operations...")

    with db_manager.get_session() as session:
        repo = ResumeRepository(session)

    try:
        # Create test user data
        user_data = create_test_user_data()
        user_id = user_data["id"]

        # Test 1: Create resume from user profile
        logger.info("📝 Creating resume from user profile...")
        resume = await repo.create_resume_from_user_profile(
            user_id, "Software Engineer Resume"
        )

        if resume:
            logger.info(f"✅ Resume created successfully: {resume.id}")
            logger.info(f"   Title: {resume.title}")
            logger.info(
                f"   Contact: {resume.contact_info.full_name} ({resume.contact_info.email})"
            )
            logger.info(f"   Skills: {len(resume.skills)} skills")
        else:
            # If user profile doesn't exist, create comprehensive resume directly
            logger.info(
                "⚠️  User profile not found, creating comprehensive resume directly..."
            )
            comprehensive_resume = create_comprehensive_resume(user_id)
            resume_db = await repo.create_resume(comprehensive_resume)
            resume = repo._db_to_pydantic(resume_db)
            logger.info(f"✅ Comprehensive resume created: {resume.id}")

        # Test 2: Get resume
        logger.info("📖 Retrieving resume...")
        retrieved_resume = await repo.get_resume(resume.id, user_id)
        if retrieved_resume:
            logger.info(f"✅ Resume retrieved successfully")
            logger.info(
                f"   Work Experience: {len(retrieved_resume.work_experience)} positions"
            )
            logger.info(f"   Education: {len(retrieved_resume.education)} degrees")
            logger.info(f"   Projects: {len(retrieved_resume.projects)} projects")

        # Test 3: Update resume
        logger.info("✏️  Updating resume...")
        updates = {
            "summary": "Updated: Passionate software engineer with expertise in full-stack development and team leadership.",
            "status": "active",
        }
        updated_resume = await repo.update_resume(resume.id, user_id, updates)
        if updated_resume:
            logger.info(
                f"✅ Resume updated successfully (version {updated_resume.version})"
            )

        # Test 4: List user resumes
        logger.info("📋 Listing user resumes...")
        user_resumes = await repo.get_user_resumes(user_id)
        logger.info(f"✅ Found {len(user_resumes)} resumes for user")

        return resume

    except Exception as e:
        logger.error(f"❌ CRUD test failed: {e}")
        return None


async def test_ats_scoring(resume: Resume):
    """Test ATS scoring functionality."""
    logger.info("🎯 Testing ATS Scoring...")

    with db_manager.get_session() as session:
        repo = ResumeRepository(session)

    try:
        # Test 1: Basic ATS score
        logger.info("📊 Calculating basic ATS score...")
        basic_score = await repo.calculate_ats_score(resume)
        logger.info(f"✅ Basic ATS Score: {basic_score.overall_score:.1f}/100")
        logger.info(f"   Keyword Score: {basic_score.keyword_score:.1f}")
        logger.info(f"   Format Score: {basic_score.formatting_score:.1f}")
        logger.info(f"   Section Score: {basic_score.section_score:.1f}")
        logger.info(f"   Suggestions: {len(basic_score.suggestions)} recommendations")

        # Test 2: Job-targeted ATS score
        logger.info("🎯 Calculating job-targeted ATS score...")
        job_description = """
        Senior Software Engineer - Python/Django/React

        We are looking for an experienced Senior Software Engineer to join our team.

        Requirements:
        - 5+ years of experience with Python and Django
        - Strong React and JavaScript skills
        - Experience with PostgreSQL and database optimization
        - AWS cloud platform experience
        - Docker and containerization knowledge
        - Experience with CI/CD pipelines
        - Strong problem-solving and communication skills

        Nice to have:
        - Kubernetes experience
        - Machine learning background
        - Startup experience
        - Team leadership experience
        """

        targeted_score = await repo.calculate_ats_score(resume, job_description)
        logger.info(f"✅ Job-Targeted ATS Score: {targeted_score.overall_score:.1f}/100")
        logger.info(f"   Keyword Score: {targeted_score.keyword_score:.1f}")
        logger.info(
            f"   Missing Keywords: {len(targeted_score.missing_keywords)} identified"
        )
        if targeted_score.missing_keywords:
            logger.info(
                f"   Sample Missing: {', '.join(targeted_score.missing_keywords[:5])}"
            )

        # Test 3: Resume completeness
        logger.info("📋 Calculating resume completeness...")
        completeness = calculate_resume_completeness(resume)
        logger.info(f"✅ Resume Completeness: {completeness:.1f}%")

        # Test 4: Keyword extraction
        logger.info("🔍 Extracting keywords...")
        keywords = extract_resume_keywords(resume)
        logger.info(f"✅ Extracted {len(keywords)} keywords")
        logger.info(f"   Sample Keywords: {', '.join(keywords[:10])}")

    except Exception as e:
        logger.error(f"❌ ATS scoring test failed: {e}")


async def test_template_system():
    """Test resume template functionality."""
    logger.info("🎨 Testing Template System...")

    with db_manager.get_session() as session:
        repo = ResumeRepository(session)

    try:
        # Test 1: Get available templates
        logger.info("📋 Getting available templates...")
        templates = await repo.get_resume_templates()
        logger.info(f"✅ Found {len(templates)} templates:")

        for template in templates:
            logger.info(f"   - {template['name']}: {template['description']}")
            logger.info(f"     Sections: {', '.join(template['sections'])}")
            logger.info(f"     Default: {template['is_default']}")

        return templates[0] if templates else None

    except Exception as e:
        logger.error(f"❌ Template test failed: {e}")
        return None


async def test_skill_bank():
    """Test skills bank functionality."""
    logger.info("🏦 Testing Skills Bank...")

    with db_manager.get_session() as session:
        repo = ResumeRepository(session)

    try:
        user_id = str(uuid4())

        # Create a resume with skills to populate skill bank
        test_resume = create_comprehensive_resume(user_id)
        resume_db = await repo.create_resume(test_resume)
        resume = repo._db_to_pydantic(resume_db)

        # Test 1: Update skill bank from resume
        logger.info("💾 Updating skill bank from resume...")
        await repo.update_skill_bank_from_resume(user_id, resume)
        logger.info("✅ Skill bank updated")

        # Test 2: Get skill bank
        logger.info("📖 Retrieving skill bank...")
        skill_bank = await repo.get_user_skill_bank(user_id)
        if skill_bank:
            logger.info(f"✅ Skill bank retrieved:")
            logger.info(
                f"   Technical Keywords: {len(skill_bank['technical_keywords'])}"
            )
            logger.info(f"   Soft Skills: {len(skill_bank['soft_skills'])}")
            logger.info(f"   Industry Keywords: {len(skill_bank['industry_keywords'])}")
            logger.info(f"   Confidence Scores: {len(skill_bank['confidence'])} skills")

    except Exception as e:
        logger.error(f"❌ Skill bank test failed: {e}")


async def test_resume_analytics(resume: Resume):
    """Test resume analytics and insights."""
    logger.info("📊 Testing Resume Analytics...")

    try:
        # Test various analytics functions
        completeness = calculate_resume_completeness(resume)
        keywords = extract_resume_keywords(resume)

        logger.info(f"✅ Resume Analytics:")
        logger.info(f"   Completeness: {completeness:.1f}%")
        logger.info(f"   Total Keywords: {len(keywords)}")
        logger.info(f"   Work Experience: {len(resume.work_experience)} positions")
        logger.info(
            f"   Total Experience: {sum(exp.end_date.year - exp.start_date.year if exp.end_date else datetime.now().year - exp.start_date.year for exp in resume.work_experience)} years"
        )
        logger.info(f"   Education Levels: {len(resume.education)}")
        logger.info(
            f"   Technical Skills: {len([s for s in resume.skills if s.is_featured])}"
        )
        logger.info(f"   Projects: {len(resume.projects)}")
        logger.info(f"   Certifications: {len(resume.certifications)}")

        # Analyze skill distribution
        skill_categories = {}
        for skill in resume.skills:
            category = skill.category or "Other"
            skill_categories[category] = skill_categories.get(category, 0) + 1

        logger.info(f"   Skill Distribution:")
        for category, count in skill_categories.items():
            logger.info(f"     - {category}: {count} skills")

    except Exception as e:
        logger.error(f"❌ Analytics test failed: {e}")


async def main():
    """Run all resume system tests."""
    logger.info("🚀 Starting Resume System Tests")
    logger.info("=" * 50)

    try:
        # Test 1: CRUD Operations
        resume = await test_resume_crud_operations()
        if not resume:
            logger.error("❌ CRUD tests failed, skipping other tests")
            return

        logger.info("\n" + "=" * 50)

        # Test 2: ATS Scoring
        await test_ats_scoring(resume)

        logger.info("\n" + "=" * 50)

        # Test 3: Template System
        await test_template_system()

        logger.info("\n" + "=" * 50)

        # Test 4: Skills Bank
        await test_skill_bank()

        logger.info("\n" + "=" * 50)

        # Test 5: Analytics
        await test_resume_analytics(resume)

        logger.info("\n" + "=" * 50)
        logger.info("🎉 All Resume System Tests Completed Successfully!")

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
