# Pass 215 Iteration 5 Restart Record

- Branch: `agent/pass215-transformer-ingestion-benchmark`
- Parent/frozen Iteration 4 head: `ce35117dd1b54574f2fc98e0254dee0ddcf0e518`
- Parent/frozen Iteration 4 tree: `a1fb44e5c43e4d504a71183ba6eb01405d730293`
- Pull request: `#172` targeting `main`
- Iteration 4 suite root: `14de39b3b326eb64bbac5d8be829c289c4a5e1f39b842bfdba59b46fea2c9acb`
- Iteration 4 terminal evidence root: `0462738157042bbd2903ed666a3e05dbc1e27c8a43ea5d2544de9b0c174f87bf`
- Iteration 4 receipt: `2SrZvFdR/*41!b++dH9qxM1IrUZMuwuRZmpNw4yl8>QYI(LA9B65A<auqlwyWoi97onfMeMc`

## Implemented in this checkpoint

1. Canonical no-float exact-expression algebra.
2. Exact RMSNorm reciprocal-square-root substrate.
3. Exact RoPE rational-power plus sine/cosine substrate.
4. Exact attention scaling.
5. Exact exponential/softmax closed-form normalization.
6. Exact sigmoid and SiLU closed-form operators.
7. Real-model bridge from the authenticated Iteration 4 Q4_0 factored `blk.0.attn_q.weight` output.
8. Hash216 output/evidence roots and Hash72 receipt chained to the frozen Iteration 4 receipt.
9. Deterministic cross-process replay validation.
10. Dependency-scoped positive and negative controls with cumulative Iterations 1–4 validation retained.

## Authority boundary

Benchmark authority remains active. Runtime mutation authority, canonical mutation, and migration remain false. Numeric or approximate transcendental evaluation remains false. Full transformer-layer forward and dense-forward replacement remain false.

## Restart action

Run `bash scripts/run_pass215_iteration5_validation.sh`, then execute the registered Iteration 5 workflow against the authenticated GGUF in independent processes. Accept the checkpoint only if the workflow succeeds on the exact committed head and reports identical nonlinear suite/evidence/receipt roots.
