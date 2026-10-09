"""Freeze authentic V4 source-general native CI diagnostic receipt without authority promotion."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "evidence/pass220/PASS220_V4_40_GATE_REPLAY_PREFLIGHT_37946520150.json"
SOURCE = ROOT / "contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode"


def _read() -> dict:
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def _gates(data: bytes):
    depth, out, i = 0, [], 0
    while i < len(data):
        if data[i:i+1] == b"(":
            depth += 1
        elif data[i:i+1] == b")":
            depth -= 1
            assert depth >= 0
        elif data[i:i+2] == b"==":
            out.append((i, depth))
            i += 1
        i += 1
    assert depth == 0
    return out


def _check(record: dict, data: bytes):
    assert record["schema"] == "HHS_PASS220_V4_NONCANONICAL_SOURCE_GENERAL_REPLAY_PREFLIGHT_EVIDENCE_V1"
    assert len(data) == record["source_bytes"] == 527
    digest = sha256(data).digest()
    assert record["source_sha256"] == digest.hex()
    assert len(record["source_hash216"]) == 216
    locations = _gates(data)
    assert len(locations) == record["gate_count"] == 40
    assert record["outer_gate_offsets"] == [offset for offset,depth in locations if depth == 0] == [253,256]
    assert len(record["gates"]) == 40
    for index,(gate,(offset,depth)) in enumerate(zip(record["gates"],locations)):
        assert gate["index"] == index
        assert gate["offset"] == offset
        assert gate["parenthesis_depth"] == depth
        assert gate["truth"] == "UNRESOLVED"
        expected_hash = sha256(
            b"GATE" + digest + index.to_bytes(4,"big") + offset.to_bytes(4,"big")
        ).hexdigest()
        assert gate["occurrence_sha256"] == expected_hash
    e = record["execution"]
    assert e["mode"] == "HHS159_MODE_EXECUTE_AND_HOLD"
    assert e["commit_policy"] == e["hold_status"] == e["native_replay_status"] == 0
    assert e["native_hold_vm81_steps"] > 0
    assert e["replay_semantic_root_equal"] and e["interpreter_compiler_match"]
    assert e["interpreter_compiler_status"] == 0
    assert e["fallback_used"] is False
    assert len(e["native_hold_receipt_hash216"]) == 216
    assert len(e["native_replay_receipt_hash216"]) == 216
    p = record["proof"]
    assert p["global_gate_truth"] == "UNRESOLVED"
    assert all(v is False for name,v in p.items() if name != "global_gate_truth")
    assert record["negative_mutation"] == "FAIL_CLOSED_REJECTED_AT_SOURCE_OCCURRENCE_MEMBRANE"
    assert record["classification"] == "NONCANONICAL_SOURCE_GENERAL_REPLAY_PREFLIGHT_VERIFIED"


def test_every_native_occurrence_bound_to_exact_source() -> None:
    _check(_read(),SOURCE.read_bytes())


def test_modified_source_does_not_inherit_receipt() -> None:
    data=SOURCE.read_bytes()
    changed=data.replace(b"==x==-y*(",b"==-y==x*(",1)
    assert changed != data
    import pytest
    with pytest.raises(AssertionError):
        _check(_read(),changed)


def test_reversed_gate_identity_is_rejected() -> None:
    record=_read()
    record["gates"][0],record["gates"][1]=record["gates"][1],record["gates"][0]
    import pytest
    with pytest.raises(AssertionError):
        _check(record,SOURCE.read_bytes())


def test_fabricated_true_gate_is_not_proof() -> None:
    record=_read()
    record["gates"][39]["truth"]="TRUE"
    import pytest
    with pytest.raises(AssertionError):
        _check(record,SOURCE.read_bytes())


def test_canonical_authority_escalation_detected() -> None:
    record=_read()
    record["proof"]["canonical_vm81_admission_verified"]=True
    import pytest
    with pytest.raises(AssertionError):
        _check(record,SOURCE.read_bytes())
