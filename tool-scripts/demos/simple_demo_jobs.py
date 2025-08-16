#!/usr/bin/env python3
"""
Simple Demo Jobs Creator
Directly creates demo job data in the database for testing the job cards.
"""

import os
import sys
from datetime import UTC, datetime
from uuid import uuid4

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.data.database import DatabaseManager, JobRepository
from app.data.models import ExperienceLevel, JobListing, JobType, RemoteType


def create_demo_jobs():
    """Create demo jobs directly in the database."""
    print("🚀 Creating demo jobs...")

    # Initialize database with the same path as web server
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    database_url = f"sqlite:///{data_dir}/jobpilot.db"
    db_manager = DatabaseManager(database_url)
    job_repo = JobRepository(db_manager)

    # Demo job data
    demo_jobs = [
        {
            "title": "Senior Python Developer",
            "company": "TechFlow Solutions",
            "location": "Remote",
            "description": "Join our team to build scalable web applications using Python, Django, and modern cloud technologies.",
            "requirements": "• 5+ years Python experience\n• Strong Django/Flask knowledge\n• Experience with AWS/Azure\n• SQL database expertise",
            "responsibilities": "• Design and develop REST APIs\n• Collaborate with frontend teams\n• Optimize database performance\n• Mentor junior developers",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.REMOTE,
            "experience_level": ExperienceLevel.SENIOR_LEVEL,
            "salary_min": 120000,
            "salary_max": 160000,
            "salary_currency": "USD",
            "skills_required": ["Python", "Django", "AWS", "PostgreSQL", "REST API"],
            "skills_preferred": ["Docker", "Kubernetes", "React"],
            "benefits": [
                "Health Insurance",
                "401(k)",
                "Remote Work",
                "Professional Development",
            ],
            "company_size": "51-200",
            "industry": "Technology",
            "source": "demo",
        },
        {
            "title": "Data Scientist",
            "company": "DataVantage AI",
            "location": "San Francisco, CA",
            "description": "Lead machine learning initiatives and extract insights from large datasets to drive business decisions.",
            "requirements": "• PhD/MS in Data Science or related field\n• 4+ years ML experience\n• Python, R, SQL expertise\n• Experience with deep learning frameworks",
            "responsibilities": "• Build predictive models\n• Analyze large datasets\n• Present findings to stakeholders\n• Collaborate with engineering teams",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.HYBRID,
            "experience_level": ExperienceLevel.SENIOR_LEVEL,
            "salary_min": 140000,
            "salary_max": 200000,
            "salary_currency": "USD",
            "skills_required": [
                "Python",
                "Machine Learning",
                "TensorFlow",
                "SQL",
                "Statistics",
            ],
            "skills_preferred": ["PyTorch", "Spark", "AWS", "Docker"],
            "benefits": [
                "Health Insurance",
                "Stock Options",
                "Flexible Hours",
                "Learning Budget",
            ],
            "company_size": "201-500",
            "industry": "Artificial Intelligence",
            "source": "demo",
        },
        {
            "title": "Frontend Developer",
            "company": "WebCraft Studios",
            "location": "Remote",
            "description": "Create beautiful, responsive user interfaces using modern JavaScript frameworks and cutting-edge web technologies.",
            "requirements": "• 3+ years frontend development\n• React/Vue.js expertise\n• JavaScript/TypeScript proficiency\n• CSS/SASS experience",
            "responsibilities": "• Develop responsive web applications\n• Collaborate with UX designers\n• Optimize application performance\n• Write clean, maintainable code",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.REMOTE,
            "experience_level": ExperienceLevel.MID_LEVEL,
            "salary_min": 85000,
            "salary_max": 120000,
            "salary_currency": "USD",
            "skills_required": ["JavaScript", "React", "CSS", "HTML", "TypeScript"],
            "skills_preferred": ["Vue.js", "Node.js", "GraphQL", "Testing"],
            "benefits": [
                "Health Insurance",
                "Remote Work",
                "Flexible Hours",
                "Equipment Allowance",
            ],
            "company_size": "11-50",
            "industry": "Web Development",
            "source": "demo",
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudScale Technologies",
            "location": "Seattle, WA",
            "description": "Build and maintain cloud infrastructure, automate deployments, and ensure system reliability at scale.",
            "requirements": "• 4+ years DevOps experience\n• AWS/Azure expertise\n• Docker/Kubernetes knowledge\n• CI/CD pipeline experience",
            "responsibilities": "• Design cloud infrastructure\n• Automate deployment processes\n• Monitor system performance\n• Ensure security best practices",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.ON_SITE,
            "experience_level": ExperienceLevel.SENIOR_LEVEL,
            "salary_min": 110000,
            "salary_max": 150000,
            "salary_currency": "USD",
            "skills_required": ["AWS", "Docker", "Kubernetes", "Terraform", "Linux"],
            "skills_preferred": ["Jenkins", "Ansible", "Monitoring", "Python"],
            "benefits": [
                "Health Insurance",
                "Stock Options",
                "On-site Gym",
                "Catered Meals",
            ],
            "company_size": "501-1000",
            "industry": "Cloud Computing",
            "source": "demo",
        },
        {
            "title": "Product Manager",
            "company": "InnovateTech Corp",
            "location": "Austin, TX",
            "description": "Drive product strategy and work cross-functionally to deliver innovative solutions that delight customers.",
            "requirements": "• 5+ years product management experience\n• Technical background preferred\n• Strong analytical skills\n• Experience with Agile methodologies",
            "responsibilities": "• Define product roadmap\n• Gather customer requirements\n• Coordinate with engineering teams\n• Analyze market trends",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.HYBRID,
            "experience_level": ExperienceLevel.SENIOR_LEVEL,
            "salary_min": 130000,
            "salary_max": 180000,
            "salary_currency": "USD",
            "skills_required": [
                "Product Management",
                "Analytics",
                "Agile",
                "Strategy",
                "Communication",
            ],
            "skills_preferred": ["SQL", "Jira", "Figma", "A/B Testing"],
            "benefits": [
                "Health Insurance",
                "401(k)",
                "Flexible Hours",
                "Stock Options",
            ],
            "company_size": "1000+",
            "industry": "Technology",
            "source": "demo",
        },
        {
            "title": "Mobile Developer (iOS)",
            "company": "AppWorks Mobile",
            "location": "Los Angeles, CA",
            "description": "Develop native iOS applications with focus on user experience and performance optimization.",
            "requirements": "• 3+ years iOS development\n• Swift/Objective-C expertise\n• App Store publication experience\n• UI/UX design sense",
            "responsibilities": "• Build iOS applications\n• Optimize app performance\n• Collaborate with designers\n• Maintain code quality",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.HYBRID,
            "experience_level": ExperienceLevel.MID_LEVEL,
            "salary_min": 95000,
            "salary_max": 140000,
            "salary_currency": "USD",
            "skills_required": ["Swift", "iOS", "Xcode", "UIKit", "Core Data"],
            "skills_preferred": ["SwiftUI", "Combine", "Firebase", "TestFlight"],
            "benefits": [
                "Health Insurance",
                "MacBook Pro",
                "Flexible Hours",
                "Learning Budget",
            ],
            "company_size": "51-200",
            "industry": "Mobile Development",
            "source": "demo",
        },
    ]

    created_count = 0

    for job_data in demo_jobs:
        try:
            # Add timestamp and ID
            job_data.update(
                {
                    "posted_date": datetime.now(UTC),
                    "job_url": f"https://demo-jobs.example.com/job/{str(uuid4())[:8]}",
                    "status": "active",
                }
            )

            # Create job listing
            job = JobListing(**job_data)
            created_job = job_repo.create_job(job)

            print(f"✅ Created: {created_job.title} at {created_job.company}")
            created_count += 1

        except Exception as e:
            print(f"❌ Error creating job {job_data['title']}: {e}")

    print(
        f"""
🎯 Demo Job Creation Complete!

✅ Created {created_count} demo jobs
🌐 Ready to test the web interface at http://localhost:8080
💼 Switch to the "Jobs" tab to see the job cards

Next steps:
1. Start the web server: python web_server.py
2. Open http://localhost:8080 in your browser
3. Click the "💼 Jobs" tab to see your new job cards!
"""
    )

    return created_count


if __name__ == "__main__":
    try:
        create_demo_jobs()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
