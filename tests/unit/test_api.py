import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_drivers_endpoint():
    """Test drivers listing endpoint."""
    response = client.get("/drivers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If drivers exist
        assert "id" in data[0]
        assert "name" in data[0]
        assert "risk_score" in data[0]

def test_driver_detail_endpoint():
    """Test individual driver endpoint."""
    response = client.get("/drivers/D001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "D001"
    assert "name" in data
    assert "risk_score" in data

def test_incidents_endpoint():
    """Test incidents listing endpoint."""
    response = client.get("/incidents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_alerts_endpoint():
    """Test alerts listing endpoint."""
    response = client.get("/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_ai_query_endpoint():
    """Test AI query endpoint."""
    response = client.post("/ai/query", json={"question": "test question"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data

def test_ai_query_empty_question():
    """Test AI query with empty question."""
    response = client.post("/ai/query", json={"question": ""})
    assert response.status_code == 400

def test_ai_status_endpoint():
    """Test AI status endpoint."""
    response = client.get("/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "rag_available" in data
    assert "model_status" in data