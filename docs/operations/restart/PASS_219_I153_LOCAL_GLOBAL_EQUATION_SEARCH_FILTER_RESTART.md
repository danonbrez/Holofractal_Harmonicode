# Pass 219 I153 — Local/Global Equation Search Filter Restart

## Repository state
- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ 94662cb6a6d4fe7b7310689a790af058cf554545`
- Branch: `agent/pass219-i153-local-global-equation-search-filter`
- Merge target: `main`
- Last implementation head before this checkpoint: `5e83245432133a507ff71edee474a6f3fe4fc441`

## Reconciled inherited equation authority

The user's local/global filter equation already exists byte-for-byte in the repository as:

`contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode`

Identity:

```text
bytes  = 348
sha256 = ac143798146d89a3fe932f39ccb4d612e4fb3e45c471abc1a8bbbebb0f9c0a6a
```

It is also embedded unchanged in:

`contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode`

Identity:

```text
bytes  = 632
sha256 = 3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53
```

I153 does not rewrite, duplicate, simplify, or re-parenthesize either inherited source.

## Implemented I153 semantics

I153 fixes:

```text
P = local state Hash216 / 5184-hydration parameter snapshot
```

The local snapshot is explicitly bound to:
- one nonzero exact integer `P`;
- `hydration_bits = 5184`;
- one declared Hash216 identity representation;
- the exact 348-byte equation source identity;
- the exact 632-byte combined whole-expression identity;
- the immutable I152 target/work/route cardinalities.

Supported Hash216 snapshot representations:
- `PASS150_HASH216_GENOME_ROOT_SHA256`
- `HASH216_THREE_HASH72_216_GLYPH`

The representation is declared, never guessed or silently converted.

## Fixed I152 cardinalities preserved

```text
target resolution      = 72^42 = 5184^21
working manifold       = 3*72^72
routes / target block  = 3*72^30
exhaustion ratio       = 81/7
```

P is local and does not resize any of these quantities.

## Search filter pipeline

```text
I152 block/route
  -> exact working-index reconstruction
  -> local P/Hash216 snapshot binding
  -> exact 348-byte UQCEL source binding
  -> exact 632-byte whole-expression source binding
  -> one shared global symbol-environment root
  -> inherited five gate offsets 96,240,266,274,285
  -> all five witness results true
  -> global environment complete
  -> cross-layer revalidation complete
  -> no local symbol shadowing
  -> survivor set
  -> downstream cost optimizer
  -> Pass169 authority still required before canonical admission
```

The filter does not produce gate truth. It consumes source-bound witness results and prunes candidates only.

## Implemented files

- `contracts/pass219/PASS_219_I153_LOCAL_GLOBAL_EQUATION_SEARCH_FILTER_1_0.json`
- `docs/pass219/PASS_219_I153_LOCAL_GLOBAL_EQUATION_SEARCH_FILTER_1_0.md`
- `hhs_runtime/pass219/local_global_equation_search_filter.py`
- `tests/pass219/test_pass219_i153_local_global_equation_search_filter.py`
- `benchmarks/pass219/pass219_i153_local_global_equation_search_filter_benchmark.py`
- `.github/workflows/pass219-i153-local-global-equation-search-filter.yml`
- this restart record.

## Bounded benchmark design

The benchmark constructs 4,096 valid I152 working routes under one local P snapshot and applies a deterministic five-bit synthetic gate pattern.

Expected exact counts:

```text
candidate_count = 4096
survivor_count  = 128
rejected_count  = 3968
candidate ratio = 4096/128 = 32
ratio_x1000     = 32000
```

The 32x ratio is expected to satisfy the I152 local `81/7` comparison.

This is bounded synthetic filter evidence only:
- synthetic gate results are not Pass169 truth;
- no full `72^42` exhaustion claim;
- no full `3*72^72` enumeration claim;
- no VM81, Hash72, or Hash216 authority promotion.

## Validation plan

The I153 workflow must:
1. verify inherited 348-byte and 632-byte source SHA-256 identities;
2. parse the I153 runtime and benchmark;
3. run I153 tests;
4. rerun dependency-scoped I152 fixed-cardinality tests;
5. rerun inherited I121.12 proof-preserving optimizer tests;
6. emit the bounded benchmark receipt;
7. enforce exact 4096 -> 128 filter counts and the 32x ratio;
8. verify canonical authority remains unchanged;
9. upload one immutable benchmark artifact.

Because a new file is added under `benchmarks/pass219`, the inherited I151 benchmark-history workflow is also expected to observe the new surface. On exact-main integration, its new accepted entry must be sealed into the cumulative JSONL history.

Current code blocker: none.
