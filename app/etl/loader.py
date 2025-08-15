"""
JobPilot ETL Data Loader
Handles loading processed job data into the database with deduplication and embedding support.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..data.models import (  # SQLAlchemy models; Pydantic models; Enums; Utilities
    ETLOperationLog,
    ETLOperationLogDB,
    ETLOperationType,
    ETLProcessingStatus,
    JobDeduplication,
    JobDeduplicationDB,
    JobEmbedding,
    JobEmbeddingDB,
    JobListing,
    JobListingDB,
    JobSource,
    JobSourceDB,
    JobSourceListing,
    JobSourceListingDB,
    JobStatus,
    ProcessedJobData,
    ProcessedJobDataDB,
    VerificationStatus,
    pydantic_to_sqlalchemy,
    sqlalchemy_to_pydantic,
)
from ..database.manager import DatabaseManager


# Settings will be passed as parameter

logger = logging.getLogger(__name__)


class DuplicationDetector:
    """Handles job duplicate detection using multiple strategies."""

    def __init__(self, db_manager: DatabaseManager, similarity_threshold: float = 0.85):
        self.db_manager = db_manager
        self.similarity_threshold = similarity_threshold

    def find_duplicates(
        self, job_data: Dict[str, Any], session: Session
    ) -> Optional[str]:
        """
        Find potential duplicates of the given job.
        Returns the canonical job ID if a duplicate is found.
        """
        # Strategy 1: Exact URL match (most reliable)
        if job_url := job_data.get("job_url"):
            existing = (
                session.query(JobListingDB)
                .filter(
                    JobListingDB.job_url == job_url,
                    JobListingDB.status == JobStatus.ACTIVE,
                )
                .first()
            )
            if existing:
                logger.debug(f"Found exact URL match for job: {existing.id}")
                return existing.id

        # Strategy 2: Title + Company + Location match
        title_match = self._find_by_title_company_location(job_data, session)
        if title_match:
            return title_match

        # Strategy 3: Content similarity (for future implementation)
        # This would use job description embeddings for semantic similarity

        return None

    def _find_by_title_company_location(
        self, job_data: Dict[str, Any], session: Session
    ) -> Optional[str]:
        """Find duplicates by matching title, company, and location."""
        title = job_data.get("title", "").strip().lower()
        company = job_data.get("company", "").strip().lower()
        job_data.get("location", "").strip().lower()

        if not title or not company:
            return None

        # Look for jobs with similar title and company
        candidates = (
            session.query(JobListingDB)
            .filter(
                and_(
                    JobListingDB.title.ilike(f"%{title}%"),
                    JobListingDB.company.ilike(f"%{company}%"),
                    JobListingDB.status == JobStatus.ACTIVE,
                )
            )
            .limit(10)
            .all()
        )  # Limit to avoid performance issues

        for candidate in candidates:
            if (
                self._calculate_similarity_score(job_data, candidate)
                > self.similarity_threshold
            ):
                logger.debug(f"Found similar job match: {candidate.id}")
                return candidate.id

        return None

    def _calculate_similarity_score(
        self, job_data: Dict[str, Any], existing_job: JobListingDB
    ) -> float:
        """Calculate similarity score between job data and existing job."""
        score = 0.0
        total_weight = 0.0

        # Title similarity (weight: 0.4)
        title_sim = self._text_similarity(
            job_data.get("title", ""), existing_job.title or ""
        )
        score += title_sim * 0.4
        total_weight += 0.4

        # Company similarity (weight: 0.3)
        company_sim = self._text_similarity(
            job_data.get("company", ""), existing_job.company or ""
        )
        score += company_sim * 0.3
        total_weight += 0.3

        # Location similarity (weight: 0.2)
        location_sim = self._text_similarity(
            job_data.get("location", ""), existing_job.location or ""
        )
        score += location_sim * 0.2
        total_weight += 0.2

        # Salary similarity (weight: 0.1)
        if job_data.get("salary_min") and existing_job.salary_min:
            salary_diff = abs(job_data["salary_min"] - existing_job.salary_min)
            salary_avg = (job_data["salary_min"] + existing_job.salary_min) / 2
            salary_sim = max(0, 1 - (salary_diff / salary_avg))
            score += salary_sim * 0.1
            total_weight += 0.1

        return score / total_weight if total_weight > 0 else 0.0

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (Jaccard similarity)."""
        if not text1 or not text2:
            return 0.0

        # Simple word-based Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0


class JobDataLoader:
    """Loads processed job data into the database with deduplication and embedding support."""

    def __init__(self, db_manager: DatabaseManager, settings=None):
        self.db_manager = db_manager
        self.settings = settings
        self.duplicate_detector = DuplicationDetector(db_manager)

        # Load counters for batch processing
        self.batch_stats = {
            "jobs_loaded": 0,
            "duplicates_found": 0,
            "duplicates_merged": 0,
            "embeddings_generated": 0,
            "errors": 0,
        }

    async def load_processed_batch(self, processing_id: str) -> str:
        """
        Load a batch of processed jobs from ProcessedJobDataDB into the main job tables.
        Returns the operation log ID.
        """
        logger.info(f"Starting load operation for processing batch {processing_id}")

        # Start operation log
        operation_log = await self._start_operation_log(
            "batch_load", {"processing_id": processing_id}
        )

        try:
            # Load processed job data
            processed_jobs = await self._get_processed_jobs(processing_id)

            if not processed_jobs:
                logger.warning(
                    f"No processed jobs found for processing ID {processing_id}"
                )
                await self._complete_operation_log(
                    operation_log.id,
                    ETLProcessingStatus.COMPLETED,
                    {"jobs_processed": 0, "message": "No jobs to process"},
                )
                return operation_log.id

            # Process each job
            for processed_job in processed_jobs:
                try:
                    await self._load_single_job(processed_job)
                    self.batch_stats["jobs_loaded"] += 1

                    # Update job load status
                    await self._update_processed_job_status(
                        processed_job.processing_id,
                        processed_job.job_index,
                        ETLProcessingStatus.COMPLETED,
                    )

                except Exception as e:
                    logger.error(f"Error loading job {processed_job.job_index}: {e}")
                    self.batch_stats["errors"] += 1

                    # Update job load status
                    await self._update_processed_job_status(
                        processed_job.processing_id,
                        processed_job.job_index,
                        ETLProcessingStatus.FAILED,
                    )
                    continue

            # Complete operation log
            status = (
                ETLProcessingStatus.COMPLETED
                if self.batch_stats["errors"] == 0
                else ETLProcessingStatus.PARTIAL
            )
            await self._complete_operation_log(
                operation_log.id, status, dict(self.batch_stats)
            )

            logger.info(f"Completed loading batch {processing_id}: {self.batch_stats}")

        except Exception as e:
            logger.error(f"Fatal error loading batch {processing_id}: {e}")
            await self._complete_operation_log(
                operation_log.id,
                ETLProcessingStatus.FAILED,
                {"error": str(e), "stats": self.batch_stats},
            )
            raise

        return operation_log.id

    async def _load_single_job(self, processed_job: ProcessedJobData):
        """Load a single processed job into the database."""
        with self.db_manager.get_session() as session:
            # Check for duplicates
            duplicate_job_id = None
            if not processed_job.duplicate_of:
                duplicate_job_id = self.duplicate_detector.find_duplicates(
                    processed_job.processed_data, session
                )
            else:
                duplicate_job_id = processed_job.duplicate_of

            if duplicate_job_id:
                # Handle duplicate job
                await self._handle_duplicate_job(
                    processed_job, duplicate_job_id, session
                )
                self.batch_stats["duplicates_found"] += 1
            else:
                # Create new job
                job_id = await self._create_new_job(processed_job, session)

                # Generate embeddings
                if processed_job.embedding_vector:
                    await self._store_job_embeddings(job_id, processed_job, session)
                    self.batch_stats["embeddings_generated"] += 1

            session.commit()

    async def _create_new_job(
        self, processed_job: ProcessedJobData, session: Session
    ) -> str:
        """Create a new job listing in the database."""
        job_data = processed_job.processed_data.copy()

        # Ensure required fields
        job_data["id"] = str(uuid4())
        job_data["status"] = JobStatus.ACTIVE
        job_data["created_at"] = datetime.utcnow()
        job_data["updated_at"] = datetime.utcnow()

        # Create JobListing Pydantic model
        job_listing = JobListing(**job_data)

        # Convert to SQLAlchemy and save
        job_db = pydantic_to_sqlalchemy(job_listing, JobListingDB)
        session.add(job_db)
        session.flush()  # Get the ID

        logger.debug(f"Created new job: {job_db.id}")
        return job_db.id

    async def _handle_duplicate_job(
        self, processed_job: ProcessedJobData, duplicate_job_id: str, session: Session
    ):
        """Handle a duplicate job by updating the existing one or recording the duplicate relationship."""
        # Get the existing job
        existing_job = (
            session.query(JobListingDB)
            .filter(JobListingDB.id == duplicate_job_id)
            .first()
        )

        if not existing_job:
            logger.warning(
                f"Duplicate job {duplicate_job_id} not found, creating new job"
            )
            await self._create_new_job(processed_job, session)
            return

        # Update source count
        existing_job.source_count = (existing_job.source_count or 1) + 1
        existing_job.updated_at = datetime.utcnow()

        # Create a new job entry for the duplicate source
        new_job_data = processed_job.processed_data.copy()
        new_job_data["id"] = str(uuid4())
        new_job_data["canonical_id"] = duplicate_job_id
        new_job_data["status"] = JobStatus.ACTIVE
        new_job_data["created_at"] = datetime.utcnow()
        new_job_data["updated_at"] = datetime.utcnow()

        new_job_listing = JobListing(**new_job_data)
        new_job_db = pydantic_to_sqlalchemy(new_job_listing, JobListingDB)
        session.add(new_job_db)
        session.flush()

        # Record the duplication relationship
        duplication = JobDeduplicationDB(
            id=str(uuid4()),
            canonical_job_id=duplicate_job_id,
            duplicate_job_id=new_job_db.id,
            confidence_score=0.9,  # High confidence from our detection
            matching_fields=["title", "company", "location"],
            merge_strategy="keep_canonical",
            reviewed=False,
            created_at=datetime.utcnow(),
        )
        session.add(duplication)

        self.batch_stats["duplicates_merged"] += 1
        logger.debug(
            f"Handled duplicate job: canonical={duplicate_job_id}, duplicate={new_job_db.id}"
        )

    async def _store_job_embeddings(
        self, job_id: str, processed_job: ProcessedJobData, session: Session
    ):
        """Store job embeddings in the database."""
        if not processed_job.embedding_vector:
            return

        # Create content hash
        content = (
            processed_job.processed_data.get("description", "")
            + " "
            + processed_job.processed_data.get("title", "")
        )
        content_hash = hashlib.md5(content.encode()).hexdigest()

        embedding = JobEmbeddingDB(
            id=str(uuid4()),
            job_id=job_id,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",  # Default model
            content_hash=content_hash,
            embedding_vector=processed_job.embedding_vector,
            embedding_dimension=len(processed_job.embedding_vector),
            content_type="job_description",
            created_at=datetime.utcnow(),
        )

        session.add(embedding)
        logger.debug(f"Stored embeddings for job {job_id}")

    async def _get_processed_jobs(self, processing_id: str) -> List[ProcessedJobData]:
        """Get all processed jobs for a processing batch."""
        processed_jobs = []

        try:
            with self.db_manager.get_session() as session:
                jobs_db = (
                    session.query(ProcessedJobDataDB)
                    .filter(
                        and_(
                            ProcessedJobDataDB.processing_id == processing_id,
                            ProcessedJobDataDB.load_status
                            == ETLProcessingStatus.PENDING,
                        )
                    )
                    .order_by(ProcessedJobDataDB.job_index)
                    .all()
                )

                for job_db in jobs_db:
                    processed_job = ProcessedJobData(
                        processing_id=job_db.processing_id,
                        job_index=job_db.job_index,
                        processed_data=job_db.processed_data,
                        embedding_vector=job_db.embedding_vector,
                        duplicate_of=job_db.duplicate_of,
                        load_status=job_db.load_status,
                        quality_score=job_db.quality_score,
                        validation_errors=job_db.validation_errors or [],
                        created_at=job_db.created_at,
                    )
                    processed_jobs.append(processed_job)

        except Exception as e:
            logger.error(f"Error getting processed jobs for {processing_id}: {e}")
            raise

        return processed_jobs

    async def _update_processed_job_status(
        self, processing_id: str, job_index: int, status: ETLProcessingStatus
    ):
        """Update the load status of a processed job."""
        try:
            with self.db_manager.get_session() as session:
                job_db = (
                    session.query(ProcessedJobDataDB)
                    .filter(
                        and_(
                            ProcessedJobDataDB.processing_id == processing_id,
                            ProcessedJobDataDB.job_index == job_index,
                        )
                    )
                    .first()
                )

                if job_db:
                    job_db.load_status = status
                    session.commit()

        except Exception as e:
            logger.error(f"Error updating processed job status: {e}")

    async def _start_operation_log(
        self, operation_name: str, input_data: Dict[str, Any]
    ) -> ETLOperationLog:
        """Start logging an ETL operation."""
        operation_log = ETLOperationLog(
            operation_type=ETLOperationType.LOADING,
            operation_name=operation_name,
            status=ETLProcessingStatus.PROCESSING,
            input_data=input_data,
        )

        try:
            with self.db_manager.get_session() as session:
                log_db = pydantic_to_sqlalchemy(operation_log, ETLOperationLogDB)
                session.add(log_db)
                session.flush()

                # Update with actual ID from database
                operation_log.id = log_db.id

        except Exception as e:
            logger.error(f"Error starting operation log: {e}")
            raise

        return operation_log

    async def _complete_operation_log(
        self,
        operation_id: str,
        status: ETLProcessingStatus,
        output_data: Optional[Dict[str, Any]] = None,
    ):
        """Complete an ETL operation log."""
        try:
            with self.db_manager.get_session() as session:
                log_db = (
                    session.query(ETLOperationLogDB)
                    .filter(ETLOperationLogDB.id == operation_id)
                    .first()
                )

                if log_db:
                    log_db.completed_at = datetime.utcnow()
                    log_db.status = status
                    log_db.duration_ms = int(
                        (log_db.completed_at - log_db.started_at).total_seconds() * 1000
                    )
                    if output_data:
                        log_db.output_data = output_data

                    session.flush()

        except Exception as e:
            logger.error(f"Error completing operation log: {e}")

    async def cleanup_old_duplicates(self, days_old: int = 30) -> int:
        """Clean up old unreviewed duplicate records."""
        cleanup_date = datetime.utcnow() - timedelta(days=days_old)
        cleaned_count = 0

        try:
            with self.db_manager.get_session() as session:
                old_duplicates = (
                    session.query(JobDeduplicationDB)
                    .filter(
                        and_(
                            JobDeduplicationDB.reviewed == False,
                            JobDeduplicationDB.created_at < cleanup_date,
                            JobDeduplicationDB.confidence_score
                            < 0.7,  # Only low confidence ones
                        )
                    )
                    .all()
                )

                for duplicate in old_duplicates:
                    session.delete(duplicate)
                    cleaned_count += 1

                session.commit()
                logger.info(f"Cleaned up {cleaned_count} old duplicate records")

        except Exception as e:
            logger.error(f"Error cleaning up duplicates: {e}")
            raise

        return cleaned_count

    async def get_load_statistics(self, start_date: datetime = None) -> Dict[str, Any]:
        """Get loading statistics."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)

        stats = {}

        try:
            with self.db_manager.get_session() as session:
                # Count total jobs loaded
                total_jobs = (
                    session.query(JobListingDB)
                    .filter(JobListingDB.created_at >= start_date)
                    .count()
                )

                # Count duplicates found
                total_duplicates = (
                    session.query(JobDeduplicationDB)
                    .filter(JobDeduplicationDB.created_at >= start_date)
                    .count()
                )

                # Count embeddings generated
                total_embeddings = (
                    session.query(JobEmbeddingDB)
                    .filter(JobEmbeddingDB.created_at >= start_date)
                    .count()
                )

                # Get recent operations
                recent_ops = (
                    session.query(ETLOperationLogDB)
                    .filter(
                        and_(
                            ETLOperationLogDB.operation_type
                            == ETLOperationType.LOADING,
                            ETLOperationLogDB.started_at >= start_date,
                        )
                    )
                    .count()
                )

                stats = {
                    "total_jobs_loaded": total_jobs,
                    "duplicates_found": total_duplicates,
                    "embeddings_generated": total_embeddings,
                    "load_operations": recent_ops,
                    "period_start": start_date.isoformat(),
                    "period_end": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error getting load statistics: {e}")
            stats = {"error": str(e)}

        return stats


# Utility functions for batch operations
async def load_all_pending_batches(loader: JobDataLoader) -> Dict[str, Any]:
    """Load all pending processed job batches."""
    results = {
        "batches_processed": 0,
        "total_jobs_loaded": 0,
        "errors": 0,
        "batch_results": [],
    }

    try:
        with loader.db_manager.get_session() as session:
            # Find all processing batches that have pending jobs to load
            pending_batches = (
                session.query(ProcessedJobDataDB.processing_id)
                .filter(ProcessedJobDataDB.load_status == ETLProcessingStatus.PENDING)
                .distinct()
                .all()
            )

            for (processing_id,) in pending_batches:
                try:
                    operation_id = await loader.load_processed_batch(processing_id)
                    results["batches_processed"] += 1
                    results["total_jobs_loaded"] += loader.batch_stats["jobs_loaded"]

                    results["batch_results"].append(
                        {
                            "processing_id": processing_id,
                            "operation_id": operation_id,
                            "status": "success",
                            "stats": dict(loader.batch_stats),
                        }
                    )

                    # Reset batch stats for next batch
                    loader.batch_stats = {k: 0 for k in loader.batch_stats}

                except Exception as e:
                    logger.error(f"Error loading batch {processing_id}: {e}")
                    results["errors"] += 1
                    results["batch_results"].append(
                        {
                            "processing_id": processing_id,
                            "status": "error",
                            "error": str(e),
                        }
                    )
                    continue

    except Exception as e:
        logger.error(f"Error in load_all_pending_batches: {e}")
        results["fatal_error"] = str(e)

    return results
