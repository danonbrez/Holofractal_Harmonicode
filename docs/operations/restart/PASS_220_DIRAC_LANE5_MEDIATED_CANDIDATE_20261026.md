# Pass 220 — Eight-sector Dirac candidate routed through I028 mediation

Date: 2026-10-26
Branch: `pass220/standalone-adaptive-device-resolution-20261023`; merge target: `main`.
Base: previous head `3421af49ad3d358ffaae95aef92dab0985e7e05f` (CI and zero-spinor fix).
Changes:
- `hhs_runtime/include/hhs_pass220_dirac_hnan_lane5_bridge_v1.h`: new bounded C ABI (commit `10c4467266afc14c07215eae1ef663bb4bdacadd`).
- `hhs_runtime/cpp/hhs_pass220_dirac_hnan_lane5_bridge_v1.cpp`: routes checked exact Gaussian-integer sector reference spinors through **existing** `hhs_exact_pass220_i028_lane5_rna_g3_route` (commit `dbde04857612a2e9a0d41b31ad794ba9b1ac61ce`).
- Source physics integrator and color controls unchanged.

## Current bounded result
- Eight ordered source addresses and exact nonzero static-z reference projector checks.
- Signed integer minimum rejected before sign-changing K action.
- Valid existing UQCEL input/VM81/predecessor/Holo4 Lane5 witness required.
- I028 candidate must prove prior RNA cell wall routing, Holo4 equivalence, zero-bypass and byte-identical VM81 frame.
- Output explicitly candidate-only, no native admission and no Hash72 mint. Boolean mapping fields are diagnostic, not authoritative mapping evidence.
- Failure returns before output assignment.

## Unverified
- The C++ linkage, header include path integration, compilation, and dependency-scoped tests **have not executed**.
- The module is not yet added to the authoritative native build/exported service index. No live runtime route or browser update is proven.
- Dynamic outward normals, eight real particle-group provenance bindings, true constrained evolution, center HNAN global closure and hydrogen spectral acceptance remain unverified.

## Next action
1. Wire this translation unit to the *existing* pass220/native build target and service index, without creating a duplicate runtime.
2. Execute native link+ABI tests with positive/negative eight-sector inputs (including invalid predecessor, wrong addresses, zero spinor, integer minimum, frame immutability, no-output-on-failure); check compiler warnings.
3. Prove actual particle-group-to-HNAN correspondence using source identifiers and native provenance; reject fabricated mappings.
4. Add dynamic unit-normal spinor projector and global conservation/flux witnesses before canonical admission.
5. Replay VM81/Hash72/Hash216 transitions, bind accepted changes to the original particle simulation, then browser/production validation and verify merged main.
