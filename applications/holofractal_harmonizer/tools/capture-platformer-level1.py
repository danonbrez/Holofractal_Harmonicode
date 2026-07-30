#!/usr/bin/env python3
"""Capture the deterministic Level 1 browser playthrough and encode H.264 MP4.

Prerequisites: Python Playwright, a Chromium executable, ffmpeg, and ffprobe.
Run the materializer first, then point --project at that directory.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--project', default='dist/platformer-level1')
parser.add_argument('--output', default='dist/platformer-level1-playthrough.mp4')
parser.add_argument('--chromium', default='/usr/bin/chromium')
args = parser.parse_args()
project = Path(args.project).resolve()
output = Path(args.output).resolve()
output.parent.mkdir(parents=True, exist_ok=True)
record_dir = output.parent / 'platformer-level1-recording'
record_dir.mkdir(exist_ok=True)
html = (project / 'index.html').read_text().replace(
    '<link rel="stylesheet" href="./style.css">',
    '<style>' + (project / 'style.css').read_text() + '</style>',
)
js = (project / 'app.js').read_text().replace(
    "const AUTOPLAY = new URLSearchParams(location.search).has('autoplay');",
    'const AUTOPLAY = true;',
)
html = html.replace('<script src="./app.js"></script>', '<script>' + js + '</script>')
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True,
        executable_path=args.chromium,
        args=['--no-sandbox', '--disable-dev-shm-usage'],
    )
    context = browser.new_context(
        viewport={'width': 1100, 'height': 700},
        record_video_dir=str(record_dir),
        record_video_size={'width': 1100, 'height': 700},
    )
    page = context.new_page()
    errors: list[str] = []
    page.on('console', lambda msg: errors.append(f'console:{msg.type}:{msg.text}') if msg.type == 'error' else None)
    page.on('pageerror', lambda err: errors.append(f'pageerror:{err}'))
    page.set_content(html, wait_until='load')
    page.wait_for_function('window.__HHS_LEVEL1_COMPLETE__ !== undefined', timeout=30000)
    final = page.evaluate('window.__HHS_LEVEL1_COMPLETE__')
    page.wait_for_timeout(1800)
    video = page.video
    page.close()
    context.close()
    browser.close()
    webm = Path(video.path())
subprocess.run(
    [
        'ffmpeg', '-y', '-i', str(webm), '-c:v', 'libx264', '-preset', 'slow',
        '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output),
    ],
    check=True,
)
probe = json.loads(
    subprocess.check_output(
        [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration,size:stream=width,height,r_frame_rate,codec_name',
            '-of', 'json', str(output),
        ],
        text=True,
    )
)
print(json.dumps({
    'classification': 'HHS_PLATFORMER_LEVEL1_PLAYTHROUGH_CAPTURED',
    'final': final,
    'errors': errors,
    'output': str(output),
    'probe': probe,
}, indent=2))
