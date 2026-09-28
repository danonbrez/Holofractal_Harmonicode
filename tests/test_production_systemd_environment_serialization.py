from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service"


def test_production_service_environment_lines_are_not_literal_newline_joined() -> None:
    text = UNIT.read_text(encoding="utf-8")
    assert "\\nEnvironment=" not in text
    assert "Environment=HHS_RUNTIME_STATUS_PROBE_TIMEOUT_SECONDS=180\n" in text
    assert "Environment=HHS_RUNTIME_STATUS_PROBE_CONCURRENCY=2\n" in text
