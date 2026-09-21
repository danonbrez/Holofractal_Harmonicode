#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static HHSExactBigUIntView one_byte(uint8_t *value) {
    HHSExactBigUIntView view;
    memset(&view, 0, sizeof(view));
    view.struct_size = sizeof(view);
    view.byte_length = 1U;
    view.bytes_be = value;
    return view;
}

static void make_input(
    HHSExactPass219Lane5TripartiteInputV1 *in,
    char state[5184],
    uint8_t *Gamma,
    uint8_t *Rho,
    uint8_t *Sigma,
    uint8_t *Omega,
    uint8_t *P,
    uint8_t *p,
    uint8_t *q
) {
    memset(in, 0, sizeof(*in));
    in->struct_size = sizeof(*in);
    in->version = HHS_EXACT_PASS219_LANE5_TRIPARTITE_VERSION;
    in->Gamma_macro = one_byte(Gamma);
    in->Rho_payload = one_byte(Rho);
    in->Sigma_2D = one_byte(Sigma);
    in->Omega_root = one_byte(Omega);
    in->P_macro = one_byte(P);
    in->p_ingress = one_byte(p);
    in->q_egress = one_byte(q);
    in->serialization_5184 = state;
    in->serialization_length = 5184U;
}

static void reset_receipt(HHSExactPass219Lane5TripartiteReceiptV1 *receipt) {
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = sizeof(*receipt);
}

int main(void) {
    HHSExactPass219Lane5TripartiteAuthorityV1 authority;
    HHSExactPass219Lane5TripartiteInputV1 in;
    HHSExactPass219Lane5TripartiteReceiptV1 receipt;
    static char state[5184];
    uint8_t Gamma = 5U, Rho = 7U, Sigma = 5U, Omega = 7U;
    uint8_t P = 2U, p = 1U, q = 3U;
    uint8_t zero = 0U;
    uint8_t six = 6U;
    uint8_t one = 1U, two = 2U;
    uint8_t malformed_bytes[2] = {0U, 2U};

    memset(state, '0', sizeof(state));

    memset(&authority, 0, sizeof(authority));
    authority.struct_size = sizeof(authority);
    CHECK(hhs_exact_pass219_lane5_tripartite_version() ==
          HHS_EXACT_PASS219_LANE5_TRIPARTITE_VERSION);
    CHECK(hhs_exact_pass219_lane5_tripartite_authority(&authority) ==
          HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.theorem_hhs_t5184_005 == 1U);
    CHECK(authority.vm81_cells == 81U);
    CHECK(authority.local_cell_width == 64U);
    CHECK(authority.serialization_characters == 5184U);
    CHECK(authority.ordered_curvature_surface_preserved == 1U);
    CHECK(authority.transition_surface_preserved == 1U);
    CHECK(authority.payload_delta_surface_preserved == 1U);
    CHECK(authority.exact_bigint_only == 1U);
    CHECK(authority.equality_by_cross_product == 1U);
    CHECK(authority.denominator_cancellation_allowed == 0U);
    CHECK(authority.division_by_zero_allowed == 0U);
    CHECK(authority.rna_cell_wall_required_downstream == 1U);
    CHECK(authority.pqc_witness_required_downstream == 1U);
    CHECK(authority.exact_cpu_vm81_replay_required_downstream == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_commit_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    /* Exact closure fixture:
       P=2,p=1,q=3 => P(q-p)/(p+q)=1 and P^2-pq=1.
       Gamma=Sigma=5, Rho=Omega=7 closes all supplied surfaces exactly. */
    make_input(&in, state, &Gamma, &Rho, &Sigma, &Omega, &P, &p, &q);
    reset_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_tripartite_verify(&in, &receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(receipt.reason == HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_NONE);
    CHECK(receipt.q_minus_p_sign == 1);
    CHECK(receipt.transition_coefficient_sign == 1);
    CHECK(receipt.serialization_width_verified == 1U);
    CHECK(receipt.omega_nonzero == 1U);
    CHECK(receipt.phase_denominator_nonzero == 1U);
    CHECK(receipt.curvature_surface_equal == 1U);
    CHECK(receipt.transition_surface_equal == 1U);
    CHECK(receipt.payload_surface_equal == 1U);
    CHECK(receipt.arithmetic_closure_delta_e_zero == 1U);
    CHECK(receipt.closure_valid == 1U);
    CHECK(receipt.candidate_only == 1U);
    CHECK(receipt.requires_rna_cell_wall == 1U);
    CHECK(receipt.requires_pqc_witness == 1U);
    CHECK(receipt.requires_exact_cpu_vm81_replay == 1U);
    CHECK(receipt.canonical_mutation_authority == 0U);
    CHECK(strlen(receipt.serialization_hash216) == 216U);
    CHECK(strlen(receipt.commit_hash216) == 216U);

    /* Sigma tamper must fail the ordered curvature surface first. */
    make_input(&in, state, &Gamma, &Rho, &six, &Omega, &P, &p, &q);
    reset_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_tripartite_verify(&in, &receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(receipt.closure_valid == 0U);
    CHECK(receipt.reason == HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_CURVATURE_MISMATCH);

    /* Omega/Delta is a non-cancellable denominator and zero fails closed. */
    make_input(&in, state, &Gamma, &Rho, &Sigma, &zero, &P, &p, &q);
    reset_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_tripartite_verify(&in, &receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(receipt.closure_valid == 0U);
    CHECK(receipt.reason == HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_DELTA_ZERO);

    /* p+q is the ordered curvature denominator.  Zero is rejected. */
    make_input(&in, state, &Gamma, &Rho, &Sigma, &Omega, &P, &zero, &zero);
    reset_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_tripartite_verify(&in, &receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(receipt.reason == HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_PHASE_DENOMINATOR_ZERO);

    /* Fixed-width 5184 binding is mandatory. */
    make_input(&in, state, &Gamma, &Rho, &Sigma, &Omega, &P, &p, &q);
    in.serialization_length = 5183U;
    reset_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_tripartite_verify(&in, &receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(receipt.reason == HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_SERIALIZATION_WIDTH);

    /* Signed transition and ordered q-p are preserved instead of underflowing. */
    make_input(&in, state, &Gamma, &Rho, &Sigma, &Omega, &one, &two, &two);
    reset_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_tripartite_verify(&in, &receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(receipt.q_minus_p_sign == 0);
    CHECK(receipt.transition_coefficient_sign == -1);
    CHECK(receipt.closure_valid == 0U);

    /* Non-canonical leading-zero BigUInt encoding is not admitted. */
    make_input(&in, state, &Gamma, &Rho, &Sigma, &Omega, &P, &p, &q);
    in.P_macro.struct_size = sizeof(in.P_macro);
    in.P_macro.byte_length = 2U;
    in.P_macro.bytes_be = malformed_bytes;
    reset_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_tripartite_verify(&in, &receipt) ==
          HHS_EXACT_STATUS_INVALID_ARGUMENT);

    puts("PASS219_LANE5_CLOAKED_TRIPARTITE_CONSTRAINT_1_61_PASS");
    return 0;
}
