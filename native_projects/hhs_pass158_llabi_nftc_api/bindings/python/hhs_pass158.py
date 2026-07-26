from __future__ import annotations

import hhs_pass158_core as _core

for _name in dir(_core):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_core, _name)

HHS158_FLAG_PROJECTION = 1 << 1
HHS158_FLAG_APPROXIMATE = 1 << 4

__all__ = list(getattr(_core, "__all__", ())) + [
    "HHS158_FLAG_PROJECTION",
    "HHS158_FLAG_APPROXIMATE",
]
