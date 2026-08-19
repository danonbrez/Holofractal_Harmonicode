#include "hhs_pass219_inherited_pass210_1_16.h"

#include <assert.h>
#include <string.h>

static HHSExactPass210HFCWitnessV1 witness(void) {
    HHSExactPass210HFCWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass210_version();
    w.runtime_verified = 1U;
    w.register_len = 5184U;
    w.grid_lo_shu = 81U;
    w.line_bytes = 64U;
    w.snapshot_width = 288U;
    w.snapshot_stride = 144U;
    w.snapshot_count = 36U;
    w.section_phi_hi = 89U;
    w.section_phi_lo = 55U;
    w.matrix_dim = 12U;
    w.modality_count = 5U;
    w.required_operation_count = 11U;
    w.double_coverage_verified = 1U;
    w.single_snapshot_erasure_drills = 36U;
    w.corruption_localization_modalities = 5U;
    w.deterministic_replay_verified = 1U;
    w.strict_domain_boundary_preserved = 1U;
    w.digest_only_reversibility_forbidden = 1U;
    w.no_float_canonical_authority = 1U;
    w.pass211_inherits_pass210 = 1U;
    w.branch_validation_run = 30994827355ULL;
    w.main_validation_run = 30994901959ULL;
    strcpy(w.validated_branch_head, "0d1433d30f9fe811dc42a3155afeafa089aa72ff");
    strcpy(w.main_merge_head, "a8cd64e76828fd911e7e6e27ffd9ad02c7d74355");
    strcpy(w.contract_git_blob, "ac46a61f568b0443794f854cf84e5a3cfc1bf908");
    strcpy(w.restart_git_blob, "3dee1ac8eb16a9bd151514ddbc4490b51d6d1df8");
    strcpy(w.runtime_git_blob, "bb85330627cd58a1cb57ab47f3d5520d8b1157b1");
    strcpy(w.api_git_blob, "6569f8f689ab48aa4239e0e2214ec1d27485dd35");
    strcpy(w.evidence_git_blob, "221afe26a8d9fd5ddc475c60e2a516aad414d7cd");
    strcpy(w.validation_script_git_blob, "939cdc583f3f245282c80217fcc1b132d2471783");
    strcpy(w.pass211_contract_git_blob, "685c6d1544cbae6966e84c0d05b6bf4b8687d903");
    strcpy(w.pass211_runtime_git_blob, "0d11f3607c81b442b76dcd455b5c47450c9ed7e9");
    strcpy(w.reference_register_hash216, "8997ab0f9c3aaa3b0d158c2855788042c7904060cf51b6f020bec4b25400567b");
    strcpy(w.reference_register_sha256, "26232cd54a39e54a9bf9a71cdceebb92133c3787e218b15778783b9b0c16e8ea");
    strcpy(w.strict_register_hash216, "02d1610350a72bace2d05cdb6447d30bd6492dd53c1ae12ecfdce5fedae7b25f");
    strcpy(w.strict_domain_witness_hash216, "0832b78e97f63692ad0036d39395124139b563609e6e713a231642fdfcba6258");
    strcpy(w.strict_roundtrip_receipt_hash72, "y97qyS8z(ChXMN2/CcdgtDl0cjdipoB(4WVdHtMGucWqv25ALrFwcLVc7o1!N!6FVvoWc!Ky");
    strcpy(w.full_session_receipt_head_hash72, "7TBLHLh0!9wHuBvCLeNCGyitXUagjDP8colu+WxSD7(f?nR4wCqyf)Fgc+Ct22YWV6uS8yQk");
    return w;
}

int main(void) {
    HHSExactPass210HFCWitnessV1 w = witness();
    HHSExactPass219InheritedPass210BindingV1 b;
    assert(hhs_exact_pass219_bind_pass210_holographic_frame_compression(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 210U);
    assert(b.exact_frame_authority_bound == 1U);
    assert(b.double_witness_coverage_bound == 1U);
    assert(b.single_snapshot_recovery_bound == 1U);
    assert(b.multimodal_agreement_bound == 1U);
    assert(b.strict_compression_domain_bound == 1U);
    assert(b.digest_decode_boundary_bound == 1U);
    assert(b.pass211_successor_bound == 1U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);
    w.strict_domain_boundary_preserved = 0U;
    assert(hhs_exact_pass219_bind_pass210_holographic_frame_compression(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.reference_register_hash216[0] = '0';
    assert(hhs_exact_pass219_bind_pass210_holographic_frame_compression(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
