# Pass 215 Iteration 6 Restart Record

- Branch: `agent/pass215-transformer-ingestion-benchmark`
- Parent/frozen Iteration 5 head: `e384058b1dedbcf7e67ca6bfc9d5c3c8531be58b`
- Parent/frozen Iteration 5 tree: `45674a23be7b7994b153a53454aec38104fb12df`
- Pull request: `#172` targeting `main`
- Iteration 5 nonlinear suite root: `26c5ac1697094d1680dbdd829fe1c2492746bf9dbad41a389aa6d1bfed3184cc`
- Iteration 5 evidence root: `f2e5c94e053e14e8060f6bf3da15ebb9b50d3059f7834205c3b776653bb41d00`
- Iteration 5 receipt: `Z9XYF<Nsxk/5uv7-wcggO4G-Fva6JNNrUsI6uy*p7lHnrz0A6DmuuzSsOjJXw1JvDZ2OA4K1`
- Iteration 5 artifact SHA-256: `746c66f63ebd78342aad270db0bcc1e5ce18f35b7d2440ccf9f359edd78c5939`

## Implemented in this checkpoint

1. Exact finite IEEE binary32 and BF16 storage-bit rational decoding.
2. Exact real `blk.0` attention/FFN norm-weight binding.
3. Reuse of all seven frozen Iteration 4 Q4_0 linear descriptor semantics.
4. Complete 21-node `blk.0` dependency graph under frozen Iteration 5 nonlinear semantics.
5. Deterministic Hash216 node, graph, suite, and evidence identities.
6. Hash72 receipt chaining from the exact Iteration 5 receipt.
7. Cross-process replay validation surface.
8. Cumulative Iterations 1–6 validation gate.

## Authority boundary

Coordinate-level complete-block evaluation is not claimed in Iteration 6. Numerical transcendental approximation, canonical float interpretation, dense-forward replacement, runtime mutation, canonical mutation, and migration remain false.

## Restart action

Run `bash scripts/run_pass215_iteration6_validation.sh`, then execute the registered Iteration 6 workflow against the authenticated GGUF in two independent processes. Accept the checkpoint only on an exact branch-head run with identical suite/evidence/receipt roots.
