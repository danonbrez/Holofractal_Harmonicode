# Pass 220 I046 — Warm Hydrated VM Boot Restart Checkpoint

## Repository identity

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `8d2abd36e0841558e618ceacf6dba58a027837c7`
- branch: `pass220/i046-warm-hydrated-vm-boot-v1`
- merge target: `main`

## Trigger

Production restart semantics were audited after the DigitalOcean VM remained
unreachable following a power-on.

The architecture requires a hydrated virtual machine to resume from durable
state rather than rebuilding the hardware/runtime environment on every backend
restart.

Audit found:

- main production `hhs.service` did not set `HHS_DISABLE_C_AUTOBUILD=1`;
- Pass 174 could fall back to repository-local `.hhs/pass174`;
- Pass 194 could fall back to checkout-local `data/pass194`;
- Pass 213 could fall back to the service user's home state directory;
- Pass 205 already had a correct durable production SQLite path.

## Implemented files

```text
deployment/digitalocean/warm_boot_manifest.py
deploy/digitalocean/hhs-pass196-integrated-environment.service
deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh
.github/workflows/pass196-integrated-environment.yml
tests/pass220/test_pass220_i046_warm_hydrated_vm_boot.py
.github/workflows/pass220-i046-warm-hydrated-vm-boot.yml
docs/pass220/PASS_220_I046_WARM_HYDRATED_VM_BOOT_V1.md
docs/operations/restart/PASS_220_I046_WARM_HYDRATED_VM_BOOT_20260923.md
```

## Warm boot implementation

Promotion:

1. validates candidate;
2. builds the native runtime once through the existing post-merge build;
3. activates the prebuilt Runtime OS release;
4. creates/preserves durable state roots under `/var/lib/hhs`;
5. seals the candidate SHA warm-boot manifest;
6. installs the candidate systemd unit;
7. starts the service.

Restart:

1. derives current deployed Git SHA;
2. loads that SHA's warm manifest;
3. requires `HHS_DISABLE_C_AUTOBUILD=1`;
4. verifies native-runtime SHA-256;
5. verifies Runtime OS index SHA-256 and release assets;
6. verifies exact durable state-root bindings;
7. starts Uvicorn without compilation or empty rehydration.

## Durable roots

```text
/var/lib/hhs/data
/var/lib/hhs/pass174
/var/lib/hhs/pass194
/var/lib/hhs/pass205/continuation.sqlite3
/var/lib/hhs/pass213/surface
/var/lib/hhs/pass218
/var/lib/hhs/pass219/lane5
/var/lib/hhs/runtime-bootstrap
/var/lib/hhs/warm-boot/releases
```

## Remaining validation

1. Open PR.
2. Run exact-head `Pass 220 I046 Warm Hydrated VM Boot`.
3. Confirm inherited `Pass 196 Integrated Environment` is green.
4. Repair only impacted I046/service-contract surfaces if needed.
5. Merge exact green head.
6. Verify main.
7. Production deployment remains dependent on SSH recovery of the existing
   DigitalOcean VM.
8. Once reachable, promote exact main and prove a second plain
   `systemctl restart hhs` performs manifest verification/adoption only, with
   no native build or hydration regeneration in the journal.
