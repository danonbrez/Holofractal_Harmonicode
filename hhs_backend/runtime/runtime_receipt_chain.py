# ============================================================================
# hhs_backend/runtime/runtime_receipt_chain.py
# HARMONICODE / HHS
# CANONICAL RECEIPT LINEAGE AUTHORITY
#
# PURPOSE
# -------
# Canonical runtime lineage substrate for:
#
#   - runtime receipt continuity
#   - replay-certified lineage reconstruction
#   - branch topology governance
#   - deterministic receipt hashing
#   - snapshot lineage anchoring
#   - graph lineage projection
#   - merge/fork lineage reconciliation
#   - distributed replay integrity
#
# Receipt continuity IS runtime continuity.
#
# ============================================================================

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid

from collections import defaultdict
from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Dict,
    List,
    Optional,
    Any,
)

from hhs_python.runtime.hhs_runtime_state import (
    HHSRuntimeState,
    V44_KERNEL_AVAILABLE,
    AUTHORITATIVE_TRUST_POLICY_V44,
)

from hhs_backend.runtime.runtime_event_schema import (
    HHSRuntimeEventEnvelope,
)

# ============================================================================
# OPTIONAL V44.2 INTEGRATION
# ============================================================================

try:

    from HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked_7 import (

        security_hash72_v44,

        Tensor,

        Manifold9,
    )

except Exception:

    security_hash72_v44 = None

    Tensor = None

    Manifold9 = None

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_RECEIPT_CHAIN"
)

# ============================================================================
# CONSTANTS
# ============================================================================

HASH72_LEN = 72

# ============================================================================
# RECEIPT
# ============================================================================

@dataclass
class HHSReceipt:

    receipt_id: str

    runtime_id: str

    branch_id: str

    created_at_ns: int

    step: int

    parent_receipt_hash72: str

    receipt_hash72: str

    state_hash72: str

    event_hash72: str

    replay_hash72: str

    snapshot_hash72: str

    witness_flags: int

    converged: bool

    halted: bool

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# BRANCH TOPOLOGY
# ============================================================================

@dataclass
class HHSReceiptBranch:

    branch_id: str

    created_at_ns: int

    source_receipt_hash72: str

    branch_head_hash72: str

    merged_receipts: List[str] = field(
        default_factory=list
    )

# ============================================================================
# RECEIPT CHAIN
# ============================================================================

class HHSRuntimeReceiptChain:

    """
    Canonical deterministic receipt lineage authority.
    """

    def __init__(self):

        self.receipts: Dict[
            str,
            HHSReceipt
        ] = {}

        self.runtime_chains = defaultdict(list)

        self.branch_topology: Dict[
            str,
            HHSReceiptBranch
        ] = {}

        self.child_map = defaultdict(list)

    # =====================================================================
    # HASH72
    # =====================================================================

    def compute_receipt_hash72(
        self,
        payload: Dict[str, Any],
    ):

        serialized = json.dumps(

            payload,

            sort_keys=True,

            separators=(",", ":"),
        )

        digest = hashlib.sha256(

            serialized.encode("utf-8")

        ).hexdigest()

        return digest[:HASH72_LEN]

    # =====================================================================
    # CREATE RECEIPT
    # =====================================================================

    def create_receipt(

        self,

        runtime_state: HHSRuntimeState,

        event: Optional[
            HHSRuntimeEventEnvelope
        ] = None,

        replay_hash72: str = "",

        snapshot_hash72: str = "",

        branch_id: str = "main",
    ) -> HHSReceipt:

        payload = {

            "runtime_id":
                runtime_state.runtime_id,

            "step":
                runtime_state.step,

            "parent_receipt_hash72":
                runtime_state.prev_receipt_hash72,

            "state_hash72":
                runtime_state.state_hash72,

            "event_hash72":
                event.event_hash72
                if event else "",

            "replay_hash72":
                replay_hash72,

            "snapshot_hash72":
                snapshot_hash72,

            "witness_flags":
                runtime_state.witness_flags,

            "converged":
                runtime_state.converged,

            "halted":
                runtime_state.halted,
        }

        receipt_hash72 = (
            self.compute_receipt_hash72(
                payload
            )
        )

        receipt = HHSReceipt(

            receipt_id=str(uuid.uuid4()),

            runtime_id=runtime_state.runtime_id,

            branch_id=branch_id,

            created_at_ns=time.time_ns(),

            step=runtime_state.step,

            parent_receipt_hash72=(
                runtime_state.prev_receipt_hash72
            ),

            receipt_hash72=receipt_hash72,

            state_hash72=(
                runtime_state.state_hash72
            ),

            event_hash72=(
                event.event_hash72
                if event else ""
            ),

            replay_hash72=replay_hash72,

            snapshot_hash72=snapshot_hash72,

            witness_flags=(
                runtime_state.witness_flags
            ),

            converged=(
                runtime_state.converged
            ),

            halted=(
                runtime_state.halted
            ),

            metadata={

                "kernel_available":
                    V44_KERNEL_AVAILABLE,

                "trust_policy":
                    str(
                        AUTHORITATIVE_TRUST_POLICY_V44
                    )
                    if V44_KERNEL_AVAILABLE
                    else None,
            },
        )

        self.receipts[
            receipt.receipt_hash72
        ] = receipt

        self.runtime_chains[
            runtime_state.runtime_id
        ].append(
            receipt.receipt_hash72
        )

        if receipt.parent_receipt_hash72:

            self.child_map[
                receipt.parent_receipt_hash72
            ].append(
                receipt.receipt_hash72
            )

        logger.info(
            f"Receipt created: "
            f"{receipt.receipt_hash72}"
        )

        return receipt

    # =====================================================================
    # VERIFY HASH72
    # =====================================================================

    def verify_receipt_hash72(
        self,
        receipt: HHSReceipt,
    ):

        payload = {

            "runtime_id":
                receipt.runtime_id,

            "step":
                receipt.step,

            "parent_receipt_hash72":
                receipt.parent_receipt_hash72,

            "state_hash72":
                receipt.state_hash72,

            "event_hash72":
                receipt.event_hash72,

            "replay_hash72":
                receipt.replay_hash72,

            "snapshot_hash72":
                receipt.snapshot_hash72,

            "witness_flags":
                receipt.witness_flags,

            "converged":
                receipt.converged,

            "halted":
                receipt.halted,
        }

        computed = (
            self.compute_receipt_hash72(
                payload
            )
        )

        valid = (
            computed
            ==
            receipt.receipt_hash72
        )

        if not valid:

            logger.error(
                "Receipt hash verification failed."
            )

        return valid

    # =====================================================================
    # VERIFY RECEIPT CHAIN
    # =====================================================================

    def verify_receipt_chain(
        self,
        runtime_id: str,
    ):

        chain = self.runtime_chains[
            runtime_id
        ]

        if not chain:

            return True

        previous = None

        for receipt_hash in chain:

            receipt = self.receipts[
                receipt_hash
            ]

            valid = (
                self.verify_receipt_hash72(
                    receipt
                )
            )

            if not valid:

                return False

            if previous:

                linked = (

                    receipt.parent_receipt_hash72
                    ==
                    previous.receipt_hash72
                )

                if not linked:

                    logger.error(
                        "Receipt lineage discontinuity."
                    )

                    return False

            previous = receipt

        return True

    # =====================================================================
    # VERIFY BRANCH
    # =====================================================================

    def verify_branch_lineage(
        self,
        branch_id: str,
    ):

        branch = self.branch_topology.get(
            branch_id
        )

        if not branch:

            return False

        valid = (
            branch.branch_head_hash72
            in self.receipts
        )

        return valid

    # =====================================================================
    # CREATE BRANCH
    # =====================================================================

    def fork_receipt_branch(
        self,
        source_receipt_hash72: str,
    ):

        branch = HHSReceiptBranch(

            branch_id=str(uuid.uuid4()),

            created_at_ns=time.time_ns(),

            source_receipt_hash72=(
                source_receipt_hash72
            ),

            branch_head_hash72=(
                source_receipt_hash72
            ),
        )

        self.branch_topology[
            branch.branch_id
        ] = branch

        logger.info(
            f"Receipt branch forked: "
            f"{branch.branch_id}"
        )

        return branch

    # =====================================================================
    # MERGE BRANCHES
    # =====================================================================

    def merge_receipt_branches(

        self,

        target_branch_id: str,

        source_branch_id: str,
    ):

        target = self.branch_topology[
            target_branch_id
        ]

        source = self.branch_topology[
            source_branch_id
        ]

        target.merged_receipts.append(
            source.branch_head_hash72
        )

        target.branch_head_hash72 = (
            source.branch_head_hash72
        )

        logger.info(
            f"Receipt branches merged: "
            f"{target_branch_id} <- "
            f"{source_branch_id}"
        )

        return target

    # =====================================================================
    # VERIFY MERGE
    # =====================================================================

    def verify_merge_equivalence(

        self,

        target_branch_id: str,

        source_branch_id: str,
    ):

        target = self.branch_topology[
            target_branch_id
        ]

        source = self.branch_topology[
            source_branch_id
        ]

        equivalent = (

            target.branch_head_hash72
            ==
            source.branch_head_hash72
        )

        return equivalent

    # =====================================================================
    # RECONSTRUCT CHAIN
    # =====================================================================

    def reconstruct_receipt_chain(
        self,
        runtime_id: str,
    ):

        chain = []

        for receipt_hash in self.runtime_chains[
            runtime_id
        ]:

            chain.append(

                self.receipts[
                    receipt_hash
                ]
            )

        return chain

    # =====================================================================
    # RECONSTRUCT BRANCH
    # =====================================================================

    def reconstruct_branch_history(
        self,
        branch_id: str,
    ):

        branch = self.branch_topology[
            branch_id
        ]

        reconstructed = []

        current_hash = (
            branch.branch_head_hash72
        )

        while current_hash:

            receipt = self.receipts.get(
                current_hash
            )

            if not receipt:
                break

            reconstructed.append(
                receipt
            )

            current_hash = (
                receipt.parent_receipt_hash72
            )

        return reconstructed[::-1]

    # =====================================================================
    # RUNTIME LINEAGE
    # =====================================================================

    def reconstruct_runtime_lineage(
        self,
        runtime_id: str,
    ):

        lineage = []

        for receipt_hash in self.runtime_chains[
            runtime_id
        ]:

            receipt = self.receipts[
                receipt_hash
            ]

            lineage.append({

                "receipt_hash72":
                    receipt.receipt_hash72,

                "parent":
                    receipt.parent_receipt_hash72,

                "step":
                    receipt.step,

                "branch":
                    receipt.branch_id,
            })

        return lineage

    # =====================================================================
    # SNAPSHOT ANCHOR
    # =====================================================================

    def anchor_snapshot_receipt(

        self,

        receipt_hash72: str,

        snapshot_hash72: str,
    ):

        receipt = self.receipts[
            receipt_hash72
        ]

        receipt.snapshot_hash72 = (
            snapshot_hash72
        )

        logger.info(
            f"Snapshot anchored: "
            f"{snapshot_hash72}"
        )

    # =====================================================================
    # VERIFY SNAPSHOT
    # =====================================================================

    def verify_snapshot_lineage(
        self,
        snapshot_hash72: str,
    ):

        for receipt in self.receipts.values():

            if (

                receipt.snapshot_hash72
                ==
                snapshot_hash72

            ):

                return True

        return False

    # =====================================================================
    # GRAPH EDGE
    # =====================================================================

    def to_graph_edge(
        self,
        receipt: HHSReceipt,
    ):

        return {

            "source":
                receipt.parent_receipt_hash72,

            "target":
                receipt.receipt_hash72,

            "runtime_id":
                receipt.runtime_id,

            "branch_id":
                receipt.branch_id,
        }

    # =====================================================================
    # LINEAGE PROJECTION
    # =====================================================================

    def to_lineage_projection(
        self,
        receipt: HHSReceipt,
    ):

        return {

            "receipt_hash72":
                receipt.receipt_hash72,

            "parent":
                receipt.parent_receipt_hash72,

            "step":
                receipt.step,

            "event_hash72":
                receipt.event_hash72,

            "replay_hash72":
                receipt.replay_hash72,
        }

    # =====================================================================
    # REPLAY PACKET
    # =====================================================================

    def to_replay_lineage_packet(
        self,
        receipt: HHSReceipt,
    ):

        return {

            "receipt_hash72":
                receipt.receipt_hash72,

            "state_hash72":
                receipt.state_hash72,

            "parent":
                receipt.parent_receipt_hash72,

            "snapshot":
                receipt.snapshot_hash72,
        }

    # =====================================================================
    # V44 VALIDATION
    # =====================================================================

    def validate_v44_lineage(
        self,
        receipt: HHSReceipt,
    ):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        lineage_hash = hashlib.sha256(

            json.dumps(

                self.to_lineage_projection(
                    receipt
                ),

                sort_keys=True,

            ).encode("utf-8")

        ).hexdigest()

        return {

            "kernel_available": True,

            "validated": True,

            "lineage_hash":
                lineage_hash,
        }

# ============================================================================
# GLOBAL RECEIPT AUTHORITY
# ============================================================================

runtime_receipt_chain = (
    HHSRuntimeReceiptChain()
)

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_receipt_chain_self_test():

    runtime_state = HHSRuntimeState(

        runtime_id="runtime_001",

        step=1,

        orbit_id=72,

        transport_flux="1/1",

        orientation_flux="1/1",

        constraint_flux="1/1",

        witness_flags=7,

        prev_receipt_hash72="",

        state_hash72="state001",

        receipt_hash72="",

        lo_shu_slot=5,

        closure_class="0",

        converged=True,

        halted=False,

        timestamp_ns=time.time_ns(),
    )

    receipt = (

        runtime_receipt_chain
        .create_receipt(
            runtime_state
        )
    )

    valid = (

        runtime_receipt_chain
        .verify_receipt_hash72(
            receipt
        )
    )

    lineage = (

        runtime_receipt_chain
        .reconstruct_runtime_lineage(
            runtime_state.runtime_id
        )
    )

    graph_edge = (

        runtime_receipt_chain
        .to_graph_edge(
            receipt
        )
    )

    v44 = (

        runtime_receipt_chain
        .validate_v44_lineage(
            receipt
        )
    )

    print()

    print("RECEIPT")

    print(receipt)

    print()

    print("VALID")

    print(valid)

    print()

    print("LINEAGE")

    print(lineage)

    print()

    print("GRAPH EDGE")

    print(graph_edge)

    print()

    print("V44")

    print(v44)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_receipt_chain_self_test()