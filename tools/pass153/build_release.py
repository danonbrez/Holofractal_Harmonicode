from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "dist" / "pass153"
EXCLUDED_PARTS = {".git", "dist", ".pytest_cache", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def included_files():
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in rel.parts) or path.suffix in EXCLUDED_SUFFIXES:
            continue
        yield path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def product_manifest() -> dict:
    entries = [
        {"path": path.relative_to(ROOT).as_posix(), "size": path.stat().st_size, "sha256": digest(path)}
        for path in included_files()
    ]
    commit = os.environ.get("GITHUB_SHA")
    if not commit:
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        except Exception:
            commit = "UNBOUND_LOCAL_TREE"
    root = hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "HHS_PASS153_RELEASE_ROOT_V1",
        "contract_id": "HHS-P153-LITERT-OPEN-MODEL-AGENT",
        "pass_number": 153,
        "git_commit": commit,
        "entries": entries,
        "file_count": len(entries),
        "product_root_sha256": root,
        "terminal_classification": "HHS_PASS_153_LITERT_OPEN_MODEL_AGENT_ENVIRONMENT_VERIFIED",
    }


def copy_repository(target: Path) -> None:
    for path in included_files():
        relative = path.relative_to(ROOT)
        output = target / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, output)


def deterministic_zip(source: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in source.rglob("*") if item.is_file()):
            info = zipfile.ZipInfo(path.relative_to(source).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build() -> dict:
    if OUT.exists():
        shutil.rmtree(OUT)
    full_nucleus = OUT / "full_inherited_nucleus"
    huggingface = OUT / "huggingface_space"
    full_nucleus.mkdir(parents=True)
    huggingface.mkdir(parents=True)
    manifest = product_manifest()
    copy_repository(full_nucleus)
    copy_repository(huggingface)
    for target in (full_nucleus, huggingface):
        (target / "HHS_PASS_153_RELEASE_ROOT.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copy2(ROOT / "deployment/pass153/huggingface/README.md", huggingface / "README.md")
    shutil.copy2(ROOT / "deployment/pass153/huggingface/Dockerfile", huggingface / "Dockerfile")
    full_zip = OUT / "hhs_pass_153_litert_open_model_agent_environment_full_inherited_nucleus.zip"
    hf_zip = OUT / "hhs_pass_153_huggingface_space_full_repo.zip"
    deterministic_zip(full_nucleus, full_zip)
    deterministic_zip(huggingface, hf_zip)
    release = {
        "release_root": manifest,
        "github_branch_role": "authoritative source tree at git_commit",
        "full_inherited_zip": {"path": full_zip.name, "sha256": digest(full_zip), "size": full_zip.stat().st_size},
        "huggingface_zip": {"path": hf_zip.name, "sha256": digest(hf_zip), "size": hf_zip.stat().st_size},
    }
    (OUT / "HHS_PASS_153_RELEASE_MANIFEST.json").write_text(json.dumps(release, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return release


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
