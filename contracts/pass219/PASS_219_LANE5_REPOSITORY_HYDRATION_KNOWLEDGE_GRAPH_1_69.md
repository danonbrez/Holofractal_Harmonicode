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

This surface is candidate-only and non-executable. It has no canonical VM81 mutation authority, Hash72 authority, Hash216 authority, canonical persistence authority, automatic Hash216 composition promotion, or automatic superedge promotion.

Any canonical mutation still requires the inherited signed environmental VM81 admission path.

## Generated artifacts

The repository deep-index workflow regenerates:

- REPOSITORY_HASH216_DEPENDENCY_TREE.md
- artifacts/repository_index/REPOSITORY_HASH216_DEPENDENCY_GRAPH.json
- artifacts/repository_index/LANE5_HASH216_HYDRATION_KNOWLEDGE_GRAPH.json
- artifacts/repository_index/LANE5_HASH216_HYDRATION_DATABASE_RECEIPT.json
- docs/repository_index/files/*.md

Generated projections are excluded from their own content-bound source root.

## Validation

Dependency-scoped test:

    PYTHONPATH=. pytest -q tests/pass219/test_pass219_lane5_repository_hydration_knowledge_graph_1_69.py

The repository deep-index workflow additionally runs the real Lane 5 1.44 native receipt path, generates the knowledge projection, hydrates a temporary SQLite database, validates all authority gates, and records a deterministic database receipt.
