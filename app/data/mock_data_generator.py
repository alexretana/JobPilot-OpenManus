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
from app.data.models import UserProfileDB
from app.data.resume_models import ExperienceType, SkillLevel
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
from app.repositories.skill_bank_repository import SkillBankRepository


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
                skills=[],  # Will be populated in SkillBank
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
        skill_bank = await self.skill_bank_repo.get_or_create_skill_bank(user_id)

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
    # DATABASE INITIALIZATION
    # =========================================================================

    async def initialize_database_with_mock_data(self) -> Dict[str, Any]:
        """Initialize database with comprehensive mock data."""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "created_users": [],
            "created_skill_banks": [],
            "errors": [],
        }

        roles = ["developer", "data_scientist", "product_manager"]

        for i, user_data in enumerate(self.SAMPLE_USERS):
            try:
                # Create user profile
                user_id = self.create_user_profile(user_data)
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

        results["summary"] = {
            "total_users_created": len(results["created_users"]),
            "total_skill_banks_created": len(results["created_skill_banks"]),
            "total_errors": len(results["errors"]),
            "success_rate": (
                len(results["created_users"]) / len(self.SAMPLE_USERS)
                if self.SAMPLE_USERS
                else 0
            ),
        }

        return results

    # =========================================================================
    # DATABASE RESET UTILITIES
    # =========================================================================

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
