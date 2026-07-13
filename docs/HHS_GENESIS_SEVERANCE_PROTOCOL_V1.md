# HHS Genesis Severance Protocol v1

## Purpose

Genesis Severance creates a lawful discontinuity boundary for opaque privacy. The parent immutable manifold may witness that the boundary was crossed, but it may not store the opaque transform, child linkage key, reversible mapping, hidden parent pointer, opaque payload, or internal privacy-domain trace.

## Boundary witness rule

```text
Parent manifold stores only the Phase_Inversion_Severance_Witness_V1.
The opaque transformation occurs outside the parent immutable manifold.
```

## Canonical Boundary Fields

These fields, in this exact order, are hashed to certify lawful Genesis severance:

1. `schema`
2. `version`
3. `witness_type`
4. `phase_rule`
5. `parent_phase`
6. `child_phase`
7. `severance_mode`
8. `parent_record_commitment`
9. `new_genesis_seed_commitment`
10. `parent_commitment_policy`
11. `severance_reason`
12. `retained_semantic_constraints`
13. `discarded_identity_fields`
14. `root_marker_declared`
15. `resonator_constant_q`
16. `closure_constant_q`
17. `ring`
18. `extended_ring`
19. `loshu_anchor`
20. `parity_required`
21. `delta_e_required`
22. `omega_required`
23. `parent_trace_continued`
24. `opaque_transform_embedded`
25. `child_public_pointer`
26. `reversible_mapping_stored`
27. `hidden_parent_pointer_stored`
28. `parent_unique_history_exported`
29. `boundary_hash_authority`

## Exact constants

```text
179971.179971 -> 179971179971/1000000
1.001         -> 1001/1000
```

Floats are rejected.

## Parent commitment policies

```text
none
sealed_private_commitment
escrowed_commitment
public_redaction_commitment
```

## Forbidden parent-manifold contents

```text
opaque_transform
opaque_transform_recipe
transform_recipe
child_linkage_key
reversible_mapping
reversible_parent_mapping
hidden_parent_pointer
opaque_payload
internal_privacy_trace
parent_unique_history_export
```

## Sample witness hash

```text
om-UngYNKqWqBONjPY/EA9H*VdtlUU!Mnv<eksC0>Sb6D4y?<9K<iciq<)KZ>jMT?t-IO6bW
```

## Sample validation

```text
GENESIS_SEVERANCE_WITNESS_VALID
```
