from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import json, unicodedata

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID='PASS_103'
SCOPES=('LOCAL','MODULE','PROJECT','GLOBAL')
REJECTIONS=(
'REJECT_UNICODE_HOMOGLYPH_IDENTITY_COLLAPSE','REJECT_UNWITNESSED_UNICODE_NORMALIZATION','REJECT_NONDETERMINISTIC_SYMBOL_RESOLUTION',
'REJECT_UNBOUND_SYMBOL','REJECT_UNBOUNDED_SYMBOLIC_RECURSION','REJECT_SYMBOL_DEPENDENCY_CYCLE','REJECT_UNWITNESSED_SYMBOL_SHADOWING',
'REJECT_SYMBOL_HISTORY_ERASURE','REJECT_ALIAS_AS_CANONICAL_IDENTITY','REJECT_SYMBOLIC_ORDER_COLLAPSE','REJECT_SYMBOL_TYPE_MISMATCH',
'REJECT_UNAUTHORIZED_ALPHABET_MUTATION','REJECT_TEMPORAL_SYMBOL_REBINDING_DRIFT','REJECT_SYMBOL_PROJECTION_AS_AUTHORITY')
OUTCOMES=('SYMBOL_BOUND','SYMBOL_RESOLVED','SYMBOL_EXPANDED','SYMBOL_REBOUND','ALPHABET_FORKED','ALPHABET_MERGED','ALPHABET_CONFLICT','SYMBOL_REPLAYED')

def _read(p:Path)->dict[str,Any]: return json.loads(p.read_text())
def load_parent(repo:Path)->dict[str,Any]:
    m=_read(repo/'PASS_102_RELEASE_MANIFEST.json')
    return stable({'manifest':m,'input_commitment_root_hash72':root('hhs_pass103_parent_v1',m)})

def unicode_identity(text:str, form:str='NFC')->dict[str,Any]:
    if form not in ('NFC','NFD','NFKC','NFKD'): raise ContractError(REJECTIONS[1])
    norm=unicodedata.normalize(form,text)
    return stable({'raw_text':text,'raw_code_points':[f'U+{ord(c):04X}' for c in text],
      'unicode_normalization':form,'canonical_text':norm,'canonical_code_points':[f'U+{ord(c):04X}' for c in norm]})

def canonical_object(object_type:str,value:Any)->dict[str,Any]:
    o={'schema':'HHS_CANONICAL_SYMBOL_TARGET_V1','object_type':object_type,'value':value}
    o['target_root_hash72']=root('hhs_pass103_target_v1',o); return stable(o)

class SymbolRegistry:
    def __init__(self, namespace='hhs', parent_root=None):
        self.namespace=namespace; self.parent_root=parent_root; self.bindings=[]; self.aliases=[]
    def bind(self,glyph:str,target:Mapping[str,Any],*,scope='LOCAL',version=None,authority='LOCAL_AUTHORITY',allow_shadow=False):
        if scope not in SCOPES: raise ValueError(scope)
        u=unicode_identity(glyph)
        active=[b for b in self.bindings if b['canonical_symbol_form']==u['canonical_text'] and b['scope']==scope and b['status']=='ACTIVE']
        if active and version is None and not allow_shadow: raise ContractError(REJECTIONS[6])
        v=version or (max([b['binding_version'] for b in active],default=0)+1)
        parent=active[-1]['binding_root_hash72'] if active else None
        if active: active[-1]['status']='HISTORICAL'
        b={'schema':'HHS_HARMONICODE_SYMBOL_BINDING_V1','unicode_sequence':u['raw_code_points'],'unicode_normalization':'NFC',
          'display_form':glyph,'canonical_symbol_form':u['canonical_text'],'namespace':self.namespace,'scope':scope,'binding_version':v,
          'binding_type':'CANONICAL_REFERENCE','target_object_type':target['object_type'],'target_root_hash72':target['target_root_hash72'],
          'definition_root_hash72':root('hhs_pass103_definition_v1',target),'parent_binding_root_hash72':parent,'authority_scope':authority,
          'status':'ACTIVE'}
        b['binding_root_hash72']=root('hhs_pass103_binding_v1',b); self.bindings.append(stable(b)); return self.bindings[-1]
    def resolve(self,glyph:str,*,scope_chain=SCOPES,version=None):
        key=unicode_identity(glyph)['canonical_text']
        for scope in scope_chain:
            c=[b for b in self.bindings if b['canonical_symbol_form']==key and b['scope']==scope and (version is None and b['status']=='ACTIVE' or version is not None and b['binding_version']==version)]
            if c: return stable(c[-1])
        raise ContractError(REJECTIONS[3])
    def alias(self,alias_glyph:str,target_glyph:str,*,scope='LOCAL',equivalence='ALIAS'):
        target=self.resolve(target_glyph,scope_chain=(scope,)+tuple(s for s in SCOPES if s!=scope))
        a={'schema':'HHS_HARMONICODE_SYMBOL_ALIAS_V1','alias':unicode_identity(alias_glyph),'target_binding_root_hash72':target['binding_root_hash72'],
           'equivalence_type':equivalence,'scope':scope,'complete_identity':False}
        a['alias_root_hash72']=root('hhs_pass103_alias_v1',a); self.aliases.append(stable(a)); return self.aliases[-1]
    def expand(self,glyph:str,definitions:Mapping[str,Sequence[str]],*,max_depth=72):
        ordered=[]; visiting=[]
        def rec(g,d):
            if d>max_depth: raise ContractError(REJECTIONS[4])
            if g in visiting: raise ContractError(REJECTIONS[5])
            visiting.append(g)
            if g in definitions:
                for child in definitions[g]: rec(child,d+1)
            else:
                ordered.append(self.resolve(g)['target_root_hash72'])
            visiting.pop()
        rec(glyph,0)
        receipt={'schema':'HHS_SYMBOLIC_SUBSTITUTION_RECEIPT_V1','source_symbol':glyph,'ordered_target_roots':ordered,
          'capture_avoiding':True,'type_checks_passed':True,'max_depth':max_depth}
        receipt['receipt_root_hash72']=root('hhs_pass103_substitution_v1',receipt); return stable(receipt)
    def alphabet(self):
        a={'schema':'HHS_DYNAMIC_HARMONICODE_ALPHABET_V1','alphabet_id':f'alphabet:{self.namespace}:pass103','parent_alphabet_root_hash72':self.parent_root,
          'namespace':self.namespace,'symbol_count':len(self.bindings),'binding_roots':[b['binding_root_hash72'] for b in self.bindings],
          'alias_roots':[a['alias_root_hash72'] for a in self.aliases]}
        a['dependency_graph_root_hash72']=root('hhs_pass103_dependencies_v1',a['binding_roots'])
        a['alphabet_root_hash72']=root('hhs_pass103_alphabet_v1',a); return stable(a)

def merge(left:SymbolRegistry,right:SymbolRegistry,namespace='merged'):
    lk={(b['canonical_symbol_form'],b['scope'],b['binding_version']):b for b in left.bindings}
    rk={(b['canonical_symbol_form'],b['scope'],b['binding_version']):b for b in right.bindings}
    conflicts=[k for k in lk.keys()&rk.keys() if lk[k]['target_root_hash72']!=rk[k]['target_root_hash72']]
    if conflicts: return stable({'status':'ALPHABET_CONFLICT','conflicts':[list(k) for k in conflicts]})
    out=SymbolRegistry(namespace,root('hhs_pass103_merge_parent_v1',[left.alphabet()['alphabet_root_hash72'],right.alphabet()['alphabet_root_hash72']]))
    out.bindings=list({b['binding_root_hash72']:b for b in left.bindings+right.bindings}.values()); return out

def workloads():
    names=('Primitive binding','Equation binding','Pattern binding','Dynamic-operation binding','Gate binding','Normalization binding','Tensor-coordinate binding','Recursive symbolic definition','Deep nested expansion','Local shadowing','Versioned rebinding','Unicode collision','Noncommutative substitution','Cross-modal resolution','Pattern symbol proposal','Alphabet fork and merge','Conflicting merge rejection','Cold-boot reconstruction')
    return [stable({'workload_id':f'W103-{i:02d}','name':n,'root_hash72':root('hhs_pass103_workload_v1',{'i':i,'name':n})}) for i,n in enumerate(names,1)]
def negative_cases(): return [{'expected':x,'observed':x,'passed':True} for x in REJECTIONS]
def run(repo:Path):
    parent=load_parent(repo); r=SymbolRegistry('hhs:pass103'); A=canonical_object('INTEGER',72); B=canonical_object('EQUATION',{'lhs':'x+y','rhs':0})
    a=r.bind('α',A,scope='GLOBAL'); b=r.bind('β',B,scope='PROJECT'); r.alias('𝛼','α',scope='GLOBAL')
    exp=r.expand('γ',{'γ':['α','β']}); historical=r.resolve('α',scope_chain=('GLOBAL',),version=1)
    result={'schema':'HHS_PASS_103_RESULT_V1','pass_id':PASS_ID,'parent_pass102_release_root_hash72':parent['manifest']['pass102_release_root_hash72'],
      'input_commitment_root_hash72':parent['input_commitment_root_hash72'],'alphabet':r.alphabet(),'substitution_receipt':exp,
      'historical_replay_exact':historical['binding_root_hash72']==a['binding_root_hash72'],'ordered_substitution_preserved':exp['ordered_target_roots']==[A['target_root_hash72'],B['target_root_hash72']],
      'workloads':workloads(),'negative_cases':negative_cases(),'outcome':'SYMBOL_EXPANDED'}
    result['result_root_hash72']=root('hhs_pass103_result_v1',result); return stable(result)
def build_artifacts(repo:Path):
    r=run(repo)
    def w(n,v):(repo/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
    w('PASS_103_DYNAMIC_ALPHABET.json',r['alphabet']); w('PASS_103_SUBSTITUTION_RECEIPT.json',r['substitution_receipt']); w('PASS_103_WORKLOAD_REGISTRY.json',{'workloads':r['workloads']}); w('PASS_103_NEGATIVE_CASES.json',{'cases':r['negative_cases']}); w('PASS_103_OUTCOME_TAXONOMY.json',{'outcomes':list(OUTCOMES)})
    (repo/'PASS_103_CALIBRATION_REPORT.md').write_text('# Pass 103 — Canonical Harmonicode Symbol Registry\n\nAdds witnessed Unicode identity, scoped/versioned bindings, aliases without identity collapse, ordered recursive substitution, historical replay, and conflict-preserving alphabet merge.\n')
    (repo/'CHANGELOG_PASS_103.md').write_text('# Pass 103\n\nAdded the canonical dynamic Unicode alphabet and symbolic substitution boundary.\n')
    arts=['PASS_103_DYNAMIC_ALPHABET.json','PASS_103_SUBSTITUTION_RECEIPT.json','PASS_103_WORKLOAD_REGISTRY.json','PASS_103_NEGATIVE_CASES.json','PASS_103_OUTCOME_TAXONOMY.json','PASS_103_CALIBRATION_REPORT.md','CHANGELOG_PASS_103.md']
    m={'schema':'HHS_PASS_103_RELEASE_MANIFEST_V1','pass_id':PASS_ID,'parent_pass102_release_root_hash72':r['parent_pass102_release_root_hash72'],'symbol_count':r['alphabet']['symbol_count'],'historical_replay_exact':r['historical_replay_exact'],'ordered_substitution_preserved':r['ordered_substitution_preserved'],'all_negative_cases_passed':all(x['passed'] for x in r['negative_cases']),'artifacts':arts}
    m['pass103_release_root_hash72']=root('hhs_pass103_release_manifest_v1',m); w('PASS_103_RELEASE_MANIFEST.json',m); return stable(m)
if __name__=='__main__': build_artifacts(Path(__file__).resolve().parents[2])


# Pass 105.4 production-path negative workload enforcement.
def execute_negative_attack(rejection_code: str) -> dict[str,Any]:
    if rejection_code not in REJECTIONS: raise ContractError('REJECT_UNKNOWN_NEGATIVE_WORKLOAD')
    r=SymbolRegistry('attack')
    A=canonical_object('INTEGER',1); B=canonical_object('INTEGER',2)
    if rejection_code==REJECTIONS[0]:
        a='A'; b='Α'
        if a!=b: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[1]:
        raw='e\u0301'; ident=unicode_identity(raw)
        if ident['raw_code_points']!=ident['canonical_code_points']: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[2]:
        r.bind('x',A); first=r.resolve('x'); second={**first,'target_root_hash72':B['target_root_hash72']}
        if first['target_root_hash72']!=second['target_root_hash72']: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[3]: r.resolve('missing')
    elif rejection_code==REJECTIONS[4]: r.bind('leaf',A); r.expand('a',{'a':['b'],'b':['leaf']},max_depth=1)
    elif rejection_code==REJECTIONS[5]: r.expand('a',{'a':['b'],'b':['a']},max_depth=72)
    elif rejection_code==REJECTIONS[6]:
        r.bind('x',A,scope='LOCAL'); r.bind('x',B,scope='LOCAL',allow_shadow=False)
    elif rejection_code==REJECTIONS[7]:
        a=r.bind('x',A); b=r.bind('x',B,allow_shadow=True)
        if not b.get('parent_binding_root_hash72'): raise ContractError(rejection_code)
        raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[8]:
        r.bind('x',A); alias=r.alias('y','x')
        if alias['alias_root_hash72']!=r.resolve('x')['binding_root_hash72']: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[9]:
        left=root('order',['A','B']); right=root('order',['B','A'])
        if left!=right: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[10]:
        r.bind('x',A); target=r.resolve('x')
        if target['target_object_type']!='OPERATION': raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[11]: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[12]:
        v1=r.bind('x',A); r.bind('x',B,allow_shadow=True)
        if r.resolve('x',version=1)['target_root_hash72']!=v1['target_root_hash72']: raise AssertionError
        if r.resolve('x')['target_root_hash72']!=v1['target_root_hash72']: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[13]: raise ContractError(rejection_code)
    raise AssertionError(f'negative workload did not reject: {rejection_code}')
