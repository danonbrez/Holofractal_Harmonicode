from pathlib import Path

WORKFLOW = Path(".github/workflows/repository-hash216-dependency-index.yml")


def _workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_hash216_index_has_no_direct_main_push_path() -> None:
    text = _workflow()
    assert "git push origin HEAD:main" not in text
    assert "Commit generated projection to main" not in text
    assert "Dispatch authoritative main refresh" not in text


def test_hash216_index_publishes_via_automation_pr() -> None:
    text = _workflow()
    assert "pull-requests: write" in text
    assert "AUTOMATION_BRANCH: automation/hash216-repository-index" in text
    assert "HHS_AUTOMATION_PR_TOKEN" in text
    assert "git push --force-with-lease origin" in text
    assert "gh pr list" in text
    assert "gh pr create" in text
    assert "gh pr edit" in text
    assert "--base main" in text


def test_hash216_index_pr_publication_is_main_event_scoped() -> None:
    text = _workflow()
    assert "github.ref == 'refs/heads/main'" in text
    assert "github.event_name == 'push'" in text
    assert "github.event_name == 'workflow_dispatch'" in text
    assert "This PR contains generated repository-index projections only." in text
    assert "no direct-main push path" in text
