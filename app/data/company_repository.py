"""
CompanyRepository for JobPilot
Repository pattern implementation for company data management.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.exc import IntegrityError

from app.data.models import (
    CompanyInfo,
    CompanyInfoDB,
    CompanySizeCategory,
    pydantic_to_sqlalchemy,
    sqlalchemy_to_pydantic,
)
from app.logger import logger
from app.utils.retry import retry_db_write


class CompanyRepository:
    """Repository for company information operations."""

    def __init__(self, db_manager):
        """Initialize company repository."""
        self.db_manager = db_manager

    @retry_db_write()
    def create_company(self, company_data: CompanyInfo) -> CompanyInfo:
        """Create a new company."""
        try:
            # Validate company name
            if not company_data.name or len(company_data.name.strip()) == 0:
                raise ValueError("Company name cannot be empty")

            with self.db_manager.get_session() as session:
                company_db = pydantic_to_sqlalchemy(company_data, CompanyInfoDB)

                # Add normalized name for matching
                company_db.normalized_name = self._normalize_company_name(
                    company_data.name
                )

                # Extract domain from website if provided
                if company_data.website:
                    company_db.domain = self._extract_domain_from_url(
                        company_data.website
                    )

                session.add(company_db)
                session.flush()  # Get the ID

                result = sqlalchemy_to_pydantic(company_db, CompanyInfo)
                logger.info(f"Created company: {result.name} (ID: {result.id})")
                return result

        except IntegrityError as e:
            if "unique_company_identity" in str(e):
                logger.error(
                    f"Company with similar name and domain already exists: {company_data.name}"
                )
                raise ValueError(
                    f"Company '{company_data.name}' already exists with this domain"
                )
            else:
                logger.error(f"Database integrity error creating company: {e}")
                raise
        except Exception as e:
            logger.error(f"Error creating company: {e}")
            raise

    def get_company(self, company_id: str) -> Optional[CompanyInfo]:
        """Get company by ID."""
        try:
            with self.db_manager.get_session() as session:
                company_db = (
                    session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.id == company_id)
                    .first()
                )
                if company_db:
                    return sqlalchemy_to_pydantic(company_db, CompanyInfo)
                return None
        except Exception as e:
            logger.error(f"Error getting company {company_id}: {e}")
            return None

    @retry_db_write()
    def update_company(
        self, company_id: str, update_data: Dict[str, Any]
    ) -> Optional[CompanyInfo]:
        """Update company information."""
        try:
            with self.db_manager.get_session() as session:
                company_db = (
                    session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.id == company_id)
                    .first()
                )
                if not company_db:
                    return None

                # Update fields
                for field, value in update_data.items():
                    if hasattr(company_db, field):
                        setattr(company_db, field, value)

                # Update normalized name if name changed
                if "name" in update_data:
                    if not update_data["name"] or len(update_data["name"].strip()) == 0:
                        raise ValueError("Company name cannot be empty")
                    company_db.normalized_name = self._normalize_company_name(
                        update_data["name"]
                    )

                # Update domain if website changed
                if "website" in update_data and update_data["website"]:
                    company_db.domain = self._extract_domain_from_url(
                        update_data["website"]
                    )

                company_db.updated_at = datetime.utcnow()
                session.flush()

                result = sqlalchemy_to_pydantic(company_db, CompanyInfo)
                logger.info(f"Updated company: {company_id}")
                return result

        except Exception as e:
            logger.error(f"Error updating company {company_id}: {e}")
            raise

    def delete_company(self, company_id: str) -> bool:
        """Delete company."""
        try:
            with self.db_manager.get_session() as session:
                company_db = (
                    session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.id == company_id)
                    .first()
                )
                if company_db:
                    session.delete(company_db)
                    logger.info(f"Deleted company: {company_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting company {company_id}: {e}")
            return False

    def search_companies(
        self,
        query: Optional[str] = None,
        industries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        size_categories: Optional[List[CompanySizeCategory]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[CompanyInfo], int]:
        """Search companies with filters."""
        try:
            with self.db_manager.get_session() as session:
                query_obj = session.query(CompanyInfoDB)

                # Text search across name, industry, and description
                if query:
                    search_filter = or_(
                        CompanyInfoDB.name.ilike(f"%{query}%"),
                        CompanyInfoDB.normalized_name.ilike(f"%{query}%"),
                        CompanyInfoDB.industry.ilike(f"%{query}%"),
                        CompanyInfoDB.description.ilike(f"%{query}%"),
                    )
                    query_obj = query_obj.filter(search_filter)

                # Filter by industries
                if industries:
                    query_obj = query_obj.filter(CompanyInfoDB.industry.in_(industries))

                # Filter by locations
                if locations:
                    location_filters = [
                        CompanyInfoDB.location.ilike(f"%{loc}%") for loc in locations
                    ]
                    query_obj = query_obj.filter(or_(*location_filters))

                # Filter by size categories
                if size_categories:
                    query_obj = query_obj.filter(
                        CompanyInfoDB.size_category.in_(size_categories)
                    )

                # Get total count
                total_count = query_obj.count()

                # Apply pagination and ordering
                companies_db = (
                    query_obj.order_by(desc(CompanyInfoDB.created_at))
                    .offset(offset)
                    .limit(limit)
                    .all()
                )

                # Convert to Pydantic models
                companies = [
                    sqlalchemy_to_pydantic(company_db, CompanyInfo)
                    for company_db in companies_db
                ]

                logger.info(
                    f"Search returned {len(companies)} companies out of {total_count} total"
                )
                return companies, total_count

        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return [], 0

    def get_companies_by_industry(
        self, industry: str, limit: int = 50
    ) -> List[CompanyInfo]:
        """Get companies in a specific industry."""
        try:
            with self.db_manager.get_session() as session:
                companies_db = (
                    session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.industry.ilike(f"%{industry}%"))
                    .order_by(desc(CompanyInfoDB.created_at))
                    .limit(limit)
                    .all()
                )

                companies = [
                    sqlalchemy_to_pydantic(company_db, CompanyInfo)
                    for company_db in companies_db
                ]
                logger.info(
                    f"Retrieved {len(companies)} companies in {industry} industry"
                )
                return companies

        except Exception as e:
            logger.error(f"Error getting companies for industry {industry}: {e}")
            return []

    def get_company_by_domain(self, domain: str) -> Optional[CompanyInfo]:
        """Get company by domain."""
        try:
            # Normalize domain (remove www, protocol, etc.)
            normalized_domain = self._normalize_domain(domain)

            with self.db_manager.get_session() as session:
                company_db = (
                    session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.domain.ilike(f"%{normalized_domain}%"))
                    .first()
                )
                if company_db:
                    return sqlalchemy_to_pydantic(company_db, CompanyInfo)
                return None
        except Exception as e:
            logger.error(f"Error getting company by domain {domain}: {e}")
            return None

    def get_company_statistics(self) -> Dict[str, Any]:
        """Get company statistics and analytics."""
        try:
            with self.db_manager.get_session() as session:
                # Total companies
                total_companies = session.query(CompanyInfoDB).count()

                # Companies by industry
                industry_stats = (
                    session.query(
                        CompanyInfoDB.industry,
                        func.count(CompanyInfoDB.id).label("count"),
                    )
                    .filter(CompanyInfoDB.industry.isnot(None))
                    .group_by(CompanyInfoDB.industry)
                    .all()
                )

                # Companies by size category
                size_stats = (
                    session.query(
                        CompanyInfoDB.size_category,
                        func.count(CompanyInfoDB.id).label("count"),
                    )
                    .filter(CompanyInfoDB.size_category.isnot(None))
                    .group_by(CompanyInfoDB.size_category)
                    .all()
                )

                stats = {
                    "total_companies": total_companies,
                    "by_industry": {
                        industry: count
                        for industry, count in industry_stats
                        if industry
                    },
                    "by_size_category": {
                        size_cat.value if size_cat else "Unknown": count
                        for size_cat, count in size_stats
                    },
                    "companies_with_website": session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.website.isnot(None))
                    .count(),
                    "companies_with_description": session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.description.isnot(None))
                    .count(),
                }

                logger.info(
                    f"Generated company statistics: {total_companies} total companies"
                )
                return stats

        except Exception as e:
            logger.error(f"Error getting company statistics: {e}")
            return {"error": str(e)}

    def find_similar_companies(
        self, company_id: str, limit: int = 5
    ) -> List[CompanyInfo]:
        """Find companies similar to the given company."""
        try:
            with self.db_manager.get_session() as session:
                # Get the target company
                target_company = (
                    session.query(CompanyInfoDB)
                    .filter(CompanyInfoDB.id == company_id)
                    .first()
                )

                if not target_company:
                    return []

                # Find similar companies based on industry and location
                similar_query = session.query(CompanyInfoDB).filter(
                    CompanyInfoDB.id != company_id
                )  # Exclude the target company

                # Prioritize by industry match
                if target_company.industry:
                    similar_query = similar_query.filter(
                        CompanyInfoDB.industry.ilike(f"%{target_company.industry}%")
                    )

                # Then by location similarity if available
                if target_company.location:
                    similar_query = similar_query.filter(
                        CompanyInfoDB.location.ilike(f"%{target_company.location}%")
                    )

                similar_companies_db = similar_query.limit(limit).all()

                # If we don't have enough matches, get more based on just industry
                if len(similar_companies_db) < limit and target_company.industry:
                    additional_query = (
                        session.query(CompanyInfoDB)
                        .filter(
                            and_(
                                CompanyInfoDB.id != company_id,
                                CompanyInfoDB.industry.ilike(
                                    f"%{target_company.industry}%"
                                ),
                            )
                        )
                        .limit(limit - len(similar_companies_db))
                    )

                    # Exclude already found companies
                    existing_ids = [comp.id for comp in similar_companies_db]
                    if existing_ids:
                        additional_query = additional_query.filter(
                            ~CompanyInfoDB.id.in_(existing_ids)
                        )

                    additional_companies = additional_query.all()
                    similar_companies_db.extend(additional_companies)

                similar_companies = [
                    sqlalchemy_to_pydantic(company_db, CompanyInfo)
                    for company_db in similar_companies_db
                ]

                logger.info(
                    f"Found {len(similar_companies)} similar companies to {company_id}"
                )
                return similar_companies

        except Exception as e:
            logger.error(f"Error finding similar companies to {company_id}: {e}")
            return []

    @retry_db_write(max_retries=2, base_delay=1.5)
    def bulk_create_companies(self, companies_data: List[CompanyInfo]) -> int:
        """Create multiple companies efficiently."""
        try:
            with self.db_manager.get_session() as session:
                companies_db = []
                for company_data in companies_data:
                    # Validate company name
                    if not company_data.name or len(company_data.name.strip()) == 0:
                        logger.warning("Skipping company with empty name")
                        continue

                    company_db = pydantic_to_sqlalchemy(company_data, CompanyInfoDB)

                    # Add normalized name for matching
                    company_db.normalized_name = self._normalize_company_name(
                        company_data.name
                    )

                    # Extract domain from website if provided
                    if company_data.website:
                        company_db.domain = self._extract_domain_from_url(
                            company_data.website
                        )

                    companies_db.append(company_db)

                session.add_all(companies_db)
                session.flush()

                count = len(companies_db)
                logger.info(f"Bulk created {count} companies")
                return count

        except Exception as e:
            logger.error(f"Error bulk creating companies: {e}")
            raise

    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for matching."""
        if not name:
            return ""

        # Convert to lowercase and remove common suffixes/prefixes
        normalized = name.lower().strip()

        # Remove common company suffixes
        suffixes = [
            "inc",
            "inc.",
            "corp",
            "corp.",
            "corporation",
            "company",
            "co",
            "co.",
            "llc",
            "llc.",
            "ltd",
            "ltd.",
            "limited",
            "plc",
            "plc.",
            "gmbh",
            "ag",
            "sa",
            "bv",
            "nv",
        ]

        # Remove suffixes
        for suffix in suffixes:
            if normalized.endswith(" " + suffix):
                normalized = normalized[: -len(" " + suffix)].strip()

        # Remove special characters and extra spaces
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def _extract_domain_from_url(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        if not url:
            return None

        try:
            # Remove protocol
            url = re.sub(r"^https?://", "", url.lower())
            # Remove www
            url = re.sub(r"^www\.", "", url)
            # Extract domain (everything before first slash or query)
            domain = url.split("/")[0].split("?")[0].split("#")[0]

            # Basic validation
            if "." in domain and len(domain) > 3:
                return domain
            return None
        except Exception:
            return None

    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain for matching."""
        if not domain:
            return ""

        # Remove protocol and www
        normalized = domain.lower().strip()
        normalized = re.sub(r"^https?://", "", normalized)
        normalized = re.sub(r"^www\.", "", normalized)

        # Remove trailing path/query/fragment
        normalized = normalized.split("/")[0].split("?")[0].split("#")[0]

        return normalized
