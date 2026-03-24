import pytest
from fastapi.testclient import TestClient
from urllib.parse import quote
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index page"""
    # Arrange - no special setup needed
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test retrieving all activities"""
    # Arrange - no special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    
    # Verify activity structure
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success():
    """Test successful student signup"""
    # Arrange
    email = "test@example.com"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    
    # Verify participant was added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity]["participants"]


def test_signup_duplicate():
    """Test preventing duplicate signup"""
    # Arrange
    email = "dup@example.com"
    activity = "Programming Class"
    
    # First signup
    client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    
    # Act - attempt duplicate signup
    response = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_activity_not_found():
    """Test signup for nonexistent activity"""
    # Arrange
    email = "test@example.com"
    activity = "Nonexistent"
    
    # Act
    response = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_success():
    """Test successful student unregister"""
    # Arrange
    email = "unreg@example.com"
    activity = "Gym Class"
    
    # First signup
    client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    
    # Act
    response = client.delete(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    
    # Verify participant was removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity]["participants"]


def test_unregister_not_signed_up():
    """Test unregister for student not signed up"""
    # Arrange
    email = "notsigned@example.com"
    activity = "Science Club"
    
    # Act
    response = client.delete(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]


def test_unregister_activity_not_found():
    """Test unregister for nonexistent activity"""
    # Arrange
    email = "test@example.com"
    activity = "Nonexistent"
    
    # Act
    response = client.delete(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]