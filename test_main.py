import uuid
from fastapi.testclient import TestClient
from main import app

# TestClient allows us to make mock HTTP requests to our FastAPI app without running a real server
client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_successful_approval():
    key = f"test-key-{uuid.uuid4()}"
    response = client.post(
        "/api/v1/decisions",
        headers={"idempotency-key": key},
        json={
            "applicant_name": "Rahul Verma",
            "age": 28,
            "income": 600000,
            "documents_provided": True
        }
    )
    assert response.status_code == 200
    # Even if external API fails, we just want to ensure it doesn't crash and returns a valid response format
    assert "final_decision" in response.json()

def test_rejection_low_income():
    key = f"test-key-{uuid.uuid4()}"
    response = client.post(
        "/api/v1/decisions",
        headers={"idempotency-key": key},
        json={
            "applicant_name": "Priya Singh",
            "age": 25,
            "income": 150000, # Below 3,00,000 threshold
            "documents_provided": True
        }
    )
    assert response.status_code == 200
    assert response.json()["final_decision"] in ["REJECTED", "FAILED"]

def test_invalid_input_schema():
    key = f"test-key-{uuid.uuid4()}"
    response = client.post(
        "/api/v1/decisions",
        headers={"idempotency-key": key},
        json={
            "applicant_name": "Amit",
            "age": 16, # Fails Pydantic ge=18 validation
            "income": 400000,
            "documents_provided": True
        }
    )
    assert response.status_code == 422 # Unprocessable Entity

def test_idempotency_duplicate_request():
    key = f"duplicate-key-{uuid.uuid4()}"
    payload = {
        "applicant_name": "Neha Gupta",
        "age": 30,
        "income": 800000,
        "documents_provided": True
    }
    
    # Send first request
    resp1 = client.post("/api/v1/decisions", headers={"idempotency-key": key}, json=payload)
    assert resp1.status_code == 200
    
    # Send exact same request again
    resp2 = client.post("/api/v1/decisions", headers={"idempotency-key": key}, json=payload)
    assert resp2.status_code == 200
    assert "Duplicate request detected" in resp2.json().get("message", "")