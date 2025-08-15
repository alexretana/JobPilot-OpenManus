"""
JSearch API Test Script
Efficiently tests JSearch API to understand data structure and quality
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the implementations directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "implementations"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from implementations.base_client import JobSearchQuery
from implementations.jsearch_client import JSearchClient, test_jsearch_api


async def comprehensive_jsearch_test(api_key: str):
    """Comprehensive test of JSearch API with minimal API calls"""

    print("=== JSearch API Investigation ===\n")

    async with JSearchClient(api_key) as client:
        try:
            # Test 1: Authentication
            print("1. Testing Authentication...")
            auth_result = await client.authenticate()
            print(f"   Authentication: {'✅ Success' if auth_result else '❌ Failed'}")

            if not auth_result:
                print("   Cannot proceed without authentication")
                return False

            # Test 2: Basic job search
            print("\n2. Testing Basic Job Search...")
            basic_query = JobSearchQuery(
                query="python developer",
                location="San Francisco, CA",
                page=1,
                num_pages=1,  # Only get first page to save API calls
            )

            jobs_basic = await client.search_jobs(basic_query)
            print(f"   Found {len(jobs_basic)} jobs for 'python developer'")

            # Test 3: Remote jobs search
            print("\n3. Testing Remote Jobs Search...")
            remote_query = JobSearchQuery(
                query="remote software engineer", page=1, num_pages=1
            )

            jobs_remote = await client.search_jobs(remote_query)
            print(f"   Found {len(jobs_remote)} remote software engineer jobs")

            # Test 4: Filter testing (minimal to save calls)
            print("\n4. Testing Employment Type Filters...")
            filter_query = JobSearchQuery(
                query="data scientist",
                location="New York, NY",
                employment_types=["FULLTIME"],
                date_posted="week",
                page=1,
                num_pages=1,
            )

            jobs_filtered = await client.search_jobs(filter_query)
            print(
                f"   Found {len(jobs_filtered)} full-time data scientist jobs posted this week"
            )

            # Analysis of results
            print("\n=== DATA ANALYSIS ===")

            all_jobs = jobs_basic + jobs_remote + jobs_filtered
            if all_jobs:
                print(f"\nTotal jobs analyzed: {len(all_jobs)}")

                # Analyze data completeness
                print("\nData Completeness Analysis:")
                fields_analysis = analyze_field_completeness(all_jobs)
                for field, stats in fields_analysis.items():
                    print(
                        f"  {field}: {stats['filled']}/{stats['total']} ({stats['percentage']:.1f}%) complete"
                    )

                # Analyze job sources
                print("\nJob Sources Analysis:")
                sources = {}
                for job in all_jobs:
                    source = job.source_site or "Unknown"
                    sources[source] = sources.get(source, 0) + 1

                for source, count in sorted(
                    sources.items(), key=lambda x: x[1], reverse=True
                )[:10]:
                    print(f"  {source}: {count} jobs")

                # Sample job details
                print("\n=== SAMPLE JOBS ===")
                for i, job in enumerate(all_jobs[:3], 1):
                    print(f"\nSample Job #{i}:")
                    print(f"  ID: {job.id}")
                    print(f"  Title: {job.title}")
                    print(f"  Company: {job.company}")
                    print(f"  Location: {job.location}")
                    print(f"  Employment Type: {job.employment_type}")
                    print(
                        f"  Salary: {job.salary_min}-{job.salary_max} {job.salary_currency}"
                    )
                    print(f"  Posted: {job.date_posted}")
                    print(f"  Source: {job.source_site}")
                    print(f"  Apply URL: {job.apply_url}")
                    print(f"  Requirements: {job.job_requirements}")
                    print(f"  Benefits: {job.benefits}")
                    print(
                        f"  Description (first 200 chars): {job.description[:200] if job.description else 'N/A'}..."
                    )

            # Usage statistics
            print("\n=== API USAGE STATISTICS ===")
            stats = client.get_usage_stats()
            rate_limits = client.get_rate_limits()

            print(f"Requests made this session: {stats['requests_made']}")
            print(
                f"Total requests used: {rate_limits.requests_used}/{rate_limits.requests_per_month}"
            )
            print(f"Requests remaining: {rate_limits.requests_remaining}")
            print(
                f"Efficiency: {len(all_jobs) / stats['requests_made']:.1f} jobs per API call"
            )

            return True

        except Exception as e:
            print(f"Error during comprehensive test: {e}")
            return False


def analyze_field_completeness(jobs):
    """Analyze how complete the data fields are across jobs"""
    fields = [
        "title",
        "company",
        "location",
        "description",
        "salary_min",
        "salary_max",
        "employment_type",
        "date_posted",
        "apply_url",
        "company_logo",
        "job_requirements",
        "benefits",
        "source_site",
    ]

    analysis = {}
    total_jobs = len(jobs)

    for field in fields:
        filled_count = sum(
            1 for job in jobs if getattr(job, field) not in [None, "", []]
        )
        analysis[field] = {
            "total": total_jobs,
            "filled": filled_count,
            "percentage": (filled_count / total_jobs) * 100 if total_jobs > 0 else 0,
        }

    return analysis


async def quick_jsearch_test(api_key: str):
    """Quick test with a single API call"""
    print("=== Quick JSearch API Test ===\n")

    jobs = await test_jsearch_api(
        api_key=api_key, query="frontend developer", location="Seattle, WA"
    )

    if jobs:
        print(f"\n✅ Quick test successful! Found {len(jobs)} jobs.")
        return True
    else:
        print("\n❌ Quick test failed.")
        return False


def save_test_results(results: dict):
    """Save test results for analysis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"api_research/analysis/jsearch_test_results_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nTest results saved to: {filename}")


if __name__ == "__main__":
    print("JSearch API Testing Tool")
    print("This tool will make 3-4 API calls to test JSearch comprehensively.")
    print("With the free tier (200/month), this uses ~2% of your quota.")

    # Get API key
    api_key = input("\nEnter your RapidAPI key for JSearch: ").strip()

    if not api_key:
        print("API key is required. Exiting.")
        sys.exit(1)

    # Choose test type
    test_type = input(
        "\nChoose test type:\n1. Quick test (1 API call)\n2. Comprehensive test (3-4 API calls)\nEnter choice (1 or 2): "
    ).strip()

    if test_type == "1":
        # Quick test
        success = asyncio.run(quick_jsearch_test(api_key))
    elif test_type == "2":
        # Comprehensive test
        success = asyncio.run(comprehensive_jsearch_test(api_key))
    else:
        print("Invalid choice. Running quick test.")
        success = asyncio.run(quick_jsearch_test(api_key))

    if success:
        print("\n🎉 JSearch API test completed successfully!")
        print("\nNext steps:")
        print("1. Review saved response samples in api_research/responses/")
        print("2. Compare with Free Web API when ready")
        print("3. Make integration decision based on data quality")
    else:
        print("\n❌ JSearch API test failed. Check your API key and connection.")
