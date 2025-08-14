"""
ETL Configuration Management
Handles configuration for the ETL pipeline components.
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ETLConfig:
    """Configuration for ETL pipeline operations."""
    
    # API Configuration
    rapidapi_key: str = field(default_factory=lambda: os.getenv("RAPIDAPI_KEY", ""))
    api_rate_limit_per_minute: int = field(default_factory=lambda: int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "10")))
    api_timeout_seconds: int = 30
    
    # JSearch API Configuration
    jsearch_base_url: str = "https://jsearch.p.rapidapi.com"
    jsearch_endpoints: Dict[str, str] = field(default_factory=lambda: {
        "search": "/search",
        "job_details": "/job-details",
        "estimated_salary": "/estimated-salary"
    })
    
    # Database Configuration
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///data/jobpilot.db"))
    
    # File Storage Configuration
    raw_data_dir: Path = field(default_factory=lambda: Path("data/raw_collections"))
    processed_data_dir: Path = field(default_factory=lambda: Path("data/processed_data"))
    failed_data_dir: Path = field(default_factory=lambda: Path("data/failed_processing"))
    logs_dir: Path = field(default_factory=lambda: Path("data/logs"))
    
    # Processing Configuration
    batch_size: int = 50  # Jobs to process in one batch
    max_retries: int = 3
    retry_delay_seconds: int = 5
    
    # Collection Configuration
    default_search_queries: List[str] = field(default_factory=lambda: [
        "software engineer",
        "data scientist", 
        "python developer",
        "frontend developer",
        "product manager"
    ])
    default_locations: List[str] = field(default_factory=lambda: [
        "San Francisco, CA",
        "New York, NY", 
        "Seattle, WA",
        "Austin, TX",
        "Remote"
    ])
    
    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Quality Control Configuration
    min_description_length: int = 50
    required_fields: List[str] = field(default_factory=lambda: ["title", "company", "location"])
    
    # Scheduler Configuration
    schedule_enabled: bool = field(default_factory=lambda: os.getenv("ETL_SCHEDULE_ENABLED", "false").lower() == "true")
    collection_interval_hours: int = 24  # Run daily by default
    processing_delay_minutes: int = 5   # Wait 5 minutes after collection
    loading_delay_minutes: int = 2      # Wait 2 minutes after processing
    
    def __post_init__(self):
        """Ensure directories exist."""
        for directory in [self.raw_data_dir, self.processed_data_dir, self.failed_data_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'ETLConfig':
        """Create config from environment variables."""
        return cls()
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.rapidapi_key:
            errors.append("RAPIDAPI_KEY environment variable is required")
        
        if self.api_rate_limit_per_minute <= 0:
            errors.append("API rate limit must be positive")
        
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        
        if self.batch_size <= 0:
            errors.append("Batch size must be positive")
        
        return errors
    
    def get_jsearch_headers(self) -> Dict[str, str]:
        """Get headers for JSearch API requests."""
        return {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
    
    def get_search_url(self) -> str:
        """Get JSearch search endpoint URL."""
        return f"{self.jsearch_base_url}{self.jsearch_endpoints['search']}"
