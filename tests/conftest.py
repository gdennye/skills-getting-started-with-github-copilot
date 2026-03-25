import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provides a TestClient for making HTTP requests to the app."""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provides test activity data."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["alice@mergington.edu", "bob@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["charlie@mergington.edu"]
        }
    }


@pytest.fixture
def reset_activities(sample_activities):
    """
    Resets the activities database to sample data before each test.
    This ensures test isolation.
    """
    # Arrange: Clear existing activities
    activities.clear()
    
    # Arrange: Populate with sample data
    activities.update(sample_activities)
    
    yield activities
    
    # Cleanup: Reset after test
    activities.clear()
