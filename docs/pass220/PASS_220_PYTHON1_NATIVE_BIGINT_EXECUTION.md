# Pass 220 Python1 — Native BigInt Execution Kernel

## Status

`IMPLEMENTED ON RESTARTABLE BRANCH — DIFFERENTIAL CI PENDING`

Branch:

`pass220-python1-native-bigint-execution`

Base at branch creation:

`main @ fa96d0dbbf3bc82ae5c156b62f86bb9409f6c68c`

## Purpose

Python1 begins replacement of the CPython execution interior while preserving
Python as an external source/API compatibility target.

It extends the existing Pass 190 Python compatibility lineage rather than
creating a competing Python registry.

The execution boundary is:

```text
Python source text
        ↓
native C11 tokenizer/parser
        ↓
native variable environment
        ↓
5,184-digit signed BigInt algebra
        ↓
native decimal result
        ↓
Python-compatible egress projection
```

CPython is not used to parse or execute the supported runtime source.

## Existing lineage preserved

Pass 190 already supplies:

- the Python 3.12 public-callable compatibility census;
- classifications for native, adapter-required, restricted, nondeterministic,
  and platform-dependent callables;
- the operation registry and HARMONICODE constructor mappings;
- governed calls such as `python.len`, `python.abs`, `python.sorted`,
  `dict.get`, `text.join`, and `math.gcd`.

Python1 does not rewrite or fork that registry.

The existing Pass 049 interpreter also establishes the fail-closed
`REJECT_INTERPRETER_HOST_EVAL` policy. Python1 strengthens the execution
slice by moving supported source parsing and integer evaluation into C11.

## Native C11 kernel

Project:

`native_projects/hhs_pass220_python_native_execution`

Properties:

- no Python C API;
- no dynamic allocation;
- source bound: 65,536 bytes;
- variable bound: 64 names;
- identifier bound: 64 bytes;
- signed integer magnitude bound: 5,184 decimal digits;
- decimal digit arrays are stored directly by the native kernel;
- grade-school exact addition/subtraction/multiplication;
- overflow beyond the declared 5,184-digit value bound fails closed.

The current parser implements Python-compatible precedence for:

- integer literals;
- variables;
- parentheses;
- unary `+` / `-`;
- multiplication;
- addition/subtraction;
- simple assignment;
- expression statements.

Multiple statements may be separated by newline or semicolon.

## Runtime membrane

`hhs_runtime.hhs_pass220_python_native_execution_v1`

uses `ctypes` only to cross the ABI.

It does not import `ast` and it does not invoke `eval`, `exec`, or
`compile`.

The C kernel returns a decimal BigInt string. Converting that final decimal
string to a Python `int` is explicitly an egress projection, not the
arithmetic implementation.

## CPython differential oracle

CPython 3.12 appears only in the test suite.

The tests execute the same supported programs through CPython and the native
kernel and require exact integer equality for:

- precedence;
- parentheses;
- unary operators;
- assignment and variable reads;
- positive and negative large integers;
- large BigInt products.

They also prove fail-closed rejection for:

- `__import__`;
- `open`;
- `eval`;
- exponentiation;
- division;
- float literals;
- imports;
- function definitions;
- list literals.

## Relationship to NumPy1

NumPy1 is already merged and is the mandatory bridge for Python float/array
semantics.

Python1 deliberately does **not** add a second float implementation.

The next Python checkpoint shall lower admitted Python float and array
operations into:

`HHS_PASS_220_NUMPY1_HARMONICODE_ARRAY_ENGINE_V1`

so Python-visible float64 behavior retains:

- exact IEEE ingress bits;
- exact dyadic state;
- symbolic pre-round arithmetic;
- deterministic nearest-even dtype rounding;
- palindromic/full-phase witness state;
- value-bound 5,184-character BigInt serialization.

## Relationship to FastAPI1

FastAPI1 is already merged. As Python compatibility expands, FastAPI's Python
source-level handlers can progressively lower into this execution layer while
the external ASGI membrane remains stable.

## Current non-claims

Python1 is not a complete Python implementation.

Not yet admitted:

- float or complex literals;
- lists, tuples, dicts, sets;
- calls and registered builtins;
- attributes/subscripts;
- comparisons and booleans;
- `if`, loops, functions, classes;
- exceptions;
- generators/async/context managers;
- imports/modules;
- Python object model/descriptors;
- garbage collection;
- bytecode compatibility.

Unsupported syntax fails closed rather than falling through to CPython.

## Next Python checkpoint

Python2 should add two explicit lowering paths:

1. numeric float/array nodes → NumPy1;
2. approved function calls → Pass 190 registered operations.

The source parser may expand only with differential behavior tests for each
added Python construct.

## Restart validation

```bash
make -C native_projects/hhs_pass220_python_native_execution clean all test
python -m pytest -q tests/pass220/test_hhs_pass220_python_native_execution_v1.py
```
