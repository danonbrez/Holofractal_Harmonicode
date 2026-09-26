"""Pass 220 Lane 5 global Pass-219/220 tool hydration.

This layer does not replace or alter Lane 5 route selection.  It creates the
global constraint surface requested by Pass 220 over the already-existing
Lane 5 selector and warms repository-validated Pass 219/220 services and merged
pull-request history into the inherited encrypted Hash216 vector store as
candidate-only tools in the exact 5,184-bit multimodal knowledge graph.

Repository source/history remain authority.  Warm vector memory is a derived
retrieval/cache projection and has no VM81, Hash72, Hash216 mint, persistence,
or route-selection authority.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_pass219_global_raw5184_serialization_hydration_v1 import (
    serialize_raw5184_bytes,
)
from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    GRAPH_SCHEMA as I042_GRAPH_SCHEMA,
    shared_multimodal_root_sha256,
)
from hhs_runtime.pass174.runtime import Hash216Array
from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore

SCHEMA = "HHS_PASS_220_LANE5_GLOBAL_PASS219_220_TOOL_HYDRATION_V1"
VERSION = "1.0.0"
TOOL_SCHEMA = "HHS_PASS_220_LANE5_5184_KNOWLEDGE_TOOL_V1"
WARM_SCHEMA = "HHS_PASS_220_LANE5_PASS219_220_WARM_VECTOR_RECEIPT_V1"
GRAPH_SCHEMA = "HHS_PASS_220_LANE5_PASS219_220_5184_TOOL_GRAPH_V1"
CPP_SURFACE_SYMBOL = "hhs_pass220_lane5_global_tool_surface_validate_v1"
CPP_SURFACE_VERSION = 0x00010001
PROJECTION_BYTES = 648
PROJECTION_BITS = 5184
HASH216_CHARS = 216

GLOBAL_CONSTRAINTS: tuple[str, ...] = (
    "LANE5_ROUTE_SELECTION_ALGORITHM_UNCHANGED",
    "CIRCULAR_PHASE_FIBER_IS_GLOBAL_CONSTRAINT_NOT_SELECTOR_REPLACEMENT",
    "ALL_REGISTERED_PASS219_PASS220_SERVICES_PRESENT_IN_WARM_TOOL_GRAPH",
    "ALL_MERGED_PASS219_PASS220_PULL_REQUESTS_PRESENT_IN_WARM_TOOL_GRAPH",
    "EVERY_WARM_TOOL_HAS_EXACT_5184_BIT_PROJECTION",
    "EVERY_WARM_TOOL_HAS_ORDERED_3XHASH72_HASH216_IDENTITY",
    "EVERY_WARM_TOOL_BINDS_VALID_CPP_LANE5_TOOL_SURFACE",
    "EVERY_WARM_TOOL_BINDS_PASS220_I042_SHARED_MULTIMODAL_ROOT",
    "WARM_VECTOR_STORE_IS_DERIVED_CANDIDATE_CACHE_ONLY",
    "REPOSITORY_SOURCE_AND_MERGE_HISTORY_REMAIN_AUTHORITY",
    "NO_WARM_TOOL_VM81_MUTATION_AUTHORITY",
    "NO_WARM_TOOL_HASH72_MINT_AUTHORITY",
    "NO_WARM_TOOL_HASH216_CANONICAL_MINT_AUTHORITY",
    "NO_WARM_TOOL_CANONICAL_PERSISTENCE_AUTHORITY",
    "NO_WARM_TOOL_FLOATING_POINT_CANONICAL_AUTHORITY",
    "WARM_CACHE_REPLAY_NEVER_BYPASSES_LANE5_OR_VM81_ADMISSION",
)

_PASS219_RE = re.compile(r"(?i)pass[_\s-]?219")
_PASS220_RE = re.compile(r"(?i)pass[_\s-]?220")
_PR_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)merge\s+pr\s+#(\d+)"),
    re.compile(r"(?i)merge\s+pull\s+request\s+#(\d+)"),
    re.compile(r"(?i)\bpr\s+#(\d+)"),
    re.compile(r"\(#(\d+)\)"),
)


class Pass220Lane5GlobalToolHydrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class WarmTool:
    tool_id: str
    tool_id_sha256: str
    kind: str
    kind_code: int
    pass_scopes: tuple[int, ...]
    source_identity: str
    provenance: Mapping[str, Any]
    hash216: str
    previous_hash72: str
    current_hash72: str
    receipt_hash72: str
    projection_bits: int
    projection_bytes: int
    projection_sha256: str
    projection_popcount: int
    i042_shared_root_sha256: str
    cpp_surface_symbol: str
    cpp_surface_version: int
    candidate_only: bool = True
    lane5_selection_unchanged: bool = True
    canonical_vm81_mutation_authority: bool = False
    canonical_hash72_authority: bool = False
    canonical_hash216_authority: bool = False
    canonical_persistence_authority: bool = False
    floating_point_canonical_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": TOOL_SCHEMA,
            "tool_id": self.tool_id,
            "tool_id_sha256": self.tool_id_sha256,
            "kind": self.kind,
            "kind_code": self.kind_code,
            "pass_scopes": list(self.pass_scopes),
            "source_identity": self.source_identity,
            "provenance": dict(self.provenance),
            "hash216": self.hash216,
            "previous_hash72": self.previous_hash72,
            "current_hash72": self.current_hash72,
            "receipt_hash72": self.receipt_hash72,
            "projection_bits": self.projection_bits,
            "projection_bytes": self.projection_bytes,
            "projection_sha256": self.projection_sha256,
            "projection_popcount": self.projection_popcount,
            "i042_shared_root_sha256": self.i042_shared_root_sha256,
            "cpp_surface_symbol": self.cpp_surface_symbol,
            "cpp_surface_version": self.cpp_surface_version,
            "candidate_only": self.candidate_only,
            "lane5_selection_unchanged": self.lane5_selection_unchanged,
            "canonical_vm81_mutation_authority": self.canonical_vm81_mutation_authority,
            "canonical_hash72_authority": self.canonical_hash72_authority,
            "canonical_hash216_authority": self.canonical_hash216_authority,
            "canonical_persistence_authority": self.canonical_persistence_authority,
            "floating_point_canonical_authority": self.floating_point_canonical_authority,
        }


def _canonical(value: Any) -> bytes:
    def reject_float(item: Any, path: str = "$") -> None:
        if isinstance(item, float):
            raise Pass220Lane5GlobalToolHydrationError(
                f"floating-point warm-tool metadata forbidden at {path}"
            )
        if isinstance(item, Mapping):
            for key, value in item.items():
                reject_float(value, f"{path}.{key}")
        elif isinstance(item, (list, tuple)):
            for index, value in enumerate(item):
                reject_float(value, f"{path}[{index}]")
    reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _scopes(text: str) -> tuple[int, ...]:
    scopes: list[int] = []
    if _PASS219_RE.search(text):
        scopes.append(219)
    if _PASS220_RE.search(text):
        scopes.append(220)
    return tuple(scopes)


def _literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return None


def _flatten_literal_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(
            f"{_flatten_literal_text(key)} {_flatten_literal_text(item)}"
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set)):
        return " ".join(_flatten_literal_text(item) for item in value)
    return ""


def discover_registered_pass219_220_services(repository_root: str | Path) -> list[dict[str, Any]]:
    root = Path(repository_root).resolve()
    registry_path = root / "hhs_runtime" / "hhs_service_registry_v1.py"
    source = registry_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(registry_path))
    records: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if not isinstance(function, ast.Attribute) or function.attr != "register_function":
            continue
        values = {
            keyword.arg: _literal(keyword.value)
            for keyword in node.keywords
            if keyword.arg is not None
        }
        joined = " ".join(
            _flatten_literal_text(value) for value in values.values()
        )
        scopes = _scopes(joined)
        if not scopes:
            continue
        name = values.get("name")
        module = values.get("module")
        target = values.get("function")
        if not all(isinstance(item, str) and item for item in (name, module, target)):
            raise Pass220Lane5GlobalToolHydrationError(
                "Pass 219/220 service registration must expose literal name/module/function"
            )
        record = {
            "kind": "REGISTERED_SERVICE",
            "name": name,
            "module": module,
            "function": target,
            "service_type": str(values.get("service_type") or "runtime"),
            "pass_scopes": list(scopes),
            "registry_path": registry_path.relative_to(root).as_posix(),
            "contract_schemas": list(values.get("contract_schemas") or []),
            "witness_schemas": list(values.get("witness_schemas") or []),
            "validators": list(values.get("validators") or []),
            "guards": list(values.get("guards") or []),
            "rejection_codes": list(values.get("rejection_codes") or []),
        }
        records.append(record)

    records.sort(key=lambda item: (item["name"], item["module"], item["function"]))
    seen: set[str] = set()
    for record in records:
        if record["name"] in seen:
            raise Pass220Lane5GlobalToolHydrationError(
                f"duplicate Pass 219/220 service inventory name: {record['name']}"
            )
        seen.add(record["name"])
    return records


def _git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Pass220Lane5GlobalToolHydrationError(
            f"repository git history unavailable: {' '.join(args)}"
        ) from exc
    return result.stdout


def _pr_numbers(message: str) -> tuple[int, ...]:
    found: set[int] = set()
    for pattern in _PR_PATTERNS:
        found.update(int(value) for value in pattern.findall(message))
    return tuple(sorted(found))


def discover_merged_pass219_220_pull_requests(
    repository_root: str | Path,
    *,
    git_ref: str = "HEAD",
) -> list[dict[str, Any]]:
    root = Path(repository_root).resolve()
    raw = _git(
        root,
        "log",
        "--first-parent",
        "--format=%H%x1f%P%x1f%s%x1f%b%x1e",
        git_ref,
    )
    records: dict[int, dict[str, Any]] = {}
    for chunk in raw.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        fields = chunk.split("\x1f")
        if len(fields) < 4:
            continue
        sha, parents_text, subject = fields[0], fields[1], fields[2]
        body = "\x1f".join(fields[3:])
        message = subject + "\n" + body
        numbers = _pr_numbers(message)
        if not numbers:
            continue
        parents = [value for value in parents_text.split() if value]
        if parents:
            changed_text = _git(root, "diff", "--name-only", parents[0], sha)
        else:
            changed_text = _git(
                root,
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--name-only",
                "-r",
                sha,
            )
        changed_paths = tuple(
            sorted({line.strip() for line in changed_text.splitlines() if line.strip()})
        )
        path_text = "\n".join(changed_paths)
        scopes = tuple(sorted(set(_scopes(message) + _scopes(path_text))))
        if not scopes:
            continue
        for number in numbers:
            prior = records.get(number)
            record = {
                "kind": "MERGED_PULL_REQUEST",
                "pr_number": number,
                "merge_commit_sha": sha,
                "subject": subject,
                "pass_scopes": list(scopes),
                "changed_paths": list(changed_paths),
                "changed_path_count": len(changed_paths),
            }
            if prior is not None and prior["merge_commit_sha"] != sha:
                raise Pass220Lane5GlobalToolHydrationError(
                    f"pull request #{number} appears in multiple first-parent commits"
                )
            records[number] = record
    return [records[number] for number in sorted(records)]


def _projection_bytes(payload: Mapping[str, Any]) -> bytes:
    seed = sha256(_canonical(payload)).digest()
    out = bytearray()
    counter = 0
    while len(out) < PROJECTION_BYTES:
        out.extend(sha256(seed + counter.to_bytes(8, "big")).digest())
        counter += 1
    raw = bytes(out[:PROJECTION_BYTES])
    return serialize_raw5184_bytes(raw)


def _tool(
    *,
    kind: str,
    kind_code: int,
    source_identity: str,
    pass_scopes: Sequence[int],
    provenance: Mapping[str, Any],
    i042_shared_root: str,
) -> tuple[WarmTool, bytes]:
    normalized_scopes = tuple(sorted({int(value) for value in pass_scopes}))
    if not normalized_scopes or not set(normalized_scopes).issubset({219, 220}):
        raise Pass220Lane5GlobalToolHydrationError("invalid Pass 219/220 tool scope")
    base = {
        "schema": TOOL_SCHEMA,
        "kind": kind,
        "kind_code": int(kind_code),
        "source_identity": source_identity,
        "pass_scopes": list(normalized_scopes),
        "provenance": dict(provenance),
        "i042_shared_root_sha256": i042_shared_root,
        "global_constraints": list(GLOBAL_CONSTRAINTS),
        "cpp_surface_symbol": CPP_SURFACE_SYMBOL,
        "cpp_surface_version": CPP_SURFACE_VERSION,
        "candidate_only": True,
        "lane5_selection_unchanged": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_canonical_authority": False,
    }
    tool_id_sha256 = sha256(_canonical(base)).hexdigest()
    tool_id = f"{kind.lower()}:{source_identity}"
    previous = hash72_digest(
        {"domain": SCHEMA, "lane": "PREVIOUS", "version": VERSION},
        {"tool_id_sha256": tool_id_sha256, "pass_scopes": list(normalized_scopes)},
    )
    current = hash72_digest(
        {"domain": SCHEMA, "lane": "CHANGE", "version": VERSION},
        base,
    )
    receipt = hash72_digest(
        {"domain": SCHEMA, "lane": "RECEIPT", "version": VERSION},
        {
            "tool_id_sha256": tool_id_sha256,
            "global_constraints": list(GLOBAL_CONSTRAINTS),
            "cpp_surface_symbol": CPP_SURFACE_SYMBOL,
        },
    )
    hash216 = previous + current + receipt
    if len(hash216) != HASH216_CHARS:
        raise Pass220Lane5GlobalToolHydrationError("Hash216 width drift")
    projection = _projection_bytes(
        {
            "tool_id_sha256": tool_id_sha256,
            "hash216": hash216,
            "i042_shared_root_sha256": i042_shared_root,
        }
    )
    tool = WarmTool(
        tool_id=tool_id,
        tool_id_sha256=tool_id_sha256,
        kind=kind,
        kind_code=kind_code,
        pass_scopes=normalized_scopes,
        source_identity=source_identity,
        provenance=dict(provenance),
        hash216=hash216,
        previous_hash72=previous,
        current_hash72=current,
        receipt_hash72=receipt,
        projection_bits=PROJECTION_BITS,
        projection_bytes=len(projection),
        projection_sha256=sha256(projection).hexdigest(),
        projection_popcount=sum(byte.bit_count() for byte in projection),
        i042_shared_root_sha256=i042_shared_root,
        cpp_surface_symbol=CPP_SURFACE_SYMBOL,
        cpp_surface_version=CPP_SURFACE_VERSION,
    )
    return tool, projection


def build_pass219_220_warm_tool_graph(
    repository_root: str | Path,
    *,
    git_ref: str = "HEAD",
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    shared_root = shared_multimodal_root_sha256()
    services = discover_registered_pass219_220_services(root)
    prs = discover_merged_pass219_220_pull_requests(root, git_ref=git_ref)

    tools: list[WarmTool] = []
    projections: dict[str, bytes] = {}
    for service in services:
        tool, projection = _tool(
            kind="REGISTERED_SERVICE",
            kind_code=1,
            source_identity=str(service["name"]),
            pass_scopes=service["pass_scopes"],
            provenance=service,
            i042_shared_root=shared_root,
        )
        tools.append(tool)
        projections[tool.tool_id_sha256] = projection

    for pr in prs:
        tool, projection = _tool(
            kind="MERGED_PULL_REQUEST",
            kind_code=2,
            source_identity=f"PR#{pr['pr_number']}",
            pass_scopes=pr["pass_scopes"],
            provenance=pr,
            i042_shared_root=shared_root,
        )
        tools.append(tool)
        projections[tool.tool_id_sha256] = projection

    tools.sort(key=lambda item: (item.kind_code, item.source_identity, item.tool_id_sha256))
    ids = [item.tool_id_sha256 for item in tools]
    if len(ids) != len(set(ids)):
        raise Pass220Lane5GlobalToolHydrationError("duplicate warm-tool identity")

    service_ids = {item.source_identity for item in tools if item.kind_code == 1}
    expected_service_ids = {str(item["name"]) for item in services}
    pr_ids = {
        int(item.source_identity.removeprefix("PR#"))
        for item in tools
        if item.kind_code == 2
    }
    expected_pr_ids = {int(item["pr_number"]) for item in prs}
    coverage = {
        "registered_service_inventory_complete": service_ids == expected_service_ids,
        "merged_pr_inventory_complete": pr_ids == expected_pr_ids,
        "all_tools_exact_5184": all(item.projection_bits == PROJECTION_BITS for item in tools),
        "all_tools_hash216_width": all(len(item.hash216) == HASH216_CHARS for item in tools),
        "all_tools_cpp_surface_bound": all(
            item.cpp_surface_symbol == CPP_SURFACE_SYMBOL
            and item.cpp_surface_version == CPP_SURFACE_VERSION
            for item in tools
        ),
        "all_tools_candidate_only": all(item.candidate_only for item in tools),
        "lane5_selection_unchanged": all(item.lane5_selection_unchanged for item in tools),
        "no_tool_canonical_authority": all(
            not item.canonical_vm81_mutation_authority
            and not item.canonical_hash72_authority
            and not item.canonical_hash216_authority
            and not item.canonical_persistence_authority
            and not item.floating_point_canonical_authority
            for item in tools
        ),
    }
    if not tools or not all(coverage.values()):
        raise Pass220Lane5GlobalToolHydrationError(
            f"global Pass 219/220 warm-tool coverage failed: {coverage}"
        )

    tool_dicts = [item.to_dict() for item in tools]
    graph_body = {
        "schema": GRAPH_SCHEMA,
        "version": VERSION,
        "parent_multimodal_graph_schema": I042_GRAPH_SCHEMA,
        "i042_shared_root_sha256": shared_root,
        "projection_bits": PROJECTION_BITS,
        "global_constraints": list(GLOBAL_CONSTRAINTS),
        "registered_service_count": len(services),
        "merged_pull_request_count": len(prs),
        "tool_count": len(tools),
        "coverage": coverage,
        "nodes": tool_dicts,
        "edges": [
            {
                "source_tool_id_sha256": item.tool_id_sha256,
                "relation": "LANE5_TOOL_TO_I042_SHARED_ROOT",
                "target_shared_root_sha256": shared_root,
                "candidate_only": True,
            }
            for item in tools
        ],
        "authority": {
            "lane5_route_selection_changed": False,
            "vector_store_is_source_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
        },
    }
    graph_root = sha256(_canonical(graph_body)).hexdigest()
    return {
        **graph_body,
        "graph_root_sha256": graph_root,
        "_projection_bytes_by_tool_id_sha256": projections,
    }


def public_tool_graph(graph: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(key): value
        for key, value in graph.items()
        if key != "_projection_bytes_by_tool_id_sha256"
    }


def cpp_manifest_lines(graph: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    for tool in graph["nodes"]:
        scopes = set(int(value) for value in tool["pass_scopes"])
        fields = (
            tool["tool_id_sha256"],
            str(int(tool["kind_code"])),
            "1" if 219 in scopes else "0",
            "1" if 220 in scopes else "0",
            tool["hash216"],
            tool["projection_sha256"],
        )
        if any("|" in field or "\n" in field for field in fields):
            raise Pass220Lane5GlobalToolHydrationError("unsafe C++ manifest field")
        lines.append("|".join(fields))
    return lines


def warm_pass219_220_tool_vector_store(
    repository_root: str | Path,
    state_root: str | Path,
    *,
    git_ref: str = "HEAD",
    vector_key: bytes | None = None,
) -> dict[str, Any]:
    graph = build_pass219_220_warm_tool_graph(repository_root, git_ref=git_ref)
    projections: Mapping[str, bytes] = graph["_projection_bytes_by_tool_id_sha256"]
    state = Path(state_root).resolve()
    state.mkdir(parents=True, exist_ok=True)
    store = PersistentEncryptedVectorStore(
        state / "pass219_220_lane5_tools.sqlite3",
        key=vector_key,
        key_path=state / "pass219_220_lane5_tools.key",
    )
    admitted = 0
    reused = 0
    object_ids: list[str] = []
    try:
        existing = {obj.operation_key: obj for obj in store.objects()}
        for logical_step, tool in enumerate(graph["nodes"], start=1):
            operation_key = (
                "pass220.lane5.5184.tool."
                + str(tool["kind"]).lower()
                + "."
                + str(tool["tool_id_sha256"])
            )
            previous = str(tool["previous_hash72"])
            current = str(tool["current_hash72"])
            receipt = str(tool["receipt_hash72"])
            expected_hash216 = str(tool["hash216"])
            operation_identity = sha256(
                (SCHEMA + ":" + str(tool["tool_id_sha256"])).encode("ascii")
            ).hexdigest()
            genesis = sha256(b"HHS-PASS220-LANE5-GLOBAL-TOOL-HYDRATION-GENESIS").hexdigest()
            legacy = sha256(_canonical(tool)).hexdigest()
            lanes = Hash216Array.build(
                previous,
                current,
                receipt,
                genesis_identity=genesis,
                logical_step=logical_step,
                operation_identity=operation_identity,
                legacy_foundation_root=legacy,
            )
            if lanes.combined != expected_hash216:
                raise Pass220Lane5GlobalToolHydrationError(
                    "Hash216 vector-store lane identity drift"
                )

            prior = existing.get(operation_key)
            if (
                prior is not None
                and prior.output_hash72 == current
                and prior.hash216.combined == expected_hash216
            ):
                prior.hash216.verify()
                object_ids.append(prior.object_id)
                reused += 1
                continue

            snapshot = projections[str(tool["tool_id_sha256"])]
            obj = store.admit(
                operation_key=operation_key,
                logical_step=logical_step,
                input_hash72=previous,
                output_hash72=current,
                operation_identity_sha256=operation_identity,
                hash216=lanes,
                output_snapshot=snapshot,
                legacy_foundation_root=legacy,
                genesis_identity=genesis,
                direct_cost_units=1,
                changed_bits=sum(byte.bit_count() for byte in snapshot),
                parent_object_id=None,
            )
            object_ids.append(obj.object_id)
            admitted += 1

        status = store.storage_status()
    finally:
        store.close()

    return {
        "schema": WARM_SCHEMA,
        "version": VERSION,
        "graph": public_tool_graph(graph),
        "state_root": str(state),
        "vector_store": status,
        "warmed_tool_count": len(graph["nodes"]),
        "newly_admitted_count": admitted,
        "reused_count": reused,
        "vector_object_ids": object_ids,
        "all_tools_warmed": admitted + reused == len(graph["nodes"]),
        "lane5_selection_changed": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
    }


def global_tool_hydration_self_test(
    repository_root: str | Path | None = None,
) -> dict[str, Any]:
    root = (
        Path(repository_root).resolve()
        if repository_root is not None
        else Path(__file__).resolve().parents[1]
    )
    graph = build_pass219_220_warm_tool_graph(root)
    public = public_tool_graph(graph)
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS",
        "registered_service_count": public["registered_service_count"],
        "merged_pull_request_count": public["merged_pull_request_count"],
        "tool_count": public["tool_count"],
        "projection_bits": public["projection_bits"],
        "graph_root_sha256": public["graph_root_sha256"],
        "coverage": public["coverage"],
        "global_constraints": list(GLOBAL_CONSTRAINTS),
        "lane5_selection_changed": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
    }


__all__ = [
    "CPP_SURFACE_SYMBOL",
    "CPP_SURFACE_VERSION",
    "GLOBAL_CONSTRAINTS",
    "GRAPH_SCHEMA",
    "HASH216_CHARS",
    "PROJECTION_BITS",
    "PROJECTION_BYTES",
    "SCHEMA",
    "TOOL_SCHEMA",
    "VERSION",
    "WARM_SCHEMA",
    "Pass220Lane5GlobalToolHydrationError",
    "WarmTool",
    "build_pass219_220_warm_tool_graph",
    "cpp_manifest_lines",
    "discover_merged_pass219_220_pull_requests",
    "discover_registered_pass219_220_services",
    "global_tool_hydration_self_test",
    "public_tool_graph",
    "warm_pass219_220_tool_vector_store",
]
