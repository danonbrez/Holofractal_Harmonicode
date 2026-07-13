# Specialized Role Contracts — Pass 054

Competence and authority scope are encoded independently.

```json
{
  "authority_graph_root_hash72": ">stO9Qu+Y5be*v+o6--9DM/7k4G!V/iMalk<NvU+0<VGIMtFpTa<I+D*NSHQzLIsE9ixAIen",
  "contracts": [
    {
      "authority": "HHS_I019_CANONICAL_DERIVATION_AUTHORITY_BOUNDARY_V1",
      "authority_scope": [
        "IMPLEMENT_APPROVED_PASS_SPECIFICATION",
        "MODIFY_DECLARED_REPOSITORY_PATHS",
        "RUN_DECLARED_VERIFICATION_TARGETS"
      ],
      "canonical_system_id": "HHS",
      "competencies": [
        "SOURCE_TREE_INSPECTION",
        "CODE_MUTATION",
        "TEST_EXECUTION",
        "ARTIFACT_REGENERATION"
      ],
      "component_id": "agent:development",
      "forbidden_authorities": [
        "REDEFINE_CANONICAL_INVARIANTS",
        "REINTERPRET_PASS_INTENT",
        "INVENT_SUBSTITUTE_AUTHORITY_PATH",
        "PROMOTE_STANDALONE_OUTPUT_TO_CANONICAL_STATE"
      ],
      "required_inputs": [
        "CANONICAL_REPOSITORY_ROOT",
        "ADMITTED_PASS_SPECIFICATION",
        "AUTHORITY_GRAPH_ROOT"
      ],
      "required_outputs": [
        "PATCH",
        "TEST_RECEIPTS",
        "GENERATED_MANIFESTS",
        "CONFORMANCE_EVIDENCE",
        "HANDOFF_PROVENANCE_BUNDLE"
      ],
      "requires_independent_revalidation": true,
      "role_contract_root_hash72": "F-e+euO>iHTcgzU9wfkFDrGGzG)Bg4-FJ4/>>!Qz>Ln9cepmeBE>fEJ7+>rXRZI4U>?wUga0",
      "role_id": "role:implementation-agent",
      "schema": "HHS_SPECIALIZED_ROLE_CONTRACT_V1",
      "shared_invariant_ids": [
        "HHS-I017",
        "HHS-I018",
        "HHS-I019"
      ],
      "version": "PASS_054_CANONICAL_AUTHORITY_GRAPH_ROLE_BOUND_AGENT_ORCHESTRATION_V1"
    }
  ],
  "schema": "HHS_SPECIALIZED_ROLE_CONTRACTS_PASS_054_V1"
}
```
