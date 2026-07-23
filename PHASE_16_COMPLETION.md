# Phase 16 — Testing and Security

## Completed

- Unified JWT configuration with the central Pydantic settings object.
- Added issuer, audience, not-before, expiry, issued-at and unique-token validation.
- Prevented custom claims from overwriting protected JWT claims.
- Refresh tokens now verify that the referenced user still exists and is active.
- Added reusable permission-based RBAC dependency alongside role checks.
- Normalized role and permission matching to prevent casing mistakes.
- Enforced production secret-key validation and minimum key length.
- Added trusted-host and restricted CORS configuration.
- Added request-ID validation and propagation.
- Added no-sniff, frame, referrer, permissions, CSP, no-store and HSTS headers.
- Kept generic server errors free of internal exception details.
- Added configuration security tests.
- Added dependency vulnerability scanning (`pip-audit`) to CI.
- Corrected the CI test secret so settings validation succeeds.

## Validation performed

- Existing Phase 8–15 workflow suite: 7 tests passed.
- Phase 16 configuration tests: 3 tests passed.
- Python compilation: passed.
- SQLAlchemy model mapper configuration: passed.
- Alembic revision graph: single head confirmed.

## Environment limitation

The execution sandbox does not provide `python-jose`, `redis`, `celery`, or
`passlib`, and its package mirror cannot install them. Therefore API/JWT tests
requiring those declared dependencies are left to GitHub Actions or the normal
project environment. They remain included in `requirements.txt` and
`pyproject.toml`.
