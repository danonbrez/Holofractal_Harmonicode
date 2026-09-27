#ifndef HHS_PASS220_PYTHON_NATIVE_EXECUTION_V1_H
#define HHS_PASS220_PYTHON_NATIVE_EXECUTION_V1_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PYTHON_NATIVE_EXECUTION_VERSION 1U
#define HHS_PYTHON_NATIVE_MAX_DIGITS 5184U
#define HHS_PYTHON_NATIVE_MAX_VARIABLES 64U
#define HHS_PYTHON_NATIVE_MAX_NAME_BYTES 64U
#define HHS_PYTHON_NATIVE_MAX_SOURCE_BYTES 65536U

typedef enum HHSPythonNativeStatusV1 {
    HHS_PYTHON_NATIVE_OK = 0,
    HHS_PYTHON_NATIVE_ERR_ARGUMENT = 1,
    HHS_PYTHON_NATIVE_ERR_SOURCE_TOO_LARGE = 2,
    HHS_PYTHON_NATIVE_ERR_SYNTAX = 3,
    HHS_PYTHON_NATIVE_ERR_NAME = 4,
    HHS_PYTHON_NATIVE_ERR_BIGINT_OVERFLOW = 5,
    HHS_PYTHON_NATIVE_ERR_VARIABLE_CAPACITY = 6,
    HHS_PYTHON_NATIVE_ERR_RESULT_CAPACITY = 7,
    HHS_PYTHON_NATIVE_ERR_UNSUPPORTED = 8
} HHSPythonNativeStatusV1;

uint32_t hhs_python_native_execution_version(void);

HHSPythonNativeStatusV1 hhs_python_native_execute(
    const char *source,
    char *result,
    size_t result_capacity,
    size_t *result_length,
    char *error,
    size_t error_capacity,
    uint32_t *statement_count
);

#ifdef __cplusplus
}
#endif

#endif
