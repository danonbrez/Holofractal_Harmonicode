"""Read-only native causal package resolution report under the actual service interpreter.

Reports module spec locations and distribution metadata without importing model
weights or exposing environment secrets. Exit nonzero when imports are unusable.
"""
from __future__ import annotations
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import sys


def probe():
    out = {"interpreter":sys.executable,"prefix":sys.prefix,
           "base_prefix":sys.base_prefix,"cwd":os.getcwd(),
           "packages":{}, "errors":[]}
    for name in ("transformers","torch","tokenizers"):
        try:
            spec=importlib.util.find_spec(name)
            location=None if spec is None else spec.origin
        except Exception as exc:
            location=None
            out["errors"].append(f"{name} spec: {type(exc).__name__}: {exc}")
        try:
            version=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            version=None
        out["packages"][name]={"version":version,"origin":location}
        if location is None:
            out["errors"].append(f"{name} not resolved")
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        if AutoTokenizer is None or AutoModelForCausalLM is None:
            raise RuntimeError("missing exported model classes")
        out["model_imports_resolved"]=True
    except Exception as exc:
        out["model_imports_resolved"]=False
        out["errors"].append(f"model imports: {type(exc).__name__}: {exc}")
    return out


if __name__=="__main__":
    result=probe()
    print(json.dumps(result,sort_keys=True))
    sys.exit(0 if result["model_imports_resolved"] else 27)
