from __future__ import annotations

from urllib.parse import quote, unquote

import pass158_service_core as _core

for _name in dir(_core):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_core, _name)


class Pass158Service(_core.Pass158Service):
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

    def dispatch(self, method: str, path: str, body=None):
        result = super().dispatch(method, self._transport_path(path), body)
        self._synchronize_path_aliases()
        return result


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
