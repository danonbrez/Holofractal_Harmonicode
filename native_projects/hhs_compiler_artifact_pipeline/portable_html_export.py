"""Fail-closed, single-file browser artifact packager for the HHS IDE.

This is an export boundary, not an alternative VM81 implementation. A portable
runtime must be supplied from the canonical native/compiler build as JavaScript
or inline-compatible WASM bootstrap, with a verifiable capability declaration.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

REQUIRED = ("vm81_admission", "hash72_receipt", "hash216_replay",
            "lane5_hydration", "ordered_transition")

class ExportContractError(ValueError):
    pass

def package_html(document: str, runtime_js: str, manifest: dict) -> str:
    if not isinstance(manifest, dict):
        raise ExportContractError("runtime manifest must be an object")
    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, dict):
        raise ExportContractError("missing runtime capabilities")
    missing = [name for name in REQUIRED if capabilities.get(name) is not True]
    if missing:
        raise ExportContractError("missing required portable runtime capabilities: " + ", ".join(missing))
    digest = hashlib.sha256(runtime_js.encode("utf-8")).hexdigest()
    if manifest.get("runtime_sha256") != digest:
        raise ExportContractError("embedded runtime SHA-256 mismatch")
    if not manifest.get("canonical_source_commit"):
        raise ExportContractError("missing canonical runtime source commit")
    if not manifest.get("selftest_vector_sha256"):
        raise ExportContractError("missing executable self-test witness identity")
    if "<html" not in document.lower() or "</head>" not in document.lower():
        raise ExportContractError("expected an HTML document with a head")
    if "</script" in runtime_js.lower():
        raise ExportContractError("unescaped script terminator in runtime payload")
    if 'src=' in runtime_js and 'http' in runtime_js:
        raise ExportContractError("potential remote runtime dependency")
    # Explicit runtime API, not an identity-shaped placeholder. Actual admission
    # and receipt behavior is subject to canonical contract test vectors.
    manifest_json = json.dumps(manifest, sort_keys=True, separators=(",", ":")).replace("<", "\\u003c")
    wrapper = (
        '<script id="hhs-portable-runtime-manifest" type="application/json">'
        + manifest_json + '</script>\n'
        + '<script id="hhs-portable-vm81-runtime">\n'
        + runtime_js + '\n'
        + '''(function(){
          const r=globalThis.HHSPortableVM81;
          const required=["admit","receiptHash72","verifyHash216","hydrateLane5","transition","selfTest"];
          if(!r || required.some(k=>typeof r[k]!=="function"))
            throw new Error("HHS_EXPORT_RUNTIME_API_MISSING");
          if(r.selfTest()!==true)
            throw new Error("HHS_EXPORT_RUNTIME_SELFTEST_FAILED");
          Object.defineProperty(globalThis,"HHS_PORTABLE_RUNTIME_READY",
            {value:true,writable:false,configurable:false});
        })();\n</script>\n'''
    )
    return document.replace("</head>", wrapper + "</head>", 1)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--runtime-js", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    output = package_html(args.html.read_text(encoding="utf-8"),
                          args.runtime_js.read_text(encoding="utf-8"),
                          json.loads(args.manifest.read_text(encoding="utf-8")))
    args.out.write_text(output, encoding="utf-8")

if __name__ == "__main__":
    main()
