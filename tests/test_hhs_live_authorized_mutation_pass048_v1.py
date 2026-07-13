from hhs_backend.runtime.live_authorized_mutation_contract_v1 import (
    live_authorized_mutation_contract_self_test,
    validate_authorized_mutation_command,
)
from hhs_backend.runtime.live_state_reversal_witness_v1 import live_state_reversal_witness_self_test
from hhs_backend.runtime.live_mutation_receipt_chain_v1 import live_mutation_receipt_chain_self_test
from hhs_backend.runtime.live_authorized_mutation_executor_v1 import (
    LiveAuthorizedMutationExecutor,
    live_authorized_mutation_executor_self_test,
)
from hhs_backend.runtime.live_gui_command_authority_loop_v1 import LiveGUICommandAuthorityLoop
import asyncio
from pathlib import Path


def test_pass048_authorized_mutation_contract_allowlist_and_direct_rejection():
    result = live_authorized_mutation_contract_self_test()
    assert result["ok"] is True
    direct = validate_authorized_mutation_command({
        "requested_operation": "direct.mutate_runtime_truth",
        "payload": {"mutate_runtime_truth_directly": True},
    })
    assert direct["ok"] is False
    assert "REJECT_UI_EVENT_AS_RUNTIME_TRUTH" in direct["reasons"]


def test_pass048_reversal_witness_requires_pre_transform_post_identity():
    result = live_state_reversal_witness_self_test()
    assert result["ok"] is True
    assert result["witness"]["pre_state_hash72"]
    assert result["witness"]["transformation_hash72"]
    assert result["witness"]["post_state_hash72"]


def test_pass048_mutation_receipt_chain_requires_reversal_witness_and_receipt():
    result = live_mutation_receipt_chain_self_test()
    assert result["ok"] is True
    assert result["receipt"]["receipt_hash72"]
    assert result["receipt"]["reversal_witness"]


def test_pass048_executor_emits_authorized_mutation_receipt():
    result = live_authorized_mutation_executor_self_test()
    assert result["ok"] is True
    assert result["admitted_snapshot"]["receipt_hash72"]
    assert result["admitted_snapshot"]["pre_state_hash72"]
    assert result["admitted_snapshot"]["post_state_hash72"]
    assert result["rejected"]["ok"] is False


def test_pass048_gui_command_loop_routes_authorized_mutation_without_gui_authority():
    async def run():
        loop = LiveGUICommandAuthorityLoop(live_workflow=None)
        result = await loop.submit({
            "requested_operation": "runtime.request_status_snapshot",
            "execution_mode": "AUTHORIZED_MUTATION",
            "client_sequence_id": 1,
        })
        return result

    result = asyncio.run(run())
    assert result["ok"] is True
    assert result["status"] == "GUI_COMMAND_ADMITTED_AUTHORIZED_MUTATION"
    assert result["receipt_hash72"]
    assert result["pre_state_hash72"]
    assert result["post_state_hash72"]
    assert result["gui_mutated_runtime_truth"] is False


def test_pass048_gui_command_loop_rejects_non_allowlisted_live_mutation():
    async def run():
        loop = LiveGUICommandAuthorityLoop(live_workflow=None)
        result = await loop.submit({
            "requested_operation": "plugin.execute_arbitrary",
            "execution_mode": "AUTHORIZED_MUTATION",
            "target_surface": "service:plugin.execute_arbitrary",
            "contract_schema": "HHS_ARBITRARY_PLUGIN_MUTATION_V1",
            "client_sequence_id": 1,
        })
        return result

    result = asyncio.run(run())
    assert result["ok"] is False
    assert result["status"] in {
        "REJECT_MUTATION_WITHOUT_RECEIPT",
        "REJECT_GUI_COMMAND_NOT_KERNEL_DERIVED",
        "REJECT_GUI_COMMAND_NOT_ADMISSIBLE",
    }


def test_pass048_gui_source_declares_mutation_projection_not_browser_authority():
    root = Path(__file__).resolve().parents[1]
    client = (root / "hhs_gui/runtime_os/core/RuntimeMutationClient.ts").read_text()
    panel = (root / "hhs_gui/runtime_os/core/RuntimeMutationPanel.tsx").read_text()
    shell = (root / "hhs_gui/runtime_os/core/RuntimeShell.tsx").read_text()
    assert "AUTHORIZED_MUTATION" in client
    assert "assume_success_locally: false" in client
    assert "runtime-mutation-panel" in panel
    assert "pre_state_hash72" in panel
    assert "transformation_hash72" in panel
    assert "post_state_hash72" in panel
    assert "RuntimeMutationPanel" in shell
