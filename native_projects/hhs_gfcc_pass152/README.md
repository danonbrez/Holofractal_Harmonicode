# HHS Golden Fractal Correspondence Constructor

Contract: `HHS-P152-GFCC`  
Pass: `152`  
Subsystem: `GFCC`

GFCC constructs one exact, dependency-preserving correspondence graph and projects that graph into VM81 state, Hash72 witnesses, Hash216 indices, generated C tables, graphics shaders, fixed-point geometry, collision constraints, receipts, and deterministic replay.

## Authority partition

- **Python** validates the canonical specification, constructs the dependency graph, generates C and shader sources, invokes compilers, aggregates manifests and receipts, coordinates replay, and packages the inherited repository.
- **Native C** owns runtime parameter loading, shell closure, VM81 construction, inherited Hash72 and Hash216 invocation, fixed-point transforms, collision admissibility, correction enforcement, deterministic stepping, typed validation, and native replay checks.
- **Shaders** are presentation-only projections. They cannot mutate VM81 state, decide canonical collision admissibility, generate authoritative Hash72 receipts, or alter Hash216 identity.
- **VM81** remains execution and transition authority.
- **Hash72** remains the symbolic witness and receipt surface.
- **Hash216** remains the indexed identity, integrity, and provenance surface.

## Exact symbolic core

```text
a² = 1
b² = 2
c² = b² + a² = 3
d² = c² + b² = 5
e² = d² + c² = 8

numerator   = e² = 8
denominator = a² + a² + (c² - a²) = 4
residual    = numerator / denominator - b² = 0
```

Finite scale is retained as the exact ratio `F(n+1)/F(n)`. The representative stage is `34/21`. The symbolic limits remain polynomial roots:

```text
Phi: x² - x - 1 = 0, positive root
Eta: 2x² - 1 = 0, positive root
```

No floating-point value is canonical authority. Shader floats record exact source, rounding policy, and float32 bit pattern.

## Delta369 and VM81

`Delta369` retains the nonary ring, both indexing conventions, the 3×3 qudit, decimal projection boundary, golden correspondence state, phase structure, and the four logical coordinates `(x, y, phase, scale_depth)`.

VM81 uses the exact reversible map:

```text
i = 9r + c
(r, c) = divmod(i, 9)
```

All 81 assignments are validated exhaustively.

## Build commands

```bash
make test-gfcc
make test-gfcc-negative
make test-gfcc-replay
make verify-gfcc
make verify-pass-152
make package-pass-152
```

Direct Python commands use `PYTHONPATH=python python -m hhs_gfcc.cli <command> --repo . --output json`. Output modes are `json`, `jsonl`, `text`, and `markdown`.

## Native and shader outputs

- `dist/libhhs_gfcc.a`
- `dist/libhhs_gfcc.so`
- `dist/hhs-gfcc`
- `dist/test_hhs_gfcc`
- `dist/hhs_gfcc_shader.spv`
- `dist/hhs_gfcc_collision_field.spv`

## Verified release

- GFCC positive matrix: `23 / 23`
- GFCC negative matrix: `25 / 25`
- Continuous receipt ledger: `18 / 18`
- Source manifest: `74 / 74`
- Inherited Pass 151 and Pass 152 gates: passed
- Native C and ASAN/UBSAN: passed
- GLSL/SPIR-V compilation, validation, disassembly, and reflection: passed
- Python/C VM81, Hash72, and Hash216 projection: matched
- Deterministic replay: `MATCH`
- Incomplete obligations: none

Final archive:

```text
hhs_pass_152_golden_fractal_correspondence_constructor_full_inherited_pass_history_nucleus.zip
```

Terminal classification:

```text
GOLDEN_FRACTAL_CORRESPONDENCE_CONSTRUCTOR_VERIFIED
```
