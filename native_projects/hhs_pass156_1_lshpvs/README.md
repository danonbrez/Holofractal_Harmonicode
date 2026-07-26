# HHS Pass 156.1 — LSHPVS Native Implementation

This project implements the executable native core of `HHS-P156.1-LSHPVS` against the repository's canonical VM81 C ABI and Hash72/Hash216 implementation.

Implemented surfaces:

- exact canonical rationals and exact complex rationals with overflow guards;
- exact 2×2 Hermitian Hamiltonian assembly;
- exact Cayley propagation and exact norm verification;
- full signed modular-overflow identity `n=qM+r` with nonnegative residue;
- winding `W=U^M` and exact reconstruction `U^n=W^q U^r`, including negative rotations;
- content-addressed Hash216 entry and state identities;
- VM81 admission through `hhs_runtime_step` and canonical Hash72 receipt commitment;
- append-only versioned store, exact-index queries, atomic batches, rollback-on-rejection;
- canonical JSON projection and deterministic replay;
- native CLI and REPL, C ABI, Python ctypes wrapper, JavaScript process wrapper;
- positive, negative, replay, binding, and sanitizer validation.

The implementation does **not** promote the complete inherited nucleus to terminal success. Passes 154, 155, and 156 remain explicitly inherited blockers until their independent closure evidence exists. The local native classification is `HHS_PASS_156_1_LOCAL_CORE_VERIFIED`; the complete-nucleus classification remains `HHS_PASS_156_1_INCOMPLETE`.

```sh
make -C native_projects/hhs_pass156_1_lshpvs verify
```
