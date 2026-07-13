# Rejection Non Amplification Pass 061

- schema: `HHS_REJECTION_NON_AMPLIFICATION_PASS_061_V1`
- status: `PASS`

```json
{
  "negative_cases": {
    "amplification": {
      "authority": "HHS_I019_BOUNDED_REJECTION_AUTHORITY_V1",
      "non_amplification_validation_root_hash72": "!GG6fwV8?v>sq+y>2ZM1Iwjn6x0TbrpXmu/*W-rEQRIdocKeDMAEK0?pP)rvJbmKmemZIFJ3",
      "non_amplifying": false,
      "permanent_denial": true,
      "propagation_root_hash72": "0JPttaIyNBxTF)m(sC>GaVp1dGLwp51f)0(t40jBb7+B<P!JlOWpSg-x?m)IC86>CI56X7Rs",
      "reasons": [
        "REJECT_REJECTION_OF_OPERATION_AS_UNRELATED_CAPABILITY_DENIAL",
        "REJECT_REJECTION_AS_PERMANENT_AMBIENT_DENIAL"
      ],
      "rejection_decision_root_hash72": "<gky!H*5/Do1X0w4SU8XE2ORfN+fAIgT9m01!YgWkjQ4dm-p08e3Uy1sN*PHAWBGplwN50I*",
      "schema": "HHS_REJECTION_NON_AMPLIFICATION_VALIDATION_V1",
      "source_identity_preserved": false,
      "status": "REJECT_AMPLIFIED_REJECTION",
      "unrelated_capabilities_preserved": false,
      "version": "PASS_061_BOUNDED_REJECTION_AUTHORITY_MINIMAL_CORRECTIVE_PROPAGATION_V1"
    },
    "excessive_propagation": {
      "affected_descendant_ids": [
        "child:a"
      ],
      "allowed_depth": 0,
      "authority": "HHS_I019_BOUNDED_REJECTION_AUTHORITY_V1",
      "necessity_evidence_roots_hash72": [
        "e"
      ],
      "propagated_target_ids": [],
      "propagation_minimal": false,
      "propagation_root_hash72": "!Y/GW-lYwp)P<S3uw2Kn9y(9ge1p0cXQg*oV1VVuhAaMmeGRpIQ?Bsd1Rutd>1wipuavA+)q",
      "reasons": [
        "REJECT_REJECTION_PROPAGATION_EXCEEDS_AFFECTED_DERIVATION",
        "REJECT_REJECTION_SCOPE_EXCEEDS_ROLE"
      ],
      "rejection_decision_root_hash72": "<gky!H*5/Do1X0w4SU8XE2ORfN+fAIgT9m01!YgWkjQ4dm-p08e3Uy1sN*PHAWBGplwN50I*",
      "requested_depth": 1,
      "requested_target_ids": [
        "child:a",
        "unrelated:b"
      ],
      "schema": "HHS_MINIMAL_CORRECTIVE_PROPAGATION_V1",
      "status": "REJECT_PROPAGATION",
      "version": "PASS_061_BOUNDED_REJECTION_AUTHORITY_MINIMAL_CORRECTIVE_PROPAGATION_V1"
    },
    "global": {
      "authority": "HHS_I019_BOUNDED_REJECTION_AUTHORITY_V1",
      "correction_scope": [
        "LOCAL"
      ],
      "evidence_roots_hash72": [
        "e"
      ],
      "expires_at_sequence": 2,
      "global_effect": false,
      "issued_at_sequence": 1,
      "permanent_effect": false,
      "reason_code": "MISSING_LOCAL_REVALIDATION",
      "reasons": [
        "REJECT_LOCAL_REJECTION_AS_GLOBAL_DENIAL"
      ],
      "rejection_active": false,
      "rejection_decision_root_hash72": "ilXDXbpnnG/l(*0WInkbyVpR(9R4fuAEijyhYjio)0dLVVC6H7HXMzLjYcFpJJ2CVja?TJSw",
      "rejection_role_contract_root_hash72": "HK1AguU<ydaEmR/nuHV<BH-<?QKiZxPswL5INOp<x*l6TBak-dlY*2(A95cD5-QCZPs+S4mh",
      "schema": "HHS_BOUNDED_REJECTION_DECISION_V1",
      "status": "REJECT_REJECTION_DECISION",
      "subject_id": "x",
      "subject_root_hash72": "root",
      "subject_type": "CANONICAL_ADMISSION_RECORD",
      "version": "PASS_061_BOUNDED_REJECTION_AUTHORITY_MINIMAL_CORRECTIVE_PROPAGATION_V1"
    },
    "no_revalidation": {
      "ambient_denial_created": false,
      "authority": "HHS_I019_BOUNDED_REJECTION_AUTHORITY_V1",
      "corrected": true,
      "corrected_subject_root_hash72": "corrected",
      "expired": false,
      "local_revalidation_performed": false,
      "reasons": [
        "REJECT_REMEDIATION_WITHOUT_INDEPENDENT_REVALIDATION",
        "REJECT_CORRECTED_STATE_REMAINS_REJECTED_WITHOUT_REVALIDATION"
      ],
      "rejection_decision_root_hash72": "<gky!H*5/Do1X0w4SU8XE2ORfN+fAIgT9m01!YgWkjQ4dm-p08e3Uy1sN*PHAWBGplwN50I*",
      "rejection_release_root_hash72": "Y7jJ(*H8Fgd26TsW4IYCSX)S1HlkipQC8GU8fgvznN6Ev<>kgCZoy904zxe/dja7a8T-Cji(",
      "rejection_released": false,
      "schema": "HHS_REJECTION_RELEASE_DECISION_V1",
      "status": "HOLD_BOUNDED_REJECTION",
      "version": "PASS_061_BOUNDED_REJECTION_AUTHORITY_MINIMAL_CORRECTIVE_PROPAGATION_V1"
    }
  },
  "schema": "HHS_REJECTION_NON_AMPLIFICATION_PASS_061_V1",
  "validation": {
    "authority": "HHS_I019_BOUNDED_REJECTION_AUTHORITY_V1",
    "non_amplification_validation_root_hash72": "9aU3mpRMf9UgUUW8/rODFQSyfM>liDZJA6xXwlhsP4z63p2nNTWcAozVYGb?73ytEi*>Rf)Q",
    "non_amplifying": true,
    "permanent_denial": false,
    "propagation_root_hash72": "0JPttaIyNBxTF)m(sC>GaVp1dGLwp51f)0(t40jBb7+B<P!JlOWpSg-x?m)IC86>CI56X7Rs",
    "reasons": [],
    "rejection_decision_root_hash72": "<gky!H*5/Do1X0w4SU8XE2ORfN+fAIgT9m01!YgWkjQ4dm-p08e3Uy1sN*PHAWBGplwN50I*",
    "schema": "HHS_REJECTION_NON_AMPLIFICATION_VALIDATION_V1",
    "source_identity_preserved": true,
    "status": "ADMIT_BOUNDED_REJECTION_EFFECT",
    "unrelated_capabilities_preserved": true,
    "version": "PASS_061_BOUNDED_REJECTION_AUTHORITY_MINIMAL_CORRECTIVE_PROPAGATION_V1"
  }
}
```
