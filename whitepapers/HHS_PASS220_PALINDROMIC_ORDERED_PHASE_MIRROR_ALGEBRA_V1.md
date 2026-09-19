# HHS Pass 220 I015 — Palindromic Ordered-Phase Mirror Algebra

**Schema:** `HHS_PASS_220_PALINDROMIC_ORDERED_PHASE_V1`  
**Status:** exact implementation cycle  
**Inherited base:** Pass 220 I014 merged main `adf663b3d35c62d74d65d937a0fbda8281b276ac`  
**Authority:** read-only exact witness/projection; no VM81, Hash72, or Hash216 mutation authority

## 1. New ordered-phase surface

The supplied four-dimensional carrier pair is

[
x=(0,1,1,0),qquad y=(0,-1,1,0).
]

Exact evaluation gives

[
xcdot y=0,qquad
|x|^2=|y|^2=2.
]

The reflection

[
M=operatorname{diag}(1,-1,1,1)
]

satisfies

[
M^2=I,qquad Mx=y,qquad My=x.
]

Thus the supplied (x,y) carriers are an exact equal-norm orthogonal mirror
pair in the stated four-coordinate representation.

The ordered multiplication relations are

[
xw=xy,qquad
wx=wz,qquad
yz=yx,qquad
zy=zw.
]

These relations identify alternate outgoing edge representatives without
identifying the underlying carrier symbols.

---

## 2. Two mirrored traversals

Define the forward traversal

[
xightarrow yightarrow zightarrow wightarrow x
]

and the reversed traversal

[
xightarrow wightarrow zightarrow yightarrow x.
]

Their ordered edge lists are

[
E_+=
(xy, yz, zw, wx)
]

and

[
E_-=
(xw, wz, zy, yx).
]

The second is obtained by reversing both the order and endpoint orientation of
the first.

Joining the two traversals at the common center gives the nine-symbol word

[
oxed{
Pi_x=xyzwxwzyx
}
]

with

[
oxed{
operatorname{Rev}(Pi_x)=Pi_x.
}
]

This is a literal ordered-word palindrome; no commutation is needed.

Its 3x3 projection is

[
oxed{
P_x=
egin{pmatrix}
x&y&z\
w&x&w\
z&y&x
end{pmatrix}
}
]

and

[
operatorname{Rot}_{180}(P_x)=P_x.
]

The nine-symbol word therefore gives a direct ordered-phase realization of the
nine local slots attached to the four wrapped (x,y,z,w) directional
families.

---

## 3. Four edge classes and two views

The supplied equations define four ordered edge classes:

[
egin{aligned}
[xy]&={xy,xw},\
[yx]&={yx,yz},\
[zw]&={zw,zy},\
[wz]&={wz,wx}.
end{aligned}
]

A canonical representative view is

[
(xy, yx, zw, wz),
]

while its alternate mirrored representative view is

[
(xw, yz, zy, wx).
]

These are componentwise equal by the supplied relations.

The path views preserve their noncommutative ordering:

[
E_+mapsto([xy],[yx],[zw],[wz])
]

while

[
E_-mapsto([xy],[wz],[zw],[yx]).
]

Therefore the edge-class *set* is shared, but the two traversal sequences are
not silently identified before a projection that proves their equality.

That preserves the directional information carried by the palindrome.

---

## 4. q=-1 scalar projection

The inherited scalar projection

[
xy=zw=+1,qquad
yx=wz=-1
]

extends through the new edge equalities to

[
xw=zy=+1,qquad
yz=wx=-1.
]

Both traversal views then project to exactly

[
oxed{
(+1,-1,+1,-1)
}
]

and both projected products are

[
oxed{+1}.
]

Thus the two ordered traversals remain distinct typed words while sharing an
exact scalar closure projection.

---

## 5. Residual tensor is representative-invariant

The previously supplied residual surface is

[
R_0:R_1:R_2
=
(x-1)(y-1):
(zw-xy)(wz-yx):
(xy-x)(yx-y).
]

Using the mirrored representatives gives

[
R_1'=(zy-xw)(wx-yz)
]

and

[
R_2'=(xw-x)(yz-y).
]

Applying only

[
xw=xy,quad
wx=wz,quad
yz=yx,quad
zy=zw
]

returns

[
oxed{R_1'=R_1}
]

and

[
oxed{R_2'=R_2}.
]

Therefore the residual tensor is invariant under switching between the two
local representative views.

---

## 6. Braid closure and the typed reciprocal

The lower ordered relations also contain

[
xyx=yxy
]

and

[
yx=-x.
]

Under associativity only, without commuting (x) and (y),

[
xyx=x(yx)=-x^2
]

while

[
yxy=(yx)y=-(xy).
]

Hence the braid equality gives

[
oxed{x^2=xy}.
]

The new mirror relation immediately extends this to

[
oxed{xw=xy=x^2}
]

and the opposite channel gives

[
oxed{yz=yx=-x}.
]

Combining the separately supplied typed reciprocal

[
xy=1/y
]

gives the typed extension

[
oxed{x^2=1/y}.
]

No conventional two-sided scalar inverse semantics are required for this
internal relation.

---

## 7. Conventional scalar projection boundary

For diagnostic comparison only, Wolfram also tested the simultaneous
conventional commutative characteristic-zero interpretation

[
xy=1/y,qquad
yx=-x,qquad
xyx=yxy,qquad y
eq0.
]

`Reduce[..., Complexes]` returns

[
oxed{	ext{False}}.
]

The first two scalar equations force

[
x=1,qquad y=-1,
]

while the braid then evaluates to

[
-1=+1.
]

This rejects that conventional commutative scalar interpretation. It does not
reject the typed ordered HHS algebra; instead it computationally confirms that
flattening the ordered products and typed reciprocal into one ordinary scalar
multiplication loses required structure.

---

## 8. Lifted X/Y constraint

The supplied lifted definitions are

[
X=xyz,qquad
Y=wxy,
]

with the explicit higher constraint

[
X=YXY.
]

Using only the local directed edge rules plus the braid rule, exact word
rewriting gives

[
xyzightarrow xyxightarrow yxy
]

and

[
wxyightarrow wzyightarrow wzw.
]

Thus

[
X_{	ext{local}}=yxy,
qquad
Y_{	ext{local}}=wzw.
]

The expanded local normal form of (YXY) is

[
wzwyxywzw,
]

which is not (yxy).

Therefore

[
oxed{X=YXY}
]

is preserved as an explicit lifted constraint and is not falsely reported as
a consequence of the lower edge/braid subset alone.

---

## 9. Coupling to the Lo Shu reciprocal involution

The canonical Lo Shu nucleus is

[
L=
egin{pmatrix}
4&9&2\
3&5&7\
8&1&6
end{pmatrix}.
]

Its reciprocal involution is

[
ho(L)=10-operatorname{Rot}_{180}(L),
]

and exactly

[
oxed{ho(L)=L}.
]

The phase matrix satisfies

[
operatorname{Rot}_{180}(P_x)=P_x.
]

Pairing the two cellwise therefore gives

[
T=
egin{pmatrix}
(4,x)&(9,y)&(2,z)\
(3,w)&(5,x)&(7,w)\
(8,z)&(1,y)&(6,x)
end{pmatrix}.
]

Under the joint involution

[
(d,p)mapsto(10-d,p)
]

after a 180-degree rotation,

[
oxed{Tmapsto T}.
]

So the numerical Sudoku/Lo Shu reciprocal geometry and the ordered-phase
palindrome share one exact 3x3 involutive carrier.

---

## 10. Preservation of the 41 fingerprint classes

Pass 220 I014 proved that the 81 oriented Sudoku fingerprints form exactly 41
classes under

[
Fmapsto10-operatorname{Rot}_{180}(F).
]

I015 attaches the centrosymmetric phase matrix (P_x) to every digit
fingerprint and applies the combined transform

[
(F,P_x)
mapsto
(10-operatorname{Rot}_{180}(F),
 operatorname{Rot}_{180}(P_x)).
]

Because

[
operatorname{Rot}_{180}(P_x)=P_x,
]

the phase layer does not split or merge the reciprocal classes.

Exhaustive evaluation over all 81 anchors gives

[
oxed{
41	ext{ combined digit+phase classes}
}
]

with the Lo Shu center remaining the unique fixed reciprocal class.

This is the exact bridge between the newly derived ordered-phase palindrome
and the existing G41 Sudoku fingerprint algebra.

---

## 11. Wolfram exact audit

A consolidated Wolfram Language audit performed exact symbolic,
noncommutative, finite-enumeration, and projection checks.

Result:

[
oxed{23/23	ext{ exact checks passed}}.
]

The checks included:

- (xcdot y=0);
- equal squared norms (2,2);
- exact four-coordinate mirror involution;
- nine-symbol path palindrome;
- phase-matrix 180-degree symmetry;
- Lo Shu reciprocal fixed point;
- combined Lo Shu/phase fixed point;
- exact forward/mirror endpoint reversal;
- residual representative invariance;
- identical (q=-1) projected traversal sequences;
- projected product (+1) in both views;
- noncommutative reduction of the braid modulo (yx=-x), yielding
  (x^2=xy);
- (X) and (Y) local word normal forms;
- independence of the lifted (X=YXY) relation from the lower subset;
- failure of the conventional commutative scalar projection;
- combined reciprocal closure for all 81 Sudoku fingerprints;
- preservation of exactly 41 combined fingerprint classes.

The noncommutative braid calculation used Wolfram's
`NonCommutativePolynomialReduction`; the 81-state checks used exact integer
enumeration only.

---

## 12. Runtime implementation

Implementation:

`hhs_runtime/hhs_pass220_palindromic_ordered_phase_v1.py`

The module provides:

- exact (x,y) four-vector mirror witnesses;
- the nine-symbol palindrome and 3x3 phase matrix;
- forward/mirror ordered edge traversal;
- edge-class normalization from all eight supplied pair products;
- exact (q=-1) projection;
- residual representative-equivalence witnesses;
- braid/typed-reciprocal derivation witness;
- deterministic local word rewriting for (X,Y);
- explicit conventional-scalar negative witness;
- combined Lo Shu/phase involution;
- exhaustive G41 combined-class verification;
- a guarded read-only self-test.

The callable service is

`pass220.palindromic_ordered_phase.self_test`.

Its conformance declaration includes HHS-I008, I010, I011, I012, I014, and
I015.

---

## 13. Authority boundaries

I015 does not:

- commute (xy) with (yx) or (zw) with (wz);
- infer (w=y) from (xw=xy);
- infer (x=z) from (wx=wz);
- identify the forward and mirror ordered class sequences before projection;
- replace the explicit lifted (X=YXY) constraint with an unproved lower-rule
  derivation;
- grant conventional scalar inverse semantics to the typed `1/y` surface;
- widen canonical VM81 mutation authority;
- mint Hash72 or Hash216 authority;
- introduce floating-point canonical authority.

The implemented result is an exact palindromic ordered-phase witness that
composes with the existing 81-cell / 41-fingerprint Sudoku geometry.
