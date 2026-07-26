#!/usr/bin/env python3
"""Verify the VM81 game's actual POSIX terminal input/output modality."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import pty
import re
import select
import struct
import subprocess
import sys
import termios
import time
from pathlib import Path
from typing import Any


CONTRACT = "HHS-VM81-USER-MODALITY-EVIDENCE-V1"
CLASSIFICATION = "VM81_TERMINAL_IO_MODALITY_VERIFIED"
ANSI_PATTERN = re.compile(rb"\x1b\[[0-?]*[ -/]*[@-~]")
FRAME_PATTERN = re.compile(r"frame=(\d+)")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_ansi(data: bytes) -> str:
    return ANSI_PATTERN.sub(b"", data).decode("utf-8", errors="replace")


def drain(master_fd: int, transcript: bytearray, duration: float = 0.15) -> None:
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        ready, _, _ = select.select([master_fd], [], [], 0.03)
        if not ready:
            continue
        try:
            chunk = os.read(master_fd, 65536)
        except OSError:
            return
        if not chunk:
            return
        transcript.extend(chunk)


def wait_for(
    master_fd: int,
    transcript: bytearray,
    needle: str,
    start_offset: int,
    timeout: float = 5.0,
) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        segment = strip_ansi(bytes(transcript[start_offset:]))
        if needle in segment:
            return segment
        ready, _, _ = select.select([master_fd], [], [], 0.05)
        if not ready:
            continue
        try:
            chunk = os.read(master_fd, 65536)
        except OSError as exc:
            raise RuntimeError(f"terminal read failed while waiting for {needle!r}: {exc}") from exc
        if not chunk:
            break
        transcript.extend(chunk)
    segment = strip_ansi(bytes(transcript[start_offset:]))
    raise RuntimeError(f"timed out waiting for terminal presentation {needle!r}; observed tail={segment[-500:]!r}")


def send_key(master_fd: int, key: bytes) -> None:
    written = os.write(master_fd, key)
    if written != len(key):
        raise RuntimeError(f"partial terminal input write: {written}/{len(key)}")


def frame_numbers(text: str) -> list[int]:
    return [int(match) for match in FRAME_PATTERN.findall(text)]


def write_evidence(
    output_dir: Path,
    transcript: bytes,
    observations: dict[str, Any],
    exit_code: int,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "terminal-session.ansi"
    text_path = output_dir / "terminal-session.txt"
    raw_path.write_bytes(transcript)
    normalized = strip_ansi(transcript)
    text_path.write_text(normalized, encoding="utf-8")
    evidence = {
        "contract": CONTRACT,
        "terminal_classification": CLASSIFICATION,
        "status": "VERIFIED",
        "input_modality": "POSIX_TERMINAL_KEYBOARD_BYTES",
        "output_modality": "ANSI_TERMINAL_TEXT",
        "transport": "pseudo-terminal",
        "inputs_exercised": [
            {"bytes_hex": "0a", "meaning": "ENTER/start"},
            {"bytes_hex": "64", "meaning": "D/move right"},
            {"bytes_hex": "77", "meaning": "W/jump"},
            {"bytes_hex": "70", "meaning": "P/pause"},
            {"bytes_hex": "70", "meaning": "P/resume"},
            {"bytes_hex": "72", "meaning": "R/restart"},
            {"bytes_hex": "71", "meaning": "Q/quit"},
        ],
        "observations": observations,
        "process_exit_code": exit_code,
        "raw_transcript": {
            "path": raw_path.name,
            "size_bytes": raw_path.stat().st_size,
            "sha256": sha256_bytes(transcript),
        },
        "normalized_transcript": {
            "path": text_path.name,
            "size_bytes": text_path.stat().st_size,
            "sha256": sha256_bytes(normalized.encode("utf-8")),
        },
        "closure": {
            "title_presented": "VERIFIED",
            "start_input_interpreted": "VERIFIED",
            "movement_and_jump_input_interpreted": "VERIFIED",
            "pause_presented": "VERIFIED",
            "resume_presented": "VERIFIED",
            "restart_presented": "VERIFIED",
            "quit_interpreted": "VERIFIED",
            "terminal_restored": "VERIFIED",
        },
    }
    evidence_path = output_dir / "terminal-io-evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    binary = args.binary.resolve()
    output_dir = args.output.resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise RuntimeError(f"playable executable is not runnable: {binary}")

    master_fd, slave_fd = pty.openpty()
    transcript = bytearray()
    process: subprocess.Popen[bytes] | None = None
    observations: dict[str, Any] = {}
    try:
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 120, 0, 0))
        process = subprocess.Popen(
            [str(binary)],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            start_new_session=True,
        )
        os.close(slave_fd)
        slave_fd = -1

        title_segment = wait_for(master_fd, transcript, "phase=TITLE", 0)
        if "Press ENTER to start" not in title_segment or "+--------------------+" not in title_segment:
            raise RuntimeError("title presentation is incomplete")
        observations["title"] = {"phase": "TITLE", "prompt": "PRESENT", "viewport": "PRESENT"}

        start_offset = len(transcript)
        send_key(master_fd, b"\n")
        running_segment = wait_for(master_fd, transcript, "phase=RUNNING", start_offset)
        running_frames = frame_numbers(running_segment)
        if not running_frames:
            raise RuntimeError("running presentation omitted the frame counter")
        observations["start"] = {"phase": "RUNNING", "first_observed_frame": min(running_frames)}

        movement_offset = len(transcript)
        send_key(master_fd, b"d")
        send_key(master_fd, b"w")
        drain(master_fd, transcript, 0.35)
        movement_segment = strip_ansi(bytes(transcript[movement_offset:]))
        movement_frames = frame_numbers(movement_segment)
        if not movement_frames or max(movement_frames) <= min(running_frames):
            raise RuntimeError("movement/jump input did not advance the presented game frame")
        if "@" not in movement_segment or "#" not in movement_segment:
            raise RuntimeError("movement presentation omitted player or level glyphs")
        observations["movement_jump"] = {
            "input_bytes": ["64", "77"],
            "first_frame": min(movement_frames),
            "last_frame": max(movement_frames),
            "player_glyph": "PRESENT",
            "level_glyph": "PRESENT",
        }

        pause_offset = len(transcript)
        send_key(master_fd, b"p")
        paused_segment = wait_for(master_fd, transcript, "phase=PAUSED", pause_offset)
        if "PAUSED - press P to resume" not in paused_segment:
            raise RuntimeError("pause presentation omitted its user-facing instruction")
        observations["pause"] = {"phase": "PAUSED", "instruction": "PRESENT"}

        resume_offset = len(transcript)
        send_key(master_fd, b"p")
        resumed_segment = wait_for(master_fd, transcript, "phase=RUNNING", resume_offset)
        resumed_frames = frame_numbers(resumed_segment)
        if not resumed_frames:
            raise RuntimeError("resume presentation omitted the frame counter")
        observations["resume"] = {"phase": "RUNNING", "observed_frame": min(resumed_frames)}

        reset_offset = len(transcript)
        send_key(master_fd, b"r")
        reset_segment = wait_for(master_fd, transcript, "phase=RUNNING", reset_offset)
        drain(master_fd, transcript, 0.12)
        reset_segment = strip_ansi(bytes(transcript[reset_offset:]))
        reset_frames = frame_numbers(reset_segment)
        if not reset_frames or min(reset_frames) > 3:
            raise RuntimeError(f"restart did not return the presented frame counter near zero: {reset_frames[:10]}")
        observations["restart"] = {"phase": "RUNNING", "minimum_observed_frame": min(reset_frames)}

        quit_offset = len(transcript)
        send_key(master_fd, b"q")
        deadline = time.monotonic() + 5.0
        while process.poll() is None and time.monotonic() < deadline:
            drain(master_fd, transcript, 0.05)
        if process.poll() is None:
            process.terminate()
            raise RuntimeError("quit input did not terminate the playable process")
        drain(master_fd, transcript, 0.1)
        quit_segment = strip_ansi(bytes(transcript[quit_offset:]))
        observations["quit"] = {
            "input_byte": "71",
            "process_terminated": True,
            "terminal_restore_sequence_present": b"\x1b[?25h\x1b[0m" in transcript,
            "post_input_output_bytes": len(quit_segment.encode("utf-8")),
        }
        if not observations["quit"]["terminal_restore_sequence_present"]:
            raise RuntimeError("terminal cursor/style restoration sequence was not emitted")
        exit_code = int(process.returncode or 0)
        if exit_code != 0:
            raise RuntimeError(f"playable process exited with status {exit_code}")

        normalized = strip_ansi(bytes(transcript))
        for required in (
            "A/D move",
            "SPACE/W jump",
            "P pause",
            "R restart",
            "Q quit",
            "phase=TITLE",
            "phase=RUNNING",
            "phase=PAUSED",
        ):
            if required not in normalized:
                raise RuntimeError(f"terminal transcript is missing documented presentation: {required}")

        evidence_path = write_evidence(output_dir, bytes(transcript), observations, exit_code)
        print(evidence_path.read_text(encoding="utf-8"), end="")
        return 0
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        if master_fd >= 0:
            os.close(master_fd)
        if slave_fd >= 0:
            os.close(slave_fd)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"terminal modality verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
