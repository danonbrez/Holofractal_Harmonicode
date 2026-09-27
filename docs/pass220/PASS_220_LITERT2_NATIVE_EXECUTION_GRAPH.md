# Pass 220 LiteRT2 — Native Execution Graph over NumPy1

## Status

`IMPLEMENTED — RESTARTABLE DIFFERENTIAL CHECKPOINT`

Branch:

`pass220-litert2-native-execution-graph`

Base:

`main @ dcf571a197bb495fa018ee7fe4665f804456f218`

## Objective

Move LiteRT-compatible execution from model/tensor registration into an actual
native operator graph without creating another numerical implementation.

LiteRT2 separates graph authority from arithmetic authority:

```text
LiteRT model identity / tensor metadata
              ↓
C11 native operator graph
              ↓
topology + dtype + broadcast validation
              ↓
NumPy1 HARMONICODE numeric lowering
              ↓
exact symbolic / BigInt arithmetic
              ↓
NumPy-compatible dtype egress
```

## Native graph

Project:

`native_projects/hhs_pass220_litert_native_execution_graph`

C11 owns:

- tensor IDs;
- input/output/constant roles;
- admitted dtype identity;
- ranks/dimensions;
- ordered operation IDs;
- producer/consumer topology;
- availability of operands before each operation;
- output production;
- NumPy-compatible broadcast-shape validation;
- deterministic graph fingerprint.

The graph layer does not contain tensor values and cannot perform numerical
state mutation.

## First operator subset

Admitted:

- `int64`
- `float64`
- ADD
- SUBTRACT
- MULTIPLY
- NumPy trailing-dimension broadcasting
- constants
- intermediate tensors
- multi-operation ordered graphs

These are lowered to the merged NumPy1 engine.

## Float64

Float64 graph inputs enter NumPy1 as raw IEEE storage values.

NumPy1 preserves:

- exact dyadic recovery;
- exact pre-round symbolic result;
- integer-only nearest-even binary64 reconstruction;
- signed zero;
- per-scalar 5,184-character BigInt carrier.

LiteRT2 therefore does not perform host float arithmetic.

## Int64

Int64 uses NumPy1's exact pre-wrap arithmetic and NumPy-compatible signed
64-bit wrap at the observable dtype boundary.

## Witness

Every execution returns a graph witness containing:

- model Hash216 identity;
- graph Hash216 identity;
- native graph fingerprint;
- ordered operations;
- result dtype/shape;
- float64 IEEE bits where applicable;
- SHA-256 identities for each 5,184-character scalar BigInt carrier;
- Hash216 execution-witness identity.

No witness field is a VM81 commit or canonical Hash72/Hash216 persistence
authority.

## Metadata not yet execution

LiteRT1 intentionally accepts metadata for the wider LiteRT dtype surface,
including float32 and quantized tensors.

LiteRT2 does not silently promote those to float64 or int64.

Currently fail-closed for numerical execution:

- float16;
- float32;
- bfloat16;
- int8/uint8 quantized paths;
- int16/int32 quantized paths;
- unsigned integer execution.

Each dtype must acquire its own exact ingress, arithmetic, rounding/saturation,
and observable egress contract before admission.

## Differential validation

The focused gate compares LiteRT2 through NumPy1 against NumPy test-only
oracles for:

- float64 broadcast addition at raw IEEE-bit equality;
- multi-operation add → multiply ordering;
- signed-zero propagation inherited from NumPy1;
- int64 overflow behavior;
- deterministic graph replay;
- output BigInt witnesses;
- rejection of malformed broadcast declarations;
- rejection of unadmitted float32 execution.

Neither the LiteRT2 runtime nor NumPy1 runtime imports NumPy.

## Next: LiteRT3

LiteRT3 should add, in dependency order:

1. exact float32 ingress/rounding/egress;
2. quantized int8/int32 scale/zero-point semantics using exact rational
   parameters rather than float authority;
3. MATMUL over the exact tensor engine;
4. native tokenizer/token-buffer objects;
5. importer that lowers external LiteRT graph metadata into the native graph;
6. differential execution against the optional external LiteRT interpreter;
7. Mojo kernels only after exact operator equivalence is established.

Mojo remains an accelerator specialization of the same RNA-registered runtime
class and model/graph identities.
