"""Executable HHS-I133 Semantic Continuity and Historical Interpretation Contract."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable

from .canonical import canonical_json, sha256_hex
from .hash72_checkpoint import make_hash72_witness

INVARIANTS = {
    "Ω1":"HISTORICAL_CONTINUITY",
    "Ω2":"SEMANTIC_RECONSTRUCTION",
    "Ω3":"ORIGIN_NOT_JUSTIFICATION",
    "Ω4":"DEVELOPMENT_CONSTRAINS_INTERPRETATION",
    "Ω5":"INTENT_PRESERVATION",
    "Ω6":"NARRATIVE_NON_SUBSTITUTION",
    "Ω7":"INCREMENTAL_MEANING",
    "Ω8":"CONTEXT_INTEGRITY",
    "Ω9":"INTERPRETATION_TRACEABILITY",
    "Ω10":"HISTORICAL_REPLAY",
    "Ω11":"DEVELOPMENTAL_MINIMALITY",
    "Ω12":"IDENTITY_THROUGH_EVOLUTION",
    "Ω13":"SEMANTIC_CONTINUITY_NOT_VALIDATION",
}


@dataclass(frozen=True)
class HistoryRecord:
    record_id: str
    parent_ids: tuple[str,...]
    authority_level: str
    kind: str
    content: dict[str,Any]
    explicit_intent: str | None = None

    def to_dict(self)->dict[str,Any]: return asdict(self)


def _closure(records:dict[str,HistoryRecord], required_ids:Iterable[str])->list[HistoryRecord]:
    needed=set(required_ids); stack=list(required_ids)
    while stack:
        rid=stack.pop()
        if rid not in records: raise ValueError(f"missing history record {rid}")
        for parent in records[rid].parent_ids:
            if parent not in needed: needed.add(parent); stack.append(parent)
    # Stable topological order by repeatedly admitting records whose parents are present.
    out=[]; admitted=set()
    while len(out)<len(needed):
        progress=False
        for rid in sorted(needed):
            rec=records[rid]
            if rid not in admitted and all(p in admitted for p in rec.parent_ids):
                out.append(rec); admitted.add(rid); progress=True
        if not progress: raise ValueError("historical cycle or missing parent")
    return out


def reconstruct_interpretation(
    *,
    current_object:dict[str,Any],
    history:list[HistoryRecord],
    required_record_ids:list[str],
    proposed_interpretation:dict[str,Any],
    introduced_assumptions:list[str] | None=None,
)->dict[str,Any]:
    introduced_assumptions=introduced_assumptions or []
    records={r.record_id:r for r in history}
    selected=_closure(records,required_record_ids)
    declared_intents=[{"record_id":r.record_id,"intent":r.explicit_intent} for r in selected if r.explicit_intent]
    unsupported_motivations=proposed_interpretation.get("motivations",[]) if not declared_intents else [
        m for m in proposed_interpretation.get("motivations",[]) if m not in {d["intent"] for d in declared_intents}
    ]
    continuity_ok=all(parent in records for r in selected for parent in r.parent_ids)
    minimal=set(r.record_id for r in selected)==set(_closure(records,required_record_ids)[i].record_id for i in range(len(selected)))
    interpretation={
        "schema":"HHS_I133_SEMANTIC_INTERPRETATION_V1",
        "current_object_hash":sha256_hex(current_object),
        "selected_history_ids":[r.record_id for r in selected],
        "declared_intents":declared_intents,
        "proposed_interpretation":proposed_interpretation,
        "introduced_assumptions":introduced_assumptions,
        "unsupported_motivations":unsupported_motivations,
        "authority_levels":[r.authority_level for r in selected],
        "governing_contracts":["HHS-I132","HHS-I133"],
        "semantic_continuity_valid":continuity_ok and minimal and not unsupported_motivations,
        "validation_authority_claimed":False,
        "invariants":INVARIANTS,
    }
    witness=make_hash72_witness("hhs_i133_semantic_interpretation_v1",interpretation).to_dict()
    interpretation["interpretation_hash"]=sha256_hex(interpretation)
    interpretation["hash72_witness"]=witness
    interpretation["status"]="SEMANTIC_CONTINUITY_RECONSTRUCTION_VERIFIED" if interpretation["semantic_continuity_valid"] else "UNAUTHORIZED_SEMANTIC_SUBSTITUTION_DETECTED"
    return interpretation


def replay_interpretation(payload:dict[str,Any])->bool:
    witness=payload["hash72_witness"]
    body={k:v for k,v in payload.items() if k not in {"interpretation_hash","hash72_witness","status"}}
    actual=make_hash72_witness("hhs_i133_semantic_interpretation_v1",body).to_dict()
    return actual["dna"]==witness["dna"]


def run_schic_self_test(parent_root:str)->dict[str,Any]:
    history=[
        HistoryRecord("origin",(),"A1","DECLARATION",{"name":"Harmonicode"},"Leverage a perspective and test stabilization intuitions."),
        HistoryRecord("algebra",("origin",),"A1","IMPLEMENTATION",{"event":"native algebra developed"}),
        HistoryRecord("hhs",("algebra",),"A1","IMPLEMENTATION",{"event":"HHS runtime passes"}),
        HistoryRecord("pass132",("hhs",),"A3","CHECKPOINT",{"root":parent_root}),
    ]
    valid=reconstruct_interpretation(
        current_object={"pass":"133","parent":parent_root},history=history,required_record_ids=["pass132"],
        proposed_interpretation={"meaning":"Continue demonstrated checkpoint development.","motivations":["Leverage a perspective and test stabilization intuitions."]},
    )
    invalid=reconstruct_interpretation(
        current_object={"pass":"133","parent":parent_root},history=history,required_record_ids=["pass132"],
        proposed_interpretation={"meaning":"Invented isolated reinterpretation.","motivations":["Validate a philosophy."]},
    )
    return {
        "schema":"HHS_I133_SCHIC_SELF_TEST_V1",
        "valid":valid,"invalid":invalid,
        "valid_replay":replay_interpretation(valid),
        "unauthorized_substitution_detected":invalid["status"]=="UNAUTHORIZED_SEMANTIC_SUBSTITUTION_DETECTED",
        "status":"PASS" if valid["semantic_continuity_valid"] and replay_interpretation(valid) and invalid["status"]=="UNAUTHORIZED_SEMANTIC_SUBSTITUTION_DETECTED" else "FAIL",
    }
