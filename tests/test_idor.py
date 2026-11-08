import uuid

import jwt

from app.core.config import get_settings

settings = get_settings()


def _make_project(client, bearer, token, name="Alpha"):
    resp = client.post("/api/v1/projects", json={"name": name}, headers=bearer(token))
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_owner_can_read_own_project(client, signup, bearer):
    a = signup("Tenant A", "a@example.com")
    pid = _make_project(client, bearer, a)
    resp = client.get(f"/api/v1/projects/{pid}", headers=bearer(a))
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alpha"


def test_cannot_read_other_tenants_project_by_id(client, signup, bearer):
    a = signup("Tenant A", "a@example.com")
    b = signup("Tenant B", "b@example.com")
    pid = _make_project(client, bearer, a)
    assert client.get(f"/api/v1/projects/{pid}", headers=bearer(b)).status_code == 404


def test_foreign_id_is_indistinguishable_from_missing_id(client, signup, bearer):
    """Attacker must not be able to tell 'exists in another tenant' from 'does not exist'."""
    a = signup("Tenant A", "a@example.com")
    b = signup("Tenant B", "b@example.com")
    real_id = _make_project(client, bearer, a)
    foreign = client.get(f"/api/v1/projects/{real_id}", headers=bearer(b))
    missing = client.get(f"/api/v1/projects/{uuid.uuid4()}", headers=bearer(b))
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()


def test_cannot_delete_other_tenants_project(client, signup, bearer):
    a = signup("Tenant A", "a@example.com")
    b = signup("Tenant B", "b@example.com")  # B is an admin in its own tenant
    pid = _make_project(client, bearer, a)
    assert client.delete(f"/api/v1/projects/{pid}", headers=bearer(b)).status_code == 404
    assert client.get(f"/api/v1/projects/{pid}", headers=bearer(a)).status_code == 200


def test_member_cannot_delete_own_tenants_project(client, signup, create_user, login, bearer):
    admin = signup("Acme", "admin@example.com")
    pid = _make_project(client, bearer, admin)
    create_user(admin, "member@example.com", "member")
    member = login("member@example.com").json()["access_token"]
    assert client.delete(f"/api/v1/projects/{pid}", headers=bearer(member)).status_code == 403


def test_admin_can_delete_own_project(client, signup, bearer):
    a = signup("Tenant A", "a@example.com")
    pid = _make_project(client, bearer, a)
    assert client.delete(f"/api/v1/projects/{pid}", headers=bearer(a)).status_code == 204
    assert client.get(f"/api/v1/projects/{pid}", headers=bearer(a)).status_code == 404


def test_tenant_id_in_request_body_is_ignored(client, signup, bearer):
    """Mass assignment: attacker tries to plant a project in another tenant."""
    a = signup("Tenant A", "a@example.com")
    b = signup("Tenant B", "b@example.com")
    b_tenant = jwt.decode(b, settings.secret_key, algorithms=["HS256"])["tenant_id"]

    resp = client.post(
        "/api/v1/projects",
        json={"name": "Planted", "tenant_id": b_tenant},
        headers=bearer(a),
    )
    assert resp.status_code == 201
    a_names = {p["name"] for p in client.get("/api/v1/projects", headers=bearer(a)).json()}
    b_names = {p["name"] for p in client.get("/api/v1/projects", headers=bearer(b)).json()}
    assert "Planted" in a_names
    assert "Planted" not in b_names


def test_malformed_project_id_rejected(client, signup, bearer):
    a = signup("Tenant A", "a@example.com")
    assert client.get("/api/v1/projects/not-a-uuid", headers=bearer(a)).status_code == 422