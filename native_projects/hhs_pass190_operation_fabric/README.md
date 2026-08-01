# HHS Pass 190 Unified Operation Fabric — Executable Foundation

This project implements the first validated executable nucleus of Pass 190.

## Implemented

- one process-wide `HHSAuthorityContext`
- canonical machine-readable operation registry
- exact registry-bound Hash216 operation identities
- safe HARMONICODE constructor parsing without `eval` or `exec`
- Bash-like `hhs` command lowering
- qualified Python compatibility identities
- generated OpenAPI 3.1 document
- dependency-free HTTP invoke/replay service
- capability-gated singleton mutation
- expected-state conflict protection
- idempotency across constructor, shell, Python, and HTTP surfaces
- 72-glyph Hash72 receipts, 216-glyph Hash216 topology, chain continuity, and replay
- exact Pass 189 contextual address decoding

## Validate

```sh
make validate
```

## Examples

```sh
PYTHONPATH=python python3 python/hhs_pass190.py --json hhs status
PYTHONPATH=python python3 python/hhs_pass190.py --json hhs eval 'Len([1,2,3])'
PYTHONPATH=python python3 python/hhs_pass190.py --json hhs invoke math.gcd '{"a":84,"b":30}'
python3 server/hhs_pass190_server.py --port 8190
```

The implementation is intentionally classified as a foundation slice. Full repository-wide operation hydration, SDK generation, WebSocket streaming, native ABI parity, GUI integration, and complete Python standard-library coverage remain open Pass 190 work.
