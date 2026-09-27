from __future__ import annotations

import json

from hhs_runtime.hhs_filesystem_hash72_ledger_v1 import (
    CHAIN_AUTHORITY,
    GENESIS_HASH72,
    append_filesystem_ledger_entry,
    make_filesystem_ledger_entry,
    verify_filesystem_ledger,
)


def _entry(tmp_path, name: str):
    target = tmp_path / name
    target.write_text(name, encoding="utf-8")
    return make_filesystem_ledger_entry(
        target,
        repo_root=tmp_path,
        event="TEST_PATH",
        hash_existing_content=True,
    )


def test_append_authority_owns_parent_chain(tmp_path):
    ledger = tmp_path / "ledger.json"
    first = _entry(tmp_path, "first.txt")
    second = _entry(tmp_path, "second.txt")

    append_filesystem_ledger_entry(ledger, first)
    payload = append_filesystem_ledger_entry(ledger, second)

    assert payload["entries"][0]["parent_hash72"] == GENESIS_HASH72
    assert payload["entries"][1]["parent_hash72"] == payload["entries"][0]["entry_hash72"]
    assert payload["chain_authority"] == CHAIN_AUTHORITY
    assert verify_filesystem_ledger(ledger)["ok"] is True


def test_legacy_flat_genesis_history_is_deterministically_rebound_on_append(tmp_path):
    ledger = tmp_path / "ledger.json"
    first = _entry(tmp_path, "legacy-a.txt").to_dict()
    second = _entry(tmp_path, "legacy-b.txt").to_dict()
    legacy = {
        "schema": "HHS_FILESYSTEM_HASH72_LEDGER_V1",
        "entries": [first, second],
        "entry_count": 2,
        "tip_hash72": second["entry_hash72"],
        "ledger_hash72": "LEGACY-FLAT-HASH",
    }
    ledger.write_text(json.dumps(legacy), encoding="utf-8")

    third = _entry(tmp_path, "current.txt")
    payload = append_filesystem_ledger_entry(ledger, third)

    assert payload["legacy_chain_repair"]["rebound_entry_count"] >= 1
    assert payload["entries"][1]["parent_hash72"] == payload["entries"][0]["entry_hash72"]
    assert payload["entries"][2]["parent_hash72"] == payload["entries"][1]["entry_hash72"]
    assert verify_filesystem_ledger(ledger)["ok"] is True


def test_verifier_recomputes_entry_hash_and_rejects_payload_tamper(tmp_path):
    ledger = tmp_path / "ledger.json"
    append_filesystem_ledger_entry(ledger, _entry(tmp_path, "tamper.txt"))
    payload = json.loads(ledger.read_text(encoding="utf-8"))
    payload["entries"][0]["relative_path"] = "forged/path.txt"
    ledger.write_text(json.dumps(payload), encoding="utf-8")

    result = verify_filesystem_ledger(ledger)

    assert result["ok"] is False
    assert any(row["reason"] == "entry_hash72 mismatch" for row in result["invalid"])
