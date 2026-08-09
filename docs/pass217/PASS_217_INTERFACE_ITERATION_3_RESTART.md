# Pass 217 Interface Iteration 3 Restart

Parent checkpoint: `1f0835a8af2203ad761324861e76aebd829ca048`
Branch: `agent/pass217-interface-integration-iteration1`
Scope: read-only Service Registry and frontend diagnostics expansion.

Changes:
- add `RuntimeDiagnosticsDrawer` as an on-demand interface surface;
- read existing `/api/runtime/services` inventory without changing service dispatch;
- summarize service count, authority-gated count, and service categories;
- expose shared frame FPS/Hz/p95/p99/jank/drop metrics;
- expose observed API endpoint p95/status telemetry from the shared fetch monitor;
- keep `IntegratedRuntimeClient` and `transportState="ON_DEMAND"` unchanged.

Validation:
- strict telemetry compilation retained;
- diagnostics and canonical IDE TSX syntax transpilation passed;
- source verifier rejects service-dispatch or Pass 217 genesis/backend coupling in the new diagnostics surface.

Next: integrate application/workspace organization incrementally, using the runtime application registry rather than adding isolated standalone apps.
