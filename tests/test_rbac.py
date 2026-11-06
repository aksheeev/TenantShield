import pytest


def test_admin_can_create_member_and_viewer(signup, create_user):
    admin = signup("Acme", "admin@example.com")
    assert create_user(admin, "member@example.com", "member").status_code == 201
    resp = create_user(admin, "viewer@example.com", "viewer")
    assert resp.status_code == 201
    assert resp.json()["role"] == "viewer"


def test_member_can_create_and_list_projects(client, signup, create_user, login, bearer):
    admin = signup("Acme", "admin@example.com")
    create_user(admin, "member@example.com", "member")
    member = login("member@example.com").json()["access_token"]

    resp = client.post("/api/v1/projects", json={"name": "P1"}, headers=bearer(member))
    assert resp.status_code == 201
    assert client.get("/api/v1/projects", headers=bearer(member)).status_code == 200


def test_viewer_can_read_but_not_create_projects(client, signup, create_user, login, bearer):
    admin = signup("Acme", "admin@example.com")
    client.post("/api/v1/projects", json={"name": "Shared"}, headers=bearer(admin))
    create_user(admin, "viewer@example.com", "viewer")
    viewer = login("viewer@example.com").json()["access_token"]

    listed = client.get("/api/v1/projects", headers=bearer(viewer))
    assert listed.status_code == 200
    assert "Shared" in {p["name"] for p in listed.json()}

    denied = client.post("/api/v1/projects", json={"name": "Nope"}, headers=bearer(viewer))
    assert denied.status_code == 403


@pytest.mark.parametrize("role", ["member", "viewer"])
def test_non_admin_cannot_create_users(role, signup, create_user, login):
    admin = signup("Acme", "admin@example.com")
    create_user(admin, "low@example.com", role)
    low = login("low@example.com").json()["access_token"]
    assert create_user(low, "another@example.com", "member").status_code == 403


@pytest.mark.parametrize("role", ["member", "viewer"])
def test_non_admin_cannot_list_users(role, client, signup, create_user, login, bearer):
    admin = signup("Acme", "admin@example.com")
    create_user(admin, "low@example.com", role)
    low = login("low@example.com").json()["access_token"]
    assert client.get("/api/v1/users", headers=bearer(low)).status_code == 403


def test_admin_sees_only_own_tenants_users(client, signup, create_user, bearer):
    a = signup("Tenant A", "admin-a@example.com")
    signup("Tenant B", "admin-b@example.com")
    create_user(a, "member-a@example.com", "member")

    resp = client.get("/api/v1/users", headers=bearer(a))
    assert resp.status_code == 200
    assert {u["email"] for u in resp.json()} == {"admin-a@example.com", "member-a@example.com"}


def test_invalid_role_rejected(signup, create_user):
    admin = signup("Acme", "admin@example.com")
    assert create_user(admin, "x@example.com", "superadmin").status_code == 422


def test_cannot_create_user_with_email_used_in_another_tenant(signup, create_user):
    a = signup("Tenant A", "admin-a@example.com")
    signup("Tenant B", "admin-b@example.com")
    assert create_user(a, "admin-b@example.com", "member").status_code == 400