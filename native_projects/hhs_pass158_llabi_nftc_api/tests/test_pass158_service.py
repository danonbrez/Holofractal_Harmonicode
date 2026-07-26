from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import unittest

from pass158_service import BASE, Pass158Service, self_test


class ServiceConformance(unittest.TestCase):
    def test_declared_service_matrix(self) -> None:
        result = self_test()
        self.assertEqual(result["classification"], "HHS_PASS_158_LOCAL_SERVICE_API_VERIFIED")
        self.assertGreaterEqual(result["integration_cases"], 18)

    def _definition_and_instance(self, service: Pass158Service, name: str, nonce: str):
        _, definition = service.dispatch("POST", f"{BASE}/nft/definitions", {
            "canonical_name": name,
            "tensor_shape": [9, 9],
            "constraint_graph": {"nodes": ["x"], "edges": []},
            "symbol_table": "x",
        })
        self.assertNotEqual(definition["status"], "REJECTED")
        definition_id = definition["object"]["definition_id"]
        _, instance = service.dispatch("POST", f"{BASE}/nft/instances", {
            "definition_id": definition_id,
            "instance_nonce": nonce,
        })
        self.assertNotEqual(instance["status"], "REJECTED")
        return definition_id, instance["object"]["instance_id"]

    def test_composition_endpoint_preserves_components(self) -> None:
        service = Pass158Service()
        try:
            definition_id, first = self._definition_and_instance(
                service, "COMPOSITION_TEST", "composition-a"
            )
            _, second_response = service.dispatch("POST", f"{BASE}/nft/instances", {
                "definition_id": definition_id,
                "instance_nonce": "composition-b",
            })
            second = second_response["object"]["instance_id"]
            instance_ids = [first, second]
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

    def test_hash216_projection_is_automatic_and_receipt_verified(self) -> None:
        service = Pass158Service()
        try:
            _, instance_id = self._definition_and_instance(
                service, "AUTOMATIC_PROJECTION_TEST", "automatic-projection"
            )
            _, capability = service.dispatch(
                "POST", f"{BASE}/nft/instances/{instance_id}/capabilities", {"commit": True}
            )
            capability_id = capability["object"]["capability_id"]
            _, bound = service.dispatch("POST", f"{BASE}/nft/instances/{instance_id}/bindings", {
                "capability_id": capability_id,
                "bindings": [{
                    "symbol": "x",
                    "kind": "RATIONAL",
                    "value": {"numerator": "1", "denominator": "3"},
                }],
            })
            self.assertEqual(bound["status"], "BOUND")
            _, status = service.dispatch("GET", f"{BASE}/status", {})
            scheduler = status["object"]["hash216_projection_scheduler"]
            self.assertGreaterEqual(scheduler["objects"], 4)
            self.assertGreaterEqual(scheduler["authoritative_queue"], 4)
            self.assertTrue(scheduler["receipt_verifier_configured"])

            gui_base = f"{BASE}/gui/projection"
            _, package_response = service.dispatch(
                "POST", f"{gui_base}/packages/next", {"frame_sequence": 1}
            )
            package = package_response["object"]
            root = package["projection_root_hash216"]
            self.assertEqual(package_response["status"], "PENDING_VM81")

            _, forged = service.dispatch(
                "POST", f"{gui_base}/packages/{root}/admit",
                {"admitted": True, "receipt_hash72": "0" * 72},
            )
            self.assertEqual(forged["classification"], "HASH72_RECEIPT_MISMATCH")

            _, transition = service.dispatch(
                "POST", f"{BASE}/nft/instances/{instance_id}/transitions",
                {
                    "capability_id": capability_id,
                    "operations": [{"opcode": "BIND_EQ", "operands": [root, root]}],
                    "commit_policy": "EXECUTE_THEN_COMMIT",
                },
            )
            self.assertEqual(transition["status"], "COMMITTED")
            receipt_id = transition["receipts"][0]["receipt_id"]
            _, admitted = service.dispatch(
                "POST", f"{gui_base}/packages/{root}/admit",
                {"admitted": True, "receipt_hash72": receipt_id},
            )
            self.assertEqual(admitted["status"], "ADMITTED")
        finally:
            service.close()

    def test_operand_boundaries_produce_distinct_transition_identities(self) -> None:
        service = Pass158Service()
        try:
            _, instance_id = self._definition_and_instance(
                service, "OPERAND_BOUNDARY_TEST", "operand-boundary"
            )
            _, capability = service.dispatch(
                "POST", f"{BASE}/nft/instances/{instance_id}/capabilities", {"commit": True}
            )
            capability_id = capability["object"]["capability_id"]
            roots = []
            for operands in (["a,b", "c"], ["a", "b,c"]):
                _, response = service.dispatch(
                    "POST", f"{BASE}/nft/instances/{instance_id}/transitions",
                    {
                        "capability_id": capability_id,
                        "operations": [{"opcode": "BIND_EQ", "operands": operands}],
                        "commit_policy": "EXECUTE_ONLY",
                    },
                )
                self.assertEqual(response["status"], "AUTHORIZED")
                roots.append(response["object"]["post_state_root"])
            self.assertNotEqual(roots[0], roots[1])
        finally:
            service.close()

    def test_dispatch_serializes_concurrent_native_mutations(self) -> None:
        service = Pass158Service()
        try:
            def register(index: int) -> str:
                _, response = service.dispatch("POST", f"{BASE}/nft/definitions", {
                    "canonical_name": f"CONCURRENT_{index}",
                    "tensor_shape": [1],
                    "constraint_graph": {"nodes": [f"x{index}"], "edges": []},
                    "symbol_table": f"x{index}",
                })
                self.assertEqual(response["status"], "REGISTERED")
                return response["object"]["definition_id"]

            with ThreadPoolExecutor(max_workers=8) as executor:
                identities = list(executor.map(register, range(12)))
            self.assertEqual(len(set(identities)), 12)
            _, status = service.dispatch("GET", f"{BASE}/status", {})
            # Raw and URL-safe aliases may both be represented; all definitions are retained.
            self.assertGreaterEqual(status["object"]["definitions"], 12)
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
