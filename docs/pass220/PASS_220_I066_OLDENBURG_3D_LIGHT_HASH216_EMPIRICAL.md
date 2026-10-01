# Pass 220 I066 — Oldenburg 3D-Light Empirical Hash216 Bridge

## Status

Candidate-only empirical-correspondence fixture.

Base main:

b99c434f691e5ac69a94e2d971e8ac877b6e167a

Branch:

pass220/i066-oldenburg-3d-light-hash216-empirical-20261001

## External source

Peer-reviewed publication:

- D. Köhnke, H.-C. Ahlswede, T. Bayer, M. Wollenhaupt
- "Multiphoton ionization with three-dimensional light fields"
- Physical Review Research 8, 033048
- published 2026-07-13
- DOI: 10.1103/r36b-vw82

The repository fixture uses publication-level facts only.

## Demonstrated empirical facts bound by I066

The paper reports:

- two different-color polarization-shaped ultrashort pulses;
- noncollinear superposition;
- electric-field components along x, y, and z;
- atomic multiphoton ionization of potassium;
- photoelectron momentum distributions recorded with velocity map imaging;
- access to all electric-dipole magnetic-sublevel changes
  Δm = -1, 0, +1;
- creation/control of free-electron angular-momentum superposition states
  beyond planar-polarization constraints;
- 3D pump-probe mapping of spin-orbit dynamics in the potassium 3d
  fine-structure doublet.

I066 does not invent wavelengths, pulse durations, field amplitudes, or
relative phases not pinned in this fixture.

## Chiral scope

The paper identifies chiral-sensitive light-matter interactions as an
application route enabled by the approach. I066 therefore records:

ROUTE_OR_FUTURE_APPLICATION

and explicitly sets:

demonstrated_by_this_potassium_experiment = false

This prevents future retrieval or training from silently converting a proposed
application into an observed result.

## Hash216 mapping

I066 preserves the inherited three-plane topology:

~~~text
PREVIOUS = peer-reviewed publication/source identity Hash72
CHANGE   = demonstrated 3D-field construction Hash72
RECEIPT  = observed selection-rule/measurement Hash72
~~~

The three Hash72 words concatenate to one 216-position Hash216 fixture.

I065 then verifies:

~~~text
72 Hash216 vertices
x 3 ordered components
3 x 5184 hydrated attached components = 15552
exact hydration/recompression roundtrip
~~~

The empirical fixture does not mint canonical Hash216 state.

## Ordered transition selection

The demonstrated dipole-selection geometry is encoded exactly as:

~~~text
Δm = (-1, 0, +1)
~~~

This tuple is stored as an externally observed physical selection-rule set.
Its numerical equality with an HHS trinary alphabet does not by itself assert
identity between the physical quantum number and an HHS internal semantic
operator.

## Empirical/formal boundary

I066 enforces:

~~~text
publication_is_external_empirical_evidence = true
publication_is_hhs_proof                   = false
hhs_theorem_is_empirical_measurement       = false
numeric_i061_calibration_satisfied_by_fixture_alone = false
~~~

I061's numeric calibration protocol is not bypassed. If later work extracts
published numerical waveforms, momentum distributions, delays, error bars, or
other quantitative measurements, those values require their own exact source
binding and calibration records.

## Lane 5 projection

Lane 5 may index the fixture by:

- source identity;
- bichromatic construction;
- noncollinear geometry;
- x/y/z field components;
- potassium;
- multiphoton ionization;
- Δm = -1,0,+1;
- velocity map imaging;
- 3d fine-structure spin-orbit mapping.

This is candidate-search metadata. It grants no canonical mutation authority.

## Formal enforcement

Lean:

formal/lean/HHS/Pass220/Oldenburg3DLightEmpirical.lean

Wolfram:

formal/wolfram/pass220_i066_oldenburg_3d_light_empirical_v1.wl

The connected Wolfram preflight passed 12/12 exact tests covering the 3D basis,
selection set, Hash216 width, VM5184 geometry, hydrated component count, and
ordered PREVIOUS/CHANGE/RECEIPT plane identity.

## Authority

~~~text
VM81 mutation authority        = false
Hash72 commit authority        = false
Hash216 persistence authority  = false
GPU canonical-state authority  = false
floating-point authority       = false
~~~
