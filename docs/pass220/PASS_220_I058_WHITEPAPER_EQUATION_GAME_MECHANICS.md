# Pass 220 I058 — White-Paper Equation Game Mechanics

## Status

Additive game-mechanics layer over the frozen I057 canonical
`examples/ParticleSimulation.html` baseline and the existing I041 exact
game/render projection constructor.

I058 does **not** reopen or rewrite I057.

## Authoritative source chain

I058 is derived from repository-visible sources:

- `whitepapers/HOLOFRACTAL_HARMONICODE.md`
- `docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md`
- `docs/whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md`
- `docs/whitepapers/HARMONICODE_Q144_H36_HOLOFRACTAL_RELATIVISTIC_GAME_ENGINE_THEOREM.md`
- `hhs_runtime/hhs_pass220_holofractal_relativistic_game_engine_v1.py`
- frozen renderer/simulation baseline: `examples/ParticleSimulation.html`

The compendium's equation-status vocabulary is executable policy:

- `CANONICAL_VERBATIM`
- `DEVELOPMENT_VERBATIM`
- `EXECUTED_EXACT`
- `HHS_NATIVE_SEMANTIC`
- `REFERENCE_ONLY`

Natural-language similarity does not authorize cross-status substitution.

## Non-reduction boundary

The indivisible exact boundary `B` remains `CANONICAL_VERBATIM`.

I058 records its source identity and explicitly sets:

```text
runtime_lowering = false
```

I058 does not split, independently solve, commute, simplify, or reinterpret
`B`.

The reference relativistic metric and drift expressions likewise remain
`REFERENCE_ONLY`:

```text
ds² = -c² dt² + dx² + dy² + dz²
tau = sqrt(1-v²/c²)
gamma = 1/tau
R = tau²
```

They may label a game/render projection, but I058 does not grant them
canonical HHS physics authority.

## Exact mechanics lowered in I058

### 1. Reciprocal macro actor pair

The licensed scalar projection is:

```text
P² = pq + 2P/(p+q)
P² - pq = 1
p+q = 2P
pq = P² - 1
```

On a legal nonzero denominator branch the exact paired roots are represented
as:

```text
p = P - 1
q = P + 1
```

The default calibration:

```text
P = 3
p = 2
q = 4
pq = 8
P²-pq = 1
2P/(p+q) = 1
```

This becomes the `reciprocal_actor_pair` mechanic. The order `p,P,q` is
retained.

### 2. Exact 5,184 world address

I058 inherits the exact I041/H36 coordinate constructor:

```text
144*36 = 12*12*3*12 = 81*64 = 72*72 = 5184
```

A game tick maps to one exact address:

```text
linear5184 = tick mod 5184
```

The coordinate simultaneously exposes Q144/H36, VM81/operation64,
Hash72 row/column, ordered phase 8x8, and harmonic-rule64 projections.

### 3. Q144 phase clock

The exact clock is:

```text
q144 = tick mod 144
reciprocal(q144) = (q144 + 72) mod 144
```

I058 reuses the existing I041 Q144 constructor and quartic render descriptor.
No new phase arithmetic is invented.

### 4. Integer translation / spawn pair

For:

```text
m²-m = m_pass
D = 1 + 4*m_pass
```

I058 requires `D` to be an exact odd square and then constructs:

```text
m_pos = (1+s)/2
m_neg = (1-s)/2
m_pos + m_neg = 1
```

Default calibration:

```text
m_pass = 6
D = 25
s = 5
(m_pos,m_neg) = (3,-2)
```

This becomes the exact `translation_spawn_pair` mechanic.

### 5. GFE reciprocal potential descriptor

For admitted nonzero `G`:

```text
Phi(G)+Phi(G^-1)
= G + G^-1 - 2
= (G-1)²/G
```

The default repository calibration is:

```text
alpha = 5/4
alpha^-1 = 4/5
rho_alpha = 1/20
```

I058 exposes `1/20` as an exact reciprocal-potential descriptor. It is not
promoted to a claim of physical energy authority.

### 6. Phase region

I058 lowers:

```text
rho² = 1-kappa
```

as an exact rational `rho_squared` plus a trinary sign branch:

```text
+1 : rho² > 0
 0 : rho² = 0
-1 : rho² < 0
```

No square root is evaluated in the exact mechanics kernel.

Default calibration:

```text
kappa = 3/4
rho² = 1/4
branch = +1
```

## Frozen renderer boundary

I058 emits exact mechanics descriptors for the frozen I057 surface:

```text
HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1
examples/ParticleSimulation.html
```

I058 does not write into that file. A later projection adapter may consume an
I058 frame and feed permitted rendering variables into the frozen engine
without making renderer floats authoritative.

## Transition witness

I058 exposes a candidate-only ordered 216-character transition witness:

```text
previous72 + current72 + receipt72
```

Each component must use the Hash72 alphabet and be exactly 72 characters.

This does not mint canonical Hash216 state:

```text
canonical_hash216_authority = false
```

## Authority

The I058 exact frame explicitly carries:

```text
host_float_arithmetic_used_by_exact_frame = false
probability_used = false
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
```

Renderer/GPU floats remain presentation-only.

## Implementation surfaces

- runtime: `hhs_runtime/hhs_pass220_whitepaper_equation_game_mechanics_v1.py`
- tests: `tests/pass220/test_hhs_pass220_i058_whitepaper_equation_game_mechanics_v1.py`
- registry service: `pass220.whitepaper_equation_game_mechanics.self_test`

## Next integration step

After the exact mechanics kernel is green, build an I058 projection adapter
that consumes `HHS_PASS_220_I058_WHITEPAPER_GAME_FRAME_V1` and maps only
declared mechanic outputs into the frozen I057 browser surface. Do not edit the
I057 baseline to invent or approximate equation semantics.
