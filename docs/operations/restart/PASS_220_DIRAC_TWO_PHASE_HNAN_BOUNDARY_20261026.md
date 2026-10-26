# Pass 220 — Two-phase Dirac spinors / eight HNAN boundary checkpoint

Date: 2026-10-26
Repository: danonbrez/Holofractal_Harmonicode
Source branch: pass220/standalone-adaptive-device-resolution-20261023
Merge target: main
Base commit: e006c753103d38f19f7798944576ed4d7f59bb98
Work type: additive specification and symbolic verification; no particle physics mutation

## Objective

Add two coupled Dirac spinor phases to existing particle groups through eight
distinct, ordered HNAN quantum boundary condition instances. Preserve the
original 4D toroidal particle dynamics, momentum, acceleration/drag, collision,
formation thresholds (collision 1.40, formation 1.25), PCM clock, Larone u^72,
81 Hz BigInt qudit serialization, and VM81/Hash72/Hash216 authority.

Do NOT assign arbitrary particle group indices. Existing HNAN octonion source
and group provenance must supply the authoritative mapping. The eight phase
roles are typed and ordered: xy, x+y, yx, xy-zw, wz-yx, wz, z+w, zw;
the HNAN center gate remains the existing center, not a ninth invented group.

## Verified Wolfram algebra (reference representation only)

Let sigma=(PauliMatrix[1],PauliMatrix[2],PauliMatrix[3]), phi and chi be
two-component spinors, psi=Join[phi,chi], and

H_D = {{m c^2 I2, c (sigma.p)}, {c (sigma.p), -m c^2 I2}}

where this displayed block notation is a 4 x 4 block matrix and p is real.
The WolframLanguageEvaluator returned True for Hermitian[H_D] and for

H_D.H_D == (m^2 c^4+c^2(p1^2+p2^2+p3^2)) IdentityMatrix[4].

A **candidate reference** boundary with unit normal n=(0,0,1):

beta = DiagonalMatrix[{1,1,-1,-1}]
alpha_n = {{0,sigma3},{sigma3,0}}
K = I beta.alpha_n
Pplus = (IdentityMatrix[4]+K)/2.

The Wolfram kernel returned True for K^dagger=K, K^2=I,
Pplus^2=Pplus, and Pplus^dagger.alpha_n.Pplus=0.
This tests an algebraic zero-normal-current constraint at a reference
boundary. It does not establish a 4D HHS-specific spin structure,
gauge background, curved-manifold Dirac operator, physical proton,
or hydrogen spectrum.

## Admission constraints

- Exactly TWO spinor phase blocks (phi, chi), not new particle types.
- Exactly EIGHT existing outer HNAN phase roles; use their native ordered
  identifiers, not invented scalar group assignments.
- For each sector i, define B_i[psi_i, n_i, phase_i, source_i] as a
  separately typed, source-bound boundary. Preserve original operator order.
- The combined eight-sector constraint is accepted only after checking
  cross-sector reciprocal phase, boundary flux, shared conservation, the
  existing HNAN center gate, and native serialization provenance.
- No imaginary normal, non-unitary projector, singular-domain division, or
  absent source-group witness may be silently admitted.
- The supplied rho/t modular-singularity equation is retained as an input
  claim, not treated as proven equivalent to Dirac equations or to a literal
  gravitational event horizon. The division-by-zero center is a domain
  boundary that cannot be canceled without a native rule.
- Candidate Dirac eigenstates may inform the browser atomic projection only
  after constrained native admission; do not move particles, inject forces,
  remint Hash72/Hash216, or modify the frozen physics in this checkpoint.

## Existing authorities inspected

- REPOSITORY_INDEX.md and AGENTS.md remain first-pass navigational contracts.
- hhs_runtime/hhs_pass220_hnan_phase5184_lossless_bridge_v1.py:
  ordered HNAN tensor/addresses and read-only candidate bridge.
- contracts/pass219/PASS_219_LANE5_EXACT_BOUNDARY_QUANTUM_THERMO_MANIFOLD_V1.md:
  global exact boundary is monolithic; unresolved full-source evaluation
  cannot be self-certified as +1.
- docs/operations/restart/PASS_220_RELATIVE_GEOMETRY_DESCRIPTOR_20261025.md:
  particle identity to native BigInt position mapping is not yet verified.

## Checkpoint / validation status

- Wolfram exact symbolic Hermiticity, squared Dirac Hamiltonian,
  projector idempotence and zero normal flux: PASS on reference matrices.
- Eight native sector-to-particle assignments: NOT VERIFIED.
- Coupling to existing C++ Pass 219 cell wall: NOT IMPLEMENTED.
- Browser atomic projection, hydrogen spectral conformity: NOT VERIFIED.
- Regression/CI/production: NOT EXECUTED; no runtime files changed.
- Source commit/branch: inspect Git commit following this document creation.

## Next action

Locate existing group address mapping and Dirac/spinor source contracts via
AGENTS.md, REPOSITORY_INDEX.md, generated dependency graph. Construct eight
native boundary *instances* preserving each ordered phase source; certify
their combined global boundary and Hermitian/flux checks using Wolfram and
Lean4, run dependency-scoped tests, then integrate through existing native
cell-wall admission. Do not change particle kinematics or presentation clock.
