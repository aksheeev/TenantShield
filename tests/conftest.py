import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import SessionLocal
from app.main import app

PASSWORD = "TestPass123!"


@pytest.fixture(autouse=True)
def clean_database():
    """Wipes tenant data before every test."""
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE users, projects, tenants CASCADE"))
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def bearer():
    return lambda token: {"Authorization": f"Bearer {token}"}


@pytest.fixture
def signup(client):
    def _signup(tenant_name, email, password=PASSWORD):
        resp = client.post(
            "/api/v1/auth/signup",
            json={"tenant_name": tenant_name, "email": email, "password": password},
        )
        assert resp.status_code == 201, resp.text
        return resp.json()["access_token"]

    return _signup


@pytest.fixture
def login(client):
    def _login(email, password=PASSWORD):
        return client.post("/api/v1/auth/login", json={"email": email, "password": password})

    return _login


@pytest.fixture
def create_user(client, bearer):
    def _create_user(token, email, role="member", password=PASSWORD):
        return client.post(
            "/api/v1/users",
            json={"email": email, "password": password, "role": role},
            headers=bearer(token),
        )

    return _create_user