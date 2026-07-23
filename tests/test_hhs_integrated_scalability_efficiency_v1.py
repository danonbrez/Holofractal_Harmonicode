from __future__ import annotations

import json
import time
from fractions import Fraction
from pathlib import Path
from time import perf_counter_ns

import pytest

from hhs_runtime.pass148.service import HHS148Service
from hhs_runtime.pass150 import Base20BigIntCodec, Hash216ImmuneSystem, KeyEpoch
from hhs_runtime.pass152 import ElasticClosureEngine
from hhs_runtime.pass152.common import sha256_json
from hhs_runtime.pass152.model import EdgeType, EquivalenceWitness, OperationNode, SkipWitness


ROOT = Path(__file__).resolve().parents[1]
PASS144_DOCS = (
    ROOT / "docs/pass_144/README.md",
    ROOT / "docs/pass_144/USER_GUIDE.md",
    ROOT / "docs/pass_144/CLI_MANUAL.md",
    ROOT / "docs/pass_144/API_MANUAL.md",
    ROOT / "docs/pass_144/INVARIANT_ALGEBRA_GUIDE.md",
    ROOT / "docs/pass_144/RECEIPTS_AND_AUTHORITY.md",
    ROOT / "docs/pass_144/PROOF_LEMMA_CORPUS_GUIDE.md",
    ROOT / "docs/pass_144/GLOSSARY.md",
)
PASS144_CORPUS = ROOT / "formal/lemmas/pass_144/LEMMA_CORPUS.json"


def _pass144_baseline() -> dict[str, int]:
    docs = [path.read_text(encoding="utf-8") for path in PASS144_DOCS]
    corpus = json.loads(PASS144_CORPUS.read_text(encoding="utf-8"))
    lemma_ids = [entry["id"] for entry in corpus["lemmas"]]
    return {
        "document_count": len(docs),
        "total_doc_bytes": sum(len(doc.encode("utf-8")) for doc in docs),
        "lemma_count": len(lemma_ids),
        "unique_lemma_count": len(set(lemma_ids)),
    }


def _bootstrap_pass148(db_path: Path) -> HHS148Service:
    service = HHS148Service(db_path)
    service.sync_semantic_registry()
    service.public_registry.synchronize()
    return service


def _analyze(service: HHS148Service, expression: str, *, source_type: str, source_reference: str) -> dict:
    contracts = ["HHS-P148-NSAM"] if source_type in {"contract", "runtime", "user_declaration"} else []
    profile = "NARRATIVE_WORLD_MODEL_V1" if source_type == "fiction" else "HHS_NATIVE_TYPED_V1"
    return service.analyze(
        expression,
        source_type=source_type,
        source_reference=source_reference,
        profile_id=profile,
        declared_scope={},
        governing_contracts=contracts,
    )


def _run_pass148_batch(service: HHS148Service, batch_size: int, *, batch_label: str) -> dict[str, object]:
    templates = (
        ("O≠π", "contract"),
        ("n/Δ=n", "contract"),
        ("Δ-Δ=0", "model_output"),
        ("AB=BA", "model_output"),
        ("The numerical experiment is a formal proof", "model_output"),
        (" \\frac{AB}{B^2} P ", "documentation"),
    )
    start = perf_counter_ns()
    proposition_ids: list[str] = []
    class_counts: dict[str, int] = {}
    contamination_total = 0
    for index in range(batch_size):
        expression, source_type = templates[index % len(templates)]
        result = _analyze(
            service,
            expression,
            source_type=source_type,
            source_reference=f"{batch_label}:{index}",
        )
        proposition = result["proposition"]
        proposition_ids.append(proposition["proposition_id"])
        class_counts[proposition["primary_class"]] = class_counts.get(proposition["primary_class"], 0) + 1
        contamination_total += len(result["contamination_findings"])
    law = _analyze(
        service,
        "n/Δ=n",
        source_type="contract",
        source_reference=f"{batch_label}:law",
    )
    derivation = service.derive(
        [law["proposition"]["proposition_id"]],
        rule_id="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1",
        substitutions={"n": "Δ"},
    )
    replay_targets = proposition_ids[:4] + [
        derivation["output_proposition"]["proposition_id"],
        derivation["derivation"]["derivation_id"],
    ]
    replay_results = [service.replay_semantic(target) for target in replay_targets]
    elapsed = perf_counter_ns() - start
    status = service.status()
    return {
        "elapsed_ns": elapsed,
        "proposition_ids": proposition_ids,
        "class_counts": class_counts,
        "contamination_total": contamination_total,
        "replay_results": replay_results,
        "status": status,
    }


def _key_material(seed: int) -> bytes:
    return bytes((seed + offset) % 256 for offset in range(32))


def _run_pass150_airgap(root: Path, *, event_count: int, payload_scale: int) -> dict[str, object]:
    system = Hash216ImmuneSystem(
        root,
        KeyEpoch.genesis(_key_material(11)),
        max_spool_records=event_count + 4,
    )
    start = perf_counter_ns()
    records = []
    codec_round_trips = []
    for index in range(event_count):
        opcodes = tuple((index + offset) % 19 for offset in range(1 + (index % 5)))
        encoded = Base20BigIntCodec.encode(opcodes)
        codec_round_trips.append(Base20BigIntCodec.decode(encoded))
        payload = {
            "sequence": index,
            "opcodes": list(opcodes),
            "payload": f"{index:04d}-" + ("P150" * payload_scale),
        }
        records.append(system.inspect("INTEGRATED_SCALE", "pass150-suite", payload))
        if index and index % 6 == 0:
            system.rotate_key(_key_material(11 + index))
    flushed = system.flush()
    elapsed = perf_counter_ns() - start
    assert system.validate_chain()
    recovered = system.recover()
    echoes = [system.echo_for_vm81(record) for record in records[: min(3, len(records))]]
    return {
        "elapsed_ns": elapsed,
        "records": records,
        "flushed": flushed,
        "recovered": recovered,
        "codec_round_trips": codec_round_trips,
        "echoes": echoes,
        "epochs_path": system.epochs_path,
    }


def _build_pass152_scaled_cycle(
    receipt_root: Path,
    *,
    workers: int,
    branch_count: int,
    delay_seconds: float,
    authority_root: str = "AUTHORITY-ROOT-152-INTEGRATED",
    authoritative_state: dict | None = None,
) -> dict[str, object]:
    engine = ElasticClosureEngine(
        authoritative_state or {"cycle": 0, "status": "OPEN"},
        authority_root,
        receipt_root,
        workers=workers,
    )
    engine.add_node(OperationNode("x", "SEED_X", estimated_cost=Fraction(1, 10)))
    engine.add_node(OperationNode("y", "SEED_Y", estimated_cost=Fraction(1, 10)))
    final_dependencies = set()
    expected_total = 0
    for index in range(branch_count):
        left_id = f"left_{index}"
        right_id = f"right_{index}"
        merge_id = f"merge_{index}"
        alias_id = f"alias_{index}"
        identity_id = f"identity_{index}"
        left_value = 10 + index + 1
        right_value = 20 + ((index + 1) * 2)
        merged_value = left_value + right_value
        expected_total += merged_value
        engine.add_node(
            OperationNode(
                left_id,
                "LEFT_BRANCH",
                compute=lambda d, offset=index: (time.sleep(delay_seconds), d["x"] + offset + 1)[1],
                estimated_cost=Fraction(5, 1),
                lane_id=f"L{index}",
            )
        )
        engine.add_node(
            OperationNode(
                right_id,
                "RIGHT_BRANCH",
                compute=lambda d, offset=index: (time.sleep(delay_seconds), d["y"] + ((offset + 1) * 2))[1],
                estimated_cost=Fraction(5, 1),
                lane_id=f"R{index}",
            )
        )
        engine.add_node(
            OperationNode(
                merge_id,
                "MERGE_BRANCH",
                compute=lambda d, left=left_id, right=right_id: (time.sleep(delay_seconds), d[left] + d[right])[1],
                estimated_cost=Fraction(4, 1),
                lane_id=f"M{index}",
            )
        )
        engine.add_node(
            OperationNode(
                alias_id,
                "MERGE_ALIAS",
                compute=lambda d, left=left_id, right=right_id: d[left] + d[right],
                estimated_cost=Fraction(4, 1),
                lane_id=f"A{index}",
            )
        )
        engine.add_node(
            OperationNode(
                identity_id,
                "IDENTITY",
                compute=lambda d, alias=alias_id: d[alias],
                estimated_cost=Fraction(1, 1),
                lane_id=f"I{index}",
            )
        )
        final_dependencies.add(identity_id)
        for source, target in (
            ("x", left_id),
            ("y", right_id),
            (left_id, merge_id),
            (right_id, merge_id),
            (left_id, alias_id),
            (right_id, alias_id),
            (alias_id, identity_id),
        ):
            engine.add_edge(source, target, EdgeType.VALUE_DEPENDS_ON)
        operand_digest = sha256_json({left_id: left_value, right_id: right_value})
        engine.register_equivalence_witness(
            EquivalenceWitness(
                f"EQ-{index}",
                merge_id,
                alias_id,
                "CONSTRAINT-ROOT-152",
                authority_root,
                engine.semantic_version,
                operand_digest,
                "ExactInteger",
                f"scope-{index}",
                "merge",
                "merge",
                "0",
                f"M{index}",
                f"A{index}",
                f"PROOF-EQ-{index}",
            )
        )
        skip_hash = sha256_json(
            {
                "operation_id": "IDENTITY",
                "input_value": merged_value,
                "constraint_root": "CONSTRAINT-ROOT-152",
                "proof_id": f"PROOF-SKIP-{index}",
            }
        )
        engine.register_skip_witness(
            SkipWitness(
                f"SKIP-{index}",
                identity_id,
                "IDENTITY",
                alias_id,
                "CONSTRAINT-ROOT-152",
                authority_root,
                engine.semantic_version,
                f"PROOF-SKIP-{index}",
                skip_hash,
            )
        )
    engine.add_node(
        OperationNode(
            "final",
            "FINALIZE",
            compute=lambda d, deps=tuple(sorted(final_dependencies)): {
                "total": sum(d[node_id] for node_id in deps),
                "branch_count": len(deps),
                "closed": True,
            },
            estimated_cost=Fraction(2, 1),
        )
    )
    for dependency in sorted(final_dependencies):
        engine.add_edge(dependency, "final", EdgeType.CLOSURE_DEPENDS_ON)
    engine.seed("x", 10, provenance={"kind": "INPUT", "name": "x", "value": 10})
    engine.seed("y", 20, provenance={"kind": "INPUT", "name": "y", "value": 20})
    proof = engine.run_until_closed()

    def vm81_admit(candidate: dict, closure_proof: dict) -> dict:
        summary = {
            "authority_root": authority_root,
            "candidate_digest": sha256_json(candidate),
            "closure_digest": sha256_json(closure_proof),
        }
        return {
            "admitted": True,
            "hash72_receipt": sha256_json(summary),
            "authority_audit": {"omega_closure": closure_proof["omega_closure"], "branch_count": branch_count},
            "authoritative_state": {
                "cycle": 1,
                "status": "COMMITTED",
                "final": candidate["values"]["final"],
                "summary": summary,
            },
        }

    commit = engine.commit(vm81_admit)
    replay = engine.replay_receipt()
    metrics = engine.metrics()
    return {
        "engine": engine,
        "proof": proof,
        "commit": commit,
        "replay": replay,
        "metrics": metrics,
        "expected_total": expected_total,
    }


def test_pass148_semantic_batches_scale_without_replay_drift(tmp_path: Path) -> None:
    with _bootstrap_pass148(tmp_path / "pass148-scale.sqlite3") as service:
        small = _run_pass148_batch(service, 8, batch_label="small")
        large = _run_pass148_batch(service, 24, batch_label="large")
    assert small["class_counts"]["DECLARED_SYSTEM_LAW"] >= 2
    assert large["class_counts"]["UNRESOLVED_EXPRESSION"] >= 8
    assert small["contamination_total"] > 0
    assert large["contamination_total"] > small["contamination_total"]
    assert all(result["ok"] for result in small["replay_results"])
    assert all(result["ok"] for result in large["replay_results"])
    large_status = large["status"]
    assert large_status["semantic_registry"]["closed"] is True
    assert large_status["counts"]["semantic_propositions"] >= 34
    small_per_item = small["elapsed_ns"] / (len(small["proposition_ids"]) + 2)
    large_per_item = large["elapsed_ns"] / (len(large["proposition_ids"]) + 2)
    assert large_per_item <= small_per_item * 3.0


def test_pass150_airgap_chain_scales_with_deterministic_integrity(tmp_path: Path) -> None:
    small = _run_pass150_airgap(tmp_path / "pass150-small", event_count=8, payload_scale=2)
    large = _run_pass150_airgap(tmp_path / "pass150-large", event_count=24, payload_scale=4)
    assert small["flushed"] == 8
    assert large["flushed"] == 24
    assert small["recovered"]["records"] == 8
    assert large["recovered"]["records"] == 24
    assert len({record.genome_root for record in small["records"]}) == 8
    assert len({record.genome_root for record in large["records"]}) == 24
    assert all(tuple_value == Base20BigIntCodec.decode(Base20BigIntCodec.encode(tuple_value)) for tuple_value in small["codec_round_trips"])
    assert all(tuple_value == Base20BigIntCodec.decode(Base20BigIntCodec.encode(tuple_value)) for tuple_value in large["codec_round_trips"])
    assert all(echo["requires_vm81_validation"] is True for echo in small["echoes"])
    assert all(echo["mutation_authority"] is False for echo in large["echoes"])
    epoch_lines = [line for line in Path(large["epochs_path"]).read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(epoch_lines) >= 4
    small_per_event = small["elapsed_ns"] / len(small["records"])
    large_per_event = large["elapsed_ns"] / len(large["records"])
    assert large_per_event <= small_per_event * 3.0


@pytest.mark.parametrize("branch_count", [4, 8])
def test_pass152_branch_scaling_preserves_closure_replay_and_efficiency(tmp_path: Path, branch_count: int) -> None:
    result = _build_pass152_scaled_cycle(
        tmp_path / f"pass152-branches-{branch_count}",
        workers=4,
        branch_count=branch_count,
        delay_seconds=0.005,
    )
    final = result["engine"].authoritative_state["final"]
    metrics = result["metrics"]
    assert result["proof"]["omega_closure"] is True
    assert result["replay"]["replay_status"] == "MATCH"
    assert final["branch_count"] == branch_count
    assert final["total"] == result["expected_total"]
    assert metrics["N_reused"] == branch_count
    assert metrics["N_skipped"] == branch_count
    assert metrics["N_committed"] == 1
    assert metrics["max_concurrent_workers_observed"] >= 2
    assert metrics["T_saved_reuse_ns"] > 0
    assert metrics["T_saved_skip_ns"] > 0


def test_pass152_parallel_workers_reduce_wall_time_for_scaled_cycle(tmp_path: Path) -> None:
    single = _build_pass152_scaled_cycle(
        tmp_path / "pass152-single",
        workers=1,
        branch_count=8,
        delay_seconds=0.01,
    )
    parallel = _build_pass152_scaled_cycle(
        tmp_path / "pass152-parallel",
        workers=4,
        branch_count=8,
        delay_seconds=0.01,
    )
    assert single["proof"]["omega_closure"] is True
    assert parallel["proof"]["omega_closure"] is True
    assert single["replay"]["replay_status"] == "MATCH"
    assert parallel["replay"]["replay_status"] == "MATCH"
    assert parallel["metrics"]["max_concurrent_workers_observed"] >= 2
    assert parallel["metrics"]["T_closure_ns"] < single["metrics"]["T_closure_ns"]


def test_pass144_148_150_152_pipeline_produces_integrated_receipt_locked_scale_signal(tmp_path: Path) -> None:
    baseline = _pass144_baseline()
    assert baseline["document_count"] == len(PASS144_DOCS)
    assert baseline["total_doc_bytes"] > 10_000
    assert baseline["lemma_count"] == baseline["unique_lemma_count"] >= 10

    with _bootstrap_pass148(tmp_path / "pipeline-pass148.sqlite3") as service:
        batch = _run_pass148_batch(service, 12, batch_label="pipeline")
        semantic_digest = sha256_json(
            {
                "propositions": batch["proposition_ids"],
                "class_counts": batch["class_counts"],
                "contamination_total": batch["contamination_total"],
            }
        )

    pass150 = _run_pass150_airgap(tmp_path / "pipeline-pass150", event_count=6, payload_scale=3)
    latest_record = pass150["records"][-1]
    assert pass150["recovered"]["records"] == 6

    result = _build_pass152_scaled_cycle(
        tmp_path / "pipeline-pass152",
        workers=4,
        branch_count=4,
        delay_seconds=0.005,
        authority_root=latest_record.genome_root,
        authoritative_state={
            "cycle": 0,
            "status": "OPEN",
            "pass144": baseline,
            "pass148_digest": semantic_digest,
            "pass150_root": latest_record.genome_root,
        },
    )
    final_state = result["engine"].authoritative_state
    assert result["proof"]["omega_closure"] is True
    assert result["replay"]["replay_status"] == "MATCH"
    assert final_state["summary"]["authority_root"] == latest_record.genome_root
    assert final_state["final"]["branch_count"] == 4
    assert final_state["status"] == "COMMITTED"
