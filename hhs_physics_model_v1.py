"""
hhs_physics_model_v1.py

HHS Physics Model V1: real-world physical-system adapter for the HARMONICODE
runtime stack.

Purpose
-------
Map observed physical variables into typed HHS carrier states, commit symbolic
constraint witnesses, apply deterministic state patches, and emit Hash72-locked
runtime receipts.

Default flow:
    physical observation / model step
    -> typed carrier projection
    -> symbolic constraint witness
    -> deterministic state patch
    -> kernel audit through HHSStateLayerV1 / AuditedRunner
    -> Hash72 receipt / quarantine report

Design rules
------------
- No scalar collapse of ordered products.
- No commutation of ordered carrier paths.
- Equality is represented as a witness constraint, not a Boolean primitive.
- Real-valued inputs are converted to exact Fractions whenever possible.
- The locked kernel remains authoritative; this module is an additive model layer.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import argparse
import json
import math
import time

from hhs_general_runtime_layer_v1 import DEFAULT_KERNEL_PATH, AuditedRunner, canonicalize_for_hash72
from hhs_state_layer_v1 import HHSStateLayerV1, StatePatch
from terminal_hhsprog_v5_macro_algebra import HHSMacroAlgebraTerminalV5
from hhs_receipt_replay_verifier_v1 import HHSReceiptReplayVerifierV1


PHYSICS_MODEL_VERSION = "HHS_PHYSICS_MODEL_V1"

# Canonical carrier slots. These are typed roles, not scalar substitutions.
DEFAULT_CARRIER_ROLES: Dict[str, str] = {
    "pressure": "x",
    "gradient": "y",
    "charge": "xy",
    "flow": "yx",
    "mass": "z",
    "curvature": "w",
    "entropy": "zw",
    "temperature": "wz",
    "energy": "O",
    "potential": "φ",
}

# Ordered-product guards. These are kept as symbolic constraints and never used
# as global rewrite rules.
LOCK_CORE_GUARDS: List[str] = [
    "x==1/y",
    "y==-x",
    "z==1/w",
    "w==-z",
    "xy≠yx",
    "zw≠wz",
    "xy==1/zw==-yx",
    "zw==1/xy==-wz",
]

MUTATION_ATTRACTOR_GUARDS: List[str] = [
    "xz==xy",
    "zx==zw",
    "yw==yx",
    "wy==wz",
]


class HHSPhysicsModelError(RuntimeError):
    pass


def fraction_from_any(value: Any) -> Fraction:
    """Convert numbers/decimal strings into exact Fraction values."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        # Use string form to avoid importing binary64 noise into the model layer.
        return Fraction(str(value))
    if isinstance(value, str):
        text = value.strip()
        if "/" in text:
            return Fraction(text)
        return Fraction(text)
    raise TypeError(f"Cannot convert {type(value).__name__} to Fraction")


def fraction_to_token(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def stable_name(name: str) -> str:
    out = []
    for ch in str(name):
        if ch.isalnum() or ch in {"_", "-"}:
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out).strip("_")
    return s or "unnamed"


@dataclass(frozen=True)
class PhysicalQuantityV1:
    name: str
    value: str
    unit: str
    role: str
    carrier: str
    phase_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        name: str,
        value: Any,
        unit: str,
        role: str,
        carrier: Optional[str] = None,
        phase_index: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "PhysicalQuantityV1":
        q = fraction_from_any(value)
        resolved_carrier = carrier or DEFAULT_CARRIER_ROLES.get(role, role)
        # Deterministic phase address: role/carrier/name/value all contribute.
        phase_seed = sum(ord(c) for c in f"{name}|{role}|{resolved_carrier}|{fraction_to_token(q)}") % 72
        return cls(
            name=str(name),
            value=fraction_to_token(q),
            unit=str(unit),
            role=str(role),
            carrier=str(resolved_carrier),
            phase_index=int(phase_index if phase_index is not None else phase_seed) % 72,
            metadata=dict(metadata or {}),
        )

    def fraction(self) -> Fraction:
        return fraction_from_any(self.value)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhysicsConstraintV1:
    name: str
    source: str
    kind: str = "SYMBOLIC_WITNESS"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhysicsStepReportV1:
    ok: bool
    model: str
    action: str
    state_result: Dict[str, Any]
    symbolic_result: Optional[Dict[str, Any]] = None
    runtime_result: Optional[Dict[str, Any]] = None
    witness: Dict[str, Any] = field(default_factory=dict)
    quarantine: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSPhysicsModelV1:
    """
    Additive physics modeling layer over the existing HHS runtime.

    This class owns no foundational authority. It only converts physical-model
    operations into HHS state patches and symbolic witnesses.
    """

    def __init__(
        self,
        *,
        kernel_path: str | Path = DEFAULT_KERNEL_PATH,
        model_name: str = "HHS_PHYSICAL_SYSTEM",
        initial_state: Optional[Dict[str, Any]] = None,
    ):
        self.kernel_path = Path(kernel_path)
        self.model_name = model_name
        self.runner = AuditedRunner(self.kernel_path)
        self.state_layer = HHSStateLayerV1(
            initial_state=initial_state or self._genesis_state(),
            runner=self.runner,
            kernel_path=self.kernel_path,
        )
        self.terminal = HHSMacroAlgebraTerminalV5(self.kernel_path)
        self.reports: List[Dict[str, Any]] = []
        self._install_physics_macros()

    def _genesis_state(self) -> Dict[str, Any]:
        return {
            "model_version": PHYSICS_MODEL_VERSION,
            "model_name": self.model_name,
            "created_at": time.time(),
            "lock_core_guards": list(LOCK_CORE_GUARDS),
            "mutation_attractor_guards": list(MUTATION_ATTRACTOR_GUARDS),
            "quantities": {},
            "constraints": {},
            "steps": [],
            "invariants": {
                "delta_e": "0",
                "psi": "0",
                "theta15": True,
                "omega": True,
                "projection_rule": "scalar_projection_after_closure_only",
            },
        }

    def _install_physics_macros(self) -> None:
        macros = [
            "DEF PHYS_BALANCE(a,b,c) := c^2-a^2==b^2",
            "DEF PHYS_RECIP_LOCK(x,y) := x==1/y==(-y)",
            "DEF PHYS_ORDERED_PRODUCT(lhs,rhs) := lhs≠rhs",
            "DEF PHYS_FLOW_BALANCE(x,y,z,w,xy,zw) := x+y+z+w+xy+zw==0",
            "DEF PHYS_CARRIER(role,carrier,value,unit,phase) := List(role,carrier,value,unit,phase)",
            "DEF PHYS_CLOSURE(p,q,defect) := p^2-q==defect",
        ]
        for src in macros:
            result = self.terminal.dispatch(src)
            if not result.get("ok"):
                # Macro installation failure is serious but should remain local to
                # this additive layer. Preserve the failure as a report.
                self.reports.append({"macro_install_failed": src, "result": result})

    @property
    def authority(self):
        return self.runner.authority

    def carrier_projection(self, quantity: PhysicalQuantityV1) -> Dict[str, Any]:
        """Create a typed carrier projection without scalar substitution."""
        q = quantity.fraction()
        carrier_payload = {
            "model": PHYSICS_MODEL_VERSION,
            "quantity": quantity.to_dict(),
            "ordered_product_policy": {
                "do_not_commute": True,
                "do_not_substitute_across_ordered_products": True,
                "witness_equality_not_boolean": True,
            },
            "carrier_statement": f"{quantity.carrier}@u^{quantity.phase_index} := {fraction_to_token(q)} {quantity.unit}",
            "lock_core_guards": list(LOCK_CORE_GUARDS),
        }
        return {
            **carrier_payload,
            "carrier_hash72": self.authority.commit(carrier_payload, domain="HHS_PHYSICS_CARRIER"),
        }

    def commit_symbolic_constraint(self, constraint: PhysicsConstraintV1) -> Dict[str, Any]:
        return self.terminal.dispatch(constraint.source)

    def observe(
        self,
        name: str,
        value: Any,
        unit: str = "unit",
        *,
        role: str = "observable",
        carrier: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add or update one physical quantity as an audited state patch."""
        quantity = PhysicalQuantityV1.create(
            name=name,
            value=value,
            unit=unit,
            role=role,
            carrier=carrier,
            metadata=metadata,
        )
        projection = self.carrier_projection(quantity)
        path = f"quantities.{stable_name(name)}"
        value_payload = {
            "quantity": quantity.to_dict(),
            "projection": projection,
        }
        state_result = self.state_layer.set(
            path,
            value_payload,
            action="OBSERVE_PHYSICAL_QUANTITY",
            model=PHYSICS_MODEL_VERSION,
        )
        witness = {
            "quantity": quantity.to_dict(),
            "projection_hash72": projection["carrier_hash72"],
            "state_hash72": state_result.get("snapshot", {}).get("state_hash72"),
        }
        report = PhysicsStepReportV1(
            ok=bool(state_result.get("ok")),
            model=self.model_name,
            action="OBSERVE",
            state_result=state_result,
            witness=witness,
            quarantine=bool(state_result.get("quarantine")),
            reason=state_result.get("reason", ""),
        ).to_dict()
        self.reports.append(report)
        return report

    def add_constraint(
        self,
        name: str,
        source: str,
        *,
        kind: str = "SYMBOLIC_WITNESS",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Commit a symbolic physics constraint and persist it into state."""
        constraint = PhysicsConstraintV1(name=name, source=source, kind=kind, metadata=dict(metadata or {}))
        symbolic_result = self.commit_symbolic_constraint(constraint)
        constraint_payload = {
            "constraint": constraint.to_dict(),
            "symbolic_result": symbolic_result,
        }
        state_result = self.state_layer.set(
            f"constraints.{stable_name(name)}",
            constraint_payload,
            action="ADD_PHYSICS_CONSTRAINT",
            model=PHYSICS_MODEL_VERSION,
        )
        ok = bool(symbolic_result.get("ok")) and bool(state_result.get("ok"))
        report = PhysicsStepReportV1(
            ok=ok,
            model=self.model_name,
            action="ADD_CONSTRAINT",
            symbolic_result=symbolic_result,
            state_result=state_result,
            witness={
                "constraint": constraint.to_dict(),
                "symbolic_hash72": symbolic_result.get("symbolic_hash72")
                or (symbolic_result.get("expanded_symbolic_commit") or {}).get("symbolic_hash72"),
            },
            quarantine=not ok,
            reason="" if ok else (symbolic_result.get("message") or symbolic_result.get("error") or state_result.get("reason", "constraint failed")),
        ).to_dict()
        self.reports.append(report)
        return report

    def balance_constraint_from_roles(
        self,
        *,
        name: str = "mass_equilibrium",
        roles: Sequence[str] = ("pressure", "gradient", "mass", "curvature", "charge", "entropy"),
    ) -> Dict[str, Any]:
        """
        Create a default HHS-style physical balance witness from carrier roles.
        The emitted expression preserves ordered products as names.
        """
        state_quantities = self.state_layer.get("quantities", {}) or {}
        role_to_carrier = {}
        for rec in state_quantities.values():
            q = (rec or {}).get("quantity", {})
            role_to_carrier[q.get("role")] = q.get("carrier")
        carriers = [role_to_carrier.get(role, DEFAULT_CARRIER_ROLES.get(role, role)) for role in roles]
        while len(carriers) < 6:
            carriers.append(f"q{len(carriers)}")
        source = f"{carriers[0]}+{carriers[1]}+{carriers[2]}+{carriers[3]}+{carriers[4]}+{carriers[5]}==0"
        return self.add_constraint(name, source, kind="PHYSICAL_BALANCE_WITNESS", metadata={"roles": list(roles), "carriers": carriers})

    def step_euler_exact(
        self,
        *,
        target: str,
        rate: Any,
        dt: Any,
        unit: str = "unit",
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deterministic exact Euler-style state update:
            target_next = target + rate * dt
        This is a host-level model update; the committed witness preserves the
        symbolic transition and the state layer audits the resulting patch.
        """
        current_record = self.state_layer.get(f"quantities.{stable_name(target)}")
        if not current_record:
            return {
                "ok": False,
                "quarantine": True,
                "reason": f"unknown target quantity: {target}",
                "model": self.model_name,
                "action": "STEP_EULER_EXACT",
            }
        q = PhysicalQuantityV1.create(**current_record["quantity"])
        next_value = q.fraction() + fraction_from_any(rate) * fraction_from_any(dt)
        step_witness_source = (
            f"{q.carrier}_next=={q.carrier}+({fraction_to_token(fraction_from_any(rate))}*{fraction_to_token(fraction_from_any(dt))})"
        )
        symbolic_result = self.commit_symbolic_constraint(
            PhysicsConstraintV1(
                name=f"{target}_euler_step",
                source=step_witness_source,
                kind="EXACT_UPDATE_WITNESS",
                metadata={"target": target, "rate": str(rate), "dt": str(dt)},
            )
        )
        observe_report = self.observe(
            target,
            next_value,
            unit,
            role=role or q.role,
            carrier=q.carrier,
            metadata={"update": "EULER_EXACT", "rate": str(rate), "dt": str(dt), "previous": q.to_dict()},
        )
        ok = bool(symbolic_result.get("ok")) and bool(observe_report.get("ok"))
        report = PhysicsStepReportV1(
            ok=ok,
            model=self.model_name,
            action="STEP_EULER_EXACT",
            state_result=observe_report.get("state_result", observe_report),
            symbolic_result=symbolic_result,
            witness={"source": step_witness_source, "next_value": fraction_to_token(next_value)},
            quarantine=not ok,
            reason="" if ok else (symbolic_result.get("message") or observe_report.get("reason", "step failed")),
        ).to_dict()
        self.reports.append(report)
        return report

    def snapshot(self) -> Dict[str, Any]:
        terminal_chain = self.terminal.runner.commitments.verify_chain()
        runtime_chain = self.runner.commitments.verify_chain()
        return {
            "model": self.model_name,
            "model_version": PHYSICS_MODEL_VERSION,
            "state": self.state_layer.snapshot(),
            "reports_count": len(self.reports),
            "runtime_chain": runtime_chain,
            "terminal_chain": terminal_chain,
            "state_history": [r.to_dict() for r in self.state_layer.history],
        }

    def verify(self) -> Dict[str, Any]:
        state_replay = self.state_layer.replay_from_history()
        runtime_replay = HHSReceiptReplayVerifierV1(self.kernel_path).verify_runner(self.runner).to_dict()
        terminal_replay = HHSReceiptReplayVerifierV1(self.kernel_path).verify_runner(self.terminal.runner).to_dict()
        return {
            "ok": bool(state_replay.get("ok")) and bool(runtime_replay.get("ok")) and bool(terminal_replay.get("ok")),
            "state_replay": state_replay,
            "runtime_replay": runtime_replay,
            "terminal_replay": terminal_replay,
        }

    def save_report(self, path: str | Path) -> Dict[str, Any]:
        path = Path(path)
        payload = {
            "format": "HHS_PHYSICS_MODEL_RUN_V1",
            "snapshot": self.snapshot(),
            "verify": self.verify(),
            "reports": self.reports,
            "state_layer_history": [r.to_dict() for r in self.state_layer.history],
            "state_runner_receipts": [r.to_dict() for r in self.runner.commitments.receipts],
            "terminal_receipts": [r.to_dict() for r in self.terminal.runner.commitments.receipts],
        }
        path.write_text(json.dumps(canonicalize_for_hash72(payload), indent=2, ensure_ascii=False), encoding="utf-8")
        return {"ok": True, "saved": str(path), "verify_ok": payload["verify"].get("ok")}


def demo() -> Dict[str, Any]:
    model = HHSPhysicsModelV1(model_name="ELECTROCHEMICAL_FLUIDIC_DEMO")
    reports = []
    reports.append(model.observe("membrane_pressure", "9/4", "kPa", role="pressure"))
    reports.append(model.observe("ion_gradient", "-9/4", "mV", role="gradient"))
    reports.append(model.observe("channel_charge", "1", "carrier", role="charge"))
    reports.append(model.observe("reverse_flow", "-1", "carrier", role="flow"))
    reports.append(model.observe("folding_mass", "5/2", "relative", role="mass"))
    reports.append(model.observe("local_curvature", "-5/2", "relative", role="curvature"))
    reports.append(model.add_constraint("lock_core", "x==1/y==(-y)"))
    reports.append(model.add_constraint("ordered_product_guard", "xy≠yx≠zw≠wz"))
    reports.append(model.add_constraint("closure_carrier", "xyzw==1"))
    reports.append(model.balance_constraint_from_roles())
    reports.append(model.step_euler_exact(target="membrane_pressure", rate="1/8", dt="2", unit="kPa", role="pressure"))
    save = model.save_report("/mnt/data/hhs_physics_model_v1_demo_report.json")
    return {"ok": all(bool(r.get("ok")) for r in reports), "reports": reports, "save": save, "verify": model.verify()}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="HHS Physics Model V1")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("demo")
    args = parser.parse_args(argv)
    if args.cmd in {None, "demo"}:
        print(json.dumps(demo(), indent=2, ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
