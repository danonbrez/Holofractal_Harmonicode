# Pass 215 Iteration 13 — Authenticated Terminal Model Head

Iteration 13 extends the frozen Iteration 12 four-token, six-block symbolic forward through the actual terminal head of the authenticated `stories15M-q4_0.gguf` model.

## Frozen parent

Iteration 12 closure commit: `7d2bfa13071692db4d9370a29b09711bd1424cd3`.

The six transformer blocks, their tensor bindings, causal-attention roots, adjacent block links, final `blk.5` output root, and complete Iteration 12 symbolic DAG are re-executed and must reproduce their frozen identities before the terminal head is admitted.

## Authenticated terminal topology

Repository/source evidence identifies an explicit terminal topology:

- `output_norm.weight`: 288-coordinate terminal RMSNorm weights, exact IEEE stored-value decoding with no Python-float canonical authority.
- `output.weight`: explicit `Q8_0` projection, shape `288 × 32000`.
- The output projection is not treated as tied to `token_embd.weight`.

Q8_0 has 32 logical weights per 34-byte block: a 2-byte binary16 scale plus 32 signed int8 codes. With width 288 there are nine blocks and 306 source bytes per vocabulary row.

## Exact Q8 execution semantics

Each Q8 output row is represented by a hash-addressed transition generator bound to:

- tensor source SHA-256,
- immutable descriptor root,
- row index,
- exact 288-coordinate symbolic input-vector root,
- exact semantic form `sum_j(exact_q8_weight[row,j] * input[j])`.

Binary16 scales are decoded using integer bit operations to exact reduced rationals. Codes are signed int8 integers. Selected real source rows are independently evaluated both as a flat 288-weight exact rational dot product and as nine block-factored exact inner dots followed by exact scale multiplication; the two paths must agree exactly.

The complete contracted projection materializes 32,000 row transitions for each of four positions:

- 128,000 Q8 row transitions,
- 36,864,000 logical weight products,
- 36,736,000 logical accumulation additions,
- 1,152,000 Q8 block-scale applications.

Including the already frozen six blocks, the contracted linear geometry is 199,424 row transitions, 60,751,872 logical products, and 60,552,448 logical additions.

## Authority boundary

A successful authenticated source run promotes only the following contracted statement: the exact symbolic full-model forward for the frozen four-token text witness reaches all vocabulary logits after all six model blocks and terminal RMSNorm.

It does **not** promote arbitrary sequence-length execution, autoregressive continuation, token choice, sampling, numerical transcendental approximation, canonical floating-point interpretation, dense-forward replacement, runtime mutation, canonical mutation, or migration.
