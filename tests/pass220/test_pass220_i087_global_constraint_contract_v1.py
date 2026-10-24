"""I087 admits no alternate ordering, graph authority, or fabricated closure."""
import json
from pathlib import Path

ROOT = Path(".")
CONTRACT = ROOT / "contracts/pass220/PASS_220_I087_GLOBAL_CONSTRAINT_RECONCILIATION_V1.json"
GRAPH = ROOT / "contracts/pass219/PASS_219_LANE5_HNAN_GLOBAL_CONSTRAINT_GRAPH_1_63.json"


def test_i087_inherits_exact_global_graph_and_precedence():
    spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    assert spec["authority"]["global_graph"] == str(GRAPH)
    assert spec["authority"]["inherit_rule_count"] == graph["mandatory_rule_count"] == 15
    assert spec["authority"]["inherit_rule_mask"] == graph["mandatory_rule_mask"] == 32767
    assert spec["authority"]["resolution_precedence"] == graph["resolution_precedence"]
    assert spec["successor"]["ordered_window"] == ["p", "P", "q"]
    assert (spec["successor"]["p"], spec["successor"]["q"]) == ("P-1", "P+1")


def test_i087_unresolved_and_normalization_remain_proof_obligations():
    spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert spec["disagreement"]["unregistered_address"] == "UNRESOLVED_FAIL_CLOSED"
    assert spec["transition"]["no_authoritative_branch_fork"] is True
    assert spec["normal_form"]["proof_status"] == "OBLIGATION_NOT_ESTABLISHED"
    assert spec["normal_form"]["idempotence"] == "N_C(N_C(S))=N_C(S)"
    assert spec["normal_form"]["fixed_point"] == "N_C(S*)=S*"
    assert spec["authority"]["canonical_mutation"] == "VM81_ONLY"
    assert spec["admission"] is False
    assert spec["hash72_minted"] is False
    assert spec["hash216_minted"] is False
