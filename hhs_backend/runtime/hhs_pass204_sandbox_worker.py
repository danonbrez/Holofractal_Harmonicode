"""Production projection for the Pass 204 disposable sandbox worker."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import hhs_backend.runtime.hhs_pass204_sandbox_worker_v1 as _v1


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _production_audit_boundary(repo_root: Path, sandbox_root: Path) -> None:
    immutable_roots = {repo_root.resolve()}
    for value in [sys.prefix, sys.base_prefix, *sys.path]:
        if not value:
            continue
        try:
            candidate = Path(value).resolve()
        except OSError:
            continue
        if candidate.exists():
            immutable_roots.add(candidate)

    def readable(path: Path) -> bool:
        return _inside(path, sandbox_root) or any(_inside(path, root) for root in immutable_roots)

    def hook(event: str, args: tuple[Any, ...]) -> None:
        if event in {"socket.connect", "socket.bind", "socket.listen"}:
            raise _v1.SandboxBoundaryError("network operation requires a mediated durable job")
        if event in {"os.system", "subprocess.Popen", "pty.spawn"}:
            raise _v1.SandboxBoundaryError("host process creation is not exposed to remote sessions")
        if event in {"ctypes.dlopen", "ctypes.dlsym"}:
            target = Path(str(args[0])) if args else Path("")
            if not readable(target):
                raise _v1.SandboxBoundaryError("native libraries must be immutable-runtime or sandbox scoped")
        if event == "open" and args:
            raw_path = args[0]
            if isinstance(raw_path, int):
                return
            path = Path(os.fsdecode(raw_path))
            if not path.is_absolute():
                path = Path.cwd() / path
            mode = str(args[1]) if len(args) > 1 else "r"
            writing = any(flag in mode for flag in ("w", "a", "x", "+"))
            if writing and not _inside(path, sandbox_root):
                raise _v1.SandboxBoundaryError("writes are restricted to the ephemeral sandbox")
            if not writing and not readable(path):
                raise _v1.SandboxBoundaryError("read is outside the immutable runtime and sandbox projections")
        if event in {"os.remove", "os.rmdir", "os.rename", "os.replace", "os.unlink"} and args:
            paths = [Path(os.fsdecode(item)) for item in args[:2] if isinstance(item, (str, bytes, os.PathLike))]
            for path in paths:
                candidate = path if path.is_absolute() else Path.cwd() / path
                if not _inside(candidate, sandbox_root):
                    raise _v1.SandboxBoundaryError("destructive operations are restricted to the ephemeral sandbox")

    sys.addaudithook(hook)


_v1._install_audit_boundary = _production_audit_boundary
main = _v1.main


if __name__ == "__main__":
    raise SystemExit(main())
