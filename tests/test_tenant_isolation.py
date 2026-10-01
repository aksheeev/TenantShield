from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _signup(tenant_name: str, email: str) -> str:
    resp = client.post(
        "/api/v1/auth/signup",
        json={"tenant_name": tenant_name, "email": email, "password": "TestPass123!"},
    )
    assert resp.status_code == 201
    return resp.json()["access_token"]


def test_tenant_cannot_see_other_tenants_projects():
    token_a = _signup("Tenant A", "a@example.com")
    token_b = _signup("Tenant B", "b@example.com")

    client.post(
        "/api/v1/projects",
        json={"name": "Alpha Secret Project"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    response = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert "Alpha Secret Project" not in names