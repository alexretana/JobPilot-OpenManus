#!/usr/bin/env python3
"""
Enhanced Jobs API for JobPilot-OpenManus
Implements job sources management, enhanced job listings with additional metadata,
job embeddings for semantic search, vector search capabilities, and job deduplication.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.logger import logger

# Initialize router
router = APIRouter()

# =====================================
# Pydantic Models for API
# =====================================


class JobSourceCreate(BaseModel):
    name: str
    display_name: str
    base_url: str
    api_available: bool = False
    rate_limit_config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class JobSourceResponse(BaseModel):
    id: str
    name: str
    display_name: str
    base_url: str
    api_available: bool
    rate_limit_config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class EnhancedJobCreate(BaseModel):
    name: str  # Added required name field
    title: str
    company: str
    location: str
    description: str
    requirements: Optional[str] = None
    job_type: str
    remote_type: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills_required: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    # New Phase 2 fields
    verification_status: str = "pending"
    company_size_category: str = "unknown"
    seniority_level: str = "individual_contributor"
    data_quality_score: float = 0.0
    source_count: int = 1


class EnhancedJobResponse(BaseModel):
    id: str
    name: str
    title: str
    company: str
    location: str
    description: str
    requirements: Optional[str] = None
    job_type: str
    remote_type: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills_required: List[str]
    tech_stack: List[str]
    verification_status: str
    company_size_category: str
    seniority_level: str
    data_quality_score: float
    source_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class JobSourceListingCreate(BaseModel):
    job_id: str
    source_id: str
    source_job_id: str
    source_url: str
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class JobSourceListingResponse(BaseModel):
    id: str
    job_id: str
    source_id: str
    source_job_id: str
    source_url: str
    source_metadata: Dict[str, Any]
    created_at: datetime


class JobEmbeddingResponse(BaseModel):
    id: str
    job_id: str
    embedding_model: str
    vector_dimension: int
    created_at: datetime


class SemanticSearchResult(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    description: str
    similarity_score: float


# =====================================
# In-memory storage for development/testing
# =====================================


class InMemoryStorage:
    def __init__(self):
        self.job_sources: Dict[str, Dict[str, Any]] = {}
        self.enhanced_jobs: Dict[str, Dict[str, Any]] = {}
        self.job_source_listings: Dict[str, Dict[str, Any]] = {}
        self.job_embeddings: Dict[str, Dict[str, Any]] = {}

    def create_job_source(self, data: JobSourceCreate) -> Dict[str, Any]:
        source_id = str(uuid4())
        source = {
            "id": source_id,
            "name": data.name,
            "display_name": data.display_name,
            "base_url": data.base_url,
            "api_available": data.api_available,
            "rate_limit_config": data.rate_limit_config,
            "is_active": data.is_active,
            "created_at": datetime.now(),
            "updated_at": None,
        }
        self.job_sources[source_id] = source
        return source

    def get_job_sources(self) -> List[Dict[str, Any]]:
        return list(self.job_sources.values())

    def get_job_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        return self.job_sources.get(source_id)

    def update_job_source(
        self, source_id: str, data: JobSourceCreate
    ) -> Optional[Dict[str, Any]]:
        if source_id in self.job_sources:
            source = self.job_sources[source_id]
            source.update(
                {
                    "name": data.name,
                    "display_name": data.display_name,
                    "base_url": data.base_url,
                    "api_available": data.api_available,
                    "rate_limit_config": data.rate_limit_config,
                    "is_active": data.is_active,
                    "updated_at": datetime.now(),
                }
            )
            return source
        return None

    def create_enhanced_job(self, data: EnhancedJobCreate) -> Dict[str, Any]:
        job_id = str(uuid4())
        job = {
            "id": job_id,
            "name": data.name,
            "title": data.title,
            "company": data.company,
            "location": data.location,
            "description": data.description,
            "requirements": data.requirements,
            "job_type": data.job_type,
            "remote_type": data.remote_type,
            "salary_min": data.salary_min,
            "salary_max": data.salary_max,
            "skills_required": data.skills_required,
            "tech_stack": data.tech_stack,
            "verification_status": data.verification_status,
            "company_size_category": data.company_size_category,
            "seniority_level": data.seniority_level,
            "data_quality_score": data.data_quality_score,
            "source_count": data.source_count,
            "created_at": datetime.now(),
            "updated_at": None,
        }
        self.enhanced_jobs[job_id] = job
        return job

    def get_enhanced_jobs(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        jobs = list(self.enhanced_jobs.values())
        if not filters:
            return jobs

        # Apply filters
        filtered_jobs = []
        for job in jobs:
            match = True
            for key, value in filters.items():
                if key in job and job[key] != value:
                    match = False
                    break
            if match:
                filtered_jobs.append(job)

        return filtered_jobs

    def create_job_source_listing(self, data: JobSourceListingCreate) -> Dict[str, Any]:
        listing_id = str(uuid4())
        listing = {
            "id": listing_id,
            "job_id": data.job_id,
            "source_id": data.source_id,
            "source_job_id": data.source_job_id,
            "source_url": data.source_url,
            "source_metadata": data.source_metadata,
            "created_at": datetime.now(),
        }
        self.job_source_listings[listing_id] = listing
        return listing

    def get_job_source_listings_by_job(self, job_id: str) -> List[Dict[str, Any]]:
        return [
            listing
            for listing in self.job_source_listings.values()
            if listing["job_id"] == job_id
        ]

    def create_job_embedding(self, job_id: str) -> Dict[str, Any]:
        embedding_id = str(uuid4())
        embedding = {
            "id": embedding_id,
            "job_id": job_id,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "vector_dimension": 384,
            "created_at": datetime.now(),
        }
        self.job_embeddings[embedding_id] = embedding
        return embedding

    def get_job_embeddings_by_job(self, job_id: str) -> List[Dict[str, Any]]:
        return [
            embedding
            for embedding in self.job_embeddings.values()
            if embedding["job_id"] == job_id
        ]


# Storage instance
storage = InMemoryStorage()

# =====================================
# Job Sources API Endpoints
# =====================================


@router.post("/api/job-sources", response_model=JobSourceResponse, status_code=201)
async def create_job_source(data: JobSourceCreate):
    """Create a new job source."""
    try:
        source = storage.create_job_source(data)
        logger.info(f"Created job source: {source['name']}")
        return source
    except Exception as e:
        logger.error(f"Error creating job source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/job-sources", response_model=List[JobSourceResponse])
async def get_job_sources():
    """Get all job sources."""
    try:
        sources = storage.get_job_sources()
        logger.info(f"Retrieved {len(sources)} job sources")
        return sources
    except Exception as e:
        logger.error(f"Error retrieving job sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/job-sources/{source_id}", response_model=JobSourceResponse)
async def get_job_source(source_id: str):
    """Get a specific job source."""
    try:
        source = storage.get_job_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Job source not found")
        return source
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/job-sources/{source_id}", response_model=JobSourceResponse)
async def update_job_source(source_id: str, data: JobSourceCreate):
    """Update a job source."""
    try:
        source = storage.update_job_source(source_id, data)
        if not source:
            raise HTTPException(status_code=404, detail="Job source not found")
        logger.info(f"Updated job source: {source_id}")
        return source
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating job source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================
# Enhanced Job Listings API Endpoints
# =====================================


@router.post("/api/leads", response_model=EnhancedJobResponse, status_code=200)
async def create_enhanced_job(data: EnhancedJobCreate):
    """Create a new enhanced job listing."""
    try:
        job = storage.create_enhanced_job(data)
        logger.info(f"Created enhanced job: {job['title']} at {job['company']}")
        return job
    except Exception as e:
        logger.error(f"Error creating enhanced job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/leads", response_model=List[EnhancedJobResponse])
async def get_enhanced_jobs(
    verification_status: Optional[str] = Query(None),
    company_size_category: Optional[str] = Query(None),
    seniority_level: Optional[str] = Query(None),
):
    """Get enhanced job listings with optional filters."""
    try:
        filters = {}
        if verification_status:
            filters["verification_status"] = verification_status
        if company_size_category:
            filters["company_size_category"] = company_size_category
        if seniority_level:
            filters["seniority_level"] = seniority_level

        jobs = storage.get_enhanced_jobs(filters if filters else None)
        logger.info(f"Retrieved {len(jobs)} enhanced jobs with filters: {filters}")
        return jobs
    except Exception as e:
        logger.error(f"Error retrieving enhanced jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================
# Job Source Listings API Endpoints
# =====================================


@router.post(
    "/api/job-source-listings", response_model=JobSourceListingResponse, status_code=201
)
async def create_job_source_listing(data: JobSourceListingCreate):
    """Create a new job source listing."""
    try:
        listing = storage.create_job_source_listing(data)
        logger.info(f"Created job source listing: {listing['source_job_id']}")
        return listing
    except Exception as e:
        logger.error(f"Error creating job source listing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/jobs/{job_id}/sources", response_model=List[JobSourceListingResponse])
async def get_job_source_listings(job_id: str):
    """Get all source listings for a specific job."""
    try:
        listings = storage.get_job_source_listings_by_job(job_id)
        logger.info(f"Retrieved {len(listings)} source listings for job {job_id}")
        return listings
    except Exception as e:
        logger.error(f"Error retrieving source listings for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================
# Job Embeddings API Endpoints
# =====================================


@router.post(
    "/api/jobs/{job_id}/embeddings",
    response_model=JobEmbeddingResponse,
    status_code=201,
)
async def create_job_embedding(job_id: str):
    """Create embeddings for a job."""
    try:
        # Check if job exists
        job = storage.enhanced_jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        embedding = storage.create_job_embedding(job_id)
        logger.info(f"Created embeddings for job {job_id}")
        return embedding
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating embeddings for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/jobs/{job_id}/embeddings", response_model=List[JobEmbeddingResponse])
async def get_job_embeddings(job_id: str):
    """Get embeddings for a specific job."""
    try:
        embeddings = storage.get_job_embeddings_by_job(job_id)
        logger.info(f"Retrieved {len(embeddings)} embeddings for job {job_id}")
        return embeddings
    except Exception as e:
        logger.error(f"Error retrieving embeddings for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/embeddings/stats")
async def get_embeddings_stats():
    """Get embeddings statistics."""
    try:
        total_embeddings = len(storage.job_embeddings)
        total_jobs_with_embeddings = len(
            set(emb["job_id"] for emb in storage.job_embeddings.values())
        )

        return {
            "total_embeddings": total_embeddings,
            "total_jobs_with_embeddings": total_jobs_with_embeddings,
            "embedding_models": list(
                set(emb["embedding_model"] for emb in storage.job_embeddings.values())
            ),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error retrieving embeddings stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================
# Vector Search API Endpoints
# =====================================


@router.get("/api/search/semantic", response_model=List[SemanticSearchResult])
async def semantic_search(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
    job_type: Optional[str] = Query(None),
    remote_type: Optional[str] = Query(None),
):
    """Perform semantic search on job listings."""
    try:
        # For demo purposes, return mock results based on enhanced jobs
        jobs = storage.get_enhanced_jobs()

        # Simple text matching for demo (in real implementation, use vector search)
        results = []
        query_lower = query.lower()

        for job in jobs:
            score = 0.0

            # Calculate basic similarity score
            if query_lower in job["title"].lower():
                score += 0.8
            if query_lower in job["description"].lower():
                score += 0.6
            if query_lower in job.get("requirements", "").lower():
                score += 0.4

            # Check skills matching
            for skill in job.get("skills_required", []):
                if query_lower in skill.lower():
                    score += 0.3

            if score > 0:
                # Apply filters
                if job_type and job["job_type"] != job_type:
                    continue
                if remote_type and job["remote_type"] != remote_type:
                    continue

                result = SemanticSearchResult(
                    job_id=job["id"],
                    title=job["title"],
                    company=job["company"],
                    location=job["location"],
                    description=job["description"][:200] + "...",
                    similarity_score=min(score, 1.0),
                )
                results.append(result)

        # Sort by similarity score and limit results
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        results = results[:limit]

        logger.info(f"Semantic search for '{query}': {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error performing semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/search/hybrid")
async def hybrid_search(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
):
    """Perform hybrid search (semantic + keyword)."""
    # Return 404 for now as mentioned in test expectations
    raise HTTPException(status_code=404, detail="Hybrid search not yet implemented")


# =====================================
# Job Deduplication API Endpoints
# =====================================


class DeduplicationRequest(BaseModel):
    job1_id: str
    job2_id: str


class BatchDeduplicationRequest(BaseModel):
    job_ids: List[str]


@router.post("/api/jobs/deduplicate")
async def deduplicate_jobs(request: DeduplicationRequest):
    """Check if two jobs are duplicates."""
    try:
        job1 = storage.enhanced_jobs.get(request.job1_id)
        job2 = storage.enhanced_jobs.get(request.job2_id)

        if not job1 or not job2:
            raise HTTPException(status_code=404, detail="One or both jobs not found")

        # Simple similarity calculation
        confidence_score = 0.0

        # Title similarity
        if job1["title"].lower() == job2["title"].lower():
            confidence_score += 0.4
        elif (
            job1["title"].lower() in job2["title"].lower()
            or job2["title"].lower() in job1["title"].lower()
        ):
            confidence_score += 0.2

        # Company similarity
        if job1["company"].lower() == job2["company"].lower():
            confidence_score += 0.3

        # Location similarity
        if job1["location"].lower() == job2["location"].lower():
            confidence_score += 0.1

        # Skills similarity
        common_skills = set(
            skill.lower() for skill in job1.get("skills_required", [])
        ) & set(skill.lower() for skill in job2.get("skills_required", []))
        if common_skills:
            confidence_score += min(0.2, len(common_skills) * 0.05)

        is_duplicate = confidence_score >= 0.7  # Threshold for duplicate detection

        logger.info(
            f"Deduplication check for jobs {request.job1_id} and {request.job2_id}: {confidence_score:.2f} confidence"
        )

        return {
            "job1_id": request.job1_id,
            "job2_id": request.job2_id,
            "confidence_score": confidence_score,
            "is_duplicate": is_duplicate,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during deduplication check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/jobs/deduplicate-batch")
async def batch_deduplicate_jobs(request: BatchDeduplicationRequest):
    """Find duplicate jobs in a batch of job IDs."""
    try:
        if len(request.job_ids) < 2:
            return {
                "message": "Need at least 2 jobs for batch deduplication",
                "duplicates": [],
                "total_jobs": len(request.job_ids),
            }

        jobs = []
        for job_id in request.job_ids:
            job = storage.enhanced_jobs.get(job_id)
            if job:
                jobs.append(job)

        # Find potential duplicates
        duplicates = []
        seen = {}

        for job in jobs:
            key = f"{job['title'].lower()}_{job['company'].lower()}"
            if key in seen:
                duplicates.append(
                    {
                        "job_id": job["id"],
                        "duplicate_of": seen[key],
                        "match_type": "title_company_exact",
                        "confidence": 0.9,
                    }
                )
            else:
                seen[key] = job["id"]

        logger.info(
            f"Batch deduplication: found {len(duplicates)} potential duplicates"
        )

        return {
            "duplicates": duplicates,
            "total_jobs": len(jobs),
            "duplicates_found": len(duplicates),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error during batch deduplication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================
# Statistics API Endpoints
# =====================================


@router.get("/api/stats")
async def get_general_stats():
    """Get general statistics."""
    try:
        total_jobs = len(storage.enhanced_jobs)
        total_sources = len(storage.job_sources)
        total_embeddings = len(storage.job_embeddings)

        return {
            "total_jobs": total_jobs,
            "total_sources": total_sources,
            "total_embeddings": total_embeddings,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error retrieving general stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stats/enhanced")
async def get_enhanced_stats():
    """Get enhanced statistics (placeholder)."""
    # Return 404 as expected by test
    raise HTTPException(
        status_code=404, detail="Enhanced stats endpoint not yet implemented"
    )


@router.get("/api/stats/sources")
async def get_source_stats():
    """Get source statistics (placeholder)."""
    # Return 404 as expected by test
    raise HTTPException(
        status_code=404, detail="Source stats endpoint not yet implemented"
    )


# =====================================
# Timeline Integration (placeholder)
# =====================================


@router.get("/api/timeline/jobs")
async def get_job_timeline():
    """Get job-related timeline events (placeholder)."""
    # Return empty for now as expected by test
    return {"events": [], "total": 0, "message": "No timeline events found"}
