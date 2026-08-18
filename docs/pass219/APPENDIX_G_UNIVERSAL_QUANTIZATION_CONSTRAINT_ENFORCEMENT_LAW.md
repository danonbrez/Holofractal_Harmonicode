# Pass 219 Appendix G — Universal Quantization Constraint Enforcement Law

Status: `NORMATIVE APPENDIX TO HHS-P219-LOSHU-DYADIC-QR-UQCEL-1.7.0`

## G-A. Native object

The object under test is not one scalar identity. It is the typed constraint bundle:

```text
Q = ConstraintJoin(L_H, C_metric, C_phase, C_QR, C_VM81, C_lineage)
```

where:

- `L_H` is the Lo Shu tensor polynomial numeral surface;
- `C_metric` is the exact dyadic quantization normalization over `u_q`;
- `C_phase` is the cyclic `u_phase` closure;
- `C_QR` is the ordered `xy/yx` quadratic-reciprocity orientation;
- `C_VM81` binds the native ordered phase witness and address occurrence;
- `C_lineage` binds the admitted state to Hash72/Hash216 predecessor/change/receipt lineage.

No component may be coerced into another component's scalar type merely to make the source string look like an ordinary equation.

## G-B. Lo Shu polynomial

```harmonicode
L_H = {
  {b^4, c^4, b^2},
  {c^2, b^2+c^2, b^4+c^2},
  {b^6, a^2, b^2*c^2}
}
```

The exact integer projection is:

```text
{{4,9,2},{3,5,7},{8,1,6}}
```

with equal row/column/diagonal magic sum.

The fixed derived polynomials used by UQCEL are:

```harmonicode
N12   = c^2*b^4
N36   = b^4*c^4
N72   = b^6*c^4
N73   = b^6*c^4+a^2
N6    = b^2*c^2
N66   = b^6*c^4-b^2*c^2
N5256 = (b^6*c^4)*(b^6*c^4+a^2)
ZERO_L = c^2-c^2
```

## G-C. Metric relation

With explicit scalar projection only at the declared bridge:

```harmonicode
C_metric:
(b^2)^(a^2/((c^2*b^4)*pi_scalar(xy)))
=
b^2*u_q^(b^6*c^4+a^2)
```

For `pi_scalar(xy)=a^2`:

```harmonicode
u_q^(b^6*c^4+a^2)
=
(b^2)^(a^2/(c^2*b^4)-a^2)
```

and one full cycle gives:

```harmonicode
u_q^((b^6*c^4)*(b^6*c^4+a^2))
*
(b^2)^(b^6*c^4-b^2*c^2)
=
a^2.
```

This is the canonical exact closure statement for the metric projection.

## G-D. Phase relation

```harmonicode
C_phase:
u_phase^(b^6*c^4)=a^2
```

`u_phase` is cyclic phase authority. `u_q` is metric-scale authority. They may be reconstructed from one native state only through an explicit bridge record.

## G-E. Quadratic reciprocity

```harmonicode
epsilon_L(p,q)
=
Mod(((p-a^2)*(q-a^2))/b^4, b^2)
```

Selection:

```text
ZERO_L -> xy -> ZERO_L mod N72
a^2    -> yx -> N36   mod N72
```

Phase address:

```harmonicode
Phi_QR = Mod((b^4*c^4)*epsilon_L, b^6*c^4)
```

The conventional sign theorem is a projection oracle. Native orientation remains `xy/yx`.

## G-F. Universal enforcement semantics

`UNIVERSAL` means:

```text
for every candidate state that declares the UQCEL profile,
all applicable UQCEL components are checked before admission.
```

It does not mean that all possible values are coerced into the QR closure subdomain. States outside a subdomain receive an explicit `OUT_OF_DECLARED_DOMAIN` classification for that component, not an invented projection.

The initial conformance audit therefore separates:

```text
SUBSTRATE_COMPATIBLE
ADMISSION_GATE_IMPLEMENTED
ADMISSION_GATE_ENFORCED
```

These statuses MUST NOT be conflated.

## G-G. Existing ABI audit surface

The current exact ABI exposes:

```text
HHS_EXACT_PHASE_X  = 0
HHS_EXACT_PHASE_Y  = 1
HHS_EXACT_PHASE_XY = 4
HHS_EXACT_PHASE_YX = 5
```

and the inherited product results:

```text
x*y -> phase ZERO_L, tag xy
y*x -> phase N36, tag yx
```

The VM81 address is:

```text
address = 64*cell + 8*left + right
```

for `81*64 = 5184` occurrences.

The first audit SHALL prove these properties exhaustively without mutating the C kernel.

## G-H. Test oracle boundary

`hhs_runtime/pass219_quantization_constraint_reference_v1.py` is a non-authoritative exact reference/oracle. It MAY:

- evaluate Lo Shu polynomial integer projections;
- derive the exact rational dyadic exponent;
- classify odd reciprocity residue pairs;
- predict `xy/yx` and `ZERO_L/N36` phase lanes;
- construct test witnesses.

It SHALL NOT:

- mint canonical VM81 state;
- alter Hash72 or Hash216 history;
- use floating point as authority;
- claim that passing correspondence tests proves the admission gate is installed.

## G-I. Advancement rule

Only after the conformance audit is green may a later implementation iteration propose UQCEL as an actual canonical admission constraint. That later step must specify:

```text
stable exact ABI record
candidate-state fields
applicability/domain classification
failure codes
rollback/reverse witness
Hash72 receipt encoding
Hash216 lineage fields
indexed-reuse behavior
Pass 218/219 activation gate
negative tests
benchmark impact
```

This appendix deliberately makes the audit safe before enforcement is introduced.
