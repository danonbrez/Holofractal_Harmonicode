#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.server
import os
from pathlib import Path
import socketserver


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the HHS VM81 spatial environment.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    os.chdir(root)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.ThreadingTCPServer((args.host, args.port), handler) as server:
        print(f"HHS VM81 spatial environment: http://{args.host}:{args.port}")
        server.serve_forever()


if __name__ == "__main__":
    main()
