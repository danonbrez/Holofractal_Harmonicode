# Global Reciprocity Validation Pass 062

- schema: `HHS_GLOBAL_RECIPROCITY_VALIDATION_PASS_062_V1`
- status: `PASS`

```json
{
  "schema": "HHS_GLOBAL_RECIPROCITY_VALIDATION_PASS_062_V1",
  "self_test": {
    "negative_cases": {
      "bad_gear": {
        "authority": "HHS_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_AUTHORITY_V1",
        "coordinates": {
          "w": 5,
          "x": 1,
          "y": 2,
          "z": 3
        },
        "local_reciprocal_pair_root_hash72": "G48qkbnmuc4kj(AfIdjN<<GTq/vq>B3XVdbBvHcQs5My(>RILR(dBf?L6UgC+DX4z00M4!3n",
        "negative_phase_axis": [
          "z",
          "w"
        ],
        "orientation_balance_mod72": 67,
        "orientation_closed": false,
        "orientation_equation": "x + y = z + w (mod 72)",
        "positive_phase_axis": [
          "x",
          "y"
        ],
        "reasons": [
          "REJECT_XYZW_ORIENTATION_CLOSURE_FAILURE"
        ],
        "role_boundary_bypassed": false,
        "schema": "HHS_XYZW_RECIPROCAL_PHASE_GEAR_V1",
        "status": "REJECT_XYZW_PHASE_GEAR",
        "version": "PASS_062_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_XYZW_PHASE_GEAR_V1",
        "xyzw_phase_gear_root_hash72": "yD1oIISZqxEvgyh1lON)VkM7AyuAU>jU*)pKTV+ijKWfmgvJxCMV(qxxm5)*lYgpDpD5lO)3"
      },
      "bad_validation": {
        "authority": "HHS_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_AUTHORITY_V1",
        "authority_non_amplifying": false,
        "canonical_reciprocity": false,
        "contraction_root_hash72": "cUIyw!4kH9tKd8?AW6PNYiUpstzIJS6Z<6KWwTE0sJwiaowR9UiY?7byOc5BezE1-jxww2UR",
        "global_reciprocity_validation_root_hash72": "Pwg1CqPrYN06eOLNyw!tJ*ly5EJ?xZBjnJczRNPut6dy)fy*sAKQs5D2xaGBx3fMDsFZQ9XV",
        "global_topology_root_hash72": "ox97RX/lRX1zlchmNu94pX6D7sr5rwT(Zn-UvJwk*SkbmMFE64Td/>qMXsRCeYDB4jE2lY2p",
        "reasons": [
          "REJECT_POSITIVE_PHASE_AMPLIFIES_AUTHORITY",
          "REJECT_NEGATIVE_PHASE_AMPLIFIES_REJECTION",
          "REJECT_RECIPROCAL_PAIR_COLLAPSES_TO_ONE_SIDED_CONTROL",
          "REJECT_CONTRACTION_NOT_LEFT_INVERSE_OF_EXPANSION"
        ],
        "reciprocal_distinction_preserved": false,
        "rejection_non_amplifying": false,
        "schema": "HHS_GLOBAL_RECIPROCAL_TOPOLOGY_VALIDATION_V1",
        "status": "REJECT_GLOBAL_RECIPROCAL_CONTINUATION",
        "version": "PASS_062_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_XYZW_PHASE_GEAR_V1"
      }
    },
    "ok": true,
    "run_root_hash72": "*HpXRq-FPZ14ZYlG!hpOl*iq1nNN3qqi5WV>aEZrt75NFqbt5yG-CQXg9>FGaLsV6!m<u2TI",
    "schema": "HHS_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_SELF_TEST_V1"
  },
  "validation": {
    "authority": "HHS_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_AUTHORITY_V1",
    "authority_non_amplifying": true,
    "canonical_reciprocity": true,
    "contraction_root_hash72": "QSoOqhl7h2FYE0LS/HQVgNmosPecg4ZVmM*b-(/W2SBxGF8(3C6fEJT9uU3GU4zesxjcQA?U",
    "global_reciprocity_validation_root_hash72": "C/v0UH4gs+/eMzc-tmwGuXgPFh*)hhvL2pr8</+9Wn(VYq5yopCpZ??56a9LekFlT?7JbX8i",
    "global_topology_root_hash72": "ox97RX/lRX1zlchmNu94pX6D7sr5rwT(Zn-UvJwk*SkbmMFE64Td/>qMXsRCeYDB4jE2lY2p",
    "reasons": [],
    "reciprocal_distinction_preserved": true,
    "rejection_non_amplifying": true,
    "schema": "HHS_GLOBAL_RECIPROCAL_TOPOLOGY_VALIDATION_V1",
    "status": "ADMIT_GLOBAL_RECIPROCAL_CONTRACT_CONTINUATION",
    "version": "PASS_062_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_XYZW_PHASE_GEAR_V1"
  }
}
```
