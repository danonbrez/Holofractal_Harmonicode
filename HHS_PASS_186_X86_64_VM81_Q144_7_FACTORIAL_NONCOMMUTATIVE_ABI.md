# HHS PASS 186 — x86_64 VM81 Q144 7! NONCOMMUTATIVE ABI

## Normative metadata

| Field | Value |
|---|---|
| Contract identifier | `HHS-P186-X64-VM81-Q144-F7-G243-NCABI` |
| Pass number | `186` |
| Canonical name | `X86_64_VM81_Q144_FACTORIAL7_NONCOMMUTATIVE_5184_243_ABI` |
| Baseline | authoritative `main` including Pass 175 VM5184 × G243 projection |
| Integer policy | exact C11 integers only; no floating-point canonical authority |
| Host target | Linux System V AMD64 / x86_64 |

## Purpose

Pass 186 establishes a direct x86_64 ABI crosswalk between the ordered Harmonicode basis `(x, y, z, w, xy, yx, zw, wz)`, VM81's `81 × 64 = 5,184` native instruction identity, the `12 × 12 = 144` root-phase quantization nucleus, the prime-7 factorial boundary `7! = 5,040`, and the existing Pass 175 `5,184 × 243 = 1,259,712` hydrated address space.

The ABI MUST preserve operand order. Equal integer multiplication witnesses do not authorize collapsing `xy` into `yx` or `zw` into `wz`.

## Exact invariant system

```text
12 × 12               = 144
35 × 144              = 5,040 = 7!
36 × 144              = 5,184
81 × 64               = 5,184
5,184 × 243           = 1,259,712
1,259,712 + 1         = 1,259,713
5,184 - 7!            = 144
```

The first 35 Q144 lanes are factorial-admitted. Lane 35 is the complete Q144 closure lane:

```text
[0, 5,039]     factorial-admitted
[5,040, 5,183] closure Q144 tensor
```

## Canonical address equations

For `g ∈ [0,242]`, `o ∈ [0,35]`, and `i,j ∈ [0,11]`, define:

```text
q144  = i × 12 + j
s5184 = o × 144 + q144
P     = s5184 × 243 + g
```

This preserves the existing Pass 175 state-major projection exactly.

The inverse is:

```text
g     = P mod 243
s5184 = P div 243
o     = s5184 div 144
q144  = s5184 mod 144
i     = q144 div 12
j     = q144 mod 12
```

The VM81 crosswalk is:

```text
cell81      = s5184 div 64
operation64 = s5184 mod 64
class8      = operation64 div 8
basis8      = operation64 mod 8
```

This is a bijection; it does not invent a second instruction numbering system.

## Ordered basis registry

| basis8 | identity | ordered tag |
|---:|---|---:|
| 0 | `x` | `0x0058` |
| 1 | `y` | `0x0059` |
| 2 | `z` | `0x005A` |
| 3 | `w` | `0x0057` |
| 4 | `xy` | `0x5859` |
| 5 | `yx` | `0x5958` |
| 6 | `zw` | `0x5A57` |
| 7 | `wz` | `0x575A` |

The ordered tag is authoritative for noncommutative identity. The optional integer product is only a magnitude witness.

## x86_64 register mapping

The public System V AMD64 C entrypoint receives:

| Register | Meaning |
|---|---|
| `RDI` | `x` |
| `RSI` | `y` |
| `RDX` | `z` |
| `RCX` | `w` |
| `R8` | quantization descriptor pointer |
| `R9` | mapping result pointer |

The assembly register probe then maps the ordered scalar lanes to:

| Canonical register | Meaning |
|---|---|
| `R8` | `x` |
| `R9` | `y` |
| `R10` | `z` |
| `R11` | `w` |

The checked probe bytes are:

```text
4c 89 c0
48 89 38
48 89 70 08
48 89 50 10
48 89 48 18
49 89 f8
49 89 f1
49 89 d2
49 89 cb
4c 89 40 20
4c 89 48 28
4c 89 50 30
4c 89 58 38
c3
```

## u^72/Q144 dual view

Every Q144 index has both an exact root coordinate and a paired ring coordinate:

```text
root coordinate = (i,j) ∈ Z12 × Z12
u72 pair         = q144 div 72 ∈ {0,1}
u72 index        = q144 mod 72 ∈ [0,71]
```

Neither view may erase the other.

## Required callable surfaces

```c
hhs186_x64_vm81_q144_map(...)
hhs186_x64_vm81_q144_unproject(...)
hhs186_x64_capture_xyzw_registers(...)
```

The ABI returns the Q144 coordinate, factorial/closure classification, VM81 cell and operation, ordered basis and tag, G243 control, projected address, and all cardinality witnesses.

## Safety and determinism

1. All bounds are checked before address construction.
2. Ordered multiplication uses checked signed 64-bit arithmetic.
3. Invalid requests do not mutate caller state.
4. No `float`, `double`, x87, SSE scalar-float, or AVX float opcode is required.
5. The outer modulus `1,259,713` is reported as a separate envelope and is not substituted for the internal cardinality `1,259,712`.
6. Opcode semantics remain registry-bound. This pass deterministically exposes every slot; it does not silently redefine inherited opcode behavior.

## Acceptance criteria

Pass 186 is accepted when:

- all `1,259,712` internal addresses round-trip exactly;
- address zero and address `1,259,711` decode correctly;
- `5,039` is factorial-admitted and `5,040` begins the closure Q144 lane;
- `xy` and `yx` remain distinct identities, as do `zw` and `wz`;
- the assembly probe proves the declared register transfers;
- strict C11 compilation succeeds with warnings treated as errors;
- disassembly contains no floating-point arithmetic instruction.
