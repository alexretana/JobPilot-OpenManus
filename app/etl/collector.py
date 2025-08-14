"""
JSearch Data Collector
Handles extraction of job data from JSearch API with robust error handling and rate limiting.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4
import aiohttp
from pathlib import Path

from app.logger import logger
from app.data.database import get_database_manager
from app.data.models import (
    RawJobCollection, RawJobCollectionDB, ETLProcessingStatus,
    ETLOperationLog, ETLOperationLogDB, ETLOperationType,
    pydantic_to_sqlalchemy
)
from .config import ETLConfig


class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self, max_calls: int, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        if len(self.calls) >= self.max_calls:
            # Need to wait until the oldest call is outside the window
            wait_time = self.time_window - (now - self.calls[0]) + 1
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
        
        self.calls.append(now)


class JSearchDataCollector:
    """Collects job data from JSearch API and stores raw responses."""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.db_manager = get_database_manager()
        self.rate_limiter = RateLimiter(config.api_rate_limit_per_minute, 60)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.api_timeout_seconds),
            headers=self.config.get_jsearch_headers()
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def collect_jobs(
        self,
        query: str,
        location: str = "United States",
        page: int = 1,
        num_pages: int = 10
    ) -> List[str]:
        """
        Collect job data from JSearch API.
        
        Args:
            query: Search query for jobs
            location: Location to search in
            page: Starting page number
            num_pages: Number of pages to collect
            
        Returns:
            List of collection IDs for the collected data
        """
        collection_ids = []
        
        operation_log = await self._start_operation_log("jsearch_collection", {
            "query": query,
            "location": location,
            "page": page,
            "num_pages": num_pages
        })
        
        try:
            for page_num in range(page, page + num_pages):
                try:
                    # Rate limiting
                    await self.rate_limiter.wait_if_needed()
                    
                    # Make API request
                    collection_data = await self._fetch_page(query, location, page_num)
                    
                    if collection_data:
                        # Store raw collection
                        collection_id = await self._store_raw_collection(collection_data)
                        collection_ids.append(collection_id)
                        logger.info(f"Collected page {page_num} for '{query}' in {location}: {collection_id}")
                    else:
                        logger.warning(f"No data returned for page {page_num}")
                        
                except Exception as e:
                    logger.error(f"Error collecting page {page_num} for '{query}': {e}")
                    await self._log_collection_error(str(e), {
                        "query": query,
                        "location": location,
                        "page": page_num
                    })
                    continue
            
            await self._complete_operation_log(operation_log.id, ETLProcessingStatus.COMPLETED, {
                "collections_created": len(collection_ids),
                "collection_ids": collection_ids
            })
            
        except Exception as e:
            logger.error(f"Fatal error in collection operation: {e}")
            await self._complete_operation_log(operation_log.id, ETLProcessingStatus.FAILED, {
                "error": str(e),
                "collections_created": len(collection_ids)
            })
            raise
        
        return collection_ids
    
    async def _fetch_page(self, query: str, location: str, page: int) -> Optional[Dict[str, Any]]:
        """Fetch a single page of results from JSearch API."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "country": "us" if location == "United States" else location,
        }
        
        try:
            start_time = time.time()
            async with self.session.get(self.config.get_search_url(), params=params) as response:
                response_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Prepare collection data
                    collection_data = {
                        "timestamp": datetime.utcnow(),
                        "api_provider": "jsearch",
                        "query_params": {
                            "query": query,
                            "location": location,
                            "page": page,
                            "country": params.get("country", "us")
                        },
                        "raw_response": data,
                        "metadata": {
                            "response_time_ms": response_time,
                            "status_code": response.status,
                            "job_count": len(data.get("data", [])),
                            "api_calls_used": 1,
                            "collection_strategy": "api_request"
                        }
                    }
                    
                    return collection_data
                
                elif response.status == 429:
                    # Rate limited
                    logger.warning(f"Rate limited by API (status 429). Will retry after delay.")
                    await asyncio.sleep(60)  # Wait 1 minute
                    return await self._fetch_page(query, location, page)  # Retry
                
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed with status {response.status}: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for query '{query}', page {page}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            return None
    
    async def _store_raw_collection(self, collection_data: Dict[str, Any]) -> str:
        """Store raw collection data in database and file system."""
        # Create RawJobCollection object
        collection = RawJobCollection(**collection_data)
        
        try:
            # Store in database
            with self.db_manager.get_session() as session:
                collection_db = pydantic_to_sqlalchemy(collection, RawJobCollectionDB)
                session.add(collection_db)
                session.flush()
                
                collection_id = collection_db.id
            
            # Store backup file
            await self._store_backup_file(collection_id, collection_data)
            
            logger.info(f"Stored raw collection {collection_id} with {collection_data['metadata']['job_count']} jobs")
            return collection_id
            
        except Exception as e:
            logger.error(f"Error storing raw collection: {e}")
            raise
    
    async def _store_backup_file(self, collection_id: str, collection_data: Dict[str, Any]):
        """Store backup file for raw collection."""
        try:
            # Create date-based directory structure
            timestamp = collection_data["timestamp"]
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            date_dir = self.config.raw_data_dir / timestamp.strftime("%Y/%m/%d")
            date_dir.mkdir(parents=True, exist_ok=True)
            
            # Store file
            filename = f"{collection_data['api_provider']}_{collection_id}.json"
            filepath = date_dir / filename
            
            # Serialize datetime objects for JSON storage
            serializable_data = self._make_json_serializable(collection_data)
            
            with open(filepath, 'w') as f:
                json.dump(serializable_data, f, indent=2)
            
            logger.debug(f"Stored backup file: {filepath}")
            
        except Exception as e:
            logger.error(f"Error storing backup file: {e}")
            # Don't raise - this is just backup
    
    def _make_json_serializable(self, data: Any) -> Any:
        """Convert data to JSON serializable format."""
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {key: self._make_json_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._make_json_serializable(item) for item in data]
        else:
            return data
    
    async def _start_operation_log(self, operation_name: str, input_data: Dict[str, Any]) -> ETLOperationLog:
        """Start logging an ETL operation."""
        operation_log = ETLOperationLog(
            operation_type=ETLOperationType.COLLECTION,
            operation_name=operation_name,
            status=ETLProcessingStatus.PROCESSING,
            input_data=input_data
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
        output_data: Optional[Dict[str, Any]] = None
    ):
        """Complete an ETL operation log."""
        try:
            with self.db_manager.get_session() as session:
                log_db = session.query(ETLOperationLogDB).filter(
                    ETLOperationLogDB.id == operation_id
                ).first()
                
                if log_db:
                    log_db.completed_at = datetime.utcnow()
                    log_db.status = status
                    log_db.duration_ms = int((log_db.completed_at - log_db.started_at).total_seconds() * 1000)
                    if output_data:
                        log_db.output_data = output_data
                    
                    session.flush()
        
        except Exception as e:
            logger.error(f"Error completing operation log: {e}")
    
    async def _log_collection_error(self, error_message: str, context: Dict[str, Any]):
        """Log a collection error."""
        error_log = ETLOperationLog(
            operation_type=ETLOperationType.COLLECTION,
            operation_name="jsearch_collection_error",
            status=ETLProcessingStatus.FAILED,
            error_message=error_message,
            input_data=context
        )
        
        try:
            with self.db_manager.get_session() as session:
                log_db = pydantic_to_sqlalchemy(error_log, ETLOperationLogDB)
                session.add(log_db)
                session.flush()
        
        except Exception as e:
            logger.error(f"Error logging collection error: {e}")
    
    async def get_pending_collections(self, limit: int = 50) -> List[RawJobCollection]:
        """Get pending raw collections that need processing."""
        try:
            with self.db_manager.get_session() as session:
                collections_db = session.query(RawJobCollectionDB).filter(
                    RawJobCollectionDB.processing_status == ETLProcessingStatus.PENDING
                ).limit(limit).all()
                
                return [
                    RawJobCollection(
                        id=c.id,
                        timestamp=c.timestamp,
                        api_provider=c.api_provider,
                        query_params=c.query_params,
                        raw_response=c.raw_response,
                        metadata=c.metadata or {},
                        processing_status=c.processing_status,
                        error_info=c.error_info,
                        created_at=c.created_at
                    ) for c in collections_db
                ]
                
        except Exception as e:
            logger.error(f"Error getting pending collections: {e}")
            return []
    
    async def mark_collection_status(self, collection_id: str, status: ETLProcessingStatus):
        """Mark a collection's processing status."""
        try:
            with self.db_manager.get_session() as session:
                collection_db = session.query(RawJobCollectionDB).filter(
                    RawJobCollectionDB.id == collection_id
                ).first()
                
                if collection_db:
                    collection_db.processing_status = status
                    session.flush()
                    logger.info(f"Updated collection {collection_id} status to {status}")
        
        except Exception as e:
            logger.error(f"Error updating collection status: {e}")
    
    async def collect_default_queries(self) -> Dict[str, List[str]]:
        """Collect jobs for all default queries and locations."""
        results = {}
        
        async with self:  # Use context manager for session
            for query in self.config.default_search_queries:
                query_results = []
                for location in self.config.default_locations:
                    try:
                        collection_ids = await self.collect_jobs(
                            query=query,
                            location=location,
                            page=1,
                            num_pages=1  # Start with 1 page per location
                        )
                        query_results.extend(collection_ids)
                        
                    except Exception as e:
                        logger.error(f"Error collecting '{query}' in {location}: {e}")
                        continue
                
                results[query] = query_results
        
        return results
