from pathlib import Path

from hhs_runtime.pass174 import Pass174Runtime, PersistentEncryptedVectorStore, build_legacy_manifest


def _foundation(tmp_path: Path):
    (tmp_path / "HHS_PASS_001_GENESIS.md").write_text("pass 1\n")
    (tmp_path / "HHS_PASS_163_VMRC.md").write_text("pass 163\n")
    (tmp_path / "HHS_PASS_173_INSTALL_VERIFY.md").write_text("pass 173\n")
    return build_legacy_manifest(tmp_path)


def test_persistent_encrypted_vector_retrieval_survives_restart(tmp_path):
    manifest = _foundation(tmp_path)
    database = tmp_path / "state" / "vectors.sqlite3"
    key_path = tmp_path / "state" / "vectors.key"

    producer_store = PersistentEncryptedVectorStore(database, key_path=key_path)
    producer = Pass174Runtime(legacy_manifest=manifest, vector_store=producer_store)
    direct = producer.execute(thread=5, writes={1: 1, 9: 1, 80: -1})
    expected_snapshot = producer.vmrc.snapshot().to_bytes()
    expected_root = producer.vmrc.state_hash72
    assert direct["path"] == "DIRECT_RUNTIME"
    assert producer_store.storage_status()["objects"] == 1
    assert producer_store.storage_status()["plaintext_persisted"] is False
    producer_store.close()

    consumer_store = PersistentEncryptedVectorStore(database, key_path=key_path)
    consumer = Pass174Runtime(legacy_manifest=manifest, vector_store=consumer_store)
    retrieved = consumer.execute(thread=5, writes={1: 1, 9: 1, 80: -1})
    assert retrieved["path"] == "RETRIEVAL"
    assert consumer.vmrc.snapshot().to_bytes() == expected_snapshot
    assert consumer.vmrc.state_hash72 == expected_root
    assert consumer.replay()["classification"] == "HHS_PASS_174_REPLAY_CLOSED"
    consumer_store.close()


def test_key_file_is_created_with_owner_only_permissions(tmp_path):
    database = tmp_path / "vectors.sqlite3"
    key_path = tmp_path / "vectors.key"
    store = PersistentEncryptedVectorStore(database, key_path=key_path)
    mode = key_path.stat().st_mode & 0o777
    assert mode == 0o600
    store.close()
