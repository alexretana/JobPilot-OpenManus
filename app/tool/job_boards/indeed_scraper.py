#!/usr/bin/env python3
"""
Indeed Jobs Scraper for JobPilot-OpenManus
Implements job data acquisition from Indeed.com using ethical web scraping practices.
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup

from app.logger import logger

from .base_scraper import JobBoardScraper, JobSearchQuery, RawJobData, clean_text


class IndeedScraper(JobBoardScraper):
    """Indeed Jobs scraper with ethical rate limiting and error handling"""

    def __init__(self):
        source_config = {
            "name": "indeed",
            "display_name": "Indeed Jobs",
            "base_url": "https://www.indeed.com",
            "api_available": False,  # Indeed has limited public API access
            "rate_limit_config": {
                "requests_per_minute": 20,  # Conservative rate limiting
                "requests_per_hour": 300,
                "concurrent_requests": 2,
                "backoff_multiplier": 1.5,
                "max_backoff": 180,
            },
        }
        super().__init__(source_config)

        # Indeed-specific configuration
        self.search_url = f"{self.base_url}/jobs"
        self.job_detail_base = f"{self.base_url}/viewjob"

        # Update headers for Indeed
        self.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "https://www.indeed.com/",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    async def search_jobs(self, query: JobSearchQuery) -> List[RawJobData]:
        """Search for jobs on Indeed"""
        jobs = []

        try:
            # Build Indeed search URL
            search_params = {
                "q": query.query,
                "l": query.location or "",
                "start": query.offset,
                "limit": min(query.limit, 50),  # Indeed typically shows 50 per page max
            }

            # Add optional filters
            if query.job_type:
                search_params["jt"] = self._map_job_type(query.job_type)

            if query.salary_min:
                search_params["salary"] = f"${query.salary_min}+"

            if query.remote_type == "remote":
                search_params["remotejob"] = "1"

            search_url = f"{self.search_url}?{urlencode(search_params)}"
            logger.info(f"Searching Indeed: {search_url}")

            response = await self.make_request(search_url)
            if not response:
                logger.warning("Failed to get search results from Indeed")
                return jobs

            # Parse search results
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # Find job cards - Indeed uses various selectors
            job_cards = soup.find_all(
                "div",
                {
                    "class": re.compile(
                        r"job_seen_beacon|slider_container|jobsearch-SerpJobCard"
                    )
                },
            )

            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all("a", {"data-jk": True})
                if job_cards:
                    logger.info(
                        f"Found {len(job_cards)} job cards using alternative selector"
                    )
                else:
                    logger.warning("No job cards found on Indeed search page")
                    return jobs

            logger.info(f"Found {len(job_cards)} job cards on Indeed")

            for card in job_cards:
                try:
                    job_data = await self._parse_job_card(card, search_url)
                    if job_data:
                        jobs.append(job_data)
                        self.stats["jobs_scraped"] += 1

                        # Respect rate limits between job detail fetches
                        if len(jobs) < len(job_cards):
                            await asyncio.sleep(1)

                except Exception as e:
                    logger.warning(f"Failed to parse job card: {e}")
                    continue

            self.stats["last_scrape_time"] = datetime.now().isoformat()
            logger.info(f"Successfully scraped {len(jobs)} jobs from Indeed")

        except Exception as e:
            logger.error(f"Error during Indeed job search: {e}")
            self.stats["errors"].append(f"Search error: {e}")

        return jobs

    async def get_job_details(self, job_url: str) -> Optional[RawJobData]:
        """Fetch detailed job information from Indeed job URL"""
        try:
            response = await self.make_request(job_url)
            if not response:
                return None

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            return await self._parse_job_detail_page(soup, job_url)

        except Exception as e:
            logger.error(f"Error fetching job details from {job_url}: {e}")
            return None

    async def parse_job_data(
        self, raw_data: Dict[str, Any], source_url: str
    ) -> RawJobData:
        """Parse Indeed-specific raw job data into standardized format"""
        return RawJobData(
            source_id=self.name,
            source_job_id=raw_data.get("job_id", ""),
            source_url=raw_data.get("url", source_url),
            title=clean_text(raw_data.get("title", "")),
            company=clean_text(raw_data.get("company", "")),
            location=clean_text(raw_data.get("location", "")),
            description=clean_text(raw_data.get("description", "")),
            raw_data=raw_data,
            scraped_at=datetime.now(),
            salary_info=raw_data.get("salary"),
            job_type=raw_data.get("job_type"),
            posted_date=raw_data.get("posted_date"),
            requirements=raw_data.get("requirements"),
            benefits=raw_data.get("benefits"),
            company_url=raw_data.get("company_url"),
        )

    async def _parse_job_card(self, card, base_url: str) -> Optional[RawJobData]:
        """Parse a job card from Indeed search results"""
        try:
            # Extract job ID and URL
            job_link = card.find("a", {"data-jk": True}) or card.find(
                "h2", {"class": re.compile(r"jobTitle")}
            ).find("a")
            if not job_link:
                return None

            job_id = (
                job_link.get("data-jk")
                or job_link.get("href", "").split("jk=")[-1].split("&")[0]
            )
            job_url = urljoin(self.base_url, job_link.get("href", ""))

            # Extract basic job info
            title_elem = card.find(
                "h2", {"class": re.compile(r"jobTitle")}
            ) or card.find("a", {"data-jk": True})
            title = clean_text(title_elem.get_text()) if title_elem else "Unknown Title"

            company_elem = card.find(
                "span", {"class": re.compile(r"companyName")}
            ) or card.find("a", {"data-tn-element": "companyName"})
            company = (
                clean_text(company_elem.get_text())
                if company_elem
                else "Unknown Company"
            )

            location_elem = card.find(
                "div", {"class": re.compile(r"companyLocation")}
            ) or card.find("span", {"class": re.compile(r"location")})
            location = (
                clean_text(location_elem.get_text())
                if location_elem
                else "Unknown Location"
            )

            # Extract salary if available
            salary_elem = card.find("span", {"class": re.compile(r"salary|estimated")})
            salary_info = clean_text(salary_elem.get_text()) if salary_elem else None

            # Extract job snippet/description
            snippet_elem = card.find(
                "div", {"class": re.compile(r"job-snippet|summary")}
            )
            description = clean_text(snippet_elem.get_text()) if snippet_elem else ""

            # Extract posting date
            posted_elem = card.find("span", {"class": re.compile(r"date|posted")})
            posted_text = clean_text(posted_elem.get_text()) if posted_elem else None
            posted_date = self._parse_posted_date(posted_text) if posted_text else None

            raw_data = {
                "job_id": job_id,
                "url": job_url,
                "title": title,
                "company": company,
                "location": location,
                "salary": salary_info,
                "description": description,
                "posted_date": posted_date,
                "source_html": str(card),
            }

            return await self.parse_job_data(raw_data, base_url)

        except Exception as e:
            logger.warning(f"Error parsing job card: {e}")
            return None

    async def _parse_job_detail_page(
        self, soup: BeautifulSoup, job_url: str
    ) -> Optional[RawJobData]:
        """Parse detailed job information from Indeed job detail page"""
        try:
            # Extract job ID from URL
            job_id = job_url.split("jk=")[-1].split("&")[0]

            # Extract detailed job info
            title_elem = soup.find("h1", {"class": re.compile(r"jobTitle")})
            title = clean_text(title_elem.get_text()) if title_elem else "Unknown Title"

            company_elem = soup.find(
                "div", {"class": re.compile(r"companyName")}
            ) or soup.find("a", {"data-tn-element": "companyName"})
            company = (
                clean_text(company_elem.get_text())
                if company_elem
                else "Unknown Company"
            )

            location_elem = soup.find("div", {"class": re.compile(r"companyLocation")})
            location = (
                clean_text(location_elem.get_text())
                if location_elem
                else "Unknown Location"
            )

            # Full job description
            desc_elem = soup.find(
                "div",
                {
                    "class": re.compile(
                        r"jobDescriptionText|jobsearch-jobDescriptionText"
                    )
                },
            )
            description = clean_text(desc_elem.get_text()) if desc_elem else ""

            # Salary information
            salary_elem = soup.find(
                "span", {"class": re.compile(r"salary|icl-u-xs-mr--xs")}
            )
            salary_info = clean_text(salary_elem.get_text()) if salary_elem else None

            # Job type (full-time, part-time, etc.)
            job_type_elem = soup.find(
                "div", {"class": re.compile(r"jobType|attribute")}
            )
            job_type = clean_text(job_type_elem.get_text()) if job_type_elem else None

            # Company URL
            company_link = soup.find("a", {"data-tn-element": "companyName"})
            company_url = (
                urljoin(self.base_url, company_link.get("href", ""))
                if company_link
                else None
            )

            raw_data = {
                "job_id": job_id,
                "url": job_url,
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "salary": salary_info,
                "job_type": job_type,
                "company_url": company_url,
                "full_detail": True,
            }

            return await self.parse_job_data(raw_data, job_url)

        except Exception as e:
            logger.error(f"Error parsing job detail page: {e}")
            return None

    def _map_job_type(self, job_type: str) -> str:
        """Map standard job types to Indeed's format"""
        type_mapping = {
            "full-time": "fulltime",
            "part-time": "parttime",
            "contract": "contract",
            "temporary": "temporary",
            "internship": "internship",
        }
        return type_mapping.get(job_type.lower(), job_type)

    def _parse_posted_date(self, posted_text: str) -> Optional[datetime]:
        """Parse Indeed's posted date formats"""
        if not posted_text:
            return None

        posted_text = posted_text.lower().strip()
        now = datetime.now()

        try:
            if "today" in posted_text:
                return now
            elif "yesterday" in posted_text:
                return now - timedelta(days=1)
            elif "day" in posted_text:
                # "2 days ago", "1 day ago"
                days = int(re.search(r"(\d+)", posted_text).group(1))
                return now - timedelta(days=days)
            elif "week" in posted_text:
                # "1 week ago", "2 weeks ago"
                weeks = int(re.search(r"(\d+)", posted_text).group(1))
                return now - timedelta(weeks=weeks)
            elif "month" in posted_text:
                # "1 month ago", "2 months ago"
                months = int(re.search(r"(\d+)", posted_text).group(1))
                return now - timedelta(days=months * 30)  # Approximate
            else:
                return None
        except (ValueError, AttributeError):
            return None


# Factory function for easy instantiation
def create_indeed_scraper() -> IndeedScraper:
    """Create and return an Indeed scraper instance"""
    return IndeedScraper()
