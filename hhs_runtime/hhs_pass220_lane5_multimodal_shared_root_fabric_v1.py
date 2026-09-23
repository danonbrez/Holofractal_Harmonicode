"""Pass 220 I042: Lane 5 multimodal shared-root projection fabric.

I042 binds language, image, audio, video, physics, and game projections to one
exact execution ancestry.  Every modality is represented by:

- immutable source bytes;
- deterministic Pass165 token/chunk graph;
- one exact 5,184-bit projection;
- one Hash72 projection witness;
- one ordered Hash216 genome root;
- the I041 exact game-engine root;
- the I040 relativistic observation root;
- the I039 shared quantum/relativistic root.

The exact root metadata seed 179971.179971 and exact 1.001 invariant gate are
bound as rationals.  No modality may replace the common root with a local model
identity.

Language carries exact token identities and a Pass166/Pass218 relational
candidate contract descriptor.  A live Word2Vec model is not silently required
or fabricated by I042; where present, Pass166 relations remain revisable
candidate evidence.

Image, audio, video, physics and game projections are deterministic egress
views of the same exact root.  Cross-modal translation is therefore an exact
root-preserving graph operation rather than a second inference authority.

This constructor is candidate/read-only.  It never commits VM81, mints
canonical Hash72/Hash216 state, updates model weights, or persists canonical
knowledge.
"""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass150.genome import Hash216Genome
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES
from hhs_runtime.pass165.ingestion import (
    MultimodalLearningService,
    MultimodalTokenizer,
    SourceObject,
    detect_modality,
)
from hhs_runtime.hhs_pass220_holofractal_relativistic_game_engine_v1 import (
    build_game_engine_cycle,
    build_relativistic_game_frame,
    holofractal_relativistic_game_engine_witness,
)
from hhs_runtime.hhs_pass220_desi_explicit_projection_corpus_v1 import (
    build_desi_explicit_projection,
    public_desi_dr2_lya_row,
    validate_desi_explicit_projection,
)

SCHEMA = "HHS_PASS_220_I042_LANE5_MULTIMODAL_SHARED_ROOT_FABRIC_V1"
VERSION = "1.0.0-checkpoint.42"
PROFILE = "PASS220-I042-LANE5-MULTIMODAL-SHARED-ROOT-FABRIC-v1"
PROJECTION_SCHEMA = "HHS_PASS_220_I042_MODALITY_PROJECTION_V1"
GRAPH_SCHEMA = "HHS_PASS_220_I042_MULTIMODAL_KNOWLEDGE_GRAPH_V1"
TRANSLATION_SCHEMA = "HHS_PASS_220_I042_CROSS_MODAL_TRANSLATION_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I042_MULTIMODAL_SHARED_ROOT_WITNESS_V1"

ROOT_METADATA_SEED_TEXT = "179971.179971"
ROOT_METADATA_SEED = Fraction(179971179971, 1000000)
INVARIANT_GATE_TEXT = "1.001"
INVARIANT_GATE = Fraction(1001, 1000)

MODALITIES: Tuple[str, ...] = (
    "LANGUAGE",
    "IMAGE",
    "AUDIO",
    "VIDEO",
    "PHYSICS",
    "GAME",
)

PASS166_LANGUAGE_CONTRACT = (
    "HHS_PASS_166_WORD2VEC_LANGUAGE_MODALITY_MODEL_"
    "ACQUISITION_IMPORT_PREINSTALLATION_AND_OFFLINE_ACTIVATION"
)
PASS218_RELATIONAL_SEMANTICS = "REVISABLE_RELATIONAL_EVIDENCE"

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "ONE_EXACT_ROOT_FOR_ALL_MODALITIES",
    "ROOT_METADATA_SEED_179971_179971_EXACT_RATIONAL",
    "INVARIANT_GATE_1_001_EXACT_RATIONAL",
    "EVERY_MODALITY_HAS_EXACT_5184_BIT_PROJECTION",
    "EVERY_MODALITY_HAS_HASH72_WITNESS",
    "EVERY_MODALITY_HAS_ORDERED_HASH216_GENOME_ROOT",
    "LANGUAGE_USES_EXACT_TOKEN_IDENTITIES",
    "PASS166_RELATIONS_REMAIN_REVISABLE_CANDIDATES",
    "IMAGE_BINDS_SPRITE216_AND_Q144_COLOR",
    "AUDIO_BINDS_H36_AND_EXACT_3_TO_2_POLYRHYTHM",
    "VIDEO_BINDS_EXACT_Q144_FRAME_TIMELINE",
    "PHYSICS_BINDS_I040_RELATIVISTIC_PROJECTION",
    "GAME_BINDS_I041_EXACT_FRAME",
    "CROSS_MODAL_TRANSLATION_PRESERVES_SHARED_ROOT",
    "CROSS_MODAL_TRANSLATION_PRESERVES_SOURCE_AND_TARGET_PROVENANCE",
    "NO_MODALITY_LOCAL_ROOT_CAN_REPLACE_SHARED_ROOT",
    "NO_HOST_FLOAT_IN_EXACT_MULTIMODAL_STATE",
    "NO_PROBABILITY_LIKELIHOOD_MCMC_REFIT",
    "NO_CANONICAL_VM81_HASH_OR_WEIGHT_AUTHORITY",
)


class Pass220I042MultimodalError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _canonical_bytes(value: Any) -> bytes:
    return _stable_json(value).encode("utf-8")


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(_canonical_bytes(record)).hexdigest()
    return record


def _receipt_matches(record: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in record:
        return False
    body = dict(record)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_canonical_bytes(body)).hexdigest()


def _fraction_record(value: Fraction) -> Dict[str, int]:
    q = Fraction(value)
    return {"numerator": q.numerator, "denominator": q.denominator}


def _hash72(domain: str, payload: Any) -> str:
    return hash72_digest({"domain": domain, "pass": 220, "iteration": 42}, payload)


@lru_cache(maxsize=1)
def _validated_i041() -> Dict[str, Any]:
    witness = holofractal_relativistic_game_engine_witness()
    if witness.get("ok") is not True:
        raise Pass220I042MultimodalError("I041 game-engine witness did not close")
    result = witness.get("result")
    if not isinstance(result, Mapping) or result.get("exact_cycle_closed") is not True:
        raise Pass220I042MultimodalError("I041 exact game-engine cycle open")
    return witness


@lru_cache(maxsize=1)
def _validated_i040() -> Dict[str, Any]:
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    result = validate_desi_explicit_projection(projection)
    if result.get("ok") is not True or result.get("u_data_close") is not True:
        raise Pass220I042MultimodalError("I040 DESI projection did not close")
    return projection


def shared_multimodal_root_payload() -> Dict[str, Any]:
    i041 = _validated_i041()
    i040 = _validated_i040()
    return {
        "schema": "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1",
        "root_metadata_seed": _fraction_record(ROOT_METADATA_SEED),
        "invariant_gate": _fraction_record(INVARIANT_GATE),
        "i041_cycle_receipt_sha256": i041["cycle_receipt_sha256"],
        "i041_relativistic_projection_root_sha256": i041["result"][
            "shared_relativistic_projection_root_sha256"
        ],
        "i041_i039_shared_root_sha256": i041["result"][
            "shared_i039_root_sha256"
        ],
        "i040_projection_root_sha256": i040["projection_root_sha256"],
        "i040_i039_shared_root_sha256": i040[
            "i039_shared_state_root_sha256"
        ],
        "coordinate_closure": {
            "vm81x64": 81 * 64,
            "hash72_square": 72 * 72,
            "q144xh36": 144 * 36,
        },
    }


def shared_multimodal_root_sha256() -> str:
    payload = shared_multimodal_root_payload()
    if (
        payload["i041_relativistic_projection_root_sha256"]
        != payload["i040_projection_root_sha256"]
    ):
        raise Pass220I042MultimodalError("I041/I040 projection root split")
    if (
        payload["i041_i039_shared_root_sha256"]
        != payload["i040_i039_shared_root_sha256"]
    ):
        raise Pass220I042MultimodalError("I041/I040 I039 root split")
    if set(payload["coordinate_closure"].values()) != {COORDINATES}:
        raise Pass220I042MultimodalError("5,184 coordinate closure split")
    return sha256(_canonical_bytes(payload)).hexdigest()


def _source_object(
    *,
    modality_role: str,
    source_bytes: bytes,
    declared_media_type: str,
    provenance: str,
) -> SourceObject:
    if modality_role not in MODALITIES:
        raise Pass220I042MultimodalError("unsupported modality role")
    if not isinstance(source_bytes, (bytes, bytearray, memoryview)):
        raise Pass220I042MultimodalError("source bytes required")
    raw = bytes(source_bytes)
    if not raw:
        raise Pass220I042MultimodalError("source bytes may not be empty")
    detected = detect_modality(raw, declared_media_type)
    source_hash = sha256(raw).hexdigest()
    source_id = sha256(
        _canonical_bytes({
            "domain": "HHS_PASS_220_I042_SOURCE_ID_V1",
            "modality_role": modality_role,
            "declared_media_type": declared_media_type,
            "detected_media_type": detected,
            "source_hash": source_hash,
            "provenance": provenance,
        })
    ).hexdigest()
    return SourceObject(
        source_id=source_id,
        source_hash=source_hash,
        source_bytes=raw,
        declared_media_type=declared_media_type,
        detected_media_type=detected,
        byte_length=len(raw),
        provenance=provenance,
        authorization_scope="PASS220_I042_READ_ONLY_PROJECTION",
        ingestion_epoch=0,
    )


def _projection_from_source(
    *,
    modality_role: str,
    source_bytes: bytes,
    declared_media_type: str,
    provenance: str,
    semantic_binding: Mapping[str, Any],
) -> Dict[str, Any]:
    source = _source_object(
        modality_role=modality_role,
        source_bytes=source_bytes,
        declared_media_type=declared_media_type,
        provenance=provenance,
    )
    tokenizer = MultimodalTokenizer()
    tokens = tokenizer.tokenize(source)
    chunks, edges = MultimodalLearningService.chunk_tokens(tokens)
    snapshot = MultimodalLearningService.project_5184(tokens, edges)
    projection_bytes = snapshot.to_bytes()
    if len(projection_bytes) != SNAPSHOT_BYTES:
        raise Pass220I042MultimodalError("5,184-bit projection byte length drift")

    shared_root = shared_multimodal_root_sha256()
    projection_hash72 = _hash72(
        "HHS_PASS_220_I042_MODALITY_PROJECTION_HASH72_V1",
        {
            "shared_root_sha256": shared_root,
            "modality_role": modality_role,
            "source_hash": source.source_hash,
            "projection_sha256": sha256(projection_bytes).hexdigest(),
        },
    )
    genome_payload = _canonical_bytes({
        "shared_root_sha256": shared_root,
        "modality_role": modality_role,
        "source_hash": source.source_hash,
        "projection_sha256": sha256(projection_bytes).hexdigest(),
        "semantic_binding": dict(semantic_binding),
    })
    positions = Hash216Genome.positions(
        genome_payload,
        previous_root=shared_root,
        sequence=MODALITIES.index(modality_role),
    )
    genome_root = Hash216Genome.root(positions)

    return _receipt({
        "schema": PROJECTION_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "modality_role": modality_role,
        "source": source.summary(),
        "token_count": len(tokens),
        "token_ids": tuple(token.token_id for token in tokens),
        "token_classes": tuple(token.token_class for token in tokens),
        "chunk_count": len(chunks),
        "chunk_ids": tuple(chunk.chunk_id for chunk in chunks),
        "graph_edge_count": len(edges),
        "graph_edges": tuple(edges),
        "projection_bits": COORDINATES,
        "projection_bytes": SNAPSHOT_BYTES,
        "projection_sha256": sha256(projection_bytes).hexdigest(),
        "projection_base64": snapshot.base64(),
        "projection_popcount": sum(
            byte.bit_count() for byte in projection_bytes
        ),
        "projection_hash72": projection_hash72,
        "hash216_position_count": len(positions),
        "hash216_positions": positions,
        "hash216_genome_root_sha256": genome_root,
        "shared_multimodal_root_sha256": shared_root,
        "semantic_binding": dict(semantic_binding),
        "source_bytes_retained_in_projection_record": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_learning_commit_authority": False,
        "model_weight_update_authority": False,
        "direct_canonical_persistence_authority": False,
        "host_float_arithmetic_used": False,
        "probability_used": False,
        "likelihood_used": False,
        "mcmc_used": False,
        "parameter_refit_performed": False,
    })


def _language_payload(frame: Mapping[str, Any]) -> bytes:
    physics = frame["relativistic_physics"]
    statement = (
        "HARMONICODE multimodal shared-root frame; "
        f"tick={frame['tick']}; "
        f"q144={frame['q144']['q144_index']}; "
        f"platonic={frame['platonic_solid']['name']}; "
        f"harmonic_rule={frame['h36_music']['harmonic_rule64']}; "
        f"z={physics['z_eff']['numerator']}/{physics['z_eff']['denominator']}; "
        f"projection_root={physics['i040_projection_root_sha256']}; "
        f"shared_root={physics['i039_shared_state_root_sha256']}."
    )
    return statement.encode("utf-8")


def _image_payload(frame: Mapping[str, Any]) -> bytes:
    # P165 recognizes PNG by its exact signature. The remaining bytes are an
    # immutable descriptor payload, not a claim to be a fully encoded PNG.
    body = _canonical_bytes({
        "sprite216": frame["holofractal_sprite216"]["sprite216"],
        "q144": frame["q144"]["q144_index"],
        "color_q144": frame["color_wheel"]["q144_index"],
        "reciprocal_color_q144": frame["color_wheel"]["reciprocal_q144"],
        "platonic": frame["platonic_solid"]["name"],
        "shader_receipt": frame["shader_ir"]["receipt_sha256"],
    })
    return b"\x89PNG\r\n\x1a\n" + body


def _audio_payload(frame: Mapping[str, Any]) -> bytes:
    body = _canonical_bytes({
        "q144": frame["q144"]["q144_index"],
        "h36_coordinate": frame["h36_music"]["coordinate"],
        "equal_temperament": frame["h36_music"]["equal_temperament"],
        "harmonic_rule64": frame["h36_music"]["harmonic_rule64"],
        "polyrhythm_3_to_2": {
            "ratio": {"numerator": 3, "denominator": 2},
            "cycle_ticks": 144,
            "three_pulse_ticks": (0, 48, 96),
            "two_pulse_ticks": (0, 72),
        },
    })
    return b"RIFF" + len(body).to_bytes(4, "little") + b"WAVE" + body


def _video_payload(frame: Mapping[str, Any]) -> bytes:
    body = _canonical_bytes({
        "timeline": {
            "q144_frame_count": 144,
            "frame_indices": tuple(range(144)),
            "exact_clock": "n/144 turns",
        },
        "source_frame_receipt": frame["receipt_sha256"],
        "sprite_geometry_seed": frame["holofractal_sprite216"]["geometry_seed"],
        "shader_receipt": frame["shader_ir"]["receipt_sha256"],
        "physics_projection_root": frame["relativistic_physics"][
            "i040_projection_root_sha256"
        ],
    })
    # P165 VIDEO detection checks bytes[4:12] for b"ftypisom".
    return b"\x00\x00\x00\x18" + b"ftypisom" + body


def _physics_payload(frame: Mapping[str, Any]) -> bytes:
    return _canonical_bytes({
        "schema": "HHS_PASS_220_I042_PHYSICS_VIEW_V1",
        "relativistic_physics": frame["relativistic_physics"],
        "euclidean_trig": frame["euclidean_trig"],
        "platonic_solid": frame["platonic_solid"],
        "typed_closure": {
            "delta_e": 0,
            "psi": 0,
            "omega": True,
        },
    })


def _game_payload(frame: Mapping[str, Any]) -> bytes:
    return _canonical_bytes({
        "schema": "HHS_PASS_220_I042_GAME_VIEW_V1",
        "tick": frame["tick"],
        "q144": frame["q144"],
        "h36_music": frame["h36_music"],
        "color_wheel": frame["color_wheel"],
        "platonic_solid": frame["platonic_solid"],
        "sprite216_receipt": frame["holofractal_sprite216"]["receipt_sha256"],
        "shader_ir_receipt": frame["shader_ir"]["receipt_sha256"],
        "relativistic_projection_root": frame["relativistic_physics"][
            "i040_projection_root_sha256"
        ],
    })


def build_language_projection(frame: Mapping[str, Any]) -> Dict[str, Any]:
    return _projection_from_source(
        modality_role="LANGUAGE",
        source_bytes=_language_payload(frame),
        declared_media_type="TEXT",
        provenance="I041_GAME_FRAME_TO_LANGUAGE_EXACT_DESCRIPTOR",
        semantic_binding={
            "grammar_surface": "ORDERED_TOKEN_GRAPH",
            "pass166_contract": PASS166_LANGUAGE_CONTRACT,
            "pass218_candidate_semantics": PASS218_RELATIONAL_SEMANTICS,
            "word2vec_live_model_required_for_i042_closure": False,
            "word2vec_candidate_truth_authority": False,
            "language_output_root": frame["receipt_sha256"],
        },
    )


def build_image_projection(frame: Mapping[str, Any]) -> Dict[str, Any]:
    return _projection_from_source(
        modality_role="IMAGE",
        source_bytes=_image_payload(frame),
        declared_media_type="IMAGE",
        provenance="I041_SPRITE216_Q144_COLOR_SHADER_IMAGE_PROJECTION",
        semantic_binding={
            "sprite216_receipt": frame["holofractal_sprite216"]["receipt_sha256"],
            "sprite_geometry_seed": frame["holofractal_sprite216"]["geometry_seed"],
            "color_q144": frame["color_wheel"]["q144_index"],
            "reciprocal_color_q144": frame["color_wheel"]["reciprocal_q144"],
            "shader_ir_receipt": frame["shader_ir"]["receipt_sha256"],
            "render_backend_is_projection_only": True,
        },
    )


def build_audio_projection(frame: Mapping[str, Any]) -> Dict[str, Any]:
    return _projection_from_source(
        modality_role="AUDIO",
        source_bytes=_audio_payload(frame),
        declared_media_type="AUDIO",
        provenance="I041_H36_Q144_EXACT_AUDIO_EVENT_PROJECTION",
        semantic_binding={
            "h36_music_receipt": frame["h36_music"]["receipt_sha256"],
            "q144_index": frame["q144"]["q144_index"],
            "polyrhythm_ratio": {"numerator": 3, "denominator": 2},
            "three_pulse_ticks": (0, 48, 96),
            "two_pulse_ticks": (0, 72),
            "audio_clock_is_exact": True,
            "pcm_device_output_is_projection_only": True,
        },
    )


def build_video_projection(frame: Mapping[str, Any]) -> Dict[str, Any]:
    return _projection_from_source(
        modality_role="VIDEO",
        source_bytes=_video_payload(frame),
        declared_media_type="VIDEO",
        provenance="I041_Q144_EXACT_FRAME_TIMELINE_VIDEO_PROJECTION",
        semantic_binding={
            "q144_frame_count": 144,
            "frame_clock": "n/144 turns",
            "source_frame_receipt": frame["receipt_sha256"],
            "shader_ir_receipt": frame["shader_ir"]["receipt_sha256"],
            "video_codec_output_is_projection_only": True,
        },
    )


def build_physics_projection(frame: Mapping[str, Any]) -> Dict[str, Any]:
    return _projection_from_source(
        modality_role="PHYSICS",
        source_bytes=_physics_payload(frame),
        declared_media_type="JSON",
        provenance="I040_I041_EXACT_PHYSICS_PROJECTION",
        semantic_binding={
            "i040_projection_root_sha256": frame["relativistic_physics"][
                "i040_projection_root_sha256"
            ],
            "i039_shared_state_root_sha256": frame["relativistic_physics"][
                "i039_shared_state_root_sha256"
            ],
            "u_data_close": frame["relativistic_physics"]["u_data_close"],
            "delta_e": 0,
            "psi": 0,
            "omega": True,
        },
    )


def build_game_projection(frame: Mapping[str, Any]) -> Dict[str, Any]:
    return _projection_from_source(
        modality_role="GAME",
        source_bytes=_game_payload(frame),
        declared_media_type="JSON",
        provenance="I041_EXACT_GAME_FRAME_PROJECTION",
        semantic_binding={
            "game_frame_receipt": frame["receipt_sha256"],
            "same_q144_drives_trig_music_color_shader": frame[
                "same_q144_drives_trig_music_color_shader"
            ],
            "game_state_is_exact": frame["game_state_is_exact"],
            "rendering_is_projection": frame["rendering_is_projection"],
        },
    )


def build_multimodal_projection_set(
    *,
    tick: int = 0,
    bit36: int = 0,
    platonic_pair: Tuple[int, int] = (5, 3),
) -> Dict[str, Dict[str, Any]]:
    frame = build_relativistic_game_frame(
        tick,
        bit36=bit36,
        platonic_pair=platonic_pair,
    )
    projections = {
        "LANGUAGE": build_language_projection(frame),
        "IMAGE": build_image_projection(frame),
        "AUDIO": build_audio_projection(frame),
        "VIDEO": build_video_projection(frame),
        "PHYSICS": build_physics_projection(frame),
        "GAME": build_game_projection(frame),
    }
    if tuple(projections) != MODALITIES:
        raise Pass220I042MultimodalError("modality order drift")
    roots = {
        projection["shared_multimodal_root_sha256"]
        for projection in projections.values()
    }
    if roots != {shared_multimodal_root_sha256()}:
        raise Pass220I042MultimodalError("modality shared-root divergence")
    return projections


def cross_modal_translation(
    projections: Mapping[str, Mapping[str, Any]],
    *,
    source_modality: str,
    target_modality: str,
) -> Dict[str, Any]:
    if source_modality not in MODALITIES or target_modality not in MODALITIES:
        raise Pass220I042MultimodalError("unsupported translation modality")
    if source_modality == target_modality:
        raise Pass220I042MultimodalError("translation requires distinct modalities")
    if set(projections) != set(MODALITIES):
        raise Pass220I042MultimodalError("complete projection set required")

    source = projections[source_modality]
    target = projections[target_modality]
    shared_root = shared_multimodal_root_sha256()
    if source.get("shared_multimodal_root_sha256") != shared_root:
        raise Pass220I042MultimodalError("source projection root drift")
    if target.get("shared_multimodal_root_sha256") != shared_root:
        raise Pass220I042MultimodalError("target projection root drift")

    return _receipt({
        "schema": TRANSLATION_SCHEMA,
        "version": VERSION,
        "source_modality": source_modality,
        "target_modality": target_modality,
        "shared_multimodal_root_sha256": shared_root,
        "source_projection_receipt_sha256": source["receipt_sha256"],
        "source_projection_hash72": source["projection_hash72"],
        "source_hash216_genome_root_sha256": source[
            "hash216_genome_root_sha256"
        ],
        "target_projection_receipt_sha256": target["receipt_sha256"],
        "target_projection_hash72": target["projection_hash72"],
        "target_hash216_genome_root_sha256": target[
            "hash216_genome_root_sha256"
        ],
        "translation_rule": "COMMON_ROOT_PLUS_EXPLICIT_PROJECTION_RELATION",
        "source_provenance_preserved": True,
        "target_provenance_preserved": True,
        "semantic_guessing_required": False,
        "probability_used": False,
        "canonical_mutation_authority": False,
    })


def build_multimodal_knowledge_graph(
    *,
    tick: int = 0,
    bit36: int = 0,
    platonic_pair: Tuple[int, int] = (5, 3),
) -> Dict[str, Any]:
    projections = build_multimodal_projection_set(
        tick=tick,
        bit36=bit36,
        platonic_pair=platonic_pair,
    )
    shared_root = shared_multimodal_root_sha256()

    root_node = {
        "node_id": f"ROOT:{shared_root}",
        "node_type": "SHARED_EXACT_EXECUTION_ROOT",
        "shared_multimodal_root_sha256": shared_root,
        "root_metadata_seed": _fraction_record(ROOT_METADATA_SEED),
        "invariant_gate": _fraction_record(INVARIANT_GATE),
    }
    modality_nodes = tuple(
        {
            "node_id": f"{modality}:{projection['receipt_sha256']}",
            "node_type": "MODALITY_PROJECTION",
            "modality": modality,
            "projection_receipt_sha256": projection["receipt_sha256"],
            "projection_hash72": projection["projection_hash72"],
            "hash216_genome_root_sha256": projection[
                "hash216_genome_root_sha256"
            ],
            "shared_multimodal_root_sha256": shared_root,
        }
        for modality, projection in projections.items()
    )
    root_edges = tuple(
        {
            "edge_type": "PROJECTS_AS",
            "from_node": root_node["node_id"],
            "to_node": node["node_id"],
            "modality": node["modality"],
        }
        for node in modality_nodes
    )

    translations = tuple(
        cross_modal_translation(
            projections,
            source_modality=source,
            target_modality=target,
        )
        for source in MODALITIES
        for target in MODALITIES
        if source != target
    )
    translation_edges = tuple(
        {
            "edge_type": "ROOT_PRESERVING_TRANSLATION",
            "from_modality": translation["source_modality"],
            "to_modality": translation["target_modality"],
            "translation_receipt_sha256": translation["receipt_sha256"],
            "shared_multimodal_root_sha256": shared_root,
        }
        for translation in translations
    )

    projection_roots = {
        projection["shared_multimodal_root_sha256"]
        for projection in projections.values()
    }
    all_5184 = all(
        projection["projection_bits"] == 5184
        and projection["projection_bytes"] == 648
        for projection in projections.values()
    )
    all_hash216 = all(
        projection["hash216_position_count"] == 216
        and len(projection["hash216_positions"]) == 216
        for projection in projections.values()
    )

    return _receipt({
        "schema": GRAPH_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "shared_root_payload": shared_multimodal_root_payload(),
        "shared_multimodal_root_sha256": shared_root,
        "root_node": root_node,
        "modality_nodes": modality_nodes,
        "root_edges": root_edges,
        "translation_edges": translation_edges,
        "translation_receipts": translations,
        "projections": projections,
        "modality_count": len(MODALITIES),
        "root_edge_count": len(root_edges),
        "directed_cross_modal_translation_count": len(translations),
        "all_modalities_share_root": projection_roots == {shared_root},
        "all_modalities_have_5184_projection": all_5184,
        "all_modalities_have_hash216_genome": all_hash216,
        "language_candidate_contract": {
            "pass166_contract": PASS166_LANGUAGE_CONTRACT,
            "pass218_candidate_semantics": PASS218_RELATIONAL_SEMANTICS,
            "candidate_only": True,
            "truth_promotion": False,
            "canonical_learning_commit": False,
        },
        "lane5_role": "READ_ONLY_MULTIMODAL_PROJECTION_AND_ROUTING_FABRIC",
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
        "host_float_arithmetic_used": False,
        "probability_used": False,
        "likelihood_used": False,
        "mcmc_used": False,
        "parameter_refit_performed": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_learning_commit_authority": False,
        "model_weight_update_authority": False,
        "direct_canonical_persistence_authority": False,
    })


def validate_multimodal_knowledge_graph(
    graph: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(graph, Mapping):
        raise Pass220I042MultimodalError("graph must be a mapping")
    if graph.get("schema") != GRAPH_SCHEMA:
        raise Pass220I042MultimodalError("graph schema mismatch")
    if not _receipt_matches(graph):
        raise Pass220I042MultimodalError("graph receipt mismatch")

    expected = build_multimodal_knowledge_graph()
    if graph != expected:
        raise Pass220I042MultimodalError("multimodal graph drift")

    shared_root = shared_multimodal_root_sha256()
    if graph.get("shared_multimodal_root_sha256") != shared_root:
        raise Pass220I042MultimodalError("shared root mismatch")
    if graph.get("modality_count") != len(MODALITIES):
        raise Pass220I042MultimodalError("modality count mismatch")
    if graph.get("root_edge_count") != len(MODALITIES):
        raise Pass220I042MultimodalError("root edge count mismatch")
    if graph.get("directed_cross_modal_translation_count") != (
        len(MODALITIES) * (len(MODALITIES) - 1)
    ):
        raise Pass220I042MultimodalError("cross-modal translation count mismatch")
    if graph.get("all_modalities_share_root") is not True:
        raise Pass220I042MultimodalError("modality root divergence")
    if graph.get("all_modalities_have_5184_projection") is not True:
        raise Pass220I042MultimodalError("5,184 projection loss")
    if graph.get("all_modalities_have_hash216_genome") is not True:
        raise Pass220I042MultimodalError("Hash216 genome loss")

    projections = graph.get("projections")
    if not isinstance(projections, Mapping):
        raise Pass220I042MultimodalError("projection mapping missing")
    if tuple(projections) != MODALITIES:
        raise Pass220I042MultimodalError("projection order mismatch")

    for modality, projection in projections.items():
        if not _receipt_matches(projection):
            raise Pass220I042MultimodalError(
                f"{modality} projection receipt mismatch"
            )
        if projection["shared_multimodal_root_sha256"] != shared_root:
            raise Pass220I042MultimodalError(
                f"{modality} shared root mismatch"
            )
        if projection["projection_bits"] != 5184:
            raise Pass220I042MultimodalError(
                f"{modality} projection width mismatch"
            )
        if projection["projection_bytes"] != 648:
            raise Pass220I042MultimodalError(
                f"{modality} projection byte width mismatch"
            )
        if projection["hash216_position_count"] != 216:
            raise Pass220I042MultimodalError(
                f"{modality} Hash216 position count mismatch"
            )
        for field in (
            "canonical_vm81_mutation_authority",
            "canonical_hash72_authority",
            "canonical_hash216_authority",
            "canonical_learning_commit_authority",
            "model_weight_update_authority",
            "direct_canonical_persistence_authority",
            "host_float_arithmetic_used",
            "probability_used",
            "likelihood_used",
            "mcmc_used",
            "parameter_refit_performed",
        ):
            if projection.get(field) is not False:
                raise Pass220I042MultimodalError(
                    f"{modality} forbidden authority/path: {field}"
                )

    translation_pairs = {
        (
            item["source_modality"],
            item["target_modality"],
        )
        for item in graph["translation_receipts"]
    }
    expected_pairs = {
        (source, target)
        for source in MODALITIES
        for target in MODALITIES
        if source != target
    }
    if translation_pairs != expected_pairs:
        raise Pass220I042MultimodalError("translation pair coverage mismatch")

    audio = projections["AUDIO"]["semantic_binding"]
    if audio.get("polyrhythm_ratio") != {"numerator": 3, "denominator": 2}:
        raise Pass220I042MultimodalError("audio 3:2 ratio drift")
    if tuple(audio.get("three_pulse_ticks", ())) != (0, 48, 96):
        raise Pass220I042MultimodalError("audio 3-pulse clock drift")
    if tuple(audio.get("two_pulse_ticks", ())) != (0, 72):
        raise Pass220I042MultimodalError("audio 2-pulse clock drift")

    language = projections["LANGUAGE"]["semantic_binding"]
    if language.get("pass166_contract") != PASS166_LANGUAGE_CONTRACT:
        raise Pass220I042MultimodalError("Pass166 language contract drift")
    if language.get("pass218_candidate_semantics") != PASS218_RELATIONAL_SEMANTICS:
        raise Pass220I042MultimodalError("Pass218 candidate semantics drift")
    if language.get("word2vec_candidate_truth_authority") is not False:
        raise Pass220I042MultimodalError("language truth authority escalation")

    for field in (
        "host_float_arithmetic_used",
        "probability_used",
        "likelihood_used",
        "mcmc_used",
        "parameter_refit_performed",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "canonical_learning_commit_authority",
        "model_weight_update_authority",
        "direct_canonical_persistence_authority",
    ):
        if graph.get(field) is not False:
            raise Pass220I042MultimodalError(
                f"graph forbidden authority/path: {field}"
            )

    return {
        "ok": True,
        "shared_multimodal_root_sha256": shared_root,
        "modality_count": len(MODALITIES),
        "projection_bits_per_modality": 5184,
        "projection_bytes_per_modality": 648,
        "hash216_positions_per_modality": 216,
        "directed_cross_modal_translation_count": len(expected_pairs),
        "audio_polyrhythm": {"numerator": 3, "denominator": 2},
        "language_pass166_candidate_contract_bound": True,
        "all_modalities_share_root": True,
        "all_modalities_have_5184_projection": True,
        "all_modalities_have_hash216_genome": True,
        "exact_multimodal_fabric_closed": True,
    }


def lane5_multimodal_shared_root_witness() -> Dict[str, Any]:
    graph = build_multimodal_knowledge_graph()
    result = validate_multimodal_knowledge_graph(graph)
    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": result["ok"],
        "result": result,
        "graph_receipt_sha256": graph["receipt_sha256"],
        "shared_multimodal_root_sha256": result[
            "shared_multimodal_root_sha256"
        ],
        "local_constraints": LOCAL_CONSTRAINTS,
        "root_metadata_seed_text": ROOT_METADATA_SEED_TEXT,
        "invariant_gate_text": INVARIANT_GATE_TEXT,
        "lane5_role": graph["lane5_role"],
        "canonical_admission_authority": False,
    })


def lane5_multimodal_shared_root_self_test() -> Dict[str, Any]:
    return lane5_multimodal_shared_root_witness()
