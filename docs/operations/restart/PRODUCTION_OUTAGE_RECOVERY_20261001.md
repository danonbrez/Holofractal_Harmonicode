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
refresh commits containing large projection artifacts before the outage. Those
commits are sufficient to trigger the exact-main delivery path under the current
workflow.

## Repair-forward branch changes

Changed files:

- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.service`
- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.timer`
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

1. run the existing dependency-scoped deployment contract CI on this branch;
2. inspect the disposable clone with DigitalOcean Recovery Console / Recovery ISO;
3. determine whether the installed guest has a full disk, failed network units,
   disabled/masked ssh/nginx, boot dependency deadlock, or updater/systemd state;
4. repair the clone first and prove 22/80/443 plus HHS health;
5. apply only the proven guest repair to production or migrate durable state to a
   clean host;
6. merge the resource-boundary repair after validation;
7. delete `hhs-recovery-20261001` after production recovery is verified.

## Next action

Use DigitalOcean's out-of-band Recovery Console on the disposable recovery
Droplet. If needed, boot that clone from the Recovery ISO, mount/chroot the disk,
then inspect disk/inode pressure, systemd failed units, network configuration,
sshd/nginx enablement, updater receipts, and the HHS warm-boot journal. Do not
restore the backup over production.
