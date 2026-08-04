from __future__ import annotations

import os

from hhs_python.runtime.hhs_pass205_native_freshness_guard import (
    ensure_pass205_native_freshness,
)


def _write(path, payload: bytes = b"x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _fixture_tree(tmp_path):
    root = tmp_path / "repo"
    source = root / "hhs_runtime" / "c" / "hhs_pass205_continuation.c"
    header = root / "hhs_runtime" / "c" / "hhs_pass205_continuation.h"
    hash_source = root / "hhs_runtime" / "src" / "hhs_hash216.c"
    hash_header = root / "hhs_runtime" / "include" / "hhs_hash216.h"
    output = root / "hhs_runtime" / "builds" / "libhhs_pass205_continuation.so"
    for path in (source, header, hash_source, hash_header, output):
        _write(path)
    return root, source, header, hash_source, hash_header, output


def test_stale_header_removes_native_library(tmp_path) -> None:
    root, source, header, hash_source, hash_header, output = _fixture_tree(tmp_path)
    base_ns = 1_700_000_000_000_000_000
    for path in (source, hash_source, hash_header):
        os.utime(path, ns=(base_ns, base_ns))
    os.utime(output, ns=(base_ns + 10, base_ns + 10))
    os.utime(header, ns=(base_ns + 20, base_ns + 20))

    report = ensure_pass205_native_freshness(root)

    assert report["stale"] is True
    assert report["removed"] is True
    assert report["ready_for_loader"] is True
    assert report["reason"] == "STALE_LIBRARY_REMOVED_REBUILD_REQUIRED"
    assert not output.exists()


def test_fresh_native_library_is_preserved(tmp_path) -> None:
    root, source, header, hash_source, hash_header, output = _fixture_tree(tmp_path)
    base_ns = 1_700_000_000_000_000_000
    for path in (source, header, hash_source, hash_header):
        os.utime(path, ns=(base_ns, base_ns))
    os.utime(output, ns=(base_ns + 20, base_ns + 20))

    report = ensure_pass205_native_freshness(root)

    assert report["stale"] is False
    assert report["removed"] is False
    assert report["ready_for_loader"] is True
    assert report["reason"] == "LIBRARY_FRESH"
    assert output.exists()


def test_prebuilt_library_fails_closed_when_source_is_missing(tmp_path) -> None:
    root, source, _header, _hash_source, _hash_header, output = _fixture_tree(tmp_path)
    source.unlink()

    report = ensure_pass205_native_freshness(root)

    assert report["stale"] is True
    assert report["removed"] is True
    assert report["ready_for_loader"] is False
    assert report["reason"] == "PREBUILT_LIBRARY_REJECTED_BUILD_INPUTS_MISSING"
    assert not output.exists()
