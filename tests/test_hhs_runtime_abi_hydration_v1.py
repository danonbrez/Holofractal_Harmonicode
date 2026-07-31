from hhs_backend.runtime.runtime_rehydration_engine import HHSRuntimeRehydrationEngine
from hhs_backend.runtime.runtime_snapshot_codec import create_abi_snapshot_packet
from hhs_python.runtime.hhs_ctypes_bridge import HHSRuntimeBridge
from tools.benchmark_hhs_runtime_abi_v1 import benchmark_runtime_abi


def test_runtime_abi_benchmark_emits_verified_report():
    report = benchmark_runtime_abi(iterations=3)

    assert report["schema"] == "HHS_RUNTIME_ABI_BENCHMARK_V1"
    assert report["iterations"] == 3
    assert report["abi_validated"] is True
    assert report["hydration_verified"] is True
    assert report["runtime_step"] == 3
    assert report["state_hash72"]
    assert report["receipt_hash72"]
    assert report["snapshot_hash72"]
    assert report["encoded_snapshot_bytes"] > 0

    for key in (
        "step_stats",
        "receipt_commit_stats",
        "snapshot_round_trip_stats",
    ):
        stats = report[key]
        assert stats["count"] == 3.0
        assert stats["mean_ms"] >= 0.0
        assert stats["median_ms"] >= 0.0
        assert stats["p95_ms"] >= 0.0
        assert stats["max_ms"] >= 0.0


def test_runtime_abi_snapshot_rehydrates_exact_projection():
    runtime = HHSRuntimeBridge()
    assert runtime.validate_abi() is True

    runtime.runtime_step()
    runtime.receipt_commit()
    projection = runtime.export_runtime_dict()

    packet = create_abi_snapshot_packet(
        projection,
        receipt_chain=[],
        event_topology=[],
        branch_topology={"main": {"head": projection["receipt_hash72"]}},
        runtime_id="hhs_runtime_abi_test",
    )

    engine = HHSRuntimeRehydrationEngine()
    result = engine.rehydrate_from_snapshot(packet)
    restored = result["runtime_state"]
    session = result["session"]

    assert restored.step == projection["step"]
    assert restored.transport_flux == projection["transport_flux"]
    assert restored.orientation_flux == projection["orientation_flux"]
    assert restored.constraint_flux == projection["constraint_flux"]
    assert restored.runtime_metadata["state_hash72"] == projection["state_hash72"]
    assert restored.runtime_metadata["receipt_hash72"] == projection["receipt_hash72"]
    assert restored.latest_receipt().receipt_hash72 == projection["receipt_hash72"]
    assert session.runtime_id == "hhs_runtime_abi_test"
    assert session.source_snapshot_hash72 == packet.snapshot_hash72
    assert session.restored_receipt_hash72 == projection["receipt_hash72"]
    assert session.replay_equivalent is True
    assert engine.verify_rehydration_equivalence(packet, restored) is True
