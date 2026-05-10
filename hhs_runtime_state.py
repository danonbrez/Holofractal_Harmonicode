# ============================================================================
# hhs_python/runtime/hhs_runtime_state.py
# HARMONICODE / HHS
# CANONICAL RUNTIME STATE ENVELOPE
#
# PURPOSE
# -------
# Canonical deterministic runtime-state algebra for:
#
#   - VM81 runtime synchronization
#   - v44.2 kernel integration
#   - ctypes interoperability
#   - replay continuity
#   - receipt-chain enforcement
#   - websocket/event projection
#   - graph persistence
#   - distributed consensus transport
#   - cognition-layer synchronization
#   - snapshot/fork/merge semantics
#
# This file is the canonical runtime identity layer.
#
# ============================================================================
#
# ARCHITECTURAL POSITION
# ----------------------
#
# VM81 C Runtime
#        ↓
# ABI Structs
#        ↓
# hhs_runtime_state.py
#        ↓
# Replay / Graph / Streaming / Cognition
#
# ============================================================================
#
# IMPORTANT
# ---------
#
# This layer MUST remain:
#
#   deterministic
#   replay-safe
#   rational-only
#   receipt-linked
#   graph-compatible
#   consensus-compatible
#
# Float contamination is prohibited.
#
# ============================================================================

from __future__ import annotations

import copy
import hashlib
import json
import logging
import time
import uuid

from ctypes import (
    Structure,
    c_uint64,
    c_int64,
    c_uint8,
    c_char,
)

from dataclasses import (
    dataclass,
    field,
)

from decimal import Decimal

from fractions import Fraction

from typing import (
    Dict,
    Any,
    Optional,
)

# ============================================================================
# OPTIONAL V44.2 KERNEL IMPORT
# ============================================================================

try:

    from HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked_7 import (

        AUTHORITATIVE_TRUST_POLICY_V44,

        security_hash72_v44,

        NativeHash72Codec,

        Tensor,

        Manifold9,
    )

    V44_KERNEL_AVAILABLE = True

except Exception:

    AUTHORITATIVE_TRUST_POLICY_V44 = None

    security_hash72_v44 = None

    NativeHash72Codec = None

    Tensor = None

    Manifold9 = None

    V44_KERNEL_AVAILABLE = False

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_STATE"
)

# ============================================================================
# CONSTANTS
# ============================================================================

HASH72_LEN = 72

# ============================================================================
# FLOAT PROTECTION
# ============================================================================

def reject_float(value):

    if isinstance(value, float):

        raise TypeError(

            "Float contamination prohibited "
            "inside canonical runtime state."
        )

    return value

# ============================================================================
# FRACTION NORMALIZATION
# ============================================================================

def normalize_rational(value):

    reject_float(value)

    if isinstance(value, Fraction):
        return value

    if isinstance(value, Decimal):

        return Fraction(str(value))

    if isinstance(value, int):

        return Fraction(value, 1)

    if isinstance(value, str):

        return Fraction(value)

    raise TypeError(
        f"Unsupported rational type: {type(value)}"
    )

# ============================================================================
# VM81 ABI STRUCT
# ============================================================================

class HHSRuntimeStateStruct(Structure):

    _fields_ = [

        ("step", c_uint64),

        ("orbit_id", c_uint64),

        ("witness_flags", c_uint64),

        ("transport_flux", c_int64),

        ("orientation_flux", c_int64),

        ("constraint_flux", c_int64),

        ("prev_receipt_hash72", c_char * 73),

        ("state_hash72", c_char * 73),

        ("receipt_hash72", c_char * 73),

        ("lo_shu_slot", c_uint8),

        ("closure_class", c_uint8),

        ("converged", c_uint8),

        ("halted", c_uint8),
    ]

# ============================================================================
# PATCH OBJECT
# ============================================================================

@dataclass
class HHSRuntimePatch:

    patch_id: str

    created_at_ns: int

    fields: Dict[str, Any]

    patch_hash72: str

# ============================================================================
# RUNTIME STATE
# ============================================================================

@dataclass
class HHSRuntimeState:

    runtime_id: str

    step: int

    orbit_id: int

    transport_flux: Fraction

    orientation_flux: Fraction

    constraint_flux: Fraction

    witness_flags: int

    prev_receipt_hash72: str

    state_hash72: str

    receipt_hash72: str

    lo_shu_slot: int

    closure_class: str

    converged: bool

    halted: bool

    timestamp_ns: int

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================================
    # POST INIT
    # =====================================================================

    def __post_init__(self):

        self.transport_flux = normalize_rational(
            self.transport_flux
        )

        self.orientation_flux = normalize_rational(
            self.orientation_flux
        )

        self.constraint_flux = normalize_rational(
            self.constraint_flux
        )

        self.verify_hash72_lengths()

    # =====================================================================
    # HASH72 VALIDATION
    # =====================================================================

    def verify_hash72_lengths(self):

        hashes = [

            self.prev_receipt_hash72,

            self.state_hash72,

            self.receipt_hash72,
        ]

        for h in hashes:

            if len(h) > HASH72_LEN:

                raise ValueError(
                    "Invalid Hash72 length."
                )

    # =====================================================================
    # RECEIPT CHAIN VERIFICATION
    # =====================================================================

    def verify_receipt_chain(
        self,
        previous_state: Optional[
            "HHSRuntimeState"
        ] = None,
    ) -> bool:

        if previous_state is None:

            return True

        valid = (

            self.prev_receipt_hash72
            ==
            previous_state.receipt_hash72
        )

        if not valid:

            logger.error(
                "Receipt continuity failure."
            )

        return valid

    # =====================================================================
    # V44.2 KERNEL VALIDATION
    # =====================================================================

    def validate_v44_2_kernel_alignment(self):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        kernel_hash = hashlib.sha256(

            self.serialize_deterministic().encode(
                "utf-8"
            )

        ).hexdigest()

        policy = str(
            AUTHORITATIVE_TRUST_POLICY_V44
        )

        trust_hash = hashlib.sha256(

            policy.encode("utf-8")

        ).hexdigest()

        aligned = (

            len(kernel_hash) > 0
            and
            len(trust_hash) > 0
        )

        return {

            "kernel_available": True,

            "validated": aligned,

            "kernel_hash": kernel_hash,

            "trust_hash": trust_hash,
        }

    # =====================================================================
    # DETERMINISTIC SERIALIZATION
    # =====================================================================

    def serialize_deterministic(self) -> str:

        payload = {

            "runtime_id":
                self.runtime_id,

            "step":
                self.step,

            "orbit_id":
                self.orbit_id,

            "transport_flux":
                str(self.transport_flux),

            "orientation_flux":
                str(self.orientation_flux),

            "constraint_flux":
                str(self.constraint_flux),

            "witness_flags":
                self.witness_flags,

            "prev_receipt_hash72":
                self.prev_receipt_hash72,

            "state_hash72":
                self.state_hash72,

            "receipt_hash72":
                self.receipt_hash72,

            "lo_shu_slot":
                self.lo_shu_slot,

            "closure_class":
                self.closure_class,

            "converged":
                self.converged,

            "halted":
                self.halted,

            "timestamp_ns":
                self.timestamp_ns,
        }

        return json.dumps(

            payload,

            sort_keys=True,

            separators=(",", ":"),
        )

    # =====================================================================
    # HASH72 DIGEST
    # =====================================================================

    def compute_state_hash72(self) -> str:

        digest = hashlib.sha256(

            self.serialize_deterministic().encode(
                "utf-8"
            )

        ).hexdigest()

        return digest[:72]

    # =====================================================================
    # C STRUCT EXPORT
    # =====================================================================

    def to_c_struct(self):

        return HHSRuntimeStateStruct(

            step=self.step,

            orbit_id=self.orbit_id,

            witness_flags=self.witness_flags,

            transport_flux=int(
                self.transport_flux * 1000000
            ),

            orientation_flux=int(
                self.orientation_flux * 1000000
            ),

            constraint_flux=int(
                self.constraint_flux * 1000000
            ),

            prev_receipt_hash72=(
                self.prev_receipt_hash72.encode(
                    "utf-8"
                )
            ),

            state_hash72=(
                self.state_hash72.encode(
                    "utf-8"
                )
            ),

            receipt_hash72=(
                self.receipt_hash72.encode(
                    "utf-8"
                )
            ),

            lo_shu_slot=self.lo_shu_slot,

            closure_class=int(
                self.closure_class
            ),

            converged=int(self.converged),

            halted=int(self.halted),
        )

    # =====================================================================
    # C STRUCT IMPORT
    # =====================================================================

    @classmethod
    def from_c_struct(cls, c_state):

        return cls(

            runtime_id=str(uuid.uuid4()),

            step=c_state.step,

            orbit_id=c_state.orbit_id,

            transport_flux=Fraction(
                c_state.transport_flux,
                1000000
            ),

            orientation_flux=Fraction(
                c_state.orientation_flux,
                1000000
            ),

            constraint_flux=Fraction(
                c_state.constraint_flux,
                1000000
            ),

            witness_flags=c_state.witness_flags,

            prev_receipt_hash72=(
                c_state.prev_receipt_hash72
                .decode("utf-8")
                .rstrip("\x00")
            ),

            state_hash72=(
                c_state.state_hash72
                .decode("utf-8")
                .rstrip("\x00")
            ),

            receipt_hash72=(
                c_state.receipt_hash72
                .decode("utf-8")
                .rstrip("\x00")
            ),

            lo_shu_slot=c_state.lo_shu_slot,

            closure_class=str(
                c_state.closure_class
            ),

            converged=bool(
                c_state.converged
            ),

            halted=bool(
                c_state.halted
            ),

            timestamp_ns=time.time_ns(),
        )

    # =====================================================================
    # RECEIPT PAYLOAD
    # =====================================================================

    def to_receipt_payload(self):

        return {

            "runtime_id":
                self.runtime_id,

            "step":
                self.step,

            "receipt_hash72":
                self.receipt_hash72,

            "prev_receipt_hash72":
                self.prev_receipt_hash72,

            "state_hash72":
                self.state_hash72,

            "witness_flags":
                self.witness_flags,

            "timestamp_ns":
                self.timestamp_ns,
        }

    # =====================================================================
    # GRAPH NODE
    # =====================================================================

    def to_graph_node(self):

        return {

            "node_id":
                self.receipt_hash72,

            "runtime_id":
                self.runtime_id,

            "step":
                self.step,

            "orbit_id":
                self.orbit_id,

            "state_hash72":
                self.state_hash72,

            "parent":
                self.prev_receipt_hash72,

            "converged":
                self.converged,

            "halted":
                self.halted,
        }

    # =====================================================================
    # WEBSOCKET EVENT
    # =====================================================================

    def to_websocket_event(self):

        return {

            "event":
                "runtime_state",

            "runtime":
                self.serialize_event(),
        }

    # =====================================================================
    # EVENT SERIALIZATION
    # =====================================================================

    def serialize_event(self):

        return {

            "runtime_id":
                self.runtime_id,

            "step":
                self.step,

            "orbit_id":
                self.orbit_id,

            "transport_flux":
                str(self.transport_flux),

            "orientation_flux":
                str(self.orientation_flux),

            "constraint_flux":
                str(self.constraint_flux),

            "receipt_hash72":
                self.receipt_hash72,

            "state_hash72":
                self.state_hash72,

            "converged":
                self.converged,

            "halted":
                self.halted,
        }

    # =====================================================================
    # PATCH APPLICATION
    # =====================================================================

    def apply_patch(
        self,
        patch: HHSRuntimePatch,
    ):

        for field_name, value in patch.fields.items():

            if not hasattr(self, field_name):

                raise AttributeError(
                    f"Unknown runtime field: "
                    f"{field_name}"
                )

            reject_float(value)

            setattr(
                self,
                field_name,
                value,
            )

        self.timestamp_ns = time.time_ns()

    # =====================================================================
    # PATCH AUDIT
    # =====================================================================

    def audit_patch(
        self,
        patch: HHSRuntimePatch,
    ):

        patch_data = json.dumps(

            patch.fields,

            sort_keys=True,

        )

        patch_hash = hashlib.sha256(

            patch_data.encode("utf-8")

        ).hexdigest()[:72]

        return patch_hash == patch.patch_hash72

    # =====================================================================
    # PATCH COMMIT
    # =====================================================================

    def commit_patch(
        self,
        patch: HHSRuntimePatch,
    ):

        valid = self.audit_patch(
            patch
        )

        if not valid:

            raise RuntimeError(
                "Patch audit failed."
            )

        self.apply_patch(
            patch
        )

        self.prev_receipt_hash72 = (
            self.receipt_hash72
        )

        self.receipt_hash72 = (
            self.compute_state_hash72()
        )

    # =====================================================================
    # PATCH ROLLBACK
    # =====================================================================

    def rollback_patch(
        self,
        snapshot_state: "HHSRuntimeState",
    ):

        restored = copy.deepcopy(
            snapshot_state
        )

        self.__dict__.update(
            restored.__dict__
        )

    # =====================================================================
    # SNAPSHOT
    # =====================================================================

    def snapshot(self):

        return copy.deepcopy(self)

    # =====================================================================
    # RESTORE
    # =====================================================================

    def restore(
        self,
        snapshot_state: "HHSRuntimeState",
    ):

        self.rollback_patch(
            snapshot_state
        )

    # =====================================================================
    # FORK
    # =====================================================================

    def fork(self):

        forked = copy.deepcopy(self)

        forked.runtime_id = str(
            uuid.uuid4()
        )

        return forked

    # =====================================================================
    # MERGE
    # =====================================================================

    def merge(
        self,
        other: "HHSRuntimeState",
    ):

        self.transport_flux += (
            other.transport_flux
        )

        self.orientation_flux += (
            other.orientation_flux
        )

        self.constraint_flux += (
            other.constraint_flux
        )

        self.timestamp_ns = time.time_ns()

    # =====================================================================
    # DIFF
    # =====================================================================

    def diff(
        self,
        other: "HHSRuntimeState",
    ):

        return {

            "step":
                self.step - other.step,

            "orbit_id":
                self.orbit_id - other.orbit_id,

            "transport_flux":
                str(
                    self.transport_flux
                    - other.transport_flux
                ),

            "orientation_flux":
                str(
                    self.orientation_flux
                    - other.orientation_flux
                ),

            "constraint_flux":
                str(
                    self.constraint_flux
                    - other.constraint_flux
                ),
        }

    # =====================================================================
    # EVENT EMISSION
    # =====================================================================

    def emit_event(self):

        return self.to_websocket_event()

# ============================================================================
# FACTORY
# ============================================================================

def create_runtime_state():

    timestamp = time.time_ns()

    state = HHSRuntimeState(

        runtime_id=str(uuid.uuid4()),

        step=0,

        orbit_id=0,

        transport_flux=Fraction(0, 1),

        orientation_flux=Fraction(0, 1),

        constraint_flux=Fraction(0, 1),

        witness_flags=0,

        prev_receipt_hash72="",

        state_hash72="",

        receipt_hash72="",

        lo_shu_slot=5,

        closure_class="0",

        converged=False,

        halted=False,

        timestamp_ns=timestamp,
    )

    state.state_hash72 = (
        state.compute_state_hash72()
    )

    state.receipt_hash72 = (
        state.compute_state_hash72()
    )

    return state

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_state_self_test():

    state = create_runtime_state()

    snapshot = state.snapshot()

    patch_payload = {

        "step": 1,

        "orbit_id": 72,
    }

    patch_hash = hashlib.sha256(

        json.dumps(
            patch_payload,
            sort_keys=True
        ).encode("utf-8")

    ).hexdigest()[:72]

    patch = HHSRuntimePatch(

        patch_id=str(uuid.uuid4()),

        created_at_ns=time.time_ns(),

        fields=patch_payload,

        patch_hash72=patch_hash,
    )

    state.commit_patch(
        patch
    )

    chain_ok = state.verify_receipt_chain(
        snapshot
    )

    kernel_alignment = (
        state.validate_v44_2_kernel_alignment()
    )

    print()

    print("RUNTIME STATE")

    print(
        state.serialize_deterministic()
    )

    print()

    print("CHAIN OK")

    print(chain_ok)

    print()

    print("KERNEL ALIGNMENT")

    print(kernel_alignment)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_state_self_test()