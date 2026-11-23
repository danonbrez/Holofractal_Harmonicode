/* Standalone exhaustive native 81x64 I001 representation membrane.
 * No source/parent/signer bypass: this only verifies exact ingress/egress bytes.
 */
#include "hhs_runtime_exact_abi.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x,msg) do{if(!(x)){fprintf(stderr,"FAIL:%s\n",msg);return 1;}}while(0)

static uint8_t canonical[5184U],malformed[5184U];
static uint8_t offsets[81U],recovered[81U],rejected[81U];
static uint8_t shared[5184U+81U];
static union {
 size_t aligned_size;
 uint8_t source_digits[81U];
} alias_length_source;
static union {
 size_t aligned_size;
 uint8_t encoded_bytes[5184U];
} alias_length_destination;

static int entirely_zero(const uint8_t *buffer,size_t count) {
 size_t i;
 for(i=0U;i<count;++i) if(buffer[i]!=0U) return 0;
 return 1;
}
static int entirely_equal(const uint8_t *buffer,size_t count,uint8_t value) {
 size_t i;
 for(i=0U;i<count;++i) if(buffer[i]!=value) return 0;
 return 1;
}
int main(int argc,char **argv) {
 size_t pos,digit,index,out_length=0U;
 FILE *fixture=NULL;
 CHECK(argc==1 || argc==2,"optional independent Python reference carrier");
 if(argc==2) {
  size_t n;
  fixture=fopen(argv[1],"rb");
  CHECK(fixture!=NULL,"Python reference fixture opened");
  n=fread(malformed,1U,sizeof(malformed),fixture);
  CHECK(!ferror(fixture) && fclose(fixture)==0 && n==5184U,
        "cross-language fixture exact 5184 bytes");
  CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
     malformed,5184U,recovered)==HHS_EXACT_STATUS_OK,
     "native parser recognizes inherited Python normalized carrier");
  CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(
     recovered,canonical,sizeof(canonical),&out_length)==HHS_EXACT_STATUS_OK &&
     out_length==5184U && memcmp(canonical,malformed,5184U)==0,
     "C parse->emit preserves independent Python I001 carrier exactly");
 }
 memset(offsets,0,sizeof(offsets));
 for(pos=0U;pos<81U;++pos) {
  for(digit=0U;digit<9U;++digit) {
   offsets[pos]=(uint8_t)digit;
   CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(
      offsets,canonical,sizeof(canonical),&out_length)==HHS_EXACT_STATUS_OK,
      "all 729 positioned exact offset encodings");
   CHECK(out_length==5184U,"fixed serializer width");
   memset(recovered,0xA5,sizeof(recovered));
   CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
      canonical,5184U,recovered)==HHS_EXACT_STATUS_OK,
      "all 729 positioned exact offset decodings");
   CHECK(memcmp(recovered,offsets,sizeof(offsets))==0,
      "all 729 byte-identical cell-position inverse roundtrips");
   offsets[pos]=0U;
  }
 }
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(
   offsets,canonical,sizeof(canonical),&out_length)==HHS_EXACT_STATUS_OK,
   "exact zero state emission");
 for(pos=0U;pos<81U;++pos) {
  /* Every source-cell can carry a malformed final numerator digit.
   * Reject and zero ALL returned offsets, never leak positions 0..pos-1. */
  memcpy(malformed,canonical,5184U);
  malformed[64U*pos+20U]='9';
  memset(rejected,0xA5,sizeof(rejected));
  CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
     malformed,5184U,rejected)!=HHS_EXACT_STATUS_OK,
     "invalid 9 digit in any tensor position rejected");
  CHECK(entirely_zero(rejected,sizeof(rejected)),
     "invalid cell never emits partially decoded offsets");
  /* Every source-cell must have canonical nonzero rational denominator. */
  memcpy(malformed,canonical,5184U);
  malformed[64U*pos+41U]='0';
  memset(rejected,0xA5,sizeof(rejected));
  CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
     malformed,5184U,rejected)!=HHS_EXACT_STATUS_OK &&
     entirely_zero(rejected,sizeof(rejected)),
     "zero denominator in any of 81 cells rejected without partial state");
  /* The exponent must be exactly +0 in this particular I001 profile. */
  memcpy(malformed,canonical,5184U);
  malformed[64U*pos+63U]='1';
  memset(rejected,0xA5,sizeof(rejected));
  CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
     malformed,5184U,rejected)!=HHS_EXACT_STATUS_OK &&
     entirely_zero(rejected,sizeof(rejected)),
     "noncanonical exponent in any cell rejected");
 }
 memcpy(malformed,canonical,5184U);
 memset(rejected,0xA5,sizeof(rejected));
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
   malformed,5183U,rejected)!=HHS_EXACT_STATUS_OK &&
   entirely_zero(rejected,sizeof(rejected)),
   "incorrect carrier width rejected atomically");

 memset(shared,0xA5,sizeof(shared));
 memcpy(shared,canonical,5184U);
 /* Deliberately overlap source and output at every offset from 0..80,
  * without permitting a write to either buffer. */
 for(index=0U;index<=81U;++index) {
  memcpy(shared,canonical,5184U);
  CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
     shared,5184U,shared+index)==HHS_EXACT_STATUS_INVALID_ARGUMENT,
     "overlapping input/output rejected without writing");
  CHECK(memcmp(shared,canonical,5184U)==0,
     "rejected overlap never mutates original tensor carrier");
 }
 memset(offsets,0,sizeof(offsets));
 offsets[80]=9U;
 memset(canonical,0xA5,sizeof(canonical));
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(
   offsets,canonical,sizeof(canonical),&out_length)!=HHS_EXACT_STATUS_OK &&
   entirely_equal(canonical,sizeof(canonical),0xA5U),
   "last invalid offset rejected before any output byte");
 offsets[80]=0U;
 /* out_length aliases source offsets: old implementation wrote 5184 before
  * reading the offsets, which could corrupt their bytes silently. */
 memset(&alias_length_source,0,sizeof(alias_length_source));
 memset(canonical,0xA5,sizeof(canonical));
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(
    alias_length_source.source_digits,canonical,sizeof(canonical),
    &alias_length_source.aligned_size)==HHS_EXACT_STATUS_INVALID_ARGUMENT,
    "length pointer inside source offsets rejected");
 CHECK(entirely_zero(alias_length_source.source_digits,81U) &&
       entirely_equal(canonical,sizeof(canonical),0xA5U),
       "length alias rejection never mutates source or destination");

 /* out_length aliases encoded output: old code could produce a mismatched
  * exact string by overwriting a segment of the emitted token stream. */
 memset(&alias_length_destination,0xA5,sizeof(alias_length_destination));
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(
    offsets,alias_length_destination.encoded_bytes,
    sizeof(alias_length_destination.encoded_bytes),
    &alias_length_destination.aligned_size)==HHS_EXACT_STATUS_INVALID_ARGUMENT,
    "length pointer inside emitted carrier rejected");
 CHECK(entirely_equal(alias_length_destination.encoded_bytes,5184U,0xA5U),
       "length alias rejection preserves all destination bytes");

 /* A malformed last digit must leave both the output buffer and the
  * independent required-length field untouched. */
 offsets[80]=9U;
 out_length=SIZE_MAX-42U;
 memset(canonical,0xA5,sizeof(canonical));
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(
    offsets,canonical,sizeof(canonical),&out_length)==
        HHS_EXACT_STATUS_INVARIANT_FAILURE,
    "invalid last digit rejected without publishing a length");
 CHECK(out_length==SIZE_MAX-42U &&
       entirely_equal(canonical,sizeof(canonical),0xA5U),
       "malformed input never changes either output parameter");
 offsets[80]=0U;
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
   NULL,5184U,rejected)==HHS_EXACT_STATUS_INVALID_ARGUMENT &&
   entirely_zero(rejected,sizeof(rejected)),
   "null encoded input clears independent outputs");
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_parse(
   canonical,5184U,NULL)==HHS_EXACT_STATUS_INVALID_ARGUMENT,
   "null output pointer rejected");

 puts("{\"schema\":\"HHS_PASS220_I001_NATIVE_INVERSE_EXHAUSTIVE_V1\","
      "\"position_digit_roundtrips\":729,"
      "\"invalid_position_signatures\":243,"
      "\"overlap_denials\":82,"
      "\"fixed_bytes\":5184,"
      "\"python_fixture_roundtrip_supported\":true,"
      "\"no_partial_state_on_invalid\":true,"
      "\"signed_vm81_admission\":false,"
      "\"canonical_hash72_hash216_receipts\":false}");
 return 0;
}
