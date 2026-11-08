# Security testing

All testing is against my own local docker-compose instance. No third-party systems.

**Used so far:** Burp Suite Community (Proxy, Intruder), pytest regression tests.
**Planned:** Nmap, OWASP ZAP, Bandit, pip-audit, Trivy.

**Status words:** *Verified* means tested and the evidence supports the claim.
*Partially verified* means something was observed but a question remains.
*Open* means not fixed.

## Finding template

| Field | Content |
|---|---|
| ID / title | |
| Severity | Critical / High / Medium / Low / Info (my own assessment) |
| OWASP mapping | |
| Affected endpoint | |
| Steps to reproduce | |
| Evidence | file path |
| Impact | |
| Remediation | |
| Re-test result | |
| Status | |

## TS-002: Login brute-force protection

| Field | Content |
|---|---|
| Severity | Medium |
| OWASP mapping | A07:2021 Identification and Authentication Failures; API2:2023 Broken Authentication |
| Affected endpoint | `POST /api/v1/auth/login` |
| Status | **Partially verified** |

**Before the fix.** Burp Intruder, 20 candidate passwords, correct one at position 15.
Every wrong guess returned 401 and no 429 was seen. Evidence: `docs/evidence/ts-002-before.png`.

**Fix.** Redis fixed-window limiter: 10 attempts per 60 seconds per client IP, 429 with
`Retry-After`. Fails open if Redis is down (availability over strictness).

**Run 1 after the fix (Intruder).** Evidence: `docs/evidence/ts-002-after-run1.png`.

| Request | Result |
|---|---|
| 7 to 9 | 401 |
| 10 | 429, `Retry-After: 1` |
| 11 to 14 | 401 |
| 15 (correct password) | 200 |

**Reading of run 1 (hypothesis, not yet confirmed).** `Retry-After: 1` means the counter was
almost expired at request 10, so it started about 59 seconds earlier. Likely causes: one
earlier login from Swagger counted toward the limit, and Burp Community's Intruder throttling
let the 60-second window expire mid-attack. A fixed window then starts fresh, which explains
requests 11 to 15.

**Re-test 2 (clean window, PowerShell loop).** [fill in after running Step 4b]
- Requests 1 to 10: [ ]
- Requests 11 to 15: [ ]
- Correct password while limited: [ ]
- Correct password after the window expired: [ ]
- Evidence: `docs/evidence/ts-002-after-run2.png`

**Known limits.**
- The limit is per IP, so many IPs get around it.
- A fixed window allows a burst at the boundary: up to about 20 attempts in a short time.
- It slows brute force (about 600 guesses per hour per IP) but does not stop it.
- Possible next steps: sliding window, per-account backoff. A hard per-account lockout would let
  an attacker lock out a victim, so that has its own trade-off.

## Cross-tenant access (IDOR) and RLS

| Check | Result | What it proves |
|---|---|---|
| Tenant B calls `GET /projects/{A's id}` in Burp | 404, `Project not found` | The endpoint does not leak the project |
| Tenant A calls the same request | 200 | The project exists and the owner can read it |
| `tests/test_idor.py` | automated | Cross-tenant read and delete blocked, foreign id looks identical to a missing id, injected `tenant_id` ignored |
| `tests/test_rls_direct.py` | automated | PostgreSQL RLS alone hides the row: raw SQL with no tenant filter returns 0 rows for another tenant and for no tenant |

The route handler has no tenant filter, so the 404 is produced by RLS, and the direct test confirms it independently of the endpoint.

## TS-007: No password policy on signup
Severity Low. Signup accepted any password. Fixed: 8 to 128 characters in the schema, covered by
`test_signup_rejects_short_password`. The upper bound also limits argon2 hashing cost on huge inputs.