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

static HHSExactBigUIntView view(uint8_t *bytes, uint32_t length) {
    HHSExactBigUIntView v;
    memset(&v, 0, sizeof(v));
    v.struct_size = sizeof(v);
    v.byte_length = length;
    v.bytes_be = bytes;
    return v;
}

static void init_input(
    HHSExactPass219Lane5TripartiteInputV1 *in,
    HHSExactBigUIntView gamma,
    HHSExactBigUIntView rho,
    HHSExactBigUIntView sigma,
    HHSExactBigUIntView omega,
    HHSExactBigUIntView P,
    HHSExactBigUIntView p,
    HHSExactBigUIntView q,
    const char *state
) {
    memset(in, 0, sizeof(*in));
    in->struct_size = sizeof(*in);
    in->version = HHS_EXACT_PASS219_LANE5_TRIPARTITE_VERSION;
    in->Gamma_macro = gamma;
    in->Rho_payload = rho;
    in->Sigma_2D = sigma;
    in->Omega_root = omega;
    in->P_macro = P;
    in->p_ingress = p;
    in->q_egress = q;
    in->serialization_5184 = state;
    in->serialization_length = 5184U;
}

static int verify(
    HHSExactPass219Lane5TripartiteInputV1 *in,
    HHSExactPass219Lane5TripartiteReceiptV1 *out
) {
    memset(out, 0, sizeof(*out));
    out->struct_size = sizeof(*out);
    return (int)hhs_exact_pass219_lane5_tripartite_verify(in, out);
}

int main(void) {
    static char state[5184];
    HHSExactPass219Lane5TripartiteInputV1 in;
    HHSExactPass219Lane5TripartiteReceiptV1 receipt;
    uint32_t valid_cases = 0U;
    uint32_t tamper_cases = 0U;
    uint32_t signed_reject_cases = 0U;
    uint32_t n;
    uint8_t gamma;
    uint8_t rho;

    /* Family:
       P=n, p=n-1, q=n+1 => P^2-pq=1 and P(q-p)=p+q.
       With Sigma=Gamma and Omega=Rho, all three exact surfaces close. */
    for (n = 2U; n <= 200U; ++n) {
        uint8_t P = (uint8_t)n;
        uint8_t p = (uint8_t)(n - 1U);
        uint8_t q = (uint8_t)(n + 1U);
        memset(state, (int)('0' + (n % 10U)), sizeof(state));

        for (gamma = 1U; gamma <= 4U; ++gamma) {
            for (rho = 1U; rho <= 4U; ++rho) {
                uint8_t sigma = gamma;
                uint8_t omega = rho;
                init_input(
                    &in,
                    view(&gamma, 1U), view(&rho, 1U),
                    view(&sigma, 1U), view(&omega, 1U),
                    view(&P, 1U), view(&p, 1U), view(&q, 1U),
                    state
                );
                CHECK(verify(&in, &receipt) == HHS_EXACT_STATUS_OK);
                CHECK(receipt.closure_valid == 1U);
                CHECK(receipt.arithmetic_closure_delta_e_zero == 1U);
                CHECK(receipt.curvature_surface_equal == 1U);
                CHECK(receipt.transition_surface_equal == 1U);
                CHECK(receipt.payload_surface_equal == 1U);
                CHECK(receipt.q_minus_p_sign == 1);
                CHECK(receipt.transition_coefficient_sign == 1);
                ++valid_cases;
            }
        }

        {
            uint8_t gamma1 = 1U, rho1 = 1U, sigma_bad = 2U, omega1 = 1U;
            init_input(
                &in,
                view(&gamma1, 1U), view(&rho1, 1U),
                view(&sigma_bad, 1U), view(&omega1, 1U),
                view(&P, 1U), view(&p, 1U), view(&q, 1U),
                state
            );
            CHECK(verify(&in, &receipt) == HHS_EXACT_STATUS_OK);
            CHECK(receipt.closure_valid == 0U);
            CHECK(receipt.reason == HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_CURVATURE_MISMATCH);
            ++tamper_cases;
        }

        {
            uint8_t p_reverse = (uint8_t)(n + 1U);
            uint8_t q_reverse = (uint8_t)(n - 1U);
            uint8_t gamma1 = 1U, rho1 = 1U, sigma1 = 1U, omega1 = 1U;
            init_input(
                &in,
                view(&gamma1, 1U), view(&rho1, 1U),
                view(&sigma1, 1U), view(&omega1, 1U),
                view(&P, 1U), view(&p_reverse, 1U), view(&q_reverse, 1U),
                state
            );
            CHECK(verify(&in, &receipt) == HHS_EXACT_STATUS_OK);
            CHECK(receipt.q_minus_p_sign == -1);
            CHECK(receipt.transition_coefficient_sign == 1);
            CHECK(receipt.closure_valid == 0U);
            ++signed_reject_cases;
        }
    }

    /* Maximum-width exact BigUInt boundary:
       P=2^(8*647), p=P-1, q=P+1.  This preserves the same T=1 family while
       exercising the full 648-byte admitted input width and derived products. */
    {
        uint8_t P[648], p[647], q[648];
        uint8_t gamma1 = 3U, rho1 = 5U, sigma1 = 3U, omega1 = 5U;
        memset(P, 0, sizeof(P));
        memset(p, 0xff, sizeof(p));
        memset(q, 0, sizeof(q));
        P[0] = 1U;
        q[0] = 1U;
        q[647] = 1U;
        memset(state, 'M', sizeof(state));

        init_input(
            &in,
            view(&gamma1, 1U), view(&rho1, 1U),
            view(&sigma1, 1U), view(&omega1, 1U),
            view(P, (uint32_t)sizeof(P)),
            view(p, (uint32_t)sizeof(p)),
            view(q, (uint32_t)sizeof(q)),
            state
        );
        CHECK(verify(&in, &receipt) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.closure_valid == 1U);
        CHECK(receipt.arithmetic_closure_delta_e_zero == 1U);
        CHECK(receipt.q_minus_p_sign == 1);
        CHECK(receipt.transition_coefficient_sign == 1);
        CHECK(strlen(receipt.commit_hash216) == 216U);
        ++valid_cases;
    }

    CHECK(valid_cases == 3185U);
    CHECK(tamper_cases == 199U);
    CHECK(signed_reject_cases == 199U);

    printf(
        "PASS219_LANE5_CLOAKED_TRIPARTITE_STRESS_1_61_PASS "
        "valid=%u tamper=%u signed_reject=%u total=%u max_bigint_bytes=648\n",
        valid_cases, tamper_cases, signed_reject_cases,
        valid_cases + tamper_cases + signed_reject_cases
    );
    return 0;
}
