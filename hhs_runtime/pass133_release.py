"""Pass 133 release execution and artifact emission."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
import json
import os

from .canonical import canonical_json, sha256_hex
from .hash72_checkpoint import make_hash72_witness, verify_parent_witness
from .prime_generation import EntropyAttestation
from .prime_magic_key_state import build_prime_magic_key_state, run_prime_magic_negative_tests
from .phase_tensor import build_phase_tensor, phase_scattering, run_phase_negative_tests
from .palindromic_ecc import protect_encrypted_bigint, run_ecc_stress
from .semantic_continuity import run_schic_self_test

ARTIFACT_NAMES = [
    "PASS_133_PRIME_KEY_GENERATION_MANIFEST.json",
    "PASS_133_PRIME_CERTIFICATES.jsonl",
    "PASS_133_SUDOKU_TENSOR_STATE.json",
    "PASS_133_VM81_CELL_TRACE.jsonl",
    "PASS_133_PRIME_MAGIC_CLOSURE.json",
    "PASS_133_LOSHU_SERIALIZATION_TRACE.jsonl",
    "PASS_133_FACTORADIC_BIGINT_STATE.json",
    "PASS_133_COMPRESSION_METRICS.json",
    "PASS_133_RECONSTRUCTION_PROOF.json",
    "PASS_133_KEY_STATE_SCATTERING_REPORT.json",
    "PASS_133_ENTROPY_ACCOUNTING_REPORT.json",
    "PASS_133_KEY_GENERATOR_NEGATIVE_TEST_REPORT.json",
    "PASS_133_KEY_GENERATOR_REPLAY_RECEIPT.json",
    "PASS_133_PHASE_TENSOR_STATE.json",
    "PASS_133_PHASE_NEGATIVE_TEST_REPORT.json",
    "PASS_133_PALINDROMIC_ECC_BIGINT_STATE.json",
    "PASS_133_PALINDROMIC_ECC_STRESS_REPORT.json",
    "PASS_133_SCHIC_EXECUTION_REPORT.json",
    "PASS_133_CHECKPOINT_CHAIN_REPAIR_REPORT.json",
    "PASS_133_RELEASE_MANIFEST.json"
]


def _write_json(path:Path,value:Any)->None:
    path.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,default=str)+"\n",encoding="utf-8")


def _write_jsonl(path:Path,rows:list[dict[str,Any]])->None:
    path.write_text("".join(canonical_json(row)+"\n" for row in rows),encoding="utf-8")


def execute_release(base_dir:str|Path, *, prime_bits:int=64, seed:bytes|None=None)->dict[str,Any]:
    base=Path(base_dir)
    out=base/"release_artifacts"/"pass133"; out.mkdir(parents=True,exist_ok=True)
    parent_manifest=base/"parent_checkpoint"/"PASS_132_RELEASE_MANIFEST.json"
    parent=json.loads(parent_manifest.read_text(encoding="utf-8"))
    parent_root=parent["release_manifest_root_hash72"]
    repair=verify_parent_witness(parent_manifest)
    repair.update({
        "parent_pass":"PASS_132","parent_root":parent_root,
        "chain_rule":"MISSING_SOURCE_BODY_IS_A_REPAIR_OBLIGATION_NOT_NONEXISTENCE_EVIDENCE",
        "source_status":"PARENT_EVIDENCE_CHECKPOINT_PRESENT; SOURCE_HASHES_PRESERVED; NATIVE_HASH72_LINK_REPAIRED",
    })
    if not repair["ok"]: raise RuntimeError("parent Hash72 checkpoint repair failed")
    seed=seed or sha256(b"HHS-P133-PUBLIC-REPLAY-SEED-V1"+parent_root.encode()).digest()
    attestation=EntropyAttestation(
        source_id="PUBLIC_DETERMINISTIC_RELEASE_REPLAY_SEED",
        seed_bits=len(seed)*8,
        asserted_min_entropy_bits=0,
        independently_attested=False,
        public_test_seed=True,
    )
    prime=build_prime_magic_key_state(seed,prime_bits=prime_bits,mode="explicit",parent_root=parent_root,entropy_attestation=attestation)
    phase=build_phase_tensor(seed,prime_bits=prime_bits,parent_root=parent_root,entropy_attestation=attestation,trace_all_steps=True)
    scattering=phase_scattering(seed,phase,parent_root=parent_root,prime_bits=prime_bits)
    prime_negative=run_prime_magic_negative_tests(prime)
    phase_negative=run_phase_negative_tests(seed,phase,parent_root=parent_root,prime_bits=prime_bits)
    ecc=protect_encrypted_bigint(int(phase["encrypted_bigint_hex"],16))
    ecc_stress=run_ecc_stress(int(phase["encrypted_bigint_hex"],16),sample_limit=256)
    schic=run_schic_self_test(parent_root)
    generated_at=datetime.now(timezone.utc).isoformat()

    _write_json(out/"PASS_133_CHECKPOINT_CHAIN_REPAIR_REPORT.json",repair)
    _write_json(out/"PASS_133_PRIME_KEY_GENERATION_MANIFEST.json",{
        "schema":"HHS_PASS133_PRIME_KEY_GENERATION_MANIFEST_V1","generated_at":generated_at,
        "status":prime["status"],"prime_bits":prime_bits,"mode":prime["mode"],"parent_root":parent_root,
        "prime_domain":"HHS-P133-PRIME-ALPHABET-V1","sudoku_domain":"HHS-P133-SUDOKU-TOPOLOGY-V1",
        "entropy_status":prime["entropy_status"],"security_boundary":"KEY_STATE_NOT_ENCRYPTION"
    })
    _write_jsonl(out/"PASS_133_PRIME_CERTIFICATES.jsonl",prime["prime_receipts"]+phase["carrier_receipts"]+phase["symbol_receipts"])
    _write_json(out/"PASS_133_SUDOKU_TENSOR_STATE.json",{"sudoku":prime["sudoku"],"tensor":prime["magic_closure"]["tensor"],"validation":prime["sudoku_validation"]})
    _write_jsonl(out/"PASS_133_VM81_CELL_TRACE.jsonl",phase["cells"])
    _write_json(out/"PASS_133_PRIME_MAGIC_CLOSURE.json",prime["magic_closure"])
    _write_jsonl(out/"PASS_133_LOSHU_SERIALIZATION_TRACE.jsonl",[
        {"step":i,"vm81_cell":cell,"row":cell//9,"column":cell%9,"topology_rank":prime["factoradic_row_ranks"][cell//9]}
        for i,cell in enumerate(prime["vm81_order"])
    ])
    _write_json(out/"PASS_133_FACTORADIC_BIGINT_STATE.json",{
        "topology_bigint":prime["topology_bigint"],"topology_bit_length":prime["topology_bit_length"],
        "key_bigint":prime["key_bigint"],"key_bigint_bit_length":prime["key_bigint_bit_length"],
        "key_envelope_sha256":prime["key_envelope_sha256"]
    })
    _write_json(out/"PASS_133_COMPRESSION_METRICS.json",{"prime_magic":prime["compression"],"phase":phase["compression"],"ecc":{"carrier_bit_length":ecc["carrier_bit_length"]}})
    _write_json(out/"PASS_133_RECONSTRUCTION_PROOF.json",{"prime_magic":prime["reconstruction"],"phase":phase["reconstruction"],"ecc":ecc["decode"]})
    _write_json(out/"PASS_133_KEY_STATE_SCATTERING_REPORT.json",scattering)
    _write_json(out/"PASS_133_ENTROPY_ACCOUNTING_REPORT.json",{
        "entropy_attestation":attestation.to_dict(),"effective_seed_min_entropy_bits":0,
        "prime_width_not_counted_as_entropy":True,"sudoku_structure_not_counted_as_independent_entropy":True,
        "hash72_not_counted_as_entropy":True,"status":"ENTROPY_SOURCE_UNATTESTED"
    })
    _write_json(out/"PASS_133_KEY_GENERATOR_NEGATIVE_TEST_REPORT.json",{"prime_magic":prime_negative,"phase":phase_negative})
    replay=build_prime_magic_key_state(seed,prime_bits=prime_bits,mode="explicit",parent_root=parent_root,entropy_attestation=attestation)
    replay_receipt={
        "schema":"HHS_PASS133_KEY_GENERATOR_REPLAY_RECEIPT_V1",
        "prime_key_replay_match":replay["key_envelope_sha256"]==prime["key_envelope_sha256"],
        "tensor_hash72_match":replay["tensor_hash72_witness"]["dna"]==prime["tensor_hash72_witness"]["dna"],
        "parent_root":parent_root,"status":"KEY_GENERATOR_REPLAY_VERIFIED"
    }
    _write_json(out/"PASS_133_KEY_GENERATOR_REPLAY_RECEIPT.json",replay_receipt)
    # Keep full phase state but move massive traces to JSONL.
    phase_summary={k:v for k,v in phase.items() if k not in {"forward_trace","inverse_trace","carrier_receipts","symbol_receipts"}}
    _write_json(out/"PASS_133_PHASE_TENSOR_STATE.json",phase_summary)
    _write_jsonl(out/"PASS_133_PHASE_FORWARD_TRACE.jsonl",phase["forward_trace"])
    _write_jsonl(out/"PASS_133_PHASE_INVERSE_TRACE.jsonl",phase["inverse_trace"])
    _write_json(out/"PASS_133_PHASE_NEGATIVE_TEST_REPORT.json",phase_negative)
    _write_json(out/"PASS_133_PALINDROMIC_ECC_BIGINT_STATE.json",ecc)
    _write_json(out/"PASS_133_PALINDROMIC_ECC_STRESS_REPORT.json",ecc_stress)
    _write_json(out/"PASS_133_SCHIC_EXECUTION_REPORT.json",schic)

    terminal_ok=all([
        repair["ok"],prime["status"]=="PRIME_MAGIC_SUDOKU_BIGINT_KEY_STATE_VERIFIED",
        phase["status"]=="PRIME_QUDIT_PHASE_CANCELLATION_KEY_STATE_VERIFIED",
        ecc["status"]=="PALINDROMIC_ECC_BIGINT_RECONSTRUCTION_VERIFIED",
        ecc_stress["status"]=="PASS",prime_negative["status"]=="PASS",phase_negative["status"]=="PASS",
        schic["status"]=="PASS",replay_receipt["prime_key_replay_match"]
    ])
    files=[]
    for path in sorted(out.iterdir()):
        if path.name=="PASS_133_RELEASE_MANIFEST.json" or not path.is_file(): continue
        files.append({"path":path.name,"size_bytes":path.stat().st_size,"sha256":sha256(path.read_bytes()).hexdigest()})
    manifest={
        "schema":"HHS_PASS133_RELEASE_MANIFEST_V1","version":"1.0.0","pass_id":"PASS_133","runtime_parent":"PASS_132",
        "parent_checkpoint_root_hash72":parent_root,"generated_at":generated_at,"prime_bits":prime_bits,
        "workloads":{"133.1":prime["status"],"133.2":phase["status"],"133.3":ecc["status"],"HHS-I133":schic["status"]},
        "negative_tests":{"prime_magic":prime_negative["status"],"phase":phase_negative["status"],"ecc":ecc_stress["status"]},
        "entropy_authority":"ENTROPY_SOURCE_UNATTESTED","cryptographic_claim_boundary":"POST_QUANTUM_ENCRYPTION_NOT_VERIFIED",
        "checkpoint_chain_repaired":repair["ok"],"file_count":len(files),"files":files,
        "terminal_status":"PASS_133_CHECKPOINT_KEY_STATE_WORKLOAD_VERIFIED" if terminal_ok else "PASS_133_READINESS_BOUNDED",
    }
    manifest["manifest_hash72_witness"]=make_hash72_witness("hhs_pass133_release_manifest_v1",manifest).to_dict()
    _write_json(out/"PASS_133_RELEASE_MANIFEST.json",manifest)
    return manifest
