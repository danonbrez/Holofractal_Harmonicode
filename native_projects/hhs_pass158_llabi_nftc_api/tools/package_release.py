from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
DIST = PROJECT / "dist"
ARCHIVE = DIST / "hhs_pass158_complete_inherited_pass_history_nucleus.zip"
MANIFEST = DIST / "PASS_158_COMPLETE_INHERITED_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    tracked = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO, check=True, capture_output=True
    ).stdout.split(b"\0")
    paths = [REPO / item.decode("utf-8") for item in tracked if item]
    evidence = sorted((DIST / "evidence").glob("*"))
    entries: list[dict[str, object]] = []
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            if not path.is_file():
                continue
            relative = path.relative_to(REPO).as_posix()
            archive.write(path, relative)
            entries.append({"path": relative, "size": path.stat().st_size, "sha256": sha256(path), "source": "tracked"})
        for path in evidence:
            relative = f"native_projects/hhs_pass158_llabi_nftc_api/dist/evidence/{path.name}"
            archive.write(path, relative)
            entries.append({"path": relative, "size": path.stat().st_size, "sha256": sha256(path), "source": "execution_evidence"})
    payload = {
        "schema": "HHS_PASS_158_COMPLETE_INHERITED_MANIFEST_V1",
        "contract_id": "HHS-P158-LLABI-NFTC-API",
        "mode": "COMPLETE_TRACKED_REPOSITORY_WITH_EXECUTION_EVIDENCE",
        "inheritance_parent": "HHS_PASS_157_UNIFIED_CLOSURE_VERIFIED",
        "archive": ARCHIVE.name,
        "archive_size": ARCHIVE.stat().st_size,
        "archive_sha256": sha256(ARCHIVE),
        "file_count": len(entries),
        "entries_root_sha256": hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    (DIST / "release-package.json").write_text(json.dumps({
        "archive": ARCHIVE.name,
        "archive_size": payload["archive_size"],
        "archive_sha256": payload["archive_sha256"],
        "manifest": MANIFEST.name,
        "manifest_sha256": sha256(MANIFEST),
        "classification": "HHS_PASS_158_COMPLETE_INHERITED_PACKAGE_BUILT",
    }, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"archive": ARCHIVE.name, "files": len(entries), "sha256": payload["archive_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
