"""
hhs_general_runtime_layer_v1.py

General programming environment layer for HARMONICODE.

Purpose
-------
This module finishes the current integration layer by making Hash72 commitments
default for normal program execution.

It does NOT replace the locked kernel. It loads the authoritative kernel by path,
binds to its HASH72 authority, and fails closed if the authority is unavailable.

Default execution contract
--------------------------
input -> exact logic -> manifold remap/witness -> drift/status -> Hash72 receipt chain -> output

Rules
-----
- No placeholder integrity hash for security or state commitment.
- No output without a LOCKED receipt.
- Every transition includes parent_receipt_hash72.
- Every transition includes input/pre/op/post/witness/receipt hashes.
- The kernel remains authoritative; this is a host execution wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import importlib.util
import json
import sys
from collections import Counter


DEFAULT_KERNEL_PATH = Path("/mnt/data/HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py")


# ---------------------------------------------------------------------------
# Canonical serialization
# ---------------------------------------------------------------------------

def canonicalize_for_hash72(obj: Any) -> Any:
    """Convert Python objects into deterministic JSON-compatible structures."""
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
    return json.dumps(
        canonicalize_for_hash72(obj),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Kernel loading and authoritative Hash72 binding
# ---------------------------------------------------------------------------

class HHSRuntimeLoadError(RuntimeError):
    pass


class HHSIntegrityError(RuntimeError):
    pass


def load_authoritative_kernel(kernel_path: str | Path = DEFAULT_KERNEL_PATH):
    """
    Load the locked kernel from a file path.

    The uploaded filename contains '-' characters, so normal Python import syntax
    cannot be used. This loader binds the file under a stable module name.
    """
    path = Path(kernel_path)
    if not path.exists():
        raise HHSRuntimeLoadError(f"Authoritative kernel not found: {path}")

    module_name = "hhs_authoritative_kernel_v44_2_locked_7"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise HHSRuntimeLoadError(f"Could not create import spec for: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class Hash72Authority:
    """
    Thin authority adapter.

    Uses kernel.security_hash72_v44 when present.
    Falls back to kernel.NativeHash72Codec.state_hash72 only if the security
    wrapper is unavailable. If neither exists, loading fails closed.
    """

    def __init__(self, kernel_module: Any):
        self.kernel = kernel_module
        self.trust_policy = getattr(kernel_module, "AUTHORITATIVE_TRUST_POLICY_V44", None)
        self.security_hash72 = getattr(kernel_module, "security_hash72_v44", None)
        self.codec = getattr(kernel_module, "NativeHash72Codec", None)

        if self.trust_policy is None:
            raise HHSRuntimeLoadError("Kernel missing AUTHORITATIVE_TRUST_POLICY_V44")

        if not bool(self.trust_policy.get("forbid_legacy_sha_for_security_or_integrity", False)):
            raise HHSRuntimeLoadError("Kernel trust policy does not forbid legacy SHA for integrity/security")

        if not callable(self.security_hash72) and self.codec is None:
            raise HHSRuntimeLoadError("Kernel missing both security_hash72_v44 and NativeHash72Codec")

        if self.codec is not None and not hasattr(self.codec, "state_hash72"):
            raise HHSRuntimeLoadError("Kernel NativeHash72Codec missing state_hash72")

    def commit(self, payload: Any, *, domain: str = "HHS_RUNTIME_COMMITMENT") -> str:
        body = canonicalize_for_hash72(payload)

        if callable(self.security_hash72):
            return self.security_hash72(body, domain=domain)

        return self.codec.state_hash72({
            "domain": domain,
            "trust_policy": self.trust_policy.get("authoritative_seal", "HASH72_AUTHORITY"),
            "body": body,
        })

    def integrity_bundle(self, payload: Any, *, symbols: str = "xyzw") -> Dict[str, Any]:
        fn = getattr(self.kernel, "authoritative_integrity_bundle_v44", None)
        if not callable(fn):
            return {
                "ok": True,
                "integrity_hash72": self.commit(payload, domain="HASH72_INTEGRITY_BUNDLE"),
                "authoritative_trust_policy": self.trust_policy,
                "note": "authoritative_integrity_bundle_v44 unavailable; used security_hash72_v44 commit",
            }
        return fn(canonicalize_for_hash72(payload), symbols=symbols)


# ---------------------------------------------------------------------------
# Receipt models
# ---------------------------------------------------------------------------

GENESIS_RECEIPT_HASH72 = "H72N-GENESIS"


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


# ---------------------------------------------------------------------------
# Commitment layer
# ---------------------------------------------------------------------------

class HashCommitmentLayerV2:
    def __init__(self, authority: Hash72Authority, *, phase: int = 0):
        self.authority = authority
        self.phase = phase
        self.receipts: List[HashCommitmentReceiptV2] = []
        self.tip_hash72 = GENESIS_RECEIPT_HASH72

    def commit_transition(
        self,
        *,
        operation: str,
        input_payload: Any,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        witness: Dict[str, Any],
        gate_status: str,
        reason: str = "",
    ) -> HashCommitmentReceiptV2:
        if not witness:
            raise HHSIntegrityError("Transition missing witness payload")

        locked = gate_status == "LOCKED"
        quarantine = not locked

        input_hash = self.authority.commit(input_payload, domain="HHS_INPUT")
        pre_hash = self.authority.commit(pre_state, domain="HHS_PRE_STATE")
        op_hash = self.authority.commit({
            "operation": operation,
            "input_hash72": input_hash,
            "parent_receipt_hash72": self.tip_hash72,
        }, domain="HHS_OPERATION")
        post_hash = self.authority.commit(post_state, domain="HHS_POST_STATE")
        witness_hash = self.authority.commit(witness, domain="HHS_WITNESS")

        receipt_core = {
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
        receipt_hash = self.authority.commit(receipt_core, domain="HHS_RECEIPT")
        integrity = self.authority.integrity_bundle({
            "receipt_core": receipt_core,
            "receipt_hash72": receipt_hash,
        })

        receipt = HashCommitmentReceiptV2(
            **receipt_core,
            receipt_hash72=receipt_hash,
            integrity_hash72=integrity.get("integrity_hash72", receipt_hash),
        )

        if receipt.locked and not receipt.receipt_hash72:
            raise HHSIntegrityError("LOCKED state missing receipt_hash72")
        if not receipt.witness_hash72:
            raise HHSIntegrityError("Transition missing witness_hash72")

        self.receipts.append(receipt)
        self.tip_hash72 = receipt.receipt_hash72
        self.phase = (self.phase + 1) % 72
        return receipt

    def verify_chain(self) -> Dict[str, Any]:
        expected_parent = GENESIS_RECEIPT_HASH72
        for idx, receipt in enumerate(self.receipts):
            if receipt.parent_receipt_hash72 != expected_parent:
                return {
                    "ok": False,
                    "index": idx,
                    "reason": "parent_receipt_hash72 mismatch",
                    "expected": expected_parent,
                    "actual": receipt.parent_receipt_hash72,
                }
            expected_parent = receipt.receipt_hash72
        return {
            "ok": True,
            "count": len(self.receipts),
            "tip_hash72": expected_parent,
        }


# ---------------------------------------------------------------------------
# Manifold remap and kernel gate adapter
# ---------------------------------------------------------------------------

def default_manifold_vars(value: Any) -> Dict[str, Fraction]:
    """
    Default remap for normal programming outputs.

    R := output mass
    a² := R
    b² := 2
    c² := R + 2
    gate identity: c² - a² = b²
    """
    R = Fraction(value)
    return {
        "n": Fraction(1, 1),
        "b^2": Fraction(2, 1),
        "x": Fraction(1, 1),
        "y": Fraction(-1, 1),
        "a^2": R,
        "c^2": R + Fraction(2, 1),
        "eq_G": Fraction(36, 1),
    }


def normalize_gate_result(result: Any) -> Tuple[Any, str]:
    """
    Kernel drift_gate variants have appeared in several forms.
    Normalize them into (drift_value, status).
    """
    if isinstance(result, tuple) and len(result) >= 2:
        return result[0], str(result[1])
    if isinstance(result, dict):
        if result.get("gate_ok") is True:
            return result.get("delta"), "LOCKED"
        return result.get("delta"), result.get("status") or "QUARANTINED"
    if result is True:
        return None, "LOCKED"
    return result, str(result)


class KernelGateAdapter:
    def __init__(self, kernel_module: Any):
        self.kernel = kernel_module
        self.Manifold9 = getattr(kernel_module, "Manifold9", None)
        self.Tensor = getattr(kernel_module, "Tensor", None)
        if self.Manifold9 is None:
            raise HHSRuntimeLoadError("Kernel missing Manifold9")
        if self.Tensor is None:
            raise HHSRuntimeLoadError("Kernel missing Tensor")

    def audit_value(self, value: Any, *, phase: int = 0) -> Dict[str, Any]:
        vars_ = default_manifold_vars(value)
        reg = self.Manifold9(phase=phase % 72, vars=vars_, tensors={"G": self.Tensor()})
        if not hasattr(reg, "drift_gate"):
            raise HHSRuntimeLoadError("Manifold9 missing drift_gate")
        drift_value, status = normalize_gate_result(reg.drift_gate())
        witness = {
            "phase": phase % 72,
            "remap": "a² := R; b² := 2; c² := R + 2",
            "identity": "c² - a² = b²",
            "value": Fraction(value),
            "vars": vars_,
            "drift_value": drift_value,
            "kernel_status": status,
        }
        return {
            "status": status,
            "locked": status == "LOCKED",
            "witness": canonicalize_for_hash72(witness),
            "vars": canonicalize_for_hash72(vars_),
        }


# ---------------------------------------------------------------------------
# Operation registry and audited runner
# ---------------------------------------------------------------------------

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
    """
    General-purpose execution host.

    Each operation:
    - executes normal Python logic
    - remaps result into Manifold9
    - runs kernel audit
    - emits Hash72 receipt chain
    - blocks output unless LOCKED
    """

    def __init__(self, kernel_path: str | Path = DEFAULT_KERNEL_PATH):
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
        return {
            "result": S,
            "mass_ok": sum(L) == sum(S),
            "shape_ok": sum(x * x for x in L) == sum(x * x for x in S),
            "multiset_ok": Counter(L) == Counter(S),
            "order_ok": all(S[i] <= S[i + 1] for i in range(len(S) - 1)),
            "audit_value": sum(S),
        }

    @staticmethod
    def _op_binary_search(S_raw: List[Any], q_raw: Any) -> Dict[str, Any]:
        S = [Fraction(x) for x in S_raw]
        q = Fraction(q_raw)
        if any(S[i] > S[i + 1] for i in range(len(S) - 1)):
            return {"found": False, "index": None, "status": "ORDER_BREACH", "path": [], "audit_value": 0}

        low, high = 0, len(S) - 1
        prev_interval = len(S) + 1
        path = []
        while low <= high:
            interval = high - low + 1
            if interval >= prev_interval:
                return {"found": False, "index": None, "status": "PATH_STUTTER", "path": path, "audit_value": interval}
            prev_interval = interval
            mid = (low + high) // 2
            probe = S[mid]
            step = {
                "low": low,
                "mid": mid,
                "high": high,
                "interval": interval,
                "probe": probe,
                "target": q,
            }
            if probe == q:
                step["decision"] = "FOUND"
                path.append(step)
                return {"found": True, "index": mid, "status": "FOUND", "path": path, "audit_value": interval}
            if probe < q:
                excluded = S[low:mid + 1]
                step["decision"] = "PRUNE_LEFT"
                step["excluded_range"] = [low, mid]
                step["exclusion_ok"] = all(x < q for x in excluded)
                if not step["exclusion_ok"]:
                    path.append(step)
                    return {"found": False, "index": None, "status": "EXCLUSION_FAIL", "path": path, "audit_value": interval}
                low = mid + 1
            else:
                excluded = S[mid:high + 1]
                step["decision"] = "PRUNE_RIGHT"
                step["excluded_range"] = [mid, high]
                step["exclusion_ok"] = all(x > q for x in excluded)
                if not step["exclusion_ok"]:
                    path.append(step)
                    return {"found": False, "index": None, "status": "EXCLUSION_FAIL", "path": path, "audit_value": interval}
                high = mid - 1
            path.append(step)

        return {"found": False, "index": None, "status": "MISSING_EXCLUSION_COMPLETE", "path": path, "audit_value": 1}

    def execute(self, operation: str, *args: Any, input_payload: Optional[Any] = None) -> Dict[str, Any]:
        op = self.registry.get(operation)
        pre_state = {
            "phase": self.commitments.phase,
            "operation": operation,
            "args": canonicalize_for_hash72(args),
            "tip": self.commitments.tip_hash72,
        }

        try:
            result = op(*args)
            audit_value = result.get("audit_value") if isinstance(result, dict) and "audit_value" in result else result
            audit = self.gate.audit_value(audit_value, phase=self.commitments.phase)
            gate_status = "LOCKED" if audit["locked"] else audit["status"]
            reason = "" if audit["locked"] else "kernel audit did not lock"

            # Operation-specific gates are part of the witness and can force quarantine.
            op_gate_ok = True
            if isinstance(result, dict):
                for key in ("mass_ok", "shape_ok", "multiset_ok", "order_ok"):
                    if key in result and not bool(result[key]):
                        op_gate_ok = False
                        reason = f"operation gate failed: {key}"
                if result.get("status") in {"ORDER_BREACH", "PATH_STUTTER", "EXCLUSION_FAIL"}:
                    op_gate_ok = False
                    reason = f"operation status failed: {result.get('status')}"

            if not op_gate_ok:
                gate_status = "QUARANTINED"

            post_state = {
                "phase": self.commitments.phase,
                "operation": operation,
                "result": canonicalize_for_hash72(result),
                "audit": audit,
            }
            witness = {
                "operation": operation,
                "args": canonicalize_for_hash72(args),
                "result": canonicalize_for_hash72(result),
                "kernel_audit": audit,
                "operation_gate_ok": op_gate_ok,
            }
            receipt = self.commitments.commit_transition(
                operation=operation,
                input_payload=input_payload if input_payload is not None else {"operation": operation, "args": args},
                pre_state=pre_state,
                post_state=post_state,
                witness=witness,
                gate_status=gate_status,
                reason=reason,
            )
            if not receipt.locked:
                return {
                    "ok": False,
                    "quarantine": True,
                    "reason": reason,
                    "receipt": receipt.to_dict(),
                    "result_blocked": True,
                }
            return {
                "ok": True,
                "result": canonicalize_for_hash72(result),
                "receipt": receipt.to_dict(),
                "chain": self.commitments.verify_chain(),
            }

        except Exception as exc:
            receipt = self.commitments.commit_transition(
                operation=operation,
                input_payload=input_payload if input_payload is not None else {"operation": operation, "args": args},
                pre_state=pre_state,
                post_state={"exception": type(exc).__name__, "message": str(exc)},
                witness={"exception": type(exc).__name__, "message": str(exc), "operation": operation},
                gate_status="QUARANTINED",
                reason=str(exc),
            )
            return {
                "ok": False,
                "quarantine": True,
                "reason": str(exc),
                "receipt": receipt.to_dict(),
                "result_blocked": True,
            }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def _demo() -> None:
    runner = AuditedRunner()
    print(json.dumps(runner.execute("ADD", 2, 3), indent=2, ensure_ascii=False))
    print(json.dumps(runner.execute("SORT", [19, 3, 42, 11, 7, 7, 1]), indent=2, ensure_ascii=False))
    print(json.dumps(runner.execute("BINARY_SEARCH", [1, 3, 7, 11, 19, 42, 55], 42), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _demo()
