from test.utils import *
from fastapi import status
from models import requests, ai_model

def test_get_all_requests(test_request):
    response = client.get("/request/all")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"requestID": 1, "userID": 1, "model_name": "GPT4.0", "input_text": "Input", "output_text": "Output"}]

def test_get_all_not_found():
    response = client.get("/request/all")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "There is no request."}

def test_get_request(test_request):
    response = client.get("/request/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Model": "GPT4.0", "Input": "Input", "Output": "Output"}

def test_get_not_found():
    response = client.get("/request/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Request does not exist."}

def test_get_wrong_id(test_request2):
    response = client.get("/request/1")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You do not have access to this request."}

def test_delete_request(test_request):
    response = client.delete("/request/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(requests).filter(requests.requestID == 1).first()

    assert model is None

def test_delete_not_found():
    response = client.delete("/request/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Request does not exist."}

def test_delete_wrong_id(test_request2):
    response = client.delete("/request/1")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You do not have access to this request."}

def test_create_request(test_request):
    req_data = {
        "modelID": 1,
        "input_text": "Input"
    }

    response = client.post("/request/create", json=req_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["userID"] is not None
    assert response.json()["modelID"] == 1

def test_create_no_model():
    req_data = {
        "modelID": 1,
        "input_text": "Input"
    }

    response = client.post("/request/create", json=req_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    db = TestingSessionLocal()
    model = db.query(ai_model).filter(ai_model.modelID == 1).first()

    assert model is None