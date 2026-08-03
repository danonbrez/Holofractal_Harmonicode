# Pass 205 writable state installation

Pass 205 continuation snapshots, lineage, vectors, deltas, and receipts are mutable production state. They must not be stored inside the Git checkout used by guarded deployment.

Run as root:

```bash
bash deployment/digitalocean/pass205_state/install.sh
```

The installer:

- discovers the configured `hhs.service` user and group;
- creates `/var/lib/hhs/pass205` with service-owned `0750` permissions;
- installs `/etc/systemd/system/hhs.service.d/20-pass205-state.conf`;
- sets `HHS_PASS205_DB=/var/lib/hhs/pass205/continuation.sqlite3`;
- grants the service write access only to the Pass 205 state directory;
- reloads systemd without restarting the service.

`bin/post_compile` invokes the installer automatically when executed as root. The guarded updater owns the subsequent service restart and health verification.

Overrides:

```text
HHS_SERVICE_NAME
HHS_PASS205_STATE_ROOT
HHS_PASS205_DB
HHS_PASS205_DROPIN_DIR
```

Repository tests and local development may continue to pass an explicit temporary database path. Production deployment must use the system state boundary.
