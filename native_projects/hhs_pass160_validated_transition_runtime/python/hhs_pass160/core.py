from __future__ import annotations

from dataclasses import dataclass, field, replace
from hashlib import sha256
import hmac
import json
import struct
from typing import Callable, Iterable

CONTRACT_ID = "HHS-P160-FPPORT-VTR"
CONTRACT_VERSION = "1.2.0"
PREMAIN_CLASSIFICATION = "HHS_PASS_160_IMPLEMENTATION_VERIFIED_PENDING_TERMINAL_EVIDENCE"
TERMINAL_CLASSIFICATION = "HHS_PASS_160_FIBONACCI_PRIME_PSEUDORANDOM_OVERLAP_RECEIPT_TIP_VALIDATED_TRANSITION_RUNTIME_VERIFIED"
HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
HASH72_LEN = 72
HASH216_LEN = 216
ZERO_HASH216 = "0" * HASH216_LEN
MASK64 = (1 << 64) - 1

class Pass160Error(ValueError):
    pass


def _mix64(x: int) -> int:
    x &= MASK64
    x ^= x >> 33
    x = (x * 0xFF51AFD7ED558CCD) & MASK64
    x ^= x >> 33
    x = (x * 0xC4CEB9FE1A85EC53) & MASK64
    x ^= x >> 33
    return x & MASK64


def _fold_bytes(data: bytes) -> int:
    state = 0x179971179971
    for i, byte in enumerate(data):
        state ^= (byte << ((i % 8) * 8)) & MASK64
        state = _mix64(state + i + 1)
    return state


def hash72(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    state = _fold_bytes(data)
    out: list[str] = []
    for i in range(HASH72_LEN):
        state = _mix64(state + (0x9E3779B97F4A7C15 * (i + 1)))
        out.append(HASH72_ALPHABET[state % HASH72_LEN])
    return "".join(out)


def hash216(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    state = _fold_bytes(data)
    out: list[str] = []
    for i in range(HASH216_LEN):
        state = _mix64(state + (0x517CC1B727220A95 * (i + 1)))
        out.append(HASH72_ALPHABET[state % HASH72_LEN])
    return "".join(out)


def domain_sha256(domain: str, data: bytes = b"") -> bytes:
    return sha256(domain.encode("utf-8") + b"\0" + data).digest()


def domain_sha256_hex(domain: str, data: bytes = b"") -> str:
    return domain_sha256(domain, data).hex()


def hash216_bound(domain: str, integrity: bytes, projection: bytes = b"") -> str:
    if len(integrity) != 32:
        raise Pass160Error("integrity must be 32 bytes")
    return hash216(domain.encode("utf-8") + b"\0" + integrity + projection)


def make_hash(domain: str, value: int) -> str:
    return hash216(f"{domain}:{value}")


def _u8(value: int) -> bytes:
    return struct.pack(">B", value)


def _u32(value: int) -> bytes:
    return struct.pack(">I", value)


def _u64(value: int) -> bytes:
    return struct.pack(">Q", value)


def _hash_bytes(value: str) -> bytes:
    raw = value.encode("ascii")
    if len(raw) != HASH216_LEN:
        raise Pass160Error(f"Hash216 length is {len(raw)}, expected {HASH216_LEN}")
    return raw


@dataclass(slots=True)
class CertifiedOperation:
    operation_id: str
    implementation_hash: str
    semantic_hash: str
    constraint_root: str
    runtime_semantic_root: str
    registry_root: str
    pass159_source_root: str
    pass159_vmir_root: str
    pass159_executable_root: str
    maximum_steps: int = 4096
    maximum_memory_bytes: int = 1 << 20
    permitted_read_mask: int = 0x7F
    permitted_write_mask: int = 0x18
    effect_class: int = 0
    deterministic: bool = True
    reusable: bool = True
    revoked: bool = False
    pass159_bound: bool = True


@dataclass(slots=True)
class ValidatedTransition:
    transition_epoch: int
    operation_sequence: int
    maximum_reuse_count: int
    original_validation_epoch: int
    parent_receipt_tip: str
    parent_state_root: str
    operation_id: str
    operation_implementation_hash: str
    operation_semantic_hash: str
    canonical_input_hash: str
    canonical_delta_hash: str
    resulting_state_root: str
    resulting_receipt_tip: str
    constraint_root: str
    runtime_semantic_root: str
    operation_registry_root: str
    validation_receipt_hash: str
    validator_manifest_hash: str
    pass159_source_root: str
    pass159_vmir_root: str
    pass159_executable_root: str
    pass159_equivalence_receipt: str
    permitted_read_mask: int
    permitted_write_mask: int
    maximum_steps: int
    maximum_memory_bytes: int
    input_schema_id: int = 1
    delta_schema_id: int = 1
    state_schema_id: int = 1
    effect_class: int = 0
    semantically_validated: bool = True
    sealed: bool = True
    revoked: bool = False
    external_effect_free: bool = True
    pass159_bound: bool = True
    transition_object_hash216: str = ZERO_HASH216
    transition_integrity_sha256: bytes = b"\0" * 32
    delta_integrity_sha256: bytes = b"\0" * 32
    validation_receipt_integrity_sha256: bytes = b"\0" * 32

    def projection_bytes(self) -> bytes:
        values = [
            _u32(1), _u64(self.transition_epoch), _u64(self.operation_sequence),
            _u64(self.maximum_reuse_count), _u64(self.original_validation_epoch),
            _hash_bytes(self.parent_receipt_tip), _hash_bytes(self.parent_state_root),
            _hash_bytes(self.operation_id), _hash_bytes(self.operation_implementation_hash),
            _hash_bytes(self.operation_semantic_hash), _hash_bytes(self.canonical_input_hash),
            _hash_bytes(self.canonical_delta_hash), _hash_bytes(self.resulting_state_root),
            _hash_bytes(self.resulting_receipt_tip), _hash_bytes(self.constraint_root),
            _hash_bytes(self.runtime_semantic_root), _hash_bytes(self.operation_registry_root),
            _hash_bytes(self.validation_receipt_hash), _hash_bytes(self.validator_manifest_hash),
            _u8(int(self.pass159_bound)),
        ]
        if self.pass159_bound:
            values.extend([
                _hash_bytes(self.pass159_source_root), _hash_bytes(self.pass159_vmir_root),
                _hash_bytes(self.pass159_executable_root), _hash_bytes(self.pass159_equivalence_receipt),
            ])
        return b"".join(values)

    def canonical_bytes(self) -> bytes:
        return b"".join([
            self.projection_bytes(), self.delta_integrity_sha256,
            self.validation_receipt_integrity_sha256,
            _u64(self.permitted_read_mask), _u64(self.permitted_write_mask),
            _u64(self.maximum_steps), _u64(self.maximum_memory_bytes),
            _u32(self.input_schema_id), _u32(self.delta_schema_id),
            _u32(self.state_schema_id), _u32(self.effect_class),
            _u8(int(self.semantically_validated)), _u8(int(self.sealed)),
            _u8(int(self.revoked)), _u8(int(self.external_effect_free)),
        ])

    def seal_identity(self) -> "ValidatedTransition":
        self.delta_integrity_sha256 = domain_sha256(
            "HHS-P160-DELTA-INTEGRITY-V1", _hash_bytes(self.canonical_delta_hash)
        )
        self.validation_receipt_integrity_sha256 = domain_sha256(
            "HHS-P160-VALIDATION-RECEIPT-INTEGRITY-V1", _hash_bytes(self.validation_receipt_hash)
        )
        self.transition_integrity_sha256 = domain_sha256(
            "HHS-P160-TRANSITION-INTEGRITY-V1", self.canonical_bytes()
        )
        self.transition_object_hash216 = hash216_bound(
            "HHS-P160-TRANSITION-IDENTITY-V1",
            self.transition_integrity_sha256,
            self.projection_bytes(),
        )
        return self

    def verify_identity(self) -> bool:
        copy = replace(
            self,
            transition_object_hash216=ZERO_HASH216,
            transition_integrity_sha256=b"\0" * 32,
            delta_integrity_sha256=b"\0" * 32,
            validation_receipt_integrity_sha256=b"\0" * 32,
        ).seal_identity()
        return (
            hmac.compare_digest(copy.transition_integrity_sha256, self.transition_integrity_sha256)
            and hmac.compare_digest(copy.transition_object_hash216, self.transition_object_hash216)
        )

    def lookup_key(self) -> tuple[str, ...]:
        return (
            self.parent_receipt_tip, self.parent_state_root, self.operation_id,
            self.canonical_input_hash, self.constraint_root, self.runtime_semantic_root,
            self.operation_implementation_hash, self.operation_registry_root,
        )

    def lookup_digest(self) -> str:
        return domain_sha256_hex(
            "HHS-P160-EXACT-LOOKUP-V1",
            b"".join(_hash_bytes(item) for item in self.lookup_key()),
        )


@dataclass(slots=True)
class SegmentCertificate:
    segment_id: int
    start_index: int
    transition_count: int
    overlap_prefix_count: int
    overlap_suffix_count: int
    transition_merkle_root_sha256: bytes
    overlap_prefix_root_sha256: bytes
    overlap_suffix_root_sha256: bytes
    transition_root_hash216: str
    overlap_prefix_root_hash216: str
    overlap_suffix_root_hash216: str
    sealed: bool = True
    quarantined: bool = False
    revoked: bool = False
    coverage_valid: bool = True


@dataclass(slots=True)
class HistoricalFrontier:
    frontier_epoch: int
    terminal_transition_epoch: int
    total_transition_count: int
    terminal_receipt_tip: str
    terminal_state_root: str
    release_frontier_integrity_sha256: bytes
    release_frontier_root: str
    frontier_certificate_hash216: str
    sealed: bool = True
    current: bool = True
    revoked: bool = False
    replay_verified: bool = True


@dataclass(slots=True)
class CommitCandidate:
    expected_frontier_epoch: int
    proposal_epoch: int
    base_frontier_hash216: str
    resulting_state_root: str
    resulting_receipt_tip: str
    local_receipt_hash72: str
    backend: int = 2
    verified: bool = True
    applied: bool = False
    outer_admission_verified: bool = False


@dataclass(slots=True)
class CoverageCertificate:
    audit_epoch: int
    domain_length: int
    temporal_cycle_length: int
    sampled_count: int
    cover_count: int
    failed_count: int
    seed_commitment_sha256: str
    sampled_result_accumulator_sha256: str
    coverage_certificate_hash216: str
    complete_permutation: bool
    every_index_visited_once: bool
    storage_integrity_valid: bool
    segment_reuse_allowed: bool


@dataclass(slots=True)
class NestedRuntime:
    runtime: "Runtime"
    runtime_instance_id: int
    maximum_steps: int
    base_frontier: HistoricalFrontier
    local_state_root: str
    local_receipt_tip: str
    local_receipt_hash72: str
    steps: int = 0
    effects: list[dict] = field(default_factory=list)
    finalized: bool = False

    @property
    def capability_count(self) -> int:
        return 0

    def reuse(self, transition_index: int, segment_id: int) -> None:
        if self.finalized or self.steps >= self.maximum_steps:
            raise Pass160Error("nested runtime bounded or finalized")
        transition = self.runtime.transitions[transition_index]
        segment = self.runtime.segments[segment_id]
        if not segment.sealed or segment.quarantined or segment.revoked:
            raise Pass160Error("segment not reusable")
        if transition.parent_receipt_tip != self.local_receipt_tip or transition.parent_state_root != self.local_state_root:
            raise Pass160Error("parent mismatch")
        if not transition.verify_identity():
            raise Pass160Error("transition identity mismatch")
        self.local_state_root = transition.resulting_state_root
        self.local_receipt_tip = transition.resulting_receipt_tip
        self.steps += 1
        self.local_receipt_hash72 = hash72(
            self.local_receipt_hash72.encode("ascii")
            + transition.transition_object_hash216.encode("ascii")
            + _u64(self.steps)
        )

    def propose_effect(self, effect_class: int, payload: bytes | str) -> dict:
        if isinstance(payload, str):
            payload = payload.encode()
        proposal = {
            "effect_class": effect_class,
            "payload_hash216": hash216(payload),
            "payload_integrity_sha256": domain_sha256_hex("HHS-P160-EFFECT-PROPOSAL-V1", payload),
            "proposal_only": True,
            "executed": False,
            "externally_admitted": False,
        }
        self.effects.append(proposal)
        return proposal

    def finalize(self, backend: int = 2) -> CommitCandidate:
        self.finalized = True
        return CommitCandidate(
            expected_frontier_epoch=self.base_frontier.frontier_epoch,
            proposal_epoch=self.base_frontier.frontier_epoch + 1,
            base_frontier_hash216=self.base_frontier.frontier_certificate_hash216,
            resulting_state_root=self.local_state_root,
            resulting_receipt_tip=self.local_receipt_tip,
            local_receipt_hash72=self.local_receipt_hash72,
            backend=backend,
        )


def merkle_root(leaves: Iterable[bytes]) -> bytes:
    level = list(leaves)
    if not level:
        return domain_sha256("HHS-P160-SEGMENT-MERKLE-V1")
    while len(level) > 1:
        next_level: list[bytes] = []
        for i in range(0, len(level), 2):
            right = level[i + 1] if i + 1 < len(level) else level[i]
            next_level.append(domain_sha256("HHS-P160-SEGMENT-MERKLE-V1", level[i] + right))
        level = next_level
    return level[0]


def fibonacci_prime_cycle_length(level: int) -> int:
    cycles = (170, 2563, 27149, 317434, 1)
    if level < 0 or level >= len(cycles):
        raise Pass160Error("unsupported Fibonacci-prime level")
    return cycles[level]


def temporal_bucket_quota(bucket: int, domain_length: int, cycle_length: int) -> int:
    if cycle_length <= 0 or bucket < 0 or bucket >= cycle_length:
        raise Pass160Error("invalid temporal bucket")
    return ((bucket + 1) * domain_length) // cycle_length - (bucket * domain_length) // cycle_length


def permutation_index(key: bytes, domain_length: int, ordinal: int) -> int:
    if len(key) != 32 or domain_length <= 0 or not 0 <= ordinal < domain_length:
        raise Pass160Error("invalid permutation arguments")
    bits = max(2, (domain_length - 1).bit_length())
    if bits % 2:
        bits += 1
    if bits > 62:
        raise Pass160Error("permutation domain bounded")
    half = bits // 2
    mask = (1 << half) - 1
    x = ordinal
    domain = b"HHS-P160-COVERAGE-PRP-V1"
    for _ in range((1 << bits) + 1):
        left = (x >> half) & mask
        right = x & mask
        for round_number in range(4):
            material = domain + bytes([round_number]) + _u64(right)
            value = int.from_bytes(hmac.new(key, material, "sha256").digest()[:8], "big")
            left, right = right, (left ^ (value & mask)) & mask
        x = ((left & mask) << half) | (right & mask)
        if x < domain_length:
            return x
    raise Pass160Error("permutation cycle walk failed")


class Runtime:
    def __init__(self) -> None:
        self.operations: dict[str, CertifiedOperation] = {}
        self.transitions: list[ValidatedTransition] = []
        self.lookup: dict[tuple[str, ...], int] = {}
        self.segments: list[SegmentCertificate] = []
        self.frontier: HistoricalFrontier | None = None
        self.receipt_tip = hash72(CONTRACT_ID)

    def register_operation(self, operation: CertifiedOperation) -> None:
        if operation.revoked or not operation.deterministic or not operation.reusable:
            raise Pass160Error("operation not reusable")
        self.operations[operation.operation_id] = operation

    def admit(self, transition: ValidatedTransition) -> int:
        operation = self.operations.get(transition.operation_id)
        if operation is None:
            raise Pass160Error("operation not registered")
        if transition.operation_implementation_hash != operation.implementation_hash:
            raise Pass160Error("implementation mismatch")
        if not transition.semantically_validated or not transition.sealed or transition.revoked:
            raise Pass160Error("transition not admissible")
        transition.seal_identity()
        if transition.lookup_key() in self.lookup:
            raise Pass160Error("transition already exists")
        index = len(self.transitions)
        self.transitions.append(transition)
        self.lookup[transition.lookup_key()] = index
        return index

    def exact_lookup(self, key: tuple[str, ...]) -> tuple[int, ValidatedTransition]:
        index = self.lookup[key]
        transition = self.transitions[index]
        if not transition.verify_identity():
            raise Pass160Error("stored identity mismatch")
        return index, transition

    def seal_segment(self, start: int, count: int, overlap_prefix: int, overlap_suffix: int) -> SegmentCertificate:
        if count <= 0 or start < 0 or start + count > len(self.transitions):
            raise Pass160Error("invalid segment")
        subset = self.transitions[start:start + count]
        leaves = [item.transition_integrity_sha256 for item in subset]
        root = merkle_root(leaves)
        prefix = merkle_root(leaves[:overlap_prefix]) if overlap_prefix else domain_sha256("HHS-P160-SEGMENT-MERKLE-V1")
        suffix = merkle_root(leaves[-overlap_suffix:]) if overlap_suffix else domain_sha256("HHS-P160-SEGMENT-MERKLE-V1")
        certificate = SegmentCertificate(
            segment_id=len(self.segments), start_index=start, transition_count=count,
            overlap_prefix_count=overlap_prefix, overlap_suffix_count=overlap_suffix,
            transition_merkle_root_sha256=root,
            overlap_prefix_root_sha256=prefix,
            overlap_suffix_root_sha256=suffix,
            transition_root_hash216=hash216_bound("HHS-P160-SEGMENT-IDENTITY-V1", root),
            overlap_prefix_root_hash216=hash216_bound("HHS-P160-SEGMENT-OVERLAP-PREFIX-V1", prefix),
            overlap_suffix_root_hash216=hash216_bound("HHS-P160-SEGMENT-OVERLAP-SUFFIX-V1", suffix),
        )
        self.segments.append(certificate)
        return certificate

    @staticmethod
    def verify_overlap(left: SegmentCertificate, right: SegmentCertificate) -> bool:
        return (
            left.sealed and right.sealed and not left.quarantined and not right.quarantined
            and left.overlap_suffix_count == right.overlap_prefix_count
            and hmac.compare_digest(left.overlap_suffix_root_sha256, right.overlap_prefix_root_sha256)
        )

    def seal_frontier(self, epoch: int, terminal_tip: str, terminal_state: str) -> HistoricalFrontier:
        if not self.segments:
            raise Pass160Error("segments required")
        roots = [segment.transition_merkle_root_sha256 for segment in self.segments]
        integrity = merkle_root(roots)
        release_root = hash216_bound("HHS-P160-RELEASE-FRONTIER-V1", integrity)
        canonical = _u64(epoch) + _u64(len(self.transitions)) + _hash_bytes(terminal_tip) + _hash_bytes(terminal_state) + integrity
        frontier_integrity = domain_sha256("HHS-P160-FRONTIER-INTEGRITY-V1", canonical)
        frontier_hash = hash216_bound("HHS-P160-FRONTIER-INTEGRITY-V1", frontier_integrity, canonical)
        if self.frontier:
            self.frontier.current = False
        self.frontier = HistoricalFrontier(
            frontier_epoch=epoch,
            terminal_transition_epoch=self.transitions[-1].transition_epoch,
            total_transition_count=len(self.transitions),
            terminal_receipt_tip=terminal_tip,
            terminal_state_root=terminal_state,
            release_frontier_integrity_sha256=integrity,
            release_frontier_root=release_root,
            frontier_certificate_hash216=frontier_hash,
        )
        return self.frontier

    def nested_begin(self, runtime_instance_id: int, maximum_steps: int) -> NestedRuntime:
        if not self.frontier or not self.frontier.current or not self.frontier.replay_verified:
            raise Pass160Error("current frontier required")
        return NestedRuntime(
            runtime=self,
            runtime_instance_id=runtime_instance_id,
            maximum_steps=maximum_steps,
            base_frontier=replace(self.frontier),
            local_state_root=self.frontier.terminal_state_root,
            local_receipt_tip=self.frontier.terminal_receipt_tip,
            local_receipt_hash72=hash72(self.frontier.frontier_certificate_hash216),
        )

    def apply_commit(self, candidate: CommitCandidate, outer_admission: Callable[[CommitCandidate], bool]) -> HistoricalFrontier:
        if not self.frontier or candidate.expected_frontier_epoch != self.frontier.frontier_epoch:
            raise Pass160Error("stale frontier")
        if candidate.base_frontier_hash216 != self.frontier.frontier_certificate_hash216:
            raise Pass160Error("frontier identity mismatch")
        if candidate.proposal_epoch != self.frontier.frontier_epoch + 1:
            raise Pass160Error("proposal epoch mismatch")
        if not outer_admission(candidate):
            raise Pass160Error("fresh outer admission required")
        candidate.outer_admission_verified = True
        candidate.applied = True
        return self.seal_frontier(candidate.proposal_epoch, candidate.resulting_receipt_tip, candidate.resulting_state_root)

    def audit(self, epoch: int, level: int, key: bytes) -> CoverageCertificate:
        cycle = fibonacci_prime_cycle_length(level)
        accumulator = domain_sha256("HHS-P160-AUDIT-ACCUMULATOR-V1")
        seed = domain_sha256("HHS-P160-AUDIT-EPOCH-KEY-V1", key + _u64(epoch))
        visited: set[int] = set()
        failed = 0
        for ordinal in range(len(self.transitions)):
            index = permutation_index(key, len(self.transitions), ordinal)
            if index in visited or not self.transitions[index].verify_identity():
                failed += 1
            visited.add(index)
            accumulator = domain_sha256(
                "HHS-P160-AUDIT-SAMPLE-V1",
                accumulator + self.transitions[index].transition_integrity_sha256 + _u64(index),
            )
        cover = sum(max(0, 1 - temporal_bucket_quota(bucket, len(self.transitions), cycle)) for bucket in range(cycle))
        canonical = b"".join([
            _u64(epoch), _u64(len(self.transitions)), _u64(cycle),
            _u64(len(self.transitions)), _u64(cover), _u64(failed), seed, accumulator,
        ])
        cert_integrity = domain_sha256("HHS-P160-COVERAGE-CERTIFICATE-V1", canonical)
        return CoverageCertificate(
            audit_epoch=epoch, domain_length=len(self.transitions), temporal_cycle_length=cycle,
            sampled_count=len(self.transitions), cover_count=cover, failed_count=failed,
            seed_commitment_sha256=seed.hex(),
            sampled_result_accumulator_sha256=accumulator.hex(),
            coverage_certificate_hash216=hash216_bound("HHS-P160-COVERAGE-CERTIFICATE-V1", cert_integrity, canonical),
            complete_permutation=True,
            every_index_visited_once=len(visited) == len(self.transitions),
            storage_integrity_valid=failed == 0,
            segment_reuse_allowed=failed == 0 and len(visited) == len(self.transitions),
        )


def make_operation() -> CertifiedOperation:
    return CertifiedOperation(
        operation_id=make_hash("operation", 1), implementation_hash=make_hash("implementation", 1),
        semantic_hash=make_hash("semantic", 1), constraint_root=make_hash("constraint", 1),
        runtime_semantic_root=make_hash("runtime-semantic", 1), registry_root=make_hash("registry", 1),
        pass159_source_root=make_hash("p159-source", 1), pass159_vmir_root=make_hash("p159-vmir", 1),
        pass159_executable_root=make_hash("p159-executable", 1),
    )


def make_transition(operation: CertifiedOperation, index: int, parent_tip: str, parent_state: str) -> ValidatedTransition:
    return ValidatedTransition(
        transition_epoch=index + 1, operation_sequence=index, maximum_reuse_count=1_000_000_000,
        original_validation_epoch=1, parent_receipt_tip=parent_tip, parent_state_root=parent_state,
        operation_id=operation.operation_id, operation_implementation_hash=operation.implementation_hash,
        operation_semantic_hash=operation.semantic_hash, canonical_input_hash=make_hash("input", index),
        canonical_delta_hash=make_hash("delta", index), resulting_state_root=make_hash("state", index + 1),
        resulting_receipt_tip=make_hash("tip", index + 1), constraint_root=operation.constraint_root,
        runtime_semantic_root=operation.runtime_semantic_root, operation_registry_root=operation.registry_root,
        validation_receipt_hash=make_hash("validation-receipt", index), validator_manifest_hash=make_hash("validator", 1),
        pass159_source_root=operation.pass159_source_root, pass159_vmir_root=operation.pass159_vmir_root,
        pass159_executable_root=operation.pass159_executable_root,
        pass159_equivalence_receipt=make_hash("p159-equivalence", index),
        permitted_read_mask=operation.permitted_read_mask, permitted_write_mask=operation.permitted_write_mask,
        maximum_steps=64, maximum_memory_bytes=4096,
    )


def build_demo(count: int = 64) -> tuple[Runtime, CertifiedOperation, list[ValidatedTransition], SegmentCertificate, SegmentCertificate, HistoricalFrontier]:
    runtime = Runtime()
    operation = make_operation()
    runtime.register_operation(operation)
    transitions: list[ValidatedTransition] = []
    parent_tip = make_hash("tip", 0)
    parent_state = make_hash("state", 0)
    for index in range(count):
        transition = make_transition(operation, index, parent_tip, parent_state)
        runtime.admit(transition)
        transitions.append(transition)
        parent_tip = transition.resulting_receipt_tip
        parent_state = transition.resulting_state_root
    left = runtime.seal_segment(0, min(32, count), 1, min(8, count - 1))
    right_start = 24 if count >= 56 else max(0, count // 2 - 4)
    right_count = min(32, count - right_start)
    right = runtime.seal_segment(right_start, right_count, min(8, right_count - 1), 1)
    frontier = runtime.seal_frontier(7, make_hash("tip", 0), make_hash("state", 0))
    return runtime, operation, transitions, left, right, frontier


def vector_report() -> dict[str, object]:
    key = bytes((i * 7 + 3) & 0xFF for i in range(32))
    operation = make_operation()
    transition = make_transition(operation, 0, make_hash("tip", 0), make_hash("state", 0)).seal_identity()
    return {
        "hash216": hash216("pass160"),
        "lookup_digest": transition.lookup_digest(),
        "permutation_64_17": permutation_index(key, 64, 17),
        "quota_sum": sum(temporal_bucket_quota(i, 64, 170) for i in range(170)),
        "sha256": domain_sha256_hex("HHS-P160-VECTOR-V1", b"pass160"),
        "transition_hash216": transition.transition_object_hash216,
        "transition_integrity_sha256": transition.transition_integrity_sha256.hex(),
    }


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
