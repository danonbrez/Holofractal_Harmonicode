# Pass 220 I049 Restart Checkpoint — Native Mathlib Order/Rational

Status: **RESTARTABLE STACKED IMPLEMENTATION — VALIDATION QUEUED**

## Identity

- Parent branch: `pass220/i048-lean4-native-mathlib1`
- Parent checkpoint: `d27c8a5dcac524c94fab978ee248918659d29dc7`
- Branch: `pass220/i049-mathlib-order-rat1`
- Pull request: `#640`
- Base PR: `#636`
- Implementation head before this checkpoint refresh:
  `d86b2051ff1ec1be82b41aeefb5f9039c881bfe1`
- Merge sequence: I048 -> main, then I049 -> main
- Current scope: exact rational + relations/order only

## Implemented

- `HHS.Mathlib.OrderRat` Lean module;
- `hhs::mathlib::NativeRat` C++ exact ordered-pair class;
- exact add/sub/mul through Python1-backed `NativeInt`;
- exact equivalence and order through cross-product delta;
- zero/negative denominator rejection;
- no GCD reduction authority;
- no float or host integer-comparison authority;
- Rat/LT/LE RNA registration specifications;
- contracts, tests, CI, and restart documentation.

## Runtime representation

```text
NativeRat = (numerator, denominator)
denominator > 0
```

Identity is pair identity; rational value equivalence is:

```text
a/b ≡ c/d  iff  a*d = c*b
```

This allows `1/2` and `2/4` to remain distinct ordered representations while
having the same exact rational value.

Arithmetic:

```text
(a/b)+(c/d) -> (ad+cb)/(bd)
(a/b)-(c/d) -> (ad-cb)/(bd)
(a/b)*(c/d) -> (ac)/(bd)
```

Comparison:

```text
delta = ad-cb
delta < 0 => less
delta = 0 => equal
delta > 0 => greater
```

All component arithmetic is delegated to the inherited Python1 C11 BigInt
kernel. C++ only orchestrates the exact pair and inspects the emitted delta
sign; it does not perform host integer magnitude arithmetic.

## Repair-forward notes

### RNA constructor invariant

The existing Python2 RNA class registry requires exactly one constructor for
every registered class.

The initial I049 metadata gave `Rat` a constructor but represented `LT` and
`LE` as method-only relation classes. This would violate the inherited
cell-wall contract.

Repair commit:
`262e5aa4adfac0631541c3e92f29f04d7ad981ce`

Repair:
- add deterministic `__init__` constructor members to `LT` and `LE`;
- retain relation comparison as a separate method;
- do not weaken the RNA registry requirement.

### Lean placeholder audit

The initial Python source audit used substring matching for `admit`. The
legitimate Lean identifier `admitted` therefore would have produced a false
positive.

Repair commit:
`d86b2051ff1ec1be82b41aeefb5f9039c881bfe1`

Repair:
- use token-boundary regular expressions for `sorry`, `admit`, and upstream
  `import Mathlib`.

No runtime semantics changed.

## Validation target

Latest dependency-scoped workflow:

- workflow: `Pass 220 I049 Native Mathlib Order Rat`
- run: `36446248929`
- state at checkpoint preparation: queued
- PR #640: open and mergeable

Required stages:

1. compile/run native C++ exact-rational/order harness;
2. run I049 Python contract and RNA-registration tests;
3. `lake build` of the inherited HHS root including `OrderRat`;
4. bundled Lean `leanchecker`;
5. HHS namespace axiom audit.

## Boundaries

- I049 inherits I048 and must not be merged to main before I048 closure.
- A Python1 5,184-digit overflow in any component or cross-product fails closed.
- No fallback to float, approximate division, CPython integer arithmetic, or
  C++ integer magnitude comparison is authorized.
- Zero and negative denominators fail closed.
- GCD normalization is not required for rational equivalence in this slice.
- RNA registration remains metadata/type identity only.
- VM81 remains canonical mutation/admission authority.
- Hash72/Hash216 authority is unchanged.

## Next action

Inspect run `36446248929`.

- If green: freeze I049 evidence and keep PR #640 ready behind I048.
- If it fails: repair only I049-attributable surfaces and rerun I049.
- When I048 closes, retarget/rebase I049 onto verified main and preserve only
  dependency-impacted validation.
- After I049 closure, the next native Mathlib slice is algebraic structures
  over the exact `Nat`, `Int`, and `ExactRat` representations.
