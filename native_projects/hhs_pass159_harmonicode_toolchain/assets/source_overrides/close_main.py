#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = ROOT.parents[1]
EVIDENCE = ROOT / "evidence"
DIST = ROOT / "dist"
PASS158_REPORT = ROOT.parent / "hhs_pass158_llabi_nftc_api" / "dist" / "native-test-report.json"
TERMINAL = "HHS_PASS_159_VM81_HASH216_HARMONICODE_INTERPRETER_AND_C11_NATIVE_COMPILER_VERIFIED"
TOOLCHAIN_REL = ROOT.relative_to(REPOSITORY).as_posix()
COMPLETION_REL = f"{TOOLCHAIN_REL}/evidence/P159_COMPLETION_RECEIPT.json"
CLOSURE_REL = f"{TOOLCHAIN_REL}/evidence/P159_AUTHORITATIVE_MAIN_CLOSURE.json"
CLOSURE_TOOL_REL = f"{TOOLCHAIN_REL}/assets/source_overrides/close_main.py"


def read_json(path: Path):
    text = path.read_text(encoding="utf-8", errors="strict").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for line in reversed(text.splitlines()):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
        raise


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPOSITORY,
        check=check,
        text=True,
        capture_output=True,
    )


def git_show_text(revision: str, relative_path: str) -> str | None:
    result = git("show", f"{revision}:{relative_path}", check=False)
    if result.returncode != 0:
        return None
    return result.stdout


def parse_json_text(text: str | None):
    if text is None:
        return None
    return json.loads(text)


def is_ancestor(ancestor: str, descendant: str) -> bool:
    if len(ancestor) != 40 or len(descendant) != 40:
        return False
    return git("merge-base", "--is-ancestor", ancestor, descendant, check=False).returncode == 0


def pass159_functional_changes(anchor: str, current: str) -> list[str]:
    result = git("diff", "--name-only", anchor, current, "--", TOOLCHAIN_REL)
    ignored_prefixes = (
        f"{TOOLCHAIN_REL}/evidence/",
        f"{TOOLCHAIN_REL}/dist/",
        f"{TOOLCHAIN_REL}/tests/",
    )
    changed = []
    for raw in result.stdout.splitlines():
        path = raw.strip()
        if not path:
            continue
        if path == CLOSURE_TOOL_REL:
            continue
        if path.startswith(ignored_prefixes):
            continue
        changed.append(path)
    return changed


def restore_committed_terminal_receipts(completion_text: str, closure_text: str) -> None:
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "P159_COMPLETION_RECEIPT.json").write_text(completion_text, encoding="utf-8")
    (EVIDENCE / "P159_AUTHORITATIVE_MAIN_CLOSURE.json").write_text(closure_text, encoding="utf-8")


ref = os.environ.get("GITHUB_REF", "")
sha = os.environ.get("GITHUB_SHA", "")
if ref != "refs/heads/main" or len(sha) != 40:
    raise SystemExit("authoritative main context required")

# The downloaded evidence artifact intentionally places the pre-main receipt in
# the working tree. Read it before consulting committed terminal receipts via
# `git show HEAD:<path>`; the two are distinct authorities.
pre = read_json(EVIDENCE / "P159_COMPLETION_RECEIPT.json")
full = read_json(DIST / "P159_FULL_VALIDATION_REPORT.json")
cross = read_json(DIST / "P159_CROSS_ARCHITECTURE_INPUT.json")
inherited = read_json(PASS158_REPORT)

checks = {
    "pre_main_omega": pre.get("omega_without_main") is True,
    "full_failures_zero": full.get("failures") == 0,
    "positive_matrix": full.get("positive_total", 0) >= 159,
    "negative_matrix": full.get("negative_total") == 159,
    "hash216_coverage": full.get("hash216_position_coverage") == 216,
    "vm81_coverage": full.get("vm81_cell_coverage") == 81,
    "equivalence_programs": full.get("equivalence_programs", 0) >= 72,
    "no_fallback": full.get("fallback_used") is False,
    "cross_architecture": cross.get("matched") is True,
    "inherited_positive": inherited.get("positive_total", 0) >= 272,
    "inherited_negative": inherited.get("negative_total", 0) >= 81,
    "authoritative_main": ref == "refs/heads/main",
}
if not all(checks.values()):
    raise SystemExit(json.dumps({"classification": "HHS_PASS_159_MAIN_CLOSURE_REJECTED", "checks": checks}, sort_keys=True))

committed_completion_text = git_show_text("HEAD", COMPLETION_REL)
committed_closure_text = git_show_text("HEAD", CLOSURE_REL)
committed_completion = parse_json_text(committed_completion_text)
committed_closure = parse_json_text(committed_closure_text)

# A completed historical pass is not re-closed merely because later cumulative
# main commits exist. Re-run all validation, then preserve the exact committed
# closure bytes when the original closure remains an ancestor and no Pass 159
# functional input changed. Any deterministic evidence mismatch is a hard
# rejection rather than permission to silently move the historical anchor.
if (
    isinstance(committed_completion, dict)
    and isinstance(committed_closure, dict)
    and committed_completion.get("classification") == TERMINAL
    and committed_completion.get("terminal_claimed") is True
    and committed_completion.get("omega_159") is True
):
    anchor = str(committed_completion.get("authoritative_main_commit", ""))
    closure_anchor = str(committed_closure.get("authoritative_main_commit", ""))
    functional_changes = pass159_functional_changes(anchor, sha) if is_ancestor(anchor, sha) else ["NON_ANCESTOR_CLOSURE_ANCHOR"]
    if anchor == closure_anchor and not functional_changes:
        deterministic_checks = {
            "pre_main_evidence_root": pre.get("evidence_root") == committed_completion.get("pre_main_evidence_root"),
            "main_closure_root": committed_completion.get("main_closure_root") == committed_closure.get("main_closure_root"),
            "full_validation": committed_closure.get("full_validation") == full,
            "cross_architecture": committed_closure.get("cross_architecture") == cross,
            "inherited_pass158": committed_closure.get("inherited_pass158") == inherited,
            "checks": committed_closure.get("checks") == checks,
            "classification": committed_closure.get("classification") == TERMINAL,
            "omega_159": committed_closure.get("omega_159") is True,
        }
        if not all(deterministic_checks.values()):
            raise SystemExit(
                json.dumps(
                    {
                        "classification": "HHS_PASS_159_IDEMPOTENT_REVALIDATION_MISMATCH",
                        "authoritative_main_commit": anchor,
                        "current_main_commit": sha,
                        "deterministic_checks": deterministic_checks,
                    },
                    sort_keys=True,
                )
            )
        assert committed_completion_text is not None and committed_closure_text is not None
        restore_committed_terminal_receipts(committed_completion_text, committed_closure_text)
        print(
            json.dumps(
                {
                    "schema": "P159_IDEMPOTENT_MAIN_CLOSURE_REVALIDATION_V1",
                    "classification": TERMINAL,
                    "omega_159": True,
                    "authoritative_main_commit": anchor,
                    "current_main_commit": sha,
                    "functional_changes": [],
                    "terminal_receipt_reused_byte_exact": True,
                    "deterministic_revalidation": True,
                },
                sort_keys=True,
            )
        )
        raise SystemExit(0)

# A genuine Pass 159 functional change requires a new closure anchor. The same
# validation evidence is bound to the current authoritative main commit exactly
# as in the original closure protocol.
closure_material = {
    "authoritative_main_commit": sha,
    "pre_main_evidence_root": pre.get("evidence_root"),
    "full_validation": full,
    "cross_architecture": cross,
    "inherited_pass158": inherited,
    "checks": checks,
}
closure_root = hashlib.sha256(json.dumps(closure_material, sort_keys=True).encode("utf-8")).hexdigest()
terminal_receipt = {
    "schema": "P159_COMPLETION_RECEIPT_V1",
    "contract": "HHS-P159-VM81-H216-HCI-C11C",
    "classification": TERMINAL,
    "terminal_claimed": True,
    "main_closure_required": False,
    "omega_159": True,
    "authoritative_branch": "main",
    "authoritative_main_commit": sha,
    "pre_main_evidence_root": pre.get("evidence_root"),
    "main_closure_root": closure_root,
    "checks": checks,
}
EVIDENCE.mkdir(exist_ok=True)
(EVIDENCE / "P159_COMPLETION_RECEIPT.json").write_text(
    json.dumps(terminal_receipt, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
(EVIDENCE / "P159_AUTHORITATIVE_MAIN_CLOSURE.json").write_text(
    json.dumps({"schema": "P159_AUTHORITATIVE_MAIN_CLOSURE_V1", **closure_material, "classification": TERMINAL, "omega_159": True, "main_closure_root": closure_root}, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(terminal_receipt, sort_keys=True))
