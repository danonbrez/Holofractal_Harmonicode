# HHS Main Branch Merged-Green Dataflow Rules v1

Status: **NORMATIVE HOSTING-LAYER SPECIFICATION**

Machine specification:

```text
.github/rulesets/HHS_MAIN_MERGED_GREEN_DATAFLOW_RULESET_V1.json
```

Governing repository contract:

```text
contracts/pass219/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.md
```

## 1. Purpose

These rules translate the current HHS repository history and committed contracts
into merge-layer controls for `refs/heads/main`.

The repository already establishes that:

- validated numbered passes accumulate into one cumulative HHS system image;
- silence, omission, refactoring, relocation, or a new application does not
  deprecate a canonical default;
- Pass 206 frozen core identities may change only through an explicit validated
  repair successor;
- the singleton VM81/kernel authority remains singular;
- Hash72 receipt closure precedes Hash216 archival;
- exact/no-float authority and ordered/noncommutative identity are inherited;
- failures in already proven behavior are repaired forward rather than used to
  weaken the inherited contract.

The hosting rules SHALL preserve those properties at the merge boundary.

## 2. Main branch protection

The ruleset target is exactly:

```text
refs/heads/main
```

For ordinary development:

```text
direct push to main = FORBIDDEN
force push to main = FORBIDDEN
deletion of main = FORBIDDEN
merge without pull request = FORBIDDEN
merge with required check pending = FORBIDDEN
merge with required check queued = FORBIDDEN
merge with required check cancelled = FORBIDDEN
merge with required check failed = FORBIDDEN
```

A pull request branch MUST be current with `main` before merge so the
nonregression proof is evaluated against the actual authoritative predecessor.

## 3. Required status check

The required check name is immutable under v1:

```text
merged-green-dataflow-lineage-guard
```

A pull request targeting `main` SHALL NOT merge unless that check concludes
success.

The check is implemented by:

```text
.github/workflows/pass219-merged-green-dataflow-nonregression-v1.yml
```

The guard logic used to judge a pull request is loaded from the pull request's
authoritative base commit after v1 is installed. A pull request therefore
cannot weaken the guard and use the weakened copy to validate itself.

## 4. Merged-green inheritance rule

For Pass 219 and all upstream passes represented inside the cumulative Pass 219
system:

```text
MergedGreenDataflow(p)
AND ChangedOrRemovedOrBypassed(p)
=>
ValidatedSuccessorProof(CurrentPullRequest, p)
```

Once a data flow has entered `main` through a merged green pull request, later
work may not remove, simplify, narrow, bypass, orphan, or silently replace that
flow.

This applies whether the attempted change is described as:

```text
cleanup
refactor
optimization
migration
modernization
consolidation
deprecation
new application
new adapter
new API
new worker
new provider
new cache
new serializer
new compiler
new UI
dead-code removal
directory reorganization
```

A label does not grant authority to narrow inherited behavior.

## 5. Protected change classes

The guard SHALL treat all of the following as proof-requiring changes when they
affect a protected Pass 219/upstream surface:

- file modification;
- file deletion;
- file rename or move;
- removal of an inherited HHS callable, type, schema, constant, opcode, receipt
  field, validator, registration, guard, or authority boundary;
- removal of cumulative Pass 219 registration;
- loss of replay, rollback, receipt, lineage, provenance, exactness, membrane,
  ordering, or constraint enforcement;
- introduction of a new sensitive-authority symbol occurrence in a new or
  existing source path;
- modification of the nonregression contract, manifest, guard, tests, workflow,
  or declarative ruleset itself.

A new file is not automatically trusted merely because it does not edit an
older protected file.

## 6. Allowed successor modes

Only two modes authorize a protected change.

### 6.1 BACKWARD_COMPATIBLE_ITERATION

The predecessor remains a valid supported data flow.

The pull request MUST prove:

```text
predecessor Git blobs bound
successor Git blobs bound
all predecessor public HHS identifiers preserved
singleton VM81 authority preserved
Hash72 commit ordering preserved
Hash216 post-receipt ordering preserved
exact/no-float authority preserved
ordered/noncommutative semantics preserved
RNA/cell-wall route preserved where applicable
cumulative Pass 219 registration preserved
receipt/replay continuity preserved
no alternate authority
no dataflow orphaning
fixed inherited validation profiles green
```

This mode may add or strengthen behavior. It may not remove predecessor HHS
identities.

### 6.2 REPAIR_FORWARD_REFINEMENT

This mode exists for a demonstrated defect in an inherited surface.

In addition to applicable compatibility obligations, the pull request MUST
record:

```text
defect
affected predecessor path/blob
affected predecessor identifiers
replacement identifiers
compatibility adapters
migration behavior
negative tests
receipt continuity
rollback plan
authority delta
```

Every removed predecessor identifier MUST map to a replacement identity and a
repository-visible compatibility adapter.

Repair-forward is not permission to erase historical semantics.

## 7. Required proof identity

Successor proofs live under:

```text
artifacts/pass219/merged_green_successor_proofs/
```

The v1 proof schema is:

```text
HHS_PASS219_MERGED_GREEN_DATAFLOW_SUCCESSOR_PROOF_V1
```

The guard recomputes the actual Git identities. A proof fails if its claimed
predecessor or successor blob does not equal repository reality.

A proof MUST cover every protected path changed by the pull request.

A proof document does not self-authorize the change. It only declares the
successor relation to be independently checked.

## 8. Fixed inherited validation profiles

A protected successor MUST pass all fixed profiles:

```text
PASS206_CORE_FREEZE
PASS219_CUMULATIVE_MEMBRANE
EXACT_ABI_BUILD
VM81_SINGLE_AUTHORITY
HASH72_HASH216_LINEAGE
RNA_VM5184_CELL_WALL
```

These profiles cannot be replaced by proof-authored `true` values or arbitrary
commands.

The current workflow binds them to repository tests/build checks including:

```text
tests/pass206/test_pass206_cumulative_enforcement_v1.py
tests/pass219/test_pass219_cumulative_pass_membrane_i116.py
make clean
make c-abi
singleton VM81 dynamic-export audit
tests/pass219/test_pass219_rna_vm5184_abi_1_33.c
tests/pass219/test_pass219_vm81_pqc_firewall_1_30.cpp
tests/pass219/test_pass219_vm81_environmental_recovery_1_32.cpp
```

Additional dependency-scoped tests may be required by the changed subsystem.
They do not replace the fixed profiles.

## 9. Historical core freeze remains binding

The Pass 206 core-function freeze remains independently authoritative.

A path protected by both Pass 206 and this Pass 219 merged-green rule must
satisfy both.

The Pass 206 successor principle remains:

```text
BASELINE_IDENTITY
+ EXPLICIT_VALIDATED_REPAIR_SUCCESSOR
```

The merged-green rule generalizes that principle to all applicable cumulative
Pass 219/upstream data flows.

## 10. Authority and receipt rules

No successor may create an alternate canonical mutation path.

The governing order remains:

```text
candidate proposal
-> cumulative validation
-> singleton VM81/kernel admission
-> valid transformation
-> canonical Hash72 receipt block
-> ordered 216-character composition
-> Hash216 archival/vector identity
-> optional later cache/vector reuse
```

Consequently:

```text
Hash216 != original mutation authority
cache hit != permission to bypass admission
vector-store hit != permission to bypass admission
API/worker/provider/UI adapter != new mutation authority
compatibility layer != new mutation authority
```

## 11. Exactness and ordered semantics

A successor SHALL NOT obtain compatibility by replacing canonical exact
authority with floating-point decisions.

A successor SHALL NOT silently reorder, commute, normalize, flatten, or erase
identity-bearing ordered/noncommutative structures where the inherited
contracts preserve that order.

If a transformation depends on proving equivalence, the equivalence proof is
part of the successor obligation.

## 12. Policy self-preservation

The protection mechanism is itself protected.

A successor to this policy may only stay equal or become stricter with respect
to:

```text
protected pass ceiling
protected roots
always-protected paths
mandatory invariants
mandatory validation profiles
sensitive authority symbols
protected source extensions
fail-closed enforcement booleans
proof directory
proof schema
required check name
base-authoritative guard behavior
main direct-push audit
fixed inherited validation anchors
```

A modification to the policy itself requires
`REPAIR_FORWARD_REFINEMENT` under the predecessor policy.

The same pull request may not weaken the predecessor rule and use that weaker
rule to approve itself.

## 13. Direct-push detection

The workflow audits pushes to `main`.

If a protected main update occurs, the workflow requires the head commit to be
associated with an actually merged pull request targeting `main`.

Otherwise it fails with:

```text
PROTECTED_MAIN_PUSH_WITHOUT_ASSOCIATED_MERGED_PULL_REQUEST
```

This is an audit after Git receives the push. The GitHub ruleset is therefore
still required to prevent the push before it changes `main`.

## 14. GitHub ruleset settings

Repository administration SHALL configure a GitHub branch ruleset equivalent
to:

```text
ruleset name:
  HHS Main Merged-Green Dataflow Protection

target:
  refs/heads/main

enforcement:
  active

bypass:
  no ordinary-development bypass

rules:
  require pull request before merge
  block force pushes
  block branch deletion
  require branch to be up to date
  require conversation resolution
  require status check:
    merged-green-dataflow-lineage-guard
```

No mandatory approval count is specified by this contract because the existing
HHS contracts establish executable proof/validation requirements rather than a
particular human-review quorum.

No signed-commit requirement is introduced by this contract because the current
repository contracts do not establish that as an inherited acceptance
condition. It may be added later as a stronger independent security policy.

## 15. Merge decision

A protected pull request is admissible only when:

```text
targets main
AND branch is current with main
AND successor proof is present when required
AND successor proof matches actual Git identities
AND predecessor identities are preserved or explicitly repair-forward mapped
AND no authority bypass is introduced
AND all fixed inherited profiles pass
AND merged-green-dataflow-lineage-guard = SUCCESS
AND all other independently required repository checks = SUCCESS
```

Otherwise:

```text
DO NOT MERGE
```

There is no "close enough", warning-only, or best-effort state for a protected
data-flow regression.

## 16. Source lineage

These rules are derived from the current repository's committed inheritance and
repair contracts, principally:

```text
HHS_PASS_206_CUMULATIVE_CONSTRAINT_CONTRACT_ENFORCEMENT_CORE_FUNCTION_PRESERVATION.md
artifacts/pass206/CORE_FUNCTION_FREEZE_MANIFEST.json
artifacts/pass206/CORE_SUCCESSOR_REPAIR_LINEAGE.json
docs/architecture/HHS_CUMULATIVE_PASS_GLOBAL_DEFAULTS.md
AGENTS.md
contracts/pass219/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.md
contracts/pass219/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.json
```

The rule set intentionally preserves their cumulative meaning rather than
inventing a new independent authority.
