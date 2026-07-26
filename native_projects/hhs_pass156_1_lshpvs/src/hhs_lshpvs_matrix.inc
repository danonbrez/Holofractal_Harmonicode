static HHSLshpvsMatrix2 matrix_identity(void) {
    HHSLshpvsMatrix2 matrix;
    size_t row;
    size_t column;

    for (row = 0; row < 2; ++row) {
        for (column = 0; column < 2; ++column) {
            matrix.cell[row][column] = complex_zero();
        }
    }
    matrix.cell[0][0] = complex_one();
    matrix.cell[1][1] = complex_one();
    return matrix;
}

static HHSLshpvsStatus matrix_mul(
    const HHSLshpvsMatrix2 *a,
    const HHSLshpvsMatrix2 *b,
    HHSLshpvsMatrix2 *out
) {
    HHSLshpvsMatrix2 result;
    size_t row;
    size_t column;
    size_t lane;

    if (a == NULL || b == NULL || out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    for (row = 0; row < 2; ++row) {
        for (column = 0; column < 2; ++column) {
            result.cell[row][column] = complex_zero();
            for (lane = 0; lane < 2; ++lane) {
                HHSLshpvsComplex product;
                HHSLshpvsComplex sum;
                HHSLshpvsStatus status = complex_mul(
                    a->cell[row][lane],
                    b->cell[lane][column],
                    &product
                );
                if (status != HHS_LSHPVS_OK) {
                    return status;
                }
                status = complex_add(
                    result.cell[row][column],
                    product,
                    &sum
                );
                if (status != HHS_LSHPVS_OK) {
                    return status;
                }
                result.cell[row][column] = sum;
            }
        }
    }
    *out = result;
    return HHS_LSHPVS_OK;
}

static HHSLshpvsStatus matrix_vector_mul(
    const HHSLshpvsMatrix2 *matrix,
    const HHSLshpvsVector2 *vector,
    HHSLshpvsVector2 *out
) {
    HHSLshpvsVector2 result;
    size_t row;
    size_t lane;

    if (matrix == NULL || vector == NULL || out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    for (row = 0; row < 2; ++row) {
        result.cell[row] = complex_zero();
        for (lane = 0; lane < 2; ++lane) {
            HHSLshpvsComplex product;
            HHSLshpvsComplex sum;
            HHSLshpvsStatus status = complex_mul(
                matrix->cell[row][lane],
                vector->cell[lane],
                &product
            );
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
            status = complex_add(result.cell[row], product, &sum);
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
            result.cell[row] = sum;
        }
    }
    *out = result;
    return HHS_LSHPVS_OK;
}

static HHSLshpvsStatus matrix_inverse(
    const HHSLshpvsMatrix2 *matrix,
    HHSLshpvsMatrix2 *out
) {
    HHSLshpvsComplex ad;
    HHSLshpvsComplex bc;
    HHSLshpvsComplex determinant;
    HHSLshpvsComplex negative;
    HHSLshpvsMatrix2 result;
    HHSLshpvsStatus status;

    if (matrix == NULL || out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    status = complex_mul(matrix->cell[0][0], matrix->cell[1][1], &ad);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_mul(matrix->cell[0][1], matrix->cell[1][0], &bc);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_sub(ad, bc, &determinant);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    if (determinant.re.num == 0 && determinant.im.num == 0) {
        return HHS_LSHPVS_SINGULAR_PROPAGATOR;
    }

    status = complex_div(matrix->cell[1][1], determinant, &result.cell[0][0]);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_neg(matrix->cell[0][1], &negative);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_div(negative, determinant, &result.cell[0][1]);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_neg(matrix->cell[1][0], &negative);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_div(negative, determinant, &result.cell[1][0]);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_div(matrix->cell[0][0], determinant, &result.cell[1][1]);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    *out = result;
    return HHS_LSHPVS_OK;
}

static int matrix_equal(
    const HHSLshpvsMatrix2 *a,
    const HHSLshpvsMatrix2 *b
) {
    size_t row;
    size_t column;

    if (a == NULL || b == NULL) {
        return 0;
    }
    for (row = 0; row < 2; ++row) {
        for (column = 0; column < 2; ++column) {
            if (!complex_equal(a->cell[row][column], b->cell[row][column])) {
                return 0;
            }
        }
    }
    return 1;
}

static HHSLshpvsStatus matrix_pow(
    const HHSLshpvsMatrix2 *base,
    int64_t exponent,
    HHSLshpvsMatrix2 *out
) {
    HHSLshpvsMatrix2 factor;
    HHSLshpvsMatrix2 accumulator = matrix_identity();
    uint64_t remaining;

    if (base == NULL || out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    factor = *base;
    if (exponent < 0) {
        HHSLshpvsStatus status = matrix_inverse(base, &factor);
        if (status != HHS_LSHPVS_OK) {
            return status;
        }
        remaining = uabs64(exponent);
    } else {
        remaining = (uint64_t)exponent;
    }

    while (remaining != UINT64_C(0)) {
        if ((remaining & UINT64_C(1)) != UINT64_C(0)) {
            HHSLshpvsMatrix2 product;
            HHSLshpvsStatus status = matrix_mul(&accumulator, &factor, &product);
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
            accumulator = product;
        }
        remaining >>= 1U;
        if (remaining != UINT64_C(0)) {
            HHSLshpvsMatrix2 square;
            HHSLshpvsStatus status = matrix_mul(&factor, &factor, &square);
            if (status != HHS_LSHPVS_OK) {
                return status;
            }
            factor = square;
        }
    }
    *out = accumulator;
    return HHS_LSHPVS_OK;
}

static HHSLshpvsStatus vector_norm(
    const HHSLshpvsVector2 *vector,
    HHSLshpvsRational *out
) {
    HHSLshpvsRational total = {0, 1};
    size_t index;

    if (vector == NULL || out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    for (index = 0; index < 2; ++index) {
        HHSLshpvsRational real_square;
        HHSLshpvsRational imag_square;
        HHSLshpvsRational magnitude;
        HHSLshpvsRational next;
        HHSLshpvsStatus status = rat_mul(
            vector->cell[index].re,
            vector->cell[index].re,
            &real_square
        );
        if (status != HHS_LSHPVS_OK) {
            return status;
        }
        status = rat_mul(
            vector->cell[index].im,
            vector->cell[index].im,
            &imag_square
        );
        if (status != HHS_LSHPVS_OK) {
            return status;
        }
        status = rat_add(real_square, imag_square, &magnitude);
        if (status != HHS_LSHPVS_OK) {
            return status;
        }
        status = rat_add(total, magnitude, &next);
        if (status != HHS_LSHPVS_OK) {
            return status;
        }
        total = next;
    }
    *out = total;
    return HHS_LSHPVS_OK;
}
