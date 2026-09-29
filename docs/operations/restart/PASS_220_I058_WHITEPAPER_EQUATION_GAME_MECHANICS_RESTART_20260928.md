# Pass 220 I058 — White-Paper Equation Game Mechanics Restart

Date: 2026-09-28

## Frozen parent

I057 is frozen on authoritative `main`:

- merged PR: #650
- merge commit: `10a215a78a215a72636c6cbd78065778ae5a8f9c`
- frozen simulation/render source: `examples/ParticleSimulation.html`
- frozen schema: `HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1`

I058 is additive and MUST NOT rewrite the I057 baseline.

## Branch

- branch: `pass220/i058-whitepaper-equation-game-mechanics-20260928`
- merge target: `main`
- purpose: lower repository-authorized white-paper equations into exact,
  typed game-mechanics descriptors while preserving equation-status boundaries.

## Source authority

- `whitepapers/HOLOFRACTAL_HARMONICODE.md`
- `docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md`
- `docs/whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md`
- `docs/whitepapers/HARMONICODE_Q144_H36_HOLOFRACTAL_RELATIVISTIC_GAME_ENGINE_THEOREM.md`
- existing I041 exact constructor:
  `hhs_runtime/hhs_pass220_holofractal_relativistic_game_engine_v1.py`

## Equation-status policy

The I058 runtime preserves the repository vocabulary:

- `CANONICAL_VERBATIM`
- `DEVELOPMENT_VERBATIM`
- `EXECUTED_EXACT`
- `HHS_NATIVE_SEMANTIC`
- `REFERENCE_ONLY`

Cross-status substitution is forbidden.

The indivisible boundary `B` and reference relativity are manifest entries
with `runtime_lowering=false`.

## Implemented exact game mechanics

1. **Reciprocal macro pair**
   - `P²=pq+2P/(p+q)`
   - `P²-pq=1`
   - licensed nonzero-denominator scalar projection:
     `p=P-1`, `q=P+1`
   - default witness: `P=3,p=2,q=4`

2. **5,184 world coordinate**
   - inherits I041 H36 mapping
   - `144*36=81*64=72*72=5184`

3. **Q144 clock**
   - `q144=tick mod 144`
   - reciprocal half turn `(q+72) mod 144`
   - inherits I041 Bott/quartic projection descriptors

4. **Integer translation pair**
   - `m²-m=m_pass`
   - exact odd-square discriminant
   - `m_pos+m_neg=1`
   - default witness: `m_pass=6 -> (3,-2)`

5. **GFE reciprocal residual**
   - `Phi(G)+Phi(G^-1)=G+G^-1-2=(G-1)²/G`
   - default calibration `alpha=5/4 -> 1/20`
   - exact gameplay potential descriptor only; no physical-energy authority

6. **Phase region**
   - `rho²=1-kappa`
   - exact rational radius-squared
   - trinary sign branch
   - no exact-path square-root evaluation
   - default `kappa=3/4 -> rho²=1/4`

7. **Candidate transition witness**
   - ordered `previous72 + current72 + receipt72`
   - exact Hash72 alphabet/length validation
   - no canonical Hash216 minting authority

## Authority boundary

I058 exact frames require:

```text
host_float_arithmetic_used_by_exact_frame = false
probability_used = false
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
```

Reference relativity is projection-only and is not promoted to canonical physics.

## Files changed

- `hhs_runtime/hhs_pass220_whitepaper_equation_game_mechanics_v1.py`
- `tests/pass220/test_hhs_pass220_i058_whitepaper_equation_game_mechanics_v1.py`
- `hhs_runtime/hhs_service_registry_v1.py`
- `docs/pass220/PASS_220_I058_WHITEPAPER_EQUATION_GAME_MECHANICS.md`
- `.github/workflows/pass220-i058-whitepaper-equation-game-mechanics.yml`
- this restart record

## Commits before checkpoint

- `413ea250834d2572923bdfa299a31f7e29c31bbc` — I058 runtime
- `ac04edf1eaec389158f42ac453edde8e09bec6c9` — I058 tests
- `2d7f07d6520a87e99877699e18cba97ef128ffd4` — service registry
- `04ef87cd3e85f3e343b4227ad9cdaa5ddfc6e9d6` — documentation
- `9e5881a68c4b53a57a6e61b56595659eecf904f3` — exact-head CI

## Validation intent

Dependency-scoped CI must:

- compile the I058 runtime/test;
- run I058 exact mechanics tests;
- rerun I041 exact game-engine tests;
- rerun frozen I057 ParticleSimulation tests;
- enforce white-paper status separation and authority boundaries.

## Next action

Open the PR, inspect exact-head CI, and repair-forward only I058-attributable
failures. When green, freeze I058 before building the browser projection adapter
that feeds declared I058 mechanics into the frozen I057 renderer.
