"""
Semantic Search Tool
AI-powered job search using embeddings and semantic similarity.
"""

from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import Field

from app.data.database import get_job_repository
from app.data.models import JobListing, JobType, RemoteType
from app.logger import logger
from app.tool.base import BaseTool


class SemanticSearchTool(BaseTool):
    """Tool for semantic job search using AI embeddings."""

    name: str = "semantic_search"
    description: str = (
        "Search for jobs using AI-powered semantic similarity. "
        "Understands job requirements beyond keywords and provides intelligent matching."
    )

    model_name: str = Field(
        default="all-MiniLM-L6-v2", description="Sentence transformer model"
    )
    max_results: int = Field(default=20, description="Maximum search results")
    min_similarity: float = Field(
        default=0.3, description="Minimum similarity threshold"
    )

    def __init__(self, **data):
        """Initialize semantic search tool."""
        super().__init__(**data)
        self.job_repo = get_job_repository()
        self._embedding_service = None

    def _get_embedding_service(self):
        """Initialize embedding service lazily."""
        if self._embedding_service is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._embedding_service = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except ImportError:
                logger.warning(
                    "sentence-transformers not installed, using fallback search"
                )
                self._embedding_service = False
        return self._embedding_service

    async def _run(
        self,
        query: str,
        job_types: str = "",
        remote_types: str = "",
        locations: str = "",
        min_salary: int = 0,
        max_salary: int = 0,
        max_results: int = 20,
    ) -> str:
        """
        Search for jobs using semantic similarity.

        Args:
            query: Search query describing the desired job
            job_types: Comma-separated job types (e.g., "Full-time,Contract")
            remote_types: Comma-separated remote types (e.g., "Remote,Hybrid")
            locations: Comma-separated locations (e.g., "San Francisco,Remote")
            min_salary: Minimum salary requirement
            max_salary: Maximum salary requirement
            max_results: Maximum number of results (1-50)

        Returns:
            Formatted search results with similarity scores
        """
        try:
            logger.info(f"Starting semantic search for: {query}")

            # Limit results
            max_results = min(max_results, 50)

            # Parse filter parameters
            job_type_list = (
                [jt.strip() for jt in job_types.split(",") if jt.strip()]
                if job_types
                else None
            )
            remote_type_list = (
                [rt.strip() for rt in remote_types.split(",") if rt.strip()]
                if remote_types
                else None
            )
            location_list = (
                [loc.strip() for loc in locations.split(",") if loc.strip()]
                if locations
                else None
            )

            # Convert job types to enums
            parsed_job_types = None
            if job_type_list:
                parsed_job_types = []
                for jt in job_type_list:
                    try:
                        parsed_job_types.append(JobType(jt))
                    except ValueError:
                        logger.warning(f"Invalid job type: {jt}")

            # Convert remote types to enums
            parsed_remote_types = None
            if remote_type_list:
                parsed_remote_types = []
                for rt in remote_type_list:
                    try:
                        parsed_remote_types.append(RemoteType(rt))
                    except ValueError:
                        logger.warning(f"Invalid remote type: {rt}")

            # Get embedding service
            embedding_service = self._get_embedding_service()

            if embedding_service:
                # Semantic search with embeddings
                matches = await self._semantic_search_with_embeddings(
                    query,
                    parsed_job_types,
                    parsed_remote_types,
                    location_list,
                    min_salary or None,
                    max_salary or None,
                    max_results,
                )
            else:
                # Fallback to keyword search
                matches = await self._fallback_keyword_search(
                    query,
                    parsed_job_types,
                    parsed_remote_types,
                    location_list,
                    min_salary or None,
                    max_salary or None,
                    max_results,
                )

            if not matches:
                return f"No jobs found matching query: '{query}' with the specified filters."

            # Format results
            result_lines = [f"Found {len(matches)} jobs matching '{query}':\n"]

            for i, match in enumerate(matches[:max_results], 1):
                if isinstance(match, dict) and "job" in match:
                    job = match["job"]
                    similarity = match.get("similarity", 0.0)

                    salary_info = ""
                    if job.salary_min and job.salary_max:
                        salary_info = f" | ${job.salary_min:,}-${job.salary_max:,}"
                    elif job.salary_min:
                        salary_info = f" | ${job.salary_min:,}+"

                    result_lines.append(
                        f"{i}. **{job.title}** at {job.company}\n"
                        f"   📍 {job.location or 'Location not specified'} | "
                        f"{job.job_type.value if job.job_type else 'Type not specified'}"
                        f"{salary_info}\n"
                        f"   🎯 Match: {similarity:.1%} | Skills: {', '.join(job.skills_required[:3]) if job.skills_required else 'Not specified'}\n"
                    )
                else:
                    # Handle JobListing objects directly
                    job = match
                    salary_info = ""
                    if job.salary_min and job.salary_max:
                        salary_info = f" | ${job.salary_min:,}-${job.salary_max:,}"

                    result_lines.append(
                        f"{i}. **{job.title}** at {job.company}\n"
                        f"   📍 {job.location or 'Location not specified'} | "
                        f"{job.job_type.value if job.job_type else 'Type not specified'}"
                        f"{salary_info}\n"
                        f"   Skills: {', '.join(job.skills_required[:3]) if job.skills_required else 'Not specified'}\n"
                    )

            result = "\n".join(result_lines)
            logger.info(f"Semantic search completed: {len(matches)} results")
            return result

        except Exception as e:
            error_msg = f"Error in semantic search: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def _semantic_search_with_embeddings(
        self,
        query: str,
        job_types: Optional[List[JobType]],
        remote_types: Optional[List[RemoteType]],
        locations: Optional[List[str]],
        min_salary: Optional[float],
        max_salary: Optional[float],
        max_results: int,
    ) -> List[Dict]:
        """Perform semantic search using embeddings."""
        try:
            # Get all jobs with filters
            jobs, _ = self.job_repo.search_jobs(
                job_types=job_types,
                remote_types=remote_types,
                locations=locations,
                min_salary=min_salary,
                max_salary=max_salary,
                limit=500,  # Get more for semantic filtering
            )

            if not jobs:
                return []

            # Generate query embedding
            query_embedding = self._embedding_service.encode([query])[0]

            # Calculate similarities
            matches = []
            for job in jobs:
                # Create job text for embedding
                job_text = self._create_job_text(job)
                job_embedding = self._embedding_service.encode([job_text])[0]

                # Calculate cosine similarity
                similarity = np.dot(query_embedding, job_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(job_embedding)
                )

                if similarity >= self.min_similarity:
                    matches.append(
                        {
                            "job": job,
                            "similarity": float(similarity),
                            "job_text": job_text,
                        }
                    )

            # Sort by similarity
            matches.sort(key=lambda x: x["similarity"], reverse=True)
            return matches[:max_results]

        except Exception as e:
            logger.error(f"Error in semantic search with embeddings: {e}")
            return []

    async def _fallback_keyword_search(
        self,
        query: str,
        job_types: Optional[List[JobType]],
        remote_types: Optional[List[RemoteType]],
        locations: Optional[List[str]],
        min_salary: Optional[float],
        max_salary: Optional[float],
        max_results: int,
    ) -> List[JobListing]:
        """Fallback keyword-based search."""
        try:
            jobs, _ = self.job_repo.search_jobs(
                query=query,
                job_types=job_types,
                remote_types=remote_types,
                locations=locations,
                min_salary=min_salary,
                max_salary=max_salary,
                limit=max_results,
            )

            logger.info(f"Fallback search found {len(jobs)} jobs")
            return jobs

        except Exception as e:
            logger.error(f"Error in fallback search: {e}")
            return []

    def _create_job_text(self, job: JobListing) -> str:
        """Create text representation of job for embedding."""
        parts = [
            job.title,
            job.company,
            job.description or "",
            job.requirements or "",
            " ".join(job.skills_required) if job.skills_required else "",
            job.location or "",
        ]

        # Add job type and remote type
        if job.job_type:
            parts.append(job.job_type.value)
        if job.remote_type:
            parts.append(job.remote_type.value)

        return " ".join(filter(None, parts))

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model."""
        embedding_service = self._get_embedding_service()
        if embedding_service:
            return {
                "model_name": self.model_name,
                "embedding_dim": 384,  # all-MiniLM-L6-v2 dimension
                "status": "loaded",
            }
        else:
            return {
                "model_name": "fallback",
                "embedding_dim": 0,
                "status": "using keyword search",
            }
