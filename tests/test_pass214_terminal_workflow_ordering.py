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


def test_pass214_benchmark_precedes_pass213_terminal_authority_gate() -> None:
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
    assert "Freeze pre-authority Pass 214 benchmark boundary" in benchmark_job
    assert "Retain pre-authority Pass 214 benchmark evidence" in benchmark_job
    assert "Require Pass 213 terminal authority inputs" not in benchmark_job

    assert "needs: pass214-benchmark" in terminal_job
    assert "environment: production" in terminal_job
    assert "Restore frozen Pass 214 benchmark evidence" in terminal_job
    assert "Verify exact Pass 214 source and evidence binding" in terminal_job
    assert "Require Pass 213 terminal authority inputs" in terminal_job
    assert "Create live Pass 213 admission and Pass 214 terminal freeze" in terminal_job
    assert terminal_job.index("Require Pass 213 terminal authority inputs") < terminal_job.index(
        "Create live Pass 213 admission and Pass 214 terminal freeze"
    )


def test_pass213_gate_cannot_erase_completed_pass214_benchmark_evidence() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    benchmark_job = _job_block(
        text,
        "  pass214-benchmark:",
        "  pass213-terminal-authority:",
    )
    terminal_job = _job_block(text, "  pass213-terminal-authority:")

    artifact_expression = "pass214-preterminal-benchmark-${{ github.run_id }}"
    assert artifact_expression in benchmark_job
    assert artifact_expression in terminal_job
    assert "pass214_benchmark_completed_before_gate" in terminal_job
    assert "if: always()" in terminal_job
    assert "terminal_roots_minted': False" in terminal_job
    assert "pass215_authorized': False" in terminal_job
