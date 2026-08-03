"""Disposable execution worker for the Pass 204 safe open cloud computer."""
from __future__ import annotations

import asyncio
import base64
import contextlib
import dataclasses
import importlib
import inspect
import io
import json
import os
import resource
import sys
import tempfile
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, get_args, get_origin, get_type_hints

MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_MEMORY_BYTES = 768 * 1024 * 1024
MAX_CPU_SECONDS = 60
MAX_CAPTURE_CHARS = 64 * 1024


class SandboxBoundaryError(RuntimeError):
    pass


def _safe(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _safe(dataclasses.asdict(value))
    if isinstance(value, Enum):
        return _safe(value.value)
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, bytes):
        return {"encoding": "base64", "data": base64.b64encode(value).decode("ascii")}
    if isinstance(value, Mapping):
        return {str(key): _safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, bool, float)):
        return value
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _safe(value.to_dict())
    if hasattr(value, "snapshot") and callable(value.snapshot):
        return _safe(value.snapshot())
    return str(value)


def _coerce(value: Any, annotation: Any, sandbox_root: Path) -> Any:
    if annotation is inspect.Signature.empty or annotation is Any or annotation is None:
        return value
    origin = get_origin(annotation)
    arguments = get_args(annotation)
    if origin is not None:
        if origin in (list, tuple, set, frozenset):
            item_type = arguments[0] if arguments else Any
            values = [_coerce(item, item_type, sandbox_root) for item in (value or [])]
            if origin is tuple:
                return tuple(values)
            if origin is set:
                return set(values)
            if origin is frozenset:
                return frozenset(values)
            return values
        if origin in (dict, Mapping):
            key_type, item_type = arguments if len(arguments) == 2 else (Any, Any)
            return {
                _coerce(key, key_type, sandbox_root): _coerce(item, item_type, sandbox_root)
                for key, item in dict(value or {}).items()
            }
        if type(None) in arguments:
            if value is None:
                return None
            non_none = next((item for item in arguments if item is not type(None)), Any)
            return _coerce(value, non_none, sandbox_root)
    if annotation is Path:
        candidate = Path(str(value))
        if not candidate.is_absolute():
            candidate = sandbox_root / candidate
        return candidate
    if annotation is Fraction:
        if isinstance(value, Mapping):
            return Fraction(int(value["numerator"]), int(value["denominator"]))
        return Fraction(str(value))
    if annotation is bytes:
        if isinstance(value, Mapping) and value.get("encoding") == "base64":
            return base64.b64decode(str(value.get("data") or ""))
        if isinstance(value, str):
            return value.encode("utf-8")
    if dataclasses.is_dataclass(annotation) and isinstance(value, Mapping):
        return annotation(**dict(value))
    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        return annotation(value)
    if annotation in (str, int, bool, float):
        return annotation(value)
    return value


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _install_audit_boundary(repo_root: Path, sandbox_root: Path) -> None:
    write_flags = {"w", "a", "x", "+"}

    def hook(event: str, args: tuple[Any, ...]) -> None:
        if event in {"socket.connect", "socket.bind", "socket.listen", "socket.getaddrinfo"}:
            raise SandboxBoundaryError("network operation is virtualized and requires a durable continuation")
        if event in {"os.system", "subprocess.Popen", "pty.spawn"}:
            raise SandboxBoundaryError("host process creation is not available to remote sandboxes")
        if event in {"ctypes.dlopen", "ctypes.dlsym"}:
            target = Path(str(args[0])) if args else Path("")
            if not (_inside(target, repo_root) or _inside(target, sandbox_root)):
                raise SandboxBoundaryError("native libraries must be repository or sandbox scoped")
        if event == "open" and args:
            raw_path = args[0]
            if isinstance(raw_path, int):
                return
            path = Path(os.fsdecode(raw_path))
            if not path.is_absolute():
                path = Path.cwd() / path
            mode = str(args[1]) if len(args) > 1 else "r"
            writing = any(flag in mode for flag in write_flags)
            if writing and not _inside(path, sandbox_root):
                raise SandboxBoundaryError("writes are restricted to the ephemeral sandbox")
            if not writing and not (_inside(path, repo_root) or _inside(path, sandbox_root)):
                raise SandboxBoundaryError("reads are restricted to repository and sandbox projections")
        if event in {"os.remove", "os.rmdir", "os.rename", "os.replace", "os.unlink"} and args:
            paths = [Path(os.fsdecode(item)) for item in args[:2] if isinstance(item, (str, bytes, os.PathLike))]
            if any(not _inside(path if path.is_absolute() else Path.cwd() / path, sandbox_root) for path in paths):
                raise SandboxBoundaryError("destructive operations are restricted to the ephemeral sandbox")

    sys.addaudithook(hook)


def _apply_limits() -> None:
    for target, value in (
        (resource.RLIMIT_CPU, MAX_CPU_SECONDS),
        (resource.RLIMIT_AS, MAX_MEMORY_BYTES),
        (resource.RLIMIT_NOFILE, 96),
        (resource.RLIMIT_NPROC, 32),
    ):
        try:
            resource.setrlimit(target, (value, value))
        except Exception:
            pass


def _bind_call(function: Any, supplied: Mapping[str, Any], sandbox_root: Path) -> tuple[list[Any], dict[str, Any]]:
    signature = inspect.signature(function)
    try:
        hints = get_type_hints(function)
    except Exception:
        hints = {}
    explicit_args = list(supplied.get("__args__") or []) if "__args__" in supplied else []
    explicit_kwargs = dict(supplied.get("__kwargs__") or {}) if "__kwargs__" in supplied else {}
    named = {key: value for key, value in supplied.items() if key not in {"__args__", "__kwargs__"}}
    explicit_kwargs.update(named)
    positional: list[Any] = []
    keywords: dict[str, Any] = {}
    explicit_index = 0
    has_var_keyword = any(parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values())
    accepted_names = set(signature.parameters)
    unknown = set(explicit_kwargs) - accepted_names
    if unknown and not has_var_keyword:
        raise TypeError(f"unknown arguments: {sorted(unknown)}")

    for name, parameter in signature.parameters.items():
        annotation = hints.get(name, parameter.annotation)
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            while explicit_index < len(explicit_args):
                positional.append(_coerce(explicit_args[explicit_index], annotation, sandbox_root))
                explicit_index += 1
            continue
        if parameter.kind is inspect.Parameter.VAR_KEYWORD:
            for key in list(explicit_kwargs):
                if key not in accepted_names:
                    keywords[key] = explicit_kwargs.pop(key)
            continue
        present = name in explicit_kwargs
        if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
            if explicit_index < len(explicit_args):
                positional.append(_coerce(explicit_args[explicit_index], annotation, sandbox_root))
                explicit_index += 1
            elif present:
                positional.append(_coerce(explicit_kwargs.pop(name), annotation, sandbox_root))
            elif parameter.default is inspect.Signature.empty:
                raise TypeError(f"missing required argument: {name}")
            continue
        if explicit_index < len(explicit_args) and parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
            positional.append(_coerce(explicit_args[explicit_index], annotation, sandbox_root))
            explicit_index += 1
        elif present:
            keywords[name] = _coerce(explicit_kwargs.pop(name), annotation, sandbox_root)
        elif parameter.default is inspect.Signature.empty:
            raise TypeError(f"missing required argument: {name}")
    if explicit_index < len(explicit_args):
        raise TypeError("too many positional arguments")
    return positional, keywords


def _python_execution(function_record: Mapping[str, Any], arguments: Mapping[str, Any], sandbox_root: Path) -> dict[str, Any]:
    module_name = str(function_record["module"])
    qualname = str(function_record["qualname"])
    if "." in qualname or qualname.startswith("_"):
        raise TypeError("only indexed public top-level declarations are executable")
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        module = importlib.import_module(module_name)
        function = getattr(module, qualname)
        if not inspect.isfunction(function):
            raise TypeError("indexed target is not a Python function")
        positional, keywords = _bind_call(function, arguments, sandbox_root)
        result = function(*positional, **keywords)
        if inspect.isawaitable(result):
            result = asyncio.run(result)
    return {
        "execution_status": "COMPLETED",
        "outcome": "PYTHON_DECLARATION_EXECUTED",
        "result": _safe(result),
        "stdout": stdout.getvalue()[-MAX_CAPTURE_CHARS:],
        "stderr": stderr.getvalue()[-MAX_CAPTURE_CHARS:],
    }


def _native_execution(function_record: Mapping[str, Any], arguments: Mapping[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema": "HHS_PASS_204_NATIVE_ABI_CALL_MANIFEST_V1",
        "symbol": function_record.get("symbol"),
        "header": function_record.get("header"),
        "return_type": function_record.get("return_type"),
        "parameters_c": function_record.get("parameters_c"),
        "arguments": _safe(arguments),
        "native_pointer_exposed": False,
        "direct_kernel_access": False,
        "execution_pipeline": ["ABI_PARSE", "VM81_LOWER", "SANDBOX_BUILD", "CALL", "RECEIPT"],
    }
    return {
        "execution_status": "ACCEPTED",
        "outcome": "NATIVE_ABI_BUILD_AND_CALL_ACCEPTED",
        "result": manifest,
    }


def main() -> int:
    _apply_limits()
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        print(json.dumps({"execution_status": "CONTINUATION_REQUIRED", "outcome": "INPUT_REQUIRES_ARTIFACT_INGRESS"}))
        return 0
    request = json.loads(raw or b"{}")
    function_record = dict(request.get("function") or {})
    arguments = dict(request.get("arguments") or {})
    repo_root = Path(str(request.get("repo_root") or Path.cwd())).resolve()
    with tempfile.TemporaryDirectory(prefix="hhs-pass204-") as temporary:
        sandbox_root = Path(temporary).resolve()
        (sandbox_root / "home").mkdir()
        (sandbox_root / "workspace").mkdir()
        (sandbox_root / "artifacts").mkdir()
        os.environ.clear()
        os.environ.update(
            {
                "PATH": "/usr/bin:/bin",
                "PYTHONPATH": str(repo_root),
                "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "HOME": str(sandbox_root / "home"),
                "TMPDIR": str(sandbox_root),
                "HHS_PASS204_SANDBOX": "1",
            }
        )
        os.chdir(sandbox_root / "workspace")
        _install_audit_boundary(repo_root, sandbox_root)
        try:
            kind = str(function_record.get("kind") or "")
            if kind == "PYTHON_FUNCTION":
                response = _python_execution(function_record, arguments, sandbox_root)
            elif kind == "NATIVE_ABI":
                response = _native_execution(function_record, arguments)
            else:
                response = {
                    "execution_status": "CONTINUATION_REQUIRED",
                    "outcome": "GOVERNED_ADAPTER_REQUIRED",
                    "continuation": {"kind": kind},
                }
        except (TypeError, ValueError, KeyError) as exc:
            response = {
                "execution_status": "INVALID_CALL",
                "outcome": "ARGUMENT_VALIDATION_REJECTED",
                "invalid_call": True,
                "reason": f"{exc.__class__.__name__}: {exc}",
            }
        except Exception as exc:
            response = {
                "execution_status": "CONTINUATION_REQUIRED",
                "outcome": "SANDBOX_CONTINUATION_CAPTURED",
                "continuation": {
                    "exception_class": exc.__class__.__name__,
                    "reason": str(exc),
                    "sandbox_boundary": isinstance(exc, SandboxBoundaryError),
                },
            }
        response.update(
            {
                "ok": True,
                "sandbox_disposed": True,
                "persistent_capabilities": False,
                "direct_kernel_access": False,
                "internal_policy_mutable": False,
            }
        )
        encoded = json.dumps(response, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        maximum = int(request.get("maximum_result_bytes") or 0)
        if maximum and len(encoded.encode("utf-8")) > maximum:
            response = {
                "ok": True,
                "execution_status": "CONTINUATION_REQUIRED",
                "outcome": "RESULT_REQUIRES_ARTIFACT_EGRESS",
                "sandbox_disposed": True,
                "persistent_capabilities": False,
                "direct_kernel_access": False,
            }
            encoded = json.dumps(response, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        print(encoded)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
