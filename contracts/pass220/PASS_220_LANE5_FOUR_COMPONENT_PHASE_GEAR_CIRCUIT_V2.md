# Pass 220 — Lane 5 Four-Component Phase Gear Circuit V2

Status: **SOURCE-LOCKED / CANDIDATE-ONLY UNTIL NATIVE VM81 ADMISSION**.

This is the newly supplied unified four-part `List` circuit. It supersedes the earlier *candidate representation* when the source expressions differ, without replacing prior admitted proofs or receipts.

## Canonical verbatim source

```wolfram
List(u^f/u^List(-72,0,72)^Mod(MatrixTimes(-180,List(List(16,2,3,13),List(5,11,10,8),List(9,7,6,12),List(4,14,15,1)))/60,72^(-1)),{{5*(x-1),-1,4,-3},{5*(x^2-1),-2,0,2},{5*(y-1),3,-4,1},{0,5*(x-1),5*(x^2-1),5*(y-1)}},List(List(List(y,y,y,0*x*y)/(z*w)==-4,List(y,y,x,1*x*y)/(z*w)==-3,List(y,x,y,10*x*y)/(z*w)==-2,List(y,x,x,11*x*y)/(z*w)==-1),List(List(x,y,y,100*x*y)/(z*w)==1,List(x,y,x,101*x*y)/(z*w)==2,List(x,x,y,110*x*y)/(z*w)==3,List(x,x,x,111*x*y)/(z*w)==4),List(List(w,w,w,0*z*w)/(x*y)==-4,List(w,w,z,1*z*w)/(x*y)==-3,List(w,z,w,10*z*w)/(x*y)==-2,List(w,z,z,11*z*w)/(x*y)==-1),List(List(z,w,w,100*z*w)/(x*y)==1,List(z,w,z,101*z*w)/(x*y)==2,List(z,z,w,110*z*w)/(x*y)==3,List(z,z,z,111*z*w)/(x*y)==4)==x+y-z-w+x*y+x^2-z*w-z^2-y^2+w^2==0),List(x^2-x-1,x^3-x-1,x^4-x^3-1,x^5-x^4-x^3-x^2-1,x^3-x^2-1,x^6-x^5-x^4+x^2-1,x^5-x^3-x^2-x-1,x^7-x^6-x^5+x^2-1,x^6-2*x^5+x^4-x^2-1,x^5-x^4-x^2-1,x^8-x^7-x^6+x^2-1==x+y-z-w+x*y-x^4-z*w+z^4+x^2-y^2+z^2-w^2==c^2-b^2-a^2)/(x^2-x-1+x^3-x-1+x^4-x^3-1+x^5-x^4-x^3-x^2-1+x^3-x^2-1+x^6-x^5-x^4+x^2-1+x^5-x^3-x^2-x-1+x^7-x^6-x^5+x^2-1+x^6-2*x^5+x^4-x^2-1+x^5-x^4-x^2-1+x^8-x^7-x^6+x^2-1==x*(x^7-x^4-x^3-x^2-x-3)-(b^4*c^2-x*y)==0))
```

## Typed four-part interpretation (no scalar reassociation)

1. Outer computational phase vector and reference Dürer return: the `-180` numerator of `MatrixTimes` is an adjustable phase-gear angle, NOT a permanently fixed coefficient. Keep the reference expression unchanged and parameterize only through an explicit typed angle input.
2. The 4×4 bordered Lo Shu spatial decoder, retaining the exact positions of `x`, `x^2`, and `y`.
3. The 4×4 bipolar spin register: sixteen ordered vector gate cells at addresses `-4,-3,-2,-1,1,2,3,4` twice, with each `==` preserved, followed by its ordered global closure `== x+y-z-w+x*y+x^2-z*w-z^2-y^2+w^2 == 0`.
4. The eleven-polynomial numerator sequence bound to ONE **sum-of-eleven-numerators** denominator gate, including the internal ordered gates in numerator 11. This replaces the earlier candidate's simplified common denominator `x^8-x^5-x^4-x^3-x^2-3*x-11` for this revision. The ratio is a typed rank-1 circuit `n ⊗ d` and not host scalar division.

## Placement and native authority

Compose four 4×4 blocks into the already-defined 8×8 layout, retaining the order T1 upper-left, T2 upper-right, T4 lower-left, T3 lower-right. The final eleven-polynomial circuit is the authoritative source input for T3's proof/gate construction; the previous numeric coefficient matrix is retained only as a historical witness unless its equivalence is itself receipted.

The complete physical circuit has 64 spatial cells. The outer parameter vectors choose configuration/phase geometry; `4^8=65536` counts possible eight-slot four-choice selections, not physical cells. The exact graph remains the inherited Lane 5 VM81 81×64=5184 knowledge graph with canonical BigInt serialization. No new independent canonical store, hash function, service clock or minting authority is created.

Preserve `0*x*y`, `1*x*y`, `10*x*y`, `100*x*y` etc. verbatim as address-bearing source notation; do not equate those digits with conventional scalar multipliers without a checked native constructor derivation.

## Native admission obligations

- Parse all four outer elements as ordered typed syntax nodes, without algebraic normalizing away the zero-indexed phase terms.
- Hydrate 16 bipolar cell addresses and the full eleven-numerator shared denominator into exact BigInt-serialized graph coordinates.
- Prove the two new global spin closure gates and internal last-polynomial gates in Lean, with Wolfram candidate witnesses.
- Confirm T3 coupling and chiral inverse T4 for this revised source.
- Route through the existing Pass 219 RNA C++ cell wall, signed VM81 environmental admission, and canonical Hash72/Hash216 three-step receipts.
- Check zero-denominator HNAN bypass (gain 1, phase and write-count unchanged), falsified gate rejection, address ordering, two-pass Genesis replay and hash identity.

The source expression is preserved as the authority for subsequent implementation; no claim of new end-to-end native closure is made here.
