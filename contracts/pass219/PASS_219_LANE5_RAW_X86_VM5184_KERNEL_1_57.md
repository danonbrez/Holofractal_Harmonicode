# Pass 219 Lane 5 1.57 — Direct Raw x86_64 VM5184 Virtual Hardware Kernel

Status: IMPLEMENTED / exact-head validation pending  
Parent: Lane 5 1.56

## Purpose

Make the already-existing raw x86_64 exact ABI membrane the direct ingress/egress surface of the Lane 5 VM5184 dynamic circuit.

No model-format translator, floating-point converter, or secondary serialization layer is introduced.

## Kernel quantum

```text
648 raw bytes
= 5,184 raw bits
= 81 VM81 cells * 64 local constructor addresses
= one VM5184 virtual-hardware frame
```

The direct step is:

```text
raw x86_64 ABI bytes
-> hhs_x86_64_bytecode_copy_exact
-> hhs_exact_vm81_frame_import_le
-> global raw5184 hydration validation
-> hhs_exact_pass219_global_raw5184_dynamic_circuit
-> hhs_exact_vm81_frame_export_le
-> identical raw bytes
```

The byte stream is treated as virtual-hardware state. It is not dispatched as host CPU instructions.

## ABI

```c
hhs_exact_pass219_lane5_raw_x86_vm5184_step(...)
hhs_exact_pass219_lane5_raw_x86_vm5184_stream(...)
```

`step` executes exactly one 648-byte VM5184 frame.

`stream` composes exact complete 648-byte frames while carrying the same dynamic-circuit state across the sequence. It rejects incomplete tails rather than padding or inventing bytes.

## Invariants

```text
direct_raw_x86_ingress = true
direct_vm81_kernel_execution = true
exact_raw_egress = true
format_translation_layer = false
floating_point_authority = false
host_instruction_execution_authority = false
canonical_vm81_mutation_authority = false
```

For admitted frames:

```text
egress( kernel( ingress(raw) ) ).bytes == raw
```

The dynamic circuit may update its candidate-only internal learning state according to the inherited Pass 219 circuit contract, but does not mutate the raw input frame or gain canonical-state authority.

## Native acceptance

1. shared exact ABI builds with warnings enabled;
2. new symbols are exported;
3. descriptor reports `648 / 5184 / 81 / 64`;
4. raw patterned frame executes and returns byte-identically;
5. every VM5184 address `0..5183` encode/decode round-trips;
6. two concatenated 648-byte frames execute sequentially and return byte-identically;
7. incomplete stream tails fail closed;
8. inherited 1.55/1.56 native surfaces remain green.
