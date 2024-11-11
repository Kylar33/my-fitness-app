import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import Session
from config.database import get_db, Base, engine, SessionLocal

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_register_trainer(client, db):
    trainer_data = {
        "email": "trainer@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe"
    }

    response = client.post("/api/v1/register/trainer", json=trainer_data)
    assert response.status_code == 200
    assert response.json()["email"] == trainer_data["email"]
    assert "id" in response.json()

def test_register_user(client, db):
    user_data = {
        "email": "user@example.com",
        "password": "password456",
        "first_name": "Jane",
        "last_name": "Doe",
        "trainer_id": 1
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    assert "id" in response.json()