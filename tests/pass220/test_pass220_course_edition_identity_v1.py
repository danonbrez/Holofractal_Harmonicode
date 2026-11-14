"""Edition identity remains separate from native proof authority."""
import json
from pathlib import Path

CONTRACT = Path("contracts/pass220/COURSE_EDITION_IDENTITY_V1.json")


def test_edition_ranges_and_distinct_blob_identities():
    edition = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert edition["historical"]["module_first"] == 0
    assert edition["historical"]["module_last"] == 12
    assert edition["expanded"]["module_first"] == 0
    assert edition["expanded"]["module_last"] == 14
    assert edition["continuation"]["module_first"] == 15
    assert edition["continuation"]["module_last"] == 26
    assert edition["historical"]["git_blob_sha"] != edition["expanded"]["git_blob_sha"]
    assert not edition["automatic_proof_inheritance_between_editions"]
    assert not edition["source_edition_identity_is_proof_authority"]
    assert not edition["vm81_admission"]


def test_current_source_matches_pinned_expanded_git_blob():
    import hashlib
    edition = json.loads(CONTRACT.read_text(encoding="utf-8"))
    raw = Path(edition["source"]).read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()
    assert git_blob == edition["expanded"]["git_blob_sha"]
