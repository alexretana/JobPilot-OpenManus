#!/usr/bin/env python3
"""
Resume Tables Migration Script
Adds resume-related tables to the existing JobPilot database schema.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from app.data.models import UserProfileDB, create_database_engine
from app.data.resume_models import (
    ResumeDB,
    ResumeGenerationDB,
    ResumeOptimizationDB,
    ResumeTemplateDB,
    SkillBankDB,
)
from app.logger import logger

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jobpilot.db")


def check_existing_tables(engine):
    """Check which tables already exist in the database."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    resume_tables = {
        "resumes",
        "resume_templates",
        "skill_banks",
        "resume_generations",
        "resume_optimizations",
    }

    missing_tables = resume_tables - existing_tables
    existing_resume_tables = resume_tables & existing_tables

    return existing_tables, missing_tables, existing_resume_tables


def create_resume_tables(engine):
    """Create resume-related tables."""
    try:
        logger.info("Creating resume tables...")

        # Only create resume tables, not all tables
        resume_tables = [
            ResumeDB.__table__,
            ResumeTemplateDB.__table__,
            SkillBankDB.__table__,
            ResumeGenerationDB.__table__,
            ResumeOptimizationDB.__table__,
        ]

        for table in resume_tables:
            logger.info(f"Creating table: {table.name}")
            table.create(engine, checkfirst=True)

        logger.info("Resume tables created successfully!")
        return True

    except Exception as e:
        logger.error(f"Error creating resume tables: {e}")
        return False


def seed_default_templates(engine):
    """Seed the database with default resume templates."""
    try:
        logger.info("Seeding default resume templates...")

        Session = sessionmaker(bind=engine)
        session = Session()

        # Check if templates already exist
        existing_count = session.query(ResumeTemplateDB).count()
        if existing_count > 0:
            logger.info(
                f"Templates already exist ({existing_count} found). Skipping seeding."
            )
            session.close()
            return True

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
                "sections": ["contact", "summary", "experience", "education", "skills"],
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
            {
                "name": "Executive",
                "description": "Professional template for senior-level positions",
                "sections": ["contact", "summary", "experience", "education", "skills"],
                "section_order": [
                    "contact",
                    "summary",
                    "experience",
                    "education",
                    "skills",
                ],
                "styling": {
                    "color_scheme": "navy",
                    "font_family": "Georgia",
                    "layout": "traditional",
                },
                "is_default": False,
                "is_system": True,
            },
        ]

        for template_data in default_templates:
            template = ResumeTemplateDB(**template_data)
            session.add(template)

        session.commit()
        session.close()

        logger.info(f"Successfully seeded {len(default_templates)} default templates!")
        return True

    except Exception as e:
        logger.error(f"Error seeding default templates: {e}")
        return False


def add_resume_relationship_to_users(engine):
    """Add resume relationship columns to user profiles table if needed."""
    try:
        logger.info("Checking user profiles table for resume relationships...")

        # This is handled by the SQLAlchemy relationships in the models
        # No additional columns needed for one-to-many relationships
        logger.info("User profiles table ready for resume relationships.")
        return True

    except Exception as e:
        logger.error(f"Error updating user profiles table: {e}")
        return False


def verify_migration(engine):
    """Verify that the migration was successful."""
    try:
        logger.info("Verifying migration...")

        Session = sessionmaker(bind=engine)
        session = Session()

        # Test basic table access
        resume_count = session.query(ResumeDB).count()
        template_count = session.query(ResumeTemplateDB).count()
        skill_bank_count = session.query(SkillBankDB).count()

        logger.info(f"Migration verification:")
        logger.info(f"  - Resumes table: {resume_count} records")
        logger.info(f"  - Templates table: {template_count} records")
        logger.info(f"  - Skill banks table: {skill_bank_count} records")

        # Test relationship access
        user_count = session.query(UserProfileDB).count()
        logger.info(f"  - User profiles table: {user_count} records")

        session.close()

        logger.info("Migration verification successful!")
        return True

    except Exception as e:
        logger.error(f"Error verifying migration: {e}")
        return False


def create_sample_data(engine):
    """Create sample resume data for testing."""
    try:
        logger.info("Creating sample resume data...")

        Session = sessionmaker(bind=engine)
        session = Session()

        # Check if we have any users to create resumes for
        users = session.query(UserProfileDB).limit(1).all()
        if not users:
            logger.info("No users found. Skipping sample resume creation.")
            session.close()
            return True

        user = users[0]

        # Check if user already has resumes
        existing_resumes = (
            session.query(ResumeDB).filter(ResumeDB.user_id == user.id).count()
        )
        if existing_resumes > 0:
            logger.info("User already has resumes. Skipping sample data creation.")
            session.close()
            return True

        # Get default template
        default_template = (
            session.query(ResumeTemplateDB)
            .filter(ResumeTemplateDB.is_default is True)
            .first()
        )

        # Create sample resume
        sample_resume = ResumeDB(
            user_id=user.id,
            title="Software Developer Resume",
            resume_type="base",
            status="draft",
            contact_info={
                "full_name": f"{user.first_name or 'John'} {user.last_name or 'Doe'}",
                "email": user.email or "john.doe@example.com",
                "phone": user.phone or "+1 (555) 123-4567",
                "location": "San Francisco, CA",
            },
            summary="Experienced software developer with expertise in Python, JavaScript, and cloud technologies. Passionate about building scalable web applications and contributing to open-source projects.",
            work_experience=[
                {
                    "company": "Tech Innovations Inc",
                    "position": "Senior Software Developer",
                    "location": "San Francisco, CA",
                    "start_date": "2021-01-01",
                    "end_date": None,
                    "is_current": True,
                    "experience_type": "full_time",
                    "description": "Led development of microservices architecture serving 1M+ users",
                    "achievements": [
                        "Reduced API response time by 40% through optimization",
                        "Mentored 3 junior developers",
                        "Implemented CI/CD pipeline reducing deployment time by 60%",
                    ],
                    "skills_used": [
                        "Python",
                        "Django",
                        "PostgreSQL",
                        "Docker",
                        "Kubernetes",
                    ],
                }
            ],
            education=[
                {
                    "institution": "University of Technology",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "location": "San Francisco, CA",
                    "start_date": "2015-09-01",
                    "end_date": "2019-05-01",
                    "gpa": 3.7,
                    "honors": ["Magna Cum Laude", "Dean's List"],
                    "relevant_coursework": [
                        "Data Structures",
                        "Algorithms",
                        "Database Systems",
                        "Software Engineering",
                    ],
                }
            ],
            skills=[
                {
                    "name": "Python",
                    "level": "advanced",
                    "category": "Programming Languages",
                    "years_experience": 5,
                    "is_featured": True,
                },
                {
                    "name": "JavaScript",
                    "level": "advanced",
                    "category": "Programming Languages",
                    "years_experience": 4,
                    "is_featured": True,
                },
                {
                    "name": "Django",
                    "level": "advanced",
                    "category": "Frameworks",
                    "years_experience": 3,
                    "is_featured": True,
                },
                {
                    "name": "React",
                    "level": "intermediate",
                    "category": "Frameworks",
                    "years_experience": 2,
                    "is_featured": False,
                },
                {
                    "name": "PostgreSQL",
                    "level": "intermediate",
                    "category": "Databases",
                    "years_experience": 3,
                    "is_featured": False,
                },
            ],
            projects=[
                {
                    "name": "E-commerce Platform",
                    "description": "Full-stack web application built with Django and React",
                    "start_date": "2020-01-01",
                    "end_date": "2020-06-01",
                    "url": "https://github.com/johndoe/ecommerce",
                    "technologies": ["Django", "React", "PostgreSQL", "Docker"],
                    "achievements": [
                        "Implemented secure payment processing",
                        "Built responsive UI serving 10k+ users",
                        "Deployed on AWS with 99.9% uptime",
                    ],
                }
            ],
            certifications=[
                {
                    "name": "AWS Certified Developer",
                    "issuer": "Amazon Web Services",
                    "issue_date": "2021-03-01",
                    "credential_id": "AWS-DEV-2021-001",
                }
            ],
            template_id=default_template.id if default_template else None,
        )

        session.add(sample_resume)

        # Create sample skill bank
        sample_skill_bank = SkillBankDB(
            user_id=user.id,
            skills={
                "Programming Languages": ["Python", "JavaScript", "Java", "Go"],
                "Frameworks": ["Django", "React", "Vue.js", "Flask"],
                "Databases": ["PostgreSQL", "MongoDB", "Redis"],
                "Cloud": ["AWS", "Docker", "Kubernetes"],
            },
            technical_keywords=[
                "python",
                "javascript",
                "django",
                "react",
                "aws",
                "docker",
            ],
            soft_skills=["leadership", "communication", "problem-solving", "teamwork"],
            industry_keywords=[
                "software development",
                "web applications",
                "microservices",
                "agile",
            ],
            skill_confidence={
                "python": 0.9,
                "javascript": 0.8,
                "django": 0.85,
                "react": 0.7,
                "aws": 0.75,
            },
        )

        session.add(sample_skill_bank)
        session.commit()
        session.close()

        logger.info("Sample resume data created successfully!")
        return True

    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        return False


def main():
    """Main migration function."""
    logger.info("Starting resume tables migration...")

    try:
        # Create database engine
        engine = create_database_engine(DATABASE_URL)
        logger.info(f"Connected to database: {DATABASE_URL}")

        # Check existing tables
        existing_tables, missing_tables, existing_resume_tables = check_existing_tables(
            engine
        )

        logger.info(f"Database status:")
        logger.info(f"  - Total existing tables: {len(existing_tables)}")
        logger.info(f"  - Missing resume tables: {missing_tables}")
        logger.info(f"  - Existing resume tables: {existing_resume_tables}")

        # Create missing resume tables
        if missing_tables:
            success = create_resume_tables(engine)
            if not success:
                logger.error("Failed to create resume tables!")
                return False
        else:
            logger.info("All resume tables already exist!")

        # Update user profiles table for relationships
        success = add_resume_relationship_to_users(engine)
        if not success:
            logger.error("Failed to update user profiles table!")
            return False

        # Seed default templates
        success = seed_default_templates(engine)
        if not success:
            logger.error("Failed to seed default templates!")
            return False

        # Verify migration
        success = verify_migration(engine)
        if not success:
            logger.error("Migration verification failed!")
            return False

        # Create sample data (optional)
        if len(existing_resume_tables) == 0:  # Only if this is a fresh migration
            success = create_sample_data(engine)
            if not success:
                logger.warning(
                    "Failed to create sample data, but migration was successful!"
                )

        logger.info("Resume tables migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Resume tables migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Resume tables migration failed!")
        sys.exit(1)
