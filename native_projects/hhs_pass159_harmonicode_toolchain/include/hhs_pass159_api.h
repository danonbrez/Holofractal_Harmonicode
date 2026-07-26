#ifndef HHS_PASS159_API_H
#define HHS_PASS159_API_H

#include "hhs_pass159_types.h"
#include "hhs_pass159_tokens.h"
#include "hhs_pass159_ast.h"
#include "hhs_pass159_ir.h"
#include "hhs_pass159_object.h"
#include "hhs_pass159_diagnostics.h"

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define HHS159_API __declspec(dllexport)
#elif defined(__GNUC__) && __GNUC__ >= 4
#define HHS159_API __attribute__((visibility("default")))
#else
#define HHS159_API
#endif

#define HHS159_CONTRACT_ID "HHS-P159-VM81-H216-HCI-C11C"
#define HHS159_CONTRACT_VERSION "1.0.0"
#define HHS159_FOUNDATION_CLASSIFICATION "HHS_PASS_159_FOUNDATION_IMPLEMENTED_PENDING_FULL_CLOSURE"
#define HHS159_TERMINAL_CLASSIFICATION "HHS_PASS_159_VM81_HASH216_HARMONICODE_INTERPRETER_AND_C11_NATIVE_COMPILER_VERIFIED"

HHS159_API uint32_t hhs159_abi_version_major(void);
HHS159_API uint32_t hhs159_abi_version_minor(void);
HHS159_API const char *hhs159_contract_id(void);
HHS159_API const char *hhs159_contract_version(void);
HHS159_API HHS159Status hhs159_context_create(const HHS159ContextConfig *config, HHS159Context **out_context);
HHS159_API void hhs159_context_release(HHS159Context *context);
HHS159_API HHS159Status hhs159_source_open_bytes(HHS159Context *context, HHS159ByteSpan bytes, const HHS159SourceOpenOptions *options, HHS159Source **out_source);
HHS159_API HHS159Status hhs159_source_open_file(HHS159Context *context, const char *path, const HHS159SourceOpenOptions *options, HHS159Source **out_source);
HHS159_API HHS159Status hhs159_source_hash216(const HHS159Source *source, HHS159MutableByteSpan *output);
HHS159_API void hhs159_source_release(HHS159Source *source);
HHS159_API HHS159Status hhs159_lex(HHS159Context *context, const HHS159Source *source, HHS159IR **out_tokens);
HHS159_API HHS159Status hhs159_parse_cst(HHS159Context *context, const HHS159Source *source, HHS159CST **out_cst);
HHS159_API HHS159Status hhs159_build_ast(HHS159Context *context, const HHS159CST *cst, HHS159AST **out_ast);
HHS159_API HHS159Status hhs159_typecheck(HHS159Context *context, const HHS159AST *ast, HHS159TypeEnvironment **out_types);
HHS159_API HHS159Status hhs159_build_constraint_graph(HHS159Context *context, const HHS159AST *ast, const HHS159TypeEnvironment *types, HHS159ConstraintGraph **out_graph);
HHS159_API HHS159Status hhs159_lower_hir(HHS159Context *context, const HHS159AST *ast, const HHS159TypeEnvironment *types, const HHS159ConstraintGraph *graph, HHS159IR **out_hir);
HHS159_API HHS159Status hhs159_lower_vmir(HHS159Context *context, const HHS159IR *hir, HHS159IR **out_vmir);
HHS159_API HHS159Status hhs159_interpreter_create(HHS159Context *context, HHS159Interpreter **out_interpreter);
HHS159_API HHS159Status hhs159_interpret(HHS159Interpreter *interpreter, const HHS159Source *source, const HHS159ExecutionOptions *options, HHS159Receipt **out_receipt);
HHS159_API HHS159Status hhs159_interpreter_replay(HHS159Interpreter *interpreter, const HHS159Receipt *receipt, HHS159Receipt **out_replay_receipt);
HHS159_API void hhs159_interpreter_release(HHS159Interpreter *interpreter);
HHS159_API HHS159Status hhs159_compiler_create(HHS159Context *context, HHS159Compiler **out_compiler);
HHS159_API HHS159Status hhs159_compile_object(HHS159Compiler *compiler, const HHS159Source *source, HHS159Object **out_object, HHS159Receipt **out_receipt);
HHS159_API HHS159Status hhs159_compile_module(HHS159Compiler *compiler, const HHS159Source *source, HHS159Module **out_module, HHS159Receipt **out_receipt);
HHS159_API void hhs159_compiler_release(HHS159Compiler *compiler);
HHS159_API HHS159Status hhs159_assemble(HHS159Context *context, HHS159ByteSpan assembly, HHS159Object **out_object, HHS159Receipt **out_receipt);
HHS159_API HHS159Status hhs159_link(HHS159Context *context, HHS159Object *const *objects, size_t object_count, HHS159Executable **out_executable, HHS159Receipt **out_receipt);
HHS159_API HHS159Status hhs159_load_executable(HHS159Context *context, HHS159ByteSpan serialized, HHS159Executable **out_executable);
HHS159_API HHS159Status hhs159_execute(HHS159Context *context, const HHS159Executable *executable, const HHS159ExecutionOptions *options, HHS159Receipt **out_receipt);
HHS159_API HHS159Status hhs159_reverse(HHS159Context *context, const HHS159Receipt *receipt, HHS159Receipt **out_reverse_receipt);
HHS159_API HHS159Status hhs159_compare_interpreter_compiler(HHS159Context *context, const HHS159Source *source, const HHS159ExecutionOptions *options, HHS159CompareResult *out_result);
HHS159_API HHS159Status hhs159_lift_trace(HHS159Context *context, const HHS159Receipt *receipt, HHS159IR **out_trace);
HHS159_API HHS159Status hhs159_get_diagnostics(HHS159Context *context, HHS159DiagnosticSet **out_diagnostics);
HHS159_API HHS159Status hhs159_get_receipt(const void *handle, HHS159Receipt **out_receipt);
HHS159_API HHS159Status hhs159_get_hash216(const void *handle, HHS159MutableByteSpan *output);
HHS159_API HHS159Status hhs159_serialize(const void *handle, HHS159MutableByteSpan *output);
HHS159_API HHS159Status hhs159_deserialize(HHS159Context *context, HHS159ByteSpan serialized, uint32_t expected_kind, void **out_handle);
HHS159_API HHS159Status hhs159_artifact_bytes(const void *handle, HHS159MutableByteSpan *output);
HHS159_API uint32_t hhs159_artifact_kind(const void *handle);
HHS159_API void hhs159_artifact_release(void *handle);
HHS159_API void hhs159_receipt_release(HHS159Receipt *receipt);
HHS159_API const char *hhs159_status_string(HHS159Status status);

#ifdef __cplusplus
}
#endif
#endif
