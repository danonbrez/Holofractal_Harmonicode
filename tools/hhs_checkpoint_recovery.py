from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence

SYSTEM_SUFFIXES = {
    '.py', '.pyi', '.c', '.h', '.hpp', '.cc', '.cpp', '.rs', '.go', '.java',
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.sh', '.ps1', '.bat',
    '.toml', '.yaml', '.yml', '.ini', '.cfg', '.json', '.schema', '.sql',
    '.hhsprog', '.md', '.txt', '.csv'
}
CACHE_PARTS = {
    '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache',
    'node_modules', '.vite', 'dist', 'build', 'builds'
}
EVIDENCE_MARKERS = {
    'PASS_132_RELEASE_EVIDENCE', 'release_artifacts', 'evidence', 'reports', 'receipts'
}
SYSTEM_DIR_MARKERS = {
    'hhs_runtime', 'hhs_backend', 'hhs_python', 'hhs_gui', 'hhs_foundation',
    'tests', 'contracts', 'schemas', 'tools', 'examples'
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def normalized_member(name: str) -> str:
    p = PurePosixPath(name)
    parts = list(p.parts)
    if parts and parts[0].lower().startswith(('holofractal_harmonicode-', 'hhs_pass_')):
        parts = parts[1:]
    return PurePosixPath(*parts).as_posix()


def is_cache_path(name: str) -> bool:
    parts = set(PurePosixPath(name).parts)
    if parts & CACHE_PARTS:
        return True
    suffix = PurePosixPath(name).suffix.lower()
    return suffix in {'.pyc', '.pyo', '.so', '.dll', '.dylib', '.o'}


def is_system_path(name: str) -> bool:
    p = PurePosixPath(name)
    if not p.name or name.endswith('/') or is_cache_path(name):
        return False
    if p.name.startswith('PASS_') or p.name.startswith('HHS_PASS_'):
        return False
    parts = set(p.parts)
    if parts & SYSTEM_DIR_MARKERS:
        return True
    return p.suffix.lower() in SYSTEM_SUFFIXES and not any(m.lower() in name.lower() for m in EVIDENCE_MARKERS)


@dataclass(frozen=True)
class ArchiveInventory:
    archive: str
    sha256: str
    total_files: int
    total_uncompressed_bytes: int
    system_files: int
    system_bytes: int
    cache_files: int
    evidence_files: int
    top_level_entries: list[str]
    archive_class: str
    reasons: list[str]


def inventory_zip(path: Path) -> ArchiveInventory:
    if not path.is_file():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
    names = [normalized_member(i.filename) for i in infos]
    system = [i for i, n in zip(infos, names) if is_system_path(n)]
    caches = [i for i, n in zip(infos, names) if is_cache_path(n)]
    evidence = [
        i for i, n in zip(infos, names)
        if any(marker.lower() in n.lower() for marker in EVIDENCE_MARKERS)
        or PurePosixPath(n).name.startswith('PASS_')
    ]
    top = sorted({PurePosixPath(n).parts[0] for n in names if PurePosixPath(n).parts})
    reasons: list[str] = []
    system_dirs_present = sorted(set(top) & SYSTEM_DIR_MARKERS)
    if system_dirs_present:
        reasons.append(f"system directories present: {', '.join(system_dirs_present)}")
    if len(system) >= 100:
        reasons.append(f"substantial system tree: {len(system)} system files")
    if len(system) < 25 and len(evidence) >= len(system):
        reasons.append("evidence/report population dominates system source population")
    if len(system) >= 100 and system_dirs_present:
        archive_class = 'FULL_SYSTEM_CHECKPOINT'
    elif len(system) >= 25:
        archive_class = 'PARTIAL_SYSTEM_OR_DELTA'
    elif len(evidence) > 0:
        archive_class = 'EVIDENCE_ONLY_OR_NONCHECKPOINT'
    else:
        archive_class = 'UNCLASSIFIED_NONCHECKPOINT'
    return ArchiveInventory(
        archive=str(path), sha256=sha256_file(path), total_files=len(infos),
        total_uncompressed_bytes=sum(i.file_size for i in infos),
        system_files=len(system), system_bytes=sum(i.file_size for i in system),
        cache_files=len(caches), evidence_files=len(evidence),
        top_level_entries=top, archive_class=archive_class, reasons=reasons,
    )


def list_noncache_members(path: Path) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    with zipfile.ZipFile(path) as zf:
        for i in zf.infolist():
            if i.is_dir():
                continue
            n = normalized_member(i.filename)
            if is_cache_path(n):
                continue
            out[n] = (i.file_size, i.CRC)
    return out


def compare_parent_child(parent: Path, child: Path) -> dict:
    p = list_noncache_members(parent)
    c = list_noncache_members(child)
    inherited = sorted(set(p) & set(c))
    missing = sorted(set(p) - set(c))
    added = sorted(set(c) - set(p))
    changed = sorted(k for k in inherited if p[k] != c[k])
    unchanged = sorted(k for k in inherited if p[k] == c[k])
    return {
        'schema': 'HHS_CHECKPOINT_ANCESTRY_COMPARISON_V1',
        'parent_noncache_files': len(p),
        'child_noncache_files': len(c),
        'inherited_paths': len(inherited),
        'unchanged_paths': len(unchanged),
        'changed_paths': len(changed),
        'added_paths': len(added),
        'missing_parent_paths': len(missing),
        'missing_parent_sample': missing[:100],
        'ancestry_complete': len(missing) == 0,
    }


def safe_extract(zf: zipfile.ZipFile, target: Path) -> None:
    root = target.resolve()
    for info in zf.infolist():
        dest = (target / info.filename).resolve()
        if root not in dest.parents and dest != root:
            raise ValueError(f'unsafe ZIP member: {info.filename}')
    zf.extractall(target)


def copy_tree_without_caches(src: Path, dst: Path) -> None:
    for path in src.rglob('*'):
        rel = path.relative_to(src)
        if any(part in CACHE_PARTS for part in rel.parts):
            continue
        if path.is_dir():
            (dst / rel).mkdir(parents=True, exist_ok=True)
        elif path.suffix.lower() not in {'.pyc', '.pyo', '.so', '.dll', '.dylib', '.o'}:
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst / rel)


def resolve_single_root(extracted: Path) -> Path:
    entries = [p for p in extracted.iterdir() if p.name != '__MACOSX']
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extracted


def build_child_checkpoint(parent_zip: Path, delta_dir: Path, output_zip: Path) -> dict:
    pinv = inventory_zip(parent_zip)
    if pinv.archive_class != 'FULL_SYSTEM_CHECKPOINT':
        raise ValueError(
            f'parent rejected: {pinv.archive_class}; a complete child pass requires a full system checkpoint parent'
        )
    with tempfile.TemporaryDirectory(prefix='hhs_recovery_') as td:
        td = Path(td)
        extracted = td / 'parent'
        work = td / 'child'
        extracted.mkdir(); work.mkdir()
        with zipfile.ZipFile(parent_zip) as zf:
            safe_extract(zf, extracted)
        parent_root = resolve_single_root(extracted)
        copy_tree_without_caches(parent_root, work)
        copy_tree_without_caches(delta_dir, work)
        output_zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for path in sorted(work.rglob('*')):
                if path.is_file():
                    zf.write(path, path.relative_to(work).as_posix())
    cinv = inventory_zip(output_zip)
    comp = compare_parent_child(parent_zip, output_zip)
    if not comp['ancestry_complete']:
        output_zip.unlink(missing_ok=True)
        raise RuntimeError('reconstructed child omitted parent files')
    return {
        'schema': 'HHS_CHECKPOINT_RECOVERY_BUILD_RECEIPT_V1',
        'parent': asdict(pinv), 'child': asdict(cinv), 'comparison': comp,
        'output_zip': str(output_zip), 'output_sha256': sha256_file(output_zip),
        'cache_policy': 'TRANSIENT_CACHES_EXCLUDED; SYSTEM_FILES_AND_CANONICAL_OUTPUTS_PRESERVED',
        'status': 'FULL_ANCESTOR_COPY_VERIFIED',
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    inv = sub.add_parser('inventory')
    inv.add_argument('archive', type=Path)
    cmp = sub.add_parser('compare')
    cmp.add_argument('parent', type=Path); cmp.add_argument('child', type=Path)
    rec = sub.add_parser('recover')
    rec.add_argument('parent', type=Path); rec.add_argument('delta', type=Path); rec.add_argument('output', type=Path)
    args = ap.parse_args()
    if args.cmd == 'inventory':
        result = asdict(inventory_zip(args.archive))
    elif args.cmd == 'compare':
        result = compare_parent_child(args.parent, args.child)
    else:
        result = build_child_checkpoint(args.parent, args.delta, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
