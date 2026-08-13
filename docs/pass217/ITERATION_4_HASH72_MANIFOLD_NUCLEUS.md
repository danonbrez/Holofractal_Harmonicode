# Pass 217 Iteration 4 — Hash72 Manifold and Immutable Nucleus

## Outcome

Iteration 4 continues from the already-merged reconciliation lineage rather than
replaying Iterations 1–3. The authoritative predecessor chain is now
repository-visible through Pass 216 and the Iteration 4 reconciliation commit,
while the Iteration 3 candidate artifacts remain byte-identical historical
inputs.

This iteration adds the contracted **non-promotional Hash72 manifold and
immutable Lo Shu/phase nucleus validation layer**. It does not select a
canonical Genesis ROM, mint Hash72 or Hash216 transition authority, generate
the physical Golay ROM, mutate the protected VM81 C runtime, begin migration,
or begin Pass 219 runtime implementation.

## Bound authority

- Iteration 4 base main: `3b55da5e8aa67491f113d1b9e9c7e481aeb1e18c`
- Pass 216 merge: `f10e453c5d7c7467cf5e57f6452958491fe763ad`
- Iteration 3 candidate: `947be39fd67700f307ff80d96c3a10c3acaa29cc`
- Iteration 4 reconciliation: `724e91c5fb1009cefc52778c3e73338257b2814c`
- Protected VM81 runtime blob: `362cd6e892ae66024333b111aec83f12023fdce3`
- Iteration 3 candidate SHA-256: `97379c7ae7cdaebd8031a3a3fb58559c967b361b360c7db34ec096acabfc8fe8`
- Iteration 3 address-map SHA-256: `2f8d8a23114b87f2dbe91f3d302ef089b750f9d91f533d744a4524e907717f5f`

Historical Iterations 1–3 hold fields remain intact as provenance. Iteration 4
supersedes the old predecessor hold only in its new authority record; no prior
artifact is rewritten or regenerated.

## Hash72 manifold validation

The validator reuses the inherited canonical 72-symbol alphabet and the frozen
wrapped operators:

```text
x = ( 0,+1)
y = (+1, 0)
z = (+1,+1)
w = (+1,-1)
```

For each direction it proves:

- exact order 72;
- one-step bijection across all 5,184 coordinates;
- 72-step closure;
- exact +1/-1 inversion;
- 72 distinct coordinates for representative boundary/interior anchors;
- deterministic one-step and anchor-orbit roots.

Frozen roots:

- Hash72 matrix: `6c0b2e9e354e8d7eb17a746d01c157b19aa95b58296884126cdf5bef7998e286`
- anchor orbits: `556a7828594f8a56cfec8d8f3af473330fffcae4f24c44ffc37616c681e69f09`
- manifold: `c757bae150d9ab94485c680ec3143e715b674d35f445a72c6fb4ea2def6f7884`

## Immutable nucleus validation

The central 3×3 VM81 cells are frozen pointwise:

```text
30 31 32
39 40 41
48 49 50
```

with Lo Shu values and ordered phase channels:

```text
4/x   9/y   2/z
3/w   5/1   7/xy
8/yx  1/zw  6/wz
```

The validator compares all nine 64-bit shards against the deterministic
Iteration 3 candidate, preserving 576 exact support bits.

- nucleus identity root: `da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164`
- nucleus support root: `ac46211412784990e08e5cf0b80df5db381aad612a7ccd8aa816815a105b0294`

Any changed nucleus shard fails closed before later admission surfaces.

## Validation policy

Iteration 4 intentionally does **not** rerun global Pass 215 strict validation.
The already-green Iterations 1–3 artifacts are reused by exact authenticated
identity. The Iteration 4 workflow runs only the new dependency-scoped Python
compile, 13 focused tests, evidence rebuild, ancestry checks, and protected
runtime identity check.

## Claim boundary

This iteration proves the reconciled manifold/nucleus validation surface only.
Canonical ROM selection/admission, physical Golay materialization, migration,
authoritative Hash72/Hash216 transition minting, and Pass 219 runtime work
remain separate future authority transitions.
