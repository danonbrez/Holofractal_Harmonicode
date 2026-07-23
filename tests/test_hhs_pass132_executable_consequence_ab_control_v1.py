"""Compatibility regression path for the historical Pass 132 test identity."""
from hhs_runtime.hhs_pass132_reconstructed_replay_v1 import pass132_reconstructed_self_test


def test_reconstructed_pass132_historical_surface_closes():
    result = pass132_reconstructed_self_test()
    assert result["ok"] is True
    assert result["workload_count"] == 18
    assert result["original_source_bytes_recovered"] is False
