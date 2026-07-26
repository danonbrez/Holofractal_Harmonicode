HHSLshpvsStatus hhs_lshpvs_rotation_decompose(
    int64_t n,
    int64_t modulus,
    int64_t *quotient,
    int64_t *residue
) {
    int64_t q;
    int64_t r;

    if (quotient == NULL || residue == NULL || modulus <= 0) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    q = n / modulus;
    r = n % modulus;
    if (r < 0) {
        --q;
        r += modulus;
    }
    *quotient = q;
    *residue = r;
    return HHS_LSHPVS_OK;
}

static int text_is_canonical(const char *text) {
    const unsigned char *cursor = (const unsigned char *)text;

    if (text == NULL || text[0] == '\0') {
        return 0;
    }
    while (*cursor != 0U) {
        if (*cursor < 0x20U || *cursor == (unsigned char)'"' ||
            *cursor == (unsigned char)'\\') {
            return 0;
        }
        ++cursor;
    }
    return 1;
}

static void hash216_text(
    const char *domain,
    const char *payload,
    char out[HHS_LSHPVS_HASH216_STRLEN]
) {
    char buffer[8192];
    const int count = snprintf(
        buffer,
        sizeof(buffer),
        "%s\n%s",
        domain,
        payload == NULL ? "" : payload
    );
    size_t length;
    HHSHash216 hash;

    if (count < 0) {
        out[0] = '\0';
        return;
    }
    length = (size_t)count;
    if (length >= sizeof(buffer)) {
        length = sizeof(buffer) - 1U;
    }
    hhs_hash216_compute(buffer, length, &hash);
    memcpy(out, hash.value, HHS_LSHPVS_HASH216_STRLEN);
}

static HHSLshpvsStatus canonical_core(
    const HHSLshpvsEntry *entry,
    char *out,
    size_t out_size
) {
    int count;

    if (entry == NULL || out == NULL || out_size == 0U) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    if (!text_is_canonical(entry->index.contract_root_hash216) ||
        !text_is_canonical(entry->index.fold_path) ||
        !text_is_canonical(entry->source_expression_root_hash216) ||
        !text_is_canonical(entry->membrane_root_hash216)) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }

    count = snprintf(
        out,
        out_size,
        "root=%s|path=%s|depth=%" PRIu32
        "|M=%" PRId64 "|n=%" PRId64 "|q=%" PRId64 "|r=%" PRId64
        "|sector=%" PRId32 "|version=%" PRIu64
        "|h00=%" PRId64 "/%" PRId64
        "|h01=%" PRId64 "/%" PRId64 "+i%" PRId64 "/%" PRId64
        "|h11=%" PRId64 "/%" PRId64
        "|dt=%" PRId64 "/%" PRId64
        "|hbar=%" PRId64 "/%" PRId64
        "|state0=%" PRId64 "/%" PRId64 "+i%" PRId64 "/%" PRId64
        "|state1=%" PRId64 "/%" PRId64 "+i%" PRId64 "/%" PRId64
        "|source=%s|membrane=%s",
        entry->index.contract_root_hash216,
        entry->index.fold_path,
        entry->index.nesting_depth,
        entry->index.modulus_M,
        entry->index.full_rotation_n,
        entry->index.overflow_quotient_q,
        entry->index.local_residue_r,
        entry->index.orientation_sector,
        entry->index.version,
        entry->parameters.h00.num,
        entry->parameters.h00.den,
        entry->parameters.h01.re.num,
        entry->parameters.h01.re.den,
        entry->parameters.h01.im.num,
        entry->parameters.h01.im.den,
        entry->parameters.h11.num,
        entry->parameters.h11.den,
        entry->parameters.delta_tau.num,
        entry->parameters.delta_tau.den,
        entry->parameters.hbar.num,
        entry->parameters.hbar.den,
        entry->pre_state.cell[0].re.num,
        entry->pre_state.cell[0].re.den,
        entry->pre_state.cell[0].im.num,
        entry->pre_state.cell[0].im.den,
        entry->pre_state.cell[1].re.num,
        entry->pre_state.cell[1].re.den,
        entry->pre_state.cell[1].im.num,
        entry->pre_state.cell[1].im.den,
        entry->source_expression_root_hash216,
        entry->membrane_root_hash216
    );
    if (count < 0 || (size_t)count >= out_size) {
        return HHS_LSHPVS_SERIALIZATION_BOUNDED;
    }
    return HHS_LSHPVS_OK;
}

HHSLshpvsStatus hhs_lshpvs_entry_prepare(HHSLshpvsEntry *entry) {
    HHSLshpvsComplex conjugate;
    HHSLshpvsStatus status;
    char canonical[4096];
    size_t index;

    if (entry == NULL || entry->index.modulus_M <= 0 ||
        entry->index.fold_path[0] == '\0' || entry->index.version == 0U) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }

    status = hhs_lshpvs_rotation_decompose(
        entry->index.full_rotation_n,
        entry->index.modulus_M,
        &entry->index.overflow_quotient_q,
        &entry->index.local_residue_r
    );
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_normalize(&entry->parameters.h00);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_normalize(&entry->parameters.h01);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_normalize(&entry->parameters.h11);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_normalize(&entry->parameters.delta_tau);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_normalize(&entry->parameters.hbar);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    if (entry->parameters.hbar.num == 0) {
        return HHS_LSHPVS_DIVIDE_BY_ZERO;
    }
    for (index = 0; index < 2; ++index) {
        status = complex_normalize(&entry->pre_state.cell[index]);
        if (status != HHS_LSHPVS_OK) {
            return status;
        }
    }

    entry->hamiltonian.cell[0][0] = (HHSLshpvsComplex){
        entry->parameters.h00,
        {0, 1}
    };
    entry->hamiltonian.cell[0][1] = entry->parameters.h01;
    status = complex_conjugate(entry->parameters.h01, &conjugate);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    entry->hamiltonian.cell[1][0] = conjugate;
    entry->hamiltonian.cell[1][1] = (HHSLshpvsComplex){
        entry->parameters.h11,
        {0, 1}
    };

    entry->hermitian_verified = (uint8_t)(
        entry->hamiltonian.cell[0][0].im.num == 0 &&
        entry->hamiltonian.cell[1][1].im.num == 0 &&
        complex_equal(entry->hamiltonian.cell[1][0], conjugate)
    );
    if (entry->hermitian_verified == 0U) {
        return HHS_LSHPVS_NON_HERMITIAN;
    }

    status = canonical_core(entry, canonical, sizeof(canonical));
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    hash216_text(DOMAIN_ENTRY, canonical, entry->key_hash216);
    return HHS_LSHPVS_OK;
}

static HHSLshpvsStatus build_cayley(
    const HHSLshpvsEntry *entry,
    HHSLshpvsMatrix2 *out
) {
    HHSLshpvsRational two = {2, 1};
    HHSLshpvsRational denominator;
    HHSLshpvsRational scale;
    HHSLshpvsMatrix2 left = matrix_identity();
    HHSLshpvsMatrix2 right = matrix_identity();
    HHSLshpvsMatrix2 inverse;
    HHSLshpvsStatus status;
    size_t row;
    size_t column;

    status = rat_mul(two, entry->parameters.hbar, &denominator);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_div(entry->parameters.delta_tau, denominator, &scale);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }

    for (row = 0; row < 2; ++row) {
        for (column = 0; column < 2; ++column) {
            HHSLshpvsComplex i_scaled_h = complex_zero();
            HHSLshpvsRational negative_imag;

            status = rat_mul(
                entry->hamiltonian.cell[row][column].re,
                scale,
                &i_scaled_h.im
            );
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
            status = rat_neg(
                entry->hamiltonian.cell[row][column].im,
                &negative_imag
            );
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
            status = rat_mul(negative_imag, scale, &i_scaled_h.re);
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
            status = complex_sub(
                left.cell[row][column],
                i_scaled_h,
                &left.cell[row][column]
            );
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
            status = complex_add(
                right.cell[row][column],
                i_scaled_h,
                &right.cell[row][column]
            );
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
        }
    }

    status = matrix_inverse(&left, &inverse);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return matrix_mul(&inverse, &right, out);
}

HHSLshpvsStatus hhs_lshpvs_entry_execute(HHSLshpvsEntry *entry) {
    HHSLshpvsRational norm_before;
    HHSLshpvsRational norm_after;
    HHSLshpvsMatrix2 winding_power;
    HHSLshpvsMatrix2 residue_power;
    HHSLshpvsMatrix2 direct_power;
    HHSLshpvsStatus status;
    char state[4096];
    size_t used;
    int appended;

    if (entry == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    status = hhs_lshpvs_entry_prepare(entry);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = build_cayley(entry, &entry->propagator);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = matrix_vector_mul(
        &entry->propagator,
        &entry->pre_state,
        &entry->post_state
    );
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = vector_norm(&entry->pre_state, &norm_before);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = vector_norm(&entry->post_state, &norm_after);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    entry->norm_verified = (uint8_t)rat_equal(norm_before, norm_after);
    if (entry->norm_verified == 0U) {
        return HHS_LSHPVS_NORM_MISMATCH;
    }

    status = matrix_pow(
        &entry->propagator,
        entry->index.modulus_M,
        &entry->winding
    );
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = matrix_pow(
        &entry->winding,
        entry->index.overflow_quotient_q,
        &winding_power
    );
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = matrix_pow(
        &entry->propagator,
        entry->index.local_residue_r,
        &residue_power
    );
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = matrix_mul(
        &winding_power,
        &residue_power,
        &entry->reconstructed_rotation
    );
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = matrix_pow(
        &entry->propagator,
        entry->index.full_rotation_n,
        &direct_power
    );
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    entry->rotation_reconstruction_verified = (uint8_t)matrix_equal(
        &direct_power,
        &entry->reconstructed_rotation
    );
    if (entry->rotation_reconstruction_verified == 0U) {
        return HHS_LSHPVS_ROTATION_RECONSTRUCTION_MISMATCH;
    }

    status = canonical_core(entry, state, sizeof(state));
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    used = strlen(state);
    appended = snprintf(
        state + used,
        sizeof(state) - used,
        "|post=%" PRId64 "/%" PRId64 "+i%" PRId64 "/%" PRId64
        ",%" PRId64 "/%" PRId64 "+i%" PRId64 "/%" PRId64,
        entry->post_state.cell[0].re.num,
        entry->post_state.cell[0].re.den,
        entry->post_state.cell[0].im.num,
        entry->post_state.cell[0].im.den,
        entry->post_state.cell[1].re.num,
        entry->post_state.cell[1].re.den,
        entry->post_state.cell[1].im.num,
        entry->post_state.cell[1].im.den
    );
    if (appended < 0 || (size_t)appended >= sizeof(state) - used) {
        return HHS_LSHPVS_SERIALIZATION_BOUNDED;
    }
    hash216_text(DOMAIN_STATE, state, entry->state_hash216);
    return HHS_LSHPVS_OK;
}
