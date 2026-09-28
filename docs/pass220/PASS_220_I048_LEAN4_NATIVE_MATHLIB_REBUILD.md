# Pass 220 I048 — Lean 4 Native Integration and Mathlib1 Rebuild Nucleus

## Status

**IMPLEMENTED ON RESTARTABLE BRANCH — DEPENDENCY-SCOPED CI PENDING**

Branch: `pass220/i048-lean4-native-mathlib1`

Base commit: `091ab8c527dcb30e8f240e6fd525ee11249fc6b4`

## Objective

Make Lean 4 a first-class HARMONICODE proof subsystem while rebuilding the
Mathlib compatibility surface progressively on HHS-native execution classes.

This checkpoint deliberately does not claim that all upstream Mathlib has
already been reimplemented.

## Authority split

```text
HARMONICODE / Lean-facing theorem surface
                |
                +--> Lean 4 kernel: proof-term verification
                |
                +--> HHS.Mathlib.Native compatibility classes
                         |
                         +--> Python1 C11 exact BigInt execution
                         |
                         +--> C++ class wrappers
                         |
                         +--> Python2 / Pass 219 RNA class identity
                                      |
                                      +--> candidate metadata only
                                                   |
                                                   v
                                         VM81 admission authority
```

Lean proves declared obligations. Lean does not mutate VM81.

Native Mathlib class registration supplies stable type/class identity. It
does not commit Hash72 or persist Hash216.

Python1 remains the exact bounded integer execution authority for the initial
`Nat` and `Int` slice. Host `eval`, `exec`, and CPython arithmetic do not
become canonical runtime authorities.

## Initial native Mathlib slice

I048 creates three compatibility anchors:

| Upstream compatibility name | Native HHS class |
| --- | --- |
| `Mathlib.Data.Nat.Basic` | `HHS.Mathlib.Data.Nat.Basic.Nat` |
| `Mathlib.Data.Int.Basic` | `HHS.Mathlib.Data.Int.Basic.Int` |
| `Mathlib.Logic.Basic` | `HHS.Mathlib.Logic.Basic.Eq` |

The `Nat` and `Int` C++ classes route addition/subtraction/multiplication
through the existing Python1 C11 5,184-digit BigInt kernel. They do not
silently substitute C++ built-in integer arithmetic.

The class/type layer reuses
`hhs::rna::PythonClassRegistration`, preserving deterministic source identity,
Hash216 class identity, member ordering, and the Pass 219 RNA cell-wall
boundary.

## Lean package

Root `lean-toolchain` and `lakefile.lean` now establish a real local Lean 4
package. The initial native module is:

`formal/lean/HHS/Mathlib/Native.lean`

It imports `Std`, not upstream Mathlib. This is intentional: upstream Mathlib
is a differential/API reference while native HHS implementations are built in
verified slices.

The module has no `sorry` or `admit` placeholders.

## Expansion rule

A new upstream Mathlib namespace is admitted into the native compatibility
surface only after all of the following hold:

1. its external theorem/type/API contract is identified;
2. the HHS Python1/C++ representation preserves required input/output types;
3. observable supported results are differentially equivalent;
4. Lean checks the formal obligations for the native slice;
5. class/proof/dependency identities are receipt-bound;
6. VM81 remains the only state-transition admission authority.

This prevents "native Mathlib" from becoming a name-only fork.

## Validation

Dependency-scoped commands:

```bash
make -C native_projects/hhs_pass220_mathlib_native clean test
python -m pytest -q tests/pass220/test_hhs_pass220_i048_native_mathlib_v1.py
lake build
```

CI additionally runs Lean kernel checking and an axiom audit for the `HHS`
namespace.

## Next slices

The next bounded rebuild stages should add, in dependency order:

`Nat/Int relations -> exact rational constructors -> algebraic structures ->
ordered structures -> finite combinatorics -> polynomial/ring structures ->
number theory`.

Upstream Mathlib remains available as a compatibility oracle during that
migration, but it is not the canonical HHS runtime implementation.
