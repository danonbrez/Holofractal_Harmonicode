"""Dependency-scoped P generative query-weight witness tests."""
from copy import deepcopy
import pytest

from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    SCHEMA, HASH72_ALPHABET, Pass220HolographicQueryError, _root,
    hydrate_p_query_weight_witness,
)


def _parent():
    data = {
        "schema": SCHEMA,
        "hash216": HASH72_ALPHABET * 3,
        "serialized_root_sha256": "a" * 64,
        "candidate_only": True,
        "hash216_commit_authority": False,
    }
    data["record_root_sha256"] = _root(data)
    return data


def test_first_query_p_identity_repeatable_and_address_sensitive():
    parent = _parent()
    args = dict(p_source="P⁴:pq:(q-p)", p_address=72,
                ordered_relations=["qp", "p-q", "P⁴"], query_weights=[2, 3, 5])
    first = hydrate_p_query_weight_witness(parent, **args)
    assert first == hydrate_p_query_weight_witness(parent, **args)
    assert first["total_query_weight"] == 10
    assert first["weighted_relations"][1]["ordered_relation"] == "p-q"
    assert first["hash216_minted"] is False
    assert first["materialized_in_vector_store"] is False
    reversed_address = hydrate_p_query_weight_witness(parent, **{**args, "p_address": 73})
    assert first["p_identity_sha256"] != reversed_address["p_identity_sha256"]


def test_first_query_rejects_tampering_and_nonexact_weights():
    parent = _parent()
    kwargs = dict(p_source="P", p_address=0, ordered_relations=["pq"], query_weights=[1])
    modified = deepcopy(parent)
    modified["serialized_root_sha256"] = "b" * 64
    with pytest.raises(Pass220HolographicQueryError, match="root mismatch"):
        hydrate_p_query_weight_witness(modified, **kwargs)
    for invalid in (True, 1.5, -1):
        with pytest.raises(Pass220HolographicQueryError):
            hydrate_p_query_weight_witness(parent, **{**kwargs, "query_weights": [invalid]})
    with pytest.raises(Pass220HolographicQueryError):
        hydrate_p_query_weight_witness(parent, **{**kwargs, "p_address": 5184})
