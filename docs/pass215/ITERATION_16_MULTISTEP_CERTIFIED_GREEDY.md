# Pass 215 Iteration 16 — Multi-Step Certified True-Greedy Continuation

Iteration 16 extends the one-step certified true-logit argmax from Iteration 15 into a bounded three-step greedy chain.

## Frozen parent

- Iteration 15 closure head: `7d58d29fa9690f4239b8e8f3ad30f34736f47f84`
- Iteration 15 closure tree: `d556c1bb07e62cefba8f45df9c6cf8978645cdc8`
- Parent selected token: `450 / ▁The`
- Parent selection root: `aac3225975c44b9b761dd131afedfc01123a3c5da187f76bd9de5c9bf2abee94`
- Parent append root: `f1757269ee3ed98a67434c799a89750da26dcaa11be9ce688a093d52febb5a75`

## Execution rule

The authenticated four-token prefix is reconstructed once in the symbolic DAG and replayed once in the 256-bit outward dyadic interval executor. Both per-block KV states are retained.

For each of three consecutive steps:

1. certify all 32,000 current logit intervals;
2. require one lower bound to be strictly above all competing upper bounds;
3. choose that true magnitude argmax;
4. append the selected token through only the new absolute position;
5. extend, rather than rebuild, both the symbolic and interval KV caches;
6. project the next complete 32,000-logit state.

Step zero must reproduce Iteration 15's `▁The` selection and its compatible append root exactly.

## Authority boundary

Promoted only if source and exact-head replay succeed:

- three consecutive complete logit-vector certifications;
- three consecutive strict true-logit argmax selections;
- three consecutive greedy append transitions;
- persistent symbolic and interval KV reuse;
- zero original-prefix replay after initialization.

Not promoted:

- probabilistic sampling;
- unbounded/general generation;
- arbitrary sequence-length transformer authority;
- canonical floating-point interpretation;
- approximate transcendental point authority;
- dense-forward replacement;
- runtime/canonical mutation or migration.
