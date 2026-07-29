from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import os
import platform
import re
import shutil
import subprocess
import time

from .canonical import hash216, stable
from .verification import sha256_file


class NativeBuildError(RuntimeError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class NativeTarget:
    target_id: str
    sources: tuple[str, ...]
    include_dirs: tuple[str, ...]
    required_symbols: tuple[str, ...]
    artifact_basename: str = "hhs_runtime"
    executable: bool = False
    link_math: bool = True

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class NativeToolchain:
    compiler: str
    symbol_inspector: str
    platform: str
    architecture: str
    library_suffix: str
    executable_suffix: str
    compiler_identity: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NativeBuildResult:
    target_id: str
    artifact_path: str
    artifact_sha256: str
    artifact_size: int
    platform: str
    architecture: str
    exported_symbols: tuple[str, ...]
    required_symbols: tuple[str, ...]
    compile_argv: tuple[str, ...]
    compile_stdout: str
    compile_stderr: str
    duration_ns: int
    build_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


def artifact_names(basename: str, *, system: str | None = None) -> tuple[str, str]:
    selected = system or platform.system()
    if selected == "Windows":
        return f"{basename}.dll", ".exe"
    if selected == "Darwin":
        return f"lib{basename}.dylib", ""
    return f"lib{basename}.so", ""


class NativeBuilder:
    def __init__(self, repository_root: str | Path, *, timeout_seconds: int = 900) -> None:
        self.repository_root = Path(repository_root).resolve()
        if not 1 <= timeout_seconds <= 7200:
            raise NativeBuildError("P172_NATIVE_TIMEOUT_INVALID", "native timeout is outside 1..7200")
        self.timeout_seconds = timeout_seconds

    def probe_toolchain(self) -> NativeToolchain:
        compiler = next((path for name in ("cc", "clang", "gcc") if (path := shutil.which(name))), None)
        if not compiler:
            raise NativeBuildError("P172_NATIVE_COMPILER_MISSING", "no supported C11 compiler is available")
        inspector_names = ("dumpbin", "llvm-nm", "nm") if platform.system() == "Windows" else ("llvm-nm", "nm")
        inspector = next((path for name in inspector_names if (path := shutil.which(name))), None)
        if not inspector:
            raise NativeBuildError("P172_NATIVE_SYMBOL_INSPECTOR_MISSING", "no supported symbol inspector is available")
        library, executable = artifact_names("hhs_runtime")
        try:
            result = subprocess.run(
                [compiler, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=min(self.timeout_seconds, 30),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise NativeBuildError("P172_NATIVE_COMPILER_PROBE_FAILED", "compiler version probe failed", {"error": f"{type(exc).__name__}:{exc}"}) from exc
        if result.returncode != 0:
            raise NativeBuildError("P172_NATIVE_COMPILER_PROBE_FAILED", "compiler version probe returned failure", {"stderr": result.stderr})
        return NativeToolchain(
            compiler=compiler,
            symbol_inspector=inspector,
            platform=platform.system(),
            architecture=platform.machine(),
            library_suffix=Path(library).suffix,
            executable_suffix=executable,
            compiler_identity=hash216(
                {"path_name": Path(compiler).name, "version": (result.stdout or result.stderr).splitlines()[:3]},
                domain="HHS-P172-NATIVE-COMPILER-V1",
            ),
        )

    def _resolve_source(self, value: str) -> Path:
        path = (self.repository_root / value).resolve()
        if self.repository_root not in path.parents:
            raise NativeBuildError("P172_NATIVE_SOURCE_ESCAPE", "native source path escapes repository", {"source": value})
        if not path.is_file():
            raise NativeBuildError("P172_NATIVE_SOURCE_MISSING", "native source file is missing", {"source": value})
        return path

    def _resolve_include(self, value: str) -> Path:
        path = (self.repository_root / value).resolve()
        if self.repository_root not in path.parents and path != self.repository_root:
            raise NativeBuildError("P172_NATIVE_INCLUDE_ESCAPE", "include path escapes repository", {"include": value})
        if not path.is_dir():
            raise NativeBuildError("P172_NATIVE_INCLUDE_MISSING", "include directory is missing", {"include": value})
        return path

    def build(self, target: NativeTarget, *, output_directory: str | Path) -> NativeBuildResult:
        toolchain = self.probe_toolchain()
        output = Path(output_directory).resolve()
        output.mkdir(parents=True, exist_ok=True)
        library_name, executable_suffix = artifact_names(target.artifact_basename, system=toolchain.platform)
        artifact = output / (f"{target.artifact_basename}{executable_suffix}" if target.executable else library_name)
        sources = [self._resolve_source(source) for source in target.sources]
        includes = [self._resolve_include(include) for include in target.include_dirs]

        argv: list[str] = [
            toolchain.compiler,
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-O2",
        ]
        if not target.executable:
            if toolchain.platform == "Darwin":
                argv.extend(["-dynamiclib", "-fPIC"])
            elif toolchain.platform == "Windows":
                argv.extend(["-shared"])
            else:
                argv.extend(["-shared", "-fPIC"])
        for include in includes:
            argv.extend(["-I", str(include)])
        argv.extend(str(source) for source in sources)
        argv.extend(["-o", str(artifact)])
        if target.link_math and toolchain.platform not in {"Windows"}:
            argv.append("-lm")

        started = time.monotonic_ns()
        try:
            completed = subprocess.run(
                argv,
                cwd=str(self.repository_root),
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise NativeBuildError(
                "P172_NATIVE_BUILD_TIMEOUT",
                "native build exceeded timeout",
                {"argv": argv, "timeout_seconds": self.timeout_seconds, "stdout": str(exc.stdout or ""), "stderr": str(exc.stderr or "")},
            ) from exc
        except OSError as exc:
            raise NativeBuildError("P172_NATIVE_BUILD_EXECUTION_FAILED", "native compiler could not be executed", {"error": f"{type(exc).__name__}:{exc}"}) from exc
        duration = time.monotonic_ns() - started
        if completed.returncode != 0:
            raise NativeBuildError(
                "P172_NATIVE_BUILD_FAILED",
                "native compilation failed",
                {"argv": argv, "exit_status": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr},
            )
        if not artifact.is_file() or artifact.stat().st_size == 0:
            raise NativeBuildError("P172_NATIVE_ARTIFACT_MISSING", "compiler succeeded without a nonempty artifact", {"artifact": str(artifact)})
        symbols = self.inspect_symbols(artifact, toolchain=toolchain)
        missing = sorted(set(target.required_symbols) - set(symbols))
        if missing:
            raise NativeBuildError("P172_NATIVE_SYMBOL_MISSING", "native artifact lacks required symbols", {"missing": missing, "artifact": str(artifact)})
        digest = sha256_file(artifact)
        payload = {
            "target": target.to_dict(),
            "toolchain": toolchain.to_dict(),
            "artifact_sha256": digest.sha256,
            "artifact_size": digest.size,
            "symbols": symbols,
            "argv": argv,
        }
        return NativeBuildResult(
            target_id=target.target_id,
            artifact_path=str(artifact),
            artifact_sha256=digest.sha256,
            artifact_size=digest.size,
            platform=toolchain.platform,
            architecture=toolchain.architecture,
            exported_symbols=tuple(symbols),
            required_symbols=target.required_symbols,
            compile_argv=tuple(argv),
            compile_stdout=completed.stdout,
            compile_stderr=completed.stderr,
            duration_ns=duration,
            build_identity=hash216(payload, domain="HHS-P172-NATIVE-BUILD-V1"),
        )

    def inspect_symbols(self, artifact: str | Path, *, toolchain: NativeToolchain | None = None) -> tuple[str, ...]:
        selected = toolchain or self.probe_toolchain()
        path = Path(artifact)
        inspector_name = Path(selected.symbol_inspector).name.lower()
        if inspector_name.startswith("dumpbin"):
            argv = [selected.symbol_inspector, "/exports", str(path)]
        elif selected.platform == "Darwin":
            argv = [selected.symbol_inspector, "-gU", str(path)]
        else:
            argv = [selected.symbol_inspector, "-D", "--defined-only", str(path)]
        try:
            completed = subprocess.run(
                argv,
                check=False,
                capture_output=True,
                text=True,
                timeout=min(self.timeout_seconds, 120),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise NativeBuildError("P172_NATIVE_SYMBOL_INSPECTION_FAILED", "symbol inspector failed", {"error": f"{type(exc).__name__}:{exc}", "argv": argv}) from exc
        if completed.returncode != 0:
            fallback = [selected.symbol_inspector, "--defined-only", str(path)] if "nm" in inspector_name else None
            if fallback:
                completed = subprocess.run(fallback, check=False, capture_output=True, text=True, timeout=min(self.timeout_seconds, 120))
            if completed.returncode != 0:
                raise NativeBuildError("P172_NATIVE_SYMBOL_INSPECTION_FAILED", "symbol inspector returned failure", {"argv": argv, "stderr": completed.stderr})
        symbols: set[str] = set()
        for line in completed.stdout.splitlines():
            fields = line.strip().split()
            if not fields:
                continue
            candidate = fields[-1]
            candidate = candidate.lstrip("_") if selected.platform == "Darwin" else candidate
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_@?$]*", candidate):
                symbols.add(candidate)
        return tuple(sorted(symbols))
