# Pass 218 Full Implementation — Iteration 7 Restart Record

**Pass:** HHS Pass 218 — Relational Curriculum Corpus Hydration  
**Iteration:** 7  
**Base commit:** `ab2fbf86a407b7141899c1dc155703f3f7820a90`  
**Branch:** `agent/pass218-full-iteration7-durable-canonical-persistence`  
**Merge target:** `main`  
**Status:** implementation checkpoint; **not** Pass 218 closure.

## Frozen inherited state

Iterations 1–6 remain inherited restart nuclei. Iteration 7 does not rewrite Genesis, grammar, narrative hydration, the Iteration-3 purge membrane, Iteration-4 staging, Iteration-5 proof/grant semantics, or the Iteration-6 canonical prepare/commit boundary.

Iteration 7 begins only after Iteration 6 has produced an already-committed canonical Pass-217/VM81 target. Durable restart is therefore **receipt replay and authority reconstruction**, not a new promotion, authorization, or canonical mutation.

## Implemented in this iteration

1. Added `Pass218DurableCanonicalStore` for durable process-restart persistence of an already-committed Iteration-6 canonical target.
2. A durable generation contains only:
   - admitted Pass-217 vector entries;
   - already-consumed Iteration-6 canonical commit receipts;
   - the exact 648-byte / 5,184-bit VM81 image;
   - target/vector/VM81 authority roots;
   - generation ancestry and validation seals.
3. Source text, source buffers, Pass-165 learning state, truth promotion, action authority, and authoritative floats remain forbidden.
4. Added canonical checkpoint sealing:
   - domain-separated checkpoint SHA-256;
   - checkpoint Hash72;
   - validation Hash72;
   - ordered Hash216 = committed canonical target root || checkpoint Hash72 || checkpoint validation Hash72.
5. Added a Hash72-sealed manifest containing the active generation plus one immediately previous durable generation for deterministic recovery.
6. Generation files are completed and `fsync`-ed before the manifest can point to them. Manifest publication uses an atomic filesystem replacement and directory `fsync` where supported.
7. Repeating a checkpoint over an unchanged canonical root + VM image is idempotent and does not advance the durable generation.
8. Restart validates the persisted generation before installation:
   - canonical JSON encoding;
   - checkpoint SHA-256 / Hash72 / Hash216 seal;
   - target entry and commit counts;
   - admitted Pass-217 vector-entry structure;
   - every embedded Iteration-6 commit Hash72;
   - every embedded Iteration-6 receipt Hash72;
   - every embedded Iteration-6 commit Hash216;
   - the ordered before-root → after-root commit chain;
   - VM image SHA-256 and projection binding;
   - deterministic 64-lane inherited VM81 replay;
   - replayed VM81 snapshot/state roots and receipt root;
   - final reconstructed canonical target root.
9. Only after all checks succeed is a new in-memory `Pass217VM81CanonicalTarget` installed with the original admitted entries, consumed authorization receipts, and exact VM81 state.
10. Restart explicitly records:
    - `new_canonical_mutation_invoked=false`;
    - `new_authorization_minted=false`;
    - `canonical_learning_commit_invoked=false`;
    - `truth_promotion=false`;
    - `action_authority_minted=false`;
    - `verbatim_source_retained=false`;
    - `pass165_source_retaining_path_invoked=false`.
11. Added interrupted-write recovery. A generation written before an injected pre-manifest failure cannot become active because the previous manifest remains byte-identical.
12. Added active-generation corruption recovery. If the active generation is invalid, restart may fall back only to the manifest-bound immediately previous generation after that generation independently passes the complete validation pipeline.
13. A recovered target can continue computation only through a new normal Iteration-5 authorization consumed by the unchanged Iteration-6 canonical commit boundary.
14. Added repository-native evidence using `creative_writing/novels/THE_SMALLEST_PERMISSION.md`, including actual durable checkpoint/restart, idempotent checkpoint replay, interrupted manifest publication, and previous-generation corruption recovery.

## Frozen Iteration-6 receipt compatibility

The first Iteration-7 durability run exposed one exact inherited serialization detail in the already-validated Iteration-6 receipt object. Iteration 6 constructs its final receipt in the form:

```python
{
    "schema": receipt_schema,
    **commit_payload,
    ...
}
```

The inherited `commit_payload` also contains a `schema` key, so the later mapping expansion leaves the validated serialized outer label as:

```text
HHS-P218-I6-CANONICAL-COMMIT-PAYLOAD-V1
```

rather than the earlier intended outer label:

```text
HHS-P218-I6-CANONICAL-COMMIT-RECEIPT-V1
```

Iteration 7 deliberately does **not** rewrite or normalize validated Iteration-6 receipt bytes. `persistence_compat.py` admits exactly those two outer labels, temporarily normalizes only the label for structural checking, recomputes the complete embedded Iteration-6 commit Hash72, receipt Hash72, and Hash216, then restores the original outer label before canonical reconstruction. No cryptographic or mutation requirement is bypassed.

This is a historical serialization compatibility membrane, not a second receipt authority.

## Durable transaction boundary

```text
Iteration-6 CANONICAL_COMMITTED target
        ↓
freeze exact entries + consumed commit receipts + 648-byte VM81 image
        ↓
validate source/learning/truth/action exclusions
        ↓
seal checkpoint SHA-256 + Hash72 + Hash216
        ↓
write generation → flush → fsync
        ↓
atomically replace Hash72-sealed manifest
        ↓
DURABLE_CHECKPOINT_COMMITTED
        ↓
process termination / fresh process
        ↓
read manifest
        ↓
validate checkpoint + every I6 receipt + root chain
        ↓
64-lane inherited VM81 deterministic reconstruction
        ↓
prove exact VM81 + Pass-217 canonical root
        ↓
RESTORED_ACTIVE_GENERATION
```

No restart step recreates an Iteration-5 authorization or replays an Iteration-6 canonical mutation.

## Failure and recovery boundaries

### Failure before manifest publication

```text
new generation fully written
        ↓
[injected failure]
        ↓
old manifest remains byte-identical
        ↓
restart selects old active generation
```

An orphan generation has no authority merely because its bytes exist on disk.

### Damaged active generation

```text
manifest points to active generation
        ↓
active validation fails
        ↓
load only manifest-bound previous generation
        ↓
full independent validation
        ↓
RECOVERED_PREVIOUS_VALID_GENERATION
```

Fallback is bounded to a previously sealed generation; corruption cannot create a new state.

## Tests added

The Iteration-7 test matrix covers:

- persistence contract constants;
- empty-target rejection;
- checkpoint/manifest creation;
- checkpoint Hash216 ordering;
- exact process restart root/snapshot/receipt equality;
- no new authorization or canonical mutation during restart;
- idempotent checkpoint replay;
- generation ancestry;
- injected failure before manifest swap;
- active-generation corruption fallback;
- fallback-disabled rejection;
- checkpoint-seal tampering;
- embedded Iteration-6 receipt tampering even after checkpoint resealing;
- VM81 snapshot tampering even after checkpoint resealing;
- noncanonical persisted JSON rejection;
- manifest tampering;
- verbatim-source exclusion from persisted bytes;
- continued canonical operation only through a new Iteration-6-authorized commit;
- checkpointing after a restored target continues execution;
- Pass-165 import exclusion;
- no authoritative float literals.

## Changed files

- `hhs_runtime/pass218/persistence.py`
- `hhs_runtime/pass218/persistence_compat.py`
- `hhs_runtime/pass218/__init__.py`
- `tests/pass218/test_pass218_iteration7_durable_canonical_persistence.py`
- `tools/pass218_iteration7_evidence.py`
- `.github/workflows/pass218-full-iteration7.yml`
- `docs/pass218/PASS_218_ITERATION_7_RESTART.md`

## Required exact-head validation

```text
python -m py_compile hhs_runtime/pass218/*.py
python -m py_compile tools/pass218_iteration1_evidence.py
python -m py_compile tools/pass218_iteration2_evidence.py
python -m py_compile tools/pass218_iteration3_evidence.py
python -m py_compile tools/pass218_iteration4_evidence.py
python -m py_compile tools/pass218_iteration5_evidence.py
python -m py_compile tools/pass218_iteration6_evidence.py
python -m py_compile tools/pass218_iteration7_evidence.py
AST no-float-literal check over hhs_runtime/pass218/*.py
pytest -q tests/pass218/test_pass218_iteration1_genesis_curriculum.py
pytest -q tests/pass218/test_pass218_iteration2_grammar_narrative_hydration.py
pytest -q tests/pass218/test_pass218_iteration3_source_transaction_membrane.py
pytest -q tests/pass218/test_pass218_iteration4_vector_vm5184_staging.py
pytest -q tests/pass218/test_pass218_iteration5_promotion_admission_proof.py
pytest -q tests/pass218/test_pass218_iteration6_canonical_commit_boundary.py
pytest -q tests/pass218/test_pass218_iteration7_durable_canonical_persistence.py
pytest -q tests/pass218/test_repository_native_creative_writing_crawler.py
python tools/pass218_iteration7_evidence.py
Pass 217 Current Main Integration workflow / inherited integration gates on the draft PR
```

## Deliberately incomplete after Iteration 7

- Pass 218 as a whole remains open;
- production lifecycle wiring must still choose and mount the durable store location under the real Runtime-OS/service process rather than a test/evidence temporary directory;
- production Pass-166 Word2Vec model activation remains required;
- contextual open-weight hydration remains required;
- deeper causal/social/perspective hydration remains required;
- production document/ZIP/folder/repository/official-site ingress adapters remain required;
- ablation suites and full Pass-218 deterministic replay remain required.

## Next deterministic action

Do not change Iterations 1–7 unless an exact validation gate falsifies them. The next Pass-218 iteration should bind this durable canonical store into the real Runtime-OS/service lifecycle so startup mounts the latest valid canonical Pass-217/VM81 generation before Pass-218 ingestion can resume, while preserving the same source-purge and authorization boundaries.
