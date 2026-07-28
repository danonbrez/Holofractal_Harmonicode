#!/usr/bin/env python3
"""Execute and emit machine-readable Pass 165 terminal evidence."""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile

from hhs_runtime.pass165.durability import DurableMultimodalLearningService, SimulatedInterruption
from hhs_runtime.pass165.ingestion import MultimodalLearningService, canonical_bytes

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tests" / "pass165_real_fixture_corpus.py"
SPEC = importlib.util.spec_from_file_location("pass165_real_fixture_corpus", HELPER)
assert SPEC and SPEC.loader
FIXTURES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURES)


def execute(output: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="hhs-pass165-terminal-") as temporary:
        temp = Path(temporary)
        source = FIXTURES.repository_source(ROOT)
        corpus = FIXTURES.build_corpus(ROOT, temp / "corpus")
        validators = {
            "PDF": FIXTURES.validate_pdf(corpus["PDF"]),
            "IMAGE": FIXTURES.validate_png(corpus["IMAGE"]),
            "AUDIO": FIXTURES.validate_wav(corpus["AUDIO"]),
            "VIDEO": FIXTURES.validate_mp4(corpus["VIDEO"], temp / "validated"),
        }
        service = MultimodalLearningService()
        ingestions = []
        for modality in ("PDF", "IMAGE", "AUDIO", "VIDEO"):
            raw = corpus[modality]
            result = service.ingest_source(
                raw,
                declared_media_type=modality,
                provenance=f"repository-derived-terminal-fixture:{modality}",
                authorization_scope="P165_TERMINAL_FIXTURE_INGEST",
            )
            source_hash = sha256(raw).hexdigest()
            ingestions.append(
                {
                    "modality": modality,
                    "source_hash": source_hash,
                    "source_preserved": service._sources[source_hash].source_bytes == raw,
                    "token_count": result["token_count"],
                    "chunk_count": result["chunk_count"],
                    "projection_hash72": result["projection_hash72"],
                    "receipt_hash72": result["receipt"]["receipt_hash72"],
                    "ingestion_operation_hash216": service._results[source_hash].ingestion_operation_hash216,
                }
            )
        replay = service.replay_ingestion()

        store = temp / "durable"
        durable = DurableMultimodalLearningService(store)
        for index in (1, 2):
            durable.ingest_source(
                f"terminal durable {index}\nvalue_{index} = {index}\nalpha alpha".encode(),
                declared_media_type="TEXT",
                provenance=f"repository-terminal-durable:{index}",
                authorization_scope="P165_DURABLE_RECOVERY_TEST",
            )
        interrupted = DurableMultimodalLearningService(store)
        interrupted._fault_after = "after_journal_fsync"
        interruption_observed = False
        try:
            interrupted.ingest_source(
                b"terminal durable 3\nvalue_3 = 3\nalpha alpha",
                declared_media_type="TEXT",
                provenance="repository-terminal-durable:3",
                authorization_scope="P165_DURABLE_RECOVERY_TEST",
            )
        except SimulatedInterruption:
            interruption_observed = True
        recovered = DurableMultimodalLearningService(store)
        recovery = recovered.recover_durable_state()
        durable_replay = recovered.replay_ingestion()

        report: dict[str, object] = {
            "schema": "HHS_PASS_165_TERMINAL_EXECUTION_EVIDENCE_V1",
            "contract_id": "HHS-P165-L5184-MMVS-ITIBP",
            "classification": "HHS_PASS_165_LIGHTWEIGHT_5184BIT_MULTIMODAL_VECTOR_STORE_INGESTION_TOKENIZATION_INVARIANT_EXTRACTION_AND_GOVERNED_BACKPROPAGATION_VERIFIED",
            "terminal": True,
            "repository_source": {
                "paths": list(FIXTURES.SOURCE_PATHS),
                "byte_length": len(source),
                "sha256": sha256(source).hexdigest(),
            },
            "real_format_validators": validators,
            "ingestions": ingestions,
            "multimodal_replay": replay,
            "durability": {
                "interruption_observed": interruption_observed,
                "recovery": recovery,
                "replay": durable_replay,
                "journal_sha256": sha256(recovered.journal_path.read_bytes()).hexdigest(),
                "frontier_sha256": sha256(recovered.head_path.read_bytes()).hexdigest(),
            },
            "authority": {
                "worker_commit_authority": False,
                "vm81_commit_authority": True,
            },
        }
        report["evidence_sha256"] = sha256(canonical_bytes(report)).hexdigest()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(canonical_bytes(report) + b"\n")
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = execute(args.output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
