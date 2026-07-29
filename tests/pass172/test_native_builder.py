from __future__ import annotations

from pathlib import Path
import shutil

import pytest

from hhs_installer.native_builder import NativeBuildError, NativeBuilder, NativeTarget, artifact_names


def test_platform_artifact_names() -> None:
    assert artifact_names("hhs_runtime", system="Linux") == ("libhhs_runtime.so", "")
    assert artifact_names("hhs_runtime", system="Darwin") == ("libhhs_runtime.dylib", "")
    assert artifact_names("hhs_runtime", system="Windows") == ("hhs_runtime.dll", ".exe")


def test_native_builder_compiles_and_verifies_symbol(tmp_path: Path) -> None:
    if not shutil.which("cc") or not (shutil.which("nm") or shutil.which("llvm-nm")):
        pytest.skip("C compiler and symbol inspector required")
    source = tmp_path / "runtime.c"
    source.write_text("int hhs_runtime_version(void) { return 172; }\n", encoding="utf-8")
    builder = NativeBuilder(tmp_path, timeout_seconds=60)
    result = builder.build(
        NativeTarget(
            target_id="test-runtime",
            sources=("runtime.c",),
            include_dirs=(),
            required_symbols=("hhs_runtime_version",),
            artifact_basename="hhs_runtime",
            link_math=False,
        ),
        output_directory=tmp_path / "out",
    )
    assert result.artifact_size > 0
    assert "hhs_runtime_version" in result.exported_symbols
    assert result.build_identity


def test_missing_required_symbol_fails(tmp_path: Path) -> None:
    if not shutil.which("cc") or not (shutil.which("nm") or shutil.which("llvm-nm")):
        pytest.skip("C compiler and symbol inspector required")
    (tmp_path / "runtime.c").write_text("int available(void) { return 1; }\n", encoding="utf-8")
    with pytest.raises(NativeBuildError) as raised:
        NativeBuilder(tmp_path, timeout_seconds=60).build(
            NativeTarget(
                target_id="missing-symbol",
                sources=("runtime.c",),
                include_dirs=(),
                required_symbols=("required_symbol",),
                link_math=False,
            ),
            output_directory=tmp_path / "out",
        )
    assert raised.value.code == "P172_NATIVE_SYMBOL_MISSING"
