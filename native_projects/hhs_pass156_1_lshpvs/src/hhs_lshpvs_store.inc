void hhs_lshpvs_store_init(HHSLshpvsStore *store) {
    if (store == NULL) {
        return;
    }
    memset(store, 0, sizeof(*store));
    store->next_sequence = 1U;
    hash216_text(DOMAIN_CHAIN, "GENESIS", store->chain_hash216);
}

const HHSLshpvsEntry *hhs_lshpvs_store_find_key(
    const HHSLshpvsStore *store,
    const char *key_hash216
) {
    size_t index;

    if (store == NULL || key_hash216 == NULL) {
        return NULL;
    }
    for (index = 0; index < store->count; ++index) {
        if (strcmp(store->entries[index].key_hash216, key_hash216) == 0) {
            return &store->entries[index];
        }
    }
    return NULL;
}

const HHSLshpvsEntry *hhs_lshpvs_store_find_index(
    const HHSLshpvsStore *store,
    const char *fold_path,
    int64_t modulus,
    int64_t full_rotation,
    uint64_t version
) {
    size_t index;

    if (store == NULL || fold_path == NULL) {
        return NULL;
    }
    for (index = 0; index < store->count; ++index) {
        const HHSLshpvsEntry *entry = &store->entries[index];
        if (strcmp(entry->index.fold_path, fold_path) == 0 &&
            entry->index.modulus_M == modulus &&
            entry->index.full_rotation_n == full_rotation &&
            entry->index.version == version) {
            return entry;
        }
    }
    return NULL;
}

static HHSLshpvsStatus validate_package(
    const HHSLshpvsStore *store,
    const HHSLshpvsTransitionPackage *package
) {
    size_t index;
    int previous_found = 0;

    if (store == NULL || package == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    if (package->vm81_authority_admission == 0U ||
        package->candidate.vm81_admitted == 0U ||
        package->candidate.key_hash216[0] == '\0') {
        return HHS_LSHPVS_VM81_REJECTED;
    }
    if (package->candidate.hermitian_verified == 0U ||
        package->candidate.norm_verified == 0U ||
        package->candidate.rotation_reconstruction_verified == 0U) {
        return HHS_LSHPVS_BATCH_REJECTED;
    }
    if (package->expected_version == UINT64_MAX ||
        package->candidate.index.version != package->expected_version + 1U) {
        return HHS_LSHPVS_VERSION_CONFLICT;
    }

    for (index = 0; index < store->count; ++index) {
        const HHSLshpvsEntry *entry = &store->entries[index];
        if (strcmp(entry->key_hash216, package->candidate.key_hash216) == 0) {
            return HHS_LSHPVS_VERSION_CONFLICT;
        }
        if (strcmp(entry->index.fold_path, package->candidate.index.fold_path) == 0 &&
            entry->index.version == package->candidate.index.version) {
            return HHS_LSHPVS_VERSION_CONFLICT;
        }
        if (package->expected_version != 0U &&
            strcmp(entry->index.fold_path, package->candidate.index.fold_path) == 0 &&
            entry->index.version == package->expected_version) {
            previous_found = 1;
        }
    }
    if (package->expected_version != 0U && previous_found == 0) {
        return HHS_LSHPVS_VERSION_CONFLICT;
    }
    return HHS_LSHPVS_OK;
}

static void compute_package_hash(HHSLshpvsTransitionPackage *package) {
    char payload[1024];

    (void)snprintf(
        payload,
        sizeof(payload),
        "%s|%s|%" PRIu64 "|%s|%s",
        package->constructor_id,
        package->candidate.key_hash216,
        package->expected_version,
        package->candidate.state_hash216,
        package->candidate.hash72_head
    );
    hash216_text(DOMAIN_PACKAGE, payload, package->package_hash216);
}

HHSLshpvsStatus hhs_lshpvs_store_commit(
    HHSLshpvsStore *store,
    const HHSLshpvsTransitionPackage *input
) {
    HHSLshpvsTransitionPackage package;
    HHSLshpvsEntry entry;
    HHSLshpvsStatus status;
    char prior_chain[HHS_LSHPVS_HASH216_STRLEN];
    char chain_payload[1024];

    if (store == NULL || input == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    if (store->count >= HHS_LSHPVS_MAX_ENTRIES) {
        return HHS_LSHPVS_STORE_FULL;
    }

    package = *input;
    compute_package_hash(&package);
    status = validate_package(store, &package);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }

    entry = package.candidate;
    entry.committed = 1U;
    entry.committed_sequence = store->next_sequence;
    ++store->next_sequence;
    store->entries[store->count] = entry;
    ++store->count;

    memcpy(prior_chain, store->chain_hash216, sizeof(prior_chain));
    (void)snprintf(
        chain_payload,
        sizeof(chain_payload),
        "%s|%s|%s|%" PRIu64,
        prior_chain,
        package.package_hash216,
        entry.key_hash216,
        entry.committed_sequence
    );
    hash216_text(DOMAIN_CHAIN, chain_payload, store->chain_hash216);
    return HHS_LSHPVS_OK;
}

HHSLshpvsStatus hhs_lshpvs_store_commit_batch(
    HHSLshpvsStore *store,
    const HHSLshpvsTransitionPackage *packages,
    size_t package_count
) {
    HHSLshpvsStore candidate;
    size_t index;

    if (store == NULL || (packages == NULL && package_count != 0U)) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    if (package_count > HHS_LSHPVS_MAX_ENTRIES - store->count) {
        return HHS_LSHPVS_STORE_FULL;
    }

    candidate = *store;
    for (index = 0; index < package_count; ++index) {
        const HHSLshpvsStatus status = hhs_lshpvs_store_commit(
            &candidate,
            &packages[index]
        );
        if (status != HHS_LSHPVS_OK) {
            return HHS_LSHPVS_BATCH_REJECTED;
        }
    }
    *store = candidate;
    return HHS_LSHPVS_OK;
}

HHSLshpvsStatus hhs_lshpvs_entry_serialize_json(
    const HHSLshpvsEntry *entry,
    char *out,
    size_t out_size,
    size_t *written
) {
    int count;

    if (entry == NULL || out == NULL || out_size == 0U) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    if (!text_is_canonical(entry->index.fold_path)) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }

    count = snprintf(
        out,
        out_size,
        "{\"schema\":\"HHS_P156_1_LSHPVS_ENTRY_V1\""
        ",\"key_hash216\":\"%s\""
        ",\"fold_path\":\"%s\""
        ",\"nesting_depth\":%" PRIu32
        ",\"modulus_M\":%" PRId64
        ",\"full_rotation_n\":%" PRId64
        ",\"overflow_quotient_q\":%" PRId64
        ",\"local_residue_r\":%" PRId64
        ",\"version\":%" PRIu64
        ",\"hermitian_verified\":%s"
        ",\"norm_verified\":%s"
        ",\"rotation_reconstruction_verified\":%s"
        ",\"vm81_admitted\":%s"
        ",\"hash72_head\":\"%s\""
        ",\"state_hash216\":\"%s\""
        ",\"committed\":%s"
        ",\"committed_sequence\":%" PRIu64 "}",
        entry->key_hash216,
        entry->index.fold_path,
        entry->index.nesting_depth,
        entry->index.modulus_M,
        entry->index.full_rotation_n,
        entry->index.overflow_quotient_q,
        entry->index.local_residue_r,
        entry->index.version,
        entry->hermitian_verified != 0U ? "true" : "false",
        entry->norm_verified != 0U ? "true" : "false",
        entry->rotation_reconstruction_verified != 0U ? "true" : "false",
        entry->vm81_admitted != 0U ? "true" : "false",
        entry->hash72_head,
        entry->state_hash216,
        entry->committed != 0U ? "true" : "false",
        entry->committed_sequence
    );
    if (count < 0 || (size_t)count >= out_size) {
        return HHS_LSHPVS_SERIALIZATION_BOUNDED;
    }
    if (written != NULL) {
        *written = (size_t)count;
    }
    return HHS_LSHPVS_OK;
}

HHSLshpvsStatus hhs_lshpvs_entry_replay_verify(
    const HHSLshpvsEntry *entry
) {
    HHSLshpvsEntry replay;
    HHSLshpvsStatus status;

    if (entry == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    replay = *entry;
    replay.vm81_admitted = 0U;
    replay.hash72_head[0] = '\0';
    replay.committed = 0U;
    replay.committed_sequence = 0U;

    status = hhs_lshpvs_entry_execute(&replay);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    if (strcmp(replay.key_hash216, entry->key_hash216) != 0 ||
        strcmp(replay.state_hash216, entry->state_hash216) != 0 ||
        !matrix_equal(&replay.propagator, &entry->propagator) ||
        !matrix_equal(&replay.winding, &entry->winding) ||
        !matrix_equal(
            &replay.reconstructed_rotation,
            &entry->reconstructed_rotation
        )) {
        return HHS_LSHPVS_REPLAY_MISMATCH;
    }
    return HHS_LSHPVS_OK;
}

const char *hhs_lshpvs_status_string(HHSLshpvsStatus status) {
    static const char *const names[] = {
        "OK",
        "INVALID_ARGUMENT",
        "DIVIDE_BY_ZERO",
        "OVERFLOW",
        "NON_HERMITIAN",
        "SINGULAR_PROPAGATOR",
        "NORM_MISMATCH",
        "ROTATION_RECONSTRUCTION_MISMATCH",
        "VM81_REJECTED",
        "STORE_FULL",
        "VERSION_CONFLICT",
        "NOT_FOUND",
        "SERIALIZATION_BOUNDED",
        "BATCH_REJECTED",
        "REPLAY_MISMATCH"
    };

    if ((unsigned)status >= sizeof(names) / sizeof(names[0])) {
        return "UNKNOWN";
    }
    return names[status];
}
