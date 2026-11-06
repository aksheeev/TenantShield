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
| CI | GitHub Actions (Postgres service, migrations, ruff, pytest) | In use |
| Database | PostgreSQL 16, SQLAlchemy, Alembic | In use |
| Auth | JWT (PyJWT), argon2 | In use |
| Access control | RBAC (admin, member, viewer), PostgreSQL RLS | In use |
| Rate limiting | Redis | Planned |
| Security testing | Burp Suite, OWASP ZAP, Nmap | Planned |
| Security scanning | Bandit, pip-audit, Trivy | Planned |
| Hosting | Render, Neon, Upstash (free tiers) | Planned |

## Roadmap


### Core build
- [x] Project skeleton and documentation stubs
- [x] FastAPI app with `/health` endpoint and first test
- [x] Docker and docker-compose (app, PostgreSQL, Redis)
- [x] CI pipeline (Postgres service, migrations, lint, tests)
- [x] Database models and Alembic migrations
- [x] Tenant and user models, JWT auth with argon2
- [x] Role-based access control (admin, member, viewer)
- [x] PostgreSQL row-level security and cross-tenant isolation tests
- [x] User management endpoint (admin-only, tenant-scoped)
- [x] Auth and RBAC negative tests (tampered, expired and `alg: none` JWTs, role checks)
- [ ] Hash-chained audit log
- [ ] Redis rate limiting
- [ ] Deployment (Render, Neon, Upstash)
- [ ] Threat model and OWASP Top 10 mapping
- [ ] Optional: PII redaction endpoint for LLM inputs

### Security testing (VAPT) of this project
Testing is done against my own local docker-compose instance only.
- [ ] IDOR test: `GET /projects/{id}` across tenants, with an automated regression test
- [ ] Intercept and replay API traffic with Burp Suite (Proxy, Repeater)
- [ ] Brute-force the login endpoint with Burp Intruder, then fix with Redis rate limiting and re-test
- [ ] Automated scan of the API with OWASP ZAP
- [ ] JWT attack testing: tampering, `alg: none`, expiry, key confusion
- [ ] Port and service scan of the docker-compose stack with Nmap
- [ ] Static analysis with Bandit and dependency audit with pip-audit
- [ ] Container image scan with Trivy
- [ ] Add Bandit, pip-audit and Trivy to CI
- [ ] Write up each finding with severity, evidence, impact and remediation (see below)

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

## Security findings

Findings in my own project, tracked with severity and status. The severity ratings are my own assessment. "Found by" shows how each one was identified, and I will update it as tool-based testing is done.

| ID | Finding | Severity | Found by | Status |
|---|---|---|---|---|
| TS-001 | Default fallback JWT secret allowed forged tokens if `SECRET_KEY` was unset | High | Code review | Fixed: `SECRET_KEY` is now required and must be 32+ characters |
| TS-002 | No rate limiting on `/auth/login`, so brute force is possible | Medium | Code review | Open |
| TS-003 | Default database password committed in `config.py` and the migration | Medium | Code review | Open |
| TS-004 | Signup response reveals which emails are already registered | Low | Code review | Open |
| TS-005 | Role is embedded in the JWT, so a role change or revocation is not reflected until expiry | Low | Code review | Open |
| TS-006 | `tenants` table is readable by the app role and has no RLS policy | Low | Code review | Open |

Earlier finding, fixed: the app first connected as the Postgres owner role, which bypasses RLS. Tenant-scoped queries now use a separate non-superuser role (`tenantshield_app`).

## Security

See [SECURITY.md](SECURITY.md). This is a learning project and is not production-ready.

## License

MIT. See [LICENSE](LICENSE).