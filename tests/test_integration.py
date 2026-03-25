import pytest


class TestGetRoot:
    """Tests for GET / endpoint"""
    
    def test_root_redirect_returns_correct_status(self, client):
        # Arrange
        expected_status = 307
        expected_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status
        assert response.headers.get("location") == expected_url


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        # Arrange
        expected_count = 2
        expected_activity_names = {"Chess Club", "Programming Class"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_count
        assert set(data.keys()) == expected_activity_names
    
    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in data.items():
            assert required_fields.issubset(set(activity_data.keys()))
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_shows_correct_participant_count(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        expected_participant_count = 2
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data[activity_name]["participants"]) == expected_participant_count


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}",
            follow_redirects=True
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_email in reset_activities[activity_name]["participants"]
    
    def test_signup_activity_not_found_returns_404(self, client, reset_activities):
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_student_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        existing_email = "alice@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_activity_at_capacity_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        new_email = "overcapacity@mergington.edu"
        # Chess Club has max 2 participants and is already full
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower() or "capacity" in response.json()["detail"].lower()
    
    def test_signup_updates_participant_list(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        new_email = "another@mergington.edu"
        initial_count = len(reset_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        updated_count = len(reset_activities[activity_name]["participants"])
        
        # Assert
        assert response.status_code == 200
        assert updated_count == initial_count + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student_success(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "alice@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email_to_remove not in reset_activities[activity_name]["participants"]
    
    def test_unregister_activity_not_found_returns_404(self, client, reset_activities):
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        unregistered_email = "notmember@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={unregistered_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_updates_participant_list(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "alice@mergington.edu"
        initial_count = len(reset_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        updated_count = len(reset_activities[activity_name]["participants"])
        
        # Assert
        assert response.status_code == 200
        assert updated_count == initial_count - 1
