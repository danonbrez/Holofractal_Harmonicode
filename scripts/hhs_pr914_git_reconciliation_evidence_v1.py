#!/usr/bin/env python3
"""Derive PR914 Git reconciliation evidence from an exact preserved census.

This pass is read-only with respect to repository refs and working trees. It uses
local Git objects to enumerate changed paths and commits and to evaluate
hypothetical merge-tree results. It never assigns an integration disposition,
proves semantic equivalence, composes a candidate, merges, pushes, or deploys.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any


class ReconciliationError(RuntimeError):
    pass


def run_git(repository: Path, *args: str, allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )
    if result.returncode not in allowed:
        raise ReconciliationError(
            f"git {' '.join(args)} failed with {result.returncode}: {result.stderr.strip()}"
        )
    return result


def git_stdout(repository: Path, *args: str) -> str:
    return run_git(repository, *args).stdout.strip()


def parse_name_status_z(value: str) -> list[dict[str, Any]]:
    fields = value.split("\0")
    if fields[-1] != "":
        raise ReconciliationError("Unterminated name-status record")
    fields.pop()
    records: list[dict[str, Any]] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        if not status:
            raise ReconciliationError("Empty name-status code")
        if status[0] in ("R", "C"):
            if index + 1 >= len(fields):
                raise ReconciliationError("Incomplete rename/copy record")
            previous_path, path = fields[index], fields[index + 1]
            index += 2
        else:
            if index >= len(fields):
                raise ReconciliationError("Incomplete path record")
            previous_path, path = None, fields[index]
            index += 1
        records.append({"status": status, "path": path, "previous_path": previous_path})
    return records


def changed_files(repository: Path, base_sha: str, head_sha: str) -> dict[str, Any]:
    output = run_git(
        repository,
        "diff",
        "--name-status",
        "-z",
        "-M",
        f"{base_sha}...{head_sha}",
    ).stdout
    records = parse_name_status_z(output) if output else []
    return {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "comparison": "MERGE_BASE_TO_HEAD",
        "count": len(records),
        "records": records,
        "paths": [record["path"] for record in records],
        "complete": True,
    }


def commit_ids(repository: Path, base_sha: str, head_sha: str) -> dict[str, Any]:
    output = git_stdout(repository, "rev-list", "--reverse", f"{base_sha}..{head_sha}")
    ids = output.splitlines() if output else []
    return {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "count": len(ids),
        "ids": ids,
        "complete": True,
    }


def merge_tree_evidence(repository: Path, base_sha: str, head_sha: str) -> dict[str, Any]:
    result = run_git(
        repository,
        "merge-tree",
        "--write-tree",
        "--name-only",
        base_sha,
        head_sha,
        allowed=(0, 1),
    )
    lines = result.stdout.splitlines()
    tree_oid = lines[0] if lines else None
    separator = lines.index("") if "" in lines else len(lines)
    conflict_paths = lines[1:separator] if result.returncode == 1 else []
    if result.returncode == 0:
        status = "CLEAN_HYPOTHETICAL_MERGE_TREE"
    elif result.returncode == 1:
        status = "CONFLICTED_HYPOTHETICAL_MERGE_TREE"
    else:  # pragma: no cover - guarded by run_git allowed codes
        raise ReconciliationError("Unexpected merge-tree status")
    return {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "status": status,
        "hypothetical_tree_oid": tree_oid,
        "conflict_paths": conflict_paths,
        "conflict_paths_complete": True,
        "integration_candidate": False,
        "working_tree_or_ref_modified": False,
    }


def dependency_cycles(records: list[dict[str, Any]]) -> list[list[int]]:
    graph = {int(record["pr_number"]): list(record["contract_dependencies"]) for record in records}
    colors: dict[int, int] = {}
    stack: list[int] = []
    cycles: set[tuple[int, ...]] = set()

    def visit(number: int) -> None:
        colors[number] = 1
        stack.append(number)
        for parent in graph.get(number, []):
            if parent not in graph:
                continue
            if colors.get(parent, 0) == 0:
                visit(parent)
            elif colors.get(parent) == 1:
                start = stack.index(parent)
                cycle = stack[start:] + [parent]
                core = cycle[:-1]
                rotations = [tuple(core[index:] + core[:index] + [core[index]]) for index in range(len(core))]
                cycles.add(min(rotations))
        stack.pop()
        colors[number] = 2

    for number in sorted(graph):
        if colors.get(number, 0) == 0:
            visit(number)
    return [list(cycle) for cycle in sorted(cycles)]


def validate_document(document: dict[str, Any]) -> None:
    records = document["pull_requests"]
    if document["observed_open_pr_count"] != len(records):
        raise ReconciliationError("PR count does not match records")
    if document["source_census_observed_pr_count"] != len(records):
        raise ReconciliationError("Source census PR set was not preserved")
    if document["g1_complete"] is not False:
        raise ReconciliationError("Git evidence cannot complete semantic G1 reconciliation")
    if document["candidate_composed"] is not False:
        raise ReconciliationError("Hypothetical merge trees are not integration candidates")
    if document["automatic_mass_merge_authorized"] is not False:
        raise ReconciliationError("Mass merge must remain unauthorized")
    if document["requires_refresh_before_any_merge"] is not True:
        raise ReconciliationError("Pre-merge refresh obligation must remain enabled")
    for record in records:
        if record["disposition"] != "UNASSESSED":
            raise ReconciliationError("Collector cannot assign terminal dispositions")
        if record["frozen_layer_impact"] != "UNASSESSED":
            raise ReconciliationError("Frozen-layer impact requires separate authority review")
        if record["canonical_source_impact"] != "UNASSESSED":
            raise ReconciliationError("Canonical impact requires separate authority review")
        if record["review_authority"] is not None:
            raise ReconciliationError("Git evidence cannot assign review authority")


def collect(args: argparse.Namespace) -> dict[str, Any]:
    census_bytes = args.census.read_bytes()
    census = json.loads(census_bytes)
    source_records = census["pull_requests"]
    records: list[dict[str, Any]] = []
    for source in sorted(source_records, key=lambda row: row["pr_number"], reverse=True):
        head_sha = source["head_sha"]
        pr_base_sha = source["pr_base_ancestry"]["base_sha"]
        current_base = source["current_base_ancestry"]
        current_base_sha = current_base["base_sha"] if current_base else None
        git_stdout(args.repository, "cat-file", "-e", f"{head_sha}^{{commit}}")
        git_stdout(args.repository, "cat-file", "-e", f"{pr_base_sha}^{{commit}}")
        if current_base_sha:
            git_stdout(args.repository, "cat-file", "-e", f"{current_base_sha}^{{commit}}")
        pr_base_files = changed_files(args.repository, pr_base_sha, head_sha)
        current_base_files = (
            changed_files(args.repository, current_base_sha, head_sha)
            if current_base_sha else None
        )
        record = {
            "pr_number": int(source["pr_number"]),
            "pr_url": source["pr_url"],
            "head_ref": source["head_ref"],
            "head_sha": head_sha,
            "base_ref": source["base_ref"],
            "source_census_base_sha": source["base_sha"],
            "pr_base_changed_files": pr_base_files,
            "current_base_changed_files": current_base_files,
            "pr_base_commits": commit_ids(args.repository, pr_base_sha, head_sha),
            "current_base_commits": (
                commit_ids(args.repository, current_base_sha, head_sha)
                if current_base_sha else None
            ),
            "current_base_merge": (
                merge_tree_evidence(args.repository, current_base_sha, head_sha)
                if current_base_sha else None
            ),
            "current_main_merge": merge_tree_evidence(
                args.repository, census["main_sha"], head_sha
            ),
            "contract_dependencies": list(source["contract_dependencies"]),
            "overlapping_current_base_paths": [],
            "reviews": {"complete": False, "records": []},
            "check_runs": {"complete": False, "records": []},
            "combined_status": {"complete": False, "records": []},
            "frozen_layer_impact": "UNASSESSED",
            "canonical_source_impact": "UNASSESSED",
            "disposition": "UNASSESSED",
            "resolution_reason": None,
            "integration_commit": None,
            "preserved_capabilities": [],
            "test_receipts": [],
            "review_authority": None,
            "status_at_merge_refresh": "OBSERVED_AT_SOURCE_CENSUS_NOT_RECONCILED",
        }
        records.append(record)

    path_owners: dict[str, list[int]] = defaultdict(list)
    for record in records:
        changed = record["current_base_changed_files"]
        if changed:
            for path in changed["paths"]:
                path_owners[path].append(record["pr_number"])
    overlaps = [
        {"path": path, "pr_numbers": sorted(numbers), "semantic_conflict_proven": False}
        for path, numbers in sorted(path_owners.items())
        if len(numbers) > 1
    ]
    overlap_by_pr: dict[int, list[str]] = defaultdict(list)
    for overlap in overlaps:
        for number in overlap["pr_numbers"]:
            overlap_by_pr[number].append(overlap["path"])
    for record in records:
        record["overlapping_current_base_paths"] = sorted(overlap_by_pr[record["pr_number"]])

    cycles = dependency_cycles(records)
    git_complete = all(
        record["pr_base_changed_files"]["complete"]
        and record["pr_base_commits"]["complete"]
        and record["current_main_merge"]["conflict_paths_complete"]
        and (
            record["current_base_changed_files"] is None
            or (
                record["current_base_changed_files"]["complete"]
                and record["current_base_commits"]["complete"]
                and record["current_base_merge"]["conflict_paths_complete"]
            )
        )
        for record in records
    )
    document = {
        "schema": "HHS_PR914_GIT_RECONCILIATION_EVIDENCE_V1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": census["repository"],
        "source_census": {
            "path": args.census.name,
            "sha256": hashlib.sha256(census_bytes).hexdigest(),
            "observed_at": census["observed_at"],
            "schema": census["schema"],
        },
        "source_census_observed_at": census["observed_at"],
        "source_census_observed_pr_count": len(source_records),
        "source_census_main_sha": census["main_sha"],
        "observed_open_pr_count": len(records),
        "observation_basis": "EXACT_SOURCE_CENSUS_AND_LOCAL_GIT_OBJECTS_NOT_A_LIVE_REFRESH",
        "live_ref_refresh_performed": False,
        "head_moves_since_source_census": "NOT_COLLECTED",
        "git_evidence_complete": git_complete,
        "changed_paths_and_commit_lists_complete": git_complete,
        "hypothetical_merge_tree_evaluation_complete": git_complete,
        "reviews_checks_and_combined_statuses_complete": False,
        "semantic_reconciliation_complete": False,
        "frozen_and_canonical_authority_review_complete": False,
        "g0_gate_passed": False,
        "g1_complete": False,
        "integrated": False,
        "candidate_composed": False,
        "terminal_dispositions_assigned": False,
        "automatic_mass_merge_authorized": False,
        "snapshot_is_promotion_evidence": False,
        "requires_refresh_before_any_merge": True,
        "dependency_cycles": cycles,
        "current_base_path_overlaps": overlaps,
        "pull_requests": records,
        "main_merge": "NOT_PERFORMED",
        "production_deploy": "NOT_PERFORMED",
    }
    validate_document(document)
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = collect(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        errors="surrogateescape",
    )
    temporary.replace(args.output)
    print(json.dumps({
        "open_prs": document["observed_open_pr_count"],
        "git_evidence_complete": document["git_evidence_complete"],
        "dependency_cycle_count": len(document["dependency_cycles"]),
        "overlap_path_count": len(document["current_base_path_overlaps"]),
        "conflicted_current_main_pr_count": sum(
            record["current_main_merge"]["status"] == "CONFLICTED_HYPOTHETICAL_MERGE_TREE"
            for record in document["pull_requests"]
        ),
        "g1_complete": document["g1_complete"],
        "candidate_composed": document["candidate_composed"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
