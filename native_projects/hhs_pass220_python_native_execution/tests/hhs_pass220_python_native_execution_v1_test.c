#include "hhs_pass220_python_native_execution_v1.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void run_case(const char *source, const char *expected, uint32_t expected_statements) {
    char result[HHS_PYTHON_NATIVE_MAX_DIGITS + 2U];
    char error[256];
    size_t result_length = 0U;
    uint32_t statements = 0U;
    HHSPythonNativeStatusV1 status = hhs_python_native_execute(
        source,
        result,
        sizeof(result),
        &result_length,
        error,
        sizeof(error),
        &statements
    );
    assert(status == HHS_PYTHON_NATIVE_OK);
    assert(strcmp(result, expected) == 0);
    assert(result_length == strlen(expected));
    assert(statements == expected_statements);
}

int main(void) {
    char result[64];
    char error[256];
    size_t result_length = 0U;
    uint32_t statements = 0U;
    HHSPythonNativeStatusV1 status;

    assert(hhs_python_native_execution_version() == 1U);

    run_case("1+2*3", "7", 1U);
    run_case("(1+2)*3", "9", 1U);
    run_case("-5*3+2", "-13", 1U);
    run_case("a=7\nb=a*11\nb-2", "75", 3U);
    run_case(
        "x=999999999999999999999999999999\n"
        "y=888888888888888888888888888888\n"
        "x*y",
        "888888888888888888888888888887111111111111111111111111111112",
        3U
    );

    status = hhs_python_native_execute(
        "missing+1",
        result,
        sizeof(result),
        &result_length,
        error,
        sizeof(error),
        &statements
    );
    assert(status == HHS_PYTHON_NATIVE_ERR_NAME);
    assert(strstr(error, "name is not defined") != NULL);

    status = hhs_python_native_execute(
        "__import__('os')",
        result,
        sizeof(result),
        &result_length,
        error,
        sizeof(error),
        &statements
    );
    assert(status != HHS_PYTHON_NATIVE_OK);

    status = hhs_python_native_execute(
        "2**8",
        result,
        sizeof(result),
        &result_length,
        error,
        sizeof(error),
        &statements
    );
    assert(status != HHS_PYTHON_NATIVE_OK);

    puts("PASS hhs_pass220_python_native_execution_v1");
    return 0;
}
