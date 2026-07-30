"""Executable dependency-scoped Pass 174 verification and evidence emitter."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from typing import Any, Callable

from hhs_runtime.pass174 import (
    Hash216Array,
    Pass174Runtime,
    PersistentEncryptedVectorStore,
    PhaseCoordinate,
    build_legacy_manifest,
)


class VerificationFailure(AssertionError):
    pass


def _check(name: str, function: Callable[[], Any], results: list[dict[str, Any]]) -> None:
    try:
        evidence = function()
    except Exception as exc:
        results.append({
            "name": name,
            "passed": False,
            "classification": getattr(exc, "classification", type(exc).__name__),
            "detail": str(exc),
        })
        return
    results.append({"name": name, "passed": True, "evidence": evidence})


def verify(repository_root: Path) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    results: list[dict[str, Any]] = []
    manifest = build_legacy_manifest(repository_root)

    def legacy_foundation() -> dict[str, Any]:
        if 173 not in manifest.pass_numbers_present:
            raise VerificationFailure("Pass 173 not present")
        if manifest.maximum_inherited_pass != 173:
            raise VerificationFailure("wrong inherited pass boundary")
        return {
            "specification_count": manifest.specification_count,
            "pass_numbers_present": list(manifest.pass_numbers_present),
            "missing_pass_numbers": list(manifest.missing_pass_numbers),
            "aggregate_root_sha256": manifest.aggregate_root_sha256,
        }

    _check("legacy_specifications_are_minimum_foundation", legacy_foundation, results)

    def geometry() -> dict[str, Any]:
        closure = PhaseCoordinate.at(5184)
        if not closure.full_phase_lock:
            raise VerificationFailure("phase closure absent")
        if (closure.phase64, closure.phase72, closure.phase81, closure.phase5184) != (0, 0, 0, 0):
            raise VerificationFailure("phase closure coordinate mismatch")
        return asdict(closure)

    _check("phase_64_72_81_closes_at_5184", geometry, results)

    with tempfile.TemporaryDirectory(prefix="hhs-pass174-") as temporary:
        state_root = Path(temporary)
        database = state_root / "vectors.sqlite3"
        key_path = state_root / "vectors.key"
        producer_store = PersistentEncryptedVectorStore(database, key_path=key_path)
        producer = Pass174Runtime(legacy_manifest=manifest, vector_store=producer_store)

        direct_holder: dict[str, Any] = {}

        def direct_execution() -> dict[str, Any]:
            result = producer.execute(thread=7, writes={0: 1, 8: 1, 72: 1, 80: -1})
            direct_holder["result"] = result
            if result["path"] != "DIRECT_RUNTIME":
                raise VerificationFailure("direct path not selected")
            hash216 = result["object"]["hash216"]
            if len(hash216["combined"]) != 216 or len(hash216["character_indexes_sha256"]) != 216:
                raise VerificationFailure("Hash216 geometry mismatch")
            if result["object"]["plaintext_exposed"]:
                raise VerificationFailure("plaintext exposed")
            return {
                "classification": result["classification"],
                "operation_key": result["operation_key"],
                "object_id": result["object"]["object_id"],
                "hash216_identity": hash216["logical_identity_sha256"],
                "hash216_index_root": hash216["index_root_sha256"],
                "state_hash72": producer.vmrc.state_hash72,
                "phase": result["phase"],
            }

        _check("direct_vm81_whole_frame_encrypted_admission", direct_execution, results)

        def hash216_reconstruction() -> dict[str, Any]:
            result = direct_holder["result"]
            raw = result["object"]["hash216"]
            candidate = Hash216Array(
                predecessor=raw["predecessor"],
                current=raw["current"],
                successor=raw["successor"],
                combined=raw["combined"],
                character_indexes_sha256=tuple(raw["character_indexes_sha256"]),
                index_root_sha256=raw["index_root_sha256"],
                logical_identity_sha256=raw["logical_identity_sha256"],
            )
            candidate.verify()
            return {
                "characters": len(candidate.combined),
                "indexes": len(candidate.character_indexes_sha256),
                "index_root_sha256": candidate.index_root_sha256,
            }

        _check("hash216_three_lane_positional_index_verification", hash216_reconstruction, results)

        def harmonic_controller() -> dict[str, Any]:
            compiled = producer.register_harmonic_gate(
                connectors=["+", "*", "Or", "=="],
                phase_offsets=[0, 8, 9, 36],
                exact_weights=["1/4", "1/4", "1/4", "1/4"],
            )
            controller = producer.phase_controller()
            if controller["planes_count"] != 3 or controller["directed_relationships_per_plane"] != 144:
                raise VerificationFailure("3:144 controller mismatch")
            return {
                "gate_identity": compiled["gate"]["identity"],
                "controller_planes": controller["planes_count"],
                "directed_relationships_per_plane": controller["directed_relationships_per_plane"],
                "total_directed_relationships": controller["total_directed_relationships"],
            }

        _check("harmonic_gate_and_virtual_qudit_controller", harmonic_controller, results)

        expected_snapshot = producer.vmrc.snapshot().to_bytes()
        expected_hash72 = producer.vmrc.state_hash72
        producer_storage_status = producer_store.storage_status()
        producer_store.close()

        consumer_store = PersistentEncryptedVectorStore(database, key_path=key_path)
        consumer = Pass174Runtime(legacy_manifest=manifest, vector_store=consumer_store)

        def persistent_retrieval() -> dict[str, Any]:
            result = consumer.execute(thread=7, writes={0: 1, 8: 1, 72: 1, 80: -1}, prefer_retrieval=True)
            if result["path"] != "RETRIEVAL":
                raise VerificationFailure("retrieval path not selected")
            if consumer.vmrc.snapshot().to_bytes() != expected_snapshot:
                raise VerificationFailure("retrieved frame mismatch")
            if consumer.vmrc.state_hash72 != expected_hash72:
                raise VerificationFailure("retrieved Hash72 mismatch")
            return {
                "classification": result["classification"],
                "epoch": consumer.vmrc.epoch,
                "state_hash72": consumer.vmrc.state_hash72,
                "persistent_storage": consumer_store.storage_status(),
                "producer_storage": producer_storage_status,
            }

        _check("durable_validated_retrieval_after_restart", persistent_retrieval, results)

        def audit_and_replay() -> dict[str, Any]:
            audit = consumer.audit(challenge="pass174-verifier-post-seal-challenge", deep=True)
            replay = consumer.replay()
            if audit["classification"] != "HHS_PASS_174_AUDIT_PASS":
                raise VerificationFailure("audit did not pass")
            if not replay["receipt_chain_valid"]:
                raise VerificationFailure("receipt chain invalid")
            if not replay["inherited_vmrc_replay"]["deterministic_replay"]:
                raise VerificationFailure("VMRC replay invalid")
            return {
                "audit": {
                    "sample_count": audit["sample_count"],
                    "vector_store_root": audit["vector_store_root"],
                    "challenge_seed": audit["challenge_seed"],
                },
                "replay": replay,
            }

        _check("genesis_audit_and_deterministic_replay", audit_and_replay, results)
        consumer_store.close()

    def visual_assets() -> dict[str, Any]:
        root = repository_root / "applications" / "pass174_visual_ide"
        required = [root / "index.html", root / "styles.css", root / "app.js"]
        missing = [str(path.relative_to(repository_root)) for path in required if not path.is_file()]
        if missing:
            raise VerificationFailure(f"missing visual assets: {missing}")
        text = (root / "index.html").read_text(encoding="utf-8")
        javascript = (root / "app.js").read_text(encoding="utf-8")
        required_markers = ["VM81 3D Manifold", "Hash216", "runPipeline", "pointerdown", "fileDropZone"]
        absent = [marker for marker in required_markers if marker not in text and marker not in javascript]
        if absent:
            raise VerificationFailure(f"missing interface markers: {absent}")
        return {
            "asset_sha256": {
                str(path.relative_to(repository_root)): sha256(path.read_bytes()).hexdigest()
                for path in required
            },
            "browser_execution": "REQUIRES_RUNNING_SERVER_BROWSER_GATE",
            "human_usability_claim": False,
        }

    _check("visual_ide_assets_and_interaction_contract", visual_assets, results)

    def deployment_surface() -> dict[str, Any]:
        required = [
            repository_root / "Procfile",
            repository_root / "deployment" / "pass174" / "Dockerfile",
            repository_root / "deployment" / "pass174" / "start.sh",
            repository_root / "deployment" / "pass174" / "docker-compose.yml",
            repository_root / "hhs_backend" / "pass174_server.py",
        ]
        missing = [str(path.relative_to(repository_root)) for path in required if not path.is_file()]
        if missing:
            raise VerificationFailure(f"missing deployment files: {missing}")
        procfile = (repository_root / "Procfile").read_text(encoding="utf-8")
        if "hhs_backend.pass174_server:app" not in procfile:
            raise VerificationFailure("Procfile does not activate Pass 174")
        return {"files": [str(path.relative_to(repository_root)) for path in required]}

    _check("deterministic_pass174_deployment_surface", deployment_surface, results)

    failures = [item for item in results if not item["passed"]]
    evidence_body = {
        "schema": "HHS_PASS_174_DEPENDENCY_SCOPED_VERIFICATION_V1",
        "repository_root": str(repository_root),
        "legacy_foundation_root_sha256": manifest.aggregate_root_sha256,
        "checks_executed": len(results),
        "checks_passed": len(results) - len(failures),
        "checks_failed": len(failures),
        "results": results,
        "classifications": {
            "static_and_runtime_verification": "PASS" if not failures else "FAIL",
            "browser_end_to_end": "NOT_EXECUTED_BY_THIS_HARNESS",
            "native_cross_architecture": "NOT_EXECUTED_BY_THIS_HARNESS",
            "human_usability": "NOT_CLAIMED",
        },
    }
    evidence_body["evidence_sha256"] = sha256(
        json.dumps(evidence_body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()
    return evidence_body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    evidence = verify(Path(args.repository_root))
    rendered = json.dumps(evidence, sort_keys=True, indent=2, ensure_ascii=False, default=str) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if evidence["checks_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
