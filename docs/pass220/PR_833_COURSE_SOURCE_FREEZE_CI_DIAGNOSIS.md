# Pass 220 PR 833 — course source-freeze CI diagnosis

## Observed CI at head 634bde50cea46e7a46a148ce0e9c59b90ad78ae4

The Pass 220 Course Module Gate Provenance workflow failed; its tests raise
`SOURCE_BLOB_CHANGED:whitepapers/Harmonicode Algebra - Course` before
assertions on the 0–26 continuation. The M1/M2/M3/M4 course workflows fail
at the same upstream frozen-corpus check. This is one shared dependency
frontier, **not** evidence that their independent mathematical gates failed.

The frozen source registry:
`contracts/pass220/PASS_220_WHITEPAPER_CORPUS_SOURCE_FREEZE_V1.json`
has source base commit
`cab00e2eea3f9f064fa7b817995032cb3ef4b19a`, and expects blob
`2744e9ecf1f260ff9a5a02870320698ee2d7dcaf`
for `whitepapers/Harmonicode Algebra - Course`.
At this PR head the GitHub Contents API reports actual blob
`a36b5627b50e241ba715c607d0896cea254b2f3e`.
These identities differ.

No frozen manifest hash or course text has been modified in this PR.
Do NOT bypass the hash check, relabel an unverified hash as authoritative,
or bulk refresh the 70-file frozen-corpus manifest.

## Repair-forward gate
1. Investigate the historical authorizing change / origin of the old
   expected blob and the current course blob.
2. Determine whether the frozen original must be restored exactly or
   whether an explicitly authorized source-freeze migration is required.
3. Re-run only affected frozen corpus and course M0–M4 tests first.
4. Then execute the new 0–26 continuation synthetic/integration tests,
   the Lean root imports, and scoped runtime/JSON contract checks.
5. Commit validation evidence and merge only after passing required gates.

## Restart state
- Branch: formal/module23-24-genesis-palindromic-identity-20261019
- Target: main; draft PR 833
- File added this stage: tests/pass220/test_pass220_course_0_26_continuation_synthetic_v1.py
- CI inspected: exact head workflow receipts; root cause shared SOURCE_BLOB_CHANGED
- Environment: GitHub connector only; no local checkout/Lean compile
- Remaining: source-freeze reconciliation; scope-tested suite; operational service binding
- No new native VM81/Hash216 state authority or receipt minted.

## Historical resolution found
Historical commit `48aa9b704f43e4ede87b25b9391cf4349537b123`
contains the exact old frozen blob `2744e9ecf1f260ff9a5a02870320698ee2d7dcaf`
with Modules 0–12 and 17,617 decoded characters.
The current main edition has blob
`a36b5627b50e241ba715c607d0896cea254b2f3e`,
44,220 decoded characters, and headings Modules 0–14.
Consequently PR 833's independent continuation has been limited to
Modules 15–26, avoiding duplicate Modules 13 and 14. Its 0–26 inventory
and synthetic tests were correspondingly updated.

The legacy frozen source manifest is still incompatible with current main.
Fail-closed `build_corpus_index` is intentionally retained. No old proof
receipt can silently be reassigned to the expanded edition. An authorized,
explicit versioned source-freeze migration or an equivalent approved
edition-aware binding is required before course CI may pass.
