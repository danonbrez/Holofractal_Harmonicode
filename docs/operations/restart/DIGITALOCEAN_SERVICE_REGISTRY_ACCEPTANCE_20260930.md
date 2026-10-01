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


## Repair-forward: stale Pass 202 successor identities

The first PR check matrix exposed one dependency-scoped failure:

```text
Pass 219 Cumulative Pass 202 Membrane I122
inherited-pass202-membrane (exact): failure
inherited-pass202-membrane (synthetic): failure
step: Prove current successor-hardened Pass 202 deployment identities
```

The historical Pass 202 identities remained valid. The failure was confined to the mutable current-successor seal. Three production deployment files had legitimately advanced on authoritative main after the prior successor seal:

```text
hhs-guarded-update.timer
  previous successor blob: 3296ee9787544542697d3915e01569562ef30046
  current blob:            4d0640477a5f7e0d9657c5fd7f4d6ba4792682bb

hhs-guarded-update.sh
  previous successor blob: 1248ce5f9cc8c1a49a1ef83aab7f47d1bd4ad180
  current blob:            3709ddcd9d5a22b18771794bc3bdbb622ccb02ac

install.sh
  previous successor blob: 9832e410e9aadf2cdda6c8ce3bc70cfd9590f18f
  current blob:            b4df0e7f9711594cf6a518e82d6ec9ca44ae1765
```

These current sources already passed the PR's DigitalOcean deployment-contract gate, Source Text Integrity, and DigitalOcean Mobile Control validation. The successor seal was therefore repaired forward without changing any frozen historical Pass 202 blob identity.

Repair commits:

- `339ebd09d79f1793568f4ad59023aede3f4ba10f` — reseal current Pass 202 deployment successors;
- `7be71021b3abb20b82db15b55be43ab8d9f068e9` — refresh the exact/synthetic CI successor checks.

Validation remaining is the rerun triggered by the repaired branch head. No already-green independent gate needs manual rerun.


## Repair-forward: Pass 202 recovery-verifier boundary

The next repaired head passed the current-successor blob identity step, cumulative C/C++ exact ABI compilation, and authority-export rejection. The remaining I122 failure moved to the Python membrane preflight:

```text
PASS202_SOURCE_BOUNDARY_DRIFT:
deployment/digitalocean/guarded_auto_update/install.sh:
ROLLBACK_HEALTH_FAILED
```

That literal was a stale source-boundary assertion. Current production recovery no longer embeds the recovery classification in `install.sh`; it delegates fail-closed classification to `verify-recovery-state.py`. The verifier still explicitly admits the legacy `ROLLBACK_HEALTH_FAILED` terminal class and the proven `VALIDATED` pre-promotion interruption class.

Repair:

- replace the stale installer-literal requirement with current semantic witnesses:
  - `verify-recovery-state.py`;
  - `HHS_GUARDED_UPDATE_RECOVERY_RECEIPT_VERIFIED=1`;
  - `HHS_ROLLBACK_BOUNDARY_HEALTHY=1`;
- add `verify-recovery-state.py` to the mutable Pass 202 current-successor blob seal at
  `63fd077254c55054c6c2929c02a2b7fa73f8578b`;
- require the verifier itself to preserve the two admitted recovery classes, previous-promoted-boundary proof, live-head rollback-boundary equality, and restart-before-new-promotion requirement;
- mirror the verifier blob identity in the exact/synthetic workflow gate.

Repair commits:

- `621b91b29d3d632afb3ce8c1f3237ceffc06f3b9` — bind recovery verifier into the Pass 202 successor membrane;
- `539845179ab04f6f4cb829108d453166ff02a80b` — seal verifier identity in exact/synthetic CI.

Historical Pass 202 blob identities remain unchanged.
