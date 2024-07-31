import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app,get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_contact(db):
    response = client.post("/contacts/",
                           json={"name": "John Doe", "email": "john.doe@example.com", "phone": "1234567890"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["phone"] == "1234567890"


def test_read_contact(db):
    response = client.post("/contacts/",
                           json={"name": "John Doe", "email": "john.doe@example.com", "phone": "1234567890"})
    assert response.status_code == 200
    contact_id = response.json()["id"]

    response = client.get(f"/contacts/{contact_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["phone"] == "1234567890"


def test_update_contact(db):
    # Create a contact first
    response = client.post("/contacts/",
                           json={"name": "John Doe", "email": "john.doe@example.com", "phone": "1234567890"})
    assert response.status_code == 200
    contact_id = response.json()["id"]

    # Update the contact
    response = client.put(f"/contacts/{contact_id}",
                          json={"name": "John Smith", "email": "john.smith@example.com", "phone": "0987654321"})

    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["email"] == "john.smith@example.com"
    assert data["phone"] == "0987654321"


def test_delete_contact(db):
    response = client.post("/contacts/",
                           json={"name": "John Doe", "email": "john.doe@example.com", "phone": "1234567890"})
    assert response.status_code == 200
    contact_id = response.json()["id"]

    response = client.delete(f"/contacts/{contact_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["phone"] == "1234567890"

    response = client.get(f"/contacts/{contact_id}")
    assert response.status_code == 404
