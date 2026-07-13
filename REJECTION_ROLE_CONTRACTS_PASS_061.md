# Rejection Role Contracts Pass 061

- schema: `HHS_REJECTION_ROLE_CONTRACTS_PASS_061_V1`
- status: `PASS`

```json
{
  "role_contract": {
    "allowed_reason_codes": [
      "INVALID_EFFECT_IDENTITY",
      "MISSING_LOCAL_REVALIDATION"
    ],
    "allowed_subject_types": [
      "CANONICAL_ADMISSION_RECORD",
      "PROJECTION"
    ],
    "authority": "HHS_I019_BOUNDED_REJECTION_AUTHORITY_V1",
    "global_denial_authority": false,
    "max_propagation_depth": 0,
    "permanent_denial_authority": false,
    "rejection_role_contract_root_hash72": "HK1AguU<ydaEmR/nuHV<BH-<?QKiZxPswL5INOp<x*l6TBak-dlY*2(A95cD5-QCZPs+S4mh",
    "requires_expiry_or_release_condition": true,
    "requires_independent_revalidation": true,
    "requires_provenance": true,
    "role_id": "role:transaction-recovery-validator",
    "schema": "HHS_BOUNDED_REJECTION_ROLE_CONTRACT_V1",
    "version": "PASS_061_BOUNDED_REJECTION_AUTHORITY_MINIMAL_CORRECTIVE_PROPAGATION_V1"
  },
  "schema": "HHS_REJECTION_ROLE_CONTRACTS_PASS_061_V1"
}
```
