"""
hhs_physics_evolution_v1.py

Physical Evolution Operator for the HHS runtime stack.

Purpose
-------
Turn the HHS physics layer from observation-only into deterministic physical
state propagation.

Flow:
    current audited physics state
    -> read typed carriers
    -> build symbolic evolution witness
    -> generate candidate next-state patch
    -> submit to HHSStateLayerV1
    -> kernel audit / Hash72 receipt
    -> accept or quarantine

Design rules:
- This layer does not replace hhs_physics_model_v1.py.
- This layer does not redefine kernel truth.
- This layer proposes candidate evolution patches only.
- HHSStateLayerV1 / AuditedRunner / kernel Hash72 remain authoritative.
- Ordered carriers are preserved; xy and yx are never commuted.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json
import time

from hhs_general_runtime_layer_v1 import DEFAULT_KERNEL_PATH
from hhs_state_layer_v1 import HHSStateLayerV1, StatePatch
from hhs_physics_model_v1 import (
    HHSPhysicsModelV1,
    fraction_from_any,
    fraction_to_token,
    stable_name,
)
from hhs_receipt_replay_verifier_v1 import HHSReceiptReplayVerifierV1


PHYSICS_EVOLUTION_VERSION = "HHS_PHYSICS_EVOLUTION_V1"


@dataclass(frozen=True)
class EvolutionRuleV1:
    name: str
    source_role: str
    target_role: str
    coupling: str
    constraint: str
    metadata: Dict[str, Any]

    def coupling_fraction(self) -> Fraction:
        return fraction_from_any(self.coupling)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvolutionStepV1:
    step_index: int
    dt: str
    parent_state_hash72: str
    next_state_hash72: str
    patch_hash72: str
    receipt_hash72: str
    locked: bool
    quarantine: bool
    reason: str
    witness: Dict[str, Any]
    created_at: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSPhysicsEvolutionV1:
    """Deterministic physical evolution operator over HHSPhysicsModelV1."""

    def __init__(self, model: HHSPhysicsModelV1):
        self.model = model
        self.state_layer: HHSStateLayerV1 = model.state_layer
        self.runner = model.runner
        self.terminal = model.terminal
        self.rules: Dict[str, EvolutionRuleV1] = {}
        self.steps: List[EvolutionStepV1] = []
        self._install_default_macros()

    def _install_default_macros(self) -> None:
        macros = [
            "DEF PHYS_EVOLVE(src,tgt,k,dt) := tgt==tgt+(src*k*dt)",
            "DEF PHYS_DECAY(src,k,dt) := src==src-(src*k*dt)",
            "DEF PHYS_BALANCE_STEP(src,tgt,k,dt) := List(src,tgt,k,dt)",
            "DEF PHYS_STEP_LOCK(parent,next,dt) := List(parent,next,dt)==List(parent,next,dt)",
        ]
        for macro in macros:
            self.terminal.dispatch(macro)

    def add_rule(
        self,
        name: str,
        source_role: str,
        target_role: str,
        coupling: Any,
        *,
        constraint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        rule = EvolutionRuleV1(
            name=stable_name(name),
            source_role=source_role,
            target_role=target_role,
            coupling=fraction_to_token(fraction_from_any(coupling)),
            constraint=constraint or "PHYS_EVOLVE(src,tgt,k,dt)",
            metadata=dict(metadata or {}),
        )
        self.rules[rule.name] = rule

        symbolic = self.terminal.dispatch(f"DEF RULE_{rule.name}() := {rule.constraint}")

        state_result = self.state_layer.set(
            f"evolution.rules.{rule.name}",
            rule.to_dict(),
            action="ADD_EVOLUTION_RULE",
            model=PHYSICS_EVOLUTION_VERSION,
        )

        return {
            "ok": bool(state_result.get("ok")) and bool(symbolic.get("ok")),
            "rule": rule.to_dict(),
            "symbolic_result": symbolic,
            "state_result": state_result,
        }

    def quantities(self) -> Dict[str, Dict[str, Any]]:
        return self.state_layer.get("quantities", {}) or {}

    @staticmethod
    def quantity_value(payload: Dict[str, Any]) -> Fraction:
        return fraction_from_any(payload["quantity"]["value"])

    @staticmethod
    def update_quantity_value(payload: Dict[str, Any], new_value: Fraction) -> Dict[str, Any]:
        updated = json.loads(json.dumps(payload))
        token = fraction_to_token(new_value)
        updated["quantity"]["value"] = token
        updated["projection"]["quantity"]["value"] = token
        carrier = updated["quantity"]["carrier"]
        phase = updated["quantity"]["phase_index"]
        unit = updated["quantity"]["unit"]
        updated["projection"]["carrier_statement"] = f"{carrier}@u^{phase} := {token} {unit}"
        return updated

    def build_candidate_state(self, dt: Fraction) -> tuple[Dict[str, Any], Dict[str, Any]]:
        current_state = self.state_layer.get(".", {}) or {}
        candidate = json.loads(json.dumps(current_state))
        quantities = candidate.get("quantities", {})
        witness_rules = []

        for rule in self.rules.values():
            src_item = None
            tgt_item = None

            for name, payload in quantities.items():
                q = payload.get("quantity", {})
                if q.get("role") == rule.source_role:
                    src_item = (name, payload)
                if q.get("role") == rule.target_role:
                    tgt_item = (name, payload)

            if src_item is None or tgt_item is None:
                witness_rules.append({
                    "rule": rule.to_dict(),
                    "applied": False,
                    "reason": "source_or_target_role_missing",
                })
                continue

            src_name, src_payload = src_item
            tgt_name, tgt_payload = tgt_item
            src_val = self.quantity_value(src_payload)
            tgt_val = self.quantity_value(tgt_payload)
            k = rule.coupling_fraction()

            delta = src_val * k * dt
            next_val = tgt_val + delta
            quantities[tgt_name] = self.update_quantity_value(tgt_payload, next_val)

            symbolic_source = (
                f"PHYS_EVOLVE({src_payload['quantity']['carrier']},"
                f"{tgt_payload['quantity']['carrier']},"
                f"{fraction_to_token(k)},{fraction_to_token(dt)})"
            )
            symbolic_result = self.terminal.dispatch(symbolic_source)

            witness_rules.append({
                "rule": rule.to_dict(),
                "applied": True,
                "source_quantity": src_name,
                "target_quantity": tgt_name,
                "source_value": fraction_to_token(src_val),
                "target_before": fraction_to_token(tgt_val),
                "delta": fraction_to_token(delta),
                "target_after": fraction_to_token(next_val),
                "symbolic_source": symbolic_source,
                "symbolic_result": symbolic_result,
            })

        candidate["quantities"] = quantities
        candidate.setdefault("steps", [])
        candidate["steps"].append({
            "evolution_version": PHYSICS_EVOLUTION_VERSION,
            "dt": fraction_to_token(dt),
            "rule_count": len(self.rules),
            "applied_count": sum(1 for r in witness_rules if r.get("applied")),
            "created_at": time.time(),
        })

        witness = {
            "evolution_version": PHYSICS_EVOLUTION_VERSION,
            "dt": fraction_to_token(dt),
            "parent_state_hash72": self.state_layer.state_hash72,
            "rules": witness_rules,
        }
        return candidate, witness

    def step(self, dt: Any = 1) -> Dict[str, Any]:
        dt_q = fraction_from_any(dt)
        parent_hash = self.state_layer.state_hash72
        candidate, witness = self.build_candidate_state(dt_q)

        patch = StatePatch(
            op="SET",
            path=".",
            value=candidate,
            metadata={
                "action": "PHYSICS_EVOLUTION_STEP",
                "model": PHYSICS_EVOLUTION_VERSION,
                "dt": fraction_to_token(dt_q),
            },
        )

        state_result = self.state_layer.apply_patch(patch)
        transition = state_result.get("transition", {})

        step_record = EvolutionStepV1(
            step_index=len(self.steps),
            dt=fraction_to_token(dt_q),
            parent_state_hash72=parent_hash,
            next_state_hash72=transition.get("state_hash72", parent_hash),
            patch_hash72=transition.get("patch_hash72", ""),
            receipt_hash72=transition.get("receipt_hash72", ""),
            locked=bool(state_result.get("ok")),
            quarantine=bool(state_result.get("quarantine")),
            reason=state_result.get("reason", ""),
            witness=witness,
            created_at=time.time(),
        )
        self.steps.append(step_record)

        return {
            "ok": step_record.locked,
            "quarantine": step_record.quarantine,
            "reason": step_record.reason,
            "evolution_step": step_record.to_dict(),
            "state_result": state_result,
            "replay": self.state_layer.replay_from_history(),
        }

    def run(self, steps: int, dt: Any = 1) -> Dict[str, Any]:
        reports = []
        for _ in range(int(steps)):
            report = self.step(dt)
            reports.append(report)
            if not report.get("ok"):
                break
        return {
            "ok": all(r.get("ok") for r in reports),
            "steps_requested": int(steps),
            "steps_completed": len(reports),
            "reports": reports,
            "state_snapshot": self.state_layer.snapshot(),
            "receipt_chain": self.runner.commitments.verify_chain(),
        }

    def save(self, path: str | Path) -> Dict[str, Any]:
        path = Path(path)
        payload = {
            "format": "HHS_PHYSICS_EVOLUTION_RUN_V1",
            "evolution_version": PHYSICS_EVOLUTION_VERSION,
            "model_name": self.model.model_name,
            "rules": {k: v.to_dict() for k, v in self.rules.items()},
            "steps": [s.to_dict() for s in self.steps],
            "state_snapshot": self.state_layer.snapshot(),
            "state_history": [h.to_dict() for h in self.state_layer.history],
            "receipts": [r.to_dict() for r in self.runner.commitments.receipts],
            "chain": self.runner.commitments.verify_chain(),
            "replay": HHSReceiptReplayVerifierV1(self.model.kernel_path).verify_runner(self.runner).to_dict(),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return {
            "ok": True,
            "saved": str(path),
            "step_count": len(self.steps),
            "state_hash72": self.state_layer.state_hash72,
            "tip_hash72": self.runner.commitments.tip_hash72,
        }


def demo() -> Dict[str, Any]:
    model = HHSPhysicsModelV1(model_name="EVOLUTION_DEMO")
    model.observe("pressure", "9/4", "kPa", role="pressure")
    model.observe("gradient", "-9/4", "mV", role="gradient")
    model.observe("charge", "1", "carrier", role="charge")
    model.observe("flow", "-1", "carrier", role="flow")

    evo = HHSPhysicsEvolutionV1(model)
    rule_a = evo.add_rule("pressure_to_flow", "pressure", "flow", "1/72")
    rule_b = evo.add_rule("gradient_to_charge", "gradient", "charge", "1/72")
    run = evo.run(steps=3, dt=1)
    save = evo.save("/mnt/data/hhs_physics_evolution_v1_demo.json")

    return {"rule_a": rule_a, "rule_b": rule_b, "run": run, "save": save}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="HHS physics evolution operator")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--out", default="/mnt/data/hhs_physics_evolution_v1_demo_stdout.json")
    args = parser.parse_args(argv)

    report = demo()
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("run", {}).get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
