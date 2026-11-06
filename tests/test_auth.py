import datetime as dt

import jwt
import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings

settings = get_settings()
PASSWORD = "TestPass123!"


def _claims(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def test_login_returns_working_token(client, signup, login, bearer):
    signup("Acme", "admin@example.com")
    resp = login("admin@example.com")
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert client.get("/api/v1/projects", headers=bearer(token)).status_code == 200


def test_duplicate_signup_rejected(client, signup):
    signup("Acme", "dup@example.com")
    resp = client.post(
        "/api/v1/auth/signup",
        json={"tenant_name": "Other", "email": "dup@example.com", "password": PASSWORD},
    )
    assert resp.status_code == 400


def test_login_wrong_password_rejected(signup, login):
    signup("Acme", "admin@example.com")
    assert login("admin@example.com", "WrongPass999!").status_code == 401


def test_login_error_does_not_reveal_whether_email_exists(signup, login):
    signup("Acme", "real@example.com")
    wrong_password = login("real@example.com", "WrongPass999!")
    unknown_email = login("ghost@example.com", "WrongPass999!")
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_missing_token_rejected(client):
    assert client.get("/api/v1/projects").status_code in (401, 403)


def test_garbage_token_rejected(client, bearer):
    assert client.get("/api/v1/projects", headers=bearer("not.a.jwt")).status_code == 401


def test_expired_token_rejected(client, signup, bearer):
    claims = _claims(signup("Acme", "admin@example.com"))
    claims["exp"] = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
    expired = jwt.encode(claims, settings.secret_key, algorithm="HS256")
    assert client.get("/api/v1/projects", headers=bearer(expired)).status_code == 401


def test_token_signed_with_wrong_key_rejected(client, signup, bearer):
    claims = _claims(signup("Acme", "admin@example.com"))
    claims["role"] = "admin"  # attacker tries to claim a role
    forged = jwt.encode(claims, "x" * 40, algorithm="HS256")
    assert client.get("/api/v1/projects", headers=bearer(forged)).status_code == 401


def test_alg_none_token_rejected(client, signup, bearer):
    claims = _claims(signup("Acme", "admin@example.com"))
    forged = jwt.encode(claims, key=None, algorithm="none")
    assert client.get("/api/v1/projects", headers=bearer(forged)).status_code == 401


def test_weak_secret_key_is_rejected():
    with pytest.raises(ValidationError):
        Settings(secret_key="short")