from __future__ import annotations

from hhs_backend.api import a0_pass205_transport_bootstrap as transport
from hhs_backend.api import pass205_continuation_routes as routes
from hhs_backend.runtime.hhs_pass205_governed_continuation_v2 import (
    GovernedPass205ContinuationRuntime,
)


class FakeAuthority:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, source: str):
        self.calls += 1
        receipt = str(self.calls % 10) * 72
        return {
            "runtime": {"step": self.calls, "halted": False, "state_hash72": "S" * 72},
            "receipt": {"receipt_hash72": receipt, "state_hash72": "S" * 72},
            "authority_audit": {"ok": True, "source": source, "reasons": []},
            "authority_state": "ADMITTED",
        }


def _event(cell: int, mask: int, control: int = 0) -> dict[str, int]:
    return {"cell": cell, "control_g": control, "xor_mask": mask}


def test_lossless_transport_serializes_uint64_fields_as_decimal_strings() -> None:
    maximum = (1 << 64) - 1
    payload = {
        "state_words": [0, (1 << 53) + 1, maximum],
        "learning_features": [maximum],
        "events": [{"cell": 1, "xor_mask": maximum}],
        "projection_channels": [[0xFFFFFFFF]],
        "generation": 72,
    }
    encoded = transport.encode_lossless_uint64(payload)
    assert encoded["state_words"] == ["0", str((1 << 53) + 1), str(maximum)]
    assert encoded["learning_features"] == [str(maximum)]
    assert encoded["events"][0]["xor_mask"] == str(maximum)
    assert encoded["projection_channels"] == [[0xFFFFFFFF]]
    assert encoded["generation"] == 72


def test_existing_request_models_accept_decimal_uint64_strings() -> None:
    maximum = str((1 << 64) - 1)
    event = routes.DeltaEvent(cell=80, control_g=242, xor_mask=maximum)
    request = routes.RetrieveRequest(target_state_words=[maximum] * 81)
    assert int(event.xor_mask) == (1 << 64) - 1
    assert all(int(value) == (1 << 64) - 1 for value in request.target_state_words)
    assert '"xor_mask":"1"' in routes.STUDIO_HTML


def test_rejected_candidate_order_is_canonical_and_root_stable(tmp_path) -> None:
    runtime = GovernedPass205ContinuationRuntime(
        tmp_path / "pass205.sqlite3",
        authority_provider=FakeAuthority(),
    )
    genesis = runtime.snapshot(runtime.genesis_root216)
    first = runtime.advance(
        parent_root216=genesis["continuation_root216"],
        events=[_event(7, 1, 7)],
    )
    second = runtime.advance(
        parent_root216=first["continuation_root216"],
        events=[_event(9, 2, 9)],
    )
    incompatible = runtime.native.hash216_bytes(b"incompatible")
    roots = [first["continuation_root216"], second["continuation_root216"]]
    with runtime._transaction() as connection:
        for root in reversed(roots):
            connection.execute(
                "UPDATE vectors SET constraint_root216=? WHERE continuation_root216=?",
                (incompatible, root),
            )

    result_a = runtime.retrieve(target_state_words=genesis["state_words"])
    rejected_a = result_a["rejected_candidates"]
    assert rejected_a == sorted(
        rejected_a,
        key=lambda item: (item["continuation_root216"], item["reason"]),
    )

    with runtime._transaction() as connection:
        rows = connection.execute(
            "SELECT * FROM vectors WHERE continuation_root216 IN (?,?)",
            tuple(roots),
        ).fetchall()
        connection.execute(
            "DELETE FROM vectors WHERE continuation_root216 IN (?,?)",
            tuple(roots),
        )
        for row in reversed(rows):
            connection.execute(
                "INSERT INTO vectors VALUES (?,?,?,?)",
                (
                    row["continuation_root216"], row["schema_root216"],
                    row["constraint_root216"], row["features_json"],
                ),
            )

    result_b = runtime.retrieve(target_state_words=genesis["state_words"])
    assert result_b["retrieval_root216"] == result_a["retrieval_root216"]
    assert result_b["rejected_candidates"] == rejected_a
    assert result_b["candidate_ordering"] == "CANONICAL_ROOT_REASON_ORDER"


def test_transport_status_route_is_additive() -> None:
    paths = {route.path for route in transport.router.routes}
    assert "/api/runtime/continuation/transport" in paths
    assert transport.PASS205_TRANSPORT_BOOTSTRAP["lossless_uint64"] is True
