# ADAPTER CAPABILITY MAP PASS 050

Status: `True`

Schema: `HHS_ADAPTER_CAPABILITY_MAP_SELF_TEST_V1`

```json
{
  "capability_map": {
    "adapter_count": 18,
    "adapter_ids": [
      "adapter:text.universal_modality",
      "adapter:harmonicode_source.universal_modality",
      "adapter:code.universal_modality",
      "adapter:json.universal_modality",
      "adapter:yaml.universal_modality",
      "adapter:csv.universal_modality",
      "adapter:pdf.universal_modality",
      "adapter:image.universal_modality",
      "adapter:audio.universal_modality",
      "adapter:video.universal_modality",
      "adapter:binary.universal_modality",
      "adapter:directory.universal_modality",
      "adapter:runtime_receipt.universal_modality",
      "adapter:ledger_fragment.universal_modality",
      "adapter:semantic_memory_object.universal_modality",
      "adapter:graph_object.universal_modality",
      "adapter:compiled_artifact.universal_modality",
      "adapter:emulator_state.universal_modality"
    ],
    "authority": "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1",
    "capabilities_by_modality": {
      "AUDIO": {
        "adapter_id": "adapter:audio.universal_modality",
        "loss_profile": "MIXED_LOSSLESS_AND_LOSSY",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "WAVEFORM_PROJECTION",
          "TRANSCRIPT_PROJECTION",
          "HARMONIC_TIME_PROJECTION"
        ],
        "source_preserved": true
      },
      "BINARY": {
        "adapter_id": "adapter:binary.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "BYTE_MANIFEST_PROJECTION"
        ],
        "source_preserved": true
      },
      "CODE": {
        "adapter_id": "adapter:code.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "SOURCE_TEXT_PROJECTION",
          "LANGUAGE_AST_PROJECTION"
        ],
        "source_preserved": true
      },
      "COMPILED_ARTIFACT": {
        "adapter_id": "adapter:compiled_artifact.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "ARTIFACT_METADATA_PROJECTION",
          "IR_PROJECTION"
        ],
        "source_preserved": true
      },
      "CSV": {
        "adapter_id": "adapter:csv.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "TABLE_PROJECTION"
        ],
        "source_preserved": true
      },
      "DIRECTORY": {
        "adapter_id": "adapter:directory.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "DIRECTORY_MANIFEST_PROJECTION"
        ],
        "source_preserved": true
      },
      "EMULATOR_STATE": {
        "adapter_id": "adapter:emulator_state.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "STATE_REGISTER_PROJECTION",
          "REPLAY_TIMELINE_PROJECTION"
        ],
        "source_preserved": true
      },
      "GRAPH_OBJECT": {
        "adapter_id": "adapter:graph_object.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "GRAPH_TOPOLOGY_PROJECTION"
        ],
        "source_preserved": true
      },
      "HARMONICODE_SOURCE": {
        "adapter_id": "adapter:harmonicode_source.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "SOURCE_TEXT_PROJECTION",
          "SYMBOLIC_AST_PROJECTION",
          "HHS_GRAPH_PROJECTION"
        ],
        "source_preserved": true
      },
      "IMAGE": {
        "adapter_id": "adapter:image.universal_modality",
        "loss_profile": "MIXED_LOSSLESS_AND_LOSSY",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "RASTER_PROJECTION",
          "VISUAL_FEATURE_PROJECTION",
          "OCR_TEXT_PROJECTION"
        ],
        "source_preserved": true
      },
      "JSON": {
        "adapter_id": "adapter:json.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "STRUCTURE_PROJECTION",
          "CANONICAL_JSON_PROJECTION"
        ],
        "source_preserved": true
      },
      "LEDGER_FRAGMENT": {
        "adapter_id": "adapter:ledger_fragment.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "LEDGER_CHAIN_PROJECTION"
        ],
        "source_preserved": true
      },
      "PDF": {
        "adapter_id": "adapter:pdf.universal_modality",
        "loss_profile": "MIXED_LOSSLESS_AND_LOSSY",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "TEXT_PROJECTION",
          "PAGE_IMAGE_PROJECTION",
          "STRUCTURE_PROJECTION"
        ],
        "source_preserved": true
      },
      "RUNTIME_RECEIPT": {
        "adapter_id": "adapter:runtime_receipt.universal_modality",
        "loss_profile": "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "private_truth_pipeline_allowed": false,
        "projection_types": [
          "RECEIPT_FIELD_PROJECTION"
        ],
        "source_preserved": true
      },
      "SEMANTIC_MEMORY_OBJECT": 
```
