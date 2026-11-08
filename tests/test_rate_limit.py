import redis

from app.core import rate_limit
from app.core.config import get_settings

settings = get_settings()


def test_login_is_rate_limited(signup, login):
    signup("Acme", "admin@example.com")
    for _ in range(settings.login_rate_limit_attempts):
        assert login("admin@example.com", "WrongPass999!").status_code == 401
    blocked = login("admin@example.com", "WrongPass999!")
    assert blocked.status_code == 429
    assert "retry-after" in blocked.headers


def test_correct_password_is_also_blocked_after_limit(signup, login):
    """Otherwise an attacker could keep guessing and just ignore the 429s."""
    signup("Acme", "admin@example.com")
    for _ in range(settings.login_rate_limit_attempts):
        login("admin@example.com", "WrongPass999!")
    assert login("admin@example.com").status_code == 429


def test_login_still_works_if_redis_is_down(monkeypatch, signup, login):
    def boom(*args, **kwargs):
        raise redis.ConnectionError("down")

    monkeypatch.setattr(rate_limit.redis_client, "pipeline", boom)
    signup("Acme", "admin@example.com")
    assert login("admin@example.com").status_code == 200