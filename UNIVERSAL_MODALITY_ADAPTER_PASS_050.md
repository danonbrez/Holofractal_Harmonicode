# UNIVERSAL MODALITY ADAPTER PASS 050

Status: `True`

Schema: `HHS_UNIVERSAL_MODALITY_ADAPTER_SELF_TEST_V1`

```json
{
  "adapter_count": 18,
  "doctrine": "NO_MODALITY_OWNS_A_PRIVATE_TRUTH_PIPELINE",
  "image_adaptation": {
    "adaptation_root_hash72": "NQGNHX+29YhIRGr43+f<adlc7dUYv-ZW)<zAZrLVB5/zKJLcY>)xp1(xwS4e2XTD/pt<XE3M",
    "adapter_contract": {
      "adapter_contract_hash72": "WPZwWFTeMz7mtkG>WBr3c/i??PsK75epPX>Bm!veBM/LGlN+<mvY!<!+>z5fqRO/o8B98dPT",
      "adapter_id": "adapter:image.universal_modality",
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
        "loss_profile_hash72": "ycfqEry2>p7)b6zkyQCuDEOC-pKLmB0F(3I!lztrgQLvolwfc4yJW4?7YGdIhz>+Z?nHkE7F",
        "lossy_outputs_must_be_marked": true,
        "lossy_projection_possible": true,
        "modality": "IMAGE",
        "projection_replaces_source": false,
        "schema": "HHS_MODALITY_LOSS_PROFILE_V1",
        "source_preserved": true,
        "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
      },
      "metadata_policy": "BOUNDED_TEMPORARY_EXPANDED_METADATA_COMPACTS_TO_RESIDUE",
      "output_projection_types": [
        "RASTER_PROJECTION",
        "VISUAL_FEATURE_PROJECTION",
        "OCR_TEXT_PROJECTION"
      ],
      "private_truth_pipeline_allowed": false,
      "projection_replaces_source": false,
      "reconstruction_strategy": "SOURCE_ROOT_PLUS_PROJECTION_RECIPE_PLUS_ARTIFACT_LINEAGE",
      "schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_V1",
      "source_modality": "IMAGE",
      "source_preserved": true,
      "supported_modalities": [
        "IMAGE"
      ],
      "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1",
      "witness_strategy": "HASH72_U72_SOURCE_PROJECTION_ARTIFACT_WITNESS_CHAIN"
    },
    "adapter_validation": {
      "adapter_id": "adapter:image.universal_modality",
      "ok": true,
      "reasons": [],
      "schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_VALIDATION_V1",
      "source_modality": "IMAGE",
      "status": "ADMIT_UNIVERSAL_MODALITY_ADAPTER",
      "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
    },
    "ok": true,
    "schema": "HHS_UNIVERSAL_MODALITY_ADAPTATION_RESULT_V1",
    "source_commitment": {
      "authority": "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1",
      "created_at_unix_ms": 1783809205880,
      "modality": "IMAGE",
      "payload_commitment_hash72": "<1w<!43u>epff!aEtW7//Po5qN91XrISjwRdLGG4np1y4HONK9/-rD7HYI-(dCB-Wt5W30<v",
      "project_id": "project:pass050",
      "projection_replaces_source": false,
      "schema": "HHS_MODALITY_SOURCE_COMMITMENT_V1",
      "source_commitment_id": "source:4375c096672649f1a161d02e0961391f",
      "source_name": "glyph.png",
      "source_preserved": true,
      "source_root_hash72": "nwwFB?GwJ+*jZ<CM!MTRheZMj!UzW/K-Bh3Lpev68<zI)k1AMbITzTcWA7k2X+cOH1C4IFT+",
      "source_size_bytes": 3,
      "source_uri": "workspace://project:pass050/source/glyph.png",
      "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
    },
    "source_never_replaced_by_projection": true,
    "source_validation": {
      "ok": true,
      "reasons": [],
      "schema": "HHS_MODALITY_SOURCE_COMMITMENT_VALIDATION_V1",
      "source_commitment_id": "source:4375c096672649f1a161d02e0961391f",
      "source_root_hash72": "nwwFB?GwJ+*jZ<CM!MTRheZMj!UzW/K-Bh3Lpev68<zI)k1AMbITzTcWA7k2X+cOH1C4IFT+",
      "status": "ADMIT_MODALITY_SOURCE_COMMITMENT",
      "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
    },
    "status": "ADMIT_UNIVERSAL_MODALITY_ADAPTATION",
    "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
  },
  "modalities": [
    "TEXT",
    "HARMONICODE_SOURCE",
    "CODE",
    "JSON",
    "YAML",
    "CSV",
    "PDF",
    "IMAGE",
    "AUDIO",
    "VIDEO",
    "BINARY",
    "DIRECTORY",
    "RUNTIME_RECEIPT",
    "LEDGER_FRAGMENT",
    "SEMANTIC_MEMORY_OBJECT",
    "GRAPH_OBJECT",
    "COMPILED_ARTIFACT",
    "EMULATOR_STATE"
  ],
  "ok": true,
  "private_truth_pipeline_rejection": {
    "adapter_id": "adapter:text.universal_modality",
    "ok": false,
    "reasons": [
      "REJECT_ADAPTER_PRIVATE_TRUTH_PIPELINE"
    ],
    "schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_VALIDATION_V1",
    "source_modality": "TEXT",
    "status": "REJECT_UNIVERSAL_MODALITY_ADAPTER",
    "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
  },
  "schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_SELF_TEST_V1",
  "version": "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
}
```
