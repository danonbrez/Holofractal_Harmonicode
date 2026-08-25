# HHS Pass 219 — Orthogonal Glyph VM81 Circuit Membrane Repair

**Repair identifier:** `HHS-P219-ORTHOGONAL-GLYPH-VM81-CIRCUIT-1.21.1`  
**Supersedes:** the membrane-local `24 × 216 = 5,184` execution interpretation in 1.21.0  
**Mode:** `APPEND-ONLY — REPAIR FORWARD — NO FROZEN HISTORY REWRITE`  
**Canonical mutation authority:** unchanged; VM81 remains the only canonical admission/commit authority.

## 1. Reason for repair

The initial 1.21.0 implementation preserved the verbatim source and ordered phase state but incorrectly used precomputed scalar phase residues as the lane execution substrate and treated 24 Hash216-width lane identities as a membrane-local 5,184 partition.

That is not the inherited HHS execution model.

The repository already establishes:

- HARMONICODE source as the syntax/constraint-graph authority;
- VM81 as the exact execution/admission authority;
- `64 × 81 = 5,184` as the permanent operation/cell fabric;
- `operation64 = left_basis8 × 8 + right_basis8` as the ordered `8 × 8` phase-product crosswalk;
- Pass 188 G243/Bott transitions over every permanent VM5184 address;
- Pass 189 41-coordinate contextual hydration over the same permanent/G243 address;
- Pass 159 source → CST → AST → type environment → constraint graph → HIR → VMIR lowering;
- the Pass 219 1.20 monolithic source as one aggregate equality-chain constraint that raw packets cannot self-promote to canonical proof.

The C++ membrane therefore SHALL expose and compose those inherited authorities rather than substitute host scalar arithmetic for them.

## 2. Reflexive source/program law

The verbatim equation is simultaneously:

1. the source program whose topology is lowered into the runtime circuit; and
2. the constraint surface that the resulting runtime state must satisfy.

The required correspondence is:

```text
verbatim HARMONICODE source
        ↕
typed source / ordered constraint graph
        ↕
source-defined VM81 thread topology
        ↕
ordered x,y,z,w,xy,yx,zw,wz circuit
        ↕
VM5184 + G243 + kappa41 hydration
        ↕
candidate-state witnesses
        ↕
the same monolithic equality chain
```

A projected numerical collision is not native identity. The complete ordered provenance and source-defined constraints remain attached to the state.

## 3. Orthogonal glyph lanes

The 24 glyph registry remains:

```text
P, t, p, q, ∆, m, b, c, u, s,
x, y, z, w, xy, yx, zw, wz,
At, f, Bt, A, B, a²
```

Each glyph lane is now a **complete equation realization**, not a 216-coordinate slice.

Every lane contains:

```text
full 348-byte verbatim source
+ exact HHSExactVM81Frame
+ x/y/z/w VM81 cell selectors
+ complete ordered 8×8 octonion surface
+ 64 operation-thread views
+ 81 VM81 cells per operation thread
+ G243/Bott coordinates and replay
+ kappa41 contextual hydration coordinates
+ source/AST/constraint-graph/VMIR/proof lineage
+ Hash216 lane identity
```

Hence each lane contains the complete native permanent fabric:

```text
64 operation threads × 81 VM81 cells = 5,184 positions
```

The 24 glyph lanes are orthogonal realizations **above** that complete per-lane substrate.

## 4. Source-defined 64-thread allocation

The frozen 348-byte native 1.20 equation contains:

```text
34 matched parenthesis shells
15 literal '=' characters
```

Each literal `=` character is retained as an equality half-gate, so a source `==` contributes two ordered half-gates.

The source therefore contributes:

```text
34 shell threads
+ 15 equality-half-gate threads
= 49 source-structure threads
```

The permanent VM81 operation fabric has 64 ordered threads, leaving:

```text
64 - 49 = 15 VMIR-derived threads
```

The membrane discovers and validates the 34/15 topology directly from the frozen verbatim bytes. It does not reuse the older Pass 168 source-specific `28 + 12 = 40` count as though the current equation had identical punctuation.

For every thread `k ∈ [0,63]`:

```text
left_basis8  = k / 8
right_basis8 = k % 8
operation64  = k
```

and every cell `c ∈ [0,80]` maps through the inherited exact ABI:

```text
VM5184(c,k) = c × 64 + k
```

Thus the source-structure thread and the ordered octonion product thread are two views of the same permanent operation identity.

## 5. Required runtime execution

A lane SHALL derive its phase surface from its VM81 frame using:

```text
hhs_exact_pass219_octonion_from_vm81
```

and SHALL validate the complete 64-product surface.

For all 5,184 `(cell81,operation64)` positions the membrane SHALL:

1. encode and decode the permanent address with the exact VM5184 ABI;
2. decode the corresponding Pass 188 G243 projected address;
3. execute and replay the inherited Pass 188 Bott transition;
4. encode and decode the Pass 189 contextual `(cell81,operation64,g243,kappa41)` address;
5. preserve the actual VM81 bit belonging to that operation thread and cell;
6. bind those results into the thread Hash216 identity.

No host-language scalar multiplication or independent phase calculator may replace this path.

## 6. `xy = zw = a² = ∆` binding

The source-level invariant remains:

```harmonicode
xy = zw = a²
and
a² = ∆
```

The repair distinguishes native identity from exact projections:

- `xy` and `zw` are derived by the ordered VM81/octonion circuit;
- `a²` and `∆` are carried as exact canonical projections and must agree exactly;
- an `xy/zw` phase-projection mismatch is immediately inconsistent;
- equality across the ordered-phase and symbolic/BigInt domains is **not** manufactured by comparing host integer fields.

The cross-domain native binding remains part of the monolithic source constraint and therefore requires the inherited Pass159 → VM81 exact proof path.

Accordingly the C++ result explicitly retains:

```text
cross_domain_binding_requires_vm81 = true
native_shared_invariant_proven = false
canonical_proof = false
```

for raw/candidate membrane evaluation.

## 7. Orthogonal contradiction equations

Contradictions are derived from complete native lane states, not scalar phase bytes alone.

For each lane pair, the membrane compares:

```text
64 VM81 thread identities
64 ordered octonion product identities
81 VM81 words
monolithic equality-edge state
semantic-family state
lowering/proof-stage state
candidate-state Hash216 identity
```

A difference produces a `ContradictionEquation` with its own Hash216 identity.

The global contradiction graph is the deterministic reduction of:

```text
source-topology Hash216
+ 24 complete lane Hash216 identities
+ ordered contradiction-equation Hash216 identities
+ exact invariant-projection state
```

Parallel scheduling is nonauthoritative; reduction order remains deterministic.

## 8. Authority boundary

This membrane performs candidate computation and exact structural verification only.

It does not:

```text
commit VM81 state
mint authoritative Hash72 receipts
promote a raw monolithic packet to PROVEN
replace Pass159 source/constraint-graph lowering
replace the inherited G243/Bott or contextual hydration runtimes
```

Canonical closure remains the inherited exact source → constraint graph → VMIR → VM81 admission → Hash72 receipt → Hash216 lineage path.

## 9. Validation requirements

The repair is falsified if any of the following occur:

- the full 348-byte source is not retained per glyph lane;
- the current source does not yield exactly 34 shell and 15 equality-half-gate threads;
- `49 + 15 != 64` or `64 × 81 != 5,184`;
- any VM5184 address fails exact encode/decode round trip;
- any Pass 188 G243 transition fails replay;
- any Pass 189 contextual address fails encode/decode round trip;
- the 64-product octonion surface is not derived from the lane VM81 frame;
- `xy` and `yx` or `zw` and `wz` are silently collapsed;
- `a²` and `∆` unequal exact projections are accepted;
- a cross-domain `xy=zw=a²=∆` proof is claimed from scalar comparison alone;
- thread scheduling changes lane or global Hash216 identities;
- the C++ membrane gains canonical mutation/receipt authority.

## 10. Canonical authority lineage and implementation checkpoint

This repair branch is rooted directly in canonical `main` at:

`f5d8fdc014d888f93c0d85d40d2a2c0c198eefdf`

The governing inherited authority is repository history already contained in that mainline, including:

```text
Pass 159 merged HARMONICODE/VM81 toolchain
8e7ffb22286f5b6b377c778276c333607a7c2a03

Pass 168 VM81 5,184-cell / 64×81 parameter circuit contract
eb88a4b88ab8c598458c0e48c0f4f9db77f81654

Pass 169 whole-expression algebra enforcement / VM81 exact symbolic authority
62e296024b27ff3209e3ef2ac4a2d565e03296ca

Pass 186 x86_64 ordered noncommutative VM81 ABI
fd42056c22071d290945b02efe3a5752aaa3d737

Pass 188 executable Bott/G243 runtime
c77e3feef42448a111d8b8912a1d1cb157d51925

Pass 189 executable HQLH/kappa41 contextual hydration runtime
a1a55a4f621ff3678f5af81119439e9558cf9db4

Frozen Pass 219 I118 ancestor
e87bc42b17c03ff98f691838b8d573a5bdf46ff2
```

The earlier `85c237023e778e655f38f6363bab7f08907fa9b2` checkpoint records validated 1.19/1.20 implementation work, but it is **not an ancestry or canonical-authority root for PR #315**. Its implementation was carried repair-forward onto the direct-main branch without rewriting either history.

Implementation branch:

`agent/pass219-orthogonal-glyph-parallel-membrane-1-21`

Pull request:

`#315`

Historical workflow run `32375615525` remains evidence for the earlier executable 1.21.1 checkpoint. Current closure must be revalidated on the main-aligned repair head; historical green evidence is not promoted into validation of later commits.
