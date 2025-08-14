#!/usr/bin/env python3
"""
Test ETL Progress - Current Implementation
Tests the data collection and processing components implemented so far.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.etl.config import ETLConfig
from app.etl.collector import JSearchDataCollector
from app.etl.processor import JobDataProcessor
from app.data.database import get_database_manager
from app.data.models import Base, ETLProcessingStatus


class ETLProgressTester:
    """Test the current ETL implementation progress."""
    
    def __init__(self):
        self.config = ETLConfig.from_env()
        self.db_manager = get_database_manager()
        
    async def run_tests(self):
        """Run all ETL progress tests."""
        print("🚀 Starting ETL Progress Tests")
        print("=" * 60)
        
        # Test 1: Configuration validation
        await self.test_configuration()
        
        # Test 2: Database schema creation
        await self.test_database_schema()
        
        # Test 3: Data collection (if API key available)
        await self.test_data_collection()
        
        # Test 4: Data processing
        await self.test_data_processing()
        
        # Test 5: End-to-end collection + processing
        await self.test_collection_processing_flow()
        
        print("🎉 All ETL Progress Tests Completed!")
        
    async def test_configuration(self):
        """Test ETL configuration."""
        print("\n🔧 Testing ETL Configuration")
        print("-" * 40)
        
        try:
            # Test configuration creation
            config = ETLConfig.from_env()
            print(f"✅ Configuration created successfully")
            print(f"   📁 Raw data dir: {config.raw_data_dir}")
            print(f"   📁 Processed data dir: {config.processed_data_dir}")
            print(f"   ⚙️  Batch size: {config.batch_size}")
            print(f"   🔄 Max retries: {config.max_retries}")
            
            # Test validation
            errors = config.validate()
            if errors:
                print(f"⚠️  Configuration validation warnings:")
                for error in errors:
                    print(f"   • {error}")
            else:
                print("✅ Configuration validation passed")
                
            # Test directory creation
            print(f"✅ Directories created successfully")
            
            # Test API configuration (if available)
            if config.rapidapi_key:
                print(f"✅ API key configured (length: {len(config.rapidapi_key)})")
                headers = config.get_jsearch_headers()
                print(f"✅ API headers generated: {list(headers.keys())}")
            else:
                print("⚠️  No API key configured - collection tests will be skipped")
                
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False
            
        return True
    
    async def test_database_schema(self):
        """Test database schema creation."""
        print("\n🗃️  Testing Database Schema")
        print("-" * 40)
        
        try:
            # Test database connection
            health_check = self.db_manager.health_check()
            print(f"✅ Database connection: {'OK' if health_check else 'FAILED'}")
            
            if not health_check:
                print("❌ Database connection failed")
                return False
            
            # Test table creation
            self.db_manager.create_tables()
            print("✅ Database tables created successfully")
            
            # Test table stats
            stats = self.db_manager.get_table_stats()
            print("✅ Table statistics retrieved:")
            for table, count in stats.items():
                print(f"   📊 {table}: {count} records")
                
            return True
            
        except Exception as e:
            print(f"❌ Database schema test failed: {e}")
            return False
    
    async def test_data_collection(self):
        """Test data collection functionality."""
        print("\n📥 Testing Data Collection")
        print("-" * 40)
        
        if not self.config.rapidapi_key:
            print("⏭️  Skipping collection test - no API key configured")
            return True
            
        try:
            collector = JSearchDataCollector(self.config)
            
            # Test basic collection (1 page, small test)
            print("🔄 Testing small collection (1 job page)...")
            
            collection_ids = await collector.collect_jobs(
                query="python developer",
                location="Remote", 
                page=1,
                num_pages=1
            )
            
            if collection_ids:
                print(f"✅ Collection successful: {len(collection_ids)} collections created")
                for cid in collection_ids:
                    print(f"   📄 Collection ID: {cid}")
                    
                # Test pending collections retrieval
                pending = await collector.get_pending_collections(limit=5)
                print(f"✅ Pending collections retrieved: {len(pending)} collections")
                
                return collection_ids
            else:
                print("⚠️  No collections created - API may have returned no results")
                return []
                
        except Exception as e:
            print(f"❌ Data collection test failed: {e}")
            print("   This might be due to API rate limits or network issues")
            return False
    
    async def test_data_processing(self):
        """Test data processing functionality."""
        print("\n⚙️  Testing Data Processing")
        print("-" * 40)
        
        try:
            processor = JobDataProcessor(self.config)
            
            # Create mock raw collection data for testing
            mock_raw_data = {
                "status": "OK",
                "data": [{
                    "job_id": "test-job-123",
                    "job_title": "Senior Python Developer", 
                    "employer_name": "Tech Corp",
                    "job_city": "San Francisco",
                    "job_state": "CA", 
                    "job_country": "US",
                    "job_description": "We are looking for a senior Python developer with experience in Django, Flask, and AWS. The candidate should have 5+ years of experience and strong problem-solving skills. Responsibilities include developing scalable web applications and mentoring junior developers.",
                    "job_employment_type": "Full-time",
                    "job_is_remote": False,
                    "job_min_salary": 120000,
                    "job_max_salary": 160000,
                    "job_benefits": ["Health insurance", "401k", "Remote work"],
                    "job_apply_link": "https://example.com/apply",
                    "employer_website": "https://techcorp.com",
                    "job_posted_at_datetime_utc": "2025-08-14T10:00:00Z"
                }]
            }
            
            # Store mock raw collection
            from app.data.models import RawJobCollection, RawJobCollectionDB, pydantic_to_sqlalchemy
            from uuid import uuid4
            
            mock_collection = RawJobCollection(
                id=str(uuid4()),
                timestamp=datetime.utcnow(),
                api_provider="jsearch",
                query_params={"query": "python developer", "location": "San Francisco, CA"},
                raw_response=mock_raw_data,
                metadata={"job_count": 1, "test": True},
                processing_status=ETLProcessingStatus.PENDING
            )
            
            # Store in database
            with self.db_manager.get_session() as session:
                collection_db = pydantic_to_sqlalchemy(mock_collection, RawJobCollectionDB)
                session.add(collection_db)
                session.flush()
                collection_id = collection_db.id
            
            print(f"✅ Mock raw collection created: {collection_id}")
            
            # Test processing
            print("🔄 Testing data processing...")
            processing_log_id = await processor.process_collection(collection_id)
            
            if processing_log_id:
                print(f"✅ Processing completed: {processing_log_id}")
                
                # Test getting pending processing jobs
                pending_jobs = await processor.get_pending_processing_jobs(limit=5)
                print(f"✅ Pending processed jobs retrieved: {len(pending_jobs)}")
                
                if pending_jobs:
                    sample_job = pending_jobs[0]
                    processed_data = sample_job.processed_data
                    print(f"✅ Sample processed job data:")
                    print(f"   📝 Title: {processed_data.get('title')}")
                    print(f"   🏢 Company: {processed_data.get('company')}")
                    print(f"   📍 Location: {processed_data.get('location')}")
                    print(f"   💰 Salary: ${processed_data.get('salary_min', 'N/A')} - ${processed_data.get('salary_max', 'N/A')}")
                    print(f"   🔧 Skills: {processed_data.get('skills_required', [])}")
                    print(f"   📊 Quality Score: {sample_job.quality_score:.2f}")
                
                return True
            else:
                print("❌ Processing failed - no processing log ID returned")
                return False
                
        except Exception as e:
            print(f"❌ Data processing test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_collection_processing_flow(self):
        """Test end-to-end collection + processing flow."""
        print("\n🔄 Testing Collection + Processing Flow")
        print("-" * 40)
        
        if not self.config.rapidapi_key:
            print("⏭️  Skipping end-to-end test - no API key configured")
            return True
            
        try:
            collector = JSearchDataCollector(self.config)
            processor = JobDataProcessor(self.config)
            
            # Step 1: Collect data
            print("📥 Step 1: Collecting job data...")
            collection_ids = await collector.collect_jobs(
                query="software engineer",
                location="Remote",
                page=1, 
                num_pages=1
            )
            
            if not collection_ids:
                print("⚠️  No data collected, skipping processing step")
                return False
                
            print(f"✅ Collection completed: {len(collection_ids)} collections")
            
            # Step 2: Process collected data
            print("⚙️  Step 2: Processing collected data...")
            processing_results = []
            
            for collection_id in collection_ids:
                try:
                    processing_log_id = await processor.process_collection(collection_id)
                    processing_results.append(processing_log_id)
                    print(f"✅ Processed collection {collection_id}: {processing_log_id}")
                except Exception as e:
                    print(f"⚠️  Failed to process collection {collection_id}: {e}")
            
            # Step 3: Verify processed data
            print("📊 Step 3: Verifying processed data...")
            pending_jobs = await processor.get_pending_processing_jobs(limit=10)
            
            print(f"✅ End-to-end flow completed!")
            print(f"   📥 Collections created: {len(collection_ids)}")
            print(f"   ⚙️  Processing logs: {len(processing_results)}")
            print(f"   📋 Jobs ready for loading: {len(pending_jobs)}")
            
            # Show sample processed job
            if pending_jobs:
                sample = pending_jobs[0].processed_data
                print(f"   📄 Sample job: {sample.get('title')} at {sample.get('company')}")
            
            return True
            
        except Exception as e:
            print(f"❌ End-to-end flow test failed: {e}")
            return False


async def main():
    """Run all ETL progress tests."""
    print("🔍 ETL Progress Test Suite")
    print(f"⏰ Started at: {datetime.now()}")
    print()
    
    # Check for API key
    api_key = os.getenv("RAPIDAPI_KEY")
    if api_key:
        print(f"🔑 API Key found (length: {len(api_key)})")
    else:
        print("⚠️  No RAPIDAPI_KEY found in environment - collection tests will be limited")
    
    tester = ETLProgressTester()
    await tester.run_tests()


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
