# Distributed Authority Federation Pass 056

Authoritative source: corresponding JSON artifact.

```json
{
  "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
  "delegated_sublease": {
    "allowed_operations": [
      "CREATE_DECLARED_MODULES"
    ],
    "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
    "authority_amplified": false,
    "capability_ids": [
      "capability:repository-mutation"
    ],
    "delegable": false,
    "delegation_depth": 1,
    "expires_at_sequence": 130,
    "federation_contract_root_hash72": "/3lxma4O5vKX2?Pf3k?(8KkfKf<?PWsM!6!8KF7A652kTFR-sROrPKLVHmxI!ly3q9uaJO+8",
    "issuance_ok": true,
    "parent_lease_root_hash72": "HH5/R7X09laHvodpaLM2)?qPLIb6u*f-eREHdaK9k4GhnOY!JA?yj)SH*b<Vb1PqoJPzW*EP",
    "reasons": [],
    "remote_component_id": "agent:remote-executor",
    "remote_identity_root_hash72": "hYxG-wiGL6(m*V/X3nsEhGBJq0xe+szLMT?hBAAbxu((yMXl0T>RP-3jGszeu*oQYLq-w<Gt",
    "remote_role_id": "role:remote-execution-agent",
    "schema": "HHS_DELEGATED_CAPABILITY_SUBLEASE_V1",
    "source_scope": [
      "object:canonical-pass054-repository"
    ],
    "sublease_id": "sublease:pass056-remote-a",
    "sublease_root_hash72": "XATqoxRF<!4ihItDhsAqn(Gaa+5ghZO1EIxGA50)h0G<ZcO7unULDeo!PGbh*rrfomQXi>jh",
    "sublease_state": "ACTIVE",
    "valid_from_sequence": 110,
    "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
  },
  "delegation_chain": {
    "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
    "chain_id": "delegation-chain:pass056",
    "complete": true,
    "delegation_chain_root_hash72": "aY+bses*)gX-ryQgWhhR4J4dhww9)N9)zVLtOlHJk7yN26djXpH4!TxFSLxcZ7or8B1zp-6q",
    "depth": 1,
    "federation_contract_root_hash72": "/3lxma4O5vKX2?Pf3k?(8KkfKf<?PWsM!6!8KF7A652kTFR-sROrPKLVHmxI!ly3q9uaJO+8",
    "local_delegation_root_hash72": "HH5/R7X09laHvodpaLM2)?qPLIb6u*f-eREHdaK9k4GhnOY!JA?yj)SH*b<Vb1PqoJPzW*EP",
    "reasons": [],
    "schema": "HHS_WITNESSED_DELEGATION_CHAIN_V1",
    "sublease_roots": [
      "XATqoxRF<!4ihItDhsAqn(Gaa+5ghZO1EIxGA50)h0G<ZcO7unULDeo!PGbh*rrfomQXi>jh"
    ],
    "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
  },
  "federated_ingress": {
    "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
    "canonical_continuation": true,
    "federated_ingress_root_hash72": "?cfxpxYF7mxWAKW4vtb)Azz!?l5m)my?<G-UEh?3iJBxefXXNcKd<SmUZ?+bOdPP45e)Q<p-",
    "federation_contract_root_hash72": "/3lxma4O5vKX2?Pf3k?(8KkfKf<?PWsM!6!8KF7A652kTFR-sROrPKLVHmxI!ly3q9uaJO+8",
    "local_revalidation_performed": true,
    "ok": true,
    "reasons": [],
    "remote_receipt_root_hash72": "G>Yrsk/JD3FQ?FEwgLpMzifPaW/vwU<+40Ud(MG/Rgyj4C+yqS2Lb/?(3x4tEytvXETqP2i0",
    "schema": "HHS_FEDERATED_RESULT_INGRESS_V1",
    "status": "ADMIT_FEDERATED_RESULT_INGRESS",
    "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
  },
  "federation_contract": {
    "accepted_remote_role_ids": [
      "role:remote-execution-agent"
    ],
    "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
    "federation_contract_root_hash72": "/3lxma4O5vKX2?Pf3k?(8KkfKf<?PWsM!6!8KF7A652kTFR-sROrPKLVHmxI!ly3q9uaJO+8",
    "federation_id": "federation:hhs-local-remote-a",
    "local_domain_id": "runtime:local",
    "max_delegation_depth": 2,
    "remote_domain_id": "runtime:remote-a",
    "remote_results_are_local_authority": false,
    "required_witness_types": [
      "HHS_HASH72_KERNEL_WITNESS_V1",
      "HHS_REMOTE_CHECKPOINT_CHAIN_V1",
      "HHS_REMOTE_DISPATCH_RECEIPT_V1"
    ],
    "requires_local_revalidation": true,
    "revocation_propagation_required": true,
    "schema": "HHS_FEDERATION_DOMAIN_CONTRACT_V1",
    "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
  },
  "ok": true,
  "parent_lease": {
    "allowed_operations": [
      "CREATE_DECLARED_MODULES",
      "UPDATE_REGISTRY",
      "ADD_TESTS",
      "REGENERATE_MANIFESTS"
    ],
    "authority": "HHS_I019_AUTHORITY_ACTIVATION_BOUNDARY_V1",
    "capability_ids": [
      "capability:repository-mutation"
    ],
    "component_id": "agent:development",
    "delegable": false,
    "expires_at_sequence": 140,
    "issuance_ok": true,
    "issuance_reasons": [],
    "issued_from_authority_graph_root_hash72": "EEHb?aKes**8AFv1IHQdt+7yDJ5Nb*5CQ7AmX<dgLfRmAp(jHY4S)gH58h1dW!(rdp)TPN/!",
    "last_transition_root_hash72": "?bshU!DFhDynFB1iFGwpLRsH5wY+U3ee3cn?jx71)PGA>f?9f(o!UyDFJcKTm46N!Jt7fWrT",
    "lease_id": "lease:pass055-runtime-dispatch",
    "lease_root_hash72": "HH5/R7X09laHvodpaLM2)?qPLIb6u*f-eREHdaK9k4GhnOY!JA?yj)SH*b<Vb1PqoJPzW*EP",
    "lease_state": "ACTIVE",
    "mutation_authority": "EXPLICIT_ONLY",
    "revocable": true,
    "role_contract_root_hash72": "F-e+euO>iHTcgzU9wfkFDrGGzG)Bg4-FJ4/>>!Qz>Ln9cepmeBE>fEJ7+>rXRZI4U>?wUga0",
    "role_id": "role:implementation-agent",
    "schema": "HHS_REVOCABLE_CAPABILITY_LEASE_V1",
    "source_scope": [
      "object:canonical-pass054-repository"
    ],
    "task_assignment_root_hash72": "abAv0*YWuxi>(Bj1>elec5Azp0JuzRdA5?iR/WLSh?Qom!bPOnydNAwKU?O1Qj3-Chfl?E<O",
    "task_id": "task:pass055-runtime-dispatch",
    "valid_from_sequence": 100,
    "version": "PASS_055_AUTHORITY_ENFORCED_RUNTIME_DISPATCH_REVOCABLE_CAPABILITY_LEASES_V1"
  },
  "rejection_codes": [
    "REJECT_REMOTE_AUTHORITY_WITHOUT_FEDERATION_CONTRACT",
    "REJECT_UNKNOWN_REMOTE_AUTHORITY_IDENTITY",
    "REJECT_DELEGATION_WITHOUT_PARENT_LEASE",
    "REJECT_DELEGATION_FROM_INACTIVE_PARENT_LEASE",
    "REJECT_SUBLEASE_SCOPE_EXCEEDS_PARENT",
    "REJECT_SUBLEASE_OUTLIVES_PARENT",
    "REJECT_DELEGATION_DEPTH_EXCEEDED",
    "REJECT_DELEGATION_CYCLE",
    "REJECT_REMOTE_EXECUTION_AFTER_PARENT_REVOCATION",
    "REJECT_REMOTE_EXECUTION_AFTER_PARENT_TASK_CLOSURE",
    "REJECT_BROKEN_DELEGATION_PROVENANCE",
    "REJECT_REMOTE_RECEIPT_WITHOUT_CHECKPOINT_CHAIN",
    "REJECT_REMOTE_RESULT_AS_LOCAL_AUTHORITY",
    "REJECT_REMOTE_RECEIPT_WITHOUT_LOCAL_REVALIDATION",
    "REJECT_REVOCATION_NOT_PROPAGATED",
    "REJECT_FEDERATED_CONTINUATION_WITHOUT_LOCAL_ADMISSION"
  ],
  "remote_checkpoint_chain": {
    "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
    "checkpoint_chain_root_hash72": "yO70yeKO?s)HEkopaJa<BhmVFLus/INT/JGJvWH2e+7rOdcYOo/U7/U2Gx*MU8HaARd?yM/w",
    "checkpoints": [
      {
        "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
        "checkpoint_root_hash72": "!yINeNAUcej!q1y>CCS>WnonY*eVtCXE+g1X+TzBfpiDduwO3T2bCOZGlH(o)p79VNqPss9U",
        "ok": true,
        "schema": "HHS_REMOTE_EXECUTION_CHECKPOINT_V1",
        "sequence": 115,
        "sublease_root_hash72": "XATqoxRF<!4ihItDhsAqn(Gaa+5ghZO1EIxGA50)h0G<ZcO7unULDeo!PGbh*rrfomQXi>jh",
        "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
      },
      {
        "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
        "checkpoint_root_hash72": "!yINeNAUcej!q1y>CCS>WnonY*eVtDTH+g1X+TzBfpiDduwO3T2bCOZGlH(o)p79VNqPss9U",
        "ok": true,
        "schema": "HHS_REMOTE_EXECUTION_CHECKPOINT_V1",
        "sequence": 122,
        "sublease_root_hash72": "XATqoxRF<!4ihItDhsAqn(Gaa+5ghZO1EIxGA50)h0G<ZcO7unULDeo!PGbh*rrfomQXi>jh",
        "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
      },
      {
        "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
        "checkpoint_root_hash72": "!yINeNAUcej!q1y>CCS>WnonY*eVtD-A+g1X+TzBfpiDduwO3T2bCOZGlH(o)p79VNqPss9U",
        "ok": true,
        "schema": "HHS_REMOTE_EXECUTION_CHECKPOINT_V1",
        "sequence": 129,
        "sublease_root_hash72": "XATqoxRF<!4ihItDhsAqn(Gaa+5ghZO1EIxGA50)h0G<ZcO7unULDeo!PGbh*rrfomQXi>jh",
        "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
      }
    ],
    "complete": true,
    "schema": "HHS_REMOTE_CHECKPOINT_CHAIN_V1",
    "sublease_root_hash72": "XATqoxRF<!4ihItDhsAqn(Gaa+5ghZO1EIxGA50)h0G<ZcO7unULDeo!PGbh*rrfomQXi>jh",
    "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
  },
  "remote_dispatch": {
    "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
    "delegation_chain_root_hash72": "aY+bses*)gX-ryQgWhhR4J4dhww9)N9)zVLtOlHJk7yN26djXpH4!TxFSLxcZ7or8B1zp-6q",
    "ok": true,
    "parent_lease_root_hash72": "HH5/R7X09laHvodpaLM2)?qPLIb6u*f-eREHdaK9k4GhnOY!JA?yj)SH*b<Vb1PqoJPzW*EP",
    "reasons": [],
    "remote_dispatch_decision_root_hash72": "x7hiiI8CK!knVSx45fzgJW+LCJ6pwYrJFKl1RfjwQ(IjgehWpG6rCFh+jT(R/9A/C2D/W/Nb",
    "schema": "HHS_REMOTE_DISPATCH_DECISION_V1",
    "sequence": 111,
    "status": "ADMIT_REMOTE_DISPATCH",
    "sublease_root_hash72": "XATqoxRF<!4ihItDhsAqn(Gaa+5ghZO1EIxGA50)h0G<ZcO7unULDeo!PGbh*rrfomQXi>jh",
    "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
  },
  "remote_execution_receipt": {
    "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
    "checkpoint_chain_root_hash72": "yO70yeKO?s)HEkopaJa<BhmVFLus/INT/JGJvWH2e+7rOdcYOo/U7/U2Gx*MU8HaARd?yM/w",
    "delegation_chain_root_hash72": "aY+bses*)gX-ryQgWhhR4J4dhww9)N9)zVLtOlHJk7yN26djXpH4!TxFSLxcZ7or8B1zp-6q",
    "ok": true,
    "reasons": [],
    "remote_dispatch_decision_root_hash72": "x7hiiI8CK!knVSx45fzgJW+LCJ6pwYrJFKl1RfjwQ(IjgehWpG6rCFh+jT(R/9A/C2D/W/Nb",
    "remote_receipt_root_hash72": "G>Yrsk/JD3FQ?FEwgLpMzifPaW/vwU<+40Ud(MG/Rgyj4C+yqS2Lb/?(3x4tEytvXETqP2i0",
    "remote_result_is_local_authority": false,
    "remote_result_root_hash72": "iEy1m+p8efcRw1nim3dD8Apfx5Ov-kK<gEkSBt+gTLIoTATzVQUBLY2BT4WN)ZXgFr7(0(*P",
    "schema": "HHS_REMOTE_DISPATCH_RECEIPT_V1",
    "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
  },
  "remote_identity": {
    "authority": "HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1",
    "component_id": "agent:remote-executor",
    "federation_contract_root_hash72": "/3lxma4O5vKX2?Pf3k?(8KkfKf<?PWsM!6!8KF7A652kTFR-sROrPKLVHmxI!ly3q9uaJO+8",
    "identity_status": "ADMITTED",
    "remote_domain_id": "runtime:remote-a",
    "remote_identity_id": "remote-identity:runtime-a-agent",
    "remote_identity_root_hash72": "hYxG-wiGL6(m*V/X3nsEhGBJq0xe+szLMT?hBAAbxu((yMXl0T>RP-3jGszeu*oQYLq-w<Gt",
    "role_id": "role:remote-execution-agent",
    "schema": "HHS_REMOTE_AUTHORITY_IDENTITY_V1",
    "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
  },
  "run_root_hash72": "*oKkH8<jt8gQydzcAq(Yzc>QTsp5vYtkxXsSw136uG)jv(Jy?852J>V?IOJ*vJmGh<9nsPOp",
  "schema": "HHS_DISTRIBUTED_AUTHORITY_FEDERATION_RUN_V1",
  "version": "PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
}
```
