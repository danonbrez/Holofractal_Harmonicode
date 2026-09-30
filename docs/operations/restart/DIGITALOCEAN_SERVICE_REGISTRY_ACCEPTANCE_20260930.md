# DigitalOcean service-registry acceptance repair — 2026-09-30

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main: `7c7dae820da99acc82cfae764df8ae0020fed9ed`
- Branch: `agent/digitalocean-service-registry-acceptance-20260930`
- Merge target: `main`
- Production host: DigitalOcean `hhs-production-04` / `159.65.178.254`
- Implementation commits before this restart record:
  - `520e9415d745e10260d89a6b364995916253ff5a` — verify production service registry end to end
  - `f7faae3ff039a0c5a4a4ed855b639a48acd10b0e` — gate production on live service registry

## Trigger

The live Runtime OS Visual Program surface was reachable and rendered its executable registry, but the browser exposed:

```text
[Errno 13] Permission denied: 'demo_reports'
```

The source repair for the implicit semantic composition cache is already present on authoritative main: production resolves the live cache through `HHS_LIVE_SEMANTIC_COMPOSITION_CACHE_PATH` / `HHS_RUNTIME_OUTPUT_DIR` under `/var/lib/hhs/data/runtime`, while the historical `demo_reports` location is only a development fallback.

The remaining delivery gap was acceptance coverage. `DigitalOcean Production Exact Main` verified system status, interface status, the Runtime OS root, exact bundle identity, and public HTTPS, but it did not exercise `GET /api/runtime/services`. A production release could therefore satisfy its existing smoke checks while the Visual Program service registry still failed.

## Implemented repair

`.github/workflows/digitalocean-production-main.yml` now requires the exact promoted backend to return a non-empty service registry twice:

1. locally on the production host through
   `http://127.0.0.1:8080/api/runtime/services`;
2. publicly through
   `https://159.65.178.254/api/runtime/services`.

Both probes use fail-on-HTTP-error semantics and parse the canonical response. An empty or malformed `services` array aborts production acceptance.

The workflow emits:

```text
HHS_DIGITALOCEAN_LOCAL_SERVICE_REGISTRY_VERIFIED=<count>
HHS_DIGITALOCEAN_PUBLIC_SERVICE_REGISTRY_VERIFIED=<count>
```

The deployment contract regression now requires both verification markers and at least two `/api/runtime/services` probes.

## Authority boundary

This repair does not weaken filesystem hardening, browser authority, Hash72/Hash216 authority, VM81 mutation authority, SSH host verification, or exact-main promotion.

Pass 218 I14 is intentionally unchanged. The production screenshot reports an empty I14 operator registry with approval threshold 2. The I14 implementation requires real Pass-146-bound operator identities and separation among preparer, two distinct approvers, and executor. No placeholder identities, keys, quorum, certificate, snapshot, or rehearsal evidence are fabricated by this repair.

## Changed files

- `.github/workflows/digitalocean-production-main.yml`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
- `docs/operations/restart/DIGITALOCEAN_SERVICE_REGISTRY_ACCEPTANCE_20260930.md`

## Validation state

Repository-visible source edits are complete. Validation still required on the branch/PR:

```text
bash -n deployment/digitalocean/guarded_auto_update/*.sh
python3 -m py_compile deployment/digitalocean/guarded_auto_update/*.py
focused test_hhs_guarded_auto_update_contract_v1 deployment-contract gate
DigitalOcean Production Exact Main pull-request contract validation
```

Live production verification must occur only after an accepted merge to exact main. Required closure evidence is both service-registry verification markers from the exact-main deployment and a browser refresh showing Visual Program without the `demo_reports` permission error.

## Next action

Open the PR, inspect dependency-scoped pull-request checks, repair forward only on failures attributable to this change, then merge when restartable/mergeable and trigger exact-main deployment. Do not populate Pass 218 I14 until the real operator identities and distributed-authority prerequisites exist.
