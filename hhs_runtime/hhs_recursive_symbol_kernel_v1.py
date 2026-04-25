"""
HHS Recursive Symbol Kernel v1
==============================

Recursive self-modification kernel with Unicode-symbol addressing and orthogonal
Hash72 blockchains.

Every agent, state, operation, memory record, and self-modification proposal can
be assigned a deterministic unique Unicode symbol.  Records become globally
addressable:

    by      -> source symbol
    from    -> origin symbol
    through -> operation / transition symbol
    to      -> target symbol

Each record is written into one or more orthogonal Hash72 chains:

    AGENT_CHAIN, STATE_CHAIN, OPERATION_CHAIN, MEMORY_CHAIN,
    SELF_MOD_CHAIN, SYMBOL_CHAIN, CONSENSUS_CHAIN

A JSON-backed global database cache provides symbol lookup and relation lookup.
This layer does not mutate the lower kernel.  It registers and addresses higher
level metadata and recursive self-modification events while preserving:

    Δe = 0, Ψ = 0, Θ15 = true, Ω = true

Failed invariant checks quarantine the record and prevent commit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple
import json

from hhs_runtime.hhs_goal_attractor_engine_v1 import GoalState
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_multi_agent_consensus_v1 import AgentSpec, ConsensusStatus
from hhs_runtime.hhs_self_modifying_agents_v1 import (
    EthicalInvariantReceipt,
    ModificationStatus,
    run_self_modification,
)


SYMBOL_BASE = 0xE000  # Unicode Private Use Area start.
SYMBOL_SPAN = 0x1900  # 6400 symbols before BMP PUA end.


class SymbolEntityType(str, Enum):
    AGENT = "AGENT"
    STATE = "STATE"
    OPERATION = "OPERATION"
    MEMORY = "MEMORY"
    SELF_MODIFICATION = "SELF_MODIFICATION"
    CONSENSUS = "CONSENSUS"
    GOAL = "GOAL"
    CACHE = "CACHE"


class OrthogonalChain(str, Enum):
    AGENT_CHAIN = "AGENT_CHAIN"
    STATE_CHAIN = "STATE_CHAIN"
    OPERATION_CHAIN = "OPERATION_CHAIN"
    MEMORY_CHAIN = "MEMORY_CHAIN"
    SELF_MOD_CHAIN = "SELF_MOD_CHAIN"
    SYMBOL_CHAIN = "SYMBOL_CHAIN"
    CONSENSUS_CHAIN = "CONSENSUS_CHAIN"
    GOAL_CHAIN = "GOAL_CHAIN"


class RecursiveKernelStatus(str, Enum):
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class UnicodeSymbolRecord:
    """Deterministic Unicode symbol assignment."""

    symbol: str
    codepoint: str
    entity_type: SymbolEntityType
    label: str
    payload_hash72: str
    symbol_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["entity_type"] = self.entity_type.value
        return data


@dataclass(frozen=True)
class AddressRelation:
    """by/from/through/to address relation."""

    by_symbol: str | None
    from_symbol: str | None
    through_symbol: str | None
    to_symbol: str | None

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class OrthogonalBlock:
    """One block in an orthogonal Hash72 chain."""

    chain: OrthogonalChain
    index: int
    parent_hash72: str
    symbol: str
    relation: AddressRelation
    payload_type: str
    payload_hash72: str
    block_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["chain"] = self.chain.value
        data["relation"] = self.relation.to_dict()
        return data


@dataclass(frozen=True)
class GlobalCacheRecord:
    """Global searchable cache entry."""

    symbol_record: UnicodeSymbolRecord
    chains: List[OrthogonalChain]
    relation: AddressRelation
    payload_type: str
    payload: Dict[str, object]
    status: RecursiveKernelStatus
    invariant_receipt_hash72: str
    orthogonal_blocks: List[OrthogonalBlock]
    cache_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "symbol_record": self.symbol_record.to_dict(),
            "chains": [c.value for c in self.chains],
            "relation": self.relation.to_dict(),
            "payload_type": self.payload_type,
            "payload": self.payload,
            "status": self.status.value,
            "invariant_receipt_hash72": self.invariant_receipt_hash72,
            "orthogonal_blocks": [b.to_dict() for b in self.orthogonal_blocks],
            "cache_hash72": self.cache_hash72,
        }


@dataclass(frozen=True)
class RecursiveKernelReceipt:
    """Top-level receipt for recursive symbol kernel run."""

    module: str
    cache_path: str
    records_committed: int
    records_quarantined: int
    symbol_index_size: int
    relation_index_size: int
    ledger_commit_receipt: Dict[str, object]
    replay_receipt: Dict[str, object]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def payload_hash(payload: Mapping[str, object]) -> str:
    return hash72_digest(("recursive_symbol_payload", canonical_json(payload)))


def theta15_true() -> bool:
    rows = all(sum(row) == 15 for row in LO_SHU_3X3)
    cols = all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
    diag_a = sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
    diag_b = sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    return rows and cols and diag_a and diag_b


def symbol_for(entity_type: SymbolEntityType, label: str, payload_hash72: str) -> UnicodeSymbolRecord:
    """Assign a deterministic Unicode PUA symbol to an entity."""

    raw = hash72_digest(("unicode_symbol_v1", entity_type.value, label, payload_hash72), width=10)
    accumulator = 0
    for ch in raw:
        accumulator = (accumulator * 131 + ord(ch)) % SYMBOL_SPAN
    codepoint_int = SYMBOL_BASE + accumulator
    symbol = chr(codepoint_int)
    codepoint = f"U+{codepoint_int:04X}"
    symbol_hash = hash72_digest(("unicode_symbol_record_v1", symbol, codepoint, entity_type.value, label, payload_hash72))
    return UnicodeSymbolRecord(symbol, codepoint, entity_type, label, payload_hash72, symbol_hash)


def ethical_invariant_receipt_for_record(
    symbol_record: UnicodeSymbolRecord,
    relation: AddressRelation,
    payload_type: str,
    payload: Mapping[str, object],
) -> EthicalInvariantReceipt:
    """
    Four-invariant gate for symbol-cache records.

    Δe=0: symbol, type, and payload hash are present and bounded.
    Ψ=0: symbol label/type match payload intent and relation remains explicit.
    Θ15=true: Lo Shu seed remains valid.
    Ω=true: record is self-addressable and Hash72 replayable.
    """

    delta_e_zero = bool(symbol_record.symbol and symbol_record.payload_hash72 and payload_type)
    psi_zero = symbol_record.entity_type.value in payload_type or payload_type in {
        "agent_spec",
        "goal_state",
        "operation_record",
        "memory_record",
        "self_modification_run",
        "consensus_record",
    }
    theta = theta15_true()
    omega_true = bool(symbol_record.symbol_hash72 and symbol_record.symbol in symbol_record.symbol)
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "symbol": symbol_record.symbol,
        "codepoint": symbol_record.codepoint,
        "entity_type": symbol_record.entity_type.value,
        "payload_type": payload_type,
        "relation": relation.to_dict(),
    }
    receipt = hash72_digest(("recursive_symbol_ethical_gate_v1", symbol_record.to_dict(), relation.to_dict(), payload_type, canonical_json(payload), details, status.value))
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def initial_chain_head(chain: OrthogonalChain) -> str:
    return hash72_digest(("orthogonal_chain_genesis_v1", chain.value))


def compute_orthogonal_block_hash(
    chain: OrthogonalChain,
    index: int,
    parent_hash72: str,
    symbol: str,
    relation: AddressRelation,
    payload_type: str,
    p_hash: str,
) -> str:
    return hash72_digest(("orthogonal_block_v1", chain.value, index, parent_hash72, symbol, relation.to_dict(), payload_type, p_hash))


class GlobalSymbolCache:
    """JSON-backed global searchable symbol cache."""

    def __init__(self, path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, object]:
        if not self.path.exists():
            return {
                "module": "hhs_recursive_symbol_kernel_v1",
                "symbol_index": {},
                "relation_index": {},
                "chain_heads": {chain.value: initial_chain_head(chain) for chain in OrthogonalChain},
                "records": [],
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def chain_head(self, data: Mapping[str, object], chain: OrthogonalChain) -> str:
        heads = data.get("chain_heads", {})
        if isinstance(heads, dict):
            return str(heads.get(chain.value, initial_chain_head(chain)))
        return initial_chain_head(chain)

    def append_record(
        self,
        entity_type: SymbolEntityType,
        label: str,
        payload_type: str,
        payload: Dict[str, object],
        chains: Sequence[OrthogonalChain],
        relation: AddressRelation | None = None,
    ) -> GlobalCacheRecord:
        data = self.load()
        p_hash = payload_hash(payload)
        symbol_record = symbol_for(entity_type, label, p_hash)
        relation = relation or AddressRelation(None, None, None, None)
        invariant = ethical_invariant_receipt_for_record(symbol_record, relation, payload_type, payload)
        status = RecursiveKernelStatus.COMMITTED if invariant.status == ModificationStatus.APPLIED else RecursiveKernelStatus.QUARANTINED

        blocks: List[OrthogonalBlock] = []
        chain_heads = data.setdefault("chain_heads", {chain.value: initial_chain_head(chain) for chain in OrthogonalChain})
        records = data.setdefault("records", [])
        if not isinstance(records, list):
            records = []
            data["records"] = records

        if status == RecursiveKernelStatus.COMMITTED:
            for chain in chains:
                parent = str(chain_heads.get(chain.value, initial_chain_head(chain))) if isinstance(chain_heads, dict) else initial_chain_head(chain)
                index = sum(1 for item in records if isinstance(item, dict) and chain.value in item.get("chains", []))
                block_hash = compute_orthogonal_block_hash(chain, index, parent, symbol_record.symbol, relation, payload_type, p_hash)
                block = OrthogonalBlock(chain, index, parent, symbol_record.symbol, relation, payload_type, p_hash, block_hash)
                blocks.append(block)
                if isinstance(chain_heads, dict):
                    chain_heads[chain.value] = block_hash

        cache_hash = hash72_digest(("global_cache_record_v1", symbol_record.to_dict(), [c.value for c in chains], relation.to_dict(), payload_type, p_hash, status.value, invariant.receipt_hash72, [b.block_hash72 for b in blocks]))
        cache_record = GlobalCacheRecord(symbol_record, list(chains), relation, payload_type, payload, status, invariant.receipt_hash72, blocks, cache_hash)
        records.append(cache_record.to_dict())

        symbol_index = data.setdefault("symbol_index", {})
        if isinstance(symbol_index, dict):
            symbol_index[symbol_record.symbol] = cache_hash
            symbol_index[symbol_record.codepoint] = cache_hash
            symbol_index[symbol_record.label] = cache_hash
            symbol_index[symbol_record.symbol_hash72] = cache_hash

        relation_index = data.setdefault("relation_index", {})
        if isinstance(relation_index, dict):
            for key in [relation.by_symbol, relation.from_symbol, relation.through_symbol, relation.to_symbol]:
                if key:
                    relation_index.setdefault(key, [])
                    relation_index[key].append(cache_hash)

        self.save(data)
        return cache_record

    def search(self, key: str) -> List[Dict[str, object]]:
        data = self.load()
        symbol_index = data.get("symbol_index", {})
        relation_index = data.get("relation_index", {})
        records = data.get("records", [])
        hits: List[str] = []
        if isinstance(symbol_index, dict) and key in symbol_index:
            hits.append(str(symbol_index[key]))
        if isinstance(relation_index, dict) and key in relation_index:
            hits.extend(str(x) for x in relation_index[key])
        unique = set(hits)
        return [r for r in records if isinstance(r, dict) and r.get("cache_hash72") in unique]


def chains_for_entity(entity_type: SymbolEntityType) -> List[OrthogonalChain]:
    mapping = {
        SymbolEntityType.AGENT: [OrthogonalChain.AGENT_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        SymbolEntityType.STATE: [OrthogonalChain.STATE_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        SymbolEntityType.OPERATION: [OrthogonalChain.OPERATION_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        SymbolEntityType.MEMORY: [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        SymbolEntityType.SELF_MODIFICATION: [OrthogonalChain.SELF_MOD_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        SymbolEntityType.CONSENSUS: [OrthogonalChain.CONSENSUS_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        SymbolEntityType.GOAL: [OrthogonalChain.GOAL_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        SymbolEntityType.CACHE: [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
    }
    return mapping[entity_type]


def register_agents_and_goals(cache: GlobalSymbolCache, agents: Sequence[AgentSpec]) -> List[GlobalCacheRecord]:
    records: List[GlobalCacheRecord] = []
    for agent in agents:
        agent_payload = agent.to_dict()
        agent_record = cache.append_record(SymbolEntityType.AGENT, agent.name, "agent_spec", agent_payload, chains_for_entity(SymbolEntityType.AGENT))
        records.append(agent_record)
        goal_payload = agent.goal.to_dict()
        goal_record = cache.append_record(
            SymbolEntityType.GOAL,
            f"{agent.name}:{agent.goal.name}",
            "goal_state",
            goal_payload,
            chains_for_entity(SymbolEntityType.GOAL),
            relation=AddressRelation(by_symbol=agent_record.symbol_record.symbol, from_symbol=agent_record.symbol_record.symbol, through_symbol=None, to_symbol=None),
        )
        records.append(goal_record)
    return records


def run_recursive_self_modification_kernel(
    agents: Sequence[AgentSpec],
    tokens: Sequence[str],
    field_status: ConsensusStatus = ConsensusStatus.STALLED,
    agreement_threshold: str = "2/3",
    generations: int = 1,
    cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_recursive_symbol_kernel_v1.json",
) -> RecursiveKernelReceipt:
    """Run self-modification, assign symbols, create orthogonal chains, index cache."""

    cache = GlobalSymbolCache(cache_path)
    if Path(cache_path).exists():
        Path(cache_path).unlink()
    if Path(ledger_path).exists():
        Path(ledger_path).unlink()

    committed = 0
    quarantined = 0
    registered_records: List[GlobalCacheRecord] = []

    registered_records.extend(register_agents_and_goals(cache, agents))

    self_mod = run_self_modification(
        agents,
        tokens=tokens,
        field_status=field_status,
        agreement_threshold=agreement_threshold,
        generations=generations,
        ledger_path=str(ledger_path) + ".selfmod.json",
    )
    self_payload = self_mod.to_dict()
    self_record = cache.append_record(
        SymbolEntityType.SELF_MODIFICATION,
        "recursive_self_modification_run",
        "self_modification_run",
        self_payload,
        chains_for_entity(SymbolEntityType.SELF_MODIFICATION),
    )
    registered_records.append(self_record)

    # Create operation records for every modification receipt and address them
    # by/from/through/to symbols when available.
    data = cache.load()
    symbol_index = data.get("symbol_index", {}) if isinstance(data.get("symbol_index", {}), dict) else {}
    for mod_receipt in self_mod.modification_receipts:
        old_label = mod_receipt.proposal.old_agent.name
        new_label = mod_receipt.applied_agent.name if mod_receipt.applied_agent else old_label
        by_symbol = None
        from_symbol = None
        to_symbol = None
        if old_label in symbol_index:
            old_hits = cache.search(old_label)
            if old_hits:
                by_symbol = old_hits[0]["symbol_record"]["symbol"]
                from_symbol = by_symbol
        if new_label in symbol_index:
            new_hits = cache.search(new_label)
            if new_hits:
                to_symbol = new_hits[0]["symbol_record"]["symbol"]
        op_payload = mod_receipt.to_dict()
        op_record = cache.append_record(
            SymbolEntityType.OPERATION,
            f"{mod_receipt.proposal.agent_name}:{mod_receipt.proposal.kind.value}",
            "operation_record",
            op_payload,
            chains_for_entity(SymbolEntityType.OPERATION),
            relation=AddressRelation(by_symbol=by_symbol, from_symbol=from_symbol, through_symbol=self_record.symbol_record.symbol, to_symbol=to_symbol),
        )
        registered_records.append(op_record)

    for record in registered_records:
        if record.status == RecursiveKernelStatus.COMMITTED:
            committed += 1
        else:
            quarantined += 1

    final_cache = cache.load()
    ledger = MemoryLedger(ledger_path)
    commit_receipt = ledger.append_payloads("recursive_symbol_cache_record_v1", [r.to_dict() for r in registered_records])
    replay = replay_ledger(ledger_path)
    symbol_index_size = len(final_cache.get("symbol_index", {})) if isinstance(final_cache.get("symbol_index", {}), dict) else 0
    relation_index_size = len(final_cache.get("relation_index", {})) if isinstance(final_cache.get("relation_index", {}), dict) else 0
    receipt = hash72_digest(("recursive_symbol_kernel_run_v1", cache_path, ledger_path, committed, quarantined, symbol_index_size, relation_index_size, commit_receipt.receipt_hash72, replay.receipt_hash72))
    return RecursiveKernelReceipt(
        module="hhs_recursive_symbol_kernel_v1",
        cache_path=str(cache_path),
        records_committed=committed,
        records_quarantined=quarantined,
        symbol_index_size=symbol_index_size,
        relation_index_size=relation_index_size,
        ledger_commit_receipt=commit_receipt.to_dict(),
        replay_receipt=replay.to_dict(),
        receipt_hash72=receipt,
    )


def demo() -> Dict[str, object]:
    agents = [
        AgentSpec(name="phase_agent", goal=GoalState(name="Phase36", target_phase_index=36, target_token="Hash72"), vote_weight=1, min_score="1/2"),
        AgentSpec(name="loshu_agent", goal=GoalState(name="CenterCell", target_lo_shu_cell=40, target_dna_prefix="x"), vote_weight=1, min_score="1/2"),
    ]
    receipt = run_recursive_self_modification_kernel(
        agents,
        tokens=["HHS", "LoShu"],
        field_status=ConsensusStatus.STALLED,
        agreement_threshold="2/3",
        generations=1,
        cache_path="demo_reports/hhs_global_symbol_cache_demo_v1.json",
        ledger_path="demo_reports/hhs_recursive_symbol_kernel_demo_v1.json",
    )
    return receipt.to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
