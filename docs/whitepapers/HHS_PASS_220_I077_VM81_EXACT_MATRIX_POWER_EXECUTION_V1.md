# HHS Pass 220 I077 — VM81 ExactMatrixPower Execution

## Scope

I077 begins from merged I076 main:

`631cb7a4a59a518475358f454604dbd36fa8d489`.

The pass turns the two source-bound `ExactMatrixPower` HIR nodes from I076 into
a native exact-ABI execution surface.

The two executed source nodes are:

```text
MatrixPower[M_wz,x^2]
MatrixPower[M_xy,x^4]
```

with preserved 4x2 topology.

I077 does **not** reinterpret either node as a conventional rectangular matrix
power. The execution unit is the exact symbolic HIR node itself.

## Native ABI

Public header:

```text
hhs_runtime/include/hhs_pass220_i077_vm81_exact_matrix_power_execution_1_0.h
```

Implementation:

```text
hhs_runtime/c/hhs_pass220_i077_vm81_exact_matrix_power_execution_1_0.inc
```

The additive aggregate exact ABI exports:

```text
hhs_exact_pass220_i077_version
hhs_exact_pass220_i077_descriptor
hhs_exact_pass220_i077_execute
```

The aggregate files are updated directly:

```text
hhs_runtime/include/hhs_runtime_exact_abi.h
hhs_runtime/c/hhs_runtime_exact_abi.c
```

A Python binding calls the same shared library:

```text
hhs_runtime/hhs_pass220_i077_vm81_exact_matrix_power_execution_v1.py
```

No Python recomputation becomes canonical authority.

## Source-bound execution nodes

### Node 0

```text
source           = MatrixPower[M_wz,x^2]
shape            = 4x2
exponent token   = x^2
cell tokens      = 0,1,1,2,2,0,3,1
```

### Node 1

```text
source           = MatrixPower[M_xy,x^4]
shape            = 4x2
exponent token   = x^4
cell tokens      = 4,3,3,5,5,4,3,1
```

The compact cell dictionary is:

```text
0 = -w*z
1 = z-w
2 = w*z
3 = y+x
4 = -x*y
5 = x*y
```

Thus the exact ordered source topology remains reconstructible while redundant
cell strings are not repeatedly materialized inside the native frame.

## Exact symbolic VM81 execution

For each node, the native implementation:

1. validates the canonical node id;
2. binds the exact source string and exponent token;
3. binds the ordered eight-cell token sequence;
4. creates SHA-256 source and ordered-topology witnesses;
5. creates a deterministic 81x64-bit candidate frame;
6. submits that frame through the existing exact VM81 UQCEL admission lane;
7. verifies the committed frame is byte-identical to the candidate;
8. repeats the admission as deterministic replay;
9. requires equal change, receipt, Hash216 triplet, and transition identities;
10. returns Hash72 and Hash216 execution evidence.

The output therefore includes:

```text
source_node_sha256
ordered_cells_sha256
change_hash72
receipt_hash72
replay_hash72
proof_hash216
transition_hash216
vm5184_address
vm81_steps
replay_vm81_steps
```

## UQCEL compatibility transport

The native HIR source/topology proof is established before transport.

The UQCEL compatibility packet is:

```text
P     = 2
p     = 1
q     = 3
Delta = 1
A     = 4
B     = 4
```

and satisfies exactly:

[
P^2=pq+Delta
]

and

[
AB=P^4.
]

Because (p=1) and (q=3),

```text
qr_bit         = 0
transport lane = X,Y
expected phase = 0
```

The UQCEL packet is transport/admission evidence only. It does not redefine the
source matrix-power node.

## What “executed” means in I077

I077 makes one deliberate distinction.

The following is now true:

```text
exact symbolic HIR node executed through VM81 = true
VM81 admission verified                       = true
Hash72 execution receipt verified             = true
Hash216 transition identity verified          = true
deterministic replay verified                 = true
```

The following remains false:

```text
host MatrixPower used                  = false
square-matrix requirement imported     = false
numeric exponent evaluated             = false
conventional matrix-power value derived= false
floating-point authority               = false
canonical state persisted              = false
```

Thus I077 closes the execution-surface gap identified by I076 without inventing
ordinary linear-algebra semantics for the native 4x2 operator.

## Wolfram formalization

Source:

```text
formal/wolfram/pass220_i077_vm81_exact_matrix_power_execution_v1.wl
```

Connected Wolfram kernel:

```text
status = PASS
checks = 30 / 30
failed = {}
nodes = 2
shapes = 4x2, 4x2
transport P,p,q,Delta = 2,1,3,1
transport A,B = 4,4
Hash216 width = 216
full attached components = 15552
```

No Wolfram `MatrixPower` invocation is used on the native rectangular nodes.

## Lean 4

Native module:

```text
HHS.Pass220.I077
```

Source:

```text
formal/lean/HHS/Pass220/VM81ExactMatrixPowerExecution.lean
```

The theorem surface proves:

- exact transport (P^2=pq+Delta);
- exact (AB=P^4) transport closure;
- exactly two execution nodes;
- exact 4x2 shapes;
- exact source nodes;
- exact exponent tokens;
- exact cell topology;
- symbolic execution / VM81 admission / replay flags;
- no host MatrixPower or premature value semantics;
- `72*72=5184`;
- `3*5184=15552`;
- I076 node-count and hydration inheritance;
- fail-closed authority boundaries.

## Native probe and negative test

The direct C probe is:

```text
tools/pass220/pass220_i077_vm81_exact_matrix_power_probe.c
```

It invokes the deployed shared exact ABI for both canonical nodes and also
requires an invalid node id to reject with the native range/reason code.

The Python dependency test additionally verifies:

- both nodes produce 72-character change/receipt/replay witnesses;
- replay receipt equals the original receipt;
- both produce 216-character proof/transition identities;
- source hashes and transition identities remain distinct;
- no host/persistence/floating authority is introduced.

## Authority boundary

I077 is an exact symbolic execution surface, but it does not become a parallel
canonical persistence authority.

The following remain false:

- canonical VM81 mutation authority;
- canonical Hash72 commit authority;
- canonical Hash216 commit authority;
- canonical Hash216 persistence authority;
- floating-point authority;
- host MatrixPower authority;
- square-matrix fallback authority;
- external-egress authority.

A later pass may define additional native value semantics for the rectangular
tensor-power operator, but such semantics must be source-bound and separately
proved. I077 does not infer them.
