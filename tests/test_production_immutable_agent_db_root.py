from __future__ import annotations

from pathlib import Path

from hhs_backend.runtime._immutable_agent_source_capsule_v1 import source

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service"


def test_immutable_agent_index_supports_explicit_database_path() -> None:
    decoded = source(
        "hhs_backend/runtime/immutable_agent_sql_index_v1.py"
    ).decode("utf-8")
    assert 'os.getenv("HHS_AGENT_INDEX_DB", DEFAULT_DB_PATH)' in decoded


def test_production_binds_immutable_agent_index_outside_checkout() -> None:
    unit = UNIT.read_text(encoding="utf-8")
    assert (
        "Environment=HHS_AGENT_INDEX_DB="
        "/var/lib/hhs/data/runtime/hhs_agent_immutable_index.sqlite3"
    ) in unit
    assert "Environment=HHS_RUNTIME_OUTPUT_DIR=/var/lib/hhs/data/runtime" in unit
    assert "ReadWritePaths=/var/lib/hhs" in unit
    assert "ReadWritePaths=/opt/hhs/app" not in unit
