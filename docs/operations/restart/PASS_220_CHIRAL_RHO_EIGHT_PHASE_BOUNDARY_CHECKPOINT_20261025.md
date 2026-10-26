# Pass 220 — Chiral rho / eight-phase boundary checkpoint (2026-10-25)

## Restart identity
- Repository: danonbrez/Holofractal_Harmonicode
- Branch: `pass220/standalone-adaptive-device-resolution-20261023`
- Merge target: `main`
- Inherited source checkpoint: `e006c753103d38f19f7798944576ed4d7f59bb98` (verify actual branch head before subsequent edits)
- Modified paths in this checkpoint: this documentation file only
- Runtime / renderer / particle mechanics modified: **none**
- Validation: preservation of user expression, algebraic consistency analysis, documentation inspection; no physics or native proof tests asserted
- Environment: connected GitHub source interface; no Android/WebGL device
- Next action: inspect exact native ordered tensor evaluator, HNAN/Larone and eight-group boundary interfaces via REPOSITORY_INDEX.md and dependency tree; add typed proof obligations before any runtime admission
- Blocker: no established native rewrite justifying the chiral linear trace, infinity-to-phase mapping, or hydrogen-spectrum match.

## User-authored candidate equation (preserve original syntax and ordering verbatim)

```text
t is rho T^(List(1,2,3)^3/List(1,2,3)^(-1)*List(1,2,3)^(-1)/List(1,2,3)^2*List(1,2,3)^(-2)/List(1,2,3)^(-1))^2*72==(t^3*72)/List(-1,0,1)==List(72*(t^3-t),ComplexInfinity,72*(-t^3+t))==u^72
```

User interpretation: volumetric expansion collapses into discrete phase rotation by a 1D chiral singularity; `t → ρ` is the density operator; opposite chiral boundaries share a linear trace; (u^{72}) is the periodic carrier. Candidate nominal closure metadata `Δe=0, Ψ=0, Ω=true` remains a **claim to prove for this expression**, not a minted receipt.

## Evaluation boundaries and explicit proof obligations

1. **Ordered exponent algebra:** Under a scalar commutative, left-associative interpretation for nonzero list members, exponent sequence `3 - (-1) + (-1) - 2 + (-2) - (-1) = 0`, so `T^0` (then squared) gives unity and the first block reduces to `72`. This is a *conditional comparison*, not permission to reorder native HNAN tensor operations. Confirm how the native evaluator types `List`, power, division, multiplication and exponent precedence.
2. **The first list has no zero:** `List(1,2,3)` allows scalar reciprocal comparisons; the *chiral* `List(-1,0,1)` includes a zero division. Native admission must represent its singular cell symbolically, without silently coercing it to a finite number.
3. **Chiral division comparison:** Conventional elementwise division `72*t^3 / [-1,0,1]` yields `[-72*t^3, undefined, +72*t^3]` for nonzero t, **not** `[72*(t^3-t), ComplexInfinity, 72*(-t^3+t)]`. The asserted equality is therefore a **native ordered rewrite/projection requiring an explicit contract**, not a scalar arithmetic identity.
4. **Boundary sign discrepancy:** User-supplied exact equality has `[72*(t^3-t), ComplexInfinity, 72*(-t^3+t)]`, whereas accompanying narrative describes `[72*(t^3+t), ComplexInfinity, 72*(-t^3+t)]`. Keep both distinguishable; do not silently choose a sign or modify the authoritative written expression.
5. **Linear trace:** For the written exact `List`, summing the two finite entries gives **zero**: `72(t^3-t)+72(-t^3+t)=0`. For the separate narrative `(+t)` pair, their sum gives `144t`. An averaging operator would give `72t`, not `144t`. These require a resolved native ordered rule.
6. **Phase closure:** `u^72=1` is the existing carrier closure. Mapping any unbounded chiral result to a bounded cyclic representative must specify a modular address/phase-homomorphism, provenance and treatment of the singular center. Never assert `144ρ == u^72` or `0 == u^72` as ordinary equalities without a typed mapping.
7. **Physical meaning:** Distinguish particle number, number density and energy density by type and units before interpreting `ρ` and `ρ^3`. Do not infer mass creation or thermodynamic closure without the underlying model's full constraints and checked evidence.
8. **Eight phase sectors:** Represent `C_i(S_i,Φ_i,∂G_i,N_i)` as **eight slots for repository-established native boundary equations** and one common global constraint; do not invent the eight actual equations, change the HNAN center gate, phase order, or native physics.

## Acceptance for subsequent implementation

- Preserve exact operator order, addressing, BigInt serialization and sample/event lineage.
- Demonstrate native legality of the typed map from chiral three-cell relation to eight-sector Larone/HNAN traversal, including zero/singularity handling.
- Use existing mechanics and existing groups. Boundary constraints restrict *admissible states*; no direct positions, velocities, hidden portal shaders, or separate atom engine.
- A hydrogen atomic projection is a **candidate use**; reproduce charge, energy levels and spectra against independent reference benchmarks before naming the candidate state a validated hydrogen model.
- Dependency-scoped negative tests: incorrect boundary signs; swapped ordered operands; division by center zero; non-admissible `u^72` mapping; broken prior-state identity; unauthorized particle mutation.
- Keep physics, collision 1.40, formation 1.25, color controls, audio schedule and optimized Liquid Light source unchanged pending a tested gated implementation.
