"""Recover secondary I15 action indexes from durable consumption receipts."""
from __future__ import annotations

import fcntl

from hhs_runtime.pass218.execution_i15 import (
    ACTION_CLAIM_INDEX_SCHEMA,
    Pass218ReleaseConsumptionJournal,
    validate_release_claim,
)


def repair_consumption_indexes(journal: Pass218ReleaseConsumptionJournal) -> int:
    repaired = 0
    with journal.lock_path.open("r+") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        for path in sorted(journal.claims.glob("*.json")):
            raw = journal._read(path)
            if raw is None:
                continue
            receipt = validate_release_claim(raw)
            index_path = journal._action_path(receipt["action_record_hash72"])
            if index_path.exists():
                continue
            journal._atomic_create(index_path, {
                "schema": ACTION_CLAIM_INDEX_SCHEMA,
                "action_record_hash72": receipt["action_record_hash72"],
                "release_record_hash72": receipt["release_record_hash72"],
                "claim_record_hash72": receipt["record_hash72"],
            })
            repaired += 1
    return repaired


__all__ = ["repair_consumption_indexes"]
