from __future__ import annotations

from urllib.parse import quote, unquote
from typing import Any

import pass158_service_core as _core
from hash216_projection_scheduler import Hash216ProjectionScheduler
from pass158_gui_projection_runtime import (
    BASE as GUI_PROJECTION_BASE,
    Pass158GuiProjectionRuntime,
)

for _name in dir(_core):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_core, _name)


class Pass158Service(_core.Pass158Service):
    """Pass 158 service with automatic Hash216 projection indexing.

    Native state remains authoritative. Every successful service mutation or
    receipt is observed by the Hash216 scheduler, while GUI projection package
    admission still requires VM81 validation and a Hash72 receipt.
    """

    def __init__(self, native=None):
        super().__init__(native)
        scheduler = Hash216ProjectionScheduler(
            receipt_verifier=self._verify_projection_receipt
        )
        self.gui_projection = Pass158GuiProjectionRuntime(scheduler)


    def _verify_projection_receipt(
        self, receipt_hash72: str, projection_root_hash216: str
    ) -> bool:
        candidates = (
            receipt_hash72,
            self.decode_path_identity(receipt_hash72),
            self.encode_path_identity(receipt_hash72),
        )
        receipt = next((self.receipts.get(key) for key in candidates if key in self.receipts), None)
        if receipt is None:
            return False
        serialized = receipt.serialize()
        if int(serialized.get("committed", 0)) != 1:
            return False
        replay = receipt.replay()
        if not replay.get("matched"):
            return False
        try:
            material = bytes.fromhex(str(serialized.get("replay_material_hex", "")))
        except ValueError:
            return False
        root_bytes = projection_root_hash216.encode("ascii")
        return (
            root_bytes in material
            or root_bytes.hex().encode("ascii") in material
        )

    @staticmethod
    def encode_path_identity(identity: str) -> str:
        return quote(identity, safe="")

    @staticmethod
    def decode_path_identity(identity: str) -> str:
        return unquote(identity)

    def _transport_path(self, path: str) -> str:
        identities = set(self.instances) | set(self.receipts) | set(self.graphs) | set(self.bindings)
        for identity in sorted(identities, key=len, reverse=True):
            path = path.replace(identity, self.encode_path_identity(identity))
        return path

    def _instance(self, instance_id: str):
        decoded = self.decode_path_identity(instance_id)
        try:
            return super()._instance(decoded)
        except KeyError:
            return super()._instance(instance_id)

    def _store_receipt(self, receipt):
        serialized = super()._store_receipt(receipt)
        receipt_id = serialized["receipt_id"]
        self.receipts[self.encode_path_identity(receipt_id)] = receipt
        return serialized

    def _synchronize_path_aliases(self) -> None:
        for instance_id, instance in list(self.instances.items()):
            if "%" not in instance_id:
                self.instances[self.encode_path_identity(instance_id)] = instance
        for instance_id, bindings in list(self.bindings.items()):
            if "%" not in instance_id:
                self.bindings[self.encode_path_identity(instance_id)] = bindings
        for instance_id, graph in list(self.graphs.items()):
            if "%" not in instance_id:
                self.graphs[self.encode_path_identity(instance_id)] = graph

    def _observe_response(self, method: str, path: str, body: Any, response: dict[str, Any]) -> None:
        if response.get("status") == "REJECTED":
            return
        scheduler = self.gui_projection.scheduler
        obj = response.get("object") if isinstance(response.get("object"), dict) else {}
        classification = str(response.get("classification", ""))
        status = str(response.get("status", ""))
        authoritative_statuses = {"REGISTERED", "INSTANTIATED", "BOUND", "COMMITTED", "AUTHORIZED", "REPLAYED"}

        for receipt in response.get("receipts", []):
            if not isinstance(receipt, dict) or not receipt.get("receipt_id"):
                continue
            scheduler.observe_runtime_state(
                f"receipt:{receipt['receipt_id']}",
                "RECEIPT_CANDIDATE_OBJECT",
                receipt,
                authoritative=True,
                delta_offset_vector=obj.get("delta_vector"),
            )

        instance_id = obj.get("instance_id")
        state_root = obj.get("post_state_root") or obj.get("state_root") or obj.get("source_state_root")
        if instance_id and state_root:
            scheduler.observe_runtime_state(
                f"instance:{instance_id}",
                "NFT_INSTANCE_STATE_OBJECT",
                {
                    "instance_id": instance_id,
                    "state_root": state_root,
                },
                authoritative=status in authoritative_statuses,
            )

        if classification == "HHS_P158_DELTA_STATE_OFFSET_NORMALIZED" and instance_id:
            scheduler.observe_runtime_state(
                f"projection:{instance_id}:{obj.get('projection_profile', 'UNKNOWN')}",
                "RENDER_ATTRIBUTE_OBJECT",
                obj,
                authoritative=False,
                dependencies=(f"instance:{instance_id}",) if state_root else (),
                delta_offset_vector=obj.get("delta_vector"),
            )

    def dispatch(self, method: str, path: str, body=None):
        with self._dispatch_lock:
            if path.startswith(GUI_PROJECTION_BASE):
                return self.gui_projection.dispatch(method, path, body)
            result = super().dispatch(method, self._transport_path(path), body)
            self._synchronize_path_aliases()
            code, response = result
            self._observe_response(method, path, body, response)
            if method.upper() == "GET" and path == f"{_core.BASE}/status" and response.get("status") != "REJECTED":
                response["object"]["hash216_projection_scheduler"] = self.gui_projection.scheduler.status()
            return code, response


_core.Pass158Service = Pass158Service
try:
    _core.Handler.service.close()
except Exception:
    pass
_core.Handler.service = Pass158Service()
Handler = _core.Handler
self_test = _core.self_test
main = _core.main
BASE = _core.BASE
API_VERSION = _core.API_VERSION
CONTRACT_ID = _core.CONTRACT_ID


if __name__ == "__main__":
    main()
