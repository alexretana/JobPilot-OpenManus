#!/usr/bin/env python3
"""
Comprehensive Backend API Tests using FastAPI TestClient and pytest

This test suite validates all backend API functionality using FastAPI's built-in
TestClient for fast, reliable testing without server startup overhead.
"""

import pytest
import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timezone
import json

# FastAPI testing imports
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ==================== Fixtures ====================

@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Get the FastAPI application instance."""
    try:
        import web_server
        return web_server.app
    except ImportError as e:
        pytest.skip(f"Cannot import web_server: {e}")


@pytest.fixture(scope="session")
def client(app: FastAPI) -> TestClient:
    """Create FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture(scope="function")
def clean_database():
    """Clean database before and after each test."""
    # Setup: Clean database
    try:
        from app.data.database import get_database_manager
        db_manager = get_database_manager()
        
        # Clean up any existing test data
        with db_manager.get_session() as session:
            # Delete test jobs (those with test prefixes)
            from app.data.models import JobListingDB
            test_jobs = session.query(JobListingDB).filter(
                JobListingDB.name.like('test_%')
            ).all()
            for job in test_jobs:
                session.delete(job)
            session.commit()
            
    except Exception as e:
        pytest.skip(f"Database setup failed: {e}")
    
    yield
    
    # Teardown: Clean database
    try:
        with db_manager.get_session() as session:
            test_jobs = session.query(JobListingDB).filter(
                JobListingDB.name.like('test_%')
            ).all()
            for job in test_jobs:
                session.delete(job)
            session.commit()
    except Exception:
        pass  # Ignore cleanup failures


@pytest.fixture
def sample_job_data() -> Dict[str, Any]:
    """Sample job data for testing."""
    return {
        "name": "test-backend-job",
        "title": "Backend Test Engineer",
        "company": "Test Corp",
        "location": "Test City, TC",
        "description": "Test backend API functionality and ensure quality",
        "requirements": "Python, FastAPI, pytest, testing experience",
        "job_type": "Full-time",
        "remote_type": "Remote",
        "salary_min": 80000,
        "salary_max": 120000,
        "skills_required": ["Python", "FastAPI", "pytest", "Testing"],
        "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
        "benefits": ["Health insurance", "Remote work", "Professional development"]
    }


@pytest.fixture
def multiple_job_data() -> List[Dict[str, Any]]:
    """Multiple job records for bulk testing."""
    return [
        {
            "name": "test-python-dev",
            "title": "Senior Python Developer",
            "company": "Python Corp",
            "location": "Remote",
            "description": "Build scalable Python applications",
            "requirements": "5+ years Python, Django/Flask",
            "job_type": "Full-time",
            "remote_type": "Remote",
            "salary_min": 100000,
            "salary_max": 140000,
            "skills_required": ["Python", "Django", "PostgreSQL"]
        },
        {
            "name": "test-react-dev",
            "title": "React Frontend Developer", 
            "company": "Frontend Inc",
            "location": "New York, NY",
            "description": "Create amazing user experiences",
            "requirements": "3+ years React, TypeScript",
            "job_type": "Full-time",
            "remote_type": "Hybrid",
            "salary_min": 85000,
            "salary_max": 115000,
            "skills_required": ["React", "TypeScript", "JavaScript"]
        },
        {
            "name": "test-data-scientist",
            "title": "Data Scientist",
            "company": "AI Innovations",
            "location": "San Francisco, CA",
            "description": "Extract insights from complex datasets",
            "requirements": "PhD in Statistics, Python, ML experience",
            "job_type": "Full-time",
            "remote_type": "Hybrid",
            "salary_min": 130000,
            "salary_max": 180000,
            "skills_required": ["Python", "Machine Learning", "Statistics", "SQL"]
        }
    ]


# ==================== Health & Basic API Tests ====================

class TestHealthAndBasics:
    """Test basic API functionality and health endpoints."""
    
    def test_health_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "ok"]
        
        # Validate timestamp format
        timestamp_str = data["timestamp"]
        datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    
    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_invalid_endpoint(self, client: TestClient):
        """Test invalid endpoint returns proper error."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404


# ==================== Job CRUD Tests ====================

class TestJobCRUD:
    """Test job creation, reading, updating, and deletion."""
    
    def test_create_job_success(self, client: TestClient, sample_job_data: Dict, clean_database):
        """Test successful job creation."""
        response = client.post("/api/leads", json=sample_job_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_job_data["title"]
        assert data["company"] == sample_job_data["company"]
        assert data["salary_min"] == sample_job_data["salary_min"]
        assert data["skills_required"] == sample_job_data["skills_required"]
        
        # Store job ID for cleanup
        return data
    
    def test_create_job_invalid_data(self, client: TestClient):
        """Test job creation with invalid data."""
        invalid_data = {
            "name": "",  # Empty name should fail
            "title": "",  # Empty title should fail
            # Missing required fields
        }
        
        response = client.post("/api/leads", json=invalid_data)
        assert response.status_code in [400, 422]  # Validation error
    
    def test_get_all_jobs(self, client: TestClient):
        """Test retrieving all jobs."""
        response = client.get("/api/leads")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_job_by_id(self, client: TestClient, sample_job_data: Dict, clean_database):
        """Test retrieving a specific job by ID."""
        # First create a job
        create_response = client.post("/api/leads", json=sample_job_data)
        assert create_response.status_code == 200
        created_job = create_response.json()
        
        # Then retrieve it
        job_id = created_job["id"]
        response = client.get(f"/api/leads/{job_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == job_id
        assert data["title"] == sample_job_data["title"]
    
    def test_get_nonexistent_job(self, client: TestClient):
        """Test retrieving a non-existent job."""
        response = client.get("/api/leads/nonexistent-id")
        assert response.status_code == 404
    
    def test_update_job(self, client: TestClient, sample_job_data: Dict, clean_database):
        """Test updating a job."""
        # Create job first
        create_response = client.post("/api/leads", json=sample_job_data)
        created_job = create_response.json()
        job_id = created_job["id"]
        
        # Update the job
        updated_data = {
            **created_job,
            "title": "Updated Backend Test Engineer",
            "salary_max": 150000,
            "description": "Updated description for testing purposes"
        }
        
        response = client.put(f"/api/leads/{job_id}", json=updated_data)
        assert response.status_code == 200
        
        updated_job = response.json()
        assert updated_job["title"] == "Updated Backend Test Engineer"
        assert updated_job["salary_max"] == 150000
        assert updated_job["id"] == job_id
    
    def test_delete_job(self, client: TestClient, sample_job_data: Dict, clean_database):
        """Test deleting a job."""
        # Create job first
        create_response = client.post("/api/leads", json=sample_job_data)
        created_job = create_response.json()
        job_id = created_job["id"]
        
        # Delete the job
        response = client.delete(f"/api/leads/{job_id}")
        assert response.status_code in [200, 204]
        
        # Verify job is deleted
        get_response = client.get(f"/api/leads/{job_id}")
        assert get_response.status_code == 404


# ==================== Job Search and Filtering Tests ====================

class TestJobSearchAndFiltering:
    """Test job search and filtering functionality."""
    
    @pytest.fixture
    def setup_multiple_jobs(self, client: TestClient, multiple_job_data: List[Dict], clean_database):
        """Set up multiple jobs for search testing."""
        created_jobs = []
        for job_data in multiple_job_data:
            response = client.post("/api/leads", json=job_data)
            if response.status_code == 200:
                created_jobs.append(response.json())
        
        yield created_jobs
    
    def test_filter_by_company(self, client: TestClient, setup_multiple_jobs):
        """Test filtering jobs by company."""
        response = client.get("/api/leads", params={"company": "Python Corp"})
        assert response.status_code == 200
        
        jobs = response.json()
        for job in jobs:
            assert "Python Corp" in job["company"]
    
    def test_filter_by_job_type(self, client: TestClient, setup_multiple_jobs):
        """Test filtering jobs by job type."""
        response = client.get("/api/leads", params={"job_type": "Full-time"})
        assert response.status_code == 200
        
        jobs = response.json()
        for job in jobs:
            assert job["job_type"] == "Full-time"
    
    def test_filter_by_remote_type(self, client: TestClient, setup_multiple_jobs):
        """Test filtering jobs by remote work type."""
        response = client.get("/api/leads", params={"remote_type": "Remote"})
        assert response.status_code == 200
        
        jobs = response.json()
        for job in jobs:
            assert job["remote_type"] == "Remote"
    
    def test_filter_by_salary_range(self, client: TestClient, setup_multiple_jobs):
        """Test filtering jobs by salary range."""
        response = client.get("/api/leads", params={"min_salary": 100000})
        assert response.status_code == 200
        
        jobs = response.json()
        for job in jobs:
            # Job should have salary_min >= 100000 or salary_max >= 100000
            assert job["salary_min"] >= 100000 or job["salary_max"] >= 100000
    
    def test_pagination(self, client: TestClient, setup_multiple_jobs):
        """Test job listing pagination."""
        # Test with limit
        response = client.get("/api/leads", params={"limit": 2})
        assert response.status_code == 200
        
        jobs = response.json()
        assert len(jobs) <= 2
        
        # Test with offset
        response = client.get("/api/leads", params={"limit": 2, "offset": 1})
        assert response.status_code == 200
    
    def test_search_functionality(self, client: TestClient, setup_multiple_jobs):
        """Test general search functionality."""
        # Test if search parameter works
        response = client.get("/api/leads", params={"search": "Python"})
        assert response.status_code == 200
        
        jobs = response.json()
        # If search is implemented, results should contain Python-related jobs
        # If not implemented, this just tests the endpoint doesn't break
    
    def test_semantic_search_endpoint(self, client: TestClient, setup_multiple_jobs):
        """Test semantic search endpoint if available."""
        response = client.get("/api/search/semantic", params={"query": "Python developer", "limit": 5})
        
        # Endpoint might not be implemented yet
        assert response.status_code in [200, 404, 501]
        
        if response.status_code == 200:
            results = response.json()
            assert isinstance(results, list)
            assert len(results) <= 5


# ==================== Statistics and Analytics Tests ====================

class TestStatisticsAndAnalytics:
    """Test statistics and analytics endpoints."""
    
    def test_basic_stats(self, client: TestClient):
        """Test basic statistics endpoint."""
        response = client.get("/api/stats")
        
        # Stats endpoint might not be fully implemented
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            # Common stats fields
            possible_fields = ["total_jobs", "total_companies", "total_applications"]
            assert any(field in data for field in possible_fields)
    
    def test_job_market_insights(self, client: TestClient, multiple_job_data, clean_database):
        """Test job market insights with test data."""
        # Create some jobs first
        for job_data in multiple_job_data:
            client.post("/api/leads", json=job_data)
        
        # Test various stats endpoints
        stats_endpoints = [
            "/api/stats",
            "/api/stats/skills",
            "/api/stats/companies",
            "/api/stats/locations"
        ]
        
        for endpoint in stats_endpoints:
            response = client.get(endpoint)
            # These might not all be implemented yet
            assert response.status_code in [200, 404, 501]


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Test API error handling and edge cases."""
    
    def test_malformed_json(self, client: TestClient):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/leads",
            data="{ invalid json }",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self, client: TestClient, sample_job_data):
        """Test request with missing content type."""
        response = client.post("/api/leads", data=json.dumps(sample_job_data))
        # Should either work or return proper error
        assert response.status_code in [200, 400, 415, 422]
    
    def test_unsupported_method(self, client: TestClient):
        """Test unsupported HTTP method."""
        response = client.patch("/api/leads")  # PATCH might not be supported
        assert response.status_code in [405, 404]  # Method not allowed or not found
    
    def test_large_payload(self, client: TestClient):
        """Test handling of unusually large payload."""
        large_description = "x" * 10000  # 10KB description
        large_job = {
            "name": "test-large-job",
            "title": "Test Job with Large Data",
            "company": "Test Corp",
            "location": "Test City",
            "description": large_description,
            "requirements": "Test requirements",
            "job_type": "Full-time",
            "remote_type": "Remote"
        }
        
        response = client.post("/api/leads", json=large_job)
        # Should either work or fail gracefully
        assert response.status_code in [200, 400, 413, 422]
    
    def test_sql_injection_attempt(self, client: TestClient):
        """Test protection against SQL injection."""
        malicious_data = {
            "name": "test'; DROP TABLE jobs; --",
            "title": "'; SELECT * FROM users; --",
            "company": "Test Corp",
            "location": "Test City",
            "description": "Test description",
            "requirements": "Test requirements",
            "job_type": "Full-time",
            "remote_type": "Remote"
        }
        
        response = client.post("/api/leads", json=malicious_data)
        # Should either sanitize input or reject it
        assert response.status_code in [200, 400, 422]




# ==================== Performance Tests with Markers ====================

class TestPerformance:
    """Performance tests for the API."""
    
    @pytest.mark.performance
    def test_health_endpoint_performance(self, client: TestClient):
        """Test health endpoint performance."""
        import time
        start_time = time.time()
        response = client.get("/api/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
    
    @pytest.mark.performance
    def test_bulk_job_creation_performance(self, client: TestClient, multiple_job_data, clean_database):
        """Test bulk job creation performance."""
        import time
        start_time = time.time()
        
        for job_data in multiple_job_data:
            response = client.post("/api/leads", json=job_data)
            assert response.status_code == 200
        
        end_time = time.time()
        response_time = end_time - start_time
        assert response_time < 10.0  # Should complete within 10 seconds for bulk operations
    
    @pytest.mark.performance
    def test_job_listing_performance(self, client: TestClient, multiple_job_data, clean_database):
        """Test job listing endpoint performance."""
        # Create test jobs first
        for job_data in multiple_job_data:
            client.post("/api/leads", json=job_data)
        
        import time
        start_time = time.time()
        response = client.get("/api/leads")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 5.0  # Should respond within 5 seconds


# ==================== Integration Tests with Markers ====================

class TestIntegration:
    """Test integration between different API components."""
    
    @pytest.mark.integration
    def test_complete_job_lifecycle(self, client: TestClient, sample_job_data, clean_database):
        """Test complete job lifecycle: create -> read -> update -> delete."""
        # 1. Create job
        create_response = client.post("/api/leads", json=sample_job_data)
        assert create_response.status_code == 200
        created_job = create_response.json()
        job_id = created_job["id"]
        
        # 2. Read job
        read_response = client.get(f"/api/leads/{job_id}")
        assert read_response.status_code == 200
        read_job = read_response.json()
        assert read_job["title"] == sample_job_data["title"]
        
        # 3. Update job
        updated_data = {**read_job, "title": "Updated Title"}
        update_response = client.put(f"/api/leads/{job_id}", json=updated_data)
        assert update_response.status_code == 200
        updated_job = update_response.json()
        assert updated_job["title"] == "Updated Title"
        
        # 4. Verify update persisted
        verify_response = client.get(f"/api/leads/{job_id}")
        assert verify_response.status_code == 200
        verified_job = verify_response.json()
        assert verified_job["title"] == "Updated Title"
        
        # 5. Delete job
        delete_response = client.delete(f"/api/leads/{job_id}")
        assert delete_response.status_code in [200, 204]
        
        # 6. Verify deletion
        final_response = client.get(f"/api/leads/{job_id}")
        assert final_response.status_code == 404
    
    @pytest.mark.integration
    def test_search_integration(self, client: TestClient, multiple_job_data, clean_database):
        """Test search integration with created jobs."""
        # Create jobs with specific patterns
        for job_data in multiple_job_data:
            response = client.post("/api/leads", json=job_data)
            assert response.status_code == 200
        
        # Test various search scenarios
        search_scenarios = [
            {"company": "Python Corp"},
            {"job_type": "Full-time"},
            {"remote_type": "Remote"}
        ]
        
        for search_params in search_scenarios:
            response = client.get("/api/leads", params=search_params)
            assert response.status_code == 200
            
            results = response.json()
            assert isinstance(results, list)
            
            # Verify filtering worked (at least one result should match)
            if results:  # If we have results, verify they match filter
                key, value = next(iter(search_params.items()))
                assert any(job.get(key) == value for job in results)
