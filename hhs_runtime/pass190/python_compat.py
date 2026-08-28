"""Pass 190 classified Python compatibility census.

The Pass 190 contract requires a one-to-one public-callable census, not a
fiction that every standard-library callable is already native. This module
therefore classifies every public callable in the pinned coverage nucleus.
Only identities with an existing canonical Pass 190 operation are marked
executable. Security-sensitive, nondeterministic, platform-conditional, and
unmapped callables remain explicit records with reasons.

The generated census is deterministic for the pinned Python runtime and is
used by CI to produce a reviewable registry artifact.
"""
from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import platform
import sys
from typing import Any, Iterable, Mapping

PYTHON_COMPAT_SCHEMA = "HHS_PYTHON_COMPATIBILITY_OPERATION_REGISTRY_V1"
PYTHON_COMPAT_VERSION = "3.12"

COVERAGE_MODULES = (
    "builtins",
    "collections",
    "collections.abc",
    "itertools",
    "functools",
    "operator",
    "math",
    "cmath",
    "fractions",
    "decimal",
    "statistics",
    "json",
    "csv",
    "base64",
    "binascii",
    "hashlib",
    "hmac",
    "re",
    "pathlib",
    "os",
    "os.path",
    "shutil",
    "io",
    "tempfile",
    "subprocess",
    "threading",
    "queue",
    "concurrent.futures",
    "multiprocessing",
    "asyncio",
    "datetime",
    "time",
    "calendar",
    "typing",
    "dataclasses",
    "enum",
    "logging",
    "argparse",
    "unittest",
    "contextlib",
    "copy",
    "pickle",
    "struct",
    "socket",
    "urllib.parse",
    "http",
    "email",
    "zipfile",
    "tarfile",
)

CLASSIFICATIONS = (
    "CANONICAL_NATIVE",
    "COMPATIBILITY_NATIVE",
    "DELEGATED_PYTHON",
    "ADAPTER_REQUIRED",
    "UNSUPPORTED_WITH_REASON",
    "SECURITY_RESTRICTED",
    "NONDETERMINISTIC",
    "PLATFORM_CONDITIONAL",
)

EXECUTABLE_MAPPINGS: dict[str, tuple[str, str]] = {
    "builtins.len": ("python.len", "Len"),
    "builtins.abs": ("python.abs", "Abs"),
    "builtins.sorted": ("python.sorted", "Sorted"),
    "builtins.str.join": ("text.join", "Join"),
    "builtins.dict.get": ("dict.get", "Get"),
    "math.gcd": ("math.gcd", "GCD"),
}

_SECURITY_IDENTITIES = {
    "builtins.eval",
    "builtins.exec",
    "builtins.compile",
    "builtins.open",
    "os.system",
    "os.popen",
    "pickle.load",
    "pickle.loads",
    "subprocess.Popen",
    "subprocess.run",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "socket.socket",
    "socket.create_connection",
}

_SECURITY_MODULES = {
    "subprocess",
    "socket",
    "multiprocessing",
}

_NONDETERMINISTIC_MODULES = {
    "time",
    "datetime",
    "tempfile",
}

_PLATFORM_MODULES = {
    "os",
    "os.path",
    "shutil",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash216(domain: str, payload: Any) -> str:
    body = _canonical({"domain": domain, "payload": payload})
    lanes = []
    for lane in ("minus", "center", "plus"):
        first = hashlib.sha256(lane.encode("ascii") + b"\0" + body).hexdigest()
        second = hashlib.sha256(b"HHS72\0" + lane.encode("ascii") + b"\0" + body).hexdigest()
        lanes.append(first + second[:8])
    value = "".join(lanes)
    if len(value) != 216:
        raise AssertionError("Pass190 compatibility Hash216 must be 216 characters")
    return value


def _safe_signature(value: Any) -> str | None:
    try:
        return str(inspect.signature(value))
    except (TypeError, ValueError):
        return None


def _module_public_names(module: Any) -> tuple[str, ...]:
    exported = getattr(module, "__all__", None)
    if isinstance(exported, (list, tuple)) and all(isinstance(item, str) for item in exported):
        return tuple(sorted(set(exported)))
    return tuple(sorted(name for name in vars(module) if not name.startswith("_")))


def _callable_kind(value: Any) -> str | None:
    if inspect.isclass(value):
        return "class"
    if inspect.iscoroutinefunction(value):
        return "async_function"
    if inspect.isfunction(value) or inspect.isbuiltin(value):
        return "function"
    if inspect.ismethoddescriptor(value) or inspect.isroutine(value):
        return "method"
    return None


def _record_classification(module_name: str, identity: str) -> tuple[str, str]:
    if identity in EXECUTABLE_MAPPINGS:
        return "CANONICAL_NATIVE", "mapped to an existing executable Pass 190 operation"
    if identity in _SECURITY_IDENTITIES or module_name in _SECURITY_MODULES:
        return "SECURITY_RESTRICTED", "requires explicit process/network/deserialization capability policy"
    if module_name in _NONDETERMINISTIC_MODULES:
        return "NONDETERMINISTIC", "depends on environment, wall clock, entropy, or ephemeral resources"
    if module_name in _PLATFORM_MODULES:
        return "PLATFORM_CONDITIONAL", "filesystem or platform semantics require a bounded adapter"
    return "ADAPTER_REQUIRED", "public callable is inventoried but not promoted to canonical execution authority"


def _append_record(
    records: list[dict[str, Any]],
    *,
    module_name: str,
    owner_type: str | None,
    callable_name: str,
    value: Any,
) -> None:
    base_identity = f"{module_name}.{callable_name}" if owner_type is None else f"{module_name}.{owner_type}.{callable_name}"
    classification, reason = _record_classification(module_name, base_identity)
    mapped = EXECUTABLE_MAPPINGS.get(base_identity)
    record = {
        "python_version": PYTHON_COMPAT_VERSION,
        "qualified_python_identity": base_identity,
        "module": module_name,
        "owner_type": owner_type,
        "callable_name": callable_name,
        "call_kind": _callable_kind(value),
        "signature": _safe_signature(value),
        "harmonicode_constructor": mapped[1] if mapped else None,
        "operation_id": mapped[0] if mapped else None,
        "implementation_class": classification,
        "classification_reason": reason,
        "effect_class": "PURE_OR_EXPLICITLY_CLASSIFIED",
        "capability_scope": "public" if mapped else None,
        "determinism_class": (
            "deterministic"
            if mapped
            else ("nondeterministic" if classification == "NONDETERMINISTIC" else "classified")
        ),
        "platform_constraints": [] if classification != "PLATFORM_CONDITIONAL" else [platform.system()],
        "parity_test_ids": (
            [f"P190-PY-{mapped[0]}"] if mapped else []
        ),
        "documentation_reference": f"python:{base_identity}",
    }
    identity = dict(record)
    record["record_hash216"] = _hash216("HHS-P190-PYTHON-COMPAT", identity)
    records.append(record)


def _class_methods(module_name: str, class_name: str, cls: type[Any]) -> Iterable[tuple[str, Any]]:
    for name, value in inspect.getmembers_static(cls):
        if name.startswith("_"):
            continue
        kind = _callable_kind(value)
        if kind is None:
            continue
        yield name, value


def build_python_compatibility_registry(
    *,
    require_pinned_version: bool = True,
) -> dict[str, Any]:
    runtime_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if require_pinned_version and runtime_version != PYTHON_COMPAT_VERSION:
        raise RuntimeError(
            f"HHS_P190_PYTHON_VERSION_DRIFT:{runtime_version}!={PYTHON_COMPAT_VERSION}"
        )

    records: list[dict[str, Any]] = []
    module_status: list[dict[str, Any]] = []
    seen: set[str] = set()

    for module_name in COVERAGE_MODULES:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            module_status.append(
                {
                    "module": module_name,
                    "status": "PLATFORM_CONDITIONAL",
                    "reason": type(exc).__name__,
                }
            )
            continue

        module_status.append({"module": module_name, "status": "IMPORTED"})
        for name in _module_public_names(module):
            try:
                value = inspect.getattr_static(module, name)
            except AttributeError:
                continue
            kind = _callable_kind(value)
            if kind is None:
                continue
            identity = f"{module_name}.{name}"
            if identity not in seen:
                _append_record(
                    records,
                    module_name=module_name,
                    owner_type=None,
                    callable_name=name,
                    value=value,
                )
                seen.add(identity)
            if inspect.isclass(value) and getattr(value, "__module__", None) == module_name:
                for method_name, method in _class_methods(module_name, name, value):
                    method_identity = f"{module_name}.{name}.{method_name}"
                    if method_identity in seen:
                        continue
                    _append_record(
                        records,
                        module_name=module_name,
                        owner_type=name,
                        callable_name=method_name,
                        value=method,
                    )
                    seen.add(method_identity)

    records.sort(key=lambda item: item["qualified_python_identity"])
    counts = {classification: 0 for classification in CLASSIFICATIONS}
    for record in records:
        counts[record["implementation_class"]] += 1

    nucleus = {
        identity: {
            "operation_id": operation_id,
            "harmonicode_constructor": constructor,
        }
        for identity, (operation_id, constructor) in sorted(EXECUTABLE_MAPPINGS.items())
    }
    identity = {
        "schema": PYTHON_COMPAT_SCHEMA,
        "python_version": PYTHON_COMPAT_VERSION,
        "coverage_modules": list(COVERAGE_MODULES),
        "module_status": module_status,
        "records": records,
        "supported_nucleus": nucleus,
        "classification_counts": counts,
    }
    return {
        **identity,
        "registry_hash216": _hash216("HHS-P190-PYTHON-COMPAT-REGISTRY", identity),
    }


def compatibility_summary(registry: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": registry["schema"],
        "python_version": registry["python_version"],
        "coverage_module_count": len(registry["coverage_modules"]),
        "public_callable_record_count": len(registry["records"]),
        "classification_counts": dict(registry["classification_counts"]),
        "supported_nucleus_count": len(registry["supported_nucleus"]),
        "registry_hash216": registry["registry_hash216"],
        "unclassified_public_callables": 0,
    }


__all__ = [
    "PYTHON_COMPAT_SCHEMA",
    "PYTHON_COMPAT_VERSION",
    "COVERAGE_MODULES",
    "CLASSIFICATIONS",
    "EXECUTABLE_MAPPINGS",
    "build_python_compatibility_registry",
    "compatibility_summary",
]
