#include "../../hhs_runtime/include/hhs_pass219b_phase_quantized_hydration_1_0.hpp"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>

int main() {
    HHSExactPass219HydrationCoordinateV1 parent{};
    auto status = hhs_exact_pass219_coordinate_from_pass189(3U, -7, 21U, 99U, &parent);
    assert(status == HHS_EXACT_STATUS_OK);

    hhs::pass219b::PhaseCell cell(parent, 23U);
    assert(cell.status() == HHS_EXACT_STATUS_OK);
    assert(cell.origin() == 23U);
    assert(cell.center_closure_preserved());
    assert(!cell.authoritative());

    auto x = cell.outer(0U);
    auto w = cell.outer(1U);
    auto yx = cell.outer(2U);
    auto zw = cell.outer(3U);
    auto y = cell.outer(4U);
    auto z = cell.outer(5U);
    auto xy = cell.outer(6U);
    auto wz = cell.outer(7U);

    assert(x.valid() && w.valid() && yx.valid() && zw.valid());
    assert(y.valid() && z.valid() && xy.valid() && wz.valid());
    assert(x.ring() == HHS_EXACT_PASS219B_RING_XY);
    assert(w.ring() == HHS_EXACT_PASS219B_RING_ZW);
    assert(x.rotation_family() == HHS_EXACT_PASS219B_ROTATION_I);
    assert(w.rotation_family() == HHS_EXACT_PASS219B_ROTATION_I2);
    assert(x.direction() == 1);
    assert(w.direction() == -1);
    assert(yx.phase_position() == 24U);
    assert(zw.phase_position() == 22U);
    assert(y.phase_position() == 25U);
    assert(z.phase_position() == 21U);
    assert(xy.phase_position() == 26U);
    assert(wz.phase_position() == 20U);

    hhs::pass219b::ExpansionPlan local_plan(1U, 81U);
    assert(local_plan.status() == HHS_EXACT_STATUS_OK);
    assert(local_plan.required_cells() == 81U);
    assert(local_plan.full_projection_cells() == 4183503552ULL);
    assert(!local_plan.requires_full_materialization());

    hhs::pass219b::ExpansionPlan surface_plan(5184U, 81U);
    assert(surface_plan.status() == HHS_EXACT_STATUS_OK);
    assert(surface_plan.required_cells() == 419904U);

    std::array<HHSExactPass219BPhaseCellV1, 5> selected{};
    std::size_t count = 0U;
    status = hhs::pass219b::expand_selected(
        &parent, 1U, 11U, 5U, selected.data(), selected.size(), &count);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(count == selected.size());
    for (std::size_t i = 0U; i < selected.size(); ++i) {
        assert(selected[i].phase_origin81 == static_cast<std::uint8_t>(11U + i));
        assert(selected[i].canonical_mutation_authority == 0U);
        assert(selected[i].canonical_persistence_authority == 0U);
        assert(selected[i].canonical_hash72_authority == 0U);
    }

    count = 0U;
    status = hhs::pass219b::expand_selected(
        &parent, 1U, 79U, 3U, selected.data(), selected.size(), &count);
    assert(status == HHS_EXACT_STATUS_RANGE_ERROR);

    return 0;
}
