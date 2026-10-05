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


def test_production_delivery_chain_serializes_exact_main_and_generated_index() -> None:
    index_workflow = Path(
        ".github/workflows/repository-hash216-dependency-index.yml"
    ).read_text(encoding="utf-8")
    exact_main = Path(
        ".github/workflows/digitalocean-production-main.yml"
    ).read_text(encoding="utf-8")

    shared_group = "'hhs-production-main-delivery'"
    assert shared_group in index_workflow
    assert shared_group in exact_main
    assert "cancel-in-progress: false" in index_workflow
    assert "cancel-in-progress: false" in exact_main

    # Hash216 no longer advances main independently on every main push. It is
    # queued only after an Exact-Main transaction has promoted and passed public
    # HTTPS verification.
    index_triggers = index_workflow.split("permissions:", 1)[0]
    assert "\n  push:" not in index_triggers
    assert "Dispatch authoritative main refresh" not in index_workflow
    assert "Queue Hash216 repository index after verified promotion" in exact_main
    assert "gh workflow run repository-hash216-dependency-index.yml --ref main" in exact_main
    assert "HHS_EXACT_MAIN_HASH216_INDEX_QUEUED=$TARGET_SHA" in exact_main
    assert exact_main.index("HHS_DIGITALOCEAN_PUBLIC_RUNTIME_OS_VERIFIED") < exact_main.index(
        "Queue Hash216 repository index after verified promotion"
    )

    # Generated projection advancement remains chained back into Exact-Main.
    assert "gh workflow run digitalocean-production-main.yml --ref main" in index_workflow


def test_exact_main_bundle_build_verifies_frontend_capability_projection_sources() -> None:
    workflow = Path(
        ".github/workflows/digitalocean-production-main.yml"
    ).read_text(encoding="utf-8")
    for command in (
        "npm run test:workspace:source",
        "npm run test:e2e:source",
        "npm run test:frontend-telemetry:source",
    ):
        assert command in workflow
