# Pass 219 — Merged-Green Dataflow Nonregression Contract v1

Status: **NORMATIVE / FAIL-CLOSED / REPOSITORY-WIDE FOR PASS 219 AND UPSTREAM DATA FLOWS**

## Governing law

A data flow that has entered authoritative `main` through a committed, merged,
green pull request becomes an inherited constraint surface.

```text
MergedGreenDataflow(p)
AND ChangedOrRemovedOrBypassed(p)
=>
ValidatedSuccessorProof(CurrentPullRequest, p)
```

The rule applies to Pass 219 and every upstream pass represented inside the
cumulative Pass 219 runtime image.

A later commit, refactor, optimization, cleanup, migration, application,
compiler, serializer, interface, cache, adapter, runtime, test, workflow, or
documentation rewrite does not acquire authority to narrow an inherited green
data flow merely because the new implementation is shorter, faster, newer, or
located elsewhere.

## Prohibited unproved changes

Without a successor proof validated on the same pull request, the repository
MUST reject any change that:

- deletes a protected predecessor file or data-flow stage;
- removes an inherited callable, type, schema, opcode, receipt field, guard,
  validator, registration, or authority boundary;
- renames or moves a protected surface without a compatibility binding;
- replaces a complete data flow with a narrower implementation;
- simplifies away ordering, provenance, exactness, membrane depth, lineage,
  rollback, replay, receipt, or authority checks;
- removes cumulative Pass 219 registration of an inherited pass;
- introduces a new call site for a sensitive canonical or pre-canonical
  authority surface without proof;
- routes around VM81, Hash72, Hash216, RNA/cell-wall, global constraint,
  environmental admission, or other inherited validated gates;
- changes a protected test or workflow in a way that could make a formerly
  mandatory proof optional.

Silence, omission, file deletion, path movement, dead-code classification, a
new facade, or a new service does not constitute deprecation.

## Allowed successor classes

Only two successor classes may modify an inherited protected data flow.

### BACKWARD_COMPATIBLE_ITERATION

A backward-compatible iteration may add or strengthen behavior while preserving
every predecessor callable/identifier discovered by the guard.

It MUST preserve the predecessor data-flow entry points, authority count,
receipt ordering, exactness constraints, replay obligations, and existing
objects.

It may add adapters, validators, evidence, optimization, new object types, or
new implementation paths only when the old path remains valid and no alternate
canonical authority is created.

### REPAIR_FORWARD_REFINEMENT

A repair-forward refinement may change a defective predecessor identity only
when the proof explicitly records:

```text
defect
affected predecessor path/blob
superseded identifier
replacement identifier
compatibility adapter
migration behavior
negative tests
receipt continuity
rollback plan
authority delta = none unless separately authorized
```

Every removed predecessor identifier MUST resolve to an explicit replacement
and a repository-visible compatibility adapter. A repair-forward refinement is
not permission to discard historical semantics.

## Protected surface discovery

The guard protects:

1. the Pass 206 frozen core and approved-successor lineage;
2. the cumulative exact ABI and build surfaces;
3. runtime, backend, Python, native-project, contract, test, benchmark, tool,
   workflow, artifact, and evidence paths whose names bind Pass 001 through
   Pass 219;
4. root `HHS_PASS_<n>` contracts for Pass 001 through Pass 219;
5. the cumulative architecture/default/authority documents named in the
   machine manifest;
6. the nonregression guard, manifest, tests, and workflow themselves.

A newly added Pass 219/upstream data-flow path becomes protected automatically
after merge because protection is computed from the authoritative base tree.
Proof files themselves are addable in the pull request that creates them and
become protected once merged.

## Successor proof

A protected change requires one or more JSON proof records under:

```text
artifacts/pass219/merged_green_successor_proofs/
```

Each proof MUST use schema:

```text
HHS_PASS219_MERGED_GREEN_DATAFLOW_SUCCESSOR_PROOF_V1
```

The proof MUST bind the actual merge base and the exact predecessor/successor
Git blobs for every protected changed path.

The proof MUST assert every mandatory inherited invariant in the manifest and
MUST request every mandatory validation profile.

Those assertions do not self-authorize the change. The CI gate recomputes the
Git identities, public-identifier delta, sensitive-authority delta, and then
runs fixed inherited validation profiles that are not chosen by the changed
module.

## Identifier preservation

For C/C++ and exact ABI surfaces the guard discovers HHS callable/type/constant
identities from the predecessor source.

For Python it discovers top-level functions and classes.

For `BACKWARD_COMPATIBLE_ITERATION`, predecessor identifiers may not
disappear.

For `REPAIR_FORWARD_REFINEMENT`, every disappeared identifier MUST have a
declared replacement and compatibility adapter that is present in the
successor tree.

This prevents a proof document from merely asserting compatibility while the
actual callable surface has been removed.

## Sensitive-authority growth

The machine manifest contains sensitive authority symbols.

If a pull request introduces any new occurrence of one of those symbols in a
source file, that file is treated as protected even if it is a brand-new path.

Therefore a new application or adapter cannot create a shadow canonical path
simply by avoiding edits to older protected files.

## Fixed validation profiles

When a successor proof is required, the pull-request gate runs a fixed
repository-defined validation set, including:

```text
Pass 206 core freeze and successor lineage
Pass 219 cumulative membrane
cumulative exact ABI build
singleton VM81 authority export audit
Hash72 -> Hash216 ordering/lineage checks
RNA VM5184 / C++ cell-wall regression
```

A proof cannot replace these with `true`, a local mock, or an arbitrary
caller-selected command.

Additional dependency-scoped tests may be included, but they do not replace
the fixed profiles.

## Base-guard authority

The pull-request validator MUST execute the guard logic from the authoritative
base commit, not from a replacement script supplied only by the pull request.

A pull request that modifies this contract, the manifest, the guard, its tests,
or its workflow is itself a protected change and requires a successor proof
under the prior base rule.

## Push audit

The workflow also evaluates pushes to `main`.

A direct push that would have required a proof MUST fail the lineage audit.
This makes unauthorized drift repository-visible even if GitHub merge controls
were bypassed.

The push audit is detection, not a substitute for merge-layer protection.

## GitHub merge-layer requirement

Hard prevention at the Git hosting layer requires the repository ruleset for
`main` to:

```text
require pull requests
disable direct pushes
require status check: merged-green-dataflow-lineage-guard
require branch to be up to date before merge
do not permit bypass of that required check for ordinary development
```

The repository contract and CI gate are authoritative source controls. The
GitHub ruleset is the hosting-layer lock that makes a failing gate physically
unable to merge.

## Relationship to Pass 206

Pass 206 already established:

```text
BASELINE IDENTITY
+ EXPLICIT VALIDATED REPAIR SUCCESSOR
```

This Pass 219 contract generalizes that law from the Pass 206 core-function
freeze to cumulative merged-green data flows.

It does not weaken any Pass 206 freeze. A path protected by both contracts must
satisfy both.

## Acceptance

The contract is accepted only when repository-visible validation proves:

```text
unproved protected edit -> reject
unproved protected deletion -> reject
unproved protected rename -> reject
unproved new sensitive call site -> reject
compatible additive iteration with exact blob proof -> admit
repair-forward with complete replacement/adapter map -> admit
removed predecessor identifier without adapter -> reject
missing inherited invariant assertion -> reject
missing fixed validation profile -> reject
proof blob mismatch -> reject
attempt to weaken the guard itself without predecessor proof -> reject
```

The governing rule is permanent until an explicitly validated successor
contract proves an equal-or-stronger nonregression mechanism.
