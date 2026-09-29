# Pass 219 Lane 5 Repository Hydration Knowledge Graph 1.69

Status: IMPLEMENTED TARGET / CANDIDATE-ONLY / RESTARTABLE / HASH216-INDEXED

## Purpose

Promote the repository index from a navigation-only projection into a first-class Lane 5 hydration knowledge map of system-wide capabilities and constructors.

The implementation binds the existing repository Hash216 file/dependency census, Lane 5 1.44 repository capability reverse discovery, and Pass 191 three-Hash72 Hash216 identity. It does not create a parallel source census.

## First-class objects

CAPABILITY nodes are lifted from Lane 5 1.44 and bind the original capability identity, source kind, authority class, semantic/export/operation name, declaring repository path, entry signature, semantic tokens, and a domain-separated 216-character Hash216 identity.

CONSTRUCTOR nodes are deterministic observations of Python classes and factory functions, C/C++ factory or initializer symbols, JavaScript/TypeScript classes and factories, and formal repository artifacts whose path explicitly declares constructor.

Discovery does not convert a symbol into execution authority.

The module also declares `LANE5_REPOSITORY_KNOWLEDGE_OPERATIONS` as a literal operation registry. Pass 214's structural registry scanner therefore feeds the map's `status`, `search`, and `neighbors` surfaces back into Lane 5 1.44 reverse discovery. On each subsequent deep scan, the knowledge system is consequently represented inside its own capability map without granting execution or mutation authority.

## Relations

DECLARED_IN_FILE binds a capability or constructor to the already Hash216-bound repository file identity.

SEMANTICALLY_ALIGNED_WITH_CAPABILITY requires the same source file and non-empty normalized name-token overlap. It is a discovery relation, not an equivalence proof or execution edge.

The existing repository dependency edges remain in the source dependency graph and are hydrated into the database rather than duplicated into the knowledge projection.

## Hash216 roots

The projection seals:

- capability_root_hash216
- constructor_root_hash216
- knowledge_node_root_hash216
- knowledge_edge_root_hash216
- projection_root_hash216

The final root binds the source repository graph root and Lane 5 model root.

## Hash216 database

Lane5RepositoryHydrationKnowledgeDatabase uses SQLite with WAL, synchronous FULL, and foreign keys.

Tables:

- repository_files
- file_dependencies
- knowledge_nodes
- knowledge_edges
- hash216_positions
- hydration_metadata

Every capability, constructor, and knowledge edge is expanded to all 216 positional records. Each position records ordinal, one of the three 72-character lanes, lane offset, symbol, and SHA-256(symbol).

The database is reconstructable from repository-visible generated artifacts and provides bounded search, neighbors, and status surfaces.

## Authority membrane

This knowledge projection is candidate-only and has no direct execution authority. That property belongs to the projection itself; it MUST NOT be reinterpreted as proof that a represented capability is non-executable. Capability visibility, executability, validation, admission, and mutation authority are separate states. A represented capability remains visible when its executability or closure state is unresolved.

The projection has no canonical VM81 mutation authority, Hash72 authority, Hash216 authority, canonical persistence authority, automatic Hash216 composition promotion, or automatic superedge promotion.

Any canonical mutation still requires the inherited signed environmental VM81 admission path.

## Generated artifacts

The repository deep-index workflow regenerates:

- REPOSITORY_HASH216_DEPENDENCY_TREE.md
- artifacts/repository_index/REPOSITORY_HASH216_DEPENDENCY_GRAPH.json
- artifacts/repository_index/LANE5_HASH216_HYDRATION_KNOWLEDGE_GRAPH.json
- artifacts/repository_index/LANE5_GLOBAL_REPOSITORY_VISIBILITY.json
- artifacts/repository_index/LANE5_HASH216_HYDRATION_DATABASE_RECEIPT.json
- docs/repository_index/files/*.md

Generated projections are excluded from their own content-bound source root.

## Validation

Dependency-scoped test:

    PYTHONPATH=. pytest -q tests/pass219/test_pass219_lane5_repository_hydration_knowledge_graph_1_69.py

The repository deep-index workflow additionally runs the real Lane 5 1.44 native receipt path, generates the knowledge projection, hydrates a temporary SQLite database, validates all authority gates, and records a deterministic database receipt.


## Pass 219 global visibility successor 1.70

The 1.70 successor implements the already-governing Pass 219 global visibility rule without creating another composition authority.

Discovery occurs before classification. The hydrated visibility manifold contains:

- every content-bound file surface from the bound main repository graph;
- every capability surface inherited from Lane 5 reverse discovery;
- static changed-file surfaces from discovered branch and pull-request Git refs.

Flags or words such as `demo`, `example`, `reference`, `candidate_only`, `enabled=false`, unresolved closure, or unvalidated branch state are metadata and MUST NOT remove a discovered surface from Lane 5 visibility.

The state separation is:

```text
VISIBLE != EXECUTABLE != VALIDATED != ADMITTED != MUTABLE
```

Unknown executability, closure, configuration, or adapter state remains `UNRESOLVED`. A `NON_EXECUTABLE`, `configuration REQUIRED`, or `adapter REQUIRED` classification requires explicit evidence; it cannot be inferred from the Pass 219 security membrane or from inability to bypass the kernel.

Branch and pull-request source is inspected through Git object metadata and diffs only. It is never imported or executed during discovery. Complete-scan bounds fail the projection instead of silently truncating capability visibility.

The resulting visibility records are Hash216-identified and hydrated into the same positional SQLite vector store as the 1.69 capability/constructor graph. This adds searchable provenance and unresolved-state information without granting canonical mutation, Hash72/Hash216 minting, persistence, PQC, or receipt-clock authority.

Dependency-scoped validation additionally runs:

    PYTHONPATH=. pytest -q tests/pass219/test_pass219_lane5_global_repository_visibility_1_70.py
