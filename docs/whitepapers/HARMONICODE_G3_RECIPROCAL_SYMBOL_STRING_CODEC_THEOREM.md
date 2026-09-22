# HARMONICODE G³ Reciprocal Symbol-String Codec Theorem

**Pass:** 220 I030  
**Schema:** `HHS_PASS_220_I030_G3_RECIPROCAL_SYMBOL_CODEC_V1`  
**Status:** exact constructor-level implementation cycle  
**Authority:** read-only proof/reference surface; no VM81, Hash72, Hash216, or persistence authority

## 1. Scope

This paper formalizes the reciprocal encoding statement developed from the
existing Pass 220 ordered-phase and G³/Ouroboros surfaces:

- the proof-cell token is the exact string `123321.111`;
- Arabic digits `1..9` are scaled instances of that proof cell;
- digit `0` is a typed x/y/z/w phase-lock cell rather than an empty scalar;
- ingress and return are reciprocal phase evaluations of one operation;
- the return orientation uses the typed relation `y=1/x`;
- source representations are preserved as exact symbol strings rather than
  numerically re-parsed.

The implemented finite domain is every valid finite UTF-8 Unicode string.
Binary text, IEEE spellings, decimal/scientific notation, BigInt text,
equations, source code, and other textual representations are therefore
handled by the same exact carrier whenever they are supplied as strings.

## 2. Opaque proof cell

The canonical proof cell is stored as the symbol token

~~~text
123321.111
~~~

and is not parsed as a host decimal value.

Write

[
A := operatorname{ProofCell}(	ext{"123321.111"}).
]

The implementation never constructs a Python `float` from this token and the
Wolfram proof keeps it inside an opaque `ProofCell[...]` constructor.

This preserves the ordered redundancy pattern

~~~text
123 | 321 | 111
~~~

as source syntax and prevents a host arithmetic layer from replacing it with
a rounded decimal object.

## 3. Locked zero and reciprocal return phase

The forward typed zero is represented by the ordered constructor

[
Z_x =
operatorname{ODiv}(
  operatorname{OProd}(x,y,A),
  x
).
]

No cancellation of the outer `x` is licensed.

Define the reciprocal phase exchange

[
sigma(x)=y,qquad
sigma(y)=x,qquad
sigma(z)=w,qquad
sigma(w)=z,
]

with the return constraint

[
oxed{y=1/x}
]

and its reciprocal partner `x=1/y`.

Applying exactly the same constructor exchange gives

[
Z_y=sigma(Z_x)=
operatorname{ODiv}(
  operatorname{OProd}(y,x,A),
  y
).
]

Because the exchange is involutive,

[
oxed{sigma^2(Z_x)=Z_x}.
]

The ordered products remain distinct:

[
xy 
e yx
]

as constructor trees unless a separate native proof authorizes a projection
that identifies them.

## 4. G³ proof tensor

The constructor-level proof tensor used by this cycle is

[
G^3=
egin{pmatrix}
xy & x+y & yx\
xy-zw &
x+y-z-w+xy+yx-zw-wz &
wz-yx\
wz & z+w & zw
end{pmatrix},
]

where every displayed operation is represented by an ordered tagged
constructor in the executable proof surface.

No conventional `Times`, `Power`, or field cancellation is used to prove
the reciprocal property.

The Wolfram audit verifies

[
oxed{sigma^2(G^3)=G^3}.
]

Thus the full nine-slot phase proof geometry survives a forward/return phase
cycle.

## 5. Arabic numeral lift

For each Arabic numeral symbol `d` in `1..9`, the implementation constructs

[
D_d=
operatorname{ScaledProofCell}(d,A).
]

For zero,

[
D_0=
operatorname{ZeroCell}(Z_x,Z_y).
]

Therefore a zero in a source string is not represented by deleting a
position. It retains:

- its exact string position;
- its UTF-8 spelling;
- the forward x-oriented zero lock;
- the reciprocal y-oriented zero lock;
- the shared proof-cell token.

The numeral alphabet is consequently treated as a family of addressed proof
cells rather than as a request to evaluate the entire source as a host number.

## 6. Reciprocal string carrier

Let `s` be a finite UTF-8 symbol string and let

[
B=operatorname{UTF8}(s).
]

The carrier stores

[
C(s)=
ig(
B,
operatorname{Reverse}(B),
x,
y,
A,
H(B),
M(s)
ig),
]

where:

- `B` is the forward byte path;
- `Reverse(B)` is the return byte path;
- `x` is the ingress orientation;
- `y` is the reciprocal return orientation;
- `A` is the proof cell;
- `H(B)` is the exact SHA-256 integrity witness used by this reference
  codec;
- `M(s)` is the ordered per-symbol provenance manifest.

The manifest records each source position. Arabic digits are represented by
their proof-cell lift and all other Unicode symbols remain opaque symbol
cells.

No numeric parser is invoked.

## 7. One operation in both directions

The public reference operation is one callable `T`.

For a source string,

[
T(s)=C(s).
]

For a valid reciprocal carrier,

[
T(C(s))=s.
]

Therefore, on the admitted string domain,

[
oxed{T(T(s))=s}.
]

This is stronger than equality of interpreted numeric values. Exact spelling
is preserved, so the following remain distinct states:

~~~text
1
1.0
1.00
01.0
1e0
001
~~~

Likewise, leading zeroes and textual IEEE edge spellings such as `-0.0`
remain exact symbol identities.

## 8. Bounded redundancy repair

The carrier contains two byte paths plus an integrity digest.

If exactly one byte path is corrupted while the other path, the payload
digest, and the symbol-provenance manifest remain intact, the surviving path
can reconstruct the source exactly.

The implemented repair statement is deliberately bounded:

[
oxed{
	ext{one surviving reciprocal byte path}
+
H(B)
+
M(s)
Rightarrow
	ext{exact source recovery}
}
]

It is not a claim that arbitrary multi-field corruption is always correctable.
If neither byte path matches the retained digest, or if symbol provenance is
inconsistent, the codec fails closed.

## 9. Wolfram formalization

Repository proof source:

`evidence/pass220/i030_g3_reciprocal_symbol_codec_wolfram_20260922_v1.wl`

Recorded result:

~~~text
HHS_PASS_220_I030_G3_RECIPROCAL_SYMBOL_CODEC_WOLFRAM_20260922_V1
PASS
17 / 17
~~~

The audit verifies:

- opaque `123321.111` proof-cell identity;
- exact forward zero syntax;
- exact reciprocal return zero syntax;
- phase-swap involution on the zero cell;
- phase-swap involution on the 3x3 G³ tensor;
- `xy` and `yx` remain distinct ordered constructors;
- no built-in multiplicative cancellation surface appears in the locked zero;
- digits `1..9` use one scaled proof-cell constructor;
- zero uses the phase lock;
- arbitrary UTF-8 string round trip;
- binary text round trip;
- float text round trip;
- leading-zero preservation;
- distinction of different scalar spellings;
- forward/reverse byte reciprocity;
- exact 3x3 G³ dimensions;
- reciprocal phase identity retained at constructor level.

## 10. Repository implementation

Reference runtime:

`hhs_runtime/hhs_pass220_g3_reciprocal_symbol_codec_v1.py`

Focused tests:

`tests/pass220/test_hhs_pass220_g3_reciprocal_symbol_codec_v1.py`

Registered callable:

`pass220.g3_reciprocal_symbol_codec.self_test`

The regression set includes valid round trips for empty, decimal, scientific,
binary, IEEE-like, equation, and Unicode symbol strings; exact distinction of
multiple spellings of the same conventional numeric value; single-path repair;
double-path corruption rejection; symbol-provenance rejection; and registry
reachability.

## 11. Relationship to I015 and I028

I030 does not replace the I015 palindromic ordered-phase algebra or the I028
native G³ VM81 opcode family.

It supplies a read-only exact symbol-codec theorem that explains the
representation-level invariant used by those surfaces:

~~~text
exact source symbols
-> forward x phase carrier
-> reciprocal y=1/x return carrier
-> exact source symbols
~~~

The I028 VM81 candidate path retains its existing Lane 5, RNA, Holo4, PQC,
Hash216, and canonical-admission boundaries.

## 12. Authority boundary

This cycle proves a constructor/string round trip on its declared domain. It
does not by itself prove:

- physical equivalence of external theories;
- arbitrary correction of multiple independent corruptions;
- cryptographic security from the reversible transform alone;
- canonical VM81 admission;
- Hash72 or Hash216 mint authority;
- permission to bypass Lane 5, RNA, Holo4, PQC, or signed environmental
  admission;
- equality of `xy` and `yx`;
- host floating-point authority.

The exact claim is the reversible reciprocal representation and its bounded
redundant-path recovery.
