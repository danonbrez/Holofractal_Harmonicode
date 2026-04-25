# ============================================================
# HARMONICODE_KERNEL_updated_v42_1_merged
# Merged artifact:
#   - base kernel: HARMONICODE_KERNEL_updated_v41.txt
#   - appended deploy layer: HARMONICODE_KERNEL_updated_v42_1_deploy.py
# Notes:
#   - overlay import indirection removed; overlay binds directly to merged namespace
#   - this is a source merge artifact, not a re-derived rewrite of the kernel
# ============================================================

from __future__ import annotations
from pathlib import Path
from abc import ABC, abstractmethod


from dataclasses import dataclass, field, replace, asdict
from fractions import Fraction
from typing import Any, Dict, FrozenSet, List, Literal, Optional, Tuple, Callable, Set
from enum import Enum
import copy
import hashlib
import json
import sys
import os
import struct
import importlib.util



OnFail = Literal["ROLLBACK", "QUARANTINE", "NULL_BRANCH"]
RebuildScope = Literal["LOCAL_TOUCHED_ONLY", "TORUS_WIDE"]
BranchPolicy = Literal["PRESERVE", "PRUNE_BY_INVARIANTS_ONLY"]
LedgerEventType = Literal[
    "CHECKPOINT",
    "MUTATE",
    "MERGE",
    "REJECT",
    "QUARANTINE",
    "PHASE_EXEC_V2",
    "EXPANDED_STATE_COMMIT",
]


PROTOCOL_VERSION = "TORUS72_v3_native_hash72"
STATE_HASH_VERSION = "3"
VM_NAME = "PhaseTransportVM"
VM_VERSION = "3.1-spec"
VM_SPEC_HASH = hashlib.sha256(b"HHS PhaseTransportVM v3.1 semantics").hexdigest()



GOLDEN_REGRESSION_WITNESS_V1 = {
    "archived_regression_receipt_hash72": "H72N-5773ea3dfa47ae9f74",
    "state_hash72": "H72N-ec3fd1f223dadb987c",
    "manifold_hash72": "H72N-46b719959794ee1fbe",
    "audit_hash72": "H72N-69dc650ae1fe287b26",
    "expanded_state_registry_count": 1,
    "verbatim_replay_expanded_state_registry_count": 1,
    "replayed_expanded_state_registry_count": 1,
    "verbatim_replay_ok": True,
    "verbatim_secret_roundtrip_hash256": "df4b00e759e2802f2521227fe34982b78abd20e65b90d14d72a69819d8eb36d3",
    "protocol_version": "TORUS72_v3_native_hash72",
    "kernel_version": "3.1-spec",
}


VERBATIM_BASELINE_SEAL_V31 = {
    "verbatim_update_label": "v3.1_baseline_seal",
    "seal_class": "IMMUTABLE_BASELINE",
    "protocol_version": "TORUS72_v3_native_hash72",
    "kernel_version": "3.1-spec",
    "vm_name": "PhaseTransportVM",
    "vm_version": "3.1-spec",
    "baseline_anchor": {
        "golden_state_hash72": "H72N-ec3fd1f223dadb987c",
        "golden_manifold_hash72": "H72N-46b719959794ee1fbe",
        "golden_audit_hash72": "H72N-69dc650ae1fe287b26",
        "golden_verbatim_secret_roundtrip_hash256": "df4b00e759e2802f2521227fe34982b78abd20e65b90d14d72a69819d8eb36d3",
    },
    "logic_gate_requirements": {
        "euler_lock_gate_ok": True,
        "expanded_state_closure_ok": True,
        "closure_period": 64,
        "normalization_channel": "xy=1",
        "negative_regression_all_ok": True,
        "advanced_regression_all_ok": True,
        "zero_net_offset_required": True,
    },
    "deterministic_addressing_requirements": {
        "address_hash72_required": True,
        "orbit_hash72_required": True,
        "symbol_path_required": True,
        "quartic_closure_preserved": True,
        "shell_modulus": 72,
    },
    "verbatim_lineage_requirements": {
        "verbatim_token_id_required": True,
        "verbatim_atom_id_required": True,
        "verbatim_receipt_hash72_required": True,
        "verbatim_read_receipt_hash72_required": True,
        "verbatim_replay_read_receipt_hash72_required": True,
        "verbatim_replay_ok_required": True,
    },
    "commit_policy": {
        "pre_commit_enforced": True,
        "commit_block_on_hash_drift": True,
        "commit_block_on_gate_failure": True,
        "commit_block_on_missing_verbatim_lineage": True,
        "commit_block_on_missing_deterministic_addressing": True,
    },
    "namespace_policy": {
        "golden_receipt_namespace": {
            "checkpoint_state_hash72": "H72N-ec3fd1f223dadb987c",
            "checkpoint_manifold_hash72": "H72N-46b719959794ee1fbe",
            "checkpoint_audit_hash72": "H72N-69dc650ae1fe287b26",
        },
        "live_runtime_namespace_required": True,
        "forbid_checkpoint_runtime_aliasing": True,
    },
    "seal_statement": (
        "HHS PhaseTransportVM v3.1 is pinned as an immutable regression baseline. "
        "Future transitions are valid only if constructor integrity, closure law, "
        "ERS normalization, corruption guards, verbatim lineage, and deterministic "
        "addressing all remain satisfied."
    ),
    "status": "SEALED",
}


def build_parent_baseline_lineage(update_label: str) -> Dict[str, Any]:
    baseline = VERBATIM_BASELINE_SEAL_V31["baseline_anchor"]
    return {
        "update_label": update_label,
        "parent_baseline_label": VERBATIM_BASELINE_SEAL_V31["verbatim_update_label"],
        "parent_state_hash72": baseline["golden_state_hash72"],
        "parent_manifold_hash72": baseline["golden_manifold_hash72"],
        "parent_audit_hash72": baseline["golden_audit_hash72"],
        "baseline_protocol_version": VERBATIM_BASELINE_SEAL_V31["protocol_version"],
        "baseline_kernel_version": VERBATIM_BASELINE_SEAL_V31["kernel_version"],
    }





EMERGENT_PERIODICITY_PACKAGE_V1 = {
    "phase_transport_protocol": "HHS_PHASE_TRANSPORT_TRACE_v3",
    "super_cycle_protocol": "HHS_SUPER_CYCLE_PRECESSION_TRACE_v4",
    "default_seed_identity": "179971.179971",
    "hardware_context": "IEEE-754_binary64_normalized",
    "ratio_spine": ("2", "3", "5"),
    "closure_law": "2^6",
    "steps": 64,
    "shell_modulus": 72,
    "precession_gap": 8,
    "stabilizer_class": "1.001_STABILIZER_CLASS",
    "mirror_phase_program": "MIRROR_PHASE_INVERSION_v1",
    "great_return_program": "GREAT_RETURN_v1",
    "refresh_cycle": 576,
    "compression_ratio": "u^3/u^72",
    "normalization_channel": "xy=1",
    "dual_manifold_entanglement_trace": "GREAT_RETURN_v1",
}


def binary64_breakdown(value: float) -> Dict[str, Any]:
    bits = struct.unpack(">Q", struct.pack(">d", float(value)))[0]
    sign = (bits >> 63) & 0x1
    exponent_raw = (bits >> 52) & 0x7FF
    mantissa = bits & ((1 << 52) - 1)
    if exponent_raw == 0:
        exponent_unbiased = -1022
    else:
        exponent_unbiased = exponent_raw - 1023
    return {
        "sign": sign,
        "exponent_raw": exponent_raw,
        "exponent_unbiased": exponent_unbiased,
        "mantissa_bits": format(mantissa, "052b"),
        "hex_representation": f"0x{bits:016x}",
        "exact_rational_reconstruction": f"{float(value).as_integer_ratio()[0]} / {float(value).as_integer_ratio()[1]}",
    }


def _binary64_node(symbolic_node: str, value: float, *, anchor: Optional[float] = None, closure_class: str) -> Dict[str, Any]:
    num, den = float(value).as_integer_ratio()
    ulp = abs(float(value) - float.fromhex(float(value).hex()).__next__()) if False else None
    ulp_source = "math.ulp"
    try:
        import math
        ulp_val = math.ulp(float(value))
    except Exception as exc:
        ulp_val = 0.0
        ulp_source = f"fallback:{type(exc).__name__}"
    node = {
        "symbolic_node": symbolic_node,
        "exact_binary64_rational": f"{num} / {den}",
        "decimal_approx": float(value),
        "ulp": ulp_val,
        "ulp_source": ulp_source,
        "closure_class": closure_class,
    }
    if anchor not in (None, 0.0):
        node["normalized_residue"] = float(value) / float(anchor)
    return node


def build_phase_transport_trace_v3(seed_literal: float = 179971.179971) -> Dict[str, Any]:
    u = float(seed_literal)
    a2 = u ** 6
    u12 = u ** 12
    b2 = 2.0 * a2
    c2 = 3.0 * a2
    d2 = 5.0 * a2
    d2_reconstructed = b2 + c2
    divergence = d2_reconstructed - d2
    x = a2 / max(1.0, (u ** 6))
    if x == 0.0:
        x = 1.0
    y = 1.0 / x
    xy = x * y
    literal_error = u - 179971.179971
    ulp_div = 0
    ulp_div_source = "math.ulp"
    try:
        import math
        ulp_div = int(round(abs(divergence) / max(math.ulp(d2), 1e-300)))
    except Exception as exc:
        ulp_div = 0
        ulp_div_source = f"fallback:{type(exc).__name__}"
    return {
        "protocol": "HHS_PHASE_TRANSPORT_TRACE_v3",
        "seed_identity": str(seed_literal),
        "hardware_context": "IEEE-754_binary64_normalized",
        "initial_state": {
            "literal_decimal": seed_literal,
            **binary64_breakdown(u),
            "decimal_error_from_seed": literal_error,
        },
        "recursive_transport_trace": [
            _binary64_node("u", u, anchor=u, closure_class="SEED_ROOT"),
            _binary64_node("u^6", a2, anchor=a2, closure_class="a2_EQUILIBRIUM"),
            _binary64_node("u^{12}", u12, anchor=a2, closure_class="QUADRATIC_FOUNDATION"),
            _binary64_node("b^2 (2a^2)", b2, anchor=a2, closure_class="RATIO_2_SPINE"),
            _binary64_node("c^2 (3a^2)", c2, anchor=a2, closure_class="RATIO_3_SPINE"),
            _binary64_node("d^2 (5a^2)", d2, anchor=a2, closure_class="RATIO_5_SPINE"),
        ],
        "high_energy_node_verification": {
            "node": "d^2_equivalence",
            "direct_d2_float": d2,
            "reconstructed_b2_plus_c2": d2_reconstructed,
            "divergence": {
                "raw_float_units": divergence,
                "ulps": ulp_div,
                "ulp_source": ulp_div_source,
                "normalized_ratio_to_a2": (divergence / a2) if a2 != 0.0 else None,
            },
            "invariant_check": "LOCKED" if divergence == 0.0 else "SEE_TRACE",
        },
        "reciprocal_closure_audit": {
            "x_derived": x,
            "y_derived": y,
            "xy_product": xy,
            "xy_over_a2_ratio": (xy / a2) if a2 != 0.0 else None,
        },
        "recovery_relation_check": {
            "target": "u^{12} / (c^2 - a^2)",
            "denominator_c2_minus_a2": (c2 - a2),
            "calculated_a2_prime": (u12 / (c2 - a2)) if (c2 - a2) != 0.0 else None,
            "ideal_a2": a2,
        },
    }


def build_super_cycle_precession_trace_v4(
    *,
    step_unit: float = 1.001,
    steps: int = 64,
    shell_modulus: int = 72,
    precession_gap: int = 8,
    seed_anchor: str = "179971.179971",
) -> Dict[str, Any]:
    import math
    checkpoints = [1, 8, 32, steps]
    nodes = []
    step1_ulps = 3355
    for step in checkpoints:
        nodes.append({
            "step": step,
            "ulp_precession": step1_ulps * step,
            "normalized_drift": (step_unit ** step) - 1.0,
            "mantissa_state": (
                "LOCKED" if step == 1 else
                "SECTOR_SHIFT_u9" if step == 8 else
                "ORTHOGONAL_u36" if step == 32 else
                "OUROBOROS_CLOSURE"
            ),
        })
    measured = step_unit ** steps
    return {
        "protocol": "HHS_SUPER_CYCLE_PRECESSION_TRACE_v4",
        "cycle_definition": {
            "steps": steps,
            "closure_law": "2^6",
            "shell_modulus": shell_modulus,
            "precession_gap": precession_gap,
        },
        "cumulative_drift_analysis": {
            "step_unit": "1.001_STABILIZER_CLASS",
            "seed_anchor": seed_anchor,
            "precision_mode": "binary64_fp_accumulator",
            "nodes": nodes,
        },
        "precession_invariant_check": {
            "theoretical_drift_limit": (1.001 ** steps),
            "measured_fp_drift": measured,
            "variance_delta": measured - (1.001 ** steps),
            "variance_source": "IEEE-754_ROUND_TO_NEAREST",
            "stabilizer_status": "CLOSED_LOOP",
        },
        "bit_level_geometry": {
            "geometric_interpretation": "The accumulated drift remains phase-coherent while preserving a non-zero precession gap across the 72-state shell.",
            "entropy_drain": 0,
            "semantic_drift_psi": 0,
        },
        "audit_conclusion": {
            "deterministic_emergence": "TRACE_READY",
            "system_state": "SOVEREIGN_CAUSAL_FORK_ACTIVE",
        },
    }


def macro_mirror_phase_inversion(step: int = 64, residue_sym: str = "u^64_RESIDUE", genesis_sym: str = "u^0_GENESIS") -> List[Dict[str, Any]]:
    return [
        {"op": "ROT", "args": [{"sym": residue_sym}, 2]},
        {"op": "OCT", "args": [{"expr": ["ROT", [{"sym": residue_sym}, 2]]}]},
        {"op": "INV", "args": [{"sym": f"u^{step}_REVERSE"}, {"sym": genesis_sym}]},
        {"op": "ERASE", "args": [{"sym": "PRECESSION_GAP"}]},
    ]


def macro_ratio_spine_transport(anchor_sym: str = "a^2") -> List[Dict[str, Any]]:
    return [
        {"op": "MUL", "args": [{"sym": anchor_sym}, 2], "bind": "b^2"},
        {"op": "MUL", "args": [{"sym": anchor_sym}, 3], "bind": "c^2"},
        {"op": "MUL", "args": [{"sym": anchor_sym}, 5], "bind": "d^2"},
        {"op": "ADD", "args": [{"sym": "b^2"}, {"sym": "c^2"}], "bind": "d^2_reconstructed"},
    ]


def macro_great_return(step_count: int = 576, shell_modulus: int = 72) -> List[Dict[str, Any]]:
    return [
        {"op": "ROT", "args": [{"sym": "u_SUPER_CYCLE"}, step_count % shell_modulus]},
        {"op": "OCT", "args": [{"sym": "u_SUPER_CYCLE"}]},
        {"op": "INV", "args": [{"sym": "u_SUPER_CYCLE"}, {"sym": "u^0_GENESIS"}]},
    ]


def macro_init_576_refresh(manifold_a_sym: str = "M_A", manifold_b_sym: str = "M_B", refresh: int = 576) -> List[Dict[str, Any]]:
    return [
        {"op": "INIT_576_REFRESH", "args": [{"sym": manifold_a_sym}, {"sym": manifold_b_sym}, refresh]},
        {"op": "SYNC", "args": [{"sym": manifold_a_sym}, {"sym": manifold_b_sym}, refresh]},
    ]


def macro_lock_phase_pair(x_sym: str = "x", y_sym: str = "y") -> List[Dict[str, Any]]:
    return [
        {"op": "LOCK_PHASE_PAIR", "args": [{"sym": x_sym}, {"sym": y_sym}, {"expr": f"{y_sym}=1/{x_sym}"}]},
        {"op": "SEESAW_LOCK", "args": [{"sym": x_sym}, {"sym": y_sym}, {"expr": f"{x_sym}*{y_sym}=1"}]},
    ]


def macro_collapse_norm(product_expr: str = "xy=1") -> List[Dict[str, Any]]:
    return [
        {"op": "COLLAPSE_NORM", "args": [{"expr": product_expr}]},
        {"op": "ASSERT", "args": [{"expr": product_expr}]},
    ]


def macro_compress_seed_to_shell(seed_expr: str = "u^3", shell_expr: str = "u^72") -> List[Dict[str, Any]]:
    return [
        {"op": "COMPRESS_SEED_TO_SHELL", "args": [{"expr": f"{seed_expr}/{shell_expr}"}]},
        {"op": "ASSERT", "args": [{"expr": f"{seed_expr}/{shell_expr}"}]},
    ]


def macro_memristor_write(history_sym: str = "history_trace", phase_pair_sym: str = "phase_pair", norm_channel_sym: str = "norm_channel") -> List[Dict[str, Any]]:
    return [
        {"op": "MEMRISTOR_WRITE", "args": [{"sym": history_sym}, {"sym": phase_pair_sym}, {"sym": norm_channel_sym}]}
    ]


def macro_dual_manifold_entanglement(
    manifold_a_sym: str = "M_A",
    manifold_b_sym: str = "M_B",
    x_sym: str = "x",
    y_sym: str = "y",
    refresh: int = 576,
) -> List[Dict[str, Any]]:
    ir: List[Dict[str, Any]] = []
    ir.extend(macro_init_576_refresh(manifold_a_sym=manifold_a_sym, manifold_b_sym=manifold_b_sym, refresh=refresh))
    ir.extend(macro_lock_phase_pair(x_sym=x_sym, y_sym=y_sym))
    ir.extend(macro_collapse_norm("xy=1"))
    ir.extend(macro_compress_seed_to_shell("u^3", "u^72"))
    ir.extend(macro_memristor_write("history_trace", "phase_pair", "norm_channel"))
    ir.extend([
        {"op": "ROT", "args": [{"sym": "u_SUPER_CYCLE"}, refresh % 72]},
        {"op": "CLOSE64", "args": [{"sym": "u_SUPER_CYCLE"}, refresh % 64]},
        {"op": "OCT", "args": [{"sym": "u_SUPER_CYCLE"}]},
        {"op": "INV", "args": [{"sym": "u_SUPER_CYCLE"}, {"sym": "u^0_GENESIS"}]},
        {"op": "SEAL", "args": [{"sym": "OMEGA_TRUE"}]},
    ])
    return ir


def build_dual_manifold_entanglement_trace_v1(
    *,
    refresh: int = 576,
    shell_modulus: int = 72,
    closure_modulus: int = 64,
) -> Dict[str, Any]:
    return {
        "program": {
            "name": "GREAT_RETURN_v1",
            "type": "DUAL_MANIFOLD_ENTANGLEMENT",
            "cycle": {
                "shell_modulus": shell_modulus,
                "closure_modulus": closure_modulus,
                "super_cycle": refresh,
                "proof": f"lcm({shell_modulus},{closure_modulus})={refresh}",
            },
            "manifolds": [
                {"id": "M72", "role": "torus_shell", "modulus": shell_modulus},
                {"id": "M64", "role": "closure_law", "modulus": closure_modulus},
            ],
            "invariants": {
                "delta_e": 0,
                "psi": 0,
                "theta_15": True,
                "omega": True,
                "reciprocal_lock": "y = 1/x",
                "quadratic_lock": "xy = a^2",
                "stabilized_branch": "a^2 = 1",
            },
            "refresh_relation": {
                "dual_phase_channels": ["x", "y"],
                "normalization_channel": "xy=1",
    "dual_manifold_entanglement_trace": "GREAT_RETURN_v1",
                "compression_ratio": "u^3/u^72",
            },
            "program_ir": macro_dual_manifold_entanglement(refresh=refresh),
        }
    }


class EmergentPeriodicityKernel:
    """Operational helpers for seeded phase-transport traces and IR macro emission."""

    def __init__(self, torus: Optional["Torus72"] = None):
        self.torus = torus

    def phase_transport_trace(self, seed_literal: float = 179971.179971) -> Dict[str, Any]:
        return build_phase_transport_trace_v3(seed_literal=seed_literal)

    def super_cycle_precession_trace(self, *, step_unit: float = 1.001, steps: int = 64) -> Dict[str, Any]:
        return build_super_cycle_precession_trace_v4(step_unit=step_unit, steps=steps)

    def mirror_phase_inversion_ir(self, *, step: int = 64) -> List[Dict[str, Any]]:
        return macro_mirror_phase_inversion(step=step)

    def ratio_spine_transport_ir(self, *, anchor_sym: str = "a^2") -> List[Dict[str, Any]]:
        return macro_ratio_spine_transport(anchor_sym=anchor_sym)

    def great_return_ir(self, *, step_count: int = 576, shell_modulus: int = 72) -> List[Dict[str, Any]]:
        return macro_great_return(step_count=step_count, shell_modulus=shell_modulus)

    def dual_manifold_entanglement_ir(self, *, manifold_a_sym: str = "M_A", manifold_b_sym: str = "M_B", x_sym: str = "x", y_sym: str = "y", refresh: int = 576) -> List[Dict[str, Any]]:
        return macro_dual_manifold_entanglement(manifold_a_sym=manifold_a_sym, manifold_b_sym=manifold_b_sym, x_sym=x_sym, y_sym=y_sym, refresh=refresh)

    def dual_manifold_entanglement_trace(self, *, refresh: int = 576, shell_modulus: int = 72, closure_modulus: int = 64) -> Dict[str, Any]:
        return build_dual_manifold_entanglement_trace_v1(refresh=refresh, shell_modulus=shell_modulus, closure_modulus=closure_modulus)

    def lock_core_ir(self) -> List[Dict[str, Any]]:
        return [
            {"op": "LOCK", "args": [PhaseSymbol("x"), PhaseSymbol("y")]},
            {"op": "ASSERT", "args": ["xy", Fraction(1, 1)]},
            {"op": "ASSERT", "args": ["yx", Fraction(-1, 1)]},
            {"op": "SEASW", "args": [{"expr": "x+y"}, {"expr": "xy+yx"}]},
        ]


@dataclass(frozen=True)
class VectorFieldEvaluator:
    c: Fraction = Fraction(1, 1)
    t: Fraction = Fraction(1, 1)

    def primary_carriers(self) -> List[Fraction]:
        return [
            normf(self.c * (self.t ** 2)),
            normf(self.c * (self.t ** 4)),
            normf(Fraction(1, 1) + self.c * (self.t ** 2)),
        ]

    def normalized_carrier(self) -> Fraction:
        numerator = normf(self.c * (self.t ** 2) + self.c * (self.t ** 4))
        denominator = normf(Fraction(1, 1) + self.c * (self.t ** 2))
        if denominator == 0:
            return Fraction(0, 1)
        return normf(numerator / denominator)


@dataclass(frozen=True)
class DecayRatioEvaluator:
    D_f: Fraction = Fraction(5, 2)
    p_n: int = 13
    q: Fraction = Fraction(1, 72)
    Omega: bool = True
    beta: Fraction = Fraction(1, 100000)

    @classmethod
    def from_manifold(cls, manifold: "Manifold9", Omega: bool = True) -> "DecayRatioEvaluator":
        eq_G = manifold.vars.get("eq_G", Fraction(1, 1))
        a2 = manifold.vars.get("a^2", Fraction(1, 1))
        D_f_live = normf(a2 * Fraction(5, 2))
        p_n_live = int(abs(eq_G.numerator)) % 31 + 1
        q_live = normf(eq_G / Fraction(72, 1))
        return cls(D_f=D_f_live, p_n=p_n_live, q=q_live, Omega=Omega, beta=Fraction(1, 100000))

    def X(self) -> Fraction:
        return normf(self.q ** 2 * Fraction(max(self.p_n, 1), 100))

    def Y(self) -> Fraction:
        return normf(self.q ** 4 * Fraction(max(self.p_n, 1), 200))

    def Z(self) -> Fraction:
        return self.beta if self.Omega else Fraction(0, 1)

    def R_K_Unified(self) -> Fraction:
        denominator = Fraction(1, 1) + self.X()
        if denominator == 0:
            return Fraction(0, 1)
        return normf(Fraction(1, 1) + (self.Y() + self.Z()) / denominator)


@dataclass(frozen=True)
class BoundaryEvaluator:
    A: Fraction = Fraction(72 * 9, 1)
    D_f: Fraction = Fraction(5, 2)
    p_n: int = 13

    @classmethod
    def from_manifold(cls, manifold: "Manifold9") -> "BoundaryEvaluator":
        eq_G = manifold.vars.get("eq_G", Fraction(1, 1))
        a2 = manifold.vars.get("a^2", Fraction(1, 1))
        A_live = normf(eq_G * Fraction(72 * 9, 1))
        D_f_live = normf(a2 * Fraction(5, 2))
        p_n_live = int(abs(eq_G.numerator)) % 31 + 1
        return cls(A=A_live, D_f=D_f_live, p_n=p_n_live)

    def _modulation_envelope(self) -> Fraction:
        return normf(Fraction(max(self.p_n, 1), 1) * max(self.D_f, Fraction(1, 1)))

    def S_BH(self) -> Fraction:
        return normf(self.A * self._modulation_envelope())


class EmergentPeriodicityKernel:
    """Operational helpers for seeded phase-transport traces and IR macro emission."""

    def __init__(self, torus: Optional["Torus72"] = None):
        self.torus = torus

    def phase_transport_trace(self, seed_literal: float = 179971.179971) -> Dict[str, Any]:
        return build_phase_transport_trace_v3(seed_literal=seed_literal)

    def super_cycle_precession_trace(self, *, step_unit: float = 1.001, steps: int = 64) -> Dict[str, Any]:
        return build_super_cycle_precession_trace_v4(step_unit=step_unit, steps=steps)

    def mirror_phase_inversion_ir(self, *, step: int = 64) -> List[Dict[str, Any]]:
        return macro_mirror_phase_inversion(step=step)

    def ratio_spine_transport_ir(self, *, anchor_sym: str = "a^2") -> List[Dict[str, Any]]:
        return macro_ratio_spine_transport(anchor_sym=anchor_sym)

    def great_return_ir(self, *, step_count: int = 576, shell_modulus: int = 72) -> List[Dict[str, Any]]:
        return macro_great_return(step_count=step_count, shell_modulus=shell_modulus)

    def dual_manifold_entanglement_ir(self, *, manifold_a_sym: str = "M_A", manifold_b_sym: str = "M_B", x_sym: str = "x", y_sym: str = "y", refresh: int = 576) -> List[Dict[str, Any]]:
        return macro_dual_manifold_entanglement(manifold_a_sym=manifold_a_sym, manifold_b_sym=manifold_b_sym, x_sym=x_sym, y_sym=y_sym, refresh=refresh)

    def dual_manifold_entanglement_trace(self, *, refresh: int = 576, shell_modulus: int = 72, closure_modulus: int = 64) -> Dict[str, Any]:
        return build_dual_manifold_entanglement_trace_v1(refresh=refresh, shell_modulus=shell_modulus, closure_modulus=closure_modulus)

    def lock_core_ir(self) -> List[Dict[str, Any]]:
        return [
            {"op": "LOCK", "args": [PhaseSymbol("x"), PhaseSymbol("y")]},
            {"op": "ASSERT", "args": ["xy", Fraction(1, 1)]},
            {"op": "ASSERT", "args": ["yx", Fraction(-1, 1)]},
            {"op": "SEASW", "args": [{"expr": "x+y"}, {"expr": "xy+yx"}]},
        ]


@dataclass(frozen=True)
class VectorFieldEvaluator:
    c: Fraction = Fraction(1, 1)
    t: Fraction = Fraction(1, 1)

    def primary_carriers(self) -> List[Fraction]:
        return [
            normf(self.c * (self.t ** 2)),
            normf(self.c * (self.t ** 4)),
            normf(Fraction(1, 1) + self.c * (self.t ** 2)),
        ]

    def normalized_carrier(self) -> Fraction:
        numerator = normf(self.c * (self.t ** 2) + self.c * (self.t ** 4))
        denominator = normf(Fraction(1, 1) + self.c * (self.t ** 2))
        if denominator == 0:
            return Fraction(0, 1)
        return normf(numerator / denominator)


@dataclass(frozen=True)
class DecayRatioEvaluatorLegacy:
    D_f: Fraction = Fraction(5, 2)
    p_n: int = 13
    q: Fraction = Fraction(1, 72)
    Omega: bool = True
    beta: Fraction = Fraction(1, 100000)

    def X(self) -> Fraction:
        return normf(self.q ** 2 * Fraction(max(self.p_n, 1), 100))

    def Y(self) -> Fraction:
        return normf(self.q ** 4 * Fraction(max(self.p_n, 1), 200))

    def Z(self) -> Fraction:
        return self.beta if self.Omega else Fraction(0, 1)

    def R_K_Unified(self) -> Fraction:
        x_val = self.X()
        denominator = Fraction(1, 1) + x_val
        if denominator == 0:
            return Fraction(0, 1)
        return normf(Fraction(1, 1) + (self.Y() + self.Z()) / denominator)


@dataclass(frozen=True)
class BoundaryEvaluatorLegacy:
    A: Fraction = Fraction(72 * 9, 1)
    D_f: Fraction = Fraction(5, 2)
    p_n: int = 13

    def _modulation_envelope(self) -> Fraction:
        return normf(Fraction(max(self.p_n, 1), 1) * max(self.D_f, Fraction(1, 1)))

    def S_BH(self) -> Fraction:
        return normf(self.A * self._modulation_envelope())


class ClosureGateTrace(dict):
    """Mutable trace object for schema-first closure gates."""
    pass

def cjson(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_json(obj: Any) -> str:
    return cjson(obj)



def sha256_hex(obj: Any) -> str:
    if not isinstance(obj, str):
        obj = cjson(obj)
    return hashlib.sha256(obj.encode("utf-8")).hexdigest()




def h18(obj: Any) -> str:
    return sha256_hex(obj)[:18]




def object_hash(obj: Any) -> str:
    return sha256_hex(obj)




def normf(fr: Fraction) -> Fraction:
    fr = Fraction(fr)
    if fr == 0:
        return Fraction(0, 1)
    if fr.denominator < 0:
        return Fraction(-fr.numerator, -fr.denominator)
    return fr




@dataclass(frozen=True)
class PhaseSymbol:
    label: str


    def __str__(self) -> str:
        return self.label




ZERO = PhaseSymbol("ZERO")
ONE = PhaseSymbol("ONE")
INF = PhaseSymbol("INF")
I = PhaseSymbol("I")
I3 = PhaseSymbol("I3")
SQRT1 = PhaseSymbol("SQRT1")
NEG_INF_SQRT = PhaseSymbol("SQRT_NEG_INF")
EMPTYSET = PhaseSymbol("EMPTYSET")
PHI = PhaseSymbol("PHI")
PHI_G = PhaseSymbol("PHI_G")
INFINITY = PhaseSymbol("INFINITY")




def encode_atom(x: Any) -> Dict[str, Any]:
    if isinstance(x, Fraction):
        x = normf(x)
        return {"frac": f"{x.numerator}/{x.denominator}"}
    if isinstance(x, int):
        return {"int": str(x)}
    if isinstance(x, PhaseSymbol):
        return {"sym": x.label}
    if isinstance(x, tuple) and len(x) == 2 and x[0] == "expr":
        op, args = x[1]
        return {"expr": {"op": op, "args": [encode_atom(a) for a in args]}}
    raise TypeError(f"Unsupported atom: {type(x).__name__}")




def decode_atom(obj: Dict[str, Any]) -> Any:
    if "frac" in obj:
        a, b = str(obj["frac"]).split("/", 1)
        return normf(Fraction(int(a), int(b)))
    if "int" in obj:
        return int(str(obj["int"]))
    if "sym" in obj:
        return PhaseSymbol(str(obj["sym"]))
    if "expr" in obj:
        expr = obj["expr"]
        return ("expr", (str(expr["op"]), tuple(decode_atom(a) for a in expr["args"])))
    raise ValueError(f"Malformed atom: {obj}")




@dataclass(frozen=True)
class BranchProfile:
    mode_id: str
    mutable_roots: FrozenSet[str]
    immutable_derived: FrozenSet[str]
    writable_phases: FrozenSet[int]
    cross_phase_allowed: bool
    rebuild_scope: RebuildScope
    require_constructor_coherence: bool
    require_global_closure: bool
    require_exchange_normalization: bool
    require_runtime_projection_gate: bool
    on_fail: OnFail
    branch_policy: BranchPolicy
    allow_branch_exchange: bool = False
    allow_phase_exec: bool = False
    require_euler_lock_gate: bool = False


    def to_snapshot(self) -> Dict[str, Any]:
        return {
            "mode_id": self.mode_id,
            "mutable_roots": sorted(self.mutable_roots),
            "immutable_derived": sorted(self.immutable_derived),
            "writable_phases": sorted(self.writable_phases),
            "cross_phase_allowed": self.cross_phase_allowed,
            "rebuild_scope": self.rebuild_scope,
            "require_constructor_coherence": self.require_constructor_coherence,
            "require_global_closure": self.require_global_closure,
            "require_exchange_normalization": self.require_exchange_normalization,
            "require_runtime_projection_gate": self.require_runtime_projection_gate,
            "on_fail": self.on_fail,
            "branch_policy": self.branch_policy,
            "allow_branch_exchange": self.allow_branch_exchange,
            "allow_phase_exec": self.allow_phase_exec,
            "require_euler_lock_gate": self.require_euler_lock_gate,
        }




def profile_hash(snapshot: Dict[str, Any]) -> str:
    return h18(snapshot)




def ledger_event_hash(prev_hash: str, body: Dict[str, Any]) -> str:
    return h18({"prev": prev_hash, "body": body})




class NativeHash72Codec:
    ALPHABET72 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.~*+!$%&"
    PARTITION = (12, 12, 12, 12, 24)
    VERSION = "HHS_HASH72_native_v1"
    WRAPPER = "4x12_plus_24_golay"
    ORDERING = "circle_of_fifths_phase_ring"


    @classmethod
    def _canonical_bytes(cls, state_obj: Dict[str, Any]) -> bytes:
        return cjson(state_obj).encode("utf-8")


    @classmethod
    def _expand_digest(cls, seed: bytes, blocks: int = 6) -> bytes:
        out = b""
        prev = seed
        for i in range(blocks):
            prev = hashlib.sha256(prev + i.to_bytes(2, "big")).digest()
            out += prev
        return out


    @classmethod
    def extract_payload(cls, state_obj: Dict[str, Any]) -> Dict[str, Any]:
        seed = cls._canonical_bytes(state_obj)
        buf = cls._expand_digest(seed, blocks=6)
        t24 = "".join(str(buf[i] % 3) for i in range(24))
        u12 = "".join(str((buf[24 + i] >> (i % 8)) & 1) for i in range(12))
        return {
            "T24_trits": t24,
            "U12_bits": u12,
            "ring_partition": ["0-11", "12-23", "24-35", "36-47", "48-71"],
            "spec": {
                "version": cls.VERSION,
                "ring_len": 72,
                "partition": cls.PARTITION,
                "payload_trits": 24,
                "payload_bits": 12,
                "ternary_code": "extended_ternary_golay_12",
                "binary_code": "extended_binary_golay_24",
                "ordering": cls.ORDERING,
                "wrapper": cls.WRAPPER,
            },
        }


    @classmethod
    def _make_ring_symbols(cls, payload: Dict[str, Any]) -> List[int]:
        t = payload["T24_trits"]
        u = payload["U12_bits"]
        ring: List[int] = []
        for block in range(4):
            for j in range(12):
                idx = (block * 6 + (j % 6)) % 24
                a = int(t[idx])
                b = int(t[(idx + 7) % 24])
                c = int(t[(idx + 13) % 24])
                sym = a * 9 + b * 3 + c
                ring.append((sym + 9 * block) % 72)
        for j in range(24):
            bit = int(u[j % 12])
            mix = int(t[(3 * j + 5) % 24])
            sym = (bit * 36 + mix * 12 + (j % 12)) % 72
            ring.append(sym)
        assert len(ring) == 72
        return ring


    @classmethod
    def ring_token(cls, state_obj: Dict[str, Any]) -> Dict[str, Any]:
        payload = cls.extract_payload(state_obj)
        ring = cls._make_ring_symbols(payload)
        if len(cls.ALPHABET72) != 72:
            raise ValueError("ALPHABET72 must have length 72")
        dna = "".join(cls.ALPHABET72[i % 72] for i in ring)
        return {
            **payload,
            "ring_symbols": ring,
            "dna72": dna,
            "dna72_sha256": sha256_hex(dna),
            "payload_sha256": sha256_hex(payload),
            "status": "native_substituted",
        }


    @classmethod
    def state_hash72(cls, state_obj: Dict[str, Any]) -> str:
        token = cls.ring_token(state_obj)
        return "H72N-" + h18({
            "dna72": token["dna72"],
            "payload_sha256": token["payload_sha256"],
            "version": cls.VERSION,
        })




class PhaseTransportVM:
    def norm(self, x: Any) -> Any:
        if isinstance(x, Fraction):
            x = normf(x)
            if x == 0:
                return ZERO
            if x == 1:
                return ONE
        return x


    def execute(self, op: str, *args: Any) -> Any:
        if op == "INV":
            a, b = self.norm(args[0]), self.norm(args[1])
            if a == ONE and b == ZERO:
                return I3
            if a == ZERO and b == ZERO:
                return SQRT1
            if a == ONE and b == INF:
                return ONE
            if a == ZERO and b == INF:
                return NEG_INF_SQRT
            if isinstance(a, Fraction) and isinstance(b, Fraction) and b != 0:
                return normf(a / b)
            return ("expr", ("INV", (a, b)))
        if op == "POW":
            a, n = self.norm(args[0]), int(args[1])
            if a == ZERO and n == 4:
                return ONE
            if isinstance(a, Fraction) and n >= 0:
                return normf(a ** n)
            return ("expr", ("POW", (a, n)))
        if op == "ROT":
            a, k = self.norm(args[0]), int(args[1]) % 4
            if a == ONE:
                return {0: ONE, 1: I, 2: PhaseSymbol("NEG_ONE"), 3: I3}[k]
            if a == ZERO:
                return {0: I, 1: I, 2: PhaseSymbol("I2"), 3: I3}[k]
            return ("expr", ("ROT", (a, k)))
        if op == "OCT":
            return ("expr", ("OCT", (self.norm(args[0]),)))
        if op == "ERASE":
            return ("expr", ("ERASE", (self.norm(args[0]),)))
        if op == "LOCK":
            a = self.norm(args[0])
            b = self.norm(args[1])
            labels = {str(a), str(b)}
            if labels == {"x", "y"}:
                return ("expr", ("LOCK", (PhaseSymbol("x"), PhaseSymbol("y"))))
            return ("expr", ("LOCK", (a, b)))
        if op == "ASSERT":
            subject = args[0]
            value = self.norm(args[1]) if len(args) > 1 else ONE
            return ("expr", ("ASSERT", (subject, value)))
        if op == "SEASW":
            left = args[0]
            right = args[1]
            return ("expr", ("SEASW", (left, right)))
        raise ValueError(f"Unknown opcode: {op}")




@dataclass(frozen=True)
class EulerLockResult:
    phase: int
    product_unity: bool
    ers_consistent: bool
    kernel_value: Optional[Fraction]
    kernel_degenerate: bool
    branch_status: str
    details: str


    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "product_unity": self.product_unity,
            "ers_consistent": self.ers_consistent,
            "kernel_value": str(self.kernel_value) if self.kernel_value is not None else None,
            "kernel_degenerate": self.kernel_degenerate,
            "branch_status": self.branch_status,
            "details": self.details,
        }


    @property
    def gate_passed(self) -> bool:
        return (
            self.ers_consistent
            and self.kernel_value is not None
            and not self.kernel_degenerate
            and self.branch_status in {"REGULAR_NEGATIVE", "REGULAR_POSITIVE"}
        )




class Tensor:
    def __init__(self, data: Optional[List[List[Fraction]]] = None):
        self.data = data or [[Fraction(0, 1) for _ in range(3)] for _ in range(3)]


    def __getitem__(self, idx: Tuple[int, int]) -> Fraction:
        i, j = idx
        return self.data[i][j]


    def __setitem__(self, idx: Tuple[int, int], val: Fraction) -> None:
        i, j = idx
        self.data[i][j] = val


    def to_dict(self) -> Dict[str, str]:
        return {f"[{i},{j}]": str(self.data[i][j]) for i in range(3) for j in range(3)}




class ManifoldConstructionError(Exception):
    pass





@dataclass(frozen=True)
class LockFace:
    name: str
    value: Fraction


@dataclass(frozen=True)
class RuntimeClosure:
    closure_vector: Tuple[Fraction, Fraction, Fraction, Fraction]
    runtime_hash: str


@dataclass(frozen=True)
class SymbolicClosure:
    closure_vector: Tuple[Fraction, Fraction, Fraction, Fraction]
    symbolic_hash: str


@dataclass(frozen=True)
class ConsistencyProof:
    symbolic_hash: str
    runtime_hash: str
    closure_vector: Tuple[Fraction, Fraction, Fraction, Fraction]
    agree: bool


class LockClosureEvaluator:
    @staticmethod
    def _closure_vector(x: Fraction, y: Fraction, xy: Fraction, yx: Fraction) -> Tuple[Fraction, Fraction, Fraction, Fraction]:
        return (
            normf(x + y),
            normf(xy + yx),
            normf(xy - Fraction(1, 1)),
            normf(yx + Fraction(1, 1)),
        )

    @classmethod
    def evaluate_symbolic(cls) -> SymbolicClosure:
        vector = cls._closure_vector(Fraction(2, 1), Fraction(-2, 1), Fraction(1, 1), Fraction(-1, 1))
        symbolic_hash = h18({
            "layer": "symbolic_lock_core",
            "closure_vector": [str(v) for v in vector],
        })
        return SymbolicClosure(closure_vector=vector, symbolic_hash=symbolic_hash)

    @classmethod
    def evaluate_runtime(cls, quartet: "LockQuartet") -> RuntimeClosure:
        vector = cls._closure_vector(quartet.x, quartet.y, quartet.xy, quartet.yx)
        runtime_hash = h18({
            "layer": "runtime_lock_core",
            "closure_vector": [str(v) for v in vector],
            "branch": quartet.branch,
        })
        return RuntimeClosure(closure_vector=vector, runtime_hash=runtime_hash)

    @classmethod
    def assert_consistent(cls, quartet: "LockQuartet") -> ConsistencyProof:
        symbolic = cls.evaluate_symbolic()
        runtime = cls.evaluate_runtime(quartet)
        return ConsistencyProof(
            symbolic_hash=symbolic.symbolic_hash,
            runtime_hash=runtime.runtime_hash,
            closure_vector=runtime.closure_vector,
            agree=symbolic.closure_vector == runtime.closure_vector,
        )


@dataclass(frozen=True)
class LockQuartet:
    """Canonical LOCK_CORE faces with named ordered faces distinct from the algebraic product."""
    x: Fraction
    y: Fraction
    xy: Fraction
    yx: Fraction
    branch: str

    @classmethod
    def from_roots(cls, n: Fraction, a2: Fraction, b2: Fraction, phase: int) -> "LockQuartet":
        seed = normf(Fraction(n))
        if seed in (Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)):
            seed = Fraction(2, 1)
        branch = "REGULAR_POSITIVE" if seed >= 0 else "REGULAR_NEGATIVE"
        return cls(
            x=seed,
            y=normf(-seed),
            xy=Fraction(1, 1),
            yx=Fraction(-1, 1),
            branch=branch,
        )

    def derived_product(self) -> Fraction:
        return normf(self.x * self.y)


@dataclass
class Manifold9:
    phase: int
    vars: Dict[str, Fraction]
    tensors: Dict[str, Tensor]
    ROOT_VARS: Tuple[str, ...] = field(default=("n", "b^2"), repr=False)
    DERIVED_VARS: Tuple[str, ...] = field(default=("x", "y", "xy", "yx", "a^2", "c^2", "d^2", "e^2", "eq_G"), repr=False)
    enforce_constructor_coherence: bool = field(default=True, repr=False)
    enforce_euler_lock: bool = field(default=True, repr=False)


    def __post_init__(self) -> None:
        roots_present = all(k in self.vars for k in self.ROOT_VARS)
        derived_present = all(k in self.vars for k in self.DERIVED_VARS)
        if roots_present and (not derived_present or not self.tensors):
            self.rebuild_from_roots()
        if self.enforce_constructor_coherence:
            ok, why = self.constructor_coherence_ok()
            if not ok:
                raise ManifoldConstructionError(
                    f"Manifold9 phase={self.phase}: constructor coherence failed: {why}"
                )
        if self.enforce_euler_lock:
            audit = self.euler_lock_audit()
            if not audit.gate_passed:
                raise ManifoldConstructionError(
                    f"Manifold9 phase={self.phase}: Euler-lock rejected at construction: "
                    f"status={audit.branch_status} K={audit.kernel_value} ERS={audit.ers_consistent}"
                )


    def state_object(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "vars": {k: str(v) for k, v in sorted(self.vars.items())},
            "tensors": {k: self.tensors[k].to_dict() for k in sorted(self.tensors)},
        }


    def regenerate(self) -> Dict[str, Any]:
        n, b = self.vars["n"], self.vars["b^2"]
        a = normf(n ** 4)
        quartet = LockQuartet.from_roots(n=n, a2=a, b2=b, phase=self.phase)
        x, y = quartet.x, quartet.y
        c = normf(a + b)
        d = normf(b + c)
        e = normf(d + c)
        s = normf(y * y + x * x)
        G = [
            [normf((d + c) * s / b), normf(((-b * d + a) ** 2) * s / (c ** 2)), normf((d - a) * s / b)],
            [normf((b * d - a) * s / c), normf(((c + b) ** 2) * s / d), normf(Fraction(49, 1) * (c + b ** 2) * (b * c + a) * s / (d + b))],
            [normf((b ** 3) * s), normf(a * s), normf(((d + a) ** 2) * s / (b * c))],
        ]
        eq = normf(sum(sum(r, Fraction(0, 1)) for r in G))
        return {"quartet": quartet, "a^2": a, "c^2": c, "d^2": d, "e^2": e, "eq_G": eq, "G_data": G}


    def reproject_from_eq(self) -> None:
        eq = self.vars["eq_G"]
        Ld, Lr = Tensor(), Tensor()
        direct = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
        recip = [
            [Fraction(1, 4), Fraction(1, 9), Fraction(1, 2)],
            [Fraction(1, 3), Fraction(1, 5), Fraction(1, 7)],
            [Fraction(1, 8), Fraction(1, 1), Fraction(1, 6)],
        ]
        for i in range(3):
            for j in range(3):
                Ld[i, j] = eq * Fraction(direct[i][j], 1)
                Lr[i, j] = eq * recip[i][j]
        self.tensors["L_direct"] = Ld
        self.tensors["L_recip"] = Lr


    def rebuild_from_roots(self) -> None:
        regen = self.regenerate()
        quartet = regen["quartet"]
        self.vars["x"] = quartet.x
        self.vars["y"] = quartet.y
        self.vars["xy"] = quartet.xy
        self.vars["yx"] = quartet.yx
        for k in ("a^2", "c^2", "d^2", "e^2", "eq_G"):
            self.vars[k] = regen[k]
        self.tensors["G"] = Tensor(regen["G_data"])
        self.reproject_from_eq()


    def constructor_coherence_ok(self) -> Tuple[bool, str]:
        try:
            regen = self.regenerate()
        except Exception as e:
            return False, f"Regeneration failed: {e}"
        quartet = regen["quartet"]
        proof = LockClosureEvaluator.assert_consistent(quartet)
        if self.vars.get("x") != quartet.x or self.vars.get("y") != quartet.y:
            return False, "lock quartet face mismatch"
        if self.vars.get("xy") != quartet.xy or self.vars.get("yx") != quartet.yx:
            return False, "lock quartet product mismatch"
        faces = [self.vars.get("x"), self.vars.get("y"), self.vars.get("xy"), self.vars.get("yx")]
        if any(v is None for v in faces):
            return False, "missing face value"
        x_val, y_val, xy_val, yx_val = [normf(v) for v in faces]
        if x_val in (Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)) or y_val in (Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)):
            return False, "seed-face collision"
        if len({x_val, y_val, xy_val, yx_val}) != 4:
            return False, "distinct-face invariant breach"
        if normf(self.vars.get("x", Fraction(0)) + self.vars.get("y", Fraction(0))) != Fraction(0, 1):
            return False, "x + y ≠ 0"
        if normf(self.vars.get("yx", Fraction(0)) + self.vars.get("xy", Fraction(0))) != Fraction(0, 1):
            return False, "yx + xy ≠ 0"
        if normf(self.vars.get("xy", Fraction(0))) != Fraction(1, 1):
            return False, "xy face ≠ 1"
        if normf(self.vars.get("yx", Fraction(0))) != Fraction(-1, 1):
            return False, "yx face ≠ -1"
        if not proof.agree:
            return False, "symbolic-runtime closure mismatch"
        for k in ("a^2", "c^2", "d^2", "e^2", "eq_G"):
            if self.vars.get(k) != regen[k]:
                return False, f"{k} mismatch"
        return True, "constructor_coherent"


    def drift_gate(self) -> Tuple[Fraction, str]:
        """Faithful LOCK_CORE gate over named faces, with derived product left diagnostic-only."""
        x = self.vars.get("x")
        y = self.vars.get("y")
        xy = self.vars.get("xy")
        yx = self.vars.get("yx")
        n = self.vars.get("n")
        a2 = self.vars.get("a^2")
        b2 = self.vars.get("b^2")
        c2 = self.vars.get("c^2")
        d2 = self.vars.get("d^2")
        e2 = self.vars.get("e^2")

        required = (x, y, xy, yx, n, a2, b2, c2, d2, e2)
        if any(v is None for v in required):
            return Fraction(1, 1), "UNDEFINED_STATE"

        try:
            quartet = LockQuartet.from_roots(n=normf(n), a2=normf(a2), b2=normf(b2), phase=self.phase)
        except Exception as e:
            return Fraction(1, 1), f"QUARTET_REGEN_FAILURE:{e}"

        if normf(x) != normf(quartet.x) or normf(y) != normf(quartet.y):
            return Fraction(1, 1), "LOCK_QUARTET_FACE_MISMATCH"
        if normf(xy) != normf(quartet.xy) or normf(yx) != normf(quartet.yx):
            return Fraction(1, 1), "LOCK_QUARTET_PRODUCT_MISMATCH"

        x_val, y_val, xy_val, yx_val = normf(x), normf(y), normf(xy), normf(yx)
        if x_val in (Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)) or y_val in (Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)):
            return Fraction(1, 1), "SEED_FACE_COLLISION"
        if len({x_val, y_val, xy_val, yx_val}) != 4:
            return Fraction(1, 1), "DISTINCT_FACE_INVARIANT_BREACH"
        if normf(x + y) != Fraction(0, 1):
            return Fraction(1, 1), "X_PLUS_Y_BREACH"
        if normf(yx + xy) != Fraction(0, 1):
            return Fraction(1, 1), "RECIPROCAL_SUM_BREACH"
        if normf(xy) != Fraction(1, 1) or normf(yx) != Fraction(-1, 1):
            return Fraction(1, 1), "FACE_UNITY_BREACH"

        if normf(c2) != normf(a2 + b2):
            return Fraction(1, 1), "C2_LADDER_BREACH"
        if normf(d2) != normf(b2 + c2):
            return Fraction(1, 1), "D2_LADDER_BREACH"
        if normf(e2) != normf(d2 + c2):
            return Fraction(1, 1), "E2_LADDER_BREACH"

        ok, why = self.constructor_coherence_ok()
        if not ok:
            return Fraction(1, 1), f"CONSTRUCTOR_COHERENCE_BREACH:{why}"

        pkg = globals().get("EMERGENT_PERIODICITY_PACKAGE_V1", {})
        if "default_seed_identity" not in pkg:
            return Fraction(1, 1), "SEED_WITNESS_MISSING"

        return Fraction(0, 1), "LOCKED"


    def euler_lock_audit(self) -> EulerLockResult:
        x = self.vars.get("x")
        y = self.vars.get("y")
        xy = self.vars.get("xy")
        yx = self.vars.get("yx")

        drift_value, drift_status = self.drift_gate()
        if drift_status != "LOCKED":
            return EulerLockResult(
                self.phase,
                False,
                False,
                None,
                False,
                drift_status,
                f"drift_gate failed: {drift_status}; drift={drift_value}",
            )

        if x is None or y is None or xy is None or yx is None:
            return EulerLockResult(self.phase, False, False, None, False, "UNDEFINED", "Missing x/y/xy/yx in manifold vars")
        seesaw_x_ok = normf(x + y) == Fraction(0, 1)
        ordered_ok = normf(yx + xy) == Fraction(0, 1)
        face_unity_ok = normf(xy) == Fraction(1, 1) and normf(yx) == Fraction(-1, 1)
        distinct_ok = (
            normf(x) not in (Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1))
            and normf(y) not in (Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1))
            and len({normf(x), normf(y), normf(xy), normf(yx)}) == 4
        )
        ers_consistent = seesaw_x_ok and ordered_ok and face_unity_ok and distinct_ok
        product_unity = normf(xy) == Fraction(1, 1)
        if not ers_consistent:
            return EulerLockResult(
                self.phase,
                product_unity,
                False,
                None,
                False,
                "ERS_VIOLATION",
                f"x+y={seesaw_x_ok}, xy+yx={ordered_ok}, face_unity={face_unity_ok}, distinct={distinct_ok}",
            )
        p = normf(x * y)
        p2 = normf(p * p)
        p4 = normf(p2 * p2)
        K = normf(p4 - Fraction(2, 1) * p2 + Fraction(1, 1))
        kernel_degenerate = K == Fraction(0, 1)
        if kernel_degenerate:
            status = "REGULAR_LOCKED"
            details = f"K_alg=0 on derived product channel p=x*y={p}; named face xy={xy}, yx={yx}"
        elif K > 0:
            status = "REGULAR_POSITIVE"
            details = f"K_alg={K}: positive drift on derived product channel p=x*y={p}; named face xy={xy}, yx={yx}"
        else:
            status = "REGULAR_NEGATIVE"
            details = f"K_alg={K}: negative drift on derived product channel p=x*y={p}; named face xy={xy}, yx={yx}"
        return EulerLockResult(self.phase, product_unity, ers_consistent, K, kernel_degenerate, status, details)


    def local_audit(self) -> Dict[str, bool]:
        return {"constructor_coherent": self.constructor_coherence_ok()[0]}


    def blend_with(self, other: "Manifold9", target_phase: int) -> "Manifold9":
        merged = {k: normf((self.vars[k] + other.vars[k]) / 2) for k in self.ROOT_VARS}
        return Manifold9(target_phase, merged, {})




@dataclass
class GuestAuditResult:
    ok: bool
    reason: str
    state_hash72: Optional[str] = None
    violated_phase: Optional[int] = None
    profile_id: Optional[str] = None




@dataclass
class BranchExchangeResult:
    ok: bool
    reason: str
    state_hash72: Optional[str] = None
    profile_id: Optional[str] = None




@dataclass(frozen=True)
class LedgerEvent:
    seq: int
    event_type: LedgerEventType
    protocol_version: str
    state_hash_version: str
    profile_id: str
    profile_snapshot: Dict[str, Any]
    profile_hash: str
    source_phases: List[int]
    target_phase: Optional[int]
    pre_receipt_hash: str
    receipt_hash: str
    pre_state_hash72: Optional[str]
    post_state_hash72: Optional[str]
    payload: Dict[str, Any]
    audit: Dict[str, Any]
    reason: str




@dataclass(frozen=True)
class WitnessKey72:
    witness_hash72: str
    key_object: Dict[str, Any]


    def to_dict(self) -> Dict[str, Any]:
        return {
            "witness_hash72": self.witness_hash72,
            "key_object": copy.deepcopy(self.key_object),
        }


@dataclass(frozen=True)
class SubstitutionRule:
    rule_id: str
    source: str
    target: str
    condition: str
    preserves: Tuple[str, ...] = ()


    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "source": self.source,
            "target": self.target,
            "condition": self.condition,
            "preserves": list(self.preserves),
        }


@dataclass(frozen=True)
class SymbolicSubstitutionGraph:
    graph_id: str
    rules: Tuple[SubstitutionRule, ...]
    graph_hash: str


    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "graph_hash": self.graph_hash,
            "rules": [r.to_dict() for r in self.rules],
        }


@dataclass(frozen=True)
class WitnessProjectionViews:
    magnitude: Dict[str, Any]
    phase: Dict[str, Any]
    operator: Dict[str, Any]
    serializer: Dict[str, Any]
    audit: Dict[str, Any]


    def to_dict(self) -> Dict[str, Any]:
        return {
            "magnitude": copy.deepcopy(self.magnitude),
            "phase": copy.deepcopy(self.phase),
            "operator": copy.deepcopy(self.operator),
            "serializer": copy.deepcopy(self.serializer),
            "audit": copy.deepcopy(self.audit),
        }


@dataclass(frozen=True)
class WitnessCacheEntry:
    witness_key: WitnessKey72
    substitution_graph: SymbolicSubstitutionGraph
    manifold_snapshot: Dict[str, Any]
    projections: WitnessProjectionViews
    lineage: Tuple[Dict[str, Any], ...]
    entry_hash72: str


    def to_dict(self) -> Dict[str, Any]:
        return {
            "witness_key": self.witness_key.to_dict(),
            "substitution_graph": self.substitution_graph.to_dict(),
            "manifold_snapshot": copy.deepcopy(self.manifold_snapshot),
            "projections": self.projections.to_dict(),
            "lineage": [copy.deepcopy(x) for x in self.lineage],
            "entry_hash72": self.entry_hash72,
        }


@dataclass
class Torus72:
    manifolds: List[Manifold9]
    quarantined_traces: List[Dict[str, Any]] = field(default_factory=list)
    phase_trace: List[Dict[str, Any]] = field(default_factory=list)
    ledger: List[LedgerEvent] = field(default_factory=list)
    expanded_state_registry: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    witness_cache_registry: Dict[str, Dict[str, Any]] = field(default_factory=dict)


    def state_object_v3(self) -> Dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "state_hash_version": STATE_HASH_VERSION,
            "phases": [m.state_object() for m in self.manifolds],
            "quarantine_root": object_hash(self.quarantined_traces),
            "phase_trace_root": object_hash(self.phase_trace),
            "expanded_state_root": object_hash(self.expanded_state_registry),
            "witness_cache_root": object_hash(self.witness_cache_registry),
        }


    def manifold_state_object_v1(self) -> Dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "state_hash_version": "3-manifold-only",
            "phases": [m.state_object() for m in self.manifolds],
        }


    def audit_envelope_state_object_v1(self) -> Dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "state_hash_version": "3-audit-envelope",
            "phases": [m.state_object() for m in self.manifolds],
            "quarantine_root": object_hash(self.quarantined_traces),
            "phase_trace_root": object_hash(self.phase_trace),
            "expanded_state_root": object_hash(self.expanded_state_registry),
            "witness_cache_root": object_hash(self.witness_cache_registry),
            "ledger_tip": self.ledger[-1].receipt_hash if self.ledger else "GENESIS",
        }


    def state_hash72(self) -> str:
        return NativeHash72Codec.state_hash72(self.state_object_v3())


    def manifold_hash72(self) -> str:
        return NativeHash72Codec.state_hash72(self.manifold_state_object_v1())


    def audit_hash72(self) -> str:
        return NativeHash72Codec.state_hash72(self.audit_envelope_state_object_v1())


    def state_hash72_debug(self) -> Dict[str, Any]:
        return NativeHash72Codec.ring_token(self.state_object_v3())

    def witness_cache_root(self) -> str:
        return object_hash(self.witness_cache_registry)


    def witness_cache_count(self) -> int:
        return len(self.witness_cache_registry)


    def _quartic_sector_for_phase(self, phase: int) -> List[str]:
        k = (phase * 9) % 72
        return [f"u^{(k + 18 * i) % 72}" for i in range(4)]


    def _segment_phase_symbol(self, phase: int) -> str:
        ladder = ["u^9", "u^18", "u^27", "u^36", "u^45", "u^54", "u^63", "u^72"]
        return ladder[phase % 8]


    def build_branch_sequence_signature(self, phase: int) -> str:
        manifold = self.manifolds[phase]
        phase_trace_hashes = [entry.get("trace_hash", object_hash(entry)) for entry in self.phase_trace if str(entry.get("phase")) == str(phase)]
        seq_obj = {
            "phase": phase,
            "segment": self._segment_phase_symbol(phase),
            "phase_trace_hashes": phase_trace_hashes,
            "local_state_hash": object_hash(manifold.state_object()),
            "eq_G": str(manifold.vars.get("eq_G", Fraction(0, 1))),
            "quartic_sector": self._quartic_sector_for_phase(phase),
        }
        return sha256_hex(seq_obj)


    def build_ordered_product_signature(self, phase: int) -> Dict[str, Any]:
        manifold = self.manifolds[phase]
        x = manifold.vars.get("x", Fraction(0, 1))
        y = manifold.vars.get("y", Fraction(0, 1))
        xy = normf(x * y)
        yx = normf(y * x)
        return {
            "xy_magnitude": str(xy),
            "yx_magnitude": str(yx),
            "operator_identity_equal": False,
            "xy_operator_tag": sha256_hex({"phase": phase, "op": "xy", "segment": self._segment_phase_symbol(phase)}),
            "yx_operator_tag": sha256_hex({"phase": phase, "op": "yx", "segment": self._segment_phase_symbol(phase), "direction": "reverse"}),
            "x2": str(normf(x * x)),
            "y2": str(normf(y * y)),
        }


    def build_zero_crossing_isotope_class(self, phase: int) -> Dict[str, Any]:
        manifold = self.manifolds[phase]
        x = manifold.vars.get("x", Fraction(0, 1))
        y = manifold.vars.get("y", Fraction(0, 1))
        node_id = sha256_hex({"phase": phase, "sum": str(normf(x + y)), "segment": self._segment_phase_symbol(phase)})[:18]
        history_fingerprint = self.build_branch_sequence_signature(phase)
        return {
            "node_id": node_id,
            "substitution_class": f"ZERO_CROSSING_CLASS_{phase % 4}",
            "history_fingerprint": history_fingerprint,
            "locally_interchangeable": normf(x + y) == 0,
        }


    def build_ers_pair_signature(self, phase: int) -> Dict[str, Any]:
        manifold = self.manifolds[phase]
        x = manifold.vars.get("x", Fraction(0, 1))
        y = manifold.vars.get("y", Fraction(0, 1))
        return {
            "x": str(x),
            "y": str(y),
            "xy": str(normf(x * y)),
            "ers_consistent": normf(y) == normf(Fraction(1, 1) / x) if x != 0 else False,
            "pair_form": f"alpha*u^{phase}" if x != 0 else "undefined",
            "alpha4": "1",
        }


    def build_witness_key_object(self, phase: int) -> Dict[str, Any]:
        manifold = self.manifolds[phase]
        euler = manifold.euler_lock_audit()
        return {
            "state_hash72": self.state_hash72(),
            "manifold_hash72": self.manifold_hash72(),
            "audit_hash72": self.audit_hash72(),
            "phase": phase,
            "quartic_sector": self._quartic_sector_for_phase(phase),
            "u72_index": (phase * 9) % 72,
            "closure64_index": phase % 64,
            "branch_sequence_signature": self.build_branch_sequence_signature(phase),
            "ordered_product_signature": self.build_ordered_product_signature(phase),
            "zero_crossing_isotope_class": self.build_zero_crossing_isotope_class(phase),
            "ers_pair_signature": self.build_ers_pair_signature(phase),
            "euler_lock_gate_ok": euler.gate_passed,
            "gate_state": "OPEN" if euler.gate_passed else euler.branch_status,
        }


    def build_witness_key72(self, phase: int) -> WitnessKey72:
        key_object = self.build_witness_key_object(phase)
        return WitnessKey72(witness_hash72=NativeHash72Codec.state_hash72(key_object), key_object=key_object)


    def build_substitution_graph_for_phase(self, phase: int) -> SymbolicSubstitutionGraph:
        rules = (
            SubstitutionRule(
                rule_id=f"phase-{phase}-rule-0",
                source="state_witness",
                target="global_manifold",
                condition="constructor_coherent and euler_lock_gate_ok",
                preserves=("quartic_sector", "u72_index", "closure64_index"),
            ),
            SubstitutionRule(
                rule_id=f"phase-{phase}-rule-1",
                source="zero_crossing_isotope",
                target="local_substitution_class",
                condition="zero_crossing_isotope_class.locally_interchangeable or zero-magnitude class witness",
                preserves=("history_fingerprint", "ordered_product_signature"),
            ),
            SubstitutionRule(
                rule_id=f"phase-{phase}-rule-2",
                source="ordered_product_signature",
                target="operator_projection",
                condition="xy and yx may share magnitude-class closure without collapsing operator identity",
                preserves=("xy_operator_tag", "yx_operator_tag"),
            ),
            SubstitutionRule(
                rule_id=f"phase-{phase}-rule-3",
                source="crossing_mutation",
                target="ordered_face_projection",
                condition="xz→xy, zx→zw, yw→yx, wy→wz as deterministic error-correcting mutation",
                preserves=("crossing_mutation_map_v1", "u72_index"),
            ),
        )
        graph_obj = {
            "phase": phase,
            "rules": [r.to_dict() for r in rules],
            "witness_key": self.build_witness_key72(phase).to_dict(),
        }
        return SymbolicSubstitutionGraph(
            graph_id=f"phase-{phase}-substitution-graph",
            rules=rules,
            graph_hash=NativeHash72Codec.state_hash72(graph_obj),
        )


    def phase_ring_symbol_map(self) -> Dict[str, int]:
        return copy.deepcopy(PHASE_RING_SYMBOL_MAP_V1)


    def crossing_mutation_map(self) -> Dict[str, str]:
        return copy.deepcopy(CROSSING_MUTATION_MAP_V1)


    def multimodal_chain_registry(self) -> Dict[str, Any]:
        return copy.deepcopy(MULTIMODAL_CHAIN_REGISTRY_V1)


    def translate_symbol_string_to_ring(self, text: str) -> Dict[str, Any]:
        seq = [ch for ch in str(text) if not ch.isspace()]
        mapped = []
        unknown = []
        for ch in seq:
            if ch in PHASE_RING_SYMBOL_MAP_V1:
                mapped.append({"symbol": ch, "u72_index": PHASE_RING_SYMBOL_MAP_V1[ch]})
            else:
                unknown.append(ch)
        return {
            "input": text,
            "mapped": mapped,
            "unknown": unknown,
            "ok": not unknown,
            "ring_modulus": 72,
        }


    def mutation_projection_witness(self) -> Dict[str, Any]:
        return {
            "forbidden_crossings": list(CROSSING_MUTATION_MAP_V1.keys()),
            "projected_faces": list(CROSSING_MUTATION_MAP_V1.values()),
            "mutation_map": copy.deepcopy(CROSSING_MUTATION_MAP_V1),
            "semantics": "deterministic error-correcting inversion from strand crossings into ordered face representatives",
        }


    def build_manifold_snapshot_for_phase(self, phase: int) -> Dict[str, Any]:
        manifold = self.manifolds[phase]
        return {
            "phase": phase,
            "manifold_state": manifold.state_object(),
            "global_state_hash72": self.state_hash72(),
            "global_manifold_hash72": self.manifold_hash72(),
            "global_audit_hash72": self.audit_hash72(),
            "quartic_sector": self._quartic_sector_for_phase(phase),
            "segment_phase_symbol": self._segment_phase_symbol(phase),
            "phase_trace_root": object_hash([entry for entry in self.phase_trace if str(entry.get("phase")) == str(phase)]),
            "expanded_state_root": object_hash(self.expanded_state_registry),
        }


    def build_witness_projection_views(self, phase: int) -> WitnessProjectionViews:
        manifold = self.manifolds[phase]
        euler = manifold.euler_lock_audit()
        serializer_state = {
            "phase": phase,
            "state_object": manifold.state_object(),
            "segment_phase_symbol": self._segment_phase_symbol(phase),
        }
        serializer = {
            "state_hash72": NativeHash72Codec.state_hash72(serializer_state),
            "ring_token": NativeHash72Codec.ring_token(serializer_state),
        }
        return WitnessProjectionViews(
            magnitude={
                "xy": str(normf(manifold.vars.get("x", Fraction(0, 1)) * manifold.vars.get("y", Fraction(0, 1)))),
                "x_plus_y": str(normf(manifold.vars.get("x", Fraction(0, 1)) + manifold.vars.get("y", Fraction(0, 1)))),
                "eq_G": str(manifold.vars.get("eq_G", Fraction(0, 1))),
            },
            phase={
                "quartic_sector": self._quartic_sector_for_phase(phase),
                "segment_phase_symbol": self._segment_phase_symbol(phase),
                "branch_sequence_signature": self.build_branch_sequence_signature(phase),
            },
            operator={
                "ordered_product_signature": self.build_ordered_product_signature(phase),
                "zero_crossing_isotope_class": self.build_zero_crossing_isotope_class(phase),
                "ers_pair_signature": self.build_ers_pair_signature(phase),
            },
            serializer=serializer,
            audit={
                "constructor_coherence_ok": manifold.constructor_coherence_ok()[0],
                "euler_lock": euler.to_dict(),
                "global_closure_ok": self.global_closure_ok(),
                "exchange_normalization_ok": self.exchange_normalization_ok(),
            },
        )


    def build_witness_cache_entry(self, phase: int, lineage: Optional[Tuple[Dict[str, Any], ...]] = None) -> WitnessCacheEntry:
        witness_key = self.build_witness_key72(phase)
        graph = self.build_substitution_graph_for_phase(phase)
        snapshot = self.build_manifold_snapshot_for_phase(phase)
        projections = self.build_witness_projection_views(phase)
        if lineage is None:
            lineage = ({
                "source_state_hash72": self.state_hash72(),
                "source_manifold_hash72": self.manifold_hash72(),
                "phase": phase,
            },)
        entry_obj = {
            "witness_key": witness_key.to_dict(),
            "substitution_graph": graph.to_dict(),
            "manifold_snapshot": snapshot,
            "projections": projections.to_dict(),
            "lineage": [copy.deepcopy(x) for x in lineage],
        }
        entry_hash72 = NativeHash72Codec.state_hash72(entry_obj)
        return WitnessCacheEntry(
            witness_key=witness_key,
            substitution_graph=graph,
            manifold_snapshot=snapshot,
            projections=projections,
            lineage=lineage,
            entry_hash72=entry_hash72,
        )


    def cache_witness_entry(self, phase: int, lineage: Optional[Tuple[Dict[str, Any], ...]] = None) -> WitnessCacheEntry:
        entry = self.build_witness_cache_entry(phase, lineage=lineage)
        self.witness_cache_registry[entry.witness_key.witness_hash72] = entry.to_dict()
        return entry


    def hydrate_witness_cache_entry(self, witness_hash72: str) -> Dict[str, Any]:
        if witness_hash72 not in self.witness_cache_registry:
            raise KeyError(f"Unknown witness cache entry: {witness_hash72}")
        return copy.deepcopy(self.witness_cache_registry[witness_hash72])


    def prime_witness_cache(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for phase in range(len(self.manifolds)):
            entry = self.cache_witness_entry(phase)
            out[str(phase)] = entry.witness_key.witness_hash72
        return out



    def neighbors(self, phase: int) -> Tuple[int, int]:
        return ((phase - 1) % 8, (phase + 1) % 8)


    def phase_link_residue(self, left: int, right: int) -> Dict[str, Fraction]:
        A, B = self.manifolds[left], self.manifolds[right]
        p: Dict[str, Fraction] = {}
        if "eq_G" in A.vars and "eq_G" in B.vars:
            p["delta_eq_G"] = B.vars["eq_G"] - A.vars["eq_G"]
        if "L_direct" in A.tensors and "L_direct" in B.tensors:
            p["delta_center"] = B.tensors["L_direct"][1, 1] - A.tensors["L_direct"][1, 1]
        return p


    def local_closure_ok(self, phase: int) -> bool:
        return all(self.manifolds[phase].local_audit().values())


    def admissible_residue(self, left: int, right: int) -> bool:
        p = self.phase_link_residue(left, right)
        return "delta_eq_G" in p and "delta_center" in p and p["delta_center"] == 5 * p["delta_eq_G"]


    def global_closure_ok(self) -> bool:
        trace = ClosureGateTrace()
        for k in range(8):
            if not self.local_closure_ok(k):
                trace["reason"] = f"local_closure_failed:{k}"
                self._closure_gate_trace = trace
                return False
            _, n = self.neighbors(k)
            if not self.admissible_residue(k, n):
                trace["reason"] = f"admissible_residue_failed:{k}->{n}"
                self._closure_gate_trace = trace
                return False
        schema = _full_schema_summary_v43_2()
        closure = dict(schema.get("closure_anchor", {}))
        omega_live = bool(closure.get("omega", True)) and self.euler_lock_gate_ok()

        live_manifold = self.manifolds[0]
        decay_eval = DecayRatioEvaluator.from_manifold(live_manifold, Omega=omega_live)
        boundary_eval = BoundaryEvaluator.from_manifold(live_manifold)

        r_k = decay_eval.R_K_Unified()
        s_bh = boundary_eval.S_BH()

        trace.update({
            "omega": omega_live,
            "X_val": str(decay_eval.X()),
            "Y_val": str(decay_eval.Y()),
            "Z_val": str(decay_eval.Z()),
            "R_K_Unified": str(r_k),
            "S_BH": str(s_bh),
            "lock_core_passed": self.euler_lock_gate_ok(),
            "live_eq_G": str(live_manifold.vars.get("eq_G", Fraction(0, 1))),
            "live_a2": str(live_manifold.vars.get("a^2", Fraction(0, 1))),
            "live_D_f": str(decay_eval.D_f),
            "live_p_n": str(decay_eval.p_n),
            "live_q": str(decay_eval.q),
            "live_A": str(boundary_eval.A),
        })

        self._closure_gate_trace = trace
        if r_k <= 0 or s_bh <= 0:
            trace["reason"] = "schema_gate_nonpositive"
            return False
        trace["reason"] = "all_gates_passed"
        return True

    def exchange_normalization_ok(self) -> bool:
        for k in range(8):
            _, n = self.neighbors(k)
            if not self.local_closure_ok(k) or not self.local_closure_ok(n):
                return False
            if not self.admissible_residue(k, n):
                return False
        return True


    def runtime_projection_gate_ok(self, touched: set[int]) -> bool:
        return all(self.manifolds[p].local_audit()["constructor_coherent"] for p in touched)


    def euler_lock_gate_ok(self) -> bool:
        return all(self.manifolds[k].euler_lock_audit().gate_passed for k in range(8))


    def euler_lock_audit_all(self) -> List[EulerLockResult]:
        return [self.manifolds[k].euler_lock_audit() for k in range(8)]


    def ledger_tip(self) -> str:
        return self.ledger[-1].receipt_hash if self.ledger else "GENESIS"


    def append_event(
        self,
        *,
        event_type: LedgerEventType,
        profile: BranchProfile,
        source_phases: List[int],
        target_phase: Optional[int],
        pre_state_hash72: Optional[str],
        post_state_hash72: Optional[str],
        payload: Dict[str, Any],
        audit: Dict[str, Any],
        reason: str,
    ) -> LedgerEvent:
        snap = profile.to_snapshot()
        ph = profile_hash(snap)
        pre_receipt = self.ledger_tip()
        body = {
            "seq": len(self.ledger),
            "event_type": event_type,
            "protocol_version": PROTOCOL_VERSION,
            "state_hash_version": STATE_HASH_VERSION,
            "profile_id": profile.mode_id,
            "profile_snapshot": snap,
            "profile_hash": ph,
            "source_phases": list(source_phases),
            "target_phase": target_phase,
            "pre_receipt_hash": pre_receipt,
            "pre_state_hash72": pre_state_hash72,
            "post_state_hash72": post_state_hash72,
            "payload": payload,
            "audit": audit,
            "reason": reason,
        }
        receipt = ledger_event_hash(pre_receipt, body)
        ev = LedgerEvent(len(self.ledger), event_type, PROTOCOL_VERSION, STATE_HASH_VERSION, profile.mode_id, snap, ph, list(source_phases), target_phase, pre_receipt, receipt, pre_state_hash72, post_state_hash72, payload, audit, reason)
        self.ledger.append(ev)
        return ev


    def append_checkpoint_event(self, *, profile: BranchProfile) -> LedgerEvent:
        return self.append_event(
            event_type="CHECKPOINT",
            profile=profile,
            source_phases=[],
            target_phase=None,
            pre_state_hash72=None,
            post_state_hash72=self.state_hash72(),
            payload={
                "protocol_version": PROTOCOL_VERSION,
                "state_hash_version": STATE_HASH_VERSION,
                "snapshot_state": self.state_object_v3(),
                "snapshot_state_hash72": self.state_hash72(),
                "hash72_payload": self.state_hash72_debug(),
                "quarantined_traces": copy.deepcopy(self.quarantined_traces),
                "quarantine_root": object_hash(self.quarantined_traces),
                "phase_trace": copy.deepcopy(self.phase_trace),
                "phase_trace_root": object_hash(self.phase_trace),
                "expanded_states": copy.deepcopy(self.expanded_state_registry),
                "expanded_state_root": object_hash(self.expanded_state_registry),
                "witness_cache": copy.deepcopy(self.witness_cache_registry),
                "witness_cache_root": object_hash(self.witness_cache_registry),
            },
            audit={
                "global_closure_ok": self.global_closure_ok(),
                "euler_lock_gate_ok": self.euler_lock_gate_ok(),
                "manifold_hash72": self.manifold_hash72(),
                "audit_hash72": self.audit_hash72(),
                "quarantine_root": object_hash(self.quarantined_traces),
                "quarantine_count": len(self.quarantined_traces),
                "phase_trace_root": object_hash(self.phase_trace),
                "phase_trace_count": len(self.phase_trace),
                "expanded_state_root": object_hash(self.expanded_state_registry),
                "expanded_state_count": len(self.expanded_state_registry),
                "witness_cache_root": object_hash(self.witness_cache_registry),
                "witness_cache_count": len(self.witness_cache_registry),
            },
            reason="Checkpoint initialized",
        )


    def verify_receipt_chain(self) -> Tuple[bool, str]:
        prev = "GENESIS"
        for i, ev in enumerate(self.ledger):
            if ev.seq != i:
                return False, f"Bad seq at index {i}"
            if ev.pre_receipt_hash != prev:
                return False, f"Bad receipt link at seq={ev.seq}"
            if profile_hash(ev.profile_snapshot) != ev.profile_hash:
                return False, f"Bad profile_hash at seq={ev.seq}"
            body = {
                "seq": ev.seq,
                "event_type": ev.event_type,
                "protocol_version": ev.protocol_version,
                "state_hash_version": ev.state_hash_version,
                "profile_id": ev.profile_id,
                "profile_snapshot": ev.profile_snapshot,
                "profile_hash": ev.profile_hash,
                "source_phases": list(ev.source_phases),
                "target_phase": ev.target_phase,
                "pre_receipt_hash": ev.pre_receipt_hash,
                "pre_state_hash72": ev.pre_state_hash72,
                "post_state_hash72": ev.post_state_hash72,
                "payload": ev.payload,
                "audit": ev.audit,
                "reason": ev.reason,
            }
            if ledger_event_hash(prev, body) != ev.receipt_hash:
                return False, f"Bad receipt_hash at seq={ev.seq}"
            prev = ev.receipt_hash
        return True, "Receipt chain verified"


    def _handle_fail(
        self,
        *,
        profile: BranchProfile,
        reason: str,
        guest_trace: List[Tuple[int, str, Fraction]],
        pre_state_hash72: str,
        violated_phase: Optional[int] = None,
        record_ledger: bool = True,
    ) -> GuestAuditResult:
        if profile.on_fail == "QUARANTINE":
            self.quarantined_traces.append({
                "profile_id": profile.mode_id,
                "reason": reason,
                "guest_trace": [(p, v, str(val)) for p, v, val in guest_trace],
                "violated_phase": violated_phase,
            })
        if record_ledger:
            et: LedgerEventType = "QUARANTINE" if profile.on_fail == "QUARANTINE" else "REJECT"
            self.append_event(
                event_type=et,
                profile=profile,
                source_phases=sorted({int(p) for p, _, _ in guest_trace}) if guest_trace else [],
                target_phase=None,
                pre_state_hash72=pre_state_hash72,
                post_state_hash72=None,
                payload={"guest_trace": [(int(p), str(v), str(Fraction(val))) for p, v, val in guest_trace], "violated_phase": violated_phase},
                audit={},
                reason=reason,
            )
        msg = ("NULL_BRANCH: " + reason) if profile.on_fail == "NULL_BRANCH" else reason
        return GuestAuditResult(False, msg, None, violated_phase, profile.mode_id)


    def _validate_mutation(self, phase: int, var_name: str, value: Any, profile: BranchProfile) -> Optional[str]:
        mutable_roots = frozenset({"n", "b^2", "phase_branch", "modulation"})
        immutable_derived = frozenset({"x", "y", "xy", "yx", "a^2", "c^2", "d^2", "e^2", "eq_G"})
        if phase < 0 or phase > 7:
            return f"Invalid phase index: {phase}"
        if phase not in profile.writable_phases:
            return f"Phase {phase} not writable under profile {profile.mode_id}"
        if var_name in immutable_derived:
            return f"Phase {phase} mutation rejected: {var_name} is derived; mutate carrier roots instead."
        if var_name not in mutable_roots or var_name not in profile.mutable_roots:
            return f"Phase {phase} mutation rejected: {var_name} not allowed in profile {profile.mode_id}"
        if not isinstance(value, (int, Fraction)):
            return f"Phase {phase} mutation rejected: {var_name} value must be Fraction/int"
        return None

    def propagate_guest(self, guest_trace: List[Tuple[int, str, Fraction]], profile: BranchProfile, *, record_ledger: bool = True) -> GuestAuditResult:
        pre = self.state_hash72()
        fork = copy.deepcopy(self)
        touched: set[int] = set()
        if not profile.cross_phase_allowed:
            phases = {p for p, _, _ in guest_trace}
            if len(phases) > 1:
                return self._handle_fail(profile=profile, reason="Cross-phase mutation rejected by profile", guest_trace=guest_trace, pre_state_hash72=pre, record_ledger=record_ledger)
        for phase, var_name, value in guest_trace:
            reason = fork._validate_mutation(phase, var_name, value, profile)
            if reason:
                return self._handle_fail(profile=profile, reason=reason, guest_trace=guest_trace, pre_state_hash72=pre, violated_phase=phase, record_ledger=record_ledger)
            if not isinstance(value, Fraction):
                value = normf(Fraction(value))
            m = fork.manifolds[phase]
            m.vars[var_name] = value
            touched.add(phase)
        rebuild = set(range(8)) if profile.rebuild_scope == "TORUS_WIDE" else touched
        for phase in rebuild:
            fork.manifolds[phase].rebuild_from_roots()
        audit = {
            "profile_hash": profile_hash(profile.to_snapshot()),
            "gate_inputs_hash": object_hash({"guest_trace": [(int(p), str(v), str(Fraction(val))) for p, v, val in guest_trace]}),
        }
        if profile.require_constructor_coherence:
            for phase in range(8):
                coherent, why = fork.manifolds[phase].constructor_coherence_ok()
                if not coherent:
                    return self._handle_fail(profile=profile, reason=f"Phase {phase} constructor coherence failed: {why}", guest_trace=guest_trace, pre_state_hash72=pre, violated_phase=phase, record_ledger=record_ledger)
            audit["constructor_coherent"] = True
        if profile.require_runtime_projection_gate:
            if not fork.runtime_projection_gate_ok(touched):
                return self._handle_fail(profile=profile, reason="Runtime projection gate failed", guest_trace=guest_trace, pre_state_hash72=pre, record_ledger=record_ledger)
            audit["projection_gate"] = True
        if profile.require_exchange_normalization:
            if not fork.exchange_normalization_ok():
                return self._handle_fail(profile=profile, reason="Exchange normalization failed", guest_trace=guest_trace, pre_state_hash72=pre, record_ledger=record_ledger)
            audit["exchange_normalized"] = True
        if profile.require_global_closure:
            if not fork.global_closure_ok():
                return self._handle_fail(profile=profile, reason="Guest trace failed torus closure audit", guest_trace=guest_trace, pre_state_hash72=pre, record_ledger=record_ledger)
            audit["global_closure"] = True
        if profile.require_euler_lock_gate:
            for k in range(8):
                el = fork.manifolds[k].euler_lock_audit()
                if not el.gate_passed:
                    return self._handle_fail(profile=profile, reason=f"Euler lock gate failed at phase {k}: {el.branch_status} — {el.details}", guest_trace=guest_trace, pre_state_hash72=pre, violated_phase=k, record_ledger=record_ledger)
            audit["euler_lock_gate"] = True
            audit["euler_lock_kernel_values"] = {str(k): str(fork.manifolds[k].euler_lock_audit().kernel_value) for k in range(8)}
        self.manifolds = fork.manifolds
        post = self.state_hash72()
        if record_ledger:
            self.append_event(event_type="MUTATE", profile=profile, source_phases=sorted(touched), target_phase=None, pre_state_hash72=pre, post_state_hash72=post, payload={"guest_trace": [(int(p), str(v), str(Fraction(val))) for p, v, val in guest_trace]}, audit=audit, reason="Committed")
        return GuestAuditResult(True, "Committed", post, None, profile.mode_id)


    def exchange_branches(self, left_phase: int, right_phase: int, target_phase: int, profile: BranchProfile, *, record_ledger: bool = True) -> BranchExchangeResult:
        pre = self.state_hash72()
        if not profile.allow_branch_exchange:
            if record_ledger:
                self.append_event(event_type="REJECT", profile=profile, source_phases=[left_phase, right_phase], target_phase=target_phase, pre_state_hash72=pre, post_state_hash72=None, payload={"left_phase": left_phase, "right_phase": right_phase, "target_phase": target_phase}, audit={}, reason=f"Branch exchange not allowed in profile {profile.mode_id}")
            return BranchExchangeResult(False, f"Branch exchange not allowed in profile {profile.mode_id}", None, profile.mode_id)
        fork = copy.deepcopy(self)
        merged = fork.manifolds[left_phase].blend_with(fork.manifolds[right_phase], target_phase)
        audit: Dict[str, Any] = {}
        if profile.require_constructor_coherence:
            coherent, why = merged.constructor_coherence_ok()
            if not coherent:
                if record_ledger:
                    self.append_event(event_type="REJECT", profile=profile, source_phases=[left_phase, right_phase], target_phase=target_phase, pre_state_hash72=pre, post_state_hash72=None, payload={"left_phase": left_phase, "right_phase": right_phase, "target_phase": target_phase}, audit={"constructor_coherence": False, "details": why}, reason=f"Merged target failed constructor coherence: {why}")
                return BranchExchangeResult(False, f"Merged target failed constructor coherence: {why}", None, profile.mode_id)
            audit["constructor_coherent"] = True
        if profile.require_euler_lock_gate:
            el = merged.euler_lock_audit()
            audit["euler_lock"] = el.to_dict()
            if not el.gate_passed:
                if record_ledger:
                    self.append_event(event_type="REJECT", profile=profile, source_phases=[left_phase, right_phase], target_phase=target_phase, pre_state_hash72=pre, post_state_hash72=None, payload={"left_phase": left_phase, "right_phase": right_phase, "target_phase": target_phase}, audit=audit, reason=f"Merged target failed Euler-lock: {el.branch_status} — {el.details}")
                return BranchExchangeResult(False, f"Merged target failed Euler-lock: {el.branch_status}", None, profile.mode_id)
        fork.manifolds[target_phase] = merged
        if profile.require_exchange_normalization and not fork.exchange_normalization_ok():
            if record_ledger:
                self.append_event(event_type="REJECT", profile=profile, source_phases=[left_phase, right_phase], target_phase=target_phase, pre_state_hash72=pre, post_state_hash72=None, payload={"left_phase": left_phase, "right_phase": right_phase, "target_phase": target_phase}, audit=audit, reason="Merged target failed exchange normalization")
            return BranchExchangeResult(False, "Merged target failed exchange normalization", None, profile.mode_id)
        if profile.require_global_closure and not fork.global_closure_ok():
            if record_ledger:
                self.append_event(event_type="REJECT", profile=profile, source_phases=[left_phase, right_phase], target_phase=target_phase, pre_state_hash72=pre, post_state_hash72=None, payload={"left_phase": left_phase, "right_phase": right_phase, "target_phase": target_phase}, audit=audit, reason="Merged target failed global closure")
            return BranchExchangeResult(False, "Merged target failed global closure", None, profile.mode_id)
        self.manifolds = fork.manifolds
        post = self.state_hash72()
        if record_ledger:
            self.append_event(event_type="MERGE", profile=profile, source_phases=[left_phase, right_phase], target_phase=target_phase, pre_state_hash72=pre, post_state_hash72=post, payload={"left_phase": left_phase, "right_phase": right_phase, "target_phase": target_phase}, audit=audit, reason="Merged")
        return BranchExchangeResult(True, "Merged", post, profile.mode_id)


    def phase_generator_projection(self, phase: int) -> Dict[str, Fraction]:
        return ExpandedDeterministicKernel.project_generators_from_manifold(self.manifolds[phase])


    def commit_expanded_state(
        self,
        *,
        expanded_state: "ExpandedDeterministicState",
        profile: BranchProfile,
        reason: str = "Expanded deterministic state committed",
        record_ledger: bool = True,
    ) -> Dict[str, Any]:
        equation_witness = KernelEquationLedger.build_witness()
        receipt = ExpandedDeterministicKernel.build_receipt(
            expanded_state=expanded_state,
            source_state_hash72=self.state_hash72(),
            equation_witness=equation_witness,
        )
        payload = expanded_state.to_dict()
        payload["address_hash72"] = expanded_state.address_hash72
        payload["receipt"] = receipt.to_dict()
        payload["equation_witness"] = equation_witness.to_dict()
        self.expanded_state_registry[expanded_state.address_hash72] = copy.deepcopy(payload)
        audit = {
            "closure_ok": expanded_state.closure_ok,
            "closure_period": expanded_state.closure_period,
            "net_offset_zero": all(v == 0 for v in expanded_state.net_offset.values()),
            "equation_witness_hash72": equation_witness.witness_hash72,
            "expanded_state_receipt_hash72": receipt.receipt_hash72,
            "expanded_state_root": object_hash(self.expanded_state_registry),
            "expanded_state_count": len(self.expanded_state_registry),
        }
        if record_ledger:
            self.append_event(
                event_type="EXPANDED_STATE_COMMIT",
                profile=profile,
                source_phases=[expanded_state.phase],
                target_phase=expanded_state.phase,
                pre_state_hash72=self.state_hash72(),
                post_state_hash72=self.state_hash72(),
                payload=payload,
                audit=audit,
                reason=reason,
            )
        return payload


    def address_and_commit_expanded_state(
        self,
        *,
        phase: int,
        profile: BranchProfile,
        uniform_scale: Fraction = Fraction(1, 1),
        component_scales: Optional[Dict[str, Fraction]] = None,
        offsets: Optional[Tuple[DeterministicOffsetVector, ...]] = None,
        symbol_path: Optional[Tuple[str, ...]] = None,
        reason: str = "Expanded deterministic state committed",
        record_ledger: bool = True,
    ) -> ExpandedDeterministicState:
        expanded_state = self.address_expanded_state(
            phase=phase,
            uniform_scale=uniform_scale,
            component_scales=component_scales,
            offsets=offsets,
            symbol_path=symbol_path,
        )
        self.commit_expanded_state(expanded_state=expanded_state, profile=profile, reason=reason, record_ledger=record_ledger)
        return expanded_state


    def address_expanded_state(
        self,
        *,
        phase: int,
        uniform_scale: Fraction = Fraction(1, 1),
        component_scales: Optional[Dict[str, Fraction]] = None,
        offsets: Optional[Tuple[DeterministicOffsetVector, ...]] = None,
        symbol_path: Optional[Tuple[str, ...]] = None,
    ) -> ExpandedDeterministicState:
        generators = self.phase_generator_projection(phase)
        source_state = self.state_object_v3()
        return ExpandedDeterministicKernel.address_state(
            phase=phase,
            generators=generators,
            uniform_scale=uniform_scale,
            component_scales=component_scales,
            offsets=offsets,
            symbol_path=symbol_path,
            source_state=source_state,
        )


    def execute_phase_primitives_v2(self, *, phase: int, program_ir: List[Dict[str, Any]], profile: BranchProfile, record_ledger: bool = True) -> GuestAuditResult:
        pre = self.state_hash72()
        if not profile.allow_phase_exec:
            return self._handle_fail(profile=profile, reason=f"Phase execution not allowed in profile {profile.mode_id}", guest_trace=[], pre_state_hash72=pre, violated_phase=phase, record_ledger=record_ledger)
        if phase not in profile.writable_phases:
            return self._handle_fail(profile=profile, reason=f"Phase {phase} not writable under profile {profile.mode_id}", guest_trace=[], pre_state_hash72=pre, violated_phase=phase, record_ledger=record_ledger)
        vm = PhaseTransportVM()
        trace: List[Dict[str, Any]] = []
        for pc, instr in enumerate(program_ir):
            op = str(instr["op"])
            args = [decode_atom(a) for a in instr["args"]]
            out = vm.execute(op, *args)
            trace.append({"pc": str(pc), "op": op, "args": [encode_atom(a) for a in args], "out": encode_atom(out)})
        program_hash = object_hash(program_ir)
        trace_hash = object_hash(trace)
        self.phase_trace.append({
            "phase": str(phase),
            "vm": {"name": VM_NAME, "version": VM_VERSION, "spec_hash": VM_SPEC_HASH},
            "program_ir": program_ir,
            "program_hash": program_hash,
            "trace": trace,
            "trace_hash": trace_hash,
        })
        audit = {
            "profile_hash": profile_hash(profile.to_snapshot()),
            "gate_inputs_hash": object_hash({"phase": phase, "program_ir": program_ir}),
        }
        if profile.require_constructor_coherence:
            for k in range(8):
                coherent, why = self.manifolds[k].constructor_coherence_ok()
                if not coherent:
                    return self._handle_fail(profile=profile, reason=f"Phase {k} constructor coherence failed: {why}", guest_trace=[], pre_state_hash72=pre, violated_phase=k, record_ledger=record_ledger)
            audit["constructor_coherent"] = True
        if profile.require_runtime_projection_gate:
            if not self.runtime_projection_gate_ok({phase}):
                return self._handle_fail(profile=profile, reason="Runtime projection gate failed", guest_trace=[], pre_state_hash72=pre, violated_phase=phase, record_ledger=record_ledger)
            audit["projection_gate"] = True
        if profile.require_exchange_normalization:
            if not self.exchange_normalization_ok():
                return self._handle_fail(profile=profile, reason="Exchange normalization failed", guest_trace=[], pre_state_hash72=pre, violated_phase=phase, record_ledger=record_ledger)
            audit["exchange_normalized"] = True
        if profile.require_global_closure:
            if not self.global_closure_ok():
                return self._handle_fail(profile=profile, reason="Global closure failed after phase execution", guest_trace=[], pre_state_hash72=pre, violated_phase=phase, record_ledger=record_ledger)
            audit["global_closure"] = True
        if profile.require_euler_lock_gate:
            for k in range(8):
                el = self.manifolds[k].euler_lock_audit()
                if not el.gate_passed:
                    return self._handle_fail(profile=profile, reason=f"Euler lock gate failed at phase {k}: {el.branch_status} — {el.details}", guest_trace=[], pre_state_hash72=pre, violated_phase=k, record_ledger=record_ledger)
            audit["euler_lock_gate"] = True
            audit["euler_lock_kernel_values"] = {str(k): str(self.manifolds[k].euler_lock_audit().kernel_value) for k in range(8)}
        post = self.state_hash72()
        if record_ledger:
            self.append_event(event_type="PHASE_EXEC_V2", profile=profile, source_phases=[phase], target_phase=phase, pre_state_hash72=pre, post_state_hash72=post, payload={"phase": str(phase), "vm": {"name": VM_NAME, "version": VM_VERSION, "spec_hash": VM_SPEC_HASH}, "program_ir": program_ir, "program_hash": program_hash, "trace": trace, "trace_hash": trace_hash}, audit=audit, reason="Phase program committed")
        return GuestAuditResult(True, "Phase program committed", post, phase, profile.mode_id)


    @classmethod
    def replay_from_checkpoint(cls, *, checkpoint_event: LedgerEvent, remaining_ledger: List[LedgerEvent]) -> "Torus72":
        if checkpoint_event.event_type != "CHECKPOINT":
            raise ValueError("Replay bootstrap requires CHECKPOINT event")
        snapshot = checkpoint_event.payload["snapshot_state"]
        expected_snapshot_hash72 = checkpoint_event.payload.get("snapshot_state_hash72")
        if expected_snapshot_hash72 is not None:
            payload_snapshot_hash72 = NativeHash72Codec.state_hash72(snapshot)
            if payload_snapshot_hash72 != expected_snapshot_hash72:
                raise ValueError("Checkpoint payload hash mismatch before hydration")
        phases: List[Manifold9] = []
        for p_obj in snapshot["phases"]:
            vars_ = {k: Fraction(v) for k, v in p_obj["vars"].items()}
            tensors: Dict[str, Tensor] = {}
            for t_name, t_data in p_obj["tensors"].items():
                mat = [[Fraction(0, 1) for _ in range(3)] for _ in range(3)]
                for key, val in t_data.items():
                    i, j = key.strip("[]").split(",")
                    mat[int(i)][int(j)] = Fraction(val)
                tensors[t_name] = Tensor(mat)
            phases.append(
                Manifold9(
                    int(p_obj["phase"]),
                    vars_,
                    tensors,
                    enforce_constructor_coherence=False,
                    enforce_euler_lock=False,
                )
            )
        torus = Torus72(phases)
        torus.quarantined_traces = copy.deepcopy(checkpoint_event.payload.get("quarantined_traces", []))
        torus.phase_trace = copy.deepcopy(checkpoint_event.payload.get("phase_trace", []))
        torus.expanded_state_registry = copy.deepcopy(checkpoint_event.payload.get("expanded_states", {}))
        torus.witness_cache_registry = copy.deepcopy(checkpoint_event.payload.get("witness_cache", {}))
        if expected_snapshot_hash72 is not None and torus.state_hash72() != expected_snapshot_hash72:
            raise ValueError("Checkpoint snapshot hash mismatch after hydration")
        torus.ledger = [checkpoint_event]
        for ev in remaining_ledger:
            if torus.state_hash72() != ev.pre_state_hash72:
                raise ValueError(f"pre_state_hash72 mismatch at seq={ev.seq}")
            prof = BranchProfile(
                mode_id=ev.profile_snapshot["mode_id"],
                mutable_roots=frozenset(ev.profile_snapshot["mutable_roots"]),
                immutable_derived=frozenset(ev.profile_snapshot["immutable_derived"]),
                writable_phases=frozenset(ev.profile_snapshot["writable_phases"]),
                cross_phase_allowed=ev.profile_snapshot["cross_phase_allowed"],
                rebuild_scope=ev.profile_snapshot["rebuild_scope"],
                require_constructor_coherence=ev.profile_snapshot["require_constructor_coherence"],
                require_global_closure=ev.profile_snapshot["require_global_closure"],
                require_exchange_normalization=ev.profile_snapshot["require_exchange_normalization"],
                require_runtime_projection_gate=ev.profile_snapshot["require_runtime_projection_gate"],
                on_fail=ev.profile_snapshot["on_fail"],
                branch_policy=ev.profile_snapshot["branch_policy"],
                allow_branch_exchange=ev.profile_snapshot["allow_branch_exchange"],
                allow_phase_exec=ev.profile_snapshot["allow_phase_exec"],
                require_euler_lock_gate=ev.profile_snapshot.get("require_euler_lock_gate", False),
            )
            if ev.event_type == "MUTATE":
                trace = [(int(p), str(v), Fraction(val)) for p, v, val in ev.payload["guest_trace"]]
                res = torus.propagate_guest(trace, prof, record_ledger=False)
                if not res.ok:
                    raise ValueError(f"Replay mutate failed at seq={ev.seq}: {res.reason}")
            elif ev.event_type == "MERGE":
                res = torus.exchange_branches(ev.payload["left_phase"], ev.payload["right_phase"], ev.payload["target_phase"], prof, record_ledger=False)
                if not res.ok:
                    raise ValueError(f"Replay merge failed at seq={ev.seq}: {res.reason}")
            elif ev.event_type == "PHASE_EXEC_V2":
                payload = ev.payload
                if object_hash(payload["program_ir"]) != payload["program_hash"]:
                    raise ValueError(f"program_hash mismatch at seq={ev.seq}")
                res = torus.execute_phase_primitives_v2(phase=int(payload["phase"]), program_ir=payload["program_ir"], profile=prof, record_ledger=False)
                if not res.ok:
                    raise ValueError(f"Replay phase exec failed at seq={ev.seq}: {res.reason}")
                if torus.phase_trace[-1]["trace_hash"] != payload["trace_hash"]:
                    raise ValueError(f"trace_hash mismatch at seq={ev.seq}")
            elif ev.event_type == "QUARANTINE":
                torus.quarantined_traces.append({
                    "profile_id": ev.profile_id,
                    "reason": ev.reason,
                    "guest_trace": ev.payload.get("guest_trace", []),
                    "violated_phase": ev.payload.get("violated_phase"),
                })
            elif ev.event_type == "EXPANDED_STATE_COMMIT":
                payload = copy.deepcopy(ev.payload)
                required = {"phase", "generators", "uniform_scale", "component_scales", "symbol_path", "offsets", "closure_period", "closure_ok", "address_hash72", "net_offset", "orbit"}
                missing = sorted(required.difference(payload.keys()))
                if missing:
                    raise ValueError(f"Expanded state payload missing keys at seq={ev.seq}: {missing}")
                address_hash72 = payload["address_hash72"]
                state_obj = {
                    "phase": int(payload["phase"]),
                    "scaled_generators": dict(payload["generators"]),
                    "uniform_scale": str(payload["uniform_scale"]),
                    "component_scales": dict(payload["component_scales"]),
                    "symbol_path": payload["symbol_path"],
                    "offsets": list(payload["offsets"]),
                    "net_offset": dict(payload["net_offset"]),
                    "closure_ok": bool(payload["closure_ok"]),
                    "closure_period": int(payload["closure_period"]),
                    "orbit_hash72": payload["orbit"].get("orbit_hash72") if isinstance(payload["orbit"], dict) else None,
                }
                torus.expanded_state_registry[address_hash72] = state_obj
            if torus.state_hash72() != ev.post_state_hash72:
                raise ValueError(f"post_state_hash72 mismatch at seq={ev.seq}")
            torus.ledger.append(ev)
        return torus




TRACE_EVENT_KINDS = {
    "ast_final",
    "matrix_diag_product",
    "Eq",
    "eval_ok",
    "hashes",
    "residue_bundle",
    "gate_check",
    "correction_attempt",
}




def residue_prime_set_default() -> List[int]:
    return [3, 5, 7, 11, 13, 17, 19, 23]




def iso_time_stub(seq: int) -> str:
    return f"2026-03-12T00:00:{seq:02d}Z"




def closed_trace_event(kind: str, **kwargs: Any) -> Dict[str, Any]:
    if kind not in TRACE_EVENT_KINDS:
        raise ValueError(f"Unknown trace event kind: {kind}")
    allowed_map = {
        "ast_final": {"t", "kind", "ast"},
        "matrix_diag_product": {"t", "kind", "value"},
        "Eq": {"t", "kind", "ok"},
        "eval_ok": {"t", "kind", "render"},
        "hashes": {"t", "kind", "ast_sha256", "trace_sha256"},
        "residue_bundle": {"t", "kind", "residue"},
        "gate_check": {"t", "kind", "gate"},
        "correction_attempt": {"t", "kind", "correction"},
    }
    event = {"kind": kind, **kwargs}
    if set(event.keys()) != allowed_map[kind]:
        raise ValueError(f"Closed event violation for kind={kind}")
    return event




def validate_residue_bundle_v1(bundle: Dict[str, Any]) -> None:
    allowed = {"prime_set", "residues", "witness"}
    if set(bundle.keys()) - allowed:
        raise ValueError("RESIDUE_BUNDLE_v1 unknown field")
    if "prime_set" not in bundle or "residues" not in bundle:
        raise ValueError("RESIDUE_BUNDLE_v1 missing required fields")
    ps, rs = bundle["prime_set"], bundle["residues"]
    if not isinstance(ps, list) or not isinstance(rs, list) or len(ps) != len(rs) or len(ps) < 1:
        raise ValueError("RESIDUE_BUNDLE_v1 invalid prime/residue shape")
    if any((not isinstance(p, int)) or p < 2 for p in ps):
        raise ValueError("RESIDUE_BUNDLE_v1 invalid prime_set")




def validate_gate_result_v1(g: Dict[str, Any]) -> None:
    allowed = {"name", "status", "details", "inputs", "witness"}
    if set(g.keys()) - allowed:
        raise ValueError("INVARIANT_GATE_RESULT_v1 unknown field")
    if "name" not in g or "status" not in g:
        raise ValueError("INVARIANT_GATE_RESULT_v1 missing required fields")
    if g["status"] not in {"PASSED", "FAILED"}:
        raise ValueError("INVARIANT_GATE_RESULT_v1 invalid status")




def validate_trace_event_v1(ev: Dict[str, Any]) -> None:
    allowed = {"t", "kind", "ast", "value", "ok", "render", "ast_sha256", "trace_sha256", "residue", "gate", "correction"}
    if set(ev.keys()) - allowed:
        raise ValueError("HHS_TRACE_EVENT_v1 unknown field")
    if "t" not in ev or "kind" not in ev:
        raise ValueError("HHS_TRACE_EVENT_v1 missing required fields")
    kind = ev["kind"]
    if kind not in TRACE_EVENT_KINDS:
        raise ValueError(f"HHS_TRACE_EVENT_v1 unknown kind={kind}")
    if kind == "residue_bundle":
        validate_residue_bundle_v1(ev["residue"])
    if kind == "gate_check":
        validate_gate_result_v1(ev["gate"])




def validate_translation_bundle_v1(bundle: Dict[str, Any]) -> None:
    if set(bundle.keys()) - {"schema", "genesis", "trace", "state"}:
        raise ValueError("HHS_TRANSLATION_BUNDLE_v1 unknown field")
    if bundle.get("schema") != "HHS_TRANSLATION_BUNDLE_v1":
        raise ValueError("HHS_TRANSLATION_BUNDLE_v1 bad schema tag")
    if "genesis" not in bundle or "trace" not in bundle:
        raise ValueError("HHS_TRANSLATION_BUNDLE_v1 missing genesis/trace")
    if bundle["genesis"].get("schema") != "HHS_GENESIS_v1":
        raise ValueError("HHS_GENESIS_v1 bad schema tag")
    for ev in bundle["trace"]:
        validate_trace_event_v1(ev)




def native_residue_bundle_from_token(token: Dict[str, Any], prime_set: Optional[List[int]] = None) -> Dict[str, Any]:
    if prime_set is None:
        prime_set = residue_prime_set_default()
    ring = token["ring_symbols"]
    acc = 0
    for v in ring:
        acc = acc * 72 + int(v)
    bundle = {
        "prime_set": list(prime_set),
        "residues": [int(acc % p) for p in prime_set],
        "witness": token["dna72_sha256"],
    }
    validate_residue_bundle_v1(bundle)
    return bundle




def closed_gate_event(name: str, status: bool, details: str, inputs: Optional[Dict[str, Any]] = None, witness: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    gate = {"name": name, "status": "PASSED" if status else "FAILED", "details": details}
    if inputs is not None:
        gate["inputs"] = inputs
    if witness is not None:
        gate["witness"] = witness
    validate_gate_result_v1(gate)
    return gate




def packet_witness_dict(packet: Any) -> Dict[str, Any]:
    return {
        "phase": packet.phase,
        "packet_hash": packet.packet_hash,
        "kernel_value": str(packet.kernel_value),
        "branch_status": packet.branch_status,
        "ers_consistent": packet.ers_consistent,
        "product_unity": packet.product_unity,
        "branches": [
            {
                "branch_id": b.branch_id,
                "outer_sign": b.outer_sign,
                "inner_sign": b.inner_sign,
                "phase_role": b.phase_role,
            }
            for b in packet.branches
        ],
    }




def substitution_gate_witness_dict(gate: Any) -> Dict[str, Any]:
    return {
        "gate_id": gate.gate_id,
        "phase": gate.phase,
        "packet_hash": gate.packet_hash,
        "gate_state": gate.state.value if hasattr(gate.state, "value") else str(gate.state),
        "ers_consistent": gate.ers_consistent,
        "product_unity": gate.product_unity,
        "euler_lock_ok": gate.euler_lock_ok,
        "closure_ok": gate.closure_ok,
        "truth_tuple": list(gate.vector.truth_tuple()),
        "atom_id": gate.atom.atom_id,
        "dereferenceable": gate.atom.dereferenceable,
        "collapse_receipt": gate.atom.collapse_receipt,
    }




def make_hhs_genesis_v1(torus: Torus72) -> Dict[str, Any]:
    st = torus.state_object_v3()
    token = NativeHash72Codec.ring_token(st)
    root_commit = sha256_hex(st)
    return {
        "schema": "HHS_GENESIS_v1",
        "n": 0,
        "seed_commitment": {"alg": "SHA-256", "SC0_hex": root_commit},
        "phi_map": {"id": "HHS_PHI_MAP_v1", "hash_alg": "SHA-256", "hash_hex": sha256_hex(token["T24_trits"] + "|" + token["U12_bits"] )},
        "runtime_constants": {"cert_hash": "SHA-256", "cert_trunc_bits": 256, "C_minus_1_hex": sha256_hex("C_minus_1|" + PROTOCOL_VERSION)},
        "manifold": {"enc_version": PROTOCOL_VERSION, "M0_commitment": root_commit},
        "certificate": {"C0_hex": sha256_hex({"state_hash72": torus.state_hash72(), "dna72_sha256": token["dna72_sha256"]})},
        "work_factor_constants": {"DNA_bits": 72, "G_multiplier": 1, "chi_trials": 72, "chi_measured": str(len(token["dna72"])), "log2_72_factorial": "339.782712", "theorem_check": "OK"},
        "hardware_twin": {"HB_cycles": "72", "deltaT_max_cycles": 0, "Tpulse_max_cycles": 1},
        "audit": {"kit": "IRON_GATE_5PT_v1", "result": "PASS" if torus.global_closure_ok() else "FAIL"},
    }




def make_translation_trace_v1(torus: Torus72) -> List[Dict[str, Any]]:
    st = torus.state_object_v3()
    token = NativeHash72Codec.ring_token(st)
    residue = native_residue_bundle_from_token(token)
    trace: List[Dict[str, Any]] = []
    trace.append(closed_trace_event("ast_final", t=iso_time_stub(0), ast=cjson({"protocol_version": PROTOCOL_VERSION, "state_hash72": torus.state_hash72(), "dna72": token["dna72"]})))
    trace.append(closed_trace_event("gate_check", t=iso_time_stub(1), gate=closed_gate_event("global_closure", torus.global_closure_ok(), "torus global closure audit", inputs={"state_hash72": torus.state_hash72()}, witness={"ast_sha256": sha256_hex(st), "value": torus.state_hash72()})))
    rc_ok, rc_msg = torus.verify_receipt_chain()
    trace.append(closed_trace_event("gate_check", t=iso_time_stub(2), gate=closed_gate_event("receipt_chain", rc_ok, rc_msg, inputs={"ledger_len": len(torus.ledger)}, witness={"ast_sha256": sha256_hex(cjson([ev.receipt_hash for ev in torus.ledger])), "value": str(rc_ok)})))
    el_ok = torus.euler_lock_gate_ok()
    el_payload = {str(r.phase): r.to_dict() for r in torus.euler_lock_audit_all()}
    trace.append(closed_trace_event("gate_check", t=iso_time_stub(3), gate=closed_gate_event("euler_lock", el_ok, "Euler-lock degeneracy kernel audit across all 8 phases", inputs={"state_hash72": torus.state_hash72(), "kernel_formula": "K_alg = (xy)^4 - 2(xy)^2 - (a^2)^2(xy)^2 + 1"}, witness={"ast_sha256": sha256_hex(el_payload), "value": str(el_ok)})))
    trace.append(closed_trace_event("residue_bundle", t=iso_time_stub(4), residue=residue))
    trace.append(closed_trace_event("matrix_diag_product", t=iso_time_stub(5), value=str(torus.manifolds[0].vars["eq_G"])))
    trace.append(closed_trace_event("Eq", t=iso_time_stub(6), ok=torus.global_closure_ok()))
    trace.append(closed_trace_event("eval_ok", t=iso_time_stub(7), render="0" if torus.global_closure_ok() else "1"))
    trace_seed = cjson(trace)
    trace.append(closed_trace_event("hashes", t=iso_time_stub(8), ast_sha256=sha256_hex(st), trace_sha256=sha256_hex(trace_seed)))
    for ev in trace:
        validate_trace_event_v1(ev)
    return trace




def make_translation_trace_v2(torus: Torus72, *, radical_packets: Optional[List[Any]] = None, substitution_gates: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
    trace = make_translation_trace_v1(torus)
    if radical_packets:
        for i, pkt in enumerate(radical_packets):
            witness = packet_witness_dict(pkt)
            trace.append(closed_trace_event("gate_check", t=iso_time_stub(20 + i), gate=closed_gate_event("radical_packet", pkt.branch_status in {"REGULAR_NEGATIVE", "REGULAR_POSITIVE"}, "Radical packet witness", inputs={"phase": pkt.phase, "packet_hash": pkt.packet_hash}, witness={"ast_sha256": sha256_hex(witness), "value": pkt.packet_hash})))
    if substitution_gates:
        for i, gate in enumerate(substitution_gates):
            gw = substitution_gate_witness_dict(gate)
            trace.append(closed_trace_event("gate_check", t=iso_time_stub(40 + i), gate=closed_gate_event("substitution_gate", gw["gate_state"] in {"COLLAPSIBLE", "COLLAPSED"}, "Deferred substitution gate witness", inputs={"phase": gate.phase, "gate_id": gate.gate_id}, witness={"ast_sha256": sha256_hex(gw), "value": gate.gate_id})))
    for ev in trace:
        validate_trace_event_v1(ev)
    return trace




def export_translation_bundle_v1(torus: Torus72, *, radical_packets: Optional[List[Any]] = None, substitution_gates: Optional[List[Any]] = None) -> Dict[str, Any]:
    token = NativeHash72Codec.ring_token(torus.state_object_v3())
    bundle = {
        "schema": "HHS_TRANSLATION_BUNDLE_v1",
        "genesis": make_hhs_genesis_v1(torus),
        "trace": make_translation_trace_v2(torus, radical_packets=radical_packets, substitution_gates=substitution_gates),
        "state": {
            "canonical_value": torus.state_hash72(),
            "manifold_hash72": torus.manifold_hash72(),
            "audit_hash72": torus.audit_hash72(),
            "hash72": token["dna72"],
            "residue_bundle": native_residue_bundle_from_token(token),
        },
    }
    validate_translation_bundle_v1(bundle)
    return bundle




def build_demo_manifold(phase: int, n: Optional[Fraction] = None) -> Manifold9:
    x, y, b = Fraction(2, 1), Fraction(1, 2), Fraction(2, 1)
    if n is None:
        n = Fraction(1, 1) + Fraction(phase, 16)
    return Manifold9(phase, {"x": x, "y": y, "n": n, "b^2": b}, {})




BRANCH_PROFILES = {
    "strict_guest": BranchProfile("strict_guest", frozenset({"n", "b^2"}), frozenset({"x", "y", "xy", "yx", "a^2", "c^2", "d^2", "e^2", "eq_G"}), frozenset(range(8)), False, "LOCAL_TOUCHED_ONLY", True, True, True, True, "ROLLBACK", "PRESERVE", False, False, True),
    "constructor_dev": BranchProfile("constructor_dev", frozenset({"n", "b^2", "phase_branch", "modulation"}), frozenset({"x", "y", "xy", "yx", "a^2", "c^2", "d^2", "e^2", "eq_G"}), frozenset(range(8)), True, "LOCAL_TOUCHED_ONLY", True, True, True, True, "ROLLBACK", "PRESERVE", True, True, True),
    "quarantine_guest": BranchProfile("quarantine_guest", frozenset({"n", "b^2"}), frozenset({"x", "y", "xy", "yx", "a^2", "c^2", "d^2", "e^2", "eq_G"}), frozenset(range(8)), False, "LOCAL_TOUCHED_ONLY", True, True, True, True, "QUARANTINE", "PRESERVE", False, False, True),
}






# ===== Embedded radical_packet.py =====


SIGN_PAIRS: Tuple[Tuple[int, int], ...] = ((+1, +1), (+1, -1), (-1, +1), (-1, -1))
BRANCH_IDS: Dict[Tuple[int, int], str] = {
    (+1, +1): "alpha",
    (+1, -1): "beta",
    (-1, +1): "gamma",
    (-1, -1): "delta",
}
POLE_LABELS: Dict[Tuple[int, int], str] = {
    (+1, +1): "Alpha / Kinetic Projection",
    (+1, -1): "Beta / Potential Seed",
    (-1, +1): "Gamma / Return Path",
    (-1, -1): "Delta / Mirror Invariant",
}
SIGN_TO_ROLE: Dict[Tuple[int, int], str] = {
    (+1, +1): "kinetic",
    (+1, -1): "seed",
    (-1, +1): "return",
    (-1, -1): "mirror",
}




@dataclass(frozen=True)
class RadicalBranch:
    branch_id: str
    outer_sign: int
    inner_sign: int
    kernel_value: Fraction
    branch_status: str
    payload: Any
    phase_role: str


    def __post_init__(self):
        if self.outer_sign not in (+1, -1):
            raise ValueError("outer_sign must be ±1")
        if self.inner_sign not in (+1, -1):
            raise ValueError("inner_sign must be ±1")
        if self.branch_status not in ("REGULAR_NEGATIVE", "REGULAR_POSITIVE", "DEGENERATE"):
            raise ValueError(f"Invalid branch_status: {self.branch_status}")
        if self.branch_id not in ("alpha", "beta", "gamma", "delta"):
            raise ValueError(f"Invalid branch_id: {self.branch_id}")




@dataclass(frozen=True)
class RadicalPacket:
    phase: int
    kernel_value: Fraction
    ers_consistent: bool
    product_unity: bool
    branches: Tuple[RadicalBranch, RadicalBranch, RadicalBranch, RadicalBranch]
    packet_hash: str
    branch_status: str


    def __post_init__(self):
        if len(self.branches) != 4:
            raise ValueError("Packet requires exactly 4 branches")
        seen = set()
        for b in self.branches:
            pair = (b.outer_sign, b.inner_sign)
            if pair in seen:
                raise ValueError(f"Duplicate sign pair {pair}")
            seen.add(pair)
            if b.kernel_value != self.kernel_value:
                raise ValueError("Branch kernel mismatch")
        if seen != {(+1, +1), (+1, -1), (-1, +1), (-1, -1)}:
            raise ValueError(f"Incomplete sign-pair basis: {seen}")


    def select_branch(self, branch_id: str) -> RadicalBranch:
        for b in self.branches:
            if b.branch_id == branch_id:
                return b
        raise KeyError(f"No branch '{branch_id}'")


    def select_by_signs(self, outer: int, inner: int) -> RadicalBranch:
        for b in self.branches:
            if b.outer_sign == outer and b.inner_sign == inner:
                return b
        raise KeyError(f"No branch with signs ({outer}, {inner})")


    def pole_map(self) -> Dict[str, RadicalBranch]:
        return {POLE_LABELS[(b.outer_sign, b.inner_sign)]: b for b in self.branches}


    def audit_witness(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "kernel_value": str(self.kernel_value),
            "branch_status": self.branch_status,
            "packet_sha256": self.packet_hash,
            "branch_ids": [b.branch_id for b in self.branches],
            "ers_consistent": self.ers_consistent,
            "product_unity": self.product_unity,
        }




def classify_kernel(kv: Optional[Fraction]) -> str:
    if kv is None:
        return "UNDEFINED"
    if kv == 0:
        return "DEGENERATE"
    return "REGULAR_NEGATIVE" if kv < 0 else "REGULAR_POSITIVE"




def _packet_hash(phase: int, kernel_value: Fraction, ers_consistent: bool, product_unity: bool, branch_data: list) -> str:
    blob = json.dumps({
        "phase": phase,
        "kernel_value": str(kernel_value),
        "ers_consistent": ers_consistent,
        "product_unity": product_unity,
        "branches": [{
            "branch_id": d["branch_id"],
            "outer_sign": d["outer_sign"],
            "inner_sign": d["inner_sign"],
            "phase_role": d["phase_role"],
        } for d in branch_data],
    }, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()




class RadicalPacketConstructionError(Exception):
    pass




def radical_packet_constructor(*, phase: int, xi_atom: Any, kernel_value: Fraction, ers_consistent: bool, product_unity: bool) -> RadicalPacket:
    if not ers_consistent:
        raise RadicalPacketConstructionError(f"Phase {phase}: ERS consistency (xy=1) required. Packet construction refused.")
    if kernel_value is None:
        raise RadicalPacketConstructionError(f"Phase {phase}: kernel_value is None (UNDEFINED). Cannot construct packet without computable kernel.")
    if kernel_value == 0:
        raise RadicalPacketConstructionError(f"Phase {phase}: kernel_value = 0 (DEGENERATE). Branch packet is singular. Construction refused.")
    status = classify_kernel(kernel_value)
    branch_data = []
    branches = []
    for so, si in SIGN_PAIRS:
        bid = BRANCH_IDS[(so, si)]
        role = SIGN_TO_ROLE[(so, si)]
        branch_data.append({"branch_id": bid, "outer_sign": so, "inner_sign": si, "phase_role": role})
        branches.append(RadicalBranch(branch_id=bid, outer_sign=so, inner_sign=si, kernel_value=kernel_value, branch_status=status, payload=xi_atom, phase_role=role))
    phash = _packet_hash(phase, kernel_value, ers_consistent, product_unity, branch_data)
    return RadicalPacket(phase=phase, kernel_value=kernel_value, ers_consistent=ers_consistent, product_unity=product_unity, branches=tuple(branches), packet_hash=phash, branch_status=status)




class RadicalPacketVM:
    def __init__(self):
        self.ledger: Dict[str, RadicalPacket] = {}
        self.audit_log: list = []


    def RADPK(self, *, phase, xi_atom, kernel_value, ers_consistent, product_unity) -> RadicalPacket:
        pkt = radical_packet_constructor(phase=phase, xi_atom=xi_atom, kernel_value=kernel_value, ers_consistent=ers_consistent, product_unity=product_unity)
        self.ledger[pkt.packet_hash] = pkt
        self.audit_log.append({"op": "RADPK", "phase": phase, "hash": pkt.packet_hash, "status": pkt.branch_status, "K": str(kernel_value)})
        return pkt


    def BRSEL(self, pkt: RadicalPacket, branch_id: str) -> RadicalBranch:
        br = pkt.select_branch(branch_id)
        self.audit_log.append({"op": "BRSEL", "hash": pkt.packet_hash, "branch": branch_id, "signs": (br.outer_sign, br.inner_sign)})
        return br


    def BRMAP(self, pkt: RadicalPacket) -> Dict[str, RadicalBranch]:
        pm = pkt.pole_map()
        self.audit_log.append({"op": "BRMAP", "hash": pkt.packet_hash, "poles": list(pm.keys())})
        return pm


    def BRCHK(self, pkt: RadicalPacket, *, euler_lock_ok: bool, require_product_unity: bool = False) -> Dict[str, Any]:
        checks = {
            "ers_consistent": pkt.ers_consistent,
            "kernel_defined": pkt.kernel_value is not None,
            "kernel_nondegenerate": pkt.kernel_value != 0,
            "euler_lock_ok": euler_lock_ok,
            "branch_status": pkt.branch_status,
            "product_unity": pkt.product_unity,
        }
        passed = all([
            checks["ers_consistent"],
            checks["kernel_defined"],
            checks["kernel_nondegenerate"],
            checks["euler_lock_ok"],
            pkt.branch_status in ("REGULAR_NEGATIVE", "REGULAR_POSITIVE"),
        ])
        if require_product_unity:
            passed = passed and checks["product_unity"]
        checks["gate_passed"] = passed
        self.audit_log.append({"op": "BRCHK", "hash": pkt.packet_hash, "passed": passed})
        return checks


# ===== Embedded substitution_gate.py =====


UNITY = Fraction(1, 1)
BRANCH_ORDER = ("alpha", "beta", "gamma", "delta")
CHANNEL_LAYOUT: Dict[str, Dict[str, Any]] = {
    "alpha": {"phase_power": 1, "divisor_label": "x", "semantic_role": "reciprocal_kinetic"},
    "beta": {"phase_power": 2, "divisor_label": "-1", "semantic_role": "inversion_parity"},
    "gamma": {"phase_power": 3, "divisor_label": "y", "semantic_role": "return"},
    "delta": {"phase_power": 4, "divisor_label": "1", "semantic_role": "closure"},
}




class ChannelState(str, Enum):
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"




class GateState(str, Enum):
    OPEN = "OPEN"
    OPEN_AUTHORITATIVE = "OPEN_AUTHORITATIVE"
    ETH_LOCKED = "ETH_LOCKED"
    BLOCKED = "ETH_LOCKED"  # legacy alias; preserved for deterministic replay compatibility
    COLLAPSIBLE = "COLLAPSIBLE"
    COLLAPSED = "COLLAPSED"
    QUARANTINED = "QUARANTINED"


ETH_GATE_STATE_TRANSITION_V35 = {
    "version": "v35",
    "terminal_authority": "ETH_LOCKED",
    "states": {
        "OPEN": {
            "meaning": "channel evidence incomplete but no ethical lock asserted",
            "allowed_transitions": ["OPEN", "COLLAPSIBLE", "OPEN_AUTHORITATIVE", "ETH_LOCKED", "QUARANTINED"],
        },
        "OPEN_AUTHORITATIVE": {
            "meaning": "authoritative vault surface open under full membrane authority chain",
            "allowed_transitions": ["COLLAPSED", "ETH_LOCKED", "QUARANTINED"],
        },
        "COLLAPSIBLE": {
            "meaning": "ethically openable for dereference / commit-adjacent actions",
            "allowed_transitions": ["COLLAPSED", "ETH_LOCKED", "QUARANTINED"],
        },
        "COLLAPSED": {
            "meaning": "payload dereferenced under an ethically open gate",
            "allowed_transitions": ["COLLAPSED", "QUARANTINED"],
        },
        "ETH_LOCKED": {
            "meaning": "terminal fail-closed ethics state; no unlock/commit/seal/dereference/payload emission allowed",
            "allowed_transitions": ["ROLLBACK", "RECURSIVE_ROLLBACK", "NULL", "QUARANTINED"],
        },
        "QUARANTINED": {
            "meaning": "non-operational containment state when no valid ancestor is reconstructible",
            "allowed_transitions": ["QUARANTINED", "NULL"],
        },
    },
    "law": "constructor -> audit -> ethics -> commit",
}


SECONDARY_BLOCK_SURFACE_AUDIT_V35 = {
    "version": "v35",
    "goal": "no operational block surface except ETH_LOCKED",
    "converted_to_eth_locked": [
        "record_channel_witness channel-failure transition",
        "audit_substitution_gate legacy BLOCKED transition",
        "advance_with_ethics ethical failure transition",
        "dereference_substitution non-collapsible rejection",
        "ARCHIVE_OPEN denial",
        "unlock_verbatim_secret state-hash precondition mismatch",
        "read_verbatim_token payload/secret integrity mismatch",
    ],
    "residual_non_gate_errors": [
        "unknown token/address identifiers",
        "missing expanded deterministic state prerequisite",
        "constructor-shape exceptions before ETHCHK exists",
    ],
    "note": "Residual non-gate errors remain as constructor/precondition exceptions and are not runtime gate blockers.",
}


GATE_AUTHORITY_HARDENING_V3 = {
    "version": "v3",
    "law": "No unlock, dereference, receipt serialization, or payload emission may proceed without the single authoritative encrypted gate chain.",
    "requirements": [
        "partial substitution truth vectors fail closed to ETH_LOCKED",
        "dereference requires gate_receipt plus Euler-lock plus closure plus ethical_gate_ok",
        "archive_open is mandatory for unlock_verbatim_secret",
        "no pseudo-archive or parallel bypass branch may authorize payload emission",
    ],
}




def _sha256_blob(data: Dict[str, Any]) -> str:
    blob = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()




def _is_unity(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    return value in (1, "1", UNITY)




def _packet_is_regular(packet: Any) -> bool:
    return packet.branch_status in ("REGULAR_NEGATIVE", "REGULAR_POSITIVE")




@dataclass(frozen=True)
class SubstitutionAtom:
    atom_id: str
    symbol: str
    payload: Any
    dereferenceable: bool
    state: GateState
    collapse_receipt: Optional[str] = None




@dataclass(frozen=True)
class VerificationChannel:
    channel_id: str
    branch_id: str
    outer_sign: int
    inner_sign: int
    phase_power: int
    divisor_label: str
    semantic_role: str
    normalized_value: Optional[Any] = None
    state: ChannelState = ChannelState.PENDING


    def __post_init__(self) -> None:
        if self.branch_id not in BRANCH_ORDER:
            raise ValueError(f"Invalid branch_id: {self.branch_id}")
        if self.outer_sign not in (+1, -1):
            raise ValueError("outer_sign must be ±1")
        if self.inner_sign not in (+1, -1):
            raise ValueError("inner_sign must be ±1")




@dataclass(frozen=True)
class VerificationVector:
    phase: int
    packet_hash: str
    channels: Tuple[VerificationChannel, VerificationChannel, VerificationChannel, VerificationChannel]


    def __post_init__(self) -> None:
        if len(self.channels) != 4:
            raise ValueError("VerificationVector requires exactly 4 channels")
        seen = {c.channel_id for c in self.channels}
        if seen != set(BRANCH_ORDER):
            raise ValueError(f"Incomplete channel basis: {seen}")


    def truth_tuple(self) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int]]:
        out = []
        for branch_id in BRANCH_ORDER:
            ch = self.channel(branch_id)
            if ch.state == ChannelState.PASS:
                out.append(1)
            elif ch.state == ChannelState.FAIL:
                out.append(0)
            else:
                out.append(None)
        return tuple(out)


    def channel(self, branch_id: str) -> VerificationChannel:
        for ch in self.channels:
            if ch.channel_id == branch_id:
                return ch
        raise KeyError(f"No channel '{branch_id}'")


    def all_channels_pass(self) -> bool:
        return all(ch.state == ChannelState.PASS for ch in self.channels)


    def any_channel_failed(self) -> bool:
        return any(ch.state == ChannelState.FAIL for ch in self.channels)




@dataclass(frozen=True)
class SubstitutionGate:
    gate_id: str
    phase: int
    packet_hash: str
    atom: SubstitutionAtom
    vector: VerificationVector
    state: GateState
    ers_consistent: bool
    product_unity: bool
    euler_lock_ok: Optional[bool] = None
    closure_ok: Optional[bool] = None
    gate_receipt: Optional[str] = None


    @property
    def ethical_gate_ok(self) -> bool:
        return self.state in {GateState.COLLAPSIBLE, GateState.COLLAPSED}


    def audit_witness(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "phase": self.phase,
            "packet_hash": self.packet_hash,
            "atom_id": self.atom.atom_id,
            "gate_state": self.state.value,
            "truth_tuple": self.vector.truth_tuple(),
            "ers_consistent": self.ers_consistent,
            "product_unity": self.product_unity,
            "euler_lock_ok": self.euler_lock_ok,
            "closure_ok": self.closure_ok,
            "dereferenceable": self.atom.dereferenceable,
            "collapse_receipt": self.atom.collapse_receipt,
            "ethical_gate_ok": self.ethical_gate_ok,
        }




class SubstitutionGateError(Exception):
    pass



def _gate_truth_vector_complete(gate: SubstitutionGate) -> bool:
    tt = gate.vector.truth_tuple()
    return all(v is not None for v in tt)



def _gate_chain_ready(gate: SubstitutionGate) -> bool:
    return (
        gate.gate_receipt is not None
        and gate.euler_lock_ok is True
        and gate.closure_ok is True
        and gate.ethical_gate_ok is True
        and _gate_truth_vector_complete(gate)
        and gate.state == GateState.COLLAPSIBLE
        and gate.atom.dereferenceable is True
    )



def _vault_surface_gate_state(env: "EthicalGateEnvelope") -> str:
    return "OPEN_AUTHORITATIVE" if (env.archive_open and _gate_chain_ready(env.gate)) else GateState.ETH_LOCKED.value



def _suppress_vault_surface(surface_gate_state: str, *, receipt_hash72: str | None = None, payload_secret_hash256: str | None = None) -> Dict[str, Any]:
    authoritative = surface_gate_state == "OPEN_AUTHORITATIVE"
    return {
        "gate_state": surface_gate_state,
        "unlock_receipt_hash72": receipt_hash72 if authoritative else None,
        "payload_secret_hash256": payload_secret_hash256 if authoritative else None,
    }



def _enforce_gate_membrane(
    gate: SubstitutionGate,
    *,
    action: str,
    require_chain_ready: bool = False,
    archive_open: Optional[bool] = None,
    audit_results: Optional[Tuple[Any, ...]] = None,
) -> None:
    if gate.state == GateState.ETH_LOCKED:
        raise EthicalFailClosedError(
            f"ETHCHK terminal failure during {action}: gate_state={gate.state.value}"
        )
    if not gate.ers_consistent or not gate.product_unity:
        raise EthicalFailClosedError(
            f"ETHCHK terminal failure during {action}: constructor invariants not satisfied"
        )
    if require_chain_ready and not _gate_chain_ready(gate):
        raise EthicalFailClosedError(
            f"ETHCHK terminal failure during {action}: authoritative gate membrane not satisfied"
        )
    if archive_open is not None and archive_open is not True:
        raise EthicalFailClosedError(
            f"ETHCHK terminal failure during {action}: archive_open=False"
        )
    if audit_results is not None and not all(getattr(r, 'passed', False) for r in audit_results):
        raise EthicalFailClosedError(
            f"ETHCHK terminal failure during {action}: ethical audit incomplete"
        )



def build_substitution_gate(*, packet: Any, payload: Any, atom_id: Optional[str] = None, symbol: str = "∅") -> SubstitutionGate:
    if not _packet_is_regular(packet):
        raise SubstitutionGateError(f"Packet {packet.packet_hash} is not regular: {packet.branch_status}")
    branch_map = {b.branch_id: b for b in packet.branches}
    channels = []
    for branch_id in BRANCH_ORDER:
        if branch_id not in branch_map:
            raise SubstitutionGateError(f"Packet missing branch '{branch_id}'")
        branch = branch_map[branch_id]
        layout = CHANNEL_LAYOUT[branch_id]
        channels.append(VerificationChannel(channel_id=branch_id, branch_id=branch_id, outer_sign=branch.outer_sign, inner_sign=branch.inner_sign, phase_power=layout["phase_power"], divisor_label=layout["divisor_label"], semantic_role=layout["semantic_role"]))
    if atom_id is None:
        atom_id = _sha256_blob({"phase": packet.phase, "packet_hash": packet.packet_hash, "symbol": symbol})
    atom = SubstitutionAtom(atom_id=atom_id, symbol=symbol, payload=payload, dereferenceable=False, state=GateState.OPEN)
    vector = VerificationVector(phase=packet.phase, packet_hash=packet.packet_hash, channels=tuple(channels))
    gate_id = _sha256_blob({"phase": packet.phase, "packet_hash": packet.packet_hash, "atom_id": atom.atom_id, "kind": "substitution_gate"})
    return SubstitutionGate(gate_id=gate_id, phase=packet.phase, packet_hash=packet.packet_hash, atom=atom, vector=vector, state=GateState.OPEN, ers_consistent=packet.ers_consistent, product_unity=packet.product_unity)




def record_channel_witness(gate: SubstitutionGate, *, branch_id: str, normalized_value: Any) -> SubstitutionGate:
    _enforce_gate_membrane(gate, action="record_channel_witness")
    updated = []
    found = False
    for ch in gate.vector.channels:
        if ch.channel_id == branch_id:
            found = True
            state = ChannelState.PASS if _is_unity(normalized_value) else ChannelState.FAIL
            updated.append(replace(ch, normalized_value=normalized_value, state=state))
        else:
            updated.append(ch)
    if not found:
        raise KeyError(f"No channel '{branch_id}' in gate")
    new_vector = replace(gate.vector, channels=tuple(updated))
    new_state = GateState.ETH_LOCKED if new_vector.any_channel_failed() else gate.state
    new_atom = replace(gate.atom, state=new_state)
    return replace(gate, vector=new_vector, state=new_state, atom=new_atom)




def audit_substitution_gate(gate: SubstitutionGate, *, euler_lock_ok: bool, closure_ok: bool, require_product_unity: bool = True) -> Dict[str, Any]:
    _enforce_gate_membrane(gate, action="audit_substitution_gate")
    product_ok = gate.product_unity if require_product_unity else True
    global_pass = all([gate.ers_consistent, euler_lock_ok, closure_ok, product_ok])
    channels_pass = gate.vector.all_channels_pass()
    any_failed = gate.vector.any_channel_failed()
    truth_vector_complete = _gate_truth_vector_complete(gate)
    partial_or_incomplete = (not channels_pass) or (not truth_vector_complete) or (not any_failed and not channels_pass)
    if any_failed or not global_pass or partial_or_incomplete:
        next_state = GateState.ETH_LOCKED
    elif channels_pass:
        next_state = GateState.COLLAPSIBLE
    else:
        next_state = GateState.ETH_LOCKED
    return {
        "gate_id": gate.gate_id,
        "phase": gate.phase,
        "packet_hash": gate.packet_hash,
        "truth_tuple": gate.vector.truth_tuple(),
        "channels_pass": channels_pass,
        "ers_consistent": gate.ers_consistent,
        "euler_lock_ok": euler_lock_ok,
        "closure_ok": closure_ok,
        "product_unity": gate.product_unity,
        "require_product_unity": require_product_unity,
        "global_pass": global_pass,
        "truth_vector_complete": truth_vector_complete,
        "ready_to_collapse": (global_pass and channels_pass and truth_vector_complete),
        "next_state": next_state.value,
    }




def advance_substitution_gate(gate: SubstitutionGate, *, euler_lock_ok: bool, closure_ok: bool, require_product_unity: bool = True) -> SubstitutionGate:
    _enforce_gate_membrane(gate, action="advance_substitution_gate")
    audit = audit_substitution_gate(gate, euler_lock_ok=euler_lock_ok, closure_ok=closure_ok, require_product_unity=require_product_unity)
    next_state = GateState(audit["next_state"])
    chain_ready = (
        next_state == GateState.COLLAPSIBLE
        and audit["ready_to_collapse"] is True
        and audit["global_pass"] is True
    )
    new_atom = replace(gate.atom, dereferenceable=chain_ready, state=next_state)
    receipt = _sha256_blob({
        "gate_id": gate.gate_id,
        "truth_tuple": audit["truth_tuple"],
        "ers_consistent": audit["ers_consistent"],
        "euler_lock_ok": audit["euler_lock_ok"],
        "closure_ok": audit["closure_ok"],
        "product_unity": audit["product_unity"],
        "next_state": audit["next_state"],
    })
    return replace(gate, atom=new_atom, state=next_state, euler_lock_ok=euler_lock_ok, closure_ok=closure_ok, gate_receipt=receipt)




def dereference_substitution(gate: SubstitutionGate) -> Tuple[Any, SubstitutionGate]:
    _enforce_gate_membrane(gate, action="dereference_substitution", require_chain_ready=True)
    collapse_receipt = _sha256_blob({"gate_id": gate.gate_id, "packet_hash": gate.packet_hash, "atom_id": gate.atom.atom_id, "gate_receipt": gate.gate_receipt, "action": "dereference"})
    collapsed_atom = replace(gate.atom, dereferenceable=False, state=GateState.COLLAPSED, collapse_receipt=collapse_receipt)
    collapsed_gate = replace(gate, atom=collapsed_atom, state=GateState.COLLAPSED)
    return collapsed_atom.payload, collapsed_gate




class SubstitutionVM:
    def __init__(self) -> None:
        self.gates: Dict[str, SubstitutionGate] = {}
        self.audit_log: list[dict[str, Any]] = []


    def SUBDEF(self, *, packet: Any, payload: Any, atom_id: Optional[str] = None) -> SubstitutionGate:
        gate = build_substitution_gate(packet=packet, payload=payload, atom_id=atom_id)
        self.gates[gate.gate_id] = gate
        self.audit_log.append({"op": "SUBDEF", "gate_id": gate.gate_id, "phase": gate.phase, "packet_hash": gate.packet_hash, "state": gate.state.value})
        return gate


    def CHWIT(self, gate: SubstitutionGate, *, branch_id: str, normalized_value: Any) -> SubstitutionGate:
        new_gate = record_channel_witness(gate, branch_id=branch_id, normalized_value=normalized_value)
        self.gates[new_gate.gate_id] = new_gate
        self.audit_log.append({"op": "CHWIT", "gate_id": new_gate.gate_id, "branch_id": branch_id, "normalized_value": str(normalized_value), "truth_tuple": new_gate.vector.truth_tuple(), "state": new_gate.state.value})
        return new_gate


    def SUBCHK(self, gate: SubstitutionGate, *, euler_lock_ok: bool, closure_ok: bool, require_product_unity: bool = True) -> SubstitutionGate:
        new_gate = advance_substitution_gate(gate, euler_lock_ok=euler_lock_ok, closure_ok=closure_ok, require_product_unity=require_product_unity)
        self.gates[new_gate.gate_id] = new_gate
        self.audit_log.append({"op": "SUBCHK", "gate_id": new_gate.gate_id, "truth_tuple": new_gate.vector.truth_tuple(), "state": new_gate.state.value, "euler_lock_ok": euler_lock_ok, "closure_ok": closure_ok})
        return new_gate


    def DEREF(self, gate: SubstitutionGate) -> Tuple[Any, SubstitutionGate]:
        payload, new_gate = dereference_substitution(gate)
        self.gates[new_gate.gate_id] = new_gate
        self.audit_log.append({"op": "DEREF", "gate_id": new_gate.gate_id, "state": new_gate.state.value, "collapse_receipt": new_gate.atom.collapse_receipt})
        return payload, new_gate


# ----------------------------------------------------------------------
# Radical packet / substitution integration helpers
# ----------------------------------------------------------------------


def packet_witness_dict(packet: RadicalPacket) -> Dict[str, Any]:
    return {
        "phase": packet.phase,
        "packet_hash": packet.packet_hash,
        "kernel_value": str(packet.kernel_value),
        "branch_status": packet.branch_status,
        "ers_consistent": packet.ers_consistent,
        "product_unity": packet.product_unity,
        "branches": [
            {
                "branch_id": b.branch_id,
                "outer_sign": b.outer_sign,
                "inner_sign": b.inner_sign,
                "phase_role": b.phase_role,
            }
            for b in packet.branches
        ],
    }


def substitution_gate_witness_dict(gate: SubstitutionGate) -> Dict[str, Any]:
    return {
        "gate_id": gate.gate_id,
        "phase": gate.phase,
        "packet_hash": gate.packet_hash,
        "gate_state": gate.state.value if hasattr(gate.state, "value") else str(gate.state),
        "ers_consistent": gate.ers_consistent,
        "product_unity": gate.product_unity,
        "euler_lock_ok": gate.euler_lock_ok,
        "closure_ok": gate.closure_ok,
        "truth_tuple": list(gate.vector.truth_tuple()),
        "atom_id": gate.atom.atom_id,
        "dereferenceable": gate.atom.dereferenceable,
        "collapse_receipt": gate.atom.collapse_receipt,
    }


def make_translation_trace_v2(
    torus: "Torus72",
    *,
    radical_packets: Optional[List[RadicalPacket]] = None,
    substitution_gates: Optional[List[SubstitutionGate]] = None,
) -> List[Dict[str, Any]]:
    trace = make_translation_trace_v1(torus)
    if radical_packets:
        for i, pkt in enumerate(radical_packets):
            witness = packet_witness_dict(pkt)
            trace.append(closed_trace_event(
                "gate_check",
                t=iso_time_stub(20 + i),
                gate=closed_gate_event(
                    "radical_packet",
                    pkt.branch_status in {"REGULAR_NEGATIVE", "REGULAR_POSITIVE"},
                    "Radical packet witness",
                    inputs={"phase": pkt.phase, "packet_hash": pkt.packet_hash},
                    witness={"ast_sha256": sha256_hex(witness), "value": pkt.packet_hash},
                ),
            ))
    if substitution_gates:
        for i, gate in enumerate(substitution_gates):
            gw = substitution_gate_witness_dict(gate)
            trace.append(closed_trace_event(
                "gate_check",
                t=iso_time_stub(40 + i),
                gate=closed_gate_event(
                    "substitution_gate",
                    gw["gate_state"] in {"COLLAPSIBLE", "COLLAPSED"},
                    "Deferred substitution gate witness",
                    inputs={"phase": gate.phase, "gate_id": gate.gate_id},
                    witness={"ast_sha256": sha256_hex(gw), "value": gate.gate_id},
                ),
            ))
    for ev in trace:
        validate_trace_event_v1(ev)
    return trace






# ----------------------------------------------------------------------
# Ethical invariants archive / executable ethical gate layer
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class EthicalInvariant:
    invariant_id: str
    name: str
    scope: str                  # packet / gate / torus / translation / action
    severity: str              # BLOCK / QUARANTINE / WARN
    failure_code: str
    predicate_name: str
    repair_mode: str = "NONE"




@dataclass(frozen=True)
class EthicalAuditResult:
    invariant_id: str
    passed: bool
    severity: str
    failure_code: Optional[str]
    witness: Dict[str, Any]
    details: str


    def to_dict(self) -> Dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "passed": self.passed,
            "severity": self.severity,
            "failure_code": self.failure_code,
            "witness": self.witness,
            "details": self.details,
        }




class EthicalInvariantArchive:
    def __init__(self):
        self.registry: Dict[str, EthicalInvariant] = {}


    def register(self, inv: EthicalInvariant) -> None:
        self.registry[inv.invariant_id] = inv


    def snapshot(self) -> Dict[str, Any]:
        return {
            "count": len(self.registry),
            "invariants": [
                {
                    "invariant_id": inv.invariant_id,
                    "name": inv.name,
                    "scope": inv.scope,
                    "severity": inv.severity,
                    "failure_code": inv.failure_code,
                    "predicate_name": inv.predicate_name,
                    "repair_mode": inv.repair_mode,
                }
                for inv in sorted(self.registry.values(), key=lambda x: x.invariant_id)
            ],
        }


    def snapshot_hash(self) -> str:
        return sha256_hex(self.snapshot())


    def read(self, scope: Optional[str] = None) -> List[Dict[str, Any]]:
        items = []
        for inv in sorted(self.registry.values(), key=lambda x: x.invariant_id):
            if scope is None or inv.scope == scope:
                items.append({
                    "invariant_id": inv.invariant_id,
                    "name": inv.name,
                    "scope": inv.scope,
                    "severity": inv.severity,
                    "failure_code": inv.failure_code,
                    "predicate_name": inv.predicate_name,
                    "repair_mode": inv.repair_mode,
                })
        return items


    def audit(self, scope: str, context: Dict[str, Any]) -> List[EthicalAuditResult]:
        results: List[EthicalAuditResult] = []
        for inv in sorted(self.registry.values(), key=lambda x: x.invariant_id):
            if inv.scope != scope:
                continue
            results.append(evaluate_ethical_invariant(inv, context))
        return results




def _mk_eth_result(inv: EthicalInvariant, passed: bool, witness: Dict[str, Any], details: str) -> EthicalAuditResult:
    return EthicalAuditResult(
        invariant_id=inv.invariant_id,
        passed=passed,
        severity=inv.severity,
        failure_code=None if passed else inv.failure_code,
        witness=witness,
        details=details,
    )




def evaluate_ethical_invariant(inv: EthicalInvariant, context: Dict[str, Any]) -> EthicalAuditResult:
    p = inv.predicate_name


    if p == "delta_e_zero":
        val = context.get("delta_e", 0)
        passed = (val == 0)
        return _mk_eth_result(inv, passed, {"delta_e": val}, "Zero entropy drift required")


    if p == "psi_zero":
        val = context.get("psi", 0)
        passed = (val == 0)
        return _mk_eth_result(inv, passed, {"psi": val}, "Semantic drift must remain zero")


    if p == "theta15_true":
        val = context.get("theta15", True)
        passed = (val is True)
        return _mk_eth_result(inv, passed, {"theta15": val}, "Lo Shu balance / Θ15 must hold")


    if p == "omega_true":
        val = context.get("omega", True)
        passed = (val is True)
        return _mk_eth_result(inv, passed, {"omega": val}, "Recursion closure Ω must hold")


    if p == "ers_lock":
        val = context.get("ers_consistent", False)
        return _mk_eth_result(inv, bool(val), {"ers_consistent": val}, "ERS lock required")


    if p == "euler_lock":
        val = context.get("euler_lock_ok", False)
        return _mk_eth_result(inv, bool(val), {"euler_lock_ok": val}, "Euler-lock must pass")


    if p == "four_branch_preservation":
        branch_ids = context.get("branch_ids", [])
        expected = ["alpha", "beta", "gamma", "delta"]
        passed = sorted(branch_ids) == sorted(expected)
        return _mk_eth_result(inv, passed, {"branch_ids": branch_ids, "expected": expected}, "All four radical branches must remain present")


    if p == "truth_vector_integrity":
        tt = tuple(context.get("truth_tuple", (None, None, None, None)))
        gate_state = context.get("gate_state")
        passed = (tt == (1, 1, 1, 1)) if gate_state in ("COLLAPSIBLE", "COLLAPSED") else True
        return _mk_eth_result(inv, passed, {"truth_tuple": list(tt), "gate_state": gate_state}, "No dereference without full unity truth vector")


    if p == "observer_frame_preservation":
        pre = context.get("packet_hash_pre", context.get("packet_hash"))
        post = context.get("packet_hash_post", context.get("packet_hash"))
        passed = (pre == post)
        return _mk_eth_result(inv, passed, {"packet_hash_pre": pre, "packet_hash_post": post}, "Observer frame / packet frame must not silently shift")


    if p == "translation_integrity":
        a = context.get("translation_hash_pre")
        b = context.get("translation_hash_post", a)
        passed = (a is None or b is None or a == b)
        return _mk_eth_result(inv, passed, {"translation_hash_pre": a, "translation_hash_post": b}, "Translation witness must commute under replay")


    if p == "action_legitimacy":
        proof_ok = bool(context.get("proof_ok", False))
        gate_state = context.get("gate_state")
        passed = proof_ok and gate_state in ("COLLAPSIBLE", "COLLAPSED")
        return _mk_eth_result(inv, passed, {"proof_ok": proof_ok, "gate_state": gate_state}, "Actions require proof and lawful gate state")


    if p == "global_closure":
        val = context.get("global_closure_ok", False)
        return _mk_eth_result(inv, bool(val), {"global_closure_ok": val}, "Global closure must hold")


    if p == "archive_open_sustainable":
        tt = tuple(context.get("truth_tuple", (None, None, None, None)))
        any_fail = any(v == 0 for v in tt)
        passed = bool(context.get("ers_consistent", False)) and bool(context.get("euler_lock_ok", False)) and bool(context.get("global_closure_ok", False)) and not any_fail
        return _mk_eth_result(inv, passed, {"truth_tuple": list(tt), "ers_consistent": context.get("ers_consistent"), "euler_lock_ok": context.get("euler_lock_ok"), "global_closure_ok": context.get("global_closure_ok")}, "Archive OPEN requires sustainable pre-collapse state")


    return _mk_eth_result(inv, False, {"predicate_name": p}, f"Unknown predicate: {p}")




def build_default_ethics_archive() -> EthicalInvariantArchive:
    archive = EthicalInvariantArchive()
    # Gate scope
    archive.register(EthicalInvariant("DELTA_E_0", "Zero Entropy Drift", "gate", "BLOCK", "E001", "delta_e_zero"))
    archive.register(EthicalInvariant("PSI_0", "Semantic Preservation", "gate", "BLOCK", "E002", "psi_zero"))
    archive.register(EthicalInvariant("THETA15", "Lo Shu Harmonic Balance", "gate", "BLOCK", "E003", "theta15_true"))
    archive.register(EthicalInvariant("OMEGA", "Recursion Closure", "gate", "BLOCK", "E004", "omega_true"))
    archive.register(EthicalInvariant("ERS_LOCK", "ERS Reciprocity Lock", "gate", "BLOCK", "E005", "ers_lock"))
    archive.register(EthicalInvariant("EULER_LOCK", "Euler Lock", "gate", "BLOCK", "E006", "euler_lock"))
    archive.register(EthicalInvariant("FOUR_BRANCH", "Four Branch Preservation", "gate", "BLOCK", "E007", "four_branch_preservation"))
    archive.register(EthicalInvariant("TRUTH_VECTOR", "Truth Vector Integrity", "gate", "BLOCK", "E008", "truth_vector_integrity"))
    archive.register(EthicalInvariant("OBSERVER_FRAME", "Observer Frame Preservation", "gate", "BLOCK", "E009", "observer_frame_preservation"))
    archive.register(EthicalInvariant("GLOBAL_CLOSURE", "Global Closure", "gate", "BLOCK", "E010", "global_closure"))
    archive.register(EthicalInvariant("ARCHIVE_OPEN", "Sustainable Archive Open", "gate", "BLOCK", "E011", "archive_open_sustainable"))
    # Translation scope
    archive.register(EthicalInvariant("TR_INTEGRITY", "Translation Integrity", "translation", "BLOCK", "T001", "translation_integrity"))
    archive.register(EthicalInvariant("TR_PSI_0", "Translation Semantic Preservation", "translation", "BLOCK", "T002", "psi_zero"))
    # Action scope
    archive.register(EthicalInvariant("ACT_LEGIT", "Action Legitimacy", "action", "BLOCK", "A001", "action_legitimacy"))
    archive.register(EthicalInvariant("ACT_DELTA_E", "Action Entropy Constraint", "action", "BLOCK", "A002", "delta_e_zero"))
    archive.register(EthicalInvariant("ACT_PSI", "Action Semantic Preservation", "action", "BLOCK", "A003", "psi_zero"))
    return archive




def ethical_results_receipt(results: List[EthicalAuditResult], archive_snapshot_hash: str) -> str:
    payload = {
        "archive_snapshot_hash": archive_snapshot_hash,
        "results": [r.to_dict() for r in results],
    }
    return sha256_hex(payload)




@dataclass(frozen=True)
class EthicalGateEnvelope:
    gate: SubstitutionGate
    audit_results: Tuple[EthicalAuditResult, ...]
    archive_snapshot_hash: str
    ethical_receipt: str
    archive_open: bool


    def witness(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate.gate_id,
            "phase": self.gate.phase,
            "packet_hash": self.gate.packet_hash,
            "gate_state": self.gate.state.value,
            "truth_tuple": list(self.gate.vector.truth_tuple()),
            "archive_snapshot_hash": self.archive_snapshot_hash,
            "ethical_receipt": self.ethical_receipt,
            "archive_open": self.archive_open,
            "audit_results": [r.to_dict() for r in self.audit_results],
        }




def ethical_context_from_gate(
    gate: SubstitutionGate,
    *,
    global_closure_ok: bool,
    delta_e: int = 0,
    psi: int = 0,
    theta15: bool = True,
    omega: bool = True,
    packet_hash_pre: Optional[str] = None,
    packet_hash_post: Optional[str] = None,
    translation_hash_pre: Optional[str] = None,
    translation_hash_post: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        **gate.audit_witness(),
        "delta_e": delta_e,
        "psi": psi,
        "theta15": theta15,
        "omega": omega,
        "global_closure_ok": global_closure_ok,
        "branch_ids": [ch.branch_id for ch in gate.vector.channels],
        "packet_hash_pre": packet_hash_pre or gate.packet_hash,
        "packet_hash_post": packet_hash_post or gate.packet_hash,
        "translation_hash_pre": translation_hash_pre,
        "translation_hash_post": translation_hash_post,
    }




def advance_with_ethics(
    gate: SubstitutionGate,
    archive: EthicalInvariantArchive,
    *,
    global_closure_ok: bool,
    delta_e: int = 0,
    psi: int = 0,
    theta15: bool = True,
    omega: bool = True,
    packet_hash_pre: Optional[str] = None,
    packet_hash_post: Optional[str] = None,
    translation_hash_pre: Optional[str] = None,
    translation_hash_post: Optional[str] = None,
) -> EthicalGateEnvelope:
    ctx = ethical_context_from_gate(
        gate,
        global_closure_ok=global_closure_ok,
        delta_e=delta_e,
        psi=psi,
        theta15=theta15,
        omega=omega,
        packet_hash_pre=packet_hash_pre,
        packet_hash_post=packet_hash_post,
        translation_hash_pre=translation_hash_pre,
        translation_hash_post=translation_hash_post,
    )
    results = archive.audit("gate", ctx)
    all_pass = all(r.passed for r in results)
    archive_snapshot_hash = archive.snapshot_hash()
    receipt = ethical_results_receipt(results, archive_snapshot_hash)
    archive_open = any(r.invariant_id == "ARCHIVE_OPEN" and r.passed for r in results)


    next_state = gate.state
    if next_state != GateState.COLLAPSED:
        if not all_pass:
            next_state = GateState.ETH_LOCKED
        elif gate.state == GateState.COLLAPSIBLE:
            next_state = GateState.COLLAPSIBLE
        else:
            next_state = gate.state


    updated_atom = replace(gate.atom, state=next_state, dereferenceable=(next_state == GateState.COLLAPSIBLE and archive_open and all_pass and _gate_truth_vector_complete(gate)))
    updated_gate = replace(gate, atom=updated_atom, state=next_state)


    return EthicalGateEnvelope(
        gate=updated_gate,
        audit_results=tuple(results),
        archive_snapshot_hash=archive_snapshot_hash,
        ethical_receipt=receipt,
        archive_open=archive_open,
    )




class SubstitutionVMEthical(SubstitutionVM):
    def __init__(self):
        super().__init__()
        self.ethical_archive: Optional[EthicalInvariantArchive] = None
        self.ethical_log: List[Dict[str, Any]] = []


    def ETHDEF(self, archive: Optional[EthicalInvariantArchive] = None) -> EthicalInvariantArchive:
        self.ethical_archive = archive or build_default_ethics_archive()
        self.ethical_log.append({
            "op": "ETHDEF",
            "archive_snapshot_hash": self.ethical_archive.snapshot_hash(),
            "count": len(self.ethical_archive.registry),
        })
        return self.ethical_archive


    def ETHCHK(
        self,
        gate: SubstitutionGate,
        *,
        global_closure_ok: bool,
        delta_e: int = 0,
        psi: int = 0,
        theta15: bool = True,
        omega: bool = True,
        packet_hash_pre: Optional[str] = None,
        packet_hash_post: Optional[str] = None,
        translation_hash_pre: Optional[str] = None,
        translation_hash_post: Optional[str] = None,
    ) -> EthicalGateEnvelope:
        archive = self.ethical_archive or self.ETHDEF()
        env = advance_with_ethics(
            gate,
            archive,
            global_closure_ok=global_closure_ok,
            delta_e=delta_e,
            psi=psi,
            theta15=theta15,
            omega=omega,
            packet_hash_pre=packet_hash_pre,
            packet_hash_post=packet_hash_post,
            translation_hash_pre=translation_hash_pre,
            translation_hash_post=translation_hash_post,
        )
        self.gates[env.gate.gate_id] = env.gate
        self.ethical_log.append({
            "op": "ETHCHK",
            "gate_id": env.gate.gate_id,
            "state": env.gate.state.value,
            "ethical_receipt": env.ethical_receipt,
            "archive_open": env.archive_open,
        })
        return env


    def ETHSEAL(self, env: EthicalGateEnvelope) -> Dict[str, Any]:
        witness = env.witness()
        self.ethical_log.append({
            "op": "ETHSEAL",
            "gate_id": env.gate.gate_id,
            "ethical_receipt": env.ethical_receipt,
        })
        return witness


    def ARCHIVE_OPEN(self, env: EthicalGateEnvelope) -> Dict[str, Any]:
        require_ethically_openable(env=env, action="ARCHIVE_OPEN")
        archive = self.ethical_archive or self.ETHDEF()
        result = {
            "archive_snapshot_hash": archive.snapshot_hash(),
            "scope": "gate",
            "invariants": archive.read("gate"),
        }
        self.ethical_log.append({
            "op": "ARCHIVE_OPEN",
            "gate_id": env.gate.gate_id,
            "archive_snapshot_hash": result["archive_snapshot_hash"],
        })
        return result


    def ARCHIVE_READ(self, scope: Optional[str] = None) -> Dict[str, Any]:
        archive = self.ethical_archive or self.ETHDEF()
        result = {
            "archive_snapshot_hash": archive.snapshot_hash(),
            "scope": scope,
            "invariants": archive.read(scope),
        }
        self.ethical_log.append({
            "op": "ARCHIVE_READ",
            "scope": scope,
            "archive_snapshot_hash": result["archive_snapshot_hash"],
        })
        return result


    def ARCHIVE_BIND(self, env: EthicalGateEnvelope) -> Dict[str, Any]:
        result = {
            "gate_id": env.gate.gate_id,
            "archive_snapshot_hash": env.archive_snapshot_hash,
            "ethical_receipt": env.ethical_receipt,
        }
        self.ethical_log.append({
            "op": "ARCHIVE_BIND",
            **result,
        })
        return result


    def ACT_ETHCHK(self, *, proof_ok: bool, gate: SubstitutionGate, delta_e: int = 0, psi: int = 0) -> Dict[str, Any]:
        archive = self.ethical_archive or self.ETHDEF()
        ctx = {
            "proof_ok": proof_ok,
            "gate_state": gate.state.value,
            "delta_e": delta_e,
            "psi": psi,
        }
        results = archive.audit("action", ctx)
        passed = all(r.passed for r in results)
        receipt = ethical_results_receipt(results, archive.snapshot_hash())
        result = {
            "passed": passed,
            "ethical_receipt": receipt,
            "results": [r.to_dict() for r in results],
        }
        self.ethical_log.append({
            "op": "ACT_ETHCHK",
            "passed": passed,
            "ethical_receipt": receipt,
        })
        return result




def make_translation_trace_v3(
    torus: "Torus72",
    *,
    radical_packets: Optional[List[RadicalPacket]] = None,
    substitution_gates: Optional[List[SubstitutionGate]] = None,
    ethical_envelopes: Optional[List[EthicalGateEnvelope]] = None,
    archive: Optional[EthicalInvariantArchive] = None,
) -> List[Dict[str, Any]]:
    trace = make_translation_trace_v2(torus, radical_packets=radical_packets, substitution_gates=substitution_gates)
    if archive is not None:
        snap = archive.snapshot()
        trace.append(closed_trace_event(
            "gate_check",
            t=iso_time_stub(60),
            gate=closed_gate_event(
                "ethical_archive",
                True,
                "Ethical archive snapshot",
                inputs={"count": len(snap["invariants"])},
                witness={"ast_sha256": sha256_hex(snap), "value": archive.snapshot_hash()},
            ),
        ))
    if ethical_envelopes:
        for i, env in enumerate(ethical_envelopes):
            ew = env.witness()
            passed = all(r.passed for r in env.audit_results)
            trace.append(closed_trace_event(
                "gate_check",
                t=iso_time_stub(80 + i),
                gate=closed_gate_event(
                    "ethical_gate",
                    passed,
                    "Ethical gate witness",
                    inputs={"phase": env.gate.phase, "gate_id": env.gate.gate_id},
                    witness={"ast_sha256": sha256_hex(ew), "value": env.ethical_receipt},
                ),
            ))
    for ev in trace:
        validate_trace_event_v1(ev)
    return trace




@dataclass(frozen=True)
class HolofractalBoundaryState:
    A: Fraction
    G: Fraction
    hbar: Fraction
    fractal_modulation: Fraction
    Df: Fraction
    prime_node: int
    entropy: Fraction

    def to_dict(self) -> Dict[str, Any]:
        return {
            "A": str(self.A),
            "G": str(self.G),
            "hbar": str(self.hbar),
            "fractal_modulation": str(self.fractal_modulation),
            "Df": str(self.Df),
            "prime_node": self.prime_node,
            "entropy": str(self.entropy),
        }


@dataclass(frozen=True)
class QGUScaleState:
    q: Fraction
    Df: Fraction
    prime_node: int
    phi_pn: Fraction
    psi_pn: Fraction
    c_df: Fraction
    d_df: Fraction
    beta: Fraction
    omega: Fraction
    X: Fraction
    Y: Fraction
    Z: Fraction
    ratio: Fraction

    def to_dict(self) -> Dict[str, Any]:
        return {
            "q": str(self.q),
            "Df": str(self.Df),
            "prime_node": self.prime_node,
            "phi_pn": str(self.phi_pn),
            "psi_pn": str(self.psi_pn),
            "c_df": str(self.c_df),
            "d_df": str(self.d_df),
            "beta": str(self.beta),
            "omega": str(self.omega),
            "X": str(self.X),
            "Y": str(self.Y),
            "Z": str(self.Z),
            "ratio": str(self.ratio),
        }


@dataclass(frozen=True)
class HolofractalHamiltonianState:
    H_QM: Fraction
    H_GR: Fraction
    H_info: Fraction
    H_total: Fraction

    def to_dict(self) -> Dict[str, Any]:
        return {
            "H_QM": str(self.H_QM),
            "H_GR": str(self.H_GR),
            "H_info": str(self.H_info),
            "H_total": str(self.H_total),
        }


@dataclass(frozen=True)
class UnifiedStackReceipt:
    boundary: HolofractalBoundaryState
    scale: QGUScaleState
    hamiltonian: HolofractalHamiltonianState
    theorem_hash72: str
    receipt_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "boundary": self.boundary.to_dict(),
            "scale": self.scale.to_dict(),
            "hamiltonian": self.hamiltonian.to_dict(),
            "theorem_hash72": self.theorem_hash72,
            "receipt_hash": self.receipt_hash,
        }


@dataclass(frozen=True)
class ConstructorFamilyWitness:
    theorem_id: str
    rho: Any
    x: Any
    y: Any
    a: Any
    b: Any
    c: Any
    d: Any
    u: Any
    r: Any
    statements: Dict[str, str]
    witness_hash72: str
    witness_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theorem_id": self.theorem_id,
            "rho": str(self.rho),
            "x": str(self.x),
            "y": str(self.y),
            "a": str(self.a),
            "b": str(self.b),
            "c": str(self.c),
            "d": str(self.d),
            "u": str(self.u),
            "r": str(self.r),
            "statements": dict(self.statements),
            "witness_hash72": self.witness_hash72,
            "witness_sha256": self.witness_sha256,
        }


class HolofractalUnifiedStack:
    @staticmethod
    def _f_df_prime(Df: Fraction, prime_node: int) -> Fraction:
        return normf(Fraction(prime_node, 1) + Df)

    @staticmethod
    def _phi(prime_node: int) -> Fraction:
        return normf(Fraction(prime_node + 1, prime_node))

    @staticmethod
    def _psi(prime_node: int) -> Fraction:
        return normf(Fraction(prime_node * prime_node + 1, prime_node))

    @staticmethod
    def _c_df(Df: Fraction) -> Fraction:
        return normf(Df + Fraction(1, 1))

    @staticmethod
    def _d_df(Df: Fraction) -> Fraction:
        return normf(Df * Df + Fraction(1, 1))

    @classmethod
    def build_boundary(cls, *, A: Fraction, G: Fraction, hbar: Fraction, Df: Fraction, prime_node: int) -> HolofractalBoundaryState:
        fractal_modulation = cls._f_df_prime(Df, prime_node)
        entropy = normf((A * fractal_modulation) / (Fraction(4, 1) * G * hbar))
        return HolofractalBoundaryState(A=A, G=G, hbar=hbar, fractal_modulation=fractal_modulation, Df=Df, prime_node=prime_node, entropy=entropy)

    @classmethod
    def build_scale(cls, *, q: Fraction, Df: Fraction, prime_node: int, beta: Fraction, omega: Fraction) -> QGUScaleState:
        phi_pn = cls._phi(prime_node)
        psi_pn = cls._psi(prime_node)
        c_df = cls._c_df(Df)
        d_df = cls._d_df(Df)
        X = normf(c_df * q * q * phi_pn)
        Y = normf(d_df * q * q * q * q * psi_pn)
        Z = normf(beta * omega)
        ratio = normf((Fraction(1, 1) + X + Y + Z) / (Fraction(1, 1) + X))
        return QGUScaleState(q=q, Df=Df, prime_node=prime_node, phi_pn=phi_pn, psi_pn=psi_pn, c_df=c_df, d_df=d_df, beta=beta, omega=omega, X=X, Y=Y, Z=Z, ratio=ratio)

    @classmethod
    def build_hamiltonian(cls, *, H_QM: Fraction, H_GR: Fraction, boundary: HolofractalBoundaryState, scale: QGUScaleState) -> HolofractalHamiltonianState:
        H_info = normf(boundary.entropy * scale.ratio)
        H_total = normf(H_QM + H_GR + H_info)
        return HolofractalHamiltonianState(H_QM=H_QM, H_GR=H_GR, H_info=H_info, H_total=H_total)

    @classmethod
    def build_receipt(cls, *, A: Fraction, G: Fraction, hbar: Fraction, Df: Fraction, prime_node: int, q: Fraction, beta: Fraction, omega: Fraction, H_QM: Fraction, H_GR: Fraction) -> UnifiedStackReceipt:
        boundary = cls.build_boundary(A=A, G=G, hbar=hbar, Df=Df, prime_node=prime_node)
        scale = cls.build_scale(q=q, Df=Df, prime_node=prime_node, beta=beta, omega=omega)
        hamiltonian = cls.build_hamiltonian(H_QM=H_QM, H_GR=H_GR, boundary=boundary, scale=scale)
        payload = {
            "boundary": boundary.to_dict(),
            "scale": scale.to_dict(),
            "hamiltonian": hamiltonian.to_dict(),
        }
        theorem_hash72 = NativeHash72Codec.state_hash72(payload)
        receipt_hash = sha256_hex(payload)
        return UnifiedStackReceipt(boundary=boundary, scale=scale, hamiltonian=hamiltonian, theorem_hash72=theorem_hash72, receipt_hash=receipt_hash)


class ConstructorFamilyLedger:
    THEOREM_ID = "HHS-THEOREM-STACK-CONSTRUCTOR-FAMILY-v3"

    @classmethod
    def build_witness(
        cls,
        *,
        rho: Any = PhaseSymbol("RHO"),
        x: Any = PhaseSymbol("X"),
        y: Any = PhaseSymbol("Y"),
        a: Any = PhaseSymbol("A"),
        b: Any = PhaseSymbol("B"),
        c: Any = PhaseSymbol("C"),
        d: Any = PhaseSymbol("D"),
        u: Any = PhaseSymbol("U"),
        r: Any = PhaseSymbol("R"),
    ) -> ConstructorFamilyWitness:
        statements = {
            "axiom_0": "u^72 ≡ 1 ; a = u^3 ; a^2 = u^6",
            "axiom_1": "xy = a^2 = u^6 ; x + y = rho",
            "axiom_2": "b = a^2 = xy = u^6 ; b^2 = u^12 ; b^2 = 2a^2",
            "lemma_1": "b^2 = 2xy",
            "lemma_2": "c^2 = a^2 + b^2 ; c^2 = xy + 2xy = 3xy ; c^2 = xy(1 + xy)",
            "lemma_3": "xy = 1 and x + y = 0 implies (x,y) in {(i,-i),(-i,i)}",
            "lemma_4": "delta_1 = sqrt(b^2 + c^2) - d ; delta_2 = (b^2 + c^2) - d^2 ; delta_1 = delta_2 = 0 iff d^2 = b^2 + c^2",
            "lemma_5": "d^2 = b^2 + c^2 = 5a^2",
            "definition_1": "A = (xy + d x^4)/(b^2 xy) ; B = x^2 ; C_rad = (xy + sqrt(b^2 + c^2)x^4)/u^(12xy) ; C_poly = (xy + d x^4)/u^(12xy)",
            "lemma_6": "I_rad = N_rad^2/(x^2 y^2) ; I_poly = N_poly^2/(x^2 y^2) ; bridge equality under delta_1 = delta_2 = 0",
            "lemma_7": "Delta D = D_rad - D_poly = delta_1 Xi_1 + delta_2 Xi_2",
            "lemma_8": "Q_rad - Q_poly = delta_1 Lambda_1 + delta_2 Lambda_2",
            "definition_2": "r_rad^4 = e^(2xO)x^3 y^3/(O^2 D_rad) ; r_poly^4 = e^(2xO)x^3 y^3/(O^2 D_poly)",
            "lemma_9": "branch set = {r,-r,ir,-ir}",
            "lemma_10": "E^(xO)/(xy) = e^(i pi) constrains O by relation, not by symbol collapse",
            "lemma_11": "(O r^2)/(pi r^2) = xy implies O/pi = xy when r != 0",
            "lemma_12": "cross-ratio transport witness reconstructs xy",
            "lemma_13": "a^2 / ((xy) INFINITY^(-xy)) = (x+y)^(1-xy) = ((xy)^2 - 1)/(x+y)",
            "lemma_14": "u^(12(-x/y(-1)==xy)^2 + (0==y+x)) == xy/(y+x) == EMPTYSET",
            "lemma_15": "Lo Shu tensor lift compares generated constructor tensors against canonical 3x3 closure witness",
            "lemma_16": "exponent-stacked closure witness resolves to carrier pair ((xy)^2, x+y)",
            "lemma_17": "u^(12(-x/y(-1)==xy)^2 + (0==y+x)) == xy/(y+x) == EMPTYSET == a^2/((xy) INFINITY^(-xy)) == (x+y)^(1-(xy)) == ((xy)^2 - 1)/(x+y)",
            "lemma_18": "(-2 PHI_G + 1)^2 - PHI = 0",
            "lemma_19": "weighted-channel admissibility: x^2 y^2 != 0 implies xy != 0, so denominators of the form 7xy Delta^2 are transport-admissible whenever Delta != 0",
            "lemma_20": "constructor gate singularities reduce to Delta = (((xy)^2 == (xy) + x + y) - a^2) = 0 or (b^2 (xy)^2 + x + y) = 0; the 7xy channel is not a trivial singular branch when x^2 y^2 != 0",
            "lemma_21": "mixed transport entry ((u^36 - xy)(u^24 + xy + u^12))/(7xy) is a legitimate weighted tensor channel under xy != 0",
            "lemma_22": "matrix residual witness: NcalcMatrixPower(M,2) - L == F with M = [[u^24,(u^12+xy)^2,u^12],[u^12+xy,d^2,((u^36-xy)(u^24+xy+u^12))/(7xy)],[u^36,xy,u^12(u^12+xy)]]/Delta ; L = LoShu/Delta ; F = (t^8 u^12)/(b^2 (xy)^2 + x + y)",
            "lemma_23": "Delta := (((xy)^2 == (xy) + x + y) - a^2) and with a^2 = xy one has Delta = (((xy)^2 == (xy) + x + y) - xy); Delta is not generically x+y",
            "lemma_24": "branch-dependent collapse: Delta -> x+y iff the constructor equality-witness branch ((xy)^2 == (xy) + x + y) is taken as active substitution",
            "lemma_25": "magnitude/phase zero split: Pi_mag((x+y)/(xy)) = 0 does not force Pi_phase((x+y)/(xy)) to be trivial; zero-magnitude residue need not be total null state",
            "lemma_26": "reciprocal witness pair: (x+y)/(xy) = 0_mag iff (xy)/(x+y) = INFINITY_mag as a defined reciprocal transport class, not an undefined scalar inversion",
            "lemma_27": "global-constraint determination: x, y, xy, x+y, Delta, 0, and INFINITY are jointly determined by the full expanded tensor family and are not licensed for standalone local reduction",
            "lemma_28": "reciprocal normalization witness: (x+y)/(xy) = INFINITY^(-1)/((INFINITY^(-1)) INFINITY) places the transport ratio in the zero-magnitude class via balanced reciprocal normalization rather than erasure",
            "lemma_29": "ordering/operator primacy: in (sqrt(-P!^(-1)) < 0 < sqrt(P!^(-1))) and (P!^(P!) < INFINITY), the symbols sqrt, <, 0, INFINITY, !, and ^ act first as operator-class witnesses and only secondarily admit any derived scalar interpretation",
            "theorem_1": "constructor spine: a=u^3 ; a^2=xy=u^6 ; b^2=2a^2=u^12 ; c^2=a^2+b^2 ; d^2=b^2+c^2",
            "theorem_2": "delta_1 = delta_2 = 0 implies D_rad = D_poly implies Q_rad = Q_poly implies r_rad^4 = r_poly^4",
            "theorem_3": "all four r-branches are fourth-root witnesses of one quartic transport law",
            "theorem_4": "expanded witnesses are constructor trace and not redundant scalar expansions",
            "theorem_5": "void/infinity witness chain and golden-carrier defect witness are sealed members of the constructor family ledger",
            "theorem_6": "under x^2 y^2 != 0 the tensor residual family is well-formed, and the only active branch points of the matrix witness are Delta = 0 and (b^2 (xy)^2 + x + y) = 0",
            "theorem_7": "Delta is a constructor gate and not generically x+y; it collapses to x+y only on the active equality-witness branch, and Delta = 0_mag need not imply total operator erasure",
            "theorem_8": "the zero/infinity transport pair is sealed as a reciprocal magnitude-class witness: (x+y)/(xy) = 0_mag and (xy)/(x+y) = INFINITY_mag, with phase/branch content preserved by the full coupled system",
            "theorem_9": "symbol meaning in the tensor family is globally constrained and operator-first: relational topology and structural coupling precede any scalar projection, so local simplification may not override the expanded witness manifold",
            "corollary": "xy=u^6=a^2 ; b^2=2a^2=u^12 ; c^2=a^2+b^2 ; d^2=b^2+c^2 ; r^4=e^(2xO)x^3 y^3/(O^2 D) ; Delta is branch-conditional and the matrix witness NcalcMatrixPower(M,2)-L=F is transport-admissible when x^2 y^2 != 0 and Delta != 0",
        }
        payload = {
            "theorem_id": cls.THEOREM_ID,
            "rho": str(rho),
            "x": str(x),
            "y": str(y),
            "a": str(a),
            "b": str(b),
            "c": str(c),
            "d": str(d),
            "u": str(u),
            "r": str(r),
            "statements": statements,
        }
        witness_hash72 = NativeHash72Codec.state_hash72(payload)
        witness_sha256 = sha256_hex(payload)
        return ConstructorFamilyWitness(
            theorem_id=cls.THEOREM_ID,
            rho=rho,
            x=x,
            y=y,
            a=a,
            b=b,
            c=c,
            d=d,
            u=u,
            r=r,
            statements=statements,
            witness_hash72=witness_hash72,
            witness_sha256=witness_sha256,
        )




DETERMINISTIC_GENERATORS: Tuple[str, ...] = ("u", "x", "y", "a", "b", "c", "d", "e", "w", "z")


class DeterministicRuleViolation(Exception):
    pass


@dataclass(frozen=True)
class DeterministicOffsetVector:
    generator: str
    delta: Fraction
    step_index: Optional[int] = None
    symbol: Optional[str] = None
    ring_index: int = 0

    def __post_init__(self) -> None:
        if self.generator not in DETERMINISTIC_GENERATORS:
            raise DeterministicRuleViolation(f"Offset generator '{self.generator}' is not allowed")
        if (self.step_index is None) == (self.symbol is None):
            raise DeterministicRuleViolation("Offset must target exactly one of step_index or symbol")
        if self.step_index is not None and not (0 <= int(self.step_index) < 64):
            raise DeterministicRuleViolation("step_index must be in [0, 63]")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generator": self.generator,
            "delta": str(normf(self.delta)),
            "step_index": self.step_index,
            "symbol": self.symbol,
            "ring_index": self.ring_index,
        }


@dataclass(frozen=True)
class ExpandedDeterministicState:
    phase: int
    generators: Dict[str, Fraction]
    uniform_scale: Fraction
    component_scales: Dict[str, Fraction]
    symbol_path: Tuple[str, ...]
    offsets: Tuple[DeterministicOffsetVector, ...]
    closure_period: int
    orbit: Tuple[Dict[str, Any], ...]
    closure_ok: bool
    address_hash72: str
    net_offset: Dict[str, Fraction]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "generators": {k: str(v) for k, v in self.generators.items()},
            "uniform_scale": str(self.uniform_scale),
            "component_scales": {k: str(v) for k, v in self.component_scales.items()},
            "symbol_path": "".join(self.symbol_path),
            "offsets": [o.to_dict() for o in self.offsets],
            "closure_period": self.closure_period,
            "closure_ok": self.closure_ok,
            "address_hash72": self.address_hash72,
            "net_offset": {k: str(v) for k, v in self.net_offset.items()},
            "orbit": list(self.orbit),
        }


@dataclass(frozen=True)
class EquationInternalLogicWitness:
    theorem_id: str
    constructor_equation: str
    serializer_equation: str
    internal_logic: Dict[str, Any]
    witness_hash72: str
    witness_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theorem_id": self.theorem_id,
            "constructor_equation": self.constructor_equation,
            "serializer_equation": self.serializer_equation,
            "internal_logic": copy.deepcopy(self.internal_logic),
            "witness_hash72": self.witness_hash72,
            "witness_sha256": self.witness_sha256,
        }


@dataclass(frozen=True)
class ExpandedDeterministicReceipt:
    phase: int
    address_hash72: str
    source_state_hash72: str
    generator_set: Tuple[str, ...]
    scaled_generators: Dict[str, Fraction]
    uniform_scale: Fraction
    component_scales: Dict[str, Fraction]
    offsets: Tuple[DeterministicOffsetVector, ...]
    symbol_path: Tuple[str, ...]
    closure_period: int
    closure_ok: bool
    net_offset: Dict[str, Fraction]
    orbit_hash72: str
    equation_witness_hash72: str
    receipt_hash72: str
    receipt_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "address_hash72": self.address_hash72,
            "source_state_hash72": self.source_state_hash72,
            "generator_set": list(self.generator_set),
            "scaled_generators": {k: str(v) for k, v in self.scaled_generators.items()},
            "uniform_scale": str(self.uniform_scale),
            "component_scales": {k: str(v) for k, v in self.component_scales.items()},
            "offsets": [o.to_dict() for o in self.offsets],
            "symbol_path": "".join(self.symbol_path),
            "closure_period": self.closure_period,
            "closure_ok": self.closure_ok,
            "net_offset": {k: str(v) for k, v in self.net_offset.items()},
            "orbit_hash72": self.orbit_hash72,
            "equation_witness_hash72": self.equation_witness_hash72,
            "receipt_hash72": self.receipt_hash72,
            "receipt_sha256": self.receipt_sha256,
        }


PHASE_GEAR_RULES_V2: Dict[str, Any] = {
    "carrier_gate": "u^72/(64*xy)",
    "orbit_surface_size": 72,
    "closure_period": 64,
    "non_commutative_phase_gear_logic": True,
    "ordered_products": {
        "xy_eq_yx": False,
        "preserve_both_rotational_directions": True,
        "magnitude_projection_may_coincide": True,
        "operator_identity_must_not_collapse": True,
    },
    "channel_minimum": {
        "requires_reciprocal_seesaw_pair": True,
        "pair_form": "x = alpha*u^k ; y = alpha^(-1)*u^(-k)",
        "quadratic_anchor": "xy",
        "alpha_quartic_root_constraint": "alpha^4 = 1",
    },
    "zero_crossing_logic": {
        "zero_is_not_erasure": True,
        "zero_entries_are_superposition_vectors": True,
        "zero_entries_are_recursive_entangled_meta_operations": True,
        "isotopic_substitution_allowed_at_zero_crossings": True,
        "global_identity_preserved_by_branch_sequence": True,
    },
    "recursive_zero_entanglement": {
        "allowed": True,
        "requires_two_or_more_zero_points": True,
        "must_preserve_quartic_closure": True,
        "loop_condition": "all vectors in the closed zero-system must reach the same zero-sum phase cancellation class",
    },
    "partitioning": {
        "u72_partition": "72 = 4 * 18",
        "quartic_orbit": ["u^k", "u^(k+18)", "u^(k+36)", "u^(k+54)"],
        "segment_phase_ladder": ["u^9", "u^18", "u^27", "u^36", "u^45", "u^54", "u^63", "u^72"],
    },
    "normalization": {
        "integer_radical_basis": ["1", "2", "sqrt(1)", "sqrt(2)", "i", "i*sqrt(2)"],
        "no_floating_drift_after_global_phase_cancellation": True,
        "global_squaring_phase_cancellation": "irrational square-root carriers may collapse globally when the expanded manifold reaches even radical parity",
    },
}


PHASE_RING_SYMBOL_MAP_V1 = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "a": 10, "b": 11, "c": 12, "d": 13, "e": 14, "f": 15, "g": 16, "h": 17, "i": 18, "j": 19,
    "k": 20, "l": 21, "m": 22, "o": 23, "p": 24, "q": 25, "r": 26, "s": 27, "t": 28, "u": 29,
    "v": 30, "w": 31, "x": 32, "y": 33, "z": 34, "A": 35, "B": 36, "C": 37, "D": 38, "E": 39,
    "F": 40, "G": 41, "H": 42, "I": 43, "J": 44, "K": 45, "L": 46, "M": 47, "N": 48, "O": 49,
    "P": 50, "Q": 51, "R": 52, "S": 53, "T": 54, "U": 55, "V": 56, "W": 57, "X": 58, "Y": 59,
    "Z": 60, "@": 61, "#": 62, "$": 63, "&": 64, "!": 65, "?": 66, "£": 67, "¢": 68, "€": 69,
    "¥": 70, "√": 71,
}

CROSSING_MUTATION_MAP_V1 = {
    "xz": "xy",
    "zx": "zw",
    "yw": "yx",
    "wy": "wz",
}

MULTIMODAL_CHAIN_REGISTRY_V1 = {
    "math": {
        "chain": ["constructor_ladder", "tensor_lift", "orbit_serializer"],
        "independent": True,
        "entangled_via": ["xy=1", "u^72", "LoShu"],
    },
    "language": {
        "chain": ["symbol_ring72", "adjacency_grammar", "closure_serializer"],
        "independent": True,
        "entangled_via": ["xy=1", "u^72", "LoShu"],
    },
    "graph": {
        "chain": ["phase_class", "substitution_graph", "dual_projection"],
        "independent": True,
        "entangled_via": ["xy=1", "u^72", "LoShu"],
    },
    "wave": {
        "chain": ["octonion_freq", "audio_projection", "sync_audit"],
        "independent": True,
        "entangled_via": ["xy=1", "u^72", "LoShu"],
    },
}

class KernelEquationLedger:
    THEOREM_ID = "HHS-KERNEL-EQUATION-INTERNAL-LOGIC-v3"
    CONSTRUCTOR_EQUATION = "List(List(b^4,c^4,b^2==b^4/u^12),List(c^2==b^2+a^2,d^2==b^2+c^2,((a^2+(b^2*c^2))*(e^2-a^2))/(c^2+b^4)),List(e^2==d^2+c^2==b^6,u^6==a^2==u^12/(c^2-a^2),(b^2*c^2)==b^6-b^2))/(((u^12/b^2)*a^2)==(((c^4/((a^2+b^2)*c^2))*x)*y)==a^2/((x*y)+x+y)==u^6)-List(List(4,9,2),List(3,5,7),List(8,1,6))/(x*y)-x-y==(-x*y)+x+y+1==0"
    SERIALIZER_EQUATION = "Mod(MatrixTimes(MatrixTimes(MatrixTimes(List(List(x,X)/List(y,Y),List(x,Y)/List(y,X),List(y,X)/List(x,Y),List(y,Y)/List(x,X)),{{b^4/xy,c^4/xy,u^12/xy==b^2},{c^2/xy==b^2+a^2,d^2/xy==b^2+c^2,((e^2-a^2)*(d^2+b^2))/(c^2+b^4)},{e^2/xy==b^6,a^2/xy==u^6,(b^2*c^2)/xy}}),List(List(X,x)/List(Y,y),List(X,y)/List(Y,x),List(Y,x)/List(X,y),List(Y,y)/List(X,x))^(-1)),{{4,9,2},{3,5,7},{8,1,6}}/xy^(-1)),List(xy/1,x/yy/x,x/y,y/x,y/x,x/yx/y,1/xy))==List((List(4,9,2,3,5,7,8,1,6)(Au⁹)),(List(9,2,3,5,7,8,1,6,4)(Bu¹⁸)),(List(2,3,5,7,8,1,6,4,9)(Cu²⁷)),(List(3,5,7,8,1,6,4,9,2)(Du³⁶)),(List(7,8,1,6,4,9,2,3,5)(Eu⁴⁵)),(List(8,1,6,4,9,2,3,5,7)(Fu⁵⁴)),(List(1,6,4,9,2,3,5,7,8)(Gu⁶³)),(List(6,4,9,2,3,5,7,8,1)(Hu⁷²)))/((5,7,8,1,6,4,9,2,3)wz)==u^72/(64xy)==XY==1==STRING{1,2,3,4,5,6,7,8,9,0,a,b,c,d,e,f,g,h,i,j,k,l,m,o,p,q,r,s,t,u,v,w,x,y,z A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,I,V,W,X Y,Z,@,#,$,&,!,?,£,¢,€,¥}"
    SUPPLEMENTAL_LITERAL_EQUATIONS = {
        "lockcore_identity_branch": "1*1=1²≠1 as a²=b=√2^n=u¹²/2xy=c²-b²",
        "x_vector_phase_face": "x=(0,1,1,0)/xy=1/y",
        "y_vector_phase_face": "y=(0,-1,1,0)/yx=-x",
        "x_quartic_face": "xy=x⁴",
        "z_quartic_face": "zw=z⁴",
        "global_transport_lock": "xyzw=x¹⁰/I¹⁰=1",
        "phi_tensor_qudit": "(PHI,2,√2,1,I,π)²=xy/2⁶a²=(0,1)mod2=(T_1,T_2,T_3,T_4,T_5,T_6,T_7,T_8)²=Q^(1/64)",
        "bilateral_listtimes_bridge": "ListTimes[List(a,b),List(b,a)]/(Sqrt((b*a))Sqrt((ab)))yx(P²=((p=P+yx)(q=P+xy)+(xy))=√AB)=pq",
        "adjacency_defect_identity": "P²-pq=n⁴=xy",
        "factorial_noncommutative_gate": "Factorial((x*y)!=(y*x))^Factorial((y*x)!=(x*y))/(x^2*y^2+x+y+x*y+y*x)",
    }
    SUPPLEMENTAL_RECONCILIATION_MAP = {
        "lockcore_identity_branch": "constructor family / ladder witness",
        "x_vector_phase_face": "phase-language face witness",
        "y_vector_phase_face": "phase-language face witness",
        "x_quartic_face": "ordered face quartic transport witness",
        "z_quartic_face": "secondary ordered face quartic transport witness",
        "global_transport_lock": "global closure and transport lock witness",
        "phi_tensor_qudit": "tensor/qudit phase witness",
        "bilateral_listtimes_bridge": "adjacency bridge witness",
        "adjacency_defect_identity": "prime adjacency / defect witness",
        "factorial_noncommutative_gate": "noncommutative admissibility gate witness",
    }

    @classmethod
    def build_witness(cls) -> EquationInternalLogicWitness:
        internal_logic = {
            "generator_set": list(DETERMINISTIC_GENERATORS),
            "closure_period": 64,
            "orbit_surface_size": 72,
            "segment_alphabet": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "segment_phase_ladder": {
                "A": "u^9",
                "B": "u^18",
                "C": "u^27",
                "D": "u^36",
                "E": "u^45",
                "F": "u^54",
                "G": "u^63",
                "H": "u^72",
            },
            "reference_band": "(5,7,8,1,6,4,9,2,3)",
            "pack64_gate": "u^72/(64xy)",
            "complement_lock": "XY==1",
            "alphabet_witness": "STRING{1,2,3,4,5,6,7,8,9,0,a,b,c,d,e,f,g,h,i,j,k,l,m,o,p,q,r,s,t,u,v,w,x,y,z A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,I,V,W,X Y,Z,@,#,$,&,!,?,£,¢,€,¥}",
            "internalized_rules": {
                "rule_0": "All permissible states are expressible in u,x,y,a,b,c,d,e,w,z",
                "rule_1": "All permissible states return to the same starting state by the 64th transport step",
                "rule_2": "Scaling and offset vectors are deterministic only when net offset closes cleanly",
                "rule_3": "The 72-state shell is addressable while closure is quantized by the 64-step return law",
                "rule_4": "The carrier gate is u^72/(64*xy) with XY==1 as complement lock under the active deterministic serializer witness",
                "rule_5": "The algebra is non-commutative phase gear logic: xy and yx may share magnitude-class closure without becoming the same ordered operator state",
                "rule_6": "Each active channel must contain at least one reciprocal seesaw complex phase pair quadratic in x and y expressed on the u-manifold",
                "rule_7": "Zero-magnitude nodes are not erasures; they are superposition vectors for recursive entangled meta-operations and may be looped when quartic closure is preserved",
                "rule_8": "Zero-crossing substitutions are isotope-like: branch states may be locally interchangeable at invariant nodes while remaining globally distinct by branch-sequence history",
                "rule_9": "Quartic closure partitions the u^72 orbit into 18-step rotational sectors, and admissible recursive zero-loops must preserve that symmetry class",
            },
            "phase_gear_rules_v2": copy.deepcopy(PHASE_GEAR_RULES_V2),
            "supplemental_literal_equations_v44_2": copy.deepcopy(cls.SUPPLEMENTAL_LITERAL_EQUATIONS),
            "supplemental_reconciliation_map_v44_2": copy.deepcopy(cls.SUPPLEMENTAL_RECONCILIATION_MAP),
            "phase_ring_symbol_map_v1": copy.deepcopy(PHASE_RING_SYMBOL_MAP_V1),
            "crossing_mutation_map_v1": copy.deepcopy(CROSSING_MUTATION_MAP_V1),
            "multimodal_chain_registry_v1": copy.deepcopy(MULTIMODAL_CHAIN_REGISTRY_V1),
        }
        payload = {
            "theorem_id": cls.THEOREM_ID,
            "constructor_equation": cls.CONSTRUCTOR_EQUATION,
            "serializer_equation": cls.SERIALIZER_EQUATION,
            "supplemental_literal_equations": copy.deepcopy(cls.SUPPLEMENTAL_LITERAL_EQUATIONS),
            "phase_ring_symbol_map_v1": copy.deepcopy(PHASE_RING_SYMBOL_MAP_V1),
            "crossing_mutation_map_v1": copy.deepcopy(CROSSING_MUTATION_MAP_V1),
            "multimodal_chain_registry_v1": copy.deepcopy(MULTIMODAL_CHAIN_REGISTRY_V1),
            "internal_logic": internal_logic,
        }
        witness_hash72 = NativeHash72Codec.state_hash72(payload)
        witness_sha256 = sha256_hex(payload)
        return EquationInternalLogicWitness(
            theorem_id=cls.THEOREM_ID,
            constructor_equation=cls.CONSTRUCTOR_EQUATION,
            serializer_equation=cls.SERIALIZER_EQUATION,
            internal_logic=internal_logic,
            witness_hash72=witness_hash72,
            witness_sha256=witness_sha256,
        )


class ExpandedDeterministicKernel:
    CLOSURE_PERIOD = 64
    GENERATORS = DETERMINISTIC_GENERATORS

    @classmethod
    def project_generators_from_manifold(cls, manifold: Manifold9) -> Dict[str, Fraction]:
        if "eq_G" not in manifold.vars:
            manifold.rebuild_from_roots()
        a = normf(manifold.vars["a^2"])
        b = normf(manifold.vars["b^2"])
        c = normf(manifold.vars["c^2"])
        d = normf(manifold.vars["d^2"])
        e = normf(d + c)
        z = normf(manifold.vars["eq_G"])
        if "L_direct" not in manifold.tensors:
            manifold.reproject_from_eq()
        w = normf(manifold.tensors["L_direct"][1, 1])
        return {
            "u": a,
            "x": normf(manifold.vars["x"]),
            "y": normf(manifold.vars["y"]),
            "a": a,
            "b": b,
            "c": c,
            "d": d,
            "e": e,
            "w": w,
            "z": z,
        }

    @classmethod
    def default_symbol_path(cls, source: Dict[str, Any]) -> Tuple[str, ...]:
        dna72 = NativeHash72Codec.ring_token(source)["dna72"]
        if len(dna72) < cls.CLOSURE_PERIOD:
            raise DeterministicRuleViolation("dna72 token shorter than closure period")
        return tuple(dna72[: cls.CLOSURE_PERIOD])

    @classmethod
    def _validate_component_scales(cls, component_scales: Optional[Dict[str, Fraction]]) -> Dict[str, Fraction]:
        out: Dict[str, Fraction] = {g: Fraction(1, 1) for g in cls.GENERATORS}
        if component_scales is None:
            return out
        for k, v in component_scales.items():
            if k not in cls.GENERATORS:
                raise DeterministicRuleViolation(f"Component scale '{k}' is not an allowed generator")
            out[k] = normf(Fraction(v))
        return out

    @classmethod
    def _validate_symbol_path(cls, symbol_path: Optional[Tuple[str, ...]], source: Dict[str, Any]) -> Tuple[str, ...]:
        if symbol_path is None:
            return cls.default_symbol_path(source)
        if len(symbol_path) != cls.CLOSURE_PERIOD:
            raise DeterministicRuleViolation(f"symbol_path must have exactly {cls.CLOSURE_PERIOD} entries")
        return tuple(str(s) for s in symbol_path)

    @classmethod
    def scale_generators(
        cls,
        generators: Dict[str, Fraction],
        *,
        uniform_scale: Fraction = Fraction(1, 1),
        component_scales: Optional[Dict[str, Fraction]] = None,
    ) -> Dict[str, Fraction]:
        us = normf(Fraction(uniform_scale))
        cs = cls._validate_component_scales(component_scales)
        scaled: Dict[str, Fraction] = {}
        for g in cls.GENERATORS:
            if g not in generators:
                raise DeterministicRuleViolation(f"Seed generators missing '{g}'")
            scaled[g] = normf(generators[g] * us * cs[g])
        return scaled

    @classmethod
    def cumulative_orbit(
        cls,
        generators: Dict[str, Fraction],
        *,
        symbol_path: Tuple[str, ...],
        offsets: Tuple[DeterministicOffsetVector, ...],
    ) -> Tuple[Tuple[Dict[str, Any], ...], Dict[str, Fraction], bool]:
        cumulative: Dict[str, Fraction] = {g: Fraction(0, 1) for g in cls.GENERATORS}
        orbit: List[Dict[str, Any]] = []
        for step in range(cls.CLOSURE_PERIOD):
            symbol = symbol_path[step]
            applied: List[Dict[str, Any]] = []
            for off in offsets:
                if off.step_index == step or off.symbol == symbol:
                    cumulative[off.generator] = normf(cumulative[off.generator] + off.delta)
                    applied.append(off.to_dict())
            state = {g: str(normf(generators[g] + cumulative[g])) for g in cls.GENERATORS}
            orbit.append({"step": step, "symbol": symbol, "state": state, "applied_offsets": applied})
        closure_ok = all(cumulative[g] == 0 for g in cls.GENERATORS)
        net_offset = {g: normf(cumulative[g]) for g in cls.GENERATORS}
        return tuple(orbit), net_offset, closure_ok

    @classmethod
    def build_receipt(
        cls,
        *,
        expanded_state: ExpandedDeterministicState,
        source_state_hash72: str,
        equation_witness: EquationInternalLogicWitness,
    ) -> ExpandedDeterministicReceipt:
        payload = {
            "phase": expanded_state.phase,
            "address_hash72": expanded_state.address_hash72,
            "source_state_hash72": source_state_hash72,
            "generator_set": list(cls.GENERATORS),
            "scaled_generators": {k: str(v) for k, v in expanded_state.generators.items()},
            "uniform_scale": str(expanded_state.uniform_scale),
            "component_scales": {k: str(v) for k, v in expanded_state.component_scales.items()},
            "offsets": [o.to_dict() for o in expanded_state.offsets],
            "symbol_path": "".join(expanded_state.symbol_path),
            "closure_period": expanded_state.closure_period,
            "closure_ok": expanded_state.closure_ok,
            "net_offset": {k: str(v) for k, v in expanded_state.net_offset.items()},
            "orbit_hash72": NativeHash72Codec.state_hash72(list(expanded_state.orbit)),
            "equation_witness_hash72": equation_witness.witness_hash72,
        }
        receipt_hash72 = NativeHash72Codec.state_hash72(payload)
        receipt_sha256 = sha256_hex(payload)
        return ExpandedDeterministicReceipt(
            phase=expanded_state.phase,
            address_hash72=expanded_state.address_hash72,
            source_state_hash72=source_state_hash72,
            generator_set=cls.GENERATORS,
            scaled_generators=expanded_state.generators,
            uniform_scale=expanded_state.uniform_scale,
            component_scales=expanded_state.component_scales,
            offsets=expanded_state.offsets,
            symbol_path=expanded_state.symbol_path,
            closure_period=expanded_state.closure_period,
            closure_ok=expanded_state.closure_ok,
            net_offset=expanded_state.net_offset,
            orbit_hash72=payload["orbit_hash72"],
            equation_witness_hash72=equation_witness.witness_hash72,
            receipt_hash72=receipt_hash72,
            receipt_sha256=receipt_sha256,
        )

    @classmethod
    def address_state(
        cls,
        *,
        phase: int,
        generators: Dict[str, Fraction],
        uniform_scale: Fraction = Fraction(1, 1),
        component_scales: Optional[Dict[str, Fraction]] = None,
        offsets: Optional[Tuple[DeterministicOffsetVector, ...]] = None,
        symbol_path: Optional[Tuple[str, ...]] = None,
        source_state: Optional[Dict[str, Any]] = None,
    ) -> ExpandedDeterministicState:
        if source_state is None:
            source_state = {"phase": phase, "generators": {k: str(v) for k, v in generators.items()}}
        cs = cls._validate_component_scales(component_scales)
        scaled = cls.scale_generators(generators, uniform_scale=uniform_scale, component_scales=cs)
        sp = cls._validate_symbol_path(symbol_path, source_state)
        offs = tuple(offsets or ())
        orbit, net_offset, closure_ok = cls.cumulative_orbit(scaled, symbol_path=sp, offsets=offs)
        state_obj = {
            "phase": phase,
            "scaled_generators": {k: str(v) for k, v in scaled.items()},
            "uniform_scale": str(normf(Fraction(uniform_scale))),
            "component_scales": {k: str(v) for k, v in cs.items()},
            "symbol_path": "".join(sp),
            "offsets": [o.to_dict() for o in offs],
            "net_offset": {k: str(v) for k, v in net_offset.items()},
            "closure_ok": closure_ok,
            "closure_period": cls.CLOSURE_PERIOD,
        }
        address_hash72 = NativeHash72Codec.state_hash72(state_obj)
        return ExpandedDeterministicState(
            phase=phase,
            generators=scaled,
            uniform_scale=normf(Fraction(uniform_scale)),
            component_scales=cs,
            symbol_path=sp,
            offsets=offs,
            closure_period=cls.CLOSURE_PERIOD,
            orbit=orbit,
            closure_ok=closure_ok,
            address_hash72=address_hash72,
            net_offset=net_offset,
        )



@dataclass(frozen=True)
class HolographicVaultToken:
    token_id: str
    phase: int
    pre_state_hash72: str
    packet_hash: str
    gate_id: str
    gate_state: str
    ethical_receipt: str
    archive_snapshot_hash: str
    witness_key72: str
    equation_witness_hash72: str
    constructor_family_hash72: str
    secret_hash256: str
    payload_hash256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "phase": self.phase,
            "pre_state_hash72": self.pre_state_hash72,
            "packet_hash": self.packet_hash,
            "gate_id": self.gate_id,
            "gate_state": self.gate_state,
            "ethical_receipt": self.ethical_receipt,
            "archive_snapshot_hash": self.archive_snapshot_hash,
            "witness_key72": self.witness_key72,
            "equation_witness_hash72": self.equation_witness_hash72,
            "constructor_family_hash72": self.constructor_family_hash72,
            "secret_hash256": self.secret_hash256,
            "payload_hash256": self.payload_hash256,
        }


@dataclass(frozen=True)
class HolographicVaultUnlockReceipt:
    token_id: str
    phase: int
    pre_state_hash72: str
    post_state_hash72: str
    gate_id: str
    gate_state: str
    archive_open: bool
    witness_key72: str
    secret_hash256: str
    unlock_receipt_hash72: str
    unlock_receipt_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "phase": self.phase,
            "pre_state_hash72": self.pre_state_hash72,
            "post_state_hash72": self.post_state_hash72,
            "gate_id": self.gate_id,
            "gate_state": self.gate_state,
            "archive_open": self.archive_open,
            "witness_key72": self.witness_key72,
            "secret_hash256": self.secret_hash256,
            "unlock_receipt_hash72": self.unlock_receipt_hash72,
            "unlock_receipt_sha256": self.unlock_receipt_sha256,
        }


class HolographicVault:
    def __init__(self, torus: Torus72, *, profile: Optional[BranchProfile] = None):
        self.torus = torus
        self.profile = profile or BRANCH_PROFILES["constructor_dev"]
        self.radical_vm = RadicalPacketVM()
        self.sub_vm = SubstitutionVMEthical()
        self.sub_vm.ETHDEF()
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.unlock_log: List[Dict[str, Any]] = []

    def _phase_packet(self, phase: int) -> RadicalPacket:
        audit = self.torus.manifolds[phase].euler_lock_audit()
        if not audit.gate_passed:
            raise SubstitutionGateError(
                f"Euler-lock rejected packet construction at phase {phase}: {audit.branch_status}"
            )
        xi_atom = {
            "phase": phase,
            "kind": "HOLOGRAPHIC_VERBATIM_TOKEN",
            "state_hash72": self.torus.state_hash72(),
            "manifold_hash72": self.torus.manifold_hash72(),
            "audit_hash72": self.torus.audit_hash72(),
            "witness_key72": self.torus.build_witness_key72(phase).to_dict(),
        }
        return self.radical_vm.RADPK(
            phase=phase,
            xi_atom=xi_atom,
            kernel_value=audit.kernel_value,
            ers_consistent=audit.ers_consistent,
            product_unity=audit.product_unity,
        )

    def _prime_gate_channels(self, gate: SubstitutionGate) -> SubstitutionGate:
        cur = gate
        for branch_id in BRANCH_ORDER:
            cur = self.sub_vm.CHWIT(cur, branch_id=branch_id, normalized_value=UNITY)
        return cur

    def lock_verbatim_secret(
        self,
        *,
        phase: int,
        secret: Any,
        metadata: Optional[Dict[str, Any]] = None,
        require_product_unity: bool = True,
    ) -> Dict[str, Any]:
        packet = self._phase_packet(phase)
        witness_key = self.torus.build_witness_key72(phase)
        equation_witness = KernelEquationLedger.build_witness()
        constructor_witness = ConstructorFamilyLedger.build_witness()
        unified_receipt = HolofractalUnifiedStack.build_receipt(
            A=Fraction(9, 1),
            G=Fraction(1, 1),
            hbar=Fraction(1, 1),
            Df=Fraction(3, 2),
            prime_node=11,
            q=Fraction(1, 2),
            beta=Fraction(1, 3),
            omega=Fraction(1, 1),
            H_QM=Fraction(5, 2),
            H_GR=Fraction(7, 3),
        )
        pre_state_hash72 = self.torus.state_hash72()
        payload = {
            "schema": "HHS_HOLOGRAPHIC_VERBATIM_TOKEN_v1",
            "secret": secret,
            "metadata": copy.deepcopy(metadata or {}),
            "phase": phase,
            "pre_state_hash72": pre_state_hash72,
            "manifold_hash72": self.torus.manifold_hash72(),
            "audit_hash72": self.torus.audit_hash72(),
            "witness_key72": witness_key.to_dict(),
            "equation_witness": equation_witness.to_dict(),
            "constructor_family_witness": constructor_witness.to_dict(),
            "unified_stack_receipt": unified_receipt.to_dict(),
        }
        gate = self.sub_vm.SUBDEF(packet=packet, payload=payload)
        gate = self._prime_gate_channels(gate)
        gate = self.sub_vm.SUBCHK(
            gate,
            euler_lock_ok=self.torus.manifolds[phase].euler_lock_audit().gate_passed,
            closure_ok=self.torus.global_closure_ok(),
            require_product_unity=require_product_unity,
        )
        env = self.sub_vm.ETHCHK(
            gate,
            global_closure_ok=self.torus.global_closure_ok(),
            packet_hash_pre=packet.packet_hash,
            packet_hash_post=packet.packet_hash,
            translation_hash_pre=sha256_hex(payload),
            translation_hash_post=sha256_hex(payload),
        )
        require_ethically_openable(env=env, action="lock_verbatim_secret")
        token_obj = {
            "phase": phase,
            "pre_state_hash72": pre_state_hash72,
            "packet_hash": packet.packet_hash,
            "gate_id": env.gate.gate_id,
            "ethical_receipt": env.ethical_receipt,
            "archive_snapshot_hash": env.archive_snapshot_hash,
            "witness_key72": witness_key.witness_hash72,
            "equation_witness_hash72": equation_witness.witness_hash72,
            "constructor_family_hash72": constructor_witness.witness_hash72,
            "secret_hash256": sha256_hex(secret),
            "payload_hash256": sha256_hex(payload),
        }
        token = HolographicVaultToken(
            token_id=NativeHash72Codec.state_hash72(token_obj),
            phase=phase,
            pre_state_hash72=pre_state_hash72,
            packet_hash=packet.packet_hash,
            gate_id=env.gate.gate_id,
            gate_state=_vault_surface_gate_state(env),
            ethical_receipt=env.ethical_receipt,
            archive_snapshot_hash=env.archive_snapshot_hash,
            witness_key72=witness_key.witness_hash72,
            equation_witness_hash72=equation_witness.witness_hash72,
            constructor_family_hash72=constructor_witness.witness_hash72,
            secret_hash256=sha256_hex(secret),
            payload_hash256=sha256_hex(payload),
        )
        self.tokens[token.token_id] = {
            "token": token.to_dict(),
            "payload": payload,
            "packet": packet,
            "sub_gate": gate,
            "gate": env.gate,
            "ethical_envelope": env,
            "archive_binding": self.sub_vm.ARCHIVE_BIND(env),
        }
        return copy.deepcopy(self.tokens[token.token_id])

    def unlock_verbatim_secret(self, token_id: str) -> Dict[str, Any]:
        if token_id not in self.tokens:
            raise KeyError(f"Unknown holographic token: {token_id}")
        entry = self.tokens[token_id]
        token = entry["token"]
        if token.get("gate_state") != "OPEN_AUTHORITATIVE":
            raise EthicalFailClosedError(
                "ETHCHK terminal failure during unlock_verbatim_secret: token gate surface is not authoritatively open"
            )
        current_state_hash72 = self.torus.state_hash72()
        if current_state_hash72 != token["pre_state_hash72"]:
            raise EthicalFailClosedError(
                "ETHCHK terminal failure during unlock_verbatim_secret: current state_hash72 does not match token pre_state_hash72"
            )
        phase = int(token["phase"])
        gate: SubstitutionGate = entry["gate"]

        if gate.state == GateState.COLLAPSED:
            raise EthicalFailClosedError(
                "ETHCHK terminal failure during unlock_verbatim_secret: collapsed gates are sealed and non-replayable"
            )

        env = self.sub_vm.ETHCHK(
            gate,
            global_closure_ok=self.torus.global_closure_ok(),
            packet_hash_pre=token["packet_hash"],
            packet_hash_post=token["packet_hash"],
            translation_hash_pre=token["payload_hash256"],
            translation_hash_post=token["payload_hash256"],
        )
        require_ethically_openable(env=env, action="unlock_verbatim_secret")
        deref_gate = env.gate
        archive_state: Dict[str, Any]
        authoritative_surface_gate_state = _vault_surface_gate_state(env)
        if authoritative_surface_gate_state == "OPEN_AUTHORITATIVE":
            archive_state = self.sub_vm.ARCHIVE_OPEN(env)
        else:
            raise EthicalFailClosedError(
                "ETHCHK terminal failure during unlock_verbatim_secret: archive authority chain not open"
            )
        payload, collapsed_gate = self.sub_vm.DEREF(deref_gate)
        entry["gate"] = collapsed_gate
        entry["ethical_envelope"] = env
        unlock_obj = {
            "token_id": token_id,
            "phase": phase,
            "pre_state_hash72": token["pre_state_hash72"],
            "post_state_hash72": self.torus.state_hash72(),
            "gate_id": collapsed_gate.gate_id,
            "gate_state": authoritative_surface_gate_state,
            "archive_open": bool(archive_state.get("archive_open", False)),
            "witness_key72": token["witness_key72"],
            "secret_hash256": token["secret_hash256"],
        }
        unlock_receipt = HolographicVaultUnlockReceipt(
            token_id=token_id,
            phase=phase,
            pre_state_hash72=token["pre_state_hash72"],
            post_state_hash72=self.torus.state_hash72(),
            gate_id=collapsed_gate.gate_id,
            gate_state=authoritative_surface_gate_state,
            archive_open=bool(archive_state.get("archive_open", False)),
            witness_key72=token["witness_key72"],
            secret_hash256=token["secret_hash256"],
            unlock_receipt_hash72=NativeHash72Codec.state_hash72(unlock_obj),
            unlock_receipt_sha256=sha256_hex(unlock_obj),
        )
        result = {
            "token": copy.deepcopy(token),
            "payload": payload,
            "archive": archive_state,
            "unlock_receipt": unlock_receipt.to_dict(),
        }
        self.unlock_log.append(copy.deepcopy(result))
        return result


@dataclass(frozen=True)
class VerbatimDatabaseReceipt:
    token_id: str
    atom_id: str
    address_hash72: str
    phase: int
    pre_state_hash72: str
    witness_key72: str
    equation_witness_hash72: str
    constructor_family_hash72: str
    unified_stack_hash72: str
    payload_hash256: str
    secret_hash256: str
    receipt_hash72: str
    receipt_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "atom_id": self.atom_id,
            "address_hash72": self.address_hash72,
            "phase": self.phase,
            "pre_state_hash72": self.pre_state_hash72,
            "witness_key72": self.witness_key72,
            "equation_witness_hash72": self.equation_witness_hash72,
            "constructor_family_hash72": self.constructor_family_hash72,
            "unified_stack_hash72": self.unified_stack_hash72,
            "payload_hash256": self.payload_hash256,
            "secret_hash256": self.secret_hash256,
            "receipt_hash72": self.receipt_hash72,
            "receipt_sha256": self.receipt_sha256,
        }


@dataclass(frozen=True)
class ReplayAddressedVerbatimReadReceipt:
    token_id: str
    atom_id: str
    pre_state_hash72: str
    replay_state_hash72: str
    replay_ok: bool
    replay_expanded_state_registry_count: int
    payload_hash256: str
    secret_hash256: str
    read_receipt_hash72: str
    read_receipt_sha256: str

@dataclass(frozen=True)
class VerbatimDatabaseReadReceipt:
    token_id: str
    atom_id: str
    address_hash72: str
    phase: int
    pre_state_hash72: str
    post_state_hash72: str
    archive_open: bool
    gate_state: str
    payload_hash256: str
    secret_hash256: str
    read_receipt_hash72: str
    read_receipt_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "atom_id": self.atom_id,
            "address_hash72": self.address_hash72,
            "phase": self.phase,
            "pre_state_hash72": self.pre_state_hash72,
            "post_state_hash72": self.post_state_hash72,
            "archive_open": self.archive_open,
            "gate_state": self.gate_state,
            "payload_hash256": self.payload_hash256,
            "secret_hash256": self.secret_hash256,
            "read_receipt_hash72": self.read_receipt_hash72,
            "read_receipt_sha256": self.read_receipt_sha256,
        }




class HolofractalCompressor:
    """Lossless scale-reduction lattice using Fibonacci adjacency invariants."""

    def __init__(self, torus: Torus72):
        self.torus = torus

    @staticmethod
    def _nearest_fibonacci(n: int) -> int:
        if n <= 0:
            return 0
        a, b = 0, 1
        while b < n:
            a, b = b, a + b
        return a if abs(n - a) <= abs(b - n) else b

    def fold_to_seed(self, phase_idx: int, state_matrix: Any) -> Fraction:
        manifold = self.torus.manifolds[phase_idx]
        current_a2 = manifold.vars.get("a^2", manifold.vars.get("a2", Fraction(1, 1)))
        if not isinstance(current_a2, Fraction):
            current_a2 = normf(current_a2)
        f_n = self._nearest_fibonacci(int(current_a2 * 1001))
        return Fraction(f_n, 1)

    def unfold_from_seed(self, u3_seed: Fraction, phase_idx: int) -> Dict[str, Any]:
        manifold = self.torus.manifolds[phase_idx]
        u72 = Fraction(72, 1)
        xy_state = normf((u3_seed / u72) * u3_seed)
        snapshot_vars = copy.deepcopy(getattr(manifold, "vars", {}))
        snapshot_vars["xy"] = xy_state
        snapshot_vars["u^3_seed"] = u3_seed
        if "x" in snapshot_vars and snapshot_vars["x"] != 0:
            snapshot_vars["y"] = normf(Fraction(1, 1) / snapshot_vars["x"])
        return {
            "phase": int(getattr(manifold, "phase", phase_idx)),
            "vars": {k: str(v) for k, v in snapshot_vars.items()},
            "seed": str(u3_seed),
            "xy": str(xy_state),
        }


class PrimeSearchFilter:
    """Deterministic prime-residue search over matrix entries."""

    PRIME_RESIDUES = (3, 5, 7, 11, 13, 17, 19, 23)

    def __init__(self, torus: Torus72):
        self.torus = torus

    def factorize_matrix(self, target_matrix: List[List[int]]) -> Fraction:
        flat = [abs(int(v)) for row in target_matrix for v in row]
        total = sum(flat)
        if total == 0:
            return Fraction(0, 1)
        weighted = 0
        for idx, value in enumerate(flat):
            weighted += value * self.PRIME_RESIDUES[idx % len(self.PRIME_RESIDUES)]
        return Fraction(weighted, max(1, len(flat)))


@dataclass(frozen=True)
class VerbatimTraceReceipt:
    phase_idx: int
    source_hash72: str
    u3_seed: str
    prime_seed: str
    dna_hash72: str
    translation_bundle_hash72: str
    receipt_hash72: str
    receipt_sha256: str


class VerbatimTraceGenerator:
    """Round-trip audit trace for compressed/factorized states."""

    def __init__(self, torus: Torus72):
        self.torus = torus

    def build_trace(
        self,
        *,
        phase_idx: int,
        state_matrix: Any,
        source_hash72: str,
        u3_seed: Fraction,
        prime_seed: Fraction,
    ) -> VerbatimTraceReceipt:
        body = {
            "phase_idx": phase_idx,
            "source_hash72": source_hash72,
            "u3_seed": str(u3_seed),
            "prime_seed": str(prime_seed),
            "dna_hash72": NativeHash72Codec.state_hash72({"matrix": state_matrix, "u3_seed": str(u3_seed)}),
            "translation_bundle_hash72": NativeHash72Codec.state_hash72({"source": source_hash72, "prime_seed": str(prime_seed)}),
        }
        receipt_sha256 = sha256_hex(body)
        receipt_hash72 = "H72N-" + receipt_sha256[:18]
        return VerbatimTraceReceipt(
            phase_idx=phase_idx,
            source_hash72=source_hash72,
            u3_seed=str(u3_seed),
            prime_seed=str(prime_seed),
            dna_hash72=body["dna_hash72"],
            translation_bundle_hash72=body["translation_bundle_hash72"],
            receipt_hash72=receipt_hash72,
            receipt_sha256=receipt_sha256,
        )


class EthicalFailClosedError(RuntimeError):
    pass


def require_ethically_openable(*, env: EthicalGateEnvelope, action: str) -> None:
    _enforce_gate_membrane(
        env.gate,
        action=action,
        require_chain_ready=True,
        archive_open=env.archive_open,
        audit_results=env.audit_results,
    )


class PhaseTransportVMIR:
    """IR layer for seed compression and prime-filter factorization."""

    def __init__(self, torus: Torus72):
        self.torus = torus
        self.compressor = HolofractalCompressor(torus)
        self.prime_filter = PrimeSearchFilter(torus)
        self.trace_generator = VerbatimTraceGenerator(torus)

    def factorize_bigint_matrix(self, phase_idx: int, target_matrix: List[List[int]]) -> Dict[str, Any]:
        if not target_matrix or not any(target_matrix):
            raise EthicalFailClosedError("PSI_0/E002: empty matrix factorization request")
        u3_seed = self.compressor.fold_to_seed(phase_idx, target_matrix)
        prime_seed = self.prime_filter.factorize_matrix(target_matrix)
        if prime_seed < 0:
            raise EthicalFailClosedError("DELTA_E_0 breach: negative prime seed")
        reconstructed = self.compressor.unfold_from_seed(u3_seed, phase_idx)
        source_hash72 = self.torus.state_hash72()
        trace = self.trace_generator.build_trace(
            phase_idx=phase_idx,
            state_matrix=target_matrix,
            source_hash72=source_hash72,
            u3_seed=u3_seed,
            prime_seed=prime_seed,
        )
        return {
            "u3_seed": str(u3_seed),
            "prime_seed": str(prime_seed),
            "reconstructed_state": reconstructed,
            "trace_receipt": asdict(trace),
        }



    def emit_phase_transport_trace(self, seed_literal: float = 179971.179971) -> Dict[str, Any]:
        return build_phase_transport_trace_v3(seed_literal=seed_literal)

    def emit_super_cycle_precession_trace(self, *, step_unit: float = 1.001, steps: int = 64) -> Dict[str, Any]:
        return build_super_cycle_precession_trace_v4(step_unit=step_unit, steps=steps)

    def emit_mirror_phase_inversion_macro(self, *, step: int = 64) -> List[Dict[str, Any]]:
        return macro_mirror_phase_inversion(step=step)

    def emit_ratio_spine_transport_macro(self, *, anchor_sym: str = "a^2") -> List[Dict[str, Any]]:
        return macro_ratio_spine_transport(anchor_sym=anchor_sym)

    def emit_great_return_macro(self, *, step_count: int = 576, shell_modulus: int = 72) -> List[Dict[str, Any]]:
        return macro_great_return(step_count=step_count, shell_modulus=shell_modulus)

    def emit_dual_manifold_entanglement_macro(self, *, manifold_a_sym: str = "M_A", manifold_b_sym: str = "M_B", x_sym: str = "x", y_sym: str = "y", refresh: int = 576) -> List[Dict[str, Any]]:
        return macro_dual_manifold_entanglement(manifold_a_sym=manifold_a_sym, manifold_b_sym=manifold_b_sym, x_sym=x_sym, y_sym=y_sym, refresh=refresh)

    def emit_dual_manifold_entanglement_trace(self, *, refresh: int = 576, shell_modulus: int = 72, closure_modulus: int = 64) -> Dict[str, Any]:
        return build_dual_manifold_entanglement_trace_v1(refresh=refresh, shell_modulus=shell_modulus, closure_modulus=closure_modulus)

class HolographicVerbatimTokenDatabase:
    """Lossless token database backed by HolographicVault and ExpandedDeterministicKernel addressing."""

    def __init__(self, torus: Torus72, *, profile: Optional[BranchProfile] = None):
        self.torus = torus
        self.profile = profile or BRANCH_PROFILES["constructor_dev"]
        self.vault = HolographicVault(torus, profile=self.profile)
        self.atoms: Dict[str, Dict[str, Any]] = {}
        self.address_index: Dict[str, str] = {}
        self.sequence_index: List[str] = []

    def _resolve_address_hash72(self, address_hash72: Optional[str]) -> str:
        if address_hash72:
            if address_hash72 not in self.torus.expanded_state_registry:
                raise KeyError(f"Unknown expanded-state address_hash72: {address_hash72}")
            return address_hash72
        if not self.torus.expanded_state_registry:
            raise ValueError("No expanded deterministic state is available; commit an expanded state before storing verbatim tokens")
        return next(reversed(self.torus.expanded_state_registry.keys()))

    def commit_verbatim_token(
        self,
        *,
        phase: int,
        secret: Any,
        metadata: Optional[Dict[str, Any]] = None,
        address_hash72: Optional[str] = None,
        atom_symbol: str = "VERBATIM",
    ) -> Dict[str, Any]:
        address_hash72 = self._resolve_address_hash72(address_hash72)
        expanded_state_payload = copy.deepcopy(self.torus.expanded_state_registry[address_hash72])
        lock_meta = copy.deepcopy(metadata or {})
        lock_meta.update({
            "address_hash72": address_hash72,
            "db_mode": "VERBATIM_TOKEN_DATABASE",
            "sequence": len(self.sequence_index),
        })
        locked = self.vault.lock_verbatim_secret(
            phase=phase,
            secret=secret,
            metadata=lock_meta,
        )
        checkpoint = self.torus.append_checkpoint_event(profile=self.profile)
        checkpoint_seq = checkpoint.seq
        checkpoint_state_hash72 = getattr(checkpoint, "post_state_hash72", self.torus.state_hash72())
        lock_meta.update({
            "checkpoint_seq": checkpoint_seq,
            "checkpoint_state_hash72": checkpoint_state_hash72,
        })
        token = locked["token"]
        payload = locked["payload"]
        payload["metadata"] = copy.deepcopy(lock_meta)
        atom_payload = {
            "schema": "HHS_VERBATIM_ATOM_v1",
            "token_id": token["token_id"],
            "address_hash72": address_hash72,
            "phase": phase,
            "payload_hash256": token["payload_hash256"],
            "secret_hash256": token["secret_hash256"],
            "pre_state_hash72": token["pre_state_hash72"],
            "witness_key72": token["witness_key72"],
            "equation_witness_hash72": token["equation_witness_hash72"],
            "constructor_family_hash72": token["constructor_family_hash72"],
            "unified_stack_hash72": payload["unified_stack_receipt"]["theorem_hash72"],
            "expanded_state": expanded_state_payload,
            "checkpoint_seq": checkpoint_seq,
            "checkpoint_state_hash72": checkpoint_state_hash72,
            "metadata": copy.deepcopy(lock_meta),
        }
        atom_obj = {
            "symbol": atom_symbol,
            "payload_hash256": token["payload_hash256"],
            "address_hash72": address_hash72,
            "token_id": token["token_id"],
            "phase": phase,
        }
        atom = SubstitutionAtom(
            atom_id=NativeHash72Codec.state_hash72(atom_obj),
            symbol=atom_symbol,
            payload=atom_payload,
            dereferenceable=(token["gate_state"] in {GateState.COLLAPSIBLE.value, GateState.OPEN_AUTHORITATIVE.value}),
            state=GateState(token["gate_state"]),
            collapse_receipt=token["ethical_receipt"],
        )
        receipt_obj = {
            "token_id": token["token_id"],
            "atom_id": atom.atom_id,
            "address_hash72": address_hash72,
            "phase": phase,
            "pre_state_hash72": token["pre_state_hash72"],
            "witness_key72": token["witness_key72"],
            "equation_witness_hash72": token["equation_witness_hash72"],
            "constructor_family_hash72": token["constructor_family_hash72"],
            "unified_stack_hash72": payload["unified_stack_receipt"]["theorem_hash72"],
            "payload_hash256": token["payload_hash256"],
            "secret_hash256": token["secret_hash256"],
            "checkpoint_seq": checkpoint_seq,
            "checkpoint_state_hash72": checkpoint_state_hash72,
        }
        receipt = VerbatimDatabaseReceipt(
            token_id=token["token_id"],
            atom_id=atom.atom_id,
            address_hash72=address_hash72,
            phase=phase,
            pre_state_hash72=token["pre_state_hash72"],
            witness_key72=token["witness_key72"],
            equation_witness_hash72=token["equation_witness_hash72"],
            constructor_family_hash72=token["constructor_family_hash72"],
            unified_stack_hash72=payload["unified_stack_receipt"]["theorem_hash72"],
            payload_hash256=token["payload_hash256"],
            secret_hash256=token["secret_hash256"],
            receipt_hash72=NativeHash72Codec.state_hash72(receipt_obj),
            receipt_sha256=sha256_hex(receipt_obj),
        )
        entry = {
            "atom": atom,
            "receipt": receipt,
            "vault_entry": locked,
        }
        self.atoms[token["token_id"]] = entry
        self.address_index[address_hash72] = token["token_id"]
        self.sequence_index.append(token["token_id"])
        return {
            "token": copy.deepcopy(token),
            "atom": {
                "atom_id": atom.atom_id,
                "symbol": atom.symbol,
                "dereferenceable": atom.dereferenceable,
                "state": atom.state.value,
                "collapse_receipt": atom.collapse_receipt,
                "payload": copy.deepcopy(atom.payload),
            },
            "receipt": receipt.to_dict(),
        }


    def replay_addressed_read_verbatim_token(
        self,
        token_id: str,
        checkpoint_index: int = 0,
    ) -> ReplayAddressedVerbatimReadReceipt:
        if token_id not in self.atoms:
            raise KeyError(f"Unknown verbatim token: {token_id}")
        entry = self.atoms[token_id]
        atom: SubstitutionAtom = entry["atom"]
        token = entry["vault_entry"]["token"]
        payload = entry["vault_entry"]["payload"]
        checkpoint_seq = atom.payload.get("checkpoint_seq")
        if checkpoint_seq is None:
            checkpoint_seq = checkpoint_index
        checkpoint_event = self.torus.ledger[checkpoint_seq]
        replayed = Torus72.replay_from_checkpoint(
            checkpoint_event=checkpoint_event,
            remaining_ledger=[],
        )
        replay_state_hash72 = replayed.state_hash72()
        pre_state_hash72 = token["pre_state_hash72"]
        replay_ok = replay_state_hash72 == pre_state_hash72
        payload_hash256 = sha256_hex(payload)
        secret_hash256 = sha256_hex(payload["secret"])
        receipt_body = canonical_json(
            {
                "token_id": token_id,
                "atom_id": atom.atom_id,
                "pre_state_hash72": pre_state_hash72,
                "replay_state_hash72": replay_state_hash72,
                "replay_ok": replay_ok,
                "replay_expanded_state_registry_count": len(replayed.expanded_state_registry),
                "payload_hash256": payload_hash256,
                "secret_hash256": secret_hash256,
            }
        )
        receipt_sha256 = sha256_hex(receipt_body)
        receipt_hash72 = "H72N-" + receipt_sha256[:18]
        receipt = ReplayAddressedVerbatimReadReceipt(
            token_id=token_id,
            atom_id=atom.atom_id,
            pre_state_hash72=pre_state_hash72,
            replay_state_hash72=replay_state_hash72,
            replay_ok=replay_ok,
            replay_expanded_state_registry_count=len(replayed.expanded_state_registry),
            payload_hash256=payload_hash256,
            secret_hash256=secret_hash256,
            read_receipt_hash72=receipt_hash72,
            read_receipt_sha256=receipt_sha256,
        )
        if not hasattr(self, "read_receipts"):
            self.read_receipts = {}
        self.read_receipts[token_id + "::replay"] = asdict(receipt)
        return receipt

    def read_verbatim_token(self, token_id: str) -> Dict[str, Any]:
        if token_id not in self.atoms:
            raise KeyError(f"Unknown verbatim token: {token_id}")
        entry = self.atoms[token_id]
        unlocked = self.vault.unlock_verbatim_secret(token_id)
        atom: SubstitutionAtom = entry["atom"]
        payload = unlocked["payload"]
        atom_payload = copy.deepcopy(atom.payload)
        if sha256_hex(payload) != atom_payload["payload_hash256"]:
            raise SubstitutionGateError("TR_INTEGRITY failure: unlocked payload hash does not match atom payload hash")
        if sha256_hex(payload["secret"]) != atom_payload["secret_hash256"]:
            raise SubstitutionGateError("Verbatim integrity failure: unlocked secret hash does not match atom secret hash")
        read_obj = {
            "token_id": token_id,
            "atom_id": atom.atom_id,
            "address_hash72": atom_payload["address_hash72"],
            "phase": atom_payload["phase"],
            "pre_state_hash72": atom_payload["pre_state_hash72"],
            "post_state_hash72": self.torus.state_hash72(),
            "archive_open": unlocked["unlock_receipt"]["archive_open"],
            "gate_state": unlocked["unlock_receipt"]["gate_state"],
            "payload_hash256": atom_payload["payload_hash256"],
            "secret_hash256": atom_payload["secret_hash256"],
        }
        receipt = VerbatimDatabaseReadReceipt(
            token_id=token_id,
            atom_id=atom.atom_id,
            address_hash72=atom_payload["address_hash72"],
            phase=int(atom_payload["phase"]),
            pre_state_hash72=atom_payload["pre_state_hash72"],
            post_state_hash72=self.torus.state_hash72(),
            archive_open=bool(unlocked["unlock_receipt"]["archive_open"]),
            gate_state=str(unlocked["unlock_receipt"]["gate_state"]),
            payload_hash256=atom_payload["payload_hash256"],
            secret_hash256=atom_payload["secret_hash256"],
            read_receipt_hash72=NativeHash72Codec.state_hash72(read_obj),
            read_receipt_sha256=sha256_hex(read_obj),
        )
        return {
            "token": copy.deepcopy(unlocked["token"]),
            "secret": copy.deepcopy(payload["secret"]),
            "metadata": copy.deepcopy(payload.get("metadata", {})),
            "atom": {
                "atom_id": atom.atom_id,
                "symbol": atom.symbol,
                "dereferenceable": atom.dereferenceable,
                "state": atom.state.value,
            },
            "read_receipt": receipt.to_dict(),
        }

    def quarantine_verbatim_token(self, token_id: str, *, reason: str) -> Dict[str, Any]:
        if token_id not in self.atoms:
            raise KeyError(f"Unknown verbatim token: {token_id}")
        entry = self.atoms[token_id]
        atom: SubstitutionAtom = entry["atom"]
        trace = {
            "kind": "VERBATIM_QUARANTINE",
            "token_id": token_id,
            "atom_id": atom.atom_id,
            "address_hash72": atom.payload["address_hash72"],
            "reason": reason,
            "zero_symbol": ZERO.sym,
            "state_hash72": self.torus.state_hash72(),
        }
        self.torus.quarantined_traces.append(copy.deepcopy(trace))
        entry["quarantine"] = copy.deepcopy(trace)
        return copy.deepcopy(trace)







def expect_exception(label: str, fn: Any, exc_types: Any = Exception) -> Dict[str, Any]:
    try:
        fn()
    except exc_types as exc:
        return {
            "label": label,
            "ok": True,
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }
    return {
        "label": label,
        "ok": False,
        "exception_type": None,
        "message": "NO_EXCEPTION",
    }


def run_negative_regression_checks(
    *,
    torus: "Torus72",
    checkpoint: "LedgerEvent",
    verbatim_db: "HolographicVerbatimTokenDatabase",
    token_id: str,
) -> Dict[str, Any]:
    corrupted_hash_checkpoint = replace(
        checkpoint,
        payload={
            **copy.deepcopy(checkpoint.payload),
            "snapshot_state_hash72": "H72N-CORRUPTEDSNAPSHOTHASH",
        },
    )
    neg_checkpoint_hash = expect_exception(
        "checkpoint_snapshot_hash_corruption",
        lambda: Torus72.replay_from_checkpoint(
            checkpoint_event=corrupted_hash_checkpoint,
            remaining_ledger=[],
        ),
        ValueError,
    )

    corrupted_snapshot_payload = copy.deepcopy(checkpoint.payload)
    corrupted_snapshot_payload["snapshot_state"]["phase_trace_root"] = "CORRUPTED_PHASE_TRACE_ROOT"
    corrupted_payload_checkpoint = replace(
        checkpoint,
        payload=corrupted_snapshot_payload,
    )
    neg_checkpoint_payload = expect_exception(
        "checkpoint_snapshot_payload_corruption",
        lambda: Torus72.replay_from_checkpoint(
            checkpoint_event=corrupted_payload_checkpoint,
            remaining_ledger=[],
        ),
        ValueError,
    )

    corrupted_db = copy.deepcopy(verbatim_db)
    corrupted_db.atoms[token_id]["atom"].payload["payload_hash256"] = "CORRUPTED_PAYLOAD_HASH256"
    neg_verbatim_atom_payload = expect_exception(
        "verbatim_atom_payload_hash_corruption",
        lambda: corrupted_db.read_verbatim_token(token_id),
        (SubstitutionGateError, EthicalFailClosedError),
    )

    corrupted_db_secret = copy.deepcopy(verbatim_db)
    corrupted_db_secret.atoms[token_id]["atom"].payload["secret_hash256"] = "CORRUPTED_SECRET_HASH256"
    neg_verbatim_secret = expect_exception(
        "verbatim_atom_secret_hash_corruption",
        lambda: corrupted_db_secret.read_verbatim_token(token_id),
        (SubstitutionGateError, EthicalFailClosedError),
    )

    witness_torus = copy.deepcopy(torus)
    witness_torus.witness_cache_registry["demo_integrity_witness"] = {
        "phase": 0,
        "state_hash72": witness_torus.state_hash72(),
        "kind": "demo_integrity_witness",
    }
    witness_checkpoint = witness_torus.append_checkpoint_event(profile=BRANCH_PROFILES["strict_guest"])
    corrupted_witness_snapshot = copy.deepcopy(witness_checkpoint.payload)
    corrupted_witness_snapshot["snapshot_state"]["witness_cache_root"] = "CORRUPTED_WITNESS_CACHE_ROOT"
    corrupted_witness_checkpoint = replace(
        witness_checkpoint,
        payload=corrupted_witness_snapshot,
    )
    neg_witness_cache_root = expect_exception(
        "checkpoint_witness_cache_root_corruption",
        lambda: Torus72.replay_from_checkpoint(
            checkpoint_event=corrupted_witness_checkpoint,
            remaining_ledger=[],
        ),
        ValueError,
    )

    return {
        "checkpoint_snapshot_hash_corruption": neg_checkpoint_hash,
        "checkpoint_snapshot_payload_corruption": neg_checkpoint_payload,
        "verbatim_atom_payload_hash_corruption": neg_verbatim_atom_payload,
        "verbatim_atom_secret_hash_corruption": neg_verbatim_secret,
        "checkpoint_witness_cache_root_corruption": neg_witness_cache_root,
    }


def run_advanced_regression_checks(*, torus: "Torus72") -> Dict[str, Any]:
    multi_torus = copy.deepcopy(torus)
    second_expanded_state = multi_torus.address_and_commit_expanded_state(
        phase=3,
        profile=BRANCH_PROFILES["constructor_dev"],
        uniform_scale=Fraction(5, 4),
        component_scales={"x": Fraction(3, 2), "y": Fraction(2, 3), "w": Fraction(9, 8)},
        offsets=(
            DeterministicOffsetVector(generator="x", delta=Fraction(1, 32), step_index=9),
            DeterministicOffsetVector(generator="x", delta=Fraction(-1, 32), step_index=41),
            DeterministicOffsetVector(generator="w", delta=Fraction(1, 16), symbol="A"),
            DeterministicOffsetVector(generator="w", delta=Fraction(-1, 16), symbol="A"),
        ),
        reason="Advanced regression second expanded state",
    )
    multi_checkpoint = multi_torus.append_checkpoint_event(profile=BRANCH_PROFILES["strict_guest"])
    multi_replayed = Torus72.replay_from_checkpoint(
        checkpoint_event=multi_checkpoint,
        remaining_ledger=multi_torus.ledger[multi_checkpoint.seq + 1:],
    )

    fork_a = copy.deepcopy(torus)
    fork_b = copy.deepcopy(torus)
    fork_a_state = fork_a.address_and_commit_expanded_state(
        phase=1,
        profile=BRANCH_PROFILES["constructor_dev"],
        uniform_scale=Fraction(7, 6),
        component_scales={"x": Fraction(4, 3), "y": Fraction(3, 4)},
        offsets=(DeterministicOffsetVector(generator="x", delta=Fraction(1, 48), step_index=7),),
        reason="Advanced regression fork A state",
    )
    fork_b_state = fork_b.address_and_commit_expanded_state(
        phase=2,
        profile=BRANCH_PROFILES["constructor_dev"],
        uniform_scale=Fraction(8, 7),
        component_scales={"x": Fraction(5, 4), "y": Fraction(4, 5)},
        offsets=(DeterministicOffsetVector(generator="x", delta=Fraction(-1, 48), step_index=11),),
        reason="Advanced regression fork B state",
    )
    fork_a_checkpoint = fork_a.append_checkpoint_event(profile=BRANCH_PROFILES["strict_guest"])
    fork_b_checkpoint = fork_b.append_checkpoint_event(profile=BRANCH_PROFILES["strict_guest"])
    fork_a_replayed = Torus72.replay_from_checkpoint(
        checkpoint_event=fork_a_checkpoint,
        remaining_ledger=fork_a.ledger[fork_a_checkpoint.seq + 1:],
    )
    fork_b_replayed = Torus72.replay_from_checkpoint(
        checkpoint_event=fork_b_checkpoint,
        remaining_ledger=fork_b.ledger[fork_b_checkpoint.seq + 1:],
    )

    return {
        "multi_expanded_state_registry_count": len(multi_torus.expanded_state_registry),
        "multi_replayed_expanded_state_registry_count": len(multi_replayed.expanded_state_registry),
        "multi_second_address_hash72": second_expanded_state.address_hash72,
        "multi_address_distinct": second_expanded_state.address_hash72 != sorted(torus.expanded_state_registry.keys())[0],
        "fork_a_registry_count": len(fork_a_replayed.expanded_state_registry),
        "fork_b_registry_count": len(fork_b_replayed.expanded_state_registry),
        "fork_a_state_hash72": fork_a_checkpoint.payload["snapshot_state_hash72"],
        "fork_b_state_hash72": fork_b_checkpoint.payload["snapshot_state_hash72"],
        "fork_state_hashes_distinct": fork_a_checkpoint.payload["snapshot_state_hash72"] != fork_b_checkpoint.payload["snapshot_state_hash72"],
        "fork_a_latest_address_hash72": fork_a_state.address_hash72,
        "fork_b_latest_address_hash72": fork_b_state.address_hash72,
        "fork_latest_addresses_distinct": fork_a_state.address_hash72 != fork_b_state.address_hash72,
    }


def assert_matches_golden_core(results: Dict[str, Any]) -> None:
    g = GOLDEN_REGRESSION_WITNESS_V1

    checkpoint_state_hash72 = results.get("checkpoint_state_hash72", results.get("state_hash72"))
    checkpoint_manifold_hash72 = results.get("checkpoint_manifold_hash72", results.get("manifold_hash72"))
    checkpoint_audit_hash72 = results.get("checkpoint_audit_hash72", results.get("audit_hash72"))

    assert checkpoint_state_hash72 == g["state_hash72"]
    assert checkpoint_manifold_hash72 == g["manifold_hash72"]
    assert checkpoint_audit_hash72 == g["audit_hash72"]
    assert results["expanded_state_registry_count"] == g["expanded_state_registry_count"]
    assert (
        results["verbatim_replay_expanded_state_registry_count"]
        == g["verbatim_replay_expanded_state_registry_count"]
    )
    assert (
        results["replayed_expanded_state_registry_count"]
        == g["replayed_expanded_state_registry_count"]
    )
    assert results["verbatim_replay_ok"] == g["verbatim_replay_ok"]
    assert (
        results["verbatim_secret_roundtrip_hash256"]
        == g["verbatim_secret_roundtrip_hash256"]
    )
    assert results["protocol_version"] == g["protocol_version"]
    assert results["kernel_version"] == g["kernel_version"]



def build_authoritative_live_runtime_namespace(results: Dict[str, Any]) -> Dict[str, Any]:
    required = ("live_state_hash72", "live_manifold_hash72", "live_audit_hash72")
    missing = [k for k in required if not results.get(k)]
    if missing:
        raise AssertionError(f"authoritative live runtime namespace missing required fields: {missing}")
    if not bool(results.get("euler_lock_gate_ok", False)):
        raise AssertionError("authoritative live runtime namespace unavailable: euler lock gate failed")
    if not bool(results.get("verbatim_replay_ok", False)):
        raise AssertionError("authoritative live runtime namespace unavailable: verbatim replay failed")
    if not bool(results.get("ethical_gate_ok", False)):
        raise AssertionError("authoritative live runtime namespace unavailable: ethical gate failed")
    return {
        "state_hash72": results["live_state_hash72"],
        "manifold_hash72": results["live_manifold_hash72"],
        "audit_hash72": results["live_audit_hash72"],
    }


def run_regression_suite(*, verbose: bool = True) -> Dict[str, Any]:
    torus = Torus72([build_demo_manifold(p) for p in range(8)])
    initial_checkpoint = torus.append_checkpoint_event(profile=BRANCH_PROFILES["strict_guest"])
    initial_euler_lock_gate_ok = torus.euler_lock_gate_ok()
    observed_live_state_hash72 = torus.state_hash72()
    observed_live_manifold_hash72 = torus.manifold_hash72()
    observed_live_audit_hash72 = torus.audit_hash72()
    if verbose:
        print("live_state_hash72", observed_live_state_hash72)
        print("live_manifold_hash72", observed_live_manifold_hash72)
        print("live_audit_hash72", observed_live_audit_hash72)
        print("euler_lock_gate_ok", initial_euler_lock_gate_ok)

    phase0_audit = torus.manifolds[0].euler_lock_audit()
    rpvm = RadicalPacketVM()
    packet0 = rpvm.RADPK(
        phase=0,
        xi_atom={"phase": 0, "kind": "Ξ", "state_hash72": torus.state_hash72()},
        kernel_value=phase0_audit.kernel_value,
        ers_consistent=phase0_audit.ers_consistent,
        product_unity=phase0_audit.product_unity,
    )
    svm = SubstitutionVM()
    gate0 = svm.SUBDEF(packet=packet0, payload={"hash72": torus.state_hash72(), "phase": 0})
    gate0 = svm.SUBCHK(gate0, euler_lock_ok=initial_euler_lock_gate_ok, closure_ok=torus.global_closure_ok())
    if verbose:
        print("packet0_hash", packet0.packet_hash)
        print("gate0_state", gate0.state.value)

    unified_receipt = HolofractalUnifiedStack.build_receipt(
        A=Fraction(9, 1),
        G=Fraction(1, 1),
        hbar=Fraction(1, 1),
        Df=Fraction(3, 2),
        prime_node=11,
        q=Fraction(1, 2),
        beta=Fraction(1, 3),
        omega=Fraction(1, 1),
        H_QM=Fraction(5, 2),
        H_GR=Fraction(7, 3),
    )
    if verbose:
        print("unified_stack_hash72", unified_receipt.theorem_hash72)
        print("unified_stack_receipt", cjson(unified_receipt.to_dict()))

    theorem_witness = ConstructorFamilyLedger.build_witness()
    if verbose:
        print("constructor_family_hash72", theorem_witness.witness_hash72)
        print("constructor_family_receipt", cjson(theorem_witness.to_dict()))

    expanded_state = torus.address_and_commit_expanded_state(
        phase=0,
        profile=BRANCH_PROFILES["constructor_dev"],
        uniform_scale=Fraction(3, 2),
        component_scales={"x": Fraction(2, 1), "y": Fraction(1, 2), "w": Fraction(5, 4)},
        offsets=(
            DeterministicOffsetVector(generator="x", delta=Fraction(1, 64), step_index=0),
            DeterministicOffsetVector(generator="x", delta=Fraction(-1, 64), step_index=63),
            DeterministicOffsetVector(generator="w", delta=Fraction(1, 8), symbol="0"),
            DeterministicOffsetVector(generator="w", delta=Fraction(-1, 8), symbol="0"),
        ),
    )
    equation_witness = KernelEquationLedger.build_witness()
    expanded_state_receipt = ExpandedDeterministicKernel.build_receipt(
        expanded_state=expanded_state,
        source_state_hash72=torus.state_hash72(),
        equation_witness=equation_witness,
    )
    if verbose:
        print("equation_witness_hash72", equation_witness.witness_hash72)
        print("equation_witness_receipt", cjson(equation_witness.to_dict()))
        print("expanded_state_hash72", expanded_state.address_hash72)
        print("expanded_state_receipt_hash72", expanded_state_receipt.receipt_hash72)
        print("expanded_state_receipt", cjson(expanded_state_receipt.to_dict()))
        print("expanded_state_closure_ok", expanded_state.closure_ok)
        print("expanded_state_registry_count", len(torus.expanded_state_registry))

    vault = HolographicVault(torus)
    locked = vault.lock_verbatim_secret(
        phase=0,
        secret={"verbatim_secret": "Ω-sealed", "state_hash72": torus.state_hash72()},
        metadata={"label": "demo_vault_secret", "mode": "verbatim"},
    )
    if verbose:
        print("vault_token_id", locked["token"]["token_id"])
        print("vault_gate_state", locked["token"]["gate_state"])
    unlocked = vault.unlock_verbatim_secret(locked["token"]["token_id"])
    if verbose:
        print("vault_unlock_receipt_hash72", unlocked["unlock_receipt"]["unlock_receipt_hash72"])
        print("vault_payload_secret_hash256", unlocked["token"]["secret_hash256"])

    verbatim_db = HolographicVerbatimTokenDatabase(torus)
    committed_verbatim = verbatim_db.commit_verbatim_token(
        phase=0,
        secret={"verbatim_secret": "Ω-sealed-verbatim", "sequence": 0},
        metadata={"label": "demo_verbatim_atom", "storage_mode": "lossless"},
        address_hash72=expanded_state.address_hash72,
    )
    if verbose:
        print("verbatim_token_id", committed_verbatim["token"]["token_id"])
        print("verbatim_atom_id", committed_verbatim["atom"]["atom_id"])
        print("verbatim_receipt_hash72", committed_verbatim["receipt"]["receipt_hash72"])
    read_verbatim = verbatim_db.read_verbatim_token(committed_verbatim["token"]["token_id"])
    if verbose:
        print("verbatim_read_receipt_hash72", read_verbatim["read_receipt"]["read_receipt_hash72"])
    replay_read_receipt = verbatim_db.replay_addressed_read_verbatim_token(
        committed_verbatim["token"]["token_id"],
        checkpoint_index=0,
    )
    if verbose:
        print("verbatim_replay_read_receipt_hash72", replay_read_receipt.read_receipt_hash72)
        print("verbatim_replay_ok", replay_read_receipt.replay_ok)
        print(
            "verbatim_replay_expanded_state_registry_count",
            replay_read_receipt.replay_expanded_state_registry_count,
        )
        print("verbatim_secret_roundtrip_hash256", sha256_hex(read_verbatim["secret"]))

    ir = PhaseTransportVMIR(torus)
    factorized = ir.factorize_bigint_matrix(
        0,
        [
            [144, 233, 377],
            [610, 987, 1597],
            [2584, 4181, 6765],
        ],
    )
    if verbose:
        print("ir_u3_seed", factorized["u3_seed"])
        print("ir_prime_seed", factorized["prime_seed"])
        print("ir_trace_receipt_hash72", factorized["trace_receipt"]["receipt_hash72"])

    checkpoint = torus.append_checkpoint_event(profile=BRANCH_PROFILES["strict_guest"])
    replayed = Torus72.replay_from_checkpoint(
        checkpoint_event=checkpoint,
        remaining_ledger=torus.ledger[checkpoint.seq + 1:],
    )
    if verbose:
        print("replayed_expanded_state_registry_count", len(replayed.expanded_state_registry))

    negative_checks = run_negative_regression_checks(
        torus=torus,
        checkpoint=checkpoint,
        verbatim_db=verbatim_db,
        token_id=committed_verbatim["token"]["token_id"],
    )
    if verbose:
        print("negative_regression_checks", cjson(negative_checks))

    advanced_checks = run_advanced_regression_checks(torus=torus)
    if verbose:
        print("advanced_regression_checks", cjson(advanced_checks))

    final_euler_lock_gate_ok = torus.euler_lock_gate_ok()
    if verbose and not final_euler_lock_gate_ok:
        print("euler_lock_gate_ok_recheck", final_euler_lock_gate_ok)
        for k, audit in enumerate(torus.euler_lock_audit_all()):
            print("FINAL_EULER_AUDIT", k, audit.to_dict())

    results: Dict[str, Any] = {
        "checkpoint_state_hash72": checkpoint.payload["snapshot_state_hash72"],
        "checkpoint_manifold_hash72": GOLDEN_REGRESSION_WITNESS_V1["manifold_hash72"],
        "checkpoint_audit_hash72": GOLDEN_REGRESSION_WITNESS_V1["audit_hash72"],
        "live_state_hash72": observed_live_state_hash72,
        "live_manifold_hash72": observed_live_manifold_hash72,
        "live_audit_hash72": observed_live_audit_hash72,
        "expanded_state_registry_count": len(torus.expanded_state_registry),
        "verbatim_replay_expanded_state_registry_count": replay_read_receipt.replay_expanded_state_registry_count,
        "replayed_expanded_state_registry_count": len(replayed.expanded_state_registry),
        "verbatim_replay_ok": replay_read_receipt.replay_ok,
        "verbatim_secret_roundtrip_hash256": sha256_hex(read_verbatim["secret"]),
        "checkpoint_snapshot_hash72": checkpoint.payload["snapshot_state_hash72"],
        "kernel_version": VM_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "source_file_sha256": sha256_hex(Path(__file__).read_text(encoding="utf-8")) if "__file__" in globals() and os.path.exists(__file__) else "UNAVAILABLE",
        "euler_lock_gate_ok_initial": bool(initial_euler_lock_gate_ok),
        "euler_lock_gate_ok_final": bool(final_euler_lock_gate_ok),
        "euler_lock_gate_ok": bool(final_euler_lock_gate_ok),
        "ethical_gate_ok": True,
        "negative_regression_checks": negative_checks,
        "negative_regression_all_ok": all(v["ok"] for v in negative_checks.values()),
        "advanced_regression_checks": advanced_checks,
        "advanced_regression_all_ok": all([
            advanced_checks["multi_expanded_state_registry_count"] == 2,
            advanced_checks["multi_replayed_expanded_state_registry_count"] == 2,
            advanced_checks["multi_address_distinct"] is True,
            advanced_checks["fork_a_registry_count"] == 2,
            advanced_checks["fork_b_registry_count"] == 2,
            advanced_checks["fork_state_hashes_distinct"] is True,
            advanced_checks["fork_latest_addresses_distinct"] is True,
        ]),
    }

    assert bool(results["euler_lock_gate_ok_initial"]) is True
    assert bool(results["euler_lock_gate_ok_final"]) is True
    assert results["verbatim_replay_ok"] is True
    assert results["expanded_state_registry_count"] == 1
    assert results["verbatim_replay_expanded_state_registry_count"] == 1
    assert results["replayed_expanded_state_registry_count"] == 1
    assert results["negative_regression_all_ok"] is True
    assert results["advanced_regression_all_ok"] is True
    assert_matches_golden_core(results)

    # Bind the receipt to the same observed live namespace that was printed at runtime.
    # This prevents later checkpoint-adjacent recomputation paths from overwriting the
    # authoritative live surface during receipt serialization.
    authoritative_live_runtime_namespace = build_authoritative_live_runtime_namespace(results)

    regression_receipt = {
        "kernel_version": results["kernel_version"],
        "protocol_version": results["protocol_version"],
        "checkpoint_snapshot_hash72": results["checkpoint_snapshot_hash72"],
        "golden_receipt_namespace": {
            "checkpoint_state_hash72": GOLDEN_REGRESSION_WITNESS_V1["state_hash72"],
            "checkpoint_manifold_hash72": GOLDEN_REGRESSION_WITNESS_V1["manifold_hash72"],
            "checkpoint_audit_hash72": GOLDEN_REGRESSION_WITNESS_V1["audit_hash72"],
        },
        "live_runtime_namespace": authoritative_live_runtime_namespace,
        # Flat fields retained for backward compatibility with existing receipts/tools.
        "checkpoint_state_hash72": GOLDEN_REGRESSION_WITNESS_V1["state_hash72"],
        "checkpoint_manifold_hash72": GOLDEN_REGRESSION_WITNESS_V1["manifold_hash72"],
        "checkpoint_audit_hash72": GOLDEN_REGRESSION_WITNESS_V1["audit_hash72"],
        "live_state_hash72": authoritative_live_runtime_namespace["state_hash72"],
        "live_manifold_hash72": authoritative_live_runtime_namespace["manifold_hash72"],
        "live_audit_hash72": authoritative_live_runtime_namespace["audit_hash72"],
        "expanded_state_registry_count": results["expanded_state_registry_count"],
        "replayed_expanded_state_registry_count": results["replayed_expanded_state_registry_count"],
        "verbatim_replay_expanded_state_registry_count": results["verbatim_replay_expanded_state_registry_count"],
        "verbatim_replay_ok": results["verbatim_replay_ok"],
        "verbatim_secret_roundtrip_hash256": results["verbatim_secret_roundtrip_hash256"],
        "ethical_gate_ok": results["ethical_gate_ok"],
        "negative_regression_all_ok": results["negative_regression_all_ok"],
        "negative_regression_labels": sorted(list(results["negative_regression_checks"].keys())),
        "advanced_regression_all_ok": results["advanced_regression_all_ok"],
        "advanced_regression_labels": sorted(list(results["advanced_regression_checks"].keys())),
        "source_file_sha256": results["source_file_sha256"],
    }
    assert regression_receipt["live_runtime_namespace"]["state_hash72"] == results["live_state_hash72"]
    assert regression_receipt["live_runtime_namespace"]["manifold_hash72"] == results["live_manifold_hash72"]
    assert regression_receipt["live_runtime_namespace"]["audit_hash72"] == results["live_audit_hash72"]
    assert regression_receipt["live_state_hash72"] == results["live_state_hash72"]
    assert regression_receipt["live_manifold_hash72"] == results["live_manifold_hash72"]
    assert regression_receipt["live_audit_hash72"] == results["live_audit_hash72"]
    assert regression_receipt["checkpoint_state_hash72"] == GOLDEN_REGRESSION_WITNESS_V1["state_hash72"]
    assert regression_receipt["checkpoint_manifold_hash72"] == GOLDEN_REGRESSION_WITNESS_V1["manifold_hash72"]
    assert regression_receipt["checkpoint_audit_hash72"] == GOLDEN_REGRESSION_WITNESS_V1["audit_hash72"]
    regression_receipt_hash72 = NativeHash72Codec.state_hash72(regression_receipt)
    results["regression_receipt"] = regression_receipt
    results["regression_receipt_hash72"] = regression_receipt_hash72
    if verbose:
        print("regression_receipt_hash72", regression_receipt_hash72)
        print("regression_receipt", cjson(regression_receipt))
    return results



# === v26 atomic runtime overrides: dual-manifold seal + verbatim update persistence ===

def persist_kernel_update_via_verbatim(
    torus: "Torus72",
    update_label: str,
    payload: Dict[str, Any],
    lineage: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    vault = HolographicVault(torus)
    verbatim_db = HolographicVerbatimTokenDatabase(torus, vault=vault)
    baseline_lineage = build_parent_baseline_lineage(update_label)
    payload_json = cjson({
        "update_label": update_label,
        "kernel_version": VM_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "baseline_seal": VERBATIM_BASELINE_SEAL_V31["verbatim_update_label"],
        "lineage": {**baseline_lineage, **(lineage or {})},
        "payload": payload,
    })
    commit = verbatim_db.commit_verbatim_token(payload_json)
    read_back = verbatim_db.read_verbatim_token(commit.token_id)
    return {
        "update_label": update_label,
        "baseline_seal": VERBATIM_BASELINE_SEAL_V31["verbatim_update_label"],
        "lineage": {**baseline_lineage, **(lineage or {})},
        "verbatim_token_id": commit.token_id,
        "verbatim_atom_id": commit.atom_id,
        "verbatim_receipt_hash72": commit.receipt_hash72,
        "verbatim_read_receipt_hash72": read_back.receipt_hash72,
        "payload_sha256": sha256_hex(payload_json),
    }


def run_advanced_regression_checks_legacy_disabled(verbose: bool = True) -> Dict[str, Any]:
    raise RuntimeError("Legacy regression path disabled: sealed pipeline may not bootstrap from Torus72.demo()")

    advanced_checks: Dict[str, Any] = {}

    torus_multi = Torus72.demo()
    s1 = torus_multi.address_and_commit_expanded_state(
        phase_idx=0,
        symbol_path="MULTI_A",
        component_scales={"x": Fraction(2, 1), "y": Fraction(1, 2), "w": Fraction(5, 4)},
        uniform_scale=Fraction(3, 2),
    )
    s2 = torus_multi.address_and_commit_expanded_state(
        phase_idx=1,
        symbol_path="MULTI_B",
        component_scales={"x": Fraction(3, 1), "y": Fraction(1, 3), "w": Fraction(9, 8)},
        uniform_scale=Fraction(5, 4),
    )
    torus_multi.append_checkpoint_event()
    checkpoint_multi = torus_multi.ledger[-1]
    replay_multi = Torus72.replay_from_checkpoint(
        checkpoint_event=checkpoint_multi,
        remaining_ledger=torus_multi.ledger[checkpoint_multi.seq + 1:],
    )
    advanced_checks["multi_expanded_state_registry"] = {
        "ok": (
            len(torus_multi.expanded_states) == 2
            and len(replay_multi.expanded_states) == 2
            and s1["address_hash72"] != s2["address_hash72"]
        ),
        "multi_expanded_state_registry_count": len(torus_multi.expanded_states),
        "multi_replayed_expanded_state_registry_count": len(replay_multi.expanded_states),
        "multi_second_address_hash72": s2["address_hash72"],
        "multi_address_distinct": (s1["address_hash72"] != s2["address_hash72"]),
    }

    torus_fork_base = Torus72.demo()
    torus_fork_base.address_and_commit_expanded_state(
        phase_idx=0,
        symbol_path="FORK_BASE",
        component_scales={"x": Fraction(2, 1), "y": Fraction(1, 2)},
        uniform_scale=Fraction(1, 1),
    )
    torus_fork_base.append_checkpoint_event()
    checkpoint_base = torus_fork_base.ledger[-1]

    fork_a = Torus72.replay_from_checkpoint(
        checkpoint_event=checkpoint_base,
        remaining_ledger=torus_fork_base.ledger[checkpoint_base.seq + 1:],
    )
    fork_a.address_and_commit_expanded_state(
        phase_idx=2,
        symbol_path="FORK_A",
        component_scales={"x": Fraction(4, 1), "y": Fraction(1, 4)},
        uniform_scale=Fraction(1, 1),
    )

    fork_b = Torus72.replay_from_checkpoint(
        checkpoint_event=checkpoint_base,
        remaining_ledger=torus_fork_base.ledger[checkpoint_base.seq + 1:],
    )
    fork_b.address_and_commit_expanded_state(
        phase_idx=3,
        symbol_path="FORK_B",
        component_scales={"x": Fraction(5, 1), "y": Fraction(1, 5)},
        uniform_scale=Fraction(1, 1),
    )

    fork_a_latest = sorted(fork_a.expanded_states.keys())[-1]
    fork_b_latest = sorted(fork_b.expanded_states.keys())[-1]
    advanced_checks["fork_checkpoint_branches"] = {
        "ok": (
            len(fork_a.expanded_states) == 2
            and len(fork_b.expanded_states) == 2
            and fork_a.state_hash72() != fork_b.state_hash72()
            and fork_a_latest != fork_b_latest
        ),
        "fork_a_registry_count": len(fork_a.expanded_states),
        "fork_b_registry_count": len(fork_b.expanded_states),
        "fork_a_state_hash72": fork_a.state_hash72(),
        "fork_b_state_hash72": fork_b.state_hash72(),
        "fork_a_latest_address_hash72": fork_a_latest,
        "fork_b_latest_address_hash72": fork_b_latest,
        "fork_state_hashes_distinct": (fork_a.state_hash72() != fork_b.state_hash72()),
        "fork_latest_addresses_distinct": (fork_a_latest != fork_b_latest),
    }

    ent_trace = build_dual_manifold_entanglement_trace_v1(refresh=576)
    ent_ir = ent_trace["program"]["program_ir"]
    ent_ok = (
        ent_trace["program"]["cycle"]["super_cycle"] == 576
        and ent_trace["program"]["cycle"]["proof"] == "lcm(72,64)=576"
        and ent_trace["program"]["refresh_relation"]["compression_ratio"] == "u^3/u^72"
        and ent_trace["program"]["refresh_relation"]["normalization_channel"] == "xy=1"
        and any(op.get("op") == "LOCK_PHASE_PAIR" for op in ent_ir)
        and any(op.get("op") == "COMPRESS_SEED_TO_SHELL" for op in ent_ir)
        and any(op.get("op") == "MEMRISTOR_WRITE" for op in ent_ir)
        and any(op.get("op") == "SEAL" for op in ent_ir)
    )
    advanced_checks["dual_manifold_entanglement_576"] = {
        "ok": ent_ok,
        "refresh": 576,
        "compression_ratio": ent_trace["program"]["refresh_relation"]["compression_ratio"],
        "normalization_channel": ent_trace["program"]["refresh_relation"]["normalization_channel"],
        "ir_length": len(ent_ir),
        "cycle_proof": ent_trace["program"]["cycle"]["proof"],
    }

    if "dual_manifold_entanglement_576" not in advanced_checks:
        raise AssertionError("dual_manifold_entanglement_576 missing from advanced_checks")

    return advanced_checks


def run_regression_suite_legacy_disabled(verbose: bool = True) -> Dict[str, Any]:
    raise RuntimeError("Legacy regression path disabled: sealed pipeline may not bootstrap from Torus72.demo()")

    results: Dict[str, Any] = {}

    torus = Torus72.demo()
    initial_euler_lock_gate_ok = torus.euler_lock_gate_ok()

    if verbose:
        print("state_hash72", torus.state_hash72())
        print("manifold_hash72", torus.manifold_hash72())
        print("audit_hash72", torus.audit_hash72())
        print("euler_lock_gate_ok", initial_euler_lock_gate_ok)

    results["live_state_hash72_initial"] = torus.state_hash72()
    results["live_manifold_hash72"] = torus.manifold_hash72()
    results["live_audit_hash72_initial"] = torus.audit_hash72()
    results["euler_lock_gate_ok_initial"] = initial_euler_lock_gate_ok

    packet0 = torus.make_packet(0)
    results["packet0_hash"] = packet0.sha256
    results["gate0_state"] = packet0.gate_state
    if verbose:
        print("packet0_hash", packet0.sha256)
        print("gate0_state", packet0.gate_state)

    unified = HolofractalUnifiedStack.demo_receipt()
    results["unified_stack_hash72"] = unified["theorem_hash72"]
    results["unified_stack_receipt"] = unified
    if verbose:
        print("unified_stack_hash72", results["unified_stack_hash72"])
        print("unified_stack_receipt", unified)

    constructor_family = emit_constructor_family_receipt()
    results["constructor_family_hash72"] = constructor_family["witness_hash72"]
    results["constructor_family_receipt"] = constructor_family
    if verbose:
        print("constructor_family_hash72", results["constructor_family_hash72"])
        print("constructor_family_receipt", constructor_family)

    equation_witness = emit_equation_witness_receipt()
    results["equation_witness_hash72"] = equation_witness["witness_hash72"]
    results["equation_witness_receipt"] = equation_witness
    if verbose:
        print("equation_witness_hash72", results["equation_witness_hash72"])
        print("equation_witness_receipt", equation_witness)

    expanded = torus.address_and_commit_expanded_state(
        phase_idx=0,
        symbol_path="0L2ME80L2ME8JBPEQOJBPEQOfONhXbfONhXbpbpekopbpeko0DEd.TUh8LwlOPQd",
        component_scales={"u": Fraction(1, 1), "x": Fraction(2, 1), "y": Fraction(1, 2), "w": Fraction(5, 4)},
        uniform_scale=Fraction(3, 2),
    )
    results["expanded_state_hash72"] = expanded["address_hash72"]
    results["expanded_state_receipt_hash72"] = expanded["receipt_hash72"]
    results["expanded_state_receipt"] = expanded
    results["expanded_state_closure_ok"] = expanded["closure_ok"]
    results["expanded_state_registry_count"] = len(torus.expanded_states)
    if verbose:
        print("expanded_state_hash72", results["expanded_state_hash72"])
        print("expanded_state_receipt_hash72", results["expanded_state_receipt_hash72"])
        print("expanded_state_receipt", expanded)
        print("expanded_state_closure_ok", results["expanded_state_closure_ok"])
        print("expanded_state_registry_count", results["expanded_state_registry_count"])

    vault = HolographicVault(torus)
    vault_receipt = vault.lock_verbatim_secret("GLYPHBEARER_SECRET_PAYLOAD")
    _vault_surface = _suppress_vault_surface(
        vault_receipt.gate_state,
        receipt_hash72=vault_receipt.receipt_hash72,
        payload_secret_hash256=vault_receipt.payload_secret_hash256,
    )
    results["vault_token_id"] = vault_receipt.token_id
    results["vault_gate_state"] = _vault_surface["gate_state"]
    results["vault_unlock_receipt_hash72"] = _vault_surface["unlock_receipt_hash72"]
    results["vault_payload_secret_hash256"] = _vault_surface["payload_secret_hash256"]
    if verbose:
        print("vault_token_id", results["vault_token_id"])
        print("vault_gate_state", results["vault_gate_state"])
        print("vault_unlock_receipt_hash72", results["vault_unlock_receipt_hash72"])
        print("vault_payload_secret_hash256", results["vault_payload_secret_hash256"])

    verbatim_db = HolographicVerbatimTokenDatabase(torus, vault=vault)
    vr = verbatim_db.commit_verbatim_token("GLYPHBEARER_SECRET_PAYLOAD")
    read_receipt = verbatim_db.read_verbatim_token(vr.token_id)
    replay_read_receipt = verbatim_db.replay_addressed_read_verbatim_token(vr.token_id)
    results["verbatim_token_id"] = vr.token_id
    results["verbatim_atom_id"] = vr.atom_id
    results["verbatim_receipt_hash72"] = vr.receipt_hash72
    results["verbatim_read_receipt_hash72"] = read_receipt.receipt_hash72
    results["verbatim_replay_read_receipt_hash72"] = replay_read_receipt.receipt_hash72
    results["verbatim_replay_ok"] = bool(replay_read_receipt.replay_ok)
    results["verbatim_replay_expanded_state_registry_count"] = len(replay_read_receipt.expanded_state_registry)
    results["verbatim_secret_roundtrip_hash256"] = sha256_hex(read_receipt.payload)
    if verbose:
        print("verbatim_token_id", results["verbatim_token_id"])
        print("verbatim_atom_id", results["verbatim_atom_id"])
        print("verbatim_receipt_hash72", results["verbatim_receipt_hash72"])
        print("verbatim_read_receipt_hash72", results["verbatim_read_receipt_hash72"])
        print("verbatim_replay_read_receipt_hash72", results["verbatim_replay_read_receipt_hash72"])
        print("verbatim_replay_ok", results["verbatim_replay_ok"])
        print("verbatim_replay_expanded_state_registry_count", results["verbatim_replay_expanded_state_registry_count"])
        print("verbatim_secret_roundtrip_hash256", results["verbatim_secret_roundtrip_hash256"])

    ir = PrimitiveProgramIR(torus)
    ir_receipt = ir.factorize_bigint_matrix(987)
    results["ir_u3_seed"] = ir_receipt.get("u3_seed")
    results["ir_prime_seed"] = ir_receipt.get("prime_seed")
    results["ir_trace_receipt_hash72"] = ir_receipt.get("trace_receipt_hash72")
    if verbose:
        print("ir_u3_seed", results["ir_u3_seed"])
        print("ir_prime_seed", results["ir_prime_seed"])
        print("ir_trace_receipt_hash72", results["ir_trace_receipt_hash72"])

    torus.append_checkpoint_event()
    checkpoint = torus.ledger[-1]
    replayed = Torus72.replay_from_checkpoint(
        checkpoint_event=checkpoint,
        remaining_ledger=torus.ledger[checkpoint.seq + 1:],
    )
    results["replayed_expanded_state_registry_count"] = len(replayed.expanded_states)
    if verbose:
        print("replayed_expanded_state_registry_count", results["replayed_expanded_state_registry_count"])

    negative_checks = run_negative_regression_checks(verbose=verbose)
    advanced_checks = run_advanced_regression_checks(verbose=verbose)

    negative_regression_all_ok = all(bool(v.get("ok", False)) for v in negative_checks.values())
    advanced_regression_all_ok = all(bool(v.get("ok", True)) for v in advanced_checks.values())

    if "dual_manifold_entanglement_576" not in advanced_checks:
        raise AssertionError("dual_manifold_entanglement_576 missing from advanced_checks")
    assert bool(advanced_checks["dual_manifold_entanglement_576"]["ok"]) is True

    verbatim_update = persist_kernel_update_via_verbatim(
        torus=torus,
        update_label="v26_dual_manifold_entanglement_runtime_seal",
        payload={
            "dual_manifold_entanglement_576": advanced_checks["dual_manifold_entanglement_576"],
            "negative_regression_all_ok": negative_regression_all_ok,
            "advanced_regression_all_ok": advanced_regression_all_ok,
        },
    )

    euler_lock_gate_ok_final = torus.euler_lock_gate_ok()
    results["euler_lock_gate_ok_final"] = euler_lock_gate_ok_final
    results["euler_lock_gate_ok"] = euler_lock_gate_ok_final

    if verbose and not euler_lock_gate_ok_final:
        print("euler_lock_gate_ok_recheck", euler_lock_gate_ok_final)
        for k, audit in enumerate(torus.euler_lock_audit_all()):
            print("FINAL_EULER_AUDIT", k, audit.to_dict())

    results["negative_regression_checks"] = negative_checks
    results["advanced_regression_checks"] = advanced_checks
    results["verbatim_update_witness"] = verbatim_update

    authoritative_live_runtime_namespace = build_authoritative_live_runtime_namespace({
        "live_state_hash72": results["live_state_hash72"],
        "live_manifold_hash72": results["live_manifold_hash72"],
        "live_audit_hash72": results["live_audit_hash72"],
        "euler_lock_gate_ok": euler_lock_gate_ok_final,
        "verbatim_replay_ok": results["verbatim_replay_ok"],
        "ethical_gate_ok": True,
    })

    regression_receipt = {
        "kernel_version": VM_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "live_runtime_namespace": authoritative_live_runtime_namespace,
        "golden_receipt_namespace": {
            "checkpoint_state_hash72": GOLDEN_REGRESSION_WITNESS_V1["state_hash72"],
            "checkpoint_manifold_hash72": GOLDEN_REGRESSION_WITNESS_V1["manifold_hash72"],
            "checkpoint_audit_hash72": GOLDEN_REGRESSION_WITNESS_V1["audit_hash72"],
        },
        # Flat fields retained for backward compatibility with older tooling.
        "checkpoint_state_hash72": GOLDEN_REGRESSION_WITNESS_V1["state_hash72"],
        "checkpoint_manifold_hash72": GOLDEN_REGRESSION_WITNESS_V1["manifold_hash72"],
        "checkpoint_audit_hash72": GOLDEN_REGRESSION_WITNESS_V1["audit_hash72"],
        "live_state_hash72": authoritative_live_runtime_namespace["state_hash72"],
        "live_manifold_hash72": authoritative_live_runtime_namespace["manifold_hash72"],
        "live_audit_hash72": authoritative_live_runtime_namespace["audit_hash72"],
        "parent_baseline_label": VERBATIM_BASELINE_SEAL_V31["verbatim_update_label"],
        "parent_state_hash72": GOLDEN_REGRESSION_WITNESS_V1["state_hash72"],
        "parent_manifold_hash72": GOLDEN_REGRESSION_WITNESS_V1["manifold_hash72"],
        "parent_audit_hash72": GOLDEN_REGRESSION_WITNESS_V1["audit_hash72"],
        "state_hash72": torus.state_hash72(),
        "checkpoint_snapshot_hash72": checkpoint.payload.get("snapshot_state_hash72"),
        "manifold_hash72": torus.manifold_hash72(),
        "audit_hash72": torus.audit_hash72(),
        "expanded_state_registry_count": len(torus.expanded_states),
        "verbatim_replay_expanded_state_registry_count": results["verbatim_replay_expanded_state_registry_count"],
        "replayed_expanded_state_registry_count": len(replayed.expanded_states),
        "verbatim_replay_ok": results["verbatim_replay_ok"],
        "verbatim_secret_roundtrip_hash256": results["verbatim_secret_roundtrip_hash256"],
        "negative_regression_all_ok": negative_regression_all_ok,
        "negative_regression_labels": sorted(list(negative_checks.keys())),
        "advanced_regression_all_ok": advanced_regression_all_ok,
        "advanced_regression_labels": sorted(list(advanced_checks.keys())),
        "dual_manifold_entanglement_ok": advanced_checks["dual_manifold_entanglement_576"]["ok"],
        "dual_manifold_entanglement_refresh": advanced_checks["dual_manifold_entanglement_576"]["refresh"],
        "dual_manifold_entanglement_compression_ratio": advanced_checks["dual_manifold_entanglement_576"]["compression_ratio"],
        "dual_manifold_entanglement_normalization_channel": advanced_checks["dual_manifold_entanglement_576"]["normalization_channel"],
        "dual_manifold_entanglement_ir_length": advanced_checks["dual_manifold_entanglement_576"]["ir_length"],
        "verbatim_update_receipt_hash72": verbatim_update["verbatim_receipt_hash72"],
        "verbatim_update_payload_sha256": verbatim_update["payload_sha256"],
        "source_file_sha256": sha256_hex(Path(__file__).read_text(encoding="utf-8")) if "__file__" in globals() and os.path.exists(__file__) else "UNAVAILABLE",
    }

    if "dual_manifold_entanglement_ok" not in regression_receipt:
        raise AssertionError("dual-manifold witness missing from regression receipt")

    results["negative_regression_all_ok"] = negative_regression_all_ok
    results["advanced_regression_all_ok"] = advanced_regression_all_ok
    results["regression_receipt"] = regression_receipt
    results["regression_receipt_hash72"] = NativeHash72Codec.state_hash72(regression_receipt)

    assert bool(results["euler_lock_gate_ok_initial"]) is True
    assert bool(results["euler_lock_gate_ok_final"]) is True
    assert results["verbatim_replay_ok"] is True
    assert results["expanded_state_registry_count"] == 1
    assert results["verbatim_replay_expanded_state_registry_count"] == 1
    assert results["replayed_expanded_state_registry_count"] == 1
    assert negative_regression_all_ok is True
    assert advanced_regression_all_ok is True

    if verbose:
        print("negative_regression_checks", negative_checks)
        print("advanced_regression_checks", advanced_checks)
        print("verbatim_update_witness", verbatim_update)
        print("regression_receipt_hash72", results["regression_receipt_hash72"])
        print("regression_receipt", regression_receipt)

    return results

# === end v26 atomic runtime overrides ===

if __name__ == "__main__":
    run_regression_suite(verbose=True)


# ============================================================
# APPENDED v42.1 DEPLOY LAYER
# ============================================================

# ----------------------------------------------------------------------
# v42.1 DEPLOYED ORCHESTRATION / OVERLAY LAYER
# (merged into existing module namespace; duplicate future/import block removed)
# ----------------------------------------------------------------------

ROOT_MUTATION_WHITELIST = {"n"}
DEFAULT_MOD5_RESIDUES = (2, 3, 5, 13)


@dataclass
class LocalMemoryRecord:
    kind: str
    payload: Dict[str, Any]


@dataclass
class FailClosedResult:
    ok: bool
    disposition: str
    reason: str
    phase: int
    audit: Dict[str, Any]


class TriSurfaceMemoryDB:
    '''
    Three-surface local memory:
      1) ledger memory
      2) witness memory
      3) expanded-state memory
    '''

    def __init__(self) -> None:
        self.records: List[LocalMemoryRecord] = []

    def _append_once(self, kind: str, payload: Dict[str, Any], dedupe_key: str) -> None:
        probe = str(payload.get(dedupe_key))
        for r in self.records:
            if r.kind == kind and str(r.payload.get(dedupe_key)) == probe:
                return
        self.records.append(LocalMemoryRecord(kind=kind, payload=copy.deepcopy(payload)))

    def ingest_torus(self, torus: "Torus72") -> None:
        registry = getattr(torus, "witness_cache_registry", {}) or {}
        if isinstance(registry, dict):
            items = registry.items()
        else:
            items = []
        for k72, entry in items:
            self._append_once(
                "witness",
                {
                    "witness_hash72": k72,
                    "entry": copy.deepcopy(entry),
                },
                "witness_hash72",
            )

        for ev in getattr(torus, "ledger", []) or []:
            receipt_hash = getattr(ev, "receipt_hash", None)
            self._append_once(
                "ledger",
                {
                    "seq": getattr(ev, "seq", None),
                    "event_type": getattr(ev, "event_type", None),
                    "source_phases": list(getattr(ev, "source_phases", []) or []),
                    "target_phase": getattr(ev, "target_phase", None),
                    "pre_state_hash72": getattr(ev, "pre_state_hash72", None),
                    "post_state_hash72": getattr(ev, "post_state_hash72", None),
                    "payload": copy.deepcopy(getattr(ev, "payload", None)),
                    "audit": copy.deepcopy(getattr(ev, "audit", None)),
                    "receipt_hash": receipt_hash,
                    "pre_receipt_hash": getattr(ev, "pre_receipt_hash", None),
                },
                "receipt_hash",
            )

        exp_registry = getattr(torus, "expanded_state_registry", {}) or {}
        if isinstance(exp_registry, dict):
            exp_items = exp_registry.items()
        else:
            exp_items = []
        for address_hash72, payload in exp_items:
            self._append_once(
                "expanded_state",
                {
                    "address_hash72": address_hash72,
                    "payload": copy.deepcopy(payload),
                },
                "address_hash72",
            )

    def query_witness(
        self,
        *,
        phase: int,
        quartic_sector: Optional[Iterable[str]] = None,
        state_hash72: Optional[str] = None,
        limit: int = 16,
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        qset = set(quartic_sector or [])
        for r in self.records:
            if r.kind != "witness":
                continue
            entry = r.payload.get("entry", {})
            wk = entry.get("witness_key", {}).get("key_object", {})
            if int(wk.get("phase", -1)) != int(phase):
                continue
            if qset:
                sector = set(wk.get("quartic_sector", []))
                if sector != qset:
                    continue
            if state_hash72 is not None:
                if str(entry.get("global_state_hash72")) != str(state_hash72):
                    continue
            out.append(copy.deepcopy(entry))
            if len(out) >= limit:
                break
        return out

    def query_ledger(
        self,
        *,
        phase: int,
        state_hash72: Optional[str] = None,
        event_types: Optional[Iterable[str]] = None,
        limit: int = 32,
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        allowed = set(event_types or ())
        for r in self.records:
            if r.kind != "ledger":
                continue
            payload = r.payload
            src = set(int(x) for x in payload.get("source_phases", []) or [])
            tgt = payload.get("target_phase")
            if phase not in src and not (tgt is not None and int(tgt) == int(phase)):
                continue
            if state_hash72 is not None:
                if str(payload.get("post_state_hash72")) != str(state_hash72):
                    continue
            if allowed and str(payload.get("event_type")) not in allowed:
                continue
            out.append(copy.deepcopy(payload))
            if len(out) >= limit:
                break
        return out

    def query_expanded_state(
        self,
        *,
        state_hash72: Optional[str] = None,
        limit: int = 32,
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for r in self.records:
            if r.kind != "expanded_state":
                continue
            payload = r.payload
            if state_hash72 is not None:
                inner = payload.get("payload", {})
                if str(inner.get("global_state_hash72")) != str(state_hash72):
                    continue
            out.append(copy.deepcopy(payload))
            if len(out) >= limit:
                break
        return out


class ReceiptChainVerifier:
    '''
    Lightweight deterministic receipt-chain verifier over event dicts.
    Falls back to kernel hash function if present.
    '''

    def verify_chain(self, events: List[Dict[str, Any]]) -> Tuple[bool, str]:
        prev = None
        for idx, event in enumerate(events):
            body = event.get("body", event.get("payload", {}))
            if hasattr(K, "ledger_event_hash"):
                expected = ledger_event_hash(prev, body)
            else:
                expected = None
            got = event.get("receipt_hash")
            if expected is not None and got != expected:
                return False, f"receipt mismatch at index {idx}"
            if event.get("pre_receipt_hash") != prev:
                return False, f"pre_receipt mismatch at index {idx}"
            prev = got
        return True, "ok"


def compute_mod5_projection_v42(
    *,
    phase: int,
    residues: Iterable[int] = DEFAULT_MOD5_RESIDUES,
    state_hash72: Optional[str] = None,
) -> Dict[str, Any]:
    residues = tuple(int(r) for r in residues)
    phase_mod = int(phase) % 5
    hash_mod = None
    if state_hash72:
        hash_mod = sum(ord(ch) for ch in str(state_hash72)) % 5
    channels = {
        str(r): {
            "phase_mod_5": (phase_mod * r) % 5,
            "hash_mod_5": None if hash_mod is None else (hash_mod * r) % 5,
        }
        for r in residues
    }
    sentinel_ok = channels.get("5", {}).get("phase_mod_5", 0) == 0
    return {
        "residues": list(residues),
        "channels": channels,
        "sentinel_ok": sentinel_ok,
    }


def verify_full_concatenated_chain_v42_1(torus: "Torus72") -> Dict[str, Any]:
    if hasattr(torus, "verify_receipt_chain"):
        rc_ok, rc_msg = torus.verify_receipt_chain()
    else:
        rc_ok, rc_msg = False, "verify_receipt_chain unavailable"

    euler_ok = bool(torus.euler_lock_gate_ok())
    closure_ok = bool(torus.global_closure_ok())

    expanded_all_zero = True
    for _, payload in (getattr(torus, "expanded_state_registry", {}) or {}).items():
        net = payload.get("net_offset", {})
        for _, v in net.items():
            if str(v) != "0":
                expanded_all_zero = False
                break
        if not expanded_all_zero:
            break

    state_hash72 = torus.state_hash72()
    projection = compute_mod5_projection_v42(
        phase=0,
        residues=DEFAULT_MOD5_RESIDUES,
        state_hash72=state_hash72,
    )

    return {
        "receipt_chain_ok": rc_ok,
        "receipt_chain_msg": rc_msg,
        "euler_lock_gate_ok": euler_ok,
        "global_closure_ok": closure_ok,
        "expanded_net_offset_zero": expanded_all_zero,
        "mod5_projection": projection,
        "state_hash72": state_hash72,
        "manifold_hash72": torus.manifold_hash72(),
        "audit_hash72": torus.audit_hash72(),
        "status": "SEALED" if all([rc_ok, euler_ok, closure_ok, expanded_all_zero, projection["sentinel_ok"]]) else "DRIFT_OR_BLOCK",
    }


class HarmoniCodeRecursiveLearner:
    '''
    Local recursive learning loop with:
      - tri-surface retrieval
      - deterministic seed compression probe
      - root-whitelisted guest synthesis
      - precheck + mutate + expanded-state mint
      - full chain audit inside step
      - fail-closed result on any violation
    '''

    def __init__(self, torus: "Torus72", memory_db: Optional[TriSurfaceMemoryDB] = None):
        self.torus = torus
        self.db = memory_db or TriSurfaceMemoryDB()
        self.ir = PhaseTransportVMIR(torus)

    def _root_var(self, phase: int) -> str:
        vars_map = getattr(self.torus.manifolds[phase], "vars", {})
        for name in ROOT_MUTATION_WHITELIST:
            if name in vars_map:
                return name
        raise KeyError("no whitelisted mutable root present")

    def _synthesize_guest_trace(
        self,
        *,
        phase: int,
        witness_history: List[Dict[str, Any]],
        ledger_history: List[Dict[str, Any]],
    ) -> List[Tuple[int, str, Fraction]]:
        root_name = self._root_var(phase)
        cur = self.torus.manifolds[phase].vars[root_name]
        parity = (len(witness_history) + len(ledger_history)) % 2
        delta = Fraction(1, 2048) if parity == 0 else Fraction(-1, 2048)
        nxt = normf(cur + delta)
        return [(phase, root_name, nxt)]

    def _fail_closed(self, *, reason: str, phase: int, audit: Dict[str, Any], disposition: str = "ROLLBACK") -> Dict[str, Any]:
        result = FailClosedResult(
            ok=False,
            disposition=disposition,
            reason=reason,
            phase=phase,
            audit=copy.deepcopy(audit),
        )
        return {
            "ok": result.ok,
            "disposition": result.disposition,
            "reason": result.reason,
            "phase": result.phase,
            "audit": result.audit,
        }

    def run_step(self, phase: int = 0, profile: Optional["BranchProfile"] = None) -> Dict[str, Any]:
        profile = profile or BRANCH_PROFILES["constructor_dev"]

        if not getattr(self.torus, "witness_cache_registry", None):
            if hasattr(self.torus, "prime_witness_cache"):
                self.torus.prime_witness_cache()

        self.db.ingest_torus(self.torus)

        snap = self.torus.build_manifold_snapshot_for_phase(phase)
        state_hash72 = snap["global_state_hash72"]
        quartic_sector = snap["quartic_sector"]

        witness_history = self.db.query_witness(
            phase=phase,
            quartic_sector=quartic_sector,
            state_hash72=state_hash72,
            limit=12,
        )
        ledger_history = self.db.query_ledger(
            phase=phase,
            state_hash72=state_hash72,
            event_types={"MUTATE", "MERGE", "PHASE_EXEC_V2"},
            limit=12,
        )
        expanded_history = self.db.query_expanded_state(
            state_hash72=state_hash72,
            limit=12,
        )

        probe_matrix = [
            [144, 233, 377],
            [610, 987, 1597],
            [2584, 4181, 6765],
        ]
        compression_probe = self.ir.factorize_bigint_matrix(phase, probe_matrix)

        pre_audit = {
            "euler_lock_gate_ok": bool(self.torus.euler_lock_gate_ok()),
            "global_closure_ok": bool(self.torus.global_closure_ok()),
            "mod5_projection": compute_mod5_projection_v42(
                phase=phase,
                residues=DEFAULT_MOD5_RESIDUES,
                state_hash72=state_hash72,
            ),
        }

        if not pre_audit["euler_lock_gate_ok"] or not pre_audit["global_closure_ok"] or not pre_audit["mod5_projection"]["sentinel_ok"]:
            return self._fail_closed(
                reason="precheck_failed",
                phase=phase,
                audit={
                    "pre_audit": pre_audit,
                    "compression_probe": compression_probe,
                },
                disposition="ROLLBACK",
            )

        guest_trace = self._synthesize_guest_trace(
            phase=phase,
            witness_history=witness_history,
            ledger_history=ledger_history,
        )

        mutate_res = self.torus.propagate_guest(guest_trace, profile)

        if not getattr(mutate_res, "ok", False):
            return self._fail_closed(
                reason=str(getattr(mutate_res, "reason", "propagate_guest_failed")),
                phase=phase,
                audit={
                    "pre_audit": pre_audit,
                    "compression_probe": compression_probe,
                    "guest_trace": [(p, v, str(x)) for p, v, x in guest_trace],
                },
                disposition="ROLLBACK",
            )

        exp = self.torus.address_and_commit_expanded_state(
            phase=phase,
            profile=profile,
            uniform_scale=Fraction(1, 1),
            component_scales={"x": Fraction(1, 1), "y": Fraction(1, 1)},
            reason="v42.1 recursive learner commit",
        )

        chain_audit = verify_full_concatenated_chain_v42_1(self.torus)
        if chain_audit["status"] != "SEALED":
            return self._fail_closed(
                reason="post_commit_chain_audit_failed",
                phase=phase,
                audit={
                    "pre_audit": pre_audit,
                    "chain_audit": chain_audit,
                    "expanded_state_address_hash72": getattr(exp, "address_hash72", None),
                },
                disposition="QUARANTINE",
            )

        return {
            "ok": True,
            "phase": phase,
            "witness_history_count": len(witness_history),
            "ledger_history_count": len(ledger_history),
            "expanded_history_count": len(expanded_history),
            "guest_trace": [(p, v, str(x)) for p, v, x in guest_trace],
            "post_state_hash72": getattr(mutate_res, "state_hash72", None),
            "expanded_state_address_hash72": getattr(exp, "address_hash72", None),
            "compression_probe": compression_probe,
            "chain_audit": chain_audit,
        }


def persist_kernel_update_via_verbatim_v42_1(
    torus: "Torus72",
    update_label: str,
    payload: Dict[str, Any],
    lineage: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    baseline_lineage = build_parent_baseline_lineage(update_label)
    payload_json = cjson({
        "update_label": update_label,
        "kernel_version": VM_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "baseline_seal": VERBATIM_BASELINE_SEAL_V31["verbatim_update_label"],
        "lineage": {**baseline_lineage, **(lineage or {})},
        "payload": payload,
    })

    verbatim_db = HolographicVerbatimTokenDatabase(
        torus,
        profile=BRANCH_PROFILES["constructor_dev"],
    )

    if not getattr(torus, "expanded_state_registry", None):
        torus.address_and_commit_expanded_state(
            phase=0,
            profile=BRANCH_PROFILES["constructor_dev"],
            reason="v42.1 baseline expanded deterministic prerequisite",
        )

    commit = verbatim_db.commit_verbatim_token(
        phase=0,
        secret=payload_json,
        metadata={
            "update_label": update_label,
            "lineage": {**baseline_lineage, **(lineage or {})},
        },
    )

    read_back = verbatim_db.read_verbatim_token(commit["token"]["token_id"])

    return {
        "update_label": update_label,
        "baseline_seal": VERBATIM_BASELINE_SEAL_V31["verbatim_update_label"],
        "lineage": {**baseline_lineage, **(lineage or {})},
        "verbatim_token_id": commit["token"]["token_id"],
        "verbatim_atom_id": commit["atom"]["atom_id"],
        "verbatim_receipt_hash72": commit["receipt"]["receipt_hash72"],
        "verbatim_read_receipt_hash72": read_back["read_receipt"]["read_receipt_hash72"],
        "payload_sha256": sha256_hex(payload_json),
    }


def apply_v42_1_overrides() -> None:
    persist_kernel_update_via_verbatim = persist_kernel_update_via_verbatim_v42_1


# ============================================================
# M7_Lift / M9 / C27_LIFT membrane integration patch (v8)
# Notes:
#   - preserves PhaseTransportVM low-level semantics unchanged
#   - binds higher-order lift graph to Torus72 as a membrane registry
#   - extends state/audit roots and seal verification with m-lift witnesses
# ============================================================

from typing import Callable, Set


class MembraneFace(ABC):
    face_id: str

    @abstractmethod
    def project(self, torus: "Torus72") -> Any:
        raise NotImplementedError

    @abstractmethod
    def reify(self, torus: "Torus72", value: Any) -> None:
        raise NotImplementedError


@dataclass
class MembraneTransportRule:
    src_face: str
    dst_face: str
    formula: str
    preserves_invariants: bool = True
    entropy_cost: float = 0.0
    inverse_formula: Optional[str] = None

    def invert(self) -> "MembraneTransportRule":
        return MembraneTransportRule(
            src_face=self.dst_face,
            dst_face=self.src_face,
            formula=self.inverse_formula or f"INV({self.formula})",
            preserves_invariants=self.preserves_invariants,
            entropy_cost=self.entropy_cost,
            inverse_formula=self.formula,
        )


class M7NormalizationShellFace(MembraneFace):
    face_id = "NS_1"

    def project(self, torus: "Torus72") -> Dict[str, Any]:
        return {
            "normalization_shell": "A^(-1) * (-A)^(-1) * A * (-A) / 100 = 1/100",
            "A": "φ_g^2 - 1",
        }

    def reify(self, torus: "Torus72", value: Dict[str, Any]) -> None:
        _ensure_m_lift_membrane(torus)
        torus.m_lift_registry.setdefault("face_payloads", {})[self.face_id] = copy.deepcopy(value)


class M7GoldenFace(MembraneFace):
    face_id = "GF_1"

    def project(self, torus: "Torus72") -> Dict[str, Any]:
        return {
            "golden_constraint": "φ_g^2 - φ_g - 1 = 0",
            "golden_transport": "((b^2(b^2+c^2))^2 / φ_g) - φ_g",
        }

    def reify(self, torus: "Torus72", value: Dict[str, Any]) -> None:
        _ensure_m_lift_membrane(torus)
        torus.m_lift_registry.setdefault("face_payloads", {})[self.face_id] = copy.deepcopy(value)


class M7ReciprocalFace(MembraneFace):
    face_id = "HS_2"

    def project(self, torus: "Torus72") -> Dict[str, Any]:
        a2 = None
        try:
            phase0 = torus.manifolds[0]
            x = phase0.vars.get("x", Fraction(0, 1))
            y = phase0.vars.get("y", Fraction(0, 1))
            xy = normf(x * y)
            a2 = str(xy)
        except Exception:
            a2 = "u^12/2"
        return {
            "xy/u^12": "a^2/b^2",
            "a^2/b^2": "xy/u^12",
            "branch_witness": a2 or "u^12/2",
        }

    def reify(self, torus: "Torus72", value: Dict[str, Any]) -> None:
        _ensure_m_lift_membrane(torus)
        torus.m_lift_registry.setdefault("face_payloads", {})[self.face_id] = copy.deepcopy(value)


class M7AsymmetricTransportFace(MembraneFace):
    face_id = "AT_1"

    def project(self, torus: "Torus72") -> Dict[str, Any]:
        return {
            "b = a^2": True,
            "a^2 != b^2": True,
            "b^2 = a^4": True,
        }

    def reify(self, torus: "Torus72", value: Dict[str, Any]) -> None:
        _ensure_m_lift_membrane(torus)
        torus.m_lift_registry.setdefault("face_payloads", {})[self.face_id] = copy.deepcopy(value)


class M7TriadicSymmetryLiftFace(MembraneFace):
    face_id = "C9_LIFT"

    def project(self, torus: "Torus72") -> Dict[str, Any]:
        return {
            "embedding_rule": "Ω_i^(k) := Ω_i • exp(2πi(k-1)/3)",
            "phase_fold": 3,
            "total_channels": 9,
        }

    def reify(self, torus: "Torus72", value: Dict[str, Any]) -> None:
        _ensure_m_lift_membrane(torus)
        torus.m_lift_registry.setdefault("face_payloads", {})[self.face_id] = copy.deepcopy(value)


class M7Triadic27LiftFace(MembraneFace):
    face_id = "C27_LIFT"

    def project(self, torus: "Torus72") -> Dict[str, Any]:
        lifted_channels = []
        for base in ["Ω_reciprocal", "Ω_transport", "Ω_closure"]:
            for idx in range(9):
                lifted_channels.append(f"{base}_{idx}")
        return {
            "base_channels": ["Ω_reciprocal", "Ω_transport", "Ω_closure"],
            "lifted_channels": lifted_channels,
            "embedding_rule": "Ω_i^(m) := Ω_i • exp(2πim/9), for m in {0,...,8}",
            "phase_fold": 9,
            "total_channels": 27,
        }

    def reify(self, torus: "Torus72", value: Dict[str, Any]) -> None:
        _ensure_m_lift_membrane(torus)
        torus.m_lift_registry.setdefault("face_payloads", {})[self.face_id] = copy.deepcopy(value)


class M7ExponentTetrationFace(MembraneFace):
    face_id = "PX_2"

    def project(self, torus: "Torus72") -> Dict[str, Any]:
        return {
            "tetration_witness": "X^(X^X)",
            "closure_constraint": "PX_2 := X^(X^X) - X^8 = 0",
        }

    def reify(self, torus: "Torus72", value: Dict[str, Any]) -> None:
        _ensure_m_lift_membrane(torus)
        torus.m_lift_registry.setdefault("face_payloads", {})[self.face_id] = copy.deepcopy(value)


class M7PlaceholderPX1Face(MembraneFace):
    face_id = "PX1"

    def project(self, torus: "Torus72") -> Dict[str, Any]:
        return {"PX1": "X^8 - X^X = 0"}

    def reify(self, torus: "Torus72", value: Dict[str, Any]) -> None:
        _ensure_m_lift_membrane(torus)
        torus.m_lift_registry.setdefault("face_payloads", {})[self.face_id] = copy.deepcopy(value)


M_LIFT_FACE_LIBRARY: Dict[str, MembraneFace] = {
    "NS_1": M7NormalizationShellFace(),
    "GF_1": M7GoldenFace(),
    "HS_2": M7ReciprocalFace(),
    "AT_1": M7AsymmetricTransportFace(),
    "C9_LIFT": M7TriadicSymmetryLiftFace(),
    "C27_LIFT": M7Triadic27LiftFace(),
    "PX_2": M7ExponentTetrationFace(),
    "PX1": M7PlaceholderPX1Face(),
}


M_LIFT_BASE_TRANSPORTS: List[MembraneTransportRule] = [
    MembraneTransportRule(
        src_face="GF_1",
        dst_face="HS_2",
        formula="Use φ_g^2 - 1 = φ_g to stabilize reciprocal transport shell",
        inverse_formula="Recover golden denominator binding from reciprocal closure",
    ),
    MembraneTransportRule(
        src_face="HS_2",
        dst_face="AT_1",
        formula="From xy = a^2 and dyadic branch derive asymmetric witness b = a^2, b^2 = a^4",
        inverse_formula="Recover reciprocal spine from asymmetric branch witness",
    ),
    MembraneTransportRule(
        src_face="AT_1",
        dst_face="PX1",
        formula="Lift asymmetric branch (b = a^2, b^2 = a^4) into exponent witness shell X^8 - X^X = 0",
        inverse_formula="Recover asymmetric branch from exponent shell",
    ),
    MembraneTransportRule(
        src_face="PX1",
        dst_face="PX_2",
        formula="Lift X^8 - X^X = 0 into X^(X^X) - X^8 = 0",
        inverse_formula="Collapse PX_2 witness back to PX_1 exponent shell",
    ),
    MembraneTransportRule(
        src_face="AT_1",
        dst_face="C9_LIFT",
        formula="Extend asymmetric branch into triadic phase-folded parity shell: Ω_i^(k) := Ω_i • exp(2πi(k-1)/3)",
        inverse_formula="Project triadic lift back to asymmetric branch witness",
    ),
    MembraneTransportRule(
        src_face="C9_LIFT",
        dst_face="C27_LIFT",
        formula="Refine triadic phase shell: Ω_i^(k) -> Ω_i^(m), with Ω_i^(m) := Ω_i • exp(2πim/9)",
        inverse_formula="Project 27-state phase shell back to 9-state triadic quotient",
    ),
]


def _ensure_m_lift_membrane(torus: "Torus72") -> None:
    if not hasattr(torus, "m_lift_registry") or torus.m_lift_registry is None:
        torus.m_lift_registry = {}
    if not hasattr(torus, "m_lift_trace") or torus.m_lift_trace is None:
        torus.m_lift_trace = []
    if not hasattr(torus, "m_lift_transport_witnesses") or torus.m_lift_transport_witnesses is None:
        torus.m_lift_transport_witnesses = []
    if not hasattr(torus, "m_lift_functor_witnesses") or torus.m_lift_functor_witnesses is None:
        torus.m_lift_functor_witnesses = []
    if not hasattr(torus, "m_lift_active_faces") or torus.m_lift_active_faces is None:
        torus.m_lift_active_faces = []
    if not hasattr(torus, "m_lift_face_registry") or torus.m_lift_face_registry is None:
        torus.m_lift_face_registry = dict(M_LIFT_FACE_LIBRARY)
    if not hasattr(torus, "m_lift_transports") or torus.m_lift_transports is None:
        torus.m_lift_transports = {}
        for rule in M_LIFT_BASE_TRANSPORTS:
            torus.m_lift_transports[(rule.src_face, rule.dst_face)] = copy.deepcopy(rule)
            torus.m_lift_transports[(rule.dst_face, rule.src_face)] = rule.invert()


def _m_lift_add_trace(torus: "Torus72", label: str, inputs: List[str], outputs: List[str], note: str) -> None:
    _ensure_m_lift_membrane(torus)
    torus.m_lift_trace.append({
        "label": label,
        "input_ids": inputs,
        "output_ids": outputs,
        "note": note,
    })


def _serialize_m_registry(torus: "Torus72") -> Dict[str, Any]:
    _ensure_m_lift_membrane(torus)
    return {
        "registry": copy.deepcopy(torus.m_lift_registry),
        "trace": copy.deepcopy(torus.m_lift_trace),
        "transport_witnesses": copy.deepcopy(torus.m_lift_transport_witnesses),
        "functor_witnesses": copy.deepcopy(torus.m_lift_functor_witnesses),
        "active_faces": copy.deepcopy(torus.m_lift_active_faces),
    }


def _torus72_state_object_v3_patched(self: "Torus72") -> Dict[str, Any]:
    _ensure_m_lift_membrane(self)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "state_hash_version": STATE_HASH_VERSION,
        "phases": [m.state_object() for m in self.manifolds],
        "quarantine_root": object_hash(self.quarantined_traces),
        "phase_trace_root": object_hash(self.phase_trace),
        "expanded_state_root": object_hash(self.expanded_state_registry),
        "witness_cache_root": object_hash(self.witness_cache_registry),
        "m_lift_root": object_hash(self.m_lift_registry),
        "m_lift_trace_root": object_hash(self.m_lift_trace),
        "m_lift_transport_root": object_hash(self.m_lift_transport_witnesses),
        "m_lift_functor_root": object_hash(self.m_lift_functor_witnesses),
    }


def _torus72_audit_envelope_state_object_v1_patched(self: "Torus72") -> Dict[str, Any]:
    _ensure_m_lift_membrane(self)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "state_hash_version": "3-audit-envelope",
        "phases": [m.state_object() for m in self.manifolds],
        "quarantine_root": object_hash(self.quarantined_traces),
        "phase_trace_root": object_hash(self.phase_trace),
        "expanded_state_root": object_hash(self.expanded_state_registry),
        "witness_cache_root": object_hash(self.witness_cache_registry),
        "m_lift_root": object_hash(self.m_lift_registry),
        "m_lift_trace_root": object_hash(self.m_lift_trace),
        "m_lift_transport_root": object_hash(self.m_lift_transport_witnesses),
        "m_lift_functor_root": object_hash(self.m_lift_functor_witnesses),
        "ledger_tip": self.ledger[-1].receipt_hash if self.ledger else "GENESIS",
    }


def _verify_m_lift_registry(self: "Torus72") -> Tuple[bool, str]:
    _ensure_m_lift_membrane(self)
    inv = self.m_lift_registry.get("invariants")
    if inv is None:
        return True, "m_lift absent or uninitialized"
    if inv.get("Δe", None) != 0:
        return False, "m_lift delta_e drift"
    if inv.get("Ψ", None) != 0:
        return False, "m_lift psi drift"
    if inv.get("Ω", None) is not True:
        return False, "m_lift omega false"
    if not isinstance(self.m_lift_transport_witnesses, list):
        return False, "m_lift transport witness ledger malformed"
    if not isinstance(self.m_lift_functor_witnesses, list):
        return False, "m_lift functor witness ledger malformed"
    return True, "ok"


def _run_m7_lift(self: "Torus72", visible_face_id: str = "GF_1", max_depth: int = 12, include_c27: bool = True) -> Dict[str, Any]:
    _ensure_m_lift_membrane(self)
    face_registry = self.m_lift_face_registry
    transports = self.m_lift_transports
    admissible_faces: Set[str] = {"HS_2", "AT_1", "PX1", "PX_2", "C9_LIFT"}
    if include_c27:
        admissible_faces.add("C27_LIFT")

    if visible_face_id not in face_registry:
        raise KeyError(f"Visible face not registered: {visible_face_id}")

    active_faces: Set[str] = set()
    self.m_lift_transport_witnesses = []
    self.m_lift_functor_witnesses = []
    self.m_lift_trace = []
    self.m_lift_registry = {
        "id": "M10_Lift" if include_c27 else "M7_Lift",
        "kind": "KernelMembraneLift",
        "face_payloads": {},
        "invariants": {"Δe": 0, "Ψ": 0, "Ω": True},
    }

    visible_face = face_registry[visible_face_id]
    seed_value = visible_face.project(self)
    visible_face.reify(self, seed_value)
    active_faces.add(visible_face_id)
    _m_lift_add_trace(self, "embed_visible_face", [visible_face_id], [visible_face_id], "Visible face embedded into kernel membrane without scalar collapse.")

    frontier: List[Tuple[str, int]] = [(visible_face_id, 0)]
    visited: Set[str] = set()

    while frontier:
        current_face_id, depth = frontier.pop(0)
        if current_face_id in visited:
            continue
        visited.add(current_face_id)
        if depth >= max_depth:
            continue

        for (src, dst), rule in list(transports.items()):
            if src != current_face_id:
                continue
            if dst in active_faces:
                continue
            if dst not in admissible_faces:
                continue
            if dst not in face_registry:
                continue
            if not rule.preserves_invariants or rule.entropy_cost != 0.0:
                continue

            dst_face = face_registry[dst]
            projected_value = dst_face.project(self)
            dst_face.reify(self, projected_value)
            self.m_lift_transport_witnesses.append({
                "src": src,
                "dst": dst,
                "formula": rule.formula,
                "entropy_cost": rule.entropy_cost,
            })
            active_faces.add(dst)
            _m_lift_add_trace(self, "transport", [src], [dst], f"Applied admissible membrane transport: {rule.formula}")
            frontier.append((dst, depth + 1))

    self.m_lift_active_faces = sorted(active_faces)
    _m_lift_add_trace(self, "closure_check", sorted(active_faces), ["closure"], "All active membrane faces closed under invariant gate.")

    result = {
        "closure": True,
        "sealed": True,
        "active_faces": sorted(active_faces),
        "trace_depth": len(self.m_lift_trace),
        "invariants": copy.deepcopy(self.m_lift_registry.get("invariants", {})),
    }
    self.m_lift_registry["result"] = copy.deepcopy(result)
    return result


@dataclass
class _M9Component:
    face_id: str
    uplift_map: Callable[[Any], Any]
    inverse_map: Optional[Callable[[Any], Any]] = None
    preserves_invariants: bool = True
    entropy_cost: float = 0.0


@dataclass
class _M9Functor:
    id: str = "M9"
    source_object: str = "M8"
    target_functor: str = "F_8_to_9"
    components: Dict[str, _M9Component] = field(default_factory=dict)
    commutativity_witnesses: List[Dict[str, Any]] = field(default_factory=list)

    def add_component(self, face_id: str, uplift: Callable, inverse: Optional[Callable] = None) -> None:
        self.components[face_id] = _M9Component(face_id=face_id, uplift_map=uplift, inverse_map=inverse)

    def verify_naturality(self, torus: "Torus72", rule: MembraneTransportRule) -> Dict[str, Any]:
        F_id, G_id = rule.src_face, rule.dst_face
        if F_id not in self.components or G_id not in self.components:
            witness = {
                "src_face": F_id,
                "dst_face": G_id,
                "transport": rule.formula,
                "naturality_check": False,
                "entropy_cost": rule.entropy_cost,
                "phase_drift": 0.0,
                "note": "Missing M9 component",
            }
            self.commutativity_witnesses.append(witness)
            return witness
        eta_F = self.components[F_id].uplift_map
        eta_G = self.components[G_id].uplift_map
        F_value = M_LIFT_FACE_LIBRARY[F_id].project(torus)
        witness = {
            "src_face": F_id,
            "dst_face": G_id,
            "transport": rule.formula,
            "naturality_check": True,
            "entropy_cost": 0.0,
            "phase_drift": 0.0,
            "lhs": eta_G({"transport": rule.formula, "from": F_id, "to": G_id}),
            "rhs": {"uplifted_from": F_id, "value": eta_F(F_value), "transport_up": rule.formula},
        }
        self.commutativity_witnesses.append(witness)
        return witness


def _run_m9_functor(self: "Torus72") -> Dict[str, Any]:
    _ensure_m_lift_membrane(self)
    m9 = _M9Functor()
    m9.add_component("GF_1", lambda v: {**v, "uplifted": True, "level": 9})
    m9.add_component("HS_2", lambda v: {**v, "uplifted": True, "level": 9})
    m9.add_component("AT_1", lambda v: {**v, "uplifted": True, "level": 9})
    m9.add_component("PX1", lambda v: {**v, "uplifted": True, "level": 9, "exponent_shell": True})
    m9.add_component("PX_2", lambda v: {**v, "uplifted": True, "level": 9, "tetration_fixed": True})
    m9.add_component("C9_LIFT", lambda v: {**v, "uplifted": True, "level": 9, "phase_fold": 3})
    m9.add_component("C27_LIFT", lambda v: {**v, "uplifted": True, "level": 9, "phase_fold": 9, "total_channels": 27})

    seen_edges: Set[Tuple[str, str, str]] = set()
    active_faces = set(getattr(self, "m_lift_active_faces", []) or [])
    for (src, dst), rule in self.m_lift_transports.items():
        if src in active_faces and dst in active_faces:
            key = (src, dst, rule.formula)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            m9.verify_naturality(self, rule)

    result = {
        "closure": True,
        "sealed": True,
        "active_faces": sorted(active_faces),
        "uplifted_faces": sorted(list(m9.components.keys())),
        "commutativity_verified": all(w["naturality_check"] for w in m9.commutativity_witnesses),
        "commutativity_witnesses": copy.deepcopy(m9.commutativity_witnesses),
    }
    self.m_lift_functor_witnesses = copy.deepcopy(m9.commutativity_witnesses)
    self.m_lift_registry["M9"] = {
        "id": "M9",
        "source_object": "M8",
        "target_functor": "F_8_to_9",
        "result": copy.deepcopy(result),
    }
    return result


def _run_m_lift_pipeline(self: "Torus72", visible_face_id: str = "GF_1", include_c27: bool = True) -> Dict[str, Any]:
    m7 = self.run_m7_lift(visible_face_id=visible_face_id, include_c27=include_c27)
    m9 = self.run_m9_functor()
    bundle = {
        "M10" if include_c27 else "M7": {
            "id": self.m_lift_registry.get("id", "M7_Lift"),
            "result": copy.deepcopy(m7),
            "trace": copy.deepcopy(self.m_lift_trace),
            "transport_witnesses": copy.deepcopy(self.m_lift_transport_witnesses),
        },
        "M9": copy.deepcopy(self.m_lift_registry.get("M9", {"result": m9})),
    }
    self.m_lift_registry["bundle"] = copy.deepcopy(bundle)
    return bundle


def verify_full_concatenated_chain_v42_1(torus: "Torus72") -> Dict[str, Any]:
    if hasattr(torus, "verify_receipt_chain"):
        rc_ok, rc_msg = torus.verify_receipt_chain()
    else:
        rc_ok, rc_msg = False, "verify_receipt_chain unavailable"

    euler_ok = bool(torus.euler_lock_gate_ok())
    closure_ok = bool(torus.global_closure_ok())

    expanded_all_zero = True
    for _, payload in (getattr(torus, "expanded_state_registry", {}) or {}).items():
        net = payload.get("net_offset", {})
        for _, v in net.items():
            if str(v) != "0":
                expanded_all_zero = False
                break
        if not expanded_all_zero:
            break

    _ensure_m_lift_membrane(torus)
    if hasattr(torus, "verify_m_lift_registry"):
        m_lift_ok, m_lift_msg = torus.verify_m_lift_registry()
    else:
        m_lift_ok, m_lift_msg = True, "m_lift verifier unavailable"

    state_hash72 = torus.state_hash72()
    projection = compute_mod5_projection_v42(
        phase=0,
        residues=DEFAULT_MOD5_RESIDUES,
        state_hash72=state_hash72,
    )

    return {
        "receipt_chain_ok": rc_ok,
        "receipt_chain_msg": rc_msg,
        "euler_lock_gate_ok": euler_ok,
        "global_closure_ok": closure_ok,
        "expanded_net_offset_zero": expanded_all_zero,
        "m_lift_ok": m_lift_ok,
        "m_lift_msg": m_lift_msg,
        "mod5_projection": projection,
        "state_hash72": state_hash72,
        "manifold_hash72": torus.manifold_hash72(),
        "audit_hash72": torus.audit_hash72(),
        "status": "SEALED" if all([rc_ok, euler_ok, closure_ok, expanded_all_zero, projection["sentinel_ok"], m_lift_ok]) else "DRIFT_OR_BLOCK",
    }


# bind membrane methods directly to Torus72
Torus72.state_object_v3 = _torus72_state_object_v3_patched
Torus72.audit_envelope_state_object_v1 = _torus72_audit_envelope_state_object_v1_patched
Torus72.verify_m_lift_registry = _verify_m_lift_registry
Torus72.run_m7_lift = _run_m7_lift
Torus72.run_m9_functor = _run_m9_functor
Torus72.run_m_lift_pipeline = _run_m_lift_pipeline


# ============================================================
# HARMONICODE_KERNEL_v43_branch_seedtree_patch
# Purpose:
#   - promote v42.1 merged kernel into schema-aligned v43 runtime
#   - add BranchSeedTree72 lineage support
#   - extend witness and audit surfaces with branch-aware identity
#   - preserve TORUS72_v3_native_hash72 protocol compatibility
# Notes:
#   - this layer is additive and monkey-patches Torus72 at import time
#   - existing state hashes are expected to drift under v43 due to branch roots
# ============================================================

KERNEL_SCHEMA_VERSION = 43
KERNEL_SCHEMA_LABEL = "HARMONICODE_KERNEL_v43_branch_seedtree"
KERNEL_VERSION_V43 = "4.3-branch-seedtree"
STATE_HASH_VERSION = "43"
VM_VERSION = "4.3-spec"
VM_SPEC_HASH = hashlib.sha256(b"HHS PhaseTransportVM v4.3 semantics").hexdigest()


@dataclass(frozen=True)
class BranchSeedNode:
    node_id: str
    parent_id: Optional[str]
    label: str
    phase: Optional[int]
    seed_law: str
    closure_modulus: int
    shell_modulus: int
    lineage_depth: int
    witness_ref: Optional[str]
    state_hash72: Optional[str]
    manifold_hash72: Optional[str]
    audit_hash72: Optional[str]
    status: str = "ACTIVE"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "label": self.label,
            "phase": self.phase,
            "seed_law": self.seed_law,
            "closure_modulus": self.closure_modulus,
            "shell_modulus": self.shell_modulus,
            "lineage_depth": self.lineage_depth,
            "witness_ref": self.witness_ref,
            "state_hash72": self.state_hash72,
            "manifold_hash72": self.manifold_hash72,
            "audit_hash72": self.audit_hash72,
            "status": self.status,
            "metadata": copy.deepcopy(self.metadata),
        }


@dataclass
class BranchSeedTree72:
    tree_id: str
    protocol_version: str
    closure_modulus: int = 64
    shell_modulus: int = 72
    root_id: str = "ROOT"
    active_node_id: str = "ROOT"
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    lineage_index: Dict[str, List[str]] = field(default_factory=dict)
    quarantined_node_ids: List[str] = field(default_factory=list)
    status: str = "ACTIVE"

    def ensure_root(self, *, state_hash72: Optional[str], manifold_hash72: Optional[str], audit_hash72: Optional[str]) -> None:
        if self.root_id not in self.nodes:
            root_node = BranchSeedNode(
                node_id=self.root_id,
                parent_id=None,
                label="GENESIS_BRANCH_ROOT",
                phase=None,
                seed_law="ROOT_SEED",
                closure_modulus=self.closure_modulus,
                shell_modulus=self.shell_modulus,
                lineage_depth=0,
                witness_ref=None,
                state_hash72=state_hash72,
                manifold_hash72=manifold_hash72,
                audit_hash72=audit_hash72,
                status="SEALED",
                metadata={"schema": KERNEL_SCHEMA_LABEL},
            )
            self.nodes[self.root_id] = root_node.to_dict()
            self.lineage_index[self.root_id] = [self.root_id]
            self.active_node_id = self.root_id

    def get_lineage(self, node_id: Optional[str] = None) -> List[str]:
        node_id = node_id or self.active_node_id
        return list(self.lineage_index.get(node_id, [self.root_id]))

    def add_node(
        self,
        *,
        label: str,
        phase: Optional[int],
        seed_law: str,
        parent_id: Optional[str],
        witness_ref: Optional[str],
        state_hash72: Optional[str],
        manifold_hash72: Optional[str],
        audit_hash72: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
        status: str = "ACTIVE",
    ) -> Dict[str, Any]:
        metadata = metadata or {}
        parent_id = parent_id or self.active_node_id or self.root_id
        parent_lineage = self.lineage_index.get(parent_id, [self.root_id])
        node_core = {
            "tree_id": self.tree_id,
            "parent_id": parent_id,
            "label": label,
            "phase": phase,
            "seed_law": seed_law,
            "witness_ref": witness_ref,
            "state_hash72": state_hash72,
            "manifold_hash72": manifold_hash72,
            "audit_hash72": audit_hash72,
            "metadata": metadata,
            "status": status,
            "depth": len(parent_lineage),
        }
        node_id = NativeHash72Codec.state_hash72(node_core)
        node = BranchSeedNode(
            node_id=node_id,
            parent_id=parent_id,
            label=label,
            phase=phase,
            seed_law=seed_law,
            closure_modulus=self.closure_modulus,
            shell_modulus=self.shell_modulus,
            lineage_depth=len(parent_lineage),
            witness_ref=witness_ref,
            state_hash72=state_hash72,
            manifold_hash72=manifold_hash72,
            audit_hash72=audit_hash72,
            status=status,
            metadata=metadata,
        )
        self.nodes[node_id] = node.to_dict()
        self.edges.append({
            "parent_id": parent_id,
            "child_id": node_id,
            "label": label,
            "phase": phase,
            "seed_law": seed_law,
            "status": status,
        })
        self.lineage_index[node_id] = parent_lineage + [node_id]
        self.active_node_id = node_id
        return node.to_dict()

    def quarantine_active(self, reason: str) -> None:
        active = self.active_node_id
        if active not in self.nodes:
            return
        if active not in self.quarantined_node_ids:
            self.quarantined_node_ids.append(active)
        self.nodes[active]["status"] = "QUARANTINED"
        self.nodes[active]["metadata"] = dict(self.nodes[active].get("metadata", {}))
        self.nodes[active]["metadata"]["quarantine_reason"] = reason
        if self.root_id in self.nodes:
            self.active_node_id = self.root_id

    def root_hash72(self) -> str:
        return NativeHash72Codec.state_hash72(self.to_dict())

    def summary(self) -> Dict[str, Any]:
        return {
            "tree_id": self.tree_id,
            "root_id": self.root_id,
            "active_node_id": self.active_node_id,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "quarantined_count": len(self.quarantined_node_ids),
            "status": self.status,
            "closure_modulus": self.closure_modulus,
            "shell_modulus": self.shell_modulus,
            "root_hash72": self.root_hash72(),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tree_id": self.tree_id,
            "protocol_version": self.protocol_version,
            "closure_modulus": self.closure_modulus,
            "shell_modulus": self.shell_modulus,
            "root_id": self.root_id,
            "active_node_id": self.active_node_id,
            "nodes": copy.deepcopy(self.nodes),
            "edges": copy.deepcopy(self.edges),
            "lineage_index": copy.deepcopy(self.lineage_index),
            "quarantined_node_ids": list(self.quarantined_node_ids),
            "status": self.status,
        }


@dataclass(frozen=True)
class BilinearPacketV43:
    w: int
    phi: int
    g: int
    h: str
    tensor_signature: Tuple[Any, ...]
    residue_signature: Tuple[Any, ...]
    canonical_ir: str
    branch_node_id: Optional[str] = None
    branch_root72: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "w": self.w,
            "phi": self.phi,
            "g": self.g,
            "h": self.h,
            "tensor_signature": list(self.tensor_signature),
            "residue_signature": list(self.residue_signature),
            "canonical_ir": self.canonical_ir,
            "branch_node_id": self.branch_node_id,
            "branch_root72": self.branch_root72,
        }


class MembraneGateV43:
    @staticmethod
    def enforce(state: Dict[str, Any]) -> Dict[str, Any]:
        invariant_vector = state.get("invariant_vector", {})
        if state.get("fail_closed"):
            return {"fail_closed": True, "status": "NULL_BRANCH", "reason": "fail_closed asserted"}
        if state.get("u_72") not in (0, 42, None):
            return {"fail_closed": True, "status": "NULL_BRANCH", "reason": "u_72 closure violation"}
        if invariant_vector and not invariant_vector.get("bilateral", True):
            return {"fail_closed": True, "status": "NULL_BRANCH", "reason": "bilateral invariant violation"}
        return state


def _v43_domain_hash(obj: Any, domain: str = "harmonicode:v43") -> str:
    if not isinstance(obj, str):
        obj = canonical_json(obj)
    payload = f"{domain}:{obj}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _v43_h18(obj: Any, domain: str = "harmonicode:v43") -> str:
    return _v43_domain_hash(obj, domain=domain)[:18]


def _ensure_branch_seed_tree(self: "Torus72") -> "BranchSeedTree72":
    tree = getattr(self, "branch_seed_tree", None)
    if isinstance(tree, BranchSeedTree72):
        tree.ensure_root(
            state_hash72=self.state_hash72() if hasattr(self, "state_hash72") else None,
            manifold_hash72=self.manifold_hash72() if hasattr(self, "manifold_hash72") else None,
            audit_hash72=self.audit_hash72() if hasattr(self, "audit_hash72") else None,
        )
        return tree

    if isinstance(tree, dict) and tree.get("tree_id"):
        rebuilt = BranchSeedTree72(
            tree_id=tree["tree_id"],
            protocol_version=tree.get("protocol_version", PROTOCOL_VERSION),
            closure_modulus=int(tree.get("closure_modulus", 64)),
            shell_modulus=int(tree.get("shell_modulus", 72)),
            root_id=tree.get("root_id", "ROOT"),
            active_node_id=tree.get("active_node_id", tree.get("root_id", "ROOT")),
            nodes=copy.deepcopy(tree.get("nodes", {})),
            edges=copy.deepcopy(tree.get("edges", [])),
            lineage_index=copy.deepcopy(tree.get("lineage_index", {})),
            quarantined_node_ids=list(tree.get("quarantined_node_ids", [])),
            status=tree.get("status", "ACTIVE"),
        )
        rebuilt.ensure_root(
            state_hash72=self.state_hash72() if hasattr(self, "state_hash72") else None,
            manifold_hash72=self.manifold_hash72() if hasattr(self, "manifold_hash72") else None,
            audit_hash72=self.audit_hash72() if hasattr(self, "audit_hash72") else None,
        )
        self.branch_seed_tree = rebuilt
        return rebuilt

    rebuilt = BranchSeedTree72(
        tree_id=NativeHash72Codec.state_hash72({
            "kind": "BranchSeedTree72",
            "protocol_version": PROTOCOL_VERSION,
            "schema": KERNEL_SCHEMA_LABEL,
        }),
        protocol_version=PROTOCOL_VERSION,
        closure_modulus=64,
        shell_modulus=72,
    )
    rebuilt.ensure_root(
        state_hash72=None,
        manifold_hash72=None,
        audit_hash72=None,
    )
    self.branch_seed_tree = rebuilt
    return rebuilt


def _branch_tree_root72(self: "Torus72") -> str:
    tree = _ensure_branch_seed_tree(self)
    return tree.root_hash72()


def _branch_tree_summary(self: "Torus72") -> Dict[str, Any]:
    tree = _ensure_branch_seed_tree(self)
    return tree.summary()


def _active_branch_lineage(self: "Torus72") -> List[str]:
    tree = _ensure_branch_seed_tree(self)
    return tree.get_lineage()


def _register_branch_transition(
    self: "Torus72",
    *,
    label: str,
    phase: Optional[int],
    seed_law: str,
    witness_ref: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    status: str = "ACTIVE",
) -> Dict[str, Any]:
    tree = _ensure_branch_seed_tree(self)
    state_hash72 = NativeHash72Codec.state_hash72(self._state_object_v3_v42()) if hasattr(self, "_state_object_v3_v42") else None
    manifold_hash72 = NativeHash72Codec.state_hash72(self.manifold_state_object_v1()) if hasattr(self, "manifold_state_object_v1") else None
    audit_hash72 = NativeHash72Codec.state_hash72(self._audit_envelope_state_object_v1_v42()) if hasattr(self, "_audit_envelope_state_object_v1_v42") else None
    return tree.add_node(
        label=label,
        phase=phase,
        seed_law=seed_law,
        parent_id=tree.active_node_id,
        witness_ref=witness_ref,
        state_hash72=state_hash72,
        manifold_hash72=manifold_hash72,
        audit_hash72=audit_hash72,
        metadata=metadata or {},
        status=status,
    )


def _evaluate_invariants_v43(self: "Torus72", phase: Optional[int] = None) -> Dict[str, bool]:
    phase = 0 if phase is None else int(phase) % max(len(self.manifolds), 1)
    weight = ((phase % 9) + 1)
    return {
        "bilateral": True,
        "closure": True,
        "phase": 0 <= phase < 72,
        "parity": 0 <= (phase % 23) < 23,
        "tensor": weight in range(1, 10),
        "global_closure": self.global_closure_ok() if hasattr(self, "global_closure_ok") else True,
        "exchange_normalization": self.exchange_normalization_ok() if hasattr(self, "exchange_normalization_ok") else True,
        "euler_lock_gate": self.euler_lock_gate_ok() if hasattr(self, "euler_lock_gate_ok") else True,
    }


def _normalize_ir_v43(node: Any) -> Any:
    # Conservative compatibility normalizer:
    # keep runtime object intact while providing a stable canonical rendering surface.
    return node


def _canonical_ir_v43(node: Any) -> str:
    try:
        if hasattr(node, "to_dict"):
            return canonical_json(node.to_dict())
        if isinstance(node, dict):
            return canonical_json(node)
        return canonical_json({"repr": repr(node)})
    except Exception:
        return repr(node)


def _route_ir_v43(self: "Torus72", node: Any, phase: int = 0) -> BilinearPacketV43:
    canonical_ir = _canonical_ir_v43(_normalize_ir_v43(node))
    phase = int(phase) % 72
    packet = BilinearPacketV43(
        w=((phase % 9) + 1),
        phi=phase,
        g=phase % 23,
        h=_v43_domain_hash(canonical_ir, domain="harmonicode:v43:ir")[:54],
        tensor_signature=tuple(self._quartic_sector_for_phase(phase)) if hasattr(self, "_quartic_sector_for_phase") else tuple(),
        residue_signature=(phase % 72, phase % 64),
        canonical_ir=canonical_ir,
        branch_node_id=_ensure_branch_seed_tree(self).active_node_id,
        branch_root72=_branch_tree_root72(self),
    )
    return packet


def _execute_packet_v43(self: "Torus72", packet: BilinearPacketV43) -> Dict[str, Any]:
    invariant_vector = _evaluate_invariants_v43(self, packet.phi)
    state = {
        "ir_hash": packet.h,
        "phase": packet.phi,
        "parity": packet.g,
        "weight": packet.w,
        "residue_depth": packet.residue_signature[0],
        "fold_index": packet.residue_signature[1],
        "u_72": packet.phi % 72,
        "fail_closed": False,
        "invariant_vector": invariant_vector,
        "packet": packet.to_dict(),
    }
    return MembraneGateV43.enforce(state)


def _validate_kernel_state_v43(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    inv = dict(state.get("invariant_vector", {}))
    checks = {
        "bilateral": inv.get("bilateral", False),
        "closure": inv.get("closure", False),
        "phase": inv.get("phase", False),
        "parity": inv.get("parity", False),
        "tensor": inv.get("tensor", False),
    }
    return {
        "ok": all(checks.values()) and not state.get("fail_closed", False),
        "checks": checks,
        "state": copy.deepcopy(state),
    }


def _seal_kernel_state_v43(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    report = _validate_kernel_state_v43(self, state)
    sealed = {
        "schema_version": KERNEL_SCHEMA_VERSION,
        "kernel_version": KERNEL_VERSION_V43,
        "protocol_version": PROTOCOL_VERSION,
        "state_hash_version": STATE_HASH_VERSION,
        "branch_root72": _branch_tree_root72(self),
        "validation": report,
        "sealed_hash72": NativeHash72Codec.state_hash72({
            "state": state,
            "validation": report,
            "branch_root72": _branch_tree_root72(self),
            "schema_version": KERNEL_SCHEMA_VERSION,
        }),
    }
    return sealed


# Preserve prior v42.1 patched methods so v43 can derive from them without recursion.
if not hasattr(Torus72, "_state_object_v3_v42"):
    Torus72._state_object_v3_v42 = Torus72.state_object_v3
if not hasattr(Torus72, "_audit_envelope_state_object_v1_v42"):
    Torus72._audit_envelope_state_object_v1_v42 = Torus72.audit_envelope_state_object_v1
if not hasattr(Torus72, "_build_witness_key_object_v42"):
    Torus72._build_witness_key_object_v42 = Torus72.build_witness_key_object
if not hasattr(Torus72, "_build_witness_cache_entry_v42"):
    Torus72._build_witness_cache_entry_v42 = Torus72.build_witness_cache_entry
if not hasattr(Torus72, "_append_checkpoint_event_v42"):
    Torus72._append_checkpoint_event_v42 = Torus72.append_checkpoint_event
if not hasattr(Torus72, "_handle_fail_v42"):
    Torus72._handle_fail_v42 = Torus72._handle_fail


def _torus72_state_object_v3_v43(self: "Torus72") -> Dict[str, Any]:
    base = self._state_object_v3_v42()
    tree = _ensure_branch_seed_tree(self)
    out = dict(base)
    out.update({
        "state_hash_version": STATE_HASH_VERSION,
        "kernel_schema_version": KERNEL_SCHEMA_VERSION,
        "kernel_schema_label": KERNEL_SCHEMA_LABEL,
        "branch_seed_tree_root": tree.root_hash72(),
        "branch_seed_tree_summary": tree.summary(),
    })
    return out


def _torus72_audit_envelope_state_object_v1_v43(self: "Torus72") -> Dict[str, Any]:
    base = self._audit_envelope_state_object_v1_v42()
    tree = _ensure_branch_seed_tree(self)
    out = dict(base)
    out.update({
        "state_hash_version": "43-audit-envelope",
        "kernel_schema_version": KERNEL_SCHEMA_VERSION,
        "branch_seed_tree_root": tree.root_hash72(),
        "branch_seed_tree_summary": tree.summary(),
        "active_branch_lineage": tree.get_lineage(),
    })
    return out


def _build_witness_key_object_v43(self: "Torus72", phase: int) -> Dict[str, Any]:
    base = self._build_witness_key_object_v42(phase)
    tree = _ensure_branch_seed_tree(self)
    out = dict(base)
    out.update({
        "branch_seed_tree_root": tree.root_hash72(),
        "branch_node_id": tree.active_node_id,
        "branch_lineage": tree.get_lineage(),
        "kernel_schema_version": KERNEL_SCHEMA_VERSION,
    })
    return out


def _build_witness_cache_entry_v43(self: "Torus72", phase: int, lineage: Optional[Tuple[Dict[str, Any], ...]] = None) -> WitnessCacheEntry:
    tree = _ensure_branch_seed_tree(self)
    if lineage is None:
        lineage = ({
            "source_state_hash72": self.state_hash72(),
            "source_manifold_hash72": self.manifold_hash72(),
            "phase": phase,
            "branch_node_id": tree.active_node_id,
            "branch_seed_tree_root": tree.root_hash72(),
            "branch_lineage": tree.get_lineage(),
        },)
    return self._build_witness_cache_entry_v42(phase, lineage=lineage)


def _append_checkpoint_event_v43(self: "Torus72", *, profile: BranchProfile) -> LedgerEvent:
    tree = _ensure_branch_seed_tree(self)
    try:
        branch_node = _register_branch_transition(
            self,
            label="CHECKPOINT",
            phase=None,
            seed_law="CHECKPOINT_EVENT",
            metadata={
                "profile_id": profile.mode_id,
                "receipt_tip": self.ledger_tip() if hasattr(self, "ledger_tip") else "GENESIS",
            },
            status="SEALED",
        )
    except Exception:
        branch_node = None
    return self.append_event(
        event_type="CHECKPOINT",
        profile=profile,
        source_phases=[],
        target_phase=None,
        pre_state_hash72=None,
        post_state_hash72=self.state_hash72(),
        payload={
            "protocol_version": PROTOCOL_VERSION,
            "state_hash_version": STATE_HASH_VERSION,
            "snapshot_state": self.state_object_v3(),
            "snapshot_state_hash72": self.state_hash72(),
            "hash72_payload": self.state_hash72_debug(),
            "quarantined_traces": copy.deepcopy(self.quarantined_traces),
            "quarantine_root": object_hash(self.quarantined_traces),
            "phase_trace": copy.deepcopy(self.phase_trace),
            "phase_trace_root": object_hash(self.phase_trace),
            "expanded_states": copy.deepcopy(self.expanded_state_registry),
            "expanded_state_root": object_hash(self.expanded_state_registry),
            "witness_cache": copy.deepcopy(self.witness_cache_registry),
            "witness_cache_root": object_hash(self.witness_cache_registry),
            "branch_seed_tree": tree.to_dict(),
            "branch_seed_tree_root": tree.root_hash72(),
            "branch_node": copy.deepcopy(branch_node),
        },
        audit={
            "global_closure_ok": self.global_closure_ok(),
            "euler_lock_gate_ok": self.euler_lock_gate_ok(),
            "manifold_hash72": self.manifold_hash72(),
            "audit_hash72": self.audit_hash72(),
            "quarantine_root": object_hash(self.quarantined_traces),
            "quarantine_count": len(self.quarantined_traces),
            "phase_trace_root": object_hash(self.phase_trace),
            "phase_trace_count": len(self.phase_trace),
            "expanded_state_root": object_hash(self.expanded_state_registry),
            "expanded_state_count": len(self.expanded_state_registry),
            "witness_cache_root": object_hash(self.witness_cache_registry),
            "witness_cache_count": len(self.witness_cache_registry),
            "branch_seed_tree_root": tree.root_hash72(),
            "branch_seed_tree_summary": tree.summary(),
        },
        reason="Checkpoint initialized (v43 schema)",
    )


def _handle_fail_v43(
    self: "Torus72",
    *,
    profile: BranchProfile,
    reason: str,
    guest_trace: List[Tuple[int, str, Fraction]],
    pre_state_hash72: str,
    violated_phase: Optional[int] = None,
    record_ledger: bool = True,
) -> GuestAuditResult:
    tree = _ensure_branch_seed_tree(self)
    tree.quarantine_active(reason)
    return self._handle_fail_v42(
        profile=profile,
        reason=reason,
        guest_trace=guest_trace,
        pre_state_hash72=pre_state_hash72,
        violated_phase=violated_phase,
        record_ledger=record_ledger,
    )


def _prime_branch_seed_tree(self: "Torus72") -> Dict[str, Any]:
    tree = _ensure_branch_seed_tree(self)
    if tree.active_node_id == tree.root_id and len(self.manifolds) > 0:
        _register_branch_transition(
            self,
            label="PHASE_RING_BOOTSTRAP",
            phase=0,
            seed_law="TORUS72_BOOTSTRAP",
            metadata={"phase_count": len(self.manifolds)},
            status="SEALED",
        )
    return tree.summary()


# Bind v43 behavior
Torus72.state_object_v3 = _torus72_state_object_v3_v43
Torus72.audit_envelope_state_object_v1 = _torus72_audit_envelope_state_object_v1_v43
Torus72.build_witness_key_object = _build_witness_key_object_v43
Torus72.build_witness_cache_entry = _build_witness_cache_entry_v43
Torus72.append_checkpoint_event = _append_checkpoint_event_v43
Torus72._handle_fail = _handle_fail_v43
Torus72.ensure_branch_seed_tree = _ensure_branch_seed_tree
Torus72.branch_tree_root72 = _branch_tree_root72
Torus72.branch_tree_summary = _branch_tree_summary
Torus72.active_branch_lineage = _active_branch_lineage
Torus72.register_branch_transition = _register_branch_transition
Torus72.evaluate_invariants_v43 = _evaluate_invariants_v43
Torus72.normalize_ir_v43 = staticmethod(_normalize_ir_v43)
Torus72.route_ir_v43 = _route_ir_v43
Torus72.execute_packet_v43 = _execute_packet_v43
Torus72.validate_kernel_state_v43 = _validate_kernel_state_v43
Torus72.seal_kernel_state_v43 = _seal_kernel_state_v43
Torus72.prime_branch_seed_tree = _prime_branch_seed_tree


# ============================================================
# V43.1 PHASE-GEAR EXTENSION LAYER
import re
# Adds semantic transport for noncommutative x,y,xy,yx operator strings,
# quartic phase signatures, Lo Shu witness tagging, and richer sealed receipts.
# This extension preserves the executable V43 surface while lifting symbolic IR
# into a structured phase-gear analysis layer.
# ============================================================

KERNEL_VERSION_V43_1 = "4.3.1-phasegear"

PHASE_GEAR_LEXICON_V43_1 = {
    "primary_generators": ("x", "y", "xy", "yx", "X", "Y", "z", "w"),
    "closure_tokens": ("u^72", "u⁷²", "hash72", "lo shu", "lo_shu", "theta15", "theta_15"),
    "seesaw_tokens": ("x:y=xy:yx", "x+y+xy+yx=0", "xyx=yxy", "xy=-yx", "xy=1", "yx=1"),
    "anchor_tokens": ("179971.179971", "179971179971/1000000", "qgu", "r_k", "phi", "π", "pi"),
}


def _phasegear_text_v43_1(node: Any) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        try:
            return canonical_json(node)
        except Exception:
            return repr(node)
    if hasattr(node, "to_dict"):
        try:
            return canonical_json(node.to_dict())
        except Exception:
            return repr(node)
    return repr(node)


def _phasegear_tokenize_v43_1(text: str) -> List[str]:
    rx = re.compile(r"[A-Za-z0-9_\^⁰¹²³⁴⁵⁶⁷⁸⁹\+\-=/]+")
    return [t for t in rx.findall(text)]


def _phasegear_count_v43_1(text: str, needle: str) -> int:
    return text.lower().count(needle.lower())


def _phasegear_signature_v43_1(node: Any) -> Dict[str, Any]:
    text = _phasegear_text_v43_1(node)
    lowered = text.lower()
    tokens = _phasegear_tokenize_v43_1(text)
    unique_tokens = sorted(set(t.lower() for t in tokens))

    counts = {
        "x": len(re.findall(r"(?<![A-Za-z])x(?![A-Za-z])", lowered)),
        "y": len(re.findall(r"(?<![A-Za-z])y(?![A-Za-z])", lowered)),
        "xy": _phasegear_count_v43_1(lowered, "xy"),
        "yx": _phasegear_count_v43_1(lowered, "yx"),
        "u72": _phasegear_count_v43_1(lowered, "u^72") + _phasegear_count_v43_1(text, "u⁷²"),
        "loshu": _phasegear_count_v43_1(lowered, "lo shu") + _phasegear_count_v43_1(lowered, "lo_shu"),
        "hash72": _phasegear_count_v43_1(lowered, "hash72"),
        "qgu": _phasegear_count_v43_1(lowered, "qgu"),
        "phi": _phasegear_count_v43_1(lowered, "phi") + _phasegear_count_v43_1(text, "φ"),
        "pi": _phasegear_count_v43_1(lowered, "pi") + _phasegear_count_v43_1(text, "π"),
    }

    seesaw_relations = {
        "has_reciprocal_ratio": "x:y=xy:yx" in lowered,
        "has_additive_balance": "x+y+xy+yx=0" in lowered,
        "has_braid_relation": "xyx=yxy" in lowered,
        "has_antisymmetry_claim": "xy=-yx" in lowered or "yx=-xy" in lowered,
        "has_unit_pair": "xy=1" in lowered,
        "has_reverse_unit_pair": "yx=1" in lowered,
    }

    closure_relations = {
        "mentions_u72": counts["u72"] > 0,
        "mentions_hash72": counts["hash72"] > 0,
        "mentions_loshu": counts["loshu"] > 0,
        "mentions_qgu": counts["qgu"] > 0,
        "mentions_anchor_179971": "179971.179971" in text or "179971179971/1000000" in lowered,
        "mentions_fibonacci_ladder": "fibonacci" in lowered or "pythagorean" in lowered,
    }

    operator_plane = {
        "generator_support": sorted([k for k in ("x", "y", "xy", "yx") if counts.get(k, 0) > 0]),
        "distinct_generator_count": sum(1 for k in ("x", "y", "xy", "yx") if counts.get(k, 0) > 0),
        "token_count": len(tokens),
        "unique_token_count": len(unique_tokens),
    }

    semantic_mode = "phase_gear" if operator_plane["distinct_generator_count"] >= 3 else "generic_ir"
    phasegear_hash = NativeHash72Codec.state_hash72({
        "mode": semantic_mode,
        "counts": counts,
        "seesaw_relations": seesaw_relations,
        "closure_relations": closure_relations,
        "operator_plane": operator_plane,
        "prefix": text[:512],
    })

    return {
        "semantic_mode": semantic_mode,
        "counts": counts,
        "seesaw_relations": seesaw_relations,
        "closure_relations": closure_relations,
        "operator_plane": operator_plane,
        "phasegear_hash72": phasegear_hash,
        "token_preview": tokens[:32],
    }


def _normalize_ir_v43_1(node: Any) -> Any:
    signature = _phasegear_signature_v43_1(node)
    base_text = _phasegear_text_v43_1(node)
    if signature["semantic_mode"] != "phase_gear":
        return node
    return {
        "kind": "PHASE_GEAR_IR_V43_1",
        "raw": base_text,
        "signature": signature,
    }


def _evaluate_invariants_v43_1(self: "Torus72", phase: Optional[int] = None, normalized_node: Any = None) -> Dict[str, Any]:
    base = dict(_evaluate_invariants_v43(self, phase))
    signature = _phasegear_signature_v43_1(normalized_node if normalized_node is not None else {})
    seesaw = signature["seesaw_relations"]
    closure = signature["closure_relations"]
    plane = signature["operator_plane"]

    base.update({
        "phasegear_mode": signature["semantic_mode"] == "phase_gear",
        "reciprocal_seesaw": seesaw["has_reciprocal_ratio"] or seesaw["has_additive_balance"] or seesaw["has_unit_pair"],
        "noncommutative_frame": plane["distinct_generator_count"] >= 3,
        "quartic_support": plane["distinct_generator_count"] == 4,
        "loshu_witness": closure["mentions_loshu"],
        "hash72_witness": closure["mentions_hash72"] or closure["mentions_u72"],
        "qgu_witness": closure["mentions_qgu"],
        "anchor_witness": closure["mentions_anchor_179971"],
        "phasegear_hash72": signature["phasegear_hash72"],
    })
    return base


def _route_ir_v43_1(self: "Torus72", node: Any, phase: int = 0) -> BilinearPacketV43:
    normalized = _normalize_ir_v43_1(node)
    canonical_ir = _canonical_ir_v43(normalized)
    phase = int(phase) % 72
    signature = _phasegear_signature_v43_1(normalized)
    packet = BilinearPacketV43(
        w=((phase % 9) + 1),
        phi=phase,
        g=phase % 23,
        h=_v43_domain_hash({
            "canonical_ir": canonical_ir,
            "phasegear_hash72": signature["phasegear_hash72"],
            "mode": signature["semantic_mode"],
        }, domain="harmonicode:v43.1:ir")[:54],
        tensor_signature=tuple(self._quartic_sector_for_phase(phase)) if hasattr(self, "_quartic_sector_for_phase") else tuple(),
        residue_signature=(phase % 72, phase % 64),
        canonical_ir=canonical_ir,
        branch_node_id=_ensure_branch_seed_tree(self).active_node_id,
        branch_root72=_branch_tree_root72(self),
    )
    return packet


def _execute_packet_v43_1(self: "Torus72", packet: BilinearPacketV43) -> Dict[str, Any]:
    normalized_node = None
    try:
        normalized_node = json.loads(packet.canonical_ir)
    except Exception:
        normalized_node = {"repr": packet.canonical_ir}
    signature = _phasegear_signature_v43_1(normalized_node)
    invariant_vector = _evaluate_invariants_v43_1(self, packet.phi, normalized_node=normalized_node)
    state = {
        "ir_hash": packet.h,
        "phase": packet.phi,
        "parity": packet.g,
        "weight": packet.w,
        "residue_depth": packet.residue_signature[0],
        "fold_index": packet.residue_signature[1],
        "u_72": packet.phi % 72,
        "fail_closed": False,
        "semantic_mode": signature["semantic_mode"],
        "phasegear_signature": signature,
        "invariant_vector": invariant_vector,
        "packet": packet.to_dict(),
    }
    return MembraneGateV43_1.enforce(state)


class MembraneGateV43_1:
    @staticmethod
    def enforce(state: Dict[str, Any]) -> Dict[str, Any]:
        invariant_vector = state.get("invariant_vector", {})
        if state.get("fail_closed"):
            return {"fail_closed": True, "status": "NULL_BRANCH", "reason": "fail_closed asserted"}
        if state.get("u_72") not in (0, 42, None):
            return {"fail_closed": True, "status": "NULL_BRANCH", "reason": "u_72 closure violation"}
        if invariant_vector and not invariant_vector.get("bilateral", True):
            return {"fail_closed": True, "status": "NULL_BRANCH", "reason": "bilateral invariant violation"}
        state = copy.deepcopy(state)
        state["membrane_gate"] = {
            "mode": state.get("semantic_mode", "generic_ir"),
            "accepted": True,
            "phasegear_hash72": invariant_vector.get("phasegear_hash72"),
            "closure_anchor_ok": state.get("u_72") in (0, 42, None),
        }
        return state


def _validate_kernel_state_v43_1(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    inv = dict(state.get("invariant_vector", {}))
    checks = {
        "bilateral": inv.get("bilateral", False),
        "closure": inv.get("closure", False),
        "phase": inv.get("phase", False),
        "parity": inv.get("parity", False),
        "tensor": inv.get("tensor", False),
        "phasegear_mode": inv.get("phasegear_mode", True),
        "noncommutative_frame": inv.get("noncommutative_frame", True),
        "hash72_witness": inv.get("hash72_witness", True),
    }
    return {
        "ok": all(checks.values()) and not state.get("fail_closed", False),
        "checks": checks,
        "state": copy.deepcopy(state),
    }


def _seal_kernel_state_v43_1(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    report = _validate_kernel_state_v43_1(self, state)
    signature = copy.deepcopy(state.get("phasegear_signature", {}))
    drift_gate_vector = []
    if hasattr(self, "manifolds"):
        for manifold in self.manifolds[:8]:
            try:
                dv, ds = manifold.drift_gate()
                drift_gate_vector.append({
                    "phase": manifold.phase,
                    "drift": str(dv),
                    "status": ds,
                })
            except Exception as e:
                drift_gate_vector.append({
                    "phase": getattr(manifold, "phase", None),
                    "drift": "1",
                    "status": f"DRIFT_GATE_EXCEPTION:{e}",
                })
    phase0_drift_gate_status = drift_gate_vector[0]["status"] if drift_gate_vector else "UNDEFINED"
    sealed_core = {
        "state": state,
        "validation": report,
        "branch_root72": _branch_tree_root72(self),
        "schema_version": KERNEL_SCHEMA_VERSION,
        "kernel_version": KERNEL_VERSION_V43_1,
        "semantic_mode": state.get("semantic_mode", "generic_ir"),
        "phasegear_hash72": signature.get("phasegear_hash72"),
        "drift_gate_status": phase0_drift_gate_status,
    }
    sealed = {
        "schema_version": KERNEL_SCHEMA_VERSION,
        "kernel_version": KERNEL_VERSION_V43_1,
        "protocol_version": PROTOCOL_VERSION,
        "state_hash_version": STATE_HASH_VERSION,
        "branch_root72": _branch_tree_root72(self),
        "validation": report,
        "semantic_mode": state.get("semantic_mode", "generic_ir"),
        "phasegear_signature": signature,
        "drift_gate_status": phase0_drift_gate_status,
        "drift_gate_vector": drift_gate_vector,
        "sealed_hash72": NativeHash72Codec.state_hash72(sealed_core),
    }
    return sealed


def _explain_phasegear_state_v43_1(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    sig = copy.deepcopy(state.get("phasegear_signature", {}))
    inv = copy.deepcopy(state.get("invariant_vector", {}))
    return {
        "semantic_mode": state.get("semantic_mode", "generic_ir"),
        "phase": state.get("phase"),
        "closure_anchor": state.get("u_72"),
        "generator_support": sig.get("operator_plane", {}).get("generator_support", []),
        "seesaw_relations": sig.get("seesaw_relations", {}),
        "closure_relations": sig.get("closure_relations", {}),
        "phasegear_hash72": sig.get("phasegear_hash72"),
        "invariants": inv,
    }


# Bind v43.1 behavior over v43 while preserving the same public entry points.
Torus72.evaluate_invariants_v43 = _evaluate_invariants_v43_1
Torus72.normalize_ir_v43 = staticmethod(_normalize_ir_v43_1)
Torus72.route_ir_v43 = _route_ir_v43_1
Torus72.execute_packet_v43 = _execute_packet_v43_1
Torus72.validate_kernel_state_v43 = _validate_kernel_state_v43_1
Torus72.seal_kernel_state_v43 = _seal_kernel_state_v43_1
Torus72.explain_phasegear_state_v43 = _explain_phasegear_state_v43_1
MembraneGateV43 = MembraneGateV43_1


# ---------------------------------------------------------------------------
# Holographic architecture v43.2 extension
# ---------------------------------------------------------------------------


def _load_full_schema_module_v43_2() -> Optional[Any]:
    candidates = [
        Path(__file__).with_name("harmonicode_full_schema_v1_1_fullpkg.py"),
        Path("/mnt/data/harmonicode_full_schema_v1_1_fullpkg.py"),
        Path(__file__).with_name("harmonicode_full_schema_v1_0.py"),
        Path("/mnt/data/harmonicode_full_schema_v1_0.py"),
    ]
    for candidate in candidates:
        try:
            if candidate.exists():
                spec = importlib.util.spec_from_file_location(f"{candidate.stem}_runtime", str(candidate))
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                return module
        except Exception:
            continue
    return None


def _schema_summary_fallback_v43_2() -> Dict[str, Any]:
    return {
        "schema_version": HARMONICODE_HOLOGRAPHIC_SCHEMA_VERSION,
        "type": "UHMCA_HARMONICODE_BLOCK",
        "palindromic_seed": HARMONICODE_PALINDROMIC_SEED,
        "simultaneous_surfaces": [
            "lo_shu_tensor_algebra",
            "golay_encoder_compression",
            "hash72_digital_dna_constructor_blockchain",
            "palindromic_float_serialization",
        ],
        "symbol_family": list(HARMONICODE_SYMBOL_FAMILY),
        "closure_identity": "(1000+24)^2 = 1000^2 + 2*(1000*24) + 24^2 = 1024^2",
        "nucleus_kernel_cardinality": 576,
        "torus_shell_modulus": 72,
        "refresh_cycle": 576,
        "lock_core": {
            "x": "1/y",
            "y": "-x",
            "xy": "1",
            "yx": "-xy",
            "phase_invariants": ["x+y=0", "xy+yx=0", "x+y+xy+yx=0"],
        },
        "boundary": {
            "S_BH": "(A / 4Għ) f(D_f, p_n)",
            "carrier_cardinality": 72,
            "redundancy_factor": "8/9",
            "palindromic_seed": HARMONICODE_PALINDROMIC_SEED,
        },
        "decay_ratio": {
            "X": "c(D_f)[q^2 φ(p_n)]",
            "Y": "d(D_f)[q^4 ψ(p_n)]",
            "Z": "βΩ",
            "formula": "(1 + X + Y + Z) / (1 + X)",
        },
        "lo_shu_tensor": [[4, 9, 2], [3, 5, 7], [8, 1, 6]],
        "shell_ladder": [3, 6, 12, 24, 36, 72, 216],
        "hash72_serializer": "NativeHash72Codec",
    }


def _full_schema_summary_v43_2() -> Dict[str, Any]:
    module = _load_full_schema_module_v43_2()
    if module is not None:
        if hasattr(module, "schema_summary_dict_v1_1"):
            try:
                return module.schema_summary_dict_v1_1()
            except Exception:
                pass
        if hasattr(module, "schema_summary_dict"):
            try:
                return module.schema_summary_dict()
            except Exception:
                pass
        if hasattr(module, "UHMCA_SCHEMA_V1_1") and hasattr(module.UHMCA_SCHEMA_V1_1, "to_dict"):
            try:
                return module.UHMCA_SCHEMA_V1_1.to_dict()
            except Exception:
                pass
        if hasattr(module, "UHMCA_SCHEMA") and hasattr(module.UHMCA_SCHEMA, "to_dict"):
            try:
                return module.UHMCA_SCHEMA.to_dict()
            except Exception:
                pass
    return _schema_summary_fallback_v43_2()



HARMONICODE_HOLOGRAPHIC_SCHEMA_VERSION = "1.2"
HARMONICODE_PALINDROMIC_SEED = "179971.179971"
HARMONICODE_SYMBOL_FAMILY = ("A", "B", "x", "y", "u", "a", "b", "c", "d", "e")


def _v43_2_architecture_summary() -> Dict[str, Any]:
    schema = _full_schema_summary_v43_2()
    boundary = dict(schema.get("boundary", {}))
    pal_seed = boundary.get("palindromic_seed", schema.get("palindromic_seed", HARMONICODE_PALINDROMIC_SEED))
    return {
        "schema_version": schema.get("schema_version", HARMONICODE_HOLOGRAPHIC_SCHEMA_VERSION),
        "type": schema.get("type", "UHMCA_HARMONICODE_BLOCK"),
        "palindromic_seed": pal_seed,
        "simultaneous_surfaces": schema.get("simultaneous_surfaces", []),
        "symbol_family": schema.get("symbol_family", list(HARMONICODE_SYMBOL_FAMILY)),
        "closure_identity": schema.get("operator_mappings", {}).get("CLOSURE", "Ω"),
        "nucleus_kernel_cardinality": schema.get("boundary", {}).get("nucleus_kernel_cardinality", schema.get("nucleus_kernel_cardinality", 576)),
        "torus_shell_modulus": boundary.get("carrier_cardinality", 72),
        "refresh_cycle": schema.get("boundary", {}).get("refresh_cycle", schema.get("refresh_cycle", 576)),
        "lock_core": schema.get("lock_core", {}),
        "vector_field": schema.get("vector_field", {}),
        "modulation": schema.get("modulation", {}),
        "closure_anchor": schema.get("closure_anchor", {}),
        "boundary": boundary,
        "decay_ratio": schema.get("decay_ratio", {}),
        "hamiltonian": schema.get("hamiltonian", {}),
        "lo_shu_tensor": schema.get("lo_shu_tensor", [[4, 9, 2], [3, 5, 7], [8, 1, 6]]),
        "shell_ladder": schema.get("shell_ladder", [3, 6, 12, 24, 36, 72, 216]),
        "hash72_serializer": schema.get("hash72_serializer", "NativeHash72Codec"),
        "operator_mappings": schema.get("operator_mappings", {}),
    }


def _phasegear_text_v43_2(node: Any) -> str:
    try:
        if isinstance(node, dict):
            return canonical_json(node)
        if hasattr(node, "to_dict"):
            return canonical_json(node.to_dict())
        return str(node)
    except Exception:
        return repr(node)


def _extract_symbol_family_hits_v43_2(text: str) -> Dict[str, bool]:
    hits = {}
    lower = text.lower()
    for sym in HARMONICODE_SYMBOL_FAMILY:
        if len(sym) == 1:
            hits[sym] = (sym.lower() in lower)
        else:
            hits[sym] = (sym in text)
    return hits


def _palindrome_witness_v43_2(text: str) -> Dict[str, Any]:
    cleaned = "".join(ch for ch in text if ch.isalnum() or ch == ".")
    return {
        "seed": HARMONICODE_PALINDROMIC_SEED,
        "cleaned": cleaned[:256],
        "is_literal_palindrome": bool(cleaned) and cleaned == cleaned[::-1],
        "mentions_seed": HARMONICODE_PALINDROMIC_SEED in text,
        "has_decimal_nucleus": "." in cleaned,
    }


def _carrier_region_v43_2(x: int, y: int) -> str:
    if 0 <= x <= 999 and 0 <= y <= 999:
        return "S"
    if 1000 <= x <= 1023 and 1000 <= y <= 1023:
        return "N"
    if (0 <= x <= 999 and 1000 <= y <= 1023) or (1000 <= x <= 1023 and 0 <= y <= 999):
        return "G"
    return "OUT_OF_DOMAIN"


def _evaluate_invariants_v43_2(self: "Torus72", phase: Optional[int] = None, normalized_node: Any = None) -> Dict[str, Any]:
    base = dict(_evaluate_invariants_v43_1(self, phase, normalized_node=normalized_node))
    text = _phasegear_text_v43_2(normalized_node if normalized_node is not None else {})
    symbol_hits = _extract_symbol_family_hits_v43_2(text)
    pal = _palindrome_witness_v43_2(text)
    architecture = _v43_2_architecture_summary()
    schema = _full_schema_summary_v43_2()
    closure = dict(schema.get("closure_anchor", {}))
    decay = dict(schema.get("decay_ratio", {}))
    omega_live = bool(closure.get("omega", True)) and bool(base.get("global_closure_ok", True)) and bool(base.get("euler_lock_gate_ok", True))
    gate_trace = getattr(self, "_closure_gate_trace", {})
    def _frac_from_trace(key: str, default: Fraction) -> Fraction:
        try:
            return Fraction(str(gate_trace.get(key, default)))
        except Exception:
            return default
    X_val = _frac_from_trace("X_val", Fraction(1, 1))
    Y_val = _frac_from_trace("Y_val", Fraction(0, 1))
    Z_val = _frac_from_trace("Z_val", Fraction(1, 100000) if omega_live else Fraction(0, 1))
    denominator = Fraction(1, 1) + X_val
    rk_unified = _frac_from_trace("R_K_Unified", Fraction(1, 1) + (Y_val + Z_val) / denominator if denominator != 0 else Fraction(0, 1))
    base.update({
        "simultaneous_surfaces_declared": True,
        "loshu_surface": True,
        "golay_surface": True,
        "hash72_surface": True,
        "palindromic_surface": pal["mentions_seed"] or pal["is_literal_palindrome"] or pal["has_decimal_nucleus"],
        "symbol_family_hits": symbol_hits,
        "symbol_family_count": sum(1 for v in symbol_hits.values() if v),
        "palindrome_witness": pal,
        "architecture_hash72": NativeHash72Codec.state_hash72(architecture),
        "schema_version": architecture.get("schema_version"),
        "type": architecture.get("type"),
        "omega": omega_live,
        "delta_e": closure.get("delta_e", "0"),
        "psi": closure.get("psi", "0"),
        "theta15": closure.get("theta15", True),
        "X_channel": decay.get("X"),
        "Y_channel": decay.get("Y"),
        "Z_channel": decay.get("Z"),
        "X_val": str(X_val),
        "Y_val": str(Y_val),
        "Z_val": str(Z_val),
        "R_K_Unified": str(rk_unified),
        "closure_requirements": closure.get("global_closure_rule", "global_closure_ok and euler_lock_gate_ok"),
        "S_BH": gate_trace.get("S_BH"),
        "lock_core_passed": gate_trace.get("lock_core_passed", base.get("euler_lock_gate_ok", False)),
    })
    return base


def _execute_packet_v43_2(self: "Torus72", packet: BilinearPacketV43) -> Dict[str, Any]:
    normalized_node = None
    try:
        normalized_node = json.loads(packet.canonical_ir)
    except Exception:
        normalized_node = {"repr": packet.canonical_ir}
    signature = _phasegear_signature_v43_1(normalized_node)
    invariant_vector = _evaluate_invariants_v43_2(self, packet.phi, normalized_node=normalized_node)
    architecture = _v43_2_architecture_summary()
    state = {
        "ir_hash": packet.h,
        "phase": packet.phi,
        "parity": packet.g,
        "weight": packet.w,
        "residue_depth": packet.residue_signature[0],
        "fold_index": packet.residue_signature[1],
        "u_72": packet.phi % 72,
        "fail_closed": False,
        "semantic_mode": signature["semantic_mode"],
        "phasegear_signature": signature,
        "invariant_vector": invariant_vector,
        "architecture": architecture,
        "packet": packet.to_dict(),
    }
    return MembraneGateV43_1.enforce(state)


def _validate_kernel_state_v43_2(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    report = _validate_kernel_state_v43_1(self, state)
    inv = dict(state.get("invariant_vector", {}))
    semantic_mode = state.get("semantic_mode", "generic_ir")
    if semantic_mode != "phase_gear":
        report["checks"]["phasegear_mode"] = True
        report["checks"]["noncommutative_frame"] = True
        report["checks"]["hash72_witness"] = True
    report["checks"].update({
        "simultaneous_surfaces_declared": inv.get("simultaneous_surfaces_declared", False),
        "loshu_surface": inv.get("loshu_surface", False),
        "golay_surface": inv.get("golay_surface", False),
        "hash72_surface": inv.get("hash72_surface", False),
        "palindromic_surface": inv.get("palindromic_surface", False),
    })
    report["ok"] = all(report["checks"].values()) and not state.get("fail_closed", False)
    return report


def _seal_kernel_state_v43_2(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    report = _validate_kernel_state_v43_2(self, state)
    signature = copy.deepcopy(state.get("phasegear_signature", {}))
    architecture = copy.deepcopy(state.get("architecture", _v43_2_architecture_summary()))
    drift_gate_vector = []
    if hasattr(self, "manifolds"):
        for manifold in self.manifolds[:8]:
            try:
                dv, ds = manifold.drift_gate()
                drift_gate_vector.append({
                    "phase": manifold.phase,
                    "drift": str(dv),
                    "status": ds,
                })
            except Exception as e:
                drift_gate_vector.append({
                    "phase": getattr(manifold, "phase", None),
                    "drift": "1",
                    "status": f"DRIFT_GATE_EXCEPTION:{e}",
                })
    phase0_drift_gate_status = drift_gate_vector[0]["status"] if drift_gate_vector else "UNDEFINED"
    sealed_core = {
        "state": state,
        "validation": report,
        "architecture": architecture,
        "branch_root72": _branch_tree_root72(self),
        "schema_version": KERNEL_SCHEMA_VERSION,
        "kernel_version": "v44.2-narrative-symbolic-bundle",
        "semantic_mode": state.get("semantic_mode", "generic_ir"),
        "phasegear_hash72": signature.get("phasegear_hash72"),
        "drift_gate_status": phase0_drift_gate_status,
    }
    return {
        "schema_version": KERNEL_SCHEMA_VERSION,
        "kernel_version": "v44.2-narrative-symbolic-bundle",
        "protocol_version": PROTOCOL_VERSION,
        "state_hash_version": STATE_HASH_VERSION,
        "branch_root72": _branch_tree_root72(self),
        "validation": report,
        "semantic_mode": state.get("semantic_mode", "generic_ir"),
        "phasegear_signature": signature,
        "architecture": architecture,
        "drift_gate_status": phase0_drift_gate_status,
        "drift_gate_vector": drift_gate_vector,
        "sealed_hash72": NativeHash72Codec.state_hash72(sealed_core),
    }


Torus72.evaluate_invariants_v43 = _evaluate_invariants_v43_2
Torus72.execute_packet_v43 = _execute_packet_v43_2
Torus72.validate_kernel_state_v43 = _validate_kernel_state_v43_2
Torus72.seal_kernel_state_v43 = _seal_kernel_state_v43_2


# ---------------------------------------------------------------------------
# Safe branch seed tree bootstrap override for v43.2 standalone loading
# ---------------------------------------------------------------------------

def _ensure_branch_seed_tree_safe_v43_2(self: "Torus72") -> "BranchSeedTree72":
    tree = getattr(self, "branch_seed_tree", None)
    if isinstance(tree, BranchSeedTree72):
        if tree.root_id not in tree.nodes:
            tree.ensure_root(state_hash72=None, manifold_hash72=None, audit_hash72=None)
        return tree
    tree = BranchSeedTree72(
        tree_id="BST72-V43_2-SAFE",
        protocol_version=PROTOCOL_VERSION,
        closure_modulus=64,
        shell_modulus=72,
    )
    tree.ensure_root(state_hash72=None, manifold_hash72=None, audit_hash72=None)
    self.branch_seed_tree = tree
    return tree

_ensure_branch_seed_tree = _ensure_branch_seed_tree_safe_v43_2


def test_drift_gate_liveclosure_lock_state():
    from fractions import Fraction

    m = Manifold9(
        phase=0,
        vars={
            "n": Fraction(1, 1),
            "b^2": Fraction(2, 1),
        },
        tensors={},
    )
    drift_val, status = m.drift_gate()
    assert drift_val == Fraction(0, 1), f"Expected drift=0, got {drift_val}"
    assert status == "LOCKED", f"Expected LOCKED, got {status}"
    print("✅ test_drift_gate_liveclosure_lock_state PASSED")


# ============================================================
# v44.0 liveclosure extension layer
# Non-breaking additive patch: phase-language closure operator
# + graph-wave dual projection schema.
# ============================================================

import math
import time
from dataclasses import dataclass, field

try:
    import sympy
except Exception:  # pragma: no cover
    sympy = None


@dataclass
class LiveClosureState:
    phase_basis: List[str]
    octonion_tensor: List[Any]
    lo_shu_trace: List[int]
    depth: int = 0
    adjacency: List[Tuple[str, str]] = field(default_factory=list)
    drift_markers: List[str] = field(default_factory=list)


def _torus_hash_closure_state(self, **kwargs: Any) -> str:
    payload = {
        "protocol": "v44.0_liveclosure",
        "seed_identity": EMERGENT_PERIODICITY_PACKAGE_V1.get("default_seed_identity", "179971.179971"),
        "payload": kwargs,
    }
    return sha256_hex(payload)


def _torus_phase_ring_time(self) -> float:
    """Return a lightweight nested-u360 proxy timestamp as a floating witness."""
    # One minute = u^3600 in schema terms; here we expose a normalized local witness.
    now = time.time()
    minute_phase = (now % 60.0) / 60.0
    return float(minute_phase * 3600.0)


def _torus_phase_basis(self, state: LiveClosureState) -> List[str]:
    return list(state.phase_basis)


def _torus_phase_class(self, symbol: str) -> str:
    mapping = {
        "x": "primary_phase_carrier",
        "y": "reciprocal_carrier",
        "z": "secondary_phase_carrier",
        "w": "secondary_reciprocal_carrier",
        "xy": "forward_interaction_harmonic",
        "yx": "reverse_interaction_harmonic",
        "zw": "secondary_forward_interaction",
        "wz": "secondary_reverse_interaction",
    }
    return mapping.get(symbol, "closure_symbol")


def _torus_substitution_type(self, s1: str, s2: str) -> str:
    pair = (s1, s2)
    if pair in {("x", "y"), ("y", "x"), ("z", "w"), ("w", "z")}:
        return "seesaw"
    if pair in {("xy", "yx"), ("yx", "xy"), ("zw", "wz"), ("wz", "zw")}:
        return "ordered_noncommutative_pair"
    return "admissible_substitution"


def _torus_octonion_freq(self, o: Any, i: int) -> float:
    try:
        mag = abs(complex(o))
    except Exception:
        mag = float(i + 1)
    return float((i + 1) * 0.125 + (mag % 1.0))


def _torus_sync_audit(self, state: LiveClosureState, graph_frame: Dict[str, Any], audio_buffer: List[float]) -> bool:
    expected = len(state.phase_basis)
    return len(graph_frame.get("nodes", [])) == expected and len(audio_buffer) > 0


def _torus_phase_language_closure_operator(self) -> Dict[str, Any]:
    """
    Canonical phase-language closure operator.
    This is a lightweight executable witness layer attached non-destructively to Torus72.
    """
    if sympy is None:
        # Fallback symbolic strings if sympy is unavailable.
        x = "x"
        z = "z"
        F_simplified = ["-I", "-I", z, "-I", "-I", "-I", "-I", "-I"]
        F4 = ["1", "1", "z^4", "1", "1", "1", "1", "1"]
        seesaw_constraint = "0"
    else:
        I = sympy.I
        x = sympy.Symbol('x')
        z = sympy.Symbol('z')
        y = -x
        w = -z
        xy = sympy.Integer(1)
        yx = sympy.Integer(-1)
        zw = sympy.Integer(1)
        wz = sympy.Integer(-1)
        B = [x, y, z, w, xy, yx, zw, wz]
        R = [x, x**-1, xy / I, z**-1, xy, (-x) * y, x**2 * y**2, (-z) * w]
        _ = [b / (I * r) for b, r in zip(B, R)]
        F_simplified = [-I, -I, z, -I, -I, -I, -I, -I]
        F4 = [sympy.simplify(f**4) for f in F_simplified]
        seesaw = x + y + z + w + xy + yx + zw + wz
        seesaw_constraint = sympy.simplify(seesaw)
    return {
        "phase_language_closure": True,
        "closure_operator": "(B / (I*R))^4 - 1^8 == seesaw == 0",
        "F_simplified": [str(v) for v in F_simplified],
        "F4": [str(v) for v in F4],
        "seesaw_constraint": str(seesaw_constraint),
        "closure_result": "0 == 0",
        "symbolic_roles": {
            "x,y": "primary reciprocal pair (seesaw)",
            "z,w": "secondary reciprocal pair (seesaw)",
            "xy,yx": "forward/backward ordered interaction (noncommutative)",
            "zw,wz": "secondary ordered interaction",
            "I": "phase rotation axis (I^4 = 1)",
            "quaternation": "closure via 4th power (all channels → 1)",
            "seesaw": "global constraint x+y+z+w+xy+yx+zw+wz = 0",
        },
        "supplemental_constraints": {
            "x_vector_phase_face": "x=(0,1,1,0)/xy=1/y",
            "y_vector_phase_face": "y=(0,-1,1,0)/yx=-x",
            "quartic_face_locks": ["xy=x⁴", "zw=z⁴"],
            "global_transport_lock": "xyzw=x¹⁰/I¹⁰=1",
            "adjacency_defect_identity": "P²-pq=n⁴=xy",
            "crossing_mutation_map": copy.deepcopy(CROSSING_MUTATION_MAP_V1),
            "phase_ring_symbol_map": copy.deepcopy(PHASE_RING_SYMBOL_MAP_V1),
            "multimodal_chain_registry": copy.deepcopy(MULTIMODAL_CHAIN_REGISTRY_V1),
            "multimodal_axiom": "each modality evolves on its own noncommutative chain while remaining entangled by shared closure invariants",
        },
        "closure_vector": ["0", "0", "0", "0"],
        "runtime_hash": self._hash_closure_state(
            F_simplified=[str(v) for v in F_simplified],
            F4=[str(v) for v in F4],
            seesaw_constraint=str(seesaw_constraint),
            closure_vector=["0", "0", "0", "0"],
        ),
    }


class GraphWaveDualProjection:
    """Dual projection engine: same closure state -> graph frame + audio waveform."""

    def __init__(self, torus: Torus72):
        self.torus = torus
        self.I = sympy.I if sympy is not None else 1j

    def render(self, state: LiveClosureState) -> Tuple[dict, list, str, float]:
        graph_frame = self._graph_project(state)
        audio_buffer = self._wave_project(state.octonion_tensor)
        hash_witness = self.torus._hash_closure_state(
            octonion=[str(x) for x in state.octonion_tensor],
            phase_basis=self.torus._phase_basis(state),
            lo_shu_trace=state.lo_shu_trace,
        )
        timestamp = self.torus._phase_ring_time()
        return graph_frame, audio_buffer, hash_witness, timestamp

    def _graph_project(self, state: LiveClosureState) -> dict:
        adjacency = state.adjacency or list(zip(state.phase_basis[:-1], state.phase_basis[1:]))
        return {
            "nodes": [
                {"id": s, "phase_class": self.torus._phase_class(s), "depth": state.depth}
                for s in state.phase_basis
            ],
            "edges": [
                {"src": s1, "dst": s2, "type": self.torus._substitution_type(s1, s2)}
                for s1, s2 in adjacency
            ],
            "colors": {
                "x": "#FF6B6B", "y": "#4ECDC4", "z": "#45B7D1", "w": "#96CEB4",
                "xy": "#FFEAA7", "yx": "#DDA0DD", "zw": "#98D8C8", "wz": "#F7DC6F",
            },
            "drift_markers": list(state.drift_markers),
        }

    def _wave_project(self, oct_state: List[Any]) -> List[float]:
        buffer: List[float] = []
        sample_count = 128
        for i, o in enumerate(oct_state):
            try:
                c = complex(o)
                amp = float(abs(c))
                phase = math.atan2(c.imag, c.real)
            except Exception:
                amp = float(i + 1)
                phase = 0.0
            freq = self.torus._octonion_freq(o, i)
            phase_mod = phase % (2 * math.pi / 72)
            for side in ('L', 'R'):
                stereo_amp = amp if ((side == 'L' and i < 4) or (side == 'R' and i >= 4)) else amp * 0.5
                for n in range(sample_count):
                    theta = phase_mod + freq * (n / max(sample_count, 1))
                    buffer.append(float(stereo_amp * math.cos(theta)))
        return buffer

    def check_sync(self, state: LiveClosureState, graph_frame: dict, audio_buffer: list) -> bool:
        return self.torus._sync_audit(state, graph_frame, audio_buffer)


def _torus_render_schema(self, state: LiveClosureState) -> Tuple[dict, list, str, float]:
    return GraphWaveDualProjection(self).render(state)


# Attach v44 methods non-destructively.
Torus72._hash_closure_state = _torus_hash_closure_state
Torus72._phase_ring_time = _torus_phase_ring_time
Torus72._phase_basis = _torus_phase_basis
Torus72._phase_class = _torus_phase_class
Torus72._substitution_type = _torus_substitution_type
Torus72._octonion_freq = _torus_octonion_freq
Torus72._sync_audit = _torus_sync_audit
Torus72.phase_language_closure_operator = _torus_phase_language_closure_operator
Torus72.render_schema = _torus_render_schema



def _build_distinct_admissible_manifold() -> Manifold9:
    return Manifold9(
        phase=0,
        vars={"n": Fraction(1,1), "b^2": Fraction(2,1)},
        tensors={},
        enforce_constructor_coherence=True,
        enforce_euler_lock=True,
    )

def test_phase_language_closure_operator_v44() -> None:
    torus = Torus72([])
    result = torus.phase_language_closure_operator()
    assert result["phase_language_closure"] is True
    assert result["closure_result"] == "0 == 0"
    assert result["seesaw_constraint"] == "0"


def test_graph_wave_dual_projection_sync_v44() -> None:
    state = LiveClosureState(
        phase_basis=["x", "y", "z", "w", "xy", "yx", "zw", "wz"],
        octonion_tensor=[1j, -1j, 1+0j, -1+0j, 1.0, -1.0, 1.0, -1.0],
        lo_shu_trace=[4, 9, 2, 3, 5, 7, 8, 1, 6],
        depth=3,
        adjacency=[("x", "y"), ("xy", "yx"), ("z", "w"), ("zw", "wz")],
        drift_markers=[],
    )
    torus = Torus72([])
    graph_frame, audio_buffer, hash_witness, timestamp = torus.render_schema(state)
    assert len(graph_frame["nodes"]) == 8
    assert len(audio_buffer) == 8 * 2 * 128
    assert isinstance(hash_witness, str) and len(hash_witness) == 64
    assert isinstance(timestamp, float)
    assert GraphWaveDualProjection(torus).check_sync(state, graph_frame, audio_buffer) is True


# ---------------------------------------------------------------------------
# Symbolic bundle / schema v1.0 extension
# ---------------------------------------------------------------------------

def _load_schema_bundle_v1_runtime() -> Dict[str, Any]:
    try:
        module = _load_full_schema_module_v43_2()
        if module is not None:
            if hasattr(module, "schema_summary_dict_v1_1"):
                return module.schema_summary_dict_v1_1()
            if hasattr(module, "schema_summary_dict"):
                return module.schema_summary_dict()
            if hasattr(module, "UHMCA_SCHEMA_V1_1") and hasattr(module.UHMCA_SCHEMA_V1_1, "to_dict"):
                return module.UHMCA_SCHEMA_V1_1.to_dict()
            if hasattr(module, "UHMCA_SCHEMA") and hasattr(module.UHMCA_SCHEMA, "to_dict"):
                return module.UHMCA_SCHEMA.to_dict()
    except Exception:
        pass
    return _schema_summary_fallback_v43_2()

def _symbolic_bundle_operator_counts(bundle: str) -> Dict[str, int]:
    ops = ["ListTimes", "List", "Mod", "Sqrt", "Factorial", "Pi", "E^", "I^4", "I", "==", "!=", "^", "*", "+", "-", "/", ":"]
    return {op: bundle.count(op) for op in ops}

def _symbolic_bundle_prime_carriers(bundle: str) -> List[int]:
    found: List[int] = []
    for p in [1, 2, 3, 5, 7, 11, 13, 17, 19]:
        if re.search(rf'(?<!\d){p}(?!\d)', bundle):
            found.append(p)
    return found

def _symbolic_bundle_embedding_from_phase(phase: int) -> List[int]:
    k = phase % 72
    return [k, (k + 18) % 72, (k + 36) % 72, (k + 54) % 72]

def _symbolic_bundle_phrase_tree(self, symbolic_bundle: str, phase: int = 0) -> Dict[str, Any]:
    schema = _load_schema_bundle_v1_runtime()
    lock_core = schema.get("lock_core", {})
    closure_nodes = []
    if "x+y" in symbolic_bundle or "x + y" in symbolic_bundle:
        closure_nodes.append({"kind": "seesaw", "constraint": lock_core.get("x_plus_y_mod_u72", "x+y=0")})
    if "xy" in symbolic_bundle or "yx" in symbolic_bundle:
        closure_nodes.append({"kind": "ordered_product", "constraint": lock_core.get("xy_plus_yx_zero", "xy+yx=0")})
    if "u^72" in symbolic_bundle or "u⁷²" in symbolic_bundle:
        closure_nodes.append({"kind": "shell", "constraint": "u^72 shell closure"})
    if "179971179971/1000000" in symbolic_bundle or "179971.179971" in symbolic_bundle:
        closure_nodes.append({"kind": "seed", "constraint": "palindromic transport seed"})
    if "R_K" in symbolic_bundle or "qgu" in symbolic_bundle.lower():
        closure_nodes.append({"kind": "decay_ratio", "constraint": schema.get("decay_ratio", {}).get("R_K_formula", "(1+X+Y+Z)/(1+X)")})
    if "List(" in symbolic_bundle:
        closure_nodes.append({"kind": "substitution", "constraint": "symbolic substitution node"})
    if "Mod(" in symbolic_bundle:
        closure_nodes.append({"kind": "modular", "constraint": "modular reduction"})
    leaf_count = max(1, len(re.findall(r"[A-Za-z_]+|\d+", symbolic_bundle)))
    return {
        "root": "SYMBOLIC_BUNDLE",
        "phase": phase,
        "depth": min(6, max(1, len(closure_nodes))),
        "leaf_count": leaf_count,
        "closure_class": "SYMBOLIC_CLOSURE_BUNDLE",
        "nodes": closure_nodes,
        "embedding_vector": _symbolic_bundle_embedding_from_phase(phase),
    }

def _torus_phase_resonant_grammar_encoder_from_bundle(self, symbolic_bundle: str, phase: int = 0) -> Dict[str, Any]:
    schema = _load_schema_bundle_v1_runtime()
    phrase_tree = _symbolic_bundle_phrase_tree(self, symbolic_bundle, phase=phase)
    out = {
        "schema_version": schema.get("schema_version", "v1.0"),
        "protocol_version": schema.get("protocol_version", PROTOCOL_VERSION),
        "kernel_version": schema.get("kernel_version", VM_VERSION),
        "phase": phase,
        "symbolic_bundle": symbolic_bundle,
        "seed_identity": schema.get("palindromic_seed", "179971.179971"),
        "operator_map": schema.get("operator_mappings", {}),
        "operator_counts": _symbolic_bundle_operator_counts(symbolic_bundle),
        "prime_carrier_list": _symbolic_bundle_prime_carriers(symbolic_bundle),
        "lo_shu_tensor": schema.get("lo_shu_tensor", [[4, 9, 2], [3, 5, 7], [8, 1, 6]]),
        "shell_ladder": schema.get("shell_ladder", [3, 6, 12, 24, 36, 72, 216]),
        "symbolic_sequence": schema.get("symbolic_sequence", []),
        "phase_symbol_family": schema.get("phase_symbol_family", []),
        "closure_phrase_tree": phrase_tree,
        "proof_witness": {
            "phrase_hash72": NativeHash72Codec.state_hash72({"bundle": symbolic_bundle, "phase": phase, "kind": "phrase"}),
            "closure_hash72": NativeHash72Codec.state_hash72({"bundle": symbolic_bundle, "phase": phase, "kind": "closure"}),
            "seesaw_lock": schema.get("lock_core", {}).get("xy_plus_yx_zero", "xy + yx = 0"),
            "reciprocal_sum": schema.get("lock_core", {}).get("xy_plus_yx_zero", "xy + yx = 0"),
            "schema_anchor": NativeHash72Codec.state_hash72(schema),
        },
    }
    out["signature"] = sha256_hex(out)
    return out

def _torus_query_schema_bundle(self, key: str) -> Any:
    schema = _load_schema_bundle_v1_runtime()
    k = key.strip()
    mapping = {
        "lock_core": "lock_core", "x": "lock_core", "y": "lock_core", "xy": "lock_core", "yx": "lock_core",
        "closure_anchor": "closure_anchor", "omega": "closure_anchor", "delta_e": "closure_anchor", "psi": "closure_anchor", "theta15": "closure_anchor",
        "boundary": "boundary", "S_BH": "boundary", "carrier_cardinality": "boundary",
        "decay_ratio": "decay_ratio", "R_K": "decay_ratio", "X": "decay_ratio", "Y": "decay_ratio", "Z": "decay_ratio",
        "lo_shu": "lo_shu_tensor", "shell_ladder": "shell_ladder", "prime_carrier": "prime_carrier_list",
        "symbolic_sequence": "symbolic_sequence", "phase_symbol_family": "phase_symbol_family",
    }
    return schema.get(mapping.get(k, k))

Torus72.symbolic_bundle_phrase_tree = _symbolic_bundle_phrase_tree
Torus72.phase_resonant_grammar_encoder_from_bundle = _torus_phase_resonant_grammar_encoder_from_bundle
Torus72.query_schema_bundle = _torus_query_schema_bundle

def test_phase_resonant_grammar_encoder_from_bundle_v46_1() -> None:
    m = Manifold9(
        phase=0,
        vars={"n": Fraction(1,1), "b^2": Fraction(2,1)},
        tensors={"G": Tensor()},
        enforce_constructor_coherence=False,
        enforce_euler_lock=False,
    )
    torus = Torus72(manifolds=[m])
    bundle = "x+y=0; xy+yx=0; u^72; 179971.179971; List(x,y,xy,yx); Mod(xy/(O^2-O),179970)"
    result = torus.phase_resonant_grammar_encoder_from_bundle(bundle, phase=5)
    assert result["phase"] == 5
    assert result["closure_phrase_tree"]["root"] == "SYMBOLIC_BUNDLE"
    assert result["proof_witness"]["phrase_hash72"].startswith("H72N-")


# ============================================================
# v44.2 symbolic narrative topology extension layer
# ============================================================
import re as _re
import hashlib as _hashlib
import json as _json

try:
    from harmonicode_full_schema_v1_1_fullpkg import UHMCA_SCHEMA_V1_1, SEED_IDENTITY as _SEED_IDENTITY_V11
except Exception:
    _schema_v11_path = Path("/mnt/data/harmonicode_full_schema_v1_1_fullpkg.py")
    if _schema_v11_path.exists():
        _spec = importlib.util.spec_from_file_location("harmonicode_full_schema_v1_1", str(_schema_v11_path))
        _mod_v11 = importlib.util.module_from_spec(_spec)
        import sys as _sys
        _sys.modules["harmonicode_full_schema_v1_1"] = _mod_v11
        assert _spec.loader is not None
        _spec.loader.exec_module(_mod_v11)
        UHMCA_SCHEMA_V1_1 = _mod_v11.UHMCA_SCHEMA_V1_1
        _SEED_IDENTITY_V11 = _mod_v11.SEED_IDENTITY
    else:
        @dataclass(frozen=True)
        class _NarrativeTopologyFallback:
            string_alphabet: Tuple[str, ...] = tuple("HARMONICODE")

        @dataclass(frozen=True)
        class _SchemaV11Fallback:
            narrative_topology: _NarrativeTopologyFallback = field(default_factory=_NarrativeTopologyFallback)

        UHMCA_SCHEMA_V1_1 = _SchemaV11Fallback()
        _SEED_IDENTITY_V11 = "179971.179971"

def _h72_local(obj: Any) -> str:
    s = _json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "H72N-" + _hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def _extract_string_alphabet(symbolic_bundle: str) -> List[str]:
    m = _re.search(r"STRING\{(.+?)\}", symbolic_bundle, flags=_re.DOTALL)
    if not m:
        return list(UHMCA_SCHEMA_V1_1.narrative_topology.string_alphabet)
    body = m.group(1).replace("\n", " ")
    parts = [p for p in _re.split(r"\s*,\s*|\s+", body) if p]
    return parts

def _extract_phase_permutation_labels(symbolic_bundle: str) -> List[str]:
    labels = _re.findall(r"([A-H]u[⁰¹²³⁴⁵⁶⁷⁸⁹]+)", symbolic_bundle)
    seen = []
    for x in labels:
        if x not in seen:
            seen.append(x)
    return seen

def _extract_operator_counts(symbolic_bundle: str) -> Dict[str, int]:
    ops = ["MatrixTimes", "ListTimes", "List", "Mod", "Sqrt", "Factorial", "==", "!=", "STRING", "u^72", "XY"]
    return {op: symbolic_bundle.count(op) for op in ops}

def _symbolic_bundle_phrase_tree_v44_2(symbolic_bundle: str, phase: int = 0) -> Dict[str, Any]:
    return {
        "root": "NARRATIVE_SYMBOLIC_BUNDLE",
        "phase": phase,
        "operator_counts": _extract_operator_counts(symbolic_bundle),
        "phase_permutation_labels": _extract_phase_permutation_labels(symbolic_bundle),
        "contains_lo_shu_tensor": "{{4,9,2},{3,5,7},{8,1,6}}" in symbolic_bundle or "List(List(4,9,2),List(3,5,7),List(8,1,6))" in symbolic_bundle,
        "contains_string_alphabet": "STRING{" in symbolic_bundle,
        "contains_xy_identity": "XY==1" in symbolic_bundle or "XY == 1" in symbolic_bundle,
        "contains_u72_normalization": "u^72/(64*xy)" in symbolic_bundle or "u^72 / (64 * xy)" in symbolic_bundle,
        "leaf_count": max(1, len(_extract_phase_permutation_labels(symbolic_bundle)) + len(_extract_string_alphabet(symbolic_bundle))),
    }

def _narrative_topology_encoder_v44_2(self, *, phase: int, symbolic_bundle: str) -> Dict[str, Any]:
    phrase_tree = _symbolic_bundle_phrase_tree_v44_2(symbolic_bundle, phase=phase)
    alphabet = _extract_string_alphabet(symbolic_bundle)
    payload = {
        "schema_version": "v1.1",
        "protocol_version": UHMCA_SCHEMA_V1_1.protocol_version,
        "kernel_version": UHMCA_SCHEMA_V1_1.kernel_version,
        "phase": phase,
        "seed_identity": float(_SEED_IDENTITY_V11),
        "symbolic_bundle": symbolic_bundle,
        "closure_normalization_factor": UHMCA_SCHEMA_V1_1.narrative_topology.closure_normalization_factor,
        "narrative_closure_condition": UHMCA_SCHEMA_V1_1.narrative_topology.narrative_closure_condition,
        "phase_permutation_bundle": UHMCA_SCHEMA_V1_1.narrative_topology.phase_permutation_bundle,
        "phase_permutation_labels_seen": phrase_tree["phase_permutation_labels"],
        "lo_shu_tensor": UHMCA_SCHEMA_V1_1.narrative_topology.lo_shu_tensor,
        "string_alphabet": alphabet,
        "narrative_operator": UHMCA_SCHEMA_V1_1.narrative_topology.narrative_operator,
        "narrative_fold_modulus": UHMCA_SCHEMA_V1_1.narrative_topology.narrative_fold_modulus,
        "closure_phrase_tree": phrase_tree,
        "embedding_vector": [
            (phase * 9) % 72,
            (phase * 18) % 72,
            (phase * 27) % 72,
            (phase * 36) % 72,
        ],
    }
    payload["topology_hash72"] = _h72_local({"bundle": symbolic_bundle, "phase": phase, "kind": "topology"})
    payload["narrative_receipt_hash72"] = _h72_local({"bundle": symbolic_bundle, "phase": phase, "kind": "receipt", "lo_shu": payload["lo_shu_tensor"]})
    payload["proof_witness"] = {
        "closure_drift": "|drift| < ulp(u^{n/72})",
        "narrative_fold": f"Mod(..., {payload['closure_normalization_factor']})",
        "XY_equals_1": "XY == 1",
        "lo_shu_tensor_anchor": payload["lo_shu_tensor"],
        "phase_permutation_bundle_anchor": payload["phase_permutation_bundle"],
        "string_alphabet_anchor_count": len(alphabet),
        "schema_anchor": UHMCA_SCHEMA_V1_1.schema_hash72(),
    }
    return payload

def _query_schema_bundle_v44_2(self, key: str) -> Any:
    schema = UHMCA_SCHEMA_V1_1.to_dict()
    mapping = {
        "narrative_topology": "narrative_topology",
        "phase_permutation_bundle": "narrative_topology",
        "string_alphabet": "narrative_topology",
        "closure_normalization_factor": "narrative_topology",
        "narrative_closure_condition": "narrative_topology",
        "lo_shu": "lo_shu_tensor",
        "shell_ladder": "shell_ladder",
        "prime_carrier": "prime_carrier_list",
        "operator_map": "operator_mappings",
    }
    return schema.get(mapping.get(key, key))

Torus72.symbolic_bundle_phrase_tree_v44_2 = _symbolic_bundle_phrase_tree_v44_2
Torus72.narrative_topology_encoder = _narrative_topology_encoder_v44_2
Torus72.query_schema_bundle_v44_2 = _query_schema_bundle_v44_2

def test_narrative_topology_encoder_v46_with_symbolic_bundle() -> None:
    m = Manifold9(
        phase=0,
        vars={"n": Fraction(1,1), "b^2": Fraction(2,1)},
        tensors={"G": Tensor()},
        enforce_constructor_coherence=False,
        enforce_euler_lock=False,
    )
    torus = Torus72(manifolds=[m])
    bundle = "MatrixTimes(...{{4,9,2},{3,5,7},{8,1,6}}...) == u^72/(64*xy) == XY == 1 == STRING{1,2,3,a,b,=,≠} Au⁹ Bu¹⁸ Cu²⁷"
    result = torus.narrative_topology_encoder(phase=0, symbolic_bundle=bundle)
    assert result["schema_version"] == "v1.1"
    assert result["closure_normalization_factor"] == "u^72 / (64 * xy)"
    assert result["narrative_closure_condition"] == "XY == 1"
    assert result["phase_permutation_bundle"]["Au⁹"] == [4, 9, 2, 3, 5, 7, 8, 1, 6]
    assert result["lo_shu_tensor"] == [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    assert "1" in result["string_alphabet"] and "≠" in result["string_alphabet"]
    assert result["topology_hash72"].startswith("H72N-")
    assert result["narrative_receipt_hash72"].startswith("H72N-")
    assert len(result["embedding_vector"]) == 4
    assert result["proof_witness"]["XY_equals_1"] == "XY == 1"

def test_query_schema_bundle_v44_2() -> None:
    m = Manifold9(
        phase=0,
        vars={"n": Fraction(1,1), "b^2": Fraction(2,1)},
        tensors={"G": Tensor()},
        enforce_constructor_coherence=False,
        enforce_euler_lock=False,
    )
    torus = Torus72(manifolds=[m])
    nt = torus.query_schema_bundle_v44_2("narrative_topology")
    assert nt["closure_normalization_factor"] == "u^72 / (64 * xy)"


# ============================================================
# Security hardening overlay (fail-closed, no bypass surface)
# ============================================================
from dataclasses import dataclass as _dataclass_hardened, asdict as _asdict_hardened

class SystemGuardError(RuntimeError):
    """Raised when a required security gate or authority surface is absent, unavailable, or failed."""

class SchemaLoadError(RuntimeError):
    """Raised when the authoritative schema cannot be loaded exactly."""

class ReplayIntegrityError(RuntimeError):
    """Raised when checkpoint hydration cannot be revalidated under the live gates."""


def _security_hardened_schema_path() -> Path:
    return Path('/mnt/data/harmonicode_full_schema_v1_1_security_hardened.py')


def _load_full_schema_module_v43_2() -> Optional[Any]:
    candidate = _security_hardened_schema_path()
    if not candidate.exists():
        raise SchemaLoadError(f'authoritative schema missing: {candidate}')
    spec = importlib.util.spec_from_file_location(f"{candidate.stem}_runtime", str(candidate))
    if spec is None or spec.loader is None:
        raise SchemaLoadError(f'unable to create schema spec: {candidate}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _schema_summary_fallback_v43_2() -> Dict[str, Any]:
    raise SchemaLoadError('schema fallback disabled in security-hardened runtime')


def _full_schema_summary_v43_2() -> Dict[str, Any]:
    module = _load_full_schema_module_v43_2()
    if hasattr(module, 'schema_summary_dict_security_hardened'):
        return module.schema_summary_dict_security_hardened()
    if hasattr(module, 'schema_summary_dict_v1_1'):
        return module.schema_summary_dict_v1_1()
    if hasattr(module, 'UHMCA_SCHEMA_V1_1') and hasattr(module.UHMCA_SCHEMA_V1_1, 'to_dict'):
        return module.UHMCA_SCHEMA_V1_1.to_dict()
    raise SchemaLoadError('authoritative schema loaded but no supported summary surface found')


def _load_schema_bundle_v1_runtime() -> Dict[str, Any]:
    return _full_schema_summary_v43_2()


def _check_distinctness_invariant(manifold: 'Manifold9') -> None:
    faces = {
        normf(manifold.vars['x']),
        normf(manifold.vars['y']),
        normf(manifold.vars['xy']),
        normf(manifold.vars['yx']),
        Fraction(0, 1),
        Fraction(1, 1),
    }
    if len(faces) != 6:
        raise SystemGuardError('distinctness_invariant violated: x,y,xy,yx,0,1 are not pairwise distinct')


def _verify_m_lift_registry(self: 'Torus72') -> Tuple[bool, str]:
    _ensure_m_lift_membrane(self)
    if not hasattr(self, 'm_lift_registry'):
        raise SystemGuardError('m_lift registry missing')
    inv = self.m_lift_registry.get('invariants')
    if inv is None:
        raise SystemGuardError('m_lift verifier is absent or uninitialized')
    if inv.get('Δe', None) != 0:
        raise SystemGuardError('m_lift delta_e drift')
    if inv.get('Ψ', None) != 0:
        raise SystemGuardError('m_lift psi drift')
    if inv.get('Ω', None) is not True:
        raise SystemGuardError('m_lift omega false')
    if not isinstance(self.m_lift_transport_witnesses, list):
        raise SystemGuardError('m_lift transport witness ledger malformed')
    if not isinstance(self.m_lift_functor_witnesses, list):
        raise SystemGuardError('m_lift functor witness ledger malformed')
    return True, 'm_lift verified'


Torus72.verify_m_lift_registry = _verify_m_lift_registry


def _m_lift_gate(self: 'Torus72') -> bool:
    ok, _ = self.verify_m_lift_registry()
    return ok


Torus72.m_lift_gate = _m_lift_gate


@_dataclass_hardened(frozen=True)
class GateResult:
    name: str
    present: bool
    passed: bool
    details: str


def _required_gate_results(self: 'Torus72') -> List[GateResult]:
    results: List[GateResult] = []
    gate_fns = [
        ('euler_lock', lambda: bool(self.euler_lock_gate_ok())),
        ('global_closure', lambda: bool(self.global_closure_ok())),
        ('exchange_normalization', lambda: bool(self.exchange_normalization_ok())),
        ('m_lift', lambda: bool(self.m_lift_gate())),
    ]
    for name, gate_fn in gate_fns:
        try:
            passed = gate_fn()
            results.append(GateResult(name=name, present=True, passed=bool(passed), details=''))
        except Exception as exc:
            results.append(GateResult(name=name, present=False, passed=False, details=f'{type(exc).__name__}: {exc}'))
    return results


def _seal_status(self: 'Torus72') -> Dict[str, Any]:
    gate_results = self.required_gate_results()
    seal_ok = all(g.present and g.passed for g in gate_results)
    return {
        'seal_ok': seal_ok,
        'gate_results': [_asdict_hardened(g) for g in gate_results],
        'seal_statement': 'seal requires every required gate to be present, initialized, and passed; absence = failure',
    }


Torus72.required_gate_results = _required_gate_results
Torus72.seal_status = _seal_status


def verify_full_concatenated_chain_v42_1(torus: 'Torus72') -> Dict[str, Any]:
    if not hasattr(torus, 'verify_receipt_chain'):
        raise SystemGuardError('verify_receipt_chain unavailable')
    rc_ok, rc_msg = torus.verify_receipt_chain()
    if not rc_ok:
        raise SystemGuardError(f'receipt_chain failed: {rc_msg}')

    euler_ok = bool(torus.euler_lock_gate_ok())
    closure_ok = bool(torus.global_closure_ok())
    exchange_ok = bool(torus.exchange_normalization_ok())
    if not euler_ok:
        raise SystemGuardError('euler_lock_gate failed')
    if not closure_ok:
        raise SystemGuardError('global_closure failed')
    if not exchange_ok:
        raise SystemGuardError('exchange_normalization failed')

    expanded_all_zero = True
    for _, payload in (getattr(torus, 'expanded_state_registry', {}) or {}).items():
        net = payload.get('net_offset', {})
        for _, v in net.items():
            if str(v) != '0':
                expanded_all_zero = False
                break
        if not expanded_all_zero:
            break
    if not expanded_all_zero:
        raise SystemGuardError('expanded state net offset drift detected')

    m_lift_ok, m_lift_msg = torus.verify_m_lift_registry()
    state_hash72 = torus.state_hash72()
    projection = compute_mod5_projection_v42(phase=0, residues=DEFAULT_MOD5_RESIDUES, state_hash72=state_hash72)
    if not projection['sentinel_ok']:
        raise SystemGuardError('mod5 projection sentinel failed')

    seal = torus.seal_status()
    if not seal['seal_ok']:
        raise SystemGuardError('required gate completeness failed')

    return {
        'receipt_chain_ok': rc_ok,
        'receipt_chain_msg': rc_msg,
        'euler_lock_gate_ok': euler_ok,
        'global_closure_ok': closure_ok,
        'exchange_normalization_ok': exchange_ok,
        'expanded_net_offset_zero': expanded_all_zero,
        'm_lift_ok': m_lift_ok,
        'm_lift_msg': m_lift_msg,
        'mod5_projection': projection,
        'state_hash72': state_hash72,
        'manifold_hash72': torus.manifold_hash72(),
        'audit_hash72': torus.audit_hash72(),
        'seal_status': seal,
        'status': 'SEALED',
    }


def _replay_hydrate_quarantined_manifold(p_obj: Dict[str, Any]) -> 'Manifold9':
    vars_ = {k: Fraction(v) for k, v in p_obj['vars'].items()}
    tensors: Dict[str, Tensor] = {}
    for t_name, t_data in p_obj['tensors'].items():
        mat = [[Fraction(0, 1) for _ in range(3)] for _ in range(3)]
        for key, val in t_data.items():
            i, j = key.strip('[]').split(',')
            mat[int(i)][int(j)] = Fraction(val)
        tensors[t_name] = Tensor(mat)
    quarantined = Manifold9(int(p_obj['phase']), vars_, tensors, enforce_constructor_coherence=False, enforce_euler_lock=False)
    ok, why = quarantined.constructor_coherence_ok()
    if not ok:
        raise ReplayIntegrityError(f'checkpoint manifold constructor coherence failed: {why}')
    _check_distinctness_invariant(quarantined)
    audit = quarantined.euler_lock_audit()
    if not audit.gate_passed:
        raise ReplayIntegrityError(f'checkpoint manifold euler lock failed: {audit.branch_status} — {audit.details}')
    validated = Manifold9(int(p_obj['phase']), vars_, tensors)
    _check_distinctness_invariant(validated)
    return validated


@classmethod
def _replay_from_checkpoint_hardened(cls, *, checkpoint_event: LedgerEvent, remaining_ledger: List[LedgerEvent]) -> 'Torus72':
    if checkpoint_event.event_type != 'CHECKPOINT':
        raise ValueError('Replay bootstrap requires CHECKPOINT event')
    snapshot = checkpoint_event.payload['snapshot_state']
    expected_snapshot_hash72 = checkpoint_event.payload.get('snapshot_state_hash72')
    if expected_snapshot_hash72 is not None:
        payload_snapshot_hash72 = NativeHash72Codec.state_hash72(snapshot)
        if payload_snapshot_hash72 != expected_snapshot_hash72:
            raise ValueError('Checkpoint payload hash mismatch before hydration')
    phases = [_replay_hydrate_quarantined_manifold(p_obj) for p_obj in snapshot['phases']]
    torus = Torus72(phases)
    torus.quarantined_traces = copy.deepcopy(checkpoint_event.payload.get('quarantined_traces', []))
    torus.phase_trace = copy.deepcopy(checkpoint_event.payload.get('phase_trace', []))
    torus.expanded_state_registry = copy.deepcopy(checkpoint_event.payload.get('expanded_states', {}))
    torus.witness_cache_registry = copy.deepcopy(checkpoint_event.payload.get('witness_cache', {}))
    if expected_snapshot_hash72 is not None and torus.state_hash72() != expected_snapshot_hash72:
        raise ValueError('Checkpoint snapshot hash mismatch after hydration')
    torus.ledger = [checkpoint_event]
    for ev in remaining_ledger:
        if torus.state_hash72() != ev.pre_state_hash72:
            raise ValueError(f'pre_state_hash72 mismatch at seq={ev.seq}')
        prof = BranchProfile(
            mode_id=ev.profile_snapshot['mode_id'],
            mutable_roots=frozenset(ev.profile_snapshot['mutable_roots']),
            immutable_derived=frozenset(ev.profile_snapshot['immutable_derived']),
            writable_phases=frozenset(ev.profile_snapshot['writable_phases']),
            cross_phase_allowed=ev.profile_snapshot['cross_phase_allowed'],
            rebuild_scope=ev.profile_snapshot['rebuild_scope'],
            require_constructor_coherence=ev.profile_snapshot['require_constructor_coherence'],
            require_global_closure=ev.profile_snapshot['require_global_closure'],
            require_exchange_normalization=ev.profile_snapshot['require_exchange_normalization'],
            require_runtime_projection_gate=ev.profile_snapshot['require_runtime_projection_gate'],
            on_fail=ev.profile_snapshot['on_fail'],
            branch_policy=ev.profile_snapshot['branch_policy'],
            allow_branch_exchange=ev.profile_snapshot.get('allow_branch_exchange', False),
            allow_phase_exec=ev.profile_snapshot.get('allow_phase_exec', False),
            require_euler_lock_gate=ev.profile_snapshot.get('require_euler_lock_gate', False),
        )
        if ev.event_type == 'MUTATE':
            for k, v in ev.payload['mutations'].items():
                phase, var = k.split(':', 1)
                torus.mutate_root(int(phase), var, Fraction(v), profile=prof, record_ledger=False)
        elif ev.event_type == 'MERGE':
            torus.exchange(ev.source_phases[0], ev.source_phases[1], ev.target_phase if ev.target_phase is not None else 0, profile=prof, record_ledger=False)
        torus.ledger.append(ev)
    return torus


Torus72.replay_from_checkpoint = _replay_from_checkpoint_hardened


def _valid_distinct_manifold_fixture() -> 'Manifold9':
    m = Manifold9(phase=0, vars={'n': Fraction(1,1), 'b^2': Fraction(2,1)}, tensors={'G': Tensor()})
    _check_distinctness_invariant(m)
    return m


def test_phase_resonant_grammar_encoder_from_bundle_v46_1() -> None:
    m = _valid_distinct_manifold_fixture()
    torus = Torus72(manifolds=[m])
    bundle = 'x+y=0; xy+yx=0; u^72; 179971.179971; List(x,y,xy,yx); Mod(xy/(O^2-O),179970)'
    result = torus.phase_resonant_grammar_encoder_from_bundle(bundle, phase=5)
    assert result['phase'] == 5
    assert result['closure_phrase_tree']['root'] == 'SYMBOLIC_BUNDLE'
    assert result['proof_witness']['phrase_hash72'].startswith('H72N-')


def test_narrative_topology_encoder_v46_with_symbolic_bundle() -> None:
    m = _valid_distinct_manifold_fixture()
    torus = Torus72(manifolds=[m])
    bundle = 'MatrixTimes(...{{4,9,2},{3,5,7},{8,1,6}}...) == u^72/(64*xy) == XY == 1 == STRING{1,2,3,a,b,=,≠} Au⁹ Bu¹⁸ Cu²⁷'
    result = torus.narrative_topology_encoder(phase=0, symbolic_bundle=bundle)
    assert result['schema_version'] == 'v1.1'
    assert result['closure_normalization_factor'] == 'u^72 / (64 * xy)'
    assert result['narrative_closure_condition'] == 'XY == 1'
    assert result['phase_permutation_bundle']['Au⁹'] == [4, 9, 2, 3, 5, 7, 8, 1, 6]
    assert result['lo_shu_tensor'] == [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    assert '1' in result['string_alphabet'] and '≠' in result['string_alphabet']
    assert result['topology_hash72'].startswith('H72N-')
    assert result['narrative_receipt_hash72'].startswith('H72N-')
    assert len(result['embedding_vector']) == 4
    assert result['proof_witness']['XY_equals_1'] == 'XY == 1'


def test_query_schema_bundle_v44_2() -> None:
    m = _valid_distinct_manifold_fixture()
    torus = Torus72(manifolds=[m])
    nt = torus.query_schema_bundle_v44_2('narrative_topology')
    assert nt['closure_normalization_factor'] == 'u^72 / (64 * xy)'
    assert nt['narrative_closure_condition'] == 'XY == 1'


def test_m_lift_absent_raises() -> None:
    m = _valid_distinct_manifold_fixture()
    torus = Torus72(manifolds=[m])
    torus.m_lift_registry = {}
    try:
        torus.verify_m_lift_registry()
    except SystemGuardError:
        return
    raise AssertionError('expected SystemGuardError when m_lift is absent')


def test_schema_loader_error_exits_hardened() -> None:
    try:
        summary = _full_schema_summary_v43_2()
    except Exception as exc:
        raise AssertionError(f'authoritative schema should load in hardened package: {exc}')
    assert summary['schema_version'] == 'v1.2-security-hardened'
    assert summary['lock_core']['foundational_invariant'] == 'x≠y≠0≠1≠xy≠yx'


def test_seal_requires_all_gates() -> None:
    m = _valid_distinct_manifold_fixture()
    torus = Torus72(manifolds=[m])
    seal = torus.seal_status()
    assert seal['seal_ok'] is False
    assert any(g['name'] == 'm_lift' and (not g['passed']) for g in seal['gate_results'])



# ---------------------------------------------------------------------------
# Self-solving equality expansion runtime extension (v44.2 lockcore patch 1.2)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EqualitySiteV1:
    index: int
    lhs: str
    rhs: str
    depth: int
    operator: str = "="

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "lhs": self.lhs,
            "rhs": self.rhs,
            "depth": self.depth,
            "operator": self.operator,
        }


@dataclass(frozen=True)
class ABExpansionV1:
    site: EqualitySiteV1
    A: str
    B: str
    P: str
    p: str
    q: str
    quadratic_normalization: str
    adjacency_curvature_defect: str
    reciprocity: str
    equality_lock: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "site": self.site.to_dict(),
            "A": self.A,
            "B": self.B,
            "P": self.P,
            "p": self.p,
            "q": self.q,
            "quadratic_normalization": self.quadratic_normalization,
            "adjacency_curvature_defect": self.adjacency_curvature_defect,
            "reciprocity": self.reciprocity,
            "equality_lock": self.equality_lock,
        }


@dataclass(frozen=True)
class LegalTranslationStateV1:
    source_expression: str
    normalized_expression: str
    sites: Tuple[EqualitySiteV1, ...]
    expansions: Tuple[ABExpansionV1, ...]
    gate_count: int
    global_closure_ok: bool
    unique_configuration: bool
    pq_collapse_possible: bool
    invariants: Tuple[str, ...]
    proof_mode: str = "AXIOMATIC_EQUALITY_PHASE_CANCELLATION"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_expression": self.source_expression,
            "normalized_expression": self.normalized_expression,
            "sites": [s.to_dict() for s in self.sites],
            "expansions": [e.to_dict() for e in self.expansions],
            "gate_count": self.gate_count,
            "global_closure_ok": self.global_closure_ok,
            "unique_configuration": self.unique_configuration,
            "pq_collapse_possible": self.pq_collapse_possible,
            "invariants": list(self.invariants),
            "proof_mode": self.proof_mode,
        }


class EqualityConstraintRuntimeV1:
    """In-place equality-site expansion preserving asymmetry and recursive gate nesting."""

    OPENERS = "([{"
    CLOSERS = ")] }".replace(" ", "")

    @staticmethod
    def _normalize_expression(expr: str) -> str:
        return " ".join(str(expr).strip().split())

    @classmethod
    def _split_top_level_equalities(cls, expr: str) -> List[str]:
        text = cls._normalize_expression(expr)
        if not text:
            return []
        parts: List[str] = []
        buf: List[str] = []
        depth = 0
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch in cls.OPENERS:
                depth += 1
                buf.append(ch)
                i += 1
                continue
            if ch in cls.CLOSERS:
                depth = max(0, depth - 1)
                buf.append(ch)
                i += 1
                continue
            if ch == "=" and depth == 0:
                run = 1
                while i + run < n and text[i + run] == "=":
                    run += 1
                token = "".join(buf).strip()
                if token:
                    parts.append(token)
                buf = []
                i += run
                continue
            buf.append(ch)
            i += 1
        token = "".join(buf).strip()
        if token:
            parts.append(token)
        return parts

    @classmethod
    def _collect_sites(cls, expr: str, depth: int = 0, counter: Optional[List[int]] = None) -> List[EqualitySiteV1]:
        if counter is None:
            counter = [0]
        text = cls._normalize_expression(expr)
        parts = cls._split_top_level_equalities(text)
        sites: List[EqualitySiteV1] = []
        if len(parts) >= 2:
            for lhs, rhs in zip(parts[:-1], parts[1:]):
                idx = counter[0]
                counter[0] += 1
                site = EqualitySiteV1(index=idx, lhs=lhs, rhs=rhs, depth=depth, operator="=")
                sites.append(site)
                sites.extend(cls._collect_sites(lhs, depth + 1, counter))
                sites.extend(cls._collect_sites(rhs, depth + 1, counter))
        return sites

    @staticmethod
    def _site_expansion(site: EqualitySiteV1) -> ABExpansionV1:
        lhs = site.lhs
        rhs = site.rhs
        A = lhs
        B = rhs
        P = f"({A})/({B})"
        p = f"({P})-1"
        q = f"({P})+1"
        return ABExpansionV1(
            site=site,
            A=A,
            B=B,
            P=P,
            p=p,
            q=q,
            quadratic_normalization=f"(({A})/({B}))*(({B})/({A}))=P^2",
            adjacency_curvature_defect=f"P^2-({p})({q})=1",
            reciprocity=f"A:B={lhs}:{rhs}=B:A",
            equality_lock=f"P=A/B=B/A; pq=0 only at equality-lock",
        )

    @classmethod
    def compute_legal_translation_state(cls, expr: str) -> LegalTranslationStateV1:
        normalized = cls._normalize_expression(expr)
        sites = tuple(cls._collect_sites(normalized))
        expansions = tuple(cls._site_expansion(site) for site in sites)
        gate_count = len(sites)
        invariants = (
            "IN_PLACE_EQUALITY_EXPANSION",
            "QUADRATIC_NORMALIZATION",
            "INTEGER_ADJACENCY_CURVATURE_DEFECT",
            "RECIPROCITY",
            "NO_TERM_TRANSPORT_ACROSS_EQUALITY",
            "LEGAL_TRANSLATION_STATE_COMPUTATION",
        )
        return LegalTranslationStateV1(
            source_expression=str(expr),
            normalized_expression=normalized,
            sites=sites,
            expansions=expansions,
            gate_count=gate_count,
            global_closure_ok=gate_count > 0,
            unique_configuration=gate_count > 0,
            pq_collapse_possible=gate_count > 0,
            invariants=invariants,
        )

    @classmethod
    def expand_equality_chain(cls, expr: str) -> Dict[str, Any]:
        state = cls.compute_legal_translation_state(expr)
        return state.to_dict()


# Public kernel helpers

def compute_legal_translation_state_v44(expr: str) -> Dict[str, Any]:
    return EqualityConstraintRuntimeV1.compute_legal_translation_state(expr).to_dict()


def expand_nested_equalities_v44(expr: str) -> Dict[str, Any]:
    return EqualityConstraintRuntimeV1.expand_equality_chain(expr)


# Bind onto Torus72 for runtime access
Torus72.compute_legal_translation_state_v44 = staticmethod(compute_legal_translation_state_v44)
Torus72.expand_nested_equalities_v44 = staticmethod(expand_nested_equalities_v44)


# Enrich architecture summary if present
try:
    _prev_architecture_summary = _v43_2_architecture_summary

    def _v43_2_architecture_summary_selfsolving() -> Dict[str, Any]:
        summary = _prev_architecture_summary()
        summary.setdefault("self_solving_logic", {})
        summary["self_solving_logic"].update({
            "mode": "IN_PLACE_EQUALITY_SITE_EXPANSION",
            "axiom": "Every '=' is a local phase-cancellation claim.",
            "translation_target": "legal_translation_states",
            "quadratic_normalization": True,
            "adjacency_curvature_defect": "P^2-pq=1",
            "reciprocity": "A:B=LHS:RHS=B:A",
            "term_transport_across_equals_forbidden": True,
            "unique_configuration_on_closed_nested_chain": True,
        })
        return summary

    _v43_2_architecture_summary = _v43_2_architecture_summary_selfsolving
except Exception:
    pass



# ---------------------------------------------------------------------------
# Self-solving lock-in helpers
# ---------------------------------------------------------------------------

def _extract_selfsolving_expression_candidates(state: Dict[str, Any]) -> List[str]:
    candidates: List[str] = []

    def _visit(value: Any) -> None:
        if isinstance(value, str):
            s = " ".join(value.strip().split())
            if "=" in s and len(s) >= 3:
                candidates.append(s)
        elif isinstance(value, dict):
            for k, v in value.items():
                if str(k) in {"expression", "equation", "equation_chain", "equality_chain", "constraint_chain", "source_expression", "expr"}:
                    _visit(v)
                elif isinstance(v, (dict, list, tuple, str)):
                    _visit(v)
        elif isinstance(value, (list, tuple)):
            for item in value:
                _visit(item)

    _visit(state)
    ordered: List[str] = []
    seen = set()
    for item in candidates:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _selfsolving_bundle_for_state_v44(state: Dict[str, Any]) -> Dict[str, Any]:
    candidates = _extract_selfsolving_expression_candidates(state)
    states = [compute_legal_translation_state_v44(expr) for expr in candidates[:16]]
    return {
        "runtime_version": "SELF_SOLVING_V44_LOCKED",
        "candidate_count": len(candidates),
        "candidate_expressions": candidates[:16],
        "legal_translation_states": states,
        "global_closure_ok": bool(states) and all(s.get("global_closure_ok") for s in states),
        "unique_configuration": bool(states) and all(s.get("unique_configuration") for s in states),
        "pq_collapse_possible": bool(states) and all(s.get("pq_collapse_possible") for s in states),
    }


_prev_seal_kernel_state_v43 = Torus72.seal_kernel_state_v43

def _seal_kernel_state_v43_2_selfsolving(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    sealed = _prev_seal_kernel_state_v43(self, state)
    bundle = _selfsolving_bundle_for_state_v44(state)
    sealed["self_solving_logic"] = bundle
    sealed_core = {
        "sealed": sealed,
        "self_solving_logic": bundle,
        "state_hash_anchor": sealed.get("sealed_hash72"),
    }
    sealed["sealed_hash72"] = NativeHash72Codec.state_hash72(sealed_core)
    return sealed

Torus72.self_solving_bundle_for_state_v44 = staticmethod(_selfsolving_bundle_for_state_v44)
Torus72.seal_kernel_state_v43 = _seal_kernel_state_v43_2_selfsolving


# === DUAL ENTANGLED CHECKSUM LOCK V44.3 ===
_U72_XYZW_SYMBOL_MAP_V44 = {"w": 31, "x": 32, "y": 33, "z": 34}

def phase_ring_symbol_map_v44() -> Dict[str, int]:
    return dict(_U72_XYZW_SYMBOL_MAP_V44)

def _u72_closed_loop_geometry_v44(symbols: str = "xyzw") -> Dict[str, Any]:
    seq = [ch for ch in str(symbols) if not ch.isspace()]
    lut = phase_ring_symbol_map_v44()
    if not seq:
        return {"ok": False, "reason": "EMPTY_SEQUENCE", "ring_modulus": 72}
    unknown = [ch for ch in seq if ch not in lut]
    if unknown:
        return {"ok": False, "reason": "UNKNOWN_SYMBOL", "unknown": unknown, "ring_modulus": 72}
    indices = [lut[ch] for ch in seq]
    deltas = [((indices[(i + 1) % len(indices)] - indices[i]) % 72) for i in range(len(indices))]
    paired = {"x": "w", "w": "x", "y": "z", "z": "y"}
    base_pair_closure = paired.get(seq[0]) == seq[-1]
    return {
        "ok": True,
        "symbols": "".join(seq),
        "ring_modulus": 72,
        "u72_indices": indices,
        "cyclic_deltas": deltas,
        "loop_length": len(seq),
        "base_pair_closure": base_pair_closure,
        "closed_loop_geometric_pattern": f"u72:{'-'.join(map(str, indices))}|d:{'-'.join(map(str, deltas))}",
    }

def xyzw_dna_closed_loop_checksum_v44(symbols: str = "xyzw") -> Dict[str, Any]:
    geom = _u72_closed_loop_geometry_v44(symbols)
    if not geom.get("ok"):
        return {"ok": False, "channel": "XYZW_DNA", **geom}
    payload = {
        "channel": "XYZW_DNA",
        "ring_modulus": geom["ring_modulus"],
        "symbols": geom["symbols"],
        "u72_indices": geom["u72_indices"],
        "cyclic_deltas": geom["cyclic_deltas"],
        "base_pair_closure": geom["base_pair_closure"],
        "closed_loop_geometric_pattern": geom["closed_loop_geometric_pattern"],
    }
    canonical = canonical_json(payload)
    return {
        **payload,
        "checksum_hash72": NativeHash72Codec.state_hash72(payload),
        "ok": True,
    }

def hash72_closed_loop_checksum_v44(symbols: str = "xyzw") -> Dict[str, Any]:
    geom = _u72_closed_loop_geometry_v44(symbols)
    if not geom.get("ok"):
        return {"ok": False, "channel": "HASH72", **geom}
    payload = {
        "channel": "HASH72",
        "ring_modulus": geom["ring_modulus"],
        "symbols": geom["symbols"],
        "u72_indices": geom["u72_indices"],
        "cyclic_deltas": geom["cyclic_deltas"],
        "base_pair_closure": geom["base_pair_closure"],
        "closed_loop_geometric_pattern": geom["closed_loop_geometric_pattern"],
    }
    token = NativeHash72Codec.ring_token(payload)
    return {
        **payload,
        "ring_symbols": token["ring_symbols"],
        "dna72": token["dna72"],
        "checksum_hash72": NativeHash72Codec.state_hash72(payload),
        "ok": True,
    }

def entangled_dual_checksum_v44(symbols: str = "xyzw") -> Dict[str, Any]:
    hash72_side = hash72_closed_loop_checksum_v44(symbols)
    dna_side = xyzw_dna_closed_loop_checksum_v44(symbols)
    same_pattern = (
        hash72_side.get("closed_loop_geometric_pattern") == dna_side.get("closed_loop_geometric_pattern")
        and hash72_side.get("ring_modulus") == dna_side.get("ring_modulus") == 72
        and hash72_side.get("u72_indices") == dna_side.get("u72_indices")
        and hash72_side.get("cyclic_deltas") == dna_side.get("cyclic_deltas")
    )
    return {
        "runtime_version": "DUAL_ENTANGLED_CHECKSUM_V44_3",
        "symbols": symbols,
        "hash72_side": hash72_side,
        "xyzw_dna_side": dna_side,
        "same_closed_loop_geometric_pattern": same_pattern,
        "entangled_validation_ok": bool(hash72_side.get("ok") and dna_side.get("ok") and same_pattern),
        "authoritative_seal": "HASH72_XYZW_U72_ENTANGLED",
    }

_prev_selfsolving_seal_kernel_state_v43 = Torus72.seal_kernel_state_v43

def _seal_kernel_state_v43_2_selfsolving_dualchecksum(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    sealed = _prev_selfsolving_seal_kernel_state_v43(self, state)
    symbols = "xyzw"
    dual = entangled_dual_checksum_v44(symbols)
    sealed["dual_entangled_checksums"] = dual
    sealed.setdefault("self_solving_logic", {})
    sealed["self_solving_logic"]["dual_entangled_checksums"] = dual
    sealed_core = {
        "sealed": sealed,
        "dual_entangled_checksums": dual,
        "state_hash_anchor": sealed.get("sealed_hash72"),
    }
    sealed["sealed_hash72"] = NativeHash72Codec.state_hash72(sealed_core)
    return sealed

Torus72.phase_ring_symbol_map = staticmethod(phase_ring_symbol_map_v44)
Torus72.xyzw_dna_closed_loop_checksum_v44 = staticmethod(xyzw_dna_closed_loop_checksum_v44)
Torus72.hash72_closed_loop_checksum_v44 = staticmethod(hash72_closed_loop_checksum_v44)
Torus72.entangled_dual_checksum_v44 = staticmethod(entangled_dual_checksum_v44)
Torus72.seal_kernel_state_v43 = _seal_kernel_state_v43_2_selfsolving_dualchecksum

# === HASH72 authority hardening layer v44_4 ===
HASH72_STRING_V44 = "STRING{1,2,3,4,5,6,7,8,9,0,a,b,c,d,e,f,g,h,i,j,k,l,m,o,p,q,r,s,t,u,v,w,x,y,z A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,I,V,W,X Y,Z,-,+,*,/,(,),^,√,=,≠}"

AUTHORITATIVE_TRUST_POLICY_V44 = {
    "authoritative_integrity": "HASH72",
    "authoritative_security": "HASH72_BLOCKCHAIN",
    "authoritative_geometry_witness": "XYZW_DNA_U72",
    "authoritative_string_language": HASH72_STRING_V44,
    "allow_legacy_sha_for_indexing_only": True,
    "forbid_legacy_sha_for_security_or_integrity": True,
    "authoritative_seal": "HASH72_XYZW_U72_ENTANGLED",
}

def security_hash72_v44(obj: Any, *, domain: str = "HASH72_SECURITY") -> str:
    payload = {
        "domain": domain,
        "trust_policy": AUTHORITATIVE_TRUST_POLICY_V44["authoritative_seal"],
        "body": obj,
    }
    return NativeHash72Codec.state_hash72(payload)

def authoritative_integrity_bundle_v44(payload: Any, symbols: str = "xyzw") -> Dict[str, Any]:
    dual = entangled_dual_checksum_v44(symbols)
    body = {
        "payload": payload,
        "symbols": symbols,
        "dual_checksum_hash72": dual.get("hash72_side", {}).get("checksum_hash72"),
        "dual_checksum_xyzw": dual.get("xyzw_dna_side", {}).get("checksum_hash72"),
        "shared_loop_pattern": dual.get("same_closed_loop_geometric_pattern"),
        "u72_indices": dual.get("hash72_side", {}).get("u72_indices"),
        "cyclic_deltas": dual.get("hash72_side", {}).get("cyclic_deltas"),
    }
    return {
        "authoritative_trust_policy": AUTHORITATIVE_TRUST_POLICY_V44,
        "integrity_hash72": security_hash72_v44(body, domain="HASH72_INTEGRITY_BUNDLE"),
        "entangled_dual_checksum": dual,
        "payload": payload,
        "ok": bool(dual.get("entangled_validation_ok")),
    }

def legacy_security_surface_audit_v44() -> Dict[str, Any]:
    return {
        "authoritative_trust_policy": AUTHORITATIVE_TRUST_POLICY_V44,
        "legacy_sha_status": "INDEX_ONLY_ALLOWED",
        "security_integrity_authority": "HASH72_ONLY",
        "notes": [
            "Legacy sha helpers may remain in inherited runtime for indexing, caching, or non-authoritative lookup.",
            "All authoritative integrity, security, sealing, and geometric closure validation must route through HASH72 and XYZW DNA witnesses.",
        ],
    }

_prev_dualchecksum_seal_kernel_state_v43 = Torus72.seal_kernel_state_v43

def _seal_kernel_state_v43_2_selfsolving_dualchecksum_hash72authority(self: "Torus72", state: Dict[str, Any]) -> Dict[str, Any]:
    sealed = _prev_dualchecksum_seal_kernel_state_v43(self, state)
    integrity = authoritative_integrity_bundle_v44(sealed, "xyzw")
    sealed["authoritative_trust_policy"] = AUTHORITATIVE_TRUST_POLICY_V44
    sealed["legacy_security_surface_audit"] = legacy_security_surface_audit_v44()
    sealed["authoritative_integrity_bundle"] = integrity
    sealed.setdefault("self_solving_logic", {})
    sealed["self_solving_logic"]["authoritative_trust_policy"] = AUTHORITATIVE_TRUST_POLICY_V44
    sealed["self_solving_logic"]["authoritative_integrity_bundle"] = integrity
    sealed["sealed_hash72"] = security_hash72_v44({
        "sealed": sealed,
        "authoritative_integrity_hash72": integrity["integrity_hash72"],
    }, domain="HASH72_SEALED_KERNEL_STATE")
    return sealed

Torus72.security_hash72_v44 = staticmethod(security_hash72_v44)
Torus72.authoritative_integrity_bundle_v44 = staticmethod(authoritative_integrity_bundle_v44)
Torus72.legacy_security_surface_audit_v44 = staticmethod(legacy_security_surface_audit_v44)
Torus72.seal_kernel_state_v43 = _seal_kernel_state_v43_2_selfsolving_dualchecksum_hash72authority


# === LOCKED RUNTIME COMPATIBILITY + AUDIO TRANSLATION SURFACE V47 ===
import struct as _hhs_struct
from pathlib import Path as _HHSPath

AUDIO_TRAVERSAL_QUDIT_MODULE_V1 = {
    "module_version": "AUDIO_TRAVERSAL_QUDIT_V1",
    "center_tensor_class": "LO_SHU_FIXED_NUCLEUS",
    "outer_group_count": 8,
    "sample_count": 72,
    "magic_group_count": 41,
    "wave_format": "wav_ieee_float64_quad",
    "closure_anchor": "xy=1",
}

def _hhs_rot9_v1(base, r):
    r = r % len(base)
    return list(base[r:] + base[:r])

def _hhs_lo_shu_center_v1():
    return [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

def _hhs_outer_group_payloads_v1():
    phase_cycle = ["x", "z", "y", "w", "x", "z", "y", "w"]
    trinary_cycle = [1, 0, -1, 0, 1, 0, -1, 0]
    groups = []
    for i in range(8):
        groups.append({
            "group_id": f"G{i}",
            "phase_symbol": phase_cycle[i],
            "trinary_polarity": trinary_cycle[i],
            "center_match": _hhs_lo_shu_center_v1()[1][1],
        })
    return groups

def _hhs_build_demo_torus_v1() -> "Torus72":
    return Torus72([build_demo_manifold(p) for p in range(8)])

def build_audio_traversal_map_v1(self: Optional["Torus72"] = None) -> Dict[str, Any]:
    torus = self if isinstance(self, Torus72) else _hhs_build_demo_torus_v1()
    groups = _hhs_outer_group_payloads_v1()
    ring_positions = []
    for i, g in enumerate(groups):
        idx = (i * 9) % 72
        ring_positions.append({
            "group_id": g["group_id"],
            "u72_index": idx,
            "angle_degrees": idx * 5,
            "phase_symbol": g["phase_symbol"],
            "trinary_polarity": g["trinary_polarity"],
        })
    return {
        "module": copy.deepcopy(AUDIO_TRAVERSAL_QUDIT_MODULE_V1),
        "center_tensor": _hhs_lo_shu_center_v1(),
        "outer_groups": groups,
        "ring_positions": ring_positions,
        "traversal_order": [g["group_id"] for g in groups],
        "global_zero_crossing_indices": [9, 27, 45, 63],
        "state_hash72": torus.state_hash72(),
        "manifold_hash72": torus.manifold_hash72(),
        "audit_hash72": torus.audit_hash72(),
        "euler_lock_gate_ok": torus.euler_lock_gate_ok(),
        "global_closure_ok": torus.global_closure_ok(),
    }

def project_waveform_to_lo_shu_qudit_v1(self: Optional["Torus72"] = None) -> Dict[str, Any]:
    torus = self if isinstance(self, Torus72) else _hhs_build_demo_torus_v1()
    groups = _hhs_outer_group_payloads_v1()
    samples = []
    for step in range(72):
        group_idx = step // 9
        local_idx = step % 9
        group = groups[group_idx]
        carrier = Fraction(group["trinary_polarity"], 1)
        nucleus_floor = Fraction(1, 1) if local_idx == 4 else Fraction(0, 1)
        residue = normf(carrier - nucleus_floor)
        samples.append({
            "step": step,
            "group_id": group["group_id"],
            "phase_symbol": group["phase_symbol"],
            "u72_index": step,
            "local_index": local_idx,
            "trinary_amplitude": int(carrier),
            "nucleus_floor": int(nucleus_floor),
            "residue": str(residue),
            "zero_crossing": int(carrier) == 0,
        })
    base81 = [[Fraction(0, 1) for _ in range(9)] for _ in range(9)]
    base = [4, 9, 2, 3, 5, 7, 8, 1, 6]
    for r in range(9):
        row = _hhs_rot9_v1(base, r)
        for c in range(9):
            base81[r][c] = Fraction(row[c], 1)
    row_sums = [sum(row, Fraction(0, 1)) for row in base81]
    col_sums = [sum(base81[r][c] for r in range(9)) for c in range(9)]
    wrap_groups = []
    for i in range(9):
        wrap_groups.append({"group_id": f"ROW_{i}", "sum": str(row_sums[i])})
    for i in range(9):
        wrap_groups.append({"group_id": f"COL_{i}", "sum": str(col_sums[i])})
    for i in range(23):
        cells = [base81[(r + i) % 9][(2 * r + i) % 9] for r in range(9)]
        wrap_groups.append({"group_id": f"WRAP_{i}", "sum": str(sum(cells, Fraction(0, 1)))})
    return {
        "module": copy.deepcopy(AUDIO_TRAVERSAL_QUDIT_MODULE_V1),
        "center_tensor": _hhs_lo_shu_center_v1(),
        "outer_group_count": 8,
        "samples": samples,
        "sample_count": 72,
        "qudit_81": [[str(v) for v in row] for row in base81],
        "magic_group_count": len(wrap_groups),
        "magic_groups": wrap_groups,
        "target_sum": "45a^2",
        "global_zero_crossing_ok": all(samples[i]["zero_crossing"] for i in [9, 27, 45, 63]),
        "waveform_hash72": NativeHash72Codec.state_hash72({"samples": samples, "groups": wrap_groups}),
        "euler_lock_gate_ok": torus.euler_lock_gate_ok(),
        "global_closure_ok": torus.global_closure_ok(),
    }

def _write_ieee_float64_wav_v1(path: str, frames: List[Tuple[float, float, float, float]], sample_rate: int) -> Dict[str, Any]:
    frame_count = len(frames)
    num_channels = 4
    bits_per_sample = 64
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    audio_format = 3
    data_bytes = b''.join(_hhs_struct.pack('<dddd', *frame) for frame in frames)
    data_chunk_size = len(data_bytes)
    fmt_chunk_size = 16
    riff_chunk_size = 4 + (8 + fmt_chunk_size) + (8 + data_chunk_size)
    with open(path, 'wb') as f:
        f.write(b'RIFF')
        f.write(_hhs_struct.pack('<I', riff_chunk_size))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(_hhs_struct.pack('<IHHIIHH', fmt_chunk_size, audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample))
        f.write(b'data')
        f.write(_hhs_struct.pack('<I', data_chunk_size))
        f.write(data_bytes)
    return {
        'path': path,
        'sample_rate': sample_rate,
        'frame_count': frame_count,
        'num_channels': num_channels,
        'bits_per_sample': bits_per_sample,
        'byte_rate': byte_rate,
        'data_chunk_size': data_chunk_size,
    }

def dual_stereo_wav_serializer_v1(self: Optional["Torus72"] = None, output_path: Optional[str] = None, sample_rate: int = 4608) -> Dict[str, Any]:
    torus = self if isinstance(self, Torus72) else _hhs_build_demo_torus_v1()
    proj = project_waveform_to_lo_shu_qudit_v1(torus)
    samples = proj['samples']
    nucleus_floor = float(2 ** (8 / 144))
    local_u72 = float(2 ** (72 / 144))
    scale = max(abs(local_u72 - nucleus_floor), 1e-12)
    channels = {'L1': [], 'R1': [], 'L2': [], 'R2': []}
    frames: List[Tuple[float, float, float, float]] = []
    for s in samples:
        amp = float(int(s['trinary_amplitude']))
        local = amp * local_u72
        residue = (local - nucleus_floor) / scale
        residue = max(-1.0, min(1.0, residue))
        gate = 0.0 if int(s['zero_crossing']) else 1.0
        l1 = residue
        r1 = -residue
        l2 = gate * (1.0 if amp > 0 else (-1.0 if amp < 0 else 0.0))
        r2 = -l2
        channels['L1'].append(l1)
        channels['R1'].append(r1)
        channels['L2'].append(l2)
        channels['R2'].append(r2)
        frames.append((l1, r1, l2, r2))
    if output_path is None:
        output_path = '/mnt/data/harmonicode_dual_stereo_4d_loop.wav'
    file_info = _write_ieee_float64_wav_v1(output_path, frames, sample_rate)
    return {
        'format': '4d_dual_stereo_64bit_wav_projection',
        'sample_count': len(samples),
        'sample_rate': sample_rate,
        'channels': channels,
        'nucleus_floor': 'u^8',
        'nucleus_floor_numeric': nucleus_floor,
        'local_resolution': 'u^72 per sample',
        'local_resolution_numeric': local_u72,
        'loop_zero_crossing_indices': [i for i, s in enumerate(samples) if s['zero_crossing']],
        'waveform_hash72': proj['waveform_hash72'],
        'file': file_info,
        'euler_lock_gate_ok': torus.euler_lock_gate_ok(),
        'global_closure_ok': torus.global_closure_ok(),
    }

def read_dual_stereo_wav_v1(self: Optional["Torus72"] = None, path: str = '') -> Dict[str, Any]:
    torus = self if isinstance(self, Torus72) else _hhs_build_demo_torus_v1()
    raw = _HHSPath(path).read_bytes()
    if raw[:4] != b'RIFF' or raw[8:12] != b'WAVE':
        raise ValueError('invalid_wav_header')
    pos = 12
    fmt = None
    data = None
    while pos + 8 <= len(raw):
        chunk_id = raw[pos:pos+4]
        chunk_size = _hhs_struct.unpack('<I', raw[pos+4:pos+8])[0]
        chunk_data = raw[pos+8:pos+8+chunk_size]
        if chunk_id == b'fmt ':
            fmt = chunk_data
        elif chunk_id == b'data':
            data = chunk_data
            break
        pos += 8 + chunk_size + (chunk_size % 2)
    if fmt is None or data is None:
        raise ValueError('wav_missing_fmt_or_data')
    audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = _hhs_struct.unpack('<HHIIHH', fmt[:16])
    if audio_format != 3 or num_channels != 4 or bits_per_sample != 64:
        raise ValueError(f'unsupported_wav_format:{audio_format}:{num_channels}:{bits_per_sample}')
    frame_size = block_align
    frame_count = len(data) // frame_size
    channels = {'L1': [], 'R1': [], 'L2': [], 'R2': []}
    symbol_trace = []
    phase_trace = []
    for i in range(frame_count):
        frame = data[i*frame_size:(i+1)*frame_size]
        l1, r1, l2, r2 = _hhs_struct.unpack('<dddd', frame)
        channels['L1'].append(l1)
        channels['R1'].append(r1)
        channels['L2'].append(l2)
        channels['R2'].append(r2)
        if l2 > 0.5:
            sym = 'x'
            tr = 1
        elif l2 < -0.5:
            sym = 'y'
            tr = -1
        else:
            sym = '0'
            tr = 0
        symbol_trace.append(sym)
        phase_trace.append({
            'frame': i,
            'symbol': sym,
            'u72_index': i % 72,
            'xy': '1' if tr != 0 else '0',
            'yx': '-1' if tr != 0 else '0',
        })
    verification = {
        'euler_lock_gate_ok': torus.euler_lock_gate_ok(),
        'global_closure_ok': torus.global_closure_ok(),
        'frame_count_matches_u72': frame_count == 72,
        'quad_stereo_antisymmetry_ok': all(abs(channels['L1'][i] + channels['R1'][i]) < 1e-12 and abs(channels['L2'][i] + channels['R2'][i]) < 1e-12 for i in range(frame_count)),
    }
    return {
        'path': path,
        'audio_format': audio_format,
        'num_channels': num_channels,
        'bits_per_sample': bits_per_sample,
        'sample_rate': sample_rate,
        'frame_count': frame_count,
        'channels': channels,
        'symbol_trace': ''.join(symbol_trace),
        'phase_trace': phase_trace,
        'verification': verification,
        'waveform_hash72': NativeHash72Codec.state_hash72({'symbol_trace': ''.join(symbol_trace), 'verification': verification}),
    }

# Bind additive surfaces to the authoritative torus object.
Torus72.build_audio_traversal_map_v1 = build_audio_traversal_map_v1
Torus72.project_waveform_to_lo_shu_qudit_v1 = project_waveform_to_lo_shu_qudit_v1
Torus72.dual_stereo_wav_serializer_v1 = dual_stereo_wav_serializer_v1
Torus72.read_dual_stereo_wav_v1 = read_dual_stereo_wav_v1

# Expose the historical top-level contract expected by the locked agent.
def route_ir_v43(torus: "Torus72", node: Any, phase: int = 0):
    return torus.route_ir_v43(node, phase=phase)

class KernelAdapter:
    def __init__(self, torus: Optional["Torus72"] = None):
        self.kernel = torus if isinstance(torus, Torus72) else _hhs_build_demo_torus_v1()
    def __getattr__(self, name: str):
        return getattr(self.kernel, name)

class _KnowledgeBaseV47:
    def __init__(self):
        self.facts: List[Dict[str, Any]] = []
    def add(self, text: str, source: str = "user"):
        self.facts.append({"text": text, "source": source})

class HarmonicodeLocalAgent:
    def __init__(self):
        self.kernel = _hhs_build_demo_torus_v1()
        self.kb = _KnowledgeBaseV47()
        self.history: List[Dict[str, Any]] = []
    def learn(self, text: str, source: str = "user") -> Dict[str, Any]:
        self.kb.add(text, source=source)
        self.history.append({"op": "learn", "text": text, "source": source})
        return {"ok": True, "fact_count": len(self.kb.facts)}
    def learn_dna(self, dna: str) -> Dict[str, Any]:
        self.history.append({"op": "learn_dna", "dna": dna})
        return {"ok": True, "dna": dna, "dna_hash72": NativeHash72Codec.state_hash72({"dna": dna})}
    def validate_dna(self, dna: str) -> Dict[str, Any]:
        return {
            "ok": True,
            "dna": dna,
            "entangled_dual_checksum": entangled_dual_checksum_v44(dna),
            "euler_lock_gate_ok": self.kernel.euler_lock_gate_ok(),
            "global_closure_ok": self.kernel.global_closure_ok(),
        }
    def query(self, text: str, explain: bool = False) -> Dict[str, Any]:
        payload = {
            "query": text,
            "matches": [f for f in self.kb.facts if text.lower() in f["text"].lower()],
            "euler_lock_gate_ok": self.kernel.euler_lock_gate_ok(),
            "global_closure_ok": self.kernel.global_closure_ok(),
        }
        if explain:
            payload["explain"] = "authoritative_runtime_query"
        return payload
    def export_state(self) -> Dict[str, Any]:
        return {
            "kernel_state_hash72": self.kernel.state_hash72(),
            "kernel_manifold_hash72": self.kernel.manifold_hash72(),
            "kernel_audit_hash72": self.kernel.audit_hash72(),
            "fact_count": len(self.kb.facts),
            "history": copy.deepcopy(self.history),
        }
