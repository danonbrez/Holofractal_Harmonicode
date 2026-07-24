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

The canonical graph preserves:

```text
a² = 1
b² = 2
c² = b² + a² = 3
d² = c² + b² = 5
e² = d² + c² = 8
```

The numerator and denominator shells close independently:

```text
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

From the repository root:

```bash
make test-gfcc
make test-gfcc-negative
make test-gfcc-replay
make verify-gfcc
make verify-pass-152
make package-pass-152
```

Direct Python commands use:

```bash
PYTHONPATH=python python -m hhs_gfcc.cli validate-spec --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli build-parameters --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli generate-c --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli generate-shaders --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli generate-collisions --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli compile-native --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli compile-shaders --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli test --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli replay --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli verify --repo . --output json
PYTHONPATH=python python -m hhs_gfcc.cli package --repo . --output json
```

Output modes are `json`, `jsonl`, `text`, and `markdown`.

## Native outputs

The native compiler produces:

- `dist/libhhs_gfcc.a`
- `dist/libhhs_gfcc.so`
- `dist/hhs-gfcc`
- `dist/test_hhs_gfcc`

The shader compiler produces validated SPIR-V artifacts for the fragment projection and collision-field visualization.

## Completion boundary

The successful terminal classification may be emitted only after all inherited, exactness, shell, Delta369, VM81, Hash72, Hash216, native C, shader, collision, receipt, replay, manifest, and archive obligations are execution-verified.

Until that complete gate passes, the subsystem must report a non-success classification and must not emit `GOLDEN_FRACTAL_CORRESPONDENCE_CONSTRUCTOR_VERIFIED`.
