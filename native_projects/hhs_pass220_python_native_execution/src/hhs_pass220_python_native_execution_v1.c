#include "hhs_pass220_python_native_execution_v1.h"

#include <stddef.h>
#include <stdint.h>

typedef struct HHSBigIntV1 {
    int sign;
    uint32_t length;
    uint8_t digits[HHS_PYTHON_NATIVE_MAX_DIGITS];
} HHSBigIntV1;

typedef struct HHSVariableV1 {
    int occupied;
    char name[HHS_PYTHON_NATIVE_MAX_NAME_BYTES];
    HHSBigIntV1 value;
} HHSVariableV1;

typedef struct HHSParserV1 {
    const char *source;
    size_t length;
    size_t pos;
    HHSVariableV1 variables[HHS_PYTHON_NATIVE_MAX_VARIABLES];
    uint32_t statement_count;
    HHSPythonNativeStatusV1 status;
    char *error;
    size_t error_capacity;
} HHSParserV1;

static void byte_zero(void *ptr, size_t count) {
    uint8_t *p = (uint8_t *)ptr;
    size_t i;
    for (i = 0U; i < count; ++i) p[i] = 0U;
}

static size_t cstr_len(const char *s) {
    size_t n = 0U;
    if (s == NULL) return 0U;
    while (s[n] != '\0') ++n;
    return n;
}

static void copy_text(char *dst, size_t capacity, const char *src) {
    size_t i = 0U;
    if (dst == NULL || capacity == 0U) return;
    if (src != NULL) {
        while (src[i] != '\0' && i + 1U < capacity) {
            dst[i] = src[i];
            ++i;
        }
    }
    dst[i] = '\0';
}

static void parser_error(
    HHSParserV1 *parser,
    HHSPythonNativeStatusV1 status,
    const char *message
) {
    if (parser->status == HHS_PYTHON_NATIVE_OK) {
        parser->status = status;
        copy_text(parser->error, parser->error_capacity, message);
    }
}

static int is_alpha_ascii(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_';
}

static int is_digit_ascii(char c) {
    return c >= '0' && c <= '9';
}

static int is_alnum_ascii(char c) {
    return is_alpha_ascii(c) || is_digit_ascii(c);
}

static void bigint_zero(HHSBigIntV1 *value) {
    byte_zero(value, sizeof(*value));
    value->sign = 0;
    value->length = 1U;
    value->digits[0] = 0U;
}

static void bigint_copy(HHSBigIntV1 *dst, const HHSBigIntV1 *src) {
    uint32_t i;
    dst->sign = src->sign;
    dst->length = src->length;
    for (i = 0U; i < src->length; ++i) dst->digits[i] = src->digits[i];
    for (; i < HHS_PYTHON_NATIVE_MAX_DIGITS; ++i) dst->digits[i] = 0U;
}

static void bigint_normalize(HHSBigIntV1 *value) {
    while (value->length > 1U && value->digits[value->length - 1U] == 0U) {
        value->length -= 1U;
    }
    if (value->length == 1U && value->digits[0] == 0U) value->sign = 0;
}

static int bigint_compare_abs(const HHSBigIntV1 *a, const HHSBigIntV1 *b) {
    uint32_t i;
    if (a->length < b->length) return -1;
    if (a->length > b->length) return 1;
    i = a->length;
    while (i > 0U) {
        --i;
        if (a->digits[i] < b->digits[i]) return -1;
        if (a->digits[i] > b->digits[i]) return 1;
    }
    return 0;
}

static HHSPythonNativeStatusV1 bigint_parse_digits(
    HHSBigIntV1 *out,
    const char *source,
    size_t start,
    size_t end
) {
    size_t count;
    size_t i;
    if (out == NULL || source == NULL || end <= start) {
        return HHS_PYTHON_NATIVE_ERR_ARGUMENT;
    }
    count = end - start;
    if (count > HHS_PYTHON_NATIVE_MAX_DIGITS) {
        return HHS_PYTHON_NATIVE_ERR_BIGINT_OVERFLOW;
    }
    bigint_zero(out);
    out->length = (uint32_t)count;
    out->sign = 1;
    for (i = 0U; i < count; ++i) {
        char c = source[end - 1U - i];
        if (!is_digit_ascii(c)) return HHS_PYTHON_NATIVE_ERR_SYNTAX;
        out->digits[i] = (uint8_t)(c - '0');
    }
    bigint_normalize(out);
    return HHS_PYTHON_NATIVE_OK;
}

static HHSPythonNativeStatusV1 bigint_add_abs(
    const HHSBigIntV1 *a,
    const HHSBigIntV1 *b,
    HHSBigIntV1 *out
) {
    uint32_t max_len = a->length > b->length ? a->length : b->length;
    uint32_t i;
    uint32_t carry = 0U;
    bigint_zero(out);
    if (max_len > HHS_PYTHON_NATIVE_MAX_DIGITS) {
        return HHS_PYTHON_NATIVE_ERR_BIGINT_OVERFLOW;
    }
    for (i = 0U; i < max_len; ++i) {
        uint32_t sum = carry;
        if (i < a->length) sum += a->digits[i];
        if (i < b->length) sum += b->digits[i];
        out->digits[i] = (uint8_t)(sum % 10U);
        carry = sum / 10U;
    }
    out->length = max_len;
    if (carry != 0U) {
        if (out->length >= HHS_PYTHON_NATIVE_MAX_DIGITS) {
            return HHS_PYTHON_NATIVE_ERR_BIGINT_OVERFLOW;
        }
        out->digits[out->length++] = (uint8_t)carry;
    }
    out->sign = 1;
    bigint_normalize(out);
    return HHS_PYTHON_NATIVE_OK;
}

static void bigint_sub_abs(
    const HHSBigIntV1 *a,
    const HHSBigIntV1 *b,
    HHSBigIntV1 *out
) {
    uint32_t i;
    int borrow = 0;
    bigint_zero(out);
    out->length = a->length;
    out->sign = 1;
    for (i = 0U; i < a->length; ++i) {
        int digit = (int)a->digits[i] - borrow;
        if (i < b->length) digit -= (int)b->digits[i];
        if (digit < 0) {
            digit += 10;
            borrow = 1;
        } else {
            borrow = 0;
        }
        out->digits[i] = (uint8_t)digit;
    }
    bigint_normalize(out);
}

static HHSPythonNativeStatusV1 bigint_add(
    const HHSBigIntV1 *a,
    const HHSBigIntV1 *b,
    HHSBigIntV1 *out
) {
    int cmp;
    HHSPythonNativeStatusV1 status;
    if (a->sign == 0) {
        bigint_copy(out, b);
        return HHS_PYTHON_NATIVE_OK;
    }
    if (b->sign == 0) {
        bigint_copy(out, a);
        return HHS_PYTHON_NATIVE_OK;
    }
    if (a->sign == b->sign) {
        status = bigint_add_abs(a, b, out);
        if (status == HHS_PYTHON_NATIVE_OK) out->sign = a->sign;
        return status;
    }
    cmp = bigint_compare_abs(a, b);
    if (cmp == 0) {
        bigint_zero(out);
    } else if (cmp > 0) {
        bigint_sub_abs(a, b, out);
        out->sign = a->sign;
    } else {
        bigint_sub_abs(b, a, out);
        out->sign = b->sign;
    }
    bigint_normalize(out);
    return HHS_PYTHON_NATIVE_OK;
}

static HHSPythonNativeStatusV1 bigint_subtract(
    const HHSBigIntV1 *a,
    const HHSBigIntV1 *b,
    HHSBigIntV1 *out
) {
    HHSBigIntV1 neg;
    bigint_copy(&neg, b);
    neg.sign = -neg.sign;
    return bigint_add(a, &neg, out);
}

static HHSPythonNativeStatusV1 bigint_multiply(
    const HHSBigIntV1 *a,
    const HHSBigIntV1 *b,
    HHSBigIntV1 *out
) {
    uint32_t accum[HHS_PYTHON_NATIVE_MAX_DIGITS * 2U];
    uint32_t i;
    uint32_t j;
    uint32_t used;
    uint32_t carry;

    if (a->sign == 0 || b->sign == 0) {
        bigint_zero(out);
        return HHS_PYTHON_NATIVE_OK;
    }
    byte_zero(accum, sizeof(accum));

    for (i = 0U; i < a->length; ++i) {
        for (j = 0U; j < b->length; ++j) {
            accum[i + j] += (uint32_t)a->digits[i] * (uint32_t)b->digits[j];
        }
    }

    used = a->length + b->length;
    if (used > HHS_PYTHON_NATIVE_MAX_DIGITS * 2U) {
        return HHS_PYTHON_NATIVE_ERR_BIGINT_OVERFLOW;
    }
    carry = 0U;
    for (i = 0U; i < used; ++i) {
        uint32_t value = accum[i] + carry;
        accum[i] = value % 10U;
        carry = value / 10U;
    }
    while (carry != 0U) {
        if (used >= HHS_PYTHON_NATIVE_MAX_DIGITS * 2U) {
            return HHS_PYTHON_NATIVE_ERR_BIGINT_OVERFLOW;
        }
        accum[used++] = carry % 10U;
        carry /= 10U;
    }
    while (used > 1U && accum[used - 1U] == 0U) --used;
    if (used > HHS_PYTHON_NATIVE_MAX_DIGITS) {
        return HHS_PYTHON_NATIVE_ERR_BIGINT_OVERFLOW;
    }

    bigint_zero(out);
    out->length = used;
    out->sign = a->sign * b->sign;
    for (i = 0U; i < used; ++i) out->digits[i] = (uint8_t)accum[i];
    bigint_normalize(out);
    return HHS_PYTHON_NATIVE_OK;
}

static HHSPythonNativeStatusV1 bigint_to_text(
    const HHSBigIntV1 *value,
    char *out,
    size_t capacity,
    size_t *out_length
) {
    size_t required;
    size_t pos = 0U;
    uint32_t i;
    required = (value->sign < 0 ? 1U : 0U) + (size_t)value->length;
    if (out_length != NULL) *out_length = required;
    if (out == NULL || capacity <= required) {
        return HHS_PYTHON_NATIVE_ERR_RESULT_CAPACITY;
    }
    if (value->sign < 0) out[pos++] = '-';
    i = value->length;
    while (i > 0U) {
        --i;
        out[pos++] = (char)('0' + value->digits[i]);
    }
    out[pos] = '\0';
    return HHS_PYTHON_NATIVE_OK;
}

static void skip_horizontal(HHSParserV1 *parser) {
    while (parser->pos < parser->length) {
        char c = parser->source[parser->pos];
        if (c == ' ' || c == '\t' || c == '\r') {
            parser->pos += 1U;
        } else {
            break;
        }
    }
}

static int at_statement_end(const HHSParserV1 *parser) {
    if (parser->pos >= parser->length) return 1;
    return parser->source[parser->pos] == '\n' || parser->source[parser->pos] == ';';
}

static int parse_identifier(
    HHSParserV1 *parser,
    char *out_name,
    size_t out_capacity
) {
    size_t start;
    size_t n;
    skip_horizontal(parser);
    if (parser->pos >= parser->length || !is_alpha_ascii(parser->source[parser->pos])) {
        return 0;
    }
    start = parser->pos++;
    while (
        parser->pos < parser->length
        && is_alnum_ascii(parser->source[parser->pos])
    ) {
        parser->pos += 1U;
    }
    n = parser->pos - start;
    if (n + 1U > out_capacity) {
        parser_error(
            parser,
            HHS_PYTHON_NATIVE_ERR_UNSUPPORTED,
            "identifier exceeds native Python1 name bound"
        );
        return -1;
    }
    {
        size_t i;
        for (i = 0U; i < n; ++i) out_name[i] = parser->source[start + i];
        out_name[n] = '\0';
    }
    return 1;
}

static int name_equal(const char *a, const char *b) {
    size_t i = 0U;
    while (a[i] != '\0' && b[i] != '\0') {
        if (a[i] != b[i]) return 0;
        ++i;
    }
    return a[i] == b[i];
}

static HHSVariableV1 *find_variable(HHSParserV1 *parser, const char *name) {
    uint32_t i;
    for (i = 0U; i < HHS_PYTHON_NATIVE_MAX_VARIABLES; ++i) {
        if (parser->variables[i].occupied && name_equal(parser->variables[i].name, name)) {
            return &parser->variables[i];
        }
    }
    return NULL;
}

static HHSPythonNativeStatusV1 set_variable(
    HHSParserV1 *parser,
    const char *name,
    const HHSBigIntV1 *value
) {
    HHSVariableV1 *slot = find_variable(parser, name);
    uint32_t i;
    if (slot == NULL) {
        for (i = 0U; i < HHS_PYTHON_NATIVE_MAX_VARIABLES; ++i) {
            if (!parser->variables[i].occupied) {
                size_t j = 0U;
                slot = &parser->variables[i];
                slot->occupied = 1;
                while (name[j] != '\0' && j + 1U < HHS_PYTHON_NATIVE_MAX_NAME_BYTES) {
                    slot->name[j] = name[j];
                    ++j;
                }
                slot->name[j] = '\0';
                break;
            }
        }
    }
    if (slot == NULL) return HHS_PYTHON_NATIVE_ERR_VARIABLE_CAPACITY;
    bigint_copy(&slot->value, value);
    return HHS_PYTHON_NATIVE_OK;
}

static int parse_expression(HHSParserV1 *parser, HHSBigIntV1 *out);

static int parse_factor(HHSParserV1 *parser, HHSBigIntV1 *out) {
    char c;
    skip_horizontal(parser);
    if (parser->pos >= parser->length) {
        parser_error(parser, HHS_PYTHON_NATIVE_ERR_SYNTAX, "expected expression factor");
        return 0;
    }
    c = parser->source[parser->pos];

    if (c == '+' || c == '-') {
        int negative = c == '-';
        parser->pos += 1U;
        if (!parse_factor(parser, out)) return 0;
        if (negative) out->sign = -out->sign;
        return 1;
    }

    if (c == '(') {
        parser->pos += 1U;
        if (!parse_expression(parser, out)) return 0;
        skip_horizontal(parser);
        if (parser->pos >= parser->length || parser->source[parser->pos] != ')') {
            parser_error(parser, HHS_PYTHON_NATIVE_ERR_SYNTAX, "expected closing parenthesis");
            return 0;
        }
        parser->pos += 1U;
        return 1;
    }

    if (is_digit_ascii(c)) {
        size_t start = parser->pos;
        HHSPythonNativeStatusV1 status;
        while (parser->pos < parser->length && is_digit_ascii(parser->source[parser->pos])) {
            parser->pos += 1U;
        }
        status = bigint_parse_digits(out, parser->source, start, parser->pos);
        if (status != HHS_PYTHON_NATIVE_OK) {
            parser_error(parser, status, "integer literal exceeds native Python1 BigInt bound");
            return 0;
        }
        return 1;
    }

    if (is_alpha_ascii(c)) {
        char name[HHS_PYTHON_NATIVE_MAX_NAME_BYTES];
        int parsed = parse_identifier(parser, name, sizeof(name));
        HHSVariableV1 *variable;
        if (parsed <= 0) return 0;
        variable = find_variable(parser, name);
        if (variable == NULL) {
            parser_error(parser, HHS_PYTHON_NATIVE_ERR_NAME, "name is not defined");
            return 0;
        }
        bigint_copy(out, &variable->value);
        return 1;
    }

    parser_error(parser, HHS_PYTHON_NATIVE_ERR_SYNTAX, "unsupported Python1 expression token");
    return 0;
}

static int parse_term(HHSParserV1 *parser, HHSBigIntV1 *out) {
    HHSBigIntV1 left;
    if (!parse_factor(parser, &left)) return 0;
    for (;;) {
        HHSBigIntV1 right;
        HHSBigIntV1 result;
        HHSPythonNativeStatusV1 status;
        skip_horizontal(parser);
        if (parser->pos >= parser->length || parser->source[parser->pos] != '*') break;
        parser->pos += 1U;
        if (!parse_factor(parser, &right)) return 0;
        status = bigint_multiply(&left, &right, &result);
        if (status != HHS_PYTHON_NATIVE_OK) {
            parser_error(parser, status, "integer multiplication exceeds native Python1 BigInt bound");
            return 0;
        }
        bigint_copy(&left, &result);
    }
    bigint_copy(out, &left);
    return 1;
}

static int parse_expression(HHSParserV1 *parser, HHSBigIntV1 *out) {
    HHSBigIntV1 left;
    if (!parse_term(parser, &left)) return 0;
    for (;;) {
        char op;
        HHSBigIntV1 right;
        HHSBigIntV1 result;
        HHSPythonNativeStatusV1 status;
        skip_horizontal(parser);
        if (parser->pos >= parser->length) break;
        op = parser->source[parser->pos];
        if (op != '+' && op != '-') break;
        parser->pos += 1U;
        if (!parse_term(parser, &right)) return 0;
        status = op == '+'
            ? bigint_add(&left, &right, &result)
            : bigint_subtract(&left, &right, &result);
        if (status != HHS_PYTHON_NATIVE_OK) {
            parser_error(parser, status, "integer arithmetic exceeds native Python1 BigInt bound");
            return 0;
        }
        bigint_copy(&left, &result);
    }
    bigint_copy(out, &left);
    return 1;
}

static int parse_statement(HHSParserV1 *parser, HHSBigIntV1 *out) {
    size_t saved;
    char name[HHS_PYTHON_NATIVE_MAX_NAME_BYTES];
    int identifier;
    skip_horizontal(parser);
    saved = parser->pos;
    identifier = parse_identifier(parser, name, sizeof(name));
    if (identifier < 0) return 0;
    if (identifier > 0) {
        skip_horizontal(parser);
        if (
            parser->pos < parser->length
            && parser->source[parser->pos] == '='
            && (
                parser->pos + 1U >= parser->length
                || parser->source[parser->pos + 1U] != '='
            )
        ) {
            HHSPythonNativeStatusV1 status;
            parser->pos += 1U;
            if (!parse_expression(parser, out)) return 0;
            status = set_variable(parser, name, out);
            if (status != HHS_PYTHON_NATIVE_OK) {
                parser_error(parser, status, "native Python1 variable capacity exceeded");
                return 0;
            }
            return 1;
        }
    }
    parser->pos = saved;
    return parse_expression(parser, out);
}

uint32_t hhs_python_native_execution_version(void) {
    return HHS_PYTHON_NATIVE_EXECUTION_VERSION;
}

HHSPythonNativeStatusV1 hhs_python_native_execute(
    const char *source,
    char *result,
    size_t result_capacity,
    size_t *result_length,
    char *error,
    size_t error_capacity,
    uint32_t *statement_count
) {
    HHSParserV1 parser;
    HHSBigIntV1 last;
    size_t source_length;
    HHSPythonNativeStatusV1 status;

    if (
        source == NULL
        || result_length == NULL
        || statement_count == NULL
        || error == NULL
        || error_capacity == 0U
    ) {
        return HHS_PYTHON_NATIVE_ERR_ARGUMENT;
    }

    source_length = cstr_len(source);
    if (source_length > HHS_PYTHON_NATIVE_MAX_SOURCE_BYTES) {
        copy_text(error, error_capacity, "source exceeds native Python1 source bound");
        return HHS_PYTHON_NATIVE_ERR_SOURCE_TOO_LARGE;
    }

    byte_zero(&parser, sizeof(parser));
    parser.source = source;
    parser.length = source_length;
    parser.error = error;
    parser.error_capacity = error_capacity;
    parser.status = HHS_PYTHON_NATIVE_OK;
    error[0] = '\0';
    bigint_zero(&last);

    while (parser.pos < parser.length) {
        while (
            parser.pos < parser.length
            && (
                parser.source[parser.pos] == '\n'
                || parser.source[parser.pos] == ';'
                || parser.source[parser.pos] == ' '
                || parser.source[parser.pos] == '\t'
                || parser.source[parser.pos] == '\r'
            )
        ) {
            parser.pos += 1U;
        }
        if (parser.pos >= parser.length) break;

        if (!parse_statement(&parser, &last)) break;
        parser.statement_count += 1U;
        skip_horizontal(&parser);
        if (!at_statement_end(&parser)) {
            parser_error(
                &parser,
                HHS_PYTHON_NATIVE_ERR_UNSUPPORTED,
                "unsupported Python1 syntax after expression"
            );
            break;
        }
        while (
            parser.pos < parser.length
            && (parser.source[parser.pos] == '\n' || parser.source[parser.pos] == ';')
        ) {
            parser.pos += 1U;
        }
    }

    *statement_count = parser.statement_count;
    if (parser.status != HHS_PYTHON_NATIVE_OK) {
        *result_length = 0U;
        if (result != NULL && result_capacity > 0U) result[0] = '\0';
        return parser.status;
    }
    if (parser.statement_count == 0U) {
        copy_text(error, error_capacity, "native Python1 program contains no statements");
        *result_length = 0U;
        return HHS_PYTHON_NATIVE_ERR_SYNTAX;
    }

    status = bigint_to_text(&last, result, result_capacity, result_length);
    if (status != HHS_PYTHON_NATIVE_OK) {
        copy_text(error, error_capacity, "native Python1 result buffer too small");
        return status;
    }
    return HHS_PYTHON_NATIVE_OK;
}
