# Pass 220 I003.2 repair checkpoint — truthful post-calibration integration

Status: **RESTARTABLE REPAIR CHECKPOINT — CI PENDING**

## Lineage

- predecessor: `537baa87fbdef21d5cc3aa7c238a8280e9b947f0`
- pre-repair checkpoint: `8660c2d87e4c3bbc57ce10d0cea728c0a5f75284`
- branch: `pass220-lo-shu-normalization-checkpoint-1`
- PR: #491

## Frozen cold raw measurement

Run `35300451657` completed the cold raw x86_64 calibration successfully before any HHS/runtime build:

- xy max closed bytes: 33,554,432
- yx max closed bytes: 33,554,432
- zw max closed bytes: 33,554,432
- wz max closed bytes: 33,554,432
- global minimum: 33,554,432 bytes
- artifact: `10530216407`
- artifact digest: `sha256:aa99ee4446c703e62d9b4277e059f8cbe94a9a20afafaa152faca3f641eaf64b`

This measurement is not altered by the query-integration repair.

## Repaired defects

1. Synthetic Hash72/Hash216 benchmark identities are now injective over the admitted bounded seed domain instead of repeating every 72 rotations.
2. `_counts(max_candidates)` now obeys the requested maximum exactly; `max_candidates=8` executes only the 8-candidate point.
3. Regression coverage now checks uniqueness beyond 72 candidates and the count ladder at 8, 2048, and 8192.
4. Post-calibration query comparison now fails unless all four cohorts close and the global time bound is respected.
5. Workflow pytest uses `set -o pipefail` so a failed test cannot be hidden by `tee`.
6. The descriptive complete 5184-bit state-equivalent divisor is corrected from 5184 bytes to the actual raw ABI width of 648 bytes; the remainder bytes are recorded separately.

## Commits

- deterministic identity/bound repair: `1e175d44b3d504d321547bdf6ffd0f584abc7409`
- regression tests: `6470eee3ec4349044e096de0351ffd40e7e12e48`
- workflow fail-closed / 648-byte divisor: `497d379265dc780f0c094f94d2f6bb54ae5c5309`

## Validation state

A fresh dedicated workflow is expected from the branch push. Per repository responsiveness policy, this repair is checkpointed without blocking the next authorized implementation task on external CI.

## Next action

Implement I004 as the exact global Genesis zero-sum Lo Shu closure halt gate: all nine local Lo Shu nuclei must close simultaneously across the zero-normalization vector, the typed AB=P⁴ witness, the 1/9 invariant witness, and the local 7-cell constraint witness; once there is no new state change, candidate expansion must halt rather than mint redundant canonical transitions.
