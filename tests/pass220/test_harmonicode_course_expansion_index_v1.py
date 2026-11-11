#!/usr/bin/env python3
"""Read-only expansion index validator; never mints VM81/Hash72/Hash216 authority."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "contracts/pass220/HARMONICODE_COURSE_EXPANSION_INDEX_V1.json"
PATTERN = re.compile(r"^#{1,4}\s+(?:Module|MODULE)\s+(\d+)\s*[—–-]\s*(.*)$", re.MULTILINE)

def validate() -> dict:
    packet = json.loads(INDEX.read_text(encoding="utf-8"))
    assert packet["schema"] == "HHS_HARMONICODE_COURSE_EXPANSION_INDEX_V1"
    source = ROOT / packet["source"]["path"]
    body = source.read_text(encoding="utf-8")
    digest = subprocess.check_output(["git", "hash-object", "--", str(source)],cwd=ROOT,text=True).strip()
    assert digest == packet["source"]["git_blob_sha"], "SOURCE_BLOB_DRIFT"
    headings = [(int(match.group(1)), match.group(0),match.start()) for match in PATTERN.finditer(body)]
    numbers = [n for n,_,_ in headings]
    assert numbers == sorted(set(numbers)), "DUPLICATED_OR_UNORDERED_MODULES"
    assert len(numbers) == packet["present_module_count"] == 191
    assert numbers == list(range(191)), "MODULE_SEQUENCE_INCOMPLETE"
    assert packet["missing_modules"] == []
    assert len(packet["modules"]) == len(headings)
    for n in (139, 140, 190):
        assert any(r["number"] == n for r in packet["modules"]), ("RESTORED_MODULE_MISSING", n)
    assert "ExactNumericalTrace == not executable from the supplied packet" in body
    assert "RotationAloneAnnihilatesNonzeroResidual == false" in body
    assert "PolynomialGCD(F,G) = x² + 1" in body
    assert "GlobalNativeEndToEndAdmission == not established" in body
    for record, (number, heading, offset) in zip(packet["modules"], headings):
        assert record["number"] == number
        assert record["id"] == f"HHC-M{number:03d}"
        assert record["source_heading"] == heading
        assert record["start_line"] == body.count("\n", 0, offset) + 1
        assert record["provenance"] == ("RECONSTRUCTED_NOT_VERBATIM" if 15 <= number <= 26 else "UPLOADED_SOURCE")
        assert record["proof_admitted"] is False
        assert record["canonical_runtime_admitted"] is False
    legacy = ROOT / packet["source"]["legacy_course_path"]
    assert legacy.exists() and "Module 123" in legacy.read_text(encoding="utf-8")
    assert (ROOT / packet["source"]["legacy_crosswalk"]).is_file()
    flags=packet["authority"]
    assert flags["course_source_index_only"] is True
    assert flags["existing_source_freeze_unchanged"] is True
    for key in ("automatic_proof_promotion", "canonical_vm81_mutation", "canonical_hash72_mint", "canonical_hash216_mint"):
        assert flags[key] is False
    return {"present_modules":len(headings),"missing_modules":[],"source_blob":digest}

def test_expanded_harmonicode_course_index() -> None:
    validate()

if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
