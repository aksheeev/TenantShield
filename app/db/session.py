import uuid
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Owner-role engine. Used ONLY for signup (creating a tenant row — not yet
# scoped to anyone) and login (looking up a user by email across all
# tenants, since we don't know the tenant until we find them). This role
# bypasses RLS, which is fine here because neither operation reads across
# tenants in a way that leaks data.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# App-role engine. Used for every tenant-scoped operation (projects, etc).
# tenantshield_app is NOT the table owner and NOT a superuser, so Postgres
# actually enforces the RLS policies for it.
app_engine = create_engine(settings.database_app_url, pool_pre_ping=True)
AppSessionLocal = sessionmaker(bind=app_engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_tenant_db(tenant_id: str) -> Generator[Session, None, None]:
    """
    DB session scoped to one tenant, using the restricted app role so RLS
    is actually enforced (see module docstring above for why two roles).

    SET LOCAL doesn't support bind parameters, so we validate tenant_id is
    a genuine UUID first (raises if not), then use its canonical str()
    form — which can only contain [0-9a-f-] — directly in the SQL string.
    """
    validated = str(uuid.UUID(str(tenant_id)))

    db = AppSessionLocal()
    try:
        db.execute(text(f"SET LOCAL app.current_tenant = '{validated}'"))
        yield db
    finally:
        db.close()