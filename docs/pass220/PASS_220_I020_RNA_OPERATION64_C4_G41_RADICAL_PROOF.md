# Pass 220 I020 — RNA operation64 / C4 / G41 Radical Proof

Status: **IMPLEMENTED — CI VALIDATION PENDING**

## Restart identity

- Base main: `4962eeeab662b0ec5e37547c7615429d2b2c7721`
- Branch: `pass220/i020-rna-operation64-c4-g41-radical-proof-v1`
- Merge target: `main`
- Parent cycle: I019 exact-head green on main, run `35455159996`, `102 passed`.

## Objective

Close the three proof obligations identified after I019:

```text
{x,y,z,w}^3 <-> operation64 = 8*left_basis8+right_basis8
x_D^3 = y_D on the I011 C4 quarter-phase projection
I014 41 reciprocal classes <-> Z_41 <-> prime-41 radical coordinate
```

## Preimplementation exact audit

Wolfram verified all three surfaces exactly:

- all `4^3=64` ordered triplets map bijectively to `0..63`;
- the six-bit triplet code splits bijectively into all `8x8` basis pairs;
- every mapping round-trips;
- `x_D=18`, `y_D=54`, `3*18 mod72=54`, `4*18 mod72=0`;
- Genesis macro `=5184`, reciprocal `=64/81`;
- differential `=419840/81`;
- radical `=32*sqrt(410)/9`;
- `410=10*41`;
- the 41 class IDs map bijectively to all residues `0..40`.

## Implemented files

- `hhs_runtime/hhs_pass220_rna_operation64_c4_g41_radical_proof_v1.py`
- `tests/pass220/test_hhs_pass220_rna_operation64_c4_g41_radical_proof_v1.py`
- `hhs_runtime/hhs_service_registry_v1.py`
- `.github/workflows/pass220-i020-rna-operation64-c4-g41-radical-proof.yml`
- `whitepapers/HHS_PASS220_RNA_OPERATION64_C4_G41_RADICAL_PROOF_V1.md`
- this restart record

## Commits

- `368e78c8156c20545d0d0646758902928e8c0202` exact proof runtime
- `ac8f7737d4f669a46c2d3fb194a47ee7bfcee281` exhaustive proof regressions
- `3809b6004ca33b78d05d7062bf9a3e79b8106d51` service registration
- `99508fcd4046d1f5995fd69110c6b4bd5bd504e1` exact-head workflow

## Acceptance gate

Run I020 plus inherited I019, I011, I015, I014, and I001 exact suites.
Repair forward only impacted failures, then merge after latest-head green and
verify the same gate on main.
