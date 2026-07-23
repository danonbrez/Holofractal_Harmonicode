# Pass 135 — Canonical CEUAC Audit

Pass 135 audits the immutable Pass 134 full-ancestry checkpoint through public build, CLI, archive, and HTTP interfaces. Source inspection is not used as A1/A2 capability evidence.

```bash
python -m hhs_runtime.hhs_pass135_ceuac_audit_v1 run PASS_134.zip release_artifacts/pass135
python -m hhs_runtime.hhs_pass135_ceuac_audit_v1 verify release_artifacts/pass135
```

Read-only audit API:

- `GET /api/audit/ceuac/pass135/status`
- `GET /api/audit/ceuac/pass135/record`
- `GET /api/audit/ceuac/pass135/scenarios`
- `GET /api/audit/ceuac/pass135/verification`
- `GET /api/audit/ceuac/pass135/errata`
