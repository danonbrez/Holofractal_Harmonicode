from __future__ import annotations

from pathlib import Path
import json

from hhs_installer.journal import atomic_write_json
from hhs_installer.management import doctor, installation_status, rollback, uninstall


def _installation(home: Path) -> None:
    (home / "versions" / "v1").mkdir(parents=True)
    (home / "versions" / "v2").mkdir(parents=True)
    (home / "state" / "workspaces").mkdir(parents=True)
    (home / "state" / "workspaces" / "user.txt").write_text("preserve", encoding="utf-8")
    atomic_write_json(
        home / "current.json",
        {
            "schema": "HHS_PASS_172_ACTIVE_VERSION_V1",
            "active_version": "v2",
            "previous_version": "v1",
        },
    )


def test_status_and_doctor_are_read_only(tmp_path: Path) -> None:
    _installation(tmp_path)
    before = sorted(str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*"))
    status = installation_status(tmp_path)
    report = doctor(tmp_path)
    after = sorted(str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*"))
    assert status["installed"] is True
    assert report["mode"] == "read_only"
    assert before == after


def test_rollback_requires_authorization(tmp_path: Path) -> None:
    _installation(tmp_path)
    proposal = rollback(tmp_path, authorized=False)
    assert proposal["status"] == "BLOCKED"
    assert json.loads((tmp_path / "current.json").read_text(encoding="utf-8"))["active_version"] == "v2"
    result = rollback(tmp_path, authorized=True)
    assert result["status"] == "SUCCESS"
    assert json.loads((tmp_path / "current.json").read_text(encoding="utf-8"))["active_version"] == "v1"


def test_uninstall_preserves_user_data_by_default(tmp_path: Path) -> None:
    _installation(tmp_path)
    proposal = uninstall(tmp_path, authorized=False)
    assert proposal["status"] == "BLOCKED"
    result = uninstall(tmp_path, authorized=True)
    assert result["status"] == "SUCCESS"
    assert (tmp_path / "state" / "workspaces" / "user.txt").read_text(encoding="utf-8") == "preserve"
    assert not (tmp_path / "versions").exists()
