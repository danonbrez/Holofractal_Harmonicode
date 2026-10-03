from __future__ import annotations

from pathlib import Path


def test_hash216_generated_main_dispatches_exact_main() -> None:
    workflow = Path(
        ".github/workflows/repository-hash216-dependency-index.yml"
    ).read_text(encoding="utf-8")

    assert "actions: write" in workflow
    assert "id: commit_projection" in workflow
    assert 'echo "committed=false" >> "$GITHUB_OUTPUT"' in workflow
    assert 'echo "committed=true" >> "$GITHUB_OUTPUT"' in workflow
    assert 'echo "committed_sha=$committed_sha" >> "$GITHUB_OUTPUT"' in workflow
    assert "steps.commit_projection.outputs.committed == 'true'" in workflow
    assert "gh workflow run digitalocean-production-main.yml --ref main" in workflow
    assert 'HHS_HASH216_EXACT_MAIN_DISPATCHED=$remote_head' in workflow


def test_exact_main_accepts_explicit_workflow_dispatch() -> None:
    workflow = Path(
        ".github/workflows/digitalocean-production-main.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
