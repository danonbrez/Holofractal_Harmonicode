from __future__ import annotations

from pathlib import Path
import hashlib
import json

TARGET = Path('hhs_runtime_api_server_v1.py')
SEAL = Path('data/runtime/agent_run_loop_recursive_patch_seal_v1.json')

OLD_DEFAULT = '    max_passes: int = 1\n'
NEW_DEFAULT = '    max_passes: int = 3\n'

START = 'def run_kernel_wired_agent_loop(expression: str, *, auto_continue: bool = True, max_passes: int = 1) -> Dict[str, Any]:\n'
END = '\n\n@app.get("/api/status")\n'

NEW_FUNCTION = '''def _pass_signature(passes: List[Dict[str, Any]]) -> str:\n    return hash72_digest(("agent_loop_pass_signature_v1", [p.get("kind") for p in passes], [p.get("hash72") for p in passes]), width=24)\n\n\ndef _closure_status(evaluation: Dict[str, Any], previous_signature: str | None, current_signature: str) -> Dict[str, Any]:\n    unresolved = _is_unresolved(evaluation)\n    repeated = previous_signature is not None and previous_signature == current_signature\n    closed = not unresolved\n    bounded_stable = unresolved and repeated\n    return {\n        "closed": closed,\n        "unresolved": unresolved,\n        "repeated_signature": repeated,\n        "bounded_stable": bounded_stable,\n        "reason": "CLOSED" if closed else ("BOUNDED_STABLE_SIGNATURE" if bounded_stable else "CONTINUE"),\n    }\n\n\ndef _kernel_pass_set(expression: str, evaluation: Dict[str, Any], cycle: int) -> List[Dict[str, Any]]:\n    items = _evaluation_items(evaluation)\n    influences = _evaluation_influences(evaluation)\n    packet = build_convergence_packet(expression, items, influences).to_dict()\n    patch = plan_transformation_patch(packet)\n    manifest = build_equation_manifest()\n    transpile = build_transpile_receipt(manifest, ["python"])\n    return [\n        {"cycle": cycle, "kind": "convergence-packet", "hash72": packet.get("packet_hash72") or packet.get("convergence_hash72"), "payload": packet},\n        {"cycle": cycle, "kind": "patch-plan", "hash72": patch.get("patch_hash72") or patch.get("plan_hash72"), "payload": patch},\n        {"cycle": cycle, "kind": "equation-manifest", "hash72": manifest.get("manifest_hash72") or manifest.get("summary_hash72"), "payload": manifest},\n        {"cycle": cycle, "kind": "transpile-receipt", "hash72": transpile.get("receipt_hash72") or transpile.get("transpile_hash72"), "payload": transpile},\n    ]\n\n\ndef run_kernel_wired_agent_loop(expression: str, *, auto_continue: bool = True, max_passes: int = 3) -> Dict[str, Any]:\n    limit = max(1, min(int(max_passes or 1), 6))\n    passes: List[Dict[str, Any]] = []\n    signatures: List[str] = []\n    previous_signature: str | None = None\n    closure: Dict[str, Any] = {"closed": False, "unresolved": True, "reason": "INIT"}\n\n    for cycle in range(1, limit + 1):\n        evaluation = _calculator_evaluation_payload(expression)\n        passes.append({"index": len(passes) + 1, "cycle": cycle, "kind": "calculator-evaluate", "hash72": evaluation.get("result_hash72"), "payload": evaluation})\n        cycle_passes = [passes[-1]]\n\n        if auto_continue and _is_unresolved(evaluation):\n            for p in _kernel_pass_set(expression, evaluation, cycle):\n                p["index"] = len(passes) + 1\n                passes.append(p)\n                cycle_passes.append(p)\n\n        signature = _pass_signature(cycle_passes)\n        signatures.append(signature)\n        closure = _closure_status(evaluation, previous_signature, signature)\n        if closure["closed"] or closure["bounded_stable"] or not auto_continue:\n            break\n        previous_signature = signature\n\n    run_hash = hash72_digest(("agent_run_loop_v2", expression, signatures, [p.get("kind") for p in passes], [p.get("hash72") for p in passes], closure), width=24)\n    return {"status": "KERNEL_WIRED_RUN_COMPLETE", "expression": expression, "auto_continue": auto_continue, "max_passes": limit, "cycles": len(signatures), "closure": closure, "unresolved": closure.get("unresolved", True), "passes": passes, "cycle_signatures_hash72": signatures, "run_hash72": run_hash, "receipt_hash72": run_hash}\n'''


def h(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def main() -> int:
    before = TARGET.read_text(encoding='utf-8')
    after = before.replace(OLD_DEFAULT, NEW_DEFAULT, 1)
    start = after.index(START)
    end = after.index(END, start)
    after = after[:start] + NEW_FUNCTION + after[end:]
    changed = before != after
    if changed:
        TARGET.write_text(after, encoding='utf-8')
    seal = {
        'schema': 'HHS_AGENT_RUN_LOOP_RECURSIVE_PATCH_SEAL_V1',
        'target': str(TARGET),
        'changed': changed,
        'scope': 'BACKEND_AGENT_RUN_LOOP_ONLY',
        'frontend_logic_unchanged': True,
        'kernel_modules_only': True,
        'before_sha256': h(before),
        'after_sha256': h(after),
        'new_function_present': 'agent_run_loop_v2' in after and 'cycle_signatures_hash72' in after,
    }
    SEAL.parent.mkdir(parents=True, exist_ok=True)
    SEAL.write_text(json.dumps(seal, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(seal, indent=2, sort_keys=True))
    return 0 if seal['new_function_present'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
