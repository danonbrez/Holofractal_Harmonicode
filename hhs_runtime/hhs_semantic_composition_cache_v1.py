"""
HHS Semantic Composition Cache v1
=================================

Pass 044 turns the existing semantic storage/search/vector substrate into a
kernel-derived composition memory.  The semantic database accelerates runtime
composition, but it never becomes an authority source: every cache hit is valid
only while dependency roots still match the kernel conformance graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import compose_surface_pipeline
from hhs_runtime.hhs_semantic_memory_guard_v1 import commit_semantic_record, semantic_hash72
from hhs_runtime.hhs_loshu_phase_embedding_v1 import embed_sequence
from hhs_runtime.hhs_receipt_vector_index_v1 import HHSReceiptVectorIndex
from hhs_runtime.hhs_expanded_state_decay_lifecycle_v1 import evaluate_decay_window

VERSION = "PASS_044_SEMANTIC_COMPOSITION_CACHE_V1"
CACHE_SCHEMA = "HHS_SEMANTIC_COMPOSITION_CACHE_V1"
ENTRY_SCHEMA = "HHS_COMPOSITION_CACHE_ENTRY_V1"
DEPENDENCY_ROOT_SCHEMA = "HHS_COMPOSITION_DEPENDENCY_ROOTS_V1"

REJECT_COMPOSITION_CACHE_STALE = "REJECT_COMPOSITION_CACHE_STALE"
REJECT_COMPOSITION_CACHE_WITHOUT_DEPENDENCY_ROOTS = "REJECT_COMPOSITION_CACHE_WITHOUT_DEPENDENCY_ROOTS"
REJECT_CACHE_HIT_WITH_INVALID_CONFORMANCE_ROOT = "REJECT_CACHE_HIT_WITH_INVALID_CONFORMANCE_ROOT"
REJECT_CACHED_PIPELINE_WITHOUT_RECONSTRUCTION_RECIPE = "REJECT_CACHED_PIPELINE_WITHOUT_RECONSTRUCTION_RECIPE"
REJECT_CACHE_ENTRY_AFTER_DECAY_EXPIRATION = "REJECT_CACHE_ENTRY_AFTER_DECAY_EXPIRATION"
REJECT_SEMANTIC_DB_AS_AUTHORITY_SOURCE = "REJECT_SEMANTIC_DB_AS_AUTHORITY_SOURCE"

DEFAULT_CACHE_PATH = Path("demo_reports/hhs_semantic_composition_cache_pass044.json")


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def _list(values: Optional[Iterable[Any]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        text = str(value).strip()
        if text:
            out.append(text)
    return sorted(dict.fromkeys(out))


def build_dependency_roots(plan: Mapping[str, Any], surface_map: Mapping[str, Any]) -> Dict[str, Any]:
    pipeline = plan.get("pipeline", {}) if isinstance(plan.get("pipeline"), Mapping) else plan
    roots = {
        "schema": DEPENDENCY_ROOT_SCHEMA,
        "version": VERSION,
        "surface_id": pipeline.get("surface_id") or plan.get("surface_id"),
        "operation": pipeline.get("operation") or plan.get("operation"),
        "invariant_registry_root": str(surface_map.get("invariant_registry_root_hash72") or surface_map.get("registry_root_hash72") or surface_map.get("conformance_root_hash72")),
        "conformance_graph_root": str(surface_map.get("conformance_root_hash72")),
        "surface_derivation_root": str((pipeline.get("decision") or {}).get("derivation_hash72") or (plan.get("decision") or {}).get("derivation_hash72") or pipeline.get("pipeline_root_hash72") or ""),
        "pipeline_root": str(pipeline.get("pipeline_root_hash72") or (plan.get("witness") or {}).get("composition_root_hash72") or ""),
        "contract_schema_root": _hash72("HHS_CONTRACT_SCHEMA_CHAIN_ROOT_V1", _list(pipeline.get("contract_schemas"))),
        "witness_schema_root": _hash72("HHS_WITNESS_SCHEMA_CHAIN_ROOT_V1", _list(pipeline.get("witness_path") or pipeline.get("witness_schemas"))),
        "validator_chain_root": _hash72("HHS_VALIDATOR_CHAIN_ROOT_V1", _list(pipeline.get("validator_path") or pipeline.get("validators"))),
        "guard_chain_root": _hash72("HHS_GUARD_CHAIN_ROOT_V1", _list(pipeline.get("guard_path") or pipeline.get("guards"))),
        "execution_mode": str(pipeline.get("execution_mode") or "COMPOSE_ONLY_RECEIPT_ONLY"),
        "mutation_policy": str(pipeline.get("mutation_policy") or "NO_EXTERNAL_STATE_MUTATION"),
        "boundedness_policy": str(pipeline.get("boundedness_policy") or "PASS_044_BOUNDED_SEMANTIC_CACHE_V1"),
    }
    roots["dependency_roots_hash72"] = _hash72(DEPENDENCY_ROOT_SCHEMA, roots)
    return roots


def build_composition_cache_key(plan: Mapping[str, Any], surface_map: Mapping[str, Any]) -> str:
    roots = build_dependency_roots(plan, surface_map)
    return _hash72("HHS_SEMANTIC_COMPOSITION_CACHE_KEY_V1", roots)


def _semantic_verbatim_text(plan: Mapping[str, Any], roots: Mapping[str, Any]) -> str:
    pipeline = plan.get("pipeline", {}) if isinstance(plan.get("pipeline"), Mapping) else plan
    parts = [
        str(pipeline.get("surface_id") or plan.get("surface_id")),
        str(pipeline.get("operation") or plan.get("operation")),
        " ".join(_list(pipeline.get("invariant_ids"))),
        " ".join(_list(pipeline.get("contract_schemas"))),
        " ".join(_list(pipeline.get("validator_path"))),
        " ".join(_list(pipeline.get("witness_path"))),
        str(roots.get("conformance_graph_root")),
        str(roots.get("dependency_roots_hash72")),
    ]
    return " | ".join(parts)


def build_semantic_ml_projection(verbatim_text: str) -> Dict[str, Any]:
    """Use existing Lo Shu phase embedding as a deterministic ML/search projection.

    The embedding is advisory memory geometry only.  Authority remains with the
    kernel roots and conformance decisions.
    """

    tokens = [tok for tok in verbatim_text.replace("|", " ").split() if tok][:12] or ["empty"]
    receipt = embed_sequence(tokens, d_model=72, dimensions=4)
    states = receipt.states[: min(16, len(receipt.states))]
    projection = {
        "schema": "HHS_SEMANTIC_COMPOSITION_ML_PROJECTION_V1",
        "version": VERSION,
        "token_count": len(tokens),
        "embedding_module": receipt.module,
        "embedding_receipt_hash72": receipt.receipt_hash72,
        "sample_phase_indices": [s.phase_index for s in states],
        "sample_carriers": [s.carrier for s in states],
        "authority": "ADVISORY_SEARCH_GEOMETRY_NOT_RUNTIME_AUTHORITY",
    }
    projection["ml_projection_hash72"] = _hash72("HHS_SEMANTIC_COMPOSITION_ML_PROJECTION_V1", projection)
    return projection


@dataclass
class _ReceiptForVectorIndex:
    receipt_hash72: str
    state_hash72: str
    witness_flags: int
    route_trace: List[str]
    validation_passed: bool


class SemanticCompositionCache:
    """JSON-backed verbatim semantic cache for kernel-derived pipeline plans."""

    def __init__(self, path: str | Path = DEFAULT_CACHE_PATH) -> None:
        self.path = Path(path)
        self.vector_index = HHSReceiptVectorIndex()

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "schema": CACHE_SCHEMA,
                "version": VERSION,
                "records": [],
                "surface_index": {},
                "invariant_index": {},
                "contract_index": {},
                "validator_index": {},
                "root_index": {},
                "verbatim_index": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(dict(data), indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def build_entry(self, plan: Mapping[str, Any], surface_map: Mapping[str, Any], *, created_at_tick: int = 0, decay_window_ticks: int = 12) -> Dict[str, Any]:
        pipeline = plan.get("pipeline", {}) if isinstance(plan.get("pipeline"), Mapping) else plan
        roots = build_dependency_roots(plan, surface_map)
        cache_key = build_composition_cache_key(plan, surface_map)
        verbatim_text = _semantic_verbatim_text(plan, roots)
        ml_projection = build_semantic_ml_projection(verbatim_text)
        compact_recipe = {
            "schema": "HHS_COMPOSITION_RECONSTRUCTION_RECIPE_V1",
            "version": VERSION,
            "recipe_mode": "ROOT_PLUS_DEPENDENCY_ROOTS_PLUS_VERBATIM_SEMANTIC_TEXT",
            "required_fields": ["dependency_roots", "pipeline_contract_root", "verbatim_semantic_text"],
            "expanded_pipeline_persisted": False,
        }
        compact_recipe["recipe_hash72"] = _hash72("HHS_COMPOSITION_RECONSTRUCTION_RECIPE_V1", compact_recipe)
        entry = {
            "schema": ENTRY_SCHEMA,
            "version": VERSION,
            "cache_key_hash72": cache_key,
            "surface_id": pipeline.get("surface_id") or plan.get("surface_id"),
            "operation": pipeline.get("operation") or plan.get("operation"),
            "invariant_ids": _list(pipeline.get("invariant_ids")),
            "contract_schemas": _list(pipeline.get("contract_schemas")),
            "validator_chain": _list(pipeline.get("validator_path")),
            "witness_chain": _list(pipeline.get("witness_path")),
            "guard_chain": _list(pipeline.get("guard_path")),
            "dependency_roots": roots,
            "composition_root_hash72": roots.get("pipeline_root"),
            "pipeline_contract_root": _hash72("HHS_PIPELINE_CONTRACT_ROOT_V1", {
                "contract_schemas": _list(pipeline.get("contract_schemas")),
                "guard_chain": _list(pipeline.get("guard_path")),
                "validator_chain": _list(pipeline.get("validator_path")),
                "witness_chain": _list(pipeline.get("witness_path")),
                "execution_mode": roots.get("execution_mode"),
            }),
            "verbatim_semantic_text": verbatim_text,
            "verbatim_semantic_text_hash72": semantic_hash72(verbatim_text),
            "ml_projection": ml_projection,
            "receipt_mode": "COMPACT_RESIDUE_WITH_RECONSTRUCTION_RECIPE_ONLY",
            "reconstruction_recipe": compact_recipe,
            "created_at_tick": int(created_at_tick),
            "last_verified_tick": int(created_at_tick),
            "decay_policy": {
                "schema": "HHS_COMPOSITION_CACHE_DECAY_POLICY_V1",
                "created_at_tick": int(created_at_tick),
                "decay_window_ticks": int(decay_window_ticks),
                "expanded_payload_retained": False,
            },
            "expanded_pipeline_payload": None,
            "expanded_payload_persisted": False,
            "authority_rule": "SEMANTIC_DB_ACCELERATES_DERIVATION_BUT_CANNOT_AUTHORIZE_RUNTIME_COMPOSITION",
        }
        entry["cache_entry_hash72"] = _hash72(ENTRY_SCHEMA, entry)
        return entry

    def store_entry(self, entry: Mapping[str, Any]) -> Dict[str, Any]:
        semantic_guard = commit_semantic_record("COMPOSITION_CACHE_WRITE", "pass044.semantic_composition_cache", {
            "cache_key_hash72": entry.get("cache_key_hash72"),
            "surface_id": entry.get("surface_id"),
            "verbatim_semantic_text_hash72": entry.get("verbatim_semantic_text_hash72"),
            "ml_projection_hash72": (entry.get("ml_projection") or {}).get("ml_projection_hash72"),
        })
        data = self.load()
        records = [r for r in data.get("records", []) if r.get("cache_key_hash72") != entry.get("cache_key_hash72")]
        stored = dict(entry)
        stored["semantic_guard_write"] = semantic_guard
        records.append(stored)
        data["records"] = records
        for idx_name in ["surface_index", "invariant_index", "contract_index", "validator_index", "root_index", "verbatim_index"]:
            data[idx_name] = {}
        for rec in records:
            key = rec.get("cache_key_hash72")
            data["surface_index"].setdefault(str(rec.get("surface_id")), []).append(key)
            for iid in rec.get("invariant_ids", []) or []:
                data["invariant_index"].setdefault(str(iid), []).append(key)
            for contract in rec.get("contract_schemas", []) or []:
                data["contract_index"].setdefault(str(contract), []).append(key)
            for validator in rec.get("validator_chain", []) or []:
                data["validator_index"].setdefault(str(validator), []).append(key)
            for root_name, root_value in (rec.get("dependency_roots") or {}).items():
                if root_name.endswith("root") or root_name.endswith("hash72"):
                    data["root_index"].setdefault(str(root_value), []).append(key)
            for token in str(rec.get("verbatim_semantic_text", "")).replace("|", " ").split():
                data["verbatim_index"].setdefault(token, []).append(key)
        self.save(data)
        self._index_receipt(stored)
        return stored

    def _index_receipt(self, entry: Mapping[str, Any]) -> None:
        receipt = _ReceiptForVectorIndex(
            receipt_hash72=str(entry.get("cache_entry_hash72"))[:72].ljust(72, "0"),
            state_hash72=str(entry.get("composition_root_hash72") or entry.get("cache_key_hash72"))[:72].ljust(72, "0"),
            witness_flags=0b111101,
            route_trace=["semantic_composition_cache", str(entry.get("surface_id")), str(entry.get("operation"))],
            validation_passed=True,
        )
        self.vector_index.insert_receipt(receipt)

    def search(self, query: str, *, limit: int = 8) -> Dict[str, Any]:
        data = self.load()
        commit_semantic_record("COMPOSITION_CACHE_SEARCH", "pass044.semantic_composition_cache", {
            "query": query,
            "query_hash72": semantic_hash72(query),
        })
        keys: List[str] = []
        for idx_name in ["surface_index", "invariant_index", "contract_index", "validator_index", "root_index", "verbatim_index"]:
            vals = data.get(idx_name, {}).get(query, [])
            keys.extend(str(v) for v in vals)
        # Fall back to verbatim substring search over the exact stored semantic text.
        if not keys:
            for rec in data.get("records", []) or []:
                if query in str(rec.get("verbatim_semantic_text", "")):
                    keys.append(str(rec.get("cache_key_hash72")))
        seen = []
        for key in keys:
            if key not in seen:
                seen.append(key)
        records = [r for r in data.get("records", []) if r.get("cache_key_hash72") in set(seen)]
        return {
            "schema": "HHS_SEMANTIC_COMPOSITION_CACHE_SEARCH_RESULT_V1",
            "version": VERSION,
            "query": query,
            "hit_count": len(records[:limit]),
            "hits": records[:limit],
            "search_authority": "VERBATIM_SEMANTIC_SEARCH_WITH_KERNEL_ROOT_REVALIDATION_REQUIRED",
        }

    def nearest(self, entry: Mapping[str, Any], *, limit: int = 4) -> Dict[str, Any]:
        self._index_receipt(entry)
        receipt = _ReceiptForVectorIndex(
            receipt_hash72=str(entry.get("cache_entry_hash72"))[:72].ljust(72, "0"),
            state_hash72=str(entry.get("composition_root_hash72") or entry.get("cache_key_hash72"))[:72].ljust(72, "0"),
            witness_flags=0b111101,
            route_trace=["semantic_composition_cache", str(entry.get("surface_id")), str(entry.get("operation"))],
            validation_passed=True,
        )
        vector = self.vector_index.compute_receipt_vector(receipt)
        nodes = self.vector_index.search_nearest(vector, limit=limit)
        return {
            "schema": "HHS_SEMANTIC_COMPOSITION_ML_NEAREST_RESULT_V1",
            "version": VERSION,
            "advisory_only": True,
            "nearest_receipt_hash72": [n.receipt_hash72 for n in nodes],
            "vector_index_stats": self.vector_index.stats(),
        }


def validate_cache_entry(entry: Mapping[str, Any], *, current_surface_map: Mapping[str, Any], current_tick: int = 0) -> Dict[str, Any]:
    reasons: List[str] = []
    roots = entry.get("dependency_roots") or {}
    if not roots:
        reasons.append(REJECT_COMPOSITION_CACHE_WITHOUT_DEPENDENCY_ROOTS)
    if roots.get("conformance_graph_root") != current_surface_map.get("conformance_root_hash72"):
        reasons.append(REJECT_CACHE_HIT_WITH_INVALID_CONFORMANCE_ROOT)
        reasons.append(REJECT_COMPOSITION_CACHE_STALE)
    if not (entry.get("reconstruction_recipe") or {}).get("recipe_hash72"):
        reasons.append(REJECT_CACHED_PIPELINE_WITHOUT_RECONSTRUCTION_RECIPE)
    decay = entry.get("decay_policy") or {}
    if decay:
        decay_decision = evaluate_decay_window({
            "created_at_tick": decay.get("created_at_tick", entry.get("created_at_tick", 0)),
            "decay_window_ticks": decay.get("decay_window_ticks", 0),
            "status": "VALIDATED",
        }, current_tick=current_tick)
        if decay_decision.get("expired") and entry.get("expanded_payload_persisted"):
            reasons.append(REJECT_CACHE_ENTRY_AFTER_DECAY_EXPIRATION)
    if entry.get("authority_rule") != "SEMANTIC_DB_ACCELERATES_DERIVATION_BUT_CANNOT_AUTHORIZE_RUNTIME_COMPOSITION":
        reasons.append(REJECT_SEMANTIC_DB_AS_AUTHORITY_SOURCE)
    return {
        "schema": "HHS_COMPOSITION_CACHE_VALIDATION_DECISION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_SEMANTIC_COMPOSITION_CACHE_ENTRY" if not reasons else "REJECT_SEMANTIC_COMPOSITION_CACHE_ENTRY",
        "reasons": reasons,
        "cache_key_hash72": entry.get("cache_key_hash72"),
        "surface_id": entry.get("surface_id"),
    }


def semantic_composition_cache_self_test() -> Dict[str, Any]:
    from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map

    surface_map = build_surface_map()
    surface = next(s for s in surface_map.get("surfaces", []) if s.get("surface_type") == "SERVICE")
    operation = (surface.get("declared_operations") or [surface.get("symbol") or "self_test"])[0]
    plan = compose_surface_pipeline(surface["surface_id"], operation=operation, surface_map=surface_map)
    cache = SemanticCompositionCache(Path("demo_reports/hhs_semantic_composition_cache_self_test.json"))
    entry = cache.build_entry(plan, surface_map, created_at_tick=1, decay_window_ticks=8)
    stored = cache.store_entry(entry)
    by_surface = cache.search(str(stored["surface_id"]))
    by_invariant = cache.search(str(stored["invariant_ids"][0]))
    nearest = cache.nearest(stored)
    validation = validate_cache_entry(stored, current_surface_map=surface_map, current_tick=2)
    return {
        "schema": "HHS_SEMANTIC_COMPOSITION_CACHE_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(by_surface.get("hit_count")) and bool(by_invariant.get("hit_count")) and validation.get("ok") and nearest.get("vector_index_stats", {}).get("node_count", 0) > 0,
        "entry": stored,
        "by_surface": by_surface,
        "by_invariant": by_invariant,
        "nearest": nearest,
        "validation": validation,
    }


if __name__ == "__main__":
    print(semantic_composition_cache_self_test())
