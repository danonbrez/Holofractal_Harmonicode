# Pass 220 I046 warm-boot repository identity repair — 2026-10-02

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `33273c3aa05309d08095c83c352cee49ecea65db`
- branch: `repair/warm-boot-sealed-repository-identity-20261002`
- merge target: `main`
- production deployment from this branch: not authorized before PR validation

## Triggering production evidence

Exact-main run `37044935240` for recovery commit
`9e9e40df1b6a1cc1c0816f432b2b24b5803aa6ee` reached the production host and passed:

- deployment-contract validation;
- pinned SSH authority;
- Runtime OS bundle build/seal;
- bundle transfer;
- recovery-state authorization;
- production checkout permission normalization;
- unified ledger recovery checks.

The authorized rollback boundary was:

`cf2764c24e85ff4980d599f528218f1328b81627`

with legacy warm-boot manifest:

`/var/lib/hhs/warm-boot/releases/cf2764c24e85ff4980d599f528218f1328b81627.json`

Service restart then failed repeatedly in `ExecStartPre`:

```text
WarmBootError: HHS_WARM_BOOT_REPOSITORY_HEAD_UNAVAILABLE
```

The preflight was executing:

```text
/opt/hhs/venv/bin/python
/opt/hhs/app/deployment/digitalocean/warm_boot_manifest.py verify
--repo-root /opt/hhs/app
--manifest-root /var/lib/hhs/warm-boot/releases
```

The verifier called `git -C /opt/hhs/app rev-parse HEAD` as the restricted `hhs`
service identity even though repository metadata is intentionally outside the
service-readable production source boundary.

Promotion and public HTTPS verification were skipped.

## Repair design

Do not make production `.git` broadly service-readable.

Instead, preserve the sealed warm-boot manifest as authority and add one
service-readable exact repository-identity pointer:

`/var/lib/hhs/warm-boot/current-repository-sha`

The pointer contains exactly one validated 40-hex Git commit identity and is
bound only to an already-existing SHA-scoped warm-boot manifest.

### Warm-boot verifier

`deployment/digitalocean/warm_boot_manifest.py` now supports:

```text
verify --repository-sha-file <path>
```

When the explicit SHA file is supplied:

- Git metadata is not consulted;
- the value must be exact 40-hex;
- the SHA-scoped warm-boot manifest must exist;
- the manifest's embedded repository SHA must equal the sealed SHA;
- manifest digest, native runtime digest, Runtime OS digest, and persistent state roots remain fully verified;
- autobuild remains forbidden.

Git `HEAD` remains the fallback for root-side creation/recovery tools that do
have repository authority.

### Stable production verifier and rollback-safe override

`hhs.service` now invokes:

```text
/usr/local/lib/hhs-guarded-update/warm_boot_manifest.py verify
--repo-root /opt/hhs/app
--manifest-root /var/lib/hhs/warm-boot/releases
--repository-sha-file /var/lib/hhs/warm-boot/current-repository-sha
```

This avoids depending on the application checkout's own Python verifier while a
rollback boundary is being recovered.

A repository-owned systemd drop-in,
`deploy/digitalocean/hhs-warm-boot-identity.conf`, clears only the inherited
`ExecStartPre` and replaces it with the stable verifier command. The exact-main
installer and guarded updater install this drop-in under
`/etc/systemd/system/hhs.service.d/20-hhs-warm-boot-identity.conf`.

This matters on rollback: the predecessor `hhs.service` definition can still be
restored unchanged while the repaired warm-boot preflight remains active. No
candidate `ExecStart`, application environment, or application service
definition is imposed on the predecessor boundary.

### Identity lifecycle

The guarded updater atomically binds:

- candidate SHA after the candidate warm-boot manifest is sealed;
- previous SHA before rollback service restart.

The exact-main installer, after recovery-state authorization and before starting
the rollback service, installs the repaired stable verifier/service definition
and atomically binds the already-authorized `current_head`.

Therefore:

```text
authorized rollback SHA
-> existing sealed SHA manifest
-> service-readable exact SHA pointer
-> stable verifier
-> hhs.service restart
```

No VM81, Hash72, Hash216, receipt, ledger, or mutation authority is moved.

## Changed files

- `deployment/digitalocean/warm_boot_manifest.py`
- `deploy/digitalocean/hhs-pass196-integrated-environment.service`
- `deploy/digitalocean/hhs-warm-boot-identity.conf`
- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh`
- `deployment/digitalocean/guarded_auto_update/install.sh`
- `tests/pass220/test_pass220_i046_warm_hydrated_vm_boot.py`
- `.github/workflows/pass220-i046-warm-hydrated-vm-boot.yml`
- `.github/workflows/digitalocean-production-main.yml`
- this restart record

## Commands executed

No local repository shell was available. Repository inspection and mutation were
performed through the connected GitHub API.

Production evidence was read from:

- workflow run `37044935240`;
- deploy job `110964290889`.

The dependency-scoped CI commands encoded on this branch include:

```text
python -m py_compile deployment/digitalocean/warm_boot_manifest.py
bash -n deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh
bash -n deployment/digitalocean/guarded_auto_update/install.sh
python -m pytest -q tests/pass220/test_pass220_i046_warm_hydrated_vm_boot.py
```

Exact-main deployment-contract validation also compiles
`deployment/digitalocean/warm_boot_manifest.py`.

## Validation completed

Before implementation, production evidence proved:

- recovery receipt authorization: PASS;
- legacy warm-boot boundary verification: PASS;
- production source/runtime permission normalization: PASS;
- service restart: FAIL only at repository HEAD discovery.

Repository implementation has been committed to the restartable branch.

New regressions cover:

- verification from sealed SHA without invoking Git;
- rejection of malformed sealed repository identity;
- production service use of the stable verifier and SHA file;
- rollback-safe systemd override changes only `ExecStartPre`;
- promotion candidate identity binding;
- rollback predecessor identity binding;
- recovery bootstrap binding before service start.

## Validation remaining

Require PR CI:

1. Pass 220 I046 warm-boot Python regressions: PASS;
2. warm-boot Python compile: PASS;
3. guarded updater shell syntax: PASS;
4. exact-main deployment-contract validation: PASS;
5. source integrity and any dependency-scoped production contracts affected by the changed files: PASS.

After merge:

6. verify exact current-main deployment reaches recovery service health;
7. verify candidate promotion completes;
8. verify `hhs.service` active on exact current-main SHA;
9. verify Lane 5 host ingress socket/service;
10. verify nginx zero-bypass;
11. verify public HTTPS Runtime OS/API closure.

## Environment state

- production host: `159.65.178.254`
- production recovery access: SSH succeeded in run `37044935240`
- rollback checkout at failure: `cf2764c24e85ff4980d599f528218f1328b81627`
- promoted target in failed recovery attempt: `9e9e40df1b6a1cc1c0816f432b2b24b5803aa6ee`
- current repository main at branch creation:
  `33273c3aa05309d08095c83c352cee49ecea65db`
- CI: GitHub Actions Ubuntu 24.04
- production service user/group: `hhs:hhs`
- service Git metadata access: remains unnecessary and intentionally unexpanded

## Blockers

- dependency-scoped PR validation is pending;
- production promotion must not be retried from an unmerged/unverified branch.

## Next action

Open a PR from `repair/warm-boot-sealed-repository-identity-20261002` to current
`main`, inspect I046 and exact-main deployment-contract gates, repair-forward
only attributable failures, then merge and allow exact-current-main promotion to
proceed through public HTTPS verification.
