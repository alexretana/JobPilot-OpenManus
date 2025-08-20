"""
Company Matching and Normalization Utilities

This module provides utilities for normalizing company names and matching
companies across different data sources to prevent duplicates.
"""

import re
from difflib import SequenceMatcher
from typing import List, Optional, Tuple
from urllib.parse import urlparse


def normalize_company_name(name: str) -> str:
    """
    Normalize company name for matching by removing common suffixes and standardizing format.

    Args:
        name: Raw company name

    Returns:
        Normalized lowercase company name without common suffixes

    Examples:
        >>> normalize_company_name("Google Inc.")
        "google"
        >>> normalize_company_name("Microsoft Corporation")
        "microsoft"
        >>> normalize_company_name("Acme Co., Ltd.")
        "acme"
    """
    if not name:
        return ""

    # First, normalize ampersands to 'and'
    name = re.sub(r"\s*&\s*", " and ", name)

    # Remove common company suffixes/prefixes (case insensitive)
    # Be careful with order - more specific patterns first
    suffixes_patterns = [
        r"\b(and Co|& Co)\b\.?",  # Handle "& Co" first
        r"\b(Inc|LLC|Corp|Corporation|Ltd|Limited|Company|Group|Holdings|Enterprises|Technologies|Systems|Services|International|Intl|LLP|LP|PLC|SA|AG|GmbH|Pty|Pvt)\b\.?",
        r"\bCo\b\.?$",  # Only remove "Co" at the end to avoid removing from "Tech Solutions Co"
    ]

    for pattern in suffixes_patterns:
        name = re.sub(pattern, "", name, flags=re.IGNORECASE)

    # Remove common punctuation and special characters (but keep spaces for words)
    name = re.sub(r"[,\.\-_\(\)\[\]{}]", " ", name)

    # Remove extra whitespace and convert to lowercase
    normalized = " ".join(name.split()).lower().strip()

    return normalized


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from company website URL.

    Args:
        url: Company website URL

    Returns:
        Domain name without www. prefix, or None if invalid URL

    Examples:
        >>> extract_domain_from_url("https://www.google.com")
        "google.com"
        >>> extract_domain_from_url("http://microsoft.com/about")
        "microsoft.com"
        >>> extract_domain_from_url("invalid-url")
        None
    """
    if not url:
        return None

    try:
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]

        # Validate domain format (basic check)
        if "." not in domain or len(domain) < 3:
            return None

        return domain

    except Exception:
        return None


def find_existing_company_by_name(
    session, name: str, similarity_threshold: float = 0.85
) -> Optional[str]:
    """
    Find existing company ID by fuzzy name matching.

    Args:
        session: SQLAlchemy session
        name: Company name to search for
        similarity_threshold: Minimum similarity score (0.0-1.0) to consider a match

    Returns:
        Company ID if match found, None otherwise
    """
    from .models import CompanyInfoDB

    normalized_search = normalize_company_name(name)

    # First try exact normalized match (fastest)
    exact_match = (
        session.query(CompanyInfoDB)
        .filter(CompanyInfoDB.normalized_name == normalized_search)
        .first()
    )

    if exact_match:
        return exact_match.id

    # If no exact match, try fuzzy matching
    all_companies = session.query(CompanyInfoDB.id, CompanyInfoDB.normalized_name).all()

    best_match = None
    best_score = 0.0

    for company_id, company_normalized_name in all_companies:
        if not company_normalized_name:
            continue

        score = similarity_score(normalized_search, company_normalized_name)

        if score > best_score and score >= similarity_threshold:
            best_score = score
            best_match = company_id

    return best_match


def find_existing_company_by_domain(session, domain: str) -> Optional[str]:
    """
    Find existing company by domain name.

    Args:
        session: SQLAlchemy session
        domain: Domain to search for

    Returns:
        Company ID if found, None otherwise
    """
    from .models import CompanyInfoDB

    if not domain:
        return None

    company = (
        session.query(CompanyInfoDB)
        .filter(CompanyInfoDB.domain == domain.lower())
        .first()
    )

    return company.id if company else None


def find_existing_company(session, name: str, domain: str = None) -> Optional[str]:
    """
    Find existing company ID by name and/or domain matching.

    This function tries multiple matching strategies:
    1. Exact domain match (if domain provided)
    2. Fuzzy name matching with high similarity threshold
    3. Combined name + domain validation

    Args:
        session: SQLAlchemy session
        name: Company name
        domain: Company domain (optional)

    Returns:
        Company ID if match found, None otherwise
    """
    # Try domain match first (most reliable)
    if domain:
        domain_match = find_existing_company_by_domain(session, domain)
        if domain_match:
            return domain_match

    # Try name matching
    name_match = find_existing_company_by_name(session, name)

    # If we have both name match and domain, validate they belong to same company
    if name_match and domain:
        from .models import CompanyInfoDB

        matched_company = (
            session.query(CompanyInfoDB).filter(CompanyInfoDB.id == name_match).first()
        )

        if matched_company and matched_company.domain:
            # If matched company has a different domain, this might be a different company
            if matched_company.domain.lower() != domain.lower():
                return None

    return name_match


def similarity_score(str1: str, str2: str) -> float:
    """
    Calculate similarity between two strings using sequence matching.

    Args:
        str1: First string
        str2: Second string

    Returns:
        Similarity score between 0.0 (no match) and 1.0 (identical)

    Examples:
        >>> similarity_score("google", "google")
        1.0
        >>> similarity_score("google", "googl")
        0.91...
        >>> similarity_score("apple", "microsoft")
        0.0
    """
    if not str1 or not str2:
        return 0.0

    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def suggest_company_matches(
    session, name: str, limit: int = 5
) -> List[Tuple[str, str, float]]:
    """
    Get a list of potential company matches with similarity scores.

    Args:
        session: SQLAlchemy session
        name: Company name to find matches for
        limit: Maximum number of suggestions to return

    Returns:
        List of tuples (company_id, company_name, similarity_score) ordered by score
    """
    from .models import CompanyInfoDB

    normalized_search = normalize_company_name(name)
    all_companies = session.query(
        CompanyInfoDB.id, CompanyInfoDB.name, CompanyInfoDB.normalized_name
    ).all()

    matches = []

    for company_id, company_name, normalized_name in all_companies:
        if not normalized_name:
            continue

        score = similarity_score(normalized_search, normalized_name)

        if score > 0.3:  # Only include reasonable matches
            matches.append((company_id, company_name, score))

    # Sort by similarity score (descending) and limit results
    matches.sort(key=lambda x: x[2], reverse=True)
    return matches[:limit]


def validate_company_data(
    name: str, domain: str = None, website: str = None
) -> Tuple[str, Optional[str], List[str]]:
    """
    Validate and normalize company data before database insertion.

    Args:
        name: Company name
        domain: Company domain (optional)
        website: Company website (optional)

    Returns:
        Tuple of (normalized_name, validated_domain, validation_errors)
    """
    errors = []

    # Validate name
    if not name or not name.strip():
        errors.append("Company name is required")
        return "", None, errors

    if len(name.strip()) > 200:
        errors.append("Company name must be 200 characters or less")

    normalized_name = normalize_company_name(name)
    if not normalized_name:
        errors.append("Company name contains no valid characters after normalization")

    # Validate domain/website
    validated_domain = None
    if website:
        validated_domain = extract_domain_from_url(website)
        if not validated_domain:
            errors.append("Invalid website URL format")
    elif domain:
        validated_domain = domain.lower().strip()
        # Basic domain validation
        if not re.match(
            r"^[a-z0-9][a-z0-9\-]*[a-z0-9]*\.([a-z]{2,}|[a-z]{2,}\.[a-z]{2,})$",
            validated_domain,
        ):
            errors.append("Invalid domain format")

    return normalized_name, validated_domain, errors


def get_company_size_category_from_string(size_string: str) -> Optional[str]:
    """
    Convert size string to CompanySizeCategory enum value.

    Args:
        size_string: Size description like "1-50 employees" or "Medium (201-1000)"

    Returns:
        CompanySizeCategory enum value or None
    """
    if not size_string:
        return None

    # Extract numbers from size string
    numbers = re.findall(r"\d+", size_string.replace(",", ""))

    # Check for "+" indicating "or more"
    has_plus = "+" in size_string

    if not numbers:
        # Try to match keywords
        size_lower = size_string.lower()
        if any(
            word in size_lower for word in ["startup", "small startup", "early stage"]
        ):
            return "startup"
        elif any(word in size_lower for word in ["small", "boutique"]):
            return "small"
        elif any(word in size_lower for word in ["medium", "mid-size", "mid size"]):
            return "medium"
        elif any(word in size_lower for word in ["large", "big"]):
            return "large"
        elif any(
            word in size_lower for word in ["enterprise", "fortune", "multinational"]
        ):
            return "enterprise"
        return None

    # Use the largest number found as the employee count
    max_employees = max(int(num) for num in numbers)

    # If it has "+" and is 5000+, it's enterprise
    if has_plus and max_employees >= 5000:
        return "enterprise"

    if max_employees <= 50:
        return "startup"
    elif max_employees <= 200:
        return "small"
    elif max_employees <= 1000:
        return "medium"
    elif max_employees <= 5000:
        return "large"
    else:
        return "enterprise"
