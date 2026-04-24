from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_hello():
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "API Works!"}

def test_grade_A():
    res = client.get("/api/grade?score=0")
    assert res.status_code == 200
    assert res.json()["grade"] == "F"

def test_grade_boundary_85():
    res = client.get("/api/grade?score=85")
    assert res.status_code == 200
    assert res.json()["grade"] == "A"

def test_grade_boundary_85():
    res = client.get("/api/grade?score=75")
    assert res.status_code == 200
    assert res.json()["grade"] == "B"