# Pass 220 — Dirac/HNAN exact boundary candidate restart (2026-10-26)

Branch: `pass220/standalone-adaptive-device-resolution-20261023`
Merge target: `main`
Inherited physics HTML update: `0978437dd371ef8efa838dafcb6f253f7c81beae`
Candidate evaluation commit: `21b28940f23128b34462c281980986d94eac9a30`
Candidate cleanup commit: `62cdc32bb5c2e44475e6f40a055e23a000af4585`
Tests commit: `f2ff04e4d9e2c93a938f991347340040d361faf9`

## Implemented
- `hhs_runtime/pass220/dirac_hnan_boundary_candidate_v1.py`: eight native HNAN role/source addresses preserved in order; exact Fraction-pair complex projector P+ and flux evaluation; eight reference boundary checks. Rejects float/complex input and role/address mismatch. Always denies native admission.
- `tests/pass220/test_dirac_hnan_boundary_candidate_v1.py`: exact reference, projector idempotence/flux, strict role ordering, float rejection, nonprojected spinor rejection, and anti-bypass witness flags.
- Existing HTML and its core physics remain unchanged by these evaluator commits.

## Incomplete
- No verified mapping between eight phase role addresses and original physical particle groups.
- No connection to native Pass 219 C++ cell wall, VM81 commit, conservation witness, central HNAN gate check, or Hash72/Hash216 receipt.
- No admitted new particle transitions and no demonstrated hydrogen spectrum.
- No executable test or browser/production run has been completed by this connector session. Source commits are NOT equivalent to passing tests.

## Next action
1. Resolve authoritative native particle-group provenance using repository index, source and runtime diagnostic paths, not guessed indices.
2. Add exact per-group spinor and sector state references to existing Pass 219 C++ cell wall, preserving operator order and existing physics integrator.
3. Enforce eight simultaneously satisfied projector conditions with dynamic unit normal, flux and global conservation checks. Do not equate static z-normal reference with curved manifold physics.
4. Admit transitions through existing VM81/Hash72/Hash216 authority, replay and negative tests. Only then expose resulting particle behavior in original `examples/ParticleSimulation.html`.
5. Run `python -m unittest tests.pass220.test_dirac_hnan_boundary_candidate_v1` (or equivalent direct module discovery), dependency-scoped integration, browser smoke tests, commit/merge, and verify main.

No invented physical particle-group mapping, independent dynamics engine, or hash authority is permitted.
