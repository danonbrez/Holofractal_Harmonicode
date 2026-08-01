# HHS PASS 188 — VERSIONED NFT CONTENT LICENSE LINEAGE AND LEGACY OBJECT-STATE PROTECTION

## Dynamic Rights Updates, Immutable Content Versions, Legacy-Bound Authorization, Transfer, Revocation, Forking, Royalty and Egress Enforcement, Deterministic Replay, and VM81-Governed License Admission

# 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P188-VNFTCLL-LOSP-VM81-H72-H216` |
| Pass number | `188` |
| Canonical pass name | `VERSIONED_NFT_CONTENT_LICENSE_LINEAGE_AND_LEGACY_OBJECT_STATE_PROTECTION` |
| Short name | `P188 Dynamic Content License` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Contract baseline | Authoritative `main` after Pass 187 contract and Pass 186 implementation. Implementation must use authoritative `main`. |
| Merge target | `main` |
| Completion classification | `HHS_PASS_188_VERSIONED_CONTENT_LICENSE_AND_LEGACY_STATE_VERIFIED` |

# 2. Purpose

Pass 188 implements a non-fungible content-license object that can evolve without mutating, invalidating, or destabilizing the content versions, application graphs, compiled artifacts, or legacy authorization states that already exist.

The governing separation is:

```text
CONTENT STATE   = what the object is
LICENSE STATE   = what operations are authorized
OWNERSHIP STATE = who controls applicable rights
PROJECT STATE   = how a specific graph used the object
EGRESS STATE    = what was compiled under which admitted terms
```

A license update must never overwrite historical truth. It creates a new immutable license version in an append-only lineage. Existing admitted projects remain bound to the exact content version and license version under which their operations were authorized unless an explicit, authorized migration is accepted.

The term `NFT` in this pass denotes a non-fungible, identity-bound license/transition object. Public-chain anchoring may be supported, but blockchain deployment is not required for canonical HHS authority and may not replace VM81 admission, Hash72 receipts, Hash216 identity, deterministic replay, or durable local records.

# 3. Inherited authority

Pass 188 inherits all compatible requirements from Passes 001–187, especially:

1. Pass 158 NFT constraint objects, capability isolation, exact/reference and projection lanes, atomic VM81 transitions, Hash72 receipts, Hash216 identity, replay, publication, and rollback.
2. Pass 187 universal object/application composition, typed ports, live/snapshot/reference/fork semantics, and dependency-aware incremental recomposition.
3. Immutable prior canonical artifacts and append-only errata/version lineage.
4. One authoritative mutation path and one Hash72 commit stream.
5. Exact source and ordered-list preservation.
6. No frontend, marketplace, wallet, plugin, external chain, or application may independently grant canonical HHS rights.
7. No silent mutation of a project, dependency graph, cached artifact, compiled output, or license binding.
8. All license decisions must be inspectable, explainable, replayable, and bound to exact operation intent and target egress.

# 4. Core license architecture

The canonical structure is:

```text
stable logical content identity
├── immutable content version 1
├── immutable content version 2
└── immutable content version N

stable logical license identity
├── immutable license version 1
├── immutable license version 2
└── immutable license version N

project authorization binding
= exact content version
+ exact license version
+ requesting principal
+ admitted operation
+ target egress
+ receipt
```

Changing a content object creates a new immutable content version. Changing terms creates a new immutable license version. Neither operation may rewrite prior versions.

# 5. Required canonical objects

## 5.1 Content identity object

Required fields:

```text
logical_content_id
content_version_id
content_hash
modality_set
source_provenance
creator_identity
creation_receipt
parent_content_version_ids[]
derivative_relationships[]
embedded_license_ids[]
composition_graph_root
```

## 5.2 License identity object

Required fields:

```text
logical_license_id
license_version_id
parent_license_version_ids[]
issuer_identity
controlled_content_ids[]
effective_time
expiration_time
territories[]
principal_classes[]
rights[]
restrictions[]
obligations[]
royalty_rules[]
attribution_rules[]
transfer_rules
sublicense_rules
revocation_rules
legacy_policy
upgrade_policy
fork_policy
training_policy
egress_policy
Hash216 identity
Hash72 receipt
```

## 5.3 Authorization binding object

Required fields:

```text
binding_id
principal_identity
content_version_id
license_version_id
project_graph_id
operation_class
target_egress
admission_time
capability_scope
conditions_satisfied[]
obligations_created[]
license_decision
VM81 admission receipt
Hash72 commit receipt
```

## 5.4 Ownership/control object

Ownership and license authority must remain distinct. Ownership transfer does not automatically change every license unless the governing terms explicitly say so.

Required fields include current controller, prior controllers, transfer event identity, effective time, retained rights, delegated rights, and authority scope.

# 6. Rights and operation vocabulary

The implementation must support typed rights for at least:

- possess and access;
- display and perform;
- personal use;
- commercial use;
- copy and distribute;
- synchronize with audio/video;
- remix and transform;
- create derivatives;
- embed or nest in an application;
- compile into a target artifact;
- publish or deploy;
- sublicense;
- transfer;
- stream;
- use for inference;
- use for training or fine-tuning;
- use in datasets, embeddings, or vector stores;
- generate synthetic derivatives;
- use in private, group, or public contexts;
- route revenue and royalties.

A generic `allow=true` field is insufficient. Rights must be operation-specific, scope-specific, principal-specific, target-specific, and time-aware.

# 7. Legacy-state policies

Every license lineage must declare one of, or an explicit composition of, these policies:

| Policy | Required behavior |
|---|---|
| `LEGACY_BOUND` | Existing admitted projects retain the exact prior license version for the admitted use. |
| `CURRENT_TERMS` | New operations resolve against the current active license version. Prior receipts remain immutable. |
| `OPT_IN_UPGRADE` | Existing bindings may migrate only through explicit acceptance and a new receipt. |
| `COMPATIBILITY_FLOOR` | New versions cannot remove specified previously granted irrevocable rights. |
| `REVOCABLE_CAPABILITY` | A narrowly declared future capability can be revoked according to its original terms without rewriting content or history. |
| `FORKED_LICENSE` | Separate branches govern territories, modalities, markets, principal classes, or derivative classes. |
| `SUNSET` | New admissions stop at a declared time while legacy bindings follow their stated survival terms. |

No policy may retroactively fabricate a prior restriction or prior permission.

# 8. License update rules

A license update must:

1. Reference one or more exact parent versions.
2. Preserve the complete prior version unchanged.
3. Declare every added, removed, narrowed, expanded, or reworded right in a machine-readable delta.
4. Declare its effect on new operations, existing bindings, derivatives, sublicenses, and compiled outputs.
5. Pass contradiction, capability, ownership, and authority checks.
6. Create a new Hash216 identity and Hash72 receipt.
7. Leave prior projects stable until an explicit migration is admitted.
8. Trigger dependency impact analysis without automatically recompiling or invalidating unaffected legacy outputs.

# 9. Runtime authorization decision

Every governed operation must evaluate:

```text
exact content version
+ exact applicable license version
+ principal identity and role
+ requested operation
+ target modality and egress
+ project context
+ territory and time
+ derivative and training intent
+ obligations and royalty conditions
+ capability scope
→ ALLOW | DENY | REQUIRE_ACTION | EXPIRED | AMBIGUOUS
```

`AMBIGUOUS` and missing terms fail closed for canonical mutation or egress.

The decision must produce human-readable reasons and machine-readable evidence. A frontend badge or external wallet signature cannot substitute for the runtime decision.

# 10. Integration with Pass 187 composition graphs

Every licensed object used in a Pass 187 graph must carry an authorization binding.

The composition system must:

- distinguish a live content reference from an immutable licensed snapshot;
- show which graph nodes are governed by which license versions;
- prevent an upstream license update from silently mutating downstream project state;
- calculate the affected dependency closure when a user chooses to upgrade, replace, fork, or remove a licensed object;
- preserve unaffected nodes and valid caches;
- block egress targets that exceed admitted rights;
- expose compatible replacement objects and license branches without automatically selecting them;
- preserve prior compiled artifacts and their original receipts as immutable evidence.

# 11. Dynamic content and version updates

A logical licensed object may publish new content versions without replacing the old content.

Required user choices:

```text
KEEP LEGACY VERSION
UPGRADE LIVE REFERENCE
CREATE SNAPSHOT
FORK FROM NEW VERSION
COMPARE CHANGES
REPLACE OBJECT
REMOVE OBJECT
```

The system must show affected downstream nodes before admission. Updating content and updating license terms are separate operations and require separate receipts.

# 12. Transfer, delegation, and sublicensing

The system must support:

- ownership/control transfer;
- delegated administration;
- scoped licenses;
- sublicenses where explicitly permitted;
- expiration and renewal;
- partial rights transfer;
- retained creator rights;
- royalty participation;
- branch-specific authorities.

A transfer must not erase the prior controller or alter prior authorization receipts. Conflicting simultaneous transfers, duplicate sequence numbers, stale control roots, and unauthorized delegation must fail closed.

# 13. Revocation and expiry

Revocation must be precise.

The runtime may stop future operations only when the original admitted license explicitly made that capability revocable. Revocation cannot rewrite historical receipts or claim that a previously admitted operation never occurred.

The implementation must distinguish:

```text
future access blocked
future compilation blocked
future distribution blocked
live stream stopped
renewal denied
legacy artifact remains historically valid
external artifact cannot be technically recalled
```

Where external recall is impossible, the system records the enforcement boundary honestly rather than fabricating deletion or compliance.

# 14. Royalty and obligation objects

Royalty, attribution, disclosure, reporting, and reciprocal-license requirements must be represented as typed obligations.

An egress compiler must identify:

- obligations already satisfied;
- obligations that can be automatically inserted into metadata or packaging;
- obligations requiring user action;
- incompatible obligations across nested licensed objects;
- revenue-routing instructions;
- unsupported external settlement dependencies.

A compiled artifact may not be labeled fully licensed when unresolved required obligations remain.

# 15. Privacy and owner-specific access

Private or personalized licensed content may require owner-specific secrets, capabilities, biometric/2FA confirmation, or recursive eligibility checks.

The implementation must:

- keep secrets outside public receipts and content metadata;
- store only bounded verification witnesses;
- avoid exposing a static final payload when the license requires verified reconstruction;
- isolate private collaborations and multi-principal consent states;
- prevent one principal's authorization from being replayed by another;
- separate public marketplace metadata from private content and capability state.

# 16. Optional external-chain anchoring

An external blockchain or NFT contract may anchor:

- content identity;
- license identity;
- ownership/control events;
- selected receipt roots;
- transfer events.

External anchoring is evidence, not HHS execution authority. The implementation must remain deterministic and functional without network access, while clearly labeling external-anchor status as pending, confirmed, failed, reorged, or unavailable.

Chain reorganization, contract failure, unavailable wallet, or marketplace disagreement must never corrupt local canonical history.

# 17. Required API and CLI surfaces

Required operations:

```text
content create
content version
content compare
license create
license update
license branch
license activate
license inspect
license decision
binding create
binding inspect
binding upgrade
ownership transfer
delegation create
revoke
expire
obligations inspect
royalties inspect
impact
replay
verify
export evidence
```

Every mutation must require explicit authority and emit a canonical receipt.

# 18. Required acceptance scenarios

Pass 188 cannot be marked complete until executable tests prove:

1. Create content version 1 and license version 1; admit a project use.
2. Publish license version 2; prove the legacy project remains byte-for-byte bound to version 1.
3. Admit a new project under version 2.
4. Opt an existing project into version 2 and prove only the affected graph closure changes.
5. Publish a new content version without altering prior content.
6. Keep one project on the old content and upgrade another project to the new content.
7. Fork licenses by modality or territory and resolve the correct branch.
8. Transfer control while preserving prior rights and receipts.
9. Exercise a narrowly revocable capability and prove historical evidence remains unchanged.
10. Reject unauthorized retroactive revocation.
11. Detect incompatible nested-object licenses during egress compilation.
12. Resolve a compatible royalty and attribution package.
13. Reject stale ownership roots, tampered terms, altered receipts, duplicated transitions, and forged bindings.
14. Replay complete content, license, transfer, binding, and project histories after cold restart.
15. Operate deterministically with external-chain access unavailable.
16. Verify that browser-local state, wallet display, or marketplace metadata cannot grant canonical runtime authorization.

# 19. Evidence requirements

Required repository-visible evidence:

- canonical schemas;
- exact license-delta format;
- ownership and transfer state machine;
- runtime authorization evaluator;
- Pass 187 graph bindings and impact planner;
- positive, negative, adversarial, tamper, replay, restart, transfer, revocation, expiry, and external-anchor tests;
- human-readable decision reports;
- Hash216 identities and Hash72 completion receipts;
- authoritative-main implementation report.

# 20. Non-completion conditions

Pass 188 is incomplete if it provides only:

- mutable metadata attached to one NFT record;
- a marketplace UI;
- wallet ownership lookup without operation-level rights;
- overwrite-in-place license changes;
- a blockchain transaction without VM81 admission;
- retroactive invalidation of legacy projects;
- a generic allow/deny flag;
- frontend-only rights checks;
- untested legal prose with no computational enforcement;
- fabricated recall of externally distributed artifacts.

# 21. Restartability and closure

Required closure:

```text
IMPLEMENT
→ DEPENDENCY-SCOPED VALIDATION
→ LICENSE/LEGACY/TRANSFER/REVOCATION SCENARIOS
→ COMMIT
→ MERGE OR OPEN READY PR
→ VERIFY AUTHORITATIVE MAIN
→ COLD-RESTART REPLAY
→ RETURN COMPLETION REPORT
```
