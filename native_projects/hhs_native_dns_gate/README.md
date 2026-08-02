# HHS Native DNS Gate

The gate resolves the Pass 189 / Pass 190 `8190` collision without renumbering either canonical service port.

```text
pass189-calibration.hhs.internal → 127.189.0.2:8190
pass190-runtime.hhs.internal     → 127.190.0.1:8190
```

Linux treats the complete `127.0.0.0/8` range as loopback. The services therefore retain port `8190` while binding different host-local addresses. The authoritative `hhs.internal` zone publishes A, PTR, SRV, NS, SOA, and TXT records through UDP and TCP DNS on `127.0.0.55:53`.

`hhs-dns-gate-resolved.service` assigns `~hhs.internal` as a route-only domain on the loopback link through `systemd-resolved`. Public DNS is not forwarded through the gate.

## Validate

```bash
make validate
```

## Install

```bash
sudo REPO_ROOT=/opt/holofractal-harmonicode deploy/install.sh
```

## Service identities

| Service | Address | Port |
|---|---:|---:|
| Pass 189 Iteration 1 | `pass189-runtime.hhs.internal` / `127.189.0.1` | `8189` |
| Pass 189 Iteration 2 | `pass189-calibration.hhs.internal` / `127.189.0.2` | `8190` |
| Pass 189 Iteration 3 | `pass189-adapter.hhs.internal` / `127.189.0.3` | `8191` |
| Pass 189 Iteration 4 | `pass189-provenance.hhs.internal` / `127.189.0.4` | `8192` |
| Pass 190 API | `pass190-runtime.hhs.internal` / `127.190.0.1` | `8190` |
| Pass 196 IDE | `pass196-ide.hhs.internal` / `127.196.0.1` | `8080` |

The gate is host-local only. It does not publish the internal zone to the public Internet and does not authorize hardware dispatch.

## systemd integration

The installer adds persistent drop-ins for the Pass 189, Pass 190, and Pass 196 units. The drop-ins make the DNS gate a required predecessor and replace only each service bind address. Original project unit files remain intact, so each project can continue to own its command, database, and hardening policy.

The gate installer is idempotent. Re-running a project installer does not remove `/etc/systemd/system/<unit>.d/10-hhs-dns-gate.conf`.
