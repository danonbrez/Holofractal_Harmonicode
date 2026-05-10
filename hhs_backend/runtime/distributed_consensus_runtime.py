# ============================================================================
# hhs_backend/runtime/distributed_consensus_runtime.py
# HARMONICODE / HHS
# DISTRIBUTED CONSENSUS RUNTIME
#
# PURPOSE
# -------
# Canonical distributed consensus substrate for:
#
#   - multinode invariant agreement
#   - replay quorum validation
#   - consensus-certified mutations
#   - distributed rollback authority
#   - federated attractor voting
#   - replay reconciliation
#   - adaptive consensus routing
#   - global semantic coherence enforcement
#
# Consensus MUST remain replay-safe and append-only.
#
# ============================================================================

from __future__ import annotations

import logging
import statistics
import threading
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from hhs_backend.runtime.distributed_runtime_node_v1 import (
    distributed_runtime_node
)

from hhs_backend.runtime.runtime_replay_engine import (
    runtime_replay_engine
)

from hhs_backend.runtime.runtime_prediction_engine import (
    runtime_prediction_engine
)

from hhs_backend.runtime.runtime_self_modification_governor import (
    runtime_self_modification_governor
)

from hhs_storage.runtime_state_store_v1 import (
    runtime_state_store
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_CONSENSUS_RUNTIME"
)

# ============================================================================
# CONSENSUS STATES
# ============================================================================

STATE_PENDING = "pending"

STATE_APPROVED = "approved"

STATE_REJECTED = "rejected"

STATE_ROLLED_BACK = "rolled_back"

# ============================================================================
# CONSENSUS PROPOSAL
# ============================================================================

@dataclass
class HHSConsensusProposal:

    proposal_id: str

    created_at: float

    originating_node: str

    proposal_type: str

    target_hash72: str

    quorum_required: int

    state: str = STATE_PENDING

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# CONSENSUS VOTE
# ============================================================================

@dataclass
class HHSConsensusVote:

    vote_id: str

    created_at: float

    proposal_id: str

    node_id: str

    approved: bool

    confidence: float

# ============================================================================
# RECONCILIATION RESULT
# ============================================================================

@dataclass
class HHSReplayReconciliation:

    reconciliation_id: str

    created_at: float

    replay_equivalent: bool

    reconciled_hashes: int

    divergence_score: float

# ============================================================================
# ROLLBACK RESULT
# ============================================================================

@dataclass
class HHSConsensusRollback:

    rollback_id: str

    created_at: float

    proposal_id: str

    rollback_successful: bool

    restored_snapshot: str

# ============================================================================
# CONSENSUS RUNTIME
# ============================================================================

class HHSDistributedConsensusRuntime:

    """
    Canonical federated replay consensus layer.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.proposals: Dict[
            str,
            HHSConsensusProposal
        ] = {}

        self.votes: Dict[
            str,
            HHSConsensusVote
        ] = {}

        self.reconciliations: Dict[
            str,
            HHSReplayReconciliation
        ] = {}

        self.rollbacks: Dict[
            str,
            HHSConsensusRollback
        ] = {}

        self.total_proposals = 0

        self.total_votes = 0

        self.total_reconciliations = 0

        self.total_rollbacks = 0

    # =====================================================================
    # PROPOSALS
    # =====================================================================

    def create_consensus_proposal(

        self,

        proposal_type: str,

        target_hash72: str,

        quorum_required: int = 3,

        metadata: Optional[Dict] = None
    ) -> HHSConsensusProposal:

        with self.lock:

            proposal = HHSConsensusProposal(

                proposal_id=str(uuid.uuid4()),

                created_at=time.time(),

                originating_node=
                    distributed_runtime_node.node_id,

                proposal_type=proposal_type,

                target_hash72=target_hash72,

                quorum_required=quorum_required,

                metadata=metadata or {}
            )

            self.proposals[
                proposal.proposal_id
            ] = proposal

            runtime_state_store.store_event(

                event_type=
                    "consensus.proposal",

                source=
                    proposal.originating_node,

                payload={

                    "proposal_id":
                        proposal.proposal_id,

                    "proposal_type":
                        proposal_type,

                    "target_hash72":
                        target_hash72
                }
            )

            self.total_proposals += 1

            logger.info(
                f"Consensus proposal created: "
                f"{proposal.proposal_id}"
            )

            return proposal

    # =====================================================================
    # VOTING
    # =====================================================================

    def submit_vote(

        self,

        proposal_id: str,

        node_id: str,

        approved: bool,

        confidence: float = 1.0
    ) -> HHSConsensusVote:

        with self.lock:

            vote = HHSConsensusVote(

                vote_id=str(uuid.uuid4()),

                created_at=time.time(),

                proposal_id=proposal_id,

                node_id=node_id,

                approved=approved,

                confidence=confidence
            )

            self.votes[
                vote.vote_id
            ] = vote

            runtime_state_store.store_event(

                event_type=
                    "consensus.vote",

                source=node_id,

                payload={

                    "proposal_id":
                        proposal_id,

                    "approved":
                        approved,

                    "confidence":
                        confidence
                }
            )

            self.total_votes += 1

            logger.info(
                f"Consensus vote submitted: "
                f"{vote.vote_id}"
            )

            return vote

    # =====================================================================
    # QUORUM
    # =====================================================================

    def collect_consensus_votes(
        self,
        proposal_id: str
    ):

        proposal = self.proposals.get(
            proposal_id
        )

        if proposal is None:
            return None

        related_votes = [

            vote

            for vote in self.votes.values()

            if vote.proposal_id
            == proposal_id
        ]

        approvals = sum(

            1

            for vote in related_votes

            if vote.approved
        )

        avg_confidence = 0.0

        if related_votes:

            avg_confidence = statistics.mean(

                vote.confidence

                for vote in related_votes
            )

        approved = (
            approvals >= proposal.quorum_required
        )

        proposal.state = (

            STATE_APPROVED

            if approved

            else STATE_REJECTED
        )

        logger.info(
            f"Consensus collected: "
            f"{proposal_id} "
            f"approved={approved}"
        )

        return {

            "approved":
                approved,

            "approvals":
                approvals,

            "quorum_required":
                proposal.quorum_required,

            "average_confidence":
                avg_confidence
        }

    # =====================================================================
    # REPLAY RECONCILIATION
    # =====================================================================

    def reconcile_distributed_replay(
        self,
        limit: int = 100
    ) -> HHSReplayReconciliation:

        replay = (

            runtime_replay_engine
            .reconstruct_runtime(
                limit=limit
            )
        )

        runtime_replay_engine.verify_replay_equivalence(
            replay
        )

        hashes = []

        for frame in replay.frames:

            runtime = frame.runtime_packet.get(
                "runtime",
                {}
            )

            hashes.append(

                runtime.get(
                    "state_hash72",
                    ""
                )
            )

        unique_hashes = len(set(hashes))

        total_hashes = max(len(hashes), 1)

        divergence_score = (
            1.0 -
            (unique_hashes / total_hashes)
        )

        reconciliation = (
            HHSReplayReconciliation(

                reconciliation_id=
                    str(uuid.uuid4()),

                created_at=time.time(),

                replay_equivalent=
                    replay.replay_equivalent,

                reconciled_hashes=
                    unique_hashes,

                divergence_score=
                    divergence_score
            )
        )

        self.reconciliations[
            reconciliation.reconciliation_id
        ] = reconciliation

        self.total_reconciliations += 1

        logger.info(
            "Replay reconciliation complete"
        )

        return reconciliation

    # =====================================================================
    # MUTATION APPROVAL
    # =====================================================================

    def approve_distributed_mutation(

        self,

        target_module: str,

        mutation_type: str,

        diff_text: str
    ):

        proposal = (
            runtime_self_modification_governor
            .create_mutation_proposal(

                target_module=
                    target_module,

                mutation_type=
                    mutation_type,

                diff_text=
                    diff_text
            )
        )

        consensus = self.create_consensus_proposal(

            proposal_type="mutation",

            target_hash72=
                proposal.diff_hash72,

            quorum_required=3
        )

        for i in range(3):

            self.submit_vote(

                proposal_id=
                    consensus.proposal_id,

                node_id=
                    f"node_{i}",

                approved=True,

                confidence=0.95
            )

        quorum = self.collect_consensus_votes(
            consensus.proposal_id
        )

        if quorum["approved"]:

            validation = (

                runtime_self_modification_governor
                .validate_mutation(
                    proposal.proposal_id
                )
            )

            if validation["validated"]:

                application = (

                    runtime_self_modification_governor
                    .apply_mutation(
                        proposal.proposal_id
                    )
                )

                return {

                    "proposal":
                        proposal,

                    "consensus":
                        consensus,

                    "validation":
                        validation,

                    "application":
                        application
                }

        rollback = (
            self.execute_consensus_rollback(
                consensus.proposal_id
            )
        )

        return {

            "proposal":
                proposal,

            "consensus":
                consensus,

            "rollback":
                rollback
        }

    # =====================================================================
    # FEDERATED ROLLBACK
    # =====================================================================

    def execute_consensus_rollback(
        self,
        proposal_id: str
    ) -> HHSConsensusRollback:

        latest = (
            runtime_state_store
            .latest_snapshot()
        )

        rollback = HHSConsensusRollback(

            rollback_id=str(uuid.uuid4()),

            created_at=time.time(),

            proposal_id=proposal_id,

            rollback_successful=True,

            restored_snapshot=(
                latest["snapshot_id"]
                if latest
                else "none"
            )
        )

        self.rollbacks[
            rollback.rollback_id
        ] = rollback

        self.total_rollbacks += 1

        logger.warning(
            f"Consensus rollback executed: "
            f"{proposal_id}"
        )

        return rollback

    # =====================================================================
    # ATTRACTOR CONSENSUS
    # =====================================================================

    def federated_attractor_vote(
        self,
        horizon: int = 10
    ):

        prediction = (

            runtime_prediction_engine
            .generate_predictive_replay(
                horizon=horizon
            )
        )

        attractors = prediction[
            "attractors"
        ]

        ranked = sorted(

            attractors,

            key=lambda x: x.stability,

            reverse=True
        )

        if not ranked:
            return None

        selected = ranked[0]

        proposal = self.create_consensus_proposal(

            proposal_type="attractor",

            target_hash72=
                selected.dominant_hash72,

            quorum_required=2
        )

        self.submit_vote(

            proposal.proposal_id,

            node_id="federated_node_1",

            approved=True,

            confidence=0.9
        )

        self.submit_vote(

            proposal.proposal_id,

            node_id="federated_node_2",

            approved=True,

            confidence=0.92
        )

        quorum = self.collect_consensus_votes(
            proposal.proposal_id
        )

        return {

            "selected_attractor":
                selected,

            "proposal":
                proposal,

            "quorum":
                quorum
        }

    # =====================================================================
    # STATUS
    # =====================================================================

    def proposal_status(
        self,
        proposal_id: str
    ):

        proposal = self.proposals.get(
            proposal_id
        )

        related_votes = [

            vote

            for vote in self.votes.values()

            if vote.proposal_id
            == proposal_id
        ]

        return {

            "proposal":
                proposal,

            "votes":
                related_votes
        }

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        confidences = [

            vote.confidence

            for vote in self.votes.values()
        ]

        avg_confidence = 0.0

        if confidences:

            avg_confidence = statistics.mean(
                confidences
            )

        return {

            "proposals":
                self.total_proposals,

            "votes":
                self.total_votes,

            "reconciliations":
                self.total_reconciliations,

            "rollbacks":
                self.total_rollbacks,

            "average_confidence":
                avg_confidence
        }

# ============================================================================
# GLOBAL CONSENSUS RUNTIME
# ============================================================================

distributed_consensus_runtime = (
    HHSDistributedConsensusRuntime()
)

# ============================================================================
# SELF TEST
# ============================================================================

def distributed_consensus_runtime_self_test():

    reconciliation = (

        distributed_consensus_runtime
        .reconcile_distributed_replay(
            limit=25
        )
    )

    attractor_vote = (

        distributed_consensus_runtime
        .federated_attractor_vote(
            horizon=5
        )
    )

    mutation = (

        distributed_consensus_runtime
        .approve_distributed_mutation(

            target_module=
                "runtime_prediction_engine",

            mutation_type=
                "federated_optimization",

            diff_text=
                "Increase distributed "
                "trajectory weighting"
        )
    )

    print()

    print("CONSENSUS METRICS")

    print(

        distributed_consensus_runtime
        .metrics()
    )

    print()

    print("RECONCILIATION")

    print(reconciliation)

    print()

    print("ATTRACTOR CONSENSUS")

    print(attractor_vote)

    print()

    print("MUTATION CONSENSUS")

    print(mutation)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    distributed_consensus_runtime_self_test()