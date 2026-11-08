# Pass 220 Q81 — Native C++ HNAN phase ingress/egress checkpoint (2026-11-07)

## Added files
- `hhs_runtime/include/hhs_pass220_q81_hnan_native_phase_candidate_v1.h`
- `hhs_runtime/cpp/hhs_pass220_q81_hnan_native_phase_candidate_v1.cpp`
- `tests/native/test_hhs_pass220_q81_hnan_phase_code_v1.cpp`
- Focused workflow `.github/workflows/pass220-q81-reversible-hnan-phase-projection.yml` updated to compile the C++ source and execute the four-case phase-code test.

## Contract
- Local phase bijection: Delta=0 ↔ (0,1)/(1,0), Delta=1 ↔ (-1,+1)/(+1,-1). Orientation is derived from ordered pairs.
- C++ candidate function first validates every ordered pair without modifying output, then calls `hhs_exact_pass220_i028_lane5_rna_g3_route`. This inherits the Pass219 C++ RNA cell wall and I028 Lane5/Holo4 constructor mediation. Candidate is rejected if mediation, no-bypass, unchanged frame, or authority evidence differs from the documented I086 pattern.
- Output remains candidate-only. `source_phase_native_certified=0`, `signed_vm81_admission_invoked=0`; no Hash72 mint, Hash216 mint, VM81 write or external egress.
- Exact source frame, predecessor and constructor witness are required inputs. Binary phase bits do NOT represent full native tensor or 5184-bit raw frame.

## Verification boundary
Earlier PR head `20a1c80875ac2802df405358a43026cdf799da1b` has Q81 workflow and source-guard success, but no evidence for the new C++ code.
New native workflow head `7dc5c2e78c15baaa16b1ce458a927cb0c45ac21d`: execution must be checked before labeling native compilation or four-case run PASS.
The new C++ function is not yet exercised end-to-end with a real accepted I028 predecessor/constructor fixture; the runtime test checks the pure four-case code only. The complete course-wide symbolic constraint solver has not yet generated the phase-pair source. Neither error should be masked by CI bypass, forced HNAN scalar zero, or fake admission receipts.

## Next
1. Examine focused C++ compile/test workflow logs and repair actual source defects if any.
2. Run the new full I028-mediated function with real predecessor, UQCEL, VM81 frame and constructor witness fixtures recovered from native test infrastructure.
3. Attach native typed phase-source certificates and confirm exact return-path/source provenance; require VM81 signed admission and replay independently.
