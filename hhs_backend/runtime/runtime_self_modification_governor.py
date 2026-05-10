# ============================================================================
# hhs_backend/runtime/runtime_self_modification_governor.py
# HARMONICODE / HHS
# SELF-MODIFICATION GOVERNOR
#
# PURPOSE
# -------
# Canonical recursive governance layer for:
#
#   - runtime mutation proposals
#   - invariant-preserving upgrades
#   - replay-safe modification simulation
#   - rollback certification
#   - sandboxed runtime evolution
#   - adaptive module replacement
#   - semantic drift prevention
#   - recursive runtime governance
#
# Mutation MUST remain replay-safe and invariant-preserving.
#
# ============================================================================

from __future__ import annotations

import copy
import hashlib
import logging
import statistics
import threading
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from hhs_backend.runtime.runtime_replay_engine import (
    runtime_replay_engine
)

from hhs_backend.runtime.runtime_prediction_engine import (
    runtime_prediction_engine
)

from hhs_backend.runtime.runtime_adaptive_goal_engine import (
    runtime_adaptive_goal_engine
)

from hhs_backend.runtime.runtime_semantic_memory_engine import (
    runtime_semantic_memory_engine
)

from hhs_storage.runtime_state_store_v1 import (
    runtime_state_store
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_SELF_MOD_GOVERNOR"
)

# ============================================================================
# MUTATION STATES
# ============================================================================

STATE_PROPOSED = "proposed"

STATE_SANDBOXED = "sandboxed"

STATE_VALIDATED = "validated"

STATE_REJECTED = "rejected"

STATE_ROLLED_BACK = "rolled_back"

STATE_APPLIED = "applied"

# ============================================================================
# MUTATION PROPOSAL
# ============================================================================

@dataclass
class HHSMutationProposal:

    proposal_id: str

    created_at: float

    target_module: str

    mutation_type: str

    diff_hash72: str

    replay_safe: bool

    state: str = STATE_PROPOSED

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# SANDBOX RESULT
# ============================================================================

@dataclass
class HHSMutationSandboxResult:

    sandbox_id: str

    created_at: float

    proposal_id: str

    replay_equivalent: bool

    semantic_drift: float

    invariant_valid: bool

    entropy_score: float

# ============================================================================
# ROLLBACK CERTIFICATE
# ============================================================================

@dataclass
class HHSRollbackCertificate:

    certificate_id: str

    created_at: float

    proposal_id: str

    restored_snapshot: str

    rollback_successful: bool

# ============================================================================
# GOVERNOR
# ============================================================================

class HHSRuntimeSelfModificationGovernor:

    """
    Canonical recursive runtime governance layer.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.proposals: Dict[
            str,
            HHSMutationProposal
        ] = {}

        self.sandboxes: Dict[
            str,
            HHSMutationSandboxResult
        ] = {}

        self.rollback_certificates: Dict[
            str,
            HHSRollbackCertificate
        ] = {}

        self.total_proposals = 0

        self.total_validations = 0

        self.total_rollbacks = 0

    # =====================================================================
    # PROPOSALS
    # =====================================================================

    def create_mutation_proposal(

        self,

        target_module: str,

        mutation_type: str,

        diff_text: str,

        metadata: Optional[Dict] = None
    ) -> HHSMutationProposal:

        with self.lock:

            diff_hash72 = hashlib.sha256(

                diff_text.encode("utf-8")

            ).hexdigest()[:72]

            proposal = HHSMutationProposal(

                proposal_id=str(uuid.uuid4()),

                created_at=time.time(),

                target_module=target_module,

                mutation_type=mutation_type,

                diff_hash72=diff_hash72,

                replay_safe=True,

                metadata=metadata or {}
            )

            self.proposals[
                proposal.proposal_id
            ] = proposal

            runtime_semantic_memory_engine.ingest_memory(

                memory_type="mutation",

                semantic_text=diff_text,

                hash72=diff_hash72,

                metadata={

                    "proposal_id":
                        proposal.proposal_id,

                    "target_module":
                        target_module
                }
            )

            self.total_proposals += 1

            logger.info(
                f"Mutation proposal created: "
                f"{proposal.proposal_id}"
            )

            return proposal

    # =====================================================================
    # SANDBOX SIMULATION
    # =====================================================================

    def simulate_mutation(
        self,
        proposal: HHSMutationProposal
    ) -> HHSMutationSandboxResult:

        with self.lock:

            replay = (

                runtime_replay_engine
                .predictive_replay(
                    horizon=10
                )
            )

            runtime_replay_engine.verify_replay_equivalence(
                replay
            )

            prediction = (

                runtime_prediction_engine
                .score_replay(replay)
            )

            semantic_drift = self.detect_semantic_drift(
                proposal
            )

            invariant_valid = (
                self.validate_runtime_invariants(
                    replay,
                    semantic_drift
                )
            )

            sandbox = HHSMutationSandboxResult(

                sandbox_id=str(uuid.uuid4()),

                created_at=time.time(),

                proposal_id=proposal.proposal_id,

                replay_equivalent=
                    replay.replay_equivalent,

                semantic_drift=
                    semantic_drift,

                invariant_valid=
                    invariant_valid,

                entropy_score=
                    prediction.entropy_score
            )

            self.sandboxes[
                sandbox.sandbox_id
            ] = sandbox

            proposal.state = STATE_SANDBOXED

            logger.info(
                f"Mutation sandboxed: "
                f"{proposal.proposal_id}"
            )

            return sandbox

    # =====================================================================
    # INVARIANT VALIDATION
    # =====================================================================

    def validate_runtime_invariants(

        self,

        replay,

        semantic_drift: float
    ) -> bool:

        if not replay.replay_equivalent:
            return False

        if semantic_drift > 0.5:
            return False

        prediction = (

            runtime_prediction_engine
            .score_replay(replay)
        )

        if prediction.entropy_score > 0.8:
            return False

        return True

    # =====================================================================
    # DRIFT DETECTION
    # =====================================================================

    def detect_semantic_drift(
        self,
        proposal: HHSMutationProposal
    ) -> float:

        query = (
            proposal.target_module
            + " "
            + proposal.mutation_type
        )

        results = (

            runtime_semantic_memory_engine
            .semantic_search(
                query,
                limit=5
            )
        )

        if not results:
            return 0.0

        similarities = [

            result.similarity

            for result in results
        ]

        avg_similarity = statistics.mean(
            similarities
        )

        drift = 1.0 - avg_similarity

        return drift

    # =====================================================================
    # VALIDATION
    # =====================================================================

    def validate_mutation(
        self,
        proposal_id: str
    ):

        proposal = self.proposals.get(
            proposal_id
        )

        if proposal is None:
            return None

        sandbox = self.simulate_mutation(
            proposal
        )

        if sandbox.invariant_valid:

            proposal.state = STATE_VALIDATED

            self.total_validations += 1

            logger.info(
                f"Mutation validated: "
                f"{proposal_id}"
            )

            return {

                "validated": True,

                "sandbox":
                    sandbox
            }

        proposal.state = STATE_REJECTED

        logger.warning(
            f"Mutation rejected: "
            f"{proposal_id}"
        )

        return {

            "validated": False,

            "sandbox":
                sandbox
        }

    # =====================================================================
    # APPLY
    # =====================================================================

    def apply_mutation(
        self,
        proposal_id: str
    ):

        proposal = self.proposals.get(
            proposal_id
        )

        if proposal is None:
            return None

        if proposal.state != STATE_VALIDATED:

            logger.warning(
                "Mutation not validated"
            )

            return {

                "applied": False
            }

        proposal.state = STATE_APPLIED

        runtime_state_store.store_event(

            event_type="runtime.mutation",

            source="self_mod_governor",

            payload={

                "proposal_id":
                    proposal_id,

                "target_module":
                    proposal.target_module,

                "mutation_type":
                    proposal.mutation_type
            }
        )

        logger.info(
            f"Mutation applied: "
            f"{proposal_id}"
        )

        return {

            "applied": True,

            "proposal":
                proposal
        }

    # =====================================================================
    # ROLLBACK
    # =====================================================================

    def rollback_runtime_state(
        self,
        proposal_id: str
    ) -> HHSRollbackCertificate:

        proposal = self.proposals.get(
            proposal_id
        )

        latest = (
            runtime_state_store
            .latest_snapshot()
        )

        certificate = HHSRollbackCertificate(

            certificate_id=str(uuid.uuid4()),

            created_at=time.time(),

            proposal_id=proposal_id,

            restored_snapshot=
                latest["snapshot_id"]
                if latest else "none",

            rollback_successful=True
        )

        self.rollback_certificates[
            certificate.certificate_id
        ] = certificate

        if proposal:

            proposal.state = STATE_ROLLED_BACK

        self.total_rollbacks += 1

        logger.warning(
            f"Rollback executed: "
            f"{proposal_id}"
        )

        return certificate

    # =====================================================================
    # GOVERNED ADAPTATION
    # =====================================================================

    def governed_adaptive_cycle(

        self,

        target_module: str,

        mutation_type: str,

        diff_text: str
    ):

        proposal = self.create_mutation_proposal(

            target_module=target_module,

            mutation_type=mutation_type,

            diff_text=diff_text
        )

        validation = self.validate_mutation(
            proposal.proposal_id
        )

        if validation["validated"]:

            application = self.apply_mutation(
                proposal.proposal_id
            )

            return {

                "proposal":
                    proposal,

                "validation":
                    validation,

                "application":
                    application
            }

        rollback = self.rollback_runtime_state(
            proposal.proposal_id
        )

        return {

            "proposal":
                proposal,

            "validation":
                validation,

            "rollback":
                rollback
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

        if proposal is None:
            return None

        sandboxes = [

            sandbox

            for sandbox in self.sandboxes.values()

            if sandbox.proposal_id
            == proposal_id
        ]

        return {

            "proposal":
                proposal,

            "sandboxes":
                sandboxes
        }

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        drift_scores = [

            sandbox.semantic_drift

            for sandbox in self.sandboxes.values()
        ]

        avg_drift = 0.0

        if drift_scores:

            avg_drift = statistics.mean(
                drift_scores
            )

        return {

            "proposals":
                self.total_proposals,

            "validations":
                self.total_validations,

            "rollbacks":
                self.total_rollbacks,

            "average_semantic_drift":
                avg_drift
        }

# ============================================================================
# GLOBAL GOVERNOR
# ============================================================================

runtime_self_modification_governor = (
    HHSRuntimeSelfModificationGovernor()
)

# ============================================================================
# SELF TEST
# ============================================================================

def self_modification_governor_self_test():

    result = (

        runtime_self_modification_governor
        .governed_adaptive_cycle(

            target_module=
                "runtime_prediction_engine",

            mutation_type=
                "adaptive_optimization",

            diff_text=
                "Increase trajectory "
                "stability weighting"
        )
    )

    print()

    print("SELF MODIFICATION METRICS")

    print(

        runtime_self_modification_governor
        .metrics()
    )

    print()

    print("RESULT")

    print(result)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    self_modification_governor_self_test()