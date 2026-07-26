#include "hhs_lshpvs.h"
#include "hhs_runtime_abi.h"

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static HHSLshpvsEntry demo_entry(void) {
    HHSLshpvsEntry entry;

    memset(&entry, 0, sizeof(entry));
    (void)snprintf(
        entry.index.contract_root_hash216,
        sizeof(entry.index.contract_root_hash216),
        "PASS156-CONTRACT-ROOT"
    );
    (void)snprintf(
        entry.index.fold_path,
        sizeof(entry.index.fold_path),
        "root/loshu/center/fold-5"
    );
    entry.index.nesting_depth = 3U;
    entry.index.modulus_M = 2;
    entry.index.full_rotation_n = -7;
    entry.index.orientation_sector = 5;
    entry.index.version = 1U;
    entry.parameters.h00 = (HHSLshpvsRational){1, 1};
    entry.parameters.h01 = (HHSLshpvsComplex){{0, 1}, {0, 1}};
    entry.parameters.h11 = (HHSLshpvsRational){2, 1};
    entry.parameters.delta_tau = (HHSLshpvsRational){1, 3};
    entry.parameters.hbar = (HHSLshpvsRational){1, 1};
    entry.pre_state.cell[0] = (HHSLshpvsComplex){{1, 1}, {0, 1}};
    entry.pre_state.cell[1] = (HHSLshpvsComplex){{0, 1}, {0, 1}};
    (void)snprintf(
        entry.source_expression_root_hash216,
        sizeof(entry.source_expression_root_hash216),
        "PASS156-AST-ROOT"
    );
    (void)snprintf(
        entry.membrane_root_hash216,
        sizeof(entry.membrane_root_hash216),
        "PASS156-MEMBRANE-ROOT"
    );
    return entry;
}

static int run_verification(void) {
    HHSLshpvsEntry entry = demo_entry();
    HHSLshpvsTransitionPackage package;
    HHSLshpvsStore store;
    HHSRuntimeState runtime;
    HHSLshpvsStatus status;
    char json[2048];
    size_t written = 0U;

    status = hhs_lshpvs_entry_execute(&entry);
    if (status != HHS_LSHPVS_OK) {
        (void)fprintf(stderr, "execute:%s\n", hhs_lshpvs_status_string(status));
        return 1;
    }
    hhs_runtime_init(&runtime);
    status = hhs_lshpvs_entry_admit_vm81(&entry, &runtime);
    if (status != HHS_LSHPVS_OK) {
        (void)fprintf(stderr, "vm81:%s\n", hhs_lshpvs_status_string(status));
        return 1;
    }

    memset(&package, 0, sizeof(package));
    (void)snprintf(
        package.constructor_id,
        sizeof(package.constructor_id),
        "CREATE_LOCAL_HAMILTONIAN_ENTRY"
    );
    package.candidate = entry;
    package.vm81_authority_admission = 1U;

    hhs_lshpvs_store_init(&store);
    status = hhs_lshpvs_store_commit(&store, &package);
    if (status != HHS_LSHPVS_OK) {
        (void)fprintf(stderr, "commit:%s\n", hhs_lshpvs_status_string(status));
        return 1;
    }
    status = hhs_lshpvs_entry_serialize_json(
        &store.entries[0],
        json,
        sizeof(json),
        &written
    );
    if (status != HHS_LSHPVS_OK) {
        return 1;
    }

    (void)printf(
        "{\"contract\":\"HHS-P156.1-LSHPVS\""
        ",\"local_status\":\"%s\""
        ",\"complete_nucleus_status\":\"%s\""
        ",\"entry\":%s"
        ",\"store_count\":%zu"
        ",\"chain_hash216\":\"%s\""
        ",\"replay\":\"%s\"}\n",
        HHS_LSHPVS_STATUS_LOCAL_VERIFIED,
        HHS_LSHPVS_STATUS_INHERITED_BLOCKED,
        json,
        store.count,
        store.chain_hash216,
        hhs_lshpvs_entry_replay_verify(&store.entries[0]) == HHS_LSHPVS_OK
            ? "MATCH"
            : "MISMATCH"
    );
    (void)written;
    return 0;
}

static int run_repl(void) {
    char line[256];

    puts("HHS-P156.1-LSHPVS REPL");
    puts("commands: decompose <n> <M> | verify | quit");
    while (fgets(line, sizeof(line), stdin) != NULL) {
        int64_t n;
        int64_t modulus;
        int64_t quotient;
        int64_t residue;

        if (strncmp(line, "quit", 4U) == 0 || strncmp(line, "exit", 4U) == 0) {
            return 0;
        }
        if (strncmp(line, "verify", 6U) == 0) {
            if (run_verification() != 0) {
                return 1;
            }
            continue;
        }
        if (sscanf(line, "decompose %" SCNd64 " %" SCNd64, &n, &modulus) == 2) {
            const HHSLshpvsStatus status = hhs_lshpvs_rotation_decompose(
                n,
                modulus,
                &quotient,
                &residue
            );
            if (status == HHS_LSHPVS_OK) {
                (void)printf(
                    "{\"n\":%" PRId64 ",\"M\":%" PRId64
                    ",\"q\":%" PRId64 ",\"r\":%" PRId64 "}\n",
                    n,
                    modulus,
                    quotient,
                    residue
                );
            } else {
                (void)printf(
                    "{\"status\":\"%s\"}\n",
                    hhs_lshpvs_status_string(status)
                );
            }
            continue;
        }
        puts("{\"status\":\"UNKNOWN_COMMAND\"}");
    }
    return 0;
}

int main(int argc, char **argv) {
    const char *command = argc > 1 ? argv[1] : "verify";

    if (strcmp(command, "--help") == 0 || strcmp(command, "help") == 0) {
        puts("usage: hhs-lshpvs [verify|demo|repl]");
        return 0;
    }
    if (strcmp(command, "repl") == 0) {
        return run_repl();
    }
    if (strcmp(command, "verify") == 0 || strcmp(command, "demo") == 0) {
        return run_verification();
    }
    (void)fprintf(stderr, "unknown command: %s\n", command);
    return 2;
}
