# Pass 219 Lane 5 1.56 — RNA Self-Ingestion Bytecode Experiment

Experiment: `HHS-X5184-001`  
Parent invariant: `HHS-T5184-004` / Lane 5 1.55  
Status: EXECUTED EXACT READ-ONLY EXPERIMENT

## 1. Question

What happens when the RNA transcription layer ingests its own ordered
`x,y,z,w` multiplicative strings as binary bytecode numbers?

The experiment keeps two representations separate so that a successful typed
self-ingestion cannot be confused with an information-losing bare-number
projection.

## 2. Typed native path

The canonical local word already has an exact T64 identity:

```text
{x,y,z,w}^3
 -> kappa
 -> operation64 in 0..63
 -> one exact byte
 -> operation64
 -> inverse kappa
 -> same ordered RNA word
```

The 1.55 invariant proves the `operation64` mapping is bijective.

Result:

```text
64 inputs
64 output identities
64 fixed points
0 provenance collisions
```

This path preserves the full ordered constructor identity.

## 3. External multiplicative spelling path

For comparison only, the experiment also serializes the external textual
spelling as bytes:

```text
xyz
x*y*z
```

and interprets those byte strings as unsigned big-endian integers.

The deliberately noncanonical projection is:

```text
operation64 = BigInt(ASCII bytes) mod 64
```

Identifier:

```text
EXPERIMENTAL_NONCANONICAL_ASCII_BIGINT_MOD64
```

This projection has no canonical HARMONICODE authority.

## 4. Exact collapse law

For bytes `b0 ... bn` interpreted in base 256:

```text
N = b0*256^n + ... + b(n-1)*256 + bn
```

Because:

```text
256 = 4*64
256 mod 64 = 0
```

it follows exactly that:

```text
N mod 64 = bn mod 64.
```

Therefore the bare-number projection discards every byte except the final one.

For the final RNA symbol:

```text
'w' = 119 -> 55 mod64 -> wyw
'x' = 120 -> 56 mod64 -> wzx
'y' = 121 -> 57 mod64 -> wzy
'z' = 122 -> 58 mod64 -> wzz
```

The compact spelling `xyz` and explicit multiplicative spelling `x*y*z`
have the same projected operation because both end in the same final symbol.

## 5. Finite-state result

Exhaustive execution of all 64 ordered RNA words produces:

```text
typed native image: 64 states
typed native fixed points: 64

untyped ASCII-BigInt/mod64 image: 4 states
untyped fixed points:
  wyw
  wzx
  wzy
  wzz
```

Every input reaches one of those four fixed points in at most one transition.

The four basins are exactly equal:

```text
wyw: 16 inputs
wzx: 16 inputs
wzy: 16 inputs
wzz: 16 inputs
```

All cycles have length 1.

## 6. T004 closure after projection

Every one of the 64 projected outputs remains a valid T64 constructor state and
therefore still passes the green `HHS-T5184-004` resolver to the terminal:

```text
(-1,-1)
```

However, the untyped projection retains only four unique operation64/provenance
addresses.

Thus terminal closure survives while ordered source identity does not.

## 7. Native byte membrane

CI builds the exact native ABI and passes, for every T64 word:

```text
compact ASCII bytes
explicit multiplicative ASCII bytes
typed one-byte operation64
```

through `hhs_x86_64_bytecode_copy_exact`.

The output bytes must equal the input bytes exactly.

This validates byte transport only. The experiment does **not** execute the
self-ingested bytes as CPU instructions.

## 8. Wolfram evidence

Connected Wolfram Language execution independently returned:

```text
status = PASS
checks = 18/18
typed image = 64
external image = 4
fixed points = {wyw,wzx,wzy,wzz}
basins = {16,16,16,16}
projected operations = {55,56,57,58}
```

Sealed evidence:

```text
source sha256 = 9f691bd9d0c636a698a241ed37321e20189965caff8bf486e9f95d0563118c6f
output sha256 = fb9ee9dad7af534b3e125a15eda994ebcd09b8bbb912274855b87c11a0452699
```

## 9. Architectural consequence

The experiment distinguishes two very different notions of “self-ingestion”:

```text
typed byte identity
  => exact 64-state self-description

untyped byte spelling interpreted as bare BigInt mod64
  => deterministic 64-to-4 provenance collapse
```

Therefore byte ingress itself is lossless, but type erasure before the local64
projection is not.

The result supports retaining the RNA/T64 type boundary when self-hosting
ordered constructor strings.

## 10. Authority

This pass is read-only.

Still false:

```text
external_ascii_projection_canonical_authority
byte_execution_authority
canonical_vm81_mutation_authority
canonical_hash72_authority
canonical_hash216_authority
canonical_persistence_authority
```

The noncanonical projection is an observed experiment result and is not promoted
to a HARMONICODE rewrite law.
