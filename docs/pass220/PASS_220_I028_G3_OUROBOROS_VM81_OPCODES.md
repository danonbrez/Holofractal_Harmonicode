
# Pass 220 I028 — G³ / Ouroboros Native VM81 Opcode Family

Date: 2026-09-22

## 1. Scope

I028 promotes the G³ palindromic RNA / Ouroboros path into an explicit
append-only VM81 interpreter opcode family.

The legacy VM81 opcode ABI remains frozen:

~~~text
OP_NOP  = 0
...
OP_HALT = 23
~~~

I028 appends:

| Opcode | Value | Canonical stage |
|---|---:|---|
| OP_G3_IEEE_INGRESS | 24 | raw IEEE boundary ingress |
| OP_G3_PAL_FOLD | 25 | ordered palindromic route |
| OP_G3_RNA_TRANSCRIBE | 26 | exact typed RNA carrier |
| OP_G3_BIND_P4_C4 | 27 | bind already-typed P^4 and c^4 carriers |
| OP_G3_CONSTRAIN_C5 | 28 | Lo Shu value-5 constraint |
| OP_G3_CONSTRAIN_C7 | 29 | Lo Shu value-7 constraint |
| OP_G3_SERIALIZE_A2_C1 | 30 | Lo Shu value-1 / a² semantic BigInt register |
| OP_G3_ZERO_SUM_CLOSE | 31 | zero-centered Lo Shu line closure |
| OP_G3_RNA_REVERSE | 32 | reverse typed RNA carrier |
| OP_G3_IEEE_EGRESS | 33 | raw IEEE boundary egress |
| OP_G3_OUROBOROS | 34 | fused bounded coordinator |

Static assertions bind 23, 24, 34, and OP__COUNT=35 so accidental
renumbering fails at compile time.

## 2. Native register geometry

The native path is:

~~~text
IEEE raw bits
-> palindromic phase route
-> RNA typed carrier
-> P4=C4 carrier equality
-> C5
-> C7
-> C1/a2 semantic serialization register
-> zero-sum closure
-> reverse RNA typed carrier
-> IEEE raw bits
~~~

with the boundary identity:

~~~text
IEEE_out_bits == IEEE_in_bits
~~~

No C floating type or floating arithmetic is used by this path.

The native C interpreter accepts the raw 64-bit representation. An external
textual IEEE representation must first be converted to the exact raw-bit
boundary object by a separately validated ingress adapter; decimal floating
evaluation is not authority.

## 3. Palindromic route

I028 inherits the I015 ordered phase palindrome:

~~~text
x y z w x w z y x
~~~

and verifies it is its own reverse.

The raw IEEE bit carrier is not itself bit-reversed. The palindrome is the
ordered phase/RNA route applied around that boundary object.

## 4. RNA relationship

I028 does not replace the I019 full 5,184-character RNA scanner.

The C opcode establishes the native typed-carrier stage while the rooted
binding requires compatibility with the inherited I019 RNA/window membrane.

Authoritative complete BigInt exactness remains dependent on:

~~~text
I019_EXACT_5184_CHARACTER_SERIALIZER_WITNESS
~~~

## 5. P⁴ = c⁴ binding

OP_G3_BIND_P4_C4 receives already-typed exact P4 and c4 carriers and
requires direct equality.

It does not solve for P, derive P², select a square-root branch, or insert an
external scalar normalization.

Thus:

~~~text
P4 == c4
~~~

is a binding gate, not branch-selection arithmetic.

## 6. Lo Shu value addressing

The canonical Lo Shu matrix is:

~~~text
4 9 2
3 5 7
8 1 6
~~~

I028 searches by value rather than hard-coded accidental C index.

Zero-based coordinates are:

~~~text
C5 -> (1,1)
C7 -> (1,2)
C1 -> (2,1)
~~~

The C1 local row-major index is therefore 7.

That local index is **not** a physical character offset in the canonical
5,184-character serialization.

The physical serialization location remains owned by the canonical serializer.
I028 explicitly keeps:

~~~text
bigint_physical_5184_character_offset_resolved = false
~~~

## 7. Zero-sum closure

Subtracting the Lo Shu nucleus value 5 produces:

~~~text
-1  4 -3
-2  0  2
 3 -4  1
~~~

I028 verifies every row, every column, and both diagonals sum exactly to zero.

OP_G3_ZERO_SUM_CLOSE is admitted only after:

~~~text
P4=C4
-> C5
-> C7
-> C1/a2 semantic register
~~~

and after the exact carrier equality between the C1 register carrier and its
RNA source is preserved.

## 8. Fail-closed stage machine

The G³ state carries an exact ten-bit stage mask.

Each primitive checks its immediate predecessor.

Examples:

- C5 cannot fire before P4=C4;
- C7 cannot fire before C5;
- C1/a² cannot serialize before C7;
- zero-sum cannot close before the C1 register;
- reverse RNA cannot fire before zero-sum;
- IEEE egress cannot fire before reverse RNA.

A rejected G³ stage:

~~~text
sets W_G3_REJECT
sets W_LEDGER_FROZEN
does not project a new admitted state
does not compose a new authoritative receipt
does not advance vm->step
halts the rejected execution path
~~~

This realizes:

~~~text
failed constituent
=> no canonical successor
=> no authoritative receipt
=> no logical-time advance
~~~

## 9. Fused Ouroboros coordinator

OP_G3_OUROBOROS is a coordinator, not a shortcut.

It invokes all ten constituent stage functions in order.

Its acceptance surface is the native realization of:

~~~text
PAL_valid
and RNA_reversible
and P4=C4
and C5
and C7
and C1/a2_register
and zero_sum
and IEEE_out=IEEE_in
~~~

while the rooted invocation binding additionally requires the inherited I019
exact 5,184-character serializer witness before authoritative BigInt exactness
may be claimed.

The fused path snapshots the pre-existing G³ state and restores it on any
failed constituent.

## 10. Witness family

The previously unused upper twelve bits of the 32-bit VM witness word are
assigned to:

~~~text
W_G3_IEEE_INGRESS
W_G3_PAL_FOLD
W_G3_RNA_TRANSCRIBE
W_G3_BIND_P4_C4
W_G3_CONSTRAIN_C5
W_G3_CONSTRAIN_C7
W_G3_SERIALIZE_A2_C1
W_G3_ZERO_SUM_CLOSE
W_G3_RNA_REVERSE
W_G3_IEEE_EGRESS
W_G3_OUROBOROS
W_G3_REJECT
~~~

Every primitive is therefore independently receipt-addressable.

## 11. Pass-079-style rooted bindings

I028 adds a new Pass-220 registry:

~~~text
HHS_PASS_220_I028_G3_OPCODE_REGISTRY_V1
~~~

It does not rewrite the historical Pass 079 registry and does not change its
29 admitted direct ABI capabilities.

Each G³ opcode receives its own:

- semantic operation identity;
- numeric opcode;
- witness class;
- pre-state witness set;
- post-state witness set;
- failure semantics;
- authority scope;
- deterministic Hash72 binding root.

Every entry carries:

~~~text
compiler_may_synthesize = false
~~~

and resolution requires:

~~~text
exact binding root
+ exact authority scope
+ ACTIVE_VALIDATED lease
+ BOUND_WITNESSED VM81 lane
~~~

## 12. Existing Ouroboros native symbol

The historical static function:

~~~text
hhs_apply_ouroboros_closure(VM81 *vm)
~~~

is retained unchanged as an inherited frozen native symbol referenced by
Pass 078 artifacts.

The I028 G³ stage machine is additive and does not silently repurpose that
historical symbol.

## 13. Pass 214 repair-forward

Pass 214 previously asserted a literal Git-blob identity for the complete
standalone VM81 source file.

That assertion was stronger than the authority it actually owned and would
forbid every later authorized append-only VM81 extension.

I028 repairs the regression to freeze the semantic dependency instead:

~~~text
legacy opcode prefix 0..23 exactly unchanged
OP_HALT remains 23
Python governed adapter still has no direct apply_instruction/vm81_step bypass
~~~

This preserves Pass 214 behavior while permitting append-only ABI evolution.

## 14. Exact Wolfram receipt

The committed Wolfram proof returns:

~~~text
HHS_PASS_220_I028_G3_OUROBOROS_WOLFRAM_20260922_V1
PASS
12 / 12
~~~

It checks:

- append-only opcode range 24..34;
- ten primitives plus fused opcode;
- unique opcode values;
- C5/C7/C1 exact Lo Shu positions;
- every zero-centered Lo Shu row/column/diagonal closes to zero;
- direct P4=C4 carrier equality introduces no P2 symbol;
- every constituent is necessary to the fused Boolean acceptance;
- all constituents together accept.

The first draft of this Wolfram proof failed three coordinate checks because
the fixture accidentally applied First twice to Position. That helper was
corrected before evidence was committed; the authoritative receipt is 12/12.

## 15. Lane 5 / four-lane hydration relationship

For Pass 219/220 integration, the Lane 5 BIOS relationship is recorded as:

~~~text
OUROBOROS_MANIFOLD_ALGORITHM
~~~

The inherited four hydration lanes remain coordinated typed views of one
singleton VM81 admission architecture.

The G³ registry does not grant them independent canonical authority.

## 16. Multimodal Platonic color-wheel / holofractal sprite geometry

The requested multimodal graphics geometry is downstream of this exact machine
substrate.

I028 records:

~~~text
PLATONIC_COLOR_WHEEL_SPRITE_PROJECTION_DOWNSTREAM_ONLY
graphics_projection_authority = false
~~~

A subsequent pass may project the exact G³/VM81/Hash state into color-wheel,
sprite, vector, or other multimodal geometry, but those projections may not
feed approximate values back into the canonical VM81 transition.

## 17. Files

Implemented:

- hhs_runtime/HARMONICODE_VM_RUNTIME.c
- hhs_runtime/hhs_pass220_g3_ouroboros_opcode_registry_v1.py
- tests/pass220/test_hhs_pass220_g3_ouroboros_vm81_native_v1.c
- tests/pass220/test_hhs_pass220_g3_ouroboros_opcode_registry_v1.py
- evidence/pass220/i028_g3_ouroboros_wolfram_20260922_v1.wl
- evidence/pass220/i028_g3_ouroboros_wolfram_20260922_v1.output.json
- Pass 214 repair-forward regression/script
- dedicated I028 workflow
- restart checkpoint

## 18. Next boundary

Once I028 native compilation and regressions are green, the next useful
projection boundary is:

~~~text
exact G3/Ouroboros VM81 receipts
+ four-lane hydration coordinates
+ Hash216 state identity
-> unified Platonic/color-wheel/sprite projection receipt
~~~

with the graphics surface remaining reversible/read-only until separately
admitted.
