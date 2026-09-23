# HARMONICODE G³ Exact IEEE Scalar Involution Theorem

**Pass:** 220 I031  
**Schema:** `HHS_PASS_220_I031_G3_IEEE_SCALAR_INVOLUTION_V1`  
**Status:** exact implementation/proof cycle  
**Authority:** read-only proof/reference surface; no VM81, Hash72, Hash216, or persistence authority

## 1. Statement

I031 strengthens the preceding reciprocal symbol-string theorem to the scalar
storage state itself.

For an admitted IEEE binary scalar with complete storage word (B), define the
typed state

[
S_x(B)=(B,x)
]

and reciprocal phase operation

[
sigma(B,x)=(B,y),qquad y=1/x.
]

The scalar coordinate does not change:

[
oxed{pi_B(sigma(B,x))=B}.
]

Applying the same reciprocal phase operation a second time gives

[
oxed{sigma^2(B,x)=(B,x)}.
]

Therefore the exact scalar-storage invariant is

[
oxed{B_{mathrm{out}}=B_{mathrm{in}}}.
]

This is a stronger statement than decimal rendering equality. It covers the
complete IEEE storage identity, including signed zero, subnormals, infinities,
and NaN payload bits.

## 2. Bit partition theorem

Let an IEEE binary format have:

- one sign bit;
- (e) exponent bits;
- (f) fraction bits.

Then the total width is

[
w=1+e+f.
]

For every integer storage word

[
0le N<2^w,
]

define

[
L=Nmod 2^{e+f},
]

[
s=leftlfloorrac{N}{2^{e+f}}ightfloor,
]

[
E=leftlfloorrac{L}{2^f}ightfloor,
]

and

[
F=Lmod 2^f.
]

The reconstruction is

[
oxed{
N=s,2^{e+f}+E,2^f+F.
}
]

This is exact Euclidean decomposition; no floating arithmetic participates.

The connected Wolfram proof returns `True` parametrically for the standard
binary interchange widths:

[
(e,f)in
{(5,10),(8,23),(11,52),(15,112)},
]

corresponding to binary16, binary32, binary64, and binary128.

The binary16 surface is additionally exhausted over all

[
2^{16}=65,536
]

storage states.

## 3. Exact finite dyadic projection

For a finite nonzero IEEE state, the stored value is exactly dyadic.

For normal states,

[
V=(-1)^s(2^f+F),2^{E-mathrm{bias}-f}.
]

For subnormal states,

[
V=(-1)^sF,2^{1-mathrm{bias}-f}.
]

The runtime reduces that expression to an exact integer numerator and
denominator using integer arithmetic only.

As a concrete binary64 witness, the machine scalar commonly printed as
`0.1` has storage word

~~~text
3FB999999999999A
~~~

and exact dyadic value

[
oxed{
rac{3602879701896397}{36028797018963968}.
}
]

Its exact difference from mathematical (1/10) is

[
oxed{
rac{1}{180143985094819840}.
}
]

This distinction matters: the IEEE scalar is already an exact finite bit
object. HARMONICODE is not required to claim it was originally the exact real
number (1/10). The theorem is that the admitted IEEE scalar itself returns
bit-for-bit unchanged.

## 4. Signed zero

The two binary64 storage states

~~~text
+0 = 0000000000000000
-0 = 8000000000000000
~~~

have the same ordinary rational projection (0/1) but remain distinct scalar
states because their sign fields differ.

Therefore

[
oxed{B_{+0}
e B_{-0}}
]

even though

[
pi_{mathbb Q}(B_{+0})
=
pi_{mathbb Q}(B_{-0})
=
0.
]

I031 preserves the complete storage word, so reciprocal transport cannot merge
the two zero encodings.

## 5. Infinity and NaN payloads

Infinity and NaN are not coerced into finite rationals.

Their exact authority for this theorem is their storage word:

[
oxed{
B_{mathrm{return}}=B_{mathrm{source}}.
}
]

Thus a NaN payload such as

~~~text
7FF8000000000042
~~~

returns with the same payload bits.

The codec does not depend on host NaN equality semantics, because bit identity
is checked directly.

## 6. Reciprocal phase separation

The inherited phase relation remains

[
oxed{y=1/x}.
]

The typed transform is

[
T(B,x)=(B,y).
]

Only the phase coordinate changes:

[
xleftrightarrow y,
]

while

[
Bightarrow B.
]

Therefore

[
oxed{
T^2(B,x)=(B,x)
}
]

and

[
oxed{
operatorname{Scalar}(T(B,x))
=
operatorname{Scalar}(B,x).
}
]

This is the formal statement behind the architecture's phase immutability:
the reciprocal phase provides routing and return geometry but does not absorb,
stretch, round, or rescale the IEEE scalar.

## 7. Relationship to the G³ proof cell

The scalar state remains bound to the inherited proof token

~~~text
123321.111
~~~

and the phase locks

[
Z_x=
operatorname{ODiv}(
operatorname{OProd}(x,y,A),x
),
]

[
Z_y=
operatorname{ODiv}(
operatorname{OProd}(y,x,A),y
).
]

No cancellation of the ordered phase constructors is introduced.

The proof cell and reciprocal phase state therefore provide the return-path
structure while the IEEE storage word remains an invariant scalar coordinate.

## 8. One operation, exact return

The public reference transform has one callable surface.

Ingress:

[
T(B)=C(B,x,y).
]

Return:

[
T(C(B,x,y))=B.
]

Hence

[
oxed{T(T(B))=B}.
]

For a host binary64 value that already exists, the test boundary may obtain its
storage bytes, pass those bytes through I031, and reconstruct the same host
binary64 storage pattern. The HHS transform itself performs no host
floating-point arithmetic.

## 9. Exhaustive and parametric evidence

The Python regression exhausts every binary16 word and reports the exact class
counts:

| Class | Count |
|---|---:|
| signed zero | 2 |
| subnormal | 2,046 |
| normal | 61,440 |
| infinity | 2 |
| NaN | 2,046 |
| **total** | **65,536** |

All 65,536 field reconstructions and reciprocal round trips are exact.

For binary32, binary64, and binary128, repository tests cover mandatory edge
states plus deterministic wide bit-pattern populations. Their universal field
rebuild identity is separately proved symbolically in Wolfram from Euclidean
bit partitioning, so correctness is not inferred from sampling alone.

## 10. Wolfram proof

Repository source:

`evidence/pass220/i031_g3_ieee_scalar_involution_wolfram_20260922_v1.wl`

Result:

~~~text
HHS_PASS_220_I031_G3_IEEE_SCALAR_INVOLUTION_WOLFRAM_20260922_V1
PASS
17 / 17
~~~

The proof checks:

- parametric field reconstruction for binary16;
- parametric field reconstruction for binary32;
- parametric field reconstruction for binary64;
- parametric field reconstruction for binary128;
- all 65,536 binary16 storage states;
- scalar-bit invariance under phase exchange;
- reciprocal phase involution;
- return phase equals (y);
- signed-zero storage distinction;
- common zero rational projection;
- NaN payload field reconstruction;
- positive and negative infinity reconstruction;
- exact binary64 `0.1` storage reconstruction;
- exact dyadic difference from mathematical (1/10);
- opaque `123321.111` proof cell;
- no scalar inflation under reciprocal phase exchange.

## 11. Runtime implementation

Implementation:

`hhs_runtime/hhs_pass220_g3_ieee_scalar_involution_v1.py`

Focused tests:

`tests/pass220/test_hhs_pass220_g3_ieee_scalar_involution_v1.py`

Registered service:

`pass220.g3_ieee_scalar_involution.self_test`

The runtime uses integer bit extraction and integer rational reduction only.
No `float()`, decimal round-trip, NaN comparison, or host floating arithmetic
is part of the codec.

## 12. Relationship to I028 and I030

I028 already carries a raw 64-bit IEEE boundary word through the native G³
Ouroboros candidate path and requires

~~~text
ieee_out_bits == ieee_in_bits
~~~

before candidate closure.

I030 proved exact reciprocal symbol-string preservation.

I031 now supplies the explicit mathematical and executable scalar theorem that
connects those surfaces:

~~~text
raw IEEE scalar bits
-> exact field partition / dyadic witness
-> x-oriented G³ carrier
-> y=1/x reciprocal return
-> identical raw IEEE scalar bits
~~~

No decimal textual proxy is required.

## 13. Claim boundary

I031 establishes bit-exact reversible transport for the admitted IEEE binary
storage formats. It does not claim:

- that an IEEE scalar equals an intended external real number exactly;
- that every physical model is validated by the transport theorem;
- canonical VM81 mutation authority;
- Hash72 or Hash216 mint authority;
- floating-point arithmetic authority;
- a bypass around Lane 5, RNA, Holo4, PQC, or signed environmental admission.

The exact claim is:

[
oxed{
orall Binmathrm{IEEEBinary}_{w},
quad
T(T(B))=B
}
]

for the implemented standard binary widths, with the universal field
reconstruction established by exact integer decomposition.
