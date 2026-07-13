# LOCAL PARALLEL BRANCH TREE PASS 065

```json
{
  "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
  "bottleneck": {
    "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
    "bottleneck_root_hash72": "HL01tILosnx(jjwVkSoU3+c+rrz83B<ncW1WhJGj8d)<37T+?Ed+ZH9lJASIBWN*k6Wf*gCo",
    "canonical_parent_root_hash72": "vE(LKbdy1fQoD96jKNU64p8xmtYa2X?(3sUTu84cdAzhNm1DE1/3?5?58uU-?JiwpSY!TyQA",
    "conflict_type": "PHASE_INTEGRATION_MISALIGNMENT",
    "constraint_id": "constraint:A=B:integration",
    "global_state_invalid": false,
    "local_scope": [
      "A",
      "B",
      "P",
      "TRANSLATION_PHASE"
    ],
    "minimum_correction_scope": "LOCAL_RELATION_SUBGRAPH",
    "preserve_unaffected_structure": true,
    "requires_parallel_resolution": true,
    "schema": "HHS_LOCAL_CONSTRAINT_BOTTLENECK_V1",
    "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
  },
  "branch_contracts": [
    {
      "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
      "authority_expires": "BRANCH_CLOSURE",
      "authority_scope": [
        "INSPECT_LOCAL_RELATIONS",
        "PROPOSE_LOCAL_TRANSFORMATION",
        "RETURN_WITNESSED_CANDIDATE"
      ],
      "branch_contract_root_hash72": "4BAlke2NdIW<R4ada+<XX0->(WYPAjqL-1wgZ!r7rpp3gy1LU*(G4BqmKI!2(Zy-Q+3V93xh",
      "branch_id": "branch:direct",
      "closed_local_tree": true,
      "forbidden_authorities": [
        "MUTATE_CANONICAL_PARENT",
        "GLOBALIZE_REJECTION",
        "ERASE_SIBLING_BRANCH",
        "CLAIM_A_EQUALS_B_WITHOUT_WITNESS"
      ],
      "local_scope": [
        "A",
        "B",
        "P",
        "TRANSLATION_PHASE"
      ],
      "parent_root_hash72": "HL01tILosnx(jjwVkSoU3+c+rrz83B<ncW1WhJGj8d)<37T+?Ed+ZH9lJASIBWN*k6Wf*gCo",
      "schema": "HHS_CLOSED_BRANCH_CONTRACT_V1",
      "strategy": "DIRECT_RECIPROCAL_ALIGNMENT",
      "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
    },
    {
      "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
      "authority_expires": "BRANCH_CLOSURE",
      "authority_scope": [
        "INSPECT_LOCAL_RELATIONS",
        "PROPOSE_LOCAL_TRANSFORMATION",
        "RETURN_WITNESSED_CANDIDATE"
      ],
      "branch_contract_root_hash72": "meeS-EtUjv3HVmrlFB(HjNWk/ION-2AH9PFOGFO<yEB*4EI?mS3rUcxnPC)!/yzKGAqKg<vn",
      "branch_id": "branch:bridge",
      "closed_local_tree": true,
      "forbidden_authorities": [
        "MUTATE_CANONICAL_PARENT",
        "GLOBALIZE_REJECTION",
        "ERASE_SIBLING_BRANCH",
        "CLAIM_A_EQUALS_B_WITHOUT_WITNESS"
      ],
      "local_scope": [
        "A",
        "B",
        "P",
        "TRANSLATION_PHASE"
      ],
      "parent_root_hash72": "HL01tILosnx(jjwVkSoU3+c+rrz83B<ncW1WhJGj8d)<37T+?Ed+ZH9lJASIBWN*k6Wf*gCo",
      "schema": "HHS_CLOSED_BRANCH_CONTRACT_V1",
      "strategy": "TRANSLATION_PHASE_BRIDGE",
      "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
    },
    {
      "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
      "authority_expires": "BRANCH_CLOSURE",
      "authority_scope": [
        "INSPECT_LOCAL_RELATIONS",
        "PROPOSE_LOCAL_TRANSFORMATION",
        "RETURN_WITNESSED_CANDIDATE"
      ],
      "branch_contract_root_hash72": "QbIEqh!MON0s)PY)7mNlqy-2CLmYbaZXDJlgMibdWqNqces9Wfs0<rddw/m*t(tsfp1unn3T",
      "branch_id": "branch:contract",
      "closed_local_tree": true,
      "forbidden_authorities": [
        "MUTATE_CANONICAL_PARENT",
        "GLOBALIZE_REJECTION",
        "ERASE_SIBLING_BRANCH",
        "CLAIM_A_EQUALS_B_WITHOUT_WITNESS"
      ],
      "local_scope": [
        "A",
        "B",
        "P",
        "TRANSLATION_PHASE"
      ],
      "parent_root_hash72": "HL01tILosnx(jjwVkSoU3+c+rrz83B<ncW1WhJGj8d)<37T+?Ed+ZH9lJASIBWN*k6Wf*gCo",
      "schema": "HHS_CLOSED_BRANCH_CONTRACT_V1",
      "strategy": "LOCAL_RECIPROCAL_CONTRACTION",
      "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
    }
  ],
  "branch_receipts": [
    {
      "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
      "branch_contract_root_hash72": "4BAlke2NdIW<R4ada+<XX0->(WYPAjqL-1wgZ!r7rpp3gy1LU*(G4BqmKI!2(Zy-Q+3V93xh",
      "branch_execution_root_hash72": ">lR/hOxzcn?<AHJhNtRx)PluzhRVB-y!U<0WMVMG-rlmnpiLAybk*ydopzYpdXQWREGMWUaw",
      "branch_id": "branch:direct",
      "candidate": {
        "A": "P^2",
        "B": "P^2",
        "cost": 3,
        "phase_residue": "0",
        "relation": "A=B"
      },
      "canonical_parent_mutated": false,
      "diagnostics": [],
      "execution_status": "CANDIDATE_RETURNED",
      "local_only": true,
      "provenance_complete": true,
      "schema": "HHS_BRANCH_EXECUTION_RECEIPT_V1",
      "strategy": "DIRECT_RECIPROCAL_ALIGNMENT",
      "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
    },
    {
      "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
      "branch_contract_root_hash72": "meeS-EtUjv3HVmrlFB(HjNWk/ION-2AH9PFOGFO<yEB*4EI?mS3rUcxnPC)!/yzKGAqKg<vn",
      "branch_execution_root_hash72": "o/A<cwNLdrOWC8vVZSfMCDMnTs4Z/WUfi2P7**YBnxVhD27v)ZuS/I5Jo)PbOy*Apo-GtUNi",
      "branch_id": "branch:bridge",
      "candidate": {
        "A": "LHS",
        "B": "RHS",
        "cost": 5,
        "phase_residue": "0",
        "relation": "A~B via witnessed bridge"
      },
      "canonical_parent_mutated": false,
      "diagnostics": [
        "LOCAL_INFORMATION_ENERGY_BOTTLENECK"
      ],
      "execution_status": "CANDIDATE_RETURNED",
      "local_only": true,
      "provenance_complete": true,
      "schema": "HHS_BRANCH_EXECUTION_RECEIPT_V1",
      "strategy": "TRANSLATION_PHASE_BRIDGE",
      "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
    },
    {
      "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
      "branch_contract_root_hash72": "QbIEqh!MON0s)PY)7mNlqy-2CLmYbaZXDJlgMibdWqNqces9Wfs0<rddw/m*t(tsfp1unn3T",
      "branch_execution_root_hash72": "))NmLqL7UO0UaeJP1D9w6>!Bepz<X4JFhwT18s+GOJgF?KGgozOD3Dvk10KAq>F/*vGeHQ9?",
      "branch_id": "branch:contract",
      "candidate": {
        "A": "P^2",
        "B": "P^2",
        "cost": 4,
        "phase_residue": "0",
        "relation": "A=B after local contraction"
      },
      "canonical_parent_mutated": false,
      "diagnostics": [
        "LOCAL_CONTRADICTION_DETECTED"
      ],
      "execution_status": "CANDIDATE_RETURNED",
      "local_only": true,
      "provenance_complete": true,
      "schema": "HHS_BRANCH_EXECUTION_RECEIPT_V1",
      "strategy": "LOCAL_RECIPROCAL_CONTRACTION",
      "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
    }
  ],
  "closure": {
    "all_branch_authority_expired": true,
    "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
    "branch_contract_roots_hash72": [
      "4BAlke2NdIW<R4ada+<XX0->(WYPAjqL-1wgZ!r7rpp3gy1LU*(G4BqmKI!2(Zy-Q+3V93xh",
      "meeS-EtUjv3HVmrlFB(HjNWk/ION-2AH9PFOGFO<yEB*4EI?mS3rUcxnPC)!/yzKGAqKg<vn",
      "QbIEqh!MON0s)PY)7mNlqy-2CLmYbaZXDJlgMibdWqNqces9Wfs0<rddw/m*t(tsfp1unn3T"
    ],
    "branch_execution_roots_hash72": [
      ">lR/hOxzcn?<AHJhNtRx)PluzhRVB-y!U<0WMVMG-rlmnpiLAybk*ydopzYpdXQWREGMWUaw",
      "o/A<cwNLdrOWC8vVZSfMCDMnTs4Z/WUfi2P7**YBnxVhD27v)ZuS/I5Jo)PbOy*Apo-GtUNi",
      "))NmLqL7UO0UaeJP1D9w6>!Bepz<X4JFhwT18s+GOJgF?KGgozOD3Dvk10KAq>F/*vGeHQ9?"
    ],
    "branch_tree_closure_root_hash72": "0gBE<<UoUEboZvhXT/7nSRa3m)N!<hF55+N9K6EHM(ZNDY(*0YPiosiAwtaH(1SdK1dQPLSW",
    "canonical_continuation": true,
    "closed_local_tree": true,
    "failed_branch_rejection_propagated": false,
    "global_rejection_emitted": false,
    "parent_root_hash72": "vE(LKbdy1fQoD96jKNU64p8xmtYa2X?(3sUTu84cdAzhNm1DE1/3?5?58uU-?JiwpSY!TyQA",
    "reintegration_root_hash72": "xG?NPI7DLbYXuxyorU)N/AQa68/2kXgYpnRPxH4NAZ3IZ1H+v/-njClyail55QSdbc8VT6Wh",
    "schema": "HHS_LOCAL_BRANCH_TREE_CLOSURE_RECEIPT_V1",
    "status": "ADMIT_CANONICAL_CONTINUATION",
    "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
  },
  "comparison": {
    "admissible_branch_ids": [
      "branch:direct",
      "branch:bridge",
      "branch:contract"
    ],
    "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
    "branch_roots_hash72": [
      ">lR/hOxzcn?<AHJhNtRx)PluzhRVB-y!U<0WMVMG-rlmnpiLAybk*ydopzYpdXQWREGMWUaw",
      "o/A<cwNLdrOWC8vVZSfMCDMnTs4Z/WUfi2P7**YBnxVhD27v)ZuS/I5Jo)PbOy*Apo-GtUNi",
      "))NmLqL7UO0UaeJP1D9w6>!Bepz<X4JFhwT18s+GOJgF?KGgozOD3Dvk10KAq>F/*vGeHQ9?"
    ],
    "comparative_revalidation_performed": true,
    "comparative_revalidation_root_hash72": "mffQQ)dsFmeRRr/Gh9+YD/ql)0U7+lQn8qOW>Y/>t(pwx0QTAjA7Aqpv<agPlDg+-kCswzLz",
    "reasons": [],
    "schema": "HHS_PARALLEL_BRANCH_COMPARATIVE_REVALIDATION_V1",
    "selected_branch_id": "branch:direct",
    "selection_rule": "MINIMUM_ADMISSIBLE_LOCAL_CORRECTION_COST_THEN_BRANCH_ID",
    "status": "ADMIT_LOCAL_BRANCH_SELECTION",
    "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
  },
  "ok": true,
  "pass064_root_hash72": "vE(LKbdy1fQoD96jKNU64p8xmtYa2X?(3sUTu84cdAzhNm1DE1/3?5?58uU-?JiwpSY!TyQA",
  "reintegration": {
    "A_state": "P^2",
    "B_state": "P^2",
    "authority": "HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1",
    "bottleneck_root_hash72": "HL01tILosnx(jjwVkSoU3+c+rrz83B<ncW1WhJGj8d)<37T+?Ed+ZH9lJASIBWN*k6Wf*gCo",
    "canonical_reintegration_admissible": true,
    "integration_relation": "A=B",
    "local_scope_preserved": true,
    "reasons": [],
    "reintegration_root_hash72": "xG?NPI7DLbYXuxyorU)N/AQa68/2kXgYpnRPxH4NAZ3IZ1H+v/-njClyail55QSdbc8VT6Wh",
    "schema": "HHS_A_EQUALS_B_PHASE_REINTEGRATION_WITNESS_V1",
    "selected_branch_id": "branch:direct",
    "status": "ADMIT_A_EQUALS_B_REINTEGRATION",
    "translation_phase_aligned": true,
    "unaffected_structure_preserved": true,
    "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
  },
  "rejection_codes": [
    "REJECT_BRANCH_WITHOUT_CANONICAL_PARENT_ROOT",
    "REJECT_BRANCH_WITHOUT_LOCAL_CONSTRAINT_SCOPE",
    "REJECT_BRANCH_AUTHORITY_EXCEEDS_PARENT",
    "REJECT_BRANCH_ESCAPES_CLOSED_LOCAL_TREE",
    "REJECT_CONTRADICTION_AS_GLOBAL_INVALIDATION",
    "REJECT_BOTTLENECK_AS_GLOBAL_FAILURE",
    "REJECT_BRANCH_RESULT_WITHOUT_PROVENANCE",
    "REJECT_BRANCH_RESULT_WITHOUT_COMPARATIVE_REVALIDATION",
    "REJECT_UNRESOLVED_PHASE_MISALIGNMENT_AS_FALSE_EQUALITY",
    "REJECT_A_EQUALS_B_WITHOUT_INTEGRATION_WITNESS",
    "REJECT_FAILED_BRANCH_PROPAGATES_REJECTION",
    "REJECT_BRANCH_TREE_WITHOUT_BOUNDED_CLOSURE"
  ],
  "run_root_hash72": "EMf/Z4X(bwFn4f(v2+<IBa2rJZIES<bGGEehYQXHN1W+9cOCeRXUU+w4vm(mDlWPr0iDvpeV",
  "schema": "HHS_LOCAL_PARALLEL_BRANCH_TREE_RUN_V1",
  "version": "PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
}
```
