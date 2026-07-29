from __future__ import annotations

from pathlib import Path
import json

from hhs_verification.pass173.coverage_matrix import CoverageMatrix, RequirementStatus


def test_traceability_load_and_terminal_gate(tmp_path: Path) -> None:
    traceability = tmp_path / "traceability.json"
    traceability.write_text(
        json.dumps(
            {
                "mappings": [
                    {
                        "requirement_ids": ["P172-A", "P173-B"],
                        "implementation_paths": ["a.py"],
                        "test_paths": ["test_a.py"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    matrix = CoverageMatrix.from_traceability(traceability)
    complete, incomplete = matrix.verify_terminal_coverage()
    assert complete is False
    assert len(incomplete) == 2

    for requirement_id in ("P172-A", "P173-B"):
        matrix.update(
            requirement_id,
            status=RequirementStatus.VERIFIED,
            positive_evidence=(f"positive:{requirement_id}",),
            negative_evidence=(f"negative:{requirement_id}",),
        )
    complete, incomplete = matrix.verify_terminal_coverage()
    assert complete is True
    assert incomplete == []
    assert matrix.to_dict()["matrix_identity"]


def test_not_applicable_requires_justification(tmp_path: Path) -> None:
    traceability = tmp_path / "traceability.json"
    traceability.write_text(
        json.dumps(
            {
                "mappings": [
                    {
                        "requirement_ids": ["P173-HARDWARE"],
                        "implementation_paths": ["gpu.py"],
                        "test_paths": ["test_gpu.py"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    matrix = CoverageMatrix.from_traceability(traceability)
    matrix.update(
        "P173-HARDWARE",
        status=RequirementStatus.NOT_APPLICABLE_WITH_JUSTIFICATION,
        justification="No real supported GPU runner is available; terminal GPU support remains unclaimed.",
    )
    assert matrix.verify_terminal_coverage() == (True, [])
