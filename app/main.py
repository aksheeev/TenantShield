from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Secure multi-tenant SaaS backend: tenant isolation with PostgreSQL "
        "row-level security, JWT auth, RBAC, and a tamper-evident audit log."
    ),
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Liveness check used by Docker, CI, and the hosting platform."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }