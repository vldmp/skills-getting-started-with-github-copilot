import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


def create_client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_data():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_data():
    client = create_client()

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    client = create_client()
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_duplicate_signup_returns_error():
    client = create_client()
    activity = "Chess Club"
    email = "michael@mergington.edu"

    first = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert first.status_code == 400

    # Ensure duplicate signups consistently return an error
    second = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert second.status_code == 400
    assert "already signed up" in second.json()["detail"]


def test_unregister_removes_participant():
    client = create_client()
    activity = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_missing_participant_returns_404():
    client = create_client()
    activity = "Chess Club"
    email = "absent@mergington.edu"

    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    assert response.status_code == 404
    assert "Student not registered" in response.json()["detail"]
