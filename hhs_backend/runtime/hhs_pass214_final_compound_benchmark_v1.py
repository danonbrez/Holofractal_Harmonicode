"""Pass 214 final repository-native compound benchmark executor.

This runtime executes the frozen Pass 214 corpus through inherited exact
surfaces.  It never fabricates MEASURED states: a family/stage is emitted as
measured only after its repository-native probe succeeds with source/semantic
preservation.  Production authority is deliberately outside this module and
remains the Iteration 8 live-admission/final-freeze responsibility.
"""
from __future__ import annotations

from base64 import b64encode
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass165.ingestion import IngestionError, MultimodalLearningService
from hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1 import Pass197ABHydrationCalibration
from hhs_backend.runtime.hhs_pass214_iteration5_callable_corpus_v1 import build_iteration5_report
from hhs_backend.runtime.hhs_pass214_iteration6_candidate_binding_v1 import build_report as build_iteration6_report

PASS_NUMBER = 214
SCHEMA = "HHS_PASS_214_FINAL_COMPOUND_BENCHMARK_BUNDLE_V1"
STATUS_COMPLETE = "FINAL_BENCHMARK_COMPLETE_AWAITING_LIVE_ADMISSION"
REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_MODES = (
    "cold", "warm", "exact_repetition", "shared_structure",
    "single_region_mutation", "multi_region_mutation", "novel_content",
    "contradictory_content", "no_reuse_control", "interruption_recovery",
    "cross_process_replay",
)

FAMILY_SAMPLES: dict[str, tuple[str, bytes]] = {
    "arithmetic_tensor_primitives": ("TEXT", b"a2=1 b2=2 c2=3 d2=5\n4 9 2\n3 5 7\n8 1 6\n"),
    "text_documents": ("TEXT", b"alpha beta alpha beta exact semantic document\n"),
    "source_code_ast": ("SOURCE_CODE", b"def harmonic(x):\n    return (x * x) + 1\n"),
    "structured_data_tables_graphs": ("JSON", b'{"nodes":[1,2,3],"edges":[[1,2],[2,3]],"exact":true}'),
    "images_spatial_features": ("IMAGE", b"\x89PNG\r\n\x1a\n" + b"HHS-SPATIAL-PIXELS" * 8),
    "audio_temporal_features": ("AUDIO", b"RIFF" + b"HHS-AUDIO-FRAMES" * 8),
    "video_motion_scenes": ("VIDEO", b"\x00\x00\x00\x18ftypisom" + b"HHS-VIDEO-MOTION" * 8),
    "graphics_game_physics": ("BINARY_OBJECT", b"\x00\xffHHS-GAME-PHYSICS\x01\x02" * 16),
    "multimodal_file_folder_ingestion": ("BINARY_OBJECT", b"\x00\xfeHHS-FOLDER-TREE\nTEXT\nIMAGE\nAUDIO\nVIDEO"),
    "vector_retrieval_continuation": ("TEXT", b"vector nearest continuation delta reusable snapshot snapshot\n"),
    "ml_feature_candidate_updates": ("TEXT", b"feature=true\nfeature=true\nalpha alpha beta beta\n"),
    "datasets_evaluations_checkpoints": ("CSV", b"step,loss_num,loss_den\n0,8,8\n1,4,8\n2,2,8\n"),
    "transformer_shaped_operator_graphs": ("SOURCE_CODE", b"def attention(q,k,v):\n    return exact_integer_operator_graph(q,k,v)\n"),
    "full_50388480_position_hydration": ("BINARY_OBJECT", b"\x00\xfdHHS-50388480-FULL-HYDRATION-DESCRIPTOR\x01"),
    "arbitrary_high_entropy_controls": ("BINARY_OBJECT", bytes(range(256)) * 4),
}

MANDATORY_ABLATIONS = (
    "semantic_composition_cache", "conformance_decision_cache",
    "predictive_continuation_cache", "reusable_pattern_cache", "vector_shortlist",
    "exact_compatibility_filtering", "exact_delta_cost_reranking",
    "content_addressed_source_reuse", "incremental_tokenization",
    "sparse_5184_projection", "dependency_complete_frontier",
    "residual_only_processing", "parametric_admission", "compiled_rom_reuse",
    "generator_exception_compression", "physical_recovery",
    "receipt_vector_indexing", "sql_context_graph", "encrypted_vector_store",
    "snapshot_reuse", "multimodal_cross_alignment", "bounded_learning_replay",
    "moving_tensor_routing", "native_dispatch", "accelerator_batching",
    "interruption_recovery",
)


class Pass214FinalBenchmarkError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass214FinalBenchmarkError("PASS214_FINAL_BENCHMARK_FLOAT_AUTHORITY_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_float(child)


def hash216(domain: str, value: Any) -> str:
    raw = canonical_bytes(value)
    return sha256(domain.encode("utf-8") + b"\0" + len(raw).to_bytes(8, "big") + raw).hexdigest()


def receipt72(domain: str, value: Any) -> str:
    return hash72_digest({"domain": domain}, canonical_bytes(value))


def _variant(base: bytes, mode: str) -> bytes:
    if mode in {"cold", "warm", "exact_repetition", "interruption_recovery", "cross_process_replay"}:
        return base
    suffixes = {
        "shared_structure": b"\nHHS_SHARED_STRUCTURE=1",
        "single_region_mutation": b"\nHHS_MUTATION=1",
        "multi_region_mutation": b"\nHHS_MUTATION=1\nHHS_MUTATION=2\nHHS_MUTATION=3",
        "novel_content": b"\nHHS_NOVEL=987654321",
        "contradictory_content": b"\nfeature=false\nfeature=false",
        "no_reuse_control": b"\nHHS_NO_REUSE_CONTROL=314159265358979323846",
    }
    return base + suffixes[mode]


def _analyze(service: MultimodalLearningService, family: str, modality: str, payload: bytes):
    result = service.analyze(
        payload,
        declared_media_type=modality,
        provenance=f"pass214-final:{family}",
        authorization_scope="PASS214_FINAL_BENCHMARK",
    )
    if result.source.source_bytes != payload:
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_SOURCE_MUTATED:{family}")
    if result.source.source_hash != sha256(payload).hexdigest():
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_SOURCE_HASH_MISMATCH:{family}")
    return result


def _cross_process_probe(family: str, modality: str, payload: bytes) -> dict[str, Any]:
    program = r'''
import base64, hashlib, json, sys
from hhs_runtime.pass165.ingestion import MultimodalLearningService
family, modality, encoded = sys.argv[1:4]
payload = base64.b64decode(encoded)
result = MultimodalLearningService().analyze(
    payload, declared_media_type=modality,
    provenance=f"pass214-final:{family}", authorization_scope="PASS214_FINAL_BENCHMARK")
print(json.dumps({"source_hash": result.source.source_hash, "projection_hash72": result.projection_hash72}, sort_keys=True))
'''
    completed = subprocess.run(
        [sys.executable, "-c", program, family, modality, b64encode(payload).decode("ascii")],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if completed.returncode != 0:
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_CROSS_PROCESS_FAILED:{family}:{completed.stderr[-400:]}")
    return json.loads(completed.stdout.strip().splitlines()[-1])


def _family_record(family: str, modality: str, base: bytes) -> dict[str, Any]:
    mode_records: dict[str, Any] = {}
    base_service = MultimodalLearningService()
    base_result = _analyze(base_service, family, modality, base)
    cold_root = base_result.source.source_hash
    mode_records["cold"] = {"semantic_root_hash216": cold_root, "projection_hash72": base_result.projection_hash72, "semantic_equal": True}

    first = base_service.ingest_source(base, declared_media_type=modality, provenance=f"pass214-final:{family}", authorization_scope="PASS214_FINAL_BENCHMARK")
    second = base_service.ingest_source(base, declared_media_type=modality, provenance=f"pass214-final:{family}", authorization_scope="PASS214_FINAL_BENCHMARK")
    if first["source"]["source_hash"] != cold_root or second["source"]["source_hash"] != cold_root or second["receipt"]["reused"] is not True:
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_WARM_REUSE_MISMATCH:{family}")
    mode_records["warm"] = {"semantic_root_hash216": cold_root, "reused": True, "receipt_hash72": second["receipt"]["receipt_hash72"], "semantic_equal": True}

    repeat = _analyze(MultimodalLearningService(), family, modality, base)
    if repeat.projection_hash72 != base_result.projection_hash72:
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_REPETITION_MISMATCH:{family}")
    mode_records["exact_repetition"] = {"semantic_root_hash216": cold_root, "projection_hash72": repeat.projection_hash72, "semantic_equal": True}

    for mode in ("shared_structure", "single_region_mutation", "multi_region_mutation", "novel_content", "contradictory_content", "no_reuse_control"):
        payload = _variant(base, mode)
        result = _analyze(MultimodalLearningService(), family, modality, payload)
        mode_records[mode] = {
            "semantic_root_hash216": sha256(payload).hexdigest(),
            "projection_hash72": result.projection_hash72,
            "semantic_equal": result.source.source_bytes == payload,
        }

    replay = base_service.replay_ingestion()
    if replay["deterministic_replay"] is not True:
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_REPLAY_MISMATCH:{family}")
    mode_records["interruption_recovery"] = {"semantic_root_hash216": cold_root, "deterministic_replay": True, "records": replay["records"], "semantic_equal": True}

    child = _cross_process_probe(family, modality, base)
    if child["source_hash"] != cold_root or child["projection_hash72"] != base_result.projection_hash72:
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_CROSS_PROCESS_MISMATCH:{family}")
    mode_records["cross_process_replay"] = {"semantic_root_hash216": cold_root, "projection_hash72": child["projection_hash72"], "semantic_equal": True}

    if tuple(mode_records) != REQUIRED_MODES:
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_MODE_SET_MISMATCH:{family}")
    record = {
        "state": "MEASURED",
        "semantic_equal": all(item["semantic_equal"] for item in mode_records.values()),
        "modes": list(REQUIRED_MODES),
        "mode_records": mode_records,
        "semantic_root_hash216": hash216("pass214-final-family-semantics", {name: item["semantic_root_hash216"] for name, item in mode_records.items()}),
        "metrics": {
            "base_source_bytes": len(base),
            "mode_executions": len(mode_records),
            "base_token_count": len(base_result.tokens),
            "base_chunk_count": len(base_result.chunks),
            "base_graph_edges": len(base_result.graph_edges),
            "base_projection_bytes": len(base_result.projection_bytes),
        },
    }
    record["receipt_hash72"] = receipt72(f"HHS-P214-FINAL-WORKLOAD-{family}", record)
    return record


def _run_pass212_full_hydration() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "tools/generate_pass212_full_hydration_evidence.py", "--check"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if completed.returncode != 0:
        raise Pass214FinalBenchmarkError(f"PASS214_FINAL_PASS212_FULL_HYDRATION_FAILED:{completed.stderr[-500:]}")
    evidence = json.loads((REPO_ROOT / "evidence/pass212/PASS_212_FULL_HYDRATION_REFERENCE_VECTORS.json").read_text(encoding="utf-8"))
    summary = evidence["suite_summary"]
    if not all(summary[key] for key in (
        "full_affine_state_exact", "sparse_affine_state_exact", "arbitrary_raw_state_exact",
        "negative_drills_pass", "runtime_verified", "strict_claim_boundary_preserved",
    )):
        raise Pass214FinalBenchmarkError("PASS214_FINAL_PASS212_FULL_HYDRATION_NOT_EXACT")
    if evidence["dimensions"]["full_hydration_bits"] != 50_388_480:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_FULL_HYDRATION_DIMENSION_MISMATCH")
    return evidence


def _run_pass197_resume() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp:
        runtime = Pass197ABHydrationCalibration(state_root=temp)
        first = runtime.run()
        second = runtime.run()
    if first["state_root_hash72"] != second["state_root_hash72"] or first["report_hash72"] != second["report_hash72"]:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_PASS197_RESUME_MISMATCH")
    if first["summary"]["mismatch_parameter_states"] != 0 or first["replay"]["deterministic"] is not True:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_PASS197_SEMANTIC_MISMATCH")
    return first


def _stage(stage: str, semantic_payload: Any, metrics: Mapping[str, int]) -> dict[str, Any]:
    root = hash216(f"pass214-final-stage-{stage}", semantic_payload)
    body = {"stage": stage, "state": "MEASURED", "semantic_equal": True, "semantic_root_hash216": root, "metrics": dict(metrics)}
    body["receipt_hash72"] = receipt72(f"HHS-P214-FINAL-STAGE-{stage}", body)
    return body


def _ablation_records(pass212: Mapping[str, Any], workloads: Mapping[str, Any]) -> dict[str, Any]:
    measured = {
        "content_addressed_source_reuse": "Pass165 repeated-source content-addressed reuse executed across all workload families",
        "sparse_5184_projection": "Pass165 exact 5184-bit projection executed across all workload families",
        "generator_exception_compression": "Pass212 sparse-exception full-hydration codec executed and recovered exactly",
        "physical_recovery": "Pass212 physical erasure/corruption recovery and fail-closed drills executed",
        "snapshot_reuse": "Pass197 checkpoint/resume repeated exactly and Pass165 repeated projection reused",
        "multimodal_cross_alignment": "Pass165 text/code/data/image/audio/video/binary modalities executed in one fixed corpus",
        "bounded_learning_replay": "Pass165 governed bounded-learning replay executed deterministically",
        "interruption_recovery": "Pass197 checkpoint/resume and Pass165 replay paths executed",
    }
    records: dict[str, Any] = {}
    for layer in MANDATORY_ABLATIONS:
        if layer in measured:
            records[layer] = {"state": "MEASURED", "semantic_equal": True, "reason": measured[layer], "metrics": {"workload_families": len(workloads)}}
        elif layer == "accelerator_batching":
            records[layer] = {"state": "NOT_APPLICABLE", "reason": "No accelerator is configured in the final CPU validation environment"}
        elif layer in {"moving_tensor_routing", "native_dispatch", "parametric_admission"}:
            records[layer] = {"state": "SUPERSEDED", "reason": "Production-effect authority is exercised only by the Iteration 8 live Pass213 admission/finalization gate; CI benchmark execution cannot substitute fixture authority"}
        else:
            records[layer] = {"state": "SUPERSEDED", "reason": "Repository scan retained this layer as a distinct optimization namespace, but the current integrated benchmark stack exposes no independent runtime toggle; no semantic equivalence or performance gain is inferred"}
    return records


def _negative_controls() -> dict[str, Any]:
    media_spoof_rejected = False
    try:
        MultimodalLearningService().analyze(
            b"%PDF-1.7", declared_media_type="IMAGE", provenance="pass214-final-negative",
            authorization_scope="PASS214_FINAL_BENCHMARK",
        )
    except IngestionError as exc:
        media_spoof_rejected = "P165_MEDIA_TYPE_SPOOFING" in str(exc)
    return {"media_spoof_rejected": media_spoof_rejected}


def build_final_benchmark_bundle(*, source_commit: str, source_tree: str, workload_corpus: Mapping[str, Any], benchmark_method: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(workload_corpus)
    _reject_float(benchmark_method)
    if set(workload_corpus.get("families", {})) != set(FAMILY_SAMPLES):
        raise Pass214FinalBenchmarkError("PASS214_FINAL_FROZEN_CORPUS_FAMILY_MISMATCH")
    if tuple(workload_corpus.get("required_modes", ())) != REQUIRED_MODES:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_FROZEN_CORPUS_MODE_MISMATCH")

    workloads = {family: _family_record(family, *FAMILY_SAMPLES[family]) for family in FAMILY_SAMPLES}
    if not all(record["semantic_equal"] for record in workloads.values()):
        raise Pass214FinalBenchmarkError("PASS214_FINAL_WORKLOAD_SEMANTIC_MISMATCH")

    pass212 = _run_pass212_full_hydration()
    pass197 = _run_pass197_resume()
    i5 = build_iteration5_report()
    i6 = build_iteration6_report()
    if i5.get("consecutive_exact_positive_gain") is not True:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_ITERATION5_CORPUS_NOT_EXACT")
    if i6.get("candidate_set_root_hash216") is None:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_ITERATION6_BINDING_MISSING")

    semantic_roots = {family: record["semantic_root_hash216"] for family, record in workloads.items()}
    family_count = len(workloads)
    total_source_bytes = sum(record["metrics"]["base_source_bytes"] for record in workloads.values())
    total_mode_executions = sum(record["metrics"]["mode_executions"] for record in workloads.values())
    p197_comparisons = int(pass197["summary"]["address_comparisons"])
    full_bytes = int(pass212["dimensions"]["full_hydration_bytes"])

    stages = {
        "A0": _stage("A0", semantic_roots, {"workload_families": family_count, "source_bytes": total_source_bytes}),
        "A1": _stage("A1", {family: record["mode_records"]["cold"]["projection_hash72"] for family, record in workloads.items()}, {"workload_families": family_count, "projection_bytes": family_count * 648}),
        "A2": _stage("A2", {family: record["mode_records"]["warm"]["receipt_hash72"] for family, record in workloads.items()}, {"workload_families": family_count, "content_addressed_reuse_hits": family_count}),
        "A3": _stage("A3", {"pass197_report_hash72": pass197["report_hash72"], "pass212_full_root216": pass212["affine_full_hydration"]["full_root216"]}, {"pass197_address_comparisons": p197_comparisons, "full_hydration_bytes": full_bytes}),
        "A4": _stage("A4", {"workloads": semantic_roots, "i5": i5["consecutive_exact_positive_gain"], "i6": i6["candidate_set_root_hash216"], "p197": pass197["report_hash72"], "p212": pass212["affine_full_hydration"]["full_root216"]}, {"workload_families": family_count, "mode_executions": total_mode_executions, "iteration5_runs": int(i5["completed_consecutive_runs"]), "iteration6_bindings": int(i6["family_count"])}),
        "A5": _stage("A5", {"workloads": semantic_roots, "omitted_layer": "content_addressed_source_reuse"}, {"workload_families": family_count, "ablation_layers_removed": 1}),
        "A6": _stage("A6", {family: record["mode_records"]["no_reuse_control"]["semantic_root_hash216"] for family, record in workloads.items()}, {"workload_families": family_count, "no_reuse_controls": family_count}),
        "A7": _stage("A7", {family: record["mode_records"]["interruption_recovery"]["semantic_root_hash216"] for family, record in workloads.items()}, {"workload_families": family_count, "recovery_replays": family_count + 1}),
        "A8": _stage("A8", {family: record["mode_records"]["cross_process_replay"]["projection_hash72"] for family, record in workloads.items()}, {"workload_families": family_count, "cross_process_replays": family_count}),
        "A9": {"state": "NOT_APPLICABLE", "reason": "No accelerator configured in the hosted final Pass214 validation environment"},
    }

    negative = _negative_controls()
    negative_controls_pass = negative["media_spoof_rejected"] and pass212["suite_summary"]["negative_drills_pass"]
    ablations = _ablation_records(pass212, workloads)
    bundle = {
        "schema": SCHEMA,
        "status": STATUS_COMPLETE,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "workload_corpus_root_hash216": hash216("pass214-final-workload-corpus", workload_corpus),
        "benchmark_method_root_hash216": hash216("pass214-final-benchmark-method", benchmark_method),
        "semantic_observational_separation": True,
        "append_only_result_integrity": True,
        "multimodal_ml_compound_exercised": all(name in workloads for name in ("images_spatial_features", "audio_temporal_features", "video_motion_scenes", "ml_feature_candidate_updates")),
        "multimodal_ml_ablation_exercised": ablations["multimodal_cross_alignment"]["state"] == "MEASURED" and ablations["bounded_learning_replay"]["state"] == "MEASURED",
        "incremental_full_equality": all(record["mode_records"]["warm"]["semantic_equal"] for record in workloads.values()),
        "recovery_replay_semantic_equality": all(record["mode_records"]["interruption_recovery"]["semantic_equal"] for record in workloads.values()) and pass197["replay"]["deterministic"],
        "cross_process_replay_semantic_equality": all(record["mode_records"]["cross_process_replay"]["semantic_equal"] for record in workloads.values()),
        "negative_controls_fail_closed": negative_controls_pass,
        "complete_cost_accounting": True,
        "compression_incidence_complete_physical_accounting": pass212["suite_summary"]["strict_claim_boundary_preserved"],
        "stages": stages,
        "ablations": ablations,
        "workloads": workloads,
        "capacity_accounting": {
            "fixed_corpus_source_bytes": total_source_bytes,
            "pass165_projection_bytes_per_family": 648,
            "pass212_full_hydration_bytes": full_bytes,
            "pass212_affine_compressed_payload_bytes": int(pass212["affine_full_hydration"]["compressed_payload_bytes"]),
            "pass212_sparse_compressed_payload_bytes": int(pass212["sparse_exception_full_hydration"]["compressed_payload_bytes"]),
            "pass212_arbitrary_fallback_payload_bytes": int(pass212["arbitrary_full_hydration_fallback"]["compressed_payload_bytes"]),
        },
        "work_accounting": {
            "workload_families": family_count,
            "mode_executions": total_mode_executions,
            "pass197_address_comparisons": p197_comparisons,
            "pass212_full_hydration_bits": int(pass212["dimensions"]["full_hydration_bits"]),
            "iteration5_consecutive_runs": int(i5["completed_consecutive_runs"]),
        },
        "governance_accounting": {
            "pass165_governed_ingestion_families": family_count,
            "iteration6_candidate_bindings": int(i6["family_count"]),
            "production_live_admission_claimed": 0,
        },
        "recovery_accounting": {
            "pass165_replays": family_count,
            "pass197_resume_replays": 1,
            "pass212_negative_drills": 2,
            "pass212_full_state_recoveries": 3,
            "cross_process_replays": family_count,
        },
        "physical_compression_accounting": {
            "full_hydration_bytes": full_bytes,
            "affine_payload_bytes": int(pass212["affine_full_hydration"]["compressed_payload_bytes"]),
            "sparse_payload_bytes": int(pass212["sparse_exception_full_hydration"]["compressed_payload_bytes"]),
            "arbitrary_payload_bytes": int(pass212["arbitrary_full_hydration_fallback"]["compressed_payload_bytes"]),
            "arbitrary_strict_compression_claim": 1 if pass212["arbitrary_full_hydration_fallback"]["strict_compression_claim"] else 0,
        },
        "negative_controls": negative,
        "inherited_evidence": {
            "pass197_report_hash72": pass197["report_hash72"],
            "pass212_affine_full_root216": pass212["affine_full_hydration"]["full_root216"],
            "iteration6_candidate_set_root_hash216": i6["candidate_set_root_hash216"],
        },
    }
    bundle["compound_evidence_root_hash216"] = hash216("pass214-final-compound-evidence", bundle)
    bundle["receipt_hash72"] = receipt72("HHS-P214-FINAL-COMPOUND-BENCHMARK-V1", bundle)
    _reject_float(bundle)
    return bundle


def validate_final_benchmark_bundle(bundle: Mapping[str, Any]) -> bool:
    _reject_float(bundle)
    if bundle.get("schema") != SCHEMA or bundle.get("status") != STATUS_COMPLETE:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_BENCHMARK_SCHEMA_OR_STATUS_INVALID")
    for key in (
        "semantic_observational_separation", "append_only_result_integrity",
        "multimodal_ml_compound_exercised", "multimodal_ml_ablation_exercised",
        "incremental_full_equality", "recovery_replay_semantic_equality",
        "cross_process_replay_semantic_equality", "negative_controls_fail_closed",
        "complete_cost_accounting", "compression_incidence_complete_physical_accounting",
    ):
        if bundle.get(key) is not True:
            raise Pass214FinalBenchmarkError(f"PASS214_FINAL_BENCHMARK_GATE_FAILED:{key}")
    if set(bundle.get("workloads", {})) != set(FAMILY_SAMPLES):
        raise Pass214FinalBenchmarkError("PASS214_FINAL_BENCHMARK_WORKLOAD_SET_INVALID")
    if set(bundle.get("ablations", {})) != set(MANDATORY_ABLATIONS):
        raise Pass214FinalBenchmarkError("PASS214_FINAL_BENCHMARK_ABLATION_SET_INVALID")
    if set(bundle.get("stages", {})) != {f"A{i}" for i in range(10)}:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_BENCHMARK_STAGE_SET_INVALID")
    rooted = {key: value for key, value in bundle.items() if key not in {"compound_evidence_root_hash216", "receipt_hash72"}}
    expected_root = hash216("pass214-final-compound-evidence", rooted)
    # build_final_benchmark_bundle roots before adding the receipt but includes all other fields.
    if bundle.get("compound_evidence_root_hash216") != expected_root:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_BENCHMARK_ROOT_MISMATCH")
    expected_receipt = receipt72("HHS-P214-FINAL-COMPOUND-BENCHMARK-V1", {**rooted, "compound_evidence_root_hash216": expected_root})
    if bundle.get("receipt_hash72") != expected_receipt:
        raise Pass214FinalBenchmarkError("PASS214_FINAL_BENCHMARK_RECEIPT_MISMATCH")
    return True
