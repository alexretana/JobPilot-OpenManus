#!/usr/bin/env python3
"""
Verify Mock Data Script
Simple script to verify that mock data was successfully created
"""

from app.data.database import DatabaseManager
from app.data.models import CompanyInfoDB, JobApplicationDB, JobListingDB, UserProfileDB
from app.data.resume_models import ResumeDB, ResumeTemplateDB


def verify_data():
    """Verify that mock data was created successfully"""
    db_manager = DatabaseManager()

    with db_manager.get_session() as session:
        print("🔍 Verifying mock data in database...\n")

        # Check users
        users = session.query(UserProfileDB).all()
        print(f"👥 Users: {len(users)}")
        for user in users:
            print(f"   - {user.first_name} {user.last_name} ({user.email})")

        # Check companies
        companies = session.query(CompanyInfoDB).all()
        print(f"\n🏢 Companies: {len(companies)}")
        for company in companies:
            print(f"   - {company.name} ({company.industry})")

        # Check jobs
        jobs = session.query(JobListingDB).all()
        print(f"\n💼 Job Listings: {len(jobs)}")
        for job in jobs:
            print(f"   - {job.title} at {job.company}")

        # Check resumes
        resumes = session.query(ResumeDB).all()
        print(f"\n📋 Resumes: {len(resumes)}")
        for resume in resumes:
            print(f"   - {resume.title}")

        # Check resume templates
        templates = session.query(ResumeTemplateDB).all()
        print(f"\n📄 Resume Templates: {len(templates)}")
        for template in templates:
            print(f"   - {template.name}")

        # Check applications
        applications = session.query(JobApplicationDB).all()
        print(f"\n📝 Job Applications: {len(applications)}")

        print("\n✅ Database verification complete!")
        print(
            f"   Total records: {len(users) + len(companies) + len(jobs) + len(resumes) + len(templates) + len(applications)}"
        )


if __name__ == "__main__":
    verify_data()
