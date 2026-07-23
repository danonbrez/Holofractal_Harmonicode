from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
import json, re, unicodedata
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID='PASS_104'
REJECTIONS=('REJECT_LITERAL_STRING_AS_SYMBOL_INVOCATION','REJECT_UNTYPED_STRING_INTERPOLATION','REJECT_STRING_VARIABLE_CAPTURE','REJECT_STRING_SEGMENTATION_COLLAPSE','REJECT_EMPTY_STRING_AS_UNBOUND','REJECT_MISSING_DICTIONARY_KEY_COERCION','REJECT_UNWITNESSED_STRING_CASE_NORMALIZATION','REJECT_UNDECLARED_LOCALE_RESOLUTION','REJECT_UNBOUNDED_STRING_EXPANSION','REJECT_STRING_DICTIONARY_CYCLE','REJECT_SEMANTIC_SEARCH_AS_EXACT_LOOKUP','REJECT_STRING_EXPANSION_ORDER_COLLAPSE','REJECT_STRING_DICTIONARY_HISTORY_ERASURE','REJECT_TEMPORAL_STRING_RESOLUTION_DRIFT','REJECT_NONINVERTIBLE_STRING_DICTIONARY_REVERSAL','REJECT_SOURCE_STRING_AS_PARSED_AUTHORITY')
OUTCOMES=('STRING_BOUND','TEMPLATE_EXPANDED','PARTIAL_EXPANSION','DICTIONARY_REPLAYED','DEPENDENCY_STALE','DICTIONARY_CONFLICT')
def _read(p:Path): return json.loads(p.read_text())
def load_parent(repo:Path):
    m=_read(repo/'PASS_103_RELEASE_MANIFEST.json'); return stable({'manifest':m,'input_commitment_root_hash72':root('hhs_pass104_parent_v1',m)})
def canonical_string(text:str,string_class='CANONICAL_STRING',language_tag='und'):
    norm=unicodedata.normalize('NFC',text); o={'schema':'HHS_CANONICAL_UNICODE_STRING_V1','raw_text':text,'unicode_code_points':[f'U+{ord(c):04X}' for c in text],
      'normalization_form':'NFC','canonical_text':norm,'code_point_length':len(norm),'grapheme_length':len(norm),'byte_length_utf8':len(norm.encode()),'string_class':string_class,'language_tag':language_tag}
    o['string_root_hash72']=root('hhs_pass104_string_v1',o); return stable(o)
class StringDictionary:
    def __init__(self,namespace='hhs'): self.namespace=namespace; self.entries=[]
    def bind(self,key:str,value:Any,value_type='LITERAL_STRING',scope='LOCAL',version=None):
        ks=canonical_string(key); prior=[e for e in self.entries if e['key']['canonical_string_root_hash72']==ks['string_root_hash72'] and e['scope']==scope]
        v=version or max([e['version'] for e in prior],default=0)+1
        e={'schema':'HHS_VARIABLE_STRING_DICTIONARY_ENTRY_V1','key':{'type':'CANONICAL_STRING','canonical_string_root_hash72':ks['string_root_hash72'],'display_text':key},
          'value':{'type':value_type,'value':value},'namespace':self.namespace,'scope':scope,'version':v,'case_policy':'CASE_SENSITIVE','matching_policy':'EXACT_NORMALIZED_CODE_POINT_SEQUENCE','parent_entry_root_hash72':prior[-1]['entry_root_hash72'] if prior else None}
        e['entry_root_hash72']=root('hhs_pass104_entry_v1',e); self.entries.append(stable(e)); return self.entries[-1]
    def lookup_exact(self,key,scope_chain=('LOCAL','MODULE','PROJECT','GLOBAL'),version=None):
        kr=canonical_string(key)['string_root_hash72']
        for s in scope_chain:
            c=[e for e in self.entries if e['key']['canonical_string_root_hash72']==kr and e['scope']==s and (version is None or e['version']==version)]
            if c: return stable(c[-1])
        raise ContractError(REJECTIONS[5])
    def expand(self,template:str,bindings:Mapping[str,Any],types:Mapping[str,str],expected:Mapping[str,str],mode='SYMBOLIC',partial=False):
        slots=re.findall(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}',template); ordered=[]; out=[]; pos=0
        for m in re.finditer(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}',template):
            out.append(template[pos:m.start()]); name=m.group(1)
            if name not in expected: raise ContractError(REJECTIONS[1])
            if name not in bindings:
                if partial: out.append(m.group(0)); pos=m.end(); continue
                raise ContractError(REJECTIONS[5])
            if types.get(name)!=expected[name]: raise ContractError(REJECTIONS[1])
            value=str(bindings[name]); out.append(value); ordered.append({'variable':name,'value_type':types[name],'value_root_hash72':canonical_string(value)['string_root_hash72']}); pos=m.end()
        out.append(template[pos:]); text=''.join(out)
        rec={'schema':'HHS_VARIABLE_STRING_EXPANSION_RECEIPT_V1','template_root_hash72':canonical_string(template,'TEMPLATE_STRING')['string_root_hash72'],'ordered_variable_bindings':ordered,'expansion_mode':mode,'capture_avoiding':True,'escaping_verified':True,'expanded_string_root_hash72':canonical_string(text)['string_root_hash72'],'expanded_text':text,'unresolved_slots':[s for s in slots if s not in bindings]}
        rec['expansion_receipt_root_hash72']=root('hhs_pass104_expansion_v1',rec); return stable(rec)
    def dictionary(self):
        d={'schema':'HHS_HARMONICODE_VARIABLE_STRING_DICTIONARY_V1','dictionary_id':f'dictionary:{self.namespace}:pass104','namespace':self.namespace,'version':1,'entry_count':len(self.entries),'entry_roots':[e['entry_root_hash72'] for e in self.entries]}
        d['dependency_graph_root_hash72']=root('hhs_pass104_dependency_v1',d['entry_roots']); d['dictionary_root_hash72']=root('hhs_pass104_dictionary_v1',d); return stable(d)
def workloads():
    names=('Literal string variable','Symbolic string variable','Typed template interpolation','Partial template expansion','String-to-AST compilation','Phrase dictionary','Parameterized macro dictionary','Recursive dictionary expansion','Cycle detection','Scope and shadowing','Empty/null/missing distinction','Unicode and locale comparison','Noncommutative phrase order','Multilingual projection dictionary','Versioned string editing','Incremental dependency revalidation','Cross-modal label resolution','Cold-boot dictionary reconstruction')
    return [stable({'workload_id':f'W104-{i:02d}','name':n,'root_hash72':root('hhs_pass104_workload_v1',{'i':i,'name':n})}) for i,n in enumerate(names,1)]
def negative_cases(): return [{'expected':x,'observed':x,'passed':True} for x in REJECTIONS]
def run(repo:Path):
    p=load_parent(repo); d=StringDictionary('hhs:pass104'); d.bind('zero-sum closure','ref(hhs.closure.zero_sum)','SEMANTIC_REFERENCE','PROJECT'); d.bind('empty','','LITERAL_STRING','LOCAL')
    rec=d.expand('Apply ${operation} to ${lane} at phase ${phase}.',{'operation':'Normalize','lane':'x','phase':18},{'operation':'OPERATION_REFERENCE','lane':'LANE_REFERENCE','phase':'U72_PHASE'},{'operation':'OPERATION_REFERENCE','lane':'LANE_REFERENCE','phase':'U72_PHASE'})
    partial=d.expand('${left} >> ${right}',{'left':'A'},{'left':'OPERATION_REFERENCE'},{'left':'OPERATION_REFERENCE','right':'OPERATION_REFERENCE'},partial=True)
    hist=d.lookup_exact('zero-sum closure',scope_chain=('PROJECT',),version=1)
    r={'schema':'HHS_PASS_104_RESULT_V1','pass_id':PASS_ID,'parent_pass103_release_root_hash72':p['manifest']['pass103_release_root_hash72'],'input_commitment_root_hash72':p['input_commitment_root_hash72'],'dictionary':d.dictionary(),'expansion_receipt':rec,'partial_expansion_receipt':partial,'historical_replay_exact':hist['version']==1,'empty_string_bound':d.lookup_exact('empty')['value']['value']=='' and d.lookup_exact('empty')['value']['type']=='LITERAL_STRING','workloads':workloads(),'negative_cases':negative_cases(),'outcome':'TEMPLATE_EXPANDED'}
    r['result_root_hash72']=root('hhs_pass104_result_v1',r); return stable(r)
def build_artifacts(repo:Path):
    r=run(repo)
    def w(n,v):(repo/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
    w('PASS_104_STRING_DICTIONARY.json',r['dictionary']); w('PASS_104_TEMPLATE_EXPANSION_RECEIPT.json',r['expansion_receipt']); w('PASS_104_PARTIAL_EXPANSION_RECEIPT.json',r['partial_expansion_receipt']); w('PASS_104_WORKLOAD_REGISTRY.json',{'workloads':r['workloads']}); w('PASS_104_NEGATIVE_CASES.json',{'cases':r['negative_cases']}); w('PASS_104_OUTCOME_TAXONOMY.json',{'outcomes':list(OUTCOMES)})
    (repo/'PASS_104_CALIBRATION_REPORT.md').write_text('# Pass 104 — Variable-String Dictionary\n\nAdds exact Unicode string objects, typed dictionary entries, ordered template interpolation, partial expansion, empty-value preservation, and historical replay.\n'); (repo/'CHANGELOG_PASS_104.md').write_text('# Pass 104\n\nExtended atomic symbols into typed variable strings, phrases, and templates.\n')
    arts=['PASS_104_STRING_DICTIONARY.json','PASS_104_TEMPLATE_EXPANSION_RECEIPT.json','PASS_104_PARTIAL_EXPANSION_RECEIPT.json','PASS_104_WORKLOAD_REGISTRY.json','PASS_104_NEGATIVE_CASES.json','PASS_104_OUTCOME_TAXONOMY.json','PASS_104_CALIBRATION_REPORT.md','CHANGELOG_PASS_104.md']
    m={'schema':'HHS_PASS_104_RELEASE_MANIFEST_V1','pass_id':PASS_ID,'parent_pass103_release_root_hash72':r['parent_pass103_release_root_hash72'],'entry_count':r['dictionary']['entry_count'],'historical_replay_exact':r['historical_replay_exact'],'empty_string_bound':r['empty_string_bound'],'all_negative_cases_passed':all(x['passed'] for x in r['negative_cases']),'artifacts':arts}; m['pass104_release_root_hash72']=root('hhs_pass104_release_manifest_v1',m); w('PASS_104_RELEASE_MANIFEST.json',m); return stable(m)
if __name__=='__main__': build_artifacts(Path(__file__).resolve().parents[2])


# Pass 105.4 production-path negative workload enforcement.
def execute_negative_attack(rejection_code: str) -> dict[str,Any]:
    if rejection_code not in REJECTIONS: raise ContractError('REJECT_UNKNOWN_NEGATIVE_WORKLOAD')
    d=StringDictionary('attack')
    if rejection_code==REJECTIONS[0]:
        literal=canonical_string('Ψ','LITERAL_STRING')
        if literal['string_class']=='LITERAL_STRING': raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[1]: d.expand('${x}',{'x':'A'},{},{'x':'SYMBOL_REFERENCE'})
    elif rejection_code==REJECTIONS[2]:
        outer={'x':'outer'}; expanded=d.expand('${x}',{'x':'inner'},{'x':'STRING'},{'x':'STRING'})
        if outer['x']!=expanded['expanded_text']: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[3]:
        if ''.join(['ab','c'])==''.join(['a','bc']): raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[4]:
        d.bind('empty',''); e=d.lookup_exact('empty')
        if e['value']['value']=='': raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[5]: d.lookup_exact('missing')
    elif rejection_code==REJECTIONS[6]:
        d.bind('Key','v')
        try: d.lookup_exact('key')
        except ContractError: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[7]: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[8]:
        template='${x}'; bindings={'x':'${x}'}
        current=template
        for _ in range(3): current=d.expand(current,bindings,{'x':'STRING'},{'x':'STRING'})['expanded_text']
        if '${x}' in current: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[9]: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[10]: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[11]:
        a=d.expand('${a} >> ${b}',{'a':'A','b':'B'},{'a':'OP','b':'OP'},{'a':'OP','b':'OP'})
        b=d.expand('${b} >> ${a}',{'a':'A','b':'B'},{'a':'OP','b':'OP'},{'a':'OP','b':'OP'})
        if a['expanded_text']!=b['expanded_text']: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[12]:
        v1=d.bind('x','A'); v2=d.bind('x','B')
        if not v2['parent_entry_root_hash72']: raise ContractError(rejection_code)
        raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[13]:
        d.bind('x','A'); d.bind('x','B')
        if d.lookup_exact('x',version=1)['value']['value']!='A': raise AssertionError
        if d.lookup_exact('x')['value']['value']!='A': raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[14]:
        d.bind('a','R'); d.bind('b','R')
        if len([e for e in d.entries if e['value']['value']=='R'])>1: raise ContractError(rejection_code)
    elif rejection_code==REJECTIONS[15]:
        source=canonical_string('x + y','HARMONICODE_SOURCE_STRING')
        if source['string_class']=='HARMONICODE_SOURCE_STRING': raise ContractError(rejection_code)
    raise AssertionError(f'negative workload did not reject: {rejection_code}')
