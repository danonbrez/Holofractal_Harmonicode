# Production outage recovery checkpoint — 2026-10-01

## Repository identity

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `613b731032157bf761fca3943d04dce1c5b2acda`
- branch: `repair/production-updater-resource-guard-20261001`
- merge target: `main`
- current branch head before this checkpoint: `2cef74827d68392e3d4b4d2227d722387adfdf1c`

## Incident state

Production Droplet:

- name: `hhs-production-04`
- DigitalOcean ID: `603583798`
- public IPv4: `159.65.178.254`
- control-plane state: `active`
- external TCP result after normal reboot and hard power cycle:
  - 22: refused
  - 80: refused
  - 443: refused
  - 8080: refused
  - 8720: refused

A normal reboot and then a DigitalOcean hard power cycle both completed successfully
without restoring any listener. Production was not restored, rebuilt, resized, or
overwritten.

## Isolated recovery clone

Source backup:

- image ID: `247876909`
- name: `hhs-production-04 2026-10-01:16`
- captured: `2026-10-01T16:21:56Z`
- status: `available`

Disposable recovery Droplet:

- name: `hhs-recovery-20261001`
- DigitalOcean ID: `605369577`
- public IPv4: `161.35.141.222`
- source image: `247876909`
- size: same 2-vCPU / 4-GiB / 120-GB production geometry
- backups: disabled
- monitoring: enabled
- tags: `hhs-recovery`, `temporary`, `incident-20261001`

The restored backup reproduces the same refused-listener state on
22/80/443/8080/8720. A root-password reset on the disposable clone completed but
did not restore listeners. This isolates the defect to guest boot/configuration or
saved system state already present in the backup rather than a post-backup-only
mutation.

## Relevant runtime observations

The browser production integration exposes phases named:

- `HYDRATING_RUNTIME_AUTHORITY`
- `HYDRATING_SERVICE_REGISTRY`

These phases wait on backend API requests and therefore do not by themselves prove
that a cold hydration computation is executing.

The I046 warm-boot contract explicitly forbids build/cold-rehydration during a
normal `hhs.service` restart. The service uses `warm_boot_manifest.py verify`
before Uvicorn and must adopt durable `/var/lib/hhs` state.

The guarded production updater remains capable of candidate validation and native
build work during promotion. Main also received generated Hash216 repository-index
refresh commits containing large projection artifacts before the outage. Those bot
commits are pushed with the repository's default GitHub token and therefore are not
treated as evidence of a recursive Actions trigger loop. The material runner defect
is instead the independent production workflows attached to ordinary real main
pushes and their persistent host-side mutations.

## GitHub-runner causal evidence

Repository and Actions evidence identifies a concrete hard-wired production
mutation chain.

### Independent production runners

Commit `a1441d3c393992413d34efc40b9e53e784b54cf5`
(`Pass 220: decouple application VM production from frontend deployment`,
2026-09-21 22:04 America/New_York) changed the Application-VM workflow from a
downstream `workflow_run` that waited for `DigitalOcean Production Exact Main`
to an independent `push: main` deployment.

The Exact-Main and Application-VM workflows then had:

- the same root SSH production target;
- different GitHub concurrency groups;
- different remote lock files;
- independent access to the same `/opt/hhs/app/.git` object/ref store;
- independent systemd/nginx mutation paths.

On 2026-09-27 commits `8699b341`, `bc95f369`, `3bc94f42`, and
`e0918dd6` moved/pinned the production workflows to
`159.65.178.254` / `hhs-production-04`.

### Production network/desktop stack mutation

The first inspected post-pin Application-VM production run
`36350240105` executed the hard-wired:

```text
HHS_APPLICATION_VM_REQUIRE_GUI=1
HHS_APPLICATION_VM_INSTALL_GUI=1
```

path on the production Droplet.

Its runner log proves that `ubuntu-desktop-minimal` was installed directly on
the server. This included persistent boot-integrated packages and services such
as:

- `network-manager`;
- `NetworkManager.service`;
- `NetworkManager-wait-online.service`;
- `gdm3`;
- GNOME/Xorg;
- `gnome-remote-desktop`;
- `dnsmasq-base`;
- OpenVPN/PPTP NetworkManager integrations;
- CUPS and other desktop-oriented services.

The log records:

```text
Setting up network-manager (1.46.0-1ubuntu2.8)
Created symlink .../network-online.target.wants/NetworkManager-wait-online.service
Created symlink .../multi-user.target.wants/NetworkManager.service
Setting up gdm3
Setting up ubuntu-desktop-minimal
```

The deployment then failed with:

```text
HHS_APPLICATION_VM_INSTALL_FAILED: native runtime export missing: hhs_hash216_compute
HHS_APPLICATION_VM_DEPLOY_FAILED=30c9f7cf5c878f47e9845b809391993dde3f5c82
```

The package/systemd side effects were not transactionally rolled back.

### Persistent Application-VM restart loop

The runner-created `hhs-application-vm.service` is enabled for
`multi-user.target`, runs as `hhs`, and historically used
`Restart=on-failure` with `RestartSec=3`.

The production workflow creates release worktrees as root under `umask 027`
without normalizing traversal/read permissions for `hhs`. Actions logs prove
the resulting unit repeatedly failed before Python startup:

```text
status=200/CHDIR
Changing to the requested working directory failed: Permission denied
```

On 2026-09-28 run `36417083465`, the restart counter was already approximately
9,580. On 2026-10-01 run `36818204021`, it exceeded 81,556 and continued
restarting every approximately three seconds. Because the unit is enabled, this
state persists across reboot and is captured in the production backup.

### Concurrent Git mutation proof

On 2026-10-01 Exact-Main run `36818203974`, SSH was still healthy and
`HHS_PRODUCTION_SSH_PREFLIGHT_VERIFIED=1` was emitted. The remote runner then
failed while another process modified the same tracking ref:

```text
error: cannot lock ref 'refs/remotes/origin/main':
is at f5c90419cbcf57f837be388f5bbde29d1f9cbde0
but expected bebae0c0e5bb5e3183c04e1e9895956ae8b49585
```

This is direct evidence that the independently locked production mutation paths
were concurrently operating on the same production Git repository.

By 2026-10-01 14:02 UTC, both Exact-Main job `110405380064` and
Application-VM job `110405068782` failed at the SSH boundary with:

```text
ssh: connect to host 159.65.178.254 port 22: Connection timed out
```

Later runners therefore observed the outage; they did not create it.

The repository evidence supports a runner-installed persistent host-state failure
as a leading cause. In particular, installing/enabling a desktop/network stack on
a server Droplet and leaving a permanently enabled failing service created boot
state that survives reboot and backup restore. Exact attribution of the final
network loss still requires offline guest inspection, but the hard-wired runner
topology and its host mutations are proven defects and must be repaired regardless.

## Repair-forward branch changes

Changed files include:

- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.service`
- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.timer`
- `.github/workflows/digitalocean-production-main.yml`
- `.github/workflows/pass220-ubuntu-application-vm-production.yml`
- `deployment/ubuntu/application_vm/hhs-application-vm.service.template`
- `tests/pass220/test_pass220_ubuntu_application_vm_control_plane.py`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
- this checkpoint

Implemented host-availability membrane:

- updater nice level: 15
- CPU quota: 100% total, leaving one production vCPU available
- CPU weight: 10
- memory high-water: 2 GiB
- memory maximum: 3 GiB
- swap maximum: 1 GiB
- I/O weight: 10
- I/O scheduling class: idle
- OOM score adjustment: 500
- task maximum: 512

Watchdog cadence:

- boot delay: 15 minutes
- periodic follower: 30 minutes
- randomized delay: 2 minutes
- accuracy: 30 seconds

Push-triggered exact-main delivery remains the primary deployment owner; this
change does not alter VM81/Hash72/Hash216 authority, promotion identity, rollback,
or receipt semantics.

### GitHub-runner mutation membrane

The branch now also enforces:

- Application-VM production is `workflow_dispatch` only; no `push: main`
  production mutation;
- Application-VM production uses
  `/run/lock/hhs-production-mutation.lock`;
- Exact-Main holds the same production-mutation lock for its complete remote
  transaction;
- the production workflow no longer sets
  `HHS_APPLICATION_VM_INSTALL_GUI=1`;
- GUI/network-stack provisioning is an explicit bootstrap action, not a deploy
  side effect;
- root-created release worktrees are normalized to `root:hhs` with group
  traversal/read access before the `hhs` service is started;
- `hhs-application-vm.service` uses a five-start/300-second rate limit and
  `RestartSec=30`, preventing unbounded restart storms.

## Validation

Completed:

- branch content re-fetched from GitHub;
- all new service resource-control tokens present;
- all new timer cadence tokens present;
- existing deployment contract test updated to assert every new invariant;
- obsolete 5-minute/30-second timer assertions absent from the timer.

Local clone execution from the task container was attempted but blocked by the
container's DNS/network restriction before repository materialization. This is an
environmental validation blocker, not a source-test failure.

Remaining:

1. run dependency-scoped CI on this branch;
2. obtain state-preserving offline guest access through DigitalOcean support or
   another provider-supported disk rescue path;
3. inspect NetworkManager/netplan/networkd authority, enabled targets, disk/inode
   pressure, ssh/nginx state, and the application-VM restart history;
4. repair the disposable clone first and prove 22/80/443 plus HHS health;
5. apply only the proven guest repair to production or migrate durable state to a
   clean host;
6. merge the runner/updater hardening only after validation;
7. delete `hhs-recovery-20261001` after production recovery is verified.

## Next action

Do not use the mobile Recovery Console as an operational dependency; it is
unusable in the current client. Preserve production and the backup. Use the
repository evidence above to guide offline repair: disable the failing
Application-VM unit, restore the intended server network renderer/authority,
remove or neutralize unintended desktop network ownership as required, then boot
the disposable clone and prove SSH/nginx/HHS before touching production.
