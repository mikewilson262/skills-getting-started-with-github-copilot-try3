import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activity_data(monkeypatch):
    data = {
        "Chess Club": {
            "description": "Learn strategies and compete",
            "schedule": "Fridays, 3:30 PM",
            "max_participants": 12,
            "participants": ["alice@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", data)
    return data


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client, activity_data):
    # Arrange
    expected = activity_data

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_adds_participant(client, activity_data):
    # Arrange
    email = "bob@example.com"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up bob@example.com for Chess Club"}
    assert activity_data["Chess Club"]["participants"] == [
        "alice@example.com",
        email,
    ]


def test_signup_returns_not_found_for_unknown_activity(client, activity_data):
    # Arrange
    email = "bob@example.com"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client, activity_data):
    # Arrange
    email = "alice@example.com"
    original_participants = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activity_data["Chess Club"]["participants"] == original_participants


def test_remove_participant_removes_signup(client, activity_data):
    # Arrange
    email = "alice@example.com"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Removed alice@example.com from Chess Club"}
    assert activity_data["Chess Club"]["participants"] == []


def test_remove_participant_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "alice@example.com"

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_not_found_when_not_registered(
    client, activity_data
):
    # Arrange
    email = "bob@example.com"
    original_participants = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activity_data["Chess Club"]["participants"] == original_participants