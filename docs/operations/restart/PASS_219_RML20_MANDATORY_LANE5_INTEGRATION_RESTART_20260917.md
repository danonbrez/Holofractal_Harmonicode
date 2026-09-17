# Pass 219 RML20 mandatory Lane 5 integration restart — 2026-09-17

## Objective

Make the proven RML20 RNA/VM5184 transport capability reachable from the production Lane 5 latency-search/composition agent. Proven compatible capability surfaces must not remain branch-only, benchmark-only, test-only, or otherwise unreachable from Lane 5.

## Base / branch

- integration branch: `pass219/saturation-deadline-warm-cache-benchmark-v3`
- pre-task checkpoint: `c05d9d014cd65a96d5d42a63b833c8d3bc86c661`
- RML20 source branch inspected: `agent/pass219-rml20-rna-vm5184-cell-wall-20260913`
- RML20 source head: `3c0d3e58faa2fc9e75faff65372c1db475d1d40e`
- RML20 source branch was 8 commits ahead and 563 commits behind this integration branch when compared; source files were therefore imported as proven blobs and build/dispatch wiring was rebased rather than merging the stale branch wholesale.

## Implemented

1. Imported the proven RML20 implementation blobs unchanged:
   - `hhs_runtime/cpp/hhs_pass219_rml20_rna_vm5184_bridge_1_34.cpp`
   - `hhs_runtime/include/hhs_pass219_rml20_rna_vm5184_bridge_1_34.h`
   - `hhs_runtime/pass219/rml20_rna_vm5184_cell_wall_bridge.py`
   - `tests/pass219/test_pass219_rml20_rna_vm5184_bridge_1_34.c`
   - `tests/pass219/test_pass219_rml20_rna_vm5184_cell_wall_bridge.py`
2. Rebased the RML20 object into the current exact ABI through `GNUmakefile`.
3. Extended `hhs_runtime/pass219/lane5_mandatory_optimization_dispatcher.py` so RML20 is a mandatory typed capability.
4. Added production-agent method `route_rml20_candidate(...)`.
5. Preserved RML20 authority constraints: candidate-only, exact-integer-only, no canonical VM81 mutation, no Hash72 mint, no Hash216 persistence, no canonical persistence, no floating-point authority.
6. Added `tests/pass219/test_lane5_rml20_mandatory_integration.py` to prove status visibility, production-agent callability, and fail-closed malformed-carrier behavior.
7. Added `.github/workflows/pass219-rml20-rna-vm5184-cell-wall-1-34.yml` on the active branch.

## Commits

- `039e7cda027f0911acc3fb79fc1f9d95bc33dc7e` — import proven RML20 runtime/tests
- `610edf4f8be1067c1b0cfa0c9d31ca95f53ba431` — link RML20 into current exact ABI
- `dd59d346baaaf958ecd5fcc8c6086359fcdfad3d` — expose RML20 through mandatory Lane 5 dispatcher
- `ec5ab538e16474156cd594f35deee2fccc3c3c80` — require RML20 production-agent reachability
- `ca9f17150608a73e9d89fd6b1945cc32be13b76c` — dedicated RML20 validation workflow

## Validation state

- dedicated run: `35274154949`
- job: `105380556690`
- workflow: `Pass 219 RML20 RNA VM5184 Cell Wall 1.34`
- state at checkpoint creation: queued; no failure evidence yet
- queued CI is not a blocker under the repository forward-progress policy.

The workflow builds the cumulative ABI, verifies RML20 public exports, verifies the canonical mutation exports remain hidden while signed environmental admission remains public, runs the native RML20 positive/negative tests, reruns inherited RNA/VM5184 regression, proves frozen RML17/native parity, and exercises RML20 through the production Lane 5 agent.

## Later-iteration scan

Repository branch search for `rml2` found the RML20 branch above. A repository commit search for `RML21` returned no matching commits, and no `rml21` branch was found in the current scan. Do not infer that no future or differently named later capability exists; repeat repository-wide lineage discovery when new iterations are introduced.

## Remaining / next action

1. Inspect run `35274154949` when it produces executable evidence.
2. Repair-forward only the concrete failing dependency if the run fails.
3. Extend the same mandatory registry/typed-dispatch rule to any subsequently discovered RML21+ or differently named proven compatible surfaces.
4. When focused validation is green, reconcile PR #492 metadata/status, merge when permitted, and verify `main`.
