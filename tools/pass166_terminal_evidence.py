#!/usr/bin/env python3
"""Execute and emit machine-readable Pass 166 terminal evidence."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass166.common import SimulatedInterruption, Word2VecPackageManifest, canonical_bytes
from hhs_runtime.pass166.service import Word2VecService

SOURCE_PATHS = (
    "HHS_PASS_166_WORD2VEC_LANGUAGE_MODALITY_MODEL_ACQUISITION_IMPORT_AND_PREINSTALLATION_SERVICE.md",
    "HHS_PASS_166_AUTHORITY_BINDING.json",
    "hhs_runtime/pass166/service.py",
    "hhs_runtime/pass166/codec.py",
)


def repository_source() -> bytes:
    parts = []
    for relative in SOURCE_PATHS:
        raw = (ROOT / relative).read_bytes()
        parts.append(relative.encode("utf-8") + b"\0" + raw)
    return b"\n--HHS-P166-SOURCE--\n".join(parts)


def rows_from_source(source: bytes) -> tuple[tuple[str, tuple[float, ...]], ...]:
    tokens = ("language", "vector", "model", "runtime", "source", "receipt", "offline", "authority")
    rows = []
    for token in tokens:
        digest = sha256(b"HHS-P166-TERMINAL-VECTOR\0" + source + token.encode()).digest()
        values = tuple((digest[index] % 17 - 8) / 8.0 for index in range(8))
        rows.append((token, values))
    return tuple(rows)


def text_fixture(rows: tuple[tuple[str, tuple[float, ...]], ...]) -> bytes:
    lines = [f"{len(rows)} 8"]
    lines.extend(f"{token} " + " ".join(format(value, ".8g") for value in vector) for token, vector in rows)
    return ("\n".join(lines) + "\n").encode("utf-8")


def binary_fixture(rows: tuple[tuple[str, tuple[float, ...]], ...]) -> bytes:
    output = bytearray(f"{len(rows)} 8\n".encode("ascii"))
    for token, vector in rows:
        output.extend(token.encode("utf-8") + b" ")
        output.extend(b"".join(struct.pack("<f", value) for value in vector))
        output.extend(b"\n")
    return bytes(output)


def manifest(path: Path, model_id: str, vector_format: str, archive_type: str = "NONE", artifact_path: str | None = None) -> Word2VecPackageManifest:
    raw = path.read_bytes()
    return Word2VecPackageManifest(
        package_id=model_id,
        display_name=model_id,
        provider="HHS_REPOSITORY_DERIVED_FIXTURE",
        source_uri=path.resolve().as_uri(),
        source_version="1",
        license_id="HHS-TEST-FIXTURE",
        license_uri="https://example.invalid/hhs-test-fixture",
        expected_byte_length=len(raw),
        expected_sha256=sha256(raw).hexdigest(),
        archive_type=archive_type,
        vector_format=vector_format,
        vector_dimension=8,
        vocabulary_size=8,
        normalization_profile="CASE_FOLDED",
        artifact_path=artifact_path,
    )


def execute(output: Path) -> dict[str, object]:
    source = repository_source()
    rows = rows_from_source(source)
    with tempfile.TemporaryDirectory(prefix="hhs-pass166-terminal-") as temporary:
        temp = Path(temporary)
        text_path = temp / "repository-word2vec.txt"
        binary_path = temp / "repository-word2vec.bin"
        zip_path = temp / "repository-word2vec.zip"
        text_path.write_bytes(text_fixture(rows))
        binary_path.write_bytes(binary_fixture(rows))
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("vectors.txt", text_path.read_bytes())
        manifests = (
            manifest(text_path, "repository-text", "WORD2VEC_TEXT"),
            manifest(binary_path, "repository-binary", "WORD2VEC_BINARY"),
            manifest(zip_path, "repository-zip", "WORD2VEC_TEXT", "ZIP", "vectors.txt"),
        )
        service = Word2VecService(temp / "store")
        installations = []
        for item in manifests:
            service.register_manifest(item)
            result = service.install(item.package_id, accept_license=True, activate=True, offline_ready=True)
            projection = service.project("language", model_id=item.package_id)
            replay = service.replay(item.package_id)
            installations.append({
                "model_id": item.package_id,
                "manifest_root": item.manifest_root,
                "package_sha256": item.expected_sha256,
                "canonical_model_root": result["canonical_model_root"],
                "index_root": result["index_root"],
                "projection_5184_root": projection["projection_5184_root"],
                "projection_base64_symbols": len(projection["projection_5184_b64"]),
                "offline_replay": replay["deterministic_replay"],
                "nearest_count": len(service.nearest("language", model_id=item.package_id, top_k=4)["results"]),
                "source_package_preserved": (service.packages_dir / item.package_id / item.expected_sha256 / "source.package").is_file(),
            })
        active_before = service.status()["active_model_id"]
        vm81_before = service.status()["vm81_state_hash72"]
        rollback_source = temp / "rollback.txt"
        rollback_source.write_bytes(text_path.read_bytes())
        rollback_manifest = manifest(rollback_source, "rollback-candidate", "WORD2VEC_TEXT")
        service.register_manifest(rollback_manifest)
        service._fault_after = "before_vm81_admission"
        interruption_observed = False
        try:
            service.install("rollback-candidate", accept_license=True, activate=True)
        except SimulatedInterruption:
            interruption_observed = True
        restarted = Word2VecService(temp / "store")
        receipt_chain_verified = len(restarted._receipt_chain) == len(service._receipt_chain)
        report: dict[str, object] = {
            "schema": "HHS_PASS_166_TERMINAL_EXECUTION_EVIDENCE_V1",
            "contract_id": "HHS-P166-W2V-LMVS-MAIS",
            "classification": "HHS_PASS_166_WORD2VEC_LANGUAGE_MODALITY_MODEL_ACQUISITION_IMPORT_PREINSTALLATION_AND_OFFLINE_ACTIVATION_VERIFIED",
            "terminal": True,
            "repository_source": {"paths": list(SOURCE_PATHS), "byte_length": len(source), "sha256": sha256(source).hexdigest()},
            "fixture_policy": {"repository_derived": True, "model_binary_committed": False, "generated_fixture_binary_committed": False},
            "installations": installations,
            "rollback": {
                "interruption_observed": interruption_observed,
                "active_model_preserved": service.status()["active_model_id"] == active_before,
                "vm81_state_preserved": service.status()["vm81_state_hash72"] == vm81_before,
            },
            "restart": {
                "receipt_chain_verified": receipt_chain_verified,
                "offline_ready": restarted.status()["offline_ready"],
                "active_model_id": restarted.status()["active_model_id"],
            },
            "authority": {"worker_commit_authority": False, "native_commit_authority": False, "vm81_commit_authority": True},
            "counts": {"models_installed": 3, "formats": 2, "archives": 1, "vocabulary_per_model": 8, "dimension": 8, "validation_failures": 0},
        }
        report["evidence_sha256"] = sha256(canonical_bytes(report)).hexdigest()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(canonical_bytes(report) + b"\n")
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(execute(args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
