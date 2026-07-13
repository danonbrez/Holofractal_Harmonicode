from hhs_runtime.hhs_runtime_integration_decisions_v1 import (
    build_integration_decisions,
    decide_path,
    integration_decisions_self_test,
)
from hhs_runtime.hhs_runtime_reachability_audit_v1 import build_reachability_manifest


def test_integration_decisions_classify_known_orphan_shapes():
    assert decide_path("data/runtime/hhs_unified_hash72_ledger.json").decision == "DOCUMENTED_ONLY"
    assert decide_path("hhs_python/runtime/hhs_invariant_consensus_engine.py").decision == "PLUGIN_READY"
    assert decide_path("hhs_foundation/HHS_M001.py").decision == "PLUGIN_READY"
    assert decide_path("gui/hhs-mobile-runtime-console/src/App.tsx").decision == "PLUGIN_READY"


def test_integration_decisions_self_test():
    result = integration_decisions_self_test()
    assert result["ok"] is True
    assert result["decision_count"] > 0
    assert len(result["hash72_kernel_witness"]["dna"]) == 72


def test_pass023_reachability_manifest_applies_decisions():
    manifest = build_reachability_manifest()
    assert manifest["schema"] == "HHS_RUNTIME_REACHABILITY_MANIFEST_V1"
    assert manifest["version"] == "PASS_023"
    assert manifest["integration_decision_count"] > 0
    assert manifest["orphan_count"] == 0
    paths = {record["path"]: record for record in manifest["records"]}
    assert paths[".github/workflows/hhs-acceptance-gate.yml"]["status"] == "DOCUMENTED_ONLY"
    assert paths["hhs_python/runtime/hhs_invariant_consensus_engine.py"]["status"] == "PLUGIN_READY"
