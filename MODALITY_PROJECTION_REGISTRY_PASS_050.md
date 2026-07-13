# MODALITY PROJECTION REGISTRY PASS 050

Status: `True`

Schema: `HHS_MODALITY_PROJECTION_REGISTRY_SELF_TEST_V1`

```json
{
  "lossy_unmarked_rejection": {
    "ok": false,
    "projection_id": "projection:fb06bcf6fe054a939d8d8797646e18d5",
    "reasons": [
      "REJECT_LOSSY_PROJECTION_UNMARKED"
    ],
    "schema": "HHS_MODALITY_PROJECTION_RECORD_VALIDATION_V1",
    "status": "REJECT_MODALITY_PROJECTION",
    "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
  },
  "ok": true,
  "projection": {
    "adapter_id": "adapter:pdf.universal_modality",
    "authority": "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1",
    "created_at_unix_ms": 1783809205892,
    "loss_profile": "LOSSY_DERIVED_PROJECTION",
    "lossy_projection": true,
    "lossy_projection_marked": true,
    "projection_id": "projection:fb06bcf6fe054a939d8d8797646e18d5",
    "projection_payload_hash72": "02egX8<5k7mhj?hdcdhBasmFabPfwgyXo><qQVyXBEqK-vKQZz!MHDSTUVWXYZ-+*/()<>!z",
    "projection_replaces_source": false,
    "projection_root_hash72": "5j<O7>8MtWU+wU5/g6yl/Cl-2x-G2!L63plN4G)se+Stz8npmdDibIrLbYJThzblBJ<MtHC9",
    "projection_type": "TEXT_PROJECTION",
    "reconstruction_recipe": {
      "artifact_root_hash72": "",
      "authority": "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1",
      "expanded_metadata_retained": false,
      "operations": [
        {
          "adapter_id": "adapter:pdf.universal_modality",
          "operation": "reconstruct_projection_from_source_and_adapter",
          "projection_type": "TEXT_PROJECTION"
        }
      ],
      "projection_roots": [],
      "recipe_id": "modality-recipe:e7a23489158d42aba60ad3921daf2430",
      "recipe_root_hash72": "GPj5P8fr?EwpK69gUasjS1wniU0Hxc6CKzq?(St?HX2IIFrRkHQMv9auJM/CKPJ5lAGY)wa+",
      "reconstruction_strategy": "SOURCE_ROOT_PLUS_TYPED_PROJECTION_STEPS_PLUS_ARTIFACT_LINEAGE",
      "schema": "HHS_MODALITY_RECONSTRUCTION_RECIPE_V1",
      "source_root_hash72": "V-b<oVrCYejcHdn716Bab0RzdkCGT0StG(NB<Z)yJBu-gUPGc+fm?NwyjndzNPTPVegf?1J5",
      "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
    },
    "schema": "HHS_MODALITY_PROJECTION_RECORD_V1",
    "source_commitment_id": "source:e04d1094a1af444583a004f1104b95ad",
    "source_modality": "PDF",
    "source_root_hash72": "V-b<oVrCYejcHdn716Bab0RzdkCGT0StG(NB<Z)yJBu-gUPGc+fm?NwyjndzNPTPVegf?1J5",
    "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
  },
  "schema": "HHS_MODALITY_PROJECTION_REGISTRY_SELF_TEST_V1",
  "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
}
```
