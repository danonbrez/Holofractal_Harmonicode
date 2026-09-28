from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_lock_certifier_honors_explicit_state_root(tmp_path: Path) -> None:
    destination = tmp_path / "runtime-certification"
    env = dict(os.environ)
    env["HHS_RUNTIME_CERTIFICATION_DIR"] = str(destination)
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import hhs_runtime.runtime_lock_certifier_v1 as m; print(m.CERT_DIR)",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.strip() == str(destination.resolve())
    assert destination.is_dir()


def test_production_service_keeps_certification_state_out_of_checkout() -> None:
    unit = (ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service").read_text(
        encoding="utf-8"
    )
    assert (
        "Environment=HHS_RUNTIME_CERTIFICATION_DIR=/var/lib/hhs/runtime-certification"
        in unit
    )
    assert "ReadWritePaths=/var/lib/hhs" in unit
    assert "ReadWritePaths=/opt/hhs/app" not in unit
