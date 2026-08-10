#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

SOURCE_TOOLCHAIN = Path(__file__).resolve().parents[1]
SOURCE_CLOSE_MAIN = SOURCE_TOOLCHAIN / "assets" / "source_overrides" / "close_main.py"
TERMINAL = "HHS_PASS_159_VM81_HASH216_HARMONICODE_INTERPRETER_AND_C11_NATIVE_COMPILER_VERIFIED"


def run(*args: str, cwd: Path, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, check=check, text=True, capture_output=True)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_commit(repo: Path, message: str, *paths: str) -> str:
    run("git", "add", "-f", *paths, cwd=repo)
    run("git", "commit", "-qm", message, cwd=repo)
    return run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hhs-pass159-close-main-") as temp:
        repo = Path(temp)
        toolchain = repo / "native_projects" / "hhs_pass159_harmonicode_toolchain"
        close_main = toolchain / "assets" / "source_overrides" / "close_main.py"
        evidence = toolchain / "evidence"
        dist = toolchain / "dist"
        pass158 = repo / "native_projects" / "hhs_pass158_llabi_nftc_api" / "dist" / "native-test-report.json"
        source = toolchain / "src" / "runtime.c"

        close_main.parent.mkdir(parents=True)
        source.parent.mkdir(parents=True)
        shutil.copy2(SOURCE_CLOSE_MAIN, close_main)
        source.write_text("int p159_runtime(void) { return 159; }\n", encoding="utf-8")

        run("git", "init", "-q", cwd=repo)
        run("git", "config", "user.name", "HHS Pass 159 Test", cwd=repo)
        run("git", "config", "user.email", "hhs-pass159-test@example.invalid", cwd=repo)
        anchor = git_commit(
            repo,
            "baseline Pass 159 implementation",
            "native_projects/hhs_pass159_harmonicode_toolchain/assets/source_overrides/close_main.py",
            "native_projects/hhs_pass159_harmonicode_toolchain/src/runtime.c",
        )

        full = {
            "failures": 0,
            "positive_total": 159,
            "negative_total": 159,
            "hash216_position_coverage": 216,
            "vm81_cell_coverage": 81,
            "equivalence_programs": 72,
            "fallback_used": False,
        }
        cross = {"matched": True, "roots": ["same", "same"]}
        inherited = {"positive_total": 272, "negative_total": 81}
        pre_root = hashlib.sha256(b"pre-main-pass159").hexdigest()
        checks = {
            "pre_main_omega": True,
            "full_failures_zero": True,
            "positive_matrix": True,
            "negative_matrix": True,
            "hash216_coverage": True,
            "vm81_coverage": True,
            "equivalence_programs": True,
            "no_fallback": True,
            "cross_architecture": True,
            "inherited_positive": True,
            "inherited_negative": True,
            "authoritative_main": True,
        }
        closure_root = hashlib.sha256(b"stable-pass159-closure").hexdigest()
        terminal = {
            "schema": "P159_COMPLETION_RECEIPT_V1",
            "contract": "HHS-P159-VM81-H216-HCI-C11C",
            "classification": TERMINAL,
            "terminal_claimed": True,
            "main_closure_required": False,
            "omega_159": True,
            "authoritative_branch": "main",
            "authoritative_main_commit": anchor,
            "pre_main_evidence_root": pre_root,
            "main_closure_root": closure_root,
            "checks": checks,
        }
        closure = {
            "schema": "P159_AUTHORITATIVE_MAIN_CLOSURE_V1",
            "authoritative_main_commit": anchor,
            "pre_main_evidence_root": pre_root,
            "full_validation": full,
            "cross_architecture": cross,
            "inherited_pass158": inherited,
            "checks": checks,
            "classification": TERMINAL,
            "omega_159": True,
            "main_closure_root": closure_root,
        }
        write_json(evidence / "P159_COMPLETION_RECEIPT.json", terminal)
        write_json(evidence / "P159_AUTHORITATIVE_MAIN_CLOSURE.json", closure)
        write_json(dist / "P159_FULL_VALIDATION_REPORT.json", full)
        write_json(dist / "P159_CROSS_ARCHITECTURE_INPUT.json", cross)
        write_json(pass158, inherited)
        git_commit(
            repo,
            "record original Pass 159 closure",
            "native_projects/hhs_pass159_harmonicode_toolchain/evidence/P159_COMPLETION_RECEIPT.json",
            "native_projects/hhs_pass159_harmonicode_toolchain/evidence/P159_AUTHORITATIVE_MAIN_CLOSURE.json",
            "native_projects/hhs_pass159_harmonicode_toolchain/dist/P159_FULL_VALIDATION_REPORT.json",
            "native_projects/hhs_pass159_harmonicode_toolchain/dist/P159_CROSS_ARCHITECTURE_INPUT.json",
            "native_projects/hhs_pass158_llabi_nftc_api/dist/native-test-report.json",
        )

        (repo / "later-system-state.txt").write_text("later cumulative pass state\n", encoding="utf-8")
        later_sha = git_commit(repo, "unrelated later main state", "later-system-state.txt")

        # Simulate actions/download-artifact replacing the working completion
        # receipt with the newly executed pre-main evidence before close_main.py.
        write_json(
            evidence / "P159_COMPLETION_RECEIPT.json",
            {"schema": "P159_PRE_MAIN_RECEIPT_V1", "omega_without_main": True, "evidence_root": pre_root},
        )
        env = dict(os.environ, GITHUB_REF="refs/heads/main", GITHUB_SHA=later_sha)
        first = run("python3", str(close_main), cwd=repo, env=env)
        first_payload = json.loads(first.stdout.strip().splitlines()[-1])
        assert first_payload["terminal_receipt_reused_byte_exact"] is True
        assert first_payload["authoritative_main_commit"] == anchor
        assert first_payload["current_main_commit"] == later_sha
        assert json.loads((evidence / "P159_COMPLETION_RECEIPT.json").read_text()) == terminal
        assert json.loads((evidence / "P159_AUTHORITATIVE_MAIN_CLOSURE.json").read_text()) == closure
        assert run(
            "git",
            "diff",
            "--quiet",
            "HEAD",
            "--",
            "native_projects/hhs_pass159_harmonicode_toolchain/evidence",
            cwd=repo,
            check=False,
        ).returncode == 0, "unrelated descendant must not rewrite terminal receipts"

        source.write_text("int p159_runtime(void) { return 160; }\n", encoding="utf-8")
        changed_sha = git_commit(repo, "genuine Pass 159 functional repair", "native_projects/hhs_pass159_harmonicode_toolchain/src/runtime.c")
        write_json(
            evidence / "P159_COMPLETION_RECEIPT.json",
            {"schema": "P159_PRE_MAIN_RECEIPT_V1", "omega_without_main": True, "evidence_root": pre_root},
        )
        env["GITHUB_SHA"] = changed_sha
        second = run("python3", str(close_main), cwd=repo, env=env)
        second_payload = json.loads(second.stdout.strip().splitlines()[-1])
        assert second_payload["authoritative_main_commit"] == changed_sha
        assert second_payload["terminal_claimed"] is True
        assert json.loads((evidence / "P159_COMPLETION_RECEIPT.json").read_text())["authoritative_main_commit"] == changed_sha
        assert run(
            "git",
            "diff",
            "--quiet",
            "HEAD",
            "--",
            "native_projects/hhs_pass159_harmonicode_toolchain/evidence",
            cwd=repo,
            check=False,
        ).returncode != 0, "genuine functional change must produce a new closure receipt"

    print("HHS_PASS_159_IDEMPOTENT_MAIN_CLOSURE_TEST=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
