from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
import json
import time

from .canonical import hash72, hash216, stable
from .journal import append_jsonl

GENESIS_TIP = hash72({"contract": "HHS-P172-UCEOCI-DRVBRAS", "receipt": "genesis"}, domain="HHS-P172-RECEIPT-GENESIS-V1")


class ReceiptError(ValueError):
    pass


@dataclass(frozen=True)
class InstallationReceipt:
    receipt_class: str
    sequence: int
    prior_tip: str
    operation: str
    requested_profile: str
    resolved_profile: str
    plan_identity: str
    platform: str
    architecture: str
    mutation_scope: tuple[str, ...]
    result: str
    failure_classification: str | None
    output_identities: Mapping[str, str]
    installation_identity: str | None
    execution_metadata: Mapping[str, Any]
    created_unix_ns: int
    receipt_identity: str
    receipt_tip: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class ReceiptChain:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.receipts: list[InstallationReceipt] = []
        if self.path.exists():
            self.receipts = self._load(self.path)

    @property
    def tip(self) -> str:
        return self.receipts[-1].receipt_tip if self.receipts else GENESIS_TIP

    @property
    def next_sequence(self) -> int:
        return len(self.receipts) + 1

    def append(
        self,
        *,
        receipt_class: str,
        operation: str,
        requested_profile: str,
        resolved_profile: str,
        plan_identity: str,
        platform: str,
        architecture: str,
        mutation_scope: tuple[str, ...] = (),
        result: str,
        failure_classification: str | None = None,
        output_identities: Mapping[str, str] | None = None,
        installation_identity: str | None = None,
        execution_metadata: Mapping[str, Any] | None = None,
    ) -> InstallationReceipt:
        if result not in {"SUCCESS", "FAILURE", "BLOCKED", "NOOP"}:
            raise ReceiptError("P172_RECEIPT_RESULT_INVALID")
        sequence = self.next_sequence
        created = time.time_ns()
        body = {
            "domain": "HHS-P172-INSTALLATION-RECEIPT-BODY-V1",
            "receipt_class": receipt_class,
            "sequence": sequence,
            "prior_tip": self.tip,
            "operation": operation,
            "requested_profile": requested_profile,
            "resolved_profile": resolved_profile,
            "plan_identity": plan_identity,
            "platform": platform,
            "architecture": architecture,
            "mutation_scope": list(mutation_scope),
            "result": result,
            "failure_classification": failure_classification,
            "output_identities": dict(sorted((output_identities or {}).items())),
            "installation_identity": installation_identity,
            "execution_metadata": stable(execution_metadata or {}),
            "created_unix_ns": created,
        }
        receipt_identity = hash216(body, domain="HHS-P172-INSTALLATION-RECEIPT-IDENTITY-V1")
        receipt_tip = hash72(
            {"prior_tip": self.tip, "receipt_identity": receipt_identity, "sequence": sequence},
            domain="HHS-P172-INSTALLATION-RECEIPT-TIP-V1",
        )
        receipt = InstallationReceipt(
            receipt_class=receipt_class,
            sequence=sequence,
            prior_tip=self.tip,
            operation=operation,
            requested_profile=requested_profile,
            resolved_profile=resolved_profile,
            plan_identity=plan_identity,
            platform=platform,
            architecture=architecture,
            mutation_scope=tuple(mutation_scope),
            result=result,
            failure_classification=failure_classification,
            output_identities=dict(output_identities or {}),
            installation_identity=installation_identity,
            execution_metadata=dict(execution_metadata or {}),
            created_unix_ns=created,
            receipt_identity=receipt_identity,
            receipt_tip=receipt_tip,
        )
        append_jsonl(self.path, receipt.to_dict())
        self.receipts.append(receipt)
        return receipt

    @staticmethod
    def _load(path: Path) -> list[InstallationReceipt]:
        receipts: list[InstallationReceipt] = []
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw_line.strip():
                continue
            try:
                payload = json.loads(raw_line)
                receipt = InstallationReceipt(**payload)
            except Exception as exc:
                raise ReceiptError(f"P172_RECEIPT_PARSE_FAILURE:{line_number}") from exc
            receipts.append(receipt)
        ReceiptChain.verify(receipts)
        return receipts

    @staticmethod
    def verify(receipts: list[InstallationReceipt]) -> None:
        prior = GENESIS_TIP
        for expected_sequence, receipt in enumerate(receipts, start=1):
            if receipt.sequence != expected_sequence:
                raise ReceiptError("P172_RECEIPT_SEQUENCE_MISMATCH")
            if receipt.prior_tip != prior:
                raise ReceiptError("P172_RECEIPT_PARENT_MISMATCH")
            body = {
                "domain": "HHS-P172-INSTALLATION-RECEIPT-BODY-V1",
                "receipt_class": receipt.receipt_class,
                "sequence": receipt.sequence,
                "prior_tip": receipt.prior_tip,
                "operation": receipt.operation,
                "requested_profile": receipt.requested_profile,
                "resolved_profile": receipt.resolved_profile,
                "plan_identity": receipt.plan_identity,
                "platform": receipt.platform,
                "architecture": receipt.architecture,
                "mutation_scope": list(receipt.mutation_scope),
                "result": receipt.result,
                "failure_classification": receipt.failure_classification,
                "output_identities": dict(sorted(receipt.output_identities.items())),
                "installation_identity": receipt.installation_identity,
                "execution_metadata": stable(receipt.execution_metadata),
                "created_unix_ns": receipt.created_unix_ns,
            }
            identity = hash216(body, domain="HHS-P172-INSTALLATION-RECEIPT-IDENTITY-V1")
            tip = hash72(
                {"prior_tip": prior, "receipt_identity": identity, "sequence": receipt.sequence},
                domain="HHS-P172-INSTALLATION-RECEIPT-TIP-V1",
            )
            if identity != receipt.receipt_identity or tip != receipt.receipt_tip:
                raise ReceiptError("P172_RECEIPT_IDENTITY_MISMATCH")
            prior = receipt.receipt_tip
