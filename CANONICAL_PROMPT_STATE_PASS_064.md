# CANONICAL PROMPT STATE PASS 064

```json
{
  "authority": "HHS_PROMPT_RESPONSE_ALIGNMENT_AUTHORITY_V1",
  "authority_sources": [
    "CANONICAL_USER_FORMAL_STATE",
    "COMMITTED_RUNTIME_STATE"
  ],
  "declared_intent": [
    "PRESERVE_SOURCE_IDENTITY",
    "EXECUTE_THROUGH_CANONICAL_RUNTIME"
  ],
  "epistemic_states": [
    "CANONICAL",
    "DECLARED",
    "TYPED_AMBIGUOUS"
  ],
  "forbidden_substitutions": [
    "LINGUISTIC_RECONSTRUCTION_AS_OPERATOR_AUTHORITY"
  ],
  "formal_objects": [
    {
      "active": true,
      "relation": {
        "members": [
          "x",
          "y",
          "0",
          "1"
        ],
        "relation": "DISTINCT"
      },
      "relation_id": "relation:00",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "members": [
          "i",
          "x",
          "y",
          "xy",
          "yx"
        ],
        "relation": "DISTINCT"
      },
      "relation_id": "relation:01",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "expression": "xy = -yx",
        "lhs": "xy",
        "relation": "ORIENTED_ANTICOMMUTATION",
        "rhs": "-yx"
      },
      "relation_id": "relation:02",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "expression": "x = 1/y",
        "lhs": "x",
        "relation": "RECIPROCAL",
        "rhs": "1/y"
      },
      "relation_id": "relation:03",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "expression": "y = -x",
        "lhs": "y",
        "relation": "PHASE_INVERSE",
        "rhs": "-x"
      },
      "relation_id": "relation:04",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "frame": "LOCAL_PRODUCT_CLOSURE",
        "lhs": "xy",
        "relation": "NORMALIZED_UNIT",
        "rhs": "1"
      },
      "relation_id": "relation:05",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "frame": "RECIPROCAL_PRODUCT_CLOSURE",
        "lhs": "yx",
        "relation": "NORMALIZED_UNIT",
        "rhs": "1"
      },
      "relation_id": "relation:06",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "canonical_ratio": "I:I^3 = 1:-1",
        "lhs": [
          "x",
          "y"
        ],
        "relation": "ORIENTED_RATIO",
        "rhs": [
          "xy",
          "yx"
        ]
      },
      "relation_id": "relation:07",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "relation": "ZERO_SUM",
        "result": "0",
        "terms": [
          "x",
          "y",
          "xy",
          "yx"
        ]
      },
      "relation_id": "relation:08",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "lhs": "xyx",
        "relation": "BRAID",
        "rhs": "yxy"
      },
      "relation_id": "relation:09",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "members": [
          "X",
          "xy",
          "z"
        ],
        "relation": "ALIAS"
      },
      "relation_id": "relation:10",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "members": [
          "Y",
          "yx",
          "w"
        ],
        "relation": "ALIAS"
      },
      "relation_id": "relation:11",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "expression": "xyXY = xyzw = 1",
        "relation": "GLOBAL_PRODUCT_CLOSURE"
      },
      "relation_id": "relation:12",
      "source": "PASS_062_XYZW_ALGEBRA"
    },
    {
      "active": true,
      "relation": {
        "expression": "x + y - z - w = 0",
        "relation": "TOPOLOGICAL_BALANCE"
      },
      "relation_id": "relation:13",
      "source": "PASS_062_XYZW_ALGEBRA"
    }
  ],
  "invariants_to_preserve": [
    "SOURCE_IDENTITY",
    "TYPED_EQUALITY",
    "EPISTEMIC_STATUS",
    "AUTHORITY_BOUNDARY",
    "PROVENANCE"
  ],
  "prompt_elements": [
    {
      "element_id": "prompt:source",
      "kind": "SOURCE_IDENTITY",
      "material": true,
      "value": "vn8i<i7HYX7!5nlzbkIUi//3)?/jfJi5v(MihqnH(N)<!hHrQb-p-V0yGw>>om-e3ej)mn9A"
    },
    {
      "element_id": "prompt:intent",
      "kind": "DECLARED_INTENT",
      "material": true,
      "value": "PRESERVE_AND_APPLY_CANONICAL_FORMAL_SYSTEM"
    },
    {
      "element_id": "prompt:typed-relations",
      "kind": "INVARIANT",
      "material": true,
      "value": "TYPED_RELATION_TOPOLOGY"
    },
    {
      "element_id": "prompt:ambiguity",
      "kind": "TYPED_AMBIGUITY",
      "material": true,
      "value": "PRESERVE_UNRESOLVED_SCOPE"
    }
  ],
  "prompt_state_root_hash72": "mlatRM86GecgD<MeC9H9uh<im2biADFOOZgJDUMJFTF?i!D+/PpfR7swNX9K5wtH5uau)Pfx",
  "schema": "HHS_CANONICAL_PROMPT_STATE_V1",
  "source_commitment_root_hash72": "+pHwHDq0W6n-ANJG9)p?EZFCyNqZq?0L3jdDk!owh6o(/u(Bvh9D-hBxx?zwTS64Z/D*-(cH",
  "typed_ambiguities": [
    "LOCAL_OPERATOR_SCOPE_REMAINS_TYPED"
  ],
  "version": "PASS_064_RECIPROCAL_PROMPT_RESPONSE_ALIGNMENT_AGENT_V1"
}
```
