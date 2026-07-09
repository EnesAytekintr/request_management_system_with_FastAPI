from test.utils import *
from fastapi import status
from models import ai_model
from routers.auth import get_current_user

def test_get_models(test_ai_model):
    response = client.get("/model/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"model_name": "GPT4.0", "modelID": 1}]

def test_not_user():
    app.dependency_overrides[get_current_user] = lambda: None

    try:
        response = client.get("/model/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Authentication failed."}

    finally:
        app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_not_found():
    response = client.get("/model/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "There is no ai model."}


def test_get_model_by_id(test_ai_model):
    response = client.get("/model/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"model_name": "GPT4.0", "modelID": 1}

def test_get_model_not_user():
    app.dependency_overrides[get_current_user] = lambda: None

    try:
        response = client.get("/model/1")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Authentication failed."}
    finally:
        app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_by_id_not_found():
    response = client.get("/model/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Model not found"}

def test_create_model(test_ai_model):
    req_data = {"model_name": "Gemini"}

    response = client.post("/model/create", json=req_data)

    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(ai_model).filter(ai_model.model_name == "Gemini").first()

    assert model is not None

def test_create_not_user():
    req_data = {"model_name": "Gemini"}
    app.dependency_overrides[get_current_user] = lambda: None

    try:
        response = client.post("/model/create", json=req_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Authentication failed."}
    finally:
        app.dependency_overrides[get_current_user] = override_get_current_user

def test_create_not_admin():
    req_data = {"model_name": "Gemini"}
    app.dependency_overrides[get_current_user] = lambda : {"userID": 1, "user_name": "Mike", "is_admin": False}

    try:
        response = client.post("/model/create", json=req_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Admin privileges required."}
    finally:
        app.dependency_overrides[get_current_user] = override_get_current_user