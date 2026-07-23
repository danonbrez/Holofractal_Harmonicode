# HHS_PORTABLE_BYTECODE_V1

## Authority boundary

`HHS_PORTABLE_BYTECODE_V1` is a deterministic representation target for admitted `HHS_EXECUTABLE_IR_V1` semantics. It is not an alternate semantic authority.

```text
INTERPRETER → reference semantic judgment
COMPILER    → verified representation projection
BYTECODE VM → target execution path
```

An artifact is admissible only when its target execution produces the exact canonical semantic projection established by the interpreter reference path.

## Encoding

The artifact is:

```text
ASCII magic: HHSBC1\n
canonical UTF-8 JSON document
```

The JSON document contains the registered target-contract root, source identity, target-IR root, executable-IR root, exact numeric model, declared effect model, and ordered instructions.

## Numeric model

- integers: exact;
- rationals: exact normalized numerator/denominator pairs;
- floats: forbidden in the canonical target;
- foreign floating-point conversion: allowed only through `HHS_FOREIGN_NUMERIC_BOUNDARY_V1` and remains an explicitly typed projection.

## Supported operations

- `GATE_DECLARE`
- `GATE_INVOKE`
- `RELATION_EQUAL`
- `ORDERED_DISTINCT`
- `EXPRESSION_EVAL`

No filesystem, network, random, wall-clock, syscall, undeclared foreign call, or float operation is admitted.

## Admission

```text
candidate bytes
+ byte-integrity digest
+ interpreter reference execution
+ target execution
+ exact semantic projection equality
+ lineage closure
+ independent package verification
= admitted artifact registry entry
```

Execution roots are expected to differ. Canonical semantic projection roots must match exactly.
