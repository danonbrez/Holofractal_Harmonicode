"""Read-only candidate checks for Hash72 nine-view address-preserving projections.

Existing I065 Hash72 geometry is authoritative.  This test deliberately does
NOT define a new HNAN phase rule, VM81 state transition, or Hash72 mint path.
Permutation ordering below is a test fixture only until bound to the native
ordered phase contract.  Nine views are projections, not nine source states.
"""
from __future__ import annotations

from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    HASH72_ALPHABET,
    HASH72_POSITIONS,
    hash72_vertex_geometry,
    compress_hash72_vertex_geometry,
)

ROOT_ROLES = ("sqrt(AB)", "sqrt(BA)", "P^2")
# Fixture ordering, NOT an authorization to rewrite native HNAN phases.
GROUP_PERMUTATIONS = ((0, 1, 2), (1, 2, 0), (2, 0, 1))


def test_existing_hash72_generator_hydration_recovers_exact_source():
    word = "".join(HASH72_ALPHABET)
    assert len(word) == HASH72_POSITIONS == 72
    vertices = hash72_vertex_geometry(word)
    assert len(vertices) == 5184
    assert compress_hash72_vertex_geometry(vertices) == word
    assert len({v["linear5184"] for v in vertices}) == 5184
    assert len({(v["vm81_cell"], v["local64"]) for v in vertices}) == 5184


def test_nine_projection_roles_retain_three_root_components():
    views = tuple(tuple(ROOT_ROLES[k] for k in perm) for perm in GROUP_PERMUTATIONS)
    assert len(views) == 3
    assert sum(len(group) for group in views) == 9
    assert all(set(group) == set(ROOT_ROLES) for group in views)
    assert all(len({group[i] for group in views}) == 3 for i in range(3))
    for group, permutation in zip(views, GROUP_PERMUTATIONS):
        inverse = tuple(permutation.index(i) for i in range(3))
        assert tuple(group[inverse[i]] for i in range(3)) == ROOT_ROLES


def test_every_projection_uses_same_native_address():
    word = "".join(HASH72_ALPHABET)
    vertices = hash72_vertex_geometry(word)
    for linear in (0, 1, 63, 64, 2591, 2592, 5183):
        vertex = vertices[linear]
        for permutation in GROUP_PERMUTATIONS:
            for phase_index in permutation:
                projected = (vertex["linear5184"], vertex["vm81_cell"],
                             vertex["local64"], ROOT_ROLES[phase_index])
                assert projected[:3] == (linear, vertex["vm81_cell"],
                                         vertex["local64"])


def test_scope_does_not_claim_native_hnan_closure():
    # This unit explicitly does not prove AB=-BA=P^4 or P^8.
    assert len(GROUP_PERMUTATIONS) == 3
