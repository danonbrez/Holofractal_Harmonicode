"""V7 native-phase-preserving *noncanonical* free-word diagnostic tests."""
import json
from pathlib import Path
from collections import Counter

import pytest

from hhs_runtime.hhs_pass220_v7_ordered_free_word_diagnostic_v1 import (
    BASIS,SIGNED_CENTER,EXPECTED_COLS,EXPECTED_ROWS,
    compute,lex_ordered_terms,as_exact_word_vector,
)
from hhs_runtime.hhs_pass220_v7_ordered_matrix_geometry_v1 import V7SourceError

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"contracts/pass220/PASS_220_V7_VM81_ORDERED_MATRIX_QUOTIENT_20261009.harmonicode"
OUT=ROOT/"artifacts/pass220/v7-ordered-words/diagnostic.json"

def test_source_specific_formal_word_provenance_and_rows():
    doc=compute(SRC.read_bytes())
    assert doc["ordered_word_basis"]==list(BASIS)
    assert doc["row_vectors"]==list(EXPECTED_ROWS)
    assert doc["column_vectors"]==list(EXPECTED_COLS)
    assert doc["column_vectors"][0]=={"yx":1,"wz":-1}
    assert doc["column_vectors"][2]=={"yx":-1,"wx":1}
    assert doc["column_vectors"][1]=={
        "x":2,"y":2,"z":-2,"xy":1,"yx":1,"zw":-1,"wz":-1}
    assert len(doc["cells"])==9
    assert [x["site"] for x in doc["cells"]]==list(range(9))
    assert len(doc["diagonal_vectors"])==2
    assert doc["diagonal_vectors"][0]!=doc["diagonal_vectors"][1]
    assert doc["free_word_projection_has_equal_row_column_magic_sum"] is False
    assert all(v is False for k,v in doc.items() if k in (
        "native_hnan_15_rules_verified_by_separate_C",
        "matrix_ordered_quotient_admissibility_verified",
        "matrix_native_inverse_or_division_proved",
        "signed_environmental_vm81_admission_verified",
        "canonical_hash72_hash216_transition_verified"))

def test_center_all_eight_ordered_signed_channels():
    doc=compute(SRC.read_bytes())
    assert [(t["word"],t["coefficient"]) for t in doc["cells"][4]["ordered_terms"]]==list(SIGNED_CENTER)
    toks=doc["term_occurrences"]
    assert len(toks)==sum(len(x["ordered_terms"]) for x in doc["cells"])
    assert [t["absolute_source_byte_offset"] for t in toks]==sorted(
        t["absolute_source_byte_offset"] for t in toks)
    assert toks[0]["word"]=="yx"
    assert all(t["native_typed_value"]=="UNRESOLVED" for t in toks)
    assert all(x["native_cell_proof"]=="UNRESOLVED" for x in doc["cells"])

def test_distinct_ordered_products_do_not_scalarize():
    assert as_exact_word_vector(lex_ordered_terms("xy-yx"))=={"xy":1,"yx":-1}
    assert as_exact_word_vector(lex_ordered_terms("zw-wz"))=={"zw":1,"wz":-1}
    assert as_exact_word_vector(lex_ordered_terms("wx-wx"))=={}
    assert as_exact_word_vector(lex_ordered_terms("yx-yx"))=={}
    assert as_exact_word_vector(lex_ordered_terms("xy+yx"))=={"xy":1,"yx":1}

@pytest.mark.parametrize("bad",[
    "xy*y","xy/yx","xw","yxwz","xy^2","y x","",",xy","xy==xy","(xy)",
])
def test_unregistered_or_ambiguous_word_not_admitted(bad):
    with pytest.raises(V7SourceError):
        lex_ordered_terms(bad)

@pytest.mark.parametrize("replacement",[
    b"yx+y+w",b"x+y-z-w+yx+xy-zw-wz",
    b"x+y-z-w+xy+yx-wz-zw",
])
def test_canonical_source_mutation_rejected_even_when_additive_projection_agrees(replacement):
    src=SRC.read_bytes()
    previous=b"x+y-z-w+xy+yx-zw-wz"
    changed=src.replace(previous,replacement,1)
    assert changed!=src
    with pytest.raises(V7SourceError,match="UNAUTHORIZED_SOURCE_MUTATION"):
        compute(changed)

def test_materialized_diagnostic_replay():
    if not OUT.exists():pytest.skip("Focused workflow materializes diagnostic")
    assert json.loads(OUT.read_text())==compute(SRC.read_bytes())
