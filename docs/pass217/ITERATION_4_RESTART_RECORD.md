# Pass 217 Iteration 4 restart record

- Base commit: `3b55da5e8aa67491f113d1b9e9c7e481aeb1e18c`
- Base tree: `a75c87a891d7326a1e01844dd5c7223acbb50940`
- Branch: `agent/pass217-iteration4-reconcile`
- Merge target: `main`
- Pass 216 merge authority: `f10e453c5d7c7467cf5e57f6452958491fe763ad`
- Prior core Iteration 4 reconciliation: `724e91c5fb1009cefc52778c3e73338257b2814c`
- Iteration 3 candidate commit: `947be39fd67700f307ff80d96c3a10c3acaa29cc`
- Protected VM81 runtime blob: `362cd6e892ae66024333b111aec83f12023fdce3`

## Implemented in this checkpoint

- Hash72 72×72 manifold validator with wrapped `x/y/z/w` order-72 closure.
- Exact one-step permutation roots and representative full-orbit roots.
- Immutable central 3×3 Lo Shu/phase nucleus validation over 576 candidate bits.
- Exact reuse of Iteration 3 candidate/address artifacts by SHA-256.
- Repository ancestry checks for Pass 216, prior Iteration 4 reconciliation,
  and this Iteration 4 main base.
- Fail-closed protected C runtime blob check.
- Machine-readable schema and deterministic evidence record.
- Dependency-scoped tests, validation script, tool, and GitHub Actions workflow.
- No floats in the new authoritative validator.
- No canonical promotion, Golay generation, migration, or Pass 219 runtime work.

## Frozen roots

- candidate SHA-256: `97379c7ae7cdaebd8031a3a3fb58559c967b361b360c7db34ec096acabfc8fe8`
- address-map SHA-256: `2f8d8a23114b87f2dbe91f3d302ef089b750f9d91f533d744a4524e907717f5f`
- Hash72 matrix root: `6c0b2e9e354e8d7eb17a746d01c157b19aa95b58296884126cdf5bef7998e286`
- Hash72 manifold root: `c757bae150d9ab94485c680ec3143e715b674d35f445a72c6fb4ea2def6f7884`
- nucleus identity root: `da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164`
- nucleus support root: `ac46211412784990e08e5cf0b80df5db381aad612a7ccd8aa816815a105b0294`
- Iteration 4 evidence root: `5c996cda648db2074a144ab8b9b0834ef442ee8bc2b2c7ed91885bc38aa6d03f`

## Validation

Repository-visible validation command:

```bash
bash scripts/run_pass217_iteration4_validation.sh
```

Remote CI is the executable validation authority for this checkpoint because
the working environment does not have a mounted repository clone.

## Next action

Run the Iteration 4 workflow against the exact checkpoint head. If green,
reconcile any newer `main` commits without changing authenticated Pass 217
inputs, update this restart record with the exact validated head/run, and merge
through a PR. If a dependency identity changed, regenerate only the affected
artifact and repair forward.
