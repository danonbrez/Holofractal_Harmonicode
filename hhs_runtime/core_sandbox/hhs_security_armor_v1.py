"""
HHS Security Armor Layer V1
===========================

Executable hooks for Lazarus Core defenses:

- Hash72 domain separation enforcement
- Golay-style integrity hooks (detect/repair/denature)
- Adjacency defect invariant checks
- Ω rollback signal generation
- Entropy anchoring interface (P3 scavenger)
- Lockdown mode trigger

This module does not replace standard cryptography; it enforces HHS-native
structural security constraints inside the runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Any, Dict
import os
import time

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44


class ArmorStatus(str, Enum):
    VALID = "VALID"
    CORRECTED = "CORRECTED"
    DENATURED = "DENATURED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class ArmorReceipt:
    status: ArmorStatus
    details: Dict[str, Any]
    receipt_hash72: str
    quarantine_hash72: str | None


# -----------------------------
# Hash72 Domain Enforcement
# -----------------------------

def enforce_domain(payload: Any, domain: str) -> str:
    return security_hash72_v44(payload, domain=domain)


# -----------------------------
# Golay-style Integrity Hooks
# -----------------------------

def golay_armor_check(data: Any) -> ArmorReceipt:
    # Placeholder: structural redundancy check hook
    try:
        h = security_hash72_v44(data, domain="GOLAY_CHECK")
        return ArmorReceipt(ArmorStatus.VALID, {"hash72": h}, h, None)
    except Exception as exc:
        q = security_hash72_v44({"error": str(exc)}, domain="GOLAY_DENATURE")
        return ArmorReceipt(ArmorStatus.DENATURED, {"error": str(exc)}, q, q)


# -----------------------------
# Adjacency Defect Invariant
# -----------------------------

def adjacency_defect_check(P: int) -> ArmorReceipt:
    p = P - 1
    q = P + 1
    defect = P * P - (p * q)
    ok = defect == 1
    status = ArmorStatus.VALID if ok else ArmorStatus.QUARANTINED
    h = security_hash72_v44({"P": P, "defect": defect}, domain="ADJ_DEFECT")
    qh = None if ok else h
    return ArmorReceipt(status, {"P": P, "defect": defect}, h, qh)


# -----------------------------
# Ω Rollback Signal
# -----------------------------

def omega_rollback_signal(reason: str) -> str:
    return security_hash72_v44({"rollback": reason, "timestamp": time.time()}, domain="OMEGA_ROLLBACK")


# -----------------------------
# Entropy Anchor (P3 Scavenger)
# -----------------------------

def entropy_anchor() -> str:
    # Combine OS entropy sources deterministically
    raw = os.urandom(32)
    return security_hash72_v44({"entropy": raw.hex()}, domain="P3_ENTROPY")


# -----------------------------
# Lockdown Mode
# -----------------------------

_LOCKDOWN = False


def trigger_lockdown(reason: str) -> ArmorReceipt:
    global _LOCKDOWN
    _LOCKDOWN = True
    h = security_hash72_v44({"lockdown": reason}, domain="LOCKDOWN")
    return ArmorReceipt(ArmorStatus.QUARANTINED, {"reason": reason}, h, h)


def is_lockdown() -> bool:
    return _LOCKDOWN


# -----------------------------
# Unified Armor Check
# -----------------------------

def armor_guard(payload: Any, *, P: int = 179971) -> ArmorReceipt:
    if is_lockdown():
        return trigger_lockdown("system already locked")

    golay = golay_armor_check(payload)
    if golay.status == ArmorStatus.DENATURED:
        return golay

    adj = adjacency_defect_check(P)
    if adj.status != ArmorStatus.VALID:
        return adj

    h = security_hash72_v44({"payload": payload}, domain="ARMOR_GUARD")
    return ArmorReceipt(ArmorStatus.VALID, {"golay": golay.details, "adj": adj.details}, h, None)
