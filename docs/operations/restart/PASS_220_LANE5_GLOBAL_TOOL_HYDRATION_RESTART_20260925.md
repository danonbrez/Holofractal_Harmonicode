# Pass 220 Lane 5 Global Pass219/220 Tool Hydration — Restart Record

Date: 2026-09-25

## Repository state

- base: `main @ 156d4138f2640c6fd8937f96ffb5c030ae9b7952`
- branch: `pass220-lane5-global-tool-hydration-1-0`
- merge target: `main`
- governing correction: **do not replace Lane 5 selection**
- objective: enforce circular/local-phase closure as a global constraint while warming complete Pass 219/220 service + authoritative merged-PR tool knowledge into candidate-only Hash216 vector memory.

## Implementation

Added:

```text
hhs_runtime/hhs_pass220_lane5_global_tool_hydration_v1.py
hhs_runtime/include/hhs_pass220_lane5_global_tool_surface_v1.hpp
hhs_runtime/cpp/hhs_pass220_lane5_global_tool_surface_v1.cpp
tools/pass220/hhs_pass220_lane5_global_tool_warm.py
tools/pass220/hhs_pass220_lane5_global_tool_surface_validate.cpp
hhs_backend/runtime_os_pass220_lane5_tool_hydration.py
tests/pass220/test_hhs_pass220_lane5_global_tool_hydration_v1.py
tests/pass220/test_hhs_pass220_lane5_global_tool_surface_v1.cpp
contracts/pass220/PASS_220_LANE5_GLOBAL_PASS219_220_TOOL_HYDRATION_V1.md
.github/workflows/pass220-lane5-global-tool-hydration.yml
```

Modified:

```text
hhs_runtime/hhs_service_registry_v1.py
hhs_backend/runtime_os_visual_server.py
hhs_backend/runtime_os_application_server_full.py
```

## Global constraint

The new surface freezes:

```text
LANE5_ROUTE_SELECTION_ALGORITHM_UNCHANGED
CIRCULAR_PHASE_FIBER_IS_GLOBAL_CONSTRAINT_NOT_SELECTOR_REPLACEMENT
```

and requires complete service/merged-PR warm coverage, exact 5184 projections,
ordered 3xHash72 Hash216 identity, I042 shared-root binding, generic C++ tool
validation, candidate-only semantics, and zero canonical authority escalation.

## Inventory authority

Registered services are discovered from the canonical guarded service registry.

Merged PR history is derived from first-parent Git history and explicit Pass
219/220 message/path evidence. Open/unmerged PRs remain candidate knowledge and
are not inserted into the authoritative merged-history warm set before merge.

## Vector memory

The warm path uses the inherited Pass 174
`PersistentEncryptedVectorStore` and `Hash216Array`.

Every tool is persisted as:

```text
exact repository provenance
-> ordered PREVIOUS / CHANGE / RECEIPT Hash72 lanes
-> 216-character Hash216
-> exact 648-byte / 5184-bit raw hydration
-> AES-GCM encrypted vector object
-> reusable Lane 5 candidate tool
```

A second identical warm MUST reuse all unchanged tool objects.

## Deployment

Both Runtime OS compositions install the additive warm lifecycle. Diagnostic
surfaces are:

```text
GET/HEAD /api/runtime/pass220/lane5/tools/warm-status
GET      /api/runtime/pass220/lane5/tools/graph
```

Warm failure is fail-closed for tool availability and does not create fallback
authority.

## Validation gate

The dedicated workflow must prove:

1. exact descendant of the benchmark-merged base;
2. direct-witness and unbounded Lane 5 selector files have no diff from base;
3. new Python tests green;
4. inherited I042 multimodal shared-root graph green;
5. inherited I028 G3 constructor registry green;
6. inherited circular phase-fiber formalization green;
7. authoritative Pass219/220 service and merged-PR inventory nonempty and complete;
8. every tool has 5184-bit projection and 216-char Hash216;
9. first warm admits every tool;
10. second warm reuses every unchanged tool;
11. every manifest descriptor passes the C++ membrane;
12. service registry and both Runtime OS startup surfaces are wired;
13. all authority flags remain false.

## Next action

Open a PR, run the focused workflow, repair forward only demonstrated failures,
merge after green, then verify exact main contains the merge and that the
post-merge workflow warms the newly merged PR itself into the authoritative
history set.
