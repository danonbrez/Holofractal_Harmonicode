from __future__ import annotations

from pathlib import Path

import pytest

from tools.verify_litert_lm_dependency_closure import (
    DependencyClosureError,
    verify_default_runtime_closure,
)


def write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_commented_litert_install_example_is_not_an_active_dependency(tmp_path: Path):
    requirements = write(
        tmp_path / "requirements.txt",
        "# The official LiteRT-LM package is optional.\n"
        "#   python -m pip install -r requirements-litert-lm.txt\n"
        "fastapi==0.128.2\n",
    )

    visited = verify_default_runtime_closure(requirements)

    assert visited == (requirements.resolve(),)


def test_direct_litert_package_is_rejected(tmp_path: Path):
    requirements = write(
        tmp_path / "requirements.txt",
        "fastapi==0.128.2\n"
        "litert-lm==0.14.0\n",
    )

    with pytest.raises(DependencyClosureError, match="external LiteRT-LM"):
        verify_default_runtime_closure(requirements)


def test_active_litert_requirements_include_is_rejected(tmp_path: Path):
    write(tmp_path / "requirements-litert-lm.txt", "litert-lm==0.14.0\n")
    requirements = write(
        tmp_path / "requirements.txt",
        "-r requirements-litert-lm.txt\n",
    )

    with pytest.raises(DependencyClosureError, match="external LiteRT-LM"):
        verify_default_runtime_closure(requirements)


def test_nested_long_form_requirements_include_is_checked(tmp_path: Path):
    write(tmp_path / "requirements-litert-lm.txt", "litert_lm>=0.14.0\n")
    write(
        tmp_path / "runtime-extra.txt",
        "--requirement requirements-litert-lm.txt\n",
    )
    requirements = write(
        tmp_path / "requirements.txt",
        "--requirement=runtime-extra.txt\n",
    )

    with pytest.raises(DependencyClosureError, match="external LiteRT-LM"):
        verify_default_runtime_closure(requirements)


def test_non_litert_nested_requirements_closure_passes(tmp_path: Path):
    write(tmp_path / "runtime-extra.txt", "uvicorn>=0.30\n")
    requirements = write(
        tmp_path / "requirements.txt",
        "-r runtime-extra.txt  # active nested runtime requirements\n",
    )

    visited = verify_default_runtime_closure(requirements)

    assert set(visited) == {
        requirements.resolve(),
        (tmp_path / "runtime-extra.txt").resolve(),
    }


def test_remote_requirements_include_fails_closed(tmp_path: Path):
    requirements = write(
        tmp_path / "requirements.txt",
        "-r https://example.invalid/runtime.txt\n",
    )

    with pytest.raises(DependencyClosureError, match="remote requirements include"):
        verify_default_runtime_closure(requirements)
