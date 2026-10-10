# Pass 220 — Dual White-Paper Global Constraint Membrane for Atomic/Neural Sprites

Status: **ADDITIVE CORPUS-BOUND SERVICE INGRESS IMPLEMENTED / CANDIDATE-ONLY / LIVE NEURAL+MATERIAL PHASE EXECUTION OPEN**

## Normative source trees

All new HHS atomic, thermodynamic, phase, geometry, and fly-agent/particle
parameters must be bound against the complete content of **both** authoritative
white-paper corpora:

```text
whitepapers/
docs/whitepapers/
```

These are global constraint sources, not optional explanatory references or
independent scalar parameter defaults. The source trees are treated together:
a parameter may cite specific files from either directory, but the **global
bundle identity includes every regular file in both trees**. Adding, changing,
or removing any corpus file invalidates an older snapshot. Source symlinks
and missing or empty corpora fail closed.

This requirement does not reverse the inherited repository authority order:
canonical equation/ABI and executable proof obligations govern mechanical
admission; white papers carry the formal sources and claims requiring that
admission. Prose alone does not certify executable equations.

## Executable preflight

```text
hhs_runtime/pass220/atomic_sprite_whitepaper_gate_v1.py
```

- `corpus_snapshot(repo_root)` computes SHA-256 identity for every regular
  file in each tree and hashes the two named tree roots into a common bundle.
- `bind_global_parameters(repo_root, parameters,
  expected_bundle_sha256=...)` validates **every parameter in the supplied
  mapping**, fails closed when either corpus or binding is missing/changed,
  and returns a deterministic candidate receipt.
- Every parameter needs a typed value, semantic kind, ordered list of valid
  white-paper source paths, equation status, role, and constraint identifier.
- Nested canonical values must be exact; Python floats are rejected, including
  inside arrays and mappings. Finite floats are permitted only in explicitly
  `PROJECTION_ONLY` values, never in canonical physics.
- `CANONICAL_VERBATIM`, `DEVELOPMENT_VERBATIM`, and `REFERENCE_ONLY`
  claims may not become `NATIVE_EXACT_CANDIDATE` parameters. Executable/native
  candidates require `EXECUTED_EXACT` or `HHS_NATIVE_SEMANTIC` status, with
  the inherited separate proof and admission gates still mandatory.
- Source text, fixed ordered symbols, Lo Shu positions, and noncommutative
  phase operators are not algebraically rewritten by this binding mechanism.
- The resulting receipt is `CORPUS_BOUND_CANDIDATE_ONLY`, not an authorization
  to mutate VM81 state, mint Hash72/Hash216, promote training weights, or
  bypass the signed environmental admission chain.

A parameter record has exactly this shape:

```python
{
    "value": exact_value,
    "kind": "ORDERED_PHASE_OR_ATOMIC_ATTRIBUTE",
    "source_paths": ["whitepapers/<actual source>", "docs/whitepapers/<actual source>"],
    "status": "EXECUTED_EXACT",
    "role": "NATIVE_EXACT_CANDIDATE",
    "constraint_id": "<an inherited proof/ABI obligation>",
}
```

The recorded `constraint_id` is an obligation identifier, **not proof that
the obligation was executed**. Fail closed unless the relevant exact
C/C++/VM81/Wolfram/Lean/Pass131/Pass067.1 native checks independently pass.

## Atomic and thermodynamic integration contract

Preserve the existing physically distinct typed fields:

| Field | Existing source / meaning |
|---|---|
| `atomic_number`, `mass_number`, `charge`, `electron_configuration` | Pass 131 atomic/electrochemical state and conservation |
| `relative_atomic_mass` / isotope identity | separate calibrated mass quantity; do not identify a mass number with measured atomic weight |
| `temperature`, `internal_energy`, `thermodynamic_phase` | thermodynamic material state; numerical values and transition thresholds require sourced units and validated constitutive models |
| `ordered_hhs_phase` | Lo Shu / Pass 067.1 ordered tensor phase; cannot collapse into material phase or Boolean charge |
| `geometry`, `bond_lineage` | I041/I057 full particle physics and constructor states |
| `neural_policy`, `actuators` | FlyVis-derived candidate controls; must enter through HHS typed membrane, not mutate browser physics directly |

Pass 131 already exposes exact ionization, reduction, symbolic Hamiltonian,
reaction balancing, and deterministic replay. Pass 067.1 supplies independent
exact Lo Shu energy redistribution and ordered phase gates. The I058
white-paper game mechanics kernel protects non-lowered `CANONICAL_VERBATIM`
and `REFERENCE_ONLY` equations. Existing I057 particle physics and rendering
are frozen; the new preflight is additive and must not modify those trajectories.

## Wired guarded input path

```text
HHS service registry:
  pass220.atomic_sprite_corpus_ingress.v1
    -> run_atomic_sprite_ingress_service(payload)
    -> bind_global_parameters(complete physical inputs, two tree roots)
    -> Pass131.create_atomic_state + validate_state
    -> Pass067.1.harmonic_phase_energy_self_test
    -> I058.build_whitepaper_game_frame + validate_whitepaper_game_frame
    -> candidate receipt; signed VM81 admission still required
```

Runtime source: `hhs_runtime/pass220/atomic_sprite_global_ingress_v1.py`.
The service uses a **fixed repository root** derived from its source path,
not a caller-controlled directory. Its required envelope contains exactly
21 declared inputs: atomic species/number/isotope mass number/charge/orbitals,
symbolic state, separately typed relative atomic mass (u), temperature (K),
internal energy (J), material phase, ordered Lo Shu VM81 cell/operation/parent
Hash216, exact ionic/gravitational controls, particle geometry and ordered
bond pairs, bounded neural motor actions, and I058 tick/seed/P/m_pass/alpha/
kappa mechanics inputs. Missing or unexpected fields, stale corpus identities,
floating canonical input, invalid particle addresses, malformed orbital counts,
and authority-confused projection controls all fail closed.

This service **really invokes** the existing exact component validators.
It does **not** validate an empirical thermodynamic equation of state, infer
chemical phase-transition temperatures, certify supplied atomic weights
against experimental sources, simulate actual FlyVis synapses, apply a novel
ionic force, modify the frozen I057 browser state, or perform signed VM81
mutation. Those obligations remain distinct; flags in the candidate receipt
record them as false. The caller must supply calibrated constitutive and
atomic-mass data under applicable approved proofs before claiming empirical
physical fidelity.

The gate is mandatory for **this new ingress route**, but legacy Pass131,
Pass067.1, I058, and I057 direct entrypoints have not been globally
rewritten to require it. Universal enforcement requires migration of those
legacy dispatch paths while preserving all inherited source contracts and
compatibility tests. Parameter binding alone is not the same as executing
each scientific theorem or constraint.

An accepted canonical state still requires the native singleton signed VM81
admission chain after the candidate receipt passes all applicable proof
obligations.

## Acceptance

Focus tests:

```bash
python -m pytest -q tests/pass220/test_atomic_sprite_whitepaper_gate_v1.py
python -m pytest -q tests/pass220/test_atomic_sprite_global_ingress_v1.py
```

Required regression behaviors: dual-tree fingerprint determinism, exact
rational typing, stale-source rejection, added-file drift, missing tree,
untrusted source path, reference-only authority escalation, nested float
rejection, and explicitly noncanonical finite projection.

## Restartability

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base SHA: `7fefacde360e6a5bb537cb01e94415c96430915b`
- Branch: `agent/pass220-dual-whitepaper-atomic-sprite-20261010`
- Merge target: `main`
- Files:
  - `hhs_runtime/pass220/atomic_sprite_whitepaper_gate_v1.py`
  - `tests/pass220/test_atomic_sprite_whitepaper_gate_v1.py`
  - `hhs_runtime/pass220/atomic_sprite_global_ingress_v1.py`
  - `tests/pass220/test_atomic_sprite_global_ingress_v1.py`
  - `hhs_runtime/hhs_service_registry_v1.py`
  - `.github/workflows/pass220-dual-whitepaper-global-constraint-gate.yml`
  - `docs/pass220/PASS_220_DUAL_WHITEPAPER_ATOMIC_SPRITE_GLOBAL_CONSTRAINTS_V1.md`
- Local gate validation: **12 passed**, executed under
  `/mnt/data/hhs_corpus_gate` with matching new-gate source/tests.
- Inherited physics integration tests require the full repository dependencies:
  source and scoped CI committed; workflow status queued at this checkpoint.
- CI/native integration: **not claimed** at this checkpoint.
- Next action: inspect scoped CI for registered candidate route, repair-forward
  any missing dependencies; integrate empirical thermodynamic transition
  witnesses and actual FlyVis motor inference into the same source-bound route
  before permission to mutate I057/VM81, then merge and verify main.
