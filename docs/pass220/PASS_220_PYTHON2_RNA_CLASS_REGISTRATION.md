# Pass 220 Python2 — RNA Cell-Wall Class Registration

## Status

`IMPLEMENTED — RESTARTABLE VALIDATION CHECKPOINT`

Branch:

`pass220-python2-rna-class-registration`

## Objective

Bind the native Python interpreter's class/module object model to the existing
Pass 219 C++ RNA transcription cell wall rather than creating a Python-only
class authority.

The registration path is:

```text
Python / future Mojo class descriptor
        ↓
stable class + source identities
        ↓
Pass 220 exact C ABI
        ↓
Pass 219 RNA Domain / Strand / Program records
        ↓
hhs::rna::PythonClassRegistration
        ↓
registration witness only
```

Registration itself performs no state transition.

Instance mutations later follow:

```text
registered class identity
  → hydrated predecessor
  → RNA transcription witness
  → Pass 219 1.12 admission candidate
  → stable exact C ABI
  → singleton C VM81 authority
  → Hash72 receipt
  → Hash216 successor hydration
```

## Native class record

The exact ABI stores:

- module ID;
- class ID;
- one constructor member ID;
- up to seven ordered constructor/field/method members;
- source SHA-256;
- 216-character class identity;
- deterministic registration fingerprint;
- generated RNA strand;
- generated nonexecuting RNA registration program.

The RNA strand contains one class-anchor domain plus one domain per member,
therefore respecting the inherited eight-domain 1.11 limit.

## Why the registration program has zero rules

Class registration describes type topology; it is not a runtime RNA state
transition.

Executing activation/binding/etc. merely to register metadata would falsely
claim RNA state semantics that have not occurred. Therefore the registration
program is intentionally a valid empty Pass 219 RNA program.

Runtime instance behavior may create real RNA rules/witnesses only when the
object actually undergoes a typed operation.

## C++ cellular membrane

The native class is:

`hhs::rna::PythonClassRegistration`

It exposes the generated strand/program and permanently reports:

- no VM81 mutation authority;
- no Hash72 commit authority;
- no Hash216 persistence authority;
- no floating-point canonical authority;
- instance transitions require RNA admission.

## Python/Mojo shared identity

The Python bridge does not use live CPython object inspection. It accepts a
deterministic class descriptor, which is the same representation that the
native Python parser and later Mojo frontend can emit.

Therefore Python and Mojo do not receive separate class registries. Both bind
to the same:

```text
module/class/member identities
+ source identity
+ Hash216 class identity
+ RNA cell-wall registration
```

## Validation

The focused workflow:

1. compiles the complete exact C ABI aggregate;
2. runs C registration/replay/negative tests;
3. runs C++17 cell-wall wrapper tests;
4. builds the shared exact ABI;
5. runs Python registration parity and deterministic replay tests.

## Next Python step

Extend the native Python parser so admitted `class` syntax lowers directly
into this descriptor. Method bodies then continue through the native Python
execution/Pass 190/NumPy boundaries already established.

## LiteRT-LM handoff

After this registration checkpoint, LiteRT-LM integration should use the same
native class and operation membrane. Model/runtime objects should register as
typed classes rather than becoming a separate Python package authority.

The first LiteRT-LM pass should identify the existing Pass 153/LiteRT surfaces,
separate external model/runtime compatibility from canonical HHS execution,
and replace the internal LiteRT-LM dependency incrementally behind this class
registry.
