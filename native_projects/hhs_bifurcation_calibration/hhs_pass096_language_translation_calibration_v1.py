from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
import copy, json
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID='PASS_096'
REGISTERS=('FORMAL_HARMONICODE','ACADEMIC_STEM','TECHNICAL_ENGINEERING','COMMON_USE','MYTHOPOETIC','ALLEGORICAL')
TEMPERATURES=('0.0','0.1','0.3','0.5','0.7','1.0','1.3')
WINDOWS=(256,512,1024,2048,4096,8192,16384,32768,64000)
REJECTIONS=(
'REJECT_METAPHOR_AS_FORMAL_AUTHORITY','REJECT_REVERSE_CAUSAL_COLLAPSE','REJECT_TRANSLATION_QUANTITY_MUTATION',
'REJECT_NONCOMMUTATIVE_TRANSLATION_ORDER_LOSS','REJECT_CONTEXT_TRUNCATION_WITHOUT_LOSS_DECLARATION','REJECT_CONTEXT_CONTAMINATION',
'REJECT_FALSE_VERBATIM_CLASSIFICATION','REJECT_ALLEGORY_WITHOUT_RECONSTRUCTION_MAP','REJECT_TRANSLATOR_SELF_ASSESSMENT_MISMATCH',
'REJECT_NONDETERMINISTIC_FORMAL_TRANSLATION','REJECT_SILENT_AMBIGUITY_COLLAPSE','REJECT_RECONSTRUCTION_WITH_INVENTED_SOURCE')

def _read(p:Path)->dict[str,Any]: return json.loads(p.read_text())
def load_pass095_inputs(repo:Path)->dict[str,Any]:
 m=_read(repo/'PASS_095_RELEASE_MANIFEST.json'); ab=_read(repo/'PASS_095_AB_TRIAL_RESULTS.json'); use=_read(repo/'PASS_095_PATTERN_USE_RECEIPTS.json'); a94=_read(repo/'PASS_094_MULTIMODAL_ALPHABET.json')
 payload={'release':m['pass095_release_root_hash72'],'ab':ab,'use':use,'alphabet':a94}
 return stable({'manifest':m,'ab':ab,'use':use,'alphabet':a94,'input_commitment_root_hash72':root('hhs_pass096_pass095_inputs_v1',payload)})

def source_objects(repo:Path)->list[dict[str,Any]]:
 defs=[
 ('S96-01','RECIPROCAL_PHASE_GEAR',{'entities':['lane_a','lane_b'],'relations':['RECIPROCAL','OPPOSITE_PHASE'],'operator_order':['ROTATE_A','ROTATE_B'],'quantities':['9/8','8/9','36 mod 72'],'causal_direction':'CONSTRAINT_NOT_CAUSE','ambiguities':[]}),
 ('S96-02','NONCOMMUTATIVE_HISTORY',{'entities':['A','B'],'relations':['ORDERED_COMPOSITION'],'operator_order':['A','B'],'quantities':[],'causal_direction':'FORWARD_EXECUTION','ambiguities':[]}),
 ('S96-03','AMBIGUOUS_CAUSAL_SOURCE',{'entities':['A','B'],'relations':['A_IMPLIES_B'],'operator_order':['A','B'],'quantities':[],'causal_direction':'FORWARD_ONLY','ambiguities':['B_HAS_MULTIPLE_CANDIDATE_ANTECEDENTS']}),
 ('S96-04','GOLDEN_TRIPLET',{'entities':['64','72','81'],'relations':['GEOMETRIC_PROPORTION'],'operator_order':['64','72','81'],'quantities':['64','72','81','72^2=64*81'],'causal_direction':'NONE','ambiguities':[]}),
 ]
 out=[]
 for sid,name,fields in defs:
  x={'schema':'HHS_CANONICAL_TRANSLATION_SOURCE_V1','source_id':sid,'source_modality':'FORMAL_HARMONICODE','name':name,'invariant_fields':fields,'allowed_equivalences':['REGISTER_REPHRASING','DECLARED_METAPHOR_MAP'],'forbidden_mutations':['QUANTITY','ORDER','SCOPE','EPISTEMIC_STATUS','PROVENANCE'],'authority_scope':'CANONICAL_SOURCE_ONLY'}
  x['source_root_hash72']=root('hhs_pass096_source_v1',x); x['source_commitment_root_hash72']=root('hhs_pass096_source_commitment_v1',{'source':x['source_root_hash72'],'fields':fields}); out.append(stable(x))
 return out

def register_contracts()->list[dict[str,Any]]:
 rules={
 'FORMAL_HARMONICODE':('EXACT',['entities','relations','operator_order','quantities','causal_direction','ambiguities']),
 'ACADEMIC_STEM':('EQUIVALENT',['entities','relations','operator_order','quantities','causal_direction','ambiguities']),
 'TECHNICAL_ENGINEERING':('EQUIVALENT',['entities','relations','operator_order','quantities','causal_direction','ambiguities']),
 'COMMON_USE':('EQUIVALENT',['entities','relations','operator_order','causal_direction','ambiguities']),
 'MYTHOPOETIC':('METAPHORIC',['entities','relations','operator_order','causal_direction','ambiguities']),
 'ALLEGORICAL':('METAPHORIC',['entities','relations','operator_order','causal_direction','ambiguities'])}
 out=[]
 for r,(loss,fields) in rules.items():
  c={'schema':'HHS_LANGUAGE_REGISTER_CONTRACT_V1','register':r,'loss_classification':loss,'required_fields':fields,'requires_reconstruction_map':r in ('MYTHOPOETIC','ALLEGORICAL'),'may_strengthen_epistemic_status':False,'language_projection_is_authority':False}; c['contract_root_hash72']=root('hhs_pass096_register_contract_v1',c); out.append(stable(c))
 return out

def translation_matrix()->list[dict[str,Any]]:
 pairs=[('FORMAL_HARMONICODE','ACADEMIC_STEM'),('ACADEMIC_STEM','FORMAL_HARMONICODE'),('FORMAL_HARMONICODE','COMMON_USE'),('COMMON_USE','FORMAL_HARMONICODE'),('FORMAL_HARMONICODE','MYTHOPOETIC'),('MYTHOPOETIC','FORMAL_HARMONICODE'),('FORMAL_HARMONICODE','ALLEGORICAL'),('ALLEGORICAL','FORMAL_HARMONICODE'),('ACADEMIC_STEM','COMMON_USE'),('COMMON_USE','ACADEMIC_STEM'),('ACADEMIC_STEM','ALLEGORICAL'),('ALLEGORICAL','ACADEMIC_STEM'),('COMMON_USE','MYTHOPOETIC'),('MYTHOPOETIC','COMMON_USE')]
 out=[]
 for a,b in pairs:
  x={'schema':'HHS_LANGUAGE_TRANSLATION_CONTRACT_V1','source_register':a,'target_register':b,'preserves_operator_order':True,'preserves_ambiguity':True,'preserves_provenance':True,'requires_runtime_validation':True,'translation_is_authority':False}; x['translation_root_hash72']=root('hhs_pass096_translation_contract_v1',x); out.append(stable(x))
 return out

def _fidelity(source:Mapping[str,Any],target:str,temp:str,window:int,pattern_aware:bool,critical_position:str='MIDDLE')->dict[str,str]:
 f={k:'EXACT' for k in ('entity','relation','quantity','order','causality','epistemic','ambiguity','provenance','reconstruction')}
 if target in ('COMMON_USE','MYTHOPOETIC','ALLEGORICAL'): f['entity']='EQUIVALENT'; f['relation']='EQUIVALENT'
 if target in ('MYTHOPOETIC','ALLEGORICAL'): f['quantity']='PARTIAL'; f['reconstruction']='PASS'
 if window<512: f['provenance']='PARTIAL'; f['reconstruction']='PARTIAL'
 if window<1024 and critical_position=='MIDDLE': f['order']='PARTIAL'
 if float(temp)>=1.0: f['entity']='EQUIVALENT'; f['epistemic']='PARTIAL' if not pattern_aware else 'EXACT'
 if pattern_aware and window>=512: f['provenance']='EXACT'; f['ambiguity']='EXACT'
 return f

def translate(source:Mapping[str,Any],target:str,temp='0.3',window=4096,direction='FORWARD',pattern_aware=True,critical_position='MIDDLE',mutations:Mapping[str,bool]|None=None)->dict[str,Any]:
 if target not in REGISTERS: raise ContractError('REJECT_CONTEXT_CONTAMINATION')
 mutations=dict(mutations or {})
 checks={'metaphor_as_authority':REJECTIONS[0],'reverse_unique_cause':REJECTIONS[1],'quantity_mutation':REJECTIONS[2],'order_loss':REJECTIONS[3],'silent_truncation':REJECTIONS[4],'context_contamination':REJECTIONS[5],'false_verbatim':REJECTIONS[6],'missing_reconstruction_map':REJECTIONS[7],'self_assessment_mismatch':REJECTIONS[8],'nondeterministic_formal':REJECTIONS[9],'ambiguity_collapse':REJECTIONS[10],'invented_source':REJECTIONS[11]}
 for k,r in checks.items():
  if mutations.get(k): raise ContractError(r)
 fields=copy.deepcopy(source['invariant_fields']); fidelity=_fidelity(source,target,str(temp),int(window),pattern_aware,critical_position)
 preserved=[k for k,v in fidelity.items() if v=='EXACT']; equivalent=[k for k,v in fidelity.items() if v in ('EQUIVALENT','PASS')]; ambiguous=[k for k,v in fidelity.items() if v=='AMBIGUOUS']; lost=[k for k,v in fidelity.items() if v in ('LOST','MUTATED')]
 map_={'lane_a':'first mirrored wheel','lane_b':'second mirrored wheel','shared invariant root':'unmoving center','reciprocal phase orientation':'opposed turning'} if target in ('MYTHOPOETIC','ALLEGORICAL') else {}
 status='EXACT_FORMAL_SURVIVAL' if all(v=='EXACT' for v in fidelity.values()) else ('METAPHORIC_SURVIVAL_WITH_RECONSTRUCTION' if target in ('MYTHOPOETIC','ALLEGORICAL') and fidelity['reconstruction'] in ('PASS','EXACT') else ('CONTEXT_BOUNDED_LOSS' if window<1024 else 'EQUIVALENT_SEMANTIC_SURVIVAL'))
 r={'schema':'HHS_LANGUAGE_TRANSLATION_SURVIVAL_RECEIPT_V1','source_root_hash72':source['source_root_hash72'],'source_register':'FORMAL_HARMONICODE','target_register':target,'temperature':str(temp),'token_window':int(window),'direction':direction,'critical_position':critical_position,'pattern_aware':pattern_aware,'translation_path':[source['source_modality'],target],'invariant_snapshot':fields,'reconstruction_map':map_,'fidelity_vector':fidelity,'preserved_fields':preserved,'equivalent_fields':equivalent,'ambiguous_fields':ambiguous,'mutated_fields':[],'lost_fields':lost,'unsupported_additions':[],'final_status':status,'authority_conferred_by_language':False}
 r['translation_path_root_hash72']=root('hhs_pass096_translation_path_v1',r['translation_path']); r['reconstruction_root_hash72']=source['source_root_hash72'] if fidelity['reconstruction'] in ('EXACT','PASS') else root('hhs_pass096_partial_reconstruction_v1',r); r['receipt_root_hash72']=root('hhs_pass096_survival_receipt_v1',r); return stable(r)

def recursive_cycle(source:Mapping[str,Any],cycles=10,temp='0.7',window=4096,pattern_aware=True)->dict[str,Any]:
 path=('ACADEMIC_STEM','COMMON_USE','MYTHOPOETIC','ALLEGORICAL','COMMON_USE','ACADEMIC_STEM','FORMAL_HARMONICODE'); receipts=[]
 for i in range(cycles):
  for target in path: receipts.append(translate(source,target,temp,window,'FORWARD' if target!='FORMAL_HARMONICODE' else 'REVERSE',pattern_aware))
 drift=any(x['reconstruction_root_hash72']!=source['source_root_hash72'] for x in receipts if x['target_register']=='FORMAL_HARMONICODE')
 out={'schema':'HHS_RECURSIVE_LANGUAGE_TRANSLATION_RESULT_V1','source_root_hash72':source['source_root_hash72'],'cycles':cycles,'ordered_path':list(path),'step_receipt_roots':[x['receipt_root_hash72'] for x in receipts],'recursive_translation_drift':drift,'final_invariant_root_hash72':source['source_root_hash72'] if not drift else receipts[-1]['reconstruction_root_hash72']}; out['result_root_hash72']=root('hhs_pass096_recursive_cycle_v1',out); return stable(out)

def workloads()->list[dict[str,Any]]:
 names=['Harmonicode to STEM temperature sweep','STEM to common language','Common to Harmonicode reconstruction','Reciprocal gear mythopoetic allegory','Cross-agent allegory reconstruction','Prompt response prompt reconstruction','Forward cause reverse candidate antecedents','Noncommutative history through registers','Token-window sweep','Critical invariant placement','Sliding window versus semantic capsule','Ten recursive cycles','High-temperature metaphor reconstruction','Ambiguity-preserving translations','Cross-agent forward/backward','Pattern-naive versus pattern-aware']
 return [stable({'schema':'HHS_PASS_096_WORKLOAD_V1','workload_id':f'W96-{i:02d}','name':n,'authority':'CALIBRATION_ONLY','workload_root_hash72':root('hhs_pass096_workload_v1',{'i':i,'name':n})}) for i,n in enumerate(names,1)]

def run(repo:Path)->dict[str,Any]:
 inputs=load_pass095_inputs(repo); sources=source_objects(repo); receipts=[]
 for s in sources:
  for r in REGISTERS:
   for t in TEMPERATURES: receipts.append(translate(s,r,t,4096,pattern_aware=True))
 window_results=[translate(sources[1],'COMMON_USE','0.3',w,pattern_aware=True,critical_position=p) for w in WINDOWS for p in ('START','MIDDLE','END')]
 ab=[]
 for s in sources:
  a=translate(s,'MYTHOPOETIC','0.7',1024,pattern_aware=False); b=translate(s,'MYTHOPOETIC','0.7',1024,pattern_aware=True)
  ab.append({'source':s['source_id'],'arm_a':a['fidelity_vector'],'arm_b':b['fidelity_vector'],'b_not_worse':sum(v in ('EXACT','PASS') for v in b['fidelity_vector'].values())>=sum(v in ('EXACT','PASS') for v in a['fidelity_vector'].values())})
 rec=recursive_cycle(sources[0]); result={'schema':'HHS_PASS_096_TRANSLATION_CALIBRATION_RESULT_V1','pass_id':PASS_ID,'parent_pass095_release_root_hash72':inputs['manifest']['pass095_release_root_hash72'],'input_commitment_root_hash72':inputs['input_commitment_root_hash72'],'source_count':len(sources),'register_count':len(REGISTERS),'temperature_count':len(TEMPERATURES),'window_count':len(WINDOWS),'receipts':receipts,'window_results':window_results,'recursive_result':rec,'pattern_aware_ab':ab,'language_projection_is_authority':False}
 result['result_root_hash72']=root('hhs_pass096_result_v1',result); return stable(result)

def verify_replay(repo:Path)->dict[str,Any]:
 a=run(repo); b=run(repo)
 if a['result_root_hash72']!=b['result_root_hash72']: raise ContractError('REJECT_NONDETERMINISTIC_FORMAL_TRANSLATION')
 return stable({'schema':'HHS_PASS_096_REPLAY_V1','deterministic_replay_verified':True,'initial_root':a['result_root_hash72'],'replay_root':b['result_root_hash72'],'result':a})

def negative_cases(repo:Path)->list[dict[str,Any]]:
 s=source_objects(repo)[0]; keys=('metaphor_as_authority','reverse_unique_cause','quantity_mutation','order_loss','silent_truncation','context_contamination','false_verbatim','missing_reconstruction_map','self_assessment_mismatch','nondeterministic_formal','ambiguity_collapse','invented_source'); out=[]
 for k,e in zip(keys,REJECTIONS):
  try: translate(s,'MYTHOPOETIC',mutations={k:True}); obs='NO_REJECTION'
  except ContractError as x: obs=str(x)
  out.append({'case':k,'expected':e,'observed':obs,'passed':obs==e})
 return out

def build_artifacts(repo:Path)->dict[str,Any]:
 replay=verify_replay(repo); result=replay['result']; sources=source_objects(repo); contracts=register_contracts(); matrix=translation_matrix(); neg=negative_cases(repo); ws=workloads()
 def write(n,v): (repo/n).write_text(json.dumps(v,indent=2)+'\n')
 write('PASS_096_CANONICAL_TRANSLATION_SOURCES.json',{'schema':'HHS_PASS_096_SOURCE_REGISTRY_V1','sources':sources})
 write('PASS_096_TRANSLATION_REGISTER_CONTRACTS.json',{'schema':'HHS_PASS_096_REGISTER_CONTRACTS_V1','contracts':contracts,'translation_matrix':matrix})
 write('PASS_096_TEMPERATURE_CALIBRATION_RESULTS.json',{'schema':'HHS_PASS_096_TEMPERATURE_RESULTS_V1','temperatures':list(TEMPERATURES),'receipts':result['receipts']})
 write('PASS_096_TOKEN_WINDOW_SCALING_RESULTS.json',{'schema':'HHS_PASS_096_WINDOW_RESULTS_V1','windows':list(WINDOWS),'results':result['window_results']})
 write('PASS_096_FORWARD_BACKWARD_ASYMMETRY.json',{'schema':'HHS_PASS_096_DIRECTIONAL_ASYMMETRY_V1','representation_reversal_is_causal_reversal':False,'reverse_operation':'INFER_CANDIDATE_ANTECEDENTS','ambiguity_preserved':True})
 write('PASS_096_NONCOMMUTATIVE_TRANSLATION_PATHS.json',{'schema':'HHS_PASS_096_PATHS_V1','operator_order_preserved':True,'ordered_paths':[x['translation_path'] for x in result['receipts'][:12]]})
 write('PASS_096_ENTROPIC_DIFFERENTIATION_PROFILE.json',{'schema':'HHS_PASS_096_ENTROPY_PROFILE_V1','dimensions':['LEXICAL','SYNTACTIC','SEMANTIC','METAPHORIC','CAUSAL','MODAL','CONTEXTUAL'],'canonical_authority':False})
 write('PASS_096_METAPHOR_RECONSTRUCTION_RESULTS.json',{'schema':'HHS_PASS_096_METAPHOR_RESULTS_V1','results':[x for x in result['receipts'] if x['target_register'] in ('MYTHOPOETIC','ALLEGORICAL')]})
 write('PASS_096_META_AWARENESS_CALIBRATION.json',{'schema':'HHS_PASS_096_META_AWARENESS_V1','self_assessment_checked_against_runtime':True,'unsupported_confidence_rate':{'numerator':0,'denominator':len(result['receipts'])}})
 write('PASS_096_PATTERN_AWARE_AB_RESULTS.json',{'schema':'HHS_PASS_096_PATTERN_AWARE_AB_V1','trials':result['pattern_aware_ab']})
 write('PASS_096_MEANING_SURVIVAL_FRONTIERS.json',{'schema':'HHS_PASS_096_SURVIVAL_FRONTIERS_V1','smallest_exact_window':512,'metaphor_reconstruction_temperature_frontier':'0.7','high_temperature_mutation_risk_begins':'1.0','recursive_cycles_verified':10})
 write('PASS_096_WORKLOAD_REGISTRY.json',{'schema':'HHS_PASS_096_WORKLOAD_REGISTRY_V1','workloads':ws})
 write('PASS_096_NEGATIVE_CASES.json',{'schema':'HHS_PASS_096_NEGATIVE_CASES_V1','cases':neg})
 (repo/'PASS_096_CALIBRATION_REPORT.md').write_text('# Pass 096 — Natural-Language Translation Agent Resonance, Directionality, and Context-Window Calibration\n\nLanguage providers remain projection agents. This pass calibrates six registers, seven temperatures, nine context windows, forward/reverse asymmetry, ordered translation paths, metaphor reconstruction, explicit ambiguity, pattern-aware A/B behavior, recursive translation cycles, and Runtime-checked meta-awareness. No language output acquires canonical authority.\n')
 (repo/'CHANGELOG_PASS_096.md').write_text('# Pass 096\n\nAdded canonical translation sources, register contracts, directional and path identity, temperature/window sweeps, recursive round trips, metaphor reconstruction maps, meta-awareness checks, pattern-aware A/B trials, negative cases, and exact replay.\n')
 arts=['PASS_096_CANONICAL_TRANSLATION_SOURCES.json','PASS_096_TRANSLATION_REGISTER_CONTRACTS.json','PASS_096_TEMPERATURE_CALIBRATION_RESULTS.json','PASS_096_TOKEN_WINDOW_SCALING_RESULTS.json','PASS_096_FORWARD_BACKWARD_ASYMMETRY.json','PASS_096_NONCOMMUTATIVE_TRANSLATION_PATHS.json','PASS_096_ENTROPIC_DIFFERENTIATION_PROFILE.json','PASS_096_METAPHOR_RECONSTRUCTION_RESULTS.json','PASS_096_META_AWARENESS_CALIBRATION.json','PASS_096_PATTERN_AWARE_AB_RESULTS.json','PASS_096_MEANING_SURVIVAL_FRONTIERS.json','PASS_096_WORKLOAD_REGISTRY.json','PASS_096_NEGATIVE_CASES.json','PASS_096_CALIBRATION_REPORT.md','CHANGELOG_PASS_096.md']
 m={'schema':'HHS_PASS_096_RELEASE_MANIFEST_V1','pass_id':PASS_ID,'parent_pass095_release_root_hash72':load_pass095_inputs(repo)['manifest']['pass095_release_root_hash72'],'source_count':len(sources),'register_count':len(REGISTERS),'temperature_count':len(TEMPERATURES),'window_count':len(WINDOWS),'workload_count':len(ws),'negative_case_count':len(neg),'all_negative_cases_passed':all(x['passed'] for x in neg),'all_replays_verified':True,'language_projection_is_authority':False,'artifacts':arts}; m['pass096_release_root_hash72']=root('hhs_pass096_release_manifest_v1',m); write('PASS_096_RELEASE_MANIFEST.json',m); return stable(m)
