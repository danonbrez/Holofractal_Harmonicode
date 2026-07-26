#ifndef HHS_PASS158_STATUS_H
#define HHS_PASS158_STATUS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef int32_t HHS158Status;

#define HHS158_OK                              ((HHS158Status)0)
#define HHS158_HELD                            ((HHS158Status)1)
#define HHS158_BUFFER_TOO_SMALL                ((HHS158Status)2)
#define HHS158_RESOURCE_BOUNDED                ((HHS158Status)3)
#define HHS158_NONTERMINAL                     ((HHS158Status)4)

#define HHS158_REJECTED                        ((HHS158Status)-1)
#define HHS158_INVALID_ARGUMENT                ((HHS158Status)-2)
#define HHS158_NOT_FOUND                       ((HHS158Status)-3)
#define HHS158_INVALID_STATE                   ((HHS158Status)-4)

#define HHS158_ABI_VERSION_UNSUPPORTED         ((HHS158Status)-1001)
#define HHS158_STRUCT_SIZE_INVALID             ((HHS158Status)-1002)
#define HHS158_TYPE_MISMATCH                   ((HHS158Status)-1003)
#define HHS158_EXACT_VALUE_LOSS                ((HHS158Status)-1004)
#define HHS158_HANDLE_RELEASED                 ((HHS158Status)-1005)
#define HHS158_INVALID_UTF8                     ((HHS158Status)-1006)
#define HHS158_INTEGER_WIDTH_TRUNCATION        ((HHS158Status)-1007)

#define HHS158_CAPABILITY_REQUIRED             ((HHS158Status)-2001)
#define HHS158_CAPABILITY_SCOPE_VIOLATION      ((HHS158Status)-2002)
#define HHS158_CAPABILITY_EXPIRED              ((HHS158Status)-2003)
#define HHS158_CAPABILITY_REVOKED              ((HHS158Status)-2004)

#define HHS158_STATE_ROOT_CONFLICT             ((HHS158Status)-3001)
#define HHS158_CONSTRAINT_CHAIN_COLLAPSED      ((HHS158Status)-3002)
#define HHS158_LIST_TOPOLOGY_LOSS              ((HHS158Status)-3003)
#define HHS158_PHASE_IDENTITY_VIOLATION        ((HHS158Status)-3004)
#define HHS158_TENSOR_SHAPE_MISMATCH           ((HHS158Status)-3005)
#define HHS158_DEPENDENCY_CYCLE_UNBOUNDED      ((HHS158Status)-3006)
#define HHS158_UNAUTHORIZED_MUTATION           ((HHS158Status)-3007)
#define HHS158_DUPLICATE_CONFLICTING_BINDING   ((HHS158Status)-3008)

#define HHS158_VM81_RESOURCE_BOUNDED           ((HHS158Status)-4001)
#define HHS158_PRIVATE_OPCODE                  ((HHS158Status)-4002)
#define HHS158_VM81_ADMISSION_REJECTED         ((HHS158Status)-4003)

#define HHS158_SERIALIZATION_INVALID           ((HHS158Status)-5001)
#define HHS158_UNKNOWN_AUTHORITY_FIELD         ((HHS158Status)-5002)
#define HHS158_IDENTITY_MISMATCH               ((HHS158Status)-5003)

#define HHS158_PROJECTION_CONTROL_COLLAPSE     ((HHS158Status)-6001)
#define HHS158_DELTA_REFERENCE_NONINVERTIBLE   ((HHS158Status)-6002)
#define HHS158_NONFINITE_PROJECTION            ((HHS158Status)-6003)
#define HHS158_DELTA_VERIFY_FAILED             ((HHS158Status)-6004)

#define HHS158_HASH72_RECEIPT_MISMATCH         ((HHS158Status)-7001)
#define HHS158_HASH216_IDENTITY_MISMATCH       ((HHS158Status)-7002)
#define HHS158_REPLAY_MISMATCH                 ((HHS158Status)-7003)
#define HHS158_RECEIPT_TRUNCATED               ((HHS158Status)-7004)

#define HHS158_MEMORY_BOUND                    ((HHS158Status)-8001)
#define HHS158_RECURSION_BOUND                 ((HHS158Status)-8002)
#define HHS158_OUTPUT_BOUND                    ((HHS158Status)-8003)
#define HHS158_CANCELLED                       ((HHS158Status)-8004)

const char *hhs158_status_classification(HHS158Status status);

#ifdef __cplusplus
}
#endif

#endif
