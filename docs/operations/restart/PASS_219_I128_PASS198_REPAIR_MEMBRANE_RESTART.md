# Pass 219 Iteration 1.28 — Pass 198 repair + membrane restart record

Status: **THIRTEEN-FINDING REPAIR IMPLEMENTED — PRE-MEMBRANE REVALIDATION PENDING**

## Repository checkpoint

```text
repository: danonbrez/Holofractal_Harmonicode
branch: agent/pass219-iteration128-pass198-repair-membrane
PR: #324
merge target: main
merge authorization: NOT GRANTED
frozen I127 predecessor: fa89488d84f845fa372551b5324e0ddd37e49daf
current main observed at PR creation: 3c926453d65b71a6d1789e06b748544f5f2bd228
latest pre-documentation implementation checkpoint: c8b92f5bb01b195e1b9ae0c666a6df139e91d717
```

The I128 branch was created directly from the exact frozen I127 head. Current main has advanced independently; I128 is not rebased or merged onto it during the repair tranche.

## Census classification

`INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE`

Pass 198 exists historically and is integrated, but PR #136 merged before its post-merge review completed. The frozen-I127 inherited V1 runtime was byte-identical to the accepted merge implementation, so the review findings were repair obligations rather than historical-only observations.

The complete PR #136 review census contains **13 substantive findings**. Earlier I128 notes that counted 12 were incomplete because review finding `3700385787` was initially missed. That finding is now included and implemented.

## Accepted Pass 198 history

```text
primary PR: #136
historical base: b40e11315840781d1fd9c12932fad46eb32e383f
reviewed historical head: a383ab8ec6a55e04ab490477c7b8cfe5d107d098
accepted merge: 122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e
historical branch: agent/pass198-operation-calibration-registry
```

Accepted/frozen-I127 V1 runtime provenance blob:

```text
hhs_backend/runtime/hhs_pass198_operation_calibration_registry_v1.py
3ec97b653344cbaf28eee89e6debbe1b6a89975d
```

Frozen-I127 API projection blob:

```text
hhs_backend/api/pass198_calibration_registry_routes.py
0e2581a3ecb0044eaf328617be1ae85e69e1e9a7
```

The accepted merge remains immutable historical provenance. I128 repairs the current inherited V1 source in place because Pass 199 and Pass 200A import `Pass198OperationCalibrationRegistry` directly from this file. Creating an isolated V2 without successor rewiring would leave the cumulative execution chain on the defective implementation.

## Definitive PR #136 review findings

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
3700385787  P1  required negative mutations are listed but never executed before proof verification
```

## Implemented repair boundary

1. Require completed deterministic full replay and nonzero admitted coverage before a run can record promotion-grade simplification proof.
2. Bind proof envelopes to actually executed tree/config coverage; partial-domain execution cannot claim promotion-grade closure.
3. Fail closed for unsupported executable axis schemas rather than silently generating the Pass197 default tree.
4. Persist the VM81 registration receipt inside the registration event and operation document.
5. Recursively reject floating-point and unsupported non-exact values throughout identity-bearing operation specifications.
6. Move idempotent registration lookup under `BEGIN IMMEDIATE`, preserving atomic multi-process startup behavior.
7. Normalize simplification IDs once and use the normalized value for lookup, event identity, and UPDATE; require exactly one updated row.
8. Re-read and validate promotion/revocation state inside the write transaction.
9. Key reusable run checkpoints by operation/spec/tree identity, with each invocation receipt bound separately.
10. Require distinct verified workload identities for staged promotion rather than distinct receipt-derived run IDs.
11. Bind the Pass197 executable adapter to the exact built-in operation ID and specification hash; generic registrations remain non-executable unless separately implemented.
12. Remove false per-simplification aggregate savings. Stable proof cost metadata is now explicitly unmeasured: `NO_PER_SIMPLIFICATION_COST_MEASURED`, `UNMEASURED_PER_SIMPLIFICATION`, and `promotion_grade_cost_claim=false`.
13. Execute and persist the exact six registered negative mutations before `ENVELOPE_VERIFIED`; every result carries `executed`, `detected`, an outcome, details, and an evidence Hash72, with a root Hash72 bound into proof/event evidence. Promotion fails closed if this executed evidence is absent or incomplete.

## Finding 13 executed mutation probes

The repaired Pass198 runtime executes these registered Pass197 negative mutations:

```text
replace xy with x*y
admit floating-point ingress
reverse matrix product order
strip VM81 lane identity
admit zero reciprocal domain
tamper checkpoint receipt tip
```

Evidence schema:

`HHS_PASS_198_EXECUTED_NEGATIVE_MUTATION_EVIDENCE_V1`

The executable set must exactly match the registered mutation set; all six probes must execute and detect/reject their mutation before a simplification proof can be verified or promoted.

## Repair implementation commits

```text
90a271c2ca5474d5dbe70320d1fc166e2bfeda91  initial restart/census checkpoint
7a78a1c7fa6a11cd6768b7b5e1ac7a759298e620  initial Pass198 runtime repair
239c518fc470a8815a13d1dff83dda0f17cfdb54  persist API registration receipt
24c920545ded9b690c590897d4314a3dc7cbbe89  initial review-finding regressions
903e9de9f486930be07e753d608a6d7563d8d3b5  dedicated I128 repair workflow
1f4176f7453385d7541beef59629b0ea7d262e0b  stabilize unmeasured per-simplification cost identity
29593e89a6bab99049f8d65f2acf83c5bb2b29f0  align cost regression with stable identity
89091a8247cfa71d74f986b44c3135e47c33b5fb  align production cost gate
3800b799d531e30a106a55bdc01d8b84b789dddd  execute/persist required negative mutations
1f4e8b50ecd96c46cf812d84c5228832a11a6f82  finding-13 focused regression
c8b92f5bb01b195e1b9ae0c666a6df139e91d717  thirteen-finding production validation gate
```

Current repaired runtime blob at the pre-documentation implementation checkpoint:

```text
hhs_backend/runtime/hhs_pass198_operation_calibration_registry_v1.py
9be70fd34fad007001a830fc225792a9a56a24e7
```

Current focused regression blob:

```text
tests/test_hhs_pass198_i128_repair_v1.py
b05a76b0cb694a51b66b147583c95520f2e54a9b
```

Current dedicated workflow blob:

```text
.github/workflows/pass198-i128-repair-validation.yml
879f6b10ed08f5be590f28510ba12b225da44d0b
```

## Validation history and compatibility constraint

Before finding 13 was discovered, checkpoint `1f4176f7453385d7541beef59629b0ea7d262e0b` had a fully green successor matrix, including Pass199, Pass200A, Pass200B, Pass200C, Pass201, Pass203, Pass204, frozen I127, VM81 Exact ABI, UQCEL, and production root. Those results established that the first twelve repairs and stable cost identity were successor-compatible, but they do **not** validate the later finding-13 runtime change.

Frozen successor source must not be rewritten merely to accommodate I128. In particular, do not modify the Pass199 files pinned by the frozen I127 membrane. I128 must preserve the existing Pass199/Pass200A call shape used by:

```text
Pass198OperationCalibrationRegistry
parameter_tree
list_simplifications
promote_simplification
_record_simplifications
_db / _lock / _event transactional integration
```

The finding-13 implementation therefore remains entirely inside the inherited Pass198 authority surface and uses existing exact Pass197 primitives for negative probes.

## Required pre-membrane gates

The exact post-finding-13 branch head must be validated through:

- dedicated Pass198 I128 thirteen-finding workflow;
- historical Pass198 production workflow;
- repaired Pass199 production workflow;
- Pass200A production workflow;
- Pass200B governed admission workflow;
- frozen I127 Pass199 membrane preservation;
- VM81 Exact ABI;
- UQCEL.

Pass200C/201 and later triggered successor workflows are useful additional compatibility evidence but are not substitutes for the required gates above.

## Environment state

No private/local state is authoritative. All continuation state is repository-visible. The branch is based on frozen I127 and PR #324 remains draft/unmerged.

## Next action

Wait only for the exact current-head pre-membrane gate set. If a gate fails, repair only the violated inherited boundary and revalidate impacted dependencies. If all required gates are terminal green, add the Pass219 I128 C ABI/C++ RNA membrane for repaired Pass198, then execute exact and synthetic membrane validation before a documentation-inclusive freeze seal.

Do not merge I128 without separate explicit integration authorization.
