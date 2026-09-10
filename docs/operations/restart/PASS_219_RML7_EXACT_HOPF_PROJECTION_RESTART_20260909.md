# Pass 219 RML7 Exact Hopf Projection — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML6 validated head: `de081a3e4405b40ac07386d465029954c2810a09`
- RML6 validation seal: `de3b12440a18734dc9c6d55501fe9210f679cb5f`
- RML6 green restart update: `ade1f0e44a41d6d2845bf76559d925caa844383b`
- RML7 implementation: `e9c7b16fab14f95ccf7810ae1c5d8ab9467f7481`
- RML7 tests: `b7a89e7ef977e9a30f6fec3ccd109c1ac6926c89`
- RML7 contract: `a4bb88dd719dbf45cda4f789a5c5791ef58b1697`
- RML7 workflow / validation target head: `71fa0ef9dd64376862585feb33e61f9e3b815457`

## Parent validation frozen

RML6 is dependency-scoped validated:

- Workflow: `Pass 219 Discrete S7 Embedding`
- Run: `34420155680`
- Job: `102693587051`
- Result: `67 passed, 0 failed, 1 inherited pytest-config warning in 9.55s`
- Generator audit: `290` finite RML5 generator cases

## RML7 purpose

RML7 defines an exact quaternionic Hopf projection candidate over the validated RML6 rational `S^7` embedding.

For an RML6 point split into two quaternions

```text
(q1,q2) in H^2
|q1|^2 + |q2|^2 = 1
```

RML7 applies

```text
H(q1,q2) = (2*q1*conjugate(q2), |q1|^2-|q2|^2)
```

and represents the result as an exact rational point in `S^4`.

No float or trigonometric approximation is used.

## Exact S4 norm proof

With integer numerator norms

```text
A = |q1_num|^2
B = |q2_num|^2
D = common S7 denominator
A+B = D^2
```

and quaternion product numerator `p=q1_num*conjugate(q2_num)`, RML7 verifies

```text
|p|^2 = A*B
```

then the five Hopf base numerators are

```text
(2*p0,2*p1,2*p2,2*p3,A-B)
```

with common denominator `D^2`.

Exact unit norm follows from

```text
4*A*B + (A-B)^2 = (A+B)^2 = D^4.
```

## Concrete fiber witness

RML7 implements the exact quaternion group

```text
Q8 = {+1,-1,+i,-i,+j,-j,+k,-k}
```

as simultaneous right multiplication:

```text
(q1,q2) -> (q1*h,q2*h).
```

For each unit `h in Q8`, exact arithmetic must verify

```text
H(q1*h,q2*h) = H(q1,q2).
```

This is a real fiber-invariance witness for an exact discrete subgroup of the `S^3` Hopf fiber.

RML7 deliberately does not claim that the transformed Q8 point is necessarily inside the RML6 discrete image, nor that the full `S^3` fiber action is closed on that image.

## RML5 generator classification

The full finite RML5 generator family remains the audit target:

```text
288 coupled generator/product Z72 cases
  2 u36 chiral-pair flips
---
290 total cases
```

Each case is classified from exact source/target `S^4` base hashes as either:

```text
FIBER_PRESERVING_SAME_HOPF_BASE
BASE_MOVING_HOPF_TRANSPORT
```

No move is assumed to be fiber-preserving in advance.

Every explicit inverse must restore the exact original Hopf base point.

## Claims not promoted

RML7 does not yet claim:

- closure of the entire RML6 discrete image under the full `S^3` fiber action;
- full RML5 generator fiber-equivariance;
- Hopf-fibration preservation as a global runtime invariant;
- Bott-periodicity correspondence;
- a physical topological hardware theorem.

## Files added

- `hhs_runtime/pass219/discrete_hopf_projection.py`
- `tests/pass219/test_pass219_discrete_hopf_projection.py`
- `contracts/pass219/PASS_219_RML7_EXACT_HOPF_PROJECTION_1_0.json`
- `.github/workflows/pass219-exact-hopf-projection.yml`
- `docs/operations/restart/PASS_219_RML7_EXACT_HOPF_PROJECTION_RESTART_20260909.md`

## Validation status at checkpoint creation

- Workflow: `Pass 219 Exact Hopf Projection`
- Run: `34420516153`
- Job: `102694683447`
- Validation target head: `71fa0ef9dd64376862585feb33e61f9e3b815457`
- Status: `queued`

No RML7 failure has been observed at checkpoint creation.

## Required next action

1. Inspect run `34420516153`, job `102694683447`.
2. If green, freeze exact pass count / elapsed time and promote the RML7 contract to dependency-scoped validated.
3. Record the generator audit partition: same-base cases versus base-moving cases.
4. If red, repair only RML7 and rerun the exact topology dependency scope.
5. After RML7 is green, use the observed classification and Q8 fiber witness to decide the next repair-forward step toward full discrete-image fiber closure/equivariance.
6. Keep Bott periodicity non-canonical until that fiber-preservation layer is demonstrated.

Do not rewrite frozen RML1-RML6, I148, or Pass169 evidence in place.
