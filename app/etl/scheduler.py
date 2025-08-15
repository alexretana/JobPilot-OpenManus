"""
JobPilot ETL Scheduler and Orchestrator
Manages the complete ETL pipeline execution with scheduling and coordination.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobExecutionEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ..data.models import ETLOperationLogDB, ETLProcessingStatus, RawJobCollection
from ..database.manager import DatabaseManager
from .collector import JSearchDataCollector
from .loader import JobDataLoader, load_all_pending_batches
from .processor import JobDataProcessor


# Settings will be passed as parameter


logger = logging.getLogger(__name__)


class ETLPhase(str, Enum):
    """ETL pipeline phases."""

    COLLECTION = "collection"
    PROCESSING = "processing"
    LOADING = "loading"
    CLEANUP = "cleanup"
    MAINTENANCE = "maintenance"


@dataclass
class ETLJobConfig:
    """Configuration for an ETL job."""

    name: str
    phase: ETLPhase
    schedule: str  # Cron expression or interval
    enabled: bool = True
    max_retries: int = 3
    retry_delay_minutes: int = 5
    timeout_minutes: int = 30
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ETLExecutionResult:
    """Result of an ETL execution."""

    job_name: str
    phase: ETLPhase
    status: ETLProcessingStatus
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    operation_id: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class ETLOrchestrator:
    """Orchestrates the complete ETL pipeline execution."""

    def __init__(self, db_manager: DatabaseManager, settings=None):
        self.db_manager = db_manager
        self.settings = settings

        # Initialize ETL components
        # Get basic config from settings for collector and processor
        basic_config = settings.basic_config if settings else None
        self.collector = JSearchDataCollector(basic_config)
        self.processor = JobDataProcessor(basic_config)
        self.loader = JobDataLoader(db_manager, settings)

        # Execution state
        self.execution_results: List[ETLExecutionResult] = []
        self.active_jobs: Dict[str, asyncio.Task] = {}

    async def run_full_pipeline(
        self, collection_params: Dict[str, Any] = None, max_concurrent_jobs: int = 3
    ) -> Dict[str, Any]:
        """
        Run the complete ETL pipeline: Collect -> Process -> Load.
        Returns execution summary.
        """
        pipeline_start = datetime.utcnow()
        results = {
            "started_at": pipeline_start.isoformat(),
            "phases": {},
            "overall_status": ETLProcessingStatus.PROCESSING,
            "total_duration_seconds": 0,
            "errors": [],
        }

        logger.info("Starting full ETL pipeline execution")

        try:
            # Phase 1: Collection
            logger.info("Phase 1: Data Collection")
            collection_result = await self._run_collection_phase(
                collection_params or {}
            )
            results["phases"]["collection"] = collection_result

            if collection_result["status"] != ETLProcessingStatus.COMPLETED:
                results["overall_status"] = ETLProcessingStatus.FAILED
                results["errors"].append("Collection phase failed")
                return results

            # Phase 2: Processing
            logger.info("Phase 2: Data Processing")
            processing_result = await self._run_processing_phase(max_concurrent_jobs)
            results["phases"]["processing"] = processing_result

            if processing_result["status"] != ETLProcessingStatus.COMPLETED:
                results["overall_status"] = ETLProcessingStatus.PARTIAL
                results["errors"].append("Processing phase partially failed")

            # Phase 3: Loading
            logger.info("Phase 3: Data Loading")
            loading_result = await self._run_loading_phase()
            results["phases"]["loading"] = loading_result

            if loading_result["status"] != ETLProcessingStatus.COMPLETED:
                results["overall_status"] = ETLProcessingStatus.PARTIAL
                results["errors"].append("Loading phase partially failed")

            # Set final status
            if results["overall_status"] == ETLProcessingStatus.PROCESSING:
                results["overall_status"] = ETLProcessingStatus.COMPLETED

        except Exception as e:
            logger.error(f"Fatal error in ETL pipeline: {e}")
            results["overall_status"] = ETLProcessingStatus.FAILED
            results["errors"].append(f"Pipeline failed: {str(e)}")

        finally:
            pipeline_end = datetime.utcnow()
            results["completed_at"] = pipeline_end.isoformat()
            results["total_duration_seconds"] = (
                pipeline_end - pipeline_start
            ).total_seconds()

            logger.info(
                f"ETL pipeline completed: {results['overall_status']} in {results['total_duration_seconds']}s"
            )

        return results

    async def _run_collection_phase(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run the data collection phase."""
        phase_start = datetime.utcnow()
        result = {
            "status": ETLProcessingStatus.PROCESSING,
            "started_at": phase_start.isoformat(),
            "collections_created": 0,
            "errors": [],
        }

        try:
            # Use default queries if none provided
            if not params.get("queries"):
                collection_results = await self.collector.collect_default_queries()

                total_collections = sum(len(ids) for ids in collection_results.values())
                result["collections_created"] = total_collections
                result["query_results"] = collection_results

            else:
                # Custom collection parameters
                collection_ids = []
                for query_config in params["queries"]:
                    ids = await self.collector.collect_jobs(
                        query=query_config.get("query", ""),
                        location=query_config.get("location", ""),
                        page=query_config.get("page", 1),
                        num_pages=query_config.get("num_pages", 1),
                    )
                    collection_ids.extend(ids)

                result["collections_created"] = len(collection_ids)
                result["collection_ids"] = collection_ids

            result["status"] = ETLProcessingStatus.COMPLETED

        except Exception as e:
            logger.error(f"Collection phase failed: {e}")
            result["status"] = ETLProcessingStatus.FAILED
            result["errors"].append(str(e))

        finally:
            phase_end = datetime.utcnow()
            result["completed_at"] = phase_end.isoformat()
            result["duration_seconds"] = (phase_end - phase_start).total_seconds()

        return result

    async def _run_processing_phase(self, max_concurrent: int = 3) -> Dict[str, Any]:
        """Run the data processing phase."""
        phase_start = datetime.utcnow()
        result = {
            "status": ETLProcessingStatus.PROCESSING,
            "started_at": phase_start.isoformat(),
            "collections_processed": 0,
            "jobs_processed": 0,
            "errors": [],
        }

        try:
            # Get pending collections
            pending_collections = await self.collector.get_pending_collections(limit=50)

            if not pending_collections:
                logger.info("No pending collections to process")
                result["status"] = ETLProcessingStatus.COMPLETED
                return result

            # Process collections with concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_collection(collection: RawJobCollection):
                async with semaphore:
                    try:
                        processing_id = await self.processor.process_collection(
                            collection.id
                        )
                        return {
                            "collection_id": collection.id,
                            "processing_id": processing_id,
                            "status": "success",
                        }
                    except Exception as e:
                        logger.error(
                            f"Error processing collection {collection.id}: {e}"
                        )
                        return {
                            "collection_id": collection.id,
                            "error": str(e),
                            "status": "error",
                        }

            # Execute processing tasks
            processing_tasks = [
                process_collection(collection) for collection in pending_collections
            ]
            processing_results = await asyncio.gather(
                *processing_tasks, return_exceptions=True
            )

            # Analyze results
            successful_processing = 0
            failed_processing = 0

            for processing_result in processing_results:
                if isinstance(processing_result, Exception):
                    failed_processing += 1
                    result["errors"].append(str(processing_result))
                elif processing_result.get("status") == "success":
                    successful_processing += 1
                else:
                    failed_processing += 1
                    result["errors"].append(
                        processing_result.get("error", "Unknown processing error")
                    )

            result["collections_processed"] = successful_processing
            result["collections_failed"] = failed_processing

            # Determine status
            if failed_processing == 0:
                result["status"] = ETLProcessingStatus.COMPLETED
            elif successful_processing > 0:
                result["status"] = ETLProcessingStatus.PARTIAL
            else:
                result["status"] = ETLProcessingStatus.FAILED

        except Exception as e:
            logger.error(f"Processing phase failed: {e}")
            result["status"] = ETLProcessingStatus.FAILED
            result["errors"].append(str(e))

        finally:
            phase_end = datetime.utcnow()
            result["completed_at"] = phase_end.isoformat()
            result["duration_seconds"] = (phase_end - phase_start).total_seconds()

        return result

    async def _run_loading_phase(self) -> Dict[str, Any]:
        """Run the data loading phase."""
        phase_start = datetime.utcnow()
        result = {
            "status": ETLProcessingStatus.PROCESSING,
            "started_at": phase_start.isoformat(),
            "batches_loaded": 0,
            "jobs_loaded": 0,
            "errors": [],
        }

        try:
            # Load all pending batches
            loading_results = await load_all_pending_batches(self.loader)

            result["batches_loaded"] = loading_results["batches_processed"]
            result["jobs_loaded"] = loading_results["total_jobs_loaded"]
            result["batch_results"] = loading_results["batch_results"]

            if loading_results.get("fatal_error"):
                result["status"] = ETLProcessingStatus.FAILED
                result["errors"].append(loading_results["fatal_error"])
            elif loading_results["errors"] > 0:
                result["status"] = ETLProcessingStatus.PARTIAL
                result["errors"] = [
                    br.get("error")
                    for br in loading_results["batch_results"]
                    if br.get("status") == "error"
                ]
            else:
                result["status"] = ETLProcessingStatus.COMPLETED

        except Exception as e:
            logger.error(f"Loading phase failed: {e}")
            result["status"] = ETLProcessingStatus.FAILED
            result["errors"].append(str(e))

        finally:
            phase_end = datetime.utcnow()
            result["completed_at"] = phase_end.isoformat()
            result["duration_seconds"] = (phase_end - phase_start).total_seconds()

        return result

    async def run_maintenance_tasks(self) -> Dict[str, Any]:
        """Run maintenance tasks like cleanup, statistics generation, etc."""
        maintenance_start = datetime.utcnow()
        result = {
            "started_at": maintenance_start.isoformat(),
            "tasks_completed": 0,
            "tasks": {},
            "errors": [],
        }

        try:
            # Task 1: Cleanup old duplicates
            logger.info("Running duplicate cleanup")
            duplicates_cleaned = await self.loader.cleanup_old_duplicates(days_old=30)
            result["tasks"]["duplicate_cleanup"] = {
                "status": "completed",
                "records_cleaned": duplicates_cleaned,
            }
            result["tasks_completed"] += 1

            # Task 2: Generate statistics
            logger.info("Generating ETL statistics")
            stats = await self._generate_etl_statistics()
            result["tasks"]["statistics"] = {"status": "completed", "stats": stats}
            result["tasks_completed"] += 1

            # Task 3: Database optimization (if needed)
            # This could include VACUUM, ANALYZE, index maintenance, etc.
            logger.info("Running database maintenance")
            db_maintenance_result = await self._run_database_maintenance()
            result["tasks"]["database_maintenance"] = db_maintenance_result
            result["tasks_completed"] += 1

        except Exception as e:
            logger.error(f"Maintenance tasks failed: {e}")
            result["errors"].append(str(e))

        finally:
            maintenance_end = datetime.utcnow()
            result["completed_at"] = maintenance_end.isoformat()
            result["duration_seconds"] = (
                maintenance_end - maintenance_start
            ).total_seconds()

        return result

    async def _generate_etl_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive ETL statistics."""
        stats = {}

        try:
            # Get collection statistics
            collection_stats = await self.collector.get_collection_statistics()
            stats["collection"] = collection_stats

            # Get processing statistics
            processing_stats = await self.processor.get_processing_statistics()
            stats["processing"] = processing_stats

            # Get loading statistics
            loading_stats = await self.loader.get_load_statistics()
            stats["loading"] = loading_stats

            # Overall pipeline health
            stats["pipeline_health"] = await self._assess_pipeline_health()

        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            stats["error"] = str(e)

        return stats

    async def _assess_pipeline_health(self) -> Dict[str, Any]:
        """Assess overall pipeline health."""
        health = {"status": "healthy", "issues": [], "recommendations": []}

        try:
            # Check recent operation success rates
            recent_operations = await self._get_recent_operations(hours=24)

            if recent_operations:
                failed_ops = [
                    op
                    for op in recent_operations
                    if op["status"] == ETLProcessingStatus.FAILED
                ]
                failure_rate = len(failed_ops) / len(recent_operations)

                if failure_rate > 0.2:  # More than 20% failure rate
                    health["status"] = "unhealthy"
                    health["issues"].append(f"High failure rate: {failure_rate:.1%}")
                    health["recommendations"].append(
                        "Investigate recurring failures and improve error handling"
                    )

                elif failure_rate > 0.1:  # More than 10% failure rate
                    health["status"] = "warning"
                    health["issues"].append(
                        f"Elevated failure rate: {failure_rate:.1%}"
                    )
                    health["recommendations"].append("Monitor for patterns in failures")

            # Check for stale data
            with self.db_manager.get_session() as session:
                from ..data.models import RawJobCollectionDB

                latest_collection = (
                    session.query(RawJobCollectionDB)
                    .order_by(RawJobCollectionDB.created_at.desc())
                    .first()
                )

                if latest_collection:
                    hours_since_collection = (
                        datetime.utcnow() - latest_collection.created_at
                    ).total_seconds() / 3600
                    if hours_since_collection > 48:  # No collection in 48 hours
                        health["status"] = "warning"
                        health["issues"].append(
                            f"No data collection in {hours_since_collection:.1f} hours"
                        )
                        health["recommendations"].append(
                            "Check collection schedule and API connectivity"
                        )

        except Exception as e:
            health["status"] = "error"
            health["issues"].append(f"Health assessment failed: {str(e)}")

        return health

    async def _get_recent_operations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent ETL operations for health assessment."""
        operations = []

        try:
            with self.db_manager.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)

                recent_ops = (
                    session.query(ETLOperationLogDB)
                    .filter(ETLOperationLogDB.started_at >= cutoff_time)
                    .order_by(ETLOperationLogDB.started_at.desc())
                    .all()
                )

                for op in recent_ops:
                    operations.append(
                        {
                            "id": op.id,
                            "operation_type": op.operation_type,
                            "operation_name": op.operation_name,
                            "status": op.status,
                            "started_at": op.started_at,
                            "completed_at": op.completed_at,
                            "duration_ms": op.duration_ms,
                        }
                    )

        except Exception as e:
            logger.error(f"Error getting recent operations: {e}")

        return operations

    async def _run_database_maintenance(self) -> Dict[str, Any]:
        """Run database maintenance tasks."""
        maintenance_result = {"status": "completed", "tasks": []}

        try:
            # For SQLite, we might run VACUUM and ANALYZE
            # For PostgreSQL, we might run VACUUM ANALYZE
            # This is database-specific and should be adapted

            with self.db_manager.get_session() as session:
                if self.db_manager.engine.dialect.name == "sqlite":
                    session.execute("VACUUM")
                    maintenance_result["tasks"].append("VACUUM completed")

                    session.execute("ANALYZE")
                    maintenance_result["tasks"].append("ANALYZE completed")

                elif self.db_manager.engine.dialect.name == "postgresql":
                    # PostgreSQL maintenance would go here
                    pass

                session.commit()

        except Exception as e:
            logger.error(f"Database maintenance failed: {e}")
            maintenance_result["status"] = "failed"
            maintenance_result["error"] = str(e)

        return maintenance_result


class ETLScheduler:
    """Handles scheduling and execution of ETL jobs."""

    def __init__(self, orchestrator: ETLOrchestrator, settings=None):
        self.orchestrator = orchestrator
        self.settings = settings
        self.scheduler = AsyncIOScheduler()

        # Default job configurations
        self.default_jobs = [
            ETLJobConfig(
                name="daily_full_pipeline",
                phase=ETLPhase.COLLECTION,
                schedule="0 2 * * *",  # Daily at 2 AM
                timeout_minutes=120,
                parameters={},
            ),
            ETLJobConfig(
                name="hourly_quick_collection",
                phase=ETLPhase.COLLECTION,
                schedule="0 * * * *",  # Every hour
                timeout_minutes=30,
                parameters={"quick_mode": True, "max_pages": 1},
            ),
            ETLJobConfig(
                name="maintenance_tasks",
                phase=ETLPhase.MAINTENANCE,
                schedule="0 4 * * 0",  # Weekly on Sunday at 4 AM
                timeout_minutes=60,
                parameters={},
            ),
        ]

        # Load custom jobs from settings
        self.jobs = self._load_job_configurations()

        # Setup event listeners
        self.scheduler.add_listener(
            self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )

    def _load_job_configurations(self) -> List[ETLJobConfig]:
        """Load job configurations from settings and defaults."""
        jobs = self.default_jobs.copy()

        # Add any custom jobs from settings
        if hasattr(self.settings, "etl_jobs") and self.settings.etl_jobs:
            for job_config in self.settings.etl_jobs:
                jobs.append(ETLJobConfig(**job_config))

        return jobs

    def start(self):
        """Start the scheduler and add all configured jobs."""
        logger.info("Starting ETL scheduler")

        # Add all configured jobs
        for job_config in self.jobs:
            if job_config.enabled:
                self._add_scheduled_job(job_config)

        self.scheduler.start()
        logger.info(f"ETL scheduler started with {len(self.jobs)} jobs")

    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping ETL scheduler")
        self.scheduler.shutdown()

    def _add_scheduled_job(self, job_config: ETLJobConfig):
        """Add a job to the scheduler."""
        try:
            # Parse schedule (support both cron and interval formats)
            if job_config.schedule.count(" ") == 4:  # Cron format
                trigger = CronTrigger.from_crontab(job_config.schedule)
            else:  # Assume interval format like "30m", "1h", "1d"
                trigger = self._parse_interval_schedule(job_config.schedule)

            # Determine job function based on phase
            job_func = self._get_job_function(job_config.phase)

            self.scheduler.add_job(
                job_func,
                trigger=trigger,
                id=job_config.name,
                name=job_config.name,
                kwargs={"job_config": job_config, "parameters": job_config.parameters},
                max_instances=1,  # Prevent overlapping executions
                coalesce=True,  # If multiple executions are scheduled, run only the latest
                misfire_grace_time=300,  # 5 minutes grace period
            )

            logger.info(
                f"Scheduled job '{job_config.name}' with schedule '{job_config.schedule}'"
            )

        except Exception as e:
            logger.error(f"Failed to schedule job '{job_config.name}': {e}")

    def _parse_interval_schedule(self, schedule: str) -> IntervalTrigger:
        """Parse interval schedule format like '30m', '1h', '2d'."""
        import re

        match = re.match(r"(\d+)([smhd])", schedule.lower())
        if not match:
            raise ValueError(f"Invalid interval schedule format: {schedule}")

        value, unit = match.groups()
        value = int(value)

        if unit == "s":
            return IntervalTrigger(seconds=value)
        elif unit == "m":
            return IntervalTrigger(minutes=value)
        elif unit == "h":
            return IntervalTrigger(hours=value)
        elif unit == "d":
            return IntervalTrigger(days=value)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")

    def _get_job_function(self, phase: ETLPhase) -> Callable:
        """Get the appropriate job function for the given phase."""
        if phase == ETLPhase.COLLECTION:
            return self._run_collection_job
        elif phase == ETLPhase.PROCESSING:
            return self._run_processing_job
        elif phase == ETLPhase.LOADING:
            return self._run_loading_job
        elif phase == ETLPhase.MAINTENANCE:
            return self._run_maintenance_job
        else:
            return self._run_full_pipeline_job

    async def _run_collection_job(
        self, job_config: ETLJobConfig, parameters: Dict[str, Any]
    ):
        """Execute a collection job."""
        logger.info(f"Executing collection job: {job_config.name}")

        try:
            result = await self.orchestrator._run_collection_phase(parameters)
            logger.info(
                f"Collection job {job_config.name} completed: {result['status']}"
            )
            return result

        except Exception as e:
            logger.error(f"Collection job {job_config.name} failed: {e}")
            raise

    async def _run_processing_job(
        self, job_config: ETLJobConfig, parameters: Dict[str, Any]
    ):
        """Execute a processing job."""
        logger.info(f"Executing processing job: {job_config.name}")

        try:
            max_concurrent = parameters.get("max_concurrent", 3)
            result = await self.orchestrator._run_processing_phase(max_concurrent)
            logger.info(
                f"Processing job {job_config.name} completed: {result['status']}"
            )
            return result

        except Exception as e:
            logger.error(f"Processing job {job_config.name} failed: {e}")
            raise

    async def _run_loading_job(
        self, job_config: ETLJobConfig, parameters: Dict[str, Any]
    ):
        """Execute a loading job."""
        logger.info(f"Executing loading job: {job_config.name}")

        try:
            result = await self.orchestrator._run_loading_phase()
            logger.info(f"Loading job {job_config.name} completed: {result['status']}")
            return result

        except Exception as e:
            logger.error(f"Loading job {job_config.name} failed: {e}")
            raise

    async def _run_maintenance_job(
        self, job_config: ETLJobConfig, parameters: Dict[str, Any]
    ):
        """Execute a maintenance job."""
        logger.info(f"Executing maintenance job: {job_config.name}")

        try:
            result = await self.orchestrator.run_maintenance_tasks()
            logger.info(
                f"Maintenance job {job_config.name} completed: {len(result.get('tasks', {}))} tasks"
            )
            return result

        except Exception as e:
            logger.error(f"Maintenance job {job_config.name} failed: {e}")
            raise

    async def _run_full_pipeline_job(
        self, job_config: ETLJobConfig, parameters: Dict[str, Any]
    ):
        """Execute a full pipeline job."""
        logger.info(f"Executing full pipeline job: {job_config.name}")

        try:
            result = await self.orchestrator.run_full_pipeline(
                collection_params=parameters.get("collection_params", {}),
                max_concurrent_jobs=parameters.get("max_concurrent", 3),
            )
            logger.info(
                f"Full pipeline job {job_config.name} completed: {result['overall_status']}"
            )
            return result

        except Exception as e:
            logger.error(f"Full pipeline job {job_config.name} failed: {e}")
            raise

    def _job_listener(self, event: JobExecutionEvent):
        """Listen to job execution events."""
        if event.exception:
            logger.error(f"Scheduled job '{event.job_id}' failed: {event.exception}")
        else:
            logger.info(f"Scheduled job '{event.job_id}' completed successfully")

    async def trigger_job(self, job_name: str) -> Dict[str, Any]:
        """Manually trigger a job execution."""
        try:
            job = self.scheduler.get_job(job_name)
            if not job:
                raise ValueError(f"Job '{job_name}' not found")

            logger.info(f"Manually triggering job: {job_name}")

            # Execute the job immediately
            result = await job.func(**job.kwargs)

            return {
                "job_name": job_name,
                "status": "completed",
                "result": result,
                "triggered_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to trigger job '{job_name}': {e}")
            return {
                "job_name": job_name,
                "status": "failed",
                "error": str(e),
                "triggered_at": datetime.utcnow().isoformat(),
            }

    def get_job_status(self) -> Dict[str, Any]:
        """Get status of all scheduled jobs."""
        jobs_status = []

        for job in self.scheduler.get_jobs():
            job_info = {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat()
                if job.next_run_time
                else None,
                "trigger": str(job.trigger),
                "max_instances": job.max_instances,
                "pending": len(
                    [
                        t
                        for t in self.orchestrator.active_jobs.values()
                        if t.get_name() == job.id
                    ]
                ),
            }
            jobs_status.append(job_info)

        return {
            "scheduler_running": self.scheduler.running,
            "total_jobs": len(jobs_status),
            "jobs": jobs_status,
            "checked_at": datetime.utcnow().isoformat(),
        }


# Utility functions for running the ETL system
async def run_etl_system(settings=None):
    """Initialize and start the complete ETL system."""
    from ..database.manager import DatabaseManager

    if not settings:
        raise ValueError("Settings object is required")
    db_manager = DatabaseManager(settings.get_database_url())

    # Initialize orchestrator and scheduler
    orchestrator = ETLOrchestrator(db_manager, settings)
    scheduler = ETLScheduler(orchestrator, settings)

    # Start the scheduler
    scheduler.start()

    logger.info("ETL system started successfully")
    return scheduler


async def run_manual_pipeline(settings=None) -> Dict[str, Any]:
    """Run the ETL pipeline manually (useful for testing)."""
    from ..database.manager import DatabaseManager

    if not settings:
        raise ValueError("Settings object is required")
    db_manager = DatabaseManager(settings.get_database_url())

    orchestrator = ETLOrchestrator(db_manager, settings)
    result = await orchestrator.run_full_pipeline()

    logger.info(f"Manual pipeline execution completed: {result['overall_status']}")
    return result
