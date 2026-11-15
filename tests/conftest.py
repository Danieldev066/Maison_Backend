import os

os.environ["SECRET_KEY"] = "test-secret-only-for-pytest-1234567890-more-characters"
os.environ["DATABASE_URL"] = "sqlite:///./test-not-used.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import DiningTable, MenuCategory, MenuItem, RestaurantInfo, User


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    local_session = sessionmaker(bind=engine, expire_on_commit=False)
    with local_session() as session:
        session.add_all([
            RestaurantInfo(name="MAISON", description="Demo", address="Test", phone="", opening_hours="Test"),
            DiningTable(number="A1", seats=2),
            DiningTable(number="B1", seats=4),
            MenuCategory(id=1, name="Main", position=1),
            MenuItem(id=1, category_id=1, name="Pasta", price_som=400, description="Pasta"),
            MenuItem(id=2, category_id=1, name="Soup", price_som=200, description="Soup"),
            User(email="admin@example.com", full_name="Admin", password_hash=hash_password("supersecurepassword"), role="admin"),
        ])
        session.commit()

    yield local_session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(db):
    def override_db():
        with db() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def user_auth(client, email="user@example.com"):
    response = client.post("/api/v1/auth/register", json={
        "email": email, "password": "strong-password-123", "full_name": "Test User"
    })
    assert response.status_code == 201, response.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "strong-password-123"})
    assert login.status_code == 200
    return {"Authorization": "Bearer " + login.json()["access_token"]}


def admin_auth(client):
    response = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "supersecurepassword"})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}
