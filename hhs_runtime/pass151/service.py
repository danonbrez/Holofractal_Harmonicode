from __future__ import annotations
import json
from pathlib import Path
from .contract_compiler import ContractCompiler
from .ledger import ObligationLedger
from .context_membrane import ContextConstraintMembrane
from .executor import DeterministicContractExecutor
from .semantic_reasoner import BoundedSemanticReasoner
from .native_bridge import RuntimeNativeValidationBridge
from .evidence import EvidenceReconciler
from .future_templates import FutureTemplateEngine
from .temporal_math import TemporalContextMathEngine, NoveltyEfficiencyScheduler
from .terminal import TerminalClassificationGate
from .replay import ReplayEngine
class Pass151Service:
    def __init__(self,root:str|Path):
        self.root=Path(root); data=self.root/"data/pass151"; receipts=self.root/"receipts/pass151"
        self.compiler=ContractCompiler(); self.ledger=ObligationLedger(data/"obligation_ledger_v2.sqlite3")
        self.context=ContextConstraintMembrane(); self.executor=DeterministicContractExecutor(self.root,receipts/"executor_trace.jsonl")
        self.reasoner=BoundedSemanticReasoner(); self.native=RuntimeNativeValidationBridge(receipts/"native_claims.jsonl")
        self.evidence=EvidenceReconciler(); self.future=FutureTemplateEngine(); self.temporal=TemporalContextMathEngine(); self.scheduler=NoveltyEfficiencyScheduler(); self.terminal=TerminalClassificationGate(); self.replay=ReplayEngine()
    def contract_load(self,path): return Path(path).read_text(encoding="utf-8")
    def contract_compile(self,path):
        c=self.compiler.compile_file(path); self.ledger.import_obligations(c["obligations"]); return c
    def obligation_list(self,state=None): return self.ledger.list(state)
    def obligation_read(self,oid): return self.ledger.read(oid)
    def obligation_transition(self,oid,state,evidence): return self.ledger.transition(oid,state,evidence)
    def executor_plan(self,ids,actions): return self.executor.plan(ids,actions)
    def executor_run(self,argv,ids,timeout=30,cwd=None): return self.executor.run(argv,ids,timeout,cwd)
    def semantic_request_create(self,*a,**k): return self.reasoner.request(*a,**k)
    def semantic_response_admit(self,response,binding): return self.context.admission({"text":response.get("diagnosis",""),"declares_completion":response.get("declares_completion",False),"preserved_obligations":response.get("verbatim_contract_text",[])},binding)
    def native_claim_submit(self,claim): return self.native.submit(claim)
    def evidence_reconcile(self,obligation,evidence): return self.evidence.reconcile(obligation,evidence)
    def context_classify(self,*a,**k): return self.context.classify(*a,**k)
    def context_decay_update(self,*a,**k): return self.temporal.evaluate(*a,**k)
    def future_opcode_preallocate(self,*a,**k): return self.future.preallocate(*a,**k)
    def future_dependency_bind(self,*a,**k): return self.future.bind(*a,**k)
    def future_template_invalidate(self,*a,**k): return self.future.invalidate(*a,**k)
    def terminal_classify(self,**k): return self.terminal.classify(self.ledger.list(),**k)
    def replay_state(self,paths,out): return self.replay.snapshot(paths,out)
    def export_evidence(self,path):
        payload={"schema":"HHS_PASS151_EVIDENCE_EXPORT_V1","obligations":self.ledger.list(),"chain_valid":self.ledger.verify_chain()}; Path(path).write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",encoding="utf-8"); return payload
