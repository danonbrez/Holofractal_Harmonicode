# Pass 220 I036 — Genesis / Reverse-Offset Holographic Lo Shu Nucleus

Date: 2026-09-23

## Scope

I036 freezes three exact coordinate views of the same Lo Shu nucleus:

~~~text
Genesis offset : {-4,-3,-2,-1,0,1,2,3,4}
Lo Shu magnitude: {1,2,3,4,5,6,7,8,9}
reverse offset : {-3,-1,1,3,5,7,9,11,13}
~~~

For each Lo Shu magnitude `m`:

~~~text
epsilon = m - 5
m       = epsilon + 5
r       = 5 + 2*epsilon
r       = 2*m - 5
~~~

All three representations remain co-resident and retain the same cell address.

## Nucleus matrices

Magnitude:

~~~text
4 9 2
3 5 7
8 1 6
~~~

Genesis offset:

~~~text
-1  4 -3
-2  0  2
 3 -4  1
~~~

Reverse offset:

~~~text
 3 13 -1
 1  5  9
11 -3  7
~~~

The Genesis view has row/column/diagonal sum 0. The magnitude and reverse-offset views each have row/column/diagonal sum 15.

## Center and reflection

The same center cell is:

~~~text
Genesis offset = 0
Lo Shu magnitude = 5
reverse offset = 5
~~~

Reflection pairs retain their layer closures:

~~~text
m + (10-m) = 10
epsilon + (-epsilon) = 0
r + (10-r) = 10
~~~

## Holographic redundancy

Each coordinate view reconstructs the same exact Lo Shu magnitude and therefore the same Lo Shu cell address. No view replaces another.

The nucleus repeats nine times over the inherited VM81 frame:

~~~text
9 nuclei * 9 cells = 81 cells
81 * 64 = 5184
72^2 = 5184
~~~

I036 therefore binds the three local nucleus coordinate views to the already-established VM81/5184 geometry without changing canonical authority.

## Authority

I036 is a validated-operation constructor only:

~~~text
contains local constraints                  = TRUE
canonical constraint creation authority    = FALSE
canonical constraint enforcement authority = FALSE
canonical VM81 mutation authority          = FALSE
canonical Hash72 authority                 = FALSE
canonical Hash216 authority                = FALSE
direct canonical persistence authority     = FALSE
~~~

The existing repository OS remains responsible for downstream hydration.

## Formal result

Connected Wolfram verification:

~~~text
HHS_PASS_220_I036_GENESIS_REVERSE_OFFSET_HOLOGRAPHIC_NUCLEUS_WOLFRAM_20260923_V1
PASS
30 / 30
failed = []
~~~
