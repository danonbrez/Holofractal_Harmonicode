from __future__ import annotations
import re
from pathlib import Path
from .common import canonical_json, sha256_text, atomic_write

NORMATIVE = re.compile(r"\b(SHALL NOT|MUST NOT|SHALL|MUST|REQUIRED|MAY|OPTIONAL)\b", re.I)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SENTENCE = re.compile(r"(?<=[.!?;:])\s+(?=[A-Z`*])")

class ContractCompiler:
    def __init__(self, contract_id: str = "HHS-P151-CGILP"):
        self.contract_id = contract_id

    def compile_text(self, text: str, source_path: str) -> dict:
        section = "ROOT"; obligations=[]; propositions=[]
        buffer=[]
        def flush():
            nonlocal buffer
            paragraph=" ".join(x.strip() for x in buffer if x.strip()).strip(); buffer=[]
            if not paragraph: return
            for raw in SENTENCE.split(paragraph):
                sentence=raw.strip(" -*\t")
                if not sentence: continue
                proposition_id="P151-PROP-"+sha256_text(f"{self.contract_id}|{section}|{sentence}")[:20].upper()
                propositions.append({"proposition_id": proposition_id,"source_path":source_path,"source_section":section,"verbatim_text":sentence,"authority":"RATIFIED_CONTRACT"})
                m=NORMATIVE.search(sentence)
                if not m: continue
                strength=m.group(1).upper()
                oid="P151-OBL-"+sha256_text(f"{self.contract_id}|{section}|{sentence}")[:24].upper()
                obligations.append({
                    "obligation_id":oid,"source_contract_id":self.contract_id,"source_path":source_path,
                    "source_section":section,"verbatim_text":sentence,"normative_strength":strength,
                    "authority_domain":self._authority(sentence),"implementation_required":strength not in {"MAY","OPTIONAL"},
                    "reachability_required":strength not in {"MAY","OPTIONAL"},"positive_tests_required":strength not in {"MAY","OPTIONAL"},
                    "negative_tests_required":"NOT" in strength or any(w in sentence.lower() for w in ("reject","prohibit","never","no ")),
                    "evidence_required":strength not in {"MAY","OPTIONAL"},"artifact_required":"artifact" in sentence.lower() or "contain" in sentence.lower(),
                    "dependencies":[],"prohibitions":self._prohibitions(sentence),"terminal_effect":"BLOCKS_FULL_SUCCESS" if strength not in {"MAY","OPTIONAL"} else "NON_BLOCKING",
                    "supersession_state":"ACTIVE","proposition_id":proposition_id
                })
        in_fence=False
        for line in text.splitlines():
            if line.strip().startswith("```"): in_fence=not in_fence
            if not in_fence:
                hm=HEADING.match(line)
                if hm:
                    flush(); section=hm.group(2).strip(); continue
            if not line.strip(): flush()
            elif not line.lstrip().startswith(("|","[","\\","```")): buffer.append(line)
        flush()
        root=sha256_text(text)
        return {"schema":"HHS_PASS151_COMPILED_CONTRACT_V1","contract_id":self.contract_id,"contract_root":root,
                "source_path":source_path,"obligation_count":len(obligations),"proposition_count":len(propositions),
                "obligations":obligations,"propositions":propositions}

    def compile_file(self, path: str | Path) -> dict:
        p=Path(path); return self.compile_text(p.read_text(encoding="utf-8"), p.as_posix())

    def write(self, compiled: dict, obligation_path: str | Path, roots_path: str | Path) -> None:
        lines="".join(canonical_json(o)+"\n" for o in compiled["obligations"])
        atomic_write(obligation_path, lines)
        roots={k:compiled[k] for k in ("schema","contract_id","contract_root","source_path","obligation_count","proposition_count")}
        atomic_write(roots_path, canonical_json(roots)+"\n")

    @staticmethod
    def _authority(text: str) -> str:
        t=text.lower()
        if "vm81" in t or "native" in t: return "VM81_NATIVE"
        if "hash72" in t: return "HASH72_RECEIPT"
        if "hash216" in t: return "HASH216_SECURITY"
        if "semantic reasoner" in t: return "SEMANTIC_ADVISORY"
        if "executor" in t or "tool" in t: return "CONTRACT_EXECUTOR"
        return "CONTRACT_GOVERNANCE"

    @staticmethod
    def _prohibitions(text: str) -> list[str]:
        return [text] if NORMATIVE.search(text) and "NOT" in NORMATIVE.search(text).group(1).upper() else []
