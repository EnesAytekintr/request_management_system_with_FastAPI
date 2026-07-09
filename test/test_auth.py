from test.utils import *
from fastapi import status

def test_create_user_success():
    user_data = {
        "user_name": "enes123",
        "first_name": "Enes",
        "last_name": "Yılmaz",
        "password": "supersecurepassword123"
    }

    response = client.post("/auth/", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED

def test_create_user_already_exists(test_user):
    user_data = {
        "user_name": "Test User",
        "first_name": "John",
        "last_name": "Doe",
        "password": "password123"
    }

    response = client.post("/auth/", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "This user name already exists."}


def test_login_for_access_token_success(test_user):
    login_data = {
        "username": "Test User",
        "password": "test1234"
    }

    response = client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


def test_login_for_access_token_wrong_password(test_user):
    login_data = {
        "username": "Test User",
        "password": "wrongpassword"
    }

    response = client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate user."}

def test_create_user_invalid_password_length():
    user_data = {
        "user_name": "enes123",
        "first_name": "Enes",
        "last_name": "Yılmaz",
        "password": "123"
    }

    response = client.post("/auth/", json=user_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_for_access_token_user_not_found():
    login_data = {
        "username": "GhostUser",
        "password": "test1234"
    }

    response = client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate user."}


def test_login_inactive_user(setup_and_teardown_db):
    db = TestingSessionLocal()

    inactive_user = users(
        userID=99,
        user_name="PasifUser",
        first_name="Mehmet",
        last_name="Can",
        hashed_password=bcrypt_context.hash("test1234"),
        is_active=False
    )
    db.add(inactive_user)
    db.commit()

    login_data = {
        "username": "PasifUser",
        "password": "test1234"
    }

    response = client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate user."}