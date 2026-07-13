# UNIVERSAL ARTIFACT PIPELINE PASS 050

Status: `True`

Schema: `HHS_UNIVERSAL_ARTIFACT_PIPELINE_SELF_TEST_V1`

```json
{
  "doctrine": "SOURCE_NE_PROJECTION_NE_ARTIFACT_NE_EXECUTION_AUTHORITY",
  "ok": true,
  "pipeline_runs": [
    {
      "adaptation": {
        "adaptation_root_hash72": "h?Iwzs+L+9Uat3ULb2Oj1OfG)VDO18HZTE736hMNpiIWcy+Vnx(b1t)cK-aIIs>cdVu3SZvQ",
        "adapter_contract": {
          "adapter_contract_hash72": "Tk8GJ+rC5eaBdehCJHj)8PrbZd!6nOPtb-0qiyfg!q(6A?P>jWAxMnOHab0Q9E1G5yNNOEa)",
          "adapter_id": "adapter:pdf.universal_modality",
          "artifact_targets": [
            "WORKSPACE_OBJECT",
            "DERIVED_ARTIFACT",
            "CROSS_MODAL_TRANSFORMATION_PLAN"
          ],
          "authority": "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1",
          "authority_tier": "AUTHORIZED_NONMUTATING",
          "chunking_policy": "ROOTED_CHUNK_MANIFEST_FOR_LARGE_SOURCES",
          "failure_modes": [
            "REJECT_MODALITY_WITHOUT_ADAPTER_CONTRACT",
            "REJECT_PROJECTION_REPLACES_SOURCE",
            "REJECT_LOSSY_PROJECTION_UNMARKED",
            "REJECT_ADAPTER_PRIVATE_TRUTH_PIPELINE"
          ],
          "input_schema": "HHS_MODALITY_SOURCE_COMMITMENT_V1",
          "loss_profile": "MIXED_LOSSLESS_AND_LOSSY",
          "loss_profile_record": {
            "loss_profile": "MIXED_LOSSLESS_AND_LOSSY",
            "loss_profile_hash72": "Gpwxs)p(SX<8f5RrnSw<E07ZQxJvaR?TMNAJ4glXGfW6H-!UXA9D5OhtzM8xNj+iq4pt<)rt",
            "lossy_outputs_must_be_marked": true,
            "lossy_projection_possible": true,
            "modality": "PDF",
            "projection_replaces_source": false,
            "schema": "HHS_MODALITY_LOSS_PROFILE_V1",
            "source_preserved": true,
            "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
          },
          "metadata_policy": "BOUNDED_TEMPORARY_EXPANDED_METADATA_COMPACTS_TO_RESIDUE",
          "output_projection_types": [
            "TEXT_PROJECTION",
            "PAGE_IMAGE_PROJECTION",
            "STRUCTURE_PROJECTION"
          ],
          "private_truth_pipeline_allowed": false,
          "projection_replaces_source": false,
          "reconstruction_strategy": "SOURCE_ROOT_PLUS_PROJECTION_RECIPE_PLUS_ARTIFACT_LINEAGE",
          "schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_V1",
          "source_modality": "PDF",
          "source_preserved": true,
          "supported_modalities": [
            "PDF"
          ],
          "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1",
          "witness_strategy": "HASH72_U72_SOURCE_PROJECTION_ARTIFACT_WITNESS_CHAIN"
        },
        "adapter_validation": {
          "adapter_id": "adapter:pdf.universal_modality",
          "ok": true,
          "reasons": [],
          "schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_VALIDATION_V1",
          "source_modality": "PDF",
          "status": "ADMIT_UNIVERSAL_MODALITY_ADAPTER",
          "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
        },
        "ok": true,
        "schema": "HHS_UNIVERSAL_MODALITY_ADAPTATION_RESULT_V1",
        "source_commitment": {
          "authority": "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1",
          "created_at_unix_ms": 1783809205981,
          "modality": "PDF",
          "payload_commitment_hash72": "?k(rTflSrakdf1tB>ZEL!Pe<OtsY>iw?bRpCrTZsRdbaxDI1-J565FWGY*bA*xP(t4V2?)(v",
          "project_id": "project:pass050",
          "projection_replaces_source": false,
          "schema": "HHS_MODALITY_SOURCE_COMMITMENT_V1",
          "source_commitment_id": "source:ed97ab64cf3d4c078f6cb985fea5e396",
          "source_name": "paper.pdf",
          "source_preserved": true,
          "source_root_hash72": "V-b<oVrCYejcHdn716Bab0RzdkCGT0StG(t-ia>RMD9zYWq+iZ(0lMXU<*lrv<9dPYgf?1J5",
          "source_size_bytes": 4,
          "source_uri": "workspace://project:pass050/source/paper.pdf",
          "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
        },
        "source_never_replaced_by_projection": true,
        "source_validation": {
          "ok": true,
          "reasons": [],
          "schema": "HHS_MODALITY_SOURCE_COMMITMENT_VALIDATION_V1",
          "source_commitment_id": "source:ed97ab64cf3d4c078f6cb985fea5e396",
          "source_root_hash72": "V-b<oVrCYejcHdn716Bab0RzdkCGT0StG(t-ia>RMD9zYWq+iZ(0lMXU<*lrv<9dPYgf?1J5",
          "status": "ADMIT_MODALITY_SOURCE_COMMITMENT",
          "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
        },
        "status": "ADMIT_UNIVERSAL_MODALITY_ADAPTATION",
        "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
      },
      "artifact": {
        "artifact_execution_authority_inferred": false,
        "artifact_id": "artifact:fa842a00f11443769d6863bbd073d210",
        "artifact_payload_hash72": "FNefPrZXB7N9YSQKjExoBJTC6w027nBRlJr141cOyg0qMyk!Mj>Re((1SzL/JBoWnTbMs5Ws",
        "artifact_root_hash72": "9Z!8->/B?jj!NlbYuHfzLiWnwhwJRp?jVmyf3lOpvIcGT9YueZe69v<+4B+FbTxbaouO+3pk",
        "artifact_type": "PDF_TEXT_HHS_SOURCE_DRAFT",
        "authority": "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1",
        "conformance_status": "ADMIT_DERIVED_ARTIFACT",
        "created_at_unix_ms": 1783809205991,
        "execution_authorized": false,
        "projection_root_hash72s": [
          "DaA/yVnwBFfWVJIPTYFsg8WhfjdFeEoI-J4>r?Gc/<UhWQlMr+Jqp2YN78STGi7!fI4mnQd7"
        ],
        "reconstruction_recipe": {
          "artifact_root_hash72": "",
          "authority": "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1",
          "expanded_metadata_retained": false,
          "operations": [
            {
              "operation": "DERIVE_ARTIFACT",
              "target_artifact_type": "PDF_TEXT_HHS_SOURCE_DRAFT",
              "target_modality": "HARMONICODE_SOURCE"
            }
          ],
          "projection_roots": [
            "DaA/yVnwBFfWVJIPTYFsg8WhfjdFeEoI-J4>r?Gc/<UhWQlMr+Jqp2YN78STGi7!fI4mnQd7"
          ],
          "recipe_id": "modality-recipe:7b72337d157
```
