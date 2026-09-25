from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_api_artifact_root_honors_explicit_state_root(tmp_path: Path) -> None:
    destination = tmp_path / "runtime-api"
    env = dict(os.environ)
    env["HHS_RUNTIME_API_ARTIFACT_ROOT"] = str(destination)
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import hhs_runtime_api_server_v1 as m; print(m.ARTIFACT_ROOT)",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.strip().endswith(str(destination))
    assert destination.is_dir()


def test_production_service_binds_runtime_api_artifact_root_outside_checkout() -> None:
    unit = (ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service").read_text(
        encoding="utf-8"
    )
    assert "Environment=HHS_RUNTIME_API_ARTIFACT_ROOT=/var/lib/hhs/runtime-api" in unit
    assert "ReadWritePaths=/opt/hhs/app" not in unit
