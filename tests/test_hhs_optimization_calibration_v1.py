from __future__ import annotations

import ast
from pathlib import Path

import hhs_backend.runtime.hhs_pass207_vm81_gpu_runtime_v1 as pass207
from hhs_backend.runtime.hhs_optimization_calibration_v1 import (
    CALIBRATION_CONTINUATION_SEEDS,
    CALIBRATION_CONTINUATION_TICKS,
    CALIBRATION_VECTOR_OBJECTS,
    CALIBRATION_VECTOR_QUERY_LIMIT,
    PASS205_RETRIEVAL_TOP_K,
    PASS207_CACHE_BYTES,
    PASS207_CACHE_ENTRIES,
    PASS208_MAX_BRANCHES,
    calibrated_profile,
)
from hhs_backend.runtime.hhs_pass208_gpu_branch_manifold_v1 import (
    Pass208GPUBranchManifold,
)

ROOT = Path(__file__).resolve().parents[1]


def _source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _function_kw_default(source: str, function_name: str, keyword: str) -> int:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            args = node.args.args + node.args.kwonlyargs
            defaults = [None] * (len(node.args.args) - len(node.args.defaults))
            defaults.extend(node.args.defaults)
            defaults.extend(node.args.kw_defaults)
            mapping = {argument.arg: default for argument, default in zip(args, defaults)}
            value = mapping[keyword]
            if not isinstance(value, ast.Constant) or type(value.value) is not int:
                raise AssertionError(f"{function_name}.{keyword} is not an exact integer literal")
            return value.value
    raise AssertionError(f"function {function_name} not found")


def test_recovered_calibration_profile_is_exact_integer_only() -> None:
    profile = calibrated_profile()
    assert profile["authoritative_float_allowed"] is False
    assert PASS205_RETRIEVAL_TOP_K == 32
    assert PASS207_CACHE_BYTES == 536_870_912
    assert PASS207_CACHE_ENTRIES == 512
    assert PASS208_MAX_BRANCHES == 256
    assert CALIBRATION_VECTOR_OBJECTS == 2048
    assert CALIBRATION_VECTOR_QUERY_LIMIT == 512
    assert CALIBRATION_CONTINUATION_TICKS == 360
    assert CALIBRATION_CONTINUATION_SEEDS == (
        1, 5, 7, 41, 64, 72, 81, 144, 216, 243, 5040, 5184, 1259713
    )
    for key, value in profile.items():
        if key in {"schema", "classification", "legacy_advisory_only_modules"}:
            continue
        if key == "authoritative_float_allowed":
            assert value is False
            continue
        if key == "calibration_continuation_seeds":
            assert all(type(item) is int for item in value)
            continue
        assert type(value) is int


def test_pass207_direct_runtime_restores_calibrated_cache_defaults(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeTranslation:
        pass

    class FakeDriver:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        def close(self) -> None:
            pass

        def status(self) -> dict[str, object]:
            return {}

    monkeypatch.delenv("HHS_PASS207_CACHE_BYTES", raising=False)
    monkeypatch.delenv("HHS_PASS207_CACHE_ENTRIES", raising=False)
    monkeypatch.setattr(pass207, "Pass205AcceleratorTranslation", FakeTranslation)
    monkeypatch.setattr(pass207, "Pass207GPUDriver", FakeDriver)

    runtime = pass207.Pass207VM81GPURuntime(backend="CPU_REFERENCE")
    try:
        assert captured["cache_capacity_bytes"] == PASS207_CACHE_BYTES
        assert captured["cache_capacity_entries"] == PASS207_CACHE_ENTRIES
        assert captured["verify_against_cpu"] is True
    finally:
        runtime.close()


def test_pass207_environment_override_remains_exact_integer(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeTranslation:
        pass

    class FakeDriver:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        def close(self) -> None:
            pass

        def status(self) -> dict[str, object]:
            return {}

    monkeypatch.setenv("HHS_PASS207_CACHE_BYTES", "1048576")
    monkeypatch.setenv("HHS_PASS207_CACHE_ENTRIES", "64")
    monkeypatch.setattr(pass207, "Pass205AcceleratorTranslation", FakeTranslation)
    monkeypatch.setattr(pass207, "Pass207GPUDriver", FakeDriver)

    runtime = pass207.Pass207VM81GPURuntime(backend="CPU_REFERENCE")
    try:
        assert captured["cache_capacity_bytes"] == 1_048_576
        assert captured["cache_capacity_entries"] == 64
        assert type(captured["cache_capacity_bytes"]) is int
        assert type(captured["cache_capacity_entries"]) is int
    finally:
        runtime.close()


def test_pass208_defaults_share_the_same_calibration_profile(monkeypatch) -> None:
    for name in (
        "HHS_PASS208_MAX_BRANCHES",
        "HHS_PASS207_CACHE_BYTES",
        "HHS_PASS207_CACHE_ENTRIES",
    ):
        monkeypatch.delenv(name, raising=False)
    manifold = Pass208GPUBranchManifold(enabled=False)
    assert manifold.max_branches == PASS208_MAX_BRANCHES
    assert manifold.cache_capacity_bytes == PASS207_CACHE_BYTES
    assert manifold.cache_capacity_entries == PASS207_CACHE_ENTRIES


def test_pass205_retrieval_default_remains_calibrated_32() -> None:
    source = _source("hhs_backend/runtime/hhs_pass205_continuation_runtime_v1.py")
    assert _function_kw_default(source, "retrieve", "top_k") == PASS205_RETRIEVAL_TOP_K
    assert _function_kw_default(source, "hydrate_target", "top_k") == PASS205_RETRIEVAL_TOP_K
    api_source = _source("hhs_backend/api/pass205_continuation_routes.py")
    assert "top_k: int = Field(default=32, ge=1, le=1024)" in api_source


def test_deployment_defaults_match_the_recovered_profile() -> None:
    env_text = _source("deployment/digitalocean/gpu/pass208-gpu.env.example")
    install_text = _source("deployment/digitalocean/gpu/install.sh")
    assert f"HHS_PASS208_MAX_BRANCHES={PASS208_MAX_BRANCHES}" in env_text
    assert f"HHS_PASS207_CACHE_BYTES={PASS207_CACHE_BYTES}" in env_text
    assert f"HHS_PASS207_CACHE_ENTRIES={PASS207_CACHE_ENTRIES}" in env_text
    assert f'HHS_PASS208_MAX_BRANCHES:-{PASS208_MAX_BRANCHES}' in install_text
    assert f'HHS_PASS207_CACHE_BYTES:-{PASS207_CACHE_BYTES}' in install_text
    assert f'HHS_PASS207_CACHE_ENTRIES:-{PASS207_CACHE_ENTRIES}' in install_text


def test_authoritative_optimization_modules_have_no_float_literals_or_legacy_float_imports() -> None:
    authoritative_paths = (
        "hhs_backend/runtime/hhs_optimization_calibration_v1.py",
        "hhs_backend/runtime/hhs_pass207_vm81_gpu_runtime_v1.py",
        "hhs_backend/runtime/hhs_pass208_gpu_branch_manifold_v1.py",
    )
    legacy_markers = (
        "hhs_receipt_vector_index_v1",
        "hhs_receipt_vector_cache_v1",
        "hhs_predictive_sandbox_engine_v1",
    )
    for path in authoritative_paths:
        source = _source(path)
        tree = ast.parse(source)
        assert not any(
            isinstance(node, ast.Constant) and type(node.value) is float
            for node in ast.walk(tree)
        ), path
        for marker in legacy_markers:
            assert marker not in source, (path, marker)
