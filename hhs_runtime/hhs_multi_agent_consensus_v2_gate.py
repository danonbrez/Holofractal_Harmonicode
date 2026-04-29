"""
HHS Multi-Agent Consensus Gate v2
================================

Aggregates multiple distributed verification receipts and produces a consensus
acceptance decision.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass(frozen=True)
class ConsensusDecision:
    total_agents: int
    verified_agents: int
    required_threshold: int
    status: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_consensus(receipts: List[Dict[str, Any]], *, threshold_ratio: float = 1.0) -> ConsensusDecision:
    total = len(receipts)
    verified = sum(1 for r in receipts if r.get("status") == "VERIFIED")
    required = int(total * threshold_ratio + 0.9999)
    status = "CONSENSUS_ACCEPTED" if verified >= required else "CONSENSUS_REJECTED"
    receipt_hash72 = hash72_digest(("hhs_multi_agent_consensus_v2", total, verified, required, status), width=24)
    return ConsensusDecision(total, verified, required, status, receipt_hash72)


if __name__ == "__main__":
    # simple self-test
    sample = [{"status": "VERIFIED"}, {"status": "VERIFIED"}]
    print(evaluate_consensus(sample).to_dict())
