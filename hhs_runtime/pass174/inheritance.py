"""Pass 174 append-only legacy specification inheritance authority.

Every repository-visible pass specification through Pass 173 is treated as a
minimum binding foundation. The manifest is derived from file bytes rather
than filenames alone so implementation and evidence can bind the exact legacy
corpus without rewriting any prior pass.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Iterable

PASS_PATTERN = re.compile(r"(?:^|[/_])(?:HHS_)?PASS[_ -]?(\d{1,3})(?:[/_ .-]|$)", re.IGNORECASE)
SPEC_SUFFIXES = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml"}
DEFAULT_EXCLUDED_PARTS = {".git", ".pytest_cache", "node_modules", "dist", "build", "__pycache__"}
ZERO_SHA256 = "0" * 64


class LegacyInheritanceError(ValueError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def parse_pass_number(path: str) -> int | None:
    match = PASS_PATTERN.search(path.replace("\\", "/"))
    return int(match.group(1)) if match else None


@dataclass(frozen=True)
class LegacySpecification:
    pass_number: int
    path: str
    size: int
    sha256: str


@dataclass(frozen=True)
class LegacyAuthorityManifest:
    schema: str
    version: int
    maximum_inherited_pass: int
    specifications: tuple[LegacySpecification, ...]
    aggregate_root_sha256: str
    pass_numbers_present: tuple[int, ...]
    missing_pass_numbers: tuple[int, ...]

    @property
    def specification_count(self) -> int:
        return len(self.specifications)

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "specification_count": self.specification_count,
            "specifications": [asdict(item) for item in self.specifications],
            "pass_numbers_present": list(self.pass_numbers_present),
            "missing_pass_numbers": list(self.missing_pass_numbers),
        }


def _candidate_files(root: Path, extra_patterns: Iterable[str] = ()) -> list[Path]:
    patterns = ("HHS_PASS_*", "PASS_*", "**/HHS_PASS_*", "**/PASS_*", "**/pass*/**/*", *tuple(extra_patterns))
    found: dict[str, Path] = {}
    for pattern in patterns:
        for path in root.glob(pattern):
            if not path.is_file() or path.suffix.lower() not in SPEC_SUFFIXES:
                continue
            relative = path.relative_to(root).as_posix()
            if any(part in DEFAULT_EXCLUDED_PARTS for part in path.parts):
                continue
            if parse_pass_number(relative) is None:
                continue
            found[relative] = path
    return [found[key] for key in sorted(found)]


def build_legacy_manifest(repository_root: str | Path, *, maximum_inherited_pass: int = 173, require_pass_173: bool = True, extra_patterns: Iterable[str] = ()) -> LegacyAuthorityManifest:
    root = Path(repository_root).resolve()
    if not root.is_dir():
        raise LegacyInheritanceError("HHS_P174_REPOSITORY_ROOT_NOT_FOUND", str(root))
    specs: list[LegacySpecification] = []
    for path in _candidate_files(root, extra_patterns):
        relative = path.relative_to(root).as_posix()
        pass_number = parse_pass_number(relative)
        if pass_number is None or pass_number > maximum_inherited_pass:
            continue
        payload = path.read_bytes()
        specs.append(LegacySpecification(pass_number=pass_number, path=relative, size=len(payload), sha256=sha256(payload).hexdigest()))
    specs.sort(key=lambda item: (item.pass_number, item.path, item.sha256))
    present = tuple(sorted({item.pass_number for item in specs}))
    if require_pass_173 and 173 not in present:
        raise LegacyInheritanceError("HHS_P174_PASS_173_FOUNDATION_REQUIRED")
    if not specs:
        raise LegacyInheritanceError("HHS_P174_NO_LEGACY_SPECIFICATIONS_FOUND")
    aggregate = ZERO_SHA256
    for item in specs:
        aggregate = sha256(b"HHS-P174-LEGACY-SPEC-CHAIN-V1\0" + bytes.fromhex(aggregate) + canonical_bytes(asdict(item))).hexdigest()
    missing = tuple(number for number in range(1, maximum_inherited_pass + 1) if number not in present)
    return LegacyAuthorityManifest(
        schema="HHS_P174_LEGACY_AUTHORITY_MANIFEST_V1",
        version=1,
        maximum_inherited_pass=maximum_inherited_pass,
        specifications=tuple(specs),
        aggregate_root_sha256=aggregate,
        pass_numbers_present=present,
        missing_pass_numbers=missing,
    )


def verify_manifest(repository_root: str | Path, expected: LegacyAuthorityManifest) -> dict[str, object]:
    observed = build_legacy_manifest(repository_root, maximum_inherited_pass=expected.maximum_inherited_pass, require_pass_173=True)
    if observed.aggregate_root_sha256 != expected.aggregate_root_sha256:
        raise LegacyInheritanceError("HHS_P174_LEGACY_FOUNDATION_ROOT_MISMATCH", f"expected={expected.aggregate_root_sha256},observed={observed.aggregate_root_sha256}")
    if observed.specification_count != expected.specification_count:
        raise LegacyInheritanceError("HHS_P174_LEGACY_FOUNDATION_COUNT_MISMATCH")
    return {
        "classification": "HHS_P174_LEGACY_FOUNDATION_VERIFIED",
        "aggregate_root_sha256": observed.aggregate_root_sha256,
        "specification_count": observed.specification_count,
        "pass_numbers_present": list(observed.pass_numbers_present),
        "missing_pass_numbers": list(observed.missing_pass_numbers),
        "append_only": True,
        "minimum_foundation": True,
    }
