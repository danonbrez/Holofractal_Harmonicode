#include <jni.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "hhs_runtime_abi.h"

JNIEXPORT jstring JNICALL
Java_org_hhs_pass145_NativeRuntime_statusJson(JNIEnv *env, jclass clazz) {
    (void)clazz;
    HHSRuntimeState state;
    hhs_runtime_init(&state);
    int valid = hhs_validate_abi(&state);
    char out[512];
    snprintf(out, sizeof(out),
             "{\"schema\":\"HHS_PASS145_NATIVE_RUNTIME_STATUS_V1\","
             "\"ok\":%s,\"runtime_magic\":\"%llx\","
             "\"abi\":\"%u.%u.%u\",\"state_hash72\":\"%s\","
             "\"canonical_float_authority\":false}",
             valid ? "true" : "false",
             (unsigned long long)state.runtime_magic,
             state.abi_major, state.abi_minor, state.abi_patch,
             state.state_hash72);
    return (*env)->NewStringUTF(env, out);
}

JNIEXPORT jstring JNICALL
Java_org_hhs_pass145_NativeRuntime_hash72Witness(JNIEnv *env, jclass clazz, jstring label, jstring payload) {
    (void)clazz;
    const char *a = (*env)->GetStringUTFChars(env, label, NULL);
    const char *b = (*env)->GetStringUTFChars(env, payload, NULL);
    HHSHash72RingState ring;
    hhs_hash72_ring_init(&ring);
    size_t offset = 0;
    for (const unsigned char *p = (const unsigned char *)a; *p; ++p, ++offset)
        hhs_hash72_ring_rotate(&ring, (uint8_t)(offset % 72), (int64_t)(((*p + offset) % 72) == 0 ? 72 : ((*p + offset) % 72)));
    for (const unsigned char *p = (const unsigned char *)b; *p; ++p, ++offset)
        hhs_hash72_ring_rotate(&ring, (uint8_t)(offset % 72), (int64_t)(((*p + offset) % 72) == 0 ? 72 : ((*p + offset) % 72)));
    char out[256];
    snprintf(out, sizeof(out), "{\"schema\":\"HHS_PASS145_NATIVE_HASH72_WITNESS_V1\",\"dna\":\"%s\",\"zero_sum\":%s,\"trace_count\":%llu}", ring.dna, ring.zero_sum ? "true" : "false", (unsigned long long)ring.trace_count);
    (*env)->ReleaseStringUTFChars(env, label, a);
    (*env)->ReleaseStringUTFChars(env, payload, b);
    return (*env)->NewStringUTF(env, out);
}
