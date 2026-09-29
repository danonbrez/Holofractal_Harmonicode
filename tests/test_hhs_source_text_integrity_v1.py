from __future__ import annotations

from pathlib import Path

from hhs_runtime.hhs_source_text_integrity_v1 import (
    find_literal_escaped_newline_issues,
    scan_repository_source_text,
)


def test_rejects_literal_escaped_newline_between_python_statements():
    source = "value = 1\\nother = 2\n"
    issues = find_literal_escaped_newline_issues("example.py", source)
    assert len(issues) == 1
    assert issues[0].line == 1
    assert issues[0].kind == "LITERAL_ESCAPED_NEWLINE_OUTSIDE_STRING_OR_COMMENT"


def test_rejects_literal_escaped_newline_between_typescript_imports():
    source = 'import x from "./x"\\nimport y from "./y"\n'
    issues = find_literal_escaped_newline_issues("bootstrap.ts", source)
    assert len(issues) == 1


def test_rejects_literal_escaped_newline_between_c_includes():
    source = '#include "a.h"\\n#include "b.h"\n'
    issues = find_literal_escaped_newline_issues("aggregate.c", source)
    assert len(issues) == 1


def test_rejects_literal_escaped_newline_between_shell_assignments():
    source = "RECOVERY_VERIFIER=/tmp/verify.py\\nSTATIC_FIRST_CONFIGURATOR=/tmp/configure.py\n"
    issues = find_literal_escaped_newline_issues("install.sh", source)
    assert len(issues) == 1
    assert issues[0].kind == "LITERAL_ESCAPED_NEWLINE_OUTSIDE_STRING_OR_COMMENT"


def test_allows_shell_newline_escape_inside_quote_and_comment():
    source = "printf '%s\\n' value\n# documentation contains \\n token\n"
    assert find_literal_escaped_newline_issues("install.sh", source) == []


def test_allows_newline_escape_inside_string_char_regex_and_comment():
    cases = [
        ("example.py", 'value = "line one\\nline two"\n# literal text \\\\n is documentation\n'),
        ("example.c", "char newline = '\\n';\n/* \\\\n */\n"),
        ("example.ts", r'const pattern = /\n/g;' + "\n" + r'const value = "a\nb";' + "\n"),
    ]
    for path, source in cases:
        assert find_literal_escaped_newline_issues(path, source) == []


def test_allows_nested_javascript_template_literal_newline_escapes():
    source = "  output.textContent += `\\n[${stamp}] ${data === undefined ? '' : `\\n${JSON.stringify(data)}`}`;\n"
    assert find_literal_escaped_newline_issues("visual-ide-state.mjs", source) == []


def test_forward_slash_n_data_is_not_treated_as_newline():
    source = 'hash72 = "abc/nxyz"\nroute = "/novel/status"\nratio = "k/n"\n'
    assert find_literal_escaped_newline_issues("example.py", source) == []


def test_repository_scan_reports_exact_file(tmp_path: Path):
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    bad = source_dir / "broken.py"
    bad.write_text("left = 1\\nright = 2\n", encoding="utf-8")

    report = scan_repository_source_text(tmp_path)

    assert report["status"] == "REJECTED"
    assert report["issue_count"] == 1
    assert report["issues"][0]["path"] == "src/broken.py"


def test_repository_scan_ignores_generated_distribution_tree(tmp_path: Path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "generated.js").write_text("left = 1\\nright = 2\n", encoding="utf-8")

    report = scan_repository_source_text(tmp_path)

    assert report["status"] == "ACCEPTED"
    assert report["issue_count"] == 0


def test_commit_gate_runs_source_text_integrity_before_heavier_checks():
    source = Path("hhs_runtime/hhs_commit_acceptance_gate_v1.py").read_text(encoding="utf-8")
    scan_call = "scan_repository_source_text(root)"
    dependency_call = "run_dependency_audit()"
    assert scan_call in source
    assert source.index(scan_call) < source.index(dependency_call)


def test_dedicated_workflow_catches_api_authored_commits_on_push_and_pr():
    workflow = Path(".github/workflows/hhs-source-text-integrity.yml").read_text(encoding="utf-8")
    assert "push:" in workflow
    assert "pull_request:" in workflow
    assert "python -m hhs_runtime.hhs_source_text_integrity_v1" in workflow
    assert "python -m pytest -q tests/test_hhs_source_text_integrity_v1.py" in workflow
