"""
Test data factories and generators for JobPilot-OpenManus testing.

This module provides consistent test data generation using factory patterns
to create realistic job listings, user profiles, and other test entities.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from faker import Faker
import uuid

# Initialize faker for generating realistic test data
fake = Faker()


@dataclass
class TestDataConfig:
    """Configuration for test data generation."""
    seed: Optional[int] = 42
    locale: str = 'en_US'
    consistent: bool = True


class JobDataFactory:
    """Factory for generating job listing test data."""
    
    # Common job titles for different categories
    TECH_TITLES = [
        "Software Engineer", "Senior Software Engineer", "Full Stack Developer",
        "Frontend Developer", "Backend Developer", "DevOps Engineer",
        "Data Scientist", "Machine Learning Engineer", "Product Manager",
        "UI/UX Designer", "Quality Assurance Engineer", "System Administrator"
    ]
    
    COMPANIES = [
        "TechCorp", "InnovateSoft", "DataDyne Solutions", "CloudFirst",
        "AI Innovations", "WebCraft Studios", "DevFlow Inc", "CodeBase Solutions",
        "Future Systems", "Digital Dynamics", "Smart Technologies", "NextGen Labs"
    ]
    
    SKILLS = {
        "backend": ["Python", "Java", "Node.js", "Go", "C#", "Ruby", "PHP", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes"],
        "frontend": ["React", "Vue.js", "Angular", "TypeScript", "JavaScript", "HTML", "CSS", "Sass", "Webpack", "Next.js", "Svelte"],
        "data": ["Python", "R", "SQL", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Apache Spark", "Tableau"],
        "devops": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Jenkins", "GitLab CI", "Prometheus", "Grafana"],
        "mobile": ["React Native", "Flutter", "Swift", "Kotlin", "Java", "Objective-C", "Xamarin", "Ionic"]
    }
    
    BENEFITS = [
        "Health insurance", "Dental insurance", "Vision insurance", "401(k) matching",
        "Flexible work hours", "Remote work options", "Professional development budget",
        "Conference attendance", "Unlimited PTO", "Parental leave", "Stock options",
        "Gym membership", "Free lunch", "Team retreats", "Learning stipend"
    ]
    
    @classmethod
    def create(cls, **overrides) -> Dict[str, Any]:
        """Create a single job listing with optional field overrides."""
        company = random.choice(cls.COMPANIES)
        title = random.choice(cls.TECH_TITLES)
        
        # Generate skills based on job title
        skill_category = cls._get_skill_category(title)
        skills = random.sample(cls.SKILLS[skill_category], k=random.randint(3, 6))
        
        # Generate salary range
        base_salary = random.randint(60, 200) * 1000
        salary_range = random.randint(10, 30) * 1000
        
        job_data = {
            "name": f"test-{fake.slug()}",
            "title": title,
            "company": company,
            "location": fake.city() + ", " + fake.state_abbr(),
            "description": cls._generate_job_description(title, company, skills),
            "requirements": cls._generate_requirements(title, skills),
            "job_type": random.choice(["Full-time", "Part-time", "Contract", "Internship"]),
            "remote_type": random.choice(["Remote", "Hybrid", "On-site"]),
            "salary_min": base_salary,
            "salary_max": base_salary + salary_range,
            "skills_required": skills[:3],  # Top 3 required skills
            "skills_preferred": skills[3:] if len(skills) > 3 else [],
            "tech_stack": random.sample(skills + ["Git", "Linux", "Agile"], k=min(5, len(skills) + 2)),
            "benefits": random.sample(cls.BENEFITS, k=random.randint(3, 7)),
            "experience_level": random.choice(["Junior", "Mid-level", "Senior", "Lead", "Manager"]),
            "posted_date": fake.date_between(start_date='-30d', end_date='today'),
            "application_deadline": fake.date_between(start_date='today', end_date='+60d')
        }
        
        # Apply any overrides
        job_data.update(overrides)
        return job_data
    
    @classmethod
    def create_batch(cls, count: int, **common_overrides) -> List[Dict[str, Any]]:
        """Create multiple job listings with optional common overrides."""
        return [cls.create(**common_overrides) for _ in range(count)]
    
    @classmethod
    def create_specific_jobs(cls) -> Dict[str, Dict[str, Any]]:
        """Create a set of specific, predictable jobs for testing."""
        return {
            "python_senior": cls.create(
                name="test-python-senior",
                title="Senior Python Developer",
                company="PythonCorp",
                location="San Francisco, CA",
                skills_required=["Python", "Django", "PostgreSQL"],
                skills_preferred=["Redis", "Celery", "AWS"],
                salary_min=120000,
                salary_max=160000,
                remote_type="Remote",
                experience_level="Senior"
            ),
            "react_frontend": cls.create(
                name="test-react-frontend",
                title="React Frontend Developer",
                company="Frontend Studios",
                location="New York, NY",
                skills_required=["React", "TypeScript", "CSS"],
                skills_preferred=["Next.js", "GraphQL", "Jest"],
                salary_min=90000,
                salary_max=120000,
                remote_type="Hybrid",
                experience_level="Mid-level"
            ),
            "data_scientist": cls.create(
                name="test-data-scientist",
                title="Data Scientist",
                company="AI Analytics",
                location="Boston, MA",
                skills_required=["Python", "Machine Learning", "SQL"],
                skills_preferred=["TensorFlow", "PyTorch", "Jupyter"],
                salary_min=110000,
                salary_max=150000,
                remote_type="On-site",
                experience_level="Mid-level"
            )
        }
    
    @classmethod
    def _get_skill_category(cls, title: str) -> str:
        """Determine skill category based on job title."""
        title_lower = title.lower()
        if any(word in title_lower for word in ["data", "scientist", "analyst", "ml", "machine learning"]):
            return "data"
        elif any(word in title_lower for word in ["frontend", "front-end", "ui", "ux", "react", "vue"]):
            return "frontend"
        elif any(word in title_lower for word in ["devops", "infrastructure", "sre", "platform"]):
            return "devops"
        elif any(word in title_lower for word in ["mobile", "ios", "android", "react native", "flutter"]):
            return "mobile"
        else:
            return "backend"
    
    @classmethod
    def _generate_job_description(cls, title: str, company: str, skills: List[str]) -> str:
        """Generate a realistic job description."""
        return f"""
Join {company} as a {title}! We're looking for a talented professional to help us build amazing products.

Key Responsibilities:
• Design and develop scalable software solutions
• Collaborate with cross-functional teams
• Write clean, maintainable code
• Participate in code reviews and technical discussions
• Contribute to architecture and design decisions

What We're Looking For:
• Experience with {', '.join(skills[:3])}
• Strong problem-solving skills
• Excellent communication abilities
• Passion for technology and continuous learning

Join our team and make a real impact while working with cutting-edge technologies!
        """.strip()
    
    @classmethod
    def _generate_requirements(cls, title: str, skills: List[str]) -> str:
        """Generate realistic job requirements."""
        experience_years = random.randint(2, 8)
        return f"""
• {experience_years}+ years of experience in software development
• Proficiency in {', '.join(skills[:2])}
• Experience with {skills[2] if len(skills) > 2 else 'modern development practices'}
• Bachelor's degree in Computer Science or equivalent experience
• Strong analytical and problem-solving skills
• Excellent written and verbal communication skills
        """.strip()


class UserDataFactory:
    """Factory for generating user profile test data."""
    
    SKILLS_POOL = [
        "Python", "JavaScript", "Java", "TypeScript", "React", "Node.js",
        "SQL", "PostgreSQL", "MongoDB", "Docker", "AWS", "Git", "Linux",
        "Machine Learning", "Data Analysis", "Project Management", "Agile"
    ]
    
    @classmethod
    def create(cls, **overrides) -> Dict[str, Any]:
        """Create a user profile with optional field overrides."""
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        user_data = {
            "id": str(uuid.uuid4()),
            "name": f"{first_name} {last_name}",
            "email": fake.email(),
            "phone": fake.phone_number(),
            "location": fake.city() + ", " + fake.state_abbr(),
            "skills": random.sample(cls.SKILLS_POOL, k=random.randint(5, 10)),
            "experience_years": random.randint(1, 15),
            "current_title": random.choice(JobDataFactory.TECH_TITLES),
            "current_company": random.choice(JobDataFactory.COMPANIES),
            "salary_expectation_min": random.randint(70, 150) * 1000,
            "salary_expectation_max": random.randint(90, 200) * 1000,
            "preferred_locations": [fake.city() + ", " + fake.state_abbr() for _ in range(random.randint(1, 3))],
            "remote_preference": random.choice(["Remote only", "Hybrid preferred", "No preference", "On-site preferred"]),
            "job_types": random.sample(["Full-time", "Part-time", "Contract"], k=random.randint(1, 2)),
            "linkedin_url": f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
            "github_url": f"https://github.com/{first_name.lower()}{last_name[0].lower()}",
            "resume_url": f"https://example.com/resumes/{fake.uuid4()}.pdf",
            "availability": random.choice(["Immediately", "2 weeks", "1 month", "3 months"])
        }
        
        # Apply any overrides
        user_data.update(overrides)
        return user_data
    
    @classmethod
    def create_batch(cls, count: int, **common_overrides) -> List[Dict[str, Any]]:
        """Create multiple user profiles."""
        return [cls.create(**common_overrides) for _ in range(count)]


class ApplicationDataFactory:
    """Factory for generating job application test data."""
    
    @classmethod
    def create(cls, job_id: str = None, user_id: str = None, **overrides) -> Dict[str, Any]:
        """Create a job application with optional field overrides."""
        application_data = {
            "id": str(uuid.uuid4()),
            "job_id": job_id or str(uuid.uuid4()),
            "user_id": user_id or str(uuid.uuid4()),
            "status": random.choice(["Applied", "Reviewing", "Phone Screen", "Technical Interview", 
                                  "Final Interview", "Offer", "Rejected", "Withdrawn"]),
            "applied_date": fake.date_between(start_date='-60d', end_date='today'),
            "cover_letter": cls._generate_cover_letter(),
            "notes": fake.sentence(nb_words=10),
            "follow_up_date": fake.date_between(start_date='today', end_date='+30d'),
            "interview_dates": [
                fake.date_time_between(start_date='today', end_date='+14d')
                for _ in range(random.randint(0, 3))
            ]
        }
        
        # Apply any overrides
        application_data.update(overrides)
        return application_data
    
    @classmethod
    def _generate_cover_letter(cls) -> str:
        """Generate a sample cover letter."""
        return f"""
Dear Hiring Manager,

I am excited to apply for this position at your company. With my background in software development and passion for technology, I believe I would be a great fit for your team.

{fake.paragraph(nb_sentences=3)}

I look forward to the opportunity to discuss how my skills and experience can contribute to your team's success.

Best regards,
{fake.name()}
        """.strip()


class TimelineEventFactory:
    """Factory for generating timeline event test data."""
    
    EVENT_TYPES = [
        "job_search_started", "application_submitted", "interview_scheduled",
        "interview_completed", "offer_received", "offer_accepted", "offer_declined",
        "follow_up_sent", "networking_event", "skill_certification", "resume_updated"
    ]
    
    @classmethod
    def create(cls, **overrides) -> Dict[str, Any]:
        """Create a timeline event with optional field overrides."""
        event_type = random.choice(cls.EVENT_TYPES)
        
        event_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "event_type": event_type,
            "title": cls._generate_event_title(event_type),
            "description": cls._generate_event_description(event_type),
            "date": fake.date_time_between(start_date='-90d', end_date='today'),
            "importance": random.choice(["low", "medium", "high"]),
            "tags": random.sample(["job-search", "interview", "networking", "skills", "application"], 
                                k=random.randint(1, 3))
        }
        
        # Apply any overrides
        event_data.update(overrides)
        return event_data
    
    @classmethod
    def _generate_event_title(cls, event_type: str) -> str:
        """Generate appropriate title for event type."""
        titles = {
            "job_search_started": "Started Job Search",
            "application_submitted": f"Applied to {random.choice(JobDataFactory.COMPANIES)}",
            "interview_scheduled": "Interview Scheduled",
            "interview_completed": "Completed Interview",
            "offer_received": "Job Offer Received",
            "offer_accepted": "Accepted Job Offer",
            "offer_declined": "Declined Job Offer",
            "follow_up_sent": "Sent Follow-up Email",
            "networking_event": f"Attended {fake.company()} Meetup",
            "skill_certification": f"Completed {random.choice(['AWS', 'Google Cloud', 'Docker'])} Certification",
            "resume_updated": "Updated Resume"
        }
        return titles.get(event_type, "Job Search Event")
    
    @classmethod
    def _generate_event_description(cls, event_type: str) -> str:
        """Generate appropriate description for event type."""
        return fake.sentence(nb_words=random.randint(5, 15))


# Helper functions for test setup

def setup_test_database_data(db_session, num_jobs: int = 5, num_users: int = 3) -> Dict[str, List[Any]]:
    """Set up test data in database for testing."""
    # Note: This would require actual database models to be implemented
    # For now, just return the data that would be created
    
    jobs = JobDataFactory.create_batch(num_jobs)
    users = UserDataFactory.create_batch(num_users)
    applications = [
        ApplicationDataFactory.create(
            job_id=random.choice(jobs)["name"], 
            user_id=random.choice(users)["id"]
        ) 
        for _ in range(random.randint(2, 8))
    ]
    
    return {
        "jobs": jobs,
        "users": users,
        "applications": applications
    }


def create_test_scenario(scenario_name: str) -> Dict[str, Any]:
    """Create predefined test scenarios for specific testing needs."""
    scenarios = {
        "job_search_workflow": {
            "user": UserDataFactory.create(
                name="Test User",
                email="test@example.com",
                skills=["Python", "React", "SQL"]
            ),
            "jobs": JobDataFactory.create_specific_jobs(),
            "searches": [
                {"query": "Python developer", "expected_matches": ["python_senior"]},
                {"query": "React frontend", "expected_matches": ["react_frontend"]},
                {"query": "Data scientist", "expected_matches": ["data_scientist"]}
            ]
        },
        "application_lifecycle": {
            "user": UserDataFactory.create(name="Applicant User"),
            "job": JobDataFactory.create(name="target-position"),
            "application_stages": [
                {"status": "Applied", "date": "2024-01-01"},
                {"status": "Phone Screen", "date": "2024-01-08"},
                {"status": "Technical Interview", "date": "2024-01-15"},
                {"status": "Offer", "date": "2024-01-22"}
            ]
        }
    }
    
    return scenarios.get(scenario_name, {})


# Test data cleanup utilities

def cleanup_test_data(db_session, prefix: str = "test-"):
    """Clean up test data from database."""
    # This would implement actual cleanup logic
    # For now, just log what would be cleaned up
    print(f"Would clean up all records with prefix: {prefix}")


def reset_test_data_factories(seed: int = 42):
    """Reset faker seed for consistent test data."""
    fake.seed_instance(seed)
    random.seed(seed)


if __name__ == "__main__":
    # Example usage and testing
    print("JobPilot Test Data Factories")
    print("=" * 50)
    
    # Create sample job data
    job = JobDataFactory.create()
    print(f"Sample Job: {job['title']} at {job['company']}")
    print(f"Skills: {', '.join(job['skills_required'])}")
    
    # Create sample user data
    user = UserDataFactory.create()
    print(f"\nSample User: {user['name']}")
    print(f"Skills: {', '.join(user['skills'][:5])}")
    
    # Create batch data
    jobs = JobDataFactory.create_batch(3, remote_type="Remote")
    print(f"\nCreated {len(jobs)} remote jobs")
    
    # Test scenario
    scenario = create_test_scenario("job_search_workflow")
    print(f"\nJob Search Scenario created with {len(scenario['jobs'])} jobs")
