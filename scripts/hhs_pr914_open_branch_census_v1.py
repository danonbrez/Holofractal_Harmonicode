#!/usr/bin/env python3
"""Collect PR914 G0 evidence without assigning integration dispositions.

The collector uses the GitHub API for exact PR/branch refs and local Git objects
for merge-base and ahead/behind ancestry. It never merges, pushes, deletes, or
classifies an entry as integrated, superseded, equivalent, or obsolete.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PAGE_SIZE = 100
DEFAULT_API_ROOT = "https://api.github.com"


class CensusError(RuntimeError):
    pass


def request_json(api_root: str, path: str, token: str | None, params: dict[str, Any]) -> Any:
    url = f"{api_root}/{path}?{urlencode(params)}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "hhs-pr914-read-only-census",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers=headers), timeout=60) as response:
                return json.load(response)
        except HTTPError as exc:
            retryable = exc.code in (429, 500, 502, 503, 504)
            if not retryable or attempt == 3:
                raise CensusError(f"GitHub API failed for {path}: HTTP {exc.code}") from exc
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def paginate(api_root: str, path: str, token: str | None, params: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 1
    while True:
        query = dict(params, per_page=PAGE_SIZE, page=page)
        batch = request_json(api_root, path, token, query)
        if not isinstance(batch, list):
            raise CensusError(f"Expected a list from {path}")
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            return rows
        page += 1


def run_git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise CensusError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def fetch_refs(repository: Path) -> None:
    run_git(
        repository,
        "fetch",
        "--quiet",
        "--no-tags",
        "--filter=blob:none",
        "origin",
        "+refs/heads/*:refs/remotes/origin/*",
        "+refs/pull/*/head:refs/remotes/pull/*",
    )


def parse_rev_list_counts(value: str) -> tuple[int, int]:
    fields = value.split()
    if len(fields) != 2:
        raise CensusError(f"Unexpected rev-list count: {value!r}")
    behind, ahead = (int(field) for field in fields)
    return behind, ahead


def git_ancestry(repository: Path, base_sha: str, head_sha: str) -> dict[str, Any]:
    merge_base = run_git(repository, "merge-base", base_sha, head_sha)
    behind, ahead = parse_rev_list_counts(
        run_git(repository, "rev-list", "--left-right", "--count", f"{base_sha}...{head_sha}")
    )
    return {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "merge_base_sha": merge_base,
        "behind_by": behind,
        "ahead_by": ahead,
    }


def dependency_parents(pull_requests: list[dict[str, Any]]) -> dict[int, list[int]]:
    heads: dict[str, list[int]] = defaultdict(list)
    for pr in pull_requests:
        heads[pr["head"]["ref"]].append(int(pr["number"]))
    parents: dict[int, list[int]] = {}
    for pr in pull_requests:
        number = int(pr["number"])
        parents[number] = sorted(
            candidate
            for candidate in heads.get(pr["base"]["ref"], [])
            if candidate != number
        )
    return parents


def build_branch_records(
    branches: list[dict[str, Any]], pull_requests: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    open_prs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pr in pull_requests:
        open_prs[pr["head"]["ref"]].append(pr)
    records = []
    for branch in sorted(branches, key=lambda row: row["name"]):
        name = branch["name"]
        linked = sorted(open_prs.get(name, []), key=lambda row: row["number"])
        if name == "main":
            classification = "DEFAULT_BRANCH"
        elif linked:
            classification = "OPEN_PR_HEAD"
        else:
            classification = "UNPR_BRANCH_REQUIRES_RECONCILIATION"
        records.append({
            "name": name,
            "sha": branch["commit"]["sha"],
            "classification": classification,
            "open_pr_numbers": [int(pr["number"]) for pr in linked],
            "matches_all_linked_open_pr_heads": all(
                branch["commit"]["sha"] == pr["head"]["sha"] for pr in linked
            ) if linked else None,
            "disposition": "UNASSESSED",
            "integration_commit": None,
        })
    return records


def snapshot_entries(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("pull_requests", "entries", "open_prs"):
        value = snapshot.get(key)
        if isinstance(value, list):
            return value
    raise CensusError("Snapshot has no pull_requests, entries, or open_prs list")


def snapshot_delta(snapshot: dict[str, Any], pull_requests: list[dict[str, Any]]) -> dict[str, Any]:
    old_entries = snapshot_entries(snapshot)
    old = {int(row.get("pr_number", row.get("number"))): row for row in old_entries}
    live = {int(pr["number"]): pr for pr in pull_requests}
    head_changes = []
    for number in sorted(old.keys() & live.keys()):
        previous = old[number].get("head_sha")
        current = live[number]["head"]["sha"]
        if previous and previous != current:
            head_changes.append({"pr_number": number, "previous": previous, "current": current})
    return {
        "snapshot_entry_count": len(old),
        "live_entry_count": len(live),
        "added_pr_numbers": sorted(live.keys() - old.keys()),
        "no_longer_open_pr_numbers": sorted(old.keys() - live.keys()),
        "head_sha_changes": head_changes,
        "comparison_complete": True,
    }


def duplicate_tip_groups(branch_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for branch in branch_records:
        grouped[branch["sha"]].append(branch["name"])
    return [
        {"sha": sha, "branch_names": sorted(names), "semantic_equivalence_proven": False}
        for sha, names in sorted(grouped.items())
        if len(names) > 1
    ]


def validate_census_document(document: dict[str, Any]) -> None:
    prs = document["pull_requests"]
    branches = document["branches"]
    if document["observed_open_pr_count"] != len(prs):
        raise CensusError("Open PR count does not match records")
    if document["observed_branch_count"] != len(branches):
        raise CensusError("Branch count does not match records")
    if document["integrated"] is not False:
        raise CensusError("Census cannot assert integration")
    if document["automatic_mass_merge_authorized"] is not False:
        raise CensusError("Census cannot authorize mass merge")
    if document["requires_refresh_before_any_merge"] is not True:
        raise CensusError("Pre-merge refresh obligation must remain enabled")
    if any(pr["disposition"] != "UNASSESSED" for pr in prs):
        raise CensusError("Collector must not assign terminal PR dispositions")
    if any(branch["disposition"] != "UNASSESSED" for branch in branches):
        raise CensusError("Collector must not assign terminal branch dispositions")


def collect(args: argparse.Namespace) -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN")
    api_path = f"repos/{args.owner}/{args.repo}"
    pulls = paginate(args.api_root, f"{api_path}/pulls", token, {
        "state": "open", "sort": "updated", "direction": "desc",
    })
    branches = paginate(args.api_root, f"{api_path}/branches", token, {})
    if not args.skip_fetch:
        fetch_refs(args.repository)
    parents = dependency_parents(pulls)
    branch_records = build_branch_records(branches, pulls)
    branch_by_name = {row["name"]: row for row in branch_records}
    main_sha = branch_by_name["main"]["sha"]
    records = []
    for pr in sorted(pulls, key=lambda row: row["number"], reverse=True):
        number = int(pr["number"])
        head_ref = pr["head"]["ref"]
        base_ref = pr["base"]["ref"]
        head_sha = pr["head"]["sha"]
        base_sha = pr["base"]["sha"]
        head_branch = branch_by_name.get(head_ref)
        base_branch = branch_by_name.get(base_ref)
        record = {
            "pr_number": number,
            "pr_url": pr["html_url"],
            "title": pr["title"],
            "draft": bool(pr["draft"]),
            "updated_at": pr["updated_at"],
            "head_ref": head_ref,
            "head_sha": head_sha,
            "base_ref": base_ref,
            "base_sha": base_sha,
            "head_branch_observed_sha": head_branch["sha"] if head_branch else None,
            "head_ref_verified": bool(head_branch and head_branch["sha"] == head_sha),
            "base_branch_observed_sha": base_branch["sha"] if base_branch else None,
            "pr_base_ancestry": git_ancestry(args.repository, base_sha, head_sha),
            "current_main_ancestry": git_ancestry(args.repository, main_sha, head_sha),
            "current_base_ancestry": (
                git_ancestry(args.repository, base_branch["sha"], head_sha)
                if base_branch else None
            ),
            "changed_files": {
                "count": pr.get("changed_files"),
                "paths": [],
                "paths_complete": False,
            },
            "commit_count": pr.get("commits"),
            "contract_dependencies": parents[number],
            "conflicts": [],
            "frozen_layer_impact": "UNASSESSED",
            "disposition": "UNASSESSED",
            "resolution_reason": None,
            "integration_commit": None,
            "preserved_capabilities": [],
            "test_receipts": [],
            "review_authority": None,
            "canonical_source_impact": "UNASSESSED",
            "status_at_merge_refresh": "OBSERVED_NOT_RECONCILED",
        }
        records.append(record)
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    document = {
        "schema": "HHS_PR914_G0_LIVE_CENSUS_V1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "repository": f"{args.owner}/{args.repo}",
        "main_sha": main_sha,
        "observed_open_pr_count": len(records),
        "observed_branch_count": len(branch_records),
        "snapshot_comparison": snapshot_delta(snapshot, pulls),
        "head_refs_verified": all(row["head_ref_verified"] for row in records),
        "sha_and_merge_bases_verified": True,
        "g0_collection_complete": True,
        "g0_gate_passed": False,
        "g1_complete": False,
        "integrated": False,
        "automatic_mass_merge_authorized": False,
        "snapshot_is_promotion_evidence": False,
        "requires_refresh_before_any_merge": True,
        "unpr_branch_count": sum(
            row["classification"] == "UNPR_BRANCH_REQUIRES_RECONCILIATION"
            for row in branch_records
        ),
        "duplicate_tip_groups": duplicate_tip_groups(branch_records),
        "pull_requests": records,
        "branches": branch_records,
    }
    validate_census_document(document)
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default="danonbrez")
    parser.add_argument("--repo", default="Holofractal_Harmonicode")
    parser.add_argument("--api-root", default=DEFAULT_API_ROOT)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-fetch", action="store_true")
    args = parser.parse_args()
    document = collect(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({
        "open_prs": document["observed_open_pr_count"],
        "branches": document["observed_branch_count"],
        "unpr_branches": document["unpr_branch_count"],
        "head_refs_verified": document["head_refs_verified"],
        "g0_collection_complete": document["g0_collection_complete"],
        "g0_gate_passed": document["g0_gate_passed"],
        "g1_complete": document["g1_complete"],
        "integrated": document["integrated"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
