# Pass 220 I018-I020 Repair-Forward Proof Closure — Restart Checkpoint

Date: 2026-09-19

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main: `857e41a868634f8c7c7906ba249b8614e9115981`
- Branch: `pass220/repair-i018-i020-proof-closure-v1`
- Current repair head: `912946c92aee76c674a2249c3c9bccdb52a16597`
- Merge target: `main`
- Main drift at checkpoint: none; branch is 35 commits ahead and 0 behind.

This checkpoint freezes the post-merge review repair before integration. No
further Pass 220 dependent merge is part of this repair branch.

## Findings closed in source

### I018

1. **Independent u^144 path**
   - exponent: `72*(b^2/a^4)=144`;
   - independent value: `b^6*c^4/(c^2-a^2)=36`;
   - HASH72 remains separately evaluated by I017 as `b^4*P^4=36`;
   - `mc^2` is independently evaluated as `(a^2+b^2)^2*b^4=36`.
   - the ratio no longer assigns one projected value to both sides.

2. **Complete ordered phase**
   - I018 now requires the I017 ordered witness
     `(sx,sz,xy,yx,zw,wz)=(0,0,1,-1,1,-1)`;
   - altered `yx`, `wz`, `xy`, `zw`, `sx`, or `sz` fails closed.

3. **Pinned UCE digest**
   - canonical source SHA-256 is recomputed;
   - it must equal the Python canonical digest, the pinned UQCEL bridge digest,
     the native C byte literal, and
     `7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42`.

4. **Reproducible Wolfram evidence**
   - input: `evidence/pass220/i018_repair_wolfram_audit_v1.wl`;
   - output: `evidence/pass220/i018_repair_wolfram_audit_v1.output.json`;
   - receipt: `evidence/pass220/i018_repair_wolfram_audit_v1.receipt.json`;
   - exact audit result: 15/15;
   - the Wolfram file self-exports the committed compact RawJSON output.

5. **Dependency propagation**
   - I018 push/PR path filters now include I014/I015 runtimes and tests,
     native UQCEL source-digest surfaces, the UCE envelope, and audit evidence.

### I019

The ordered q=-1 phase is now derived from the supplied 5,184-character state
rather than copied into the receipt:

- each local64 coordinate decodes to one ordered `{x,y,z,w}^3` RNA word;
- the first two symbols select the ordered phase pair;
- all 64 operation addresses are covered in every one of 81 qudit cells;
- `xy/yx/zw/wz` each occur exactly `81*4=324` times;
- the actual serialized character participates in the phase-binding root;
- changing a canonical serialized state changes the binding root.

Both the Python witness and native C++ ABI now implement this derivation. The
native ABI version is advanced to `0x00010002` and exposes pair counts plus a
serialized ordered-phase binding signature.

### I020

The previously claimed independent Wolfram audit is now repository-visible:

- input: `evidence/pass220/i020_wolfram_audit_v1.wl`;
- output: `evidence/pass220/i020_wolfram_audit_v1.output.json`;
- receipt: `evidence/pass220/i020_wolfram_audit_v1.receipt.json`;
- exact audit result: 18/18.

I020 dependency triggers and tests now include repaired I018 and I019 surfaces.

## Open Stack race repair

`.github/workflows/pass219-open-stack-consolidation.yml` now:

- runs on exact `main` pushes in addition to the historical consolidation branch;
- uses the frozen pull-request base SHA for PR ancestry rather than moving
  `origin/main`;
- uses exact HEAD==origin/main equality on main push;
- restricts source-stack merge/push operations to the dedicated consolidation
  branch only;
- applies the same stable event-base/exact-main rule to the final integration
  assertion.

This removes the known post-merge ancestry race without weakening the
substantive Open Stack build/regression stages.

## Validation already executed

Independent Wolfram exact audits:

```text
I018 repair: 15/15
I020 audit:  18/18
```

Repository CI for the repair branch has not yet been used as acceptance
evidence at this checkpoint.

## Files changed

Core repair surfaces:

- `hhs_runtime/hhs_pass220_h36_hash72_unit_bridge_v1.py`
- `tests/pass220/test_hhs_pass220_h36_hash72_unit_bridge_v1.py`
- `hhs_runtime/hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1.py`
- `hhs_runtime/include/hhs_pass220_rna_hash72_dna_qudit_phase_lock_1_0.h`
- `hhs_runtime/cpp/hhs_pass220_rna_hash72_dna_qudit_phase_lock_1_0.cpp`
- `tests/pass220/test_hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1.py`
- `tests/pass220/test_hhs_pass220_rna_hash72_dna_qudit_phase_lock_native_v1.c`
- I018/I019/I020 workflows
- Open Stack workflow
- I018/I020 Wolfram evidence triplets
- I018/I019/I020 whitepapers and restart documentation.

## Next action

1. Open one repair-forward PR to `main`.
2. Require green I018, I019, I020 and Open Stack PR gates plus triggered
   inherited Pass 220 checks.
3. Repair forward only impacted failures.
4. Merge only after latest-head green.
5. Verify exact main with I018-I020 and the new Open Stack main-push gate.
6. Leave the separately known Runtime OS deployment composition fault in its
   existing workstream; this repair introduces no new deployment failure class.
