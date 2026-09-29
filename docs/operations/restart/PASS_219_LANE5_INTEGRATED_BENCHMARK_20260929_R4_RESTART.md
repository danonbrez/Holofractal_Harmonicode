# Pass 219 Lane 5 Integrated Benchmark R4 — Restart

Status: **CURRENT-MAIN REPAIR BASE — BENCHMARK REVALIDATION PENDING**

## Identity

- Authoritative main observed before R4: `9cc8f89620183a90f9e269968ef75ee7476adeb8`
- Main meaning: PR #656 native Lane 5 provider policy and PR #658 I062 native pytest are merged; later repository work including PR #659 is also present.
- Provider repair prerequisite head: `85bd6b5430bef9e03e9a2e600aa9d3250938d5f9`
- Provider repair PR: `#662`
- Branch: `bench/lane5-integrated-benchmark-20260929-r4`
- Merge target: `main`
- R4 harness carry-forward commit: `6644979fdb45f6afe6d61e067c4a95e8b89d5da1`
- R4 workflow commit: `b70fc6b970b742ffff54dc7feb97c9a8e9a2336d`

## Why R4

R3 was a valid repair-forward campaign but its branch later diverged from current
main by 28 commits. Final benchmark evidence therefore must not be published
from the R3 source tree.

R4 is cut from current main plus only the attributable provider repair required
by the latest R3 failure.

## Frozen R3 evidence

Latest diagnostic R3 run:

- run: `36612949506`
- job: `109558712026`
- exact ABI build: PASS
- exact-head repository-index regeneration: PASS
- generated R3 diagnostic index:
  - tracked files: 8,886
  - dependency edges: 73,622
  - Lane 5 capability nodes: 2,085
  - constructors: 4,310
  - knowledge edges: 13,395
- scoped native-I062 regression gate: 26 PASS / 4 ERROR

All four errors came from `tests/test_hhs_service_registry_v1.py` and had the
same cause:

```text
ModuleNotFoundError: No module named 'fastapi'
```

Import frontier:

```text
make_default_service_registry
 -> live_fastapi_workflow_v1
 -> live_cognition_runtime_v1
 -> distributed_consensus_runtime
 -> distributed_runtime_node_v1
 -> runtime_orchestrator
 -> hhs_backend.websocket.runtime_stream_manager
 -> from fastapi import WebSocket
```

No performance timing beyond the index-regeneration frontier from this failed
run is accepted as final campaign evidence.

## Current-main provider repair inherited by R4

PR #662 / repair head `85bd6b5430bef9e03e9a2e600aa9d3250938d5f9` contains only the attributable
provider boundary repairs:

1. `hhs_backend/server.py`
   - replaces the literal `\\n` token between provider declarations with a
     real source newline;
2. `hhs_backend/websocket/runtime_stream_manager.py`
   - resolves `WebSocket` through
     `hhs_backend.runtime.hhs_fastapi_provider_v1`;
3. `hhs_runtime/runtime_ws.py`
   - resolves `WebSocket` and `WebSocketDisconnect` through the same
     native-first provider membrane;
4. `tests/pass220/test_hhs_native_fastapi_default_provider_v1.py`
   - blocks all `fastapi*` imports in a subprocess and proves both WebSocket
     runtime paths resolve native compatibility classes.

No external FastAPI dependency is restored.

## R4 campaign

R4 preserves the R3 integrated harness so timing remains directly comparable.
It additionally runs the native FastAPI provider regression in the I062-native
correctness gate.

The workflow:

1. verifies ancestry from current main and the provider repair head;
2. installs bounded build dependencies, NumPy, and cryptography only;
3. does **not** install upstream pytest or FastAPI;
4. compiles the benchmark harness;
5. builds the cumulative exact ABI;
6. regenerates the repository Hash216/Lane 5 index at exact R4 HEAD;
7. requires generated graph/knowledge/database source identity == exact HEAD;
8. runs scoped semantic/index/service-registry/provider regressions through the
   I062 native pytest provider;
9. benchmarks the integrated repository index, service registry, WordNet/I051,
   I060 Lean identity, Lane 5 1.75, provider policy, and I062 native pytest;
10. runs HNAN, one-million-candidate native scaling, Q-info normalization,
    real-world repository/ledger workloads, circular-attractor exact reduction,
    Pass 214 compound validation, full Pass 212 hydration check, and raw5184
    audio;
11. seals exactness/replay/negative-control and observational timing evidence;
12. uploads one immutable campaign artifact.

## Authority

- timing authority: observational only;
- no benchmark result authorizes semantic weakening;
- no external compatibility provider gains VM81 mutation authority;
- no benchmark path gains Hash72 commit or Hash216 persistence authority;
- GPU/candidate paths remain candidate-only;
- exact parity/replay and negative controls remain mandatory.

## Next action

Use the newest `Pass 219 Lane 5 Integrated Benchmark 2026-09-29 R4` run.

If failed:
- repair only the first attributable frontier;
- preserve completed exact/index evidence;
- do not install external FastAPI or restore upstream pytest as a bypass.

If green:
- freeze the artifact;
- extract current service/index/native-provider/I062/HNAN/native-stream/
  real-world/circular/Pass214/Pass212/raw5184 metrics;
- compare observational timing against historical anchors;
- merge the runtime repair and benchmark evidence as appropriate;
- verify final main and record the authoritative benchmark closure.
