# Pass 189 Iteration 3

Iteration 3 adds a fail-closed device-adapter membrane above Iteration 2 physical candidates.

## Validate

```bash
make validate
```

## Run

```bash
HHS189_I3_DB=/tmp/pass189-i3.sqlite3 HHS189_I3_STATE=/tmp/pass189-i3-state python3 server/hhs_pass189_iteration3_server.py --host 127.0.0.1 --port 8191
```

Open `/pass189/i3/`.

Only `LOOPBACK` and sandboxed `FILE_SINK` adapters execute. Their traces are software evidence, never hardware measurements. GPIO, serial, USB, network-device, and actuator dispatch are not implemented.
