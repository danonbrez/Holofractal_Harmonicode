"""Partition Pass 196 gaps without relabeling or hiding unresolved evidence."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

SCHEMA = "HHS_PASS_196_INTEGRATION_GAP_PARTITION_V1"
LEGACY_END = 99
CURRENT_FRONTIER_START = 196


def _stable_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def partition_integration_gaps(
    unresolved_passes: Iterable[Mapping[str, Any]],
    *,
    maximum_discovered_pass: int,
    legacy_end: int = LEGACY_END,
    current_frontier_start: int = CURRENT_FRONTIER_START,
) -> dict[str, Any]:
    """Classify scope while preserving every original unresolved row.

    This is a reporting projection only. It never changes a pass state to
    INTEGRATED and never suppresses a gap from the canonical raw report.
    """

    unresolved = _stable_rows(unresolved_passes)
    legacy = [row for row in unresolved if int(row["pass_number"]) <= legacy_end]
    bridge = [
        row
        for row in unresolved
        if legacy_end < int(row["pass_number"]) < current_frontier_start
    ]
    current = [
        row
        for row in unresolved
        if int(row["pass_number"]) >= current_frontier_start
    ]
    current_frontier_present = maximum_discovered_pass >= current_frontier_start
    current_frontier_closed = current_frontier_present and not current

    return {
        "schema": SCHEMA,
        "maximum_discovered_pass": int(maximum_discovered_pass),
        "legacy_range": [1, int(legacy_end)],
        "bridge_range": [int(legacy_end) + 1, int(current_frontier_start) - 1],
        "current_frontier_range": [
            int(current_frontier_start),
            int(maximum_discovered_pass),
        ],
        "legacy_unresolved_count": len(legacy),
        "bridge_unresolved_count": len(bridge),
        "current_frontier_unresolved_count": len(current),
        "legacy_unresolved_passes": legacy,
        "bridge_unresolved_passes": bridge,
        "current_frontier_unresolved_passes": current,
        "current_frontier_present": current_frontier_present,
        "current_frontier_closed": current_frontier_closed,
        "global_integration_closed": not unresolved,
        "raw_gap_count_preserved": len(unresolved),
        "classification_mutates_canonical_state": False,
    }
