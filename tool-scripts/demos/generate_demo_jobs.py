#!/usr/bin/env python3
"""
Generate Demo Jobs Script
Creates sample job data using the JobPilot job scraper tool for testing.
"""

import asyncio
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.data.database import get_database_manager, get_job_repository
from app.logger import logger
from app.tool.job_scraper.job_scraper_tool import JobScraperTool


async def generate_demo_jobs():
    """Generate demo jobs using the job scraper tool."""
    logger.info("🚀 Starting demo job generation...")

    # Initialize database
    get_database_manager()
    job_repo = get_job_repository()

    # Initialize job scraper tool
    scraper = JobScraperTool()

    # Demo queries to generate diverse jobs
    demo_queries = [
        {"query": "software engineer", "location": "Remote", "max_results": 10},
        {"query": "data scientist", "location": "San Francisco", "max_results": 8},
        {"query": "product manager", "location": "New York", "max_results": 6},
        {"query": "frontend developer", "location": "Remote", "max_results": 8},
        {"query": "machine learning engineer", "location": "Seattle", "max_results": 7},
        {"query": "devops engineer", "location": "Austin", "max_results": 6},
        {"query": "python developer", "location": "Remote", "max_results": 10},
        {"query": "mobile developer", "location": "Los Angeles", "max_results": 5},
    ]

    total_jobs_created = 0

    for query_info in demo_queries:
        logger.info(
            f"🔍 Generating jobs for: {query_info['query']} in {query_info['location']}"
        )

        try:
            result = await scraper._run(
                query=query_info["query"],
                location=query_info["location"],
                max_results=query_info["max_results"],
            )

            logger.info(f"✅ {result}")
            total_jobs_created += query_info["max_results"]

        except Exception as e:
            logger.error(f"❌ Error generating jobs for {query_info['query']}: {e}")

    # Get final job count
    recent_jobs = job_repo.get_recent_jobs(limit=100)
    actual_jobs = len(recent_jobs)

    logger.info(f"🎉 Demo job generation complete!")
    logger.info(f"📊 Total jobs in database: {actual_jobs}")

    if actual_jobs > 0:
        # Show sample of created jobs
        logger.info("📋 Sample jobs created:")
        for i, job in enumerate(recent_jobs[:5]):
            logger.info(f"  {i + 1}. {job.title} at {job.company} - {job.location}")

    return actual_jobs


async def main():
    """Main function."""
    try:
        jobs_created = await generate_demo_jobs()

        if jobs_created > 0:
            print(
                f"""
🎯 Demo Job Generation Complete!

✅ Generated {jobs_created} demo jobs
🌐 Ready to test the web interface at http://localhost:8080
💼 Switch to the "Jobs" tab to see the job cards

Next steps:
1. Start the web server: python web_server.py
2. Open http://localhost:8080 in your browser
3. Click the "Jobs" tab to see your new job cards!
"""
            )
        else:
            print("❌ No jobs were created. Please check the logs for errors.")

    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
