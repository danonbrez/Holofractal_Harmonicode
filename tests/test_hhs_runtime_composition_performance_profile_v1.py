from hhs_runtime.hhs_runtime_composition_performance_profile_v1 import build_performance_profile


def test_runtime_composition_performance_profile_passes():
    profile = build_performance_profile()
    assert profile["ok"] is True
    assert profile["cache_reuse"]["second_cache_hit"] is True
    assert profile["decay_lifecycle"]["expanded_payload_persisted_after_decay"] is False
