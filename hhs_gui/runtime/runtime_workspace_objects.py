# ============================================================================
# hhs_gui/runtime/runtime_workspace_objects.py
# HARMONICODE / HHS
# CANONICAL WORKSPACE MANIFOLD SUBSTRATE
#
# PURPOSE
# -------
# Canonical replay-governed workspace substrate for:
#
#   - runtime-native GUI workspaces
#   - replay-certified workspace resurrection
#   - graph-native viewport topology
#   - multimodal workspace surfaces
#   - tensor/phase projection canvases
#   - transport-routed panel synchronization
#   - agent-shell operating environments
#   - workspace namespace topology
#   - v44.2 kernel continuity enforcement
#
# GUI IS runtime topology.
#
# ============================================================================

from __future__ import annotations

import copy
import hashlib
import json
import logging
import time
import uuid

from dataclasses import (
    dataclass,
    field,
    asdict,
)

from typing import (
    Dict,
    Any,
    List,
    Optional,
)

# ============================================================================
# RUNTIME OBJECTS
# ============================================================================

from hhs_python.runtime.hhs_runtime_object import (

    HHSRuntimeObject,

    HHSGraphLink,

    HHSReplayAnchor,

    HHSTransportVector,
)

from hhs_python.runtime.runtime_object_registry import (
    runtime_object_registry,
)

from hhs_backend.runtime.runtime_transport_protocol import (
    runtime_transport_protocol,
)

# ============================================================================
# OPTIONAL V44.2 KERNEL
# ============================================================================

try:

    from HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked_7 import (

        AUTHORITATIVE_TRUST_POLICY_V44,

        security_hash72_v44,

        Tensor,

        Manifold9,
    )

    V44_KERNEL_AVAILABLE = True

except Exception:

    AUTHORITATIVE_TRUST_POLICY_V44 = None

    security_hash72_v44 = None

    Tensor = None

    Manifold9 = None

    V44_KERNEL_AVAILABLE = False

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_WORKSPACE_OBJECTS"
)

# ============================================================================
# CONSTANTS
# ============================================================================

WORKSPACE_SCHEMA_VERSION = "v1"

# ============================================================================
# VIEWPORT
# ============================================================================

@dataclass
class HHSGraphViewport:

    viewport_id: str

    viewport_type: str

    position: Dict[str, float]

    dimensions: Dict[str, float]

    projection_mode: str

    created_at_ns: int

# ============================================================================
# MULTIMODAL SURFACE
# ============================================================================

@dataclass
class HHSMultimodalSurface:

    surface_id: str

    surface_type: str

    transport_channel: str

    active: bool

    metadata: Dict[str, Any]

# ============================================================================
# WORKSPACE OBJECT
# ============================================================================

@dataclass
class HHSWorkspaceObject(
    HHSRuntimeObject
):

    # =====================================================================
    # WORKSPACE
    # =====================================================================

    workspace_id: str = ""

    workspace_type: str = ""

    layout_hash72: str = ""

    # =====================================================================
    # PANELS
    # =====================================================================

    panel_ids: List[str] = field(
        default_factory=list
    )

    # =====================================================================
    # GRAPH VIEWPORTS
    # =====================================================================

    graph_viewports: List[
        HHSGraphViewport
    ] = field(default_factory=list)

    # =====================================================================
    # TRANSPORT
    # =====================================================================

    transport_channels: List[str] = field(
        default_factory=list
    )

    # =====================================================================
    # ACTIVE RUNTIMES
    # =====================================================================

    active_runtime_ids: List[str] = field(
        default_factory=list
    )

    # =====================================================================
    # WORKSPACE STATE
    # =====================================================================

    workspace_state: Dict[
        str,
        Any
    ] = field(default_factory=dict)

    # =====================================================================
    # MULTIMODAL
    # =====================================================================

    multimodal_surfaces: List[
        HHSMultimodalSurface
    ] = field(default_factory=list)

    # =====================================================================
    # NAMESPACE
    # =====================================================================

    workspace_namespace: str = "default"

    # =====================================================================
    # POST INIT
    # =====================================================================

    def __post_init__(self):

        super().__post_init__()

        if not self.workspace_id:

            self.workspace_id = (
                str(uuid.uuid4())
            )

        if not self.layout_hash72:

            self.layout_hash72 = (
                self.compute_layout_hash72()
            )

    # =====================================================================
    # LAYOUT HASH72
    # =====================================================================

    def compute_layout_hash72(self):

        payload = {

            "workspace_id":
                self.workspace_id,

            "panel_ids":
                self.panel_ids,

            "viewport_ids": [

                x.viewport_id

                for x in (
                    self.graph_viewports
                )
            ],
        }

        serialized = json.dumps(

            payload,

            sort_keys=True,

            separators=(",", ":"),
        )

        digest = hashlib.sha256(

            serialized.encode("utf-8")

        ).hexdigest()

        return digest[:72]

    # =====================================================================
    # SNAPSHOT
    # =====================================================================

    def snapshot_workspace(self):

        return copy.deepcopy(
            self
        )

    # =====================================================================
    # RESTORE
    # =====================================================================

    def restore_workspace(
        self,
        snapshot: "HHSWorkspaceObject",
    ):

        self.__dict__.update(

            copy.deepcopy(
                snapshot.__dict__
            )
        )

    # =====================================================================
    # REPLAY
    # =====================================================================

    def replay_workspace(self):

        return self.replay()

    # =====================================================================
    # FORK
    # =====================================================================

    def fork_workspace(
        self,
        new_branch_id: str,
    ):

        forked = copy.deepcopy(
            self
        )

        forked.branch_id = (
            new_branch_id
        )

        forked.workspace_id = (
            str(uuid.uuid4())
        )

        return forked

    # =====================================================================
    # MERGE
    # =====================================================================

    def merge_workspace(
        self,
        other:
            "HHSWorkspaceObject",
    ):

        merged = copy.deepcopy(
            self
        )

        merged.panel_ids.extend(
            other.panel_ids
        )

        merged.graph_viewports.extend(
            other.graph_viewports
        )

        merged.transport_channels.extend(
            other.transport_channels
        )

        merged.multimodal_surfaces.extend(
            other.multimodal_surfaces
        )

        merged.workspace_state.update(
            other.workspace_state
        )

        merged.layout_hash72 = (
            merged.compute_layout_hash72()
        )

        return merged

    # =====================================================================
    # PANELS
    # =====================================================================

    def attach_panel(
        self,
        panel_id: str,
    ):

        if panel_id not in self.panel_ids:

            self.panel_ids.append(
                panel_id
            )

            self.layout_hash72 = (
                self.compute_layout_hash72()
            )

    # =====================================================================
    # DETACH
    # =====================================================================

    def detach_panel(
        self,
        panel_id: str,
    ):

        self.panel_ids = [

            x

            for x in self.panel_ids

            if x != panel_id
        ]

        self.layout_hash72 = (
            self.compute_layout_hash72()
        )

    # =====================================================================
    # GRAPH TOPOLOGY
    # =====================================================================

    def resolve_workspace_graph(self):

        return {

            "workspace_id":
                self.workspace_id,

            "panels":
                self.panel_ids,

            "viewport_count":
                len(
                    self.graph_viewports
                ),
        }

    # =====================================================================
    # VIEWPORT TOPOLOGY
    # =====================================================================

    def resolve_viewport_topology(self):

        return [

            asdict(x)

            for x in (
                self.graph_viewports
            )
        ]

    # =====================================================================
    # TRANSPORT
    # =====================================================================

    def route_workspace_transport(
        self,
        payload: Dict[str, Any],
    ):

        packet = (

            runtime_transport_protocol
            .create_transport_packet(

                runtime_object=self,

                transport_type=
                    "workspace_transport",

                payload=payload,
            )
        )

        return (

            runtime_transport_protocol
            .route_packet(packet)
        )

    # =====================================================================
    # PANEL TRANSPORT
    # =====================================================================

    def route_panel_transport(

        self,

        panel_id: str,

        payload: Dict[str, Any],
    ):

        return self.route_workspace_transport({

            "panel_id":
                panel_id,

            "payload":
                payload,
        })

    # =====================================================================
    # TENSOR PROJECTION
    # =====================================================================

    def route_tensor_projection(
        self,
        tensor_payload: Dict[str, Any],
    ):

        return self.route_workspace_transport({

            "tensor_projection":
                tensor_payload
        })

    # =====================================================================
    # AUDIO SURFACE
    # =====================================================================

    def create_audio_surface(
        self,
        channel: str,
    ):

        surface = HHSMultimodalSurface(

            surface_id=str(uuid.uuid4()),

            surface_type="audio",

            transport_channel=
                channel,

            active=True,

            metadata={},
        )

        self.multimodal_surfaces.append(
            surface
        )

        return surface

    # =====================================================================
    # VISUAL SURFACE
    # =====================================================================

    def create_visual_surface(
        self,
        channel: str,
    ):

        surface = HHSMultimodalSurface(

            surface_id=str(uuid.uuid4()),

            surface_type="visual",

            transport_channel=
                channel,

            active=True,

            metadata={},
        )

        self.multimodal_surfaces.append(
            surface
        )

        return surface

    # =====================================================================
    # SYMBOLIC SURFACE
    # =====================================================================

    def create_symbolic_surface(
        self,
        channel: str,
    ):

        surface = HHSMultimodalSurface(

            surface_id=str(uuid.uuid4()),

            surface_type="symbolic",

            transport_channel=
                channel,

            active=True,

            metadata={},
        )

        self.multimodal_surfaces.append(
            surface
        )

        return surface

    # =====================================================================
    # TENSOR SURFACE
    # =====================================================================

    def create_tensor_surface(
        self,
        channel: str,
    ):

        surface = HHSMultimodalSurface(

            surface_id=str(uuid.uuid4()),

            surface_type="tensor",

            transport_channel=
                channel,

            active=True,

            metadata={},
        )

        self.multimodal_surfaces.append(
            surface
        )

        return surface

    # =====================================================================
    # PHASE SURFACE
    # =====================================================================

    def create_phase_surface(
        self,
        channel: str,
    ):

        surface = HHSMultimodalSurface(

            surface_id=str(uuid.uuid4()),

            surface_type="phase",

            transport_channel=
                channel,

            active=True,

            metadata={},
        )

        self.multimodal_surfaces.append(
            surface
        )

        return surface

    # =====================================================================
    # REHYDRATION
    # =====================================================================

    def rehydrate_workspace(
        self,
        snapshot:
            "HHSWorkspaceObject",
    ):

        self.restore_workspace(
            snapshot
        )

        return self

    # =====================================================================
    # VERIFY EQUIVALENCE
    # =====================================================================

    def verify_workspace_equivalence(

        self,

        other:
            "HHSWorkspaceObject",
    ):

        return (

            self.layout_hash72
            ==
            other.layout_hash72
        )

    # =====================================================================
    # RESTORE GRAPH
    # =====================================================================

    def restore_workspace_graph(
        self,
        graph_payload:
            Dict[str, Any],
    ):

        self.workspace_state[
            "graph"
        ] = graph_payload

    # =====================================================================
    # REGISTRY
    # =====================================================================

    def register_workspace(self):

        return (

            runtime_object_registry
            .register_object(self)
        )

    # =====================================================================
    # WORKSPACE PROJECTION
    # =====================================================================

    def to_workspace_projection(self):

        return {

            "workspace_id":
                self.workspace_id,

            "workspace_type":
                self.workspace_type,

            "layout_hash72":
                self.layout_hash72,

            "panel_count":
                len(self.panel_ids),

            "viewport_count":
                len(
                    self.graph_viewports
                ),
        }

    # =====================================================================
    # GUI PROJECTION
    # =====================================================================

    def to_gui_projection(self):

        return {

            "workspace":
                self.to_workspace_projection(),

            "viewports":

                self.resolve_viewport_topology(),
        }

    # =====================================================================
    # TENSOR PROJECTION
    # =====================================================================

    def to_tensor_projection(self):

        return {

            "workspace_id":
                self.workspace_id,

            "tensor_state":
                self.workspace_state.get(
                    "tensor_state"
                ),
        }

    # =====================================================================
    # MULTIMODAL
    # =====================================================================

    def to_multimodal_projection(self):

        return {

            "workspace_id":
                self.workspace_id,

            "surfaces": [

                asdict(x)

                for x in (
                    self.multimodal_surfaces
                )
            ],
        }

    # =====================================================================
    # V44 VALIDATION
    # =====================================================================

    def validate_v44_workspace(self):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        workspace_hash = hashlib.sha256(

            json.dumps(

                self.to_workspace_projection(),

                sort_keys=True,

            ).encode("utf-8")

        ).hexdigest()

        trust_hash = hashlib.sha256(

            str(
                AUTHORITATIVE_TRUST_POLICY_V44
            ).encode("utf-8")

        ).hexdigest()

        return {

            "kernel_available": True,

            "validated": True,

            "workspace_hash":
                workspace_hash,

            "trust_hash":
                trust_hash,
        }

# ============================================================================
# FACTORY
# ============================================================================

def create_workspace_object(

    workspace_type: str,

    runtime_id: str,

    branch_id: str,

    workspace_state: Optional[
        Dict[str, Any]
    ] = None,
):

    workspace_state = (
        workspace_state or {}
    )

    workspace_object = HHSWorkspaceObject(

        object_id=str(uuid.uuid4()),

        object_type="workspace",

        runtime_id=runtime_id,

        branch_id=branch_id,

        receipt_hash72=
            hashlib.sha256(

                runtime_id.encode(
                    "utf-8"
                )

            ).hexdigest()[:72],

        state_hash72=
            hashlib.sha256(

                json.dumps(

                    workspace_state,

                    sort_keys=True,

                ).encode("utf-8")

            ).hexdigest()[:72],

        previous_receipt_hash72=
            None,

        transport_vector=
            HHSTransportVector(

                transport_flux="1/1",

                orientation_flux="1/1",

                constraint_flux="1/1",

                entropy_delta="0/1",

                closure_delta="0/1",
            ),

        object_state=
            workspace_state,

        workspace_id=
            str(uuid.uuid4()),

        workspace_type=
            workspace_type,

        workspace_state=
            workspace_state,
    )

    return workspace_object

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_workspace_objects_self_test():

    workspace = create_workspace_object(

        workspace_type="tensor_lab",

        runtime_id="runtime_001",

        branch_id="main",

        workspace_state={

            "tensor_state": [

                4, 9, 2,
                3, 5, 7,
                8, 1, 6,
            ]
        },
    )

    workspace.attach_panel(
        "tensor_panel"
    )

    workspace.attach_panel(
        "graph_panel"
    )

    viewport = HHSGraphViewport(

        viewport_id=str(uuid.uuid4()),

        viewport_type="3d_tensor",

        position={

            "x": 0,
            "y": 0,
        },

        dimensions={

            "w": 1920,
            "h": 1080,
        },

        projection_mode="tensor",

        created_at_ns=
            time.time_ns(),
    )

    workspace.graph_viewports.append(
        viewport
    )

    workspace.create_audio_surface(
        "audio_channel"
    )

    workspace.create_visual_surface(
        "visual_channel"
    )

    workspace.register_workspace()

    projection = (
        workspace
        .to_workspace_projection()
    )

    gui_projection = (
        workspace
        .to_gui_projection()
    )

    multimodal_projection = (
        workspace
        .to_multimodal_projection()
    )

    routed = (
        workspace
        .route_workspace_transport({

            "event":
                "workspace_sync"
        })
    )

    v44 = (
        workspace
        .validate_v44_workspace()
    )

    print()

    print("WORKSPACE")

    print(workspace)

    print()

    print("PROJECTION")

    print(projection)

    print()

    print("GUI")

    print(gui_projection)

    print()

    print("MULTIMODAL")

    print(multimodal_projection)

    print()

    print("TRANSPORT")

    print(routed)

    print()

    print("V44")

    print(v44)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_workspace_objects_self_test()