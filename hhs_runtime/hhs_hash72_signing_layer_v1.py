"""
HHS Hash72 Signing Layer v1
===========================

Provides a deterministic signing/stamping layer for final acceptance receipts.
This is not asymmetric crypto; it is a structural signature derived from the
final system state.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass(frozen=True)
class Hash72Signature:
    subject: str
    signature_hash72: str
    payload_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def sign_payload(subject: str, payload: Dict[str, Any]) -> Hash72Signature:
    payload_hash72 = hash72_digest(("hhs_sign_payload_v1", payload), width=24)
    signature_hash72 = hash72_digest(("hhs_signature_v1", subject, payload_hash72), width=24)
    return Hash72Signature(subject=subject, signature_hash72=signature_hash72, payload_hash72=payload_hash72)


def verify_signature(subject: str, payload: Dict[str, Any], signature: Dict[str, Any]) -> bool:
    expected = sign_payload(subject, payload)
    return (
        signature.get("subject") == expected.subject
        and signature.get("payload_hash72") == expected.payload_hash72
        and signature.get("signature_hash72") == expected.signature_hash72
    )


if __name__ == "__main__":
    print(sign_payload("test", {"ok": True}).to_dict())
