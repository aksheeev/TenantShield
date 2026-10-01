import pytest
from sqlalchemy import text

from app.db.session import SessionLocal


@pytest.fixture(autouse=True)
def clean_database():
    """Runs before every test — wipes tenant data so each test starts fresh."""
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE users, projects, tenants CASCADE"))
        db.commit()
    finally:
        db.close()
    yield