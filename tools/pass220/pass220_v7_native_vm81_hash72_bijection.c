/* Pass220 V7: native C11 exact 5184-position ADDRESS BIJECTION only.
 * Do not treat the ordered 3x3 denominator as a commutative matrix or claim
 * canonical VM81 execution/Hash72 generation from this preflight.
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char SOURCE[]="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))\n";
static const char *const ORDERED_CELLS[9]={
    "yx","y+w","wx",
    "-xy-wz","x+y-z-w+xy+yx-zw-wz","-zw-yx",
    "xy","x-z","zw"
};

int main(int argc,char **argv){
    unsigned char buffer[256],digest[SHA256_DIGEST_LENGTH];
    unsigned char seen[72][72]={{0}};
    FILE *f;
    size_t n,site,subcell,bit,visited=0U,j;
    const char *cursor=SOURCE;
    if(argc!=2 || (f=fopen(argv[1],"rb"))==NULL){fputs("V7_READ_ERROR\n",stderr);return 2;}
    n=fread(buffer,1U,sizeof(buffer),f);
    if(ferror(f) || !feof(f)){fclose(f);fputs("V7_INPUT_TOO_LONG\n",stderr);return 2;}
    fclose(f);
    if(n!=sizeof(SOURCE)-1U || memcmp(buffer,SOURCE,n)!=0){
        fputs("V7_EXACT_SOURCE_MISMATCH\n",stderr);return 1;
    }
    if(SHA256(buffer,n,digest)==NULL)return 1;
    printf("source_sha256=");
    for(j=0U;j<SHA256_DIGEST_LENGTH;j++)printf("%02x",(unsigned)digest[j]);
    putchar('\n');
    for(j=0U;j<9U;j++){
        const char *found=strstr(cursor,ORDERED_CELLS[j]);
        if(found==NULL){fputs("V7_CELL_ADDRESS_DRIFT\n",stderr);return 1;}
        printf("ordered_cell_%zu_byte_offset=%zu\n",j,(size_t)(found-SOURCE));
        cursor=found+strlen(ORDERED_CELLS[j]);
    }
    for(site=0U;site<9U;site++){
        for(subcell=0U;subcell<9U;subcell++){
            for(bit=0U;bit<64U;bit++){
                const size_t vm81=site*9U+subcell;
                const size_t position=vm81*64U+bit;
                const size_t row72=position/72U;
                const size_t col72=position%72U;
                const size_t inverse_vm81=(row72*72U+col72)/64U;
                const size_t inverse_bit=(row72*72U+col72)%64U;
                if(row72>=72U || col72>=72U || seen[row72][col72] ||
                   inverse_vm81!=vm81 || inverse_bit!=bit)return 1;
                seen[row72][col72]=1U;
                visited++;
            }
        }
    }
    if(visited!=81U*64U || visited!=72U*72U)return 1;
    for(j=0U;j<72U*72U;j++)
        if(!seen[j/72U][j%72U])return 1;
    puts("ordered_3x3_source_check=PASS");
    puts("vm81_hash72_position_roundtrip=PASS");
    printf("bijection_positions=%zu\n",visited);
    puts("native_ordered_matrix_quotient_evaluation=UNRESOLVED");
    puts("pqc_signed_vm81_admission_verified=0");
    puts("hash72_hash216_canonical_transition_verified=0");
    return 0;
}
