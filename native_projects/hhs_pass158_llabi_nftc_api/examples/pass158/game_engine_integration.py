from pass158_service import BASE, Pass158Service

service = Pass158Service()
try:
    _, definition = service.dispatch("POST", f"{BASE}/nft/definitions", {
        "canonical_name": "GAME_WORLD_STATE",
        "tensor_shape": [9, 9],
        "constraint_graph": {"nodes": ["position", "velocity"], "edges": [["position", "velocity"]]},
        "symbol_table": "position,velocity,timestep",
    })
    definition_id = definition["object"]["definition_id"]
    _, instance = service.dispatch("POST", f"{BASE}/nft/instances", {
        "definition_id": definition_id,
        "instance_nonce": "world-frame-0001",
    })
    instance_id = instance["object"]["instance_id"]
    service.dispatch("POST", f"{BASE}/nft/instances/{instance_id}/bindings", {
        "bindings": [{"symbol": "timestep", "kind": "RATIONAL", "value": {"numerator": "1", "denominator": "60"}}]
    })
    _, capability = service.dispatch("POST", f"{BASE}/nft/instances/{instance_id}/capabilities", {"commit": True})
    capability_id = capability["object"]["capability_id"]
    _, transition = service.dispatch("POST", f"{BASE}/nft/instances/{instance_id}/transitions", {
        "capability_id": capability_id,
        "operations": [{"opcode": "BIND_EQ", "operands": ["position_next", "position+velocity*timestep"]}],
        "commit_policy": "EXECUTE_THEN_COMMIT",
    })
    print(transition)
finally:
    service.close()
