# DigitalOcean Runtime OS live-source and permission repair — 2026-09-27

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main at branch creation: `e8d6b5fab35b77a21c48ba5b90305de314186cf6`
- Repair branch: `agent/runtime-os-live-source-permission-repair-20260927`
- Merge target: `main`
- Main advanced after branch creation through `6fdd761c3bb392d1c2d49f41e925fad34c712653` with generated Hash216 repository-index refreshes. Those generated main-only documentation commits are outside the repair surface and must be integrated by PR merge before exact-main deployment.
- Production surface observed: Runtime OS served from the DigitalOcean host shown in the operator screenshots.

## Observed production symptoms

1. Runtime authority HTTP projection was reachable and all four browser WebSocket channels connected, but Runtime, Replay, Graph, and Transport showed `NO_LIVE_KERNEL_SOURCE`.
2. The Runtime surface reported the background task inactive.
3. Visual Program service discovery failed with `[Errno 13] Permission denied: 'demo_reports'`.
4. Pass 218 I14 showed an empty operator registry with threshold 2 and therefore remained fail-closed. This repair does not populate or bypass that registry.

## Root-cause trace

### Live source

The production service intentionally sets:

```text
HHS_COGNITION_AUTO_TICK=0
```

This is a valid production constraint: no continuous background mutation is required merely to keep the browser projection alive. However, `LiveFastAPIRuntimeWorkflow.start()` previously emitted no kernel event when `auto_start=False`. A browser attaching later therefore had no receipt-backed event to classify as a live kernel source.

The production authority projection also reads `workflow["authority_ready"]`, but the workflow status did not previously expose that field.

A startup-only event is not sufficient by itself because it is emitted before browser clients normally connect. The WebSocket manager therefore also needs a projection-only late-client path that sends the most recent committed event without advancing the VM or minting a new receipt.

### `demo_reports` permission fault

`GET /api/runtime/services` traverses the Pass 217 cumulative route composer. Its inherited Pass 044 semantic composition cache defaulted to:

```text
demo_reports/hhs_live_semantic_composition_cache_pass217.json
```

The production unit runs from `/opt/hhs/app` with `ProtectSystem=full` and only `/var/lib/hhs` admitted through `ReadWritePaths`. The first service-discovery request could therefore attempt a write under the read-only repository and raise the observed `Permission denied: 'demo_reports'`.

The canonical production runtime state directory is already `/var/lib/hhs/data/runtime`; the cache is now bound there.

## Implemented repair

### `hhs_backend/runtime/live_fastapi_workflow_v1.py`

- Prime exactly one canonical kernel emission during `start()`, including when continuous auto-tick is disabled.
- Preserve `HHS_COGNITION_AUTO_TICK=0`; no continuous background mutation was introduced.
- Publish explicit `authority_ready` and `startup_prime_complete` status.
- Fail startup closed if the prime itself fails.

### `hhs_backend/runtime/runtime_ws.py`

- Retain the last canonical `HHSRuntimeEventEnvelope` in memory.
- On each late Runtime/Replay/Graph/Transport WebSocket connection, project that existing committed event through the channel-specific projection contract.
- The late-client path does **not** call the emulator, advance a tick, append a new runtime receipt, or grant browser authority.

### `hhs_runtime/hhs_inherited_execution_stage_bridge_v1.py`

Cache resolution is now:

1. explicit `HHS_LIVE_SEMANTIC_COMPOSITION_CACHE_PATH`;
2. otherwise `$HHS_RUNTIME_OUTPUT_DIR/hhs_live_semantic_composition_cache_pass217.json`;
3. only outside a configured runtime output boundary, retain the historical `demo_reports/...` development fallback.

### `deploy/digitalocean/hhs-pass196-integrated-environment.service`

Added:

```text
HHS_LIVE_SEMANTIC_COMPOSITION_CACHE_PATH=/var/lib/hhs/data/runtime/hhs_live_semantic_composition_cache_pass217.json
```

No systemd filesystem hardening was relaxed. `ProtectSystem=full`, `ReadWritePaths=/var/lib/hhs`, and `HHS_COGNITION_AUTO_TICK=0` remain intact.

## Tests added/updated

- `tests/test_hhs_live_fastapi_runtime_pass045_v1.py`
  - startup with `auto_start=False` must still produce one canonical receipt-backed emission;
  - workflow must report authority-ready after that prime;
  - late WebSocket clients on all four channels must receive the latest committed canonical event without a new tick.
- `tests/test_hhs_inherited_execution_stage_bridge_v1.py`
  - production-style `HHS_RUNTIME_OUTPUT_DIR` must redirect the default live semantic cache outside `demo_reports`.
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
  - the production systemd unit must retain the read-only repository boundary while placing the semantic cache under the writable runtime-state root.
- `.github/workflows/hhs-agi-runtime-wiring.yml`
  - changes to the live workflow/WebSocket transport trigger the runtime-wiring gate;
  - the gate executes the complete Pass 045 live-runtime test file, including late-client projection coverage.

## Commit chain on repair branch

- `ef144b71a7470aa4ad3d1e66fb7b7429998eb354` — startup kernel projection prime
- `2d7c3c6f33bb50f125957039df28cfe63a979ee4` — runtime-state semantic cache fallback
- `d94c322428c6b0222a8fbb6576777a152f9c3c77` — production semantic-cache environment binding
- `ee81567d546a51ac40035f459d8f7197511ece5d` — startup live-source regression test
- `e178b60f7bfbf3de25f298988e0e2cca509e3bd2` — late-client canonical WebSocket projection
- `bb7bfc10c5f7967d1c82d763203417818e25f0e4` — late-client projection regression test
- `faafb9e8128e17e5b8c7af8765c482828dad9e7a` — semantic-cache runtime-output test
- `7628f72c6e134f3107d81b485a2ae07320f23095` — production systemd cache-boundary test
- `3fdbc7ee38ae38295ef113972f228c1164a82745` — preserve inherited Pass 045 CI selector compatibility
- `fff329a431ef5516569ebd75bba61950a4a11d3b` — bind replay snapshot to the current kernel source
- `0d3804559d8460c8365295fa2689e211724e770d` — replay snapshot regression coverage
- `1c3e50831e40ca4dc14dd2fce6ea433145788700` — run the complete Pass 045 live-projection test file in AGI runtime CI

## Dependency-scoped validation

Run:

```bash
python3 -m py_compile \
  hhs_backend/runtime/live_fastapi_workflow_v1.py \
  hhs_backend/runtime/runtime_ws.py \
  hhs_runtime/hhs_inherited_execution_stage_bridge_v1.py

python3 -m pytest -q \
  tests/test_hhs_live_fastapi_runtime_pass045_v1.py \
  tests/test_hhs_inherited_execution_stage_bridge_v1.py \
  tests/test_hhs_guarded_auto_update_contract_v1.py
```

Then run the existing DigitalOcean candidate gate through the PR/exact-main deployment workflow.

## Production acceptance after merge

After exact-main promotion and one ordinary `systemctl restart hhs`:

1. `GET /api/runtime/authority/status` reports the production runtime authority online with nonempty receipt and runtime-state Hash72 values.
2. A newly opened Runtime tab reaches `LIVE_KERNEL_CONNECTED` on Runtime, Replay, Graph, and Transport without requiring the user to advance a tick first.
3. `GET /api/runtime/services` succeeds and Visual Program no longer surfaces the `demo_reports` permission error.
4. The live semantic composition cache exists only in the admitted runtime-state boundary under `/var/lib/hhs/data/runtime` unless an explicit alternate environment path is configured.
5. Pass 218 I14 remains fail-closed while its registry is empty; this repair does not create preparers, approvers, executors, quorum, certificates, snapshots, or recovery-rehearsal evidence.
6. Browser authority remains projection/request only; canonical runtime mutation still belongs to the backend/kernel authority chain.

## Remaining actions

1. Execute dependency-scoped CI for this branch.
2. Resolve any failures repair-forward.
3. Merge through the PR with current main included.
4. Verify the resulting exact main SHA.
5. Observe the exact-main DigitalOcean deployment and verify the six production acceptance conditions above.
