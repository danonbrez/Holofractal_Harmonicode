"""Isolated bounded Python function worker for Pass 203."""
from __future__ import annotations

import asyncio
import base64
import dataclasses
import importlib
import inspect
import json
import resource
import sys
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, get_args, get_origin

MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_MEMORY_BYTES = 512 * 1024 * 1024
MAX_CPU_SECONDS = 30


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
    return str(value)


def _coerce(value: Any, annotation: Any) -> Any:
    if annotation is inspect.Signature.empty or annotation is Any:
        return value
    origin = get_origin(annotation)
    arguments = get_args(annotation)
    if origin is not None:
        if origin in (list, tuple, set, frozenset):
            item_type = arguments[0] if arguments else Any
            values = [_coerce(item, item_type) for item in (value or [])]
            if origin is tuple:
                return tuple(values)
            if origin is set:
                return set(values)
            if origin is frozenset:
                return frozenset(values)
            return values
        if origin in (dict, Mapping):
            key_type, item_type = arguments if len(arguments) == 2 else (Any, Any)
            return {_coerce(key, key_type): _coerce(item, item_type) for key, item in dict(value or {}).items()}
        if type(None) in arguments:
            if value is None:
                return None
            non_none = next((item for item in arguments if item is not type(None)), Any)
            return _coerce(value, non_none)
    if annotation is Path:
        return Path(str(value))
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


def _apply_limits() -> None:
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (MAX_CPU_SECONDS, MAX_CPU_SECONDS))
    except Exception:
        pass
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_BYTES, MAX_MEMORY_BYTES))
    except Exception:
        pass
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    except Exception:
        pass


def main() -> int:
    _apply_limits()
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        print(json.dumps({"ok": False, "error": "input exceeds worker limit"}))
        return 2
    try:
        request = json.loads(raw or b"{}")
        module_name = str(request["module"])
        qualname = str(request["qualname"])
        allowed = tuple(str(item) for item in request.get("allowed_module_prefixes") or [])
        if not allowed or not module_name.startswith(allowed):
            raise ValueError("module is not permitted")
        if "." in qualname or qualname.startswith("_"):
            raise ValueError("only public top-level functions are permitted")
        module = importlib.import_module(module_name)
        function = getattr(module, qualname)
        if not inspect.isfunction(function):
            raise TypeError("target is not a Python function")
        signature = inspect.signature(function)
        supplied = dict(request.get("arguments") or {})
        unknown = set(supplied) - set(signature.parameters)
        if unknown:
            raise TypeError(f"unknown arguments: {sorted(unknown)}")
        kwargs = {}
        for name, parameter in signature.parameters.items():
            if name in supplied:
                kwargs[name] = _coerce(supplied[name], parameter.annotation)
            elif parameter.default is inspect.Signature.empty:
                raise TypeError(f"missing required argument: {name}")
        result = function(**kwargs)
        if inspect.isawaitable(result):
            result = asyncio.run(result)
        payload = {"ok": True, "result": _safe(result)}
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        maximum = int(request.get("maximum_result_bytes") or 0)
        if maximum and len(encoded.encode("utf-8")) > maximum:
            raise ValueError("result exceeds worker limit")
        print(encoded)
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"{exc.__class__.__name__}: {exc}"}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
