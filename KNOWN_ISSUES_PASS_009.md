# KNOWN ISSUES PASS 009

## Remaining Containment Targets

- Audit graph projection, replay topology, snapshot codec, transport protocol, prediction, sandbox, and distributed runtime modules for local `compute_hash72()` implementations and direct packet emission.
- Adapt GUI websocket consumers to display/ignore compact `io_egress_record` projections safely.
- Add static checks that fail CI when new API/websocket/stream write surfaces do not use IO/dataflow guard wrappers.
- C runtime still builds with non-blocking warnings in native demo/runtime code.
- GUI TypeScript verification still requires installing Node dependencies outside the ZIP.
