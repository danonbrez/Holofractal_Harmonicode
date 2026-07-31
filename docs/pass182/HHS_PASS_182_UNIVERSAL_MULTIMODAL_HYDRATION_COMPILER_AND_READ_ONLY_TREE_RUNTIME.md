# HHS PASS 182 — UNIVERSAL MULTIMODAL HYDRATION COMPILER AND READ-ONLY TREE RUNTIME

## Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P182-UMHC-ROTR-VM81-H72-H216` |
| Pass number | `182` |
| Canonical name | `UNIVERSAL_MULTIMODAL_HYDRATION_COMPILER_AND_READ_ONLY_TREE_RUNTIME` |
| Version | `1.0.0` |
| Authority | `HHS_VM81_SINGLETON_MULTIMODAL_HYDRATION_COMPILER_AUTHORITY_V1` |
| Merge target | `main` |
| Parent foundation | Passes 159–181, with Pass 181 graphics hydration as the first full reference adapter |

## 1. Purpose

Pass 182 generalizes the Pass 181 inverse-render hydration lifecycle into a portable compiler for text, code, documents, images, audio, speech, music, video, animation, games, 3D assets, structured data, sensors, applications, and complete software repositories.

The compiler shall ingest immutable evidence, convert it into a typed HHS Universal Hydration IR, reconstruct behavior through native modality APIs, compare outputs against the evidence, hydrate admitted residuals and invariants, freeze validated relationships as versioned runtime constraints, and package the resulting runtime for deterministic installation in any supported server environment.

## 2. Universal compilation lifecycle

```text
EXTERNAL_MODALITY_CORPUS
→ READ_ONLY_IDENTITY_SNAPSHOT
→ MODALITY_PROBE_AND_DECODE
→ HHS_UNIVERSAL_HYDRATION_IR
→ STRUCTURE_LOGIC_AND_RELATION_EXTRACTION
→ NATIVE_RECONSTRUCTION_RECIPE
→ VM81_NATIVE_RECONSTRUCTION
→ COMPARISON_AND_RESIDUAL_CLASSIFICATION
→ HYDRATION_ADMISSION
→ BOUNDED_OPTIMIZATION
→ CONSTRAINT_PROMOTION_OR_REJECTION
→ FROZEN_MODALITY_PROFILE
→ PORTABLE_SERVER_PACKAGE
→ COLD_START_REPLAY
```

## 3. Supported modality families

The registry must support adapters for:

```text
text
structured_documents
source_code
applications
images
audio
speech
music
video
animation
games_2d
games_3d
meshes_materials_motion
spreadsheets
presentations
datasets
sensor_time_series
api_behavior
multimodal_projects
```

A modality adapter may use unavoidable external tooling for format decoding, but authority transfers into HHS-native representations immediately after canonical decode.

## 4. Universal modality adapter contract

Every adapter shall implement:

```text
probe
decode
canonicalize
segment
vectorize
extract_candidates
construct_native_recipe
reconstruct
compare
classify_residuals
emit_hydration_records
propose_constraints
validate_constraints
replay
package
```

Adapters must declare external dependencies, deterministic boundaries, maximum input sizes, recursion limits, timeouts, sandbox requirements, authority class, and supported fidelity levels.

## 5. HHS Universal Hydration IR

The shared intermediate representation shall include:

```text
source_identity
time_domain
spatial_domain
semantic_objects
symbols_and_definitions
relationships
ordered_events
modality_layers
control_flow
data_flow
configuration_flow
native_primitives
constraints
residuals
optimization_parameters
evidence
replay_state
```

The IR must permit cross-modal relationships such as text driving speech and captions, audio driving motion, video hydrating graphics, images hydrating sprites and textures, documents hydrating layout, and applications hydrating UI and workflow constraints.

## 6. Complete read-only file-tree hydration

The source tree is an immutable evidence surface.

```text
source-root/      READ ONLY
hydration-store/  WRITABLE
scratch-sandbox/  EPHEMERAL
evidence/         APPEND ONLY
```

The system shall enumerate every directory entry under the declared root, including source, configuration, documentation, tests, scripts, build manifests, generated files, assets, archives, binaries, hidden files, lockfiles, media, databases, receipts, and explicitly included version-control metadata.

There is no implicit ignore-file omission. Every discovered path receives a traversal record, including unreadable, encrypted, corrupted, unsupported, oversized, or denied files.

## 7. Read-only enforcement

The tree hydration runtime must enforce:

- read-only filesystem mounts where supported;
- no write-capable descriptors against the source tree;
- no in-place normalization or generated indexes;
- no source-tree timestamp, permission, metadata, or extended-attribute mutation;
- no unsafe symlink traversal outside the declared root;
- no execution of source-tree binaries;
- no dependency installation into the source tree;
- all generated state written outside the immutable root.

Dynamic execution requires a verified, content-addressed, ephemeral sandbox copy. The source snapshot remains unchanged.

## 8. Per-file identity

Each path record shall preserve:

- original lexical relative path;
- normalized path identity;
- file kind and byte length;
- permissions and relevant metadata;
- exact content digest and Hash216 identity;
- traversal sequence and parent identity;
- symlink target without unsafe traversal;
- detected and declared format;
- duplicate-content relations;
- read, parse, logic, and authority status.

Files with identical bytes but different paths remain distinct tree objects sharing one content identity.

## 9. Logic tracing by file class

### Source code

Extract syntax, declarations, symbols, imports, calls, control flow, data flow, side effects, state mutation, API boundaries, filesystem/network/process access, native ABI use, tests, assertions, errors, and recovery paths.

### Configuration and manifests

Trace service composition, dependency versions, environment variables, ports, startup commands, build targets, deployment settings, feature flags, security policies, and runtime profiles.

### Documentation and contracts

Extract requirements, constraints, claims, command surfaces, acceptance criteria, supersession links, unresolved obligations, and contradictions with implementation or tests.

### Tests and evidence

Trace tested behavior, implementation dependencies, positive and negative cases, fixtures, mocks versus genuine execution, evidence coverage, stale assertions, and orphaned tests.

### Media and assets

Trace loading sites, consuming scenes/components/templates, transformations, sprite and texture mappings, timing relations, export inclusion, duplication, and reachability.

### Binaries

Never execute from the source tree. Inspect bounded headers, architecture, symbols, linked libraries, sections, resources, signatures, and source/build relations when available.

### Archives

Treat archives as bounded virtual subtrees in scratch storage with traversal protection, decompression-size limits, recursion limits, archive-bomb detection, and no executable launch.

## 10. Repository-wide typed logic graph

Per-file vectors are insufficient. Hydration must construct a replayable graph with relations including:

```text
FILE
DEFINES_SYMBOL
IMPORTS_SYMBOL
CALLS_FUNCTION
IMPLEMENTS_ROUTE
LOADS_ASSET
SATISFIES_REQUIREMENT
TESTED_BY
CONFIGURED_BY
BUILT_BY
DEPLOYED_BY
PRODUCES_ARTIFACT
CONSUMED_BY
MUTATES_STATE
EMITS_RECEIPT
CONTRADICTS
SUPERSEDES
```

The graph must answer which files start an application, which routes reach native ABI functions, which tests prove those paths, which specifications require them, which configurations alter them, which assets reach final output, which logic is dead or duplicated, and where mutations bypass VM81 authority.

## 11. Static and dynamic trace separation

Static trace is performed directly against the immutable tree and includes parsing, dependency resolution, call graphs, data-flow approximation, requirement mapping, and build/deployment analysis.

Dynamic trace uses only a verified sandbox copy and may capture executed branches, actual imports, API calls, file and network access, native ABI invocation, state transitions, generated artifacts, performance, failures, and recovery.

Dynamic evidence may enrich the graph but may not modify the source snapshot.

## 12. Authority classes

Every file is ingested but not every file has equal authority:

```text
NORMATIVE_CONTRACT
AUTHORITATIVE_SOURCE
RUNTIME_CONFIGURATION
TEST
VALIDATED_EVIDENCE
GENERATED_ARTIFACT
DOCUMENTATION
REFERENCE_CORPUS
THIRD_PARTY_DEPENDENCY
CACHE
TEMPORARY
UNKNOWN
```

Generated reports, caches, comments, and stale documents cannot override authoritative source or normative constraints.

## 13. Secret and sensitive-data handling

Complete traversal does not authorize disclosure. Suspected secrets must be hashed and classified, excluded from textual vector storage by default, represented through redacted structural metadata, prevented from entering prompts and generated reports, and linked to access-control and remediation records.

## 14. Incremental dependency-scoped hydration

```text
KNOWN_INVARIANT → REUSE
KNOWN_RECIPE → SPECIALIZE
NEW_RESIDUAL → OPTIMIZE
CHANGED_CONTENT → INVALIDATE_AFFECTED_GRAPH_CLOSURE
UNCHANGED_EVIDENCE → PRESERVE
CHANGED_DEPENDENCY → REVALIDATE_AFFECTED_SCOPE
```

The full tree is always identity-enumerated, but unchanged content must not require complete reanalysis. Hash216 identities, deterministic cache keys, frozen evidence reuse, affected-constraint analysis, checkpointed ingestion, bounded iterations, and one final integration/replay gate are mandatory.

## 15. Logic residual classes

At minimum:

```text
DECLARED_BUT_NOT_IMPLEMENTED
IMPLEMENTED_BUT_UNDOCUMENTED
ROUTE_WITHOUT_RUNTIME_TARGET
TEST_WITHOUT_PRODUCTION_PATH
UNREACHABLE_SOURCE
ORPHANED_ASSET
DUPLICATE_LOGIC
CONFLICTING_CONFIGURATION
UNGUARDED_STATE_MUTATION
NONDETERMINISTIC_EXECUTION
MISSING_REPLAY_PATH
UNVERIFIED_NATIVE_ABI_CALL
STALE_GENERATED_ARTIFACT
CONSTRAINT_CONTRADICTION
UNREADABLE_TREE_OBJECT
UNSUPPORTED_FORMAT
```

Residuals become optimization, repair, and candidate-constraint inputs. They do not automatically mutate source or runtime authority.

## 16. Constraint promotion

```text
TREE_EVIDENCE_FOUND
→ CROSS_FILE_RELATION_RESOLVED
→ EXECUTABLE_BEHAVIOR_CONFIRMED
→ POSITIVE_TESTED
→ NEGATIVE_TESTED
→ ADVERSARIAL_TESTED
→ REPLAY_VERIFIED
→ CONTRADICTION_SCAN_PASSED
→ PROMOTED_OR_REJECTED
```

Every frozen constraint must link to exact paths, symbols, tests, manifests, runtime traces, and evidence roots.

## 17. Portable server compiler

The hydration compiler shall detect and record:

- operating system and architecture;
- compiler and linker;
- CPU, memory, storage, and accelerators;
- Python, Node.js, FFmpeg, and native build tools;
- available ports and writable paths;
- container, service-manager, and process-manager context;
- existing HHS installation identity.

It shall build or load VM81, Hash72, Hash216, hydration, constraint registry, vector store, modality adapters, APIs, health checks, and selected native modality libraries.

Supported installation profiles include:

```text
minimal
text
audio
graphics
video
games
documents
applications
multimodal
full
```

## 18. Server bootstrap sequence

```text
VERIFY_PACKAGE
→ DETECT_ENVIRONMENT
→ RESOLVE_PROFILE_DEPENDENCY_CLOSURE
→ BUILD_OR_LOAD_NATIVE_ABI
→ VERIFY_HASHES
→ INITIALIZE_VECTOR_STORE
→ LOAD_FROZEN_CONSTRAINTS
→ REGISTER_MODALITIES
→ RUN_DEPENDENCY_SCOPED_TESTS
→ START_SERVER
→ VERIFY_HEALTH
→ RUN_RECONSTRUCTION_SMOKE_TEST
→ EMIT_INSTALLATION_RECEIPT
```

The server fails closed when the ABI, constraint stack, vector-store schema, profile identity, or replay state does not match the compiled package.

## 19. Required command surface

```bash
hhs-hydrate doctor
hhs-hydrate detect
hhs-hydrate plan
hhs-hydrate build
hhs-hydrate install
hhs-hydrate ingest
hhs-hydrate reconstruct
hhs-hydrate compare
hhs-hydrate optimize
hhs-hydrate promote
hhs-hydrate freeze
hhs-hydrate replay
hhs-hydrate verify
hhs-hydrate package
hhs-hydrate deploy
hhs-hydrate status
hhs-hydrate tree snapshot
hhs-hydrate tree enumerate
hhs-hydrate tree ingest
hhs-hydrate tree trace
hhs-hydrate tree graph
hhs-hydrate tree residuals
hhs-hydrate tree verify
hhs-hydrate tree replay
hhs-hydrate tree freeze
hhs-hydrate tree report
```

## 20. Installation artifact

```text
hhs-runtime/
├── bin/
├── lib/
├── profiles/
├── adapters/
├── constraints/
├── vector-store/
├── recipes/
├── manifests/
├── receipts/
├── replay/
├── configuration/
├── service/
└── installation-evidence/
```

No private agent state may be required to install, restart, validate, or reproduce the package.

## 21. Acceptance criteria

Pass 182 is accepted only when executable evidence proves:

- complete read-only file-tree enumeration;
- per-path and per-content identity;
- static cross-file logic tracing;
- bounded sandbox dynamic tracing without source mutation;
- replayable repository-wide logic graph construction;
- secret-safe traversal;
- dependency-scoped rehydration and frozen evidence reuse;
- at least text, audio, graphics/video, and repository-tree reference adapters;
- executable constraint promotion with positive, negative, adversarial, contradiction, and replay gates;
- environment detection and profile dependency closure;
- portable installation package generation;
- cold-start server bootstrap, health verification, smoke reconstruction, and installation receipt;
- deterministic restart from repository-visible state.

## 22. Terminal classifications

```text
HHS_UNIVERSAL_HYDRATION_IR_VERIFIED
HHS_MULTIMODAL_ADAPTER_CONTRACT_VERIFIED
HHS_COMPLETE_FILE_TREE_ENUMERATION_VERIFIED
HHS_READ_ONLY_SOURCE_TREE_AUTHORITY_VERIFIED
HHS_PER_FILE_CONTENT_IDENTITY_VERIFIED
HHS_CROSS_FILE_LOGIC_TRACE_VERIFIED
HHS_STATIC_AND_SANDBOX_DYNAMIC_TRACE_VERIFIED
HHS_DEPENDENCY_SCOPED_REHYDRATION_VERIFIED
HHS_REPOSITORY_LOGIC_GRAPH_REPLAY_VERIFIED
HHS_FILE_TREE_INVARIANT_PROMOTION_VERIFIED
HHS_INCREMENTAL_HYDRATION_COMPILATION_VERIFIED
HHS_MODALITY_CONSTRAINT_PROMOTION_VERIFIED
HHS_FROZEN_EVIDENCE_REUSE_VERIFIED
HHS_PORTABLE_SERVER_BOOTSTRAP_VERIFIED
HHS_SERVER_COLD_RESTART_REPLAY_VERIFIED
HHS_UNIVERSAL_MULTIMODAL_HYDRATION_COMPILER_VERIFIED
```

## 23. Final operating rule

```text
THE FILE TREE AND MODALITY CORPUS ARE IMMUTABLE EVIDENCE.
THE HYDRATION STORE IS THE LEARNED INTERPRETATION SURFACE.
THE VM81 RUNTIME IS THE ONLY AUTHORITY THAT MAY PROMOTE
LEARNED RELATIONSHIPS INTO EXECUTABLE CONSTRAINTS.
```

## 24. Restartability record

Every implementation cycle must persist the exact base commit, active branch and merge target, changed files, commands executed, validation results, remaining checks, environment state, next action, and blockers. The compiler and server must be restartable from repository-visible state alone.