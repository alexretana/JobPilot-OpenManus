"""
Base API Client for Job Search APIs
Provides abstract interface for different job search API implementations
"""

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import aiohttp


class JobSearchProvider(Enum):
    """Supported job search API providers"""

    JSEARCH = "jsearch"
    FREEWEBAPI = "freewebapi"


@dataclass
class JobSearchQuery:
    """Standard job search query parameters"""

    query: str
    location: Optional[str] = None
    country: Optional[str] = "US"
    page: int = 1
    num_pages: int = 1
    date_posted: Optional[str] = None  # all, today, 3days, week, month
    employment_types: Optional[List[str]] = (
        None  # FULLTIME, PARTTIME, CONTRACTOR, INTERN
    )
    job_requirements: Optional[List[str]] = (
        None  # under_3_years_experience, more_than_3_years_experience, no_experience, no_degree
    )
    company_types: Optional[List[str]] = None
    radius: Optional[int] = None


@dataclass
class RateLimitInfo:
    """Rate limiting information"""

    requests_per_month: int
    requests_used: int
    requests_remaining: int
    reset_date: Optional[datetime] = None


@dataclass
class JobListing:
    """Standardized job listing data structure"""

    # Core fields
    id: str
    title: str
    company: str
    location: str
    description: str

    # Optional fields
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    employment_type: Optional[str] = None
    date_posted: Optional[str] = None
    apply_url: Optional[str] = None
    company_logo: Optional[str] = None
    job_requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None

    # Metadata
    source_provider: Optional[str] = None
    source_site: Optional[str] = None
    raw_data: Optional[Dict] = None


@dataclass
class APITestResult:
    """Results from API testing"""

    provider: JobSearchProvider
    success: bool
    response_time_ms: int
    jobs_returned: int
    error_message: Optional[str] = None
    sample_job: Optional[JobListing] = None
    rate_limit_info: Optional[RateLimitInfo] = None


class JobAPIClient(ABC):
    """Abstract base class for job search API clients"""

    def __init__(self, api_key: Optional[str] = None, base_url: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_count = 0
        self._start_time = time.time()

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def authenticate(self) -> bool:
        """Test authentication and connection"""

    @abstractmethod
    async def search_jobs(self, query: JobSearchQuery) -> List[JobListing]:
        """Search for jobs using the API"""

    @abstractmethod
    def get_rate_limits(self) -> RateLimitInfo:
        """Get current rate limit information"""

    @abstractmethod
    def transform_response(self, raw_response: Dict) -> List[JobListing]:
        """Transform API-specific response to standardized JobListing format"""

    async def _make_request(
        self, endpoint: str, params: Dict = None, headers: Dict = None
    ) -> Dict:
        """Make HTTP request with error handling and rate limit tracking"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        self._request_count += 1
        start_time = time.time()

        try:
            full_url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

            async with self.session.get(
                full_url, params=params, headers=headers
            ) as response:
                response_time = int((time.time() - start_time) * 1000)

                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "response_time_ms": response_time,
                        "status_code": response.status,
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": error_text,
                        "response_time_ms": response_time,
                        "status_code": response.status,
                    }

        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": response_time,
                "status_code": 0,
            }

    def get_usage_stats(self) -> Dict:
        """Get client usage statistics"""
        elapsed_time = time.time() - self._start_time
        return {
            "requests_made": self._request_count,
            "elapsed_time_seconds": elapsed_time,
            "requests_per_minute": (
                (self._request_count / elapsed_time) * 60 if elapsed_time > 0 else 0
            ),
        }

    async def test_connection(
        self, test_query: str = "software engineer"
    ) -> APITestResult:
        """Test API connection and basic functionality"""
        start_time = time.time()

        try:
            # Test authentication
            auth_success = await self.authenticate()
            if not auth_success:
                return APITestResult(
                    provider=self.get_provider_type(),
                    success=False,
                    response_time_ms=int((time.time() - start_time) * 1000),
                    jobs_returned=0,
                    error_message="Authentication failed",
                )

            # Test job search
            test_query_obj = JobSearchQuery(
                query=test_query, location="New York, NY", page=1, num_pages=1
            )

            jobs = await self.search_jobs(test_query_obj)
            response_time = int((time.time() - start_time) * 1000)

            return APITestResult(
                provider=self.get_provider_type(),
                success=True,
                response_time_ms=response_time,
                jobs_returned=len(jobs),
                sample_job=jobs[0] if jobs else None,
                rate_limit_info=self.get_rate_limits(),
            )

        except Exception as e:
            return APITestResult(
                provider=self.get_provider_type(),
                success=False,
                response_time_ms=int((time.time() - start_time) * 1000),
                jobs_returned=0,
                error_message=str(e),
            )

    @abstractmethod
    def get_provider_type(self) -> JobSearchProvider:
        """Return the provider type for this client"""


# Utility functions for testing and analysis


def save_response_sample(
    provider: str, endpoint: str, response: Dict, query_params: Dict = None
):
    """Save API response sample for analysis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"api_research/responses/{provider}_{endpoint}_{timestamp}.json"

    sample_data = {
        "provider": provider,
        "endpoint": endpoint,
        "query_params": query_params,
        "timestamp": timestamp,
        "response": response,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)

    return filename


def load_response_sample(filename: str) -> Dict:
    """Load saved API response sample"""
    with open(filename, encoding="utf-8") as f:
        return json.load(f)
