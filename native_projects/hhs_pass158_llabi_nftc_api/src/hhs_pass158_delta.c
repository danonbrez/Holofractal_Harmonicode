#include "hhs_pass158_internal.h"

#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int64_t numerator;
    int64_t denominator;
} HHS158Fraction;

static int64_t gcd64(int64_t a, int64_t b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) { int64_t next = a % b; a = b; b = next; }
    return a ? a : 1;
}

static HHS158Status fraction_reduce(HHS158Fraction *value) {
    int64_t divisor;
    if (!value || value->denominator == 0) return HHS158_DELTA_REFERENCE_NONINVERTIBLE;
    if (value->denominator < 0) {
        if (value->numerator == INT64_MIN || value->denominator == INT64_MIN) return HHS158_INTEGER_WIDTH_TRUNCATION;
        value->numerator = -value->numerator;
        value->denominator = -value->denominator;
    }
    divisor = gcd64(value->numerator, value->denominator);
    value->numerator /= divisor;
    value->denominator /= divisor;
    return HHS158_OK;
}

static HHS158Status parse_fraction_span(HHS158ByteSpan span, HHS158Fraction *out) {
    char text[256];
    char *slash;
    char *dot;
    char *end;
    long long numerator;
    long long denominator = 1;
    size_t fraction_digits;
    size_t i;
    if (!out || !span.data || span.size == 0u || span.size >= sizeof(text)) return HHS158_TYPE_MISMATCH;
    memcpy(text, span.data, span.size);
    text[span.size] = '\0';
    if (strcmp(text, "nan") == 0 || strcmp(text, "NaN") == 0 || strcmp(text, "inf") == 0 || strcmp(text, "Infinity") == 0 || strcmp(text, "-Infinity") == 0) return HHS158_NONFINITE_PROJECTION;
    slash = strchr(text, '/');
    dot = strchr(text, '.');
    if (slash && dot) return HHS158_TYPE_MISMATCH;
    if (slash) {
        *slash = '\0';
        numerator = strtoll(text, &end, 10);
        if (*end != '\0') return HHS158_TYPE_MISMATCH;
        denominator = strtoll(slash + 1, &end, 10);
        if (*end != '\0' || denominator == 0) return HHS158_DELTA_REFERENCE_NONINVERTIBLE;
    } else if (dot) {
        int negative = text[0] == '-';
        char digits[256];
        size_t before = (size_t)(dot - text);
        size_t after = strlen(dot + 1);
        size_t offset = 0u;
        if (after > 9u) return HHS158_EXACT_VALUE_LOSS;
        if (negative) { digits[offset++] = '-'; }
        for (i = negative ? 1u : 0u; i < before; ++i) digits[offset++] = text[i];
        for (i = 0u; i < after; ++i) digits[offset++] = dot[1u + i];
        digits[offset] = '\0';
        numerator = strtoll(digits, &end, 10);
        if (*end != '\0') return HHS158_TYPE_MISMATCH;
        fraction_digits = after;
        denominator = 1;
        for (i = 0; i < fraction_digits; ++i) denominator *= 10;
    } else {
        numerator = strtoll(text, &end, 10);
        if (*end != '\0') return HHS158_TYPE_MISMATCH;
    }
    if (numerator > 1000000000LL || numerator < -1000000000LL || denominator > 1000000000LL || denominator < -1000000000LL) return HHS158_INTEGER_WIDTH_TRUNCATION;
    out->numerator = (int64_t)numerator;
    out->denominator = (int64_t)denominator;
    return fraction_reduce(out);
}

static HHS158Status fraction_mul(HHS158Fraction left, HHS158Fraction right, HHS158Fraction *out) {
    if (!out) return HHS158_INVALID_ARGUMENT;
    if (llabs(left.numerator) > 1000000000LL || llabs(left.denominator) > 1000000000LL ||
        llabs(right.numerator) > 1000000000LL || llabs(right.denominator) > 1000000000LL) return HHS158_INTEGER_WIDTH_TRUNCATION;
    out->numerator = left.numerator * right.numerator;
    out->denominator = left.denominator * right.denominator;
    return fraction_reduce(out);
}

static HHS158Status fraction_sub(HHS158Fraction left, HHS158Fraction right, HHS158Fraction *out) {
    if (!out) return HHS158_INVALID_ARGUMENT;
    if (llabs(left.numerator) > 1000000000LL || llabs(left.denominator) > 1000000000LL ||
        llabs(right.numerator) > 1000000000LL || llabs(right.denominator) > 1000000000LL) return HHS158_INTEGER_WIDTH_TRUNCATION;
    out->numerator = left.numerator * right.denominator - right.numerator * left.denominator;
    out->denominator = left.denominator * right.denominator;
    return fraction_reduce(out);
}

static HHS158Status fraction_div(HHS158Fraction left, HHS158Fraction right, HHS158Fraction *out) {
    HHS158Fraction reciprocal;
    if (right.numerator == 0) return HHS158_DELTA_REFERENCE_NONINVERTIBLE;
    reciprocal.numerator = right.denominator;
    reciprocal.denominator = right.numerator;
    return fraction_mul(left, reciprocal, out);
}

static int instance_valid(const HHS158Instance *instance) {
    return instance && instance->magic == HHS158_INSTANCE_MAGIC && !instance->released && instance->context &&
        instance->context->magic == HHS158_CONTEXT_MAGIC && !instance->context->released;
}

HHS158Status hhs158_instance_project(HHS158Instance *instance, const HHS158ProjectionProfile *profile,
    HHS158Value *out_projection, HHS158Receipt **out_receipt) {
    HHS158Status status;
    const uint8_t *payload;
    size_t payload_size;
    char projected[128];
    HHS158Fraction fraction;
    size_t i;
    if (!out_projection || !out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_receipt = NULL;
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    if (!profile || !hhs158_header_valid(&profile->header, sizeof(*profile))) return HHS158_STRUCT_SIZE_INVALID;
    if (profile->kind == HHS158_PROJECTION_EXACT_REFERENCE) {
        payload = (const uint8_t *)instance->current_state_root;
        payload_size = HHS158_HASH216_LENGTH;
        status = hhs158_value_set(out_projection, HHS158_VALUE_STATE_ROOT,
            HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE, payload, payload_size);
    } else if (profile->kind == HHS158_PROJECTION_IEEE754_BINARY64_CONTROL || profile->kind == HHS158_PROJECTION_RENDER_FLOAT32) {
        int found = 0;
        double value = 0.0;
        for (i = 0; i < instance->binding_count; ++i) {
            if (instance->bindings[i].kind == HHS158_VALUE_RATIONAL) {
                HHS158ByteSpan span = {instance->bindings[i].payload, instance->bindings[i].payload_size};
                status = parse_fraction_span(span, &fraction);
                if (status != HHS158_OK) return status;
                value = (double)fraction.numerator / (double)fraction.denominator;
                found = 1;
                break;
            }
        }
        if (!found) value = 0.0;
        if (!isfinite(value)) return HHS158_NONFINITE_PROJECTION;
        {
            int written = snprintf(projected, sizeof(projected), profile->kind == HHS158_PROJECTION_RENDER_FLOAT32 ? "%.9g" : "%.17g", value);
            if (written < 0 || (size_t)written >= sizeof(projected)) return HHS158_OUTPUT_BOUND;
            status = hhs158_value_set(out_projection, HHS158_VALUE_EXPRESSION,
                HHS158_FLAG_PROJECTION | HHS158_FLAG_APPROXIMATE | HHS158_FLAG_IMMUTABLE,
                (const uint8_t *)projected, (size_t)written);
        }
    } else return HHS158_TYPE_MISMATCH;
    if (status != HHS158_OK) return status;
    status = hhs158_make_receipt(instance->context, HHS158_OK, "HHS_P158_PROJECTION_NON_MUTATING",
        instance->definition, instance, NULL, instance->current_state_root, instance->current_state_root, NULL,
        (const char *)out_projection->canonical_payload.data, out_projection->canonical_payload.size, 0u, 0u,
        instance->lifecycle, 0u, out_receipt);
    return status;
}

HHS158Status hhs158_delta_compute(const HHS158Value *projected_state, const HHS158Value *reference_state,
    const HHS158DeltaPolicy *policy, HHS158Value *out_delta_vector) {
    HHS158Fraction projected;
    HHS158Fraction reference;
    HHS158Fraction ratio;
    HHS158Fraction additive;
    HHS158Fraction relative;
    HHS158Fraction one = {1, 1};
    char encoded[512];
    int written;
    HHS158Status status;
    if (!projected_state || !reference_state || !policy || !out_delta_vector) return HHS158_INVALID_ARGUMENT;
    if (!hhs158_header_valid(&projected_state->header, sizeof(*projected_state)) ||
        !hhs158_header_valid(&reference_state->header, sizeof(*reference_state)) ||
        !hhs158_header_valid(&policy->header, sizeof(*policy))) return HHS158_STRUCT_SIZE_INVALID;
    status = parse_fraction_span(projected_state->canonical_payload, &projected);
    if (status != HHS158_OK) return status;
    status = parse_fraction_span(reference_state->canonical_payload, &reference);
    if (status != HHS158_OK) return status;
    status = fraction_div(projected, reference, &ratio);
    if (status != HHS158_OK && (policy->mode == HHS158_DELTA_RATIO || policy->mode == HHS158_DELTA_REL || policy->mode == HHS158_DELTA_ALL || policy->require_invertible_reference)) return status;
    if (status != HHS158_OK) { ratio.numerator = 0; ratio.denominator = 1; }
    status = fraction_sub(projected, reference, &additive);
    if (status != HHS158_OK) return status;
    status = fraction_sub(ratio, one, &relative);
    if (status != HHS158_OK) return status;
    written = snprintf(encoded, sizeof(encoded),
        "mode=%u;projected=%lld/%lld;reference=%lld/%lld;ratio=%lld/%lld;add=%lld/%lld;rel=%lld/%lld",
        policy->mode, (long long)projected.numerator, (long long)projected.denominator,
        (long long)reference.numerator, (long long)reference.denominator,
        (long long)ratio.numerator, (long long)ratio.denominator,
        (long long)additive.numerator, (long long)additive.denominator,
        (long long)relative.numerator, (long long)relative.denominator);
    if (written < 0 || (size_t)written >= sizeof(encoded)) return HHS158_OUTPUT_BOUND;
    return hhs158_value_set(out_delta_vector, HHS158_VALUE_DELTA_VECTOR,
        HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE, (const uint8_t *)encoded, (size_t)written);
}

HHS158Status hhs158_delta_normalize(const HHS158Value *projected_state, const HHS158Value *delta_vector,
    HHS158Value *out_normalized_state) {
    char delta[512];
    char *reference;
    char *end;
    HHS158Fraction projected;
    HHS158Fraction reference_fraction;
    HHS158Status status;
    char normalized[128];
    int written;
    if (!projected_state || !delta_vector || !out_normalized_state) return HHS158_INVALID_ARGUMENT;
    if (!hhs158_header_valid(&projected_state->header, sizeof(*projected_state)) ||
        !hhs158_header_valid(&delta_vector->header, sizeof(*delta_vector))) return HHS158_STRUCT_SIZE_INVALID;
    if (delta_vector->kind != HHS158_VALUE_DELTA_VECTOR || delta_vector->canonical_payload.size >= sizeof(delta)) return HHS158_TYPE_MISMATCH;
    if (delta_vector->canonical_payload.size && !delta_vector->canonical_payload.data) return HHS158_INVALID_ARGUMENT;
    status = parse_fraction_span(projected_state->canonical_payload, &projected);
    if (status != HHS158_OK) return status;
    memcpy(delta, delta_vector->canonical_payload.data, delta_vector->canonical_payload.size);
    delta[delta_vector->canonical_payload.size] = '\0';
    reference = strstr(delta, "reference=");
    if (!reference) return HHS158_SERIALIZATION_INVALID;
    reference += strlen("reference=");
    end = strchr(reference, ';');
    if (end) *end = '\0';
    {
        HHS158ByteSpan span = {(const uint8_t *)reference, strlen(reference)};
        status = parse_fraction_span(span, &reference_fraction);
    }
    if (status != HHS158_OK) return status;
    written = snprintf(normalized, sizeof(normalized), "%lld/%lld", (long long)reference_fraction.numerator,
        (long long)reference_fraction.denominator);
    if (written < 0 || (size_t)written >= sizeof(normalized)) return HHS158_OUTPUT_BOUND;
    (void)projected;
    return hhs158_value_set(out_normalized_state, HHS158_VALUE_RATIONAL,
        HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE, (const uint8_t *)normalized, (size_t)written);
}
