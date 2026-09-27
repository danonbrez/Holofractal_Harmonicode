from __future__ import annotations

from hhs_runtime import hhs_qgu_temporal_phase_guard_v1 as qgu


def test_implicit_temporal_window_does_not_expire_during_its_own_construction(monkeypatch):
    ticks = iter((1_000_000_000, 1_100_000_000))
    monkeypatch.setattr(qgu, "now_ns", lambda: next(ticks))

    receipt = qgu.evaluate_temporal_admissibility(
        {"op": "SET", "path": "runtime.intent", "value": {"next": "phase_locked_state"}}
    )

    assert receipt.window.created_at_ns == 1_000_000_000
    assert receipt.status != qgu.TemporalGuardStatus.EXPIRED


def test_explicit_stale_temporal_window_still_fails_closed():
    window = qgu.make_temporal_window(
        max_latency_ms=20,
        created_at_ns=1_000_000_000,
    )
    receipt = qgu.evaluate_temporal_admissibility(
        {"op": "SET", "path": "runtime.intent", "value": {"next": "phase_locked_state"}},
        window=window,
        observed_at_ns=1_100_000_000,
    )

    assert receipt.status == qgu.TemporalGuardStatus.EXPIRED
    assert receipt.closes_before_noise_floor is False
