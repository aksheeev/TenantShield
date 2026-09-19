# TenantShield

![CI](https://github.com/YOUR_USERNAME/TenantShield/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A secure multi-tenant SaaS backend where many organizations share one system but can never see each other's data. Built for the *Information and Cyber Security* course, with a focus on real engineering practice: tests, CI, containers, and a documented threat model.

> **Status: in progress.** The roadmap below shows exactly what is built and what is planned.

## Goals

- **Tenant isolation** enforced at the database level with PostgreSQL row-level security (RLS), not just in application code
- **Authentication and authorization** with JWT, argon2 password hashing, and role-based access control
- **Tamper-evident audit log** using a hash chain, with an insert-only database role
- **Abuse protection** with Redis-backed rate limiting
- **Secure engineering pipeline** with automated tests plus Bandit, pip-audit, and Trivy scans in CI
- **Documented security thinking** through a threat model and an OWASP Top 10 mapping

## Tech stack

| Area | Technology | Status |
|---|---|---|
| API | FastAPI, Python 3.12 | In use |
| Containers | Docker, docker-compose | In use |
| CI | GitHub Actions, ruff, pytest | In use |
| Database | PostgreSQL, SQLAlchemy, Alembic | Planned |
| Auth | JWT, argon2 | Planned |
| Rate limiting | Redis | Planned |
| Security scanning | Bandit, pip-audit, Trivy | Planned |
| Hosting | Render, Neon, Upstash (free tiers) | Planned |

## Roadmap

- [x] Project skeleton and documentation stubs
- [x] FastAPI app with `/health` endpoint and first test
- [x] Docker and docker-compose (app, PostgreSQL, Redis)
- [x] CI pipeline (lint and tests)
- [ ] Database models and Alembic migrations
- [ ] Tenant and user models, JWT auth with argon2
- [ ] Role-based access control (admin, member, viewer)
- [ ] PostgreSQL row-level security and cross-tenant isolation tests
- [ ] Hash-chained audit log
- [ ] Redis rate limiting
- [ ] Bandit, pip-audit, and Trivy in CI
- [ ] Deployment (Render, Neon, Upstash)
- [ ] Threat model and OWASP Top 10 mapping
- [ ] Optional: PII redaction endpoint for LLM inputs

## Quick start

### With Docker

```bash
git clone https://github.com/YOUR_USERNAME/TenantShield.git
cd TenantShield
cp .env.example .env
docker compose up --build
```

Then open http://localhost:8000/docs for the interactive API docs and http://localhost:8000/health for the health check.

### Without Docker

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

### Run tests and lint

```bash
pytest
ruff check .
```

## Project structure

```
app/
  api/v1/        route handlers (auth, tenants, users, projects, audit)
  core/          config, security helpers, rate limiting
  db/            database session and base
  models/        SQLAlchemy models
  schemas/       Pydantic schemas
  services/      business logic (e.g. audit log)
tests/           pytest suite, including tenant-isolation tests
docs/            architecture, threat model, OWASP mapping
```

## Documentation

- [Architecture](docs/architecture.md)
- [Threat model](docs/threat-model.md)
- [OWASP Top 10 mapping](docs/owasp-mapping.md)

## Security

See [SECURITY.md](SECURITY.md). This is a learning project and is not production-ready.

## License

MIT. See [LICENSE](LICENSE).