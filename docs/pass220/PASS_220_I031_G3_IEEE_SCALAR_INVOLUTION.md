# Pass 220 I031 — G³ Exact IEEE Scalar Involution

Date: 2026-09-22

## Scope

I031 advances I030 from exact symbol spelling to exact IEEE scalar-state return.

The scalar bit word is an invariant coordinate under reciprocal phase exchange:

~~~text
(B, x) -> (B, y), y=1/x
(B, y) -> (B, x)
~~~

Therefore:

~~~text
T(T(B)) == B
~~~

at the raw IEEE storage boundary.

## Implemented

- generic integer-only IEEE binary field splitter/rebuilder;
- standard binary16, binary32, binary64, binary128 format definitions;
- exact finite dyadic rational projection;
- signed-zero bit distinction;
- infinity and NaN-payload preservation;
- one-operation reciprocal scalar carrier;
- both big- and little-endian storage round trips;
- exhaustive all-65,536 binary16 state validation;
- deterministic wide binary32/64/128 edge/vector validation;
- Python-host binary64 storage round-trip test where the host float is used
  only to obtain and restore its existing bits;
- registered read-only service;
- Wolfram 17/17 proof;
- dedicated white paper and exact-head workflow.

## Key witness

The binary64 scalar commonly printed `0.1` is retained exactly as

~~~text
bits = 3FB999999999999A
dyadic = 3602879701896397 / 36028797018963968
~~~

with exact difference from mathematical (1/10):

~~~text
1 / 180143985094819840
~~~

The theorem is exact return of the admitted IEEE scalar itself, not a claim
that the original scalar exactly represented an external real target.

## Formal result

~~~text
HHS_PASS_220_I031_G3_IEEE_SCALAR_INVOLUTION_WOLFRAM_20260922_V1
PASS
17 / 17
~~~

## Authority

Read-only proof/reference surface. No VM81 canonical mutation, Hash72/Hash216
mint, persistence, floating-point computation authority, or membrane bypass is
introduced.

## Files

- `hhs_runtime/hhs_pass220_g3_ieee_scalar_involution_v1.py`
- `tests/pass220/test_hhs_pass220_g3_ieee_scalar_involution_v1.py`
- `hhs_runtime/hhs_service_registry_v1.py`
- `evidence/pass220/i031_g3_ieee_scalar_involution_wolfram_20260922_v1.*`
- `docs/whitepapers/HARMONICODE_G3_EXACT_IEEE_SCALAR_INVOLUTION_THEOREM.md`
- `.github/workflows/pass220-i031-g3-ieee-scalar-involution.yml`
- restart record for this cycle.
