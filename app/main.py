from fastapi import FastAPI

from app.api.v1 import auth, projects
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

app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }