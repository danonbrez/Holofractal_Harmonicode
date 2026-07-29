from __future__ import annotations

from pathlib import Path
import hashlib
import io
import tarfile
import zipfile

import pytest

from hhs_installer.acquisition import AcquisitionError, SourceAcquirer
from hhs_installer.schema import NetworkPolicy, SourceKind, SourceSpec
from hhs_installer.security import ArchivePolicy, SecurityError, extract_archive, inspect_archive


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_safe_zip_inspection_and_extraction(tmp_path: Path) -> None:
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("repo/file.txt", "payload")
    inspection = inspect_archive(archive)
    assert inspection.archive_type == "zip"
    assert inspection.expanded_bytes == 7
    destination = tmp_path / "out"
    extract_archive(archive, destination)
    assert (destination / "repo" / "file.txt").read_text(encoding="utf-8") == "payload"


def test_zip_traversal_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("../escape.txt", "bad")
    with pytest.raises(SecurityError) as raised:
        inspect_archive(archive)
    assert raised.value.code == "P172_ARCHIVE_PATH_TRAVERSAL"


def test_tar_symlink_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w") as output:
        item = tarfile.TarInfo("link")
        item.type = tarfile.SYMTYPE
        item.linkname = "/etc/passwd"
        output.addfile(item)
    with pytest.raises(SecurityError) as raised:
        inspect_archive(archive)
    assert raised.value.code == "P172_ARCHIVE_UNSAFE_ENTRY"


def test_archive_size_bound_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "large.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("large.bin", b"x" * 64)
    with pytest.raises(SecurityError) as raised:
        inspect_archive(archive, ArchivePolicy(maximum_expanded_bytes=32, maximum_single_file_bytes=128))
    assert raised.value.code == "P172_ARCHIVE_EXPANSION_BOUND_EXCEEDED"


def test_local_file_acquisition_requires_matching_identity(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    result = SourceAcquirer(tmp_path / "cache").acquire(
        SourceSpec(SourceKind.LOCAL, str(source), _sha(source)),
        network_policy=NetworkPolicy.OFFLINE,
    )
    assert result.verified is True
    with pytest.raises(AcquisitionError) as raised:
        SourceAcquirer(tmp_path / "cache2").acquire(
            SourceSpec(SourceKind.LOCAL, str(source), "0" * 64),
            network_policy=NetworkPolicy.OFFLINE,
        )
    assert raised.value.code == "P172_SOURCE_IDENTITY_MISMATCH"


def test_offline_policy_rejects_network_source(tmp_path: Path) -> None:
    with pytest.raises(AcquisitionError) as raised:
        SourceAcquirer(tmp_path / "cache").acquire(
            SourceSpec(SourceKind.RELEASE, "https://example.invalid/hhs.zip", "0" * 64),
            network_policy=NetworkPolicy.OFFLINE,
        )
    assert raised.value.code == "P172_OFFLINE_NETWORK_POLICY_VIOLATION"
