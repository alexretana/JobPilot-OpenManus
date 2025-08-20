"""
Test suite for Skill Bank API endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_user_id():
    """Test user ID for skill bank operations."""
    return "test-user-12345"


def test_get_skill_bank_creates_default(client, test_user_id):
    """Test that GET /skill-bank/{user_id} creates a default skill bank if none exists."""
    response = client.get(f"/api/skill-bank/{test_user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == test_user_id
    assert "skills" in data
    assert "summary_variations" in data
    assert "work_experiences" in data


def test_add_skill(client, test_user_id):
    """Test adding a new skill to the skill bank."""
    skill_data = {
        "name": "Python",
        "level": "advanced",
        "category": "technical",
        "subcategory": "Programming Languages",
        "years_experience": 5,
        "proficiency_score": 0.9,
        "description": "Expert Python developer",
        "keywords": ["programming", "backend", "web"],
        "is_featured": True,
        "display_order": 1,
    }

    response = client.post(f"/api/skill-bank/{test_user_id}/skills", json=skill_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Python"
    assert data["level"] == "advanced"
    assert data["category"] == "technical"


def test_get_skills(client, test_user_id):
    """Test getting all skills for a user."""
    # First add a skill
    skill_data = {"name": "React", "level": "intermediate", "category": "technical"}
    client.post(f"/api/skill-bank/{test_user_id}/skills", json=skill_data)

    # Then get all skills
    response = client.get(f"/api/skill-bank/{test_user_id}/skills")
    assert response.status_code == 200

    skills = response.json()
    assert isinstance(skills, list)
    assert len(skills) >= 1
    assert any(skill["name"] == "React" for skill in skills)


def test_add_summary_variation(client, test_user_id):
    """Test adding a summary variation."""
    summary_data = {
        "title": "Technical Focus",
        "content": "Senior software engineer with expertise in Python and web development.",
        "tone": "professional",
        "length": "standard",
        "focus": "technical",
        "target_industries": ["Technology", "Software"],
        "target_roles": ["Software Engineer", "Backend Developer"],
        "keywords_emphasized": ["Python", "API", "Database"],
    }

    response = client.post(
        f"/api/skill-bank/{test_user_id}/summaries", json=summary_data
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Technical Focus"
    assert data["focus"] == "technical"


def test_add_experience(client, test_user_id):
    """Test adding a work experience entry."""
    experience_data = {
        "company": "Tech Corp",
        "position": "Senior Developer",
        "location": "San Francisco, CA",
        "start_date": "2020-01-01",
        "end_date": "2023-12-31",
        "is_current": False,
        "experience_type": "full_time",
        "default_description": "Led development of web applications using Python and React.",
        "skills_used": ["Python", "React", "PostgreSQL"],
        "technologies": ["Django", "FastAPI", "Docker"],
    }

    response = client.post(
        f"/api/skill-bank/{test_user_id}/experience", json=experience_data
    )
    assert response.status_code == 201

    data = response.json()
    assert data["company"] == "Tech Corp"
    assert data["position"] == "Senior Developer"
    assert data["experience_type"] == "full_time"


def test_get_skill_categories(client, test_user_id):
    """Test getting skill categories."""
    # Ensure skill bank exists
    client.get(f"/api/skill-bank/{test_user_id}")

    response = client.get(f"/api/skill-bank/{test_user_id}/categories")
    assert response.status_code == 200

    categories = response.json()
    assert isinstance(categories, list)


def test_get_skill_bank_stats(client, test_user_id):
    """Test getting skill bank statistics."""
    # Ensure skill bank exists with some data
    client.get(f"/api/skill-bank/{test_user_id}")

    # Add a skill
    skill_data = {"name": "JavaScript", "category": "technical"}
    client.post(f"/api/skill-bank/{test_user_id}/skills", json=skill_data)

    response = client.get(f"/api/skill-bank/{test_user_id}/stats")
    assert response.status_code == 200

    stats = response.json()
    assert "total_skills" in stats
    assert "skills_by_category" in stats
    assert "total_summary_variations" in stats
    assert "total_work_experiences" in stats


def test_update_skill(client, test_user_id):
    """Test updating an existing skill."""
    # First add a skill
    skill_data = {"name": "TypeScript", "level": "beginner", "category": "technical"}
    response = client.post(f"/api/skill-bank/{test_user_id}/skills", json=skill_data)
    skill = response.json()
    skill_id = skill["id"]

    # Then update it
    update_data = {"level": "intermediate", "years_experience": 2}
    response = client.put(
        f"/api/skill-bank/{test_user_id}/skills/{skill_id}", json=update_data
    )
    assert response.status_code == 200

    updated_skill = response.json()
    assert updated_skill["level"] == "intermediate"
    assert updated_skill["years_experience"] == 2


def test_delete_skill(client, test_user_id):
    """Test deleting a skill."""
    # First add a skill
    skill_data = {"name": "Temporary Skill", "category": "technical"}
    response = client.post(f"/api/skill-bank/{test_user_id}/skills", json=skill_data)
    skill = response.json()
    skill_id = skill["id"]

    # Then delete it
    response = client.delete(f"/api/skill-bank/{test_user_id}/skills/{skill_id}")
    assert response.status_code == 204

    # Verify it's gone
    skills_response = client.get(f"/api/skill-bank/{test_user_id}/skills")
    skills = skills_response.json()
    assert not any(skill["id"] == skill_id for skill in skills)


if __name__ == "__main__":
    pytest.main([__file__])
