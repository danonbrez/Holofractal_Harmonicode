# Pass 219 Iteration 1.28 — Pass 198 repair + membrane restart record

Status: **CENSUS COMPLETE — REPAIR IMPLEMENTATION PENDING**

## Repository checkpoint

```text
repository: danonbrez/Holofractal_Harmonicode
branch: agent/pass219-iteration128-pass198-repair-membrane
PR: #324
merge target: main
merge authorization: NOT GRANTED
frozen I127 predecessor: fa89488d84f845fa372551b5324e0ddd37e49daf
current main observed at PR creation: 3c926453d65b71a6d1789e06b748544f5f2bd228
```

The I128 branch was created directly from the exact frozen I127 head. Current main has advanced independently; I128 is not rebased or merged onto it during the repair tranche.

## Census classification

`INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE`

Pass 198 exists historically and is integrated, but PR #136 merged before its post-merge review completed. The current inherited V1 runtime remains byte-identical to the accepted merge version, so the review findings remain repair obligations rather than historical-only observations.

## Accepted Pass 198 history

```text
primary PR: #136
historical base: b40e11315840781d1fd9c12932fad46eb32e383f
reviewed historical head: a383ab8ec6a55e04ab490477c7b8cfe5d107d098
accepted merge: 122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e
historical branch: agent/pass198-operation-calibration-registry
```

Accepted/current V1 runtime blob:

```text
hhs_backend/runtime/hhs_pass198_operation_calibration_registry_v1.py
3ec97b653344cbaf28eee89e6debbe1b6a89975d
```

Current API projection blob at frozen I127:

```text
hhs_backend/api/pass198_calibration_registry_routes.py
0e2581a3ecb0044eaf328617be1ae85e69e1e9a7
```

The accepted merge blob remains immutable historical provenance. I128 repairs the current inherited V1 source in place because Pass 199 and Pass 200A import `Pass198OperationCalibrationRegistry` directly from this file. Creating an isolated V2 without successor rewiring would leave the cumulative execution chain on the defective implementation.

## Reproducible review findings

```text
3700385770  P1  simplifications can verify without full replay
3700385771  P1  proof envelope can include states never compared / zero admitted coverage
3700385772  P2  unsupported registered axes silently fall back to Pass197 defaults
3700385773  P1  API registration authorization receipt is not persisted
3700385776  P2  nested operation-spec identity can contain floats
3700385777  P1  built-in idempotent registration is not atomic across processes
3700385778  P1  normalized simplification IDs are not used by persistent UPDATE
3700385779  P1  promotion state is validated before the write transaction
3700385780  P2  retry checkpoint identity is incorrectly bound to each new tick receipt
3700385781  P1  cross-workload promotion counts receipt-derived run IDs, not workloads
3700385783  P1  arbitrary specifications can claim the built-in executable adapter
3700385785  P1  every simplification receives the same aggregate cost claim
```

## Planned repair boundary

1. Require completed deterministic full replay and nonzero admitted coverage before a run can record promotion-grade simplification proof.
2. Bind proof envelopes to the actually executed tree/config coverage; reject partial-domain execution as promotion-grade closure.
3. Fail closed for unsupported executable axis schemas rather than silently generating the Pass197 default tree.
4. Persist the VM81 registration receipt inside the canonical registration event/document.
5. Recursively reject floats and unsupported non-exact identity values throughout operation specifications.
6. Move idempotent registration lookup under `BEGIN IMMEDIATE`, preserving atomic multi-process startup.
7. Normalize simplification IDs once and use the normalized value for lookup, events, and UPDATE; require exactly one row update.
8. Re-read and validate promotion/revocation state inside the write transaction.
9. Key reusable run checkpoints by operation/spec/tree identity, with per-invocation receipt bound separately.
10. Require distinct verified workload identities for staged promotion rather than distinct receipt-derived run IDs.
11. Bind the built-in Pass197 executable adapter to the exact built-in operation ID and specification hash; generic registration remains non-executable.
12. Replace duplicated aggregate per-simplification cost assertions with bounded per-simplification claim metadata, preserving only measured/derivable promotion-grade cost evidence.

## Successor compatibility constraint

Frozen successor source must not be rewritten merely to accommodate I128. In particular, do not modify the Pass199 files pinned by the frozen I127 membrane. I128 must preserve the existing Pass199/Pass200A call shape used by:

```text
Pass198OperationCalibrationRegistry
parameter_tree
list_simplifications
promote_simplification
_record_simplifications
_db / _lock / _event transactional integration
```

Dependency-scoped validation must include Pass198, repaired Pass199 production, Pass200A production, frozen I127 exact/synthetic membrane preservation, VM81 Exact ABI, and UQCEL before adding the I128 membrane.

## Environment state

No private/local state is authoritative. All continuation state is repository-visible. The branch is based on frozen I127 and PR #324 remains draft/unmerged.

## Next action

Repair the current inherited Pass198 V1 runtime and API registration projection, add focused regressions for all twelve findings, expand the Pass198 workflow, then execute dependency-scoped successor validation. Add the Pass219 I128 C/C++ RNA membrane only after the repaired runtime and immediate successors are terminal green.

Do not merge I128 without separate explicit integration authorization.
