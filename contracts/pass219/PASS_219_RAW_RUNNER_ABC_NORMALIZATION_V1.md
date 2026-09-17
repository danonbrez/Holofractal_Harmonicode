# Pass 219 — Raw Workflow Runner A:B:C Normalization Contract v1

## Purpose

This contract extends the sealed four-phase reciprocal A:B Lane 5 calibration with a raw workflow-runner control over the **same deterministic dataset**.

## Arms

```text
A = Lane 5 exact route validation
    + direct Harmonic36/Hash216 occurrence binding
    + M exponent-lattice bind/validate

B = matched Lane 5 exact route validation only

C = raw native-C record validation/folding only
```

C MUST call neither Lane 5 route admission nor H36/Hash216 M proof APIs during its timed arm.

## Four reciprocal gates

```text
xy : phase 0  -> inverse 36
yx : phase 36 -> inverse 0
zw : phase 18 -> inverse 54
wz : phase 54 -> inverse 18
```

Ordered products remain distinct. No global commutativity rule is introduced.

## Difficulty gradient

Nine exact ranks are required:

```text
rank:      1     2     3     4    5    6    7    8    9
gradient: -1   -3/4  -1/2  -1/4  0   1/4  1/2  3/4   1
N target:  8    16    32    64   128  256  512  1024  2048
```

The gradient is the repository-authoritative `exact_percentile_gradient(rank, 9)` surface.

## Same-dataset invariant

For each `(rank, phase, iteration)` coordinate, one deterministic raw record identity is defined from:

- previous/current/goal values;
- the five 32-byte digest fields;
- workload byte count and integer route cost;
- evidence and contradiction counts;
- reciprocal phase slots;
- binary/trinary/nested-zero state.

A, B, and C MUST generate the same record identity. Each timed arm accumulates a dataset digest independent of its route/proof/control result. For a completed triplet:

```text
A.dataset_digest == B.dataset_digest == C.dataset_digest
```

A and B MUST additionally have identical route digests.

## Raw-runner invariant

For arm C:

```text
route_receipts = 0
m_witnesses = 0
raw_validations = completed
```

The raw validator reconstructs the expected deterministic record and compares the entire defined payload. A corrupted raw record MUST fail closed.

## Run-order normalization

The three timed arms execute in the same workflow job and executable. Order rotates across samples:

```text
ABC
BCA
CAB
```

This does not eliminate all runner noise, but prevents one arm from always occupying the same cache/thermal/order position.

## Exact normalized metrics

For arm `X`:

```text
R_X = completed_X * 1,000,000,000 / elapsed_ns_X
```

All ratios are retained as exact rationals:

```text
A:B = R_A / R_B
A:C = R_A / R_C
B:C = R_B / R_C
```

Decimal display is non-authoritative.

## Difficulty / energy calibration

The existing Pass 067.1 quantity remains the shared rating denominator:

```text
logical tensor quantity          = 225 exact units
logical reciprocal-pair quantity = 450 exact units
rank-r calibration denominator   = r * 450
```

This denominator permits the same difficulty scale to be applied across A/B/C. It MUST NOT be interpreted as granting HHS logical-energy authority to arm C.

Physical joules, watts, package energy, or wall power are **not measured** by this benchmark.

## HHS authority membrane

For A/B:

```text
candidate_only                               = 1
canonical VM81 mutation authority            = 0
canonical Hash72 authority                   = 0
canonical Hash216 authority                  = 0
canonical persistence authority              = 0
floating-point canonical authority           = 0
requires signed environmental VM81 admission = 1
translator_required                          = 0
```

Arm C bypasses those HHS services and therefore does not acquire any of their authority.

## Negative controls

The executable MUST fail closed for at least:

1. illegal reciprocal phase/inverse pair;
2. forced `translator_required=1` in the M witness;
3. corrupted M exponent coordinate;
4. corrupted raw dataset record.

No performance result is admissible before the negative controls pass.

## Admission

A calibration run is valid only when:

- all four phases execute;
- all nine ranks execute;
- all 36 A:B:C triplets complete their target dataset;
- per-triplet dataset digests match across A/B/C;
- A/B route digests match;
- C performs zero HHS route/proof operations;
- exact analyzer checks Pass 067.1 gate closure;
- global and per-leg time bounds hold;
- the HHS authority membrane remains unchanged.
