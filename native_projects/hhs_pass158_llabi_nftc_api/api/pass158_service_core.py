from __future__ import annotations

import argparse
import ctypes as C
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from threading import RLock
from typing import Any

from hhs_pass158 import (
    ByteSpan,
    Context,
    ExactRational,
    HHS158_BUFFER_TOO_SMALL,
    HHS158_FLAG_APPROXIMATE,
    HHS158_FLAG_PROJECTION,
    HHS158_OK,
    HHS158_OP_BIND_EQ,
    HHS158_OP_CHAIN_APPEND,
    Instance,
    MutableByteSpan,
    NativeLibrary,
    Receipt,
    Value,
    _PinnedSpan,
    _header,
)

API_VERSION = "1.0.0"
CONTRACT_ID = "HHS-P158-LLABI-NFTC-API"
BASE = "/api/v1/hhs/pass158"


class ProjectionProfile(C.Structure):
    _fields_ = [
        ("header", __import__("hhs_pass158").Header),
        ("kind", C.c_uint32),
        ("flags", C.c_uint32),
        ("profile_name", ByteSpan),
        ("decimal_digits", C.c_uint32),
        ("reserved", C.c_uint32),
    ]


class DeserializationOptions(C.Structure):
    _fields_ = [
        ("header", __import__("hhs_pass158").Header),
        ("format", C.c_uint32),
        ("preserve_unknown_fields", C.c_uint32),
        ("reject_authority_unknown_fields", C.c_uint32),
        ("flags", C.c_uint32),
    ]


class CompositionPolicy(C.Structure):
    _fields_ = [
        ("header", __import__("hhs_pass158").Header),
        ("allow_declared_cycles", C.c_uint32),
        ("isolation_level", C.c_uint32),
        ("max_dependency_depth", C.c_uint64),
        ("namespace_prefix", ByteSpan),
        ("flags", C.c_uint32),
        ("reserved", C.c_uint32),
    ]


def _request_id(method: str, path: str, body: Any) -> str:
    canonical = json.dumps([method, path, body], sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _envelope(method: str, path: str, body: Any, *, status: str, classification: str,
              obj: Any = None, receipts: list[Any] | None = None,
              warnings: list[Any] | None = None, errors: list[Any] | None = None) -> dict[str, Any]:
    return {
        "api_version": API_VERSION,
        "contract_id": CONTRACT_ID,
        "request_id": _request_id(method, path, body),
        "status": status,
        "classification": classification,
        "authority_level": "A1_EXECUTION_EVIDENCE",
        "object": obj if obj is not None else {},
        "receipts": receipts or [],
        "warnings": warnings or [],
        "errors": errors or [],
    }


class Pass158Service:
    def __init__(self, native: NativeLibrary | None = None):
        self.context = Context(native)
        self.native = self.context.native
        self.definitions: dict[str, Any] = {}
        self.instances: dict[str, Instance] = {}
        self.capabilities: dict[str, Any] = {}
        self.receipts: dict[str, Receipt] = {}
        self.graphs: dict[str, dict[str, Any]] = {}
        self.bindings: dict[str, dict[str, Any]] = {}
        self._dispatch_lock = RLock()
        self._declare_extra()

    def close(self) -> None:
        with self._dispatch_lock:
            self.context.close()

    def _declare_extra(self) -> None:
        lib = self.native.lib
        lib.hhs158_abi_descriptor_json.argtypes = [C.POINTER(MutableByteSpan)]
        lib.hhs158_abi_descriptor_json.restype = C.c_int32
        lib.hhs158_opcode_descriptor_json.argtypes = [C.POINTER(MutableByteSpan)]
        lib.hhs158_opcode_descriptor_json.restype = C.c_int32
        lib.hhs158_capabilities_json.argtypes = [C.POINTER(MutableByteSpan)]
        lib.hhs158_capabilities_json.restype = C.c_int32
        lib.hhs158_instance_project.argtypes = [C.c_void_p, C.POINTER(ProjectionProfile), C.POINTER(Value), C.POINTER(C.c_void_p)]
        lib.hhs158_instance_project.restype = C.c_int32
        lib.hhs158_value_release.argtypes = [C.POINTER(Value)]
        lib.hhs158_instance_deserialize.argtypes = [C.c_void_p, ByteSpan, C.POINTER(DeserializationOptions), C.POINTER(C.c_void_p), C.POINTER(C.c_void_p)]
        lib.hhs158_instance_deserialize.restype = C.c_int32
        lib.hhs158_instance_compose.argtypes = [C.c_void_p, C.POINTER(C.c_void_p), C.c_size_t, C.POINTER(CompositionPolicy), C.POINTER(C.c_void_p), C.POINTER(C.c_void_p)]
        lib.hhs158_instance_compose.restype = C.c_int32

    def _descriptor(self, name: str) -> Any:
        function = getattr(self.native.lib, name)
        output = MutableByteSpan(None, 0, 0)
        self.native.check(function(C.byref(output)), HHS158_BUFFER_TOO_SMALL)
        buffer = (C.c_uint8 * output.size_written)()
        output.data = C.cast(buffer, C.POINTER(C.c_uint8))
        output.capacity = len(buffer)
        self.native.check(function(C.byref(output)))
        return json.loads(bytes(buffer[: output.size_written]))

    def _store_receipt(self, receipt: Receipt) -> dict[str, Any]:
        serialized = receipt.serialize()
        self.receipts[serialized["receipt_id"]] = receipt
        return serialized

    def _instance(self, instance_id: str) -> Instance:
        try:
            return self.instances[instance_id]
        except KeyError as error:
            raise KeyError("INSTANCE_NOT_FOUND") from error

    def dispatch(self, method: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        body = body or {}
        with self._dispatch_lock:
            try:
                return 200, self._dispatch(method.upper(), path, body)
            except Exception as error:
                classification = getattr(error, "classification", None) or str(error).strip("'") or error.__class__.__name__
                return 200, _envelope(method, path, body, status="REJECTED", classification=classification,
                                      errors=[{"type": error.__class__.__name__, "message": str(error)}])

    def _dispatch(self, method: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
        if method == "GET" and path == f"{BASE}/capabilities":
            return _envelope(method, path, body, status="OK", classification="PASS158_CAPABILITIES",
                             obj=self._descriptor("hhs158_capabilities_json"))
        if method == "GET" and path == f"{BASE}/abi":
            return _envelope(method, path, body, status="OK", classification="PASS158_ABI_DESCRIPTOR",
                             obj=self._descriptor("hhs158_abi_descriptor_json"))
        if method == "GET" and path == f"{BASE}/opcodes":
            return _envelope(method, path, body, status="OK", classification="PASS158_PUBLIC_OPCODE_REGISTRY",
                             obj=self._descriptor("hhs158_opcode_descriptor_json"))
        if method == "GET" and path == f"{BASE}/status":
            return _envelope(method, path, body, status="OK", classification="PASS158_SERVICE_READY",
                             obj={"definitions": len(self.definitions), "instances": len(self.instances), "receipts": len(self.receipts)})
        if method == "GET" and path == f"{BASE}/manifest":
            return _envelope(method, path, body, status="OK", classification="PASS158_APPLICATION_MANIFEST",
                             obj={"required_abi_version": "1.0", "numeric_policy": "EXACT_SYMBOLIC", "replay_required": True})

        if method == "POST" and path == f"{BASE}/nft/definitions":
            graph = body.get("constraint_graph", {})
            constraints = body.get("canonical_constraints") or json.dumps(graph, sort_keys=True, separators=(",", ":"))
            definition, receipt = self.context.register_definition(
                name=body["canonical_name"], constraints=constraints,
                symbols=body.get("symbol_table", ""), shape=tuple(body.get("tensor_shape", (1,))),
                ancestry=body.get("ancestry", "P154|P155|P156|P156.1|P157"),
            )
            evidence = self._store_receipt(receipt)
            definition_id = evidence["definition_id"]
            self.definitions[definition_id] = definition
            return _envelope(method, path, body, status="REGISTERED", classification="HHS_P158_NFT_DEFINITION_REGISTERED",
                             obj={"definition_id": definition_id, "canonical_hash": evidence["object_root"]}, receipts=[evidence])

        if method == "POST" and path == f"{BASE}/nft/instances":
            definition = self.definitions[body["definition_id"]]
            nonce = body["instance_nonce"].encode("utf-8")
            instance, receipt = definition.instantiate(nonce)
            evidence = self._store_receipt(receipt)
            instance_id = instance.instance_id
            self.instances[instance_id] = instance
            self.bindings[instance_id] = {}
            self.graphs[instance_id] = {"nodes": [instance_id], "edges": [], "definition_id": body["definition_id"]}
            return _envelope(method, path, body, status="INSTANTIATED", classification="HHS_P158_NFT_INSTANCE_CONSTRUCTED",
                             obj={"instance_id": instance_id, "state_root": instance.state_root}, receipts=[evidence])

        match = re.fullmatch(re.escape(BASE) + r"/nft/instances/([^/]+)/bindings", path)
        if method == "POST" and match:
            instance_id = match.group(1); instance = self._instance(instance_id)
            capability = self.capabilities[body["capability_id"]]
            evidences: list[dict[str, Any]] = []
            for binding in body.get("bindings", []):
                kind = binding["kind"]
                if kind == "RATIONAL":
                    value = binding["value"]
                    exact = ExactRational(int(value["numerator"]), int(value["denominator"]))
                    binding_receipt = instance.bind_rational(binding["symbol"], exact, capability)
                    stored: Any = {"kind": kind, "value": {"numerator": str(exact.numerator), "denominator": str(exact.denominator)}}
                elif kind == "LIST":
                    binding_receipt = instance.bind_ordered_list(binding["symbol"], binding["value"], capability)
                    stored = {"kind": kind, "value": list(binding["value"])}
                else:
                    raise ValueError("TYPE_MISMATCH")
                self.bindings[instance_id][binding["symbol"]] = stored
                evidences.append(self._store_receipt(binding_receipt))
            if not evidences:
                raise ValueError("BINDINGS_REQUIRED")
            return _envelope(method, path, body, status="BOUND", classification="HHS_P158_ABI_APPLICATION_BINDING_VALIDATED",
                             obj={"instance_id": instance_id, "state_root": instance.state_root,
                                  "bindings": self.bindings[instance_id]}, receipts=evidences)

        match = re.fullmatch(re.escape(BASE) + r"/nft/instances/([^/]+)/validate", path)
        if method == "POST" and match:
            instance = self._instance(match.group(1)); report = instance.validate()
            return _envelope(method, path, body, status="VALIDATED", classification=report["classification"], obj=report)

        match = re.fullmatch(re.escape(BASE) + r"/nft/instances/([^/]+)/capabilities", path)
        if method == "POST" and match:
            instance = self._instance(match.group(1)); capability = instance.capability(commit=bool(body.get("commit", True)))
            capability_id = hashlib.sha256((instance.instance_id + json.dumps(body, sort_keys=True)).encode()).hexdigest()
            self.capabilities[capability_id] = capability
            return _envelope(method, path, body, status="AUTHORIZED", classification="HHS_P158_CAPABILITY_OPENED",
                             obj={"capability_id": capability_id, "instance_id": instance.instance_id})

        match = re.fullmatch(re.escape(BASE) + r"/nft/instances/([^/]+)/transitions", path)
        if method == "POST" and match:
            instance = self._instance(match.group(1)); capability = self.capabilities[body["capability_id"]]
            operation_map = {"BIND_EQ": HHS158_OP_BIND_EQ, "CHAIN_APPEND": HHS158_OP_CHAIN_APPEND}
            operations = [
                (
                    operation_map[item["opcode"]],
                    json.dumps(
                        [str(operand) for operand in item.get("operands", [])],
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                )
                for item in body["operations"]
            ]
            summary, receipt = instance.execute(capability, operations, commit=body.get("commit_policy", "EXECUTE_THEN_COMMIT") != "EXECUTE_ONLY")
            evidence = self._store_receipt(receipt)
            return _envelope(method, path, body, status="COMMITTED" if "COMMITTED" in summary.classification else "AUTHORIZED",
                             classification=summary.classification,
                             obj={"instance_id": instance.instance_id, "pre_state_root": summary.pre_state_root,
                                  "post_state_root": summary.post_state_root, "vm81_steps": summary.vm81_steps}, receipts=[evidence])

        match = re.fullmatch(re.escape(BASE) + r"/nft/instances/([^/]+)/project", path)
        if method == "POST" and match:
            instance = self._instance(match.group(1)); profile_name = body.get("profile", "IEEE754_BINARY64_CONTROL")
            profile_pin = _PinnedSpan(profile_name); profile = ProjectionProfile(); _header(profile)
            profile.kind = 2 if profile_name == "IEEE754_BINARY64_CONTROL" else 1; profile.profile_name = profile_pin.span
            projected = Value(); receipt_handle = C.c_void_p()
            self.native.check(self.native.lib.hhs158_instance_project(instance.handle, C.byref(profile), C.byref(projected), C.byref(receipt_handle)))
            payload = bytes(projected.canonical_payload.data[: projected.canonical_payload.size]).decode("utf-8")
            flags = projected.flags
            self.native.lib.hhs158_value_release(C.byref(projected))
            evidence = self._store_receipt(Receipt(self.context, receipt_handle))
            source = self.bindings.get(instance.instance_id, {})
            return _envelope(method, path, body, status="PROJECTED", classification="HHS_P158_DELTA_STATE_OFFSET_NORMALIZED",
                             obj={"source_state_root": instance.state_root, "projection_profile": profile_name,
                                  "projected_value": payload, "projection_flags": flags,
                                  "approximate": bool(flags & (HHS158_FLAG_APPROXIMATE | HHS158_FLAG_PROJECTION)),
                                  "delta_vector": {"bindings": source}}, receipts=[evidence])

        if method == "POST" and path == f"{BASE}/nft/compose":
            components = [self._instance(item) for item in body["instance_ids"]]
            handles = (C.c_void_p * len(components))(*[item.handle.value for item in components])
            policy = CompositionPolicy(); _header(policy); policy.max_dependency_depth = int(body.get("max_dependency_depth", 72)); policy.allow_declared_cycles = int(body.get("allow_declared_cycles", False))
            composite_handle = C.c_void_p(); receipt_handle = C.c_void_p()
            self.native.check(self.native.lib.hhs158_instance_compose(self.context.handle, handles, len(components), C.byref(policy), C.byref(composite_handle), C.byref(receipt_handle)))
            composite = Instance(self.context, composite_handle); self.instances[composite.instance_id] = composite
            self.graphs[composite.instance_id] = {"nodes": body["instance_ids"] + [composite.instance_id], "edges": [[item, composite.instance_id] for item in body["instance_ids"]]}
            evidence = self._store_receipt(Receipt(self.context, receipt_handle))
            return _envelope(method, path, body, status="INSTANTIATED", classification="HHS_P158_NFT_INSTANCE_CONSTRUCTED",
                             obj={"instance_id": composite.instance_id, "components": body["instance_ids"]}, receipts=[evidence])

        match = re.fullmatch(re.escape(BASE) + r"/nft/instances/([^/]+)/serialize", path)
        if method == "POST" and match:
            instance = self._instance(match.group(1)); serialized = instance.serialize()
            return _envelope(method, path, body, status="OK", classification="HHS_P158_SERIALIZATION_CANONICAL",
                             obj={"format": "HHS_CANONICAL_JSON", "serialized": serialized.decode("utf-8")})

        if method == "POST" and path == f"{BASE}/nft/deserialize":
            pin = _PinnedSpan(body["serialized"]); options = DeserializationOptions(); _header(options)
            options.format = 2; options.preserve_unknown_fields = 1; options.reject_authority_unknown_fields = 1
            instance_handle = C.c_void_p(); receipt_handle = C.c_void_p()
            self.native.check(self.native.lib.hhs158_instance_deserialize(self.context.handle, pin.span, C.byref(options), C.byref(instance_handle), C.byref(receipt_handle)))
            instance = Instance(self.context, instance_handle); self.instances[instance.instance_id] = instance
            evidence = self._store_receipt(Receipt(self.context, receipt_handle))
            return _envelope(method, path, body, status="INSTANTIATED", classification="HHS_P158_NFT_INSTANCE_DESERIALIZED_UNPRIVILEGED",
                             obj={"instance_id": instance.instance_id, "privileged": False}, receipts=[evidence])

        match = re.fullmatch(re.escape(BASE) + r"/receipts/([^/]+)/replay", path)
        if method == "POST" and match:
            replay = self.receipts[match.group(1)].replay()
            return _envelope(method, path, body, status="REPLAYED", classification=replay["classification"], obj=replay)

        match = re.fullmatch(re.escape(BASE) + r"/receipts/([^/]+)", path)
        if method == "GET" and match:
            receipt = self.receipts[match.group(1)].serialize()
            return _envelope(method, path, body, status="OK", classification="HHS_P158_RECEIPT_INSPECTED", obj=receipt)

        match = re.fullmatch(re.escape(BASE) + r"/nft/instances/([^/]+)/graph", path)
        if method == "GET" and match:
            graph = self.graphs.get(match.group(1), {"nodes": [match.group(1)], "edges": []})
            return _envelope(method, path, body, status="OK", classification="HHS_P158_GRAPH_QUERY_NON_MUTATING", obj=graph)

        raise KeyError("ENDPOINT_NOT_FOUND")


def self_test() -> dict[str, Any]:
    service = Pass158Service()
    cases: list[tuple[str, str, dict[str, Any]]] = []
    try:
        for path in ("capabilities", "abi", "opcodes", "status", "manifest"):
            cases.append(("GET", f"{BASE}/{path}", {}))
        definition_request = {
            "canonical_name": "SERVICE_TEST_OBJECT", "tensor_shape": [9, 9],
            "constraint_graph": {"nodes": ["A", "B", "C"], "edges": [["A", "B"], ["B", "C"]]},
            "symbol_table": "A,B,C,x,ordered",
        }
        code, response = service.dispatch("POST", f"{BASE}/nft/definitions", definition_request); assert code == 200 and response["status"] == "REGISTERED"
        definition_id = response["object"]["definition_id"]; cases.append(("POST", f"{BASE}/nft/definitions", definition_request))
        instance_request = {"definition_id": definition_id, "instance_nonce": "service-test-instance"}
        _, response = service.dispatch("POST", f"{BASE}/nft/instances", instance_request); instance_id = response["object"]["instance_id"]; cases.append(("POST", f"{BASE}/nft/instances", instance_request))
        capability_request = {"commit": True}
        _, capability_response = service.dispatch("POST", f"{BASE}/nft/instances/{instance_id}/capabilities", capability_request)
        capability_id = capability_response["object"]["capability_id"]
        binding_request = {"capability_id": capability_id, "bindings": [{"symbol": "x", "kind": "RATIONAL", "value": {"numerator": "1", "denominator": "3"}}, {"symbol": "ordered", "kind": "LIST", "value": ["x", "x", "y"]}]}
        cases.extend([
            ("POST", f"{BASE}/nft/instances/{instance_id}/bindings", binding_request),
            ("POST", f"{BASE}/nft/instances/{instance_id}/validate", {"mode": "FULL"}),
        ])
        for method, path, body in cases:
            _, result = service.dispatch(method, path, body); assert result["status"] != "REJECTED", result
        transition_request = {"capability_id": capability_id, "operations": [{"opcode": "BIND_EQ", "operands": ["A", "B"]}, {"opcode": "CHAIN_APPEND", "operands": ["B", "C"]}], "commit_policy": "EXECUTE_THEN_COMMIT"}
        _, transition = service.dispatch("POST", f"{BASE}/nft/instances/{instance_id}/transitions", transition_request); assert transition["status"] == "COMMITTED"
        receipt_id = transition["receipts"][0]["receipt_id"]
        integration = [
            ("POST", f"{BASE}/nft/instances/{instance_id}/transitions", transition_request),
            ("POST", f"{BASE}/nft/instances/{instance_id}/project", {"profile": "IEEE754_BINARY64_CONTROL"}),
            ("POST", f"{BASE}/nft/instances/{instance_id}/serialize", {"format": "HHS_CANONICAL_JSON"}),
            ("POST", f"{BASE}/receipts/{receipt_id}/replay", {}),
            ("GET", f"{BASE}/receipts/{receipt_id}", {}),
            ("GET", f"{BASE}/nft/instances/{instance_id}/graph", {}),
        ]
        serialized_response = service.dispatch("POST", f"{BASE}/nft/instances/{instance_id}/serialize", {})[1]
        integration.append(("POST", f"{BASE}/nft/deserialize", {"serialized": serialized_response["object"]["serialized"]}))
        for method, path, body in integration:
            _, result = service.dispatch(method, path, body); assert result["status"] != "REJECTED", result
        rejected = service.dispatch("POST", f"{BASE}/nft/instances/{instance_id}/bindings", {"capability_id": capability_id, "bindings": [{"symbol": "bad", "kind": "RATIONAL", "value": {"numerator": "1", "denominator": "0"}}]})[1]
        assert rejected["status"] == "REJECTED"
        total = len(cases) + len(integration) + 2
        assert total >= 18
        return {"classification": "HHS_PASS_158_LOCAL_SERVICE_API_VERIFIED", "integration_cases": total, "rejection_classified": rejected["classification"]}
    finally:
        service.close()


class Handler(BaseHTTPRequestHandler):
    service = Pass158Service()

    def _handle(self) -> None:
        length = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")
        _, response = self.service.dispatch(self.command, self.path, body)
        encoded = json.dumps(response, sort_keys=True, separators=(",", ":")).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    do_GET = _handle
    do_POST = _handle
    def log_message(self, *_: Any) -> None: pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("serve", "self-test"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8158)
    args = parser.parse_args()
    if args.command == "self-test":
        print(json.dumps(self_test(), sort_keys=True))
        return
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        server.serve_forever()
    finally:
        Handler.service.close()


if __name__ == "__main__":
    main()
