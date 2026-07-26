from __future__ import annotations

import unittest

from pass158_service import BASE, Pass158Service, self_test


class ServiceConformance(unittest.TestCase):
    def test_declared_service_matrix(self) -> None:
        result = self_test()
        self.assertEqual(result["classification"], "HHS_PASS_158_LOCAL_SERVICE_API_VERIFIED")
        self.assertGreaterEqual(result["integration_cases"], 18)

    def test_composition_endpoint_preserves_components(self) -> None:
        service = Pass158Service()
        try:
            _, definition = service.dispatch("POST", f"{BASE}/nft/definitions", {
                "canonical_name": "COMPOSITION_TEST",
                "tensor_shape": [9, 9],
                "constraint_graph": {"nodes": ["x"], "edges": []},
                "symbol_table": "x",
            })
            definition_id = definition["object"]["definition_id"]
            instance_ids = []
            for nonce in ("composition-a", "composition-b"):
                _, instance = service.dispatch("POST", f"{BASE}/nft/instances", {
                    "definition_id": definition_id,
                    "instance_nonce": nonce,
                })
                instance_ids.append(instance["object"]["instance_id"])
            _, composed = service.dispatch("POST", f"{BASE}/nft/compose", {
                "instance_ids": instance_ids,
                "max_dependency_depth": 72,
                "allow_declared_cycles": False,
            })
            self.assertEqual(composed["status"], "INSTANTIATED")
            self.assertEqual(composed["object"]["components"], instance_ids)
            composite_id = composed["object"]["instance_id"]
            _, graph = service.dispatch("GET", f"{BASE}/nft/instances/{composite_id}/graph")
            self.assertEqual(len(graph["object"]["edges"]), 2)
            self.assertEqual(graph["classification"], "HHS_P158_GRAPH_QUERY_NON_MUTATING")
        finally:
            service.close()

    def test_transport_success_does_not_imply_constraint_success(self) -> None:
        service = Pass158Service()
        try:
            code, result = service.dispatch("POST", f"{BASE}/nft/instances/missing/validate", {})
            self.assertEqual(code, 200)
            self.assertEqual(result["status"], "REJECTED")
            self.assertTrue(result["errors"])
        finally:
            service.close()


if __name__ == "__main__":
    unittest.main()
