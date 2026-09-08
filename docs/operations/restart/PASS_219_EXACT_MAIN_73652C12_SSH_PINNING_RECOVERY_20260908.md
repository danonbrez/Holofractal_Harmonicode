# Pass 219 exact-main 73652c12 SSH pinning recovery — 2026-09-08

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative production payload: `main@73652c122ffff6a8b9bde9de00020610964d704c`
- Recovery branch: `agent/pass219-exact-main-73652c12-ssh-pinning-recovery-20260908`
- Intended merge target after production closure: `main`
- Production host variable/default: `HHS_DIGITALOCEAN_HOST` / `137.184.223.84`

## Failure state

The exact-main production workflow built and sealed the Runtime OS payload for `73652c122ffff6a8b9bde9de00020610964d704c`, then failed before transfer because `.github/workflows/digitalocean-production-main.yml` performs live `ssh-keyscan -T 15 -H "$HHS_PRODUCTION_HOST"`. Transfer, guarded promotion, and public HTTPS verification therefore did not execute.

The repository contains no audited production host-key material that can safely be substituted for the scan. No host key may be invented, learned opportunistically, or accepted with `StrictHostKeyChecking=no`.

## Recovery design

The workflow repair will:

1. Require a pre-provisioned repository secret `HHS_DIGITALOCEAN_KNOWN_HOSTS` containing the audited OpenSSH `known_hosts` entry for the production target.
2. Materialize only that pinned value into the runner `known_hosts` file; runtime `ssh-keyscan` is forbidden.
3. Keep `StrictHostKeyChecking=yes`, set the `UserKnownHostsFile` explicitly, and disable `UpdateHostKeys` for deployment SSH/SCP calls.
4. Fail closed before bundle build/transfer when the SSH private key or pinned host-key material is absent or the pinned file does not contain the configured production host.
5. Allow this recovery branch to execute the repaired workflow while checking out and deploying **exact payload SHA** `73652c122ffff6a8b9bde9de00020610964d704c`.
6. Preserve the remote guard requiring `origin/main == TARGET_SHA`; therefore the workflow repair is not merged to `main` before exact-main production closure.
7. Run the inherited transfer, guarded promotion, service/runtime checks, and public HTTPS verification unchanged after SSH trust succeeds.

## Validation / deployment state

- Workflow inspection: complete.
- Existing live key-scan dependency identified: complete.
- Audited repository host key found: no.
- Recovery branch created from exact main: complete.
- Workflow repair: pending.
- YAML / static validation: pending.
- Recovery deployment: pending.
- Production promotion: pending.
- Public HTTPS verification: pending.

## Blocker semantics

If `HHS_DIGITALOCEAN_KNOWN_HOSTS` is not already provisioned in repository Actions secrets, the repaired workflow must stop with an explicit missing-pinned-host-key error. The GitHub connector available to this task does not expose secret values or permit secret administration, so this task cannot fabricate or silently provision that trust root.

## Restart instruction

Resume from this branch and record. Patch `.github/workflows/digitalocean-production-main.yml` only as necessary for pinned host trust and exact-SHA recovery. Do not advance `main` before deployment of `73652c122ffff6a8b9bde9de00020610964d704c` succeeds, because the remote guarded promotion requires `origin/main` to remain that exact SHA.