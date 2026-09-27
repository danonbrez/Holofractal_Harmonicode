# Pass 220 I047 — Native Library Bytecode Relationship Training Dataset v1

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / CANDIDATE-ONLY  
Base: main @ 31d89bfaec1521ae35fc4dc248be4c2dd84a67f4

## Purpose

I047 prepares training data for the existing Lane 5 compilation/hydration path from complete conventional software libraries. It does not create a second optimizer, scheduler, algebra authority, Hash authority, or mutation path.

The dataset binds:

    complete raw library byte image
    + architecture / ABI / provenance / byte-region metadata
    + entrypoint typed input-output contracts
    + operator / dependency / phase / timing relationships
    + VM81 / RNA / Hash-lineage relationship hints
    + outputs observed by invoking the source library
    -> deterministic candidate training record
    -> Lane 5 constructor-recognition / training input

Lane 5 remains responsible for HARMONICODE algebraic lifting, constructor reuse, latency/phase scheduling, and elimination of repetitive linear recomputation.

## Exact source and reference behavior

The complete source library bytes are immutable evidence and are materialized as:

    raw/<source-sha256>.bin

Byte regions are views over that image and may not escape its bounds. A source-byte change changes the training identity.

Reference vectors are admitted only when:

    reference_origin = SOURCE_LIBRARY_OBSERVED_OUTPUT
    source_library_invoked = true
    observed_output = true

Each input/output value preserves data_type, encoding, byte_length, payload_base64, and payload_sha256. The source library is therefore the behavioral oracle for the training example rather than duplicated host arithmetic.

The compatibility target is:

    L_source : X -> Y
    L_native : X -> Y

where the external input contract, expected output data types, and declared observable result are preserved.

## Metadata relationships

Every source library declares library_id, format, architecture, ABI, provenance, codec_boundary, byte_regions, entrypoints, and relationships.

Entrypoints preserve symbol identity, ordered input/output types and encodings, side-effect/state boundaries, math/operator identities, constructor dependencies, ordered phase relationships, timing constraints, VM81 relationships, and RNA relationships.

Generic relationship edges preserve relation_id, relation_type, source, target, order, and attributes.

## Stable ingress / egress membrane

Every record requires ingress_encoder_id, egress_decoder_id, and preserve_external_contract=true.

Lane 5 may optimize native representation, constructors, phase timing, scheduling, hydration, and execution while the external membrane remains:

    external input
    -> ingress encoder
    -> native HARMONICODE modality/runtime
    -> egress decoder
    -> external output

## Lane 5 handoff

Every record requests:

    algebraic_lifting_requested = true
    latency_phase_scheduling_requested = true
    reuse_validated_constructor_relations_requested = true
    repetitive_linear_recomputation_requested = false

I047 simultaneously proves:

    algebraic_lifting_performed_here = false
    latency_phase_scheduling_performed_here = false
    alternate_scheduler_created = false
    alternate_optimizer_created = false

## Materialization

CLI:

    python scripts/pass220_i047_native_library_training_dataset_v1.py \
      --spec <input-spec.json> \
      --output <dataset-directory>

Input schema: HHS_PASS_220_I047_NATIVE_LIBRARY_DATASET_INPUT_V1.

Output:

    manifest.json
    records.jsonl
    raw/<sha256>.bin

Dataset SHA-256 identities are noncanonical corpus identities. They do not mint canonical Hash72 or commit canonical Hash216 state.

## Authority boundary

I047 remains candidate-only:

    vm81_mutation_invoked = false
    canonical_hash72_minted = false
    canonical_hash216_committed = false
    canonical_persistence_invoked = false
    model_weight_mutation_invoked = false

Any resulting native constructor or knowledge-graph mutation must later pass through the inherited Lane 5 / VM81 / Hash72 / Hash216 authority path.

## Validation

The dependency-scoped test compiles a real x86_64 ELF shared library, invokes it through ctypes, captures its observed outputs, and verifies exact raw-byte preservation, deterministic content addressing, output type/encoding fidelity, mandatory codec metadata, bounded byte regions, changed-byte identity changes, and candidate-only authority.

Local preflight result: 7 passed.
