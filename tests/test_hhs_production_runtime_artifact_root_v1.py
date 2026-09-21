from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_legacy_runtime_api_artifacts_follow_runtime_output_boundary(tmp_path: Path) -> None:
    runtime_output = tmp_path / "runtime"
    runtime_output.mkdir()
    readonly_cwd = tmp_path / "readonly"
    readonly_cwd.mkdir()
    readonly_cwd.chmod(0o555)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["HHS_RUNTIME_OUTPUT_DIR"] = str(runtime_output)
    env.pop("HHS_RUNTIME_API_ARTIFACT_ROOT", None)

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import hhs_runtime_api_server_v1 as m; "
                "print(m.ARTIFACT_ROOT.resolve())"
            ),
        ],
        cwd=readonly_cwd,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    expected = (runtime_output / "runtime_api").resolve()
    assert completed.stdout.strip().splitlines()[-1] == str(expected)
    assert expected.is_dir()


def test_explicit_runtime_api_artifact_root_overrides_runtime_output(tmp_path: Path) -> None:
    runtime_output = tmp_path / "runtime"
    runtime_output.mkdir()
    explicit = tmp_path / "explicit-runtime-api"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["HHS_RUNTIME_OUTPUT_DIR"] = str(runtime_output)
    env["HHS_RUNTIME_API_ARTIFACT_ROOT"] = str(explicit)

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import hhs_runtime_api_server_v1 as m; "
                "print(m.ARTIFACT_ROOT.resolve())"
            ),
        ],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().splitlines()[-1] == str(explicit.resolve())
    assert explicit.is_dir()
