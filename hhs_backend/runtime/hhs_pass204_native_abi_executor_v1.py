"""Canonical native ABI execution adapter for Pass 204 sandboxes."""
from __future__ import annotations

import ctypes
import importlib
from typing import Any, Dict, Mapping, Sequence


class NativeBindingUnavailable(RuntimeError):
    pass


class NativeArgumentError(ValueError):
    pass


def _safe_ctypes(value: Any) -> Any:
    if isinstance(value, ctypes.Array):
        if getattr(value, "_type_", None) is ctypes.c_char:
            return bytes(value).rstrip(b"\0").decode("utf-8", errors="replace")
        return [_safe_ctypes(item) for item in value]
    if isinstance(value, ctypes.Structure):
        return {name: _safe_ctypes(getattr(value, name)) for name, *_ in value._fields_}
    if hasattr(value, "value"):
        raw = value.value
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
        return raw
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if value is None or isinstance(value, (str, int, bool, float)):
        return value
    return str(value)


def _populate_structure(instance: ctypes.Structure, value: Mapping[str, Any]) -> None:
    fields = {name: field_type for name, field_type, *_ in instance._fields_}
    unknown = set(value) - set(fields)
    if unknown:
        raise NativeArgumentError(f"unknown structure fields: {sorted(unknown)}")
    for name, raw in value.items():
        field_type = fields[name]
        current = getattr(instance, name)
        if isinstance(current, ctypes.Array):
            values = raw
            if isinstance(raw, str) and getattr(current, "_type_", None) is ctypes.c_char:
                encoded = raw.encode("utf-8")[: len(current) - 1]
                for index, byte in enumerate(encoded):
                    current[index] = bytes([byte])
                continue
            for index, item in enumerate(list(values or [])[: len(current)]):
                current[index] = item
        elif isinstance(current, ctypes.Structure) and isinstance(raw, Mapping):
            _populate_structure(current, raw)
        else:
            setattr(instance, name, raw)


def _scalar_value(argtype: Any, raw: Any) -> Any:
    if argtype is ctypes.c_char_p:
        if raw is None:
            return None
        return str(raw).encode("utf-8")
    if argtype is ctypes.c_void_p:
        if raw in (None, 0):
            return None
        raise NativeArgumentError("raw host pointers are not accepted")
    try:
        return argtype(0 if raw is None else raw)
    except Exception as exc:
        raise NativeArgumentError(f"cannot coerce {raw!r} to {getattr(argtype, '__name__', argtype)}") from exc


def _prepare_argument(argtype: Any, raw: Any) -> tuple[Any, Any]:
    pointed = getattr(argtype, "_type_", None) if isinstance(argtype, type) else None
    is_pointer = isinstance(argtype, type) and issubclass(argtype, ctypes._Pointer)
    if is_pointer:
        instance = pointed()
        if isinstance(instance, ctypes.Structure) and isinstance(raw, Mapping):
            _populate_structure(instance, raw)
        elif isinstance(instance, ctypes.Array) and raw is not None:
            for index, item in enumerate(list(raw)[: len(instance)]):
                instance[index] = item
        elif raw not in (None, {}):
            try:
                instance.value = raw
            except Exception as exc:
                raise NativeArgumentError(f"cannot populate pointer argument {argtype}") from exc
        return ctypes.byref(instance), instance
    value = _scalar_value(argtype, raw)
    return value, value


def execute_core_symbol(symbol: str, arguments: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        bridge = importlib.import_module("hhs_python.runtime.hhs_ctypes_bridge")
    except Exception as exc:
        raise NativeBindingUnavailable(f"canonical ctypes bridge unavailable: {exc.__class__.__name__}: {exc}") from exc
    library = getattr(bridge, "_RUNTIME_LIB", None)
    if library is None or not hasattr(library, symbol):
        raise NativeBindingUnavailable(f"symbol is not loaded by the canonical runtime bridge: {symbol}")
    function = getattr(library, symbol)
    argtypes: Sequence[Any] = list(getattr(function, "argtypes", None) or [])
    supplied = list(arguments.get("__args__") or [])
    if len(supplied) > len(argtypes):
        raise NativeArgumentError(f"expected at most {len(argtypes)} arguments, received {len(supplied)}")
    prepared = []
    retained = []
    for index, argtype in enumerate(argtypes):
        raw = supplied[index] if index < len(supplied) else None
        call_value, retained_value = _prepare_argument(argtype, raw)
        prepared.append(call_value)
        retained.append(retained_value)
    result = function(*prepared)
    return {
        "schema": "HHS_PASS_204_NATIVE_ABI_EXECUTION_V1",
        "symbol": symbol,
        "execution_status": "COMPLETED",
        "outcome": "CANONICAL_CTYPES_ABI_EXECUTED",
        "result": _safe_ctypes(result),
        "arguments_after_call": [_safe_ctypes(item) for item in retained],
        "argument_count": len(argtypes),
        "raw_pointer_exposed": False,
        "canonical_bridge": "hhs_python.runtime.hhs_ctypes_bridge",
    }


__all__ = [
    "NativeArgumentError",
    "NativeBindingUnavailable",
    "execute_core_symbol",
]
