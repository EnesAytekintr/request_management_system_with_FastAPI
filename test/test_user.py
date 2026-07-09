from test.utils import *
from fastapi import status
from models import users

def test_user_get_profile(test_user):
    response =client.get("/users/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"userID": 1, "user_name":"Test User", "first_name":"Mike", "last_name":"Tylor", "is_active": True, "subscription": False}

def test_user_wrong_id(test_user):
    response = client.get("/users/3")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You can only view your own profile."}

def test_user_not_found():
    response = client.get("/users/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}

def test_update_user(test_user):
    req_data = {"user_name":"Test User", "first_name":"Sam", "last_name":"Tylor", "current_password":"test1234",
                "new_password": "holymoly"}

    response = client.put("/users/1", json=req_data)

    db = TestingSessionLocal()
    model = db.query(users).filter(users.userID == 1).first()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model.first_name == "Sam"

def test_update_wrong_password(test_user):
    req_data = {"user_name": "Test User", "first_name": "Mike", "last_name": "Tylor", "current_password": "wrongpassword",
                "new_password": "holymoly"}

    response = client.put("/users/1", json=req_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Current password is invalid."}


def test_update_wrong_id(test_user):
    req_data = {"user_name": "Test User", "first_name": "Mike", "last_name": "Tylor",
                "current_password": "test1234",
                "new_password": "holymoly"}

    response = client.put("/users/2", json=req_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You can only update your profile."}

def test_update_not_found():
    req_data = {"user_name": "Test User", "first_name": "Mike", "last_name": "Tylor",
                "current_password": "test1234",
                "new_password": "holymoly"}

    response = client.put("/users/1", json=req_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}

def test_subscribe_user(test_user):
    req_data = {"subscription": True}

    response = client.put("/users/1/subscribe", json=req_data)

    db = TestingSessionLocal()
    model = db.query(users).filter(users.userID == 1).first()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model.subscription is True
    db.close()


def test_subscribe_not_found():
    req_data = {"subscription": True}

    response = client.put("/users/1/subscribe", json=req_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}

def test_subscribe_wrong_id(test_user):
    req_data = {"subscription": True}

    response = client.put("/users/2/subscribe", json=req_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You can only update your own subscription."}


