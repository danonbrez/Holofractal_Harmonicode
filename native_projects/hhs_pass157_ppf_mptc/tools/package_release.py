from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

project = Path(__file__).resolve().parents[1]
repo = project.parents[1]
dist = project / "dist"
dist.mkdir(exist_ok=True)

try:
    listing = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout
    paths = [Path(item.decode()) for item in listing.split(b"\0") if item]
    generated_ledger = project.relative_to(repo) / "contracts" / "PASS_157_OBLIGATION_LEDGER.json"
    if (repo / generated_ledger).is_file() and generated_ledger not in paths:
        paths.append(generated_ledger)
    mode = "COMPLETE_TRACKED_REPOSITORY"
except (subprocess.CalledProcessError, FileNotFoundError):
    paths = [path.relative_to(repo) for path in project.rglob("*") if path.is_file() and "dist" not in path.parts]
    mode = "LOCAL_PROJECT_FIXTURE"

entries = []
for relative in sorted(paths, key=lambda value: value.as_posix()):
    absolute = repo / relative
    if not absolute.is_file():
        continue
    data = absolute.read_bytes()
    entries.append({
        "path": relative.as_posix(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    })
manifest_payload = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
manifest = {
    "schema": "HHS_PASS_157_COMPLETE_INHERITED_MANIFEST_V1",
    "mode": mode,
    "file_count": len(entries),
    "total_size": sum(item["size"] for item in entries),
    "manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
    "entries": entries,
}
manifest_path = dist / "PASS_157_COMPLETE_INHERITED_MANIFEST.json"
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

archive = dist / "hhs_pass_157_ppf_mptc_full_inherited_pass_history_nucleus.zip"
if mode == "COMPLETE_TRACKED_REPOSITORY":
    subprocess.run(["git", "-C", str(repo), "archive", "--format=zip", f"--output={archive}", "HEAD"], check=True)
    generated = project / "contracts" / "PASS_157_OBLIGATION_LEDGER.json"
    if generated.is_file():
        with zipfile.ZipFile(archive, "a", compression=zipfile.ZIP_DEFLATED) as bundle:
            bundle.write(generated, generated.relative_to(repo))
else:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for entry in entries:
            bundle.write(repo / entry["path"], entry["path"])
archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
release = {
    "schema": "HHS_PASS_157_RELEASE_PACKAGE_V1",
    "mode": mode,
    "archive": archive.name,
    "archive_size": archive.stat().st_size,
    "archive_sha256": archive_hash,
    "manifest": manifest_path.name,
    "manifest_sha256": manifest["manifest_sha256"],
}
(dist / "release-package.json").write_text(json.dumps(release, indent=2, sort_keys=True) + "\n")
print(json.dumps(release, sort_keys=True))
