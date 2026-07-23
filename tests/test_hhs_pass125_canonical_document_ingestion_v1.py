import copy
import pytest
from pathlib import Path

from hhs_runtime.hhs_pass125_canonical_document_ingestion_v1 import (
    CanonicalDocumentIngestionEngine, DocumentIngestionBounds, Pass125Error, pass125_self_test
)

@pytest.fixture
def e():
    return CanonicalDocumentIngestionEngine(DocumentIngestionBounds(max_bytes=1024, max_segments=16, max_segment_chars=8))

def test_text_ingestion_normalizes_and_roots(e):
    s=e.ingest_bytes("e\u0301\r\nx".encode(), source_kind="TEST", source_id="x", mime_type="text/plain")
    assert s["canonical_text"] == "é\nx" and s["execution_authority"] is False

def test_lossless_segmentation_manifest_and_replay(e):
    s=e.ingest_bytes(b"alpha beta gamma", source_kind="TEST", source_id="x", mime_type="text/plain")
    seg=e.segment(s); m=e.build_manifest(s,seg); r=e.replay(s,seg,m)
    assert "".join(x["content"] for x in seg)==s["canonical_text"] and r["status"]=="LOSSLESS_REPLAY_VALIDATED"

def test_local_file_ingestion(tmp_path,e):
    p=tmp_path/"a.md"; p.write_text("hello",encoding="utf-8")
    assert e.ingest_text_file(p)["mime_type"]=="text/markdown"

def test_drive_export_ingestion(e):
    raw=b"drive text"
    s=e.ingest_drive_export(file_id="id1",name="Doc",mime_type="application/vnd.google-apps.document",
        modified_time="2026-07-17T12:00:00Z",export_mime_type="text/plain",exported_bytes=raw)
    assert s["source_kind"]=="GOOGLE_DRIVE_EXPORT" and s["metadata"]["drive_file_id"]=="id1"

def test_drive_metadata_required(e):
    with pytest.raises(Pass125Error) as x:
        e.ingest_drive_export(file_id="",name="Doc",mime_type="application/vnd.google-apps.document",modified_time="",export_mime_type="text/plain",exported_bytes=b"x")
    assert x.value.code=="REJECT_DRIVE_METADATA_INCOMPLETE"

def test_invalid_utf8_rejected(e):
    with pytest.raises(Pass125Error) as x: e.ingest_bytes(b"\xff",source_kind="T",source_id="x",mime_type="text/plain")
    assert x.value.code=="REJECT_INVALID_UTF8"

def test_size_bound(e):
    with pytest.raises(Pass125Error) as x: e.ingest_bytes(b"x"*1025,source_kind="T",source_id="x",mime_type="text/plain")
    assert x.value.code=="REJECT_DOCUMENT_TOO_LARGE"

def test_source_tamper_rejected(e):
    s=e.ingest_bytes(b"abc",source_kind="T",source_id="x",mime_type="text/plain"); s["canonical_text"]="abd"
    with pytest.raises(Pass125Error) as x: e.segment(s)
    assert x.value.code=="REJECT_SOURCE_ROOT_MISMATCH"

def test_segment_tamper_rejected(e):
    s=e.ingest_bytes(b"abcdefghij",source_kind="T",source_id="x",mime_type="text/plain"); seg=e.segment(s); seg[0]["content"]="Z"
    with pytest.raises(Pass125Error) as x: e.build_manifest(s,seg)
    assert x.value.code=="REJECT_SEGMENT_ROOT_MISMATCH"

def test_manifest_tamper_replay_rejected(e):
    s=e.ingest_bytes(b"abc",source_kind="T",source_id="x",mime_type="text/plain"); seg=e.segment(s); m=e.build_manifest(s,seg); m["segment_count"]=99
    with pytest.raises(Pass125Error) as x: e.replay(s,seg,m)
    assert x.value.code=="REJECT_REPLAY_MISMATCH"

def test_authority_escalation_rejected(e):
    with pytest.raises(Pass125Error) as x: e.assert_no_authority_escalation({"schema":"X","execution_authority":True,"mutation_authority":False})
    assert x.value.code=="REJECT_EXECUTION_AUTHORITY_ESCALATION"

def test_self_test():
    assert pass125_self_test()["status"]=="PASS"
