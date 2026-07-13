from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_interpret_compile_emulate_gui_sources():
    interpreter = (ROOT / "hhs_gui/runtime_os/console/InterpreterConsole.tsx").read_text(encoding="utf-8")
    compiler = (ROOT / "hhs_gui/runtime_os/compiler/CompilerWorkbench.tsx").read_text(encoding="utf-8")
    emulator = (ROOT / "hhs_gui/runtime_os/emulator/EmulatorControlPanel.tsx").read_text(encoding="utf-8")
    assert "interpret.execute" in interpreter
    assert "No arbitrary host-language evaluation" in interpreter
    assert "compile.execute" in compiler
    assert "Compilation does not imply execution authorization" in compiler
    assert "emulator.step" in emulator
    assert "rewind never erases history" in emulator
