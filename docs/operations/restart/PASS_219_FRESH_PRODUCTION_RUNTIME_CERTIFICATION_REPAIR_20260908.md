# Pass 219 Fresh Production Runtime Certification Repair Restart

## Scope

Recover the fresh DigitalOcean production initialization for exact canonical payload `73652c122ffff6a8b9bde9de00020610964d704c` without changing that payload and without granting the `hhs` service write authority over `/opt/hhs/app`.

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Recovery branch: `agent/pass219-fresh-production-bootstrap-73652c12-20260908`
- Recovery base before this repair: `ad88b002fca8295c12f4fd9fc7c5e2d0b5670816`
- Runtime-state repair implementation commit: `c64dbbb2d95ecd896ef8513dfb93403a1787a539`
- Canonical production payload: `main@73652c122ffff6a8b9bde9de00020610964d704c`
- Production host: `hhs-production-01` / `165.227.220.193`

## Authenticated SSH boundary

The production host Ed25519 key was verified independently from the host console and pinned in the recovery branch. The GitHub Actions deployment key was subsequently enrolled in `/root/.ssh/authorized_keys`. Bootstrap attempt 2 proved SSH authentication successfully before mutation.

Host fingerprint:

`SHA256:PcLB4oPPvDDmMFVe61ep5Wy9tbrUqbKSVAUoIOeX9Lc`

GitHub deployment public-key fingerprint:

`SHA256:D7Y3y7rKj0Qov3EL6zFp1QhiJ1tsX7mA3BhWnQkJeDo`

## Completed validation from bootstrap run 34269238167 attempt 2

Job `102207544252` completed the following gates before the service failure:

1. exact recovery checkout;
2. exact payload checkout at `73652c122ffff6a8b9bde9de00020610964d704c`;
3. pinned host-key validation;
4. SSH authentication as root;
5. Node 22 frontend typecheck and Vite production build;
6. deterministic Runtime OS bundle creation and verification;
7. transfer of the exact bundle to the fresh host;
8. Ubuntu host dependency installation;
9. exact repository hydration on production;
10. Python virtual environment and requirements installation;
11. native `make c-abi` build, including `libhhs_runtime.so`;
12. production checkout permission normalization, with `HHS_PRODUCTION_CHECKOUT_PERMISSION_RECEIPT_V2` result `PASS`.

Runtime OS evidence:

- archive SHA-256: `59081ab668a94dcb180c9f1ca4825c71af8c8e6656dab6e14543da65e6353cab`
- manifest SHA-256: `0dd748aecc2a0c3fc0eb839d20222e75146569d33425e14e12194117aa334c74`

## Failure

The initial `hhs.service` health gate timed out after the service entered a restart loop. The deterministic blocker was:

`PermissionError: [Errno 13] Permission denied: '/opt/hhs/app/runtime_certification'`

The source is `hhs_runtime/runtime_lock_certifier_v1.py`, which resolves `CERT_DIR` as `REPO_ROOT / "runtime_certification"` and creates it at import time. The canonical production service intentionally runs as `User=hhs`, uses `ProtectSystem=full`, and grants writable state only under `/var/lib/hhs` via `ReadWritePaths=/var/lib/hhs`.

The deployment must not repair this by making the repository writable.

## Repair

`deployment/digitalocean/fresh_host_runtime_certification_repair.sh` installs an idempotent systemd drop-in:

```ini
[Service]
BindPaths=/var/lib/hhs/runtime-certification:/opt/hhs/app/runtime_certification
```

The source state directory is owned by `hhs:hhs` with mode `0750`. The unchanged exact payload therefore continues to resolve its historical path, but the service mount namespace maps that path onto the canonical writable production state root. The script requires exact production HEAD and a clean worktree both before and after repair, starts the service, waits for `/api/system/status`, and verifies from the service mount namespace that `hhs` can write the bound certification path.

## Remaining work

1. Execute `fresh_host_runtime_certification_repair.sh` through the already pinned SSH channel.
2. Require green loopback service health and zero repository drift.
3. Resume the existing idempotent fresh-host bootstrap against exact `73652c12` using the already transferred Runtime OS bundle.
4. Install/verify the guarded follower.
5. Configure browser-trusted public HTTPS and certificate renewal.
6. Write and verify `HHS_FRESH_PRODUCTION_INITIALIZATION_RECEIPT_V1` without fabricating rollback history.
7. Verify public HTTPS root and `/api/system/status`.
8. Verify production language/assistant authority separately.
9. Record final receipts and either merge/ready the recovery changes or record the precise remaining blocker.

## Exact next action

Run the repository-visible repair through pinned SSH, then continue bootstrap only if the repair proves loopback health and a clean exact payload tree.
