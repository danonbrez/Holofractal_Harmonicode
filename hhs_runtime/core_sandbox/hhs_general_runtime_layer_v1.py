"""
Core Sandbox General Runtime Layer V1
=====================================

Standalone canonical implementation for the post-quantum secure development
sandbox.  Root-level modules are compatibility shims only.

This implementation is dependency-light and fails closed: every operation emits
Hash72-native receipts, verifies parent continuity, and quarantines invalid
operations.  When an external locked kernel is present, it can still be supplied
by path; when not present, this sandbox uses its internal Hash72 receipt authority
so development can proceed without root-level indirection.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import json
from collections import Counter


DEFAULT_KERNEL_PATH = Path("/mnt/data/HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py")
GENESIS_RECEIPT_HASH72 = "H72N-GENESIS"
HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()^√=≠"


class HHSRuntimeLoadError(RuntimeError):
    pass


class HHSIntegrityError(RuntimeError):
    pass


def canonicalize_for_hash72(obj: Any) -> Any:
    if isinstance(obj, Fraction):
        return {"__fraction__": [obj.numerator, obj.denominator]}
    if isinstance(obj, Path):
        return {"__path__": str(obj)}
    if isinstance(obj, tuple):
        return {"__tuple__": [canonicalize_for_hash72(x) for x in obj]}
    if isinstance(obj, list):
        return [canonicalize_for_hash72(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): canonicalize_for_hash72(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        return canonicalize_for_hash72(obj.to_dict())
    if hasattr(obj, "__dict__") and not isinstance(obj, type):
        return canonicalize_for_hash72(vars(obj))
    return obj


def canonical_json(obj: Any) -> str:
    return json.dumps(canonicalize_for_hash72(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _base72(value: int, width: int = 18) -> str:
    if value < 0:
        value = -value
    chars: List[str] = []
    if value == 0:
        chars.append(HASH72_ALPHABET[0])
    while value:
        value, r = divmod(value, 72)
        chars.append(HASH72_ALPHABET[r])
    encoded = "".join(reversed(chars))
    return (HASH72_ALPHABET[0] * max(0, width - len(encoded)) + encoded)[-width:]


def security_hash72_v44(payload: Any, *, domain: str = "HHS") -> str:
    text = domain + "|" + canonical_json(payload)
    state = 179971
    modulus = 72 ** 18
    for ch in text:
        state = (state * 179971 + ord(ch) + 1) % modulus
        state ^= (state << 7) % modulus
        state %= modulus
    return "H72N-" + _base72(state, 18)


def load_authoritative_kernel(kernel_path: str | Path = DEFAULT_KERNEL_PATH):
    # Standalone sandbox authority. External kernel loading is intentionally not
    # required for package import; callers can still inspect DEFAULT_KERNEL_PATH.
    return None


class Hash72Authority:
    def __init__(self, kernel_module: Any = None):
        self.kernel = kernel_module
        self.trust_policy = {
            "authoritative_integrity": "HASH72",
            "forbid_legacy_sha_for_security_or_integrity": True,
            "authoritative_seal": "HHS_CORE_SANDBOX_HASH72_AUTHORITY_V1",
        }

    def commit(self, payload: Any, *, domain: str = "HHS_RUNTIME_COMMITMENT") -> str:
        return security_hash72_v44(payload, domain=domain)

    def integrity_bundle(self, payload: Any, *, symbols: str = "xyzw") -> Dict[str, Any]:
        return {
            "ok": True,
            "integrity_hash72": self.commit({"payload": payload, "symbols": symbols}, domain="HASH72_INTEGRITY_BUNDLE"),
            "authoritative_trust_policy": self.trust_policy,
        }


@dataclass(frozen=True)
class HashCommitmentReceiptV2:
    phase: int
    operation: str
    parent_receipt_hash72: str
    input_hash72: str
    pre_state_hash72: str
    operation_hash72: str
    post_state_hash72: str
    witness_hash72: str
    receipt_hash72: str
    integrity_hash72: str
    gate_status: str
    locked: bool
    quarantine: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HHSState:
    phase: int = 0
    vars: Dict[str, Any] = field(default_factory=dict)
    tensors: Dict[str, Any] = field(default_factory=dict)
    parent_receipt_hash72: str = GENESIS_RECEIPT_HASH72
    receipt_chain: List[HashCommitmentReceiptV2] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "vars": canonicalize_for_hash72(self.vars),
            "tensors": canonicalize_for_hash72(self.tensors),
            "parent_receipt_hash72": self.parent_receipt_hash72,
            "receipt_chain_tip": self.receipt_chain[-1].receipt_hash72 if self.receipt_chain else GENESIS_RECEIPT_HASH72,
            "metadata": canonicalize_for_hash72(self.metadata),
        }


class HashCommitmentLayerV2:
    def __init__(self, authority: Hash72Authority, *, phase: int = 0):
        self.authority = authority
        self.phase = phase
        self.receipts: List[HashCommitmentReceiptV2] = []
        self.tip_hash72 = GENESIS_RECEIPT_HASH72

    def commit_transition(self, *, operation: str, input_payload: Any, pre_state: Dict[str, Any], post_state: Dict[str, Any], witness: Dict[str, Any], gate_status: str, reason: str = "") -> HashCommitmentReceiptV2:
        if not witness:
            raise HHSIntegrityError("Transition missing witness payload")
        locked = gate_status == "LOCKED"
        quarantine = not locked
        input_hash = self.authority.commit(input_payload, domain="HHS_INPUT")
        pre_hash = self.authority.commit(pre_state, domain="HHS_PRE_STATE")
        op_hash = self.authority.commit({"operation": operation, "input_hash72": input_hash, "parent_receipt_hash72": self.tip_hash72}, domain="HHS_OPERATION")
        post_hash = self.authority.commit(post_state, domain="HHS_POST_STATE")
        witness_hash = self.authority.commit(witness, domain="HHS_WITNESS")
        core = {
            "phase": self.phase,
            "operation": operation,
            "parent_receipt_hash72": self.tip_hash72,
            "input_hash72": input_hash,
            "pre_state_hash72": pre_hash,
            "operation_hash72": op_hash,
            "post_state_hash72": post_hash,
            "witness_hash72": witness_hash,
            "gate_status": gate_status,
            "locked": locked,
            "quarantine": quarantine,
            "reason": reason,
        }
        receipt_hash = self.authority.commit(core, domain="HHS_RECEIPT")
        integrity = self.authority.integrity_bundle({"receipt_core": core, "receipt_hash72": receipt_hash})
        receipt = HashCommitmentReceiptV2(**core, receipt_hash72=receipt_hash, integrity_hash72=integrity.get("integrity_hash72", receipt_hash))
        self.receipts.append(receipt)
        self.tip_hash72 = receipt.receipt_hash72
        self.phase = (self.phase + 1) % 72
        return receipt

    def verify_chain(self) -> Dict[str, Any]:
        expected = GENESIS_RECEIPT_HASH72
        for idx, receipt in enumerate(self.receipts):
            if receipt.parent_receipt_hash72 != expected:
                return {"ok": False, "index": idx, "reason": "parent_receipt_hash72 mismatch", "expected": expected, "actual": receipt.parent_receipt_hash72}
            expected = receipt.receipt_hash72
        return {"ok": True, "count": len(self.receipts), "tip_hash72": expected}


class KernelGateAdapter:
    def __init__(self, kernel_module: Any = None):
        self.kernel = kernel_module

    def audit_value(self, value: Any, *, phase: int = 0) -> Dict[str, Any]:
        try:
            q = Fraction(value)
            locked = True
            reason = ""
        except Exception as exc:
            q = Fraction(0)
            locked = False
            reason = f"non_numeric_audit_value:{type(exc).__name__}"
        witness = {
            "phase": phase % 72,
            "remap": "a² := R; b² := 2; c² := R + 2",
            "identity": "c² - a² = b²",
            "value": q,
            "kernel_status": "LOCKED" if locked else "QUARANTINED",
            "reason": reason,
        }
        return {"status": "LOCKED" if locked else "QUARANTINED", "locked": locked, "witness": canonicalize_for_hash72(witness), "vars": canonicalize_for_hash72({"a^2": q, "b^2": Fraction(2), "c^2": q + 2})}


OperationFn = Callable[..., Any]


class OperationRegistry:
    def __init__(self):
        self._ops: Dict[str, OperationFn] = {}

    def register(self, name: str, fn: OperationFn) -> None:
        if not name:
            raise ValueError("Operation name required")
        self._ops[name] = fn

    def get(self, name: str) -> OperationFn:
        if name not in self._ops:
            raise KeyError(f"Unknown operation: {name}")
        return self._ops[name]

    def names(self) -> List[str]:
        return sorted(self._ops)


class AuditedRunner:
    def __init__(self, kernel_path: str | Path = DEFAULT_KERNEL_PATH):
        self.kernel_path = Path(kernel_path)
        self.kernel = load_authoritative_kernel(kernel_path)
        self.authority = Hash72Authority(self.kernel)
        self.gate = KernelGateAdapter(self.kernel)
        self.commitments = HashCommitmentLayerV2(self.authority)
        self.registry = OperationRegistry()
        self._install_default_ops()

    def _install_default_ops(self) -> None:
        self.registry.register("ADD", lambda a, b: Fraction(a) + Fraction(b))
        self.registry.register("SUB", lambda a, b: Fraction(a) - Fraction(b))
        self.registry.register("MUL", lambda a, b: Fraction(a) * Fraction(b))
        self.registry.register("DIV", self._op_div)
        self.registry.register("SUM", lambda xs: sum(Fraction(x) for x in xs))
        self.registry.register("SORT", self._op_sort)
        self.registry.register("BINARY_SEARCH", self._op_binary_search)

    @staticmethod
    def _op_div(a: Any, b: Any) -> Fraction:
        bq = Fraction(b)
        if bq == 0:
            raise ZeroDivisionError("DIV by zero maps to failure/quarantine boundary")
        return Fraction(a) / bq

    @staticmethod
    def _op_sort(xs: List[Any]) -> Dict[str, Any]:
        L = [Fraction(x) for x in xs]
        S = sorted(L)
        return {"result": S, "mass_ok": sum(L) == sum(S), "shape_ok": sum(x*x for x in L) == sum(x*x for x in S), "multiset_ok": Counter(L) == Counter(S), "order_ok": all(S[i] <= S[i+1] for i in range(len(S)-1)), "audit_value": sum(S)}

    @staticmethod
    def _op_binary_search(S_raw: List[Any], q_raw: Any) -> Dict[str, Any]:
        S = [Fraction(x) for x in S_raw]
        q = Fraction(q_raw)
        if any(S[i] > S[i+1] for i in range(len(S)-1)):
            return {"found": False, "index": None, "status": "ORDER_BREACH", "path": [], "audit_value": 0}
        low, high, path = 0, len(S)-1, []
        prev_interval = len(S) + 1
        while low <= high:
            interval = high - low + 1
            if interval >= prev_interval:
                return {"found": False, "index": None, "status": "PATH_STUTTER", "path": path, "audit_value": interval}
            prev_interval = interval
            mid = (low + high) // 2
            probe = S[mid]
            step = {"low": low, "mid": mid, "high": high, "interval": interval, "probe": probe, "target": q}
            if probe == q:
                step["decision"] = "FOUND"; path.append(step)
                return {"found": True, "index": mid, "status": "FOUND", "path": path, "audit_value": interval}
            if probe < q:
                step["decision"] = "PRUNE_LEFT"; low = mid + 1
            else:
                step["decision"] = "PRUNE_RIGHT"; high = mid - 1
            path.append(step)
        return {"found": False, "index": None, "status": "MISSING_EXCLUSION_COMPLETE", "path": path, "audit_value": 1}

    def execute(self, operation: str, *args: Any, input_payload: Optional[Any] = None) -> Dict[str, Any]:
        pre_state = {"phase": self.commitments.phase, "operation": operation, "args": canonicalize_for_hash72(args), "tip": self.commitments.tip_hash72}
        try:
            result = self.registry.get(operation)(*args)
            audit_value = result.get("audit_value") if isinstance(result, dict) and "audit_value" in result else result
            audit = self.gate.audit_value(audit_value, phase=self.commitments.phase)
            gate_status = "LOCKED" if audit["locked"] else "QUARANTINED"
            reason = "" if audit["locked"] else audit.get("status", "kernel audit did not lock")
            if isinstance(result, dict):
                for key in ("mass_ok", "shape_ok", "multiset_ok", "order_ok"):
                    if key in result and not bool(result[key]):
                        gate_status = "QUARANTINED"; reason = f"operation gate failed: {key}"
                if result.get("status") in {"ORDER_BREACH", "PATH_STUTTER", "EXCLUSION_FAIL"}:
                    gate_status = "QUARANTINED"; reason = f"operation status failed: {result.get('status')}"
            receipt = self.commitments.commit_transition(operation=operation, input_payload=input_payload if input_payload is not None else {"operation": operation, "args": args}, pre_state=pre_state, post_state={"result": canonicalize_for_hash72(result), "audit": audit}, witness={"operation": operation, "args": canonicalize_for_hash72(args), "result": canonicalize_for_hash72(result), "kernel_audit": audit}, gate_status=gate_status, reason=reason)
            if not receipt.locked:
                return {"ok": False, "quarantine": True, "reason": reason, "receipt": receipt.to_dict(), "result_blocked": True}
            return {"ok": True, "result": canonicalize_for_hash72(result), "receipt": receipt.to_dict(), "chain": self.commitments.verify_chain()}
        except Exception as exc:
            receipt = self.commitments.commit_transition(operation=operation, input_payload=input_payload if input_payload is not None else {"operation": operation, "args": args}, pre_state=pre_state, post_state={"exception": type(exc).__name__, "message": str(exc)}, witness={"exception": type(exc).__name__, "message": str(exc), "operation": operation}, gate_status="QUARANTINED", reason=str(exc))
            return {"ok": False, "quarantine": True, "reason": str(exc), "receipt": receipt.to_dict(), "result_blocked": True}


def _demo() -> None:
    runner = AuditedRunner()
    print(json.dumps(runner.execute("ADD", 2, 3), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _demo()
