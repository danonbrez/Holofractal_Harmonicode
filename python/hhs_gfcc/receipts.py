from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .core import (
    CONTRACT_ID,
    IMPLEMENTATION_VERSION,
    INTERPRETATION_VERSION,
    PASS_NUMBER,
    canonical_bytes,
    digest256,
    inherited_hash72,
    stable,
    write_json,
    write_jsonl,
)


def make_receipt(
    operation_id: str,
    sequence: int,
    predecessor: str,
    inputs: Any,
    outputs: Any,
    classification: str = "IMPLEMENTED_AND_EXECUTION_VERIFIED",
    *,
    authority_level: str = "A1",
    error_classification: str | None = None,
    build_identity: str | None = None,
    replay_identity: str | None = None,
) -> dict[str, Any]:
    body = {
        "contract_id": CONTRACT_ID,
        "pass_number": PASS_NUMBER,
        "operation_id": operation_id,
        "deterministic_sequence": int(sequence),
        "authority_level": authority_level,
        "input_digest": digest256(inputs),
        "output_digest": digest256(outputs),
        "predecessor_receipt_digest": predecessor,
        "result_classification": classification,
        "error_classification": error_classification,
        "implementation_version": IMPLEMENTATION_VERSION,
        "interpretation_version": INTERPRETATION_VERSION,
        "build_identity": build_identity,
        "replay_identity": replay_identity,
    }
    body["hash72_witness"] = inherited_hash72(canonical_bytes(body))
    body["receipt_digest"] = digest256(body)
    return stable(body)


def build_receipt_chain(
    operations: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    predecessor = "0" * 64
    receipts: list[dict[str, Any]] = []
    for sequence, operation in enumerate(operations, start=1):
        receipt = make_receipt(
            str(operation["operation_id"]),
            sequence,
            predecessor,
            operation.get("inputs"),
            operation.get("outputs"),
            str(
                operation.get(
                    "classification", "IMPLEMENTED_AND_EXECUTION_VERIFIED"
                )
            ),
            authority_level=str(operation.get("authority_level", "A1")),
            error_classification=operation.get("error_classification"),
            build_identity=operation.get("build_identity"),
            replay_identity=operation.get("replay_identity"),
        )
        receipts.append(receipt)
        predecessor = receipt["receipt_digest"]
    return receipts


def write_named_receipt_set(
    receipts_dir: Path,
    receipt_names: Sequence[str],
    receipts: Sequence[Mapping[str, Any]],
) -> None:
    if len(receipt_names) != len(receipts):
        raise ValueError("receipt name and receipt count mismatch")
    receipts_dir.mkdir(parents=True, exist_ok=True)
    for filename, receipt in zip(receipt_names, receipts, strict=True):
        write_json(receipts_dir / filename, receipt)
    write_jsonl(receipts_dir / "hhs_gfcc_receipts.jsonl", receipts)


def verify_receipt_chain(receipts: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    predecessor = "0" * 64
    expected_sequence = 1
    errors = []
    observed = 0
    terminal = predecessor
    for receipt in receipts:
        observed += 1
        supplied = str(receipt.get("receipt_digest", ""))
        unsigned = {key: value for key, value in receipt.items() if key != "receipt_digest"}
        calculated = digest256(unsigned)
        if supplied != calculated:
            errors.append(
                {
                    "sequence": expected_sequence,
                    "error": "RECEIPT_DIGEST_MISMATCH",
                    "expected": calculated,
                    "observed": supplied,
                }
            )
        if int(receipt.get("deterministic_sequence", 0)) != expected_sequence:
            errors.append(
                {
                    "sequence": expected_sequence,
                    "error": "SEQUENCE_MISMATCH",
                    "observed": receipt.get("deterministic_sequence"),
                }
            )
        if receipt.get("predecessor_receipt_digest") != predecessor:
            errors.append(
                {
                    "sequence": expected_sequence,
                    "error": "PREDECESSOR_MISMATCH",
                    "expected": predecessor,
                    "observed": receipt.get("predecessor_receipt_digest"),
                }
            )
        expected_witness = inherited_hash72(
            canonical_bytes(
                {
                    key: value
                    for key, value in unsigned.items()
                    if key != "hash72_witness"
                }
            )
        )
        if receipt.get("hash72_witness") != expected_witness:
            errors.append(
                {
                    "sequence": expected_sequence,
                    "error": "HASH72_WITNESS_MISMATCH",
                }
            )
        predecessor = supplied
        terminal = supplied
        expected_sequence += 1
    return {
        "valid": not errors,
        "receipt_count": observed,
        "terminal_receipt_digest": terminal if not errors else None,
        "errors": errors,
    }


__all__ = [
    "build_receipt_chain",
    "make_receipt",
    "verify_receipt_chain",
    "write_jsonl",
    "write_named_receipt_set",
]
