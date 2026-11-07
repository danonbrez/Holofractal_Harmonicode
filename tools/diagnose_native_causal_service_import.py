#!/usr/bin/env python3
"""Fail-closed causal-model dependency import probe under the actual service UID.

Provides bounded interpreter / import-resolution facts for diagnosis. Does not
load model weights, alter the environment, or grant inference/runtime authority.
"""
from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import os
import sys
import traceback


def probe() -> dict:
    result = {
        "schema": "HHS_NATIVE_CAUSAL_SERVICE_IMPORT_PROBE_V1",
        "uid": os.geteuid(),
        "interpreter": sys.executable,
        "python_prefix": sys.prefix,
        "pythonpath_explicit": bool(os.environ.get("PYTHONPATH")),
        "distributions": {},
        "module_specs": {},
        "ok": False,
    }
    for package in ("transformers", "torch", "tokenizers", "huggingface-hub"):
        try:
            result["distributions"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result["distributions"][package] = None
    for module in ("transformers", "torch", "tokenizers"):
        try:
            spec = importlib.util.find_spec(module)
            result["module_specs"][module] = {
                "found": spec is not None,
                "origin": str(spec.origin) if spec else None,
            }
        except Exception as exc:
            result["module_specs"][module] = {"found": False, "error": repr(exc)}
    try:
        from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM
        import torch
        result["ok"] = all((AutoConfig, AutoTokenizer, AutoModelForCausalLM, torch))
        result["ok"] = bool(result["ok"])
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)[:1500]
        result["traceback_tail"] = traceback.format_exc(limit=8)[-5000:]
    return result


if __name__ == "__main__":
    outcome = probe()
    print(json.dumps(outcome, sort_keys=True))
    raise SystemExit(0 if outcome["ok"] else 1)
