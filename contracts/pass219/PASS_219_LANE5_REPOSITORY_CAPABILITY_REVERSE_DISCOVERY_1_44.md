# Pass 219 Lane 5 Repository Capability Reverse Discovery 1.44

## Purpose

1.44 extends the executable Lane 5 capability self-model without redefining the validated 1.43 source families. It adds a bounded third repository-visible capability source: Pass214 structural Python operation-registry keys.

The successor is discovery and evidence only. A discovered operation name is not execution proof and is not automatically a Hash216 composition edge, superedge, VM81 mutation authority, or canonical receipt authority.

## Inherited source contracts

- Pass147 public registry coverage = COMPLETE for the validated repository state.
- cumulative exact ABI export coverage = COMPLETE for the validated repository state.
- 1.44 MUST derive those two surfaces through the inherited 1.43 implementation and MUST preserve the same public/native source roots on the same repository tree.
- `hhs_exact_pass219_vm81_environment_admit_signed` remains the only canonical admission boundary.

## New source family

Source kind `3` is `PYTHON_OPERATION_REGISTRY`.

The source is exactly `extract_python_operation_registry_keys()` from `hhs_backend/runtime/hhs_pass214_python_operation_registry_v1.py`. That extractor is already constrained to tracked Python files outside test/evidence/benchmark fixture areas; static AST assignments only; strict operation/service/capability/dispatch-style registry names; literal dictionary keys or literal sequence members; credible bounded identifiers; and deterministic operation keys.

1.44 requires:

- Pass214 structural Python operation-registry coverage = COMPLETE for the validated repository state;
- `python_registry_parse_errors == []`;
- extraction policy `STRUCTURAL_KEYS_ONLY_STRICT_OPERATION_REGISTRY_NAMES`;
- manifest count equals the exact number of discovered source records;
- a non-empty source family.

A dynamic assignment such as `OPERATIONS = build_registry()` does not qualify as a discovered operation. Arbitrary functions, arbitrary string constants, and fuzzy Python `def` scanning are not capability evidence in this contract.

## Authority membrane

Every Python operation-registry record enters 1.44 with:

- authority class `OBSERVATION`;
- `execution_authority = DISCOVERY_ONLY_UNCLASSIFIED`;
- `hash216_composition_eligible = false`;
- `superedge_promotion_eligible = false`.

The native membrane MUST reject a source-kind-3 entry carrying any authority class other than `OBSERVATION`. A canonical admission boundary MUST be source kind `NATIVE_EXACT_ABI`, and the model MUST contain exactly one such boundary.

The following remain false for 1.44 itself:

- automatic Hash216 composition promotion;
- automatic superedge promotion;
- canonical VM81 mutation authority;
- canonical Hash72 authority;
- canonical Hash216 authority;
- canonical persistence authority;
- PQC key authority;
- receipt-clock authority;
- floating-point canonical authority.

Canonical state changes still require `hhs_exact_pass219_vm81_environment_admit_signed`.

## Deterministic identity

All source records are normalized into typed nodes with unique node IDs and nonzero unique 64-bit entry signatures. Native validation receives entries sorted by signature and rejects zero, duplicate, or non-increasing signatures.

1.44 seals five deterministic roots:

1. inherited Pass147 public-catalog Hash72 root;
2. inherited cumulative exact-ABI SHA-256 root;
3. structural Python operation-registry SHA-256 root;
4. typed dependency-topology SHA-256 root;
5. complete 1.44 model SHA-256 root.

The native receipt binds all three source counts, all five roots through their exact 64-bit bridge signatures, the singleton canonical boundary signature, and the ordered source/authority tuple sequence.

## Scope statement

`repository-total historical capability coverage = NOT YET CLAIMED`.

1.44 closes only the precise structural Python operation-registry family on top of the already validated Pass147 public and cumulative exact-ABI surfaces. Later reverse passes may add other validated callable families, including explicit C++/application/service registries and other repository-defined surfaces, but each source family requires its own deterministic parser, type classification, negative tests, and authority-preserving admission contract.
