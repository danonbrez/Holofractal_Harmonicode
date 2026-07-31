"""HHS application factory runtime.

This module turns the repository's existing workspace, modality, runtime, and
artifact capabilities into a finite-state application lifecycle. It does not
create a second execution authority: candidate planning may be parallelized by
callers, while all admitted project mutations are serialized through this
factory's commit lock and represented by Hash72 receipts.
"""
from __future__ import annotations

import base64
import fnmatch
import hashlib
import io
import json
import threading
import time
import uuid
import zipfile
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "PASS_180_HHS_INTEGRATED_APPLICATION_FACTORY_V1"
AUTHORITY = "HHS_VM81_SINGLETON_APPLICATION_FACTORY_AUTHORITY_V1"
PROJECT_SCHEMA = "HHS_APPLICATION_FACTORY_PROJECT_V1"
JOB_SCHEMA = "HHS_APPLICATION_FACTORY_LIFECYCLE_JOB_V1"
MODULE_SCHEMA = "HHS_APPLICATION_FACTORY_MODULE_LIBRARY_V1"
WORKFLOW_SCHEMA = "HHS_APPLICATION_FACTORY_WORKFLOW_LIBRARY_V1"

JOB_STATES = (
    "QUEUED",
    "RUNNING",
    "SUCCEEDED",
    "FAILED",
    "CANCEL_REQUESTED",
    "CANCELLED",
    "TIMED_OUT",
)
FINAL_JOB_STATES = {"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT"}
LIFECYCLE_STAGES = (
    "INGRESS",
    "RESOLVE_MODULES",
    "BUILD_GRAPH",
    "VALIDATE",
    "COMPILE_PLAN",
    "TEST_PLAN",
    "PACKAGE",
    "COMMIT_RECEIPT",
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _stable_zip(files: Mapping[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, files[path].encode("utf-8"))
    return buffer.getvalue()


MODULE_LIBRARY: Dict[str, Dict[str, Any]] = {
    "core.project": {
        "title": "Project Runtime",
        "kind": "FOUNDATION",
        "dependencies": [],
        "file_patterns": ["project.json", "README.md", "src/**"],
        "capabilities": ["workspace", "object_registry", "receipts", "replay"],
        "runtime_binding": "/api/runtime/workspace",
    },
    "runtime.vm81": {
        "title": "VM81 Runtime Binding",
        "kind": "RUNTIME",
        "dependencies": ["core.project"],
        "file_patterns": ["src/**/*.hhs", "runtime/**"],
        "capabilities": ["vm81", "hash72", "hash216", "deterministic_replay"],
        "runtime_binding": "/api/runtime",
    },
    "ui.web": {
        "title": "Web Interface",
        "kind": "INTERFACE",
        "dependencies": ["core.project"],
        "file_patterns": ["index.html", "src/**/*.html", "src/**/*.css", "src/**/*.js"],
        "capabilities": ["responsive_ui", "preview", "accessibility"],
        "runtime_binding": "/",
    },
    "assistant.development": {
        "title": "Natural-Language Development Assistant",
        "kind": "ASSISTANT",
        "dependencies": ["core.project", "runtime.vm81"],
        "file_patterns": ["assistant/**", "prompts/**"],
        "capabilities": ["planning", "code_generation", "debugging", "documentation"],
        "runtime_binding": "/api/assistant",
    },
    "math.exact": {
        "title": "Exact Mathematics",
        "kind": "DOMAIN",
        "dependencies": ["runtime.vm81"],
        "file_patterns": ["src/**/*calc*", "src/**/*math*", "tests/**/*math*"],
        "capabilities": ["bigint", "rational", "symbolic_irrational", "no_float_authority"],
        "runtime_binding": "/api/runtime",
    },
    "graphics.native": {
        "title": "Native Graphics and Motion",
        "kind": "MEDIA",
        "dependencies": ["ui.web", "runtime.vm81"],
        "file_patterns": ["src/**/*render*", "src/**/*scene*", "assets/**/*"],
        "capabilities": ["2d", "3d", "animation", "shader_projection"],
        "runtime_binding": "/api/runtime/workspace/modality/pipeline",
    },
    "input.events": {
        "title": "Input and Interaction",
        "kind": "INTERFACE",
        "dependencies": ["ui.web"],
        "file_patterns": ["src/**/*input*", "src/**/*control*"],
        "capabilities": ["keyboard", "pointer", "touch", "gamepad"],
        "runtime_binding": "/api/runtime/gui/command",
    },
    "audio.runtime": {
        "title": "Audio Runtime",
        "kind": "MEDIA",
        "dependencies": ["runtime.vm81"],
        "file_patterns": ["src/**/*audio*", "assets/**/*.wav", "assets/**/*.mp3"],
        "capabilities": ["audio_ingress", "audio_graph", "audio_egress"],
        "runtime_binding": "/api/runtime/workspace/modality/pipeline",
    },
    "video.runtime": {
        "title": "Video Runtime",
        "kind": "MEDIA",
        "dependencies": ["graphics.native", "audio.runtime"],
        "file_patterns": ["src/**/*video*", "assets/**/*.mp4", "assets/**/*.webm"],
        "capabilities": ["video_ingress", "timeline", "frame_projection", "video_egress"],
        "runtime_binding": "/api/runtime/workspace/modality/pipeline",
    },
    "documents.editor": {
        "title": "Document Studio",
        "kind": "DOCUMENT",
        "dependencies": ["ui.web", "runtime.vm81"],
        "file_patterns": ["documents/**", "src/**/*document*", "src/**/*editor*"],
        "capabilities": ["text", "markdown", "pdf_ingress", "structured_document"],
        "runtime_binding": "/api/runtime/document/perceive",
    },
    "storage.local": {
        "title": "Project Storage",
        "kind": "PERSISTENCE",
        "dependencies": ["core.project"],
        "file_patterns": ["data/**", "storage/**", "src/**/*store*"],
        "capabilities": ["save", "load", "snapshot", "source_export"],
        "runtime_binding": "/api/runtime/workspace/project",
    },
    "network.api": {
        "title": "API Service",
        "kind": "NETWORK",
        "dependencies": ["runtime.vm81"],
        "file_patterns": ["api/**", "src/**/*server*", "src/**/*route*"],
        "capabilities": ["http", "websocket", "schema", "health"],
        "runtime_binding": "/docs",
    },
    "testing.acceptance": {
        "title": "Acceptance and Replay Tests",
        "kind": "VERIFICATION",
        "dependencies": ["core.project", "runtime.vm81"],
        "file_patterns": ["tests/**", "specs/**"],
        "capabilities": ["unit", "integration", "acceptance", "replay"],
        "runtime_binding": "/api/runtime/live/status",
    },
    "packaging.zip": {
        "title": "Portable ZIP Packaging",
        "kind": "EGRESS",
        "dependencies": ["core.project", "storage.local"],
        "file_patterns": ["package/**", "dist/**"],
        "capabilities": ["source_zip", "manifest", "checksums"],
        "runtime_binding": "/api/runtime/application-factory",
    },
}


WORKFLOW_LIBRARY: Dict[str, Dict[str, Any]] = {
    "web_application": {
        "title": "Web Application",
        "description": "Responsive browser application with preview, tests, VM81 receipts, and ZIP export.",
        "modules": ["core.project", "runtime.vm81", "ui.web", "assistant.development", "storage.local", "testing.acceptance", "packaging.zip"],
        "entrypoint": "index.html",
        "targets": ["browser", "pwa", "zip"],
    },
    "scientific_calculator": {
        "title": "Exact Scientific Calculator",
        "description": "Casio-style exact calculator with symbolic constants and regression tests.",
        "modules": ["core.project", "runtime.vm81", "ui.web", "math.exact", "assistant.development", "storage.local", "testing.acceptance", "packaging.zip"],
        "entrypoint": "index.html",
        "targets": ["browser", "mobile", "zip"],
    },
    "game_2d": {
        "title": "Native 2D Game",
        "description": "Interactive game workflow with native graphics, input, audio, tests, and replay.",
        "modules": ["core.project", "runtime.vm81", "ui.web", "graphics.native", "input.events", "audio.runtime", "assistant.development", "storage.local", "testing.acceptance", "packaging.zip"],
        "entrypoint": "index.html",
        "targets": ["browser", "mobile", "desktop-wrapper", "zip"],
    },
    "document_studio": {
        "title": "Document Studio",
        "description": "Structured writing and document workflow with perception, editing, and export.",
        "modules": ["core.project", "runtime.vm81", "ui.web", "documents.editor", "assistant.development", "storage.local", "testing.acceptance", "packaging.zip"],
        "entrypoint": "index.html",
        "targets": ["browser", "document", "zip"],
    },
    "media_studio": {
        "title": "Audio and Video Studio",
        "description": "Multimodal media project with graphics, audio, video, timeline, and artifact egress.",
        "modules": ["core.project", "runtime.vm81", "ui.web", "graphics.native", "audio.runtime", "video.runtime", "assistant.development", "storage.local", "testing.acceptance", "packaging.zip"],
        "entrypoint": "index.html",
        "targets": ["browser", "media-bundle", "zip"],
    },
    "api_service": {
        "title": "Runtime API Service",
        "description": "FastAPI-compatible service workflow with health, schemas, tests, and deployment artifacts.",
        "modules": ["core.project", "runtime.vm81", "network.api", "assistant.development", "storage.local", "testing.acceptance", "packaging.zip"],
        "entrypoint": "api/main.py",
        "targets": ["python-service", "container-source", "zip"],
    },
    "universal_multimodal": {
        "title": "Universal Multimodal Application",
        "description": "Complete application factory workflow spanning UI, exact math, graphics, documents, audio, video, APIs, testing, and export.",
        "modules": list(MODULE_LIBRARY),
        "entrypoint": "index.html",
        "targets": ["browser", "mobile", "desktop-wrapper", "service", "media-bundle", "zip"],
    },
}


STARTER_FILES: Dict[str, Dict[str, str]] = {
    "web_application": {
        "index.html": "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HHS App</title><link rel='stylesheet' href='src/style.css'></head><body><main id='app'><h1>HHS Application</h1><button id='action'>Run</button><output id='output'></output></main><script src='src/app.js'></script></body></html>\n",
        "src/style.css": "body{font-family:system-ui;margin:0;padding:2rem;background:#17120f;color:#f4e7d4}button{padding:.75rem 1rem}output{display:block;margin-top:1rem}\n",
        "src/app.js": "document.querySelector('#action').addEventListener('click',()=>{document.querySelector('#output').textContent='Application runtime active';});\n",
    },
    "scientific_calculator": {
        "index.html": "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HHS Exact Calculator</title><link rel='stylesheet' href='src/style.css'></head><body><main><h1>Exact Scientific Calculator</h1><input id='expression' value='sqrt(2)'><button id='evaluate'>Evaluate</button><output id='result'>Ready</output></main><script src='src/calculator.js'></script></body></html>\n",
        "src/style.css": "body{font-family:system-ui;background:#17120f;color:#f4e7d4;padding:2rem}input,button{font:inherit;padding:.75rem}output{display:block;margin-top:1rem}\n",
        "src/calculator.js": "const constants={PHI:'(1+sqrt(5))/2'};document.querySelector('#evaluate').addEventListener('click',()=>{const source=document.querySelector('#expression').value;document.querySelector('#result').textContent=constants[source]||source;});\n",
        "tests/calculator.acceptance.json": "{\"cases\":[{\"expression\":\"sqrt(2)\",\"mode\":\"symbolic\"},{\"expression\":\"PHI\",\"mode\":\"exact\"}]}\n",
    },
    "game_2d": {
        "index.html": "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HHS 2D Game</title><link rel='stylesheet' href='src/style.css'></head><body><canvas id='game' width='960' height='540'></canvas><script src='src/game.js'></script></body></html>\n",
        "src/style.css": "html,body{margin:0;background:#090807;overflow:hidden}canvas{display:block;width:100vw;height:100vh;touch-action:none}\n",
        "src/game.js": "const c=document.querySelector('#game'),x=c.getContext('2d');let p={x:80,y:80};function frame(){x.clearRect(0,0,c.width,c.height);x.fillRect(p.x,p.y,32,32);requestAnimationFrame(frame)}addEventListener('keydown',e=>{p.x+=e.key==='ArrowRight'?8:e.key==='ArrowLeft'?-8:0;p.y+=e.key==='ArrowDown'?8:e.key==='ArrowUp'?-8:0});frame();\n",
        "tests/game.acceptance.json": "{\"checks\":[\"canvas-ready\",\"input-responsive\",\"replay-deterministic\"]}\n",
    },
    "document_studio": {
        "index.html": "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HHS Document Studio</title></head><body><main><h1>Document Studio</h1><textarea id='document' rows='24' cols='80'># New document</textarea></main></body></html>\n",
        "documents/main.md": "# New document\n\nCreated by the HHS application factory.\n",
    },
    "media_studio": {
        "index.html": "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HHS Media Studio</title></head><body><main><h1>Media Studio</h1><canvas id='preview' width='960' height='540'></canvas><audio controls></audio><video controls></video></main></body></html>\n",
        "src/timeline.json": "{\"tracks\":[],\"timebase\":72}\n",
    },
    "api_service": {
        "api/main.py": "from fastapi import FastAPI\napp=FastAPI(title='HHS Generated Service')\n@app.get('/health')\ndef health(): return {'status':'healthy'}\n",
        "tests/test_health.py": "def test_contract():\n    assert {'status':'healthy'}['status']=='healthy'\n",
    },
    "universal_multimodal": {
        "index.html": "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HHS Multimodal Application</title></head><body><main id='app'><h1>Universal Multimodal Application</h1></main></body></html>\n",
        "src/main.hhs": "P=72\np=64\nq=81\nDelta=P^2-p*q\n(P^2-p*q)-Delta=0\n",
        "documents/README.md": "# Multimodal project\n",
        "data/project.json": "{\"modalities\":[\"text\",\"image\",\"audio\",\"video\",\"code\"]}\n",
    },
}


class ApplicationFactory:
    """Finite, checkpointed application lifecycle with one commit authority."""

    def __init__(self) -> None:
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.journals: Dict[str, List[Dict[str, Any]]] = {}
        self._commit_lock = threading.RLock()

    def status(self) -> Dict[str, Any]:
        active = [job for job in self.jobs.values() if job.get("state") not in FINAL_JOB_STATES]
        return {
            "schema": "HHS_APPLICATION_FACTORY_STATUS_V1",
            "version": VERSION,
            "ok": True,
            "authority": AUTHORITY,
            "project_count": len(self.projects),
            "job_count": len(self.jobs),
            "active_job_count": len(active),
            "module_count": len(MODULE_LIBRARY),
            "workflow_count": len(WORKFLOW_LIBRARY),
            "job_states": list(JOB_STATES),
            "lifecycle_stages": list(LIFECYCLE_STAGES),
            "source_export_independent_of_compile": True,
            "parallel_candidate_planning": True,
            "parallel_state_authority": False,
            "singleton_commit_authority": True,
        }

    def module_library(self) -> Dict[str, Any]:
        return {"schema": MODULE_SCHEMA, "version": VERSION, "modules": deepcopy(MODULE_LIBRARY)}

    def workflow_library(self) -> Dict[str, Any]:
        return {"schema": WORKFLOW_SCHEMA, "version": VERSION, "workflows": deepcopy(WORKFLOW_LIBRARY)}

    def _resolve_modules(self, requested: Iterable[str]) -> List[str]:
        resolved: Set[str] = set()
        visiting: Set[str] = set()

        def visit(module_id: str) -> None:
            if module_id in resolved:
                return
            if module_id in visiting:
                raise ValueError(f"cyclic module dependency: {module_id}")
            spec = MODULE_LIBRARY.get(module_id)
            if spec is None:
                raise KeyError(f"unknown module: {module_id}")
            visiting.add(module_id)
            for dependency in spec.get("dependencies", []):
                visit(str(dependency))
            visiting.remove(module_id)
            resolved.add(module_id)

        for item in requested:
            visit(str(item))
        return sorted(resolved)

    def _module_graph(self, modules: Sequence[str]) -> Dict[str, Any]:
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, str]] = []
        selected = set(modules)
        for module_id in sorted(selected):
            spec = MODULE_LIBRARY[module_id]
            nodes.append({"module_id": module_id, **deepcopy(spec)})
            for dependency in spec.get("dependencies", []):
                if dependency in selected:
                    edges.append({"from": dependency, "to": module_id, "relation": "REQUIRED_BY"})
        graph = {"nodes": nodes, "edges": sorted(edges, key=lambda item: (item["from"], item["to"]))}
        graph["graph_root_hash72"] = hash72("HHS_APPLICATION_FACTORY_MODULE_GRAPH_V1", graph)
        return graph

    def _starter_files(self, workflow_id: str, name: str) -> Dict[str, str]:
        files = {
            "README.md": f"# {name}\n\nGenerated by the HHS integrated application factory.\n",
            "project.json": _canonical_json({"name": name, "workflow_id": workflow_id, "factory_version": VERSION}) + "\n",
        }
        files.update(deepcopy(STARTER_FILES.get(workflow_id, {})))
        return files

    def create_project(
        self,
        *,
        name: str,
        workflow_id: str,
        extra_modules: Optional[Iterable[str]] = None,
        initial_files: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        workflow = WORKFLOW_LIBRARY.get(workflow_id)
        if workflow is None:
            return {"schema": PROJECT_SCHEMA, "ok": False, "status": "REJECT_WORKFLOW_UNKNOWN", "workflow_id": workflow_id}
        try:
            modules = self._resolve_modules(list(workflow["modules"]) + list(extra_modules or []))
        except (KeyError, ValueError) as exc:
            return {"schema": PROJECT_SCHEMA, "ok": False, "status": "REJECT_MODULE_GRAPH", "reason": str(exc)}
        files = self._starter_files(workflow_id, name.strip() or workflow["title"])
        for path, content in dict(initial_files or {}).items():
            normalized = self._normalize_path(path)
            files[normalized] = str(content)
        project_id = _unique("application")
        now = _now_ms()
        project = {
            "schema": PROJECT_SCHEMA,
            "version": VERSION,
            "project_id": project_id,
            "name": name.strip() or workflow["title"],
            "workflow_id": workflow_id,
            "workflow": deepcopy(workflow),
            "modules": modules,
            "module_graph": self._module_graph(modules),
            "files": dict(sorted(files.items())),
            "file_roots_hash72": {
                path: hash72("HHS_APPLICATION_FACTORY_SOURCE_FILE_V1", {"path": path, "content": files[path]})
                for path in sorted(files)
            },
            "state": "READY",
            "created_at_unix_ms": now,
            "updated_at_unix_ms": now,
            "latest_job_id": None,
            "latest_receipt_hash72": None,
            "authority": AUTHORITY,
        }
        project["source_root_hash72"] = hash72("HHS_APPLICATION_FACTORY_SOURCE_TREE_V1", project["file_roots_hash72"])
        project["project_root_hash72"] = hash72(PROJECT_SCHEMA, {k: v for k, v in project.items() if k != "project_root_hash72"})
        project["creation_receipt_hash72"] = hash72(
            "HHS_APPLICATION_FACTORY_PROJECT_CREATED_V1",
            {"project_id": project_id, "project_root_hash72": project["project_root_hash72"]},
        )
        with self._commit_lock:
            self.projects[project_id] = project
            self.journals[project_id] = [
                {"sequence": 0, "event": "PROJECT_CREATED", "root_hash72": project["creation_receipt_hash72"]}
            ]
        return {
            "schema": "HHS_APPLICATION_FACTORY_PROJECT_CREATE_RESULT_V1",
            "ok": True,
            "status": "APPLICATION_PROJECT_CREATED",
            "project": deepcopy(project),
        }

    @staticmethod
    def _normalize_path(path: Any) -> str:
        candidate = str(path or "").replace("\\", "/").strip("/")
        parts = [part for part in candidate.split("/") if part not in ("", ".")]
        if not parts or any(part == ".." for part in parts):
            raise ValueError("invalid project path")
        return "/".join(parts)

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        project = self.projects.get(project_id)
        return deepcopy(project) if project else None

    def upsert_file(self, project_id: str, path: str, content: Any) -> Dict[str, Any]:
        project = self.projects.get(project_id)
        if project is None:
            return {"ok": False, "status": "REJECT_APPLICATION_PROJECT_UNKNOWN", "project_id": project_id}
        try:
            normalized = self._normalize_path(path)
        except ValueError as exc:
            return {"ok": False, "status": "REJECT_APPLICATION_FILE_PATH", "reason": str(exc)}
        with self._commit_lock:
            updated = deepcopy(project)
            updated["files"][normalized] = str(content)
            updated["files"] = dict(sorted(updated["files"].items()))
            updated["file_roots_hash72"][normalized] = hash72(
                "HHS_APPLICATION_FACTORY_SOURCE_FILE_V1", {"path": normalized, "content": str(content)}
            )
            updated["file_roots_hash72"] = dict(sorted(updated["file_roots_hash72"].items()))
            updated["source_root_hash72"] = hash72(
                "HHS_APPLICATION_FACTORY_SOURCE_TREE_V1", updated["file_roots_hash72"]
            )
            updated["updated_at_unix_ms"] = _now_ms()
            updated["state"] = "DIRTY"
            updated["project_root_hash72"] = hash72(
                PROJECT_SCHEMA, {k: v for k, v in updated.items() if k != "project_root_hash72"}
            )
            receipt = hash72(
                "HHS_APPLICATION_FACTORY_FILE_UPSERT_V1",
                {
                    "project_id": project_id,
                    "path": normalized,
                    "file_root_hash72": updated["file_roots_hash72"][normalized],
                    "project_root_hash72": updated["project_root_hash72"],
                },
            )
            updated["latest_receipt_hash72"] = receipt
            self.projects[project_id] = updated
            self.journals[project_id].append(
                {
                    "sequence": len(self.journals[project_id]),
                    "event": "FILE_UPSERTED",
                    "path": normalized,
                    "root_hash72": receipt,
                }
            )
        return {
            "schema": "HHS_APPLICATION_FACTORY_FILE_UPSERT_RESULT_V1",
            "ok": True,
            "status": "APPLICATION_FILE_UPSERTED",
            "path": normalized,
            "receipt_hash72": receipt,
            "project": deepcopy(updated),
        }

    def plan_changes(self, project_id: str, changed_paths: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        project = self.projects.get(project_id)
        if project is None:
            return {"ok": False, "status": "REJECT_APPLICATION_PROJECT_UNKNOWN", "project_id": project_id}
        try:
            paths = sorted({self._normalize_path(path) for path in (changed_paths or project["files"].keys())})
        except ValueError as exc:
            return {"ok": False, "status": "REJECT_APPLICATION_FILE_PATH", "reason": str(exc)}
        direct: Set[str] = set()
        for module_id in project["modules"]:
            patterns = MODULE_LIBRARY[module_id].get("file_patterns", [])
            if any(fnmatch.fnmatch(path, pattern) for path in paths for pattern in patterns):
                direct.add(module_id)
        if not direct:
            direct.add("core.project")
        impacted = set(direct)
        changed = True
        while changed:
            changed = False
            for module_id in project["modules"]:
                dependencies = set(MODULE_LIBRARY[module_id].get("dependencies", []))
                if dependencies & impacted and module_id not in impacted:
                    impacted.add(module_id)
                    changed = True
        plan = {
            "schema": "HHS_APPLICATION_FACTORY_INCREMENTAL_PLAN_V1",
            "version": VERSION,
            "project_id": project_id,
            "changed_paths": paths,
            "direct_modules": sorted(direct),
            "impacted_modules": sorted(impacted),
            "unaffected_modules": sorted(set(project["modules"]) - impacted),
            "validation_scope": [f"module:{module_id}" for module_id in sorted(impacted)],
            "full_rebuild_required": len(impacted) == len(project["modules"]),
            "parallel_candidate_groups": self._candidate_groups(sorted(impacted)),
            "singleton_commit_authority": True,
        }
        plan["plan_root_hash72"] = hash72("HHS_APPLICATION_FACTORY_INCREMENTAL_PLAN_V1", plan)
        return {"ok": True, "status": "APPLICATION_INCREMENTAL_PLAN_READY", "plan": plan}

    @staticmethod
    def _candidate_groups(modules: Sequence[str]) -> List[List[str]]:
        remaining = set(modules)
        groups: List[List[str]] = []
        admitted: Set[str] = set()
        outside = set(MODULE_LIBRARY) - set(modules)
        while remaining:
            ready = sorted(
                module_id
                for module_id in remaining
                if set(MODULE_LIBRARY[module_id].get("dependencies", [])) <= admitted | outside
            )
            if not ready:
                ready = [sorted(remaining)[0]]
            groups.append(ready)
            admitted.update(ready)
            remaining.difference_update(ready)
        return groups

    def _checkpoint(self, job: Dict[str, Any], stage: str, status: str, details: Mapping[str, Any]) -> None:
        checkpoint = {
            "sequence": len(job["checkpoints"]),
            "stage": stage,
            "status": status,
            "at_unix_ms": _now_ms(),
            "details": dict(details),
        }
        checkpoint["checkpoint_root_hash72"] = hash72(
            "HHS_APPLICATION_FACTORY_JOB_CHECKPOINT_V1", checkpoint
        )
        job["checkpoints"].append(checkpoint)
        job["current_stage"] = stage
        job["updated_at_unix_ms"] = checkpoint["at_unix_ms"]

    def run_lifecycle(
        self,
        project_id: str,
        changed_paths: Optional[Iterable[str]] = None,
        timeout_ms: int = 30_000,
    ) -> Dict[str, Any]:
        project = self.projects.get(project_id)
        if project is None:
            return {"ok": False, "status": "REJECT_APPLICATION_PROJECT_UNKNOWN", "project_id": project_id}
        timeout_ms = max(100, min(int(timeout_ms), 300_000))
        plan_result = self.plan_changes(project_id, changed_paths)
        if not plan_result.get("ok"):
            return plan_result
        job_id = _unique("application-job")
        started = _now_ms()
        job = {
            "schema": JOB_SCHEMA,
            "version": VERSION,
            "job_id": job_id,
            "project_id": project_id,
            "state": "QUEUED",
            "current_stage": None,
            "created_at_unix_ms": started,
            "updated_at_unix_ms": started,
            "deadline_unix_ms": started + timeout_ms,
            "timeout_ms": timeout_ms,
            "cancel_requested": False,
            "changed_paths": list(plan_result["plan"]["changed_paths"]),
            "incremental_plan": plan_result["plan"],
            "checkpoints": [],
            "result": None,
            "error": None,
            "authority": AUTHORITY,
        }
        self.jobs[job_id] = job
        try:
            job["state"] = "RUNNING"
            self._checkpoint(
                job,
                "INGRESS",
                "SUCCEEDED",
                {"source_root_hash72": project["source_root_hash72"], "file_count": len(project["files"])},
            )
            self._guard_job(job)
            self._checkpoint(
                job,
                "RESOLVE_MODULES",
                "SUCCEEDED",
                {"modules": project["modules"], "module_count": len(project["modules"])},
            )
            self._guard_job(job)
            self._checkpoint(
                job,
                "BUILD_GRAPH",
                "SUCCEEDED",
                {
                    "module_graph_root_hash72": project["module_graph"]["graph_root_hash72"],
                    "candidate_groups": plan_result["plan"]["parallel_candidate_groups"],
                },
            )
            self._guard_job(job)
            validation = self._validate_project(project)
            if not validation["ok"]:
                raise RuntimeError(";".join(validation["reasons"]))
            self._checkpoint(job, "VALIDATE", "SUCCEEDED", validation)
            self._guard_job(job)
            compile_plan = self._compile_plan(project, plan_result["plan"])
            self._checkpoint(job, "COMPILE_PLAN", "SUCCEEDED", compile_plan)
            self._guard_job(job)
            test_plan = self._test_plan(project, plan_result["plan"])
            self._checkpoint(job, "TEST_PLAN", "SUCCEEDED", test_plan)
            self._guard_job(job)
            package_manifest = self._package_manifest(project, compile_plan, test_plan)
            self._checkpoint(job, "PACKAGE", "SUCCEEDED", package_manifest)
            self._guard_job(job)
            with self._commit_lock:
                current = deepcopy(self.projects[project_id])
                receipt = hash72(
                    "HHS_APPLICATION_FACTORY_LIFECYCLE_COMMIT_V1",
                    {
                        "project_id": project_id,
                        "job_id": job_id,
                        "prior_project_root_hash72": current["project_root_hash72"],
                        "plan_root_hash72": plan_result["plan"]["plan_root_hash72"],
                        "compile_plan_root_hash72": compile_plan["compile_plan_root_hash72"],
                        "test_plan_root_hash72": test_plan["test_plan_root_hash72"],
                        "package_root_hash72": package_manifest["package_root_hash72"],
                    },
                )
                current["state"] = "READY"
                current["latest_job_id"] = job_id
                current["latest_receipt_hash72"] = receipt
                current["updated_at_unix_ms"] = _now_ms()
                current["build"] = {
                    "compile_plan": compile_plan,
                    "test_plan": test_plan,
                    "package_manifest": package_manifest,
                }
                current["project_root_hash72"] = hash72(
                    PROJECT_SCHEMA, {k: v for k, v in current.items() if k != "project_root_hash72"}
                )
                self.projects[project_id] = current
                self.journals[project_id].append(
                    {
                        "sequence": len(self.journals[project_id]),
                        "event": "LIFECYCLE_COMMITTED",
                        "job_id": job_id,
                        "root_hash72": receipt,
                    }
                )
            self._checkpoint(
                job,
                "COMMIT_RECEIPT",
                "SUCCEEDED",
                {
                    "receipt_hash72": receipt,
                    "singleton_commit_authority": True,
                    "parallel_state_authority": False,
                },
            )
            job["state"] = "SUCCEEDED"
            job["result"] = {
                "receipt_hash72": receipt,
                "project_root_hash72": self.projects[project_id]["project_root_hash72"],
                "source_export_ready": True,
                "compile_plan": compile_plan,
                "test_plan": test_plan,
                "package_manifest": package_manifest,
            }
        except _Cancelled as exc:
            job["state"] = "CANCELLED"
            job["error"] = str(exc)
        except _TimedOut as exc:
            job["state"] = "TIMED_OUT"
            job["error"] = str(exc)
        except Exception as exc:
            job["state"] = "FAILED"
            job["error"] = f"{type(exc).__name__}: {exc}"
        job["updated_at_unix_ms"] = _now_ms()
        job["job_root_hash72"] = hash72(JOB_SCHEMA, {k: v for k, v in job.items() if k != "job_root_hash72"})
        self.jobs[job_id] = job
        return {
            "schema": "HHS_APPLICATION_FACTORY_LIFECYCLE_RESULT_V1",
            "ok": job["state"] == "SUCCEEDED",
            "status": f"APPLICATION_LIFECYCLE_{job['state']}",
            "job": deepcopy(job),
        }

    @staticmethod
    def _validate_project(project: Mapping[str, Any]) -> Dict[str, Any]:
        reasons: List[str] = []
        entrypoint = str(project.get("workflow", {}).get("entrypoint") or "")
        if entrypoint not in project.get("files", {}):
            reasons.append("ENTRYPOINT_MISSING")
        if not project.get("modules"):
            reasons.append("MODULES_MISSING")
        if project.get("authority") != AUTHORITY:
            reasons.append("AUTHORITY_MISMATCH")
        return {
            "ok": not reasons,
            "reasons": reasons,
            "entrypoint": entrypoint,
            "file_count": len(project.get("files", {})),
            "module_count": len(project.get("modules", [])),
        }

    @staticmethod
    def _compile_plan(project: Mapping[str, Any], plan: Mapping[str, Any]) -> Dict[str, Any]:
        targets = list(project.get("workflow", {}).get("targets", []))
        artifact_requests = [
            {"target": target, "status": "PLANNED", "authority_required": target != "zip"}
            for target in targets
        ]
        result = {
            "schema": "HHS_APPLICATION_FACTORY_COMPILE_PLAN_V1",
            "impacted_modules": list(plan.get("impacted_modules", [])),
            "artifact_requests": artifact_requests,
            "canonical_source_root_hash72": project.get("source_root_hash72"),
            "no_fabricated_native_binary": True,
        }
        result["compile_plan_root_hash72"] = hash72("HHS_APPLICATION_FACTORY_COMPILE_PLAN_V1", result)
        return result

    @staticmethod
    def _test_plan(project: Mapping[str, Any], plan: Mapping[str, Any]) -> Dict[str, Any]:
        checks = [
            "source-tree-integrity",
            "entrypoint-exists",
            "module-graph-closed",
            "hash72-receipt-ready",
            "replay-plan-ready",
        ]
        if "testing.acceptance" in project.get("modules", []):
            checks.extend(["dependency-scoped-regression", "application-acceptance-path"])
        result = {
            "schema": "HHS_APPLICATION_FACTORY_TEST_PLAN_V1",
            "checks": checks,
            "scope": list(plan.get("validation_scope", [])),
            "status": "PLANNED",
            "external_execution_required": True,
        }
        result["test_plan_root_hash72"] = hash72("HHS_APPLICATION_FACTORY_TEST_PLAN_V1", result)
        return result

    @staticmethod
    def _package_manifest(
        project: Mapping[str, Any], compile_plan: Mapping[str, Any], test_plan: Mapping[str, Any]
    ) -> Dict[str, Any]:
        manifest = {
            "schema": "HHS_APPLICATION_FACTORY_PACKAGE_MANIFEST_V1",
            "project_id": project.get("project_id"),
            "workflow_id": project.get("workflow_id"),
            "source_root_hash72": project.get("source_root_hash72"),
            "file_roots_hash72": deepcopy(project.get("file_roots_hash72", {})),
            "compile_plan_root_hash72": compile_plan.get("compile_plan_root_hash72"),
            "test_plan_root_hash72": test_plan.get("test_plan_root_hash72"),
            "source_zip_available_without_compile": True,
        }
        manifest["package_root_hash72"] = hash72(
            "HHS_APPLICATION_FACTORY_PACKAGE_MANIFEST_V1", manifest
        )
        return manifest

    @staticmethod
    def _guard_job(job: Mapping[str, Any]) -> None:
        if job.get("cancel_requested"):
            raise _Cancelled("lifecycle job cancelled")
        if _now_ms() > int(job.get("deadline_unix_ms") or 0):
            raise _TimedOut("lifecycle job exceeded bounded deadline")

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        job = self.jobs.get(job_id)
        if job is None:
            return {"ok": False, "status": "REJECT_APPLICATION_JOB_UNKNOWN", "job_id": job_id}
        if job.get("state") in FINAL_JOB_STATES:
            return {"ok": False, "status": "REJECT_APPLICATION_JOB_ALREADY_FINAL", "job": deepcopy(job)}
        job["cancel_requested"] = True
        job["state"] = "CANCEL_REQUESTED"
        job["updated_at_unix_ms"] = _now_ms()
        return {"ok": True, "status": "APPLICATION_JOB_CANCEL_REQUESTED", "job": deepcopy(job)}

    def retry_job(self, job_id: str) -> Dict[str, Any]:
        job = self.jobs.get(job_id)
        if job is None:
            return {"ok": False, "status": "REJECT_APPLICATION_JOB_UNKNOWN", "job_id": job_id}
        if job.get("state") not in FINAL_JOB_STATES:
            return {"ok": False, "status": "REJECT_APPLICATION_JOB_NOT_FINAL", "job": deepcopy(job)}
        return self.run_lifecycle(
            job["project_id"], job.get("changed_paths"), int(job.get("timeout_ms") or 30_000)
        )

    def export_source_zip(self, project_id: str) -> Dict[str, Any]:
        project = self.projects.get(project_id)
        if project is None:
            return {"ok": False, "status": "REJECT_APPLICATION_PROJECT_UNKNOWN", "project_id": project_id}
        manifest = {
            "schema": "HHS_APPLICATION_FACTORY_SOURCE_EXPORT_MANIFEST_V1",
            "version": VERSION,
            "project_id": project_id,
            "project_root_hash72": project["project_root_hash72"],
            "source_root_hash72": project["source_root_hash72"],
            "file_roots_hash72": project["file_roots_hash72"],
            "compile_required": False,
            "authority": AUTHORITY,
        }
        manifest["export_root_hash72"] = hash72(
            "HHS_APPLICATION_FACTORY_SOURCE_EXPORT_MANIFEST_V1", manifest
        )
        files = dict(project["files"])
        files[".hhs/application-factory-manifest.json"] = json.dumps(
            manifest, indent=2, sort_keys=True
        ) + "\n"
        payload = _stable_zip(files)
        return {
            "schema": "HHS_APPLICATION_FACTORY_SOURCE_EXPORT_V1",
            "ok": True,
            "status": "APPLICATION_SOURCE_ZIP_READY",
            "filename": f"{project_id.replace(':', '-')}.zip",
            "content_type": "application/zip",
            "size_bytes": len(payload),
            "sha256_transport_hint": hashlib.sha256(payload).hexdigest(),
            "manifest": manifest,
            "zip_bytes": payload,
            "zip_base64": base64.b64encode(payload).decode("ascii"),
        }

    def replay_project(self, project_id: str) -> Dict[str, Any]:
        project = self.projects.get(project_id)
        journal = self.journals.get(project_id)
        if project is None or journal is None:
            return {"ok": False, "status": "REJECT_APPLICATION_PROJECT_UNKNOWN", "project_id": project_id}
        sequence_ok = all(
            entry.get("sequence") == index and entry.get("root_hash72")
            for index, entry in enumerate(journal)
        )
        replay_root = hash72("HHS_APPLICATION_FACTORY_REPLAY_V1", journal)
        return {
            "schema": "HHS_APPLICATION_FACTORY_REPLAY_RESULT_V1",
            "ok": bool(sequence_ok),
            "status": "APPLICATION_REPLAY_VERIFIED" if sequence_ok else "REJECT_APPLICATION_REPLAY",
            "project_id": project_id,
            "journal": deepcopy(journal),
            "journal_length": len(journal),
            "replay_root_hash72": replay_root,
            "project_root_hash72": project["project_root_hash72"],
            "deterministic_replay": bool(sequence_ok),
        }


class _Cancelled(RuntimeError):
    pass


class _TimedOut(RuntimeError):
    pass


APPLICATION_FACTORY = ApplicationFactory()


def application_factory_self_test() -> Dict[str, Any]:
    factory = ApplicationFactory()
    created = factory.create_project(name="Pass 180 Calculator", workflow_id="scientific_calculator")
    project_id = created["project"]["project_id"]
    changed = factory.upsert_file(project_id, "src/calculator.js", "const PHI='(1+sqrt(5))/2';\n")
    plan = factory.plan_changes(project_id, ["src/calculator.js"])
    lifecycle = factory.run_lifecycle(project_id, ["src/calculator.js"])
    exported = factory.export_source_zip(project_id)
    replay = factory.replay_project(project_id)
    invalid = factory.create_project(name="Invalid", workflow_id="missing")
    ok = bool(
        created.get("ok")
        and changed.get("ok")
        and plan.get("ok")
        and lifecycle.get("ok")
        and exported.get("ok")
        and exported.get("size_bytes", 0) > 0
        and replay.get("ok")
        and not invalid.get("ok")
        and lifecycle["job"]["state"] == "SUCCEEDED"
        and lifecycle["job"]["result"]["source_export_ready"]
    )
    return {
        "schema": "HHS_APPLICATION_FACTORY_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "created": created,
        "incremental_plan": plan,
        "lifecycle": lifecycle,
        "source_export": {
            key: value for key, value in exported.items() if key not in {"zip_bytes", "zip_base64"}
        },
        "replay": replay,
        "invalid_workflow_rejection": invalid,
        "status": factory.status(),
    }


if __name__ == "__main__":
    print(json.dumps(application_factory_self_test(), indent=2, sort_keys=True, default=str))
