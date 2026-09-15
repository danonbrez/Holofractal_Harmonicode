# Pass 219 fresh production droplet bootstrap — 2026-09-08

## Repository authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Exact production payload remains: `main@73652c122ffff6a8b9bde9de00020610964d704c`
- Recovery branch: `agent/pass219-exact-main-73652c12-ssh-pinning-recovery-20260908`
- Draft recovery PR: `#411` — **DO NOT MERGE before production closure**
- Recovery branch base: exact `main@73652c122ffff6a8b9bde9de00020610964d704c`
- New-host diagnostic commit: `21189e3cf27ce96e85d17ce44a28d71d57495c9c`

## Root-cause closure for the former production host

The former production droplet was not merely unreachable. DigitalOcean action history records:

- former droplet ID: `589036816`
- name: `hhs-production-01`
- region: `nyc1`
- `power_off` action `3389161995` started `2026-09-05T10:20:53Z`
- `destroy` action `3394109060` started `2026-09-08T05:05:31Z` and completed two seconds later

The account had been locked after a payment problem. The lock is now resolved and the DigitalOcean account reports `status=active`.

Because the former droplet was destroyed, the all-port timeout observed at `137.184.223.84` is no longer treated as an SSH/firewall-only incident. That IP is retired from production recovery authority.

## Replacement production host

A fresh droplet was explicitly authorized as the preferred recovery because the repository is the canonical application/source backup and no destroyed-host filesystem state is required.

DigitalOcean created:

- droplet ID: `598826630`
- name: `hhs-production-01`
- status after provisioning: `active`
- region: `nyc3`
- image: Ubuntu `24.04 (LTS) x64`, image ID `235153036`, slug `ubuntu-24-04-x64`
- size: `s-2vcpu-4gb-120gb-intel`
- vCPU: `2`
- RAM: `4096 MiB`
- disk: `120 GiB`
- public IPv4: `165.227.220.193`
- private IPv4: `10.108.0.2`
- backups: requested at creation, preserving the former production policy
- monitoring: enabled
- injected administrative SSH key: DigitalOcean key `58136400`, name `hhs-phone`, Ed25519 fingerprint `91:64:cf:1c:46:35:24:62:7a:5b:bb:87:09:d8:03:44`

The exact former size is no longer offered in `nyc1`; `nyc3` was selected to preserve the same 2-vCPU / 4-GiB / 120-GiB / $32-month compute footprint instead of silently reducing disk capacity.

## Repository-side new-host preparation

`.github/workflows/pass219-exact-main-ssh-reachability-diagnostic.yml` was updated at commit `21189e3cf27ce96e85d17ce44a28d71d57495c9c` to target the replacement public IP `165.227.220.193` directly.

The diagnostic remains non-authoritative for trust. It may observe an Ed25519 host-key candidate and print its SHA-256 fingerprint, but explicitly records:

```text
HHS_PRODUCTION_HOST_KEY_CANDIDATE_TRUSTED=0
HHS_PRODUCTION_HOST_KEY_CANDIDATE_USE_FOR_DEPLOYMENT=0
```

No observed network key is accepted automatically.

### Replacement-host reachability receipt

GitHub Actions run `34267887235`, job `102201765150`, executed from a `centralus` Ubuntu runner after the replacement droplet became active.

Observed network state:

```text
HHS_PRODUCTION_SSH_BANNER_VALID=1 banner=SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.16
HHS_PRODUCTION_TCP_22=reachable
HHS_PRODUCTION_TCP_80=unreachable detail=ConnectionRefusedError:[Errno 111] Connection refused
HHS_PRODUCTION_TCP_443=unreachable detail=ConnectionRefusedError:[Errno 111] Connection refused
HHS_PRODUCTION_TCP_8080=unreachable detail=ConnectionRefusedError:[Errno 111] Connection refused
```

This closes the former all-port network outage: the replacement host is publicly reachable and SSH is listening. Ports 80, 443, and 8080 are refused rather than timed out because nginx and the HHS production service have not yet been installed on the fresh Ubuntu host.

The diagnostic observed, but did not trust, this Ed25519 host-key candidate:

```text
165.227.220.193 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA1Nj/yZ1JtFnjy7I5ORTZcLJ18dk4BgcD8W4+FfecU1
SHA256:PcLB4oPPvDDmMFVe61ep5Wy9tbrUqbKSVAUoIOeX9Lc
```

The HTTPS probe failed with curl exit `7`, which is expected before the public web boundary exists. No production application deployment has occurred yet.

## Fresh-host semantic difference

The existing exact-main workflow was designed for an already-installed host. Its remote path assumes all of the following already exist:

- `/opt/hhs/app/.git`
- the `hhs` production service user and service filesystem
- `/opt/hhs/venv`
- `hhs.service`
- the guarded updater state root and prior receipts
- an existing nginx/TLS production boundary

Those assumptions are false on a fresh Ubuntu droplet. Therefore the next deployment must use an explicit first-install/bootstrap phase rather than forge a rollback receipt or pretend the new machine is the destroyed host.

The canonical repository already contains the installation inputs needed for bootstrap, including:

- root `requirements.txt`
- `deploy/digitalocean/hhs-pass196-integrated-environment.service`
- `deployment/digitalocean/guarded_auto_update/*`
- `docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md`
- `scripts/complete_hhs_production_https_mobile.sh`

Host-local provider credentials remain secrets and must not be committed. The Pass 196 example specifically treats provider keys as optional host configuration.

## Trust enrollment requirement

The fresh droplet has a new SSH host identity. The destroyed host's `known_hosts` value must not be reused.

Before GitHub deployment authority is enabled, obtain the new host's Ed25519 public host key through an authenticated administrative path tied to droplet `598826630` (preferably the DigitalOcean web console), verify its fingerprint against the observed candidate above, and then pin the resulting `known_hosts` entry for `165.227.220.193`.

The deployment path must continue to use:

```text
StrictHostKeyChecking=yes
UserKnownHostsFile=<pinned file>
UpdateHostKeys=no
```

No `StrictHostKeyChecking=no` and no runtime `ssh-keyscan` may establish production trust.

## Current main invariant

`main` must remain exactly:

```text
73652c122ffff6a8b9bde9de00020610964d704c
```

until this exact payload has been initialized and publicly verified on the replacement host. Draft PR `#411` remains unmerged.

## Exact resumable next action

1. Through the authenticated DigitalOcean web console for droplet `598826630`, run `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256` and require the result to equal `SHA256:PcLB4oPPvDDmMFVe61ep5Wy9tbrUqbKSVAUoIOeX9Lc`; also capture `cat /etc/ssh/ssh_host_ed25519_key.pub`.
2. Pin the verified Ed25519 key for `165.227.220.193` as production deployment trust material.
3. Add a recovery-branch-only fresh-host bootstrap workflow or bootstrap path that:
   - installs Ubuntu host prerequisites;
   - creates the `hhs` service account and protected state roots;
   - clones `danonbrez/Holofractal_Harmonicode` into `/opt/hhs/app`;
   - requires `origin/main == 73652c122ffff6a8b9bde9de00020610964d704c`;
   - creates `/opt/hhs/venv` and installs repository requirements;
   - builds/verifies the native runtime;
   - stages the exact prebuilt Runtime OS bundle;
   - installs `hhs.service` and the guarded updater without fabricating historical recovery receipts;
   - establishes the nginx/HTTPS boundary;
   - verifies loopback and public HTTPS health.
4. Record first-install success as an initialization receipt distinct from an update/rollback receipt.
5. Only after exact-main production verification succeeds, update the canonical deployment host identity and merge the recovery PR.

## Terminal state at this checkpoint

**IN PROGRESS — replacement infrastructure exists, is active, and is SSH-reachable; production software is not yet initialized.**

No claim is made that `73652c12` is in production yet.
