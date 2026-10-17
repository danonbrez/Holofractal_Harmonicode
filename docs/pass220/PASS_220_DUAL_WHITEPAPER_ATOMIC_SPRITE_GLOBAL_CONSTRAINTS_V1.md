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

## Exact calibrated calorimetry extension

The additive service `pass220.atomic_sprite_thermal_ingress.v1` composes
the original 21-field candidate ingress unchanged, adding three *also
corpus-bound* inputs: `thermal_profile`, `energy_transfer_joules`, and
`phase_fraction`. It therefore validates **24 exact inputs** using the
same two complete directory identities and exercises the same inherited
Pass131/Pass067.1/I058 component witnesses.

Implemented at `hhs_runtime/pass220/atomic_sprite_calorimetry_v1.py`.
The caller-supplied profile explicitly supplies:

- species/isotope identity and separate exact relative atomic mass in u;
- melting and boiling temperatures in kelvin;
- solid/liquid/gas heat capacities in joules/kelvin **per modeled particle**;
- latent fusion and vaporization energies in joules per modeled particle;
- an exact energy reference and a calibration/model identity.

All capacities, phase thresholds and latent heats are positive exact
rationals, `T_melt < T_boil`; reference energy may be signed. Unsupported
plasma, missing calibration, wrong isotope/mass lineage, negative Kelvin,
unaccounted enthalpy, and host floats all fail closed.

This is an **explicitly declared constant-heat-capacity piecewise
calorimetric model**, not a claim that source prose contains measured
calorimetric coefficients. For exact model parameters `C_s,C_l,C_g`,
melting/boiling temperatures `T_m,T_b`, latent heats `L_f,L_v`,
and reference `E_0`, the exact state energy follows:

```text
SOLID:          E = E_0 + C_s * T                         T <= T_m
SOLID_LIQUID:   E = E_0 + C_s*T_m + f*L_f                 0<f<1, T=T_m
LIQUID:         E = E_0 + C_s*T_m + L_f + C_l*(T-T_m)     T_m<=T<=T_b
LIQUID_GAS:     E = E_0 + C_s*T_m + L_f
                    + C_l*(T_b-T_m) + f*L_v             0<f<1, T=T_b
GAS:            E = E_0 + C_s*T_m + L_f
                    + C_l*(T_b-T_m) + L_v
                    + C_g*(T-T_b)                       T>=T_b
```

The transition preserves exactly `E_after = E_before + energy_transfer`,
rejects starting-state/enthalpy mismatch, and proves exact reversibility by
reconstructing the end energy from the end phase state. The `x/y/z/w`
ordered tensor phase and all VM81/Hash216 ancestry remain **unchanged**;
material coexistence phases are distinct typed state. No geometry or bond
mutation is authorized by this candidate.

The fixture temperatures and heats in the regression suite are marked
`SYNTHETIC_TEST_ONLY`; they must **not** be represented as lithium
experimental measurements. Before actual atomic-weight-dependent geometry
or physically calibrated phase dynamics, independent empirical provenance
and the signed VM81 membrane must be validated.

Separate test:
```bash
python -m pytest -q tests/pass220/test_atomic_sprite_calorimetry_v1.py
node tests/pass220/test_agentic_electron_sprite_v1.cjs
```

Local dependency-independent thermodynamics kernel passed **11/11 tests**
(including phase boundary heating, cooling, source-preserving exact energy,
and negative controls). The complete dual-corpus + inherited-service
integration test lives in the repository and awaits CI execution.

## I057 browser rendering regression: standalone entrypoint fix

**Bug reproduced from source:** the initial derived page loaded
`hhs_agentic_electron_sprite_v1.js` as an external *relative* script,
then unconditionally threw `NEURAL_PROJECTION_MODULE_MISSING` when
opened as a single HTML artifact from a location without that sibling file.
The scene was constructed but its animation loop never started. The
canonical HHS boot check was independently evaluated in V8 and passed
all four boot predicates, so that gate was not the cause.

**Repair:** `ParticleSimulationAtomicNeural.html` now embeds the matching
neural controller source in its own inline `<script>` block.
Opening that one file requires no *additional local* neural JavaScript
asset. The inherited THREE.js/OrbitControls CDN dependencies still
require network access, as in the frozen original I057 HTML.

The preview's failure is now isolated: if controller initialization
fails, the neural status panel shows a disabled preview, while the
I057 particle field continues to render. If all-sensor prevalidation
fails during recurrence, the controller is quarantined without
modifying either the native authority or the underlying field loop.
A true HHS boot invariant failure still blocks startup, as required.

The JavaScript regression was repaired to compile **both inline scripts**,
execute the actual embedded controller, verify the original HHS boot
predicates, check the absence of sibling-module dependency, and assert
the isolated preview-failure behavior. The candidate-only neural
physics admission remains unchanged.

The corrected entrypoint is:
`examples/ParticleSimulationAtomicNeural.html`.
No original I057 source modification or production deployment is claimed.

## Follow-up browser errors: startup, controls, diagnostics and command repairs

The second browser repair cycle addresses additional integration defects
without changing the frozen I057 HTML:

1. Render the **very first** animation frame immediately rather than waiting
   for `renderTick%4===0`. Every-fourth projection cadence resumes afterward;
   the rendered-frame counter includes that extra first presentation frame.
   The inherited `QuarticSkipTest` remains quarantined on this derived page
   because the new first-frame convention intentionally differs from its
   exact original cadence assertion.
2. Remove unused `dat.gui` script dependency and pin OrbitControls at
   `three@0.128.0`. If the optional OrbitControls script is unavailable,
   use a **static-camera fallback**, preserving physical computation and
   visible particles. Missing core THREE.js or a WebGL failure remains a
   genuine rendering prerequisite; startup errors are now exposed in a
   visible on-page `runtimeDiagnostics` element instead of disappearing
   behind a black canvas.
3. Do not allow `TopoInversionTest` to run destructively against the live
   derived page while the physical topology control requires native
   admission. It is quarantined alongside the other mutation-capable
   diagnostic receipts.
4. Catch command/module execution exceptions separately from JSON parsing.
   Both the OS shell and QPU command interfaces report
   `COMMAND_RUNTIME_REJECTED` or `MODULE_RUNTIME_REJECTED` for execution
   failures, not the misleading `Invalid JSON` message.
5. Keep the optional neural controller embedded in the standalone HTML;
   its initialization failure or invalid sensor frame does **not** suppress
   the underlying 10,368-particle graphics/physics.

In addition to the source-regression test, this cycle commits
`tests/pass220/test_agentic_electron_sprite_browser_smoke_v1.cjs`.
It **executes both controller and simulation** against deterministic
browser/THREE interface doubles, checking first-frame display, eight more
animation callbacks, working agent inspection, measured-calibration
callbacks, strict physical UI control boundaries, and successful rendering
without either OrbitControls or the neural overlay. Both JS regression
suites passed in the in-session V8 test harness against exact branch
source. Repository CI includes both tests, but **real GPU/WebGL
rendering remains pending separate graphical smoke**.

These changes are targeted *browser projection/diagnostics* repairs:
no source corpus constraint, VM81 admission authority, Hash72/Hash216
provenance, canonical ordered phase, or original I057 force equation was
weakened or replaced.

## I057-preserving derived agentic electron-sprite browser

The I057 authority baseline `examples/ParticleSimulation.html` remains
**exactly unchanged** (blob `218d89d67803b5b10ab86b1cdb97434438e25082`).
The new complete runnable projection page is:

```text
examples/ParticleSimulationAtomicNeural.html
examples/hhs_agentic_electron_sprite_v1.js
```

Open `ParticleSimulationAtomicNeural.html` directly as a single file
for the simulation and its embedded neural overlay (Three.js and
OrbitControls still load from the existing external CDNs). The second
`.js` file is preserved as the matching source module for tests and
reusable integration; it is no longer a runtime loading prerequisite. The
derived page preserves all 10,368 graphical particles, both 5,184-carrier
layers, the original field equations, bond channels and receipt computations
in source, while layering candidate neural inference over the existing
particle-derived Float32 sensory buffers.

The new recurrent **FlyVis-inspired surrogate** is not the original
FlyVis connectome and is not a trained 86.8-billion-neuron model. It runs
a deterministic four-channel recurrent state for each of the 10,368
carriers each physics substep, with projected sensory channels for
velocity, distance, charge, phase, neighbor density, phase budget and mass.
It emits bounded thrust/yaw/pitch/roll and bond-request **proposals**.
These are not connected to the particle's force or bond writes, and neither
mint Hash216 nor update canonical VM81 state. They are explicitly a
noncanonical candidate projection to exercise the sensory/control interface.

The derived page exposes a visible per-agent inspector and live counts for
active neural carriers, recurrent steps and candidate bond requests.
`AgenticElectronSpriteStatus` is also callable through the inherited
diagnostic shell. All physical slider controls and topology/key toggles
are disabled pending *real* dual-whitepaper and signed-VM81 admission.
`init_system` rejects direct global parameter assignment with
`FAIL_CLOSED_GLOBAL_CORPUS_NATIVE_ADMISSION_REQUIRED`. The pointer
observer is sensing-only and does not inject unauthenticated forces.
There is no browser-supplied flag/token that can unlock physical writes.

The boot check now actually gates `initScene()` on
`!window.HHS.boot.boot_halt`; a false boot never starts the sim.
Invalid/nonfinite incoming neural observations are checked **before**
changing recurrent state; a rejection disables the **neural projection**
but **does not halt particle physics or graphics rendering**. Browser JSON text is rendered with `textContent`
rather than `innerHTML`, and the Calibration button now reports observed
render/callback counters rather than a constant computed from `dt`.
The O(10,368) position-text hash is computed on explicit `get_state`,
not at every derived projection redraw.

Side-effecting diagnostics `FractalLayer2Test`, `VirtualDecayTest`,
`SolidConstructorTest`, `QuarticSkipTest` and
`EntanglementChannelTest` are **quarantined** in the derived live page
until isolated snapshot/replay execution is supplied. They still exist
unmodified in the original I057 file. Other diagnostic side effects have
not all been exhaustively isolated by this change.

This is a **live graphical preview of neural proposals**, not production
signed actuation or an empirical mass/thermal/geometry model. The next
integration obligation remains the same: native service-specific
authorization of the source-calibrated atomic/thermal state and trained
motor outputs before a changed physical trajectory can be accepted.
Neither the native VM81 membrane nor frozen I057 logic has been bypassed.

Focused JavaScript regression:

```bash
node --check examples/hhs_agentic_electron_sprite_v1.js
node tests/pass220/test_agentic_electron_sprite_v1.cjs
```

The source-equivalent V8 validation executed the committed JavaScript
and compiled the derived HTML inline script. It passed:
full 10,368 carriers; 5,184 split address mapping; deterministic
recurrence; exact negative/nonfinite-frame rejection before state update;
mass-sensitive motor output; zero canonical authority; guarded browser
parameter input; quarantined live-destructive tests; and unchanged
original I057 Git blob. Full Node CI is tracked separately and must not
be marked passed until the scoped workflow completes.

## Acceptance

Focus tests:

```bash
python -m pytest -q tests/pass220/test_atomic_sprite_whitepaper_gate_v1.py
python -m pytest -q tests/pass220/test_atomic_sprite_global_ingress_v1.py
python -m pytest -q tests/pass220/test_atomic_sprite_calorimetry_v1.py
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
  - `hhs_runtime/pass220/atomic_sprite_calorimetry_v1.py`
  - `tests/pass220/test_atomic_sprite_calorimetry_v1.py`
  - `examples/ParticleSimulationAtomicNeural.html`
  - `examples/hhs_agentic_electron_sprite_v1.js`
  - `tests/pass220/test_agentic_electron_sprite_v1.cjs`
  - `hhs_runtime/hhs_service_registry_v1.py`
  - `.github/workflows/pass220-dual-whitepaper-global-constraint-gate.yml`
  - `docs/pass220/PASS_220_DUAL_WHITEPAPER_ATOMIC_SPRITE_GLOBAL_CONSTRAINTS_V1.md`
- Local gate validation: **12 passed**, executed under
  `/mnt/data/hhs_corpus_gate` with matching new-gate source/tests.
- Standalone exact calorimetric kernel: **11 passed locally**, independent
  of repository-native dependencies.
- Inherited physics and complete-corpus integration tests require the full
  repository dependencies; source and scoped CI committed, pending run result.
- CI/native integration: **not claimed** at this checkpoint.
- Next action: inspect scoped CI for both registered candidate routes and the
  browser regression; repair-forward failures. Introduce actual trained FlyVis
  inference and certified isotopic calorimetry/thermal transfer, and connect
  the resulting motor inputs through the signed native membrane before any
  physical action is authorized. Merge and verify main only after required
  scope validations.
