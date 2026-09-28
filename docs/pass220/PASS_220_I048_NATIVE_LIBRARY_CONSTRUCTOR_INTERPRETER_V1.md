# Pass 220 I048 — Native Library Constructor Binding + HARMONICODE Interpreter v1

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / CANDIDATE-ONLY

## Purpose

I048 consumes the already-integrated I047 native-library training records. It
does not recrawl libraries or duplicate Lane 5 optimization. It turns I047
metadata into deterministic constructor-binding candidates and provides a
fail-closed HARMONICODE interpreter surface.

The pipeline is:

    I047 raw library + metadata + source-observed vectors
    -> I048 constructor binding
    -> HHS compiler IR artifact (execution_authorized=false)
    -> exact reference-vector interpreter replay when evidence exists
    -> otherwise explicit native-constructor/runtime-adapter requirement
    -> downstream Lane 5 / VM81 admission remains authoritative

## Constructor binding

Each binding preserves:

- source record identity and source library SHA-256;
- architecture and ABI;
- exact symbol and entrypoint identity;
- ordered input/output data types and encodings;
- ingress encoder and egress decoder IDs;
- side-effect and state-boundary classification;
- operator/constructor/phase/timing/VM81/RNA relationship metadata;
- read-only HHS IR projection.

The binding may not remove the external codec membrane or authorize execution.

## Interpreter semantics

For PURE and READ_ONLY entrypoints, a call whose typed input payloads exactly
match an I047 source-observed reference vector may replay that exact observed
output. The interpreter does not recompute the source operation.

For an unseen input:

    status = NATIVE_CONSTRUCTOR_EXECUTION_REQUIRED
    outputs = []

No guessed result is emitted.

For STATEFUL_BOUNDED, IO_BOUNDED, or OPAQUE_FOREIGN entrypoints, even an exact
reference-vector input returns:

    status = EXPLICIT_RUNTIME_ADMISSION_REQUIRED
    outputs = []

This prevents reference replay from erasing source side effects or state.

## Equivalence boundary

I048 can prove exact replay over the observed I047 reference corpus. It does not
claim generalized constructor equivalence from finite examples.

Generalized equivalence remains:

    native constructor execution
    + exact external input/output contract
    + observed behavior comparison
    + inherited VM81 / Hash72 / Hash216 admission

## Developer-library import

The CLI consumes I047 records.jsonl and writes a deterministic I048 constructor
registry:

    python -m scripts.pass220_i048_native_library_constructor_interpreter_v1 \
      --records <i047-dataset>/records.jsonl \
      --output <constructor-registry.json>

This implements the Pass 220 developer-library import nucleus without granting
the imported library canonical authority.

## Authority

I048 does not:

- execute foreign bytecode;
- mutate VM81;
- mint canonical Hash72;
- persist canonical Hash216;
- create a second scheduler or optimizer;
- remove ingress/egress compatibility encoders;
- infer outputs for unseen inputs.

The next successor may bind validated Lane 5 native constructors to the runtime
adapter for unseen-input execution while preserving this interpreter contract.
