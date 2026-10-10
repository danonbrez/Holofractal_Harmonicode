# Pass 220 — Dual White-Paper Global Constraint Membrane for Atomic/Neural Sprites

Status: **ADDITIVE PREFLIGHT IMPLEMENTED / CANDIDATE-ONLY / NATIVE INTEGRATION OPEN**

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

A global integration is accepted only when a real participant ingress path
invokes this gate for **all** its parameter fields, subsequently invokes
the applicable native constraint witnesses, and observes canonical signed
VM81 admission. Merely creating the gate does **not** yet enforce it on
legacy callers across the repository.

## Acceptance

Focus tests:

```bash
python -m pytest -q tests/pass220/test_atomic_sprite_whitepaper_gate_v1.py
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
  - `docs/pass220/PASS_220_DUAL_WHITEPAPER_ATOMIC_SPRITE_GLOBAL_CONSTRAINTS_V1.md`
- Local focused validation: **12 passed** using equivalent new source and test
  content in an isolated Python fixture environment.
- CI/native integration: **not claimed** at this checkpoint.
- Next action: dependency-scoped PR validation; wire the shared gate to
  Pass131/Pass067.1 and fly-agent/particle ingress, with per-obligation
  runtime witnesses and no modifications to the frozen I057 monolith;
  commit and verify any necessary repair-forward changes.
