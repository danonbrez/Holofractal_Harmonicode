# Cross-Modal Consensus Receipt Repair — 2026-09-27

Status: IMPLEMENTED / PR PENDING VALIDATION

## Base

```text
repository: danonbrez/Holofractal_Harmonicode
base main: 5e1602ae41e72940cc89cf25513201aaded2ead1
branch: repair/cross-modal-consensus-receipt-arity-current-main-20260927
merge target: main
```

## Observed failure

Latest HHS Consensus Gate failure on the current repair stream reached
`hhs_realtime_phase_certification_v1.py` and failed only in
`locked_witnesses_commit_through_shell`:

```text
TypeError:
CrossModalConsensusReceipt.__init__() takes 27 positional arguments
but 28 were given
```

The dataclass currently defines:

```text
agreed_next_state_hash72
anchor_phase_index
phase_max_distance
...
```

but `cross_modal_consensus()` still supplied an obsolete positional `None`
between `agreed` and `anchor`.

History inspection shows this is residue from the earlier
`agreed_phase_hash72` positional field that existed before the phase-tolerance
refactor. The refactor replaced that field with anchor/distance semantics but
left the old placeholder in the constructor call.

## Repair

`hhs_runtime/hhs_cross_modal_shell_gate_v1.py` now constructs
`CrossModalConsensusReceipt` with explicit named arguments.

No gate, quorum, phase, temporal, Hash72, armor, state, authority, or receipt
semantics were changed.

The named construction makes the dataclass/call binding explicit and prevents
future silent positional drift.

## Regression

Added:

```text
tests/test_hhs_cross_modal_consensus_receipt_repair_v1.py
```

The regression executes the same complete three-case
`RealtimePhaseCertificationV1.run_all()` path used by the commit acceptance
gate and requires:

```text
all_ok = true
failed = 0
passed = 3
status = CERTIFIED_REALTIME_PHASE_LOCKED
```

This preserves:

1. mandatory witness phase lock;
2. missing mandatory witness fail-closed behavior;
3. locked witness commit through CrossModalShellGateV1.

## Deployment relationship

The SSH known-host secret rotation was independently verified before this
repair:

- pinned known-host configuration passed;
- SSH deploy credential verification passed;
- exact-main bundle transfer passed.

The subsequent exact-main failure was a deliberate stale-main rejection after
`origin/main` advanced.
The Application VM failure was a shared Git remote-ref lock race while the
authoritative main ref was moving.

Those deployment races are not addressed by this source repair.

## Next action

1. Open the repair PR.
2. Run HHS Consensus Gate and the targeted regression.
3. Repair only attributable failures.
4. Merge and verify main if green.
5. Reconcile PR #618 onto the verified main.
6. Merge #618 only after its Hash216 PR-only publication path and Consensus Gate
   are green.
7. Dispatch production workflows sequentially from one current-main SHA after
   the direct-main Hash216 publication path has been removed.


## Consensus inherited-surface closure — 2026-09-27

Exact-head HHS Consensus Gate run `36346004850` on `cbe8736808c113cd07fdad5f053742ff5ebfadc4` failed before reaching the repaired cross-modal constructor. Verify job `108695151628` executed the acceptance gate by pathname:

```text
python hhs_runtime/hhs_commit_acceptance_gate_v1.py
ModuleNotFoundError: No module named 'hhs_runtime.hhs_repo_paths_v1'
```

This is the already-proven import-root regression from PR #619, not a new repository-path implementation defect. The current #622 base contains the exact established `hhs_runtime/hhs_repo_paths_v1.py` blob `4cd632a13bc61ec6a2c8e3c814a257b8349732aa`.

Rather than merge the stale #619 branch, this PR now ports its independently verified repair surfaces onto current main:

1. Consensus workflow:
   - package-module execution via `python -m hhs_runtime...`;
   - full checkout history for exact successor ancestry checks;
   - repository checkout in the downstream consensus job.
2. Pass 078 successor lineage:
   - baseline manifest remains unchanged;
   - exact current VM runtime blob `92afd8d0e26119b6db6420740c05db25a37d389a`;
   - exact current ABI blob `6a3ed4a10c5d83fa77bb4d118819fc230d32248a`;
   - only repository-visible validated successors are admissible.
3. Certification successor API:
   - use topology-aware `run_smoke_suite()`;
   - consume `summary.all_ok`;
   - do not restore the removed `HHSSmokeTestSuiteV1`.
4. Acceptance diagnostics:
   - preserve subprocess return code/stdout/stderr in failures.
5. Pre-commit parity:
   - package-module invocation matches CI.
6. Regression:
   - lock import-root behavior, exact successor admission, smoke successor use, and diagnostic preservation.

The #622 cross-modal named-field constructor repair remains intact and is not replaced by #619 content.

Observed status before this commit:
- base/main: `5e1602ae41e72940cc89cf25513201aaded2ead1`;
- #622 Hash216 run `36346004838`: success;
- #622 Consensus run `36346004850`: failure at import-root boundary.

Next action:
1. inspect current-head Consensus and Hash216 runs once;
2. if queued/not registered, stop at the restartable boundary;
3. if red, repair only the newly exposed inherited frontier;
4. if green, merge #622 and verify authoritative main before reconciling #618.


## QGU implicit-window self-expiry repair — 2026-09-27

Exact-head HHS Consensus Gate run `36346469303` on `048ccbd1be0e80b404abb4679798e2d10baec25c` completed red while Hash216 run `36346469506` completed green.

The constructor and inherited Consensus repairs executed successfully. The new failure frontier is temporal admission inside the realtime certification:

```text
locked_witnesses_commit_through_shell
→ all shell projections temporal_status = EXPIRED
→ CrossModalShellGateV1 quarantines
```

The live phase-lock stage already passed its explicit observation/window timestamps. The shell is the only caller using the QGU guard's implicit window path. In that path, `make_temporal_window()` captures `created_at_ns` before computing its Hash72 window commitment; the subsequent implicit `now_ns()` can therefore fall outside the 20 ms TTL solely because constructing the window itself consumed the budget.

Repair:
- when both window and observation timestamp are implicit, treat the observation as occurring at the newly created window's own `created_at_ns`;
- preserve existing wall-clock evaluation for explicit windows and explicit observation timestamps;
- keep explicit stale-window rejection fail-closed.

Regression coverage:
- simulate a 100 ms clock jump during implicit window construction and require the result not to self-expire;
- prove an explicit 20 ms window observed 100 ms later still returns `EXPIRED`.

No phase, quorum, Hash72, recursion, noise-floor, or explicit stale-data rule is weakened.

Repository state observed before this repair:
- PR #622 head: `048ccbd1be0e80b404abb4679798e2d10baec25c`;
- authoritative main: `30c9f7cf5c878f47e9845b809391993dde3f5c82`;
- #622 is behind current main and must still be reconciled after its attributable Consensus frontier is green.

Next action:
1. inspect the new exact-head Consensus/Hash216 runs once;
2. if queued/not registered, stop;
3. if red, repair only the next exposed inherited frontier;
4. if green, reconcile #622 onto then-current main and run only impacted exact-head validation before merge.


## Consensus artifact isolation repair — 2026-09-27

Exact-head run `36350469355` reached the downstream consensus job after all three verify jobs completed successfully. The aggregator reported:

```text
ConsensusDecision(total_agents=15, verified_agents=0, required_threshold=15, status='CONSENSUS_REJECTED')
```

Root cause:
- the downstream job now correctly checks out the repository so `hhs_runtime.hhs_multi_agent_consensus_v2_gate` can import;
- downloaded artifacts were placed under `receipts/`;
- the repository itself also contains JSON under `receipts/`;
- `glob('receipts/**/*.json')` therefore mixed repository receipt fixtures/history with the three downloaded distributed-verification artifacts.

Repair:
- download CI artifacts into the dedicated `_hhs_consensus_artifacts/` directory;
- evaluate consensus only over JSON found under that directory;
- add regression coverage that forbids the repository-wide `receipts/**/*.json` glob.

This does not weaken the 100% consensus threshold. It restores the intended three-agent input set.

Observed state:
- exact-head verify matrix: passed;
- exact-head Hash216 run `36350469315`: success;
- exact-head downstream Consensus: failed only from artifact namespace contamination;
- authoritative main had advanced beyond this branch and must still be reconciled after this attributable frontier closes.

Next action:
1. inspect the new exact-head Consensus and Hash216 runs once;
2. when green, reconcile the branch to then-current main;
3. rerun only impacted exact-head checks;
4. merge #622 and verify main.


## Filesystem Hash72 chain-authority repair — 2026-09-27

Exact-head Consensus run `36351448671` on `35b53aa3d3b6c15bd981f5a6970ed7fb34ebe595` isolated the downloaded artifact set correctly and evaluated exactly three agents:

```text
total_agents=3
verified_agents=0
required_threshold=3
CONSENSUS_REJECTED
```

All three verify jobs completed, but their distributed receipts were `FAILED` because `verify_filesystem_ledger()` found thousands of historical parent-link mismatches:

```text
actual: H72-FS-GENESIS
expected: <prior entry Hash72>
reason: parent_hash72 mismatch
```

The unified Hash72 ledger remained valid. Inspection of the filesystem ledger writer showed the inherited defect: every path observation was constructed with the default genesis parent, while the verifier correctly required an append-only parent chain. The persisted ledger history contains this legacy flat-genesis form.

Repair-forward behavior:
1. append-time filesystem-ledger authority now owns the parent link;
2. the first subsequent append deterministically rebinds legacy entries in their original order;
3. observation payload, ordering, paths, events, sizes, content commitments, and recorded timestamps are preserved;
4. a repository-visible deterministic migration receipt records the prior ledger hash and rebound count;
5. subsequent appends are O(1) against the persisted tip rather than repeatedly rebuilding history;
6. verification now recomputes every entry Hash72 from its stored payload + parent, validates the tip, and validates the aggregate ledger Hash72.

The verifier is not weakened. It is stricter than before because payload tampering can no longer pass with a trusted stored `entry_hash72`.

Regression coverage locks:
- append authority parent chaining;
- deterministic migration of legacy flat-genesis history;
- fail-closed rejection when an entry payload is modified without a matching Hash72 recomputation.

Current external state before this repair:
- Hash216 exact-head run `36351448675`: success;
- Consensus verify nodes: success;
- downstream Consensus: rejected because all three filesystem-ledger receipts were invalid;
- authoritative main observed at `ee42d27bdd0f4b12853bcde2fe4ed2dd7103d9ec`.

Next action:
1. inspect the new exact-head Consensus + Hash216 runs once;
2. if green, reconcile #622 to then-current main;
3. run only impacted exact-head validation;
4. merge #622 and verify main;
5. reconcile #618 and remove direct Hash216 publication to main.


## Filesystem aggregate canonicalization repair — 2026-09-27

Exact-head Consensus run `36353424931` on `ac80ca038072fec375bd4a2017fb90bfd9e45ecb` showed that the parent-chain repair is active:
- `chain_authority = HHS_FILESYSTEM_HASH72_APPEND_CHAIN_AUTHORITY_V1`;
- 3,397 legacy entries were deterministically rebound;
- entry parent links, entry hashes, and the stored tip all validated.

The sole remaining filesystem-ledger failure was:

```text
reason: ledger_hash72 mismatch
stored:     3srX9kn/AsgzEM=2Uaky=krv
recomputed: nhFm677√I^+22≠8fj0GKL)Sb
```

Root cause: the aggregate ledger hash consumed the raw Python list-of-dicts representation. The ledger is persisted with `json.dumps(..., sort_keys=True)`, so dict key order on reload differs from the in-memory insertion order used when the aggregate was first committed. Entry hashes are unaffected because their cores are explicitly ordered; only the aggregate commitment drifted across serialization.

Repair:
- aggregate Hash72 now consumes canonical JSON with sorted keys and compact separators;
- parent-chain authority, entry-hash recomputation, tip validation, and fail-closed tamper rejection are unchanged;
- regression appends entries, reloads the sorted JSON from disk, and requires stored/recomputed aggregate Hash72 identity.

Observed external state before this repair:
- Hash216 run `36353425033`: success;
- Consensus verify jobs: acceptance gate success;
- distributed receipts: failed only on aggregate filesystem `ledger_hash72`;
- downstream unanimous consensus therefore remained rejected;
- authoritative main observed at `75a7da5fc907b2e4034a713d0f5f56b7af99c7c7`.

Next action:
1. inspect this new exact head once;
2. if green, reconcile #622 onto then-current main;
3. run only impacted exact-head validation;
4. merge #622 and verify main;
5. reconcile #618 and close direct-main Hash216 publication.
