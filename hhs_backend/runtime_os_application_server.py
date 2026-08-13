"""Full HHS application composition with the TypeScript Runtime OS at ``/``.

All Pass 174+ application/server composition remains inherited from
:mod:`hhs_backend.application_ide_server`. This final layer removes only its
public-root visual mount, installs the Pass-218 durable lifecycle gate, the I13
diagnostic/operator authority control plane, the I14 multi-party approval
plane, and the I15/I16 maintenance-consumption plane, then projects the same
backend through ``hhs_gui/dist``. Supporting surfaces such as
``/runtime-console`` remain intact.
"""
from __future__ import annotations

from hhs_backend.application_ide_server import app as inherited_app
from hhs_backend.runtime_os_pass218_authority_i13 import (
    PASS218_AUTHORITY_ACTION_PREPARE_PATH,
    PASS218_AUTHORITY_ALERTS_PATH,
    PASS218_AUTHORITY_RUN_RECORD_PATH,
    PASS218_AUTHORITY_STATUS_PATH,
    install_pass218_authority_control_plane,
)
from hhs_backend.runtime_os_pass218_approval_i14 import (
    PASS218_I14_EVALUATE_PATH,
    PASS218_I14_PREFLIGHT_PATH,
    PASS218_I14_STATUS_PATH,
    install_pass218_i14_approval_control_plane,
)
from hhs_backend.runtime_os_pass218_consumption_i15 import (
    PASS218_I15_ATTEST_PATH,
    PASS218_I15_CLAIM_PATH,
    PASS218_I15_RECONCILE_PATH,
    PASS218_I15_STATUS_PATH,
)
from hhs_backend.runtime_os_pass218_consumption_i16 import (
    PASS218_I16_STATUS_PATH,
    PASS218_I16_SYNCHRONIZE_PATH,
    install_pass218_i16_consumption_control_plane,
)
from hhs_backend.runtime_os_pass218_lifecycle import (
    PASS218_RUNTIME_STATUS_PATH,
    install_pass218_runtime_os_lifecycle,
    resolve_pass218_state_root,
)
from hhs_backend.runtime_os_projection import (
    RUNTIME_OS_ASSETS,
    RUNTIME_OS_INDEX,
    RUNTIME_OS_ROOT,
    project_runtime_os,
)

PUBLIC_MOUNT_NAME = "hhs-runtime-os-application-home"

app = inherited_app
app.title = "HHS Runtime OS Application Environment"
app.description = (
    "Full cumulative HHS application, API, assistant, VM81, Hash72/Hash216, pass, "
    "workspace, compiler, emulator, replay, and runtime surfaces projected through "
    "the TypeScript/React/Vite Runtime OS."
)
PASS218_RUNTIME_OS_LIFECYCLE = install_pass218_runtime_os_lifecycle(app)
PASS218_AUTHORITY_CONTROL_PLANE = install_pass218_authority_control_plane(
    app,
    PASS218_RUNTIME_OS_LIFECYCLE,
    state_root=resolve_pass218_state_root(),
)
PASS218_I14_APPROVAL_CONTROL_PLANE = install_pass218_i14_approval_control_plane(
    app,
    PASS218_AUTHORITY_CONTROL_PLANE,
    state_root=resolve_pass218_state_root(),
)
PASS218_I16_CONSUMPTION_CONTROL_PLANE = install_pass218_i16_consumption_control_plane(
    app,
    PASS218_RUNTIME_OS_LIFECYCLE,
    PASS218_AUTHORITY_CONTROL_PLANE,
    PASS218_I14_APPROVAL_CONTROL_PLANE,
    state_root=resolve_pass218_state_root(),
)
PASS218_I15_CONSUMPTION_CONTROL_PLANE = PASS218_I16_CONSUMPTION_CONTROL_PLANE
project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)

__all__ = [
    "PASS218_AUTHORITY_ACTION_PREPARE_PATH",
    "PASS218_AUTHORITY_ALERTS_PATH",
    "PASS218_AUTHORITY_CONTROL_PLANE",
    "PASS218_AUTHORITY_RUN_RECORD_PATH",
    "PASS218_AUTHORITY_STATUS_PATH",
    "PASS218_I14_APPROVAL_CONTROL_PLANE",
    "PASS218_I14_EVALUATE_PATH",
    "PASS218_I14_PREFLIGHT_PATH",
    "PASS218_I14_STATUS_PATH",
    "PASS218_I15_ATTEST_PATH",
    "PASS218_I15_CLAIM_PATH",
    "PASS218_I15_CONSUMPTION_CONTROL_PLANE",
    "PASS218_I15_RECONCILE_PATH",
    "PASS218_I15_STATUS_PATH",
    "PASS218_I16_CONSUMPTION_CONTROL_PLANE",
    "PASS218_I16_STATUS_PATH",
    "PASS218_I16_SYNCHRONIZE_PATH",
    "PASS218_RUNTIME_OS_LIFECYCLE",
    "PASS218_RUNTIME_STATUS_PATH",
    "PUBLIC_MOUNT_NAME",
    "RUNTIME_OS_ASSETS",
    "RUNTIME_OS_INDEX",
    "RUNTIME_OS_ROOT",
    "app",
]
