from pathlib import Path
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_runtime.pass153 import AgentEnvironment, LiteRTModelAdapter, ModelSpec, Pass153Error, ReferenceOpenModel, ToolSpec, build_default_environment
from hhs_runtime.pass153.api import router


def test_reference_open_model_is_deterministic():
    env = build_default_environment()
    env.create_session("hhs-reference-open-model-v1", session_id="s")
    a = env.chat("s", "HHS", max_tokens=8)
    env2 = build_default_environment()
    env2.create_session("hhs-reference-open-model-v1", session_id="s")
    b = env2.chat("s", "HHS", max_tokens=8)
    assert a["content"] == b["content"]
    assert a["authoritative"] is False and a["validated"] is True


def test_model_replacement_requires_generation_advance():
    env = AgentEnvironment()
    model = ReferenceOpenModel({"*": ["ok."]})
    env.register_model(ModelSpec("m", "reference", "memory", 128, generation=0), model)
    with pytest.raises(Pass153Error, match="P153_STALE_MODEL_GENERATION"):
        env.register_model(ModelSpec("m", "reference", "memory", 128, generation=0), model)
    env.register_model(ModelSpec("m", "reference", "memory", 128, generation=1), model)


def test_session_isolation_and_receipt_replay():
    env = build_default_environment()
    env.create_session("hhs-reference-open-model-v1", session_id="a")
    env.create_session("hhs-reference-open-model-v1", session_id="b")
    env.chat("a", "one", max_tokens=4)
    env.chat("b", "two", max_tokens=4)
    assert env.sessions["a"].receipt_head != env.sessions["b"].receipt_head
    assert env.replay_session("a")["status"] == "MATCH"
    assert env.replay_session("b")["status"] == "MATCH"


def test_tools_are_declared_and_capability_gated():
    env = AgentEnvironment(tool_authorizer=lambda spec, args: not spec.mutating)
    env.register_model(ModelSpec("m", "reference", "memory", 128), ReferenceOpenModel({"*": ["ok."]}))
    env.register_tool(ToolSpec("read", "read", False), lambda args: args)
    env.register_tool(ToolSpec("write", "write", True, "mutation"), lambda args: args)
    env.create_session("m", session_id="s")
    assert env.invoke_tool("s", "read", {"x": 1})["status"] == "TOOL_RESULT_VALIDATED"
    with pytest.raises(Pass153Error, match="P153_TOOL_UNAUTHORIZED"):
        env.invoke_tool("s", "write", {})


class FakeInterpreter:
    def __init__(self, model_path):
        self.value = None
    def allocate_tensors(self):
        pass
    def get_input_details(self):
        return [{"name": "prompt", "index": 0}]
    def get_output_details(self):
        return [{"name": "text", "index": 1}]
    def set_tensor(self, index, value):
        self.value = value
    def invoke(self):
        pass
    def get_tensor(self, index):
        return self.value


def test_litert_adapter_executes_injected_interpreter():
    adapter = LiteRTModelAdapter("model.tflite", input_encoder=lambda prompt, _: prompt.upper(), output_decoder=lambda raw, _: raw[0] + "!", interpreter_factory=FakeInterpreter)
    assert adapter.generate("hello") == "HELLO!"


def test_litert_adapter_rejects_missing_tensor_contract():
    class Empty(FakeInterpreter):
        def get_input_details(self):
            return []
    with pytest.raises(Pass153Error, match="P153_LITERT_TENSOR_CONTRACT"):
        LiteRTModelAdapter("bad.tflite", input_encoder=lambda prompt, details: prompt, output_decoder=lambda raw, details: "x", interpreter_factory=Empty)


def test_output_validator_fails_closed():
    env = AgentEnvironment(output_validator=lambda text: False)
    env.register_model(ModelSpec("m", "reference", "memory", 128), ReferenceOpenModel({"*": ["draft."]}))
    env.create_session("m", session_id="s")
    with pytest.raises(Pass153Error, match="P153_OUTPUT_REJECTED"):
        env.chat("s", "prompt")


def test_fastapi_routes_cover_status_session_chat_tool_replay():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    assert client.get("/api/pass153/status").status_code == 200
    created = client.post("/api/pass153/sessions", json={"model_id": "hhs-reference-open-model-v1", "session_id": "api-test"})
    assert created.status_code == 200
    turn = client.post("/api/pass153/sessions/api-test/chat", json={"prompt": "HHS", "max_tokens": 8}).json()
    assert turn["authoritative"] is False
    tool = client.post("/api/pass153/sessions/api-test/tools/echo", json={"arguments": {"a": 1}}).json()
    assert tool["result"]["echo"] == {"a": 1}
    assert client.get("/api/pass153/sessions/api-test/replay").json()["status"] == "MATCH"


def test_gui_contains_all_required_workspaces():
    text = (Path(__file__).resolve().parents[2] / "hhs_gui/pass153/index.html").read_text(encoding="utf-8")
    for label in ("Dashboard", "Model Manager", "Agent Workspace", "Session Manager", "Tool Registry", "Receipt & Replay", "Deployment"):
        assert label in text


def test_cli_status_and_chat(capsys):
    from hhs_runtime.pass153.cli import main
    assert main(["status"]) == 0
    assert "HHS_PASS153_AGENT_ENVIRONMENT_STATUS_V1" in capsys.readouterr().out
    assert main(["chat", "HHS", "--max-tokens", "4"]) == 0
    assert "ADVISORY_MODEL_OUTPUT_VALIDATED" in capsys.readouterr().out


def test_release_builder_produces_matching_commitment(tmp_path, monkeypatch):
    from tools.pass153 import build_release
    monkeypatch.setattr(build_release, "OUT", tmp_path / "dist")
    release = build_release.build()
    assert release["release_root"]["product_root_sha256"]
    assert (build_release.OUT / release["full_inherited_zip"]["path"]).is_file()
    assert (build_release.OUT / release["huggingface_zip"]["path"]).is_file()
    product_root = json.loads((build_release.OUT / "full_inherited_nucleus/HHS_PASS_153_RELEASE_ROOT.json").read_text())
    hf_root = json.loads((build_release.OUT / "huggingface_space/HHS_PASS_153_RELEASE_ROOT.json").read_text())
    assert product_root == hf_root


def test_deployment_surfaces_are_complete():
    root = Path(__file__).resolve().parents[2]
    required = [
        "deployment/pass153/Dockerfile",
        "deployment/pass153/docker-compose.yml",
        "deployment/pass153/start.sh",
        "deployment/pass153/huggingface/README.md",
        "deployment/pass153/huggingface/Dockerfile",
        "sdk/python/hhs_pass153_client.py",
        "hhs_backend/pass153_server.py",
    ]
    assert all((root / path).is_file() for path in required)
