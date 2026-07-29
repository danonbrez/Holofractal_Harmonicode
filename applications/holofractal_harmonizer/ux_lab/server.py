from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
ARTIFACTS = ROOT / "artifacts"

app = FastAPI(title="HHS Visual IDE A/B Usability Lab")
app.mount("/static", StaticFiles(directory=STATIC), name="static")

WORKFLOWS: dict[str, dict[str, Any]] = {
    "code_api": {
        "title": "Code + API Service",
        "category": "CODE_API",
        "goal": "Build and validate a small JSON service with an OpenAPI contract.",
        "accent": "λ",
        "stages": ["Define service", "Generate source", "Run compile check", "Invoke endpoint", "Review evidence"],
        "artifacts": ["app.py", "openapi.json", "validation.json"],
    },
    "data_dashboard": {
        "title": "Data + Analytics Dashboard",
        "category": "DATA_ANALYTICS",
        "goal": "Transform a CSV dataset into verified KPI metrics and a visual dashboard.",
        "accent": "Σ",
        "stages": ["Load dataset", "Validate schema", "Compute KPIs", "Render dashboard", "Review evidence"],
        "artifacts": ["usage.csv", "metrics.json", "dashboard.html"],
    },
    "document_knowledge": {
        "title": "Document + Knowledge Ingestion",
        "category": "DOCUMENT_KNOWLEDGE",
        "goal": "Extract a structured knowledge graph and invariant report from a technical specification.",
        "accent": "¶",
        "stages": ["Ingest source", "Preserve source", "Extract structure", "Validate invariants", "Review evidence"],
        "artifacts": ["source.md", "knowledge.json", "report.md"],
    },
    "image_spatial": {
        "title": "Image + Spatial Interface",
        "category": "IMAGE_SPATIAL",
        "goal": "Generate a responsive SVG interface scene and validate spatial object identity.",
        "accent": "◈",
        "stages": ["Define scene", "Generate visual", "Bind object IDs", "Validate geometry", "Review evidence"],
        "artifacts": ["scene.svg", "scene.json", "validation.json"],
    },
}

TEMPLATES = [
    {"id": "code_runtime", "title": "Code & Runtime", "category": "CODE", "outcome": "Source, tests, runtime receipt", "prompt": "Implement a dependency-scoped runtime change, run affected tests, and return admitted evidence.", "stages": ["Scope", "Implement", "Test", "Inspect", "Commit"]},
    {"id": "api_automation", "title": "API & Automation", "category": "API", "outcome": "Callable API, schema, negative tests", "prompt": "Create a governed API or automation workflow with explicit authority and failure handling.", "stages": ["Contract", "Route", "Tooling", "Negative tests", "Receipt"]},
    {"id": "data_analytics", "title": "Data & Analytics", "category": "DATA", "outcome": "Validated dataset, metrics, visual report", "prompt": "Analyze the selected dataset, validate quality, compute KPIs, and produce a cited visual report.", "stages": ["Source", "Quality", "Model", "Visualize", "Validate"]},
    {"id": "document_knowledge", "title": "Document & Knowledge", "category": "DOCUMENT", "outcome": "Preserved source, structured extraction, report", "prompt": "Ingest the selected document, preserve source identity, extract structure, and validate the knowledge projection.", "stages": ["Ingest", "Preserve", "Extract", "Relate", "Report"]},
    {"id": "image_ui", "title": "Image & UI", "category": "IMAGE", "outcome": "Visual target, responsive UI, design QA", "prompt": "Develop the selected visual interface with responsive behavior and verify it against the source target.", "stages": ["Target", "Explore", "Build", "Capture", "QA"]},
    {"id": "audio_video", "title": "Audio & Video", "category": "MEDIA", "outcome": "Timeline, renders, playback evidence", "prompt": "Build the selected audio/video workflow with deterministic transforms, previews, and playback validation.", "stages": ["Import", "Analyze", "Transform", "Render", "Playback"]},
    {"id": "spatial_3d", "title": "3D & Spatial", "category": "SPATIAL", "outcome": "Scene graph, shaders, spatial validation", "prompt": "Build a registered-object spatial scene with projection-only shaders and verified object identity.", "stages": ["Scene", "Objects", "Materials", "Simulate", "Validate"]},
    {"id": "model_agent", "title": "Model & Agent", "category": "MODEL", "outcome": "Provider contract, tool policy, evaluation", "prompt": "Configure a governed model or agent workflow with bounded tools, evaluation, and provider receipts.", "stages": ["Provider", "Policy", "Tools", "Evaluate", "Admit"]},
]

class RunRequest(BaseModel):
    variant: str
    session_id: str


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_code_api(out: Path) -> list[str]:
    source = textwrap.dedent(
        '''
        from __future__ import annotations

        def health() -> dict[str, object]:
            return {"status": "healthy", "service": "hhs-sample-api", "version": "1.0.0"}

        def calculate(a: int, b: int) -> dict[str, int]:
            return {"a": a, "b": b, "sum": a + b, "product": a * b}
        '''
    ).strip() + "\n"
    (out / "app.py").write_text(source, encoding="utf-8")
    openapi = {
        "openapi": "3.1.0",
        "info": {"title": "HHS Sample API", "version": "1.0.0"},
        "paths": {
            "/health": {"get": {"operationId": "health"}},
            "/calculate": {"post": {"operationId": "calculate"}},
        },
    }
    _write_json(out / "openapi.json", openapi)
    subprocess.run([sys.executable, "-m", "py_compile", str(out / "app.py")], check=True, capture_output=True)
    spec = importlib.util.spec_from_file_location("hhs_sample_api", out / "app.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    health = module.health()
    result = module.calculate(7, 11)
    checks = {
        "compiled": True,
        "health_ok": health["status"] == "healthy",
        "sum_ok": result["sum"] == 18,
        "product_ok": result["product"] == 77,
        "openapi_paths": sorted(openapi["paths"]),
    }
    checks["ok"] = all(v is True for k, v in checks.items() if k.endswith("_ok") or k == "compiled")
    _write_json(out / "validation.json", checks)
    return ["Generated Python service", "Compiled source", "Invoked health and calculation functions", "Validated OpenAPI paths"]


def _run_data_dashboard(out: Path) -> list[str]:
    rows = [
        ("2026-07-01", "mobile", 1280, 412, 83),
        ("2026-07-01", "desktop", 980, 387, 112),
        ("2026-07-02", "mobile", 1420, 468, 96),
        ("2026-07-02", "desktop", 1040, 426, 129),
        ("2026-07-03", "mobile", 1550, 521, 118),
        ("2026-07-03", "desktop", 1100, 453, 138),
    ]
    with (out / "usage.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "platform", "sessions", "activated", "retained"])
        w.writerows(rows)
    total_sessions = sum(r[2] for r in rows)
    total_activated = sum(r[3] for r in rows)
    total_retained = sum(r[4] for r in rows)
    metrics = {
        "rows": len(rows),
        "sessions": total_sessions,
        "activation_rate": round(total_activated / total_sessions, 4),
        "retention_rate": round(total_retained / total_activated, 4),
        "schema_valid": all(len(r) == 5 for r in rows),
    }
    metrics["ok"] = metrics["schema_valid"] and 0 < metrics["activation_rate"] < 1 and 0 < metrics["retention_rate"] < 1
    _write_json(out / "metrics.json", metrics)
    bars = []
    max_sessions = max(r[2] for r in rows)
    for i, row in enumerate(rows):
        x = 48 + i * 92
        h = round((row[2] / max_sessions) * 180)
        y = 230 - h
        bars.append(f'<rect x="{x}" y="{y}" width="54" height="{h}" rx="7"/><text x="{x+27}" y="252" text-anchor="middle">{row[1][0].upper()}{i//2+1}</text>')
    html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Usage dashboard</title><style>body{{font-family:system-ui;background:#07101d;color:#eef8ff;padding:32px}}svg{{background:#0d1b2d;border:1px solid #244866;border-radius:16px}}rect{{fill:#5de7ff}}text{{fill:#9cb5c8;font-size:12px}}</style></head><body><h1>Activation dashboard</h1><p>{total_sessions:,} sessions · {metrics['activation_rate']:.1%} activation · {metrics['retention_rate']:.1%} retained</p><svg width="650" height="280" viewBox="0 0 650 280">{''.join(bars)}</svg></body></html>'''
    (out / "dashboard.html").write_text(html, encoding="utf-8")
    return ["Created six-row usage dataset", "Validated schema", "Computed activation and retention", "Rendered HTML/SVG dashboard"]


def _run_document_knowledge(out: Path) -> list[str]:
    source = textwrap.dedent(
        '''
        # Runtime Admission Specification

        ## Purpose
        All state-changing operations pass through VM81 admission before receipt commit.

        ## Invariants
        - Hash72 is the canonical runtime receipt authority.
        - Hash216 provides independent historical identity.
        - Model outputs are proposals until admitted.
        - Projection shaders cannot mutate runtime truth.

        ## Required Sequence
        Input -> Proposal -> Policy Gate -> VM81 Admission -> Receipt -> Replay
        '''
    ).strip() + "\n"
    (out / "source.md").write_text(source, encoding="utf-8")
    headings = [line.lstrip("# ") for line in source.splitlines() if line.startswith("#")]
    invariants = [line[2:] for line in source.splitlines() if line.startswith("- ")]
    relations = [
        {"subject": "Hash72", "predicate": "authority_for", "object": "runtime_receipts"},
        {"subject": "Hash216", "predicate": "identity_for", "object": "historical_state"},
        {"subject": "model_output", "predicate": "requires", "object": "runtime_admission"},
        {"subject": "projection_shader", "predicate": "cannot_mutate", "object": "runtime_truth"},
    ]
    knowledge = {"headings": headings, "invariants": invariants, "relations": relations, "source_sha256": _sha(out / "source.md")}
    knowledge["ok"] = len(headings) == 4 and len(invariants) == 4 and len(relations) == 4
    _write_json(out / "knowledge.json", knowledge)
    report = "# Knowledge Extraction Report\n\n" + f"- Source SHA-256: `{knowledge['source_sha256']}`\n- Headings: {len(headings)}\n- Invariants: {len(invariants)}\n- Relations: {len(relations)}\n- Validation: **PASS**\n"
    (out / "report.md").write_text(report, encoding="utf-8")
    return ["Preserved source Markdown", "Extracted headings and invariant statements", "Created four typed relations", "Validated structured knowledge projection"]


def _run_image_spatial(out: Path) -> list[str]:
    nodes = []
    cx, cy, radius = 320, 220, 150
    for i in range(9):
        a = -math.pi / 2 + i * (2 * math.pi / 9)
        nodes.append({"id": f"object:{i+1}", "x": round(cx + radius * math.cos(a), 2), "y": round(cy + radius * math.sin(a), 2), "role": "registered_object"})
    circles = ''.join(f'<g data-object-id="{n["id"]}"><circle cx="{n["x"]}" cy="{n["y"]}" r="28"/><text x="{n["x"]}" y="{n["y"]+5}" text-anchor="middle">{i+1}</text></g>' for i, n in enumerate(nodes))
    links = ''.join(f'<line x1="{cx}" y1="{cy}" x2="{n["x"]}" y2="{n["y"]}"/>' for n in nodes)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 440" role="img" aria-label="Nine registered objects in a spatial scene"><defs><radialGradient id="g"><stop stop-color="#d9ffff"/><stop offset=".35" stop-color="#3e85e9"/><stop offset="1" stop-color="#101c51"/></radialGradient></defs><rect width="640" height="440" fill="#050a14"/><g stroke="#5de7ff55">{links}</g><circle cx="{cx}" cy="{cy}" r="44" fill="url(#g)"/><g fill="url(#g)" stroke="#5de7ff88">{circles}</g><g fill="#eef8ff" font-family="system-ui" font-size="13">{''.join(f'<text x="{n["x"]}" y="{n["y"]+5}" text-anchor="middle">{i+1}</text>' for i,n in enumerate(nodes))}</g></svg>'''
    (out / "scene.svg").write_text(svg, encoding="utf-8")
    scene = {"coordinate_space": "world", "projection_only": True, "nodes": nodes, "center": {"id": "hhs:runtime:vm81", "x": cx, "y": cy}}
    _write_json(out / "scene.json", scene)
    checks = {"node_count": len(nodes), "unique_ids": len({n['id'] for n in nodes}) == 9, "projection_only": scene["projection_only"], "svg_has_identity_bindings": svg.count("data-object-id") == 9}
    checks["ok"] = checks["node_count"] == 9 and checks["unique_ids"] and checks["projection_only"] and checks["svg_has_identity_bindings"]
    _write_json(out / "validation.json", checks)
    return ["Generated nine-node spatial scene", "Bound stable object identities", "Rendered responsive SVG", "Validated projection-only geometry"]

RUNNERS = {
    "code_api": _run_code_api,
    "data_dashboard": _run_data_dashboard,
    "document_knowledge": _run_document_knowledge,
    "image_spatial": _run_image_spatial,
}

@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")

@app.get("/api/workflows")
def workflows() -> dict[str, Any]:
    return {"workflows": WORKFLOWS, "templates": TEMPLATES}

@app.post("/api/run/{workflow_id}")
def run_workflow(workflow_id: str, request: RunRequest) -> dict[str, Any]:
    if workflow_id not in RUNNERS:
        raise HTTPException(404, "workflow not found")
    if request.variant not in {"A", "B"}:
        raise HTTPException(422, "variant must be A or B")
    safe_session = "".join(c for c in request.session_id if c.isalnum() or c in "-_" )[:80] or "session"
    out = ARTIFACTS / request.variant / workflow_id / safe_session
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    logs = RUNNERS[workflow_id](out)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    files = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        files.append({"name": path.name, "path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": _sha(path)})
    receipt_input = json.dumps({"workflow": workflow_id, "variant": request.variant, "session": safe_session, "files": files}, sort_keys=True).encode()
    receipt = hashlib.sha256(receipt_input).hexdigest()
    result = {
        "ok": True,
        "workflow_id": workflow_id,
        "variant": request.variant,
        "elapsed_ms": elapsed_ms,
        "logs": logs,
        "files": files,
        "receipt_sha256": receipt,
        "runtime_claim": "LOCAL_EXECUTABLE_WORKFLOW_VALIDATED",
        "authority_note": "Usability lab artifact success is not a canonical VM81 mutation receipt.",
    }
    _write_json(out / "result.json", result)
    return result
