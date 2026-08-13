# Pass 215 Iteration 17 — Scalable RoPE Certified Greedy Continuation

Iteration 17 removes Iteration 16's fixed direct trigonometric argument ceiling from the certified RoPE executor without introducing floating point or a pi approximation.

For |angle| <= 8 the executor preserves the frozen Iteration 16 direct Taylor/Lagrange path exactly. Larger RoPE angles are repeatedly halved as outward-rounded dyadic intervals until |x| <= 1/8. Sine and cosine are enclosed with the inherited 40-term rational Taylor recurrences and explicit Lagrange remainders, then reconstructed using exact double-angle identities. Unit-range intersection is used only as a mathematically valid enclosure tightening step.

The contracted authenticated workload remains `Hello world!` on `ggml-org/tiny-llamas/stories15M-q4_0.gguf` with SHA-256 `6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04`.

The workload performs seven consecutive complete 32,000-logit certifications and seven true-greedy appends at 256-bit dyadic precision. The first three transitions must reproduce Iteration 16 exactly. At least one later argmax must be certified from a hidden state whose RoPE computation used the new range-reduced path. Symbolic and interval K/V caches remain persistent and the original four-token prefix is never replayed after initialization.

The evidence records exact per-step strict margins, logit interval widths, K/V reuse, Q8 projection work, range-reduction call counts, halving/reconstruction counts, and whether each selected state depended on range-reduced RoPE.

This remains bounded benchmark authority. It does not authorize probabilistic sampling, unbounded generation, arbitrary sequence-length forward authority, adaptive-precision authority, canonical floating point, dense-forward replacement, runtime mutation, canonical mutation, or migration.
