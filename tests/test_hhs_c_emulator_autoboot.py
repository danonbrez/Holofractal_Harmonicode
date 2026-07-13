from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator, HHSEmulatorConfig


def test_c_emulator_boots_and_ticks():
    emulator = HHSCEmulator(
        HHSEmulatorConfig(max_steps_per_run=8)
    )

    boot = emulator.boot()
    assert boot["booted"] is True
    assert boot["runtime"]["step"] == 0

    tick = emulator.tick()
    assert tick["runtime"]["step"] == 1
    assert tick["receipt"] is not None
    assert tick["authority_audit"]["ok"] is True
    assert tick["authority_audit"]["omega"] is True
    assert tick["packet"] is not None


def test_c_emulator_run_is_bounded():
    emulator = HHSCEmulator(
        HHSEmulatorConfig(max_steps_per_run=2)
    )

    result = emulator.run(steps=5)
    assert result["executed_steps"] == 2
    assert result["capped"] is True
    assert result["runtime"]["step"] == 2
