from hhs_backend.runtime.hhs_visual_emulator_session_v1 import visual_emulator_session_self_test

def test_visual_emulator_session_self_test():
    result = visual_emulator_session_self_test()
    assert result["ok"]
    assert result["step"]["receipt"]["history_erased"] is False
    assert not result["unbounded_rejection"]["ok"]
