from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_json, hash72, sha256_bytes, stable_id
from .errors import Pass145Error

PASS_ID = "HHS-P145"
PARSER_VERSION = "1.0.0"


@dataclass(frozen=True)
class ParseBounds:
    max_bytes: int = 16 * 1024 * 1024
    max_depth: int = 128
    max_nodes: int = 250_000
    max_segments: int = 32_768
    max_segment_chars: int = 4096
    max_scripts: int = 4096
    max_table_cells: int = 1_000_000

    def validate(self) -> None:
        if any(int(v) <= 0 for v in vars(self).values()):
            raise Pass145Error("RESOURCE_BOUND_UNRESOLVED", "all parser bounds must be positive", "ADMISSION")


MIME_BY_SUFFIX = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".html": "text/html",
    ".htm": "text/html",
    ".json": "application/json",
    ".jsonl": "application/x-ndjson",
    ".csv": "text/csv",
    ".xml": "application/xml",
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".hhs": "application/x-hhs-script",
    ".hhsprog": "application/x-hhs-program",
}

SUPPORTED_MIME = frozenset(MIME_BY_SUFFIX.values()) | {
    "application/javascript",
    "application/vnd.hhs.manifest+json",
    "application/vnd.hhs.receipt+json",
}


def detect_mime(name: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit.split(";", 1)[0].strip().lower()
    return MIME_BY_SUFFIX.get(Path(name).suffix.lower(), "text/plain")


class _BoundedHTMLParser(HTMLParser):
    HIDDEN = {"script", "style", "template", "noscript"}
    BLOCK = {"address", "article", "aside", "blockquote", "br", "div", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section", "table", "tr", "ul"}

    def __init__(self, bounds: ParseBounds):
        super().__init__(convert_charrefs=True)
        self.bounds = bounds
        self.stack: list[dict[str, Any]] = []
        self.nodes: list[dict[str, Any]] = []
        self.text_parts: list[str] = []
        self.scripts: list[dict[str, Any]] = []
        self.styles: list[str] = []
        self.links: list[dict[str, Any]] = []
        self.images: list[dict[str, Any]] = []
        self.forms: list[dict[str, Any]] = []
        self.metadata: dict[str, Any] = {}
        self.title_parts: list[str] = []
        self._script_buf: list[str] | None = None
        self._style_buf: list[str] | None = None

    def _check(self) -> None:
        if len(self.nodes) > self.bounds.max_nodes:
            raise Pass145Error("RESOURCE_BOUNDED", "HTML node bound reached", "PARSE")
        if len(self.stack) > self.bounds.max_depth:
            raise Pass145Error("RESOURCE_BOUNDED", "HTML nesting bound reached", "PARSE")
        if len(self.scripts) > self.bounds.max_scripts:
            raise Pass145Error("RESOURCE_BOUNDED", "HTML script bound reached", "PARSE")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        amap = {k.lower(): (v or "") for k, v in attrs}
        path = [n["tag"] for n in self.stack] + [tag]
        node = {"index": len(self.nodes), "tag": tag, "attrs": amap, "path": path, "kind": "start"}
        self.nodes.append(node)
        self.stack.append(node)
        if tag in self.BLOCK:
            self.text_parts.append("\n")
        if tag == "script":
            self._script_buf = []
            self.scripts.append({"attrs": amap, "source": "", "executed": False, "mode": "PARSE_ONLY+STATIC_ANALYSIS"})
        elif tag == "style":
            self._style_buf = []
        elif tag == "a":
            self.links.append({"href": amap.get("href", ""), "rel": amap.get("rel", ""), "text": "", "node_index": node["index"]})
        elif tag == "img":
            self.images.append({"src": amap.get("src", ""), "alt": amap.get("alt", ""), "title": amap.get("title", ""), "node_index": node["index"]})
        elif tag == "form":
            self.forms.append({"action": amap.get("action", ""), "method": amap.get("method", "get").lower(), "node_index": node["index"]})
        elif tag == "meta":
            key = amap.get("name") or amap.get("property") or amap.get("http-equiv")
            if key:
                self.metadata.setdefault(key, []).append(amap.get("content", ""))
        elif tag == "html" and amap.get("lang"):
            self.metadata["language"] = amap["lang"]
        self._check()

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "script" and self._script_buf is not None:
            self.scripts[-1]["source"] = "".join(self._script_buf)
            self._script_buf = None
        elif tag == "style" and self._style_buf is not None:
            self.styles.append("".join(self._style_buf))
            self._style_buf = None
        if tag in self.BLOCK:
            self.text_parts.append("\n")
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._script_buf is not None:
            self._script_buf.append(data)
            return
        if self._style_buf is not None:
            self._style_buf.append(data)
            return
        active = {n["tag"] for n in self.stack}
        if active & self.HIDDEN:
            return
        if "title" in active:
            self.title_parts.append(data)
        if data:
            self.text_parts.append(data)
            if self.links and any(n["tag"] == "a" for n in self.stack):
                self.links[-1]["text"] += data

    def result(self) -> dict[str, Any]:
        visible = re.sub(r"[ \t]+", " ", "".join(self.text_parts))
        visible = re.sub(r"\n\s*\n+", "\n\n", visible).strip()
        return {
            "title": re.sub(r"\s+", " ", "".join(self.title_parts)).strip(),
            "metadata": self.metadata,
            "visible_text": visible,
            "dom_nodes": self.nodes,
            "links": self.links,
            "images": self.images,
            "forms": self.forms,
            "scripts": self.scripts,
            "styles": self.styles,
            "script_execution": "NOT_PERFORMED",
        }


def _js_static_analysis(source: str) -> dict[str, Any]:
    # This is intentionally syntax-preserving/static.  It never executes input.
    imports = re.findall(r"(?:import\s+(?:[^;]+?\s+from\s+)?|require\s*\()\s*['\"]([^'\"]+)", source)
    exports = re.findall(r"\bexport\s+(?:default\s+)?(?:class|function|const|let|var)?\s*([A-Za-z_$][\w$]*)?", source)
    declarations = re.findall(r"\b(?:class|function|const|let|var)\s+([A-Za-z_$][\w$]*)", source)
    calls = re.findall(r"\b([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*\(", source)
    urls = re.findall(r"https?://[^\s'\"`<>]+", source)
    events = re.findall(r"addEventListener\s*\(\s*['\"]([^'\"]+)", source)
    dangerous = sorted(set(re.findall(r"\b(eval|Function|fetch|XMLHttpRequest|WebSocket|document\.cookie|localStorage|indexedDB|require|process|child_process|fs)\b", source)))
    return {
        "imports": sorted(set(imports)),
        "exports": sorted(set(x for x in exports if x)),
        "declarations": sorted(set(declarations)),
        "call_targets": sorted(set(calls)),
        "urls": sorted(set(urls)),
        "event_bindings": sorted(set(events)),
        "dangerous_capability_references": dangerous,
        "execution_performed": False,
        "default_policy": "REJECT_EXECUTION",
    }


def _xml_depth(elem: ET.Element, depth: int = 1) -> int:
    maximum = depth
    stack = [(elem, depth)]
    while stack:
        node, current = stack.pop()
        maximum = max(maximum, current)
        stack.extend((child, current + 1) for child in list(node))
    return maximum


def _segment_text(text: str, bounds: ParseBounds, source_root: str) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    start = 0
    while start < len(text):
        hard = min(len(text), start + bounds.max_segment_chars)
        end = hard
        if hard < len(text):
            split = max(text.rfind("\n", start, hard), text.rfind(" ", start, hard))
            if split > start:
                end = split + 1
        content = text[start:end]
        payload = {
            "schema": "HHS_PASS145_SEGMENT_V1",
            "source_root_hash72": source_root,
            "segment_index": len(segments),
            "start_offset": start,
            "end_offset": end,
            "section_path": [],
            "text": content,
            "language": "und",
            "parser_version": PARSER_VERSION,
        }
        payload["segment_hash"] = hash72("hhs_pass145_segment_v1", payload)
        payload["segment_id"] = stable_id("SEG", "hhs_pass145_segment_id_v1", payload)
        segments.append(payload)
        if len(segments) > bounds.max_segments:
            raise Pass145Error("RESOURCE_BOUNDED", "segment count bound reached", "SEGMENT")
        start = end
    return segments


def _extract_entities(text: str, source_root: str) -> list[dict[str, Any]]:
    candidates: list[tuple[str, str, int, int]] = []
    patterns = [
        ("URL", r"https?://[^\s<>\]\[(){}'\"]+"),
        ("DATE", r"\b\d{4}-\d{2}-\d{2}\b"),
        ("SYMBOL", r"(?<!\w)(?:π|Ω|Ψ|Θ|Δ|[A-Z][A-Za-z0-9_]{0,31})(?!\w)"),
        ("IDENTIFIER", r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b"),
    ]
    seen: set[tuple[str, int, int]] = set()
    for etype, pattern in patterns:
        for m in re.finditer(pattern, text):
            key = (etype, m.start(), m.end())
            if key not in seen:
                candidates.append((etype, m.group(0), m.start(), m.end()))
                seen.add(key)
    out = []
    for etype, value, a, b in sorted(candidates, key=lambda x: (x[2], x[3], x[0])):
        payload = {
            "schema": "HHS_PASS145_ENTITY_V1",
            "entity_type": etype,
            "verbatim": value,
            "normalized": unicodedata.normalize("NFC", value),
            "start_offset": a,
            "end_offset": b,
            "source_root_hash72": source_root,
        }
        payload["entity_hash72"] = hash72("hhs_pass145_entity_v1", payload)
        payload["entity_id"] = stable_id("ENT", "hhs_pass145_entity_id_v1", payload)
        out.append(payload)
    return out


def parse_document(raw: bytes, *, name: str, mime_type: str | None = None, source_kind: str = "LOCAL_FILE", namespace: str = "default", acquisition: dict[str, Any] | None = None, bounds: ParseBounds | None = None) -> dict[str, Any]:
    bounds = bounds or ParseBounds()
    bounds.validate()
    if not raw:
        raise Pass145Error("INGESTION_REJECTED", "empty document", "ADMISSION")
    if len(raw) > bounds.max_bytes:
        raise Pass145Error("RESOURCE_BOUNDED", f"source exceeds {bounds.max_bytes} bytes", "ADMISSION")
    mime = detect_mime(name, mime_type)
    if mime not in SUPPORTED_MIME:
        raise Pass145Error("INGESTION_REJECTED", f"unsupported MIME type: {mime}", "ADMISSION")
    try:
        decoded = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise Pass145Error("PARSE_FAILED", f"invalid UTF-8: {exc}", "DECODE") from exc
    text = unicodedata.normalize("NFC", decoded.replace("\r\n", "\n").replace("\r", "\n"))
    raw_sha = sha256_bytes(raw)
    source_evidence = {
        "schema": "HHS_PASS145_SOURCE_EVIDENCE_V1",
        "pass_id": PASS_ID,
        "namespace": namespace,
        "source_kind": source_kind,
        "source_name": name,
        "mime_type": mime,
        "encoding": "UTF-8",
        "byte_length": len(raw),
        "raw_sha256": raw_sha,
        "acquisition": acquisition or {},
        "parser_id": "HHS_PASS145_DETERMINISTIC_DOCUMENT_PARSER",
        "parser_version": PARSER_VERSION,
        "ingestion_policy_version": "HHS-P145-POLICY-1",
        "permission_context": "CALLER_ADMITTED_LOCAL_SOURCE",
        "execution_authority": False,
        "mutation_authority": False,
    }
    source_evidence["source_root_hash72"] = hash72("hhs_pass145_source_evidence_v1", source_evidence)
    source_evidence["source_id"] = stable_id("SRC", "hhs_pass145_source_id_v1", source_evidence)

    parsed: dict[str, Any]
    extracted_text = text
    if mime == "text/html":
        parser = _BoundedHTMLParser(bounds)
        try:
            parser.feed(text)
            parser.close()
        except Pass145Error:
            raise
        except Exception as exc:
            raise Pass145Error("PARSE_FAILED", f"HTML parse failed: {exc}", "PARSE") from exc
        parsed = parser.result()
        for script in parsed["scripts"]:
            script["static_analysis"] = _js_static_analysis(script["source"])
        extracted_text = parsed["visible_text"]
        parsed["format"] = "HTML"
    elif mime in {"text/javascript", "application/javascript"}:
        parsed = {"format": "JAVASCRIPT", "source_text": text, "static_analysis": _js_static_analysis(text), "execution": "NOT_PERFORMED"}
    elif mime in {"application/json", "application/vnd.hhs.manifest+json", "application/vnd.hhs.receipt+json", "application/x-hhs-program"}:
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise Pass145Error("PARSE_FAILED", f"invalid JSON at line {exc.lineno} column {exc.colno}", "PARSE") from exc
        try:
            canonical_value = canonical_json(value)
        except TypeError as exc:
            raise Pass145Error("RUNTIME_REJECTED", "JSON contains an undeclared IEEE floating-point value", "PARSE") from exc
        parsed = {"format": "JSON", "value": value, "canonical_json": canonical_value}
    elif mime == "application/x-ndjson":
        values = []
        for line_no, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                values.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise Pass145Error("PARSE_FAILED", f"invalid JSONL line {line_no}: {exc.msg}", "PARSE") from exc
        try:
            canonical_json(values)
        except TypeError as exc:
            raise Pass145Error("RUNTIME_REJECTED", "JSONL contains an undeclared IEEE floating-point value", "PARSE") from exc
        parsed = {"format": "JSONL", "records": values, "record_count": len(values)}
    elif mime == "text/csv":
        try:
            rows = list(csv.reader(io.StringIO(text)))
        except csv.Error as exc:
            raise Pass145Error("PARSE_FAILED", f"CSV parse failed: {exc}", "PARSE") from exc
        cells = sum(len(r) for r in rows)
        if cells > bounds.max_table_cells:
            raise Pass145Error("RESOURCE_BOUNDED", "CSV cell bound reached", "PARSE")
        parsed = {"format": "CSV", "rows": rows, "row_count": len(rows), "cell_count": cells}
    elif mime == "application/xml":
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            raise Pass145Error("PARSE_FAILED", f"XML parse failed: {exc}", "PARSE") from exc
        depth = _xml_depth(root)
        nodes = sum(1 for _ in root.iter())
        if depth > bounds.max_depth or nodes > bounds.max_nodes:
            raise Pass145Error("RESOURCE_BOUNDED", "XML structural bound reached", "PARSE")
        parsed = {
            "format": "XML",
            "root_tag": root.tag,
            "depth": depth,
            "node_count": nodes,
            "elements": [{"tag": e.tag, "attrs": dict(sorted(e.attrib.items())), "text": e.text or ""} for e in root.iter()],
        }
        extracted_text = "\n".join((e.text or "").strip() for e in root.iter() if (e.text or "").strip())
    elif mime == "text/markdown":
        headings = []
        links = []
        code_blocks = []
        in_code = False
        code_buf: list[str] = []
        for line_no, line in enumerate(text.splitlines(), 1):
            if line.startswith("```"):
                if in_code:
                    code_blocks.append({"start_line": line_no - len(code_buf) - 1, "end_line": line_no, "content": "\n".join(code_buf)})
                    code_buf = []
                in_code = not in_code
                continue
            if in_code:
                code_buf.append(line)
            m = re.match(r"^(#{1,6})\s+(.+)$", line)
            if m:
                headings.append({"level": len(m.group(1)), "text": m.group(2), "line": line_no})
            for lm in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", line):
                links.append({"text": lm.group(1), "href": lm.group(2), "line": line_no})
        parsed = {"format": "MARKDOWN", "headings": headings, "links": links, "code_blocks": code_blocks, "source_text": text}
    else:
        parsed = {"format": "TEXT", "source_text": text, "line_count": len(text.splitlines())}

    parse_payload = {
        "schema": "HHS_PASS145_PARSE_V1",
        "source_id": source_evidence["source_id"],
        "source_root_hash72": source_evidence["source_root_hash72"],
        "parser_id": source_evidence["parser_id"],
        "parser_version": PARSER_VERSION,
        "mime_type": mime,
        "parsed": parsed,
        "extracted_text": extracted_text,
        "script_execution": "NOT_PERFORMED",
    }
    parse_payload["parse_root_hash72"] = hash72("hhs_pass145_parse_v1", parse_payload)
    parse_payload["parse_id"] = stable_id("PAR", "hhs_pass145_parse_id_v1", parse_payload)
    segments = _segment_text(extracted_text, bounds, source_evidence["source_root_hash72"]) if extracted_text else []
    entities = _extract_entities(extracted_text, source_evidence["source_root_hash72"])
    return {
        "source": source_evidence,
        "raw_bytes": raw,
        "parse": parse_payload,
        "segments": segments,
        "entities": entities,
    }
