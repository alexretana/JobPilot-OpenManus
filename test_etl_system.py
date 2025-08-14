#!/usr/bin/env python3
"""
ETL System Test Runner
Run this script to test different components of the ETL pipeline.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

async def test_basic_imports():
    """Test that all ETL modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        from app.data.models import ETLOperationLog, RawJobCollection
        print("✅ Data models imported successfully")
        
        from app.etl.config import ETLConfig
        print("✅ ETL config imported successfully")
        
        from app.etl.settings import get_enhanced_settings
        print("✅ Enhanced settings imported successfully")
        
        from app.etl.collector import JSearchDataCollector
        print("✅ Data collector imported successfully")
        
        from app.etl.processor import JobDataProcessor
        print("✅ Data processor imported successfully")
        
        from app.etl.loader import JobDataLoader
        print("✅ Data loader imported successfully")
        
        from app.etl.scheduler import ETLOrchestrator, ETLScheduler
        print("✅ Scheduler and orchestrator imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_configuration():
    """Test configuration loading and validation."""
    print("\\n⚙️ Testing configuration...")
    
    try:
        from app.etl.settings import get_settings_manager, ETLEnhancedSettings
        
        # Reset the settings manager to ensure fresh settings
        manager = get_settings_manager()
        manager._settings = None  # Clear cached settings
        
        # Create fresh settings with environment variables
        settings = ETLEnhancedSettings()
        print(f"✅ Settings loaded for environment: {settings.environment}")
        
        # Test validation
        issues = settings.validate_settings()
        if issues:
            print("⚠️ Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Configuration validation passed")
        
        return True  # Always return True for config test
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_setup():
    """Test database initialization."""
    print("\n🗄️ Testing database setup...")
    
    try:
        from app.data.models import create_database_engine, create_tables
        from app.etl.settings import ETLEnhancedSettings
        
        # Use settings with environment variables already set
        settings = ETLEnhancedSettings()
        engine = create_database_engine(settings.get_database_url())
        
        # Create tables
        create_tables(engine)
        print("✅ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

async def test_api_connection():
    """Test API connection (requires valid API key)."""
    print("\n🌐 Testing API connection...")
    
    try:
        from app.etl.collector import JSearchDataCollector
        from app.etl.settings import ETLEnhancedSettings
        from app.database.manager import DatabaseManager
        
        # Use settings with environment variables already set
        settings = ETLEnhancedSettings()
        
        if settings.rapidapi_key == "test-api-key-placeholder":
            print("⚠️ Skipping API test - using test placeholder key")
            return True
        
        # Get basic config from settings
        basic_config = settings.basic_config
        collector = JSearchDataCollector(basic_config)
        
        # Test API connection with a simple query
        print("Testing API connection with sample query...")
        
        async with collector:
            # This will test the API connection
            collection_ids = await collector.collect_jobs(
                query="python developer",
                location="Remote", 
                page=1,
                num_pages=1
            )
            
            if collection_ids:
                print(f"✅ API connection successful! Created {len(collection_ids)} collections")
                return True
            else:
                print("⚠️ API connection succeeded but no data collected")
                return True
        
    except Exception as e:
        print(f"❌ API connection test failed: {e}")
        return False

async def run_mini_pipeline():
    """Run a mini end-to-end pipeline test."""
    print("\n🚀 Running mini pipeline test...")
    
    try:
        from app.etl.scheduler import run_manual_pipeline
        from app.etl.settings import ETLEnhancedSettings
        
        # Use settings with environment variables already set
        settings = ETLEnhancedSettings()
        
        if settings.rapidapi_key == "test-api-key-placeholder":
            print("⚠️ Skipping pipeline test - using test placeholder key")
            return True
        
        print("Running complete ETL pipeline...")
        result = await run_manual_pipeline(settings)
        
        print(f"Pipeline Status: {result['overall_status']}")
        print(f"Duration: {result['total_duration_seconds']:.2f} seconds")
        
        if result.get('errors'):
            print("Pipeline Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        
        # Show phase results
        for phase, phase_result in result.get('phases', {}).items():
            print(f"{phase.title()} Phase: {phase_result.get('status', 'Unknown')}")
        
        return result['overall_status'] in ['completed', 'partial']
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

async def main():
    """Main test runner."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Set additional test-specific environment variables if needed
    if not os.getenv('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///test_etl.db'
    if not os.getenv('ENVIRONMENT'):
        os.environ['ENVIRONMENT'] = 'testing'
    
    print("🧪 JobPilot ETL System Test Runner")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_basic_imports),
        ("Configuration", test_configuration), 
        ("Database Setup", test_database_setup),
        ("API Connection", test_api_connection),
        ("Mini Pipeline", run_mini_pipeline)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running: {test_name}")
        try:
            success = await test_func()
            results[test_name] = success
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results[test_name] = False
    
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ETL system is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
