"""
Job Data Processor
Transforms raw job data from external APIs to JobPilot schema with validation and enrichment.
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4

from app.logger import logger
from app.data.database import get_database_manager
from app.data.models import (
    RawJobCollection, RawJobCollectionDB, JobProcessingLog, JobProcessingLogDB, 
    ProcessedJobData, ProcessedJobDataDB, ETLProcessingStatus, ETLOperationType, 
    JobType, RemoteType, ExperienceLevel, VerificationStatus, CompanySizeCategory, 
    SeniorityLevel, JobListing, pydantic_to_sqlalchemy
)
from .config import ETLConfig


class JobDataProcessor:
    """Processes raw job collection data and transforms it to JobPilot schema."""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.db_manager = get_database_manager()
        
        # Precompiled regex patterns for efficiency
        self.salary_patterns = [
            re.compile(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)', re.IGNORECASE),
            re.compile(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)(?:\s*per\s*year)?', re.IGNORECASE),
            re.compile(r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|thousand)', re.IGNORECASE),
        ]
        
        self.skills_patterns = [
            re.compile(r'\b(?:python|java|javascript|react|angular|vue|node\.?js|django|flask|aws|azure|gcp|docker|kubernetes|sql|postgresql|mysql|mongodb|redis|git|linux|unix|html|css|typescript|go|rust|scala|kotlin|swift|c\+\+|c#|ruby|php|laravel|spring|express|pandas|numpy|tensorflow|pytorch|scikit-learn|spark|hadoop|kafka|elasticsearch|jenkins|terraform|ansible|prometheus|grafana)\b', re.IGNORECASE),
        ]
    
    async def process_collection(self, collection_id: str) -> str:
        """
        Process a raw job collection and create processed job data.
        
        Args:
            collection_id: ID of the raw collection to process
            
        Returns:
            Processing log ID
        """
        # Load raw collection
        raw_collection = await self._load_raw_collection(collection_id)
        if not raw_collection:
            raise ValueError(f"Raw collection {collection_id} not found")
        
        # Start processing log
        processing_log = await self._start_processing_log(collection_id)
        
        try:
            jobs_processed = 0
            jobs_failed = 0
            errors = []
            
            raw_jobs = raw_collection.raw_response.get('data', [])
            
            for job_index, raw_job in enumerate(raw_jobs):
                try:
                    # Transform individual job
                    processed_job = await self._transform_job(raw_job, raw_collection.api_provider)
                    
                    # Generate embeddings
                    embedding_vector = await self._generate_embeddings(processed_job)
                    
                    # Assess data quality
                    quality_score = self._assess_data_quality(processed_job)
                    
                    # Check for duplicates
                    duplicate_of = await self._check_for_duplicates(processed_job)
                    
                    # Store processed data
                    await self._store_processed_job(
                        processing_id=processing_log.id,
                        job_index=job_index,
                        processed_data=processed_job,
                        embedding_vector=embedding_vector,
                        duplicate_of=duplicate_of,
                        quality_score=quality_score
                    )
                    
                    jobs_processed += 1
                    
                except Exception as e:
                    logger.error(f"Error processing job {job_index}: {e}")
                    errors.append({
                        "job_index": job_index,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "raw_data": raw_job
                    })
                    jobs_failed += 1
                    continue
            
            # Update processing status
            status = ETLProcessingStatus.COMPLETED if jobs_failed == 0 else ETLProcessingStatus.PARTIAL
            await self._complete_processing_log(
                processing_log.id,
                status,
                jobs_processed,
                jobs_failed,
                errors
            )
            
            # Update raw collection status
            await self._update_collection_status(collection_id, ETLProcessingStatus.COMPLETED)
            
            logger.info(f"Completed processing collection {collection_id}: {jobs_processed} processed, {jobs_failed} failed")
            
        except Exception as e:
            logger.error(f"Fatal error processing collection {collection_id}: {e}")
            await self._complete_processing_log(
                processing_log.id,
                ETLProcessingStatus.FAILED,
                0,
                0,
                [{"error_type": "fatal", "error_message": str(e)}]
            )
            await self._update_collection_status(collection_id, ETLProcessingStatus.FAILED)
            raise
        
        return processing_log.id
    
    async def _load_raw_collection(self, collection_id: str) -> Optional[RawJobCollection]:
        """Load raw collection from database."""
        try:
            with self.db_manager.get_session() as session:
                collection_db = session.query(RawJobCollectionDB).filter(
                    RawJobCollectionDB.id == collection_id
                ).first()
                
                if not collection_db:
                    return None
                
                return RawJobCollection(
                    id=collection_db.id,
                    timestamp=collection_db.timestamp,
                    api_provider=collection_db.api_provider,
                    query_params=collection_db.query_params,
                    raw_response=collection_db.raw_response,
                    metadata=collection_db.metadata or {},
                    processing_status=collection_db.processing_status,
                    error_info=collection_db.error_info,
                    created_at=collection_db.created_at
                )
                
        except Exception as e:
            logger.error(f"Error loading raw collection {collection_id}: {e}")
            return None
    
    async def _start_processing_log(self, collection_id: str) -> JobProcessingLog:
        """Start a processing log."""
        processing_log = JobProcessingLog(
            collection_id=collection_id,
            operation_type=ETLOperationType.PROCESSING,
            status=ETLProcessingStatus.PROCESSING
        )
        
        try:
            with self.db_manager.get_session() as session:
                log_db = pydantic_to_sqlalchemy(processing_log, JobProcessingLogDB)
                session.add(log_db)
                session.flush()
                
                processing_log.id = log_db.id
                
        except Exception as e:
            logger.error(f"Error starting processing log: {e}")
            raise
        
        return processing_log
    
    async def _transform_job(self, raw_job: Dict[str, Any], api_provider: str) -> Dict[str, Any]:
        """Transform raw job data to JobPilot schema."""
        if api_provider == "jsearch":
            return await self._transform_jsearch_job(raw_job)
        else:
            raise ValueError(f"Unsupported API provider: {api_provider}")
    
    async def _transform_jsearch_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Transform JSearch job data to JobPilot schema."""
        # Basic fields
        transformed = {
            "title": self._clean_text(raw_job.get("job_title", "")),
            "company": self._clean_text(raw_job.get("employer_name", "")),
            "location": self._normalize_location(raw_job.get("job_city"), raw_job.get("job_state"), raw_job.get("job_country")),
            "description": self._clean_text(raw_job.get("job_description", "")),
            "requirements": self._extract_requirements(raw_job.get("job_description", "")),
            "responsibilities": self._extract_responsibilities(raw_job.get("job_description", "")),
        }
        
        # Job details
        transformed["job_type"] = self._normalize_job_type(raw_job.get("job_employment_type"))
        transformed["remote_type"] = self._determine_remote_type(raw_job.get("job_is_remote"), transformed["location"])
        transformed["experience_level"] = self._determine_experience_level(
            raw_job.get("job_required_experience", {}),
            transformed["description"]
        )
        
        # Salary information
        salary_min, salary_max, currency = self._extract_salary_info(raw_job)
        transformed["salary_min"] = salary_min
        transformed["salary_max"] = salary_max
        transformed["salary_currency"] = currency
        
        # Skills and qualifications
        transformed["skills_required"] = self._extract_skills(transformed["description"])
        transformed["skills_preferred"] = []
        transformed["education_required"] = self._extract_education_requirements(transformed["description"])
        
        # Additional information
        transformed["benefits"] = self._extract_benefits(raw_job.get("job_benefits", []))
        transformed["company_size"] = raw_job.get("employer_company_type")
        transformed["industry"] = self._normalize_industry(raw_job.get("job_category"))
        
        # URLs and external references
        transformed["job_url"] = raw_job.get("job_apply_link")
        transformed["company_url"] = raw_job.get("employer_website")
        transformed["application_url"] = raw_job.get("job_apply_link")
        
        # Dates
        transformed["posted_date"] = self._parse_date(raw_job.get("job_posted_at_datetime_utc"))
        transformed["application_deadline"] = self._parse_date(raw_job.get("job_offer_expiration_datetime_utc"))
        
        # Metadata
        transformed["source"] = "jsearch"
        transformed["scraped_at"] = datetime.utcnow()
        transformed["verification_status"] = VerificationStatus.UNVERIFIED
        
        # Enhanced metadata
        transformed["company_size_category"] = self._categorize_company_size(raw_job.get("employer_company_type"))
        transformed["seniority_level"] = self._determine_seniority_level(transformed["title"], transformed["description"])
        transformed["tech_stack"] = self._extract_tech_stack(transformed["description"])
        
        return transformed
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text fields."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        
        return text
    
    def _normalize_location(self, city: str, state: str, country: str) -> str:
        """Normalize location information."""
        parts = []
        
        if city:
            parts.append(self._clean_text(city))
        if state:
            parts.append(self._clean_text(state))
        if country and country.lower() != "us":
            parts.append(self._clean_text(country))
        
        return ", ".join(parts) if parts else "Remote"
    
    def _normalize_job_type(self, employment_type: str) -> Optional[JobType]:
        """Normalize job employment type."""
        if not employment_type:
            return None
        
        employment_type = employment_type.lower()
        
        if "full" in employment_type and "time" in employment_type:
            return JobType.FULL_TIME
        elif "part" in employment_type and "time" in employment_type:
            return JobType.PART_TIME
        elif "contract" in employment_type:
            return JobType.CONTRACT
        elif "freelance" in employment_type:
            return JobType.FREELANCE
        elif "intern" in employment_type:
            return JobType.INTERNSHIP
        elif "temp" in employment_type:
            return JobType.TEMPORARY
        
        return None
    
    def _determine_remote_type(self, is_remote: bool, location: str) -> Optional[RemoteType]:
        """Determine remote work type."""
        if is_remote:
            return RemoteType.REMOTE
        elif location and "remote" in location.lower():
            return RemoteType.REMOTE
        elif location and "hybrid" in location.lower():
            return RemoteType.HYBRID
        else:
            return RemoteType.ON_SITE
    
    def _determine_experience_level(self, required_exp: Dict[str, Any], description: str) -> Optional[ExperienceLevel]:
        """Determine experience level from job data."""
        # Check structured experience data
        if required_exp:
            exp_required = required_exp.get("experience_mentioned", False)
            if not exp_required:
                return ExperienceLevel.ENTRY_LEVEL
        
        # Check description for experience keywords
        if description:
            description_lower = description.lower()
            
            if any(keyword in description_lower for keyword in ["entry", "junior", "graduate", "intern"]):
                return ExperienceLevel.ENTRY_LEVEL
            elif any(keyword in description_lower for keyword in ["senior", "sr.", "lead"]):
                return ExperienceLevel.SENIOR_LEVEL
            elif any(keyword in description_lower for keyword in ["director", "head of", "vp", "vice president"]):
                return ExperienceLevel.DIRECTOR
            elif any(keyword in description_lower for keyword in ["cto", "ceo", "cfo", "president"]):
                return ExperienceLevel.EXECUTIVE
            elif re.search(r'\b(?:2-4|3-5)\s+years?\b', description_lower):
                return ExperienceLevel.ASSOCIATE
            elif re.search(r'\b(?:5-8|6-10)\s+years?\b', description_lower):
                return ExperienceLevel.MID_LEVEL
        
        return ExperienceLevel.MID_LEVEL  # Default
    
    def _extract_salary_info(self, raw_job: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], str]:
        """Extract salary information."""
        salary_min = None
        salary_max = None
        currency = "USD"
        
        # Check structured salary fields
        if raw_job.get("job_min_salary"):
            salary_min = float(raw_job["job_min_salary"])
        if raw_job.get("job_max_salary"):
            salary_max = float(raw_job["job_max_salary"])
        
        # If no structured data, try to parse from description
        if not salary_min and not salary_max:
            description = raw_job.get("job_description", "")
            salary_min, salary_max = self._parse_salary_from_text(description)
        
        return salary_min, salary_max, currency
    
    def _parse_salary_from_text(self, text: str) -> Tuple[Optional[float], Optional[float]]:
        """Parse salary information from text."""
        for pattern in self.salary_patterns:
            match = pattern.search(text)
            if match:
                if len(match.groups()) == 2:
                    # Range format
                    min_sal = float(match.group(1).replace(',', ''))
                    max_sal = float(match.group(2).replace(',', ''))
                    return min_sal, max_sal
                else:
                    # Single value
                    sal = float(match.group(1).replace(',', ''))
                    return sal, None
        
        return None, None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description."""
        skills = set()
        
        for pattern in self.skills_patterns:
            matches = pattern.findall(description)
            skills.update(match.lower() for match in matches)
        
        return list(skills)
    
    def _extract_requirements(self, description: str) -> str:
        """Extract requirements section from job description."""
        if not description:
            return ""
        
        # Look for requirements section
        requirements_patterns = [
            r'(?:requirements?|qualifications?|what you.ll need|what we.re looking for):?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'(?:must have|required skills?|minimum qualifications?):?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in requirements_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                return self._clean_text(match.group(1))
        
        return ""
    
    def _extract_responsibilities(self, description: str) -> str:
        """Extract responsibilities section from job description."""
        if not description:
            return ""
        
        # Look for responsibilities section
        resp_patterns = [
            r'(?:responsibilities?|duties|what you.ll do|role overview):?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'(?:key responsibilities?|main duties):?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in resp_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                return self._clean_text(match.group(1))
        
        return ""
    
    def _extract_education_requirements(self, description: str) -> Optional[str]:
        """Extract education requirements."""
        if not description:
            return None
        
        education_patterns = [
            r'(?:bachelor|master|phd|degree|diploma)',
            r'(?:bs|ba|ms|ma|mba|phd)',
            r'(?:university|college)'
        ]
        
        for pattern in education_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                # Extract the sentence containing education requirement
                sentences = description.split('.')
                for sentence in sentences:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        return self._clean_text(sentence.strip())
        
        return None
    
    def _extract_benefits(self, benefits_list: List[str]) -> List[str]:
        """Extract and normalize benefits."""
        if not benefits_list:
            return []
        
        return [self._clean_text(benefit) for benefit in benefits_list if benefit]
    
    def _normalize_industry(self, category: str) -> Optional[str]:
        """Normalize industry/category."""
        if not category:
            return None
        
        # Map common categories to normalized names
        category_map = {
            "information technology": "Technology",
            "it": "Technology",
            "software": "Technology",
            "finance": "Financial Services",
            "healthcare": "Healthcare",
            "education": "Education",
            "marketing": "Marketing",
            "sales": "Sales",
            "engineering": "Engineering",
        }
        
        category_lower = category.lower()
        return category_map.get(category_lower, self._clean_text(category))
    
    def _categorize_company_size(self, company_type: str) -> Optional[CompanySizeCategory]:
        """Categorize company size."""
        if not company_type:
            return None
        
        company_type_lower = company_type.lower()
        
        if "startup" in company_type_lower or "small" in company_type_lower:
            return CompanySizeCategory.STARTUP
        elif "medium" in company_type_lower:
            return CompanySizeCategory.MEDIUM
        elif "large" in company_type_lower or "enterprise" in company_type_lower:
            return CompanySizeCategory.LARGE
        
        return None
    
    def _determine_seniority_level(self, title: str, description: str) -> Optional[SeniorityLevel]:
        """Determine seniority level."""
        text = f"{title} {description}".lower()
        
        if any(keyword in text for keyword in ["director", "head of", "vp", "vice president"]):
            return SeniorityLevel.DIRECTOR
        elif any(keyword in text for keyword in ["cto", "ceo", "cfo", "president"]):
            return SeniorityLevel.C_LEVEL
        elif any(keyword in text for keyword in ["manager", "lead", "principal"]):
            return SeniorityLevel.MANAGER
        elif any(keyword in text for keyword in ["team lead", "tech lead"]):
            return SeniorityLevel.TEAM_LEAD
        else:
            return SeniorityLevel.INDIVIDUAL_CONTRIBUTOR
    
    def _extract_tech_stack(self, description: str) -> List[str]:
        """Extract technology stack."""
        tech_keywords = [
            "python", "javascript", "java", "react", "angular", "vue", "node.js",
            "django", "flask", "spring", "express", "aws", "azure", "gcp",
            "docker", "kubernetes", "postgresql", "mysql", "mongodb", "redis"
        ]
        
        found_tech = []
        description_lower = description.lower()
        
        for tech in tech_keywords:
            if tech in description_lower:
                found_tech.append(tech)
        
        return found_tech
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        
        try:
            # Handle common date formats
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {e}")
            return None
    
    async def _generate_embeddings(self, job_data: Dict[str, Any]) -> Optional[List[float]]:
        """Generate embeddings for job data."""
        try:
            # Combine relevant text fields for embedding
            text_parts = [
                job_data.get("title", ""),
                job_data.get("description", ""),
                job_data.get("requirements", ""),
                " ".join(job_data.get("skills_required", []))
            ]
            
            content = " ".join(part for part in text_parts if part)
            
            if not content:
                return None
            
            # For now, return a placeholder - in production, integrate with sentence transformers
            # This would be replaced with actual embedding generation
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Placeholder embedding (in production, use actual model)
            embedding = [0.0] * self.config.embedding_dimension
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None
    
    def _assess_data_quality(self, job_data: Dict[str, Any]) -> float:
        """Assess data quality score (0.0 to 1.0)."""
        score = 0.0
        max_score = 0.0
        
        # Check required fields
        for field in self.config.required_fields:
            max_score += 1.0
            if job_data.get(field):
                score += 1.0
        
        # Check optional but important fields
        important_fields = ["description", "requirements", "salary_min", "job_type"]
        for field in important_fields:
            max_score += 0.5
            if job_data.get(field):
                score += 0.5
        
        # Check description length
        max_score += 0.5
        description = job_data.get("description", "")
        if len(description) >= self.config.min_description_length:
            score += 0.5
        
        return min(score / max_score, 1.0) if max_score > 0 else 0.0
    
    async def _check_for_duplicates(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Check if job is a duplicate and return canonical job ID."""
        try:
            # Simple duplicate detection based on title + company + location
            title = job_data.get("title", "").lower().strip()
            company = job_data.get("company", "").lower().strip()
            location = job_data.get("location", "").lower().strip()
            
            if not (title and company):
                return None
            
            # Create a hash for similarity matching
            job_hash = hashlib.md5(f"{title}|{company}|{location}".encode()).hexdigest()
            
            # In production, this would check against existing jobs in the database
            # For now, return None (no duplicates found)
            return None
            
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            return None
    
    async def _store_processed_job(
        self,
        processing_id: str,
        job_index: int,
        processed_data: Dict[str, Any],
        embedding_vector: Optional[List[float]],
        duplicate_of: Optional[str],
        quality_score: float
    ):
        """Store processed job data."""
        processed_job = ProcessedJobData(
            processing_id=processing_id,
            job_index=job_index,
            processed_data=processed_data,
            embedding_vector=embedding_vector,
            duplicate_of=duplicate_of,
            quality_score=quality_score
        )
        
        try:
            with self.db_manager.get_session() as session:
                job_db = pydantic_to_sqlalchemy(processed_job, ProcessedJobDataDB)
                session.add(job_db)
                session.flush()
                
        except Exception as e:
            logger.error(f"Error storing processed job: {e}")
            raise
    
    async def _complete_processing_log(
        self,
        processing_id: str,
        status: ETLProcessingStatus,
        jobs_processed: int,
        jobs_failed: int,
        errors: List[Dict[str, Any]]
    ):
        """Complete processing log."""
        try:
            with self.db_manager.get_session() as session:
                log_db = session.query(JobProcessingLogDB).filter(
                    JobProcessingLogDB.id == processing_id
                ).first()
                
                if log_db:
                    log_db.completed_at = datetime.utcnow()
                    log_db.status = status
                    log_db.jobs_processed = jobs_processed
                    log_db.jobs_failed = jobs_failed
                    log_db.errors = errors
                    
                    # Calculate metrics
                    duration = (log_db.completed_at - log_db.started_at).total_seconds()
                    log_db.metrics = {
                        "duration_seconds": duration,
                        "jobs_per_second": jobs_processed / duration if duration > 0 else 0,
                        "success_rate": jobs_processed / (jobs_processed + jobs_failed) if (jobs_processed + jobs_failed) > 0 else 0
                    }
                    
                    session.flush()
        
        except Exception as e:
            logger.error(f"Error completing processing log: {e}")
    
    async def _update_collection_status(self, collection_id: str, status: ETLProcessingStatus):
        """Update raw collection processing status."""
        try:
            with self.db_manager.get_session() as session:
                collection_db = session.query(RawJobCollectionDB).filter(
                    RawJobCollectionDB.id == collection_id
                ).first()
                
                if collection_db:
                    collection_db.processing_status = status
                    session.flush()
        
        except Exception as e:
            logger.error(f"Error updating collection status: {e}")
    
    async def get_pending_processing_jobs(self, limit: int = 50) -> List[ProcessedJobData]:
        """Get processed jobs ready for loading."""
        try:
            with self.db_manager.get_session() as session:
                jobs_db = session.query(ProcessedJobDataDB).filter(
                    ProcessedJobDataDB.load_status == ETLProcessingStatus.PENDING
                ).limit(limit).all()
                
                return [
                    ProcessedJobData(
                        processing_id=job.processing_id,
                        job_index=job.job_index,
                        processed_data=job.processed_data,
                        embedding_vector=job.embedding_vector,
                        duplicate_of=job.duplicate_of,
                        load_status=job.load_status,
                        quality_score=job.quality_score,
                        validation_errors=job.validation_errors,
                        created_at=job.created_at
                    ) for job in jobs_db
                ]
                
        except Exception as e:
            logger.error(f"Error getting pending processing jobs: {e}")
            return []
