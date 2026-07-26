#include "hhs_lshpvs.h"
#include "hhs_runtime_abi.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static HHSLshpvsEntry make_entry(const char *path,int64_t n,int64_t M,uint64_t version) {
    HHSLshpvsEntry e; memset(&e,0,sizeof(e));
    snprintf(e.index.contract_root_hash216,sizeof(e.index.contract_root_hash216),"ROOT-156");
    snprintf(e.index.fold_path,sizeof(e.index.fold_path),"%s",path);
    e.index.nesting_depth=2; e.index.modulus_M=M; e.index.full_rotation_n=n; e.index.orientation_sector=5; e.index.version=version;
    e.parameters.h00=(HHSLshpvsRational){1,1};
    e.parameters.h01=(HHSLshpvsComplex){{0,1},{0,1}};
    e.parameters.h11=(HHSLshpvsRational){2,1};
    e.parameters.delta_tau=(HHSLshpvsRational){1,3};
    e.parameters.hbar=(HHSLshpvsRational){1,1};
    e.pre_state.cell[0]=(HHSLshpvsComplex){{1,1},{0,1}};
    e.pre_state.cell[1]=(HHSLshpvsComplex){{0,1},{0,1}};
    snprintf(e.source_expression_root_hash216,sizeof(e.source_expression_root_hash216),"AST-ROOT");
    snprintf(e.membrane_root_hash216,sizeof(e.membrane_root_hash216),"MEMBRANE-ROOT");
    return e;
}

static void execute_and_admit(HHSLshpvsEntry *e,HHSRuntimeState *runtime) {
    assert(hhs_lshpvs_entry_execute(e)==HHS_LSHPVS_OK);
    assert(e->hermitian_verified&&e->norm_verified&&e->rotation_reconstruction_verified);
    assert(hhs_lshpvs_entry_admit_vm81(e,runtime)==HHS_LSHPVS_OK);
    assert(e->vm81_admitted&&strlen(e->hash72_head)==72);
}

int main(void) {
    int64_t q=0,r=0;
    assert(hhs_lshpvs_rotation_decompose(12,5,&q,&r)==HHS_LSHPVS_OK&&q==2&&r==2);
    assert(hhs_lshpvs_rotation_decompose(-7,5,&q,&r)==HHS_LSHPVS_OK&&q==-2&&r==3);
    assert(hhs_lshpvs_rotation_decompose(1,0,&q,&r)==HHS_LSHPVS_INVALID_ARGUMENT);

    HHSRuntimeState runtime; hhs_runtime_init(&runtime);
    HHSLshpvsEntry e=make_entry("root/fold-a",-7,2,1); execute_and_admit(&e,&runtime);
    assert(hhs_lshpvs_entry_replay_verify(&e)==HHS_LSHPVS_OK);

    HHSLshpvsStore store; hhs_lshpvs_store_init(&store);
    HHSLshpvsTransitionPackage p; memset(&p,0,sizeof(p)); snprintf(p.constructor_id,sizeof(p.constructor_id),"CREATE_LOCAL_HAMILTONIAN_ENTRY"); p.candidate=e; p.vm81_authority_admission=1;
    assert(hhs_lshpvs_store_commit(&store,&p)==HHS_LSHPVS_OK);
    assert(store.count==1&&hhs_lshpvs_store_find_key(&store,e.key_hash216)!=NULL);
    assert(hhs_lshpvs_store_find_index(&store,"root/fold-a",2,-7,1)!=NULL);
    assert(hhs_lshpvs_store_commit(&store,&p)==HHS_LSHPVS_VERSION_CONFLICT);

    HHSLshpvsEntry a=make_entry("root/fold-b",8,5,1),b=make_entry("root/fold-c",9,5,1);
    execute_and_admit(&a,&runtime); execute_and_admit(&b,&runtime);
    HHSLshpvsTransitionPackage batch[2]; memset(batch,0,sizeof(batch));
    snprintf(batch[0].constructor_id,sizeof(batch[0].constructor_id),"FOLD_COMPOSE"); batch[0].candidate=a; batch[0].vm81_authority_admission=1;
    snprintf(batch[1].constructor_id,sizeof(batch[1].constructor_id),"FOLD_COMPOSE"); batch[1].candidate=b; batch[1].vm81_authority_admission=1;
    assert(hhs_lshpvs_store_commit_batch(&store,batch,2)==HHS_LSHPVS_OK&&store.count==3);
    size_t before=store.count; batch[1].candidate.vm81_admitted=0;
    assert(hhs_lshpvs_store_commit_batch(&store,batch,2)==HHS_LSHPVS_BATCH_REJECTED&&store.count==before);

    HHSLshpvsEntry invalid=make_entry("root/invalid",1,5,1); invalid.parameters.hbar.num=0;
    assert(hhs_lshpvs_entry_execute(&invalid)==HHS_LSHPVS_DIVIDE_BY_ZERO);
    invalid=make_entry("root/unadmitted",1,5,1); assert(hhs_lshpvs_entry_execute(&invalid)==HHS_LSHPVS_OK);
    HHSLshpvsTransitionPackage bad; memset(&bad,0,sizeof(bad)); bad.candidate=invalid;
    assert(hhs_lshpvs_store_commit(&store,&bad)==HHS_LSHPVS_VM81_REJECTED);

    char json[2048]; size_t written=0; assert(hhs_lshpvs_entry_serialize_json(&store.entries[0],json,sizeof(json),&written)==HHS_LSHPVS_OK&&written>0);
    assert(strstr(json,"\"overflow_quotient_q\":-4")!=NULL);
    assert(hhs_lshpvs_entry_serialize_json(&store.entries[0],json,8,&written)==HHS_LSHPVS_SERIALIZATION_BOUNDED);

    puts("HHS_PASS_156_1_LOCAL_CORE_VERIFIED");
    puts("positive=14 negative=8 replay=MATCH vm81=ADMITTED hash72=CLOSED hash216=INDEXED");
    puts("complete_nucleus=HHS_PASS_156_1_INCOMPLETE inherited_blockers=P154,P155,P156");
    return 0;
}
