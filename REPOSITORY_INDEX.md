# HHS Repository Index

This file is the curated navigation map for the Holofractal Harmonicode (HHS) repository. It points to canonical implementation surfaces, formal contracts, pass documentation, validation entry points, deployment assets, and user-facing applications without duplicating the repository's large pass-by-pass evidence archive.

> **Authority note:** this index is navigational. Canonical authority remains with the applicable contracts, exact runtime implementation, validation evidence, receipt lineage, and the current authoritative `main` state.

## Start here

| Path | Purpose |
|---|---|
| [`README.md`](README.md) | System overview, current authoritative state, startup, and major acceptance surfaces |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Ownership boundaries, canonical paths, layering, and anti-drift rules |
| [`RUNTIME_FLOW.md`](RUNTIME_FLOW.md) | End-to-end execution, admission, receipt, replay, API, worker, and visual flow |
| [`GLOSSARY.md`](GLOSSARY.md) | Stable definitions for principal HHS terms |
| [`AGENTS.md`](AGENTS.md) | Repository navigation, implementation, validation, and agent execution rules |
| [`CHANGELOG.md`](CHANGELOG.md) | Repository-level change history |
| [`docs/README.md`](docs/README.md) | Documentation entry point |

## Full Hash216 file and dependency graph

The repository-wide generated deep index is [REPOSITORY_HASH216_DEPENDENCY_TREE.md](REPOSITORY_HASH216_DEPENDENCY_TREE.md). It binds the Pass 214 complete Git-tree census, Pass 173 dependency observations, Pass 191 three-Hash72 Hash216 identities, and Lane 5 repository capability topology into a reproducible read-only file/dependency graph.

Generation, authority checks, evidence upload, and refresh are defined by [.github/workflows/repository-hash216-dependency-index.yml](.github/workflows/repository-hash216-dependency-index.yml).

## Canonical execution stack

### Runtime authority

- [`hhs_runtime/`](hhs_runtime/) — canonical runtime substrate, VM81 execution/admission surfaces, Hash72/Hash216 integration, native code, pass runtimes, and testing.
  - [`hhs_runtime/core/`](hhs_runtime/core/) — core runtime components.
  - [`hhs_runtime/core_sandbox/`](hhs_runtime/core_sandbox/) — governed compatibility and sandbox authority surfaces.
  - [`hhs_runtime/c/`](hhs_runtime/c/) — C runtime sources.
  - [`hhs_runtime/cpp/`](hhs_runtime/cpp/) — C++ runtime and ABI surfaces.
  - [`hhs_runtime/native/`](hhs_runtime/native/) — native execution components.
  - [`hhs_runtime/include/`](hhs_runtime/include/) — native headers.
  - [`hhs_runtime/acceleration/`](hhs_runtime/acceleration/) — acceleration-specific runtime work.
  - [`hhs_runtime/testing/`](hhs_runtime/testing/) — runtime-focused validation support.
  - [`hhs_runtime/pass218/`](hhs_runtime/pass218/), [`pass219/`](hhs_runtime/pass219/), and [`pass220/`](hhs_runtime/pass220/) — recent pass-scoped runtime implementations.

### Python control and API layers

- [`hhs_python/runtime/`](hhs_python/runtime/) — Python runtime controller and native bridge surfaces.
- [`hhs_backend/`](hhs_backend/) — backend servers, orchestration, assistant/runtime services, APIs, and visual projection.
  - [`hhs_backend/api/`](hhs_backend/api/) — HTTP/API routes.
  - [`hhs_backend/runtime/`](hhs_backend/runtime/) — backend runtime services.
  - [`hhs_backend/websocket/`](hhs_backend/websocket/) — WebSocket transport.
  - [`hhs_backend/visual_server.py`](hhs_backend/visual_server.py) — integrated visual-development server entry point.

### Graph and persistence

- [`hhs_graph/`](hhs_graph/) — receipt and multimodal graph topology.
- [`hhs_storage/`](hhs_storage/) — durable state and persistence primitives.

## Formal contracts and specifications

- [`contracts/`](contracts/) — machine- and human-readable authority contracts.
  - [`contracts/authority/`](contracts/authority/) — authority-specific contracts.
  - Pass-scoped contracts are organized as `contracts/passNNN/`; current repository surfaces include [`pass219/`](contracts/pass219/), [`pass220/`](contracts/pass220/), and [`pass221/`](contracts/pass221/).
- [`docs/HARMONICODE_SPEC_v1.md`](docs/HARMONICODE_SPEC_v1.md) — Harmonicode language/system specification.
- [`docs/HARMONICODE_IR_v1.md`](docs/HARMONICODE_IR_v1.md) — Harmonicode IR.
- [`docs/HHS_KERNEL_INVARIANT_REGISTRY_V1.md`](docs/HHS_KERNEL_INVARIANT_REGISTRY_V1.md) — kernel invariant registry.
- [`docs/HHS_ACCEPTANCE_GATE.md`](docs/HHS_ACCEPTANCE_GATE.md) — acceptance-gate documentation.
- [`docs/HASH72_FORMAL_THEOREM_v1.md`](docs/HASH72_FORMAL_THEOREM_v1.md) — Hash72 formal theorem surface.
- [`docs/HARMONICODE_AXIOM_AND_PROJECTION_REGISTRY.md`](docs/HARMONICODE_AXIOM_AND_PROJECTION_REGISTRY.md) — axiom and projection registry.
- [`docs/HARMONICODE_FORMAL_EVALUATION_PROTOCOL.md`](docs/HARMONICODE_FORMAL_EVALUATION_PROTOCOL.md) — formal evaluation protocol.

## Documentation library

| Directory | Contents |
|---|---|
| [`docs/architecture/`](docs/architecture/) | Architecture and cross-layer design contracts |
| [`docs/deployment/`](docs/deployment/) | Deployment and production operations |
| [`docs/manuals/`](docs/manuals/) | Operational and optimization manuals |
| [`docs/operations/`](docs/operations/) | Operational procedures and records |
| [`docs/research/`](docs/research/) | Research material |
| [`docs/tutorials/`](docs/tutorials/) | Tutorials and learning material |
| [`docs/whitepapers/`](docs/whitepapers/) | White papers and extended manuscripts |
| [`docs/SPECS/`](docs/SPECS/) | Additional specifications |

Pass-specific documentation is organized primarily under `docs/passNNN/`. The current documentation tree extends through [`docs/pass221/`](docs/pass221/), while older pass material may also remain at the repository root for lineage compatibility.

## Native implementation projects

The [`native_projects/`](native_projects/) tree contains pass-scoped native implementations, contracts, validation harnesses, deployment assets, and restartable delivery records.

### Language, compiler, and exact-runtime foundations

- [`native_projects/hhs_harmonicode_language/`](native_projects/hhs_harmonicode_language/)
- [`native_projects/hhs_harmonicode_interpreter/`](native_projects/hhs_harmonicode_interpreter/)
- [`native_projects/hhs_compiler_artifact_pipeline/`](native_projects/hhs_compiler_artifact_pipeline/)
- [`native_projects/hhs_exact_recursive_symbolic_runtime/`](native_projects/hhs_exact_recursive_symbolic_runtime/)
- [`native_projects/hhs_pass159_harmonicode_toolchain/`](native_projects/hhs_pass159_harmonicode_toolchain/)
- [`native_projects/hhs_pass160_validated_transition_runtime/`](native_projects/hhs_pass160_validated_transition_runtime/)

### VM81, hydration, composition, and operation fabrics

- [`native_projects/hhs_pass175_virtual_instruction_processor/`](native_projects/hhs_pass175_virtual_instruction_processor/)
- [`native_projects/hhs_pass175_vm5184_g243/`](native_projects/hhs_pass175_vm5184_g243/)
- [`native_projects/hhs_pass183_probability_hydration/`](native_projects/hhs_pass183_probability_hydration/)
- [`native_projects/hhs_pass186_x64_vm81_q144/`](native_projects/hhs_pass186_x64_vm81_q144/)
- [`native_projects/hhs_pass187_bott_hydration/`](native_projects/hhs_pass187_bott_hydration/)
- [`native_projects/hhs_pass187_composition_fabric/`](native_projects/hhs_pass187_composition_fabric/)
- [`native_projects/hhs_pass188_bott_runtime/`](native_projects/hhs_pass188_bott_runtime/)
- [`native_projects/hhs_pass189_hqlh_runtime/`](native_projects/hhs_pass189_hqlh_runtime/)
- [`native_projects/hhs_pass190_operation_fabric/`](native_projects/hhs_pass190_operation_fabric/)
- [`native_projects/hhs_pass191_dyadic_quartic_phase_lattice/`](native_projects/hhs_pass191_dyadic_quartic_phase_lattice/)

### Recent Pass 219–220 native surfaces

- [`native_projects/hhs_pass219_discrete_transport_conservation/`](native_projects/hhs_pass219_discrete_transport_conservation/)
- [`native_projects/hhs_pass219_ethical_scope_membrane/`](native_projects/hhs_pass219_ethical_scope_membrane/)
- [`native_projects/hhs_pass219_rml13_route_binding/`](native_projects/hhs_pass219_rml13_route_binding/)
- [`native_projects/hhs_pass219_rml14_route_bound_receipt/`](native_projects/hhs_pass219_rml14_route_bound_receipt/)
- [`native_projects/hhs_pass219_rml15_route_reverse_replay/`](native_projects/hhs_pass219_rml15_route_reverse_replay/)
- [`native_projects/hhs_pass220_gfx1_native_render_commands/`](native_projects/hhs_pass220_gfx1_native_render_commands/)

## Visual environment and applications

- [`hhs_gui/`](hhs_gui/) — primary GUI and visual runtime surface.
  - [`hhs_gui/rendering/`](hhs_gui/rendering/) — rendering layer.
  - [`hhs_gui/runtime/`](hhs_gui/runtime/) — GUI runtime integration.
  - [`hhs_gui/runtime_apps/`](hhs_gui/runtime_apps/) — runtime applications.
  - [`hhs_gui/runtime_os/`](hhs_gui/runtime_os/) — runtime-OS visual surfaces.
  - [`hhs_gui/spatial_environment/`](hhs_gui/spatial_environment/) — spatial environment.
- [`applications/`](applications/) — user-facing application packages:
  - [`applications/holofractal_harmonizer/`](applications/holofractal_harmonizer/)
  - [`applications/pass174_visual_ide/`](applications/pass174_visual_ide/)
  - [`applications/probability_hydration_studio/`](applications/probability_hydration_studio/)
  - [`applications/storybook_reel_studio/`](applications/storybook_reel_studio/)

## Validation and CI entry points

Repository-level baseline validation:

```bash
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
```

Pass-specific validation belongs with the implementation it validates. Example:

```bash
make -C native_projects/hhs_pass190_operation_fabric validate
```

CI configuration and automation live under [`.github/`](.github/).

## Deployment and operations

- [`docs/deployment/`](docs/deployment/) — deployment documentation.
- [`docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md`](docs/deployment/DIGITALOCEAN_INSTALLATION_OPERATIONS_MAINTENANCE.md) — DigitalOcean installation, operation, backup, restore, rollback, security, and maintenance.
- [`docs/operations/`](docs/operations/) — operational procedures and state records.
- Root `start.sh` remains the integrated local startup entry point described by the README.

## Pass and artifact naming conventions

The repository intentionally preserves historical evidence. Use the pass number as the primary join key across layers:

| Pattern | Meaning |
|---|---|
| `CHANGELOG_PASS_NNN.md` | Pass-specific history and delivery notes |
| `*_PASS_NNN.md`, `*_PASS_NNN.json` | Pass evidence, reports, witnesses, registries, and snapshots |
| `contracts/passNNN/` | Normative pass contracts |
| `docs/passNNN/` | Pass documentation and formalization |
| `hhs_runtime/passNNN/` | Pass-scoped runtime implementation |
| `native_projects/hhs_passNNN_*/` | Native pass implementation/project nucleus |

Some older passes use suffixes such as `_1`, `_2`, or historical naming variants. Preserve those names as lineage rather than renaming them solely for cosmetic consistency.

## Canonical path policy

- Prefer structured package paths for new canonical implementation.
- Treat root-level compatibility modules and historical pass artifacts as lineage/compatibility surfaces unless the applicable contract explicitly makes them authoritative.
- Do not bypass VM81 admission, Hash72 receipt lineage, Hash216 identity/topology, exact arithmetic, ordered-product semantics, or replay requirements merely to simplify integration.
- When a new long-lived subsystem becomes canonical, add its stable entry point to this index.
- Do not turn this file into an exhaustive generated manifest; keep it focused on durable navigation and use pass naming conventions to locate detailed evidence.

## Fast repository lookup

Examples:

```bash
# Find all tracked files associated with a pass.
git ls-files | grep -i 'pass219'

# Find canonical and compatibility references to a subsystem.
git grep -n 'Hash216'

# List native pass projects.
find native_projects -maxdepth 1 -type d -name 'hhs_pass*' | sort

# List pass documentation.
find docs -maxdepth 1 -type d -name 'pass*' | sort
```

For current system state and startup instructions, return to [`README.md`](README.md).
