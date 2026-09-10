# Pass 219 RML7 Exact Hopf Projection — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML6 validated head: `de081a3e4405b40ac07386d465029954c2810a09`
- RML6 validation seal: `de3b12440a18734dc9c6d55501fe9210f679cb5f`
- RML7 implementation: `e9c7b16fab14f95ccf7810ae1c5d8ab9467f7481`
- RML7 tests: `b7a89e7ef977e9a30f6fec3ccd109c1ac6926c89`
- RML7 workflow / validated head: `71fa0ef9dd64376862585feb33e61f9e3b815457`
- RML7 dependency-scoped validation seal: `429f4f4104deb6f26db4f3129f7e0d6466300f68`

## RML7 validation frozen green

- Workflow: `Pass 219 Exact Hopf Projection`
- Run: `34420516153`
- Job: `102694683447`
- Result: `88 passed, 0 failed, 1 inherited pytest-config warning in 12.20s`
- Validated dependency scope: RML5 through RML7 topology tests.

Observed complete generator partition on the canonical audit fixture:

```text
4   FIBER_PRESERVING_SAME_HOPF_BASE
286 BASE_MOVING_HOPF_TRANSPORT
0   inverse Hopf-base restoration failures
---
290 total generator cases
```

The four same-base cases are exactly the zero-step identity moves:

```text
x:0
y:0
z:0
w:0
```

Both `u^36` chiral-pair flips are base-moving under the RML7 Hopf candidate, but each exact self-inverse restores the original Hopf base.

## Exact topology result

RML7 consumes the validated RML6 rational `S^7` embedding and applies the exact quaternionic map

```text
H(q1,q2) = (2*q1*conjugate(q2), |q1|^2-|q2|^2)
```

with no float authority.

The exact unit `S^4` identity is verified from

```text
A+B = D^2
|q1*conjugate(q2)|^2 = A*B
4*A*B + (A-B)^2 = (A+B)^2 = D^4.
```

RML7 also proves exact Hopf-base invariance under the discrete quaternion subgroup

```text
Q8 = {+1,-1,+i,-i,+j,-j,+k,-k}
```

acting simultaneously on the right of `(q1,q2)`.

## Authority and claim boundary

RML7 proves:

- exact rational `S^7 -> S^4` Hopf projection on the RML6 image;
- exact unit-norm `S^4` output;
- exact `Q8` fiber invariance;
- complete classification of all 290 RML5 generator cases;
- exact inverse restoration of the source Hopf base in every case.

RML7 does not claim:

- closure of the entire RML6 discrete image under the full `S^3` fiber action;
- full RML5 generator fiber-equivariance;
- classical Bott-periodicity theorem correspondence;
- physical topological hardware authority.

## Repair-forward successor already started

RML8 binds the validated RML7 topology packet to the inherited Pass 187/188 native Bott substrate instead of creating a parallel Bott abstraction.

Current RML8 lineage at this update:

- implementation: `6ed16bcf65ff7f890845dce0e7d0011945bd7035`
- tests: `9845865df562ad4f7718fb040d71702bd111f653`
- contract: `c9795757ced93b3494e152ca30a920e789ec719e`
- checksum contract repair: `87e7b0171032c77197934d04c0b4c321cc189f8d`
- workflow / target head: `47854f340aa4910c620ccff11e0c02399605db67`
- targeted run: `34425763871`
- targeted job: `102710529097`
- current status: queued

## Required next action

1. Resolve RML8 run `34425763871`, job `102710529097`.
2. If green, freeze both native Pass188 `make validate` and RML5-RML8 Python dependency evidence.
3. If red, repair only the impacted RML8/native bridge surface.
4. Keep the Pass188 `basis8` asymmetric-collapse map typed as a classifier/projection; it must not overwrite RML5 reciprocal phase-state authority.
5. Only after the repository-internal Bott8 bridge is green should any stronger classical Bott-periodicity correspondence be attempted.

Do not rewrite frozen RML1-RML7, I148, Pass187/188, or Pass169 evidence in place.
