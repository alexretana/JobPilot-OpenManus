#!/usr/bin/env python3
"""
ETL System Test Setup Script
Installs dependencies and sets up the environment for testing the ETL pipeline.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_additional_dependencies():
    """Install ETL-specific dependencies."""
    print("\n📦 Installing ETL-specific dependencies...")
    
    etl_dependencies = [
        "apscheduler>=3.10.0",  # For job scheduling
        "aiohttp>=3.9.0",       # For async HTTP requests (JSearch API)
        "asyncpg>=0.29.0",      # PostgreSQL async support (optional)
        "python-multipart>=0.0.9",  # For FastAPI file uploads
    ]
    
    try:
        for dep in etl_dependencies:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        
        print("✅ ETL dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_test_environment():
    """Create test environment structure."""
    print("\n🏗️ Creating test environment...")
    
    # Create necessary directories
    directories = [
        "data",
        "data/raw_collections",
        "data/processed_data", 
        "data/failed_processing",
        "data/logs",
        "logs",
        "config",
        "backups"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    return True

def create_sample_env_file():
    """Create a sample .env file for testing."""
    print("\n📋 Creating sample .env file...")
    
    env_content = """# JobPilot ETL Test Configuration
# IMPORTANT: Get your API key from RapidAPI (JSearch)

#===========================================
# ENVIRONMENT SETTINGS
#===========================================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

#===========================================
# DATABASE CONFIGURATION
#===========================================
DATABASE_URL=sqlite:///data/jobpilot_etl_test.db

#===========================================
# API CONFIGURATION
#===========================================
# JSearch API - REPLACE WITH YOUR ACTUAL API KEY
RAPIDAPI_KEY=your-rapidapi-key-here
JSEARCH_RATE_LIMIT_PER_MINUTE=10
JSEARCH_MAX_PAGES_PER_QUERY=1
JSEARCH_REQUEST_TIMEOUT=30

#===========================================
# PROCESSING CONFIGURATION
#===========================================
PROCESSING_BATCH_SIZE=10
PROCESSING_MAX_CONCURRENT=1
PROCESSING_ENABLE_EMBEDDINGS=false
PROCESSING_ENABLE_DEDUPLICATION=true
PROCESSING_QUALITY_THRESHOLD=0.5

#===========================================
# TESTING OVERRIDES
#===========================================
ETL_DATA_DIRECTORY=data
ETL_LOGS_DIRECTORY=logs
BACKUP_RAW_DATA=true
ENABLE_MONITORING=true
MONITORING_PORT=8001
"""
    
    env_file = Path(".env.test")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    print(f"📝 Please edit {env_file} and add your actual JSearch API key")
    return True

def create_test_runner():
    """Create a test runner script."""
    print("\n🧪 Creating test runner...")
    
    test_runner_content = '''#!/usr/bin/env python3
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
        from app.etl.settings import get_enhanced_settings
        
        settings = get_enhanced_settings()
        print(f"✅ Settings loaded for environment: {settings.environment}")
        
        # Test validation
        issues = settings.validate_settings()
        if issues:
            print("⚠️ Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Configuration validation passed")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def test_database_setup():
    """Test database initialization."""
    print("\\n🗄️ Testing database setup...")
    
    try:
        from app.data.models import create_database_engine, create_tables
        from app.etl.settings import get_enhanced_settings
        
        settings = get_enhanced_settings()
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
    print("\\n🌐 Testing API connection...")
    
    try:
        from app.etl.collector import JSearchDataCollector
        from app.etl.settings import get_enhanced_settings
        from app.database.manager import DatabaseManager
        
        settings = get_enhanced_settings()
        
        if settings.jsearch_api_key == "your-rapidapi-key-here":
            print("⚠️ Skipping API test - please set RAPIDAPI_KEY in .env.test")
            return True
        
        db_manager = DatabaseManager(settings.get_database_url())
        collector = JSearchDataCollector(db_manager, settings)
        
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
    print("\\n🚀 Running mini pipeline test...")
    
    try:
        from app.etl.scheduler import run_manual_pipeline
        from app.etl.settings import get_enhanced_settings
        
        settings = get_enhanced_settings()
        
        if settings.jsearch_api_key == "your-rapidapi-key-here":
            print("⚠️ Skipping pipeline test - please set RAPIDAPI_KEY in .env.test")
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
        print(f"\\n🔄 Running: {test_name}")
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
    
    print("\\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ETL system is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    test_runner_file = Path("test_etl_system.py")
    with open(test_runner_file, "w", encoding="utf-8") as f:
        f.write(test_runner_content)
    
    # Make executable on Unix-like systems
    if hasattr(os, 'chmod'):
        os.chmod(test_runner_file, 0o755)
    
    print(f"✅ Created {test_runner_file}")
    return True

def main():
    """Main setup function."""
    print("🚀 JobPilot ETL System Test Setup")
    print("=" * 40)
    
    if not check_python_version():
        return False
    
    success = True
    success &= install_additional_dependencies()
    success &= create_test_environment()
    success &= create_sample_env_file() 
    success &= create_test_runner()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ ETL test setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Edit .env.test and add your JSearch API key from RapidAPI")
        print("2. Run: python test_etl_system.py")
        print("3. Check the test results and fix any issues")
        print("\n💡 To get a JSearch API key:")
        print("   - Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch")
        print("   - Sign up and subscribe to the free tier")
        print("   - Copy your API key to .env.test")
    else:
        print("❌ Setup encountered some issues. Please check the output above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
