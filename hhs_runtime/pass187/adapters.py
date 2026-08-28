"""Executable Ubuntu/Linux integration adapters for Pass 187.

Adapter outputs are typed external evidence. They do not mutate the composition
graph until explicitly imported under an inherited VM81 Hash72 receipt.
"""
from __future__ import annotations

import hashlib
import http.client
import os
import socket
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from .composition import hash72


def _evidence(kind: str, payload: bytes, metadata: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "kind": kind,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "payload_size": len(payload),
        "metadata": dict(metadata),
        "evidence_hash72": hash72(
            "HHS-P187-ADAPTER-EVIDENCE",
            {
                "kind": kind,
                "payload_sha256": hashlib.sha256(payload).hexdigest(),
                "payload_size": len(payload),
                "metadata": dict(metadata),
            },
        ),
        "canonical_mutation_authority": False,
    }


def read_file(path: str | os.PathLike[str]) -> dict[str, Any]:
    source = Path(path)
    payload = source.read_bytes()
    return _evidence("file", payload, {"path": str(source), "exists": True})


def run_process(command: Sequence[str], stdin: bytes = b"") -> dict[str, Any]:
    completed = subprocess.run(
        list(command),
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    joined = completed.stdout + b"\0STDERR\0" + completed.stderr
    result = _evidence(
        "process",
        joined,
        {"command": list(command), "returncode": completed.returncode},
    )
    result["stdout"] = completed.stdout.decode("utf-8", errors="replace")
    result["stderr"] = completed.stderr.decode("utf-8", errors="replace")
    return result


def unix_socket_roundtrip(path: str, payload: bytes, timeout: float = 2.0) -> dict[str, Any]:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect(path)
        client.sendall(payload)
        client.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            chunk = client.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        client.close()
    response = b"".join(chunks)
    result = _evidence("unix_socket", response, {"path": path, "request_sha256": hashlib.sha256(payload).hexdigest()})
    result["response"] = response.decode("utf-8", errors="replace")
    return result


def http_get(host: str, port: int, path: str, timeout: float = 3.0) -> dict[str, Any]:
    connection = http.client.HTTPConnection(host, int(port), timeout=timeout)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        payload = response.read()
        status = response.status
    finally:
        connection.close()
    result = _evidence("http", payload, {"host": host, "port": int(port), "path": path, "status": status})
    result["body"] = payload.decode("utf-8", errors="replace")
    return result
