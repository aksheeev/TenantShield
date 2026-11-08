import logging

import redis
from fastapi import HTTPException, Request, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)


def clear_rate_limits() -> None:
    """Used by tests so one test's attempts never count against another."""
    for key in redis_client.scan_iter("rl:*"):
        redis_client.delete(key)


def rate_limit(name: str, max_attempts: int, window_seconds: int):
    """Fixed-window limiter per client IP. Needs Redis 7 (EXPIRE ... NX)."""

    def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rl:{name}:{client_ip}"
        try:
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds, nx=True)
            pipe.ttl(key)
            count, _, ttl = pipe.execute()
        except redis.RedisError:
            # Fail-open: a Redis outage must not lock every user out of login.
            logger.warning("Rate limiter unavailable, allowing request")
            return
        if count > max_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Try again later.",
                headers={"Retry-After": str(max(ttl, 1))},
            )

    return dependency