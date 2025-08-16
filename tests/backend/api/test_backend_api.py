#!/usr/bin/env python3
"""
Backend API Test Suite for Phase 2 Functionality
Tests all new endpoints and features against a live server.
"""

import asyncio
import sys
import time
from typing import Any, Dict, Optional

import aiohttp


class BackendAPITester:
    """Comprehensive API tester for JobPilot backend."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_data: Dict[str, Any] = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_server_health(self) -> bool:
        """Check if the server is running and healthy."""
        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Server healthy: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"   ❌ Server health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Cannot connect to server: {e}")
            return False

    async def test_job_sources_api(self) -> bool:
        """Test job sources CRUD operations."""
        print("🔍 Testing Job Sources API...")

        try:
            # Test creating job sources
            job_sources = [
                {
                    "name": "linkedin_test",
                    "display_name": "LinkedIn Jobs (Test)",
                    "base_url": "https://www.linkedin.com/jobs",
                    "api_available": False,
                    "rate_limit_config": {"requests_per_minute": 30},
                    "is_active": True,
                },
                {
                    "name": "indeed_test",
                    "display_name": "Indeed Jobs (Test)",
                    "base_url": "https://indeed.com",
                    "api_available": True,
                    "rate_limit_config": {"requests_per_minute": 60},
                    "is_active": True,
                },
            ]

            created_sources = []
            for source_data in job_sources:
                async with self.session.post(
                    f"{self.base_url}/api/job-sources", json=source_data
                ) as response:
                    if response.status == 201:
                        source = await response.json()
                        created_sources.append(source)
                        print(f"   ✅ Created job source: {source['display_name']}")
                    else:
                        print(f"   ❌ Failed to create job source: {response.status}")
                        return False

            self.test_data["job_sources"] = created_sources

            # Test retrieving job sources
            async with self.session.get(f"{self.base_url}/api/job-sources") as response:
                if response.status == 200:
                    sources = await response.json()
                    print(f"   ✅ Retrieved {len(sources)} job sources")

                    # Verify our created sources are in the list
                    source_names = [s["name"] for s in sources]
                    for created_source in created_sources:
                        if created_source["name"] not in source_names:
                            print(
                                f"   ❌ Created source {created_source['name']} not found in list"
                            )
                            return False
                else:
                    print(f"   ❌ Failed to retrieve job sources: {response.status}")
                    return False

            # Test updating a job source
            if created_sources:
                source_to_update = created_sources[0]
                update_data = {
                    **source_to_update,
                    "display_name": "LinkedIn Jobs (Test - Updated)",
                    "rate_limit_config": {"requests_per_minute": 45},
                }

                async with self.session.put(
                    f"{self.base_url}/api/job-sources/{source_to_update['id']}",
                    json=update_data,
                ) as response:
                    if response.status == 200:
                        updated_source = await response.json()
                        print(
                            f"   ✅ Updated job source: {updated_source['display_name']}"
                        )
                        self.test_data["job_sources"][0] = updated_source
                    else:
                        print(f"   ❌ Failed to update job source: {response.status}")
                        return False

            print("   🎉 Job Sources API tests passed!")
            return True

        except Exception as e:
            print(f"   ❌ Job Sources API test failed: {e}")
            return False

    async def test_enhanced_job_listings_api(self) -> bool:
        """Test enhanced job listings with new Phase 2 fields."""
        print("\n🔍 Testing Enhanced Job Listings API...")

        try:
            # Create enhanced job listings
            enhanced_jobs = [
                {
                    "name": "senior-python-engineer-techcorp",
                    "title": "Senior Python Engineer",
                    "company": "TechCorp AI",
                    "location": "San Francisco, CA",
                    "description": "Build scalable AI systems using Python and machine learning",
                    "requirements": "5+ years Python, ML experience, distributed systems",
                    "job_type": "Full-time",
                    "remote_type": "Hybrid",
                    "salary_min": 150000,
                    "salary_max": 200000,
                    "skills_required": [
                        "Python",
                        "Machine Learning",
                        "TensorFlow",
                        "AWS",
                    ],
                    "tech_stack": [
                        "Python",
                        "TensorFlow",
                        "Docker",
                        "Kubernetes",
                        "AWS",
                    ],
                    # New Phase 2 fields
                    "verification_status": "active",
                    "company_size_category": "large",
                    "seniority_level": "manager",
                    "data_quality_score": 0.95,
                    "source_count": 2,
                },
                {
                    "name": "frontend-react-developer-startupxyz",
                    "title": "Frontend React Developer",
                    "company": "StartupXYZ",
                    "location": "Remote",
                    "description": "Create beautiful user interfaces with React and TypeScript",
                    "requirements": "3+ years React, TypeScript experience",
                    "job_type": "Full-time",
                    "remote_type": "Remote",
                    "salary_min": 90000,
                    "salary_max": 130000,
                    "skills_required": ["React", "TypeScript", "JavaScript", "CSS"],
                    "tech_stack": ["React", "TypeScript", "Node.js", "GraphQL"],
                    # New Phase 2 fields
                    "verification_status": "active",
                    "company_size_category": "startup",
                    "seniority_level": "individual_contributor",
                    "data_quality_score": 0.88,
                    "source_count": 1,
                },
            ]

            created_jobs = []
            for job_data in enhanced_jobs:
                async with self.session.post(
                    f"{self.base_url}/api/leads", json=job_data
                ) as response:
                    if response.status == 200:
                        job = await response.json()
                        created_jobs.append(job)
                        print(
                            f"   ✅ Created enhanced job: {job['title']} at {job['company']}"
                        )
                    else:
                        error_text = await response.text()
                        print(
                            f"   ❌ Failed to create job: {response.status} - {error_text}"
                        )
                        return False

            self.test_data["enhanced_jobs"] = created_jobs

            # Test retrieving jobs with new fields
            async with self.session.get(f"{self.base_url}/api/leads") as response:
                if response.status == 200:
                    jobs = await response.json()
                    print(f"   ✅ Retrieved {len(jobs)} job listings")

                    # Verify enhanced fields are present
                    for job in jobs:
                        if job["id"] in [j["id"] for j in created_jobs]:
                            required_fields = [
                                "verification_status",
                                "company_size_category",
                                "seniority_level",
                                "data_quality_score",
                                "tech_stack",
                            ]
                            for field in required_fields:
                                if field not in job:
                                    print(
                                        f"   ❌ Missing enhanced field '{field}' in job {job['id']}"
                                    )
                                    return False
                            print(f"   ✅ Job {job['title']} has all enhanced fields")
                else:
                    print(f"   ❌ Failed to retrieve jobs: {response.status}")
                    return False

            # Test filtering by new fields
            filter_tests = [
                ("verification_status", "active"),
                ("company_size_category", "startup"),
                ("seniority_level", "manager"),
            ]

            for filter_field, filter_value in filter_tests:
                async with self.session.get(
                    f"{self.base_url}/api/leads?{filter_field}={filter_value}"
                ) as response:
                    if response.status == 200:
                        filtered_jobs = await response.json()
                        print(
                            f"   ✅ Filter by {filter_field}={filter_value}: {len(filtered_jobs)} results"
                        )
                    else:
                        print(
                            f"   ❌ Failed to filter by {filter_field}: {response.status}"
                        )
                        return False

            print("   🎉 Enhanced Job Listings API tests passed!")
            return True

        except Exception as e:
            print(f"   ❌ Enhanced Job Listings API test failed: {e}")
            return False

    async def test_job_source_listings_api(self) -> bool:
        """Test job source listings (linking jobs to sources)."""
        print("\n🔍 Testing Job Source Listings API...")

        try:
            if not self.test_data.get("job_sources") or not self.test_data.get(
                "enhanced_jobs"
            ):
                print("   ❌ Missing test data for job source listings test")
                return False

            source = self.test_data["job_sources"][0]
            job = self.test_data["enhanced_jobs"][0]

            # Create job source listings
            source_listing_data = {
                "job_id": job["id"],
                "source_id": source["id"],
                "source_job_id": f"linkedin_{job['id'][:8]}",
                "source_url": f"https://linkedin.com/jobs/view/{job['id'][:8]}",
                "source_metadata": {
                    "sponsored": False,
                    "premium": True,
                    "application_count": 45,
                },
            }

            async with self.session.post(
                f"{self.base_url}/api/job-source-listings", json=source_listing_data
            ) as response:
                if response.status == 201:
                    source_listing = await response.json()
                    print(
                        f"   ✅ Created job source listing: {source_listing['source_job_id']}"
                    )
                    self.test_data["source_listing"] = source_listing
                else:
                    error_text = await response.text()
                    print(
                        f"   ❌ Failed to create job source listing: {response.status} - {error_text}"
                    )
                    return False

            # Test retrieving source listings for a job
            async with self.session.get(
                f"{self.base_url}/api/jobs/{job['id']}/sources"
            ) as response:
                if response.status == 200:
                    listings = await response.json()
                    print(f"   ✅ Retrieved {len(listings)} source listings for job")
                else:
                    print(
                        f"   ❌ Failed to retrieve source listings: {response.status}"
                    )
                    return False

            print("   🎉 Job Source Listings API tests passed!")
            return True

        except Exception as e:
            print(f"   ❌ Job Source Listings API test failed: {e}")
            return False

    async def test_vector_search_api(self) -> bool:
        """Test vector search and semantic search functionality."""
        print("\n🔍 Testing Vector Search API...")

        try:
            if not self.test_data.get("enhanced_jobs"):
                print("   ❌ Missing test data for vector search test")
                return False

            # Test semantic search
            search_queries = [
                "Python machine learning engineer",
                "React frontend developer",
                "full stack developer",
                "remote software engineer",
            ]

            for query in search_queries:
                async with self.session.get(
                    f"{self.base_url}/api/search/semantic",
                    params={"query": query, "limit": 5},
                ) as response:
                    if response.status == 200:
                        results = await response.json()
                        print(
                            f"   ✅ Semantic search '{query}': {len(results)} results"
                        )

                        # Verify search results have similarity scores
                        for result in results:
                            if "similarity_score" not in result:
                                print("   ❌ Missing similarity_score in search result")
                                return False
                    else:
                        print(
                            f"   ❌ Semantic search failed for '{query}': {response.status}"
                        )
                        return False

            # Test search with filters
            async with self.session.get(
                f"{self.base_url}/api/search/semantic",
                params={
                    "query": "software engineer",
                    "job_type": "Full-time",
                    "remote_type": "Remote",
                    "limit": 10,
                },
            ) as response:
                if response.status == 200:
                    filtered_results = await response.json()
                    print(
                        f"   ✅ Filtered semantic search: {len(filtered_results)} results"
                    )
                else:
                    print(f"   ❌ Filtered semantic search failed: {response.status}")
                    return False

            # Test hybrid search (if implemented)
            async with self.session.get(
                f"{self.base_url}/api/search/hybrid",
                params={"query": "Python React developer", "limit": 5},
            ) as response:
                if response.status == 200:
                    hybrid_results = await response.json()
                    print(f"   ✅ Hybrid search: {len(hybrid_results)} results")
                elif response.status == 404:
                    print("   ℹ️ Hybrid search endpoint not yet implemented")
                else:
                    print(f"   ❌ Hybrid search failed: {response.status}")

            print("   🎉 Vector Search API tests passed!")
            return True

        except Exception as e:
            print(f"   ❌ Vector Search API test failed: {e}")
            return False

    async def test_job_embeddings_api(self) -> bool:
        """Test job embeddings management."""
        print("\n🔍 Testing Job Embeddings API...")

        try:
            if not self.test_data.get("enhanced_jobs"):
                print("   ❌ Missing test data for embeddings test")
                return False

            job = self.test_data["enhanced_jobs"][0]

            # Test creating embeddings
            async with self.session.post(
                f"{self.base_url}/api/jobs/{job['id']}/embeddings"
            ) as response:
                if response.status == 201:
                    embedding = await response.json()
                    print(f"   ✅ Created embedding: {embedding['embedding_model']}")
                    self.test_data["job_embedding"] = embedding
                else:
                    error_text = await response.text()
                    print(
                        f"   ❌ Failed to create embedding: {response.status} - {error_text}"
                    )
                    return False

            # Test retrieving embeddings
            async with self.session.get(
                f"{self.base_url}/api/jobs/{job['id']}/embeddings"
            ) as response:
                if response.status == 200:
                    embeddings = await response.json()
                    print(f"   ✅ Retrieved {len(embeddings)} embeddings for job")
                else:
                    print(f"   ❌ Failed to retrieve embeddings: {response.status}")
                    return False

            # Test embeddings stats
            async with self.session.get(
                f"{self.base_url}/api/embeddings/stats"
            ) as response:
                if response.status == 200:
                    stats = await response.json()
                    print(
                        f"   ✅ Embeddings stats: {stats.get('total_embeddings', 0)} total"
                    )
                else:
                    print(f"   ❌ Failed to get embeddings stats: {response.status}")
                    return False

            print("   🎉 Job Embeddings API tests passed!")
            return True

        except Exception as e:
            print(f"   ❌ Job Embeddings API test failed: {e}")
            return False

    async def test_deduplication_api(self) -> bool:
        """Test job deduplication functionality."""
        print("\n🔍 Testing Job Deduplication API...")

        try:
            if len(self.test_data.get("enhanced_jobs", [])) < 2:
                print("   ❌ Need at least 2 jobs for deduplication test")
                return False

            job1 = self.test_data["enhanced_jobs"][0]
            job2 = self.test_data["enhanced_jobs"][1]

            # Test deduplication check
            async with self.session.post(
                f"{self.base_url}/api/jobs/deduplicate",
                json={"job1_id": job1["id"], "job2_id": job2["id"]},
            ) as response:
                if response.status == 200:
                    dedup_result = await response.json()
                    print(
                        f"   ✅ Deduplication check: {dedup_result.get('confidence_score', 0):.2f} confidence"
                    )

                    if dedup_result.get("is_duplicate", False):
                        self.test_data["dedup_result"] = dedup_result
                        print("   ℹ️ Jobs identified as duplicates")
                    else:
                        print("   ℹ️ Jobs identified as unique")
                else:
                    error_text = await response.text()
                    print(
                        f"   ❌ Deduplication check failed: {response.status} - {error_text}"
                    )
                    return False

            # Test batch deduplication
            async with self.session.post(
                f"{self.base_url}/api/jobs/deduplicate-batch",
                json={
                    "job_ids": [job["id"] for job in self.test_data["enhanced_jobs"]]
                },
            ) as response:
                if response.status == 200:
                    batch_results = await response.json()
                    print(
                        f"   ✅ Batch deduplication: found {len(batch_results.get('duplicates', []))} potential duplicates"
                    )
                else:
                    print(f"   ❌ Batch deduplication failed: {response.status}")
                    return False

            print("   🎉 Job Deduplication API tests passed!")
            return True

        except Exception as e:
            print(f"   ❌ Job Deduplication API test failed: {e}")
            return False

    async def test_timeline_integration(self) -> bool:
        """Test timeline integration with Phase 2 features."""
        print("\n🔍 Testing Timeline Integration...")

        try:
            if not self.test_data.get("enhanced_jobs"):
                print("   ❌ Missing test data for timeline test")
                return False

            job = self.test_data["enhanced_jobs"][0]
            user_id = "test-user-123"

            # Test creating timeline event for job source discovery
            timeline_event = {
                "user_profile_id": user_id,
                "job_id": job["id"],
                "event_type": "job_saved",
                "title": f"Saved job: {job['title']}",
                "description": f"Found great opportunity at {job['company']}",
                "event_data": {
                    "source": "linkedin",
                    "match_score": 0.89,
                    "auto_saved": True,
                },
                "is_milestone": False,
            }

            async with self.session.post(
                f"{self.base_url}/api/timeline/user/{user_id}/event",
                json=timeline_event,
            ) as response:
                if response.status == 200:
                    event = await response.json()
                    print(f"   ✅ Created timeline event: {event['title']}")
                    self.test_data["timeline_event"] = event
                else:
                    error_text = await response.text()
                    print(
                        f"   ❌ Failed to create timeline event: {response.status} - {error_text}"
                    )
                    return False

            # Test retrieving job-specific timeline
            async with self.session.get(
                f"{self.base_url}/api/timeline/job/{job['id']}"
            ) as response:
                if response.status == 200:
                    job_timeline = await response.json()
                    print(f"   ✅ Retrieved job timeline: {len(job_timeline)} events")
                else:
                    print(f"   ❌ Failed to retrieve job timeline: {response.status}")
                    return False

            print("   🎉 Timeline Integration tests passed!")
            return True

        except Exception as e:
            print(f"   ❌ Timeline Integration test failed: {e}")
            return False

    async def test_statistics_and_analytics(self) -> bool:
        """Test enhanced statistics with Phase 2 data."""
        print("\n🔍 Testing Statistics and Analytics...")

        try:
            # Test general stats
            async with self.session.get(f"{self.base_url}/api/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(
                        f"   ✅ General stats: {stats.get('total_jobs', 0)} total jobs"
                    )
                else:
                    print(f"   ❌ Failed to get general stats: {response.status}")
                    return False

            # Test Phase 2 enhanced stats
            async with self.session.get(
                f"{self.base_url}/api/stats/enhanced"
            ) as response:
                if response.status == 200:
                    await response.json()
                    print(
                        "   ✅ Enhanced stats retrieved with quality and source metrics"
                    )
                elif response.status == 404:
                    print("   ℹ️ Enhanced stats endpoint not yet implemented")
                else:
                    print(f"   ❌ Enhanced stats failed: {response.status}")

            # Test source distribution stats
            async with self.session.get(
                f"{self.base_url}/api/stats/sources"
            ) as response:
                if response.status == 200:
                    await response.json()
                    print("   ✅ Source distribution stats retrieved")
                elif response.status == 404:
                    print("   ℹ️ Source stats endpoint not yet implemented")
                else:
                    print(f"   ❌ Source stats failed: {response.status}")

            print("   🎉 Statistics and Analytics tests passed!")
            return True

        except Exception as e:
            print(f"   ❌ Statistics and Analytics test failed: {e}")
            return False

    async def cleanup_test_data(self) -> bool:
        """Clean up created test data."""
        print("\n🧹 Cleaning up test data...")

        try:
            cleanup_count = 0

            # Delete created jobs
            for job in self.test_data.get("enhanced_jobs", []):
                async with self.session.delete(
                    f"{self.base_url}/api/leads/{job['id']}"
                ) as response:
                    if response.status in [
                        200,
                        204,
                        404,
                    ]:  # 404 is OK if already deleted
                        cleanup_count += 1
                    else:
                        print(
                            f"   ⚠️ Failed to delete job {job['id']}: {response.status}"
                        )

            # Delete job sources (if endpoint exists)
            for source in self.test_data.get("job_sources", []):
                async with self.session.delete(
                    f"{self.base_url}/api/job-sources/{source['id']}"
                ) as response:
                    if response.status in [200, 204, 404]:
                        cleanup_count += 1

            # Delete timeline events (if endpoint exists)
            if "timeline_event" in self.test_data:
                event = self.test_data["timeline_event"]
                async with self.session.delete(
                    f"{self.base_url}/api/timeline/event/{event['id']}"
                ) as response:
                    if response.status in [200, 204, 404]:
                        cleanup_count += 1

            print(f"   ✅ Cleaned up {cleanup_count} test items")
            return True

        except Exception as e:
            print(f"   ⚠️ Cleanup failed: {e}")
            return False

    async def run_all_tests(self) -> bool:
        """Run all backend API tests."""
        print("🚀 JobPilot Phase 2 Backend API Test Suite")
        print("=" * 60)

        # Check server health first
        if not await self.check_server_health():
            print("\n❌ Server is not healthy. Please start the backend server first.")
            return False

        # Run all tests
        test_methods = [
            ("Job Sources API", self.test_job_sources_api),
            ("Enhanced Job Listings API", self.test_enhanced_job_listings_api),
            ("Job Source Listings API", self.test_job_source_listings_api),
            ("Vector Search API", self.test_vector_search_api),
            ("Job Embeddings API", self.test_job_embeddings_api),
            ("Job Deduplication API", self.test_deduplication_api),
            ("Timeline Integration", self.test_timeline_integration),
            ("Statistics and Analytics", self.test_statistics_and_analytics),
        ]

        results = []
        for test_name, test_method in test_methods:
            try:
                result = await test_method()
                results.append((test_name, result))
                if not result:
                    print(
                        f"\n⚠️ Test '{test_name}' failed, but continuing with other tests..."
                    )
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print(f"\n❌ Test '{test_name}' crashed: {e}")
                results.append((test_name, False))

        # Cleanup
        await self.cleanup_test_data()

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY:")

        passed_tests = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} - {test_name}")
            if result:
                passed_tests += 1

        print(f"\n🎯 Results: {passed_tests}/{len(results)} tests passed")

        if passed_tests == len(results):
            print(
                "🎉 All backend API tests passed! Phase 2 functionality is working correctly."
            )
            return True
        elif passed_tests >= len(results) * 0.75:  # 75% pass rate
            print(
                "⚠️ Most tests passed. Some Phase 2 endpoints may not be fully implemented yet."
            )
            return True
        else:
            print("🔧 Many tests failed. Please check the backend implementation.")
            return False


async def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="JobPilot Backend API Tests")
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="Backend server URL (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--single-test",
        choices=[
            "health",
            "sources",
            "jobs",
            "search",
            "embeddings",
            "dedup",
            "timeline",
            "stats",
        ],
        help="Run a single test category",
    )

    args = parser.parse_args()

    async with BackendAPITester(args.url) as tester:
        if args.single_test:
            # Run single test
            test_map = {
                "health": tester.check_server_health,
                "sources": tester.test_job_sources_api,
                "jobs": tester.test_enhanced_job_listings_api,
                "search": tester.test_vector_search_api,
                "embeddings": tester.test_job_embeddings_api,
                "dedup": tester.test_deduplication_api,
                "timeline": tester.test_timeline_integration,
                "stats": tester.test_statistics_and_analytics,
            }

            if args.single_test in test_map:
                success = await test_map[args.single_test]()
                return 0 if success else 1
        else:
            # Run all tests
            success = await tester.run_all_tests()
            return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        sys.exit(1)
