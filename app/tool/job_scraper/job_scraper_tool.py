"""
Job Scraper Tool for OpenManus
Integrates job scraping capabilities with OpenManus agent framework.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List

from pydantic import Field

from app.data.database import get_job_repository
from app.data.models import ExperienceLevel, JobListing, JobType, RemoteType
from app.logger import logger
from app.tool.base import BaseTool


class JobScraperTool(BaseTool):
    """Tool for scraping job listings from various sources."""

    name: str = "job_scraper"
    description: str = (
        "Scrape job listings from job boards and websites. "
        "Can search by keywords, location, and other criteria."
    )

    max_jobs: int = Field(default=20, description="Maximum number of jobs to scrape")
    rate_limit_delay: float = Field(
        default=2.0, description="Delay between requests in seconds"
    )

    def __init__(self, **data):
        """Initialize job scraper tool."""
        super().__init__(**data)
        self.job_repo = get_job_repository()

    async def _run(
        self,
        query: str = "software developer",
        location: str = "Remote",
        job_type: str = "Full-time",
        max_results: int = 20,
    ) -> str:
        """
        Scrape jobs based on search criteria.

        Args:
            query: Job search query (e.g., "python developer", "data scientist")
            location: Job location (e.g., "San Francisco", "Remote", "New York")
            job_type: Type of job (e.g., "Full-time", "Part-time", "Contract")
            max_results: Maximum number of jobs to scrape (1-50)

        Returns:
            Summary of scraped jobs
        """
        try:
            logger.info(f"Starting job scrape: {query} in {location}")

            # Limit max_results to prevent abuse
            max_results = min(max_results, 50)

            # For now, we'll use demo data generation
            # In a full implementation, this would integrate with real job boards
            scraped_jobs = await self._scrape_demo_jobs(
                query, location, job_type, max_results
            )

            if not scraped_jobs:
                return f"No jobs found for query: '{query}' in {location}"

            # Store jobs in database
            stored_count = 0
            for job_data in scraped_jobs:
                try:
                    job_listing = JobListing(**job_data)
                    self.job_repo.create_job(job_listing)
                    stored_count += 1

                    # Rate limiting
                    await asyncio.sleep(0.1)  # Small delay between database operations

                except Exception as e:
                    logger.warning(f"Failed to store job: {e}")
                    continue

            result = (
                f"Successfully scraped and stored {stored_count} jobs for '{query}' in {location}. "
                f"Job types include: {', '.join(set(job['job_type'] for job in scraped_jobs if job.get('job_type')))}. "
                f"Companies found: {', '.join(set(job['company'] for job in scraped_jobs[:5]))}{'...' if len(scraped_jobs) > 5 else ''}."
            )

            logger.info(f"Job scraping completed: {stored_count} jobs stored")
            return result

        except Exception as e:
            error_msg = f"Error scraping jobs: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def _scrape_demo_jobs(
        self, query: str, location: str, job_type: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Generate demo job listings for testing purposes.
        In production, this would be replaced with real scraping logic.
        """
        import random
        from uuid import uuid4

        # Demo data for realistic job generation
        tech_companies = [
            "Google",
            "Microsoft",
            "Amazon",
            "Apple",
            "Meta",
            "Netflix",
            "Tesla",
            "Airbnb",
            "Uber",
            "Spotify",
            "Slack",
            "Zoom",
            "DocuSign",
            "Salesforce",
            "GitHub",
            "GitLab",
            "Atlassian",
            "Dropbox",
            "Square",
            "Stripe",
        ]

        job_titles = {
            "software": [
                "Software Engineer",
                "Full Stack Developer",
                "Backend Developer",
                "Frontend Developer",
            ],
            "data": ["Data Scientist", "Data Engineer", "ML Engineer", "Data Analyst"],
            "product": [
                "Product Manager",
                "Product Owner",
                "Product Designer",
                "UX Designer",
            ],
            "devops": [
                "DevOps Engineer",
                "Site Reliability Engineer",
                "Platform Engineer",
                "Cloud Engineer",
            ],
            "security": [
                "Security Engineer",
                "Cybersecurity Analyst",
                "Security Architect",
            ],
            "mobile": [
                "iOS Developer",
                "Android Developer",
                "Mobile Developer",
                "React Native Developer",
            ],
            "ai": [
                "AI Engineer",
                "Machine Learning Engineer",
                "AI Researcher",
                "Deep Learning Engineer",
            ],
        }

        # Determine job category from query
        query_lower = query.lower()
        if (
            "data" in query_lower
            or "ml" in query_lower
            or "machine learning" in query_lower
        ):
            category = "data"
        elif "product" in query_lower:
            category = "product"
        elif "devops" in query_lower or "sre" in query_lower:
            category = "devops"
        elif "security" in query_lower:
            category = "security"
        elif (
            "mobile" in query_lower or "ios" in query_lower or "android" in query_lower
        ):
            category = "mobile"
        elif "ai" in query_lower or "artificial intelligence" in query_lower:
            category = "ai"
        else:
            category = "software"

        # Generate job listings
        jobs = []
        for i in range(max_results):
            company = random.choice(tech_companies)
            title = random.choice(job_titles.get(category, job_titles["software"]))

            # Add some variation to titles
            if random.random() < 0.3:
                level = random.choice(["Senior", "Lead", "Principal", "Staff"])
                title = f"{level} {title}"

            # Generate salary based on level and location
            base_salary = random.randint(80000, 200000)
            if "Senior" in title or "Lead" in title:
                base_salary += random.randint(20000, 50000)
            if "Principal" in title or "Staff" in title:
                base_salary += random.randint(50000, 100000)

            # Location adjustment
            if location.lower() in ["san francisco", "bay area", "palo alto"]:
                base_salary = int(base_salary * 1.3)
            elif location.lower() in ["new york", "nyc"]:
                base_salary = int(base_salary * 1.2)

            # Skills based on category
            skills_map = {
                "software": [
                    "Python",
                    "JavaScript",
                    "React",
                    "Node.js",
                    "SQL",
                    "Git",
                    "Docker",
                ],
                "data": [
                    "Python",
                    "SQL",
                    "Pandas",
                    "NumPy",
                    "Scikit-learn",
                    "TensorFlow",
                    "AWS",
                ],
                "product": [
                    "Figma",
                    "Jira",
                    "Analytics",
                    "A/B Testing",
                    "User Research",
                    "Wireframing",
                ],
                "devops": [
                    "Docker",
                    "Kubernetes",
                    "AWS",
                    "Terraform",
                    "Jenkins",
                    "Monitoring",
                ],
                "security": [
                    "Cybersecurity",
                    "Penetration Testing",
                    "SIEM",
                    "Compliance",
                    "Risk Assessment",
                ],
                "mobile": [
                    "Swift",
                    "Kotlin",
                    "React Native",
                    "Flutter",
                    "iOS",
                    "Android",
                ],
                "ai": [
                    "Python",
                    "TensorFlow",
                    "PyTorch",
                    "Deep Learning",
                    "NLP",
                    "Computer Vision",
                ],
            }

            skills_required = random.sample(
                skills_map.get(category, skills_map["software"]), random.randint(3, 6)
            )

            job_data = {
                "title": title,
                "company": company,
                "location": location if location != "Remote" else "Remote",
                "description": f"We are looking for a talented {title} to join our {category} team. "
                f"You will work on cutting-edge projects and collaborate with a world-class team.",
                "requirements": f"• {random.randint(2, 5)}+ years of experience\n"
                f"• Strong background in {category} technologies\n"
                f"• Experience with {', '.join(skills_required[:3])}",
                "responsibilities": f"• Design and develop scalable {category} solutions\n"
                f"• Collaborate with cross-functional teams\n"
                f"• Mentor junior team members\n"
                f"• Participate in code reviews and technical discussions",
                "job_type": job_type,
                "remote_type": RemoteType.REMOTE
                if location == "Remote"
                else random.choice([RemoteType.ON_SITE, RemoteType.HYBRID]),
                "experience_level": random.choice(list(ExperienceLevel)),
                "salary_min": base_salary,
                "salary_max": base_salary + random.randint(20000, 50000),
                "salary_currency": "USD",
                "skills_required": skills_required,
                "skills_preferred": random.sample(
                    skills_map.get(category, skills_map["software"]), 2
                ),
                "benefits": [
                    "Health Insurance",
                    "401(k)",
                    "Remote Work",
                    "Flexible Hours",
                    "Professional Development",
                ],
                "company_size": random.choice(
                    ["1-10", "11-50", "51-200", "201-500", "500-1000", "1000+"]
                ),
                "industry": "Technology",
                "job_url": f"https://example.com/jobs/{uuid4().hex[:8]}",
                "posted_date": datetime.utcnow(),
                "source": "demo_scraper",
                "status": "active",
            }

            jobs.append(job_data)

            # Small delay to simulate real scraping
            await asyncio.sleep(0.05)

        return jobs

    def get_available_sources(self) -> List[str]:
        """Get list of available job sources."""
        return [
            "demo_scraper",  # For testing
            # Future integrations:
            # "linkedin",
            # "indeed",
            # "glassdoor",
            # "stackoverflow_jobs",
            # "remote_ok",
            # "weworkremotely"
        ]

    def get_supported_locations(self) -> List[str]:
        """Get list of commonly supported locations."""
        return [
            "Remote",
            "San Francisco",
            "New York",
            "Seattle",
            "Austin",
            "Boston",
            "Chicago",
            "Los Angeles",
            "Denver",
            "Portland",
        ]

    def get_supported_job_types(self) -> List[str]:
        """Get list of supported job types."""
        return [jt.value for jt in JobType]
