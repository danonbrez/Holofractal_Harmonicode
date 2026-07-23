from pathlib import Path
import pytest
from native_projects.hhs_bifurcation_calibration.hhs_pass105_dictionary_syntax_enforcement_v1 import *
R=Path(__file__).resolve().parents[1]
SRC='dictionary d version 1 { string x : CANONICAL_STRING := "a"; }'
def test_parent(): assert load_parent(R)['manifest']['pass_id']=='PASS_104'
def test_parse_determinism(): assert parse(SRC)['syntax_tree_root_hash72']==parse(SRC)['syntax_tree_root_hash72']
def test_source_ast_distinction():
 a=parse(SRC); assert a['source_root_hash72']!=a['syntax_tree_root_hash72']
def test_canonical_roundtrip():
 a=parse(SRC); b=parse(canonicalize(a)); assert a['syntax_tree_root_hash72']==b['syntax_tree_root_hash72']
def test_bidi_rejected():
 with pytest.raises(ContractError): parse('dictionary d version 1 { string x : T := "a\u202e"; }')
def test_duplicate_rejected():
 with pytest.raises(ContractError): parse('dictionary d version 1 { string x : T := "a"; string x : T := "b"; }')
def test_run():
 r=run(R); assert r['parse_replay_exact'] and r['serialization_reparse_exact'] and len(r['workloads'])==18 and len(r['negative_cases'])==19
