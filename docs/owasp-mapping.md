# OWASP Top 10 (2021) Mapping

> Status: planned. Each row will be updated to "Implemented" once the defense exists and is tested.

| Risk | Planned defense | Status |
|---|---|---|
| A01 Broken Access Control | PostgreSQL RLS, RBAC, cross-tenant tests | Planned |
| A02 Cryptographic Failures | argon2 password hashing, signed JWTs, secrets from environment | Planned |
| A03 Injection | SQLAlchemy parameterized queries, Pydantic validation | Planned |
| A04 Insecure Design | Threat model, tenant isolation at DB level | Planned |
| A05 Security Misconfiguration | Non-root container, no secrets in code, minimal CI permissions | Partly done |
| A06 Vulnerable and Outdated Components | Dependabot, pip-audit, Trivy | Partly done |
| A07 Identification and Authentication Failures | JWT expiry and refresh, rate limiting | Planned |
| A08 Software and Data Integrity Failures | Hash-chained audit log, CI checks | Planned |
| A09 Security Logging and Monitoring Failures | Audit log of security-relevant events | Planned |
| A10 Server-Side Request Forgery | Not applicable yet, to be reviewed | Planned |