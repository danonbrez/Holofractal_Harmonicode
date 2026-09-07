# Pass 219 — Core Holographic Four-Lane Phase 2 Restart

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ b6c1980a014fc050c8ae562b92c3afe03e38b094`
- Branch: `agent/pass219-core-dynamic-circuit-20260907`
- Phase-2 starting head: `7d85806ca8ccaecd1f6258a47d0862f83217469f`
- Branch relation to current main at start: `11 ahead / 0 behind`
- Intended target: experimental branch only; no PR or merge authorized
- Frozen predecessor experiment: run `34127851354` at `56181b6facd306657d6c85671e11442438197943` — SUCCESS

## Phase-2 scope

Extend the already validated 542-byte verbatim core constraint circuit into the existing Pass 219 runtime organization rather than introducing a parallel authority system.

The requested circuit is to operate as an exact local-to-global manifold with:

1. 81 VM81 cells arranged as a 9x9 Sudoku knowledge graph;
2. nested 3x3 Lo Shu tensor coordinates at both local-cell-bank and macro-bank scales;
3. per-cell exact integer parameter weights and per-bank weights;
4. x/y/z/w/xy/yx/zw/wz ordered reciprocal phase-pair coordinates modulo 72;
5. bounded trinary activations and bounded online learning;
6. explicit 20-peer Sudoku adjacency per cell (row, column, and 3x3 bank, de-duplicated);
7. Hash216 transition identity as authenticated routing provenance;
8. direct composition with the existing Pass 219 C++ `hhs::rna::OrthogonalGlyphMembrane` cell wall;
9. VM81 exact ABI carriage without minting new canonical authority;
10. four hydration-routing decisions using the already-defined integrated lanes:
   - `RAW5184_X86_64`
   - `VM81_HASH72_HASH216`
   - `OCTONION_DUAL_STEREO_TERNARY`
   - `HARMONIC36_144X36`

The inherited Hash216 three-part lineage (`previous`, `change`, `receipt`) remains the lineage input and is not redefined as the four hydration outputs.

## Authority boundary

Phase 2 remains candidate-only. It SHALL NOT independently acquire:

- canonical VM81 mutation authority;
- Hash72 mint/commit authority;
- Hash216 persistence/commit authority;
- canonical persistence authority;
- floating-point authority.

The existing RNA lowering / singleton VM81 admission boundary remains the only path by which a later separately-authorized candidate could become canonical.

## Planned files

- `hhs_runtime/include/hhs_pass219_core_holographic_four_lane_1_24.h`
- `hhs_runtime/c/hhs_pass219_core_holographic_four_lane_1_24.inc`
- `hhs_runtime/include/hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp`
- additive includes in `hhs_runtime/include/hhs_runtime_exact_abi.h`
- additive includes in `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `tests/pass219/test_pass219_core_holographic_four_lane_1_24.c`
- `tests/pass219/test_pass219_core_holographic_rna_cell_wall_1_24.cpp`
- `benchmarks/pass219/core_holographic_four_lane_benchmark.cpp`
- update `.github/workflows/pass219-core-dynamic-circuit-experiment.yml`
- update this restart record with exact run/receipt evidence

## Validation contract

Dependency-scoped validation must prove at minimum:

- `make c-abi` succeeds and exports the Phase-2 C ABI;
- predecessor dynamic-circuit tests remain green;
- all 81 cells are present and each has exactly 20 unique Sudoku peers;
- 9 local/macro Lo Shu banks are preserved;
- reciprocal phase pairs close modulo 72 for all 81 cells;
- exact frame feature extraction still requires one shared 81-word pass;
- four-lane scores are deterministic and candidate-only;
- sequential C four-lane scoring equals the C++ cell-wall parallel scoring result exactly;
- the Hash216 input identity is preserved in the routing receipt;
- no route gains VM81/Hash72/Hash216/persistence/floating-point authority;
- bounded synthetic local-cell learning improves a controlled four-lane calibration task;
- wall timing is observational only and is never an authority or acceptance threshold.

## Restart action

Implement the additive Phase-2 ABI and C++ cell-wall adapter, extend the branch-scoped workflow, run the repository-native experiment, repair forward on any failure, then seal exact measurements here. Do not open or merge a PR without separate authorization.
