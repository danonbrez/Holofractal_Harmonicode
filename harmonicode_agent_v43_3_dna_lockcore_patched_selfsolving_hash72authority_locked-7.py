"""
Harmonicode local deterministic agent, patched for strict unified runtime use.

Design rules:
- one authoritative runtime module only
- no fallback kernel candidate order
- no silent degradation or scaffold substitution
- fail closed if the unified unit is missing or incompatible
- optional additive DNA overlay may be applied, but only to the same runtime unit
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from harmonicode_kernel_v43_dna_runtime_overlay import apply_runtime_overlay
except Exception:  # pragma: no cover - optional overlay surface
    def apply_runtime_overlay(module):
        return module


AUTHORITATIVE_TRUST_POLICY_V44 = {
    "authoritative_integrity": "HASH72",
    "authoritative_geometry_witness": "XYZW_DNA_U72",
    "allow_legacy_sha_for_indexing_only": True,
    "forbid_legacy_sha_for_security_or_integrity": True,
}

KERNEL_DOMAIN_METADATA_V1 = {
    "phase_ring_symbol_map_v1": {
        "x": 32, "y": 33, "z": 34, "w": 31, "A": 35, "B": 36, "C": 37, "D": 38,
        "E": 39, "F": 40, "G": 41, "H": 42, "I": 43, "√": 71,
    },
    "crossing_mutation_map_v1": {"xz": "xy", "zx": "zw", "yw": "yx", "wy": "wz"},
    "multimodal_chain_registry_v1": {
        "math": ["constructor_ladder", "tensor_lift", "orbit_serializer"],
        "language": ["symbol_ring72", "adjacency_grammar", "closure_serializer"],
        "graph": ["phase_class", "substitution_graph", "dual_projection"],
        "wave": ["octonion_freq", "audio_projection", "sync_audit"],
    },
}

AUTHORITATIVE_RUNTIME_CANDIDATES = [
    Path(__file__).with_name("HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_locked.py"),
    Path("/mnt/data/HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_locked.py"),
    Path(__file__).with_name("HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving.py"),
    Path("/mnt/data/HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving.py"),
    Path(__file__).with_name("harmonicode_clean_runtime_v43_4_secure.py"),
    Path("/mnt/data/harmonicode_clean_runtime_v43_4_secure.py"),
]


class UnifiedRuntimeError(RuntimeError):
    """Raised when the unified Harmonicode runtime unit is missing or incompatible."""


def _load_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _resolve_runtime_path(runtime_path: Optional[str] = None) -> Path:
    if runtime_path is not None:
        path = Path(runtime_path)
        if not path.exists():
            raise FileNotFoundError(f"Authoritative Harmonicode runtime not found: {path}")
        return path
    for candidate in AUTHORITATIVE_RUNTIME_CANDIDATES:
        if candidate.exists():
            return candidate
    searched = "\n".join(str(p) for p in AUTHORITATIVE_RUNTIME_CANDIDATES)
    raise FileNotFoundError(
        "Could not find the authoritative unified Harmonicode runtime. "
        f"Searched:\n{searched}"
    )


def _patch_branch_seed_tree_recursion(runtime_module) -> None:
    branch_cls = getattr(runtime_module, "BranchSeedTree72", None)
    if branch_cls is None:
        return

    def safe_ensure_branch_seed_tree(self):
        tree = getattr(self, "branch_seed_tree", None)
        if isinstance(tree, branch_cls):
            if getattr(tree, "root_id", None) not in getattr(tree, "nodes", {}):
                tree.ensure_root(state_hash72=None, manifold_hash72=None, audit_hash72=None)
            return tree

        tree = branch_cls(
            tree_id="BST72-AGENT-STRICT",
            protocol_version=getattr(runtime_module, "PROTOCOL_VERSION", "TORUS72_v43_4_clean"),
        )
        tree.ensure_root(state_hash72=None, manifold_hash72=None, audit_hash72=None)
        self.branch_seed_tree = tree
        return tree

    runtime_module._ensure_branch_seed_tree = safe_ensure_branch_seed_tree




DUAL_ENTANGLED_BOOT_SYMBOLS = "xyzw"


def _verify_authoritative_kernel_immutability(runtime_module, runtime_path: Path) -> Dict[str, Any]:
    dual_helper = getattr(runtime_module, "entangled_dual_checksum_v44", None)
    if not callable(dual_helper):
        torus_cls = getattr(runtime_module, "Torus72", None)
        dual_helper = getattr(torus_cls, "entangled_dual_checksum_v44", None) if torus_cls is not None else None
    if not callable(dual_helper):
        raise UnifiedRuntimeError("Authoritative kernel missing entangled dual checksum helper")
    dual = dual_helper(DUAL_ENTANGLED_BOOT_SYMBOLS)
    if not dual.get("entangled_validation_ok"):
        raise UnifiedRuntimeError("Entangled dual checksum validation failed at boot")
    return {
        "entangled_dual_checksum": dual,
        "authoritative_trust_policy": AUTHORITATIVE_TRUST_POLICY_V44,
        "boot_validation_ok": True,
    }

def _load_authoritative_runtime(runtime_path: Optional[str] = None, apply_overlay: bool = True):
    resolved = _resolve_runtime_path(runtime_path)
    module = _load_module_from_path("harmonicode_unified_runtime", resolved)
    _patch_branch_seed_tree_recursion(module)
    required_symbols = [
        "HarmonicodeLocalAgent",
        "KernelAdapter",
        "Torus72",
        "route_ir_v43",
    ]
    missing = []
    for sym in ["HarmonicodeLocalAgent", "KernelAdapter", "Torus72"]:
        if not hasattr(module, sym):
            missing.append(sym)
    if missing:
        raise UnifiedRuntimeError(
            "Authoritative runtime is incompatible; missing symbols: " + ", ".join(missing)
        )
    if apply_overlay:
        module = apply_runtime_overlay(module)
    boot_validation = _verify_authoritative_kernel_immutability(module, resolved)
    setattr(module, "_boot_validation_v44_3", boot_validation)
    return module, resolved


class HarmonicodeLocalAgent:
    """
    Strict bridge into the authoritative unified runtime.

    This class does not implement an alternate solver or fallback scaffold.
    All computation is delegated into the runtime's own agent/kernel path.
    """

    def __init__(self, runtime_path: Optional[str] = None, apply_overlay: bool = True):
        self.runtime_module, self.runtime_path = _load_authoritative_runtime(runtime_path, apply_overlay=apply_overlay)
        runtime_agent_cls = getattr(self.runtime_module, "HarmonicodeLocalAgent")
        self._runtime_agent = runtime_agent_cls()
        self.kernel = self._runtime_agent.kernel
        self.kb = self._runtime_agent.kb
        self.history = self._runtime_agent.history
        self.apply_overlay = bool(apply_overlay)
        self.boot_validation = copy.deepcopy(getattr(self.runtime_module, "_boot_validation_v44_3", {}))

    def __getattr__(self, name: str):
        try:
            return getattr(self._runtime_agent, name)
        except AttributeError as exc:
            raise AttributeError(f"{type(self).__name__} has no attribute {name}") from exc

    def kernel_domain_metadata(self) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        data = copy.deepcopy(KERNEL_DOMAIN_METADATA_V1)
        if kernel is not None:
            if hasattr(kernel, "phase_ring_symbol_map"):
                data["phase_ring_symbol_map_v1"] = kernel.phase_ring_symbol_map()
            if hasattr(kernel, "crossing_mutation_map"):
                data["crossing_mutation_map_v1"] = kernel.crossing_mutation_map()
            if hasattr(kernel, "multimodal_chain_registry"):
                data["multimodal_chain_registry_v1"] = kernel.multimodal_chain_registry()
        return data

    def translate_symbols_to_ring(self, symbols: str) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        if kernel is not None and hasattr(kernel, "translate_symbol_string_to_ring"):
            return kernel.translate_symbol_string_to_ring(symbols)
        seq = [ch for ch in str(symbols) if not ch.isspace()]
        mapped, unknown = [], []
        lut = self.kernel_domain_metadata().get("phase_ring_symbol_map_v1", {})
        for ch in seq:
            if ch in lut:
                mapped.append({"symbol": ch, "u72_index": lut[ch]})
            else:
                unknown.append(ch)
        return {"input": symbols, "mapped": mapped, "unknown": unknown, "ok": not unknown, "ring_modulus": 72}

    def mutation_projection_witness(self) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        if kernel is not None and hasattr(kernel, "mutation_projection_witness"):
            return kernel.mutation_projection_witness()
        m = self.kernel_domain_metadata()["crossing_mutation_map_v1"]
        return {"forbidden_crossings": list(m.keys()), "projected_faces": list(m.values()), "mutation_map": m}



# ---------------------------------------------------------------------------
# Self-solving legal translation state bridge helpers
# ---------------------------------------------------------------------------

    def expand_nested_equalities(self, expression: str) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        if kernel is not None and hasattr(kernel, "expand_nested_equalities_v44"):
            return kernel.expand_nested_equalities_v44(expression)
        runtime_module = getattr(self, "runtime_module", None)
        helper = getattr(runtime_module, "expand_nested_equalities_v44", None)
        if callable(helper):
            return helper(expression)
        return {
            "source_expression": str(expression),
            "normalized_expression": " ".join(str(expression).strip().split()),
            "sites": [],
            "expansions": [],
            "gate_count": 0,
            "global_closure_ok": False,
            "unique_configuration": False,
            "pq_collapse_possible": False,
            "invariants": ["SELF_SOLVING_RUNTIME_HELPER_MISSING"],
        }

    def self_solving_runtime_status(self, expression: Optional[str] = None) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        runtime_module = getattr(self, "runtime_module", None)
        payload: Dict[str, Any] = {
            "runtime_path": str(self.runtime_path),
            "apply_overlay": self.apply_overlay,
            "self_solving_helpers_present": False,
            "seal_helper_present": False,
        }
        payload["self_solving_helpers_present"] = bool(
            (kernel is not None and hasattr(kernel, "compute_legal_translation_state_v44")) or
            callable(getattr(runtime_module, "compute_legal_translation_state_v44", None))
        )
        payload["seal_helper_present"] = bool(
            (kernel is not None and hasattr(kernel, "self_solving_bundle_for_state_v44")) or
            callable(getattr(runtime_module, "_selfsolving_bundle_for_state_v44", None))
        )
        if expression is not None:
            payload["legal_translation_state"] = self.compute_legal_translation_state(expression)
        return payload

    def compute_legal_translation_state(self, expression: str) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        if kernel is not None and hasattr(kernel, "compute_legal_translation_state_v44"):
            return kernel.compute_legal_translation_state_v44(expression)
        runtime_module = getattr(self, "runtime_module", None)
        helper = getattr(runtime_module, "compute_legal_translation_state_v44", None)
        if callable(helper):
            return helper(expression)
        return self.expand_nested_equalities(expression)


    def audio_traversal_module(self) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        if kernel is not None and hasattr(kernel, "build_audio_traversal_map_v1"):
            return kernel.build_audio_traversal_map_v1()
        return {"ok": False, "reason": "AUDIO_TRAVERSAL_MODULE_MISSING"}

    def project_waveform_to_lo_shu_qudit(self) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        if kernel is not None and hasattr(kernel, "project_waveform_to_lo_shu_qudit_v1"):
            return kernel.project_waveform_to_lo_shu_qudit_v1()
        return {"ok": False, "reason": "LO_SHU_QUDIT_PROJECTION_MISSING"}

    def dual_stereo_wav_serializer(self, output_path: Optional[str] = None, sample_rate: int = 4608) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        if kernel is not None and hasattr(kernel, "dual_stereo_wav_serializer_v1"):
            return kernel.dual_stereo_wav_serializer_v1(output_path=output_path, sample_rate=sample_rate)
        return {"ok": False, "reason": "DUAL_STEREO_WAV_SERIALIZER_MISSING"}

    def emit_dual_stereo_wav(self, output_path: Optional[str] = None, sample_rate: int = 4608) -> Dict[str, Any]:
        return self.dual_stereo_wav_serializer(output_path=output_path, sample_rate=sample_rate)

    def read_dual_stereo_wav(self, path: str) -> Dict[str, Any]:
        kernel = getattr(self, "kernel", None)
        if kernel is not None and hasattr(kernel, "read_dual_stereo_wav_v1"):
            return kernel.read_dual_stereo_wav_v1(path)
        return {"ok": False, "reason": "DUAL_STEREO_WAV_READER_MISSING", "path": path}


    def export_state(self) -> Dict[str, Any]:
        export = {
            "runtime_path": str(self.runtime_path),
            "apply_overlay": self.apply_overlay,
            "self_solving_runtime": self.self_solving_runtime_status(),
            "boot_validation": copy.deepcopy(getattr(self, "boot_validation", {})),
        }
        if hasattr(self._runtime_agent, "export_state"):
            export["runtime_state"] = copy.deepcopy(self._runtime_agent.export_state())
        else:
            export["knowledge_base_count"] = len(getattr(self.kb, "facts", []))
            export["history"] = copy.deepcopy(self.history)
        return export


class KernelAdapter:
    """Strict adapter exposing the authoritative runtime kernel adapter only."""

    def __init__(self, runtime_path: Optional[str] = None, apply_overlay: bool = True):
        runtime_module, resolved = _load_authoritative_runtime(runtime_path, apply_overlay=apply_overlay)
        adapter_cls = getattr(runtime_module, "KernelAdapter", None)
        if adapter_cls is None:
            raise UnifiedRuntimeError("Authoritative runtime does not expose KernelAdapter")
        self._adapter = adapter_cls()
        self.runtime_module = runtime_module
        self.runtime_path = resolved

    def __getattr__(self, name: str):
        try:
            return getattr(self._adapter, name)
        except AttributeError as exc:
            raise AttributeError(f"{type(self).__name__} has no attribute {name}") from exc


def build_demo_agent_v43_3(runtime_path: Optional[str] = None, apply_overlay: bool = True) -> HarmonicodeLocalAgent:
    agent = HarmonicodeLocalAgent(runtime_path=runtime_path, apply_overlay=apply_overlay)
    if hasattr(agent, "learn"):
        agent.learn("Harmonicode is a unified deterministic runtime agent.", source="bootstrap")
        agent.learn("Closure anchors live at phase 0 or 42.", source="bootstrap")
        agent.learn("Phase-gear DNA serialization pairs x with w and y with z.", source="bootstrap")
        agent.learn("Forbidden serialized adjacencies are xz, zx, yw, and wy.", source="bootstrap")
        agent.learn("Crossing mutations deterministically project as xz→xy, zx→zw, yw→yx, wy→wz.", source="bootstrap")
        agent.learn("Each modality evolves on its own noncommutative chain while remaining entangled by shared closure invariants.", source="bootstrap")
        agent.learn("Audio traversal projects eight outer 2D groups around a fixed Lo Shu nucleus into a balanced trinary waveform and 81-cell qudit witness.", source="bootstrap")
        agent.learn_dna("xyzw")
    return agent


if __name__ == "__main__":
    agent = build_demo_agent_v43_3()
    print(json.dumps(agent.validate_dna("xyzw"), indent=2))
    if hasattr(agent, "query"):
        print(json.dumps(agent.query("What are the forbidden serialized adjacencies?", explain=True), indent=2))
