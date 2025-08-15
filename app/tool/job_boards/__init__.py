#!/usr/bin/env python3
"""
Job Board Scrapers Package for JobPilot-OpenManus
Provides ethical job data acquisition from various job boards and platforms.
"""

from .base_scraper import JobBoardScraper, JobSearchQuery, RateLimiter, RawJobData
from .indeed_scraper import IndeedScraper, create_indeed_scraper


__all__ = [
    "JobBoardScraper",
    "JobSearchQuery",
    "RawJobData",
    "RateLimiter",
    "IndeedScraper",
    "create_indeed_scraper",
]

# Registry of available scrapers
AVAILABLE_SCRAPERS = {
    "indeed": create_indeed_scraper,
    # Future scrapers will be added here:
    # 'linkedin': create_linkedin_scraper,
    # 'glassdoor': create_glassdoor_scraper,
    # 'dice': create_dice_scraper,
}


def get_scraper(name: str) -> JobBoardScraper:
    """Get a scraper instance by name"""
    if name not in AVAILABLE_SCRAPERS:
        raise ValueError(
            f"Unknown scraper: {name}. Available: {list(AVAILABLE_SCRAPERS.keys())}"
        )

    return AVAILABLE_SCRAPERS[name]()


def list_scrapers():
    """List all available scraper names"""
    return list(AVAILABLE_SCRAPERS.keys())
