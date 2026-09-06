from __future__ import annotations

from pathlib import Path
import argparse

TARGET = Path("hhs_backend/server.py")
OLD = '        "hhs_backend.server:app",'
NEW = '        "hhs_backend.public_api_server:app",'


def inspect() -> tuple[int, int]:
    source = TARGET.read_text(encoding="utf-8")
    return source.count(OLD), source.count(NEW)


def apply() -> bool:
    source = TARGET.read_text(encoding="utf-8")
    old_count = source.count(OLD)
    new_count = source.count(NEW)
    if old_count == 0 and new_count == 1:
        return False
    if old_count != 1 or new_count != 0:
        raise RuntimeError(
            f"PASS170_I176_CANONICAL_BASE_LAUNCHER_SOURCE_UNEXPECTED:old={old_count}:new={new_count}"
        )
    TARGET.write_text(source.replace(OLD, NEW, 1), encoding="utf-8")
    return True


def check() -> None:
    old_count, new_count = inspect()
    if old_count != 0 or new_count != 1:
        raise RuntimeError(
            f"PASS170_I176_CANONICAL_BASE_LAUNCHER_REDIRECT_INVALID:old={old_count}:new={new_count}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        changed = apply()
        print("changed" if changed else "already-canonical")
    check()


if __name__ == "__main__":
    main()
