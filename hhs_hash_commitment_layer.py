# hhs_hash_commitment_layer.py

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict
import json

def canonical_json(obj: Any) -> str:
    def encode(x):
        if isinstance(x, Fraction):
            return {"Fraction": [x.numerator, x.denominator]}
        if isinstance(x, dict):
            return {str(k): encode(v) for k, v in sorted(x.items())}
        if isinstance(x, (list, tuple)):
            return [encode(v) for v in x]
        return x

    return json.dumps(encode(obj), sort_keys=True, separators=(",", ":"))

def hash72(payload: Any) -> str:
    data = canonical_json(payload)
    acc = 0
    alphabet = "1234567890abcdefghijklmnopqrstuvwxyxzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()^√=≠"
    for ch in data:
        acc = (acc * 72 + ord(ch)) % (72 ** 12)
    out = []
    for _ in range(12):
        out.append(alphabet[acc % 72])
        acc //= 72
    return "H72N-" + "".join(reversed(out))

@dataclass(frozen=True)
class HashCommitmentReceipt:
    phase: int
    operation: str
    input_hash72: str
    pre_state_hash72: str
    operation_hash72: str
    post_state_hash72: str
    witness_hash72: str
    receipt_hash72: str
    gate_status: str
    locked: bool

class HashCommitmentLayer:
    def __init__(self, phase: int = 0):
        self.phase = phase
        self.receipts = []

    def commit_transition(
        self,
        *,
        operation: str,
        input_payload: Any,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        witness: Dict[str, Any],
        gate_status: str,
    ) -> HashCommitmentReceipt:

        input_hash = hash72(input_payload)
        pre_hash = hash72(pre_state)
        op_hash = hash72({"operation": operation, "input_hash72": input_hash})
        post_hash = hash72(post_state)
        witness_hash = hash72(witness)

        receipt_core = {
            "phase": self.phase,
            "operation": operation,
            "input_hash72": input_hash,
            "pre_state_hash72": pre_hash,
            "operation_hash72": op_hash,
            "post_state_hash72": post_hash,
            "witness_hash72": witness_hash,
            "gate_status": gate_status,
            "locked": gate_status == "LOCKED",
        }

        receipt_hash = hash72(receipt_core)

        receipt = HashCommitmentReceipt(
            **receipt_core,
            receipt_hash72=receipt_hash,
        )

        if receipt.locked and not receipt.receipt_hash72:
            raise RuntimeError("LOCKED state missing receipt_hash72")

        if not receipt.witness_hash72:
            raise RuntimeError("Transition missing witness_hash72")

        self.receipts.append(receipt)
        self.phase = (self.phase + 1) % 72
        return receipt
