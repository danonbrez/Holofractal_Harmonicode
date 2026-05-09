# hhs_runtime/hhs_execution_router_v1.py
#
# HARMONICODE / HHS
# Canonical Execution Router v1
#
# Purpose:
# --------
# Defines the canonical execution geometry for all runtime flows.
#
# ALL execution paths MUST traverse this router.
#
# This file becomes the orchestration bridge between:
#
#   Python symbolic layer
#   ↓
#   Tokenization / normalization
#   ↓
#   IR lowering
#   ↓
#   VM execution
#   ↓
#   Receipt validation
#   ↓
#   Receipt graph insertion
#   ↓
#   Replay prediction
#   ↓
#   Sandbox projection
#
# Canonical invariant:
#
#   Receipts are the ONLY canonical memory anchors.
#
# Everything else is:
#   replay
#   prediction
#   projection
#   sandboxing
#
# The VM runtime remains the authoritative validator.
#

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from hhs_runtime.hhs_receipt_vector_index_v1 import (
    HHSReceiptVectorIndex,
)

from hhs_runtime.hhs_replay_prediction_engine_v1 import (
    HHSReplayPredictionEngine,
)

from hhs_runtime.hhs_canonical_state_manager_v1 import (
    HHSCannonicalStateManager,
)

from hhs_runtime.hhs_sandbox_projection_engine_v1 import (
    HHSSandboxProjectionEngine,
)

from hhs_runtime.hhs_vm_bridge_v1 import (
    HHSVMBridge,
)

from hhs_runtime.hhs_ir_bridge_v1 import (
    HHSIRBridge,
)

from hhs_runtime.hhs_hash72_v1 import (
    hash72_string,
)

# ============================================================
# ROUTE STAGES
# ============================================================

ROUTE_STAGE_NORMALIZE = "normalize"
ROUTE_STAGE_TOKENIZE = "tokenize"
ROUTE_STAGE_IR = "ir_lowering"
ROUTE_STAGE_VM = "vm_execution"
ROUTE_STAGE_VALIDATE = "validate"
ROUTE_STAGE_COMMIT = "commit"
ROUTE_STAGE_INDEX = "index"
ROUTE_STAGE_REPLAY = "replay"
ROUTE_STAGE_PROJECT = "project"

# ============================================================
# ROUTE RECEIPT
# ============================================================


@dataclass
class HHSRouteReceipt:

    route_id: str

    timestamp: float

    input_payload: Any

    normalized_payload: Any = None

    tokens: List[Any] = field(default_factory=list)

    ir_nodes: List[Dict[str, Any]] = field(default_factory=list)

    vm_result: Dict[str, Any] = field(default_factory=dict)

    receipt_hash72: str = ""

    state_hash72: str = ""

    witness_flags: int = 0

    validation_passed: bool = False

    replay_predictions: List[Dict[str, Any]] = field(default_factory=list)

    sandbox_projection: Dict[str, Any] = field(default_factory=dict)

    route_trace: List[str] = field(default_factory=list)

# ============================================================
# EXECUTION ROUTER
# ============================================================


class HHSExecutionRouter:

    """
    Canonical orchestration layer.

    All runtime flows pass through here.
    """

    def __init__(self):

        self.vm_bridge = HHSVMBridge()

        self.ir_bridge = HHSIRBridge()

        self.vector_index = HHSReceiptVectorIndex()

        self.replay_engine = HHSReplayPredictionEngine()

        self.state_manager = HHSCannonicalStateManager()

        self.sandbox_engine = HHSSandboxProjectionEngine()

    # ========================================================
    # ENTRY
    # ========================================================

    def execute(
        self,
        payload: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HHSRouteReceipt:

        receipt = HHSRouteReceipt(
            route_id=str(uuid.uuid4()),
            timestamp=time.time(),
            input_payload=payload,
        )

        # ----------------------------------------------------
        # NORMALIZE
        # ----------------------------------------------------

        receipt.route_trace.append(ROUTE_STAGE_NORMALIZE)

        normalized = self.normalize_payload(payload)

        receipt.normalized_payload = normalized

        # ----------------------------------------------------
        # TOKENIZE
        # ----------------------------------------------------

        receipt.route_trace.append(ROUTE_STAGE_TOKENIZE)

        tokens = self.tokenize_payload(normalized)

        receipt.tokens = tokens

        # ----------------------------------------------------
        # LOWER TO IR
        # ----------------------------------------------------

        receipt.route_trace.append(ROUTE_STAGE_IR)

        ir_nodes = self.ir_bridge.lower_tokens(tokens)

        receipt.ir_nodes = ir_nodes

        # ----------------------------------------------------
        # VM EXECUTION
        # ----------------------------------------------------

        receipt.route_trace.append(ROUTE_STAGE_VM)

        vm_result = self.vm_bridge.execute_ir(ir_nodes)

        receipt.vm_result = vm_result

        receipt.receipt_hash72 = vm_result.get(
            "receipt_hash72",
            "",
        )

        receipt.state_hash72 = vm_result.get(
            "state_hash72",
            "",
        )

        receipt.witness_flags = vm_result.get(
            "witness_flags",
            0,
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        receipt.route_trace.append(ROUTE_STAGE_VALIDATE)

        validation = self.validate_execution(vm_result)

        receipt.validation_passed = validation

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        if validation:

            receipt.route_trace.append(ROUTE_STAGE_COMMIT)

            self.state_manager.commit_receipt(
                receipt
            )

        # ----------------------------------------------------
        # VECTOR INDEX
        # ----------------------------------------------------

        if validation:

            receipt.route_trace.append(ROUTE_STAGE_INDEX)

            self.vector_index.insert_receipt(
                receipt
            )

        # ----------------------------------------------------
        # REPLAY PREDICTION
        # ----------------------------------------------------

        receipt.route_trace.append(ROUTE_STAGE_REPLAY)

        replay_predictions = (
            self.replay_engine.predict_next(
                receipt
            )
        )

        receipt.replay_predictions = replay_predictions

        # ----------------------------------------------------
        # SANDBOX PROJECTION
        # ----------------------------------------------------

        receipt.route_trace.append(ROUTE_STAGE_PROJECT)

        projection = (
            self.sandbox_engine.project(
                receipt,
                replay_predictions,
            )
        )

        receipt.sandbox_projection = projection

        return receipt

    # ========================================================
    # NORMALIZATION
    # ========================================================

    def normalize_payload(self, payload: Any):

        if payload is None:
            return ""

        if isinstance(payload, bytes):
            payload = payload.decode("utf-8", errors="ignore")

        return str(payload).strip()

    # ========================================================
    # TOKENIZATION
    # ========================================================

    def tokenize_payload(self, payload: str):

        tokens = []

        for ch in payload:

            token = {
                "char": ch,
                "ord": ord(ch),
                "hash72": hash72_string(ch),
            }

            tokens.append(token)

        return tokens

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_execution(
        self,
        vm_result: Dict[str, Any],
    ) -> bool:

        if not vm_result:
            return False

        if not vm_result.get("success", False):
            return False

        if "receipt_hash72" not in vm_result:
            return False

        if "state_hash72" not in vm_result:
            return False

        return True

# ============================================================
# FACTORY
# ============================================================


_ROUTER_SINGLETON: Optional[HHSExecutionRouter] = None


def get_execution_router() -> HHSExecutionRouter:

    global _ROUTER_SINGLETON

    if _ROUTER_SINGLETON is None:
        _ROUTER_SINGLETON = HHSExecutionRouter()

    return _ROUTER_SINGLETON

# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    router = get_execution_router()

    result = router.execute(
        "HARMONICODE_EXECUTION_TEST"
    )

    print("\n=== ROUTE RECEIPT ===")
    print("route_id:", result.route_id)
    print("receipt_hash72:", result.receipt_hash72)
    print("state_hash72:", result.state_hash72)
    print("validation_passed:", result.validation_passed)
    print("route_trace:", result.route_trace)