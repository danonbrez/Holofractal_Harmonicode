from pathlib import Path

from hhs_runtime.pass174 import build_legacy_manifest


def test_evidence_tests_and_reports_do_not_redefine_legacy_specification_root(tmp_path: Path):
    (tmp_path / "HHS_PASS_001_GENESIS.md").write_text("pass 1 contract\n")
    (tmp_path / "HHS_PASS_173_INSTALL_VERIFY.md").write_text("pass 173 contract\n")
    baseline = build_legacy_manifest(tmp_path)

    evidence = tmp_path / "evidence" / "pass173"
    evidence.mkdir(parents=True)
    (evidence / "PASS_173_RECEIPT.json").write_text('{"status":"PASS"}\n')
    tests = tmp_path / "tests" / "pass173"
    tests.mkdir(parents=True)
    (tests / "PASS_173_TEST_REPORT.md").write_text("executed later\n")
    reports = tmp_path / "reports" / "pass173"
    reports.mkdir(parents=True)
    (reports / "PASS_173_REPORT.md").write_text("later report\n")

    observed = build_legacy_manifest(tmp_path)
    assert observed.aggregate_root_sha256 == baseline.aggregate_root_sha256
    assert observed.specification_count == baseline.specification_count == 2


def test_contract_directory_numbered_manifest_is_inherited(tmp_path: Path):
    (tmp_path / "HHS_PASS_173_INSTALL_VERIFY.md").write_text("pass 173 contract\n")
    contract_dir = tmp_path / "contracts" / "pass150"
    contract_dir.mkdir(parents=True)
    (contract_dir / "authority.json").write_text('{"pass":150,"authority":"Hash216"}\n')
    manifest = build_legacy_manifest(tmp_path)
    assert 150 in manifest.pass_numbers_present
    assert any(item.path == "contracts/pass150/authority.json" for item in manifest.specifications)
