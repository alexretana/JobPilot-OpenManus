#!/usr/bin/env python3
"""
Test Script for Job Board Scrapers
Tests the job scraping infrastructure with basic functionality checks.
"""

import asyncio
from datetime import datetime

import pytest

from app.tool.job_boards import JobSearchQuery, get_scraper, list_scrapers


@pytest.mark.asyncio
async def test_scraper_health_checks():
    """Test health checks for all available scrapers"""
    print("🔍 Testing scraper health checks...")

    available_scrapers = list_scrapers()
    print(f"Available scrapers: {available_scrapers}")

    results = {}

    for scraper_name in available_scrapers:
        print(f"\n📡 Testing {scraper_name} scraper:")

        try:
            scraper = get_scraper(scraper_name)

            async with scraper:
                health = await scraper.health_check()
                results[scraper_name] = health

                status = health.get("status", "unknown")
                accessible = health.get("accessible", False)
                response_time = health.get("response_time", 0)

                if accessible:
                    print(f"   ✅ Status: {status}")
                    print(f"   ✅ Response time: {response_time:.2f}s")
                    print(f"   ✅ Base URL accessible")
                else:
                    print(f"   ❌ Status: {status}")
                    print(f"   ❌ Response time: {response_time:.2f}s")
                    print(f"   ❌ Base URL not accessible")
                    if "error" in health:
                        print(f"   ❌ Error: {health['error']}")

        except Exception as e:
            print(f"   ❌ Failed to test {scraper_name}: {e}")
            results[scraper_name] = {"status": "error", "error": str(e)}

    return results


@pytest.mark.asyncio
async def test_scraper_basic_functionality():
    """Test basic scraping functionality with a simple query"""
    print("\n🔍 Testing basic scraping functionality...")

    # Test query
    test_query = JobSearchQuery(
        query="software engineer",
        location="San Francisco",
        limit=3,  # Small limit for testing
    )

    available_scrapers = list_scrapers()
    results = {}

    for scraper_name in available_scrapers:
        print(f"\n🔍 Testing {scraper_name} scraper search functionality:")

        try:
            scraper = get_scraper(scraper_name)

            async with scraper:
                # Run the test
                test_result = await scraper.test_scraper(test_query)
                results[scraper_name] = test_result

                status = test_result.get("status", "unknown")

                if status == "success":
                    jobs_found = test_result.get("jobs_found", 0)
                    scrape_time = test_result.get("scrape_time", 0)

                    print(f"   ✅ Status: {status}")
                    print(f"   ✅ Jobs found: {jobs_found}")
                    print(f"   ✅ Scrape time: {scrape_time:.2f}s")

                    # Show sample job data
                    sample_jobs = test_result.get("sample_jobs", [])
                    for i, job in enumerate(sample_jobs, 1):
                        print(f"   📋 Sample Job {i}:")
                        print(f"      Title: {job.title}")
                        print(f"      Company: {job.company}")
                        print(f"      Location: {job.location}")
                        print(f"      URL: {job.source_url}")

                elif status == "failed":
                    reason = test_result.get("reason", "Unknown")
                    print(f"   ❌ Status: {status}")
                    print(f"   ❌ Reason: {reason}")

                else:  # error
                    error = test_result.get("error", "Unknown error")
                    print(f"   ❌ Status: {status}")
                    print(f"   ❌ Error: {error}")

        except Exception as e:
            print(f"   ❌ Failed to test {scraper_name}: {e}")
            results[scraper_name] = {"status": "error", "error": str(e)}

    return results


@pytest.mark.asyncio
async def test_scraper_statistics():
    """Test scraper statistics and monitoring"""
    print("\n📊 Testing scraper statistics...")

    available_scrapers = list_scrapers()

    for scraper_name in available_scrapers:
        print(f"\n📊 {scraper_name} scraper statistics:")

        try:
            scraper = get_scraper(scraper_name)

            async with scraper:
                # Make a small request first
                await scraper.health_check()

                # Get statistics
                stats = scraper.get_stats()

                print(f"   📈 Scraper: {stats['display_name']}")
                print(f"   📈 Requests made: {stats['stats']['requests_made']}")
                print(f"   📈 Successful: {stats['stats']['successful_requests']}")
                print(f"   📈 Failed: {stats['stats']['failed_requests']}")
                print(f"   📈 Jobs scraped: {stats['stats']['jobs_scraped']}")

                rate_limits = stats["rate_limits"]
                print(f"   🚦 Rate limits:")
                print(f"      Per minute: {rate_limits['requests_per_minute']}")
                print(f"      Per hour: {rate_limits['requests_per_hour']}")
                print(f"      Current minute: {rate_limits['current_minute_requests']}")
                print(f"      Current hour: {rate_limits['current_hour_requests']}")
                print(f"      Backoff: {rate_limits['current_backoff']:.1f}s")

        except Exception as e:
            print(f"   ❌ Failed to get stats for {scraper_name}: {e}")


async def main():
    """Main test runner"""
    print("🚀 JobPilot Job Scrapers Test Suite")
    print("=" * 50)

    start_time = datetime.now()

    try:
        # Test 1: Health checks
        health_results = await test_scraper_health_checks()

        # Test 2: Basic functionality (only if health checks pass)
        healthy_scrapers = [
            name
            for name, health in health_results.items()
            if health.get("accessible", False)
        ]

        if healthy_scrapers:
            print(f"\n🎯 Proceeding with functionality tests for: {healthy_scrapers}")
            functionality_results = await test_scraper_basic_functionality()
        else:
            print("\n⚠️ No healthy scrapers found, skipping functionality tests")
            functionality_results = {}

        # Test 3: Statistics
        await test_scraper_statistics()

        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY:")

        total_scrapers = len(list_scrapers())
        healthy_count = len(healthy_scrapers)
        working_count = sum(
            1
            for result in functionality_results.values()
            if result.get("status") == "success"
        )

        print(f"   Total scrapers: {total_scrapers}")
        print(f"   Healthy scrapers: {healthy_count}")
        print(f"   Working scrapers: {working_count}")

        for scraper_name in list_scrapers():
            health_status = health_results.get(scraper_name, {}).get(
                "status", "unknown"
            )
            func_status = functionality_results.get(scraper_name, {}).get(
                "status", "not_tested"
            )

            if health_status == "healthy" and func_status == "success":
                print(f"   ✅ {scraper_name}: Fully operational")
            elif health_status == "healthy":
                print(f"   ⚠️ {scraper_name}: Accessible but scraping issues")
            else:
                print(f"   ❌ {scraper_name}: Not accessible")

        elapsed = datetime.now() - start_time
        print(f"\n🎯 Tests completed in {elapsed.total_seconds():.1f} seconds")

        if working_count > 0:
            print("🎉 Job scraper infrastructure is working!")
            return True
        else:
            print("🔧 Job scraper infrastructure needs attention")
            return False

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return False


if __name__ == "__main__":
    import sys

    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        sys.exit(1)
