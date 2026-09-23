# HARMONICODE Q144/H36 Holofractal Relativistic Game-Engine Theorem

## 1. Shared 5,184 state

The game engine uses one exact finite state geometry:

~~~text
144*36
=
12*12*3*12
=
81*64
=
72*72
=
5184.
~~~

These are simultaneous coordinate systems over one exact address space.

## 2. Euclidean rotation

For each Q144 address k, define zeta as a primitive 144th root of unity.

Then:

~~~text
cos_k = (zeta^k + zeta^-k)/2
sin_k = (zeta^k - zeta^-k)/(2i).
~~~

The Euclidean rotation matrix is therefore represented exactly in
`Q(zeta_144)` without scalar trigonometric approximation.

## 3. Harmonic36 coordinate

For each address n in `0..5183`:

~~~text
word144 = floor(n/36)
bit36 = n mod 36

bank3 = floor(bit36/12)
pitch12 = bit36 mod 12

cell81 = floor(n/64)
operation64 = n mod 64

phase_left8 = floor(operation64/8)
phase_right8 = operation64 mod 8

rule64 = operation64 + 1.
~~~

This is the Python projection of the existing native H36 coordinate contract.

## 4. Platonic closure

For an admitted Schläfli pair `{p,q}`, let:

~~~text
E = 2 p q / (2p + 2q - pq)
V = 2E/q
F = 2E/p.
~~~

I041 admits only exact integral closures satisfying:

~~~text
pF=2E
qV=2E
V-E+F=2.
~~~

Exactly five regular convex families close.

## 5. Sprite identity

A deterministic source root generates:

~~~text
PREV72 || STATE72 || RECEIPT72
~~~

of total length 216.

Each phase index has exact reciprocal:

~~~text
r(v) = (v+36) mod 72.
~~~

The descriptor is exact before any rendering projection.

## 6. Color/music relation

Q144 provides the exact color phase.

H36 provides the exact bank/pitch/rule phase.

Both are attached to the same game-frame Q144 coordinate and the same 5,184
address geometry.

Color reciprocity is:

~~~text
q'=(q+72) mod 144.
~~~

## 7. Shader projection

The shader consumes the exact sprite, Q144 rotation, H36 music coordinate,
Platonic topology, and reciprocal color coordinate.

A GPU may lower the shader to floating values, but those values are projection
data and cannot replace the exact state that generated them.

## 8. Relativistic game state

The frame additionally carries the frozen I040 observation projection and I039
shared root.

Therefore the game-physics projection, graphics projection, music projection,
and sprite projection are siblings of one exact state rather than independent
engines.

## 9. Closure

Define `G(S)` as the conjunction of:

~~~text
Q144 exact address closure
H36 full 5184 coverage
Q(zeta_144) Euclidean rotation identity
all five Platonic incidence closures
Sprite216 closure
Q144 color reciprocal closure
typed shader-source identity
I040 relativistic projection closure.
~~~

I041 accepts the game-engine cycle exactly when:

~~~text
G(S)=true.
~~~
