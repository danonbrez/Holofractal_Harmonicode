from __future__ import annotations

import asyncio

from hhs_backend.api import litert_lm_assistant_routes as routes


class FakeRouteService:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.thread_id = "thread:startup-warmup"

    def create_thread(self, *, project_id: str, title: str, metadata):
        return {
            "thread_id": self.thread_id,
            "project_id": project_id,
            "title": title,
            "metadata": dict(metadata or {}),
        }

    async def send_message(self, thread_id: str, **kwargs):
        self.calls.append({"thread_id": thread_id, **kwargs})
        if len(self.calls) == 1:
            return {
                "ok": True,
                "thread_id": thread_id,
                "assistant_message": {"content": "remembered"},
            }
        return {
            "ok": True,
            "thread_id": thread_id,
            "assistant_message": {"content": "HHS-PRODUCTION-CHATBOT-E2E-7249"},
        }


def test_production_startup_warmup_executes_identical_two_turn_chat_handler(monkeypatch):
    fake = FakeRouteService()
    monkeypatch.setattr(routes, "_SERVICE", fake)

    receipt = asyncio.run(routes.production_assistant_route_warmup())

    assert receipt["ok"] is True
    assert receipt["two_turn_exact_memory_verified"] is True
    assert receipt["thread_continuity_verified"] is True
    assert receipt["thread_id"] == fake.thread_id
    assert receipt["token"] == "HHS-PRODUCTION-CHATBOT-E2E-7249"
    assert receipt["elapsed_ms"] >= 0
    assert len(fake.calls) == 2
    assert fake.calls[0]["thread_id"] == fake.thread_id
    assert fake.calls[1]["thread_id"] == fake.thread_id
    assert fake.calls[0]["assistant_mode"] == "BOTH"
    assert fake.calls[1]["assistant_mode"] == "BOTH"
    assert (
        fake.calls[0]["content"]
        == "Remember this exact token for my next message: "
        "HHS-PRODUCTION-CHATBOT-E2E-7249. Reply briefly."
    )
    assert (
        fake.calls[1]["content"]
        == "What exact token did I ask you to remember in my previous message? "
        "Reply with only the token."
    )


def test_production_startup_warmup_fails_closed_on_recall_mismatch(monkeypatch):
    fake = FakeRouteService()

    async def wrong_second_turn(thread_id: str, **kwargs):
        fake.calls.append({"thread_id": thread_id, **kwargs})
        return {
            "ok": True,
            "thread_id": thread_id,
            "assistant_message": {"content": "wrong-token"},
        }

    fake.send_message = wrong_second_turn
    monkeypatch.setattr(routes, "_SERVICE", fake)

    try:
        asyncio.run(routes.production_assistant_route_warmup())
    except RuntimeError as exc:
        assert "warmup recall mismatch" in str(exc)
    else:
        raise AssertionError("startup warmup must fail closed on recall mismatch")
