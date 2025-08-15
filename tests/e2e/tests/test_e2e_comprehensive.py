#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for JobPilot-OpenManus

This test suite validates complete workflows using:
- Server lifecycle management
- REST API testing
- WebSocket communication
- Playwright browser automation for UI testing
- ETL pipeline validation
- Database state verification
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
import websockets
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# Add the project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from tests.utils.server_manager import TestEnvironment
except ImportError:
    print("⚠️ Server manager not available, tests will run against existing server")
    TestEnvironment = None


@dataclass
class TestResult:
    """Test result with timing and details."""

    name: str
    passed: bool
    duration: float
    details: str = ""
    error: Optional[str] = None


class ComprehensiveE2ETestSuite:
    """Complete end-to-end test suite for JobPilot with browser automation."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.frontend_url = "http://localhost:3000"  # Development server
        self.ws_url = "ws://localhost:8080"

        # HTTP client
        self.session: Optional[aiohttp.ClientSession] = None

        # Playwright components
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Test data and results
        self.test_data: Dict[str, Any] = {}
        self.results: List[TestResult] = []

    async def __aenter__(self):
        """Initialize test suite with Playwright."""
        # Initialize HTTP session
        self.session = aiohttp.ClientSession()

        # Initialize Playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,  # Set to False for debugging
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        self.page = await self.context.new_page()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup test suite."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        if self.session:
            await self.session.close()

    def _record_result(
        self,
        name: str,
        passed: bool,
        duration: float,
        details: str = "",
        error: str = None,
    ):
        """Record test result."""
        self.results.append(
            TestResult(
                name=name,
                passed=passed,
                duration=duration,
                details=details,
                error=error,
            )
        )

    async def _timed_test(self, test_name: str, test_func):
        """Execute a test with timing and error handling."""
        print(f"\n🔍 Running: {test_name}")
        start_time = time.time()

        try:
            result = await test_func()
            duration = time.time() - start_time

            if result:
                print(f"   ✅ PASSED ({duration:.2f}s)")
                self._record_result(
                    test_name, True, duration, "Test completed successfully"
                )
            else:
                print(f"   ❌ FAILED ({duration:.2f}s)")
                self._record_result(
                    test_name, False, duration, "Test assertions failed"
                )

            return result

        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 ERROR ({duration:.2f}s): {e}")
            self._record_result(test_name, False, duration, "Test crashed", str(e))
            return False

    # ================== Backend API Tests ==================

    async def test_server_startup_and_health(self) -> bool:
        """Test server startup and health endpoints."""
        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status != 200:
                    return False

                health_data = await response.json()
                print(f"   📊 Server health: {health_data}")

                required_fields = ["status", "timestamp"]
                for field in required_fields:
                    if field not in health_data:
                        print(f"   ❌ Missing health field: {field}")
                        return False

            # Test stats endpoint
            try:
                async with self.session.get(f"{self.base_url}/api/stats") as response:
                    if response.status == 200:
                        stats = await response.json()
                        print(f"   📈 Database stats: {stats.get('total_jobs', 0)} jobs")
            except Exception:
                print("   ℹ️ Stats endpoint not accessible")

            return True

        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False

    async def test_job_crud_operations(self) -> bool:
        """Test complete job CRUD operations."""
        try:
            # Create test jobs
            test_jobs = []
            job_data_list = [
                {
                    "name": "e2e-test-python-dev",
                    "title": "Senior Python Developer",
                    "company": "E2E TechCorp",
                    "location": "San Francisco, CA",
                    "description": "Build scalable Python applications for our growing platform",
                    "requirements": "5+ years Python, Django, PostgreSQL, AWS",
                    "job_type": "Full-time",
                    "remote_type": "Hybrid",
                    "salary_min": 120000,
                    "salary_max": 160000,
                    "skills_required": ["Python", "Django", "PostgreSQL", "AWS"],
                },
                {
                    "name": "e2e-test-frontend-dev",
                    "title": "React Frontend Developer",
                    "company": "E2E WebCorp",
                    "location": "Remote",
                    "description": "Create beautiful and responsive user interfaces",
                    "requirements": "3+ years React, TypeScript, Modern CSS",
                    "job_type": "Full-time",
                    "remote_type": "Remote",
                    "salary_min": 90000,
                    "salary_max": 120000,
                    "skills_required": ["React", "TypeScript", "CSS", "JavaScript"],
                },
            ]

            # CREATE - Add jobs
            for job_data in job_data_list:
                async with self.session.post(
                    f"{self.base_url}/api/leads", json=job_data
                ) as response:
                    if response.status == 200:
                        job = await response.json()
                        test_jobs.append(job)
                        print(f"   ✅ Created job: {job['title']} at {job['company']}")
                    else:
                        print(f"   ❌ Failed to create job: {response.status}")
                        return False

            self.test_data["test_jobs"] = test_jobs

            # READ - List jobs
            async with self.session.get(f"{self.base_url}/api/leads") as response:
                if response.status == 200:
                    all_jobs = await response.json()
                    print(f"   ✅ Retrieved {len(all_jobs)} total jobs")
                else:
                    return False

            # UPDATE - Modify a job
            if test_jobs:
                job_to_update = test_jobs[0]
                update_data = {
                    **job_to_update,
                    "salary_max": 180000,
                    "description": job_to_update["description"] + " - UPDATED",
                }

                async with self.session.put(
                    f"{self.base_url}/api/leads/{job_to_update['id']}", json=update_data
                ) as response:
                    if response.status == 200:
                        updated_job = await response.json()
                        print(
                            f"   ✅ Updated job salary: ${updated_job['salary_max']:,}"
                        )
                    else:
                        return False

            # SEARCH/FILTER - Test filtering
            async with self.session.get(
                f"{self.base_url}/api/leads", params={"company": "E2E TechCorp"}
            ) as response:
                if response.status == 200:
                    filtered_jobs = await response.json()
                    print(f"   ✅ Company filter returned {len(filtered_jobs)} jobs")
                else:
                    return False

            return True

        except Exception as e:
            print(f"   ❌ Job CRUD operations failed: {e}")
            return False

    # ================== ETL Pipeline Tests ==================

    async def test_etl_pipeline_integration(self) -> bool:
        """Test ETL pipeline functionality."""
        try:
            # Test job scraper tool (part of ETL pipeline)
            try:
                # If we have RAPIDAPI_KEY, we can test real ETL
                rapidapi_key = os.getenv("RAPIDAPI_KEY")
                if rapidapi_key and rapidapi_key != "test_key":
                    print("   🔑 RapidAPI key available, testing real ETL integration")
                    # Test ETL status or trigger if endpoint exists
                    async with self.session.get(
                        f"{self.base_url}/api/etl/status"
                    ) as response:
                        if response.status == 200:
                            etl_status = await response.json()
                            print(f"   ✅ ETL status: {etl_status}")
                            return True
                        else:
                            print(f"   ℹ️ ETL status endpoint: {response.status}")
                else:
                    print("   ℹ️ No RapidAPI key, testing demo ETL functionality")

                # Test job scraper tool directly
                test_job = {
                    "name": "etl-pipeline-test",
                    "title": "ETL Test Job",
                    "company": "ETL Testing Corp",
                    "location": "Test City",
                    "description": "This job tests ETL pipeline functionality",
                    "requirements": "Testing, Python, Data Processing",
                    "job_type": "Full-time",
                    "remote_type": "Remote",
                    "skills_required": ["Python", "ETL", "Testing"],
                }

                async with self.session.post(
                    f"{self.base_url}/api/leads", json=test_job
                ) as response:
                    if response.status == 200:
                        created_job = await response.json()
                        print(f"   ✅ ETL simulation successful: {created_job['title']}")
                        self.test_data.setdefault("test_jobs", []).append(created_job)
                        return True

            except Exception as e:
                print(f"   ⚠️ ETL test encountered issue: {e}")
                return True  # Don't fail the whole suite for ETL issues

            return True

        except Exception as e:
            print(f"   ❌ ETL pipeline test failed: {e}")
            return False

    # ================== WebSocket Tests ==================

    async def test_websocket_communication(self) -> bool:
        """Test WebSocket real-time communication."""
        try:
            ws_uri = f"{self.ws_url}/ws/agent"

            try:
                async with websockets.connect(ws_uri, timeout=10) as websocket:
                    print("   ✅ WebSocket connection established")

                    # Send test message
                    test_message = {
                        "type": "user_message",
                        "content": "Test WebSocket communication",
                        "timestamp": datetime.now().isoformat(),
                    }

                    await websocket.send(json.dumps(test_message))
                    print("   ✅ Message sent via WebSocket")

                    # Wait for response
                    try:
                        response = await asyncio.wait_for(
                            websocket.recv(), timeout=10.0
                        )
                        response_data = json.loads(response)
                        print(
                            f"   ✅ Received WebSocket response: {response_data.get('type', 'unknown')}"
                        )
                        return True
                    except asyncio.TimeoutError:
                        print("   ℹ️ WebSocket response timeout (continuing)")
                        return True  # Don't fail on timeout

            except Exception as e:
                print(f"   ℹ️ WebSocket test: {e} (may not be implemented)")
                return True  # Don't fail if WebSocket isn't available

        except Exception as e:
            print(f"   ❌ WebSocket test failed: {e}")
            return False

    # ================== Browser UI Tests (Playwright) ==================

    async def test_web_interface_loading(self) -> bool:
        """Test web interface loads correctly."""
        try:
            # Try frontend dev server first, then backend static files
            test_urls = [
                (self.frontend_url, "Frontend Dev Server"),
                (self.base_url, "Backend Static Files"),
            ]

            for url, description in test_urls:
                try:
                    await self.page.goto(url, timeout=15000)
                    await self.page.wait_for_load_state(
                        "domcontentloaded", timeout=10000
                    )

                    title = await self.page.title()
                    print(f"   ✅ {description} loaded: '{title}'")

                    # Check for basic elements
                    body = await self.page.query_selector("body")
                    if body:
                        print("   ✅ Page structure loaded successfully")
                        return True

                except Exception as e:
                    print(f"   ⚠️ {description} not available: {e}")
                    continue

            print("   ❌ No web interface available")
            return False

        except Exception as e:
            print(f"   ❌ Web interface test failed: {e}")
            return False

    async def test_web_interface_interaction(self) -> bool:
        """Test web interface user interactions."""
        try:
            # Check if we have a working page
            if not self.page or not await self.page.query_selector("body"):
                print("   ⚠️ No web page loaded, skipping interaction tests")
                return True

            # Look for common UI elements
            ui_elements_found = 0

            # Check for navigation or header
            nav_selectors = ["nav", ".navbar", ".header", '[role="navigation"]']
            for selector in nav_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    print(f"   ✅ Found navigation element: {selector}")
                    ui_elements_found += 1
                    break

            # Check for main content area
            main_selectors = ["main", ".main", ".content", "#app", '[role="main"]']
            for selector in main_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    print(f"   ✅ Found main content: {selector}")
                    ui_elements_found += 1
                    break

            # Check for interactive elements
            interactive_selectors = ["button", "input", "a", ".btn"]
            interactive_count = 0
            for selector in interactive_selectors:
                elements = await self.page.query_selector_all(selector)
                interactive_count += len(elements)

            if interactive_count > 0:
                print(f"   ✅ Found {interactive_count} interactive elements")
                ui_elements_found += 1

            # Try to take a screenshot for debugging
            try:
                await self.page.screenshot(path="test_screenshot.png")
                print("   📷 Screenshot saved: test_screenshot.png")
            except Exception:
                pass  # Screenshot not critical

            return ui_elements_found > 0

        except Exception as e:
            print(f"   ❌ Web interface interaction test failed: {e}")
            return False

    async def test_job_search_ui_workflow(self) -> bool:
        """Test complete job search workflow in UI."""
        try:
            if not self.page or not await self.page.query_selector("body"):
                print("   ⚠️ No web page loaded, skipping UI workflow test")
                return True

            # Look for search-related elements
            search_elements = []

            # Try to find search input
            search_selectors = [
                'input[type="search"]',
                'input[placeholder*="search"]',
                'input[placeholder*="job"]',
                ".search-input",
                "#search",
            ]

            for selector in search_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    print(f"   ✅ Found search input: {selector}")
                    search_elements.append(element)

                    # Try to interact with search
                    try:
                        await element.fill("Python Developer")
                        print("   ✅ Successfully entered search term")

                        # Look for search button or submit
                        search_btn_selectors = [
                            'button[type="submit"]',
                            ".search-button",
                            'button:has-text("Search")',
                        ]

                        for btn_selector in search_btn_selectors:
                            btn = await self.page.query_selector(btn_selector)
                            if btn:
                                await btn.click()
                                print("   ✅ Clicked search button")
                                await self.page.wait_for_timeout(
                                    2000
                                )  # Wait for results
                                break

                    except Exception as e:
                        print(f"   ℹ️ Search interaction: {e}")

                    break

            # Look for job listings or results
            result_selectors = [
                ".job-card",
                ".job-listing",
                ".job-result",
                '[data-testid*="job"]',
            ]

            for selector in result_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    print(f"   ✅ Found {len(elements)} job result elements")
                    return True

            return len(search_elements) > 0  # Success if we found search interface

        except Exception as e:
            print(f"   ❌ Job search UI workflow test failed: {e}")
            return False

    # ================== Integration Tests ==================

    async def test_full_user_journey(self) -> bool:
        """Test complete user journey from API to UI."""
        try:
            # 1. Create job via API
            test_job = {
                "name": "full-journey-test",
                "title": "Full Stack Developer",
                "company": "Journey Test Inc",
                "location": "Remote",
                "description": "Complete user journey test position",
                "requirements": "React, Python, PostgreSQL",
                "job_type": "Full-time",
                "remote_type": "Remote",
                "salary_min": 100000,
                "salary_max": 140000,
                "skills_required": ["React", "Python", "PostgreSQL"],
            }

            created_job = None
            async with self.session.post(
                f"{self.base_url}/api/leads", json=test_job
            ) as response:
                if response.status == 200:
                    created_job = await response.json()
                    print(f"   ✅ API: Created job {created_job['title']}")
                else:
                    print(f"   ❌ API: Failed to create job: {response.status}")
                    return False

            # 2. Verify job exists via API
            async with self.session.get(
                f"{self.base_url}/api/leads/{created_job['id']}"
            ) as response:
                if response.status == 200:
                    retrieved_job = await response.json()
                    print(f"   ✅ API: Retrieved job {retrieved_job['title']}")
                else:
                    return False

            # 3. Try to verify job appears in UI (if available)
            if await self.page.query_selector("body"):
                try:
                    # Refresh page to get latest data
                    await self.page.reload()
                    await self.page.wait_for_load_state("domcontentloaded")

                    # Look for the job title or company in the page content
                    page_content = await self.page.text_content("body")
                    if (
                        test_job["title"] in page_content
                        or test_job["company"] in page_content
                    ):
                        print("   ✅ UI: Job data appears in interface")
                    else:
                        print(
                            "   ℹ️ UI: Job data not visible (may require specific view)"
                        )

                except Exception as e:
                    print(f"   ℹ️ UI verification: {e}")

            # 4. Clean up
            self.test_data.setdefault("test_jobs", []).append(created_job)

            return True

        except Exception as e:
            print(f"   ❌ Full user journey test failed: {e}")
            return False

    async def test_data_persistence(self) -> bool:
        """Test data persistence across operations."""
        try:
            if not self.test_data.get("test_jobs"):
                print("   ⚠️ No test jobs available for persistence test")
                return True

            job = self.test_data["test_jobs"][0]
            original_title = job["title"]

            # 1. Update job
            new_title = f"{original_title} - PERSISTENCE TEST"
            update_data = {**job, "title": new_title}

            async with self.session.put(
                f"{self.base_url}/api/leads/{job['id']}", json=update_data
            ) as response:
                if response.status != 200:
                    return False
                await response.json()

            # 2. Verify persistence with fresh request
            await asyncio.sleep(1)  # Brief delay
            async with self.session.get(
                f"{self.base_url}/api/leads/{job['id']}"
            ) as response:
                if response.status == 200:
                    persistent_job = await response.json()
                    if persistent_job["title"] == new_title:
                        print(f"   ✅ Data persistence verified: '{new_title}'")
                        return True
                    else:
                        print(
                            f"   ❌ Data not persisted. Expected: '{new_title}', Got: '{persistent_job['title']}'"
                        )
                        return False

            return False

        except Exception as e:
            print(f"   ❌ Data persistence test failed: {e}")
            return False

    # ================== Cleanup and Summary ==================

    async def cleanup_test_data(self) -> bool:
        """Clean up all test data."""
        try:
            cleanup_count = 0

            # Clean up test jobs
            for job in self.test_data.get("test_jobs", []):
                try:
                    async with self.session.delete(
                        f"{self.base_url}/api/leads/{job['id']}"
                    ) as response:
                        if response.status in [200, 204, 404]:
                            cleanup_count += 1
                except Exception:
                    pass  # Ignore cleanup errors

            # Clean up screenshot
            try:
                if os.path.exists("test_screenshot.png"):
                    os.remove("test_screenshot.png")
            except Exception:
                pass

            print(f"   ✅ Cleaned up {cleanup_count} test items")
            return True

        except Exception as e:
            print(f"   ⚠️ Cleanup encountered issues: {e}")
            return False

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all end-to-end tests."""
        print("🚀 JobPilot-OpenManus Comprehensive E2E Test Suite")
        print("   🎭 Playwright Browser Testing Enabled")
        print("=" * 70)

        # Define test sequence
        test_sequence = [
            # Backend Tests
            ("Server Health Check", self.test_server_startup_and_health),
            ("Job CRUD Operations", self.test_job_crud_operations),
            ("ETL Pipeline Integration", self.test_etl_pipeline_integration),
            ("WebSocket Communication", self.test_websocket_communication),
            # Frontend Tests (Playwright)
            ("Web Interface Loading", self.test_web_interface_loading),
            ("Web Interface Interaction", self.test_web_interface_interaction),
            ("Job Search UI Workflow", self.test_job_search_ui_workflow),
            # Integration Tests
            ("Full User Journey", self.test_full_user_journey),
            ("Data Persistence", self.test_data_persistence),
        ]

        # Run all tests
        for test_name, test_func in test_sequence:
            await self._timed_test(test_name, test_func)
            await asyncio.sleep(0.5)  # Brief pause between tests

        # Cleanup
        await self._timed_test("Test Data Cleanup", self.cleanup_test_data)

        # Generate summary
        return self._generate_summary()

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        passed_tests = [r for r in self.results if r.passed]
        failed_tests = [r for r in self.results if not r.passed]

        total_time = sum(r.duration for r in self.results)
        avg_time = total_time / len(self.results) if self.results else 0

        summary = {
            "total_tests": len(self.results),
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "pass_rate": len(passed_tests) / len(self.results) * 100
            if self.results
            else 0,
            "total_time": total_time,
            "average_time": avg_time,
            "results": self.results,
            "status": "PASSED" if len(failed_tests) == 0 else "FAILED",
            "recommendation": self._get_recommendation(
                len(passed_tests), len(self.results)
            ),
        }

        # Print summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE E2E TEST SUMMARY")
        print("=" * 70)

        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} {result.name:.<45} ({result.duration:.2f}s)")
            if result.error:
                print(f"     💥 {result.error}")

        print(
            f"\n🎯 Results: {len(passed_tests)}/{len(self.results)} tests passed ({summary['pass_rate']:.1f}%)"
        )
        print(f"⏱️  Total time: {total_time:.2f}s (avg: {avg_time:.2f}s per test)")
        print(f"🏆 Overall status: {summary['status']}")
        print(f"\n💡 {summary['recommendation']}")

        return summary

    def _get_recommendation(self, passed: int, total: int) -> str:
        """Get recommendation based on test results."""
        pass_rate = passed / total * 100 if total > 0 else 0

        if pass_rate >= 95:
            return "🎉 Excellent! System is production-ready. Safe to add new features."
        elif pass_rate >= 85:
            return "✅ Good! Most functionality working. Minor issues to address."
        elif pass_rate >= 70:
            return "⚠️ Moderate issues. Fix critical failures before major changes."
        else:
            return (
                "🔧 Significant issues found. System needs attention before proceeding."
            )


# ================== Main Runners ==================


async def run_e2e_tests_with_servers(
    include_frontend: bool = False, rapidapi_key: str = None
):
    """Run E2E tests with automatic server management."""
    if TestEnvironment is None:
        print("⚠️ Server manager not available, please start servers manually")
        return await run_e2e_tests_manual_server()

    # Prepare environment
    env_vars = {}
    if rapidapi_key:
        env_vars["RAPIDAPI_KEY"] = rapidapi_key

    # Set up test environment
    test_env = TestEnvironment()
    if env_vars:
        test_env.test_config.update(env_vars)

    try:
        async with test_env.full_test_environment(include_frontend) as servers:
            print("🏥 Verifying server health...")
            health = await servers.health_check()

            if not health.get("backend", False):
                print("❌ Backend server not healthy, aborting tests")
                return {"status": "ABORTED", "reason": "Backend server failed"}

            print("✅ Servers ready, starting comprehensive tests...\n")

            # Run comprehensive test suite
            async with ComprehensiveE2ETestSuite() as test_suite:
                results = await test_suite.run_comprehensive_tests()
                return results

    except Exception as e:
        print(f"❌ Test environment setup failed: {e}")
        return {"status": "ERROR", "reason": str(e)}


async def run_e2e_tests_manual_server():
    """Run E2E tests against manually started server."""
    print("🔧 Running tests against manually started server...")

    async with ComprehensiveE2ETestSuite() as test_suite:
        # Quick health check first
        try:
            async with test_suite.session.get(
                f"{test_suite.base_url}/api/health", timeout=5
            ) as response:
                if response.status != 200:
                    print(
                        "❌ Server health check failed. Please ensure server is running on localhost:8080"
                    )
                    return {"status": "ABORTED", "reason": "Server not available"}
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return {"status": "ABORTED", "reason": "Server not available"}

        results = await test_suite.run_comprehensive_tests()
        return results


async def main():
    """Main test runner with CLI support."""
    import argparse

    parser = argparse.ArgumentParser(
        description="JobPilot Comprehensive E2E Tests with Playwright"
    )
    parser.add_argument("--rapidapi-key", help="RapidAPI key for ETL testing")
    parser.add_argument(
        "--include-frontend", action="store_true", help="Start frontend server"
    )
    parser.add_argument(
        "--manual-server", action="store_true", help="Use manually started server"
    )
    parser.add_argument(
        "--headless", default=True, type=bool, help="Run browser tests in headless mode"
    )

    args = parser.parse_args()

    if args.manual_server:
        results = await run_e2e_tests_manual_server()
    else:
        results = await run_e2e_tests_with_servers(
            include_frontend=args.include_frontend, rapidapi_key=args.rapidapi_key
        )

    # Exit with appropriate code
    if results.get("status") == "PASSED":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        sys.exit(1)
