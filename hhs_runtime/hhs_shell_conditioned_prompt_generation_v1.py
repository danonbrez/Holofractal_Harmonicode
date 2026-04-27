"""
HHS Shell-Conditioned Prompt Generation v1
==========================================

LLM-facing prompt envelope generator for HARMONICODE linguistic reasoning.

Purpose
-------
Convert adaptive ERS temporal shells into structured prompt conditions so an LLM
or local language agent can generate text inside the HHS phase manifold.

This module does not call an LLM directly. It produces deterministic prompt
packets that can be sent to any model, then later scored by
hhs_linguistic_operator_training_loop_v1.

Carrier mapping
---------------
    x  -> syntax channel
    y  -> semantic channel
    xy -> structure / logic channel

Pipeline
--------
    input task
    -> adaptive temporal shells
    -> carrier-conditioned prompt packets
    -> prompt run receipt
    -> downstream model generation
    -> linguistic training feedback
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_entangled_reciprocal_seesaw_temporal_shell_v1 import TemporalShellRun, generate_temporal_shells
from hhs_runtime.hhs_linguistic_operator_training_loop_v1 import carrier_operator


class PromptMode(str, Enum):
    TRANSLATE = "TRANSLATE"
    EXPLAIN = "EXPLAIN"
    REWRITE = "REWRITE"
    PROVE = "PROVE"
    CODE = "CODE"
    DAW_ASSIST = "DAW_ASSIST"


@dataclass(frozen=True)
class ShellPromptPacket:
    index: int
    phase_index: int
    carrier: str
    operator_kind: str
    mode: PromptMode
    system_condition: str
    user_condition: str
    constraints: List[str]
    prompt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["mode"] = self.mode.value
        return data


@dataclass(frozen=True)
class ShellPromptRun:
    seed_hash72: str
    task_hash72: str
    shell_receipt_hash72: str
    mode: PromptMode
    packets: List[ShellPromptPacket]
    aggregate_hash72: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_hash72": self.seed_hash72,
            "task_hash72": self.task_hash72,
            "shell_receipt_hash72": self.shell_receipt_hash72,
            "mode": self.mode.value,
            "packets": [p.to_dict() for p in self.packets],
            "aggregate_hash72": self.aggregate_hash72,
            "receipt_hash72": self.receipt_hash72,
        }


def _mode_instruction(mode: PromptMode) -> str:
    if mode == PromptMode.TRANSLATE:
        return "Translate while preserving semantic anchors, symbolic constraints, and ordered-product distinctions."
    if mode == PromptMode.EXPLAIN:
        return "Explain the content without flattening symbolic layers or introducing unauthorized assumptions."
    if mode == PromptMode.REWRITE:
        return "Rewrite for clarity while preserving all invariant-bearing terms and constraint structure."
    if mode == PromptMode.PROVE:
        return "Produce a proof-style derivation using only declared constraints, preserving non-commutative order."
    if mode == PromptMode.CODE:
        return "Generate executable code that preserves HARMONICODE invariants and emits receipts for audited transitions."
    return "Assist with audio, waveform, sequencing, or mastering decisions while preserving phase and harmonic constraints."


def _carrier_instruction(carrier: str) -> str:
    if carrier == "x":
        return "SYNTAX CHANNEL: optimize grammar, segmentation, punctuation, and program-surface form only. Do not change meaning."
    if carrier == "y":
        return "SEMANTIC CHANNEL: preserve definitions, anchors, subject continuity, and intended meaning. Do not collapse structure."
    return "STRUCTURE_LOGIC CHANNEL: validate implication order, equality chains, invariants, and non-commutative products."


def _constraints_for_packet(carrier: str, phase_index: int) -> List[str]:
    base = [
        "Preserve Δe=0, Ψ=0, Θ15=true, Ω=true.",
        "Do not commute ordered products: xy and yx remain distinct unless explicitly projected.",
        "Do not simplify away active witnesses or projection layers.",
        f"Bind this generation to phase_index={phase_index} on the 72-step torus.",
    ]
    if carrier == "x":
        base.append("Only syntactic changes are allowed in this packet unless the user task explicitly requires more.")
    elif carrier == "y":
        base.append("Semantic anchors must be copied or explicitly mapped, never silently replaced.")
    else:
        base.append("All equality/inequality chains must remain globally reconcilable as one constraint graph.")
    return base


def build_shell_prompt_packets(
    task_text: str,
    *,
    mode: PromptMode | str = PromptMode.EXPLAIN,
    seed: str = "HHS_PROMPT_SEED",
    cycles: int = 1,
    feedback_records: Sequence[Dict[str, Any]] | None = None,
    max_packets: int = 9,
) -> ShellPromptRun:
    prompt_mode = mode if isinstance(mode, PromptMode) else PromptMode(str(mode))
    shells: TemporalShellRun = generate_temporal_shells(seed, cycles=cycles, feedback_records=feedback_records)
    packets: List[ShellPromptPacket] = []
    task_hash = hash72_digest(("shell_prompt_task_v1", task_text, prompt_mode.value), width=24)
    seed_hash = hash72_digest(("shell_prompt_seed_v1", seed, cycles), width=24)

    for shell in shells.steps[:max_packets]:
        op = carrier_operator(shell.carrier)
        system_condition = "\n".join([
            "You are operating inside a HARMONICODE shell-conditioned generation packet.",
            _mode_instruction(prompt_mode),
            _carrier_instruction(shell.carrier),
            f"Carrier={shell.carrier}; Operator={op.kind.value}; Phase={shell.phase_index}; Shell={shell.expansion.get('temporal_shell')}",
        ])
        constraints = _constraints_for_packet(shell.carrier, shell.phase_index)
        user_condition = "\n".join([
            "TASK:",
            task_text,
            "",
            "SHELL CONSTRAINTS:",
            *[f"- {c}" for c in constraints],
        ])
        prompt_hash = hash72_digest(("shell_prompt_packet_v1", shell.shell_hash72, op.to_dict(), prompt_mode.value, system_condition, user_condition, constraints), width=24)
        packets.append(ShellPromptPacket(shell.index, shell.phase_index, shell.carrier, op.kind.value, prompt_mode, system_condition, user_condition, constraints, prompt_hash))

    aggregate = hash72_digest(("shell_prompt_run_aggregate_v1", seed_hash, task_hash, shells.receipt_hash72, [p.prompt_hash72 for p in packets]), width=24)
    receipt = hash72_digest(("shell_prompt_run_receipt_v1", aggregate, prompt_mode.value, len(packets)), width=24)
    return ShellPromptRun(seed_hash, task_hash, shells.receipt_hash72, prompt_mode, packets, aggregate, receipt)


def format_prompt_packet_for_llm(packet: ShellPromptPacket) -> Dict[str, str]:
    """Return OpenAI/chat-style message objects without depending on any model API."""
    return {"system": packet.system_condition, "user": packet.user_condition}


def main() -> None:
    run = build_shell_prompt_packets("Explain xy≠yx while preserving HHS invariants.", mode="EXPLAIN", max_packets=3)
    print(json.dumps(run.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
