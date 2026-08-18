#include "hhs_pass219_rna_rule_grammar_1_11.hpp"

#include <cassert>
#include <cstring>

int main() {
    hhs::rna::Domain a(10U, 20U, HHS_EXACT_PHASE_X, 0U, HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD);
    hhs::rna::Domain b(20U, 10U, HHS_EXACT_PHASE_Y, 1U, HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN);
    assert(a.status() == HHS_EXACT_STATUS_OK);
    assert(b.status() == HHS_EXACT_STATUS_OK);

    hhs::rna::Strand strand(7U);
    assert(strand.add(a) == HHS_EXACT_STATUS_OK);
    assert(strand.add(b) == HHS_EXACT_STATUS_OK);

    hhs::rna::Complement complement(1U, 10U, 20U);
    hhs::rna::Binding binding(2U, 10U, 20U);
    hhs::rna::ToeholdGate toehold(3U, 10U, 20U);
    hhs::rna::ActivationGate activate(4U, 10U, 20U);
    hhs::rna::Cleavage cleavage(5U, 10U, 20U);
    hhs::rna::Release release(6U, 10U, 20U);
    hhs::rna::HairpinGate hairpin(7U, 20U, 10U);
    hhs::rna::InhibitionGate inhibit(8U, 10U, 20U);

    assert(complement.status() == HHS_EXACT_STATUS_OK);
    assert(binding.status() == HHS_EXACT_STATUS_OK);
    assert(toehold.status() == HHS_EXACT_STATUS_OK);
    assert(activate.status() == HHS_EXACT_STATUS_OK);
    assert(cleavage.status() == HHS_EXACT_STATUS_OK);
    assert(release.status() == HHS_EXACT_STATUS_OK);
    assert(hairpin.status() == HHS_EXACT_STATUS_OK);
    assert(inhibit.status() == HHS_EXACT_STATUS_OK);

    hhs::rna::TranscriptionProgram program(99U);
    assert(program.add(complement) == HHS_EXACT_STATUS_OK);
    assert(program.add(binding) == HHS_EXACT_STATUS_OK);
    assert(program.add(toehold) == HHS_EXACT_STATUS_OK);
    assert(program.add(activate) == HHS_EXACT_STATUS_OK);
    assert(program.add(cleavage) == HHS_EXACT_STATUS_OK);
    assert(program.add(release) == HHS_EXACT_STATUS_OK);

    HHSExactPass219RNALineageV1 lineage{};
    lineage.struct_size = static_cast<std::uint32_t>(sizeof(lineage));
    lineage.version = hhs_exact_pass219_rna_rule_version();
    assert(hhs_exact_pass219_native_phase_witness(
        HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &lineage.native_phase) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_trinary_phase_gate(0U, &lineage.trinary_gate) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_coordinate_from_pass189(
        0U, 0, 1U, 0U, &lineage.coordinate) == HHS_EXACT_STATUS_OK);
    std::memset(lineage.predecessor_hash72, '0', HHS_EXACT_HASH72_LEN);
    lineage.predecessor_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    std::memset(lineage.predecessor_hash216_identity, '1', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    lineage.predecessor_hash216_identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    hhs::rna::TranscriptionWitness witness(strand, program, lineage);
    assert(witness.status() == HHS_EXACT_STATUS_OK);
    assert(witness.record().executed_rule_count == 6U);
    assert((witness.record().after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_CLEAVED) != 0U);
    assert((witness.record().after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_RELEASED) != 0U);
    assert(witness.record().lineage.coordinate.slot5184 == lineage.coordinate.slot5184);

    hhs::rna::TranscriptionProgram hairpin_program(100U);
    assert(hairpin_program.add(hairpin) == HHS_EXACT_STATUS_OK);
    hhs::rna::TranscriptionWitness hairpin_witness(strand, hairpin_program, lineage);
    assert(hairpin_witness.status() == HHS_EXACT_STATUS_OK);
    assert((hairpin_witness.record().after[1].state_flags & HHS_EXACT_PASS219_RNA_STATE_FOLDED) != 0U);

    hhs::rna::TranscriptionProgram inhibit_program(101U);
    assert(inhibit_program.add(inhibit) == HHS_EXACT_STATUS_OK);
    hhs::rna::TranscriptionWitness inhibit_witness(strand, inhibit_program, lineage);
    assert(inhibit_witness.status() == HHS_EXACT_STATUS_OK);
    assert((inhibit_witness.record().after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_INHIBITED) != 0U);

    return 0;
}
