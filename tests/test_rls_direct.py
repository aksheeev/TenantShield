import jwt
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import AppSessionLocal

settings = get_settings()


def _tenant_id(token: str) -> str:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])["tenant_id"]


def _visible_rows(project_id: str, tenant_id: str | None = None) -> int:
    """Raw SQL as the restricted app role, with NO tenant filter in the query itself."""
    db = AppSessionLocal()
    try:
        if tenant_id:
            db.execute(text(f"SET LOCAL app.current_tenant = '{tenant_id}'"))
        return db.execute(
            text("SELECT count(*) FROM projects WHERE id = :id"), {"id": project_id}
        ).scalar_one()
    finally:
        db.close()


def test_rls_alone_hides_rows_from_other_tenants(client, signup, bearer):
    a = signup("Tenant A", "a@example.com")
    b = signup("Tenant B", "b@example.com")
    pid = client.post("/api/v1/projects", json={"name": "Alpha"}, headers=bearer(a)).json()["id"]

    assert _visible_rows(pid, _tenant_id(a)) == 1  # owner tenant sees it
    assert _visible_rows(pid, _tenant_id(b)) == 0  # other tenant does not
    assert _visible_rows(pid) == 0                 # no tenant context: fails closed