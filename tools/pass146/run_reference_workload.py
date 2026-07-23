#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass145.canonical import canonical_json, hash72
from hhs_runtime.pass146.service import HHS146Service

ART = ROOT / "release_artifacts/pass146"
REF = ART / "reference"
RECEIPTS = ART / "receipts"


def clean_db(path: Path) -> None:
    for suffix in ("", "-wal", "-shm", ".pass146-session.json"):
        p = Path(str(path) + suffix)
        if p.exists():
            p.unlink()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def export_receipts(service: HHS146Service, prefix: str) -> list[str]:
    exported = []
    seen = set()
    for receipt in reversed(service.db.list_receipts(10_000)):
        rtype = str(receipt.get("receipt_type", "UNKNOWN_RECEIPT"))
        if rtype in seen:
            continue
        seen.add(rtype)
        name = f"{prefix}_{rtype}.json"
        write_json(RECEIPTS / name, receipt)
        exported.append(name)
    return exported


def main() -> int:
    REF.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    sender_db = REF / "PASS_146_SENDER_REFERENCE.sqlite3"
    receiver_db = REF / "PASS_146_RECEIVER_REFERENCE.sqlite3"
    clean_db(sender_db); clean_db(receiver_db)

    with HHS146Service(sender_db) as sender:
        root = sender.security.bootstrap_local_owner("Reference Sender")
        sid, sgrant, stoken = root["result"]["identity_id"], root["result"]["grant_id"], root["authentication_token"]
        public = sender.security.identity_public_record(sid)

        ingest_contract = sender.security.construct_path(sid, sgrant, stoken, "INGEST_TEXT", {
            "text": "O denotes the HHS operator. π denotes the circular constant. Hash72 preserves witnessed ancestry.",
            "name": "pass146-reference.txt", "namespace": "pass146-reference", "classification": "INTERNAL"
        })
        ingest = sender.security.execute_path(ingest_contract["result"]["contract_id"], sid, stoken)
        query_contract = sender.security.construct_path(sid, sgrant, stoken, "QUERY", {
            "question": "Show every definition of O", "namespace": "pass146-reference", "classification": "INTERNAL"
        })
        query = sender.security.execute_path(query_contract["result"]["contract_id"], sid, stoken)
        negotiation_contract = sender.security.construct_path(sid, sgrant, stoken, "NEGOTIATE_CONFLICT", {
            "left_state": {"claim": "A", "shared": 1}, "right_state": {"claim": "B", "shared": 1},
            "policy": {"winner": "NONE"}, "classification": "INTERNAL"
        })
        negotiation = sender.security.execute_path(negotiation_contract["result"]["contract_id"], sid, stoken)
        propagation_contract = sender.security.construct_path(sid, sgrant, stoken, "PROPAGATE", {
            "data": {"source_id": ingest["result"]["result"]["source_id"], "statement": "O != π"},
            "provenance": {"source_contract_id": ingest_contract["result"]["contract_id"]},
            "source_peer": "reference-sender", "destination_peer": "reference-receiver", "classification": "INTERNAL",
            "expected_destination_state": {"admission": "RECEIVER_BOUNDARY_REQUIRED"}
        }, destination={"kind": "PEER", "id": "reference-receiver"})
        propagated = sender.security.execute_path(propagation_contract["result"]["contract_id"], sid, stoken)
        propagated_result = propagated["result"]["result"]
        envelope = {k: v for k, v in propagated_result.items() if k not in {"status", "payload_detached_from_contract"}}
        write_json(REF / "PASS_146_SIGNED_ENVELOPE.json", envelope)
        sender_replay = {
            "query": sender.security.replay_path(query_contract["result"]["contract_id"]),
            "propagation": sender.security.replay_path(propagation_contract["result"]["contract_id"]),
        }
        sender_integrity = sender.db.integrity_check()
        sender_chain = sender.db.verify_receipt_chain()
        sender_receipts = export_receipts(sender, "SENDER")

    with HHS146Service(receiver_db) as receiver:
        root = receiver.security.bootstrap_local_owner("Reference Receiver")
        rid, rgrant, rtoken = root["result"]["identity_id"], root["result"]["grant_id"], root["authentication_token"]
        trust = receiver.security.trust_peer(rid, rgrant, rtoken, "reference-sender", public["public_key_b64"], classifications=["INTERNAL"], destinations=["reference-receiver"])
        receive_contract = receiver.security.construct_path(rid, rgrant, rtoken, "RECEIVE_PROPAGATION", {
            "envelope": envelope, "source_peer": "reference-sender", "destination_peer": "reference-receiver", "classification": "INTERNAL"
        }, destination={"kind": "PEER", "id": "reference-receiver"})
        received = receiver.security.execute_path(receive_contract["result"]["contract_id"], rid, rtoken)
        receiver_replay = receiver.security.replay_path(receive_contract["result"]["contract_id"])
        message = receiver.security.inspect_message(envelope["message_id"])
        receiver_integrity = receiver.db.integrity_check()
        receiver_chain = receiver.db.verify_receipt_chain()
        receiver_receipts = export_receipts(receiver, "RECEIVER")

    summary = {
        "schema": "HHS_PASS146_REFERENCE_WORKLOAD_V1",
        "sender_database": str(sender_db.relative_to(ROOT)),
        "receiver_database": str(receiver_db.relative_to(ROOT)),
        "sender_contracts": [ingest_contract["result"]["contract_id"], query_contract["result"]["contract_id"], negotiation_contract["result"]["contract_id"], propagation_contract["result"]["contract_id"]],
        "receiver_contract": receive_contract["result"]["contract_id"],
        "signed_message_id": envelope["message_id"],
        "signed_message_hash72": envelope["message_hash72"],
        "signature_valid": message["signature_verification"]["signature_valid"],
        "peer_trust_status": trust["result"]["status"],
        "receiver_status": received["result"]["result"]["status"],
        "conflict_status": negotiation["result"]["result"]["status"],
        "query_replay": sender_replay["query"]["status"],
        "propagation_replay": sender_replay["propagation"]["status"],
        "receiver_replay": receiver_replay["status"],
        "sender_integrity": sender_integrity,
        "receiver_integrity": receiver_integrity,
        "sender_receipt_chain": sender_chain,
        "receiver_receipt_chain": receiver_chain,
        "sender_receipts": sender_receipts,
        "receiver_receipts": receiver_receipts,
        "prior_admission_reused_without_validation": received["result"]["result"]["prior_admission_reused_without_validation"],
    }
    summary["workload_hash72"] = hash72("hhs_pass146_reference_workload_v1", summary)
    write_json(REF / "PASS_146_REFERENCE_WORKLOAD.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
