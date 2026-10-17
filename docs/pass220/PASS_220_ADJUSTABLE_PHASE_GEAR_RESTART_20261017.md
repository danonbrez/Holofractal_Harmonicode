# Pass 220 — Adjustable Phase Gear: Restartable Integration Checkpoint

## Source and branch
- Base: `main` at branch creation, 2026-10-17 (resolve exact parent SHA from first commit).
- Work branch: `feature/pass220-phasegear-lean-wolfram-lane5-20261017`
- Target: `main`
- PR: #825
- Related documentation PR: #824 (including correction of `-180` to adjustable angle).

## Changes committed
- `formal/lean/HHS/Pass220/AdjustablePhaseGearCircuit.lean`
- `formal/lean/HHS.lean`
- `evidence/pass220/adjustable_phase_gear_circuit_20261017.wl`
- `native_projects/pass220/adjustable_phase_gear_candidate.hpp`
- `native_projects/pass220/test_adjustable_phase_gear.cpp`
- This restart record.

## Semantics frozen
- Adjustable gear angle `theta`; `-180` is only the reference setting.
- Ordered 4x4 M16 / D' permutation; no commutative scalar substitution.
- HNAN zero quantization bypass: gain 1, unchanged phase, zero writes.
- Lane 5 remains candidate-only. Canonical VM81 admission and Hash72/Hash216 minting are not delegated to a new service.
- Preserve exact RNA C ABI, fixed-address provenance, signed environmental admission and current Hash216 serialization and lineage.

## Validation completed
- Independent exact SymPy multiplication confirmed the corrected 4x4 T_rat and T_cov values supplied in the course.
- Static Lean module and C++ candidate/regression source committed; no assertion that the pinned Lean or Wolfram executables were run.
- GitHub accepted five code file commits and imported Lean module into root library.

## Validation remaining
1. `lake build HHS` using repository-pinned toolchain; repair compilation failures.
2. `wolframscript -file evidence/pass220/adjustable_phase_gear_circuit_20261017.wl`; require PASS and persist stdout as evidence.
3. `g++ -std=c++17 -Wall -Wextra -pedantic -I native_projects/pass220 native_projects/pass220/test_adjustable_phase_gear.cpp -o /tmp/hhs_phasegear_test && /tmp/hhs_phasegear_test`.
4. Examine existing Pass219 `CoreHolographicRNACellWall` and Pass220 Lane 5 API, then add typed phase-gear candidate routing through them; do not infer the ABI.
5. Route admitted candidate through signed environmental VM81 authorization and existing Hash72/Hash216 three-state receipts. Test first, middle, and last leaf SHA-256 vectors and two-pass Genesis replay.
6. Test multiple angles, angle orientation reversal, all 16 ordered register slots, 11 n/Q polynomial cells, failed constraints, and zero denominator HNAN bypass. Verify angle-specific geometry and identical canonical results on replay.
7. Dependency-scoped integration, CI evidence, merge/verify main; production deployment not in this PR.

## Next action
Implement the cell-wall integration using its existing typed C ABI after inspecting the current authoritative headers and tests. Preserve the candidate service as a reusable compile-time nucleus, not a competing cryptographic mint.

## 2026-10-17 correction — single Lane 5 / VM81 / BigInt / Hash216 authority

The adjustable phase gear is a NEW CONSTRUCTOR / RELATION in the SAME already-existing Lane 5 5184-position VM81 BigInt-serialization Hash216 knowledge graph. It must not launch a second graph, service clock, serialization authority, stand-alone hash database, or secondary VM81. All 16 circuit cells resolve through inherited 5184 addresses; angle is typed provenance for the same graph, not permission to change canonical grid topology. Existing Lane 5 search can hydrate or optimize validated graph records; exact CPU replay, RNA C++ cell wall and signed-environment VM81 authority remain compulsory prior to canonical mutation or lineage.

The C++ candidate header now includes an explicit graph projection with 16 fixed ordered addresses, exact decimal BigInt digits, and 216-symbol parent lineage, rejecting invalid ranges and malformed numeric encoding. This is candidate metadata only, not a substitution for the authoritative fixed-width VM81 BigInt serializer. Exact inherited Hash216 alphabet validation, parent lineage authenticity, position-to-frame mapping, admission service wiring and replay remain outstanding. A 216-character input by itself is not an authenticated receipt.

Updated next action: connect this candidate projection to the existing Pass219 RNA VM5184 C ABI, the existing 5184 graph binding/BigInt serializer, and native Hash216 receipt path. No competing `hash216()` implementation may be introduced. Add negative tests for genuine admission, authenticated lineage, 16-cell address ownership, angle-specific graph relations, and rollback/no-write on every rejection.

## 2026-10-17 full circuit correction — outer computational vectors

The authoritative new construction is FOUR complete ordered 4×4 tensors assembled into ONE 8×8 64-cell logical circuit: T1 top-left, T2 top-right, T4 bottom-left, T3 bottom-right. All 64 cells must retain their own BigInt serialization positions, tensor-block/local address, and inherited 5184-position VM81 graph address. No zero padding or disconnected per-block service is permitted.

The outer parameters are COMPUTATIONAL PHASE VECTORS rather than scalar decoration. An 8-slot vector with four choices per slot has `4^8 = 65536` potential configurations; this is a configuration-space count, NOT a claim that `4^8 = 64`. The 64 circuit cells are the spatial 8×8 carrier. Neither the outer angle nor the reference -180 is globally fixed. Phase-gate geometry must be hydrated by Lane 5 and returned through existing provenance and admission.

Implementation: `FullCircuitCandidate`, `OuterPhaseVectors`, `Circuit8`, `compose8`, `project_full_circuit` added to existing candidate header. This maps 64 cells to inherited 5184 indices with exact decimal BigInt text, and retains read-only parent Hash216. It does not replace the authoritative VM81 serializer; specific native angle-to-geometry evaluation, 4-choice phase encoding, 64-cell address binding to the RNA ABI, and closing proof of the full circuit remain validation obligations.

## 2026-10-17 source-lock: revised complete List tensor

Source-locked contract: `contracts/pass220/PASS_220_LANE5_FOUR_COMPONENT_PHASE_GEAR_CIRCUIT_V2.md` (full exact user expression, no elisions).
The revision changes the source of the spin closure and the full 11-polynomial denominator, and explicitly retains gate syntax `==`. This takes precedence over earlier candidate-only simplified polynomial expressions. Native code in this PR still encodes structural block placement, not full evaluated closure of this V2 expression. Do not call the V2 implementation done until source AST, ordered BigInt serialization, Lean theorem, Wolfram exact witness, RNA C++ wall and signed VM81 Hash216 receipts agree.

Next targeted action: add a typed parser/constructor for V2's exact four outer elements; validate the eleven-numerator denominator and 16 bipolar registers, then integrate with the existing 5184 knowledge graph and canonical admission ABI. No host floating-point or scalar replacement for rank-1 division.
