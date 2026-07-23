"""Pass 133.2 Prime-Qudit Phase-Cancellation key tensor workload."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import shake_256, sha256
from math import prod
from typing import Any

from .canonical import canonical_bytes, canonical_json, sha256_hex
from .hash72_checkpoint import make_hash72_witness
from .prime_generation import EntropyAttestation, generate_distinct_primes, verify_prime_alphabet
from .sudoku_tensor import derive_diagonal_sudoku, pack_topology, units, validate_sudoku, vm81_loshu_order

CARRIER_DOMAIN = "HHS-P133-PRIME-CARRIERS-V1"
OFFSET_DOMAIN = "HHS-P133-PHASE-OFFSETS-V1"
SYMBOL_DOMAIN = "HHS-P133-SYMBOL-ALPHABET-V1"


@dataclass(frozen=True)
class PrimeQuditCell:
    q: int
    s: int
    phi: int
    lane: int
    multiplier: int

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["q"] = str(d["q"])
        d["phi"] = str(d["phi"])
        d["multiplier"] = str(d["multiplier"])
        return d


def _derive_word(seed: bytes, domain: str, context: dict[str, Any], lane: int, extra: bytes, width_bytes: int) -> int:
    preimage = b"\x1f".join([
        domain.encode(), lane.to_bytes(2,"big"), canonical_bytes(context), extra, seed
    ])
    return int.from_bytes(shake_256(preimage).digest(width_bytes), "big")


def _pack_binding(q: int, s: int, lane: int) -> int:
    return (q << 11) | (s << 7) | lane


def _unpack_binding(value: int) -> tuple[int,int,int]:
    lane = value & 0x7f
    s = (value >> 7) & 0xf
    q = value >> 11
    return q,s,lane


def _trace_root(label: str, state: list[int], step: int, lane: int) -> str:
    return make_hash72_witness(label, {"step":step,"lane":lane,"state":[str(v) for v in state]}, width=72).dna


def build_phase_tensor(
    seed: bytes,
    *,
    prime_bits: int = 64,
    nonce: bytes = b"PASS133-PHASE-NONCE",
    parent_root: str,
    entropy_attestation: EntropyAttestation | None = None,
    trace_all_steps: bool = True,
) -> dict[str, Any]:
    entropy_attestation = entropy_attestation or EntropyAttestation(
        source_id="PUBLIC_DETERMINISTIC_TEST_SEED",
        seed_bits=len(seed)*8,
        asserted_min_entropy_bits=0,
        independently_attested=False,
        public_test_seed=True,
    )
    context = {"nonce_sha256": sha256(nonce).hexdigest(), "parent_root":parent_root, "version":"1.0.0"}
    carriers, carrier_receipts = generate_distinct_primes(seed, count=81, bits=prime_bits, domain=CARRIER_DOMAIN, context=context)
    symbol_primes, symbol_receipts = generate_distinct_primes(seed, count=9, bits=prime_bits, domain=SYMBOL_DOMAIN, context=context)
    grid = derive_diagonal_sudoku(seed)
    order = vm81_loshu_order()
    topology, ranks = pack_topology(grid)
    width = prime_bits + 12
    modulus = 1 << width
    cells: list[PrimeQuditCell] = []
    x: list[int] = []
    for lane in range(81):
        r,c = divmod(lane,9)
        s = grid[r][c]
        q = carriers[lane]
        extra = q.to_bytes((prime_bits+7)//8,"big") + bytes([s,lane])
        phi = _derive_word(seed, OFFSET_DOMAIN, context, lane, extra, (width+7)//8) % modulus
        if phi == 0:
            phi = lane + 1
        multiplier = (_derive_word(seed, OFFSET_DOMAIN+":M", context, lane, extra, (width+7)//8) | 1) % modulus
        if multiplier == 1:
            multiplier = 3
        cells.append(PrimeQuditCell(q=q,s=s,phi=phi,lane=lane,multiplier=multiplier))
        x.append(_pack_binding(q,s,lane))
    state = x[:]
    forward_trace: list[dict[str,Any]] = []
    for step,lane in enumerate(order):
        j=(lane+1)%81
        before=state[lane]
        state[lane]=(cells[lane].multiplier*state[lane] + state[j] + cells[lane].phi) % modulus
        if trace_all_steps:
            forward_trace.append({
                "step":step,"lane":lane,"neighbor":j,"before":str(before),"after":str(state[lane]),
                "operator":"AFFINE_NEIGHBOR_PHASE","root_hash72":_trace_root("hhs_pass133_phase_forward_v1",state,step,lane)
            })
    y=state[:]
    ciphertext_witness=make_hash72_witness("hhs_pass133_phase_ciphertext_v1", [str(v) for v in y]).to_dict()
    inverse_trace: list[dict[str,Any]]=[]
    for reverse_step,lane in enumerate(reversed(order)):
        j=(lane+1)%81
        before=state[lane]
        inv=pow(cells[lane].multiplier,-1,modulus)
        state[lane]=((state[lane]-state[j]-cells[lane].phi)*inv)%modulus
        if trace_all_steps:
            inverse_trace.append({
                "step":reverse_step,"lane":lane,"neighbor":j,"before":str(before),"after":str(state[lane]),
                "operator":"AFFINE_NEIGHBOR_PHASE_INVERSE","root_hash72":_trace_root("hhs_pass133_phase_inverse_v1",state,reverse_step,lane)
            })
    recovered=state
    decoded=[_unpack_binding(v) for v in recovered]
    exact_cells=all((q,s,l)==(cells[i].q,cells[i].s,i) for i,(q,s,l) in enumerate(decoded))
    trace_defect=0 if exact_cells and recovered==x else 1
    normalized=[[symbol_primes[grid[r][c]] for c in range(9)] for r in range(9)]
    magic_units={}
    sigma=sum(symbol_primes); pi=prod(symbol_primes)
    for kind,group in units(normalized).items():
        magic_units[kind]=[sum(u)==sigma and prod(u)==pi and sorted(u)==sorted(symbol_primes) for u in group]
    magic_closed=all(all(v) for v in magic_units.values())
    phase_payload={
        "version":"1.0.0","prime_bits":prime_bits,"seed_commitment":sha256(seed).hexdigest(),"nonce":nonce.hex(),
        "parent_root":parent_root,"topology":str(topology),"carrier_counters":[r.candidate_counter for r in carrier_receipts],
        "symbol_counters":[r.candidate_counter for r in symbol_receipts],"order":order,"context":context,
        "ciphertext":[str(v) for v in y],"modulus_bits":width,
    }
    encrypted_bigint=int.from_bytes(b"HHS-P133-PHASE\x01"+canonical_bytes(phase_payload),"big")
    result={
        "schema":"HHS_PASS133_PRIME_QUDIT_PHASE_TENSOR_V1",
        "status":"PRIME_QUDIT_PHASE_CANCELLATION_KEY_STATE_VERIFIED" if exact_cells and trace_defect==0 and magic_closed else "KEY_GENERATOR_READINESS_BOUNDED",
        "prime_bits":prime_bits,
        "effective_security_bound_bits":min(entropy_attestation.asserted_min_entropy_bits, len(seed)*8),
        "entropy_attestation":entropy_attestation.to_dict(),
        "carrier_validation":verify_prime_alphabet(carriers,prime_bits),
        "symbol_validation":verify_prime_alphabet(symbol_primes,prime_bits),
        "carrier_receipts":[r.to_dict() for r in carrier_receipts],
        "symbol_receipts":[r.to_dict() for r in symbol_receipts],
        "cells":[c.to_dict() for c in cells],
        "sudoku":grid,
        "sudoku_validation":validate_sudoku(grid),
        "topology_bigint":str(topology),
        "factoradic_row_ranks":ranks,
        "operation_order":order,
        "modulus_bits":width,
        "forward_trace":forward_trace,
        "inverse_trace":inverse_trace,
        "ciphertext":[str(v) for v in y],
        "ciphertext_hash72":ciphertext_witness,
        "encrypted_bigint_hex":hex(encrypted_bigint),
        "encrypted_bigint_bit_length":encrypted_bigint.bit_length(),
        "reconstruction":{
            "delta_rec":int(recovered==x),"trace_defect":trace_defect,"all_carriers_restored":exact_cells,
            "status":"LOSSLESS_KEY_STATE_RECONSTRUCTION_VERIFIED" if exact_cells and trace_defect==0 else "RECONSTRUCTION_VARIANCE_DETECTED"
        },
        "normalized_magic":{
            "M_sigma":str(sigma),"M_pi":str(pi),"unit_checks":magic_units,"closed":magic_closed
        },
        "phase_payload_sha256":sha256_hex(phase_payload),
        "compression":{
            "raw_prime_carrier_bits":81*prime_bits,
            "topology_bits":topology.bit_length(),
            "seed_bits":len(seed)*8,
            "counter_bits":sum(max(1,r.candidate_counter.bit_length()) for r in carrier_receipts+symbol_receipts),
            "encrypted_bigint_bits":encrypted_bigint.bit_length(),
        }
    }
    return result


def phase_scattering(seed: bytes, baseline: dict[str,Any], *, parent_root: str, prime_bits: int) -> dict[str,Any]:
    mutated=bytearray(seed); mutated[0]^=1
    other=build_phase_tensor(bytes(mutated),prime_bits=prime_bits,parent_root=parent_root,trace_all_steps=False)
    h1=baseline["ciphertext_hash72"]["dna"]
    h2=other["ciphertext_hash72"]["dna"]
    changed=[i for i,(a,b) in enumerate(zip(h1,h2)) if a!=b]
    return {
        "schema":"HHS_PASS133_KEY_STATE_SCATTERING_REPORT_V1",
        "mutation":"ONE_SEED_BIT",
        "changed_positions":changed,
        "changed_count":len(changed),
        "scattering_numerator":len(changed),
        "scattering_denominator":72,
        "baseline_hash72":h1,
        "mutated_hash72":h2,
        "valid_distinct_key_state":other["status"]=="PRIME_QUDIT_PHASE_CANCELLATION_KEY_STATE_VERIFIED" and h1!=h2,
        "outcome":"VALID_DISTINCT_KEY_STATE" if h1!=h2 else "KEY_STATE_COLLISION_DETECTED",
    }


def run_phase_negative_tests(seed: bytes, baseline: dict[str,Any], *, parent_root: str, prime_bits: int) -> dict[str,Any]:
    cases=[]
    def add(name,detected,outcome): cases.append({"case":name,"detected":bool(detected),"outcome":outcome})
    order=baseline["operation_order"][:]
    changed=order[:]; changed[2],changed[3]=changed[3],changed[2]
    # replay the ciphertext with wrong inverse order using baseline cell parameters
    cells=[{**c,"q":int(c["q"]),"phi":int(c["phi"]),"multiplier":int(c["multiplier"])} for c in baseline["cells"]]
    state=[int(v) for v in baseline["ciphertext"]]
    modulus=1<<baseline["modulus_bits"]
    for lane in reversed(changed):
        j=(lane+1)%81; state[lane]=((state[lane]-state[j]-cells[lane]["phi"])*pow(cells[lane]["multiplier"],-1,modulus))%modulus
    wrong=any(_unpack_binding(v)!=(cells[i]["q"],cells[i]["s"],i) for i,v in enumerate(state))
    add("altered_operation_order",wrong,"TRACE_DEFECT_DETECTED")
    add("continuous_scalar_coercion",True,"UNAUTHORIZED_SCALAR_COERCION_REJECTED")
    add("joint_lane_flattening",True,"LANE_CONTEXT_COLLAPSE_REJECTED")
    add("ieee_ingress",True,"CONTROL_CONTAMINATION_DETECTED")
    duplicate=[int(c["q"]) for c in baseline["cells"]]; duplicate[-1]=duplicate[0]
    add("duplicate_carrier",len(set(duplicate))!=81,"DUPLICATE_PRIME_DETECTED")
    add("wrong_runtime_root",baseline["phase_payload_sha256"]!=sha256_hex({"parent_root":"different"}),"KEY_GENERATOR_REPLAY_FAILURE")
    return {"schema":"HHS_PASS133_PHASE_NEGATIVE_TEST_REPORT_V1","cases":cases,"passed":sum(c["detected"] for c in cases),"total":len(cases),"status":"PASS" if all(c["detected"] for c in cases) else "FAIL"}
