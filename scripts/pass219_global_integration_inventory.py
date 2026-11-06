#!/usr/bin/env python3
"""Read-only repository-wide branch/PR CI admission inventory for Pass219 Lane5.

Does not merge, rewrite branches, mint receipts, or infer green from missing checks.
GitHub branch protection and native signed VM81 admission remain separate gates.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

REPO = os.getenv("GITHUB_REPOSITORY", "danonbrez/Holofractal_Harmonicode")
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
BASE = "https://api.github.com/repos/" + REPO

def api(path):
    if not TOKEN:
        raise RuntimeError("GitHub token required for complete inventory")
    req = urllib.request.Request(
        BASE + path, headers={"Accept": "application/vnd.github+json",
                              "Authorization": "Bearer " + TOKEN,
                              "X-GitHub-Api-Version": "2022-11-28",
                              "User-Agent": "hhs-pass219-inventory"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)

def pages(path):
    results = []
    page = 1
    while True:
        separator = "&" if "?" in path else "?"
        items = api(path + separator + f"per_page=100&page={page}")
        if not isinstance(items, list):
            raise ValueError("expected paginated GitHub array")
        results.extend(items)
        if len(items) != 100:
            return results
        page += 1

def all_check_runs(sha):
    """Enumerate every check run for one immutable head SHA; fail closed on truncation."""
    runs = []
    page = 1
    while True:
        data = api(f"/commits/{urllib.parse.quote(sha, safe='')}/check-runs?per_page=100&page={page}")
        batch = data.get("check_runs")
        total = data.get("total_count")
        if not isinstance(batch, list) or not isinstance(total, int):
            raise RuntimeError("check-run response incomplete")
        runs.extend(batch)
        if len(runs) >= total:
            if len(runs) != total:
                raise RuntimeError("check-run count mismatch")
            return runs
        if not batch:
            raise RuntimeError("truncated check-runs pagination")
        page += 1

def all_commit_statuses(sha):
    """Include all legacy status contexts, not just the first API page."""
    statuses = pages(f"/commits/{urllib.parse.quote(sha, safe='')}/statuses")
    # Newest status is authoritative for each context; old failures are superseded.
    latest = {}
    for status in statuses:
        context = status.get("context")
        if not isinstance(context, str) or not context:
            raise RuntimeError("commit status lacks context")
        if context not in latest:
            latest[context] = status
    return list(latest.values())

def collect():
    pulls = pages("/pulls?state=open")
    branches = pages("/branches")
    branch_names = {b["name"] for b in branches}
    pr_heads = {p["head"]["ref"] for p in pulls
                if p["head"]["repo"] and p["head"]["repo"]["full_name"] == REPO}
    records = []
    cache = {}
    for pr in pulls:
        sha = pr["head"]["sha"]
        if sha not in cache:
            runs = all_check_runs(sha)
            statuses = all_commit_statuses(sha)
            cache[sha] = (runs, statuses)
        runs, statuses = cache[sha]
        contexts = [s.get("state") for s in statuses]
        observed = bool(runs or statuses)
        green = (observed and
                 all(r.get("status") == "completed" and
                     r.get("conclusion") in ("success", "skipped", "neutral")
                     for r in runs) and
                 all(s == "success" for s in contexts))
        branch = pr["head"]["ref"]
        candidate = bool(green and not pr["draft"] and
                         pr["base"]["ref"] == "main" and
                         pr["head"]["repo"] and
                         pr["head"]["repo"]["full_name"] == REPO)
        records.append({
            "number": pr["number"], "title": pr["title"], "body": pr.get("body") or "",
            "head": branch, "head_sha": sha, "base": pr["base"]["ref"],
            "draft": pr["draft"], "observed_check_count": len(runs)+len(statuses),
            "observed_green": green, "integration_candidate": candidate,
            "blocking_checks": sorted([r["name"] for r in runs
                     if r.get("status") != "completed" or
                     r.get("conclusion") not in ("success","skipped","neutral")] +
                     [s.get("context","legacy-status") for s in statuses
                      if s.get("state") != "success"]),
            "url": pr["html_url"]
        })
    return {
        "schema": "HHS_PASS219_GLOBAL_BRANCH_PR_ADMISSION_INVENTORY_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repository": REPO,
        "source": "GitHub API paginated current branches and open PRs",
        "branch_count": len(branches), "open_pr_count": len(pulls),
        "orphan_branches_without_open_pr": sorted(branch_names-pr_heads-{"main"}),
        "open_prs": records,
        "policy": {
            "green": "all observed checks completed successfully/neutral/skipped and legacy statuses success",
            "candidate": "green, same-repo, non-draft, main-targeted; not merger authorization",
            "required_before_merge": [
                "fresh main rebase/compare and conflict detection",
                "branch protection and required checks",
                "deduplicate already merged inherited changes",
                "dependency-scoped tests and ordered tensor/VM81/Hash72/Hash216 constraints",
                "signed environment admission and deterministic replay",
                "production and deployment boundary review for affected paths"
            ]}}

def main():
    report = collect()
    destination = sys.argv[1] if len(sys.argv)>1 else "pass219-global-integration-inventory.json"
    with open(destination, "w", encoding="utf-8") as out:
        json.dump(report, out, indent=2, sort_keys=True)
        out.write("\n")
    print(f"BRANCHES={report['branch_count']} PRS={report['open_pr_count']} "
          f"CANDIDATES={sum(p['integration_candidate'] for p in report['open_prs'])} "
          f"ORPHAN_BRANCHES={len(report['orphan_branches_without_open_pr'])}")

if __name__ == "__main__":
    main()
