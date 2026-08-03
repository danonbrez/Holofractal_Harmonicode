from __future__ import annotations

import json

import pytest

from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import ContinuationRejected
from hhs_backend.runtime.hhs_pass205_governed_continuation_v2 import (
    GovernedPass205ContinuationRuntime,
)


def _event(cell: int, mask: int, control: int = 0) -> dict[str, int]:
    return {"cell": cell, "control_g": control, "xor_mask": mask}


class FakeAuthority:
    def __init__(self) -> None:
        self.calls = 0
        self.blocked = False

    def __call__(self, source: str):
        self.calls += 1
        digit = str(self.calls % 10)
        receipt = digit * 72
        return {
            "runtime": {
                "step": self.calls,
                "halted": False,
                "state_hash72": "S" * 72,
                "receipt_hash72": receipt,
            },
            "receipt": {
                "step": self.calls,
                "state_hash72": "S" * 72,
                "receipt_hash72": receipt,
            },
            "authority_audit": {
                "ok": not self.blocked,
                "source": source,
                "reasons": ["blocked for test"] if self.blocked else [],
            },
            "authority_state": "QUARANTINED" if self.blocked else "ADMITTED",
        }


def test_new_continuation_requires_vm81_admission_before_persistence(tmp_path) -> None:
    authority = FakeAuthority()
    runtime = GovernedPass205ContinuationRuntime(
        tmp_path / "pass205.sqlite3",
        authority_provider=authority,
    )
    genesis = runtime.snapshot(runtime.genesis_root216)
    child = runtime.advance(
        parent_root216=genesis["continuation_root216"],
        expected_parent_receipt_hash72=genesis["receipt_hash72"],
        events=[_event(5, 1 << 63, 242)],
    )

    assert authority.calls == 1
    assert child["receipt_hash72"] == "1" * 72
    assert child["vm81_admission"]["authority_audit"]["ok"] is True
    assert runtime.verify(child["continuation_root216"])["ok"]
    status = runtime.status()
    assert status["vm81_admission_count"] == 1
    assert status["vm81_admission_required_before_persistence"] is True


def test_quarantined_authority_cannot_persist_snapshot(tmp_path) -> None:
    authority = FakeAuthority()
    authority.blocked = True
    runtime = GovernedPass205ContinuationRuntime(
        tmp_path / "pass205.sqlite3",
        authority_provider=authority,
    )
    genesis = runtime.snapshot(runtime.genesis_root216)
    before = runtime.status()["snapshot_count"]

    with pytest.raises(ContinuationRejected, match="VM81 authority blocked"):
        runtime.advance(
            parent_root216=genesis["continuation_root216"],
            events=[_event(1, 2, 1)],
        )

    assert runtime.status()["snapshot_count"] == before
    assert runtime.status()["vm81_admission_count"] == 0


def test_replay_reconstructs_ordered_deltas_and_detects_payload_tamper(tmp_path) -> None:
    authority = FakeAuthority()
    runtime = GovernedPass205ContinuationRuntime(
        tmp_path / "pass205.sqlite3",
        authority_provider=authority,
    )
    genesis = runtime.snapshot(runtime.genesis_root216)
    first = runtime.advance(
        parent_root216=genesis["continuation_root216"],
        events=[_event(2, 4, 72)],
    )
    second = runtime.advance(
        parent_root216=first["continuation_root216"],
        events=[_event(70, 8, 216)],
    )

    replay = runtime.replay(second["continuation_root216"])
    assert replay["ok"]
    assert replay["reconstructed_from_ordered_deltas"] is True
    assert replay["reconstructed_target_state_words"] == second["state_words"]

    tampered = list(first["state_words"])
    tampered[2] ^= 1
    with runtime._transaction() as connection:
        connection.execute(
            "UPDATE snapshots SET state_json=? WHERE continuation_root216=?",
            (json.dumps(tampered), first["continuation_root216"]),
        )

    replay = runtime.replay(second["continuation_root216"])
    assert not replay["ok"]
    assert any(
        "STATE_PAYLOAD_RECONSTRUCTION_MISMATCH" in failure.get("reasons", [])
        for failure in replay["failures"]
    )


def test_public_federation_bootstrap_rebinds_legacy_routes() -> None:
    from hhs_backend.api import a_pass205_governed_bootstrap as bootstrap
    from hhs_backend.api import pass205_continuation_routes as routes

    assert bootstrap.PASS205_GOVERNED_ROUTE_BINDING["ok"]
    assert isinstance(routes.PASS205_CONTINUATION_RUNTIME, GovernedPass205ContinuationRuntime)
