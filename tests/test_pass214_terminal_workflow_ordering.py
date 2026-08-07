from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "pass214-production-terminal-finalize.yml"


def _job_block(text: str, start: str, end: str | None = None) -> str:
    begin = text.index(start)
    if end is None:
        return text[begin:]
    finish = text.index(end, begin + len(start))
    return text[begin:finish]


def test_pass214_closes_before_pass213_runtime_authority_gate() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert text.index("  pass214-benchmark:") < text.index("  pass213-terminal-authority:")

    benchmark_job = _job_block(
        text,
        "  pass214-benchmark:",
        "  pass213-terminal-authority:",
    )
    terminal_job = _job_block(text, "  pass213-terminal-authority:")

    assert "environment: production" not in benchmark_job
    assert "Validate cumulative Pass 214" in benchmark_job
    assert "Generate exact-head census and compatibility evidence" in benchmark_job
    assert "Execute frozen final Pass 214 compound benchmark" in benchmark_job
    assert "Mint Pass 214 terminal benchmark authority" in benchmark_job
    assert "Enforce eight-root Pass 214 terminal closure" in benchmark_job
    assert "Freeze exact-head Pass 214 closure boundary" in benchmark_job
    assert "Retain Pass 214 terminal benchmark authority" in benchmark_job
    assert "PASS214_TRUSTED_ANCHOR_JSON_B64" not in benchmark_job

    assert "needs: pass214-benchmark" in terminal_job
    assert "environment: production" in terminal_job
    assert "Restore frozen Pass 214 terminal evidence" in terminal_job
    assert "Verify exact Pass 214 terminal source and evidence binding" in terminal_job
    assert "Inspect downstream Pass 213 runtime authority inputs" in terminal_job
    assert "Attempt downstream live Pass 213 admission without affecting Pass 214 closure" in terminal_job


def test_pass213_runtime_gate_cannot_redefine_or_erase_pass214_closure() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    benchmark_job = _job_block(
        text,
        "  pass214-benchmark:",
        "  pass213-terminal-authority:",
    )
    terminal_job = _job_block(text, "  pass213-terminal-authority:")

    artifact_expression = "pass214-terminal-benchmark-${{ github.run_id }}"
    assert artifact_expression in benchmark_job
    assert artifact_expression in terminal_job

    for required in (
        "terminal_roots_minted'] is True",
        "benchmark_authority_promoted'] is True",
        "pass215_authorized'] is True",
        "pass213_gates_preserved'] is True",
        "runtime_mutation_authority_promoted'] is False",
        "canonical_mutation_authorized'] is False",
        "migration_active'] is False",
    ):
        assert required in benchmark_job

    assert "pass214_terminal_closure_complete': True" in terminal_job
    assert "pass214_benchmark_authority_promoted': True" in terminal_job
    assert "runtime_mutation_authority_promoted': False" in terminal_job
    assert "canonical_mutation_authorized': False" in terminal_job
    assert "if: always()" in terminal_job
    assert "exit 0" in terminal_job
