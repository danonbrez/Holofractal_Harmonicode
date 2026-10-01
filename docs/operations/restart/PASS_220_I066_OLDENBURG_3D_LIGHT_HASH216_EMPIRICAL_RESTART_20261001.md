# Pass 220 I066 restart checkpoint — 2026-10-01

## Identity

- Base main: b99c434f691e5ac69a94e2d971e8ac877b6e167a
- Branch: pass220/i066-oldenburg-3d-light-hash216-empirical-20261001
- Merge target: main
- Scope: Oldenburg 3D-light experimental source -> typed field/transition record
  -> Hash216 candidate fixture -> I065 hydration -> Lane 5 empirical retrieval.
- External source DOI: 10.1103/r36b-vw82

## Implemented

1. hhs_runtime/hhs_pass220_i066_oldenburg_3d_light_hash216_empirical_v1.py
2. tests/pass220/test_hhs_pass220_i066_oldenburg_3d_light_hash216_empirical_v1.py
3. formal/lean/HHS/Pass220/Oldenburg3DLightEmpirical.lean
4. formal/lean/HHS.lean
5. formal/wolfram/pass220_i066_oldenburg_3d_light_empirical_v1.wl
6. contracts/pass220/PASS_220_I066_OLDENBURG_3D_LIGHT_HASH216_EMPIRICAL_V1.json
7. docs/pass220/PASS_220_I066_OLDENBURG_3D_LIGHT_HASH216_EMPIRICAL.md
8. docs/whitepapers/HHS_PASS_220_I066_OLDENBURG_3D_LIGHT_EMPIRICAL_BRIDGE_V1.md
9. docs/operations/restart/PASS_220_I066_OLDENBURG_3D_LIGHT_HASH216_EMPIRICAL_RESTART_20261001.md
10. .github/workflows/pass220-i066-oldenburg-3d-light-empirical.yml

## Frozen empirical facts

- two different-color polarization-shaped ultrashort pulses;
- noncollinear superposition;
- electric-field components x/y/z;
- potassium multiphoton ionization;
- velocity-map-imaging photoelectron momentum distributions;
- dipole selection changes -1, 0, +1;
- 3D pump-probe mapping of potassium 3d fine-structure spin-orbit dynamics.

## Frozen non-claims

- no invented wavelength values;
- no invented pulse-duration values;
- no invented field amplitudes;
- no invented relative phases;
- no claim that this potassium experiment demonstrated chiral sensing;
- no claim that categorical source binding substitutes for I061 numeric calibration;
- no claim that the publication proves HHS.

## Hash216 binding

~~~text
PREVIOUS = publication/source identity
CHANGE   = 3D field construction
RECEIPT  = observed transition selection + measurement
~~~

I065 exact hydration/recompression is mandatory.

## External Wolfram preflight

2026-10-01:

~~~text
VerificationTests: 12
Succeeded:         12
Failed:             0
AllSucceeded:    True
~~~

## Validation remaining at checkpoint creation

- I066 Python test on branch;
- I065 hydration regression;
- Lean build/kernel checker/axiom audit;
- PR workflow;
- mergeability against current main.

## Resume

1. Inspect branch head and this checkpoint.
2. Run the I066 dependency-scoped test.
3. Run I065 hydration regression.
4. Run pinned Lean build/checker/axiom audit.
5. Open/update PR to main.
6. Repair only impacted I066 dependencies.
7. Merge when the I066 gate is green and PR is mergeable.
8. Verify main contains the merge commit.
