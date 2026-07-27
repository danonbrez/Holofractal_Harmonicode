#ifndef HHS159_INTERNAL_H
#define HHS159_INTERNAL_H

#include "hhs_pass159_api.h"
#include "hhs_hash216.h"

#include <stddef.h>
#include <stdint.h>

#define HHS159_MAGIC UINT64_C(0x484853313539434F)
#define HHS159_DEFAULT_MAX_SOURCE (1024u * 1024u)
#define HHS159_DEFAULT_MAX_TOKENS 200000u
#define HHS159_DEFAULT_MAX_NESTING 1024u
#define HHS159_DEFAULT_MAX_OUTPUT (4u * 1024u * 1024u)

typedef struct {
    uint64_t magic;
    uint32_t kind;
    uint32_t stage;
    uint8_t *bytes;
    size_t size;
    char hash216[HHS159_HASH216_LENGTH + 1u];
    char source_root[HHS159_HASH216_LENGTH + 1u];
    char parent_root[HHS159_HASH216_LENGTH + 1u];
} HHS159ArtifactBase;

struct HHS159Context {
    uint64_t magic;
    HHS159ContextConfig config;
    HHS159Status last_status;
    char diagnostic_code[64];
    char diagnostic_message[512];
};

struct HHS159Source { HHS159ArtifactBase base; char encoding[32]; char source_name[256]; uint32_t bom_present; };
struct HHS159Module { HHS159ArtifactBase base; };
struct HHS159CST { HHS159ArtifactBase base; };
struct HHS159AST { HHS159ArtifactBase base; };
struct HHS159TypeEnvironment { HHS159ArtifactBase base; };
struct HHS159ConstraintGraph { HHS159ArtifactBase base; };
struct HHS159IR { HHS159ArtifactBase base; };
struct HHS159Object { HHS159ArtifactBase base; };
struct HHS159Executable { HHS159ArtifactBase base; };
struct HHS159Interpreter { uint64_t magic; HHS159Context *context; };
struct HHS159Compiler { uint64_t magic; HHS159Context *context; };
struct HHS159Linker { uint64_t magic; HHS159Context *context; };
struct HHS159Receipt { HHS159ArtifactBase base; HHS159Status status; char phase[64]; char semantic_root[HHS159_HASH216_LENGTH + 1u]; char hash72[HHS159_HASH72_LENGTH + 1u]; uint64_t vm81_steps; uint32_t committed; uint32_t fallback_used; };
struct HHS159DiagnosticSet { HHS159ArtifactBase base; };

int hhs159_context_valid(const HHS159Context *context);
int hhs159_artifact_valid(const void *handle);
void hhs159_set_diag(HHS159Context *context, HHS159Status status, const char *code, const char *message);
HHS159Status hhs159_copy_out(const uint8_t *data, size_t size, HHS159MutableByteSpan *output);
HHS159Status hhs159_make_artifact(uint32_t kind, uint32_t stage, const char *domain, const uint8_t *bytes, size_t size, const char *source_root, const char *parent_root, size_t object_size, void **out_object);
void hhs159_domain_hash(const char *domain, const uint8_t *bytes, size_t size, char out[HHS159_HASH216_LENGTH + 1u]);
void hhs159_domain_hash72(const char *domain, const uint8_t *bytes, size_t size, char out[HHS159_HASH72_LENGTH + 1u]);
int hhs159_utf8_valid(const uint8_t *data, size_t size);
HHS159Status hhs159_frontend_to_vmir(HHS159Context *context, const HHS159Source *source, HHS159IR **out_vmir);
HHS159Status hhs159_make_receipt(HHS159Context *context, const char *phase, HHS159Status status, const char *semantic_root, const char *source_root, const char *parent_root, uint64_t steps, uint32_t committed, uint32_t fallback_used, HHS159Receipt **out_receipt);
const char *hhs159_find_field(const uint8_t *data, size_t size, const char *field);

#endif
