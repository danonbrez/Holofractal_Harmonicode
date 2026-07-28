from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
import importlib
import json
import time
import uuid

from python.hhs_gfcc.core import inherited_hash72, inherited_hash216

CONTRACT_ID = "HHS-P153-LITERT-OPEN-MODEL-AGENT"
PASS_NUMBER = 153
TERMINAL_CLASSIFICATION = "HHS_PASS_153_LITERT_OPEN_MODEL_AGENT_ENVIRONMENT_VERIFIED"
GENESIS_RECEIPT = "H72-P153-GENESIS"


class Pass153Error(ValueError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


def canonical(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    elif hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def hash72(value: Any) -> str:
    return inherited_hash72(canonical_bytes(value))


def hash216(value: Any) -> str:
    return inherited_hash216(canonical_bytes(value))


class ModelBackend(Protocol):
    def generate(self, prompt: str, *, max_tokens: int = 64) -> str: ...


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    backend: str
    source: str
    context_tokens: int
    capabilities: tuple[str, ...] = ("text-generation",)
    generation: int = 0
    model_index: str = ""

    def __post_init__(self) -> None:
        if not self.model_id or not self.backend or self.context_tokens <= 0:
            raise Pass153Error("P153_INVALID_MODEL_SPEC", "model identity, backend, and positive context are required")
        payload = {"domain": "HHS-P153-MODEL-SPEC-V1", "model_id": self.model_id, "backend": self.backend, "source": self.source, "context_tokens": self.context_tokens, "capabilities": list(self.capabilities), "generation": self.generation}
        expected = hash216(payload)
        if self.model_index and self.model_index != expected:
            raise Pass153Error("P153_MODEL_INDEX_MISMATCH", "model index does not match canonical specification")
        object.__setattr__(self, "model_index", expected)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReferenceOpenModel:
    def __init__(self, weights: Mapping[str, list[str]], *, seed_phrase: str = "hhs") -> None:
        self.weights = {str(k).lower(): tuple(str(x) for x in v) for k, v in weights.items()}
        self.seed_phrase = seed_phrase

    @classmethod
    def from_file(cls, path: str | Path) -> "ReferenceOpenModel":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(payload["transitions"], seed_phrase=payload.get("seed_phrase", "hhs"))

    def generate(self, prompt: str, *, max_tokens: int = 64) -> str:
        if max_tokens <= 0 or max_tokens > 512:
            raise Pass153Error("P153_INVALID_MAX_TOKENS", "max_tokens must be in 1..512")
        tokens = [token.strip(".,:;!?()[]{}\"'").lower() for token in prompt.split() if token.strip()]
        current = tokens[-1] if tokens else self.seed_phrase
        out: list[str] = []
        for step in range(max_tokens):
            options = self.weights.get(current) or self.weights.get("*") or (self.seed_phrase,)
            choice = options[hash72({"prompt": prompt, "step": step, "current": current})[0].encode("utf-8")[0] % len(options)]
            out.append(choice)
            current = choice.lower()
            if choice.endswith("."):
                break
        return " ".join(out)


def resolve_litert_interpreter_factory() -> Callable[..., Any]:
    candidates = (("ai_edge_litert.interpreter", "Interpreter"), ("ai_edge_litert", "Interpreter"), ("tflite_runtime.interpreter", "Interpreter"))
    errors: list[str] = []
    for module_name, symbol in candidates:
        try:
            module = importlib.import_module(module_name)
            return getattr(module, symbol)
        except Exception as exc:
            errors.append(f"{module_name}:{type(exc).__name__}")
    raise Pass153Error("P153_LITERT_UNAVAILABLE", "no supported LiteRT interpreter package is installed", {"attempts": errors})


class LiteRTModelAdapter:
    def __init__(self, model_path: str | Path, *, input_encoder: Callable[[str, list[dict[str, Any]]], Any], output_decoder: Callable[[Any, list[dict[str, Any]]], str], interpreter_factory: Callable[..., Any] | None = None) -> None:
        self.model_path = str(model_path)
        self.input_encoder = input_encoder
        self.output_decoder = output_decoder
        factory = interpreter_factory or resolve_litert_interpreter_factory()
        self.interpreter = factory(model_path=self.model_path)
        self.interpreter.allocate_tensors()
        self.inputs = list(self.interpreter.get_input_details())
        self.outputs = list(self.interpreter.get_output_details())
        if not self.inputs or not self.outputs:
            raise Pass153Error("P153_LITERT_TENSOR_CONTRACT", "LiteRT model must expose input and output tensors")

    def generate(self, prompt: str, *, max_tokens: int = 64) -> str:
        encoded = self.input_encoder(prompt, self.inputs)
        if isinstance(encoded, Mapping):
            for detail in self.inputs:
                name = detail.get("name")
                if name not in encoded:
                    raise Pass153Error("P153_LITERT_INPUT_MISSING", "encoder omitted a required input", {"name": name})
                self.interpreter.set_tensor(detail["index"], encoded[name])
        elif len(self.inputs) == 1:
            self.interpreter.set_tensor(self.inputs[0]["index"], encoded)
        else:
            raise Pass153Error("P153_LITERT_INPUT_AMBIGUOUS", "multi-input model requires a mapping encoder")
        self.interpreter.invoke()
        raw = [self.interpreter.get_tensor(detail["index"]) for detail in self.outputs]
        text = self.output_decoder(raw, self.outputs)
        if not isinstance(text, str) or not text.strip():
            raise Pass153Error("P153_LITERT_EMPTY_OUTPUT", "decoder must return non-empty text")
        return text[: max(1, max_tokens * 32)]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    mutating: bool = False
    required_capability: str = "read"


@dataclass
class Session:
    session_id: str
    model_id: str
    created_at: int
    receipt_head: str = GENESIS_RECEIPT
    messages: list[dict[str, Any]] = field(default_factory=list)
    status: str = "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        return canonical(asdict(self))


class AgentEnvironment:
    def __init__(self, *, output_validator: Callable[[str], bool] | None = None, tool_authorizer: Callable[[ToolSpec, Mapping[str, Any]], bool] | None = None) -> None:
        self.models: dict[str, tuple[ModelSpec, ModelBackend]] = {}
        self.tools: dict[str, tuple[ToolSpec, Callable[[Mapping[str, Any]], Any]]] = {}
        self.sessions: dict[str, Session] = {}
        self.output_validator = output_validator or (lambda text: bool(text.strip()))
        self.tool_authorizer = tool_authorizer or (lambda spec, args: not spec.mutating)

    def register_model(self, spec: ModelSpec, backend: ModelBackend) -> ModelSpec:
        if spec.model_id in self.models and self.models[spec.model_id][0].generation >= spec.generation:
            raise Pass153Error("P153_STALE_MODEL_GENERATION", "model generation must advance")
        self.models[spec.model_id] = (spec, backend)
        return spec

    def register_tool(self, spec: ToolSpec, handler: Callable[[Mapping[str, Any]], Any]) -> ToolSpec:
        if not spec.name or spec.name in self.tools:
            raise Pass153Error("P153_DUPLICATE_TOOL", "tool names must be unique and non-empty")
        self.tools[spec.name] = (spec, handler)
        return spec

    def create_session(self, model_id: str, *, session_id: str | None = None) -> Session:
        if model_id not in self.models:
            raise Pass153Error("P153_MODEL_NOT_FOUND", "requested model is not registered", {"model_id": model_id})
        sid = session_id or str(uuid.uuid4())
        if sid in self.sessions:
            raise Pass153Error("P153_DUPLICATE_SESSION", "session already exists")
        session = Session(sid, model_id, int(time.time()))
        self.sessions[sid] = session
        return session

    def invoke_tool(self, session_id: str, name: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        session = self._session(session_id)
        if name not in self.tools:
            raise Pass153Error("P153_TOOL_NOT_FOUND", "tool is not registered", {"tool": name})
        spec, handler = self.tools[name]
        if not self.tool_authorizer(spec, arguments):
            raise Pass153Error("P153_TOOL_UNAUTHORIZED", "tool invocation was rejected by capability policy", {"tool": name})
        result = canonical(handler(arguments))
        receipt = hash72({"domain": "HHS-P153-TOOL-RECEIPT-V1", "parent": session.receipt_head, "tool": spec.name, "arguments": arguments, "result": result})
        session.receipt_head = receipt
        session.messages.append({"role": "tool", "tool": name, "arguments": canonical(arguments), "result": result, "receipt": receipt})
        return {"status": "TOOL_RESULT_VALIDATED", "authoritative": False, "result": result, "receipt": receipt}

    def chat(self, session_id: str, prompt: str, *, max_tokens: int = 64) -> dict[str, Any]:
        session = self._session(session_id)
        if session.status != "ACTIVE":
            raise Pass153Error("P153_SESSION_NOT_ACTIVE", "session is not active")
        if not isinstance(prompt, str) or not prompt.strip():
            raise Pass153Error("P153_EMPTY_PROMPT", "prompt must be non-empty")
        spec, backend = self.models[session.model_id]
        draft = backend.generate(prompt, max_tokens=max_tokens)
        if not self.output_validator(draft):
            raise Pass153Error("P153_OUTPUT_REJECTED", "model output failed the HHS validation boundary")
        event = {"domain": "HHS-P153-AGENT-TURN-V1", "parent": session.receipt_head, "session": session.session_id, "model_index": spec.model_index, "prompt": prompt, "draft": draft, "validated": True}
        receipt = hash72(event)
        session.receipt_head = receipt
        session.messages.extend(({"role": "user", "content": prompt}, {"role": "assistant", "content": draft, "validated": True, "authoritative": False, "receipt": receipt}))
        return {"status": "ADVISORY_MODEL_OUTPUT_VALIDATED", "authoritative": False, "validated": True, "session_id": session.session_id, "model_id": spec.model_id, "model_index": spec.model_index, "content": draft, "receipt": receipt}

    def replay_session(self, session_id: str) -> dict[str, Any]:
        session = self._session(session_id)
        parent = GENESIS_RECEIPT
        turn_receipts: list[str] = []
        last_user = ""
        for message in session.messages:
            if message.get("role") == "user":
                last_user = message["content"]
            elif message.get("role") == "assistant":
                spec = self.models[session.model_id][0]
                parent = hash72({"domain": "HHS-P153-AGENT-TURN-V1", "parent": parent, "session": session.session_id, "model_index": spec.model_index, "prompt": last_user, "draft": message["content"], "validated": True})
                turn_receipts.append(parent)
            elif message.get("role") == "tool":
                parent = hash72({"domain": "HHS-P153-TOOL-RECEIPT-V1", "parent": parent, "tool": message["tool"], "arguments": message["arguments"], "result": message["result"]})
                turn_receipts.append(parent)
        return {"status": "MATCH" if parent == session.receipt_head else "DIVERGED", "receipt_head": parent, "turn_receipts": turn_receipts}

    def status(self) -> dict[str, Any]:
        return {"schema": "HHS_PASS153_AGENT_ENVIRONMENT_STATUS_V1", "contract_id": CONTRACT_ID, "pass_number": PASS_NUMBER, "models": [spec.to_dict() for spec, _ in sorted(self.models.values(), key=lambda pair: pair[0].model_id)], "tools": [asdict(spec) for spec, _ in sorted(self.tools.values(), key=lambda pair: pair[0].name)], "sessions": [session.to_dict() for session in sorted(self.sessions.values(), key=lambda item: item.session_id)], "authority": {"model_output": "ADVISORY_ONLY", "tools": "CAPABILITY_GATED", "runtime_state": "VM81_ONLY", "receipts": "HASH72"}}

    def _session(self, session_id: str) -> Session:
        try:
            return self.sessions[session_id]
        except KeyError as exc:
            raise Pass153Error("P153_SESSION_NOT_FOUND", "session does not exist", {"session_id": session_id}) from exc


def build_default_environment(weights_path: str | Path | None = None) -> AgentEnvironment:
    path = Path(weights_path) if weights_path else Path(__file__).with_name("reference_model.json")
    env = AgentEnvironment()
    env.register_model(ModelSpec("hhs-reference-open-model-v1", "reference-ngram", "hhs_runtime/pass153/reference_model.json", 2048), ReferenceOpenModel.from_file(path))
    env.register_tool(ToolSpec("status", "Return the governed agent environment status", mutating=False), lambda _args: {"status": "online", "pass": 153})
    env.register_tool(ToolSpec("echo", "Return a canonical echo payload", mutating=False), lambda args: {"echo": canonical(args)})
    return env
