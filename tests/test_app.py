import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirects_to_static_index():
    response = client.get("/")
    assert response.status_code == 200
    assert str(response.url).endswith("/static/index.html")
    assert "Mergington High School" in response.text


def test_get_activities_returns_activity_list():
    response = client.get("/activities")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    email = "teststudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate_returns_400():
    existing = activities["Chess Club"]["participants"][0]
    response = client.post("/activities/Chess Club/signup", params={"email": existing})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_success():
    email = activities["Chess Club"]["participants"][0]
    response = client.delete("/activities/Chess Club/participants", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_remove_participant_not_found_returns_404():
    response = client.delete("/activities/Chess Club/participants", params={"email": "missing@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Nonexistent/signup", params={"email": "someone@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_unknown_activity_returns_404():
    response = client.delete("/activities/Nonexistent/participants", params={"email": "someone@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
