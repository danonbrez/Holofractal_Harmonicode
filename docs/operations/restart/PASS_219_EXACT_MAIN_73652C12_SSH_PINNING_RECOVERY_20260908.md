# Pass 219 exact-main 73652c12 SSH pinning recovery — 2026-09-08

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative production payload: `main@73652c122ffff6a8b9bde9de00020610964d704c`
- Recovery branch: `agent/pass219-exact-main-73652c12-ssh-pinning-recovery-20260908`
- Recovery branch base: `73652c122ffff6a8b9bde9de00020610964d704c`
- Workflow-repair commit: `90864bfa512b44db19db3d7b13bfee205289841c`
- SSH reachability diagnostic commit: `be14318c0e7952cffa7cf08c05db0df9a716dbd2`
- Intended merge target after production closure: `main`
- Production host variable/default: `HHS_DIGITALOCEAN_HOST` / `137.184.223.84`

## Original failure state

The exact-main production workflow built and sealed the Runtime OS payload for `73652c122ffff6a8b9bde9de00020610964d704c`, then failed before transfer because `.github/workflows/digitalocean-production-main.yml` performed live `ssh-keyscan -T 15 -H "$HHS_PRODUCTION_HOST"`. Transfer, guarded promotion, and public HTTPS verification therefore did not execute.

The repository contains no audited production host-key material that can safely be substituted for the scan. No host key may be invented, learned opportunistically, or accepted with `StrictHostKeyChecking=no`.

## Implemented recovery design

The recovery-branch workflow now:

1. Requires repository secret `HHS_DIGITALOCEAN_KNOWN_HOSTS` containing the audited OpenSSH `known_hosts` entry for the production target.
2. Materializes only that pinned value into the runner `known_hosts` file; runtime `ssh-keyscan` is removed from the deployment path.
3. Keeps `StrictHostKeyChecking=yes`, sets `UserKnownHostsFile` explicitly through runner SSH config, and disables `UpdateHostKeys`.
4. Fails closed before bundle build/transfer when the SSH private key or pinned host-key material is absent, or when the pinned file does not contain the configured production host.
5. Allows this recovery branch to execute the repaired workflow while checking out and deploying exact payload SHA `73652c122ffff6a8b9bde9de00020610964d704c`.
6. Preserves the remote guard requiring `origin/main == TARGET_SHA`; therefore the workflow repair is not merged to `main` before exact-main production closure.
7. Leaves inherited transfer, guarded promotion, production service/runtime checks, and public HTTPS verification unchanged after SSH trust succeeds.

A separate diagnostic workflow performs only TCP/22 connection and SSH-banner reachability. It does not request, scan, learn, or accept a host key.

## Validation receipts

### Recovery deployment workflow

Run: `34196672498`

- `validate-deployment-contract`: **SUCCESS**
- Exact checkout observed by the deployment job: `73652c122ffff6a8b9bde9de00020610964d704c`
- Existing `HHS_DIGITALOCEAN_SSH_PRIVATE_KEY`: present
- `HHS_DIGITALOCEAN_KNOWN_HOSTS`: absent
- `Require DigitalOcean SSH authority`: **FAIL**, exit `3`
- Bundle build: skipped by fail-closed authority gate
- Transfer: skipped
- Promotion: skipped
- Public HTTPS verification: skipped

This proves the recovery workflow can target the required exact main SHA without moving `main`, and that its new trust gate fails closed when the pinned host key is not provisioned.

### Independent SSH reachability diagnostic

Run: `34196847576`

Target: `137.184.223.84:22`

Observed result:

```text
HHS_PRODUCTION_SSH_TCP_REACHABLE=0
error=TimeoutError:timed out
```

No SSH banner was received within 15 seconds. Host-key discovery was not attempted.

Therefore the current production delivery has **two independent external prerequisites**:

1. TCP/22 reachability from GitHub-hosted Ubuntu runners to `137.184.223.84` must be restored.
2. An out-of-band verified production `known_hosts` entry must be provisioned as repository Actions secret `HHS_DIGITALOCEAN_KNOWN_HOSTS`.

A pinned host key alone cannot repair the present TCP timeout; reopening TCP/22 alone does not authorize trust without the pinned key.

## Current main invariant

At checkpoint time, `main` remains exactly:

```text
73652c122ffff6a8b9bde9de00020610964d704c
```

Do not advance or merge the recovery workflow into `main` before this exact SHA is promoted, because the remote guarded deployment requires `origin/main == TARGET_SHA`.

## External recovery requirement

Restore SSH network access in the production infrastructure path (DigitalOcean Cloud Firewall, droplet firewall/sshd/listener, or upstream ACL as applicable) so GitHub-hosted runners can establish TCP/22 to `137.184.223.84`.

Independently obtain the production SSH host public key through a trusted out-of-band channel, for example the DigitalOcean console or another already-authenticated administrative path on the droplet, verify its fingerprint against the intended host, and provision its exact OpenSSH `known_hosts` line as `HHS_DIGITALOCEAN_KNOWN_HOSTS`.

The available GitHub connector cannot read or administer Actions secret values, and no suitable audited host key exists in the repository. This checkpoint therefore does not fabricate either external prerequisite.

## Exact resumable next action

After both prerequisites are satisfied, rerun **only the failed deployment job/run** for recovery workflow run `34196672498`. The successful deployment-contract job need not be repeated. The repaired job will then continue through:

```text
exact 73652c12 checkout
-> authority gate
-> Runtime OS bundle build/seal
-> pinned SSH trust validation
-> transfer
-> guarded exact-main promotion
-> production service/runtime verification
-> public HTTPS Runtime OS verification
```

If the retry fails after connectivity is restored, repair only the newly impacted deployment stage and preserve this exact-main boundary.

## Merge state

- Recovery workflow changes: not merged.
- Production exact-main promotion: not completed.
- Public HTTPS exact-main verification: not completed.
- Main intentionally unchanged at `73652c122ffff6a8b9bde9de00020610964d704c`.

## Restart instruction

Resume from this branch and record. Do not reconstruct the failure from conversational context. Use the recorded workflow runs, exact SHA, and branch state as the authoritative recovery receipt.