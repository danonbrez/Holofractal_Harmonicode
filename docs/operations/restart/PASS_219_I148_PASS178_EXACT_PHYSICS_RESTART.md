# Pass 219 I148 / Pass 178 exact physics restart record

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- branch: `agent/pass219-iteration148-pass178-exact-physics-reconciliation`
- merge target: `main`
- frozen predecessor I147 checkpoint: `d6a9e81361938c53536f14f4f23be9bc4080e838`
- first exact-physics nucleus commit: `97498ede3a9a5907c0cfc25f5fd868072577fcdc`
- served Physics Studio wiring commit: `553589499985890fcbf493d59e65fe76c2a07e52`
- pre-cumulative validation implementation head: `a19d601fd4141dda04d945ef72ed2bac4d4dabac`
- failed dedicated run: `33626494423`
- repair commit: `0b7ae01ff50e7f0ab3df6ab2b068506ea22d6c31`
- repair test commit: `1f63e08370d0e3c54390a7b4b3bec8ef042ddfa3`
- repair validation run: `33626761513`
- merge status: UNMERGED
- authoritative-main verification: NOT PERFORMED
- cumulative Pass 178 binding: NOT YET ADMITTED
- terminal Pass 178 completion: FALSE

## Census

Before I148 the repository contained only the normative Pass 178 contract. Required runtime, native project, machine contract, source corpus, tests, studio and evidence were absent.

Classification:

`CONTRACT_ONLY_WITH_MISSING_RUNTIME_AND_CUMULATIVE_EXPOSURE`

## Implemented nucleus

I148 adds exact rational/complex algebra, symbolic algebraic roots, typed constraint relations, exact relativity and quantum nuclei, source identity, model registration, inherited VM81 admission, replay, immutable render packets, a C ABI nucleus, three laboratory templates, governed HTTP routes, served Physics Studio, capture tooling, and native/Python conformance tests.

## Explicit nonterminal boundaries

The repository-visible corpus is only the contract-visible corpus nucleus. The complete historical user-supplied corpus is not claimed.

The following remain terminal debt: complete compiler pipeline, thermodynamic kernel, charged-particle field lab, full double-slit lab, measurement authority, singular Hash72 clock integration, full Three.js viewport, MP4 capture, browser/mobile performance/security acceptance, and authoritative-main closure.

## Dedicated pre-cumulative validation failure and repair

Dedicated workflow:

`.github/workflows/pass219-i148-pass178-exact-physics.yml`

Run `33626494423` executed against exact head `a19d601fd4141dda04d945ef72ed2bac4d4dabac` and failed only at `Run Pass 178 Python conformance`.

Observed result:

- 10 tests passed;
- 1 test failed;
- failure: `tests/test_hhs_pass178_abi_replay.py::test_vm81_admission_and_replay_chain`;
- exception: `P178_CANDIDATE_NOT_VALIDATED`;
- later native/corpus/capture/policy stages were skipped because the dependency-scoped Python gate failed;
- unrelated Pass 205/166/174/acceptance/relay failures remain outside I148 scope.

Root cause: an admitted relativistic state serializes exact rationals as canonical `[numerator, denominator]` pairs, but `ExactRational.coerce()` accepted exact objects, integers, strings and `Fraction` while rejecting the same canonical pair representation during the next validation cycle. This caused `_evolve()` output to fail re-validation before VM81 admission. The commit path therefore failed closed as intended.

Repair:

- `0b7ae01ff50e7f0ab3df6ab2b068506ea22d6c31` adds exact two-integer list/tuple pair coercion while preserving Boolean rejection, zero-denominator rejection, normalization and float rejection;
- `1f63e08370d0e3c54390a7b4b3bec8ef042ddfa3` adds explicit canonical pair round-trip coverage;
- no VM81, Hash72, Hash216, GPU, browser, renderer, corpus-completeness or floating-point authority was widened.

Repair validation run `33626761513` is the authoritative next dependency-scoped run on exact repair head `1f63e08370d0e3c54390a7b4b3bec8ef042ddfa3`.

## Next action

If repair run `33626761513` is green, freeze its exact receipt/artifact, add the cumulative inherited Pass 178 C/C++ binding, extend global defaults to floor `178` / binding count `43`, preserve `terminal_pass178_completion=false` and `repair_forward_required=true`, and execute one bounded post-binding cumulative validation.

If the repair run fails, inspect and repair only the newly failing Pass 178 dependency-scoped surface.

Preserve singleton inherited VM81 authority, no independent Hash72 commit clock, archival-only Hash216 identity, no renderer/GPU/browser/floating-point canonical authority, and the explicit nonterminal status of the contract-visible corpus. Do not merge to main without separate authorization.
