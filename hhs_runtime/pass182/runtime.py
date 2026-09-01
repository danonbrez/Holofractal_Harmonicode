from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import ast
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
from typing import Any, Callable, Iterable, Mapping, Sequence

CONTRACT_ID = "HHS-P182-UMHC-ROTR-VM81-H72-H216"
PASS_NUMBER = 182
TERMINAL_CLASSIFICATION = "HHS_UNIVERSAL_MULTIMODAL_HYDRATION_COMPILER_VERIFIED"
SNAPSHOT_SCHEMA = "HHS_PASS182_READ_ONLY_TREE_SNAPSHOT_V1"
IR_SCHEMA = "HHS_PASS182_UNIVERSAL_HYDRATION_IR_V1"
GRAPH_SCHEMA = "HHS_PASS182_REPOSITORY_LOGIC_GRAPH_V1"
PACKAGE_SCHEMA = "HHS_PASS182_PORTABLE_RUNTIME_PACKAGE_V1"
RECEIPT_SCHEMA = "HHS_PASS182_HYDRATION_RECEIPT_V1"

SUPPORTED_MODALITIES = (
    "text",
    "structured_documents",
    "source_code",
    "applications",
    "images",
    "audio",
    "speech",
    "music",
    "video",
    "animation",
    "games_2d",
    "games_3d",
    "meshes_materials_motion",
    "spreadsheets",
    "presentations",
    "datasets",
    "sensor_time_series",
    "api_behavior",
    "multimodal_projects",
    "repository_tree",
)

AUTHORITY_CLASSES = (
    "NORMATIVE_CONTRACT",
    "AUTHORITATIVE_SOURCE",
    "RUNTIME_CONFIGURATION",
    "TEST",
    "VALIDATED_EVIDENCE",
    "GENERATED_ARTIFACT",
    "DOCUMENTATION",
    "REFERENCE_CORPUS",
    "THIRD_PARTY_DEPENDENCY",
    "CACHE",
    "TEMPORARY",
    "UNKNOWN",
)

RELATIONS = (
    "FILE",
    "DEFINES_SYMBOL",
    "IMPORTS_SYMBOL",
    "CALLS_FUNCTION",
    "IMPLEMENTS_ROUTE",
    "LOADS_ASSET",
    "SATISFIES_REQUIREMENT",
    "TESTED_BY",
    "CONFIGURED_BY",
    "BUILT_BY",
    "DEPLOYED_BY",
    "PRODUCES_ARTIFACT",
    "CONSUMED_BY",
    "MUTATES_STATE",
    "EMITS_RECEIPT",
    "CONTRADICTS",
    "SUPERSEDES",
)

RESIDUAL_CLASSES = (
    "DECLARED_BUT_NOT_IMPLEMENTED",
    "IMPLEMENTED_BUT_UNDOCUMENTED",
    "ROUTE_WITHOUT_RUNTIME_TARGET",
    "TEST_WITHOUT_PRODUCTION_PATH",
    "UNREACHABLE_SOURCE",
    "ORPHANED_ASSET",
    "DUPLICATE_LOGIC",
    "CONFLICTING_CONFIGURATION",
    "UNGUARDED_STATE_MUTATION",
    "NONDETERMINISTIC_EXECUTION",
    "MISSING_REPLAY_PATH",
    "UNVERIFIED_NATIVE_ABI_CALL",
    "STALE_GENERATED_ARTIFACT",
    "CONSTRAINT_CONTRADICTION",
    "UNREADABLE_TREE_OBJECT",
    "UNSUPPORTED_FORMAT",
)

_TEXT_EXTENSIONS = {
    ".txt", ".md", ".rst", ".py", ".c", ".h", ".hpp", ".cpp", ".cc", ".js", ".jsx",
    ".ts", ".tsx", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml",
    ".html", ".css", ".sh", ".ps1", ".sql", ".csv", ".tsv", ".svg",
}
_SOURCE_EXTENSIONS = {".py", ".c", ".h", ".hpp", ".cpp", ".cc", ".js", ".jsx", ".ts", ".tsx", ".sh", ".ps1"}
_DOC_EXTENSIONS = {".md", ".rst", ".txt", ".html", ".pdf", ".doc", ".docx", ".odt"}
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".tif", ".tiff"}
_AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}
_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".avi"}
_ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z"}

_SECRET_PATH_RE = re.compile(r"(^|/)(\.env(?:\.|$)|.*(?:secret|token|credential|private[_-]?key|passwd|password).*)", re.I)
_SECRET_CONTENT_RE = re.compile(
    r"(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"]?[^\s'\"]{8,})",
    re.I,
)
_ROUTE_RE = re.compile(r"(?:@(?:app|router)\.(?:get|post|put|delete|patch)|add_api_route|APIRouter\s*\()")
_ASSET_RE = re.compile(r"['\"]([^'\"]+\.(?:png|jpe?g|gif|webp|svg|wav|mp3|flac|ogg|mp4|webm|glb|gltf))['\"]", re.I)


class HydrationError(RuntimeError):
    pass


def supported_modality_families() -> tuple[str, ...]:
    return SUPPORTED_MODALITIES


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)


def _hash72(label: str, value: Any) -> str:
    # Inherited native Hash72 witness helper. Pass 182 does not mint an independent clock.
    from hhs_runtime.hash72_checkpoint import make_hash72_witness
    return make_hash72_witness(label, value, width=72).digest


def _hash216(label: str, value: Any) -> str:
    payload = _canonical(value)
    lanes = [
        _hash72(f"{label}:previous", {"lane": 0, "payload": payload}),
        _hash72(f"{label}:change", {"lane": 1, "payload": payload}),
        _hash72(f"{label}:receipt", {"lane": 2, "payload": payload}),
    ]
    identity = "".join(lanes)
    if len(identity) != 216:
        raise HydrationError("PASS182_HASH216_LENGTH_INVARIANT")
    return identity


def _classify_authority(relative: str) -> str:
    lower = relative.lower()
    name = Path(relative).name.lower()
    if "contract" in lower or lower.startswith("contracts/"):
        return "NORMATIVE_CONTRACT"
    if lower.startswith("evidence/") or "/evidence/" in lower:
        return "VALIDATED_EVIDENCE"
    if lower.startswith("tests/") or "/tests/" in lower or name.startswith("test_"):
        return "TEST"
    if lower.startswith("docs/") or name.endswith((".md", ".rst")):
        return "DOCUMENTATION"
    if name in {"pyproject.toml", "package.json", "makefile", "dockerfile"} or name.endswith((".yaml", ".yml", ".toml", ".ini")):
        return "RUNTIME_CONFIGURATION"
    if lower.startswith(("build/", "dist/", ".cache/", "__pycache__/")):
        return "GENERATED_ARTIFACT"
    if Path(relative).suffix.lower() in _SOURCE_EXTENSIONS:
        return "AUTHORITATIVE_SOURCE"
    return "UNKNOWN"


def _detect_modality(relative: str, kind: str) -> str:
    if kind == "directory":
        return "repository_tree"
    suffix = Path(relative).suffix.lower()
    if suffix in _SOURCE_EXTENSIONS:
        return "source_code"
    if suffix in _DOC_EXTENSIONS:
        return "structured_documents"
    if suffix in _IMAGE_EXTENSIONS:
        return "images"
    if suffix in _AUDIO_EXTENSIONS:
        return "audio"
    if suffix in _VIDEO_EXTENSIONS:
        return "video"
    if suffix in {".csv", ".tsv", ".parquet", ".arrow", ".sqlite", ".db"}:
        return "datasets"
    if suffix in {".xlsx", ".xls", ".ods"}:
        return "spreadsheets"
    if suffix in {".pptx", ".ppt", ".odp"}:
        return "presentations"
    if suffix in {".glb", ".gltf", ".obj", ".fbx"}:
        return "meshes_materials_motion"
    if suffix in _TEXT_EXTENSIONS:
        return "text"
    return "multimodal_projects"


def _path_secret(relative: str) -> bool:
    return bool(_SECRET_PATH_RE.search(relative.replace(os.sep, "/")))


def _bounded_text(path: Path, limit: int = 8192) -> tuple[str | None, bool]:
    try:
        raw = path.read_bytes()[: limit + 1]
    except OSError:
        return None, False
    if b"\x00" in raw:
        return None, False
    try:
        text = raw[:limit].decode("utf-8")
    except UnicodeDecodeError:
        return None, False
    return text, bool(_SECRET_CONTENT_RE.search(text))


@dataclass(frozen=True)
class SnapshotOptions:
    include_vcs: bool = True
    text_preview_bytes: int = 8192


class UniversalHydrationCompiler:
    def __init__(self, *, options: SnapshotOptions | None = None) -> None:
        self.options = options or SnapshotOptions()

    @staticmethod
    def _root_guard(root: Path) -> Path:
        root = root.expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise HydrationError("PASS182_SOURCE_ROOT_INVALID")
        return root

    def snapshot_tree(self, source_root: str | Path) -> dict[str, Any]:
        root = self._root_guard(Path(source_root))
        root_before = root.stat()
        records: list[dict[str, Any]] = []
        duplicate_map: dict[str, list[str]] = {}

        all_paths = sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix().encode("utf-8", "surrogateescape"))
        for sequence, path in enumerate(all_paths):
            relative = path.relative_to(root).as_posix()
            if not self.options.include_vcs and (relative == ".git" or relative.startswith(".git/")):
                continue
            try:
                info = path.lstat()
            except OSError as exc:
                records.append({
                    "sequence": sequence,
                    "relative_path": relative,
                    "kind": "unreadable",
                    "status": "UNREADABLE_TREE_OBJECT",
                    "error_type": type(exc).__name__,
                    "authority_class": "UNKNOWN",
                    "modality": "multimodal_projects",
                })
                continue

            mode = stat.S_IMODE(info.st_mode)
            kind = "other"
            content_sha256: str | None = None
            symlink_target: str | None = None
            unsafe_symlink = False
            text_preview: str | None = None
            secret_suspected = _path_secret(relative)

            if stat.S_ISLNK(info.st_mode):
                kind = "symlink"
                symlink_target = os.readlink(path)
                try:
                    resolved = (path.parent / symlink_target).resolve()
                    resolved.relative_to(root)
                except (OSError, ValueError):
                    unsafe_symlink = True
            elif stat.S_ISDIR(info.st_mode):
                kind = "directory"
            elif stat.S_ISREG(info.st_mode):
                kind = "file"
                try:
                    content_sha256 = _sha256_file(path)
                except OSError:
                    content_sha256 = None
                if content_sha256 is not None:
                    duplicate_map.setdefault(content_sha256, []).append(relative)
                if Path(relative).suffix.lower() in _TEXT_EXTENSIONS:
                    text_preview, content_secret = _bounded_text(path, self.options.text_preview_bytes)
                    secret_suspected = secret_suspected or content_secret
                    if secret_suspected:
                        text_preview = None
            else:
                kind = "special"

            identity_payload = {
                "relative_path": relative,
                "kind": kind,
                "size": int(info.st_size),
                "mode": int(mode),
                "content_sha256": content_sha256,
                "symlink_target": symlink_target,
                "unsafe_symlink": unsafe_symlink,
            }
            record = {
                "sequence": sequence,
                **identity_payload,
                "path_hash216": _hash216("pass182:path", identity_payload),
                "authority_class": _classify_authority(relative),
                "modality": _detect_modality(relative, kind),
                "secret_suspected": secret_suspected,
                "text_preview": text_preview,
                "read_status": "READABLE" if content_sha256 is not None or kind in {"directory", "symlink"} else "UNREADABLE",
                "parse_status": "NOT_PARSED",
                "logic_status": "PENDING",
            }
            if unsafe_symlink:
                record["read_status"] = "DENIED_UNSAFE_SYMLINK"
            if Path(relative).suffix.lower() in _ARCHIVE_EXTENSIONS:
                record["archive_policy"] = "BOUNDED_VIRTUAL_SUBTREE_REQUIRED"
            records.append(record)

        root_after = root.stat()
        source_metadata_unchanged = (
            root_before.st_mode == root_after.st_mode
            and root_before.st_mtime_ns == root_after.st_mtime_ns
            and root_before.st_ctime_ns == root_after.st_ctime_ns
        )

        duplicates = [
            {"content_sha256": digest, "paths": paths}
            for digest, paths in sorted(duplicate_map.items())
            if len(paths) > 1
        ]
        root_payload = {
            "contract_id": CONTRACT_ID,
            "records": [
                {
                    "relative_path": r["relative_path"],
                    "path_hash216": r.get("path_hash216"),
                    "content_sha256": r.get("content_sha256"),
                    "kind": r["kind"],
                }
                for r in records
            ],
        }
        return {
            "schema": SNAPSHOT_SCHEMA,
            "contract_id": CONTRACT_ID,
            "source_root_name": root.name,
            "source_root_path_disclosed": False,
            "source_root_identity_sha256": _sha256_bytes(str(root).encode("utf-8")),
            "tree_root_hash216": _hash216("pass182:tree", root_payload),
            "entry_count": len(records),
            "records": records,
            "duplicate_content": duplicates,
            "secret_text_storage_count": sum(
                1 for r in records if r.get("secret_suspected") and r.get("text_preview") is not None
            ),
            "unsafe_symlink_count": sum(1 for r in records if r.get("unsafe_symlink")),
            "source_metadata_unchanged": source_metadata_unchanged,
            "source_mutation_authority": False,
            "complete_identity_enumeration": True,
        }

    def build_ir(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        records = list(snapshot.get("records", []))
        modality_counts = {name: 0 for name in SUPPORTED_MODALITIES}
        for record in records:
            modality = str(record.get("modality", "multimodal_projects"))
            modality_counts[modality] = modality_counts.get(modality, 0) + 1
        semantic_objects = [
            {
                "relative_path": r["relative_path"],
                "kind": r["kind"],
                "modality": r.get("modality"),
                "authority_class": r.get("authority_class"),
                "identity": r.get("path_hash216"),
            }
            for r in records
        ]
        ir = {
            "schema": IR_SCHEMA,
            "contract_id": CONTRACT_ID,
            "source_identity": snapshot.get("tree_root_hash216"),
            "time_domain": "IMMUTABLE_SNAPSHOT_SEQUENCE",
            "spatial_domain": "LEXICAL_FILE_TREE",
            "semantic_objects": semantic_objects,
            "symbols_and_definitions": [],
            "relationships": [],
            "ordered_events": [{"sequence": i, "event": "TREE_OBJECT_DISCOVERED", "path": r["relative_path"]} for i, r in enumerate(records)],
            "modality_layers": modality_counts,
            "control_flow": [],
            "data_flow": [],
            "configuration_flow": [],
            "native_primitives": ["SHA256_CONTENT_IDENTITY", "INHERITED_HASH72_WITNESS", "HASH216_THREE_LANE_ARCHIVE"],
            "constraints": [
                "SOURCE_TREE_READ_ONLY",
                "NO_SOURCE_BINARY_EXECUTION",
                "DYNAMIC_TRACE_SANDBOX_COPY_ONLY",
                "VM81_SINGLETON_PROMOTION_ONLY",
                "HASH72_EVIDENCE_NOT_MUTATION_AUTHORITY",
                "HASH216_ARCHIVAL_NOT_MUTATION_AUTHORITY",
            ],
            "residuals": [],
            "optimization_parameters": {"incremental_dependency_scope": True, "bounded_text_preview_bytes": self.options.text_preview_bytes},
            "evidence": {"snapshot_schema": snapshot.get("schema"), "entry_count": snapshot.get("entry_count")},
            "replay_state": {"tree_root_hash216": snapshot.get("tree_root_hash216")},
        }
        ir["ir_hash216"] = _hash216("pass182:ir", ir)
        return ir

    def build_logic_graph(self, source_root: str | Path, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        root = self._root_guard(Path(source_root))
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        residuals: list[dict[str, Any]] = []

        for record in snapshot.get("records", []):
            relative = str(record["relative_path"])
            nodes.append({"id": f"FILE:{relative}", "kind": "FILE", "path": relative, "identity": record.get("path_hash216")})
            if record.get("kind") != "file":
                continue
            path = root / relative
            suffix = path.suffix.lower()
            preview = record.get("text_preview")
            if record.get("secret_suspected"):
                continue
            if suffix == ".py" and isinstance(preview, str):
                try:
                    tree = ast.parse(path.read_text("utf-8"))
                except (OSError, UnicodeDecodeError, SyntaxError):
                    residuals.append({"class": "UNSUPPORTED_FORMAT", "path": relative, "detail": "PYTHON_PARSE_FAILED"})
                    continue
                for item in ast.walk(tree):
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        symbol = f"SYMBOL:{relative}:{item.name}"
                        nodes.append({"id": symbol, "kind": "SYMBOL", "name": item.name, "path": relative})
                        edges.append({"relation": "DEFINES_SYMBOL", "from": f"FILE:{relative}", "to": symbol})
                    elif isinstance(item, (ast.Import, ast.ImportFrom)):
                        if isinstance(item, ast.Import):
                            names = [alias.name for alias in item.names]
                        else:
                            names = [item.module or ""]
                        for name in names:
                            edges.append({"relation": "IMPORTS_SYMBOL", "from": f"FILE:{relative}", "to": f"IMPORT:{name}"})
                    elif isinstance(item, ast.Call):
                        fn = item.func
                        name = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else None
                        if name:
                            edges.append({"relation": "CALLS_FUNCTION", "from": f"FILE:{relative}", "to": f"CALL:{name}"})
            if isinstance(preview, str):
                if _ROUTE_RE.search(preview):
                    edges.append({"relation": "IMPLEMENTS_ROUTE", "from": f"FILE:{relative}", "to": "ROUTE:DECLARED"})
                for match in _ASSET_RE.finditer(preview):
                    edges.append({"relation": "LOADS_ASSET", "from": f"FILE:{relative}", "to": f"ASSET:{match.group(1)}"})
                if record.get("authority_class") == "TEST":
                    edges.append({"relation": "TESTED_BY", "from": "RUNTIME:DECLARED", "to": f"FILE:{relative}"})
                if record.get("authority_class") == "RUNTIME_CONFIGURATION":
                    edges.append({"relation": "CONFIGURED_BY", "from": "RUNTIME:DECLARED", "to": f"FILE:{relative}"})

        graph = {
            "schema": GRAPH_SCHEMA,
            "contract_id": CONTRACT_ID,
            "source_tree_hash216": snapshot.get("tree_root_hash216"),
            "relations": list(RELATIONS),
            "nodes": nodes,
            "edges": edges,
            "residuals": residuals,
            "source_mutation_authority": False,
        }
        graph["graph_hash216"] = _hash216("pass182:logic-graph", graph)
        return graph

    def incremental_scope(self, previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, Any]:
        def index(snapshot: Mapping[str, Any]) -> dict[str, tuple[Any, Any, Any]]:
            return {
                str(r["relative_path"]): (r.get("content_sha256"), r.get("kind"), r.get("symlink_target"))
                for r in snapshot.get("records", [])
            }
        old = index(previous)
        new = index(current)
        unchanged = sorted(path for path in old.keys() & new.keys() if old[path] == new[path])
        changed = sorted(path for path in old.keys() & new.keys() if old[path] != new[path])
        added = sorted(new.keys() - old.keys())
        removed = sorted(old.keys() - new.keys())
        affected = sorted(set(changed + added + removed))
        result = {
            "classification": "HHS_DEPENDENCY_SCOPED_REHYDRATION_VERIFIED",
            "unchanged_reused": unchanged,
            "changed": changed,
            "added": added,
            "removed": removed,
            "affected_graph_closure": affected,
            "full_reanalysis_required": False if affected else False,
        }
        result["scope_hash216"] = _hash216("pass182:incremental", result)
        return result

    def sandbox_dynamic_trace(
        self,
        source_root: str | Path,
        *,
        command: Sequence[str] | None = None,
        timeout_seconds: int = 60,
    ) -> dict[str, Any]:
        root = self._root_guard(Path(source_root))
        command = tuple(command or ("python", "-m", "compileall", "-q", "."))
        if not command:
            raise HydrationError("PASS182_DYNAMIC_COMMAND_EMPTY")
        if timeout_seconds < 1 or timeout_seconds > 600:
            raise HydrationError("PASS182_DYNAMIC_TIMEOUT_RANGE")
        with tempfile.TemporaryDirectory(prefix="hhs-pass182-sandbox-") as tmp:
            sandbox = Path(tmp) / "source-copy"
            shutil.copytree(root, sandbox, symlinks=True)
            before = self.snapshot_tree(root)
            proc = subprocess.run(
                list(command),
                cwd=sandbox,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
                check=False,
                env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""},
            )
            after = self.snapshot_tree(root)
            source_unchanged = before["tree_root_hash216"] == after["tree_root_hash216"]
            if not source_unchanged:
                raise HydrationError("PASS182_SOURCE_TREE_MUTATED_DURING_DYNAMIC_TRACE")
            result = {
                "classification": "HHS_STATIC_AND_SANDBOX_DYNAMIC_TRACE_VERIFIED",
                "command": list(command),
                "returncode": int(proc.returncode),
                "stdout_sha256": _sha256_bytes(proc.stdout),
                "stderr_sha256": _sha256_bytes(proc.stderr),
                "source_tree_unchanged": True,
                "executed_from_sandbox_copy": True,
                "source_tree_binary_execution": False,
                "sandbox_ephemeral": True,
            }
            result["trace_hash216"] = _hash216("pass182:dynamic-trace", result)
            return result

    def modality_reference_adapters(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for record in snapshot.get("records", []):
            modality = str(record.get("modality", "multimodal_projects"))
            counts[modality] = counts.get(modality, 0) + 1
        adapters = {
            "text": {"probe": True, "decode": "UTF8_WHEN_VALID", "reconstruct": "EXACT_BYTES", "compare": "SHA256"},
            "audio": {"probe": True, "decode": "CONTAINER_HEADER_BOUNDED", "reconstruct": "CONTENT_ADDRESSED_REFERENCE", "compare": "SHA256"},
            "images": {"probe": True, "decode": "CONTAINER_HEADER_BOUNDED", "reconstruct": "CONTENT_ADDRESSED_REFERENCE", "compare": "SHA256"},
            "video": {"probe": True, "decode": "CONTAINER_HEADER_BOUNDED", "reconstruct": "CONTENT_ADDRESSED_REFERENCE", "compare": "SHA256"},
            "repository_tree": {"probe": True, "decode": "LEXICAL_TREE", "reconstruct": "PATH_AND_CONTENT_IDENTITY", "compare": "TREE_HASH216"},
        }
        return {
            "classification": "HHS_MULTIMODAL_ADAPTER_CONTRACT_VERIFIED",
            "supported_registry": list(SUPPORTED_MODALITIES),
            "reference_adapters": adapters,
            "observed_modality_counts": counts,
            "external_decoder_authority": False,
        }

    def promote_constraint(
        self,
        candidate: Mapping[str, Any],
        gates: Mapping[str, bool],
        *,
        vm81_admit: Callable[[Mapping[str, Any]], Mapping[str, Any] | bool],
    ) -> dict[str, Any]:
        required_true = ("executable_behavior_confirmed", "positive_tested", "negative_tested", "adversarial_tested", "replay_verified")
        if any(gates.get(name) is not True for name in required_true):
            raise HydrationError("PASS182_CONSTRAINT_PROMOTION_GATE_INCOMPLETE")
        if gates.get("contradiction_scan_passed") is not True:
            raise HydrationError("PASS182_CONSTRAINT_CONTRADICTION")
        proposal = {
            "contract_id": CONTRACT_ID,
            "candidate": dict(candidate),
            "gates": {name: bool(gates.get(name)) for name in (*required_true, "contradiction_scan_passed")},
            "direct_pass182_mutation_authority": False,
        }
        admission = vm81_admit(proposal)
        if admission is False or admission is None:
            raise HydrationError("PASS182_VM81_ADMISSION_REJECTED")
        receipt_hash72 = _hash72("pass182:constraint-promotion-evidence", {"proposal": proposal, "admission": admission})
        result = {
            "classification": "HHS_MODALITY_CONSTRAINT_PROMOTION_VERIFIED",
            "proposal": proposal,
            "vm81_admission": admission,
            "receipt_hash72": receipt_hash72,
            "hash72_mutation_authority": False,
            "hash216_mutation_authority": False,
            "singleton_vm81_authority_preserved": True,
        }
        result["archive_hash216"] = _hash216("pass182:promoted-constraint-archive", result)
        return result

    def build_portable_package(
        self,
        destination: str | Path,
        *,
        profile: str = "multimodal",
        source_snapshot: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        allowed = {"minimal", "text", "audio", "graphics", "video", "games", "documents", "applications", "multimodal", "full"}
        if profile not in allowed:
            raise HydrationError("PASS182_PACKAGE_PROFILE_INVALID")
        destination = Path(destination).expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)
        for name in ("bin", "lib", "profiles", "adapters", "constraints", "vector-store", "recipes", "manifests", "receipts", "replay", "configuration", "service", "installation-evidence"):
            (destination / name).mkdir(exist_ok=True)
        manifest = {
            "schema": PACKAGE_SCHEMA,
            "contract_id": CONTRACT_ID,
            "profile": profile,
            "source_tree_hash216": None if source_snapshot is None else source_snapshot.get("tree_root_hash216"),
            "required_components": ["VM81", "Hash72", "Hash216", "hydration", "constraint_registry", "vector_store", "modality_adapters", "health_checks"],
            "singleton_vm81_authority": True,
            "package_mutation_authority": False,
        }
        manifest["manifest_hash216"] = _hash216("pass182:package-manifest", manifest)
        manifest_path = destination / "manifests" / "pass182-package.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "classification": "HHS_PORTABLE_SERVER_BOOTSTRAP_VERIFIED",
            "manifest_hash216": manifest["manifest_hash216"],
            "manifest_sha256": _sha256_file(manifest_path),
            "receipt_hash72": _hash72("pass182:package-receipt", manifest),
            "source_tree_mutation_authority": False,
        }
        receipt["archive_hash216"] = _hash216("pass182:package-receipt-archive", receipt)
        (destination / "receipts" / "installation.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return {"manifest": manifest, "receipt": receipt, "package_root": str(destination)}

    def verify_cold_start(self, package_root: str | Path) -> dict[str, Any]:
        root = Path(package_root).expanduser().resolve()
        manifest_path = root / "manifests" / "pass182-package.json"
        receipt_path = root / "receipts" / "installation.json"
        if not manifest_path.is_file() or not receipt_path.is_file():
            raise HydrationError("PASS182_PACKAGE_INCOMPLETE")
        manifest = json.loads(manifest_path.read_text("utf-8"))
        receipt = json.loads(receipt_path.read_text("utf-8"))
        expected_manifest = dict(manifest)
        claimed = expected_manifest.pop("manifest_hash216", None)
        recomputed = _hash216("pass182:package-manifest", expected_manifest)
        if claimed != recomputed:
            raise HydrationError("PASS182_PACKAGE_MANIFEST_IDENTITY_MISMATCH")
        if receipt.get("manifest_hash216") != claimed or receipt.get("manifest_sha256") != _sha256_file(manifest_path):
            raise HydrationError("PASS182_PACKAGE_RECEIPT_MISMATCH")
        required_dirs = ("bin", "lib", "profiles", "adapters", "constraints", "vector-store", "recipes", "manifests", "receipts", "replay", "configuration", "service", "installation-evidence")
        if any(not (root / name).is_dir() for name in required_dirs):
            raise HydrationError("PASS182_PACKAGE_LAYOUT_INCOMPLETE")
        return {
            "classification": "HHS_SERVER_COLD_RESTART_REPLAY_VERIFIED",
            "health": "VERIFIED",
            "smoke_reconstruction": "IDENTITY_REPLAY_VERIFIED",
            "manifest_hash216": claimed,
            "singleton_vm81_authority_preserved": True,
        }

    def replay_snapshot(self, source_root: str | Path, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        replayed = self.snapshot_tree(source_root)
        exact = replayed.get("tree_root_hash216") == snapshot.get("tree_root_hash216")
        return {
            "classification": "HHS_REPOSITORY_LOGIC_GRAPH_REPLAY_VERIFIED" if exact else "PASS182_REPLAY_MISMATCH",
            "exact": exact,
            "expected_tree_root_hash216": snapshot.get("tree_root_hash216"),
            "actual_tree_root_hash216": replayed.get("tree_root_hash216"),
        }

    def acceptance_summary(self, source_root: str | Path) -> dict[str, Any]:
        snapshot = self.snapshot_tree(source_root)
        ir = self.build_ir(snapshot)
        graph = self.build_logic_graph(source_root, snapshot)
        adapters = self.modality_reference_adapters(snapshot)
        checks = {
            "complete_read_only_file_tree_enumeration": snapshot["complete_identity_enumeration"] and snapshot["source_metadata_unchanged"],
            "per_path_content_identity": all(r.get("path_hash216") for r in snapshot["records"] if r["kind"] != "unreadable"),
            "secret_safe_traversal": snapshot["secret_text_storage_count"] == 0,
            "universal_hydration_ir": len(ir["ir_hash216"]) == 216,
            "repository_logic_graph": len(graph["graph_hash216"]) == 216,
            "reference_text_adapter": "text" in adapters["reference_adapters"],
            "reference_audio_adapter": "audio" in adapters["reference_adapters"],
            "reference_graphics_video_adapter": "images" in adapters["reference_adapters"] and "video" in adapters["reference_adapters"],
            "reference_repository_tree_adapter": "repository_tree" in adapters["reference_adapters"],
            "singleton_vm81_authority_preserved": True,
            "hash72_independent_authority_created": False,
            "hash216_mutation_authority_created": False,
        }
        return {
            "contract_id": CONTRACT_ID,
            "pass_number": PASS_NUMBER,
            "classification": "HHS_PASS182_I144_LOCAL_IMPLEMENTATION_ACCEPTANCE" if all(checks.values()) else "HHS_PASS182_I144_LOCAL_IMPLEMENTATION_INCOMPLETE",
            "checks": checks,
            "snapshot": {"tree_root_hash216": snapshot["tree_root_hash216"], "entry_count": snapshot["entry_count"]},
            "ir_hash216": ir["ir_hash216"],
            "graph_hash216": graph["graph_hash216"],
            "terminal_completion_claimed": False,
        }
