"""
JobPilot ETL Enhanced Settings Management
Advanced configuration loading, validation, and environment-specific settings.
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field, validator
from pydantic_settings import BaseSettings

from .config import ETLConfig

logger = logging.getLogger(__name__)


class ETLEnvironment(str, Enum):
    """ETL environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class APIConfiguration:
    """Configuration for external API providers."""

    provider_name: str
    base_url: str
    api_key: Optional[str] = None
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_backoff_factor: float = 2.0
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class SchedulerJobConfig:
    """Configuration for scheduled ETL jobs."""

    name: str
    phase: str  # collection, processing, loading, maintenance
    schedule: str  # Cron expression or interval
    enabled: bool = True
    max_retries: int = 3
    timeout_minutes: int = 30
    parameters: Dict[str, Any] = field(default_factory=dict)


class ETLEnhancedSettings(BaseSettings):
    """Enhanced ETL settings with environment variable support."""

    # Environment and basic settings
    environment: ETLEnvironment = ETLEnvironment.DEVELOPMENT
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO

    # Inherit basic config
    basic_config: ETLConfig = field(default_factory=ETLConfig.from_env)

    # Database settings (extended)
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # API settings (extended)
    rapidapi_key: str = Field(..., description="RapidAPI Key for JSearch")
    jsearch_rate_limit_per_minute: int = Field(
        default=60, env="JSEARCH_RATE_LIMIT_PER_MINUTE"
    )
    jsearch_max_pages_per_query: int = Field(
        default=5, env="JSEARCH_MAX_PAGES_PER_QUERY"
    )
    jsearch_request_timeout: int = Field(default=30, env="JSEARCH_REQUEST_TIMEOUT")

    # Processing settings (extended)
    processing_batch_size: int = Field(default=100, env="PROCESSING_BATCH_SIZE")
    processing_max_concurrent: int = Field(default=3, env="PROCESSING_MAX_CONCURRENT")
    processing_enable_embeddings: bool = Field(
        default=True, env="PROCESSING_ENABLE_EMBEDDINGS"
    )
    processing_enable_deduplication: bool = Field(
        default=True, env="PROCESSING_ENABLE_DEDUPLICATION"
    )
    processing_quality_threshold: float = Field(
        default=0.7, env="PROCESSING_QUALITY_THRESHOLD"
    )

    # Embedding settings
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL"
    )
    embedding_batch_size: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    embedding_cache_size: int = Field(default=1000, env="EMBEDDING_CACHE_SIZE")

    # Deduplication settings
    duplicate_similarity_threshold: float = Field(
        default=0.85, env="DUPLICATE_SIMILARITY_THRESHOLD"
    )
    duplicate_title_weight: float = Field(default=0.4, env="DUPLICATE_TITLE_WEIGHT")
    duplicate_company_weight: float = Field(default=0.3, env="DUPLICATE_COMPANY_WEIGHT")
    duplicate_location_weight: float = Field(
        default=0.2, env="DUPLICATE_LOCATION_WEIGHT"
    )
    duplicate_salary_weight: float = Field(default=0.1, env="DUPLICATE_SALARY_WEIGHT")

    # File storage paths
    data_directory: Path = Field(default=Path("data"), env="ETL_DATA_DIRECTORY")
    logs_directory: Path = Field(default=Path("logs"), env="ETL_LOGS_DIRECTORY")
    config_directory: Path = Field(default=Path("config"), env="ETL_CONFIG_DIRECTORY")

    # Backup and archival
    backup_raw_data: bool = Field(default=True, env="BACKUP_RAW_DATA")
    backup_directory: Path = Field(default=Path("backups"), env="BACKUP_DIRECTORY")
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    data_retention_days: int = Field(default=90, env="DATA_RETENTION_DAYS")

    # Monitoring and alerting
    enable_monitoring: bool = Field(default=True, env="ENABLE_MONITORING")
    monitoring_port: int = Field(default=8000, env="MONITORING_PORT")
    health_check_interval_seconds: int = Field(default=300, env="HEALTH_CHECK_INTERVAL")

    # Alert settings
    alert_failure_rate_threshold: float = Field(
        default=0.2, env="ALERT_FAILURE_RATE_THRESHOLD"
    )
    alert_response_time_threshold: int = Field(
        default=300, env="ALERT_RESPONSE_TIME_THRESHOLD"
    )

    # Email alert settings
    alert_email_enabled: bool = Field(default=False, env="ALERT_EMAIL_ENABLED")
    alert_email_smtp_host: Optional[str] = Field(
        default=None, env="ALERT_EMAIL_SMTP_HOST"
    )
    alert_email_smtp_port: int = Field(default=587, env="ALERT_EMAIL_SMTP_PORT")
    alert_email_username: Optional[str] = Field(
        default=None, env="ALERT_EMAIL_USERNAME"
    )
    alert_email_password: Optional[str] = Field(
        default=None, env="ALERT_EMAIL_PASSWORD"
    )
    alert_email_recipients: List[str] = Field(
        default_factory=list, env="ALERT_EMAIL_RECIPIENTS"
    )

    # Scheduler settings
    scheduler_timezone: str = Field(default="UTC", env="SCHEDULER_TIMEZONE")
    scheduler_max_running_jobs: int = Field(default=5, env="SCHEDULER_MAX_RUNNING_JOBS")
    scheduler_misfire_grace_time: int = Field(
        default=300, env="SCHEDULER_MISFIRE_GRACE_TIME"
    )

    # Performance settings
    max_memory_usage_mb: int = Field(default=2048, env="MAX_MEMORY_USAGE_MB")
    connection_pool_size: int = Field(default=20, env="CONNECTION_POOL_SIZE")
    worker_thread_count: int = Field(default=4, env="WORKER_THREAD_COUNT")

    # Feature flags
    enable_async_processing: bool = Field(default=True, env="ENABLE_ASYNC_PROCESSING")
    enable_job_prioritization: bool = Field(
        default=True, env="ENABLE_JOB_PRIORITIZATION"
    )
    enable_auto_scaling: bool = Field(default=False, env="ENABLE_AUTO_SCALING")

    # Custom job configurations (loaded from files)
    custom_job_configs: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @validator(
        "data_directory", "logs_directory", "config_directory", "backup_directory"
    )
    def ensure_path_exists(cls, v):
        """Ensure directories exist."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v

    @validator("alert_email_recipients", pre=True)
    def parse_email_recipients(cls, v):
        """Parse email recipients from string or list."""
        if isinstance(v, str):
            return [email.strip() for email in v.split(",") if email.strip()]
        return v or []

    @validator("processing_quality_threshold", "duplicate_similarity_threshold")
    def validate_threshold_range(cls, v):
        """Ensure thresholds are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        return v

    def get_api_config(self, provider: str = "jsearch") -> APIConfiguration:
        """Get API configuration for a specific provider."""
        if provider.lower() == "jsearch":
            return APIConfiguration(
                provider_name="jsearch",
                base_url=self.basic_config.jsearch_base_url,
                api_key=self.rapidapi_key,
                rate_limit_requests=self.jsearch_rate_limit_per_minute,
                timeout_seconds=self.jsearch_request_timeout,
                retry_attempts=self.basic_config.max_retries,
                headers={
                    "X-RapidAPI-Key": self.rapidapi_key,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
                },
            )
        else:
            raise ValueError(f"Unknown API provider: {provider}")

    def get_database_url(self) -> str:
        """Get database URL with fallback to basic config."""
        return self.basic_config.database_url

    def get_search_queries(self) -> List[str]:
        """Get search queries with fallback to basic config."""
        return self.basic_config.default_search_queries

    def get_search_locations(self) -> List[str]:
        """Get search locations with fallback to basic config."""
        return self.basic_config.default_locations

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == ETLEnvironment.PRODUCTION

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == ETLEnvironment.DEVELOPMENT

    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        log_level = "DEBUG" if self.debug else self.log_level.value

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d [%(funcName)s]: %(message)s"
                },
            },
            "handlers": {
                "console": {
                    "level": log_level,
                    "formatter": "standard" if not self.debug else "detailed",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "level": log_level,
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.logs_directory / "etl.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                },
                "error_file": {
                    "level": "ERROR",
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.logs_directory / "etl_errors.log"),
                    "maxBytes": 5242880,  # 5MB
                    "backupCount": 3,
                },
            },
            "loggers": {
                "": {  # root logger
                    "handlers": ["console", "file", "error_file"],
                    "level": log_level,
                    "propagate": False,
                },
                "app.etl": {
                    "handlers": ["console", "file", "error_file"],
                    "level": log_level,
                    "propagate": False,
                },
                "sqlalchemy": {
                    "handlers": ["file"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }

    def get_scheduler_jobs(self) -> List[SchedulerJobConfig]:
        """Get scheduler job configurations."""
        jobs = []

        # Default jobs based on environment
        if self.environment == ETLEnvironment.PRODUCTION:
            jobs.extend(
                [
                    SchedulerJobConfig(
                        name="production_daily_full_pipeline",
                        phase="collection",
                        schedule="0 2 * * *",  # Daily at 2 AM
                        timeout_minutes=180,
                        parameters={
                            "collection_params": {"full_collection": True},
                            "max_concurrent": self.processing_max_concurrent,
                        },
                    ),
                    SchedulerJobConfig(
                        name="production_hourly_incremental",
                        phase="collection",
                        schedule="0 * * * *",  # Every hour
                        timeout_minutes=45,
                        parameters={
                            "collection_params": {"incremental": True, "max_pages": 2},
                            "max_concurrent": 2,
                        },
                    ),
                    SchedulerJobConfig(
                        name="production_maintenance",
                        phase="maintenance",
                        schedule="0 4 * * 0",  # Sunday at 4 AM
                        timeout_minutes=120,
                        parameters={"deep_clean": True},
                    ),
                ]
            )
        else:
            # Development/testing jobs
            jobs.extend(
                [
                    SchedulerJobConfig(
                        name="development_test_collection",
                        phase="collection",
                        schedule="0 */6 * * *",  # Every 6 hours
                        timeout_minutes=60,
                        parameters={
                            "collection_params": {"max_pages": 1},
                            "max_concurrent": 1,
                        },
                    ),
                    SchedulerJobConfig(
                        name="development_maintenance",
                        phase="maintenance",
                        schedule="0 3 * * *",  # Daily at 3 AM
                        timeout_minutes=30,
                        parameters={"light_clean": True},
                    ),
                ]
            )

        # Add custom jobs from configuration
        for custom_job in self.custom_job_configs:
            if custom_job.get("enabled", True):
                jobs.append(SchedulerJobConfig(**custom_job))

        return jobs

    def validate_settings(self) -> List[str]:
        """Validate settings and return any issues."""
        issues = []

        # Validate basic config first
        basic_issues = self.basic_config.validate()
        issues.extend(basic_issues)

        # Additional validations
        if self.processing_batch_size <= 0:
            issues.append("Processing batch size must be positive")

        if self.processing_max_concurrent <= 0:
            issues.append("Processing max concurrent must be positive")

        if self.monitoring_port < 1024 or self.monitoring_port > 65535:
            issues.append("Monitoring port must be between 1024 and 65535")

        if self.alert_email_enabled:
            if not self.alert_email_smtp_host:
                issues.append("Email alerts enabled but SMTP host not configured")
            if not self.alert_email_recipients:
                issues.append("Email alerts enabled but no recipients configured")

        # Check directory permissions
        for dir_path in [
            self.data_directory,
            self.logs_directory,
            self.backup_directory,
        ]:
            if not os.access(dir_path, os.W_OK):
                issues.append(f"Directory not writable: {dir_path}")

        return issues

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance-related configuration."""
        return {
            "max_memory_usage_mb": self.max_memory_usage_mb,
            "connection_pool_size": self.connection_pool_size,
            "worker_thread_count": self.worker_thread_count,
            "processing_batch_size": self.processing_batch_size,
            "processing_max_concurrent": self.processing_max_concurrent,
            "embedding_batch_size": self.embedding_batch_size,
            "enable_async_processing": self.enable_async_processing,
        }

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            "enabled": self.enable_monitoring,
            "port": self.monitoring_port,
            "health_check_interval": self.health_check_interval_seconds,
            "alerts": {
                "failure_rate_threshold": self.alert_failure_rate_threshold,
                "response_time_threshold": self.alert_response_time_threshold,
                "email_enabled": self.alert_email_enabled,
                "email_recipients": self.alert_email_recipients,
            },
        }


class ETLSettingsManager:
    """Manages ETL settings loading, validation, and file operations."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config")
        self.config_path.mkdir(parents=True, exist_ok=True)
        self._settings: Optional[ETLEnhancedSettings] = None

    def load_settings(self, env_file: Optional[str] = None) -> ETLEnhancedSettings:
        """Load ETL settings from environment and config files."""
        if self._settings is not None:
            return self._settings

        # Set environment file if provided
        if env_file:
            os.environ.setdefault("ETL_ENV_FILE", env_file)

        try:
            self._settings = ETLEnhancedSettings()

            # Load custom job configurations
            self._load_custom_job_configs()

            logger.info(
                f"Loaded ETL settings for environment: {self._settings.environment}"
            )
            return self._settings

        except Exception as e:
            logger.error(f"Failed to load ETL settings: {e}")
            raise

    def _load_custom_job_configs(self):
        """Load custom job configurations from files."""
        if self._settings is None:
            return

        jobs_config_file = self.config_path / "scheduler_jobs.yaml"
        if jobs_config_file.exists():
            try:
                with open(jobs_config_file, "r", encoding="utf-8") as f:
                    jobs_config = yaml.safe_load(f)

                if jobs_config and "jobs" in jobs_config:
                    self._settings.custom_job_configs = jobs_config["jobs"]
                    logger.info(
                        f"Loaded {len(jobs_config['jobs'])} custom job configurations"
                    )

            except Exception as e:
                logger.error(f"Failed to load custom job configs: {e}")

    def create_sample_files(self):
        """Create sample configuration files."""

        # Sample scheduler jobs
        sample_jobs = {
            "jobs": [
                {
                    "name": "custom_tech_jobs_collection",
                    "phase": "collection",
                    "schedule": "0 */3 * * *",  # Every 3 hours
                    "enabled": True,
                    "timeout_minutes": 45,
                    "parameters": {
                        "collection_params": {
                            "queries": [
                                "python developer",
                                "data scientist",
                                "devops engineer",
                            ],
                            "locations": [
                                "San Francisco, CA",
                                "New York, NY",
                                "Remote",
                            ],
                            "max_pages": 3,
                        }
                    },
                },
                {
                    "name": "weekend_deep_processing",
                    "phase": "processing",
                    "schedule": "0 6 * * 6,0",  # Saturday and Sunday at 6 AM
                    "enabled": True,
                    "timeout_minutes": 120,
                    "parameters": {
                        "max_concurrent": 5,
                        "enable_advanced_matching": True,
                    },
                },
            ]
        }

        # Sample monitoring configuration
        sample_monitoring = {
            "alerts": {
                "failure_rate_threshold": 0.15,
                "response_time_threshold": 300,
                "disk_space_threshold": 0.85,
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "recipients": ["admin@yourcompany.com", "etl-team@yourcompany.com"],
                    "smtp_settings": {
                        "host": "smtp.gmail.com",
                        "port": 587,
                        "use_tls": True,
                    },
                },
                "webhook": {
                    "enabled": False,
                    "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                },
            },
            "dashboards": {"grafana_enabled": False, "prometheus_enabled": False},
        }

        # Save sample files
        with open(self.config_path / "scheduler_jobs_sample.yaml", "w") as f:
            yaml.dump(sample_jobs, f, default_flow_style=False, indent=2)

        with open(self.config_path / "monitoring_sample.yaml", "w") as f:
            yaml.dump(sample_monitoring, f, default_flow_style=False, indent=2)

        # Create comprehensive .env.sample file
        sample_env = """# JobPilot ETL Enhanced Configuration
# Copy this file to .env and update with your actual values

#===========================================
# ENVIRONMENT SETTINGS
#===========================================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

#===========================================
# DATABASE CONFIGURATION
#===========================================
DATABASE_URL=sqlite:///data/jobpilot_etl.db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_ECHO=false

#===========================================
# API CONFIGURATION
#===========================================
# JSearch API (RapidAPI) - REQUIRED
RAPIDAPI_KEY=your-rapidapi-key-here
JSEARCH_RATE_LIMIT_PER_MINUTE=60
JSEARCH_MAX_PAGES_PER_QUERY=5
JSEARCH_REQUEST_TIMEOUT=30

#===========================================
# PROCESSING CONFIGURATION
#===========================================
PROCESSING_BATCH_SIZE=100
PROCESSING_MAX_CONCURRENT=3
PROCESSING_ENABLE_EMBEDDINGS=true
PROCESSING_ENABLE_DEDUPLICATION=true
PROCESSING_QUALITY_THRESHOLD=0.7

#===========================================
# EMBEDDING CONFIGURATION
#===========================================
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=32
EMBEDDING_CACHE_SIZE=1000

#===========================================
# DEDUPLICATION CONFIGURATION
#===========================================
DUPLICATE_SIMILARITY_THRESHOLD=0.85
DUPLICATE_TITLE_WEIGHT=0.4
DUPLICATE_COMPANY_WEIGHT=0.3
DUPLICATE_LOCATION_WEIGHT=0.2
DUPLICATE_SALARY_WEIGHT=0.1

#===========================================
# FILE STORAGE CONFIGURATION
#===========================================
ETL_DATA_DIRECTORY=data
ETL_LOGS_DIRECTORY=logs
ETL_CONFIG_DIRECTORY=config
BACKUP_DIRECTORY=backups

#===========================================
# BACKUP AND RETENTION
#===========================================
BACKUP_RAW_DATA=true
BACKUP_RETENTION_DAYS=30
DATA_RETENTION_DAYS=90

#===========================================
# MONITORING CONFIGURATION
#===========================================
ENABLE_MONITORING=true
MONITORING_PORT=8000
HEALTH_CHECK_INTERVAL=300

#===========================================
# ALERTING CONFIGURATION
#===========================================
ALERT_FAILURE_RATE_THRESHOLD=0.2
ALERT_RESPONSE_TIME_THRESHOLD=300

# Email Alerts (Optional)
ALERT_EMAIL_ENABLED=false
ALERT_EMAIL_SMTP_HOST=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_EMAIL_RECIPIENTS=admin@yourcompany.com,team@yourcompany.com

#===========================================
# SCHEDULER CONFIGURATION
#===========================================
SCHEDULER_TIMEZONE=UTC
SCHEDULER_MAX_RUNNING_JOBS=5
SCHEDULER_MISFIRE_GRACE_TIME=300

#===========================================
# PERFORMANCE CONFIGURATION
#===========================================
MAX_MEMORY_USAGE_MB=2048
CONNECTION_POOL_SIZE=20
WORKER_THREAD_COUNT=4

#===========================================
# FEATURE FLAGS
#===========================================
ENABLE_ASYNC_PROCESSING=true
ENABLE_JOB_PRIORITIZATION=true
ENABLE_AUTO_SCALING=false
"""

        with open(Path(".env.sample"), "w", encoding="utf-8") as f:
            f.write(sample_env)

        logger.info("Created sample configuration files")

    def validate_configuration(self) -> List[str]:
        """Validate the current configuration."""
        settings = self.load_settings()
        return settings.validate_settings()

    def export_config(self, output_file: Path):
        """Export current configuration to file."""
        settings = self.load_settings()

        config_export = {
            "environment": settings.environment,
            "database": {
                "pool_size": settings.database_pool_size,
                "max_overflow": settings.database_max_overflow,
                "pool_timeout": settings.database_pool_timeout,
            },
            "processing": settings.get_performance_config(),
            "monitoring": settings.get_monitoring_config(),
            "scheduler_jobs": [
                {
                    "name": job.name,
                    "phase": job.phase,
                    "schedule": job.schedule,
                    "enabled": job.enabled,
                    "parameters": job.parameters,
                }
                for job in settings.get_scheduler_jobs()
            ],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(config_export, f, default_flow_style=False, indent=2)

        logger.info(f"Exported configuration to {output_file}")


# Global settings manager
_settings_manager: Optional[ETLSettingsManager] = None


def get_settings_manager() -> ETLSettingsManager:
    """Get the global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = ETLSettingsManager()
    return _settings_manager


def get_enhanced_settings() -> ETLEnhancedSettings:
    """Get the current enhanced ETL settings."""
    return get_settings_manager().load_settings()


def setup_enhanced_logging(settings: ETLEnhancedSettings = None):
    """Setup enhanced logging configuration."""
    if settings is None:
        settings = get_enhanced_settings()

    import logging.config

    log_config = settings.get_log_config()
    logging.config.dictConfig(log_config)

    logger.info(f"Enhanced logging configured for {settings.environment} environment")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create-samples":
            manager = get_settings_manager()
            manager.create_sample_files()
            print("✅ Sample configuration files created!")

        elif command == "validate":
            manager = get_settings_manager()
            issues = manager.validate_configuration()

            if not issues:
                print("✅ Configuration validation passed!")
            else:
                print("❌ Configuration validation failed:")
                for issue in issues:
                    print(f"  - {issue}")
                sys.exit(1)

        elif command == "export":
            output_file = Path(
                sys.argv[2] if len(sys.argv) > 2 else "config_export.yaml"
            )
            manager = get_settings_manager()
            manager.export_config(output_file)
            print(f"✅ Configuration exported to {output_file}")

        else:
            print(
                "Usage: python settings.py [create-samples|validate|export [output_file]]"
            )
            sys.exit(1)
    else:
        # Default: validate configuration
        manager = get_settings_manager()
        issues = manager.validate_configuration()

        if not issues:
            print("✅ Configuration validation passed!")
        else:
            print("❌ Configuration validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
