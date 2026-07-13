# HHS Transformation Permanence Invariant v1

## Rule

```text
Derived HHS Entry => Permanent Transformation Record
```

Any new entry synthesized from HHS-encoded content must permanently preserve the manipulation that produced it, unless it enters Genesis severance and makes no continuity claim with the source.

## Valid paths

```text
Continuity Path:
Source S -> Transformation T -> Derived Entry D
T is permanently stored.

Genesis Severance Path:
Source S -> Boundary Witness
New Genesis Seed -> New Entry D
D does not claim continuous identity with S.
```

## Invalid path

```text
Source S -> hidden manipulation T -> Derived Entry D
D claims legitimacy while T is omitted.
```

## Rejection codes

```text
REJECT_DERIVED_HHS_ENTRY_WITHOUT_PERMANENT_TRANSFORMATION_RECORD
REJECT_FALSE_CONTINUITY_PROVENANCE_BYPASS
REJECT_SUBSTRATE_EQUIVALENCE_AS_IDENTITY_CONTINUITY
REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM
REJECT_PRIVACY_RECORD_WITHOUT_VALID_SEVERANCE_WITNESS
```
