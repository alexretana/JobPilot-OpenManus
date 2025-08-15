#!/usr/bin/env python3
"""
Base Job Board Scraper for JobPilot-OpenManus
Abstract base class for all job board scrapers providing common functionality
for rate limiting, session management, and data standardization.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

from app.logger import logger


@dataclass
class JobSearchQuery:
    """Standardized job search parameters across all platforms"""

    query: str
    location: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, etc.
    experience_level: Optional[str] = None  # entry, mid, senior, etc.
    remote_type: Optional[str] = None  # remote, hybrid, on-site
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    limit: int = 50
    offset: int = 0


@dataclass
class RawJobData:
    """Raw job data before standardization"""

    source_id: str
    source_job_id: str
    source_url: str
    title: str
    company: str
    location: str
    description: str
    raw_data: Dict[str, Any]  # Platform-specific raw data
    scraped_at: datetime

    # Optional fields that might be available
    salary_info: Optional[str] = None
    job_type: Optional[str] = None
    posted_date: Optional[datetime] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    company_url: Optional[str] = None


class RateLimiter:
    """Simple rate limiting for API and scraping requests"""

    def __init__(self, config: Dict[str, Any]):
        self.requests_per_minute = config.get("requests_per_minute", 30)
        self.requests_per_hour = config.get("requests_per_hour", 1000)
        self.concurrent_requests = config.get("concurrent_requests", 3)
        self.backoff_multiplier = config.get("backoff_multiplier", 2.0)
        self.max_backoff = config.get("max_backoff", 300)

        # Tracking
        self.minute_requests = []
        self.hour_requests = []
        self.current_concurrent = 0
        self.current_backoff = 1.0

    async def wait_if_needed(self):
        """Wait if rate limits would be exceeded"""
        now = datetime.now()

        # Clean old requests
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        self.minute_requests = [t for t in self.minute_requests if t > minute_ago]
        self.hour_requests = [t for t in self.hour_requests if t > hour_ago]

        # Check rate limits
        if len(self.minute_requests) >= self.requests_per_minute:
            wait_time = 61  # Wait just over a minute
            logger.info(f"Rate limit hit (minute), waiting {wait_time}s")
            await asyncio.sleep(wait_time)

        if len(self.hour_requests) >= self.requests_per_hour:
            wait_time = 3660  # Wait just over an hour
            logger.info(f"Rate limit hit (hour), waiting {wait_time}s")
            await asyncio.sleep(wait_time)

        # Check concurrent requests
        while self.current_concurrent >= self.concurrent_requests:
            await asyncio.sleep(0.1)

        # Apply backoff if needed
        if self.current_backoff > 1.0:
            wait_time = min(self.current_backoff, self.max_backoff)
            logger.info(f"Applying backoff: waiting {wait_time}s")
            await asyncio.sleep(wait_time)

    async def mark_request_start(self):
        """Mark the start of a request"""
        await self.wait_if_needed()

        now = datetime.now()
        self.minute_requests.append(now)
        self.hour_requests.append(now)
        self.current_concurrent += 1

    async def mark_request_end(self, success: bool = True):
        """Mark the end of a request"""
        self.current_concurrent = max(0, self.current_concurrent - 1)

        if success:
            # Reset backoff on success
            self.current_backoff = 1.0
        else:
            # Increase backoff on failure
            self.current_backoff = min(
                self.current_backoff * self.backoff_multiplier, self.max_backoff
            )


class JobBoardScraper(ABC):
    """Abstract base class for all job board scrapers"""

    def __init__(self, source_config: Dict[str, Any]):
        self.name = source_config["name"]
        self.display_name = source_config["display_name"]
        self.base_url = source_config["base_url"]
        self.api_available = source_config.get("api_available", False)

        # Rate limiting
        rate_config = source_config.get("rate_limit_config", {})
        self.rate_limiter = RateLimiter(rate_config)

        # Session configuration
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        # Statistics
        self.stats = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "jobs_scraped": 0,
            "last_scrape_time": None,
            "errors": [],
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()

    async def initialize(self):
        """Initialize the scraper session"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)

        self.session = aiohttp.ClientSession(
            headers=self.headers, connector=connector, timeout=timeout
        )

        logger.info(f"Initialized {self.display_name} scraper")

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            self.session = None

        logger.info(f"Cleaned up {self.display_name} scraper")

    async def make_request(
        self, url: str, method: str = "GET", **kwargs
    ) -> Optional[aiohttp.ClientResponse]:
        """Make a rate-limited HTTP request"""
        if not self.session:
            raise RuntimeError("Scraper not initialized. Use async context manager.")

        await self.rate_limiter.mark_request_start()

        try:
            self.stats["requests_made"] += 1

            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    self.stats["successful_requests"] += 1
                    await self.rate_limiter.mark_request_end(success=True)
                    return response
                else:
                    self.stats["failed_requests"] += 1
                    await self.rate_limiter.mark_request_end(success=False)

                    error = f"HTTP {response.status} for {url}"
                    self.stats["errors"].append(error)
                    logger.warning(error)

                    return None

        except Exception as e:
            self.stats["failed_requests"] += 1
            await self.rate_limiter.mark_request_end(success=False)

            error = f"Request failed for {url}: {e}"
            self.stats["errors"].append(error)
            logger.error(error)

            return None

    @abstractmethod
    async def search_jobs(self, query: JobSearchQuery) -> List[RawJobData]:
        """Search for jobs on this platform"""

    @abstractmethod
    async def get_job_details(self, job_url: str) -> Optional[RawJobData]:
        """Fetch detailed job information from a job URL"""

    @abstractmethod
    async def parse_job_data(
        self, raw_data: Dict[str, Any], source_url: str
    ) -> RawJobData:
        """Parse platform-specific raw job data into standardized format"""

    async def health_check(self) -> Dict[str, Any]:
        """Check if the source is accessible and responsive"""
        try:
            if not self.session:
                await self.initialize()

            start_time = time.time()
            response = await self.make_request(self.base_url)
            response_time = time.time() - start_time

            if response:
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "accessible": True,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response_time,
                    "accessible": False,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Health check failed for {self.display_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "accessible": False,
                "timestamp": datetime.now().isoformat(),
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics"""
        return {
            "scraper_name": self.name,
            "display_name": self.display_name,
            "stats": self.stats.copy(),
            "rate_limits": {
                "requests_per_minute": self.rate_limiter.requests_per_minute,
                "requests_per_hour": self.rate_limiter.requests_per_hour,
                "current_minute_requests": len(self.rate_limiter.minute_requests),
                "current_hour_requests": len(self.rate_limiter.hour_requests),
                "current_concurrent": self.rate_limiter.current_concurrent,
                "current_backoff": self.rate_limiter.current_backoff,
            },
        }

    async def test_scraper(
        self, test_query: Optional[JobSearchQuery] = None
    ) -> Dict[str, Any]:
        """Test the scraper with a simple query"""
        if test_query is None:
            test_query = JobSearchQuery(
                query="software engineer", location="San Francisco", limit=5
            )

        try:
            logger.info(f"Testing {self.display_name} scraper...")

            # Health check
            health = await self.health_check()
            if not health.get("accessible", False):
                return {
                    "status": "failed",
                    "reason": "Health check failed",
                    "health": health,
                }

            # Try to scrape a few jobs
            start_time = time.time()
            jobs = await self.search_jobs(test_query)
            scrape_time = time.time() - start_time

            return {
                "status": "success",
                "jobs_found": len(jobs),
                "scrape_time": scrape_time,
                "health": health,
                "sample_jobs": jobs[:2] if jobs else [],  # First 2 jobs as examples
            }

        except Exception as e:
            logger.error(f"Test failed for {self.display_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "health": await self.health_check(),
            }


# Utility functions for job data processing


def clean_text(text: str) -> str:
    """Clean and normalize text data"""
    if not text:
        return ""

    # Remove extra whitespace
    text = " ".join(text.split())

    # Remove common HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    return text.strip()


def extract_salary_info(salary_text: str) -> Dict[str, Any]:
    """Extract salary information from text"""
    if not salary_text:
        return {}

    import re

    # Common salary patterns
    patterns = {
        "range": r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*[-–—]\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "single": r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "hourly": r"\$(\d{1,3}(?:\.\d{2})?)\s*(?:per\s*hour|/hr|hr)",
        "yearly": r"\$(\d{1,3}(?:,\d{3})*)\s*(?:per\s*year|/year|annually)",
    }

    result = {"raw_text": salary_text}

    # Try to match salary range
    range_match = re.search(patterns["range"], salary_text, re.IGNORECASE)
    if range_match:
        result["min"] = int(range_match.group(1).replace(",", ""))
        result["max"] = int(range_match.group(2).replace(",", ""))
        result["type"] = "range"
        return result

    # Try single salary
    single_match = re.search(patterns["single"], salary_text, re.IGNORECASE)
    if single_match:
        result["amount"] = int(single_match.group(1).replace(",", ""))
        result["type"] = "single"
        return result

    # Check for hourly
    if "hour" in salary_text.lower() or "/hr" in salary_text.lower():
        result["period"] = "hourly"
    elif "year" in salary_text.lower() or "annual" in salary_text.lower():
        result["period"] = "yearly"

    return result
