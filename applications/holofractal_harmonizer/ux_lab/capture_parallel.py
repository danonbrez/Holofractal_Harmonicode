from __future__ import annotations

import concurrent.futures
import hashlib
import json
import shutil
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
CAPTURE = ROOT / "static"
EVIDENCE = ROOT / "evidence"
FRAMES = EVIDENCE / "frames"
SHOTS = EVIDENCE / "screenshots"
VIDEOS = EVIDENCE / "videos"
ARTIFACTS = ROOT / "artifacts" / "capture"
for p in (FRAMES, SHOTS, VIDEOS, ARTIFACTS):
    p.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
import server  # noqa: E402

WORKFLOW_IDS = ["code_api", "data_dashboard", "document_knowledge", "image_spatial"]


def execute(workflow_id: str, variant: str) -> dict[str, Any]:
    session_id = f"{workflow_id}-{variant.lower()}"
    out = ARTIFACTS / variant / workflow_id / session_id
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    logs = server.RUNNERS[workflow_id](out)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    files = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        files.append({"name": path.name, "path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": server._sha(path)})
    receipt_input = json.dumps({"workflow": workflow_id, "variant": variant, "session": session_id, "files": files}, sort_keys=True).encode()
    receipt = hashlib.sha256(receipt_input).hexdigest()
    result = {
        "ok": True,
        "workflow_id": workflow_id,
        "variant": variant,
        "elapsed_ms": elapsed_ms,
        "logs": logs,
        "files": files,
        "receipt_sha256": receipt,
        "runtime_claim": "LOCAL_EXECUTABLE_WORKFLOW_VALIDATED",
        "authority_note": "Usability lab artifact success is not a canonical VM81 mutation receipt.",
    }
    server._write_json(out / "result.json", result)
    return result


def page_html(variant: str, workflow_id: str, session_id: str) -> str:
    css = (CAPTURE / "styles.css").read_text(encoding="utf-8")
    js = (CAPTURE / "app.js").read_text(encoding="utf-8")
    js = js.replace("fetch(`/api/run/${workflowId}`", "fetch(`http://hhs.local/api/run/${workflowId}`")
    js = js.replace("fetch('/api/workflows')", "fetch('http://hhs.local/api/workflows')")
    js = js.replace(
        "const params = new URLSearchParams(location.search);",
        f"const params = new URLSearchParams('?variant={variant}&workflow={workflow_id}&session={session_id}');",
        1,
    )
    return f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HHS Visual IDE A/B Lab</title><style>{css}</style></head><body><div id='app' aria-live='polite'></div><script type='module'>{js}</script></body></html>"


def run_variant(workflow_id: str, variant: str, precomputed: dict[str, Any]) -> dict[str, Any]:
    session_id = f"{workflow_id}-{variant.lower()}"
    frame_dir = FRAMES / workflow_id / variant
    if frame_dir.exists():
        shutil.rmtree(frame_dir)
    frame_dir.mkdir(parents=True)
    frame_index = 0

    def snap(page, name: str, delay_ms: int = 280) -> None:
        nonlocal frame_index
        page.wait_for_timeout(delay_ms)
        page.screenshot(path=str(frame_dir / f"{frame_index:03d}-{name}.png"), full_page=False)
        frame_index += 1

    with sync_playwright() as p:
        configured = os.getenv("HHS_UX_CHROMIUM")
        executable = configured or next((shutil.which(name) for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable") if shutil.which(name)), None)
        launch_options = {"headless": True, "args": ["--no-sandbox", "--disable-gpu"]}
        if executable:
            launch_options["executable_path"] = executable
        browser = p.chromium.launch(**launch_options)
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)

        def handler(route):
            url = route.request.url
            if url.endswith("/api/workflows"):
                route.fulfill(status=200, content_type="application/json", body=json.dumps({"workflows": server.WORKFLOWS, "templates": server.TEMPLATES}))
                return
            if "/api/run/" in url:
                route.fulfill(status=200, content_type="application/json", body=json.dumps(precomputed))
                return
            route.continue_()

        page.route("http://hhs.local/**", handler)
        page.set_content(page_html(variant, workflow_id, session_id), wait_until="domcontentloaded")
        page.wait_for_selector("#metric-badge")
        snap(page, "start", 450)

        if variant == "A":
            sequence = [
                ("#a-object-workspace", "open-objects", 320),
                ("#a-select-task", "select-workflow", 280),
                ("#a-assistant-home", "return-assistant", 320),
                ("#a-quick-prompt", "choose-prompt", 260),
                ("#a-send", "submit-prompt", 340),
                ("#a-open-api", "open-api", 360),
                ("#a-api-invoke", "run-workflow", 500),
            ]
            for selector, label, delay in sequence:
                page.click(selector)
                if selector == "#a-api-invoke":
                    page.wait_for_selector("#a-complete", timeout=30000)
                snap(page, label, delay)
            page.click("#a-complete")
            snap(page, "complete", 600)
        else:
            page.click("button.template.active")
            snap(page, "select-template", 300)
            page.click("#b-start")
            snap(page, "start-workflow", 380)
            page.click("#b-run-all")
            page.wait_for_selector("#b-review", timeout=30000)
            snap(page, "run-workflow", 520)
            page.click("#b-review")
            snap(page, "complete", 600)

        page.wait_for_function("document.body.dataset.completed === 'true'", timeout=30000)
        metrics = page.evaluate("window.__HHS_UX_METRICS__")
        page.screenshot(path=str(SHOTS / f"{workflow_id}-{variant}-success.png"), full_page=False)
        browser.close()
    return {"metrics": metrics, "frame_count": frame_index, "frame_dir": str(frame_dir)}


def add_label(image: Image.Image, label: str) -> Image.Image:
    out = Image.new("RGB", (image.width, image.height + 44), (2, 5, 11))
    out.paste(image.convert("RGB"), (0, 44))
    draw = ImageDraw.Draw(out)
    draw.text((16, 15), label, fill=(239, 250, 255))
    return out


def prepare_video_frames(workflow_id: str, variant: str, max_count: int) -> Path:
    label = "VARIANT A — OBJECT-FIRST BASELINE" if variant == "A" else "VARIANT B — WORKFLOW-FIRST CANDIDATE"
    source_dir = FRAMES / workflow_id / variant
    dest_dir = FRAMES / workflow_id / f"{variant}-video"
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)
    files = sorted(source_dir.glob("*.png"))
    for idx in range(max_count):
        src = files[min(idx, len(files) - 1)]
        add_label(Image.open(src), label).save(dest_dir / f"{idx:03d}.png")
    return dest_dir


def render_videos(workflow_id: str, a_dir: Path, b_dir: Path) -> None:
    a_mp4 = VIDEOS / f"{workflow_id}-A.mp4"
    b_mp4 = VIDEOS / f"{workflow_id}-B.mp4"
    ab_mp4 = VIDEOS / f"{workflow_id}-AB.mp4"
    encode = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-y"]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-framerate", "1", "-i", str(a_dir / "%03d.png"), *encode, str(a_mp4)], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-framerate", "1", "-i", str(b_dir / "%03d.png"), *encode, str(b_mp4)], check=True)
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-i", str(a_mp4), "-i", str(b_mp4),
        "-filter_complex", "[0:v][1:v]hstack=inputs=2[v]", "-map", "[v]", "-c:v", "libx264",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-y", str(ab_mp4)
    ], check=True)


def combine_success(workflow_id: str) -> None:
    a = add_label(Image.open(SHOTS / f"{workflow_id}-A-success.png"), "VARIANT A — OBJECT-FIRST BASELINE")
    b = add_label(Image.open(SHOTS / f"{workflow_id}-B-success.png"), "VARIANT B — WORKFLOW-FIRST CANDIDATE")
    canvas = Image.new("RGB", (a.width + b.width, max(a.height, b.height)), (2, 5, 11))
    canvas.paste(a, (0, 0))
    canvas.paste(b, (a.width, 0))
    canvas.save(SHOTS / f"{workflow_id}-AB-success.png", quality=92)


def main() -> None:
    results: dict[str, Any] = {}
    selected = sys.argv[1:] or WORKFLOW_IDS
    for workflow_id in selected:
        precomputed = {variant: execute(workflow_id, variant) for variant in ("A", "B")}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(run_variant, workflow_id, "A", precomputed["A"])
            future_b = executor.submit(run_variant, workflow_id, "B", precomputed["B"])
            a = future_a.result(timeout=120)
            b = future_b.result(timeout=120)
        results[workflow_id] = {"A": a, "B": b}
        max_count = max(a["frame_count"], b["frame_count"])
        a_dir = prepare_video_frames(workflow_id, "A", max_count)
        b_dir = prepare_video_frames(workflow_id, "B", max_count)
        render_videos(workflow_id, a_dir, b_dir)
        combine_success(workflow_id)
        print(workflow_id, a["metrics"], b["metrics"], flush=True)
    (EVIDENCE / "metrics_raw.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
