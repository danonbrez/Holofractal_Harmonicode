"""Genuine Pass 174/VM81 authority adapter for Pass 183."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from typing import Any, Mapping, Protocol

from .core import AUTHORITY_ID, Pass174Runtime, Pass183Error, _canonical, _fraction_string, _hash72


class Authority(Protocol):
    def status(self) -> Mapping[str, Any]: ...
    def execute(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def replay(self) -> Mapping[str, Any]: ...


class ProbabilityVM81Authority:
    """P183 receipt adapter over the inherited Pass 174/163 singleton VM81."""

    def __init__(self, authority: Authority | None = None) -> None:
        if authority is None:
            if Pass174Runtime is None:
                raise Pass183Error("P183_INTERNAL_ERROR", "genuine_pass174_authority_unavailable")
            authority = Pass174Runtime()
        self.authority = authority

    def status(self) -> dict[str, Any]:
        return {
            "classification": "HHS_PASS_183_VM81_AUTHORITY_READY",
            "authority": AUTHORITY_ID,
            "singleton_vm81": True,
            "inherited": dict(self.authority.status()),
        }

    def commit(self, *, operation_identity: str, hash216_identity: str, exact_result: Fraction) -> dict[str, Any]:
        digest = sha256(
            b"P183-VM81-COMMIT\0"
            + bytes.fromhex(operation_identity)
            + bytes.fromhex(hash216_identity)
            + _fraction_string(exact_result).encode("ascii")
        ).digest()
        writes = {index: (1 if byte & 1 else -1) for index, byte in enumerate(digest[:16])}
        inherited = self.authority.execute(
            thread=0,
            writes=writes,
            operation="VMRC_COMMIT",
            capability_scope="P183_PROBABILITY_HYDRATION",
            prefer_retrieval=True,
        )
        payload = {
            "schema": "P183_VM81_ADMISSION_RECEIPT_V1",
            "authority": AUTHORITY_ID,
            "operation_identity_sha256": operation_identity,
            "hash216_identity_sha256": hash216_identity,
            "exact_result": _fraction_string(exact_result),
            "vmrc_operation_class": "VMRC_COMMIT",
            "capability_scope": "P183_PROBABILITY_HYDRATION",
            "inherited_classification": inherited.get("classification"),
            "inherited_operation_key": inherited.get("operation_key"),
            "mutation_authority": True,
        }
        receipt_hash72 = _hash72(payload, _canonical(inherited))
        return {
            "classification": "HHS_PASS_183_SINGLETON_VM81_ADMITTED",
            "payload": payload,
            "receipt_hash72": receipt_hash72,
            "receipt_sha256": sha256(
                b"P183-VM81-RECEIPT\0" + receipt_hash72.encode("ascii") + _canonical(payload)
            ).hexdigest(),
            "inherited": dict(inherited),
        }

    def replay(self) -> dict[str, Any]:
        return {
            "classification": "HHS_PASS_183_VM81_AUTHORITY_REPLAY",
            "inherited": dict(self.authority.replay()),
            "singleton_vm81": True,
        }


@dataclass(frozen=True)
class EvaluationRecord:
    request: Mapping[str, Any]
    evaluation: Mapping[str, Any]
    receipt: Mapping[str, Any]
    authority_receipt: Mapping[str, Any]
