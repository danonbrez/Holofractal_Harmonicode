"""Course-Lane5 metadata binding must never imply executable admission."""
import json
from pathlib import Path

INDEX = Path("contracts/pass220/PASS_220_COURSE_LANE5_BINDING_INDEX_V1.json")


def test_course_lane5_binding_is_complete_but_candidate_only():
    data = json.loads(INDEX.read_text("utf-8"))
    assert data["course_module_range"] == [0, 26]
    assert data["bindings"][0]["modules"] == [0, 14]
    assert data["bindings"][1]["modules"] == [15, 26]
    for key in ("course_inventory", "proof_corpus", "lean_root", "lane5_knowledge_graph"):
        assert Path(data[key]).is_file()
    assert data["status"] == "CANDIDATE_METADATA_ONLY"
    assert data["vm81_admission"] is False
    assert data["hash216_minted"] is False
    assert data["native_end_to_end_verified"] is False
