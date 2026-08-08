# Pass 215 Iteration 15 — Certified Exact Greedy Logit Selection

Iteration 15 inherits the exact frozen Pass 215 Iteration 14 closure and attacks one barrier only: replace deterministic Hash216-identity selection with a proven ordering by the actual terminal logit magnitudes for the authenticated `Hello world!` witness.

## Authority target

The source model and prompt remain frozen:

- `ggml-org/tiny-llamas/stories15M-q4_0.gguf`
- SHA-256 `6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04`
- prompt `Hello world!`
- token IDs `[1, 15043, 3186, 29991]`
- vocabulary size `32000`

Iteration 14 remains valid as a deterministic symbolic continuation benchmark, but its selection rule intentionally ordered Hash216 identities and did **not** represent numerical argmax. Iteration 15 does not reinterpret that earlier result. It adds a separate certified magnitude-comparison authority.

## Certified arithmetic

The authoritative comparator uses fixed dyadic intervals with denominator `2^256`. Every endpoint is an integer. Every operation rounds outward.

The four-token model path is replayed from authenticated GGUF tensors using:

- exact Q4_0/Q8_0 integer codes and exact binary16 rational scales;
- integer-ratio square-root bounds for RMSNorm and attention scaling;
- integer nth-root bounds for rational RoPE powers;
- rational Taylor enclosures with explicit remainder bounds for `exp`, `sin`, and `cos`;
- interval addition, multiplication, inverse, residuals, softmax, and SiLU;
- no Python float authority and no transcendental point value promoted as canonical.

The complete final-position vocabulary projection produces 32,000 outward intervals. Selection succeeds only when one candidate satisfies

`selected.lower > max(other.upper)`.

If the intervals overlap at 256 certification bits, the iteration fails closed. It must not fall back to Decimal, binary float, approximate argmax, Hash216 ordering, or probabilistic selection.

## Continuation

Once the true logit argmax is certified, exactly one selected token is appended through the frozen Iteration-14 incremental execution machinery. The inherited per-block K/V prefix cache must be reused and `prefix_hidden_rows_recomputed` must remain zero.

This iteration therefore targets one **true greedy** autoregressive transition, not general generation.

## Still outside authority

- arbitrary sequence length;
- unbounded or general text generation;
- probabilistic sampling;
- approximate transcendental point evaluation as authority;
- canonical float interpretation;
- dense-forward replacement;
- runtime mutation authority;
- canonical mutation;
- migration.

## Closure rule

The iteration closes only after:

1. cumulative Iterations 1–15 validation passes;
2. the authenticated model is SHA-256 verified;
3. complete 32,000-logit interval certification proves a strict argmax;
4. one greedy append executes with prefix/KV reuse;
5. an independent second process reproduces the same token and semantic roots;
6. the restart-state commit is exact-head replayed successfully.
