# Pass 079 — Native ABI Closure and Executable IR Opcode Registry

## Purpose

Pass 079 binds `HHS_EXECUTABLE_IR_V1` native requests to admitted native capability contracts. It does not infer authority from names, signatures, callability, or output resemblance.

## Canonical chain

`IR request → rooted opcode binding → authority validation → lease validation → VM81 lane validation → bounded invocation eligibility`

Pass 079 resolves eligibility only. Native execution admission remains reserved for Pass 080's constraint membrane.

## Results

- Existing direct ABI capabilities registered: **29 / 29**
- Pass 078.1 typed-unresolved declarations excluded: **15 / 15**
- Name-only bindings: **0**
- Signature-only bindings: **0**
- Unproven semantic bindings: **0**
- Compiler-created native operations: **0**

Each `HHS_NATIVE_OPCODE_BINDING_V1` records semantic operation identity, exact ABI symbol, ABI disposition, input/output schemas, ownership, bounds, mutation class, authority scope, lease requirements, pre/post witnesses, failure semantics, receipt schema, and a deterministic binding root.

## Authority boundary

The compiler may request only a registered native opcode and must carry its exact binding root. Resolution does not itself execute the function. A valid request remains subordinate to authority, lease, VM81 binding, and the forthcoming native transition membrane.
