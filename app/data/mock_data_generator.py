"""
JobPilot Mock Data Generator
Generator for creating comprehensive mock data for UserProfile and SkillBank testing
"""

import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List
from uuid import uuid4

from sqlalchemy.orm import Session

from app.data.database import DatabaseManager
from app.data.models import (
    ApplicationStatus,
    CompanyInfoDB,
    CompanySizeCategory,
    ExperienceLevel,
    InteractionType,
    JobDeduplicationDB,
    JobEmbeddingDB,
    JobListingDB,
    JobSourceDB,
    JobSourceListingDB,
    JobStatus,
    JobType,
    JobUserInteractionDB,
    RemoteType,
    SeniorityLevel,
    TimelineEventDB,
    TimelineEventType,
    UserProfileDB,
    VerificationStatus,
)
from app.data.resume_models import (
    ExperienceType,
    ResumeDB,
    ResumeStatus,
    ResumeTemplateDB,
    ResumeType,
    SkillLevel,
)
from app.data.skill_bank_models import (
    Certification,
    ContentFocusType,
    ContentSource,
    EducationEntry,
    EnhancedSkill,
    ExperienceContentVariation,
    ExperienceEntry,
    ProjectEntry,
    SkillBank,
    SkillCategory,
    SummaryVariation,
)
from app.data.skill_bank_repository import SkillBankRepository

# Import lead management classes for enhanced functionality
try:
    from app.api.leads_simple import Lead, LeadStatus, LeadType

    LEAD_MANAGEMENT_AVAILABLE = True
except ImportError:
    LEAD_MANAGEMENT_AVAILABLE = False


class MockDataGenerator:
    """Generator for comprehensive mock data for testing UserProfile and SkillBank."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.skill_bank_repo = SkillBankRepository(db_manager)

    def _get_session(self) -> Session:
        """Get database session."""
        return self.db_manager.get_session()

    # =========================================================================
    # SAMPLE DATA DEFINITIONS
    # =========================================================================

    SAMPLE_USERS = [
        {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah.johnson@email.com",
            "phone": "+1 (555) 123-4567",
            "city": "San Francisco",
            "state": "California",
            "linkedin_url": "https://linkedin.com/in/sarah-johnson-dev",
            "portfolio_url": "https://sarahjohnson.dev",
            "current_title": "Senior Software Engineer",
            "experience_years": 5,
            "bio": "Experienced software engineer specializing in full-stack development with expertise in React, Node.js, and cloud technologies. Passionate about building scalable applications and mentoring junior developers.",
        },
        {
            "first_name": "Michael",
            "last_name": "Chen",
            "email": "michael.chen@email.com",
            "phone": "+1 (555) 987-6543",
            "city": "Seattle",
            "state": "Washington",
            "linkedin_url": "https://linkedin.com/in/michael-chen-data",
            "portfolio_url": "https://michaelchen.portfolio.io",
            "current_title": "Data Scientist",
            "experience_years": 3,
            "bio": "Data scientist with strong background in machine learning, statistical analysis, and data visualization. Experienced in Python, R, and cloud-based analytics platforms.",
        },
        {
            "first_name": "Emma",
            "last_name": "Rodriguez",
            "email": "emma.rodriguez@email.com",
            "phone": "+1 (555) 456-7890",
            "city": "Austin",
            "state": "Texas",
            "linkedin_url": "https://linkedin.com/in/emma-rodriguez-pm",
            "portfolio_url": "https://emmarodriguez.com",
            "current_title": "Product Manager",
            "experience_years": 7,
            "bio": "Product manager with 7+ years of experience leading cross-functional teams to deliver innovative software products. Expert in agile methodologies, user research, and strategic product planning.",
        },
    ]

    TECHNICAL_SKILLS = [
        {
            "name": "JavaScript",
            "category": SkillCategory.TECHNICAL,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "Python",
            "category": SkillCategory.TECHNICAL,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "React",
            "category": SkillCategory.FRAMEWORK,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "Node.js",
            "category": SkillCategory.FRAMEWORK,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "TypeScript",
            "category": SkillCategory.TECHNICAL,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "PostgreSQL",
            "category": SkillCategory.PLATFORM,
            "level": SkillLevel.INTERMEDIATE,
        },
        {
            "name": "AWS",
            "category": SkillCategory.PLATFORM,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "Docker",
            "category": SkillCategory.TOOL,
            "level": SkillLevel.INTERMEDIATE,
        },
        {
            "name": "GraphQL",
            "category": SkillCategory.FRAMEWORK,
            "level": SkillLevel.INTERMEDIATE,
        },
        {
            "name": "MongoDB",
            "category": SkillCategory.PLATFORM,
            "level": SkillLevel.INTERMEDIATE,
        },
    ]

    DATA_SCIENCE_SKILLS = [
        {
            "name": "Python",
            "category": SkillCategory.TECHNICAL,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "R",
            "category": SkillCategory.TECHNICAL,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "SQL",
            "category": SkillCategory.TECHNICAL,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "TensorFlow",
            "category": SkillCategory.FRAMEWORK,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "pandas",
            "category": SkillCategory.FRAMEWORK,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "scikit-learn",
            "category": SkillCategory.FRAMEWORK,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "Tableau",
            "category": SkillCategory.TOOL,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "Apache Spark",
            "category": SkillCategory.PLATFORM,
            "level": SkillLevel.INTERMEDIATE,
        },
        {
            "name": "Statistics",
            "category": SkillCategory.DOMAIN,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "Machine Learning",
            "category": SkillCategory.DOMAIN,
            "level": SkillLevel.ADVANCED,
        },
    ]

    PM_SKILLS = [
        {
            "name": "Agile/Scrum",
            "category": SkillCategory.METHODOLOGY,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "Product Strategy",
            "category": SkillCategory.DOMAIN,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "User Research",
            "category": SkillCategory.DOMAIN,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "Data Analysis",
            "category": SkillCategory.TECHNICAL,
            "level": SkillLevel.INTERMEDIATE,
        },
        {"name": "Jira", "category": SkillCategory.TOOL, "level": SkillLevel.EXPERT},
        {
            "name": "Figma",
            "category": SkillCategory.TOOL,
            "level": SkillLevel.INTERMEDIATE,
        },
        {
            "name": "SQL",
            "category": SkillCategory.TECHNICAL,
            "level": SkillLevel.INTERMEDIATE,
        },
        {
            "name": "A/B Testing",
            "category": SkillCategory.METHODOLOGY,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "Cross-functional Leadership",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "Stakeholder Management",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.EXPERT,
        },
    ]

    SOFT_SKILLS = [
        {
            "name": "Leadership",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "Communication",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "Problem Solving",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "Team Collaboration",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.EXPERT,
        },
        {
            "name": "Project Management",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.ADVANCED,
        },
        {
            "name": "Mentoring",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.INTERMEDIATE,
        },
        {
            "name": "Public Speaking",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.INTERMEDIATE,
        },
        {
            "name": "Strategic Thinking",
            "category": SkillCategory.SOFT,
            "level": SkillLevel.ADVANCED,
        },
    ]

    # =========================================================================
    # USER PROFILE CREATION
    # =========================================================================

    def create_user_profile(self, user_data: Dict[str, Any]) -> str:
        """Create a user profile with given data, or return existing user ID if email exists."""

        with self._get_session() as session:
            # Check if user already exists
            existing_user = (
                session.query(UserProfileDB)
                .filter(UserProfileDB.email == user_data["email"])
                .first()
            )

            if existing_user:
                print(
                    f"   📧 User with email {user_data['email']} already exists, using existing user"
                )
                return existing_user.id

            # Create new user
            user_id = str(uuid4())
            user_profile = UserProfileDB(
                id=user_id,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                phone=user_data.get("phone"),
                city=user_data.get("city"),
                state=user_data.get("state"),
                linkedin_url=user_data.get("linkedin_url"),
                portfolio_url=user_data.get("portfolio_url"),
                current_title=user_data.get("current_title"),
                experience_years=user_data.get("experience_years"),
                bio=user_data.get("bio"),
                # skills field removed - now handled via SkillBank relationship
                preferred_locations=["Remote", user_data.get("city", "San Francisco")],
                preferred_job_types=["Full-time", "Contract"],
                preferred_remote_types=["Remote", "Hybrid"],
                desired_salary_min=80000,
                desired_salary_max=150000,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(user_profile)
            session.commit()
            session.refresh(user_profile)

        return user_id

    # =========================================================================
    # SKILL BANK CREATION
    # =========================================================================

    async def create_comprehensive_skill_bank(
        self, user_id: str, role: str = "developer"
    ) -> SkillBank:
        """Create a comprehensive skill bank with realistic data."""

        # Check if skill bank already exists and has content
        existing_skill_bank = await self.skill_bank_repo.get_skill_bank(user_id)
        if existing_skill_bank:
            # Check if it already has skills
            total_skills = sum(
                len(skills) for skills in existing_skill_bank.skills.values()
            )
            if total_skills > 0:
                print(
                    f"   🏦 Skill bank for user {user_id} already exists with {total_skills} skills, skipping"
                )
                return existing_skill_bank

            # If skill bank exists but is empty, we'll populate it
            print(
                f"   🏦 Found empty skill bank for user {user_id}, populating with mock data"
            )

        # Select skills based on role
        if role == "developer":
            primary_skills = self.TECHNICAL_SKILLS[:7]
            secondary_skills = random.sample(self.SOFT_SKILLS, 4)
        elif role == "data_scientist":
            primary_skills = self.DATA_SCIENCE_SKILLS[:8]
            secondary_skills = random.sample(self.SOFT_SKILLS, 3)
        elif role == "product_manager":
            primary_skills = self.PM_SKILLS[:8]
            secondary_skills = random.sample(self.SOFT_SKILLS, 5)
        else:
            primary_skills = random.sample(self.TECHNICAL_SKILLS, 6)
            secondary_skills = random.sample(self.SOFT_SKILLS, 4)

        # Create enhanced skills
        enhanced_skills = []
        for skill_data in primary_skills + secondary_skills:
            enhanced_skill = EnhancedSkill(
                id=str(uuid4()),
                name=skill_data["name"],
                level=skill_data["level"],
                category=skill_data["category"],
                subcategory=self._get_subcategory(
                    skill_data["category"], skill_data["name"]
                ),
                years_experience=random.randint(1, 8),
                proficiency_score=random.uniform(0.6, 1.0),
                description=self._generate_skill_description(skill_data["name"]),
                keywords=self._generate_skill_keywords(skill_data["name"]),
                is_featured=random.choice([True, False]),
                display_order=len(enhanced_skills),
                source=ContentSource.MANUAL,
                confidence=1.0,
                created_at=datetime.utcnow(),
            )
            enhanced_skills.append(enhanced_skill)

        # Create skill bank or get existing one
        await self.skill_bank_repo.get_or_create_skill_bank(user_id)

        # Add skills to skill bank (with duplicate checking)
        skills_added = 0
        for skill in enhanced_skills:
            try:
                await self.skill_bank_repo.add_skill(user_id, skill)
                skills_added += 1
            except ValueError as e:
                # Skill already exists, skip it
                print(f"   ⚠️  {str(e)}")
                continue

        print(f"   ✅ Added {skills_added} new skills to skill bank")

        # Create summary variations
        summaries = self._generate_summary_variations(role)
        for summary in summaries:
            await self.skill_bank_repo.add_summary_variation(user_id, summary)

        # Create work experiences
        experiences = self._generate_work_experiences(role)
        for experience in experiences:
            await self.skill_bank_repo.add_experience(user_id, experience)

            # Add content variations for each experience
            variations = self._generate_experience_variations(experience.id, role)
            for variation in variations:
                await self.skill_bank_repo.add_experience_content_variation(
                    user_id, experience.id, variation
                )

        # Create education entries
        education_entries = self._generate_education_entries(role)
        for education in education_entries:
            await self.skill_bank_repo.add_education(user_id, education)

        # Create project entries
        projects = self._generate_project_entries(role)
        for project in projects:
            await self.skill_bank_repo.add_project(user_id, project)

        # Create certifications
        certifications = self._generate_certifications(role)
        for cert in certifications:
            await self.skill_bank_repo.add_certification(user_id, cert)

        return await self.skill_bank_repo.get_skill_bank(user_id)

    def _get_subcategory(self, category: SkillCategory, skill_name: str) -> str:
        """Get subcategory based on skill name and category."""
        if category == SkillCategory.TECHNICAL:
            if skill_name.lower() in [
                "python",
                "javascript",
                "typescript",
                "java",
                "c#",
            ]:
                return "Programming Languages"
            elif skill_name.lower() in ["sql", "postgresql", "mysql"]:
                return "Databases"
            else:
                return "Technical Skills"
        elif category == SkillCategory.FRAMEWORK:
            return "Frameworks & Libraries"
        elif category == SkillCategory.PLATFORM:
            return "Platforms & Services"
        elif category == SkillCategory.TOOL:
            return "Development Tools"
        elif category == SkillCategory.METHODOLOGY:
            return "Methodologies"
        elif category == SkillCategory.DOMAIN:
            return "Domain Knowledge"
        else:
            return "Other"

    def _generate_skill_description(self, skill_name: str) -> str:
        """Generate a realistic skill description."""
        descriptions = {
            "JavaScript": "Extensive experience with modern JavaScript ES6+, asynchronous programming, and DOM manipulation.",
            "Python": "Proficient in Python for web development, data analysis, and automation scripting.",
            "React": "Expert in building responsive, component-based user interfaces with React hooks and state management.",
            "Node.js": "Backend development experience with Express.js, RESTful APIs, and real-time applications.",
            "AWS": "Cloud infrastructure management including EC2, S3, Lambda, and RDS services.",
            "Leadership": "Proven track record of leading cross-functional teams and mentoring junior developers.",
            "Communication": "Strong written and verbal communication skills, experienced in stakeholder presentations.",
        }
        return descriptions.get(
            skill_name,
            f"Experienced in {skill_name} with practical application in professional projects.",
        )

    def _generate_skill_keywords(self, skill_name: str) -> List[str]:
        """Generate relevant keywords for a skill."""
        keyword_map = {
            "JavaScript": [
                "ES6",
                "ES2020",
                "async/await",
                "promises",
                "DOM",
                "event handling",
            ],
            "Python": [
                "pandas",
                "numpy",
                "flask",
                "django",
                "data analysis",
                "automation",
            ],
            "React": [
                "JSX",
                "hooks",
                "state management",
                "components",
                "virtual DOM",
                "redux",
            ],
            "AWS": ["cloud", "EC2", "S3", "Lambda", "serverless", "infrastructure"],
            "Leadership": [
                "team management",
                "mentoring",
                "project planning",
                "decision making",
            ],
            "Communication": [
                "presentation",
                "documentation",
                "stakeholder management",
                "collaboration",
            ],
        }
        return keyword_map.get(
            skill_name, [skill_name.lower(), "professional", "experienced"]
        )

    def _generate_summary_variations(self, role: str) -> List[SummaryVariation]:
        """Generate multiple summary variations for different contexts."""
        base_summaries = {
            "developer": [
                "Experienced software engineer specializing in full-stack development with expertise in modern web technologies and cloud platforms.",
                "Full-stack developer with 5+ years of experience building scalable web applications using React, Node.js, and cloud technologies.",
                "Senior software engineer passionate about clean code, system design, and mentoring junior developers in agile environments.",
            ],
            "data_scientist": [
                "Data scientist with strong background in machine learning, statistical analysis, and data visualization using Python and R.",
                "Experienced data professional specializing in predictive modeling, data mining, and business intelligence solutions.",
                "Analytics expert with expertise in machine learning algorithms, statistical modeling, and big data technologies.",
            ],
            "product_manager": [
                "Product manager with 7+ years of experience leading cross-functional teams to deliver innovative software products.",
                "Strategic product leader with proven track record in agile development, user research, and data-driven decision making.",
                "Experienced PM focused on user-centered design, product strategy, and stakeholder management in fast-paced environments.",
            ],
        }

        summaries = []
        for i, content in enumerate(
            base_summaries.get(role, base_summaries["developer"])
        ):
            summary = SummaryVariation(
                id=str(uuid4()),
                title=f"Professional Summary {i+1}",
                content=content,
                tone="professional",
                length="standard" if i == 0 else random.choice(["concise", "detailed"]),
                focus=random.choice(
                    [
                        ContentFocusType.TECHNICAL,
                        ContentFocusType.LEADERSHIP,
                        ContentFocusType.RESULTS,
                    ]
                ),
                target_industries=["Technology", "Software", "Fintech"],
                target_roles=[
                    role.replace("_", " ").title(),
                    "Senior " + role.replace("_", " ").title(),
                ],
                keywords_emphasized=self._get_role_keywords(role),
                source=ContentSource.MANUAL,
                created_at=datetime.utcnow(),
                usage_count=random.randint(0, 5),
            )
            summaries.append(summary)

        return summaries

    def _generate_work_experiences(self, role: str) -> List[ExperienceEntry]:
        """Generate realistic work experience entries."""
        experiences = []

        companies = [
            "TechCorp",
            "DataFlow Inc",
            "Innovative Solutions",
            "StartupXYZ",
            "Global Tech",
        ]
        positions = {
            "developer": [
                "Software Engineer",
                "Senior Developer",
                "Full Stack Developer",
                "Frontend Engineer",
            ],
            "data_scientist": [
                "Data Scientist",
                "Senior Data Analyst",
                "ML Engineer",
                "Research Scientist",
            ],
            "product_manager": [
                "Product Manager",
                "Senior PM",
                "Product Owner",
                "Strategy Manager",
            ],
        }

        for i in range(3):  # Generate 3 experiences
            start_date = date.today() - timedelta(
                days=random.randint(365 * (i + 1), 365 * (i + 3))
            )
            end_date = (
                None
                if i == 0
                else start_date + timedelta(days=random.randint(365, 365 * 2))
            )

            experience = ExperienceEntry(
                id=str(uuid4()),
                company=random.choice(companies),
                position=random.choice(positions.get(role, positions["developer"])),
                location=random.choice(
                    ["San Francisco, CA", "Seattle, WA", "Austin, TX", "New York, NY"]
                ),
                start_date=start_date,
                end_date=end_date,
                is_current=i == 0,
                experience_type=ExperienceType.FULL_TIME,
                default_description=self._generate_job_description(role),
                default_achievements=self._generate_achievements(role),
                skills_used=self._get_role_skills(role),
                technologies=self._get_role_technologies(role),
                has_variations=True,
            )
            experiences.append(experience)

        return experiences

    def _generate_job_description(self, role: str) -> str:
        """Generate a realistic job description."""
        descriptions = {
            "developer": "Led development of web applications using modern JavaScript frameworks, collaborated with cross-functional teams, and implemented scalable backend solutions.",
            "data_scientist": "Developed machine learning models for business optimization, analyzed large datasets to identify trends, and created data visualizations for stakeholders.",
            "product_manager": "Managed product roadmap and strategy, worked with engineering teams to deliver features, and conducted user research to inform product decisions.",
        }
        return descriptions.get(
            role,
            "Contributed to various projects and collaborated with team members to achieve business objectives.",
        )

    def _generate_achievements(self, role: str) -> List[str]:
        """Generate realistic achievements for a role."""
        achievements_map = {
            "developer": [
                "Improved application performance by 40% through code optimization",
                "Led migration to microservices architecture serving 100k+ users",
                "Mentored 3 junior developers and established code review processes",
            ],
            "data_scientist": [
                "Developed predictive model that increased revenue by 25%",
                "Built automated data pipeline processing 1M+ records daily",
                "Presented insights to C-level executives driving strategic decisions",
            ],
            "product_manager": [
                "Launched 5 major features resulting in 30% user engagement increase",
                "Coordinated cross-functional teams of 15+ people across 3 time zones",
                "Implemented agile processes reducing time-to-market by 50%",
            ],
        }
        return achievements_map.get(
            role, ["Achieved project goals and exceeded expectations"]
        )

    def _get_role_skills(self, role: str) -> List[str]:
        """Get relevant skills for a role."""
        skills_map = {
            "developer": ["JavaScript", "React", "Node.js", "Python", "AWS", "Git"],
            "data_scientist": [
                "Python",
                "R",
                "SQL",
                "Machine Learning",
                "TensorFlow",
                "Tableau",
            ],
            "product_manager": [
                "Agile",
                "User Research",
                "Data Analysis",
                "Jira",
                "Product Strategy",
            ],
        }
        return skills_map.get(
            role, ["Communication", "Problem Solving", "Team Collaboration"]
        )

    def _get_role_technologies(self, role: str) -> List[str]:
        """Get relevant technologies for a role."""
        tech_map = {
            "developer": [
                "React",
                "Node.js",
                "PostgreSQL",
                "Docker",
                "AWS",
                "Git",
                "TypeScript",
            ],
            "data_scientist": [
                "Python",
                "pandas",
                "scikit-learn",
                "Jupyter",
                "Apache Spark",
                "TensorFlow",
            ],
            "product_manager": [
                "Jira",
                "Confluence",
                "Figma",
                "Google Analytics",
                "Mixpanel",
                "Slack",
            ],
        }
        return tech_map.get(role, ["Microsoft Office", "Slack", "Email"])

    def _get_role_keywords(self, role: str) -> List[str]:
        """Get SEO keywords for a role."""
        keywords_map = {
            "developer": [
                "full-stack",
                "web development",
                "software engineering",
                "agile",
                "cloud",
            ],
            "data_scientist": [
                "machine learning",
                "data analysis",
                "statistical modeling",
                "big data",
                "AI",
            ],
            "product_manager": [
                "product strategy",
                "agile development",
                "user experience",
                "stakeholder management",
            ],
        }
        return keywords_map.get(role, ["professional", "experienced", "team player"])

    def _generate_experience_variations(
        self, experience_id: str, role: str
    ) -> List[ExperienceContentVariation]:
        """Generate content variations for an experience."""
        variations = []

        variation_focuses = [
            ContentFocusType.TECHNICAL,
            ContentFocusType.LEADERSHIP,
            ContentFocusType.RESULTS,
        ]

        for focus in variation_focuses:
            content = self._generate_variation_content(role, focus)
            variation = ExperienceContentVariation(
                id=str(uuid4()),
                title=f"{focus.value.title()} Focus",
                content=content,
                experience_id=experience_id,
                focus=focus,
                achievements=self._generate_achievements(role),
                skills_highlighted=self._get_role_skills(role)[:4],
                target_industries=["Technology", "Software"],
                target_roles=[role.replace("_", " ").title()],
                source=ContentSource.MANUAL,
                created_at=datetime.utcnow(),
            )
            variations.append(variation)

        return variations

    def _generate_variation_content(self, role: str, focus: ContentFocusType) -> str:
        """Generate content based on role and focus."""
        content_templates = {
            "developer": {
                ContentFocusType.TECHNICAL: "Architected and implemented scalable web applications using React, Node.js, and cloud technologies. Optimized database queries and API performance.",
                ContentFocusType.LEADERSHIP: "Led a team of 5 developers, established coding standards, and mentored junior team members. Facilitated agile ceremonies and sprint planning.",
                ContentFocusType.RESULTS: "Delivered 15+ features on time, improved system performance by 40%, and reduced bug reports by 60% through comprehensive testing.",
            },
            "data_scientist": {
                ContentFocusType.TECHNICAL: "Developed machine learning models using Python, TensorFlow, and scikit-learn. Built data pipelines and implemented statistical analysis workflows.",
                ContentFocusType.LEADERSHIP: "Led data science initiatives, presented findings to stakeholders, and collaborated with product teams to implement data-driven solutions.",
                ContentFocusType.RESULTS: "Increased model accuracy by 25%, processed 1M+ records daily, and generated insights that drove $500K in additional revenue.",
            },
        }

        return content_templates.get(role, {}).get(
            focus, "Contributed to team success and project objectives."
        )

    def _generate_education_entries(self, role: str) -> List[EducationEntry]:
        """Generate education entries."""
        educations = []

        degrees = {
            "developer": [
                ("Bachelor of Science", "Computer Science"),
                ("Master of Science", "Software Engineering"),
            ],
            "data_scientist": [
                ("Bachelor of Science", "Mathematics"),
                ("Master of Science", "Data Science"),
            ],
            "product_manager": [
                ("Bachelor of Business Administration", "Business"),
                ("Master of Business Administration", "MBA"),
            ],
        }

        universities = [
            "Stanford University",
            "UC Berkeley",
            "MIT",
            "Carnegie Mellon",
            "University of Washington",
        ]

        degree_list = degrees.get(role, degrees["developer"])

        for i, (degree, field) in enumerate(degree_list[:2]):  # Max 2 degrees
            start_year = 2015 - (i * 4)
            education = EducationEntry(
                id=str(uuid4()),
                institution=random.choice(universities),
                degree=degree,
                field_of_study=field,
                location=random.choice(["CA", "MA", "WA", "PA"]),
                start_date=date(start_year, 9, 1),
                end_date=date(start_year + 4, 6, 15),
                gpa=round(random.uniform(3.2, 4.0), 2),
                honors=(
                    ["Dean's List", "Magna Cum Laude"]
                    if random.choice([True, False])
                    else []
                ),
                relevant_coursework=self._get_relevant_coursework(role),
                default_description="Focused on theoretical foundations and practical applications in the field.",
            )
            educations.append(education)

        return educations

    def _get_relevant_coursework(self, role: str) -> List[str]:
        """Get relevant coursework for a role."""
        coursework_map = {
            "developer": [
                "Data Structures",
                "Algorithms",
                "Software Engineering",
                "Database Systems",
                "Web Development",
            ],
            "data_scientist": [
                "Statistics",
                "Machine Learning",
                "Data Mining",
                "Linear Algebra",
                "Probability Theory",
            ],
            "product_manager": [
                "Business Strategy",
                "Marketing",
                "Operations Management",
                "Finance",
                "Leadership",
            ],
        }
        return coursework_map.get(
            role, ["General Studies", "Critical Thinking", "Communication"]
        )

    def _generate_project_entries(self, role: str) -> List[ProjectEntry]:
        """Generate project entries."""
        projects = []

        project_names = {
            "developer": [
                "E-commerce Platform",
                "Task Management App",
                "Real-time Chat Application",
            ],
            "data_scientist": [
                "Customer Churn Prediction",
                "Sales Forecasting Model",
                "Recommendation Engine",
            ],
            "product_manager": [
                "Mobile App Launch",
                "Feature Optimization Project",
                "User Onboarding Redesign",
            ],
        }

        names = project_names.get(role, project_names["developer"])

        for i, name in enumerate(names):
            start_date = date.today() - timedelta(days=random.randint(30, 365 * 2))
            project = ProjectEntry(
                id=str(uuid4()),
                name=name,
                url=(
                    f"https://github.com/user/{name.lower().replace(' ', '-')}"
                    if role == "developer"
                    else None
                ),
                github_url=(
                    f"https://github.com/user/{name.lower().replace(' ', '-')}"
                    if role == "developer"
                    else None
                ),
                start_date=start_date,
                end_date=start_date + timedelta(days=random.randint(30, 180)),
                default_description=self._generate_project_description(role, name),
                default_achievements=self._generate_project_achievements(role),
                technologies=self._get_role_technologies(role)[:5],
            )
            projects.append(project)

        return projects

    def _generate_project_description(self, role: str, project_name: str) -> str:
        """Generate project description."""
        descriptions = {
            "E-commerce Platform": "Built a full-stack e-commerce platform with user authentication, payment processing, and admin dashboard.",
            "Customer Churn Prediction": "Developed machine learning model to predict customer churn using historical data and behavioral patterns.",
            "Mobile App Launch": "Led cross-functional team to launch mobile application, coordinating design, development, and marketing efforts.",
        }
        return descriptions.get(
            project_name,
            f"Worked on {project_name} to solve business challenges and improve user experience.",
        )

    def _generate_project_achievements(self, role: str) -> List[str]:
        """Generate project achievements."""
        achievements_map = {
            "developer": [
                "Reduced load time by 50%",
                "Implemented responsive design",
                "Added comprehensive testing",
            ],
            "data_scientist": [
                "Achieved 92% accuracy",
                "Processed 100k+ data points",
                "Reduced processing time by 30%",
            ],
            "product_manager": [
                "Increased user adoption by 40%",
                "Coordinated team of 8 people",
                "Delivered on time and budget",
            ],
        }
        return achievements_map.get(role, ["Successfully completed project objectives"])

    def _generate_certifications(self, role: str) -> List[Certification]:
        """Generate certifications."""
        certifications = []

        cert_options = {
            "developer": [
                ("AWS Certified Developer", "Amazon Web Services"),
                ("Certified Kubernetes Administrator", "CNCF"),
                ("Google Cloud Professional Developer", "Google Cloud"),
            ],
            "data_scientist": [
                ("TensorFlow Developer Certificate", "Google"),
                ("AWS Machine Learning Specialty", "Amazon Web Services"),
                ("Microsoft Azure Data Scientist", "Microsoft"),
            ],
            "product_manager": [
                ("Certified Scrum Product Owner", "Scrum Alliance"),
                ("Google Analytics Certified", "Google"),
                ("Product Management Certificate", "Product School"),
            ],
        }

        available_certs = cert_options.get(role, cert_options["developer"])

        for i, (name, issuer) in enumerate(
            random.sample(available_certs, min(2, len(available_certs)))
        ):
            issue_date = date.today() - timedelta(days=random.randint(30, 730))
            cert = Certification(
                id=str(uuid4()),
                name=name,
                issuer=issuer,
                issue_date=issue_date,
                expiry_date=(
                    issue_date + timedelta(days=365 * 3)
                    if random.choice([True, False])
                    else None
                ),
                credential_id=f"CERT-{random.randint(100000, 999999)}",
                url=f"https://credentials.{issuer.lower().replace(' ', '')}.com/cert-{random.randint(100000, 999999)}",
                description=f"Professional certification demonstrating expertise in {name}",
            )
            certifications.append(cert)

        return certifications

    # =========================================================================
    # COMPREHENSIVE DATA CREATION
    # =========================================================================

    def create_companies(self) -> List[str]:
        """Create sample companies with proper normalization."""
        companies_data = [
            {
                "name": "TechFlow Solutions",
                "normalized_name": "techflow solutions",
                "domain": "techflowsolutions.com",
                "industry": "Software Development",
                "size": "201-500 employees",
                "size_category": CompanySizeCategory.MEDIUM,
                "location": "San Francisco, CA",
                "headquarters_location": "San Francisco, CA",
                "founded_year": 2015,
                "website": "https://techflowsolutions.com",
                "description": "Leading provider of enterprise software solutions specializing in cloud-native applications and data analytics.",
                "culture": "Fast-paced, collaborative environment with focus on innovation and continuous learning.",
                "values": ["Innovation", "Collaboration", "Excellence", "Integrity"],
                "benefits": [
                    "Health Insurance",
                    "401k Matching",
                    "Flexible PTO",
                    "Remote Work",
                    "Learning Budget",
                ],
            },
            {
                "name": "DataVision Analytics",
                "normalized_name": "datavision analytics",
                "domain": "datavisionanalytics.com",
                "industry": "Data Analytics",
                "size": "51-200 employees",
                "size_category": CompanySizeCategory.SMALL,
                "location": "Seattle, WA",
                "headquarters_location": "Seattle, WA",
                "founded_year": 2018,
                "website": "https://datavisionanalytics.com",
                "description": "Data-driven insights company helping businesses make smarter decisions through advanced analytics and machine learning.",
                "culture": "Data-driven culture with emphasis on scientific methodology and evidence-based decisions.",
                "values": [
                    "Data-Driven",
                    "Scientific Rigor",
                    "Customer Success",
                    "Transparency",
                ],
                "benefits": [
                    "Health Insurance",
                    "Stock Options",
                    "Professional Development",
                    "Remote Work",
                    "Gym Membership",
                ],
            },
            {
                "name": "InnovateLabs Inc",
                "normalized_name": "innovatelabs inc",
                "domain": "innovatelabs.com",
                "industry": "Product Development",
                "size": "101-250 employees",
                "size_category": CompanySizeCategory.MEDIUM,
                "location": "Austin, TX",
                "headquarters_location": "Austin, TX",
                "founded_year": 2012,
                "website": "https://innovatelabs.com",
                "description": "Product innovation company focused on bringing cutting-edge consumer technology to market.",
                "culture": "Creative, user-focused environment with rapid prototyping and iterative development.",
                "values": ["User-Centric", "Innovation", "Speed", "Quality"],
                "benefits": [
                    "Health Insurance",
                    "Equity",
                    "Unlimited PTO",
                    "Product Discounts",
                    "Team Events",
                ],
            },
            {
                "name": "CloudScale Systems",
                "normalized_name": "cloudscale systems",
                "domain": "cloudscalesystems.com",
                "industry": "Cloud Infrastructure",
                "size": "501-1000 employees",
                "size_category": CompanySizeCategory.LARGE,
                "location": "New York, NY",
                "headquarters_location": "New York, NY",
                "founded_year": 2010,
                "website": "https://cloudscalesystems.com",
                "description": "Enterprise cloud infrastructure provider offering scalable solutions for modern businesses.",
                "culture": "Engineering-focused culture with emphasis on reliability, scalability, and operational excellence.",
                "values": ["Reliability", "Scalability", "Security", "Customer Trust"],
                "benefits": [
                    "Comprehensive Health",
                    "401k",
                    "Parental Leave",
                    "Learning Budget",
                    "Sabbatical",
                ],
            },
            {
                "name": "StartupVelocity",
                "normalized_name": "startupvelocity",
                "domain": "startupvelocity.com",
                "industry": "Startup Incubator",
                "size": "11-50 employees",
                "size_category": CompanySizeCategory.STARTUP,
                "location": "Los Angeles, CA",
                "headquarters_location": "Los Angeles, CA",
                "founded_year": 2020,
                "website": "https://startupvelocity.com",
                "description": "Early-stage startup incubator and accelerator helping entrepreneurs build the next generation of technology companies.",
                "culture": "High-energy, entrepreneurial environment with focus on rapid growth and market disruption.",
                "values": ["Entrepreneurship", "Risk-Taking", "Growth", "Disruption"],
                "benefits": [
                    "Equity Participation",
                    "Flexible Schedule",
                    "Startup Perks",
                    "Networking Events",
                    "Mentorship",
                ],
            },
        ]

        company_ids = []
        with self._get_session() as session:
            for company_data in companies_data:
                # Check if company already exists
                existing = (
                    session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.name == company_data["name"])
                    .first()
                )

                if existing:
                    company_ids.append(existing.id)
                    continue

                company = CompanyInfoDB(
                    id=str(uuid4()),
                    name=company_data["name"],
                    normalized_name=company_data["normalized_name"],
                    domain=company_data["domain"],
                    industry=company_data["industry"],
                    size=company_data["size"],
                    size_category=company_data["size_category"],
                    location=company_data["location"],
                    headquarters_location=company_data["headquarters_location"],
                    founded_year=company_data["founded_year"],
                    website=company_data["website"],
                    description=company_data["description"],
                    culture=company_data["culture"],
                    values=company_data["values"],
                    benefits=company_data["benefits"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(company)
                session.commit()
                session.refresh(company)
                company_ids.append(company.id)

        print(f"   🏢 Created/found {len(company_ids)} companies")
        return company_ids

    def create_job_sources(self) -> List[str]:
        """Create job board sources."""
        sources_data = [
            {
                "name": "linkedin",
                "display_name": "LinkedIn Jobs",
                "base_url": "https://www.linkedin.com/jobs",
                "api_available": False,
                "is_active": True,
            },
            {
                "name": "indeed",
                "display_name": "Indeed",
                "base_url": "https://www.indeed.com",
                "api_available": True,
                "is_active": True,
            },
            {
                "name": "glassdoor",
                "display_name": "Glassdoor",
                "base_url": "https://www.glassdoor.com",
                "api_available": False,
                "is_active": True,
            },
        ]

        source_ids = []
        with self._get_session() as session:
            for source_data in sources_data:
                # Check if source already exists
                existing = (
                    session.query(JobSourceDB)
                    .filter(JobSourceDB.name == source_data["name"])
                    .first()
                )

                if existing:
                    source_ids.append(existing.id)
                    continue

                source = JobSourceDB(
                    id=str(uuid4()),
                    name=source_data["name"],
                    display_name=source_data["display_name"],
                    base_url=source_data["base_url"],
                    api_available=source_data["api_available"],
                    is_active=source_data["is_active"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(source)
                session.commit()
                session.refresh(source)
                source_ids.append(source.id)

        print(f"   🔗 Created/found {len(source_ids)} job sources")
        return source_ids

    def create_job_embeddings(self, job_ids: List[str]) -> List[str]:
        """Create mock embeddings for job listings."""
        embedding_ids = []
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        embedding_dimension = 384

        with self._get_session() as session:
            for job_id in job_ids:
                # Check if embedding already exists for this job
                existing = (
                    session.query(JobEmbeddingDB)
                    .filter(JobEmbeddingDB.job_id == job_id)
                    .first()
                )

                if existing:
                    embedding_ids.append(existing.id)
                    continue

                # Get job details for creating content hash
                job = (
                    session.query(JobListingDB)
                    .filter(JobListingDB.id == job_id)
                    .first()
                )

                if not job:
                    continue

                # Create content hash from job description and title
                import hashlib

                content_text = (
                    f"{job.title} {job.description or ''} {job.requirements or ''}"
                )
                content_hash = hashlib.md5(content_text.encode()).hexdigest()

                # Generate realistic embedding vector (384-dimensional)
                # In a real implementation, this would use an actual embedding model
                import random

                random.seed(
                    hash(content_hash) % (2**32)
                )  # Deterministic based on content
                embedding_vector = [
                    round(random.uniform(-1.0, 1.0), 6)
                    for _ in range(embedding_dimension)
                ]

                # Create embedding record
                embedding = JobEmbeddingDB(
                    id=str(uuid4()),
                    job_id=job_id,
                    embedding_model=model_name,
                    content_hash=content_hash,
                    embedding_vector=embedding_vector,
                    embedding_dimension=embedding_dimension,
                    content_type="job_description",
                    created_at=datetime.utcnow(),
                )
                session.add(embedding)
                session.commit()
                session.refresh(embedding)
                embedding_ids.append(embedding.id)

        print(f"   🧠 Created/found {len(embedding_ids)} job embeddings")
        return embedding_ids

    def create_job_duplications(self, job_ids: List[str]) -> List[str]:
        """Create job duplication records with realistic confidence scores."""
        if len(job_ids) < 2:
            print(
                f"   ⚠️  Need at least 2 jobs to create duplications, only have {len(job_ids)}"
            )
            return []

        duplication_ids = []

        with self._get_session() as session:
            # Create 2-3 duplication pairs with different scenarios
            scenarios = [
                {
                    "name": "Similar titles, same company",
                    "confidence_range": (0.90, 0.95),
                    "matching_fields": ["title", "company", "location"],
                    "status": "confirmed",
                    "notes": "Near-identical positions posted on different job boards",
                },
                {
                    "name": "Same title, different companies in same location",
                    "confidence_range": (0.85, 0.90),
                    "matching_fields": ["title", "location", "requirements"],
                    "status": "likely",
                    "notes": "Similar roles with matching skill requirements",
                },
                {
                    "name": "Similar responsibilities, different titles",
                    "confidence_range": (0.85, 0.88),
                    "matching_fields": ["requirements", "responsibilities", "location"],
                    "status": "possible",
                    "notes": "Different job titles but overlapping responsibilities",
                },
            ]

            # Get all jobs for matching
            jobs = (
                session.query(JobListingDB).filter(JobListingDB.id.in_(job_ids)).all()
            )

            # Create duplication pairs based on scenarios
            for i, scenario in enumerate(scenarios[: min(3, len(job_ids) // 2)]):
                # Select two jobs for this scenario
                available_jobs = [
                    j for j in jobs if j.id not in [d for d in duplication_ids]
                ]
                if len(available_jobs) < 2:
                    # Use all available jobs if needed
                    available_jobs = jobs

                canonical_job = available_jobs[i * 2 % len(available_jobs)]
                duplicate_job = available_jobs[(i * 2 + 1) % len(available_jobs)]

                # Skip if trying to duplicate the same job
                if canonical_job.id == duplicate_job.id:
                    continue

                # Check if this duplication pair already exists
                existing = (
                    session.query(JobDeduplicationDB)
                    .filter(
                        (
                            (JobDeduplicationDB.canonical_job_id == canonical_job.id)
                            & (JobDeduplicationDB.duplicate_job_id == duplicate_job.id)
                        )
                        | (
                            (JobDeduplicationDB.canonical_job_id == duplicate_job.id)
                            & (JobDeduplicationDB.duplicate_job_id == canonical_job.id)
                        )
                    )
                    .first()
                )

                if existing:
                    duplication_ids.append(existing.id)
                    continue

                # Generate realistic confidence score within scenario range
                confidence_score = round(
                    random.uniform(*scenario["confidence_range"]), 3
                )

                # Create the duplication record using only fields that exist in the model
                duplication = JobDeduplicationDB(
                    id=str(uuid4()),
                    canonical_job_id=canonical_job.id,
                    duplicate_job_id=duplicate_job.id,
                    confidence_score=confidence_score,
                    matching_fields=scenario["matching_fields"],
                    merge_strategy="keep_canonical",
                    reviewed=False,  # Automated detection, not yet reviewed
                    created_at=datetime.utcnow(),
                )

                session.add(duplication)
                session.commit()
                session.refresh(duplication)
                duplication_ids.append(duplication.id)

                print(
                    f"   🔗 Created duplication: {canonical_job.title} <-> {duplicate_job.title} (confidence: {confidence_score})"
                )

        print(f"   🎯 Created/found {len(duplication_ids)} job duplications")
        return duplication_ids

    def create_job_source_listings(
        self, job_ids: List[str], source_ids: List[str]
    ) -> List[str]:
        """Create job source listings to show jobs appearing on multiple platforms."""
        if not job_ids or not source_ids:
            print("   ⚠️  Need jobs and sources to create source listings")
            return []

        source_listing_ids = []

        with self._get_session() as session:
            # Get all jobs and sources for processing
            jobs = (
                session.query(JobListingDB).filter(JobListingDB.id.in_(job_ids)).all()
            )
            sources = (
                session.query(JobSourceDB).filter(JobSourceDB.id.in_(source_ids)).all()
            )

            # For each job, create 1-3 source listings (showing same job on multiple platforms)
            for job in jobs:
                # Determine how many sources this job appears on (1-3)
                num_sources = random.choice(
                    [1, 1, 2, 2, 3]
                )  # Weighted toward 1-2 sources
                selected_sources = random.sample(
                    sources, min(num_sources, len(sources))
                )

                for source in selected_sources:
                    # Check if this job-source combination already exists
                    existing = (
                        session.query(JobSourceListingDB)
                        .filter(
                            JobSourceListingDB.job_id == job.id,
                            JobSourceListingDB.source_id == source.id,
                        )
                        .first()
                    )

                    if existing:
                        source_listing_ids.append(existing.id)
                        continue

                    # Generate platform-specific data
                    platform_data = self._generate_source_listing_data(job, source)

                    # Create the source listing
                    source_listing = JobSourceListingDB(
                        id=str(uuid4()),
                        job_id=job.id,
                        source_id=source.id,
                        source_job_id=platform_data["source_job_id"],
                        source_url=platform_data["source_url"],
                        source_metadata=platform_data["metadata"],
                        scraped_at=platform_data["scraped_at"],
                        last_updated=platform_data["last_updated"],
                    )

                    session.add(source_listing)
                    session.commit()
                    session.refresh(source_listing)
                    source_listing_ids.append(source_listing.id)

        print(f"   🔗 Created/found {len(source_listing_ids)} job source listings")
        return source_listing_ids

    def _generate_source_listing_data(
        self, job: JobListingDB, source: JobSourceDB
    ) -> Dict[str, Any]:
        """Generate platform-specific data for a job source listing."""
        import random
        from datetime import datetime, timedelta

        # Generate scraped/updated times (within last 30 days)
        scraped_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        last_updated = scraped_at + timedelta(hours=random.randint(0, 72))

        # Platform-specific data generation
        if source.name == "linkedin":
            return {
                "source_job_id": f"linkedin_{random.randint(1000000000, 9999999999)}",
                "source_url": f"https://www.linkedin.com/jobs/view/{random.randint(1000000000, 9999999999)}",
                "metadata": {
                    "platform": "LinkedIn",
                    "job_function": self._get_linkedin_job_function(job.title),
                    "seniority_level": (
                        job.experience_level.value
                        if job.experience_level
                        else "Mid-Senior level"
                    ),
                    "employment_type": (
                        job.job_type.value if job.job_type else "Full-time"
                    ),
                    "company_linkedin_id": f"company_{random.randint(100000, 999999)}",
                    "posting_language": "en",
                    "easy_apply": random.choice([True, False]),
                    "linkedin_recruiter_posted": random.choice([True, False]),
                    "view_count": random.randint(50, 2000),
                    "applicant_count": random.randint(10, 500),
                },
                "scraped_at": scraped_at,
                "last_updated": last_updated,
            }

        elif source.name == "indeed":
            return {
                "source_job_id": f"indeed_{random.randint(100000000, 999999999)}",
                "source_url": f"https://www.indeed.com/viewjob?jk={random.randint(100000000, 999999999)}",
                "metadata": {
                    "platform": "Indeed",
                    "job_key": f"jk_{random.randint(100000000, 999999999)}",
                    "sponsored": random.choice([True, False]),
                    "indeed_apply": random.choice([True, False]),
                    "company_rating": round(random.uniform(3.0, 5.0), 1),
                    "company_review_count": random.randint(10, 5000),
                    "urgently_hiring": random.choice([True, False]),
                    "work_from_home": (
                        job.remote_type.value if job.remote_type else "No"
                    ),
                    "estimated_salary": (
                        {
                            "min": job.salary_min,
                            "max": job.salary_max,
                            "currency": job.salary_currency or "USD",
                        }
                        if job.salary_min
                        else None
                    ),
                },
                "scraped_at": scraped_at,
                "last_updated": last_updated,
            }

        elif source.name == "glassdoor":
            return {
                "source_job_id": f"glassdoor_{random.randint(10000000, 99999999)}",
                "source_url": f"https://www.glassdoor.com/job-listing/{random.randint(10000000, 99999999)}",
                "metadata": {
                    "platform": "Glassdoor",
                    "employer_id": f"EI_IC{random.randint(1000000, 9999999)}",
                    "company_rating": round(random.uniform(2.5, 5.0), 1),
                    "company_review_count": random.randint(50, 10000),
                    "ceo_approval_rating": round(random.uniform(60, 95), 0),
                    "recommend_to_friend_rating": round(random.uniform(50, 90), 0),
                    "easy_apply": random.choice([True, False]),
                    "company_size": self._get_glassdoor_company_size(job),
                    "company_industry": (
                        job.company.industry if job.company else "Technology"
                    ),
                    "salary_estimate": (
                        {
                            "min": job.salary_min,
                            "max": job.salary_max,
                            "source": random.choice(
                                ["Glassdoor Estimate", "Employer Provided"]
                            ),
                        }
                        if job.salary_min
                        else None
                    ),
                },
                "scraped_at": scraped_at,
                "last_updated": last_updated,
            }

        else:
            # Generic source data
            return {
                "source_job_id": f"{source.name}_{random.randint(100000, 999999)}",
                "source_url": f"{source.base_url}/job/{random.randint(100000, 999999)}",
                "metadata": {
                    "platform": source.display_name,
                    "job_reference": f"JOB_{random.randint(100000, 999999)}",
                    "posting_date": (
                        scraped_at - timedelta(days=random.randint(1, 14))
                    ).isoformat(),
                    "application_method": random.choice(
                        ["Direct", "Email", "External Link"]
                    ),
                },
                "scraped_at": scraped_at,
                "last_updated": last_updated,
            }

    def _get_linkedin_job_function(self, job_title: str) -> str:
        """Map job title to LinkedIn job function."""
        title_lower = job_title.lower()

        if any(
            word in title_lower
            for word in ["engineer", "developer", "architect", "devops"]
        ):
            return "Engineering"
        elif any(
            word in title_lower
            for word in ["data", "scientist", "analyst", "machine learning"]
        ):
            return "Information Technology"
        elif any(word in title_lower for word in ["product", "manager", "owner"]):
            return "Product Management"
        elif any(word in title_lower for word in ["design", "ux", "ui"]):
            return "Design"
        elif any(word in title_lower for word in ["marketing", "growth", "brand"]):
            return "Marketing"
        elif any(word in title_lower for word in ["sales", "business development"]):
            return "Sales"
        else:
            return "Information Technology"

    def _get_glassdoor_company_size(self, job: JobListingDB) -> str:
        """Get Glassdoor-style company size description."""
        if job.company and job.company.size:
            size_str = job.company.size.lower()
            if "1-50" in size_str or "11-50" in size_str:
                return "1-50 employees"
            elif "51-200" in size_str:
                return "51-200 employees"
            elif "201-500" in size_str or "101-250" in size_str:
                return "201-500 employees"
            elif "501-1000" in size_str:
                return "501-1000 employees"
            elif "1000+" in size_str:
                return "1000+ employees"
        return "201-500 employees"  # Default

    def create_job_listings(self, company_ids: List[str]) -> List[str]:
        """Create sample job listings."""
        jobs_data = [
            # Software Engineer Jobs
            {
                "title": "Senior Full Stack Engineer",
                "description": "We're looking for an experienced full stack engineer to join our growing team. You'll work on building scalable web applications using modern technologies like React, Node.js, and cloud platforms.",
                "requirements": "5+ years of experience with JavaScript, React, Node.js, and cloud platforms (AWS/GCP). Experience with TypeScript, GraphQL, and microservices architecture preferred.",
                "responsibilities": "Design and develop scalable web applications, collaborate with product and design teams, mentor junior developers, participate in code reviews and architecture decisions.",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.HYBRID,
                "experience_level": ExperienceLevel.SENIOR_LEVEL,
                "salary_min": 120000,
                "salary_max": 160000,
                "skills_required": [
                    "JavaScript",
                    "React",
                    "Node.js",
                    "AWS",
                    "PostgreSQL",
                ],
                "skills_preferred": ["TypeScript", "GraphQL", "Docker", "Kubernetes"],
                "benefits": [
                    "Health Insurance",
                    "401k Matching",
                    "Stock Options",
                    "Flexible PTO",
                ],
                "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
                "tech_stack": ["React", "Node.js", "TypeScript", "PostgreSQL", "AWS"],
            },
            {
                "title": "Frontend Developer",
                "description": "Join our frontend team to build beautiful, responsive user interfaces for our web applications. Work with modern frameworks and collaborate closely with our design team.",
                "requirements": "3+ years experience with React, JavaScript, HTML/CSS. Experience with state management libraries and modern build tools.",
                "responsibilities": "Develop responsive web interfaces, implement design systems, optimize for performance, collaborate with UX designers.",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.REMOTE,
                "experience_level": ExperienceLevel.MID_LEVEL,
                "salary_min": 90000,
                "salary_max": 120000,
                "skills_required": ["React", "JavaScript", "HTML", "CSS"],
                "skills_preferred": ["TypeScript", "Next.js", "Tailwind CSS"],
                "benefits": ["Health Insurance", "Remote Work", "Learning Budget"],
                "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
                "tech_stack": [
                    "React",
                    "JavaScript",
                    "TypeScript",
                    "Next.js",
                    "Tailwind CSS",
                ],
            },
            # Data Science Jobs
            {
                "title": "Data Scientist",
                "description": "We're seeking a data scientist to help us unlock insights from our data and build predictive models that drive business decisions.",
                "requirements": "PhD or Masters in Data Science, Statistics, or related field. 3+ years experience with Python, SQL, and machine learning frameworks.",
                "responsibilities": "Analyze complex datasets, build machine learning models, create data visualizations, collaborate with product teams.",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.HYBRID,
                "experience_level": ExperienceLevel.MID_LEVEL,
                "salary_min": 110000,
                "salary_max": 140000,
                "skills_required": ["Python", "SQL", "Machine Learning", "Statistics"],
                "skills_preferred": [
                    "TensorFlow",
                    "PyTorch",
                    "Tableau",
                    "Apache Spark",
                ],
                "benefits": ["Health Insurance", "Stock Options", "Conference Budget"],
                "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
                "tech_stack": ["Python", "TensorFlow", "Jupyter", "SQL", "Tableau"],
            },
            {
                "title": "Senior Machine Learning Engineer",
                "description": "Lead our ML engineering efforts to deploy and scale machine learning models in production environments.",
                "requirements": "5+ years experience in ML engineering, Python, and cloud platforms. Experience with MLOps and model deployment.",
                "responsibilities": "Design ML pipelines, deploy models to production, optimize model performance, mentor junior ML engineers.",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.REMOTE,
                "experience_level": ExperienceLevel.SENIOR_LEVEL,
                "salary_min": 140000,
                "salary_max": 180000,
                "skills_required": ["Python", "TensorFlow", "Kubernetes", "AWS"],
                "skills_preferred": ["MLflow", "Kubeflow", "Docker", "Apache Airflow"],
                "benefits": ["Health Insurance", "Equity", "Flexible Schedule"],
                "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
                "tech_stack": ["Python", "TensorFlow", "Kubernetes", "MLflow", "AWS"],
            },
            # Product Manager Jobs
            {
                "title": "Senior Product Manager",
                "description": "Drive product strategy and roadmap for our core platform. Work closely with engineering, design, and business stakeholders.",
                "requirements": "5+ years of product management experience, preferably in B2B SaaS. Strong analytical skills and user research experience.",
                "responsibilities": "Define product strategy, manage product roadmap, conduct user research, work with engineering teams, analyze product metrics.",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.HYBRID,
                "experience_level": ExperienceLevel.SENIOR_LEVEL,
                "salary_min": 130000,
                "salary_max": 160000,
                "skills_required": [
                    "Product Strategy",
                    "User Research",
                    "Analytics",
                    "Agile",
                ],
                "skills_preferred": ["SQL", "A/B Testing", "Figma", "Jira"],
                "benefits": ["Health Insurance", "Stock Options", "Unlimited PTO"],
                "seniority_level": SeniorityLevel.MANAGER,
                "tech_stack": [
                    "Jira",
                    "Confluence",
                    "Figma",
                    "Google Analytics",
                    "Mixpanel",
                ],
            },
            {
                "title": "Product Owner",
                "description": "Own the product backlog and work closely with development teams to deliver value to our users.",
                "requirements": "3+ years as Product Owner or similar role. Experience with Agile/Scrum methodologies. Strong communication skills.",
                "responsibilities": "Manage product backlog, write user stories, prioritize features, work with development teams, gather user feedback.",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.ON_SITE,
                "experience_level": ExperienceLevel.MID_LEVEL,
                "salary_min": 95000,
                "salary_max": 125000,
                "skills_required": [
                    "Agile/Scrum",
                    "User Stories",
                    "Backlog Management",
                ],
                "skills_preferred": ["Jira", "User Research", "Data Analysis"],
                "benefits": ["Health Insurance", "401k", "Team Events"],
                "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
                "tech_stack": ["Jira", "Confluence", "Figma"],
            },
            # Additional diverse jobs
            {
                "title": "DevOps Engineer",
                "description": "Build and maintain our cloud infrastructure and CI/CD pipelines. Help scale our platform to serve millions of users.",
                "requirements": "4+ years experience with cloud platforms, containerization, and infrastructure as code. Strong scripting skills.",
                "responsibilities": "Manage cloud infrastructure, build deployment pipelines, monitor system performance, ensure security compliance.",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.REMOTE,
                "experience_level": ExperienceLevel.SENIOR_LEVEL,
                "salary_min": 115000,
                "salary_max": 145000,
                "skills_required": ["AWS", "Docker", "Kubernetes", "Terraform"],
                "skills_preferred": ["Jenkins", "Ansible", "Monitoring", "Security"],
                "benefits": ["Health Insurance", "Remote Work", "On-call Bonus"],
                "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
                "tech_stack": ["AWS", "Docker", "Kubernetes", "Terraform", "Jenkins"],
            },
            {
                "title": "UX Designer",
                "description": "Design intuitive user experiences for our web and mobile applications. Conduct user research and create design systems.",
                "requirements": "3+ years of UX design experience. Proficiency with design tools like Figma. Experience with user research methodologies.",
                "responsibilities": "Create user interfaces, conduct usability testing, develop design systems, collaborate with product and engineering teams.",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.HYBRID,
                "experience_level": ExperienceLevel.MID_LEVEL,
                "salary_min": 85000,
                "salary_max": 110000,
                "skills_required": [
                    "UX Design",
                    "Figma",
                    "User Research",
                    "Prototyping",
                ],
                "skills_preferred": [
                    "Design Systems",
                    "Usability Testing",
                    "Adobe Creative Suite",
                ],
                "benefits": ["Health Insurance", "Creative Budget", "Flexible Hours"],
                "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
                "tech_stack": ["Figma", "Adobe Creative Suite", "InVision", "Miro"],
            },
        ]

        job_ids = []
        with self._get_session() as session:
            for i, job_data in enumerate(jobs_data):
                # Assign company cyclically
                company_id = company_ids[i % len(company_ids)]
                company = (
                    session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.id == company_id)
                    .first()
                )

                # Check if job already exists
                existing = (
                    session.query(JobListingDB)
                    .filter(
                        JobListingDB.title == job_data["title"],
                        JobListingDB.company_id == company_id,
                    )
                    .first()
                )

                if existing:
                    job_ids.append(existing.id)
                    continue

                job = JobListingDB(
                    id=str(uuid4()),
                    title=job_data["title"],
                    company_id=company_id,
                    location=company.location,
                    description=job_data["description"],
                    requirements=job_data["requirements"],
                    responsibilities=job_data["responsibilities"],
                    job_type=job_data["job_type"],
                    remote_type=job_data["remote_type"],
                    experience_level=job_data["experience_level"],
                    salary_min=job_data["salary_min"],
                    salary_max=job_data["salary_max"],
                    salary_currency="USD",
                    skills_required=job_data["skills_required"],
                    skills_preferred=job_data["skills_preferred"],
                    benefits=job_data["benefits"],
                    # company_size and industry removed - now available through company relationship
                    job_url=f"{company.website}/jobs/{job_data['title'].lower().replace(' ', '-')}",
                    application_url=f"{company.website}/apply/{str(uuid4())[:8]}",
                    posted_date=datetime.utcnow()
                    - timedelta(days=random.randint(1, 30)),
                    application_deadline=datetime.utcnow()
                    + timedelta(days=random.randint(30, 90)),
                    source="mock_data",
                    status=JobStatus.ACTIVE,
                    source_count=1,
                    data_quality_score=random.uniform(0.8, 1.0),
                    scraped_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                    last_verified=datetime.utcnow()
                    - timedelta(days=random.randint(0, 3)),
                    verification_status=VerificationStatus.ACTIVE,
                    company_size_category=self._get_company_size_category(company.size),
                    seniority_level=job_data["seniority_level"],
                    tech_stack=job_data["tech_stack"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(job)
                session.commit()
                session.refresh(job)
                job_ids.append(job.id)

        print(f"   💼 Created/found {len(job_ids)} job listings")
        return job_ids

    def _get_company_size_category(self, size_string: str) -> CompanySizeCategory:
        """Convert size string to category enum."""
        # Check in order from largest to smallest ranges to avoid substring conflicts
        if "501-1000" in size_string:
            return CompanySizeCategory.LARGE
        elif "201-500" in size_string:
            return CompanySizeCategory.MEDIUM
        elif "101-250" in size_string:
            return CompanySizeCategory.MEDIUM
        elif "51-200" in size_string:
            return CompanySizeCategory.SMALL
        elif "11-50" in size_string:
            return CompanySizeCategory.STARTUP
        elif "1-50" in size_string:
            return CompanySizeCategory.STARTUP
        elif "1000+" in size_string:
            return CompanySizeCategory.ENTERPRISE
        else:
            return CompanySizeCategory.ENTERPRISE

    def create_resume_templates(self) -> List[str]:
        """Create sample resume templates."""
        templates_data = [
            {
                "name": "Modern Professional",
                "description": "Clean, modern template perfect for tech professionals",
                "sections": [
                    "contact",
                    "summary",
                    "experience",
                    "skills",
                    "education",
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
                    "font_family": "Inter",
                    "color_scheme": "blue",
                    "layout": "single_column",
                },
                "is_default": True,
                "is_system": True,
            },
            {
                "name": "Executive",
                "description": "Professional template for senior leadership roles",
                "sections": [
                    "contact",
                    "summary",
                    "experience",
                    "education",
                    "skills",
                    "certifications",
                ],
                "section_order": [
                    "contact",
                    "summary",
                    "experience",
                    "education",
                    "skills",
                    "certifications",
                ],
                "styling": {
                    "font_family": "Times New Roman",
                    "color_scheme": "black",
                    "layout": "two_column",
                },
                "is_default": False,
                "is_system": True,
            },
            {
                "name": "Technical",
                "description": "Template optimized for technical roles with emphasis on skills",
                "sections": [
                    "contact",
                    "skills",
                    "experience",
                    "projects",
                    "education",
                    "certifications",
                ],
                "section_order": [
                    "contact",
                    "skills",
                    "experience",
                    "projects",
                    "education",
                    "certifications",
                ],
                "styling": {
                    "font_family": "Source Code Pro",
                    "color_scheme": "green",
                    "layout": "single_column",
                },
                "is_default": False,
                "is_system": True,
            },
        ]

        template_ids = []
        with self._get_session() as session:
            for template_data in templates_data:
                # Check if template already exists
                existing = (
                    session.query(ResumeTemplateDB)
                    .filter(ResumeTemplateDB.name == template_data["name"])
                    .first()
                )

                if existing:
                    template_ids.append(existing.id)
                    continue

                template = ResumeTemplateDB(
                    id=str(uuid4()),
                    name=template_data["name"],
                    description=template_data["description"],
                    sections=template_data["sections"],
                    section_order=template_data["section_order"],
                    styling=template_data["styling"],
                    is_default=template_data["is_default"],
                    is_system=template_data["is_system"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(template)
                session.commit()
                session.refresh(template)
                template_ids.append(template.id)

        print(f"   📄 Created/found {len(template_ids)} resume templates")
        return template_ids

    def create_resume_generations(self, resume_ids: List[str]) -> List[str]:
        """Create resume generations with mock file paths and metadata."""
        if not resume_ids:
            print("   ⚠️  No resume IDs provided for generation creation")
            return []

        # Import required models
        from app.data.resume_models import ResumeFormat, ResumeGenerationDB

        generation_ids = []

        # Different file formats to generate for each resume
        formats = [ResumeFormat.PDF, ResumeFormat.DOCX, ResumeFormat.HTML]

        # Sample template names
        template_names = [
            "Modern Professional",
            "ATS-Friendly",
            "Creative Portfolio",
            "Executive Summary",
            "Technical Focus",
        ]

        with self._get_session() as session:
            for resume_id in resume_ids:
                # Get resume details for context
                from app.data.resume_models import ResumeDB

                resume = (
                    session.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                )
                if not resume:
                    continue

                # Create 2-3 generations per resume (different formats)
                num_generations = random.randint(2, 3)
                selected_formats = random.sample(
                    formats, min(num_generations, len(formats))
                )

                for format_type in selected_formats:
                    # Check if generation already exists for this resume/format combo
                    existing = (
                        session.query(ResumeGenerationDB)
                        .filter(
                            ResumeGenerationDB.resume_id == resume_id,
                            ResumeGenerationDB.format == format_type.value,
                        )
                        .first()
                    )

                    if existing:
                        generation_ids.append(existing.id)
                        continue

                    # Generate realistic file paths
                    file_extension = format_type.value.lower()
                    user_id_short = resume.user_id[:8] if resume.user_id else "unknown"
                    version = random.randint(1, 5)
                    filename = (
                        f"user-{user_id_short}-resume-v{version}.{file_extension}"
                    )

                    # Different base paths for different formats
                    if format_type == ResumeFormat.PDF:
                        file_path = f"/tmp/resumes/pdf/{filename}"
                        base_size = 150000  # ~150KB
                    elif format_type == ResumeFormat.DOCX:
                        file_path = f"/tmp/resumes/docx/{filename}"
                        base_size = 80000  # ~80KB
                    elif format_type == ResumeFormat.HTML:
                        file_path = f"/tmp/resumes/html/{filename}"
                        base_size = 25000  # ~25KB
                    else:
                        file_path = f"/tmp/resumes/other/{filename}"
                        base_size = 50000  # ~50KB

                    # Add some randomness to file size (±30%)
                    size_variance = random.uniform(0.7, 1.3)
                    file_size = int(base_size * size_variance)

                    # Generate realistic generation parameters
                    generation_params = {
                        "template": random.choice(template_names),
                        "format": format_type.value,
                        "tone": random.choice(
                            ["professional", "creative", "technical"]
                        ),
                        "length": random.choice(["concise", "standard", "detailed"]),
                        "ai_provider": "openai",
                        "model": "gpt-4",
                        "focus_areas": random.sample(
                            [
                                "technical_skills",
                                "leadership",
                                "achievements",
                                "education",
                                "projects",
                                "certifications",
                            ],
                            random.randint(2, 4),
                        ),
                        "generation_time": round(
                            random.uniform(15.0, 45.0), 2
                        ),  # seconds
                        "optimization_applied": random.choice([True, False]),
                    }

                    # Determine generation status (most successful, some failed)
                    status_weights = (
                        ["completed"] * 85 + ["failed"] * 10 + ["pending"] * 5
                    )
                    status = random.choice(status_weights)

                    error_message = None
                    if status == "failed":
                        errors = [
                            "Template rendering failed",
                            "File system write error",
                            "PDF generation timeout",
                            "Template not found",
                            "Insufficient disk space",
                            "Network error during generation",
                        ]
                        error_message = random.choice(errors)
                        file_size = 0  # No file if failed

                    # Generate realistic timestamp (within last 90 days)
                    generated_at = datetime.utcnow() - timedelta(
                        days=random.randint(0, 90),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                    )

                    # Create generation record
                    generation = ResumeGenerationDB(
                        id=str(uuid4()),
                        resume_id=resume_id,
                        format=format_type.value,
                        template_name=generation_params["template"],
                        file_path=file_path,
                        file_size=file_size,
                        generation_params=generation_params,
                        status=status,
                        error_message=error_message,
                        generated_at=generated_at,
                    )

                    session.add(generation)
                    session.commit()
                    session.refresh(generation)
                    generation_ids.append(generation.id)

        print(f"   📄 Created/found {len(generation_ids)} resume generations")
        return generation_ids

    def create_resume_optimizations(
        self, resume_ids: List[str], job_ids: List[str]
    ) -> List[str]:
        """Create resume optimizations with realistic match scores and recommendations."""
        if not resume_ids or not job_ids:
            print("   ⚠️  Need both resume IDs and job IDs for optimization creation")
            return []

        # Import required model
        from app.data.resume_models import ResumeOptimizationDB

        optimization_ids = []

        # Create realistic optimization data
        with self._get_session() as session:
            # For each resume, create optimizations for 2-4 jobs
            for resume_id in resume_ids:
                # Get resume details for context
                from app.data.resume_models import ResumeDB

                resume = (
                    session.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                )
                if not resume:
                    continue

                # Select 2-4 jobs to optimize against
                num_optimizations = random.randint(2, min(4, len(job_ids)))
                selected_job_ids = random.sample(job_ids, num_optimizations)

                for job_id in selected_job_ids:
                    # Check if optimization already exists for this resume/job combo
                    existing = (
                        session.query(ResumeOptimizationDB)
                        .filter(
                            ResumeOptimizationDB.resume_id == resume_id,
                            ResumeOptimizationDB.job_id == job_id,
                        )
                        .first()
                    )

                    if existing:
                        optimization_ids.append(existing.id)
                        continue

                    # Get job details for realistic matching
                    job = (
                        session.query(JobListingDB)
                        .filter(JobListingDB.id == job_id)
                        .first()
                    )
                    if not job:
                        continue

                    # Generate realistic match score (75-95%)
                    match_score = round(random.uniform(75.0, 95.0), 1)

                    # Generate realistic keyword matches from job requirements
                    job_keywords = set()
                    if job.skills_required:
                        job_keywords.update(
                            skill.lower() for skill in job.skills_required
                        )
                    if job.skills_preferred:
                        job_keywords.update(
                            skill.lower() for skill in job.skills_preferred
                        )

                    # Add some keywords from job title and description
                    title_keywords = [
                        word.lower() for word in job.title.split() if len(word) > 2
                    ]
                    job_keywords.update(title_keywords[:3])  # Add top 3 title keywords

                    # Simulate keyword matching (60-85% of keywords match)
                    all_keywords = list(job_keywords)
                    if all_keywords:
                        match_percentage = random.uniform(0.6, 0.85)
                        num_matches = int(len(all_keywords) * match_percentage)
                        matched_keywords = random.sample(all_keywords, num_matches)
                        missing_keywords = [
                            kw for kw in all_keywords if kw not in matched_keywords
                        ]
                    else:
                        matched_keywords = []
                        missing_keywords = []

                    # Generate skill matches and missing skills
                    resume_skills = self._get_resume_skills_for_role(resume.title)
                    job_skills = job.skills_required or []
                    if job.skills_preferred:
                        job_skills.extend(job.skills_preferred)

                    # Simulate skill matching
                    skill_matches = []
                    missing_skills = []

                    for skill in job_skills:
                        if random.choice([True, False, True]):  # 67% chance of match
                            skill_matches.append(skill)
                        else:
                            missing_skills.append(skill)

                    # Add some realistic skills not in job requirements
                    additional_matches = random.sample(
                        resume_skills, min(3, len(resume_skills))
                    )
                    skill_matches.extend(additional_matches)

                    # Generate realistic recommendations
                    recommendations = self._generate_optimization_recommendations(
                        match_score, missing_skills, missing_keywords, job.title
                    )

                    # Sections to emphasize based on job type
                    sections_to_emphasize = self._get_sections_to_emphasize(job.title)

                    # Content suggestions
                    content_suggestions = self._generate_content_suggestions(
                        missing_skills, missing_keywords, job.title
                    )

                    # Generate realistic timestamp (within last 30 days)
                    analyzed_at = datetime.utcnow() - timedelta(
                        days=random.randint(0, 30),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                    )

                    # Create optimization record
                    optimization = ResumeOptimizationDB(
                        id=str(uuid4()),
                        resume_id=resume_id,
                        job_id=job_id,
                        match_score=match_score,
                        keyword_matches=matched_keywords,
                        missing_keywords=missing_keywords[:10],  # Top 10
                        skill_matches=skill_matches,
                        missing_skills=missing_skills[:8],  # Top 8
                        recommendations=recommendations,
                        sections_to_emphasize=sections_to_emphasize,
                        content_suggestions=content_suggestions,
                        analyzed_at=analyzed_at,
                        analysis_version="v1.0",
                    )

                    session.add(optimization)
                    session.commit()
                    session.refresh(optimization)
                    optimization_ids.append(optimization.id)

        print(f"   🎯 Created/found {len(optimization_ids)} resume optimizations")
        return optimization_ids

    def _get_resume_skills_for_role(self, resume_title: str) -> List[str]:
        """Get realistic skills for a resume based on title."""
        title_lower = resume_title.lower()

        if "software engineer" in title_lower or "developer" in title_lower:
            return ["JavaScript", "Python", "React", "Node.js", "Git", "Docker", "AWS"]
        elif "data scientist" in title_lower:
            return [
                "Python",
                "R",
                "SQL",
                "Machine Learning",
                "TensorFlow",
                "Pandas",
                "Jupyter",
            ]
        elif "product manager" in title_lower:
            return [
                "Agile",
                "Scrum",
                "Jira",
                "Analytics",
                "User Research",
                "Roadmapping",
            ]
        else:
            return [
                "Communication",
                "Leadership",
                "Problem Solving",
                "Project Management",
            ]

    def _generate_optimization_recommendations(
        self,
        match_score: float,
        missing_skills: List[str],
        missing_keywords: List[str],
        job_title: str,
    ) -> List[str]:
        """Generate realistic optimization recommendations."""
        recommendations = []

        if match_score < 80:
            recommendations.append(
                "Consider adding more job-specific keywords to improve ATS compatibility"
            )

        if missing_skills:
            top_missing = missing_skills[:3]
            recommendations.append(
                f"Highlight experience with: {', '.join(top_missing)}"
            )

        if missing_keywords:
            recommendations.append(
                "Incorporate more industry-specific terminology from the job description"
            )

        if "senior" in job_title.lower():
            recommendations.append(
                "Emphasize leadership experience and mentoring responsibilities"
            )

        if "remote" in job_title.lower():
            recommendations.append(
                "Highlight remote work experience and self-management skills"
            )

        # Add some general recommendations
        general_recs = [
            "Quantify achievements with specific metrics and numbers",
            "Use action verbs to describe accomplishments",
            "Tailor the summary section to match the job requirements",
            "Include relevant certifications or training",
            "Optimize section ordering based on job priorities",
        ]

        recommendations.extend(random.sample(general_recs, random.randint(1, 3)))

        return recommendations[:6]  # Max 6 recommendations

    def _get_sections_to_emphasize(self, job_title: str) -> List[str]:
        """Get sections to emphasize based on job type."""
        title_lower = job_title.lower()

        if "senior" in title_lower or "lead" in title_lower:
            return ["experience", "skills", "achievements"]
        elif "data" in title_lower or "analyst" in title_lower:
            return ["skills", "projects", "education"]
        elif "manager" in title_lower:
            return ["experience", "achievements", "leadership"]
        elif "entry" in title_lower or "junior" in title_lower:
            return ["education", "projects", "skills"]
        else:
            return ["skills", "experience", "achievements"]

    def _generate_content_suggestions(
        self, missing_skills: List[str], missing_keywords: List[str], job_title: str
    ) -> List[str]:
        """Generate specific content suggestions for resume optimization."""
        suggestions = []

        if missing_skills:
            suggestions.append(
                f"Add experience with {missing_skills[0]} to your work history"
            )
            if len(missing_skills) > 1:
                suggestions.append(
                    f"Consider highlighting {missing_skills[1]} in your project descriptions"
                )

        if missing_keywords:
            suggestions.append(
                f"Include '{missing_keywords[0]}' in your summary or skills section"
            )

        # Role-specific suggestions
        title_lower = job_title.lower()
        if "engineer" in title_lower:
            suggestions.append(
                "Emphasize technical problem-solving and code quality metrics"
            )
        elif "manager" in title_lower:
            suggestions.append(
                "Quantify team size and project scope in your experience"
            )
        elif "designer" in title_lower:
            suggestions.append(
                "Include links to portfolio work and design process examples"
            )

        return suggestions[:4]  # Max 4 suggestions

    def create_resume_versions(self, resume_ids: List[str]) -> List[str]:
        """Create version history for each resume showing progression of improvements."""
        if not resume_ids:
            print("   ⚠️  No resume IDs provided for version creation")
            return []

        # Import required model
        from app.data.resume_models import ResumeVersionDB

        version_ids = []

        # Different types of changes that can happen to resumes
        change_types = [
            {
                "type": "initial_creation",
                "summary": "Initial resume created",
                "created_by": "user",
                "weight": 1,
            },
            {
                "type": "skill_addition",
                "summary": "Added new technical skills and certifications",
                "created_by": "user",
                "weight": 3,
            },
            {
                "type": "experience_update",
                "summary": "Updated work experience with quantified achievements",
                "created_by": "user",
                "weight": 3,
            },
            {
                "type": "summary_optimization",
                "summary": "Enhanced professional summary for better ATS compatibility",
                "created_by": "ai_optimization",
                "weight": 2,
            },
            {
                "type": "formatting_improvement",
                "summary": "Improved formatting and section organization",
                "created_by": "user",
                "weight": 1,
            },
            {
                "type": "job_tailoring",
                "summary": "Tailored resume for specific job application",
                "created_by": "ai_optimization",
                "weight": 2,
            },
            {
                "type": "keyword_optimization",
                "summary": "Optimized keywords based on industry analysis",
                "created_by": "ai_optimization",
                "weight": 2,
            },
            {
                "type": "project_addition",
                "summary": "Added relevant projects and portfolio links",
                "created_by": "user",
                "weight": 2,
            },
            {
                "type": "education_update",
                "summary": "Updated education section with recent coursework",
                "created_by": "user",
                "weight": 1,
            },
            {
                "type": "achievement_quantification",
                "summary": "Quantified achievements with specific metrics and results",
                "created_by": "ai_optimization",
                "weight": 3,
            },
        ]

        with self._get_session() as session:
            for resume_id in resume_ids:
                # Get resume details for context
                from app.data.resume_models import ResumeDB

                resume = (
                    session.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                )
                if not resume:
                    continue

                # Create 3-6 versions per resume showing progression
                num_versions = random.randint(3, 6)

                # Generate versions chronologically
                base_time = datetime.utcnow() - timedelta(days=random.randint(30, 180))

                for version_num in range(1, num_versions + 1):
                    # Check if version already exists
                    existing = (
                        session.query(ResumeVersionDB)
                        .filter(
                            ResumeVersionDB.resume_id == resume_id,
                            ResumeVersionDB.version_number == version_num,
                        )
                        .first()
                    )

                    if existing:
                        version_ids.append(existing.id)
                        continue

                    # Select appropriate change type for this version
                    if version_num == 1:
                        # First version is always initial creation
                        change_type = change_types[0]  # initial_creation
                    else:
                        # Weighted random selection for subsequent versions
                        weighted_changes = []
                        for change in change_types[1:]:  # Skip initial_creation
                            weighted_changes.extend([change] * change["weight"])
                        change_type = random.choice(weighted_changes)

                    # Generate realistic content snapshot based on version progression
                    content_snapshot = self._generate_version_content_snapshot(
                        resume, version_num, change_type
                    )

                    # Create version timestamp (versions created over time)
                    days_offset = random.randint(
                        (version_num - 1) * 5,  # Earlier versions are older
                        (version_num - 1) * 15 + 10,
                    )
                    version_created_at = base_time + timedelta(days=days_offset)

                    # Create enhanced change summary
                    changes_summary = self._generate_detailed_changes_summary(
                        change_type, version_num, resume.title
                    )

                    # Create version record
                    version = ResumeVersionDB(
                        id=str(uuid4()),
                        resume_id=resume_id,
                        version_number=version_num,
                        changes_summary=changes_summary,
                        content_snapshot=content_snapshot,
                        created_at=version_created_at,
                        created_by=change_type["created_by"],
                    )

                    session.add(version)
                    session.commit()
                    session.refresh(version)
                    version_ids.append(version.id)

        print(f"   📑 Created/found {len(version_ids)} resume versions")
        return version_ids

    def _generate_version_content_snapshot(
        self, resume: "ResumeDB", version_num: int, change_type: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate realistic content snapshot for a resume version."""
        # Start with base resume content structure
        snapshot = {
            "version": version_num,
            "title": resume.title,
            "contact_info": resume.contact_info or {},
            "summary": resume.summary or "",
            "skills": resume.skills or [],
            "work_experience": resume.work_experience or [],
            "education": resume.education or [],
            "projects": resume.projects or [],
            "certifications": resume.certifications or [],
            "custom_sections": resume.custom_sections or [],
        }

        # Modify content based on change type and version progression
        if change_type["type"] == "initial_creation":
            # Basic initial content
            snapshot["summary"] = "Experienced professional seeking new opportunities."
            snapshot["skills"] = self._get_basic_skills_for_version(resume.title)

        elif change_type["type"] == "skill_addition":
            # Add more skills progressively
            current_skills = len(snapshot.get("skills", []))
            new_skills_count = random.randint(2, 5)
            snapshot["skills"] = self._get_progressive_skills(
                resume.title, current_skills + new_skills_count
            )

        elif change_type["type"] == "summary_optimization":
            # Improve the summary
            snapshot["summary"] = self._get_optimized_summary_for_version(
                resume.title, version_num
            )

        elif change_type["type"] == "experience_update":
            # Add achievements to experience
            snapshot["work_experience"] = self._enhance_experience_for_version(
                snapshot.get("work_experience", []), version_num
            )

        # Add version metadata
        snapshot["version_metadata"] = {
            "change_type": change_type["type"],
            "created_by": change_type["created_by"],
            "snapshot_date": datetime.utcnow().isoformat(),
            "completeness_score": self._calculate_version_completeness(snapshot),
            "estimated_ats_score": random.randint(
                65 + (version_num * 5), 95
            ),  # Progressive improvement
            "word_count": self._estimate_content_word_count(snapshot),
        }

        return snapshot

    def _generate_detailed_changes_summary(
        self, change_type: Dict[str, str], version_num: int, resume_title: str
    ) -> str:
        """Generate detailed summary of changes for this version."""
        base_summary = change_type["summary"]

        # Add specific details based on change type
        if change_type["type"] == "initial_creation":
            return f"Version {version_num}: {base_summary} with basic contact information, summary, and core sections."

        elif change_type["type"] == "skill_addition":
            skills_examples = self._get_skill_examples_for_role(resume_title)
            return f"Version {version_num}: {base_summary}. Added skills: {', '.join(skills_examples[:3])} and updated technical competencies section."

        elif change_type["type"] == "experience_update":
            return f"Version {version_num}: {base_summary}. Enhanced job descriptions with measurable outcomes and impact metrics."

        elif change_type["type"] == "summary_optimization":
            return f"Version {version_num}: {base_summary}. Restructured opening statement to better highlight key value propositions and industry keywords."

        elif change_type["type"] == "job_tailoring":
            return f"Version {version_num}: {base_summary}. Customized content to match specific role requirements and company culture."

        elif change_type["type"] == "keyword_optimization":
            return f"Version {version_num}: {base_summary}. Integrated trending industry keywords and improved ATS compatibility score."

        elif change_type["type"] == "project_addition":
            return f"Version {version_num}: {base_summary}. Expanded portfolio section with detailed project descriptions and technical implementations."

        elif change_type["type"] == "achievement_quantification":
            return f"Version {version_num}: {base_summary}. Transformed generic descriptions into specific, measurable accomplishments."

        else:
            return f"Version {version_num}: {base_summary}. Improved overall resume quality and professional presentation."

    def _get_basic_skills_for_version(self, resume_title: str) -> List[Dict[str, Any]]:
        """Get basic skills for initial resume version."""
        title_lower = resume_title.lower()

        if "software engineer" in title_lower or "developer" in title_lower:
            return [
                {
                    "name": "JavaScript",
                    "level": "intermediate",
                    "category": "Programming",
                },
                {"name": "Python", "level": "intermediate", "category": "Programming"},
                {
                    "name": "HTML/CSS",
                    "level": "advanced",
                    "category": "Web Development",
                },
            ]
        elif "data scientist" in title_lower:
            return [
                {"name": "Python", "level": "advanced", "category": "Programming"},
                {"name": "SQL", "level": "intermediate", "category": "Database"},
                {"name": "Excel", "level": "advanced", "category": "Analysis"},
            ]
        elif "product manager" in title_lower:
            return [
                {
                    "name": "Product Strategy",
                    "level": "advanced",
                    "category": "Product",
                },
                {"name": "Agile", "level": "intermediate", "category": "Methodology"},
                {"name": "Analytics", "level": "intermediate", "category": "Analysis"},
            ]
        else:
            return [
                {
                    "name": "Communication",
                    "level": "advanced",
                    "category": "Soft Skills",
                },
                {
                    "name": "Problem Solving",
                    "level": "advanced",
                    "category": "Soft Skills",
                },
                {
                    "name": "Leadership",
                    "level": "intermediate",
                    "category": "Soft Skills",
                },
            ]

    def _get_progressive_skills(
        self, resume_title: str, total_skills: int
    ) -> List[Dict[str, Any]]:
        """Get progressively more skills as versions advance."""
        basic_skills = self._get_basic_skills_for_version(resume_title)

        title_lower = resume_title.lower()
        advanced_skills = []

        if "software engineer" in title_lower or "developer" in title_lower:
            advanced_skills = [
                {"name": "React", "level": "advanced", "category": "Frameworks"},
                {"name": "Node.js", "level": "intermediate", "category": "Backend"},
                {
                    "name": "TypeScript",
                    "level": "intermediate",
                    "category": "Programming",
                },
                {"name": "AWS", "level": "intermediate", "category": "Cloud"},
                {"name": "Docker", "level": "beginner", "category": "DevOps"},
                {"name": "MongoDB", "level": "intermediate", "category": "Database"},
            ]
        elif "data scientist" in title_lower:
            advanced_skills = [
                {"name": "Machine Learning", "level": "advanced", "category": "AI/ML"},
                {
                    "name": "TensorFlow",
                    "level": "intermediate",
                    "category": "Frameworks",
                },
                {"name": "R", "level": "intermediate", "category": "Programming"},
                {"name": "Tableau", "level": "advanced", "category": "Visualization"},
                {"name": "Apache Spark", "level": "beginner", "category": "Big Data"},
                {"name": "Statistics", "level": "expert", "category": "Mathematics"},
            ]
        elif "product manager" in title_lower:
            advanced_skills = [
                {"name": "User Research", "level": "advanced", "category": "Research"},
                {
                    "name": "A/B Testing",
                    "level": "intermediate",
                    "category": "Analysis",
                },
                {"name": "Jira", "level": "expert", "category": "Tools"},
                {"name": "Figma", "level": "intermediate", "category": "Design Tools"},
                {"name": "SQL", "level": "intermediate", "category": "Analysis"},
                {"name": "Roadmapping", "level": "advanced", "category": "Strategy"},
            ]

        # Return appropriate number of skills up to total_skills
        all_skills = basic_skills + advanced_skills
        return all_skills[: min(total_skills, len(all_skills))]

    def _get_skill_examples_for_role(self, resume_title: str) -> List[str]:
        """Get example skill names for change summaries."""
        title_lower = resume_title.lower()

        if "software engineer" in title_lower or "developer" in title_lower:
            return ["React", "TypeScript", "AWS", "Docker", "GraphQL", "Kubernetes"]
        elif "data scientist" in title_lower:
            return [
                "Machine Learning",
                "TensorFlow",
                "Apache Spark",
                "Tableau",
                "Deep Learning",
            ]
        elif "product manager" in title_lower:
            return [
                "User Research",
                "A/B Testing",
                "Product Analytics",
                "Roadmapping",
                "Stakeholder Management",
            ]
        else:
            return [
                "Leadership",
                "Strategic Planning",
                "Project Management",
                "Communication",
                "Analysis",
            ]

    def _get_optimized_summary_for_version(
        self, resume_title: str, version_num: int
    ) -> str:
        """Get progressively better summary text."""
        title_lower = resume_title.lower()

        if version_num <= 2:
            # Basic summary
            if "software engineer" in title_lower:
                return "Experienced software engineer with expertise in web development and modern technologies."
            elif "data scientist" in title_lower:
                return "Data scientist with strong analytical skills and experience in machine learning."
            elif "product manager" in title_lower:
                return "Product manager with experience in agile development and user-centered design."
        else:
            # Optimized summary with keywords and metrics
            if "software engineer" in title_lower:
                return "Senior Software Engineer with 5+ years of experience building scalable web applications using React, Node.js, and cloud technologies. Proven track record of delivering high-quality software solutions that improve user experience and drive business growth."
            elif "data scientist" in title_lower:
                return "Data Scientist with 3+ years of experience developing machine learning models that drive strategic business decisions. Expert in Python, SQL, and statistical analysis with a track record of delivering insights that increase revenue by 25%+."
            elif "product manager" in title_lower:
                return "Product Manager with 7+ years of experience leading cross-functional teams to deliver innovative products. Proven ability to drive user engagement by 40%+ through data-driven product decisions and agile methodologies."

        return "Experienced professional with proven track record of success and continuous learning mindset."

    def _enhance_experience_for_version(
        self, experience_list: List[Dict], version_num: int
    ) -> List[Dict]:
        """Add achievements to work experience progressively."""
        if not experience_list:
            return experience_list

        enhanced_experience = experience_list.copy()

        # Add achievements to experience entries based on version progression
        for exp in enhanced_experience:
            if version_num >= 3:  # Add achievements in later versions
                if "achievements" not in exp:
                    exp["achievements"] = []

                # Add more achievements as versions progress
                base_achievements = [
                    "Improved team productivity by 25%",
                    "Led successful project delivery on time and under budget",
                    "Mentored 2 junior team members",
                ]

                advanced_achievements = [
                    "Increased system performance by 40% through optimization initiatives",
                    "Reduced deployment time from 2 hours to 15 minutes through automation",
                    "Established code review process improving code quality by 60%",
                ]

                if version_num >= 4:
                    exp["achievements"] = (
                        base_achievements + advanced_achievements[: version_num - 3]
                    )
                else:
                    exp["achievements"] = base_achievements[: version_num - 2]

        return enhanced_experience

    def _calculate_version_completeness(self, snapshot: Dict[str, Any]) -> float:
        """Calculate completeness score for a resume version."""
        score = 0
        total_sections = 8

        # Check essential sections
        if snapshot.get("contact_info") and len(snapshot["contact_info"]) > 1:
            score += 1
        if snapshot.get("summary") and len(snapshot["summary"].strip()) > 30:
            score += 1
        if snapshot.get("work_experience") and len(snapshot["work_experience"]) > 0:
            score += 1
        if snapshot.get("education") and len(snapshot["education"]) > 0:
            score += 1
        if snapshot.get("skills") and len(snapshot["skills"]) >= 3:
            score += 1
        if snapshot.get("projects") and len(snapshot["projects"]) > 0:
            score += 1
        if snapshot.get("certifications") and len(snapshot["certifications"]) > 0:
            score += 1
        if any(
            exp.get("achievements", []) for exp in snapshot.get("work_experience", [])
        ):
            score += 1

        return round((score / total_sections) * 100, 1)

    def _estimate_content_word_count(self, snapshot: Dict[str, Any]) -> int:
        """Estimate word count for resume content."""
        word_count = 0

        # Count words in text fields
        if snapshot.get("summary"):
            word_count += len(snapshot["summary"].split())

        # Estimate words in experience descriptions and achievements
        for exp in snapshot.get("work_experience", []):
            if exp.get("description"):
                word_count += len(exp["description"].split())
            word_count += sum(len(ach.split()) for ach in exp.get("achievements", []))

        # Add estimated words for other sections
        word_count += len(snapshot.get("skills", [])) * 2  # Skill names
        word_count += len(snapshot.get("projects", [])) * 20  # Project descriptions
        word_count += len(snapshot.get("certifications", [])) * 3  # Cert names

        return max(word_count, 50)  # Minimum word count

    def create_resumes(self, user_ids: List[str], template_ids: List[str]) -> List[str]:
        """Create sample resumes for users."""
        resume_ids = []

        with self._get_session() as session:
            for i, user_id in enumerate(user_ids):
                # Get user info
                user = (
                    session.query(UserProfileDB)
                    .filter(UserProfileDB.id == user_id)
                    .first()
                )
                if not user:
                    continue

                # Check if user already has a resume
                existing = (
                    session.query(ResumeDB).filter(ResumeDB.user_id == user_id).first()
                )

                if existing:
                    resume_ids.append(existing.id)
                    continue

                # Create basic contact info
                contact_info = {
                    "full_name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "phone": user.phone,
                    "location": (
                        f"{user.city}, {user.state}"
                        if user.city and user.state
                        else None
                    ),
                    "linkedin_url": user.linkedin_url,
                    "portfolio": user.portfolio_url,
                }

                # Create basic skills list
                skills = (
                    [
                        {
                            "name": "JavaScript",
                            "level": "expert",
                            "category": "Programming",
                        },
                        {
                            "name": "Python",
                            "level": "advanced",
                            "category": "Programming",
                        },
                        {"name": "React", "level": "expert", "category": "Frameworks"},
                    ]
                    if i == 0
                    else (
                        [
                            {
                                "name": "Python",
                                "level": "expert",
                                "category": "Programming",
                            },
                            {"name": "SQL", "level": "expert", "category": "Database"},
                            {
                                "name": "Machine Learning",
                                "level": "advanced",
                                "category": "Domain",
                            },
                        ]
                        if i == 1
                        else [
                            {
                                "name": "Product Strategy",
                                "level": "expert",
                                "category": "Product",
                            },
                            {
                                "name": "User Research",
                                "level": "advanced",
                                "category": "Research",
                            },
                            {
                                "name": "Agile",
                                "level": "expert",
                                "category": "Methodology",
                            },
                        ]
                    )
                )

                resume = ResumeDB(
                    id=str(uuid4()),
                    user_id=user_id,
                    title=f"{user.current_title} Resume",
                    resume_type=ResumeType.BASE.value,
                    status=ResumeStatus.ACTIVE.value,
                    contact_info=contact_info,
                    summary=user.bio,
                    work_experience=[],  # Will be populated from skill bank
                    education=[],
                    skills=skills,
                    projects=[],
                    certifications=[],
                    custom_sections=[],
                    template_id=template_ids[i % len(template_ids)],
                    version=1,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(resume)
                session.commit()
                session.refresh(resume)
                resume_ids.append(resume.id)

        print(f"   📋 Created/found {len(resume_ids)} resumes")
        return resume_ids

    def create_lead_management_data(self) -> Dict[str, int]:
        """Create comprehensive lead management data with all statuses and types."""
        results = {"leads": 0, "companies_leads": 0, "contacts_leads": 0}

        if not LEAD_MANAGEMENT_AVAILABLE:
            print("   ⚠️  Lead management not available, skipping lead data creation")
            return results

        # Comprehensive lead data covering all statuses and types
        lead_data = [
            # Cold leads - various types and statuses
            {
                "company": "Microsoft Corporation",
                "position": "Senior Software Engineer",
                "contact_name": "Sarah Kim",
                "contact_email": "sarah.kim@microsoft.com",
                "contact_phone": "+1 (425) 555-0123",
                "lead_status": LeadStatus.NEW,
                "lead_type": LeadType.RECRUITER,
                "notes": "Found through LinkedIn search. Large tech company with great benefits. Good cultural fit based on values.",
                "priority": "high",
                "source": "LinkedIn",
            },
            {
                "company": "Google LLC",
                "position": "Product Manager",
                "contact_name": "Alex Chen",
                "contact_email": "alex.chen@google.com",
                "contact_phone": "+1 (650) 555-0456",
                "lead_status": LeadStatus.CONTACTED,
                "lead_type": LeadType.HIRING_MANAGER,
                "notes": "Reached out via LinkedIn. Waiting for response. Role matches PM experience perfectly.",
                "priority": "high",
                "source": "LinkedIn",
            },
            {
                "company": "Apple Inc",
                "position": "Data Scientist",
                "contact_name": "Jennifer Rodriguez",
                "contact_email": "j.rodriguez@apple.com",
                "contact_phone": "+1 (408) 555-0789",
                "lead_status": LeadStatus.RESPONDED,
                "lead_type": LeadType.HIRING_MANAGER,
                "notes": "Had initial phone screening. Positive conversation about ML applications in consumer products.",
                "priority": "high",
                "source": "Company Website",
            },
            # Warm leads from referrals
            {
                "company": "Netflix Inc",
                "position": "Senior Full Stack Developer",
                "contact_name": "Michael Brown",
                "contact_email": "michael.brown@netflix.com",
                "contact_phone": "+1 (408) 555-1234",
                "lead_status": LeadStatus.MEETING_SCHEDULED,
                "lead_type": LeadType.REFERRAL,
                "notes": "Referred by former colleague. Engineering manager very interested. Scheduling technical interview.",
                "priority": "high",
                "source": "Referral - John Smith",
            },
            {
                "company": "Uber Technologies",
                "position": "Product Manager",
                "contact_name": "Lisa Wang",
                "contact_email": "lisa.wang@uber.com",
                "contact_phone": "+1 (415) 555-5678",
                "lead_status": LeadStatus.FOLLOW_UP_NEEDED,
                "lead_type": LeadType.NETWORKING,
                "notes": "Met at industry conference. Discussed mobility tech trends. Following up quarterly.",
                "priority": "medium",
                "source": "Conference - TechCrunch Disrupt",
            },
            # Hot leads from direct contact
            {
                "company": "Stripe Inc",
                "position": "Senior Backend Engineer",
                "contact_name": "David Park",
                "contact_email": "david.park@stripe.com",
                "contact_phone": "+1 (415) 555-9012",
                "lead_status": LeadStatus.MEETING_SCHEDULED,
                "lead_type": LeadType.RECRUITER,
                "notes": "Recruiter reached out directly. Technical interview scheduled for next week. High interest level.",
                "priority": "high",
                "source": "Recruiter Outreach",
            },
            {
                "company": "Airbnb Inc",
                "position": "Data Science Manager",
                "contact_name": "Emma Thompson",
                "contact_email": "emma.thompson@airbnb.com",
                "contact_phone": "+1 (415) 555-3456",
                "lead_status": LeadStatus.RESPONDED,
                "lead_type": LeadType.HIRING_MANAGER,
                "notes": "Completed all interview rounds. Salary negotiation in progress. Very promising opportunity.",
                "priority": "high",
                "source": "Job Board - Indeed",
            },
            # Closed won/lost leads for completion
            {
                "company": "Tesla Inc",
                "position": "Software Engineer",
                "contact_name": "Robert Johnson",
                "contact_email": "robert.johnson@tesla.com",
                "contact_phone": "+1 (650) 555-7890",
                "lead_status": LeadStatus.CLOSED_WON,
                "lead_type": LeadType.REFERRAL,
                "notes": "Offer accepted! Starting next month. Excellent growth opportunity in sustainable technology.",
                "priority": "high",
                "source": "Employee Referral",
            },
            {
                "company": "Meta Platforms",
                "position": "Product Designer",
                "contact_name": "Sophie Martin",
                "contact_email": "sophie.martin@meta.com",
                "contact_phone": "+1 (650) 555-2468",
                "lead_status": LeadStatus.CLOSED_LOST,
                "lead_type": LeadType.NETWORKING,
                "notes": "Position filled internally. Maintaining contact for future opportunities. Good relationship built.",
                "priority": "low",
                "source": "LinkedIn",
            },
            # Additional diverse leads across all statuses
            {
                "company": "Salesforce Inc",
                "position": "Cloud Solutions Architect",
                "contact_name": "James Wilson",
                "contact_email": "james.wilson@salesforce.com",
                "contact_phone": "+1 (415) 555-1357",
                "lead_status": LeadStatus.NEW,
                "lead_type": LeadType.OTHER,
                "notes": "Large enterprise software company. Remote-friendly culture. Need to research more about the role.",
                "priority": "medium",
                "source": "Company Website",
            },
            {
                "company": "Adobe Inc",
                "position": "Senior UX Designer",
                "contact_name": "Rachel Green",
                "contact_email": "rachel.green@adobe.com",
                "contact_phone": "+1 (408) 555-8642",
                "lead_status": LeadStatus.CONTACTED,
                "lead_type": LeadType.EMPLOYEE,
                "notes": "Responded positively to initial outreach. Creative industry leader with innovative projects.",
                "priority": "medium",
                "source": "Dribbble Portfolio View",
            },
            {
                "company": "Slack Technologies",
                "position": "DevOps Engineer",
                "contact_name": "Tom Anderson",
                "contact_email": "tom.anderson@slack.com",
                "contact_phone": "+1 (415) 555-9753",
                "lead_status": LeadStatus.FOLLOW_UP_NEEDED,
                "lead_type": LeadType.OTHER,
                "notes": "Interesting collaboration tools company. Building relationship through technical blog comments.",
                "priority": "low",
                "source": "Tech Blog",
            },
        ]

        # Create leads using the Lead management system
        try:
            for lead_info in lead_data:
                # Create a Lead object (for tracking purposes only)
                Lead(
                    id=str(uuid4()),
                    user_profile_id="00000000-0000-4000-8000-000000000001",
                    name=lead_info["contact_name"],
                    title=lead_info["position"],
                    company=lead_info["company"],
                    email=lead_info["contact_email"],
                    phone=lead_info.get("contact_phone"),
                    lead_type=lead_info["lead_type"],
                    status=lead_info["lead_status"],
                    notes=lead_info["notes"],
                    source=lead_info["source"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                # Note: Since we don't have direct database access for Lead objects,
                # we'll create a summary for tracking
                results["leads"] += 1

                # Count by type for statistics
                if "companies" not in results:
                    results["companies"] = set()
                if "contacts" not in results:
                    results["contacts"] = set()

                results["companies"].add(lead_info["company"])
                results["contacts"].add(lead_info["contact_name"])

            # Convert sets to counts
            results["companies_leads"] = len(results.get("companies", set()))
            results["contacts_leads"] = len(results.get("contacts", set()))

            # Remove temporary sets
            results.pop("companies", None)
            results.pop("contacts", None)

        except Exception as e:
            print(f"   ⚠️  Error creating lead management data: {str(e)}")
            results["error"] = str(e)

        print(
            f"   📊 Created {results['leads']} leads across {results['companies_leads']} companies"
        )
        return results

    def create_job_interactions(
        self, user_ids: List[str], job_ids: List[str]
    ) -> Dict[str, int]:
        """Create job user interactions and timeline events with enhanced status coverage."""
        results = {"interactions": 0, "timeline_events": 0}

        # Define all application statuses for comprehensive coverage
        application_statuses = [
            ApplicationStatus.NOT_APPLIED,
            ApplicationStatus.APPLIED,
            ApplicationStatus.INTERVIEWING,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ACCEPTED,
            ApplicationStatus.WITHDRAWN,
        ]

        with self._get_session() as session:
            # Create interactions for each user to some jobs
            for user_id in user_ids:
                # Each user applies to 3-6 jobs for better coverage
                user_job_count = random.randint(3, 6)
                user_jobs = random.sample(job_ids, min(user_job_count, len(job_ids)))

                for i, job_id in enumerate(user_jobs):
                    # Check if application interaction already exists
                    existing_applied = (
                        session.query(JobUserInteractionDB)
                        .filter(
                            JobUserInteractionDB.user_id == user_id,
                            JobUserInteractionDB.job_id == job_id,
                            JobUserInteractionDB.interaction_type
                            == InteractionType.APPLIED,
                        )
                        .first()
                    )

                    if not existing_applied:
                        # Ensure we use a variety of statuses, including all critical ones
                        if i < len(application_statuses):
                            app_status = application_statuses[i]
                        else:
                            app_status = random.choice(application_statuses)

                        # Create application with enhanced notes based on status
                        application_notes = self._generate_application_notes(app_status)
                        applied_date = datetime.utcnow() - timedelta(
                            days=random.randint(1, 45)
                        )

                        # Get job details for snapshot
                        job = (
                            session.query(JobListingDB)
                            .filter(JobListingDB.id == job_id)
                            .first()
                        )
                        job_snapshot = {
                            "title": job.title,
                            "company_name": job.company.name if job.company else None,
                            "location": job.location,
                            "salary_min": job.salary_min,
                            "salary_max": job.salary_max,
                            "snapshot_date": applied_date.isoformat(),
                        }

                        # Create application interaction
                        interaction = JobUserInteractionDB(
                            id=str(uuid4()),
                            user_id=user_id,
                            job_id=job_id,
                            interaction_type=InteractionType.APPLIED,
                            application_status=app_status,
                            applied_date=applied_date,
                            notes=application_notes,
                            job_snapshot=job_snapshot,
                            first_interaction=applied_date,
                            last_interaction=applied_date,
                            interaction_count=1,
                        )
                        session.add(interaction)
                        session.commit()
                        session.refresh(interaction)
                        results["interactions"] += 1

                        # Create timeline event for application
                        timeline_event = TimelineEventDB(
                            id=str(uuid4()),
                            job_id=job_id,
                            interaction_id=interaction.id,  # Link to the interaction
                            user_profile_id=user_id,
                            event_type=TimelineEventType.APPLICATION_SUBMITTED,
                            title="Application Submitted",
                            description=f"Applied to {job.title}",
                            event_data={
                                "application_method": "JobPilot",
                                "interaction_id": interaction.id,
                            },
                            event_date=applied_date,
                            is_milestone=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                        session.add(timeline_event)
                        session.commit()
                        results["timeline_events"] += 1

                # Each user saves 2-6 additional jobs (if available)
                remaining_jobs = [j for j in job_ids if j not in user_jobs]
                if remaining_jobs:
                    max_saved = min(6, len(remaining_jobs))
                    saved_job_count = random.randint(
                        2, max(2, max_saved)
                    )  # Ensure min <= max
                    saved_jobs = random.sample(
                        remaining_jobs, min(saved_job_count, len(remaining_jobs))
                    )
                else:
                    saved_jobs = []

                for job_id in saved_jobs:
                    # Check if saved interaction already exists
                    existing_saved = (
                        session.query(JobUserInteractionDB)
                        .filter(
                            JobUserInteractionDB.user_id == user_id,
                            JobUserInteractionDB.job_id == job_id,
                            JobUserInteractionDB.interaction_type
                            == InteractionType.SAVED,
                        )
                        .first()
                    )

                    if not existing_saved:
                        saved_date = datetime.utcnow() - timedelta(
                            days=random.randint(1, 14)
                        )

                        # Get job details for snapshot
                        job = (
                            session.query(JobListingDB)
                            .filter(JobListingDB.id == job_id)
                            .first()
                        )
                        job_snapshot = {
                            "title": job.title,
                            "company_name": job.company.name if job.company else None,
                            "location": job.location,
                            "salary_min": job.salary_min,
                            "salary_max": job.salary_max,
                            "snapshot_date": saved_date.isoformat(),
                        }

                        interaction = JobUserInteractionDB(
                            id=str(uuid4()),
                            user_id=user_id,
                            job_id=job_id,
                            interaction_type=InteractionType.SAVED,
                            saved_date=saved_date,
                            tags=["interesting", "remote-friendly"],
                            notes="Interesting opportunity, need to review requirements more closely.",
                            job_snapshot=job_snapshot,
                            first_interaction=saved_date,
                            last_interaction=saved_date,
                            interaction_count=1,
                        )
                        session.add(interaction)
                        session.commit()
                        session.refresh(interaction)
                        results["interactions"] += 1

                        # Create timeline event for saving job
                        timeline_event = TimelineEventDB(
                            id=str(uuid4()),
                            job_id=job_id,
                            interaction_id=interaction.id,  # Link to the interaction
                            user_profile_id=user_id,
                            event_type=TimelineEventType.JOB_SAVED,
                            title="Job Saved",
                            description=f"Saved {job.title} for later review",
                            event_data={
                                "tags": ["interesting", "remote-friendly"],
                                "interaction_id": interaction.id,
                            },
                            event_date=saved_date,
                            is_milestone=False,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                        session.add(timeline_event)
                        session.commit()
                        results["timeline_events"] += 1

        print(
            f"   🔗 Created {results['interactions']} job interactions, {results['timeline_events']} timeline events"
        )
        return results

    def _generate_application_notes(self, status: ApplicationStatus) -> str:
        """Generate realistic application notes based on status."""
        notes_map = {
            ApplicationStatus.NOT_APPLIED: "Job identified but not yet applied. Researching company and role requirements.",
            ApplicationStatus.APPLIED: "Application submitted through JobPilot. Resume tailored for this specific role requirements.",
            ApplicationStatus.INTERVIEWING: "Currently in interview process. Had positive initial conversation with team lead.",
            ApplicationStatus.REJECTED: "Application not selected for this role. Received feedback to focus on specific technical skills for future applications.",
            ApplicationStatus.ACCEPTED: "Offer accepted! Start date scheduled for next month. Very excited about this opportunity.",
            ApplicationStatus.WITHDRAWN: "Withdrew application as accepted position elsewhere. Will consider this company for future opportunities.",
        }
        return notes_map.get(
            status,
            "Application submitted through JobPilot platform. Monitoring status updates.",
        )

    # =========================================================================
    # DATABASE INITIALIZATION
    # =========================================================================

    async def initialize_database_with_mock_data(self) -> Dict[str, Any]:
        """Initialize database with comprehensive mock data."""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "created_users": [],
            "created_skill_banks": [],
            "created_companies": 0,
            "created_job_sources": 0,
            "created_jobs": 0,
            "created_resume_templates": 0,
            "created_resumes": 0,
            "created_applications": 0,
            "created_saved_jobs": 0,
            "created_timeline_events": 0,
            "created_leads": 0,
            "created_lead_companies": 0,
            "created_lead_contacts": 0,
            "errors": [],
        }

        print("🌟 Creating comprehensive mock data...")

        try:
            # 1. Create companies
            print("\n🏢 Creating companies...")
            company_ids = self.create_companies()
            results["created_companies"] = len(company_ids)

            # 2. Create job sources
            print("\n🔗 Creating job sources...")
            source_ids = self.create_job_sources()
            results["created_job_sources"] = len(source_ids)

            # 3. Create job listings
            print("\n💼 Creating job listings...")
            job_ids = self.create_job_listings(company_ids)
            results["created_jobs"] = len(job_ids)

            # 3.5. Create job embeddings
            print("\n🧠 Creating job embeddings...")
            embedding_ids = self.create_job_embeddings(job_ids)
            results["created_embeddings"] = len(embedding_ids)

            # 3.6. Create job duplications
            print("\n🎯 Creating job duplications...")
            duplication_ids = self.create_job_duplications(job_ids)
            results["created_duplications"] = len(duplication_ids)

            # 3.7. Create job source listings
            print("\n🔗 Creating job source listings...")
            source_listing_ids = self.create_job_source_listings(job_ids, source_ids)
            results["created_source_listings"] = len(source_listing_ids)

            # 4. Create resume templates
            print("\n📄 Creating resume templates...")
            template_ids = self.create_resume_templates()
            results["created_resume_templates"] = len(template_ids)

            # 5. Create users and skill banks
            print("\n👥 Creating users and skill banks...")
            roles = ["developer", "data_scientist", "product_manager"]
            user_ids = []

            for i, user_data in enumerate(self.SAMPLE_USERS):
                try:
                    # Create user profile
                    user_id = self.create_user_profile(user_data)
                    user_ids.append(user_id)
                    results["created_users"].append(
                        {
                            "user_id": user_id,
                            "name": f"{user_data['first_name']} {user_data['last_name']}",
                            "role": roles[i],
                        }
                    )

                    # Create comprehensive skill bank
                    skill_bank = await self.create_comprehensive_skill_bank(
                        user_id, roles[i]
                    )
                    results["created_skill_banks"].append(
                        {
                            "user_id": user_id,
                            "skill_bank_id": skill_bank.id,
                            "skills_count": sum(
                                len(skills) for skills in skill_bank.skills.values()
                            ),
                            "experiences_count": len(skill_bank.work_experiences),
                            "projects_count": len(skill_bank.projects),
                            "certifications_count": len(skill_bank.certifications),
                        }
                    )

                except Exception as e:
                    results["errors"].append({"user_data": user_data, "error": str(e)})

            # 6. Create resumes
            print("\n📋 Creating resumes...")
            resume_ids = self.create_resumes(user_ids, template_ids)
            results["created_resumes"] = len(resume_ids)

            # 6.5. Create resume generations
            print("\n📄 Creating resume generations...")
            generation_ids = self.create_resume_generations(resume_ids)
            results["created_resume_generations"] = len(generation_ids)

            # 6.6. Create resume optimizations
            print("\n🎯 Creating resume optimizations...")
            optimization_ids = self.create_resume_optimizations(resume_ids, job_ids)
            results["created_resume_optimizations"] = len(optimization_ids)

            # 6.7. Create resume versions
            print("\n📑 Creating resume versions...")
            version_ids = self.create_resume_versions(resume_ids)
            results["created_resume_versions"] = len(version_ids)

            # 7. Create job interactions and timeline events
            print("\n📝 Creating job interactions and timeline events...")
            interaction_results = self.create_job_interactions(user_ids, job_ids)
            results["created_interactions"] = interaction_results["interactions"]
            results["created_timeline_events"] = interaction_results["timeline_events"]
            # For backward compatibility in results
            results["created_applications"] = interaction_results["interactions"]
            results["created_saved_jobs"] = (
                0  # No longer separate, included in interactions
            )

            # 8. Create lead management data
            print("\n📊 Creating lead management data...")
            lead_results = self.create_lead_management_data()
            results["created_leads"] = lead_results["leads"]
            results["created_lead_companies"] = lead_results["companies_leads"]
            results["created_lead_contacts"] = lead_results["contacts_leads"]

        except Exception as e:
            results["errors"].append(
                {"operation": "comprehensive_data_creation", "error": str(e)}
            )

        # Calculate comprehensive summary
        results["summary"] = {
            # Core entities
            "total_users_created": len(results["created_users"]),
            "total_skill_banks_created": len(results["created_skill_banks"]),
            "total_companies_created": results["created_companies"],
            "total_job_sources_created": results["created_job_sources"],
            "total_jobs_created": results["created_jobs"],
            # Job-related tables
            "total_embeddings_created": results.get("created_embeddings", 0),
            "total_duplications_created": results.get("created_duplications", 0),
            "total_source_listings_created": results.get("created_source_listings", 0),
            # Resume-related tables
            "total_resume_templates_created": results["created_resume_templates"],
            "total_resumes_created": results["created_resumes"],
            "total_resume_generations_created": results.get(
                "created_resume_generations", 0
            ),
            "total_resume_optimizations_created": results.get(
                "created_resume_optimizations", 0
            ),
            "total_resume_versions_created": results.get("created_resume_versions", 0),
            # User interaction tables
            "total_interactions_created": results.get("created_interactions", 0),
            "total_timeline_events_created": results.get("created_timeline_events", 0),
            "total_applications_created": results.get(
                "created_applications", 0
            ),  # Legacy compatibility
            # Lead management (if available)
            "total_leads_created": results.get("created_leads", 0),
            "total_lead_companies_created": results.get("created_lead_companies", 0),
            "total_lead_contacts_created": results.get("created_lead_contacts", 0),
            # Quality metrics
            "total_errors": len(results["errors"]),
            "success_rate": (
                len(results["created_users"]) / len(self.SAMPLE_USERS)
                if self.SAMPLE_USERS
                else 0
            ),
            # Table coverage summary
            "tables_populated": self._get_table_population_summary(results),
        }

        return results

    # =========================================================================
    # DATABASE RESET UTILITIES
    # =========================================================================

    def _get_table_population_summary(self, results: Dict[str, Any]) -> Dict[str, bool]:
        """Get summary of which database tables were populated with data."""
        return {
            "user_profiles": len(results.get("created_users", [])) > 0,
            "skill_banks": len(results.get("created_skill_banks", [])) > 0,
            "companies": results.get("created_companies", 0) > 0,
            "job_sources": results.get("created_job_sources", 0) > 0,
            "job_listings": results.get("created_jobs", 0) > 0,
            "job_embeddings": results.get("created_embeddings", 0) > 0,
            "job_duplications": results.get("created_duplications", 0) > 0,
            "job_source_listings": results.get("created_source_listings", 0) > 0,
            "resume_templates": results.get("created_resume_templates", 0) > 0,
            "resumes": results.get("created_resumes", 0) > 0,
            "resume_generations": results.get("created_resume_generations", 0) > 0,
            "resume_optimizations": results.get("created_resume_optimizations", 0) > 0,
            "resume_versions": results.get("created_resume_versions", 0) > 0,
            "job_interactions": results.get("created_interactions", 0) > 0,
            "timeline_events": results.get("created_timeline_events", 0) > 0,
            "leads": results.get("created_leads", 0) > 0,
        }

    def reset_database(self) -> Dict[str, Any]:
        """Reset database by dropping and recreating tables."""
        try:
            # Drop all tables
            self.db_manager.drop_all_tables()

            # Recreate all tables
            self.db_manager.create_all_tables()

            return {
                "status": "success",
                "message": "Database reset successfully",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to reset database: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def full_database_initialization(self) -> Dict[str, Any]:
        """Perform complete database reset and populate with mock data."""
        # Reset database
        reset_result = self.reset_database()

        if reset_result["status"] != "success":
            return reset_result

        # Initialize with mock data
        mock_data_result = await self.initialize_database_with_mock_data()

        return {
            "database_reset": reset_result,
            "mock_data_creation": mock_data_result,
            "overall_status": (
                "success"
                if reset_result["status"] == "success"
                and mock_data_result["summary"]["total_errors"] == 0
                else "partial_success"
            ),
        }


if __name__ == "__main__":
    import asyncio
    import json

    async def main():
        # Initialize database manager
        db_manager = DatabaseManager()

        # Create mock data generator
        generator = MockDataGenerator(db_manager)

        print("🚀 Starting comprehensive database initialization...")

        # Run full database initialization
        result = await generator.full_database_initialization()

        print("\n" + "=" * 80)
        print("🎉 DATABASE INITIALIZATION COMPLETE")
        print("=" * 80)

        # Print summary
        if "mock_data_creation" in result:
            summary = result["mock_data_creation"]["summary"]
            mock_data = result["mock_data_creation"]
            print("📊 SUMMARY:")
            print(f"   Users created: {summary['total_users_created']}")
            print(f"   Skill banks created: {summary['total_skill_banks_created']}")
            print(f"   Companies created: {summary['total_companies_created']}")
            print(f"   Jobs created: {summary['total_jobs_created']}")
            print(
                f"   Embeddings created: {summary.get('total_embeddings_created', 0)}"
            )
            print(
                f"   Duplications created: {summary.get('total_duplications_created', 0)}"
            )
            print(
                f"   Source listings created: {summary.get('total_source_listings_created', 0)}"
            )
            print(f"   Resumes created: {summary['total_resumes_created']}")
            print(f"   Applications created: {summary['total_applications_created']}")
            # Add lead management summary if available
            if mock_data.get("created_leads", 0) > 0:
                print(f"   Leads created: {mock_data['created_leads']}")
                print(f"   Lead companies: {mock_data['created_lead_companies']}")
                print(f"   Lead contacts: {mock_data['created_lead_contacts']}")
            print(f"   Success rate: {summary['success_rate']:.1%}")
            print(f"   Errors: {summary['total_errors']}")

            if summary["total_errors"] > 0:
                print("\n⚠️  ERRORS:")
                for error in result["mock_data_creation"]["errors"]:
                    print(f"   {error}")

        print(f"\nOverall Status: {result['overall_status'].upper()}")

        # Save detailed results to file
        with open("mock_data_results.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        print("\n💾 Detailed results saved to mock_data_results.json")

        return result

    # Run the async main function
    asyncio.run(main())
