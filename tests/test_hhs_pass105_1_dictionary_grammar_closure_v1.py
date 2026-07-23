from pathlib import Path
import pytest

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass105_1_dictionary_grammar_closure_v1 import (
    REJECTIONS, canonicalize, compile_dictionary, enforce, execute_negative_case,
    load_parent, merge_validate, negative_fixtures, parse, run,
)

R = Path(__file__).resolve().parents[1]
SIMPLE = 'dictionary d version 1 { string x : CANONICAL_STRING := "a"; }'
TEMPLATE = 'dictionary d version 1 { template t(x : CANONICAL_STRING, phase : U72_PHASE = 18) -> CANONICAL_STRING := t"${x}"; }'


def test_parent_is_pass105():
    assert load_parent(R)["manifest"]["pass_id"] == "PASS_105"


def test_template_parameters_roundtrip_exact():
    a = parse(TEMPLATE)
    b = parse(canonicalize(a))
    assert a["syntax_tree_root_hash72"] == b["syntax_tree_root_hash72"]
    assert b["ast"]["declarations"][0]["parameters"][1]["default"] == ["18"]


def test_full_declaration_roundtrip():
    source = '''dictionary d version 1 {
 import hhs.core@1 as core;
 symbol Ψ : CONSTRAINT_OPERATOR := ref(hhs.operator.psi);
 string x : CANONICAL_STRING := "a";
 variable y : INTEGER := 2;
 constant z : INTEGER := 3;
 phrase "shared genesis" : SEMANTIC_REFERENCE := ref(hhs.semantic.shared_genesis);
 template t(x : CANONICAL_STRING) -> CANONICAL_STRING := t"${x}";
 alias ↔ -> ref(hhs.relation.reciprocal);
 scope LOCAL s { string q : CANONICAL_STRING := "q"; }
}'''
    a = parse(source)
    b = parse(canonicalize(a))
    assert a["syntax_tree_root_hash72"] == b["syntax_tree_root_hash72"]


def test_unknown_version_rejected():
    with pytest.raises(ContractError, match="REJECT_UNSUPPORTED_DICTIONARY_VERSION"):
        enforce(parse('dictionary d version 999 { string x : T := "a"; }'))


def test_unknown_type_rejected():
    with pytest.raises(ContractError, match="REJECT_UNKNOWN_TYPE"):
        enforce(parse('dictionary d version 1 { string x : NOT_A_TYPE := "a"; }'))


def test_missing_reference_rejected():
    with pytest.raises(ContractError, match="REJECT_UNRESOLVED_REFERENCE"):
        enforce(parse('dictionary d version 1 { string x : T := ref(missing); }'))


def test_reference_cycle_rejected():
    src = 'dictionary d version 1 { string a : T := ref(b); string b : T := ref(a); }'
    with pytest.raises(ContractError, match="REJECT_REFERENCE_DEPENDENCY_CYCLE"):
        enforce(parse(src))


def test_import_must_be_pinned_and_locked():
    with pytest.raises(ContractError, match=REJECTIONS[12]):
        enforce(parse('dictionary d version 1 { import hhs.core; string x : T := "a"; }'))
    parsed = parse('dictionary d version 1 { import hhs.core@1; string x : T := "a"; }')
    with pytest.raises(ContractError, match=REJECTIONS[11]):
        enforce(parsed)
    assert enforce(parsed, import_locks={"hhs.core@1": "hash72:root"})["admission_status"] == "ADMITTED"


def test_diagnostic_recovery_never_admitted():
    recovered = parse('dictionary d version 1 { string x : T := "a" }', diagnostic_recovery=True)
    assert recovered["syntax_status"] == "DIAGNOSTIC_RECOVERY_ONLY"
    with pytest.raises(ContractError, match=REJECTIONS[4]):
        canonicalize(recovered)


def test_shadowing_rejected():
    src = 'dictionary d version 1 { string x : T := "a"; scope LOCAL s { string x : T := "b"; } }'
    with pytest.raises(ContractError, match=REJECTIONS[10]):
        enforce(parse(src))


def test_merge_last_write_wins_rejected():
    parsed = parse(SIMPLE)
    with pytest.raises(ContractError, match=REJECTIONS[13]):
        merge_validate(parsed, parsed, "LAST_WRITE_WINS")


def test_all_negative_cases_are_executed():
    results = [execute_negative_case(case) for case in negative_fixtures()]
    assert len(results) == 19
    assert all(row["passed"] and row["observed"] == row["expected"] for row in results)


def test_runtime_compile_surface():
    result = compile_dictionary({"source": SIMPLE, "authority_granted": True})
    assert result["status"] == "DICTIONARY_ADMITTED"
    assert result["enforcement_receipt"]["admission_status"] == "ADMITTED"


def test_runtime_authority_rejected():
    with pytest.raises(ContractError, match=REJECTIONS[14]):
        compile_dictionary({"source": SIMPLE, "authority_granted": False})


def test_run_closure():
    result = run(R)
    assert result["parse_replay_exact"]
    assert result["serialization_reparse_exact"]
    assert result["template_parameters_preserved"]
    assert all(x["passed"] for x in result["negative_cases"])

def test_service_registry_reachability():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    assert registry.has_service("harmonicode.dictionary.compile_enforce_v1")
    spec = next(x for x in registry.services() if x["name"] == "harmonicode.dictionary.compile_enforce_v1")
    assert spec["conformance_decision"]["derivation_complete"]
