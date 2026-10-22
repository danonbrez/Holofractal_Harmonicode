"""M22 source-ingress regression: preserve native ordered tokens, no scalar admission."""
from pathlib import Path

from hhs_runtime.pass148.parser import tokenize

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "evidence/pass220/course_m22_circulant_source_contract_20261020.md"


def test_module22_verbatim_list_is_source_preserved():
    doc = SOURCE.read_text(encoding="utf-8")
    source = doc.split("## Verbatim author expression\n\n```\n", 1)[1].split("\n```", 1)[0]
    assert source.startswith("List(x,x^2,y,y^4,z,z^2,w,w^4)^List(")
    assert source.endswith("List(1,2,3,4))))")
    # Existing native-facing parser keeps source positions and operator identity.
    tokens = tokenize(source)
    assert all(t.kind != "UNKNOWN" for t in tokens)
    assert "".join(source[t.start:t.end] for t in tokens if t.kind != "EOF") == source
    operators = [t.text for t in tokens if t.kind == "OP"]
    assert "^" in operators and "/" in operators and "-" in operators
    # Source is a candidate: the external circulant projection cannot act
    # as proof of identity for two typed occurrences of the prefix.
    assert "Unresolved native acceptance:" in doc
    assert "Do not replace source with scalar -C" in doc
