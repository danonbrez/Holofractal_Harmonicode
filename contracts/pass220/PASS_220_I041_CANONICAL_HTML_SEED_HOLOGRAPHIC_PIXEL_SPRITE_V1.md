# Pass 220 I041 — Canonical HTML Seed / Holographic Pixel Sprite V1

Status: **NORMATIVE SEED BINDING / SOURCE-PRESERVING / PROJECTION-ONLY**

## Canonical seed identity

The canonical browser seed is the user-supplied monolithic HTML surface titled:

```text
Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041
```

The optimized repository surface:

```text
applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html
```

is a derived execution adapter.  It MAY optimize rendering and data layout but
MUST preserve the seed's ordered animation geometry unless a native repository
contract requires a repair.

## Preserved visual/animation invariants

The adapter MUST preserve:

- 5184 = 72^2 Lane-5 address topology;
- eight phase groups;
- Q144 octant 18, quarter-turn 36, half-turn 72;
- reciprocal phase/color relation;
- Layer-2 orthogonal +pi/2 / quarter-turn geometry;
- golden-spiral seed geometry;
- shared SO(4) xw/yz projection descriptor;
- tesseract 16 vertices / 32 edges / 8 cubic cells;
- Bott eight-group sweep;
- quartic one-in-four projection cadence while state ticks continue;
- deterministic pathway replay from a named seed;
- browser/GPU projection-only authority.

## Repository-contract repairs

Seed behavior is preserved except where executable helper logic conflicts with
the repository.  The following repairs are mandatory.

### Exact Q(sqrt2,sqrt3) field division

The Pass-219 1.66 Pell branch is exact.  Coefficients of the field inverse MUST
remain BigInt rationals.  Integer BigInt quotient truncation is forbidden.

Required witness:

```text
p/q = 2 + sqrt(3)
q/p = 2 - sqrt(3)
P^2 - pq = -1
B = 2sqrt(3) + 4sqrt(6) - 2sqrt(2)
(1/B) * B = 1 exactly
```

### VM81 closure is six-cell and fail-closed

The browser mirror MUST match the frozen C surface:

```text
check_gate_closure(VM81*, Pc, pc, qc, nc, xc, yc)
P^2 - pq == n^4
n^4 == xy
```

Missing x or y cannot mean "cell gate omitted".  Missing/noninteger folded cell
coordinates MUST reject the browser receipt.

### HNAN typing

The HNAN browser witness is the ordered 1/0 typed transition:

```text
(x+y-z-w+xy+yx-zw-wz)/EmptySet
```

It MUST NOT become a generic host division function.  Ordinary nonzero
browser/projection division is a separately named helper with zero canonical
authority.

### Cycle-9 rational transport

The exact root-isolation coordinate remains rational:

```text
P0 = 2133185666641251 / 10^15
p = P - 1
q = P + 1
```

The adapter verifies the exact rational identities directly.  It MUST NOT
silently coerce this nonintegral coordinate into a Z/72 residue.

### Determinism and side-effect discipline

The final adapter MUST use deterministic seed-derived animation/path state.
Diagnostic receipts MUST NOT mutate the authoritative simulation merely to
prove themselves.

If the canonical seed's bond/constructor subsystem is reintroduced, capture
bonds and construction bonds MUST carry distinct budget provenance:
construction edges spend no capture budget and therefore MUST NOT refund a
capture slot when broken.

Projection fingerprints MUST remain explicitly noncanonical.

## Holographic pixel-sprite display invariant

The renderer first produces one full-resolution RGBA source frame.  The
holographic compositor consumes that SAME frame at the SAME drawing-buffer
resolution.

For every output pixel:

```text
source pixel -> dense bright nucleus
neighbor source pixels -> translucent halo overlap
output = source + nucleus modulation + halo contribution
```

Required invariants:

```text
source_frame_resolution == output_drawing_buffer_resolution
source_pixel_is_dense_nucleus == true
driving_pixel_remains_behind_halo == true
halo_may_overlap_adjacent_pixel_cells == true
empty_halo_background_alpha == 0
```

The virtual relationship surface is:

```text
5184 * 5184 = 26,873,856
```

This virtual field does not replace the physical raster.  720p, 1080p, 4K, or
other display dimensions remain the actual output resolution.

## Tuning surface

The HTML MUST expose live projection-only tuning for at least:

- nucleus gain;
- halo radius in output pixels;
- halo gain;
- deterministic phase amplitude;
- deterministic phase speed;
- source-only, nucleus-only, halo-only, and composite views.

## Acceptance

Before MP4 capture, the browser harness MUST verify:

```text
HHS_I041_CANONICAL_SEED_MATH_REPAIR_RECEIPT_V1 == PASS
HHS_I041_HOLOGRAPHIC_PIXEL_SPRITE_DISPLAY_V1.sameResolution == true
```

MP4/video evidence remains projection evidence.  It grants no VM81 mutation,
Hash72 mint, Hash216 persistence, receipt-clock, or floating-point canonical
authority.
