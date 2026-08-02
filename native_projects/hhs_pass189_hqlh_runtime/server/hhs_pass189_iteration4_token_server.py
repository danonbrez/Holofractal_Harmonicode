#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import hhs_pass189_iteration4_server as base
from hhs_pass189_iteration4_token_lifecycle import DriverProvenanceLifecycleAuthority

DATABASE = Path(os.environ.get("HHS189_I4_DB", "/var/lib/hhs-pass189/iteration4.sqlite3"))
QUARANTINE = Path(os.environ.get("HHS189_I4_QUARANTINE", "/var/lib/hhs-pass189/iteration4-quarantine"))
base.AUTHORITY.close()
base.AUTHORITY = DriverProvenanceLifecycleAuthority(DATABASE, quarantine_directory=QUARANTINE)


class Handler(base.Handler):
    server_version = "HHS189-I4-LIFECYCLE/1.0"

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        if path not in ("/api/pass189/i4/promotion/validate", "/api/pass189/i4/promotion/sweep"):
            super().do_POST()
            return
        try:
            body = self._body()
            if path.endswith("/validate"):
                self._json(base.AUTHORITY.validate_promotion_token(str(body.get("token_hash72", "")), at_ns=body.get("at_ns")))
            else:
                self._json(base.AUTHORITY.sweep_expired_promotions(at_ns=body.get("at_ns")))
        except (ValueError, KeyError, TypeError) as exc:
            self._json({"error": str(exc)}, 400)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("HHS189_I4_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("HHS189_I4_PORT", "8192")))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"HHS Pass 189 Iteration 4 lifecycle listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        base.AUTHORITY.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
