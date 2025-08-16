"""
JSearch API Client Implementation
Connects to JSearch API via RapidAPI for aggregated job search
"""

import hashlib
from typing import Dict, List

from base_client import (
    JobAPIClient,
    JobListing,
    JobSearchProvider,
    JobSearchQuery,
    RateLimitInfo,
    save_response_sample,
)


class JSearchClient(JobAPIClient):
    """JSearch API client implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, base_url="https://jsearch.p.rapidapi.com")
        self._requests_used = 0
        self._monthly_limit = 200  # Free tier limit

    def get_provider_type(self) -> JobSearchProvider:
        return JobSearchProvider.JSEARCH

    async def authenticate(self) -> bool:
        """Test authentication by making a simple request"""
        try:
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            }

            # Test with a minimal search to verify auth
            params = {"query": "test", "page": "1", "num_pages": "1"}

            result = await self._make_request("search", params=params, headers=headers)
            return result["success"]

        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    async def search_jobs(self, query: JobSearchQuery) -> List[JobListing]:
        """Search for jobs using JSearch API"""
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }

        # Build query parameters
        params = {
            "query": query.query,
            "page": str(query.page),
            "num_pages": str(query.num_pages),
        }

        if query.location:
            params["query"] += f" in {query.location}"

        if query.date_posted:
            params["date_posted"] = query.date_posted

        if query.employment_types:
            params["employment_types"] = ",".join(query.employment_types)

        if query.job_requirements:
            params["job_requirements"] = ",".join(query.job_requirements)

        # Make the API request
        result = await self._make_request("search", params=params, headers=headers)

        if result["success"]:
            # Save sample response for analysis
            save_response_sample(
                provider="jsearch",
                endpoint="search",
                response=result["data"],
                query_params=params,
            )

            return self.transform_response(result["data"])
        else:
            raise Exception(
                f"API request failed: {result.get('error', 'Unknown error')}"
            )

    def transform_response(self, raw_response: Dict) -> List[JobListing]:
        """Transform JSearch response to standardized JobListing format"""
        jobs = []

        # JSearch response structure analysis
        data = raw_response.get("data", [])

        for job_data in data:
            try:
                # Generate a unique ID from job details
                job_id = self._generate_job_id(job_data)

                # Extract core fields
                title = job_data.get("job_title", "")
                company = job_data.get("employer_name", "")
                location = self._format_location(job_data)
                description = job_data.get("job_description", "")

                # Extract optional fields
                salary_min, salary_max, salary_currency = self._extract_salary_info(
                    job_data
                )
                employment_type = job_data.get("job_employment_type", "")
                date_posted = job_data.get("job_posted_at_datetime_utc", "")
                apply_url = job_data.get("job_apply_link", "")
                company_logo = job_data.get("employer_logo", "")

                # Extract job requirements and benefits
                job_requirements = self._extract_requirements(job_data)
                benefits = job_data.get("job_benefits", [])

                # Create standardized job listing
                job_listing = JobListing(
                    id=job_id,
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency=salary_currency,
                    employment_type=employment_type,
                    date_posted=date_posted,
                    apply_url=apply_url,
                    company_logo=company_logo,
                    job_requirements=job_requirements,
                    benefits=benefits,
                    source_provider="jsearch",
                    source_site=job_data.get("job_publisher", ""),
                    raw_data=job_data,
                )

                jobs.append(job_listing)

            except Exception as e:
                print(f"Error transforming job data: {e}")
                print(f"Job data: {job_data}")
                continue

        return jobs

    def get_rate_limits(self) -> RateLimitInfo:
        """Get current rate limit information"""
        return RateLimitInfo(
            requests_per_month=self._monthly_limit,
            requests_used=self._request_count,
            requests_remaining=self._monthly_limit - self._request_count,
        )

    def _generate_job_id(self, job_data: Dict) -> str:
        """Generate a unique ID for the job"""
        # Use job_id if available, otherwise generate from key fields
        if "job_id" in job_data:
            return job_data["job_id"]

        # Generate hash from key identifying fields
        key_fields = [
            job_data.get("job_title", ""),
            job_data.get("employer_name", ""),
            job_data.get("job_city", ""),
            job_data.get("job_apply_link", ""),
        ]
        key_string = "|".join(str(field) for field in key_fields)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _format_location(self, job_data: Dict) -> str:
        """Format location from job data"""
        city = job_data.get("job_city", "")
        state = job_data.get("job_state", "")
        country = job_data.get("job_country", "")

        location_parts = [part for part in [city, state, country] if part]
        return ", ".join(location_parts) if location_parts else "Remote"

    def _extract_salary_info(self, job_data: Dict) -> tuple:
        """Extract salary information"""
        try:
            salary_min = job_data.get("job_min_salary")
            salary_max = job_data.get("job_max_salary")
            salary_currency = job_data.get("job_salary_currency", "USD")

            # Convert to float if present
            if salary_min is not None:
                salary_min = float(salary_min)
            if salary_max is not None:
                salary_max = float(salary_max)

            return salary_min, salary_max, salary_currency

        except (ValueError, TypeError):
            return None, None, None

    def _extract_requirements(self, job_data: Dict) -> List[str]:
        """Extract job requirements from description or highlights"""
        requirements = []

        # Check for specific requirement fields
        if "job_required_experience" in job_data:
            req = job_data["job_required_experience"]
            if isinstance(req, dict):
                exp_required = req.get("experience_mentioned", False)
                exp_level = req.get("required_experience_in_months", 0)
                if exp_required:
                    years = exp_level / 12 if exp_level else 0
                    requirements.append(
                        f"Experience: {years} years"
                        if years > 0
                        else "Experience required"
                    )

        # Check for required skills
        if "job_required_skills" in job_data:
            skills = job_data["job_required_skills"]
            if isinstance(skills, list):
                requirements.extend([f"Skill: {skill}" for skill in skills])

        # Check for education requirements
        if "job_required_education" in job_data:
            edu = job_data["job_required_education"]
            if isinstance(edu, dict) and edu.get("education_mentioned"):
                degree = edu.get("degree_mentioned", "Degree required")
                requirements.append(f"Education: {degree}")

        return requirements


# Convenience functions for testing


async def test_jsearch_api(
    api_key: str, query: str = "software engineer", location: str = "New York, NY"
):
    """Test JSearch API with a simple query"""
    async with JSearchClient(api_key) as client:
        try:
            # Test authentication
            auth_result = await client.authenticate()
            print(f"Authentication: {'✅ Success' if auth_result else '❌ Failed'}")

            if not auth_result:
                return None

            # Test job search
            test_query = JobSearchQuery(
                query=query, location=location, page=1, num_pages=1
            )

            print(f"Searching for: '{query}' in '{location}'...")
            jobs = await client.search_jobs(test_query)

            print(f"Found {len(jobs)} jobs")

            # Display first job as sample
            if jobs:
                job = jobs[0]
                print("\nSample Job:")
                print(f"  Title: {job.title}")
                print(f"  Company: {job.company}")
                print(f"  Location: {job.location}")
                print(f"  Employment Type: {job.employment_type}")
                print(
                    f"  Salary: {job.salary_min}-{job.salary_max} {job.salary_currency}"
                )
                print(f"  Posted: {job.date_posted}")
                print(f"  Apply URL: {job.apply_url}")
                print(f"  Description (first 200 chars): {job.description[:200]}...")

            # Display usage stats
            stats = client.get_usage_stats()
            rate_limits = client.get_rate_limits()

            print("\nUsage Stats:")
            print(f"  Requests made: {stats['requests_made']}")
            print(
                f"  Rate limit: {rate_limits.requests_used}/{rate_limits.requests_per_month}"
            )
            print(f"  Remaining: {rate_limits.requests_remaining}")

            return jobs

        except Exception as e:
            print(f"Error testing JSearch API: {e}")
            return None


if __name__ == "__main__":
    import asyncio

    # Test with your API key
    API_KEY = input("Enter your RapidAPI key: ")

    asyncio.run(test_jsearch_api(API_KEY))
