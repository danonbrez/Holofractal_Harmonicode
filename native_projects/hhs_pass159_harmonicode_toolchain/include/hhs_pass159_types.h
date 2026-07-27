#ifndef HHS_PASS159_TYPES_H
#define HHS_PASS159_TYPES_H

#include <stddef.h>
#include <stdint.h>
#include "hhs_pass159_status.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS159_ABI_VERSION_MAJOR 1u
#define HHS159_ABI_VERSION_MINOR 0u
#define HHS159_STRUCT_VERSION_1 1u
#define HHS159_HASH72_LENGTH 72u
#define HHS159_HASH216_LENGTH 216u

#define HHS159_FLAG_AUTHORITATIVE (1u << 0)
#define HHS159_FLAG_PROJECTION    (1u << 1)
#define HHS159_FLAG_ORDERED       (1u << 2)
#define HHS159_FLAG_RECOVERED     (1u << 3)

typedef struct HHS159Context HHS159Context;
typedef struct HHS159Source HHS159Source;
typedef struct HHS159Module HHS159Module;
typedef struct HHS159CST HHS159CST;
typedef struct HHS159AST HHS159AST;
typedef struct HHS159TypeEnvironment HHS159TypeEnvironment;
typedef struct HHS159ConstraintGraph HHS159ConstraintGraph;
typedef struct HHS159IR HHS159IR;
typedef struct HHS159Object HHS159Object;
typedef struct HHS159Executable HHS159Executable;
typedef struct HHS159Interpreter HHS159Interpreter;
typedef struct HHS159Compiler HHS159Compiler;
typedef struct HHS159Linker HHS159Linker;
typedef struct HHS159Receipt HHS159Receipt;
typedef struct HHS159DiagnosticSet HHS159DiagnosticSet;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
} HHS159StructHeader;

typedef struct {
    const uint8_t *data;
    size_t size;
} HHS159ByteSpan;

typedef struct {
    uint8_t *data;
    size_t capacity;
    size_t size_written;
} HHS159MutableByteSpan;

typedef enum {
    HHS159_ARTIFACT_UNKNOWN = 0,
    HHS159_ARTIFACT_SOURCE = 1,
    HHS159_ARTIFACT_TOKEN_STREAM = 2,
    HHS159_ARTIFACT_CST = 3,
    HHS159_ARTIFACT_AST = 4,
    HHS159_ARTIFACT_TYPE_ENV = 5,
    HHS159_ARTIFACT_CONSTRAINT_GRAPH = 6,
    HHS159_ARTIFACT_HIR = 7,
    HHS159_ARTIFACT_VMIR = 8,
    HHS159_ARTIFACT_ASSEMBLY = 9,
    HHS159_ARTIFACT_OBJECT = 10,
    HHS159_ARTIFACT_EXECUTABLE = 11,
    HHS159_ARTIFACT_TRACE = 12,
    HHS159_ARTIFACT_RECEIPT = 13
} HHS159ArtifactKind;

typedef enum {
    HHS159_MODE_CHECK = 1,
    HHS159_MODE_EVALUATE_PURE = 2,
    HHS159_MODE_VALIDATE_ONLY = 3,
    HHS159_MODE_EXECUTE_CANDIDATE = 4,
    HHS159_MODE_EXECUTE_AND_HOLD = 5,
    HHS159_MODE_EXECUTE_AND_COMMIT = 6,
    HHS159_MODE_REPLAY = 7,
    HHS159_MODE_TRACE = 8
} HHS159InterpreterMode;

typedef struct {
    HHS159StructHeader header;
    uint64_t max_source_bytes;
    uint64_t max_tokens;
    uint64_t max_nesting;
    uint64_t max_output_bytes;
    uint64_t deterministic_epoch;
    uint32_t flags;
    uint32_t reserved;
} HHS159ContextConfig;

typedef struct {
    HHS159StructHeader header;
    HHS159ByteSpan source_name;
    HHS159ByteSpan encoding;
    uint32_t preserve_bom;
    uint32_t flags;
} HHS159SourceOpenOptions;

typedef struct {
    HHS159StructHeader header;
    uint32_t mode;
    uint32_t commit_policy;
    uint64_t max_vm81_steps;
    uint64_t max_recursion;
    uint64_t max_output_bytes;
    const volatile uint32_t *cancel_flag;
} HHS159ExecutionOptions;

typedef struct {
    HHS159StructHeader header;
    HHS159Status status;
    uint32_t matched;
    uint32_t fallback_used;
    uint64_t interpreter_steps;
    uint64_t compiled_steps;
    char interpreter_semantic_root[HHS159_HASH216_LENGTH + 1u];
    char compiled_semantic_root[HHS159_HASH216_LENGTH + 1u];
    char classification[96];
} HHS159CompareResult;

#ifdef __cplusplus
}
#endif
#endif
