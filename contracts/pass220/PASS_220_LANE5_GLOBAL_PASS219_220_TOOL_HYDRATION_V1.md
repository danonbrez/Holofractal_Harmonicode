# Pass 220 — Global Lane 5 Pass 219/220 Tool Hydration Constraint

**Schema:** `HHS_PASS_220_LANE5_GLOBAL_PASS219_220_TOOL_HYDRATION_V1`  
**Status:** additive global constraint / candidate-memory hydration / selector-preserving  
**Base:** `main @ 156d4138f2640c6fd8937f96ffb5c030ae9b7952`

## 1. Purpose

This cycle does **not** replace, reorder, or reinterpret the Lane 5 selection
algorithm.

The circular phase-fiber result from PR #586 and the latency evidence from
PR #587 are promoted only as a **global constraint condition** over compatible
Lane 5 candidate/tool surfaces:

```text
local circular phase closure at every compatible scale
+ inherited Pass 219/220 constraints
+ exact 5184 projection
+ ordered Hash216 identity
+ registered C++ tool surface
= admissible warm Lane 5 tool descriptor
```

The existing Lane 5 selector remains responsible for candidate selection under
its existing ordering rules.

## 2. Global enforcement

Every warmed tool MUST satisfy all of the following:

1. Lane 5 route-selection implementation is unchanged.
2. Circular phase-fiber closure is a global admissibility/constraint property,
   not a replacement comparator.
3. The tool has an exact 5,184-bit / 648-byte projection.
4. The tool has an ordered `PREVIOUS || CHANGE || RECEIPT` Hash216 identity,
   exactly 216 Hash72 characters.
5. The tool binds the Pass 220 I042 shared multimodal root.
6. The tool binds the generic native C++ Lane 5 tool membrane
   `hhs_pass220_lane5_global_tool_surface_validate_v1`.
7. The tool remains candidate-only.
8. The tool has no VM81 mutation, Hash72 mint, Hash216 canonical mint,
   canonical persistence, or floating-point canonical authority.
9. Warm-cache reuse never bypasses Lane 5, RNA/PQC, or signed environmental
   VM81 admission.
10. Repository source, registered service metadata, and authoritative merge
    history remain source authority.

## 3. Required warm inventory

Two repository-visible constructor classes are mandatory.

### 3.1 Registered Pass 219/220 services

The authoritative service inventory is derived from literal
`registry.register_function(...)` declarations in
`hhs_runtime/hhs_service_registry_v1.py` whose declared name/module/type,
contracts, witnesses, validators, guards, or rejection metadata explicitly
bind Pass 219 or Pass 220.

Every such registration MUST appear exactly once in the warm tool graph.

### 3.2 Authoritative merged Pass 219/220 pull requests

The authoritative PR inventory is derived from first-parent Git history.

A merged PR belongs to this inventory when its merge/squash message or changed
path set explicitly binds Pass 219 or Pass 220. Its tool descriptor retains:

- PR number;
- authoritative merge commit;
- subject;
- Pass 219/220 scope;
- deterministic changed-path inventory.

Unmerged branches and open pull requests may be visible elsewhere as candidate
knowledge, but they are not members of the authoritative merged-history warm
inventory and gain no authority by being visible.

## 4. 5,184 multimodal knowledge graph

Every service and merged-PR constructor becomes one node in:

`HHS_PASS_220_LANE5_PASS219_220_5184_TOOL_GRAPH_V1`.

Each node carries:

```text
source/provenance identity
Pass scope
exact 5184-bit projection
projection SHA-256
ordered Hash216
I042 shared multimodal root
C++ tool-surface symbol/version
candidate-only and no-authority flags
```

Every node has an explicit edge to the same Pass 220 I042 shared multimodal
root. The graph is therefore an additive tool dimension of the existing Lane 5
multimodal knowledge graph, not a detached registry or second execution engine.

## 5. Hash216 vector-store warming

Deployment startup MUST attempt to hydrate the complete graph into the inherited
Pass 174 `PersistentEncryptedVectorStore`.

Warm records use:

- SQLite/WAL/FULL persistence;
- AES-GCM authenticated encryption;
- exact 648-byte snapshots;
- `Hash216Array` positional indexing;
- deterministic operation keys;
- idempotent reuse when an identical tool record is already warm.

The vector store remains a derived retrieval/cache projection. It is not source
authority and does not create a canonical state transition merely because an
entry exists or matches.

A startup warm failure makes the Lane 5 warm-tool graph unavailable
fail-closed. It does not grant fallback authority and does not replace the
existing Runtime OS or Lane 5 selector.

## 6. Native C++ tool membrane

All tool descriptors pass through one additive generic C++ membrane:

`hhs_pass220_lane5_global_tool_surface_validate_v1`.

The membrane verifies fixed structure/version, exact 5,184 projection width,
Pass 219/220 scope, candidate-only status, selector-preservation status,
Hash216 width, SHA-256 descriptor fields, and zero canonical authority.

This native membrane makes every warm service/PR descriptor a typed C++ Lane 5
tool surface without rewriting the underlying historical implementation or
creating per-PR executable code.

## 7. Runtime exposure

The Runtime OS installs the warm lifecycle before public projection and exposes
read-only diagnostics:

```text
GET/HEAD /api/runtime/pass220/lane5/tools/warm-status
GET      /api/runtime/pass220/lane5/tools/graph
```

The graph endpoint is available only after successful hydration.

## 8. Acceptance

Acceptance requires:

```text
Lane 5 selector diff == empty
AND Pass219 registered-service inventory coverage == complete
AND Pass220 registered-service inventory coverage == complete
AND authoritative merged Pass219/220 PR inventory coverage == complete
AND every tool projection == 5184 bits
AND every tool Hash216 width == 216
AND every tool C++ membrane == valid
AND every tool I042 root == shared root
AND vector warm == complete and replayable
AND second warm reuses unchanged records
AND all canonical authority flags == false
AND deployment startup wiring is present
AND inherited I042/G3/Lane5 constraint regressions remain green
```

No acceptance statement from this cycle may say that the Lane 5 selection
algorithm was replaced.
