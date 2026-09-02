# Pass 219 I148 — Raw 5184 / octonion dual-stereo PCM64 hydration restart

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- branch: `agent/pass219-iteration148-raw5184-octonion-audio-hydration`
- base / merge target: `main @ bcfe5652ecb210e3c7b118bcb129bd8c399ae72f`
- predecessor: Pass 219 I147 / PR #349
- intended merge target: `main`

## Reconciliation

Existing executable authority on current main:

- exact VM81 frame: `81 × 64 = 5184 bits = 648 bytes`;
- canonical VM81 byte import/export: little-endian;
- ordered Pass 219 phase basis:
  `x,y,z,w,xy,yx,zw,wz`;
- ordered octonion surface:
  `hhs_exact_pass219_octonion_from_vm81`;
- exact integer phase arithmetic; no float authority;
- H36 exact closure identity;
- singleton VM81 mutation and inherited Hash72/Hash216 authority.

Existing Pass 167 contract specifies:

- signed PCM64 transport;
- exact 5184-bit audio snapshot;
- `x,y,z,w` phase roles;
- deterministic no-float pilot;
- reversible 81-sample PCM64 superframe;
- Sudoku/VM81 routing;
- Hash72/Hash216 receipt lineage.

Observed gap:

- the Pass 167 contract names `pcm81_snapshot_*`, `pcm81_serial_*`,
  phase, and pilot surfaces, but those implementation symbols are not present
  on current main.

I148 closes the reusable low-level serialization/hydration subset of that
gap without creating a second audio or VM81 authority.

## Canonical I148 wiring

```text
5184-symbol raw binary string
    ↕ exact LSB0 bit projection
648 canonical little-endian bytes
    ↕ inherited VM81 import/export
VM81[81] × uint64
    ↕ bit-preserving PCM64 carrier
PCM64 superframe[81]
    ↕ phase grouping
20 × {x,y,z,w} dual-stereo quads + pilot cell 80
    ↓ inherited ordered octonion surface
20 × {x,y,z,w,xy,yx,zw,wz}
    ↓ exact ternary/H36 coordinates
trit ∈ {-1,0,+1}
resonance36 ∈ [0,35]
half_turn ∈ {0,1}
```

### Raw bitstring order

For cell `c∈[0,80]`, bit `b∈[0,63]`:

```text
string_index = 64*c + b
character = '1' iff VM81.word[c] bit b is set
```

This is LSB0 inside each 64-bit cell and ascending cell order.

### Dual stereo mapping

Cells `0..79` form 20 ordered phase quads:

```text
quad q:
  x = cell 4q+0
  y = cell 4q+1
  z = cell 4q+2
  w = cell 4q+3

stereo A = (x,y)
stereo B = (z,w)
```

Cell `80` remains the independent pilot/carrier cell.

The grouping is a reversible transport view; it does not replace the inherited
Pass 167 sector registry.

### Ternary/H36 hydration

For each inherited phase `p∈[0,71]`:

```text
trit        = (p mod 3) - 1
resonance36 = p mod 36
half_turn   = floor(p/36)
p           = resonance36 + 36*half_turn
```

Therefore the H36 coordinate pair preserves the exact phase value.

### PCM64 rule

The lossless PCM carrier preserves the exact 64-bit word pattern for every
VM81 cell. No normalization, mix, gain, trigonometric approximation, or float
is allowed on the reversible carrier path.

A separately derived harmonic monitor waveform MAY map exact trinary/H36
coordinates to signed PCM64 amplitudes, but that monitor is not reversible
authority and cannot substitute for the 81-sample carrier.

## Required implementation

1. exact C/C++ raw-bitstring ↔ VM81 ↔ PCM64 ABI;
2. 20-quad dual-stereo mapping + pilot;
3. inherited octonion surface per quad;
4. exact ternary/H36 phase coordinate recovery;
5. deterministic integer-only derived resonance waveform;
6. Python mirror/reference implementation;
7. public registration and mandatory serialization guard binding;
8. exact positive/negative/round-trip tests;
9. exact logical-work/throughput-count benchmark;
10. normative contract and formal documentation;
11. dependency-scoped workflow;
12. restart/evidence seal;
13. ready PR, merge, verify main.

## Negative gates

- bitstring length other than 5184;
- any character other than ASCII `0` or `1`;
- host-endian substitution;
- loss of any of the 5184 source bits;
- cell reorder;
- x/y or z/w stereo reorder;
- ordered `xy/yx` or `zw/wz` collapse;
- invalid ternary value;
- invalid H36 resonance/half-turn reconstruction;
- pilot substitution;
- PCM carrier normalization or clipping;
- float/double in canonical C/C++ surface;
- new VM81 mutation authority;
- new Hash72/Hash216 commit authority.

## Status

- reconciliation: COMPLETE
- restart checkpoint: THIS COMMIT
- implementation: PENDING
- validation: PENDING
- merge: PENDING

## Exact next action

Implement the additive exact C/C++ and Python bridge, register it in the
cumulative exact ABI, then run only the I148 + inherited octonion/H36/cross-modal
dependency frontier.
