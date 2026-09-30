from pathlib import Path
import re
import subprocess

PARENT = "c8cab5b215e4d461e7829e5b6aac69f9afd4254e"
SOURCE = Path("examples/ParticleSimulation.html")


def current_source() -> str:
    return SOURCE.read_text(encoding="utf-8")


def parent_source() -> str:
    return subprocess.check_output(
        ["git", "show", f"{PARENT}:examples/ParticleSimulation.html"],
        text=True,
    )


def extract_function(text: str, name: str) -> str:
    needle = f"function {name}("
    start = text.index(needle)
    brace = text.index("{", start)
    i = brace
    depth = 0
    quote = None
    line_comment = False
    block_comment = False
    escape = False

    while i < len(text):
        ch = text[i]
        nx = text[i + 1] if i + 1 < len(text) else ""

        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue

        if block_comment:
            if ch == "*" and nx == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue

        if quote is not None:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
            i += 1
            continue

        if ch == "/" and nx == "/":
            line_comment = True
            i += 2
            continue
        if ch == "/" and nx == "*":
            block_comment = True
            i += 2
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            i += 1
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1

    raise AssertionError(f"unterminated function {name}")


def function_names(text: str) -> list[str]:
    return re.findall(r"\\bfunction\\s+([A-Za-z_$][\\w$]*)\\s*\\(", text)


def sim_params_block(text: str) -> str:
    start = text.index("const simParams = {")
    end = text.index("const DEBUG_MODE", start)
    return text[start:end]


def test_i064_preserves_every_inherited_function_byte_for_byte():
    before = parent_source()
    after = current_source()

    inherited = function_names(before)
    assert inherited, "parent function surface unexpectedly empty"

    missing = [name for name in inherited if f"function {name}(" not in after]
    assert not missing, f"I064 removed inherited functions: {missing}"

    changed = [
        name
        for name in inherited
        if extract_function(before, name) != extract_function(after, name)
    ]
    assert not changed, f"I064 changed inherited functions: {changed}"


def test_i064_preserves_authoritative_simulation_parameters_byte_for_byte():
    assert sim_params_block(current_source()) == sim_params_block(parent_source())


def test_i064_parent_is_the_exact_repair_authority():
    parent = parent_source()
    current = current_source()

    assert len(function_names(parent)) == 86
    assert len(function_names(current)) >= 86
    assert "HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1" in current
