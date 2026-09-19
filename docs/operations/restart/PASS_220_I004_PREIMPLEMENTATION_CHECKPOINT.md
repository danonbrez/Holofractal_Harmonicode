# Pass 220 I004 preimplementation checkpoint — global Genesis zero-sum halt gate

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor repair checkpoint: `532a8e2bb80162ac6507eabfc12e9e4c9eb1a3a9`
- merge target: `main`
- PR: #491

## Authorized invariant

Scaling is mathematically bounded by global zero-sum Genesis closure.

The VM81 surface contains nine local Lo Shu nuclei.  In each local Lo Shu nucleus the `1` cell is the local closure anchor.  Global halt requires every local nucleus to close simultaneously through:

1. zero-normalized local Lo Shu state;
2. typed `AB=P⁴` closure witness;
3. typed `1/9` invariant closure witness;
4. typed local `7`-cell constraint closure witness;
5. no new normalized state change.

When all nine nuclei close and the complete 81-cell normalized state has no change, candidate expansion must halt.  No extra canonical Hash72/Hash216 transition may be minted merely to represent repeated closure.

## Implementation constraints

- Preserve the canonical equation surfaces as typed witnesses; do not independently scalarize or substitute for `AB=P⁴`, the `1/9` invariant, or the 7-cell constraint equations.
- Reuse I001's exact 81-cell normalization offsets and nine-nucleus Lo Shu geometry.
- Exact integers/booleans only; reject floats and bool-as-int ambiguity.
- Require exactly nine ordered nucleus witnesses and one witness per nucleus.
- Derive the local Lo Shu `1` and `7` cell indices from the canonical Lo Shu reference.
- Global halt requires all 81 current offsets zero and current/next normalized offsets byte-for-byte/elements-equal.
- A nonclosed nucleus, nonzero offset, missing witness, duplicate nucleus, or state change keeps expansion open.
- HALT is an execution/scheduler decision; it does not widen VM81 mutation, Hash72 commit, or Hash216 commit authority.
- Provide a Lane 5 composition wrapper that returns before ranking when closure is proven.

## Planned files

- `hhs_runtime/hhs_pass220_genesis_zero_sum_halt_v1.py`
- `hhs_backend/runtime/hhs_pass220_genesis_zero_sum_lane5_gate_v1.py`
- `tests/pass220/test_hhs_pass220_genesis_zero_sum_halt_v1.py`
- `docs/pass220/PASS_220_I004_GENESIS_ZERO_SUM_LO_SHU_GLOBAL_HALT.md`
- dedicated/updated workflow coverage
- postimplementation restart checkpoint
