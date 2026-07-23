# HHS PASS 146 — Boundary-Constructed Network Security

**Contract identifier:** HHS-P146  
**Parent:** Full inherited HHS pass-history nucleus through HHS-P145  
**Governance:** HHS-I132 Continuous External Usability Audit Contract  
**Status:** Normative implementation authority  
**Rule:** `NO_OPERATION_WITHOUT_BOUNDARY`

## Canonical invariant

An authorized operation is the composition of an authenticated identity, active authority grant, minimum admissible capability pathway, validated ordered state transition, explicit reversibility class, and replayable closure receipt.

```text
AUTHORIZED_OPERATION
=
BOUNDARY_CONTRACT
+ MINIMUM_ADMISSIBLE_PATH
+ VALIDATED_STATE_TRANSITION
+ CLOSURE_RECEIPT
```

A pathway that cannot be constructed is non-representable in the admitted execution graph. Rejection occurs before a canonical pathway row is created whenever identity, authority, source state, destination, disclosure, peer trust, signature, capability, resource, recursion, or reversibility admission fails.

## Binding invariants

1. The boundary constructs the execution path; it does not merely inspect an ambient route.
2. The derived path contains only the capabilities required by the registered operation adapter.
3. Parent capability does not automatically propagate to a child operation.
4. Recursive child boundaries preserve or narrow authority, disclosure, resource, and depth surfaces.
5. Temporary capabilities exist only between path activation and validated closure or recovery halt.
6. Every propagation object carries data identity, provenance, authority witness, boundary witness, disclosure scope, expected destination state, reversal information, source, destination, and signature.
7. Every receiver constructs and closes an independent receiving boundary. Sender admission is not receiver admission.
8. Network membership, peer trust, valid data, and destination mutation authority are independent predicates.
9. Every mutable operation declares one of the canonical reversibility classes before activation.
10. Every ordered transition emits attributable high-resolution step witnesses.
11. Invalid paths are rejected before partial instantiation where admission evidence is available.
12. Conflict negotiation preserves both source states and never silently selects a winner.
13. Exact HHS authority remains canonical; floats cannot enter boundary contracts as canonical values.
14. Queries and validation remain non-mutating except for their append-only audit receipts.
15. Public Pass 145 CLI/API operations are routed through Pass 146 boundaries; no parallel unbounded public listener is exposed.
16. Completion requires execution evidence, external capability evidence, deterministic replay, and accurate limitations.

## Canonical operation classes

- `QUERY`
- `SEARCH`
- `VALIDATE_SOURCE`
- `INGEST_TEXT`
- `RUN_SCRIPT`
- `RUN_LVM`
- `RUN_CLI_COMMAND`
- `PROPAGATE`
- `RECEIVE_PROPAGATION`
- `NEGOTIATE_CONFLICT`

## Canonical failure classes

```text
IDENTITY_UNRESOLVED
AUTHORITY_INSUFFICIENT
CAPABILITY_OVERBROAD
SOURCE_STATE_INVALID
DESTINATION_STATE_INVALID
DISCLOSURE_PATH_INVALID
PROVENANCE_INCOMPLETE
NONDETERMINISTIC_ROUTE
REVERSAL_UNDEFINED
RESOURCE_BOUND_UNRESOLVED
RECURSIVE_AUTHORITY_EXPANSION
COMPARTMENT_ESCAPE_RISK
REPLAY_PATH_INCOMPLETE
BOUNDARY_CONSTRUCTION_FAILED
```

## Full-nucleus inheritance

HHS-P146 is additive to the complete functioning HHS-P145 nucleus. It may repair inherited public dispatch seams where those seams would create alternate unbounded routes, but it may not remove inherited capabilities, evidence, obligations, or history. The release artifact is the full authoritative system nucleus, not a Pass 146 delta.
