"""Pass 150 Hash216 constraint genome and air-gapped causal immune system.

This subsystem is orthogonal to VM81. It may observe attempted external state changes,
produce immutable high-resolution evidence, and return an echo requiring VM81
validation. It never mutates VM81 state directly.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import base64, hmac, json, os, threading, time, uuid, zlib
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

DOMAIN = b"HHS-P150-HASH216-CONSTRAINT-GENOME-V1\0"
POSITION_DOMAIN = b"HHS-P150-POSITION-V1\0"
RECORD_DOMAIN = b"HHS-P150-RECORD-V1\0"
KEY_DOMAIN = b"HHS-P150-KEY-EPOCH-V1\0"
OPCODES = tuple(range(19))
BASE = 20


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

@dataclass(frozen=True)
class KeyEpoch:
    epoch: int
    key_id: str
    key_b64: str
    previous_key_id: str | None = None
    previous_signature: str | None = None
    current_signature: str | None = None

    @property
    def key(self) -> bytes:
        return base64.b64decode(self.key_b64)

    @classmethod
    def genesis(cls, key: bytes, epoch: int = 0) -> "KeyEpoch":
        if len(key) < 32:
            raise ValueError("key must contain at least 256 bits")
        kid = sha256(KEY_DOMAIN + key).hexdigest()
        sig = hmac.new(key, f"{epoch}:{kid}:GENESIS".encode(), sha256).hexdigest()
        return cls(epoch, kid, base64.b64encode(key).decode(), None, None, sig)

    def rotate(self, new_key: bytes) -> "KeyEpoch":
        if len(new_key) < 32:
            raise ValueError("key must contain at least 256 bits")
        new_epoch = self.epoch + 1
        new_id = sha256(KEY_DOMAIN + new_key).hexdigest()
        body = f"{new_epoch}:{new_id}:{self.key_id}".encode()
        return KeyEpoch(new_epoch, new_id, base64.b64encode(new_key).decode(), self.key_id,
                        hmac.new(self.key, body, sha256).hexdigest(),
                        hmac.new(new_key, body, sha256).hexdigest())

    def verify_transition(self, previous: "KeyEpoch") -> bool:
        if self.previous_key_id != previous.key_id or self.epoch != previous.epoch + 1:
            return False
        body = f"{self.epoch}:{self.key_id}:{previous.key_id}".encode()
        return (hmac.compare_digest(self.previous_signature or "", hmac.new(previous.key, body, sha256).hexdigest())
                and hmac.compare_digest(self.current_signature or "", hmac.new(self.key, body, sha256).hexdigest()))

@dataclass(frozen=True)
class Hash216Record:
    record_id: str
    sequence: int
    timestamp_ns: int
    event_type: str
    actor: str
    payload_b64: str
    payload_sha256: str
    positions: tuple[str, ...]
    genome_root: str
    previous_root: str
    key_epoch: int
    key_id: str
    signature: str
    vm81_echo_required: bool
    reversal_of: str | None = None

    def body(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("signature")
        return d

class Hash216Genome:
    @staticmethod
    def positions(payload: bytes, *, previous_root: str = "0" * 64, sequence: int = 0) -> tuple[str, ...]:
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("payload must be bytes")
        seed = sha256(DOMAIN + previous_root.encode() + sequence.to_bytes(16, "big") + payload).digest()
        out = []
        for index in range(216):
            out.append(sha256(POSITION_DOMAIN + index.to_bytes(2, "big") + seed + payload).hexdigest())
        return tuple(out)

    @staticmethod
    def root(positions: Sequence[str]) -> str:
        if len(positions) != 216:
            raise ValueError("exactly 216 positions are required")
        if any(len(x) != 64 for x in positions):
            raise ValueError("every position must be a SHA-256 hex digest")
        return sha256(DOMAIN + b"".join(bytes.fromhex(x) for x in positions)).hexdigest()

class Base20BigIntCodec:
    """Lossless 19-opcode + framing serialization in a base-20 container."""
    @staticmethod
    def encode(opcodes: Sequence[int]) -> int:
        if any(x not in OPCODES for x in opcodes):
            raise ValueError("opcode outside active 0..18 set")
        # terminal framing digit 19 disambiguates leading zero opcodes and empty streams
        value = 19
        for opcode in reversed(tuple(opcodes)):
            value = value * BASE + opcode
        return value

    @staticmethod
    def decode(value: int) -> tuple[int, ...]:
        if not isinstance(value, int) or value < 19:
            raise ValueError("invalid base-20 bigint container")
        out = []
        while value != 19:
            value, digit = divmod(value, BASE)
            if digit == 19 or digit not in OPCODES:
                raise ValueError("invalid opcode/framing placement")
            out.append(digit)
        return tuple(out)

class Hash216ImmuneSystem:
    def __init__(self, root: os.PathLike[str] | str, key_epoch: KeyEpoch, *, replicas: int = 3,
                 max_spool_records: int = 1024) -> None:
        if replicas < 3:
            raise ValueError("at least three independent replicas are required")
        if max_spool_records < 1:
            raise ValueError("max_spool_records must be positive")
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.spool = self.root / "spool"
        self.spool.mkdir(exist_ok=True)
        self.replicas = tuple(self.root / f"replica_{i}.jsonl" for i in range(replicas))
        self.epochs_path = self.root / "key_epochs.jsonl"
        self.max_spool_records = max_spool_records
        self.key_epoch = key_epoch
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._worker: threading.Thread | None = None
        self._persist_epoch(key_epoch)

    def _persist_epoch(self, epoch: KeyEpoch) -> None:
        existing = []
        if self.epochs_path.exists():
            existing = [json.loads(x) for x in self.epochs_path.read_text().splitlines() if x.strip()]
        if not existing or existing[-1]["key_id"] != epoch.key_id:
            with self.epochs_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(epoch), sort_keys=True) + "\n")
                f.flush(); os.fsync(f.fileno())

    def rotate_key(self, new_key: bytes) -> KeyEpoch:
        with self._lock:
            new_epoch = self.key_epoch.rotate(new_key)
            if not new_epoch.verify_transition(self.key_epoch):
                raise RuntimeError("dual-signed key transition failed")
            self._persist_epoch(new_epoch)
            self.key_epoch = new_epoch
            return new_epoch

    def _load_records(self, path: Path) -> list[Hash216Record] | None:
        if not path.exists(): return []
        try:
            return [Hash216Record(**json.loads(line)) for line in path.read_text().splitlines() if line.strip()]
        except (json.JSONDecodeError, TypeError, ValueError):
            return None

    def _majority_chain(self) -> list[Hash216Record]:
        chains = [self._load_records(p) for p in self.replicas]
        serial = [json.dumps([asdict(r) for r in c], sort_keys=True) if c is not None else "__INVALID_REPLICA__" + str(i)
                  for i, c in enumerate(chains)]
        candidates = [x for x in serial if not x.startswith("__INVALID_REPLICA__")]
        if not candidates:
            raise RuntimeError("replica quorum unavailable")
        winner = max(set(candidates), key=candidates.count)
        if serial.count(winner) < (len(serial)//2 + 1):
            raise RuntimeError("replica quorum unavailable")
        return [Hash216Record(**x) for x in json.loads(winner)]

    def _sign(self, body: Mapping[str, Any], key: bytes | None = None) -> str:
        return hmac.new(key or self.key_epoch.key, RECORD_DOMAIN + canonical_bytes(body), sha256).hexdigest()

    def _epoch_key(self, epoch: int, key_id: str) -> bytes | None:
        if not self.epochs_path.exists(): return None
        for line in self.epochs_path.read_text().splitlines():
            if not line.strip(): continue
            item = KeyEpoch(**json.loads(line))
            if item.epoch == epoch and item.key_id == key_id:
                return item.key
        return None

    def verify_record(self, record: Hash216Record, previous_root: str) -> bool:
        payload = zlib.decompress(base64.b64decode(record.payload_b64))
        if sha256(payload).hexdigest() != record.payload_sha256: return False
        positions = Hash216Genome.positions(payload, previous_root=previous_root, sequence=record.sequence)
        if positions != tuple(record.positions): return False
        if Hash216Genome.root(positions) != record.genome_root: return False
        if record.previous_root != previous_root: return False
        key = self._epoch_key(record.key_epoch, record.key_id)
        if key is None: return False
        return hmac.compare_digest(record.signature, self._sign(record.body(), key))

    def inspect(self, event_type: str, actor: str, payload: Any, *, reversal_of: str | None = None) -> Hash216Record:
        if not event_type or not actor: raise ValueError("event_type and actor are required")
        with self._lock:
            if len(list(self.spool.glob("*.json"))) >= self.max_spool_records:
                raise BufferError("hard spool bound reached")
            chain = self._majority_chain()
            pending = []
            for pending_path in sorted(self.spool.glob("*.json")):
                pending.append(Hash216Record(**json.loads(pending_path.read_text())))
            previous_root = pending[-1].genome_root if pending else (chain[-1].genome_root if chain else "0" * 64)
            sequence = len(chain) + len(pending)
            raw = canonical_bytes(payload)
            positions = Hash216Genome.positions(raw, previous_root=previous_root, sequence=sequence)
            body = dict(record_id=str(uuid.uuid4()), sequence=sequence, timestamp_ns=time.time_ns(),
                        event_type=event_type, actor=actor,
                        payload_b64=base64.b64encode(zlib.compress(raw, 9)).decode(),
                        payload_sha256=sha256(raw).hexdigest(), positions=positions,
                        genome_root=Hash216Genome.root(positions), previous_root=previous_root,
                        key_epoch=self.key_epoch.epoch, key_id=self.key_epoch.key_id,
                        vm81_echo_required=True, reversal_of=reversal_of)
            record = Hash216Record(signature=self._sign(body), **body)
            temp = self.spool / f"{sequence:020d}-{record.record_id}.tmp"
            final = temp.with_suffix(".json")
            temp.write_text(json.dumps(asdict(record), sort_keys=True), encoding="utf-8")
            with temp.open("rb") as f: os.fsync(f.fileno())
            os.replace(temp, final)
            return record

    def flush(self) -> int:
        with self._lock:
            files = sorted(self.spool.glob("*.json"))
            committed = 0
            for item in files:
                line = item.read_text(encoding="utf-8") + "\n"
                record = Hash216Record(**json.loads(line))
                for replica in self.replicas:
                    with replica.open("a", encoding="utf-8") as f:
                        f.write(line); f.flush(); os.fsync(f.fileno())
                item.unlink()
                committed += 1
            return committed

    def recover(self) -> dict[str, int]:
        with self._lock:
            removed_tmp = 0
            for item in self.spool.glob("*.tmp"):
                item.unlink(); removed_tmp += 1
            chain = self._majority_chain()
            canonical = "".join(json.dumps(asdict(r), sort_keys=True) + "\n" for r in chain)
            repaired = 0
            for replica in self.replicas:
                if (replica.read_text() if replica.exists() else "") != canonical:
                    replica.write_text(canonical); repaired += 1
            self.validate_chain()
            return {"removed_tmp": removed_tmp, "repaired_replicas": repaired, "records": len(chain)}

    def validate_chain(self) -> bool:
        chain = self._majority_chain()
        previous = "0" * 64
        for index, record in enumerate(chain):
            if record.sequence != index or not self.verify_record(record, previous):
                raise ValueError(f"invalid chain record {index}")
            previous = record.genome_root
        return True

    def reverse(self, record_id: str, actor: str, reason: str) -> Hash216Record:
        chain = self._majority_chain()
        target = next((x for x in chain if x.record_id == record_id), None)
        if target is None: raise KeyError(record_id)
        return self.inspect("REVERSAL", actor, {"target": record_id, "reason": reason,
                    "target_root": target.genome_root}, reversal_of=record_id)

    def signal(self, name: str, payload: Any) -> Hash216Record:
        return self.inspect("SIGNAL", "hash216-airgap", {"name": name, "payload": payload})

    def echo_for_vm81(self, record: Hash216Record) -> dict[str, Any]:
        return {"schema": "HHS_P150_VM81_ECHO_V1", "record_id": record.record_id,
                "genome_root": record.genome_root, "sequence": record.sequence,
                "requires_vm81_validation": True, "mutation_authority": False}

    def start_worker(self, interval: float = 0.05) -> None:
        if self._worker and self._worker.is_alive(): return
        self._stop.clear()
        def run() -> None:
            while not self._stop.wait(interval):
                try: self.flush()
                except Exception: pass
        self._worker = threading.Thread(target=run, name="hhs-hash216-airgap", daemon=True)
        self._worker.start()

    def stop_worker(self) -> None:
        self._stop.set()
        if self._worker: self._worker.join(timeout=2)
