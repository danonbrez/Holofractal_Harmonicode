# Pass 220 production permission regression import repair — 2026-10-02

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `7c7e984c8763d89d023c3a388c575345c6dedd77`
- branch: `repair/production-permission-test-sys-import-20261002`
- merge target: `main`
- triggering exact-main run: `37080420077`
- triggering deploy job: `111079541362`

## Triggering evidence

PR #693 merged as `d3afe3f0518020ce8b81a43889bb2dbe50c95d1c`.

Its production recovery path proved the sealed warm-boot identity repair:

- recovery state authorization: PASS;
- unified Hash72 ledger boundary: PASS;
- `HHS_RECOVERY_WARM_BOOT_REPOSITORY_IDENTITY_BOUND=cf2764c24e85ff4980d599f528218f1328b81627`;
- predecessor service recovered healthy:
  `HHS_ROLLBACK_BOUNDARY_HEALTHY=1`.

Candidate validation then failed only in:

```text
tests/test_hhs_production_service_permissions_v2.py::
test_installed_normalizer_imports_recovery_from_explicit_repo_root
```

Pytest reported:

```text
NameError: name 'sys' is not defined. Did you forget to import 'sys'
```

The test uses `sys.modules` and `sys.path`, but the test module omitted
`import sys`.

The production normalizer implementation already contains the required explicit
repository-root behavior:

```text
repository_root = root.resolve()
sys.path.insert(0, str(repository_root))
```

Therefore this failure is test-harness divergence, not authorization to weaken
or alter the production recovery semantics.

## Repair

Changed:

- `tests/test_hhs_production_service_permissions_v2.py`
- `.github/workflows/pass219-cumulative-pass202-membrane-i122.yml`

The test adds the missing standard-library import:

```python
import sys
```

The first PR run exposed a separate inherited successor-identity drift from PR #693:
the Pass 202 membrane still pinned the pre-#693 blobs for the guarded updater and
installer. Historical Pass 202 identities remain frozen; only the current successor
pins were refreshed to the repository-visible current blobs:

```text
hhs-guarded-update.sh
444d8015a06444771d30bc8992c3881570c4bced

install.sh
51fb5fab508324f42acf2da1caf5202ab39bd2bb
```

No runtime, service, warm-boot, VM81, Hash72, Hash216, ledger, permission,
promotion, rollback, or deployment authority changed by this repair.

## Commands executed

No local repository shell was available. Repository evidence and mutation were
performed through the connected GitHub API.

The failing production candidate validation executed:

```text
python -m pytest -q
  tests/test_hhs_guarded_auto_update_contract_v1.py
  tests/test_hhs_production_service_permissions_v2.py
  tests/test_hhs_full_application_ide_root_v1.py
  tests/test_hhs_repository_history_surface_v1.py
  tests/test_hhs_pass205_continuation_runtime_v1.py
```

Result before repair:

```text
1 failed, 48 passed, 1 warning
```

## Validation completed

- failure reproduced from production workflow logs;
- exact failing exception identified as missing `sys` import;
- production normalizer explicit repo-root path confirmed present;
- repair committed on exact current-main base;
- first inherited Pass 202 PR run failed before pytest on stale successor hashes;
- current updater and installer blob identities were read from authoritative main and
  substituted only into the current-successor identity assertions.

## Validation remaining

Require dependency-scoped CI:

1. production service-permission regression suite: PASS;
2. inherited Pass 202/production membrane affected by this test path: PASS;
3. source integrity: PASS;
4. merge only after the exact test gate is green.

After merge, allow exact-current-main promotion to rerun and verify:

5. sealed warm-boot recovery;
6. candidate validation;
7. promotion receipt;
8. `hhs.service` and Lane 5 service/socket active;
9. nginx zero-bypass;
10. public HTTPS Runtime OS verification.

## Environment state

- current main at branch creation:
  `7c7e984c8763d89d023c3a388c575345c6dedd77`
- production rollback boundary:
  `cf2764c24e85ff4980d599f528218f1328b81627`
- recovery warm-boot SHA binding: verified
- production rollback service health: verified
- candidate promotion: blocked before mutation by candidate validation
- public HTTPS verification: not reached

## Blockers

- dependency-scoped CI for the repaired test must pass.

## Next action

Open the repair PR, inspect the production-permission and inherited membrane
checks, merge with expected-head protection when green, then follow the newest
exact-main production run through HTTPS closure.
