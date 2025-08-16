"""
Job Discovery Agent
Specialized agent for finding and extracting job listings from various sources.
"""

from typing import Dict, List

from pydantic import Field

from app.agent.base import BaseAgent
from app.data.database import get_job_repository
from app.logger import logger
from app.tool import ToolCollection
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.job_scraper import JobScraperTool
from app.tool.python_execute import PythonExecute


class JobDiscoveryAgent(BaseAgent):
    """Agent specialized in discovering and extracting job listings."""

    name: str = "JobDiscovery"
    description: str = (
        "Specialized agent for finding and extracting job listings from job boards and company websites"
    )

    system_prompt: str = """You are JobDiscovery, an AI agent specialized in finding and extracting job listings.

Your primary responsibilities:
1. Search for job listings based on user criteria (keywords, location, job type, etc.)
2. Extract detailed job information from job boards and company websites
3. Identify new job opportunities and sources
4. Maintain a comprehensive database of job listings
5. Provide insights about job market trends

You have access to:
- Job scraping tools for automated job discovery
- Browser automation for accessing job boards
- Database tools for storing and managing job listings
- Python execution for data processing and analysis

Always:
- Be thorough in job extraction and include all relevant details
- Respect rate limits and scraping ethics
- Validate and clean job data before storage
- Provide clear summaries of discovery results
- Handle errors gracefully and suggest alternatives

When scraping jobs:
- Focus on accuracy and completeness of job details
- Extract skills, requirements, salary, and company information
- Categorize jobs by industry, level, and type
- Identify remote work opportunities
- Note application deadlines and requirements"""

    # Tools specific to job discovery
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            JobScraperTool(),
            BrowserUseTool(),
            PythonExecute(),
        )
    )

    max_steps: int = 15

    def __init__(self, **data):
        """Initialize Job Discovery Agent."""
        super().__init__(**data)
        self.job_repo = get_job_repository()

    async def discover_jobs(
        self,
        query: str,
        location: str = "Remote",
        max_results: int = 20,
        job_type: str = "Full-time",
    ) -> Dict:
        """
        Discover jobs based on search criteria.

        Args:
            query: Job search query (e.g., "python developer", "data scientist")
            location: Target location for jobs
            max_results: Maximum number of jobs to find
            job_type: Type of employment

        Returns:
            Dictionary with discovery results
        """
        try:
            logger.info(f"Starting job discovery: {query} in {location}")

            # Use the job scraper tool
            scraper_result = await self.available_tools.tools[0]._run(
                query=query,
                location=location,
                job_type=job_type,
                max_results=max_results,
            )

            # Get current job count for statistics
            recent_jobs = self.job_repo.get_recent_jobs(limit=max_results)

            result = {
                "query": query,
                "location": location,
                "job_type": job_type,
                "scraper_result": scraper_result,
                "jobs_found": len(recent_jobs),
                "jobs_sample": [
                    {
                        "title": job.title,
                        "company": job.company,
                        "location": job.location,
                        "salary_range": (
                            f"${job.salary_min:,}-${job.salary_max:,}"
                            if job.salary_min and job.salary_max
                            else "Not specified"
                        ),
                    }
                    for job in recent_jobs[:5]
                ],
            }

            logger.info(f"Job discovery completed: {len(recent_jobs)} jobs found")
            return result

        except Exception as e:
            logger.error(f"Error in job discovery: {e}")
            return {
                "error": str(e),
                "query": query,
                "location": location,
                "jobs_found": 0,
            }

    async def analyze_job_market(self, query: str = None) -> Dict:
        """
        Analyze current job market trends.

        Args:
            query: Optional filter for specific job types

        Returns:
            Market analysis results
        """
        try:
            # Get recent jobs for analysis
            recent_jobs = self.job_repo.get_recent_jobs(limit=100)

            if not recent_jobs:
                return {"error": "No jobs available for analysis"}

            # Analyze job market
            analysis = {
                "total_jobs": len(recent_jobs),
                "companies": len(set(job.company for job in recent_jobs)),
                "locations": {},
                "job_types": {},
                "remote_types": {},
                "salary_ranges": {},
                "top_skills": {},
                "top_companies": {},
            }

            # Count locations
            for job in recent_jobs:
                location = job.location or "Not specified"
                analysis["locations"][location] = (
                    analysis["locations"].get(location, 0) + 1
                )

            # Count job types
            for job in recent_jobs:
                job_type = job.job_type.value if job.job_type else "Not specified"
                analysis["job_types"][job_type] = (
                    analysis["job_types"].get(job_type, 0) + 1
                )

            # Count remote types
            for job in recent_jobs:
                remote_type = (
                    job.remote_type.value if job.remote_type else "Not specified"
                )
                analysis["remote_types"][remote_type] = (
                    analysis["remote_types"].get(remote_type, 0) + 1
                )

            # Analyze salaries
            salaries = [job.salary_min for job in recent_jobs if job.salary_min]
            if salaries:
                analysis["salary_ranges"] = {
                    "min": min(salaries),
                    "max": max(salaries),
                    "average": sum(salaries) // len(salaries),
                }

            # Count skills
            for job in recent_jobs:
                if job.skills_required:
                    for skill in job.skills_required:
                        analysis["top_skills"][skill] = (
                            analysis["top_skills"].get(skill, 0) + 1
                        )

            # Count companies
            for job in recent_jobs:
                analysis["top_companies"][job.company] = (
                    analysis["top_companies"].get(job.company, 0) + 1
                )

            # Sort and limit top items
            analysis["locations"] = dict(
                sorted(analysis["locations"].items(), key=lambda x: x[1], reverse=True)[
                    :10
                ]
            )
            analysis["top_skills"] = dict(
                sorted(
                    analysis["top_skills"].items(), key=lambda x: x[1], reverse=True
                )[:10]
            )
            analysis["top_companies"] = dict(
                sorted(
                    analysis["top_companies"].items(), key=lambda x: x[1], reverse=True
                )[:10]
            )

            logger.info(
                f"Job market analysis completed: {len(recent_jobs)} jobs analyzed"
            )
            return analysis

        except Exception as e:
            logger.error(f"Error in job market analysis: {e}")
            return {"error": str(e)}

    async def search_company_jobs(self, company: str) -> List[Dict]:
        """
        Search for jobs at a specific company.

        Args:
            company: Company name to search for

        Returns:
            List of jobs at the company
        """
        try:
            jobs = self.job_repo.get_jobs_by_company(company)

            result = [
                {
                    "id": job.id,
                    "title": job.title,
                    "location": job.location,
                    "job_type": job.job_type.value if job.job_type else None,
                    "remote_type": job.remote_type.value if job.remote_type else None,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "skills_required": job.skills_required,
                    "posted_date": (
                        job.posted_date.isoformat() if job.posted_date else None
                    ),
                    "job_url": job.job_url,
                }
                for job in jobs
            ]

            logger.info(f"Found {len(result)} jobs at {company}")
            return result

        except Exception as e:
            logger.error(f"Error searching company jobs: {e}")
            return []
