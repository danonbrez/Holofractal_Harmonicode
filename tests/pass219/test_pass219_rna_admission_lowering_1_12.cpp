#include "hhs_pass219_rna_admission_lowering_1_12.hpp"

#include <cassert>
#include <cstdint>
#include <cstring>
#include <type_traits>

template <class T, class = void>
struct has_commit_member : std::false_type {};

template <class T>
struct has_commit_member<T, std::void_t<decltype(&T::commit)>> : std::true_type {};

template <class T, class = void>
struct has_admit_member : std::false_type {};

template <class T>
struct has_admit_member<T, std::void_t<decltype(&T::admit)>> : std::true_type {};

int main() {
    using namespace hhs::rna;

    HHSExactPass219RNALineageV1 lineage{};
    HHSExactVM81Frame predecessor{};
    HHSExactVM81Frame target{};
    HHSExactVM81Frame reconstructed{};
    HHSExactVM81Frame rollback{};
    std::uint8_t frontier[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES]{};

    lineage.struct_size = static_cast<std::uint32_t>(sizeof(lineage));
    lineage.version = hhs_exact_pass219_rna_rule_version();
    assert(hhs_exact_pass219_native_phase_witness(
        HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &lineage.native_phase) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_coordinate_from_pass189(
        41U, 0, 1U, 0U, &lineage.coordinate) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_trinary_phase_gate(
        lineage.coordinate.trit, &lineage.trinary_gate) == HHS_EXACT_STATUS_OK);
    std::memset(lineage.predecessor_hash72, '0', HHS_EXACT_HASH72_LEN);
    lineage.predecessor_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    std::memset(lineage.predecessor_hash216_identity, '1', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    lineage.predecessor_hash216_identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    Domain a{10U, 20U, HHS_EXACT_PHASE_X, 0U, HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD};
    Domain b{20U, 10U, HHS_EXACT_PHASE_Y, 1U, HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN};
    Strand strand{7U};
    assert(strand.add(a) == HHS_EXACT_STATUS_OK);
    assert(strand.add(b) == HHS_EXACT_STATUS_OK);
    TranscriptionProgram program{112U};
    InhibitionGate inhibit{1U, 10U, 20U};
    assert(program.add(inhibit) == HHS_EXACT_STATUS_OK);
    TranscriptionWitness witness{strand, program, lineage};
    assert(witness.status() == HHS_EXACT_STATUS_OK);

    for (std::size_t i = 0; i < HHS_EXACT_VM81_CELLS; ++i) {
        predecessor.words[i] = UINT64_C(0x1111111100000000) ^ static_cast<std::uint64_t>(i);
        target.words[i] = UINT64_C(0x2222222200000000) ^ static_cast<std::uint64_t>(i);
    }
    for (std::size_t i = 0; i < sizeof(frontier); ++i)
        frontier[i] = static_cast<std::uint8_t>(i + 1U);

    AdmissionCandidate candidate{witness, predecessor, target, frontier};
    assert(candidate.status() == HHS_EXACT_STATUS_OK);
    assert(candidate.reconstruct(reconstructed) == HHS_EXACT_STATUS_OK);
    assert(std::memcmp(&reconstructed, &target, sizeof(target)) == 0);
    assert(candidate.rollback(rollback) == HHS_EXACT_STATUS_OK);
    assert(std::memcmp(&rollback, &predecessor, sizeof(predecessor)) == 0);
    assert(candidate.record().program_id == 112U);

    static_assert(!has_commit_member<AdmissionCandidate>::value,
                  "C++ candidate must not expose VM81 commit authority");
    static_assert(!has_admit_member<AdmissionCandidate>::value,
                  "C++ candidate must not expose VM81 admission authority");
    static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAAdmissionCandidateV1>);

    return 0;
}
