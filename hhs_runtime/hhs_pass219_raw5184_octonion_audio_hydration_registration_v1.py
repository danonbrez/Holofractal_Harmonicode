"""Pass 219 I148 raw-5184 octonion/PCM64 serialization guard registration."""

from __future__ import annotations

from typing import Any, Dict

VERSION = "PASS_219_I148_RAW5184_OCTONION_AUDIO_HYDRATION_1_0"
SCHEMA = "HHS_PASS219_RAW5184_OCTONION_AUDIO_HYDRATION_V1"
SURFACE_ID = "guard:pass219.raw5184.octonion_audio_hydration"
MANDATORY_GUARD = "pass219_raw5184_octonion_audio_hydration"
PIPELINE_SYMBOL = "hhs_exact_pass219_audio5184_pipeline"
HYDRATE_SYMBOL = "hhs_exact_pass219_audio5184_hydrate"
VALIDATE_SYMBOL = "hhs_exact_pass219_audio5184_hydration_validate"
BIT_IMPORT_SYMBOL = "hhs_exact_pass219_audio5184_bitstring_import"
BIT_EXPORT_SYMBOL = "hhs_exact_pass219_audio5184_bitstring_export"
PCM_TO_FRAME_SYMBOL = "hhs_exact_pass219_audio5184_pcm64_to_frame"
FRAME_TO_PCM_SYMBOL = "hhs_exact_pass219_audio5184_frame_to_pcm64"


def surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "GUARD",
        "module": "hhs_runtime_exact_abi",
        "symbol": PIPELINE_SYMBOL,
        "contract_schemas": [SCHEMA],
        "validators": [
            BIT_IMPORT_SYMBOL,
            BIT_EXPORT_SYMBOL,
            FRAME_TO_PCM_SYMBOL,
            PCM_TO_FRAME_SYMBOL,
            HYDRATE_SYMBOL,
            VALIDATE_SYMBOL,
            PIPELINE_SYMBOL,
        ],
        "guards": [
            "exact_5184_symbol_lsb0_serialization",
            "exact_648_byte_little_endian_roundtrip",
            "exact_pcm64_bit_identity",
            "twenty_ordered_xyzw_dual_stereo_quads",
            "cell80_pilot_identity",
            "ordered_octonion_xy_yx_zw_wz",
            "ternary_h36_phase_reconstruction",
            "integer_only_pcm64_monitor_projection",
            "no_pcm_carrier_normalization_or_clipping",
            "no_new_vm81_hash72_hash216_authority",
        ],
        "rejection_codes": [
            "REJECT_RAW5184_LENGTH",
            "REJECT_RAW5184_NONBINARY_CHARACTER",
            "REJECT_RAW5184_ENDIAN_DRIFT",
            "REJECT_RAW5184_BIT_LOSS",
            "REJECT_AUDIO_DUAL_STEREO_ORDER_DRIFT",
            "REJECT_AUDIO_ORDERED_OCTONION_COLLAPSE",
            "REJECT_AUDIO_TERNARY_H36_RECONSTRUCTION_DRIFT",
            "REJECT_AUDIO_PILOT_SUBSTITUTION",
            "REJECT_AUDIO_PCM64_CARRIER_NORMALIZATION",
            "REJECT_AUDIO_FLOAT_CANONICAL_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "WITNESS_AND_REVERSIBLE_TRANSPORT_ONLY",
        "declared_operations": [PIPELINE_SYMBOL],
    }


def manifest() -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "surface_id": SURFACE_ID,
        "mandatory_guard": MANDATORY_GUARD,
        "raw": {
            "bits": 5184,
            "bytes": 648,
            "bit_order": "LSB0_PER_UINT64_CELL",
            "cell_order": "ASCENDING_0_TO_80",
            "byte_order": "LITTLE_ENDIAN",
        },
        "pcm64": {
            "samples_per_superframe": 81,
            "bits_per_sample": 64,
            "carrier_is_bit_preserving": True,
            "carrier_is_normalized": False,
        },
        "phase": {
            "quad_count": 20,
            "quad_cells": "4q+[0,1,2,3]",
            "dual_stereo": {"A": ["x", "y"], "B": ["z", "w"]},
            "ordered_channels": ["x", "y", "z", "w", "xy", "yx", "zw", "wz"],
            "pilot_cell": 80,
        },
        "ternary_h36": {
            "trit": "(phase72 mod 3)-1",
            "resonance36": "phase72 mod 36",
            "half_turn": "floor(phase72/36)",
            "reconstruction": "resonance36+36*half_turn",
            "monitor_pcm64": "signed_phase*2^56+trit*2^48",
        },
        "canonical_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }


__all__ = [
    "VERSION", "SCHEMA", "SURFACE_ID", "MANDATORY_GUARD", "PIPELINE_SYMBOL",
    "HYDRATE_SYMBOL", "VALIDATE_SYMBOL", "BIT_IMPORT_SYMBOL",
    "BIT_EXPORT_SYMBOL", "PCM_TO_FRAME_SYMBOL", "FRAME_TO_PCM_SYMBOL",
    "surface_declaration", "manifest",
]
