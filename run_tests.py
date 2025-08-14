#!/usr/bin/env python3
"""
JobPilot-OpenManus Test Runner

This script provides easy access to run different test suites:
- Fast backend API tests using FastAPI TestClient
- Comprehensive E2E tests with Playwright
- Specific test categories and performance tests
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def print_banner():
    """Print test runner banner."""
    print("=" * 80)
    print("🧪 JobPilot-OpenManus Test Runner")
    print("   🚀 FastAPI TestClient | 🎭 Playwright E2E | 📊 Performance")
    print("=" * 80)


def run_pytest_command(args_list):
    """Run pytest with given arguments."""
    cmd = [sys.executable, "-m", "pytest"] + args_list
    print(f"🔧 Running: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, cwd=Path.cwd())
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return 1


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="JobPilot Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Suite Options:
  --backend         Fast backend API tests (FastAPI TestClient)  
  --e2e            Comprehensive E2E tests (Playwright + servers)
  --integration    Integration tests only
  --performance    Performance tests only
  --unit           Unit tests only
  --all            All tests (excluding E2E)
  
Examples:
  python run_tests.py --backend              # Fast backend tests
  python run_tests.py --e2e                  # Full E2E suite  
  python run_tests.py --backend --performance # Backend + perf tests
  python run_tests.py --all                  # All tests except E2E
  python run_tests.py -k test_health         # Tests matching pattern
  python run_tests.py --backend -v           # Verbose backend tests
        """
    )
    
    # Test suite selection
    parser.add_argument("--backend", action="store_true", help="Run fast backend API tests")
    parser.add_argument("--e2e", action="store_true", help="Run comprehensive E2E tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests (except E2E)")
    
    # Test filtering
    parser.add_argument("-k", "--keyword", help="Only run tests matching keyword")
    parser.add_argument("-m", "--markers", help="Only run tests with specific markers")
    parser.add_argument("--not-slow", action="store_true", help="Skip slow tests")
    
    # Output options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    parser.add_argument("--tb", choices=["short", "long", "auto", "no"], default="short", help="Traceback format")
    parser.add_argument("--html", help="Generate HTML report")
    parser.add_argument("--cov", action="store_true", help="Generate coverage report")
    
    # Parallel execution
    parser.add_argument("-n", "--numprocesses", type=int, help="Number of parallel processes")
    
    # E2E specific options
    parser.add_argument("--rapidapi-key", help="RapidAPI key for ETL testing")
    parser.add_argument("--include-frontend", action="store_true", help="Start frontend server for E2E")
    parser.add_argument("--manual-server", action="store_true", help="Use manually started server for E2E")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Build pytest command
    pytest_args = []
    
    # Add verbosity
    if args.verbose:
        pytest_args.extend(["-v", "-s"])
    elif args.quiet:
        pytest_args.append("-q")
    
    # Add traceback format
    pytest_args.extend([f"--tb={args.tb}"])
    
    # Add coverage if requested
    if args.cov:
        pytest_args.extend([
            "--cov=app", 
            "--cov-report=html", 
            "--cov-report=term-missing"
        ])
    
    # Add HTML report if requested
    if args.html:
        pytest_args.extend([f"--html={args.html}"])
    
    # Add parallel execution if requested
    if args.numprocesses:
        pytest_args.extend(["-n", str(args.numprocesses)])
    
    # Handle test filtering
    if args.keyword:
        pytest_args.extend(["-k", args.keyword])
    
    if args.markers:
        pytest_args.extend(["-m", args.markers])
    elif args.not_slow:
        pytest_args.extend(["-m", "not slow"])
    
    # Determine which tests to run
    if args.e2e:
        print("🎭 Running Comprehensive E2E Tests (Playwright + Server Management)")
        
        # For E2E tests, we need to run the special E2E suite
        if args.manual_server:
            pytest_args.append("tests/test_e2e_comprehensive.py::run_e2e_tests_manual_server")
        else:
            # Set up environment variables
            env = os.environ.copy()
            if args.rapidapi_key:
                env['RAPIDAPI_KEY'] = args.rapidapi_key
            if args.include_frontend:
                env['INCLUDE_FRONTEND'] = 'true'
            
            pytest_args.append("tests/test_e2e_comprehensive.py")
        
    elif args.backend:
        print("🚀 Running Fast Backend API Tests (FastAPI TestClient)")
        pytest_args.append("tests/test_backend_fastapi.py")
        
        if args.performance:
            pytest_args.extend(["-m", "performance or not performance"])
        elif args.integration:
            pytest_args.extend(["-m", "integration"])
        
    elif args.all:
        print("📋 Running All Tests (Backend + Core Components)")
        # Run all tests except E2E
        pytest_args.extend([
            "tests/test_backend_fastapi.py",
            "tests/test_core_components.py",
            "tests/test_job_scrapers.py",
            "tests/test_backend_api.py"
        ])
        
    elif args.integration:
        print("🔄 Running Integration Tests Only")
        pytest_args.extend(["-m", "integration"])
        
    elif args.performance:
        print("⚡ Running Performance Tests Only")
        pytest_args.extend(["-m", "performance"])
        
    elif args.unit:
        print("🧪 Running Unit Tests Only")
        pytest_args.extend(["-m", "unit or not (integration or performance or e2e)"])
        
    else:
        # Default: run backend tests
        print("🚀 Running Default Backend API Tests")
        print("   (Use --help to see all options)")
        pytest_args.append("tests/test_backend_fastapi.py")
    
    print()
    
    # Check if required files exist
    required_files = ["pytest.ini"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"⚠️ Missing files: {missing_files}")
        print("   Some test configuration may not work properly")
    
    # Run the tests
    exit_code = run_pytest_command(pytest_args)
    
    # Print summary
    print()
    print("=" * 80)
    if exit_code == 0:
        print("🎉 All tests passed!")
    elif exit_code == 130:
        print("⚠️ Tests were interrupted")
    else:
        print(f"❌ Tests failed (exit code: {exit_code})")
        print("\nQuick troubleshooting:")
        print("  • For backend tests: Ensure web_server.py is importable")
        print("  • For E2E tests: Check server dependencies and ports")
        print("  • For database tests: Verify database connectivity")
    
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
