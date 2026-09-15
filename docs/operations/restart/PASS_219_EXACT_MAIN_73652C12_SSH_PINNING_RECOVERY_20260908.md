# Pass 219 exact-main 73652c12 SSH pinning recovery — 2026-09-08

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative production payload: `main@73652c122ffff6a8b9bde9de00020610964d704c`
- Recovery branch: `agent/pass219-exact-main-73652c12-ssh-pinning-recovery-20260908`
- Recovery branch base: `73652c122ffff6a8b9bde9de00020610964d704c`
- Workflow-repair commit: `90864bfa512b44db19db3d7b13bfee205289841c`
- Initial SSH reachability diagnostic commit: `be14318c0e7952cffa7cf08c05db0df9a716dbd2`
- Widened production reachability diagnostic commit: `28ef90ac295e813d213e7705548b65ed61db86c4`
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

The diagnostic workflow is non-mutating. It does not request, scan, learn, or accept a host key.

## Validation receipts

### Initial recovery deployment workflow

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

### Initial SSH reachability diagnostic

Run: `34196847576`

Target: `137.184.223.84:22`

Initial attempt, GitHub-hosted Ubuntu runner in `centralus`:

```text
HHS_PRODUCTION_SSH_TCP_REACHABLE=0
error=TimeoutError:timed out
```

A targeted rerun used a different GitHub-hosted runner region (`eastus`) and reproduced the same terminal result:

```text
HHS_PRODUCTION_SSH_TCP_REACHABLE=0 host=137.184.223.84 error=TimeoutError:timed out
```

No SSH banner was received within 15 seconds on either attempt. Host-key discovery was not attempted.

### Widened production reachability diagnostic

Commit: `28ef90ac295e813d213e7705548b65ed61db86c4`

Run: `34265010382`

Job: `102192056386`

Runner region: `mexicocentral`

The diagnostic probed the production IP without host-key discovery and produced:

```text
HHS_PRODUCTION_TCP_22=unreachable detail=TimeoutError:timed out
HHS_PRODUCTION_TCP_80=unreachable detail=TimeoutError:timed out
HHS_PRODUCTION_TCP_443=unreachable detail=TimeoutError:timed out
HHS_PRODUCTION_TCP_8080=unreachable detail=TimeoutError:timed out
HHS_PRODUCTION_HOST_KEY_DISCOVERY_ATTEMPTED=0
```

All four independently probed production TCP surfaces timed out. This rules out an SSH-only failure at this checkpoint: the configured production IP is not reachable from that GitHub-hosted runner on SSH, HTTP, HTTPS, or the direct application port.

The same outage class has now reproduced across GitHub-hosted runner regions `centralus`, `eastus`, and `mexicocentral`.

### Latest exact-main recovery workflow

Run: `34265010375`

- `validate-deployment-contract` job `102192056420`: **SUCCESS**
- `deploy-exact-main` job `102192120618`: **FAILURE** at the fail-closed authority gate
- exact payload checkout: `73652c122ffff6a8b9bde9de00020610964d704c`
- `HHS_DIGITALOCEAN_SSH_PRIVATE_KEY`: present
- `HHS_DIGITALOCEAN_KNOWN_HOSTS`: absent
- bundle build: skipped
- transfer: skipped
- guarded promotion: skipped
- public HTTPS verification: skipped

No production mutation occurred in this run.

## DigitalOcean control-plane observation

The DigitalOcean integration connected during this recovery does not expose the production droplet: its droplet listing is empty and it cannot be used as authority for `137.184.223.84`. No droplet, firewall, reboot, rebuild, or network mutation was attempted through that unrelated control plane.

The recovery must not provision a replacement droplet merely to bypass this outage. The existing production host is part of the exact-main deployment authority and must be recovered or explicitly replaced by a separately authorized infrastructure migration.

## Current blocker classification

**BLOCKED — external production control plane / network authority plus missing pinned trust root.**

Two independent prerequisites remain:

1. Restore reachability of the existing production host `137.184.223.84` through the correct DigitalOcean account/control plane. Because ports 22, 80, 443, and 8080 all time out, inspect droplet power/state, public networking, DigitalOcean Cloud Firewall, host firewall, and upstream ACL/routing before treating this as an SSH-daemon-only issue.
2. Obtain the production SSH host public key through a trusted out-of-band administrative path, verify its fingerprint against the intended host, and provision its exact OpenSSH `known_hosts` entry as repository Actions secret `HHS_DIGITALOCEAN_KNOWN_HOSTS`.

A pinned host key alone cannot repair the current all-port timeout. Restoring network reachability alone does not authorize SSH trust without the pinned key.

No insecure fallback is permitted: no `StrictHostKeyChecking=no`, no opportunistic runtime `ssh-keyscan`, no fabricated host key, and no replacement host under the existing production identity without explicit migration authority.

## Current main invariant

At checkpoint time, `main` remains exactly:

```text
73652c122ffff6a8b9bde9de00020610964d704c
```

Do not advance or merge the recovery workflow into `main` before this exact SHA is promoted, because the remote guarded deployment requires `origin/main == TARGET_SHA`.

## Exact resumable next action

Using the **correct production DigitalOcean account/control plane**:

1. locate the droplet owning `137.184.223.84`;
2. verify it is powered on and still owns that public IP;
3. inspect Cloud Firewall and host/network policy for inbound 22/80/443 and the expected application topology;
4. restore network reachability without weakening unrelated security policy;
5. obtain and verify the host SSH public key out of band;
6. provision `HHS_DIGITALOCEAN_KNOWN_HOSTS` in GitHub Actions secrets;
7. rerun only the latest failed exact-main deployment job `102192120618` from run `34265010375`.

The repaired job will then continue through:

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

If the retry fails after infrastructure recovery, repair only the newly impacted deployment stage and preserve this exact-main boundary.

## Merge state

- Recovery workflow changes: committed on the recovery branch and intentionally not merged.
- Production exact-main promotion: not completed.
- Public HTTPS exact-main verification: not completed.
- Main intentionally unchanged at `73652c122ffff6a8b9bde9de00020610964d704c`.
- A pull request may exist against `main` as a review/restart artifact, but it must remain unmerged until exact-main production closure because merging would advance `origin/main` and invalidate the guarded target-SHA equality.

## Restart instruction

Resume from this branch and record. Do not reconstruct the failure from conversational context. Use this record, the exact SHA, branch state, run `34265010382`, and run `34265010375` as the authoritative recovery receipt.
