# Pass 219 Lane 5 mandatory optimization integration restart — 2026-09-17

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- merge target: `main`
- base main at task start: `63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- working branch: `pass219/saturation-deadline-warm-cache-benchmark-v3`
- predecessor restart checkpoint: `06dfcbbb93c80d1cc9ba9dbb080f4e7886ce298f`
- PR: `#492` (draft while implementation is in progress)

## Defect classification

This task treats proven optimizations as mandatory Lane 5 execution capabilities. A proven optimization may remain candidate-only or noncanonical where its existing contract requires that, but it may not be silently unavailable to the Lane 5 latency search / composition path merely because its implementation is linked only into the aggregate ABI or exercised only by a dedicated benchmark.

Verified integration gaps at task start:

1. `hhs_runtime/hhs_pass219_nonagentic_allegorical_warm_hydration_v1.py::default_lane5_search()` binds directly to the older Lane 5 `1.37` Hash216 GPU phase-interlace optimizer and therefore does not expose the later composition/reuse stack by default.
2. `hhs_exact_pass219_h36_branch_ref_resolve()` is implemented, tested, and benchmarked, but repository search does not show a production consumer outside its dedicated test/benchmark surfaces.
3. `hhs_exact_pass219_h36_global_latency_select()` still invokes fresh `hhs_exact_pass219_h36_stack_select()` instead of a mandatory proven-cache/reference-aware selection surface.
4. The repository already contains later Lane 5 composition/search capabilities (`1.38` jump store, `1.39` persistent composition memory, `1.40` recursive graph, `1.41` superedge hierarchy, `1.42` automatic routing, `1.43` capability self-model, `1.44` reverse discovery, `1.45` fractal-qudit admission, `1.46` direct-witness routing, `1.48` unbounded-workload scaling), but the older default search binding does not make that accumulated optimization lineage available as one default composition/latency surface.
5. Pass 219 RML19 provides exact route/composition certificate reuse, and Pass 165 provides content-addressed ingestion reuse; these must remain separately typed optimizations rather than being silently collapsed into a raw recomputation path.

## Implementation objective

Implement a repository-visible mandatory optimization dispatcher for Lane 5 that:

- preserves the existing exact/candidate-only authority boundaries;
- exposes the proven optimization lineage to default latency search and composition;
- prefers direct validated cache/reference/jump/superedge reuse when exact identity permits it;
- falls back to the inherited exact fresh path only when no validated reuse applies;
- never treats a missing optional physical accelerator as authority failure when a validated CPU-reference implementation exists;
- reports exactly which optimization surfaces were available, selected, bypassed as inapplicable, or failed closed;
- prevents regression back to a `1.37`-only default binding;
- adds tests that fail if a proven mandatory optimization becomes unreachable from the default Lane 5 search/composition surface.

## Planned dependency-scoped validation

- Python compile for modified/new Lane 5 dispatcher and warm-hydration surfaces;
- existing 1.37 through 1.48 focused tests that are dependency-relevant;
- RML19 route/composition acceleration tests;
- H36 stack-cache / branch-reference / global-latency native tests;
- aggregate exact ABI build;
- mandatory-default integration contract checks;
- targeted negative tests for cache/reference tamper, authority escalation, stale identity, and optimization bypass;
- saturation benchmark retained as observational evidence only.

## Restartability

If interrupted, continue from this file and the current branch head. Do not discard the already-frozen benchmark work. Repair forward only impacted dependency surfaces.