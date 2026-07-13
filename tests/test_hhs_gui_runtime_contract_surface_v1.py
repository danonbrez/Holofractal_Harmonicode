from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "hhs_gui" / "runtime_os" / "core"


def test_frontend_contract_envelope_adapter_exists():
    adapter = CORE / "RuntimeContractEnvelope.ts"
    text = adapter.read_text(encoding="utf-8")
    assert "HHS_CANONICAL_RUNTIME_CONTRACT_V1" in text
    assert "HHS_HASH72_KERNEL_WITNESS_V1" in text
    assert "unwrapRuntimePacketEnvelope" in text
    assert "unwrapAPIResponseEnvelope" in text
    assert "validateRuntimeContract" in text
    assert "HASH72_LENGTH = 72" in text


def test_runtime_kernel_bridge_consumes_contract_envelopes():
    text = (CORE / "RuntimeKernelBridge.ts").read_text(encoding="utf-8")
    assert "unwrapRuntimePacketEnvelope" in text
    assert "validateRuntimeContract" in text
    assert "lastContractHash72" in text
    assert "lastContractValid" in text
    assert "lastContractReasons" in text


def test_runtime_socket_manager_surfaces_contract_metadata():
    text = (CORE / "RuntimeSocketManager.ts").read_text(encoding="utf-8")
    assert "unwrapRuntimePacketEnvelope" in text
    assert "validateRuntimeContract" in text
    assert "contract_hash72" in text
    assert "payload_hash72" in text
    assert "contract_valid" in text
    assert "contract_reasons" in text


def test_runtime_kernel_bridge_exposes_guarded_srcg_api_dispatch():
    text = (CORE / "RuntimeKernelBridge.ts").read_text(encoding="utf-8")
    assert "apiBaseUrl" in text
    assert "postContractAPI" in text
    assert "dispatchService" in text
    assert "executeSRCGSelfSolve" in text
    assert "/api/runtime/srcg/selfsolve" in text
    assert "validateRuntimeContract" in text
