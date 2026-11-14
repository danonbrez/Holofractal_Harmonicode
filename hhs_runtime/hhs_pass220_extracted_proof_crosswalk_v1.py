"""Source-bound lemma/course crosswalk against inherited proof and Lane 5 registries.

This is discovery evidence, not a theorem-prover, and never self-certifies
absence. Match registered lemma IDs within their own source identity; match
constructor names only as candidates. Preserve collisions and all refs.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Mapping

EXTRACTION_SCHEMA="HHS_PASS220_SOURCE_BOUND_PROOF_EXTRACTION_V1"
SCHEMA="HHS_PASS220_EXTRACTED_PROOF_CROSSWALK_V1"

class ProofCrosswalkError(ValueError):
    pass

def _str(value: Any) -> bool:
    return isinstance(value,str) and bool(value.strip())

def crosswalk(extraction: Mapping[str,Any], *,
              lemma_registry: Mapping[str,Any],
              lane5_projection: Mapping[str,Any]) -> dict[str,Any]:
    if extraction.get("schema")!=EXTRACTION_SCHEMA or not isinstance(extraction.get("extracted_sources"),list):
        raise ProofCrosswalkError("EXTRACTION_SCHEMA_INVALID")
    lemmas=lemma_registry.get("lemmas")
    if not isinstance(lemmas,list) or any(not isinstance(x,Mapping) or not _str(x.get("id")) or not _str(x.get("statement")) for x in lemmas):
        raise ProofCrosswalkError("LEMMA_REGISTRY_INVALID")
    lemma_ids={}
    for lemma in lemmas:
        if lemma["id"] in lemma_ids:
            raise ProofCrosswalkError("LEMMA_REGISTRY_DUPLICATE_ID")
        lemma_ids[lemma["id"]]=lemma
    nodes=lane5_projection.get("constructors")
    if not isinstance(nodes,list):
        raise ProofCrosswalkError("LANE5_CONSTRUCTOR_GRAPH_INVALID")
    by_name={}
    for node in nodes:
        if not isinstance(node,Mapping) or not _str(node.get("node_id")) or not _str(node.get("name")) or not _str(node.get("source_path")) or not _str(node.get("hash216")) or len(node["hash216"])!=216:
            raise ProofCrosswalkError("LANE5_CONSTRUCTOR_NODE_INVALID")
        by_name.setdefault(node["name"],[]).append(node)
    source_records=[]
    by_lemma={}
    course={}
    for source in extraction["extracted_sources"]:
        if not isinstance(source,Mapping) or not all(_str(source.get(k)) for k in ("repository","path","git_blob","commit","ref")) or not isinstance(source.get("objects"),list):
            raise ProofCrosswalkError("EXTRACTED_SOURCE_IDENTITY_INVALID")
        for obj in source["objects"]:
            if not isinstance(obj,Mapping) or not _str(obj.get("kind")):
                raise ProofCrosswalkError("EXTRACTED_PROOF_OBJECT_INVALID")
            witness={k:source[k] for k in ("repository","path","git_blob","commit","ref")}
            witness["kind"]=obj["kind"]
            witness["identifier"]=obj.get("identifier")
            witness["source_locator"]=obj.get("source_locator")
            witness["proof_executed_by_crosswalk"]=False
            if obj["kind"]=="REGISTERED_LEMMA":
                key=obj.get("identifier")
                original=lemma_ids.get(key) if _str(key) else None
                if original is not None:
                    witness["registry_relation"]=(
                        "EXACT_RECORDED_STATEMENT_MATCH" if obj.get("exact_expression")==original["statement"]
                        and obj.get("assumptions")==original.get("assumptions")
                        and obj.get("dependencies")==original.get("dependencies")
                        else "REGISTERED_ID_SOURCE_DIVERGENCE"
                    )
                    witness["registry_id"]=key
                    witness["registry_declared_status"]=original.get("status")
                    witness["declared_status_match"]=obj.get("declared_status")==original.get("status")
                else:
                    witness["registry_relation"]="REGISTRY_ID_NOT_LOCATED"
                if _str(key):
                    by_lemma.setdefault(key,[]).append({"git_blob":source["git_blob"],"statement":obj.get("exact_expression"),
                        "assumptions":obj.get("assumptions"),"dependencies":obj.get("dependencies"),
                        "declared_status":obj.get("declared_status"),"source":source["path"],"ref":source["ref"]})
            elif obj["kind"]=="COURSE_MODULE":
                num=obj.get("identifier")
                if type(num) is not int or num<0:
                    raise ProofCrosswalkError("COURSE_MODULE_ID_INVALID")
                course.setdefault(num,[]).append({"git_blob":source["git_blob"],"path":source["path"],"ref":source["ref"],
                                                    "equation_candidates":obj.get("equation_candidates",[])})
                witness["registry_relation"]="COURSE_SOURCE_ONLY"
            else:
                witness["registry_relation"]="DECLARATION_CANDIDATE_ONLY"
            name=obj.get("identifier")
            candidates=by_name.get(name,[]) if isinstance(name,str) else []
            witness["lane5_constructor_candidates"]=[
                {"node_id":n["node_id"],"hash216":n["hash216"],"source_path":n["source_path"],
                 "same_path":n["source_path"]==source["path"]}
                for n in candidates
            ]
            witness["native_constructor_equivalence_verified"]=False
            source_records.append(witness)
    lemma_conflicts=[]
    for lemma_id,variants in sorted(by_lemma.items()):
        distinct={(v["statement"],json.dumps(v["assumptions"],sort_keys=True),
                   json.dumps(v["dependencies"],sort_keys=True)) for v in variants}
        if len(distinct)>1:
            lemma_conflicts.append({"lemma_id":lemma_id,"variant_count":len(distinct),
                                    "source_occurrences":variants})
    course_variants=[]
    for number,variants in sorted(course.items()):
        identity={(json.dumps(v["equation_candidates"],sort_keys=True)) for v in variants}
        if len(identity)>1:
            course_variants.append({"module":number,"distinct_equation_candidate_lists":len(identity),
                                    "source_occurrences":variants})
    return {"schema":SCHEMA,"source_records":source_records,
            "registered_lemma_count":len(lemmas),"indexed_constructor_count":len(nodes),
            "extracted_record_count":len(source_records),
            "lemma_source_conflicts":lemma_conflicts,"course_source_variants":course_variants,
            "skipped_blobs":extraction.get("skipped_blobs",[]),
            "source_tree_report_truncated":extraction.get("source_tree_report_truncated",True),
            "source_tree_errors":extraction.get("source_tree_errors",[]),
            "proof_equivalence_verified":False,"native_proof_executed":False,
            "negative_existence_claim_authorized":False,
            "vm81_mutation_authority":False,"canonical_hash216_minted":False}

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--extraction",required=True)
    parser.add_argument("--lemma-registry",default="formal/lemmas/pass_144/LEMMA_CORPUS.json")
    parser.add_argument("--lane5",default="artifacts/repository_index/LANE5_HASH216_HYDRATION_KNOWLEDGE_GRAPH.json")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    extraction=json.loads(Path(args.extraction).read_text("utf-8"))
    lemmas=json.loads(Path(args.lemma_registry).read_text("utf-8"))
    lane=json.loads(Path(args.lane5).read_text("utf-8"))
    result=crosswalk(extraction,lemma_registry=lemmas,lane5_projection=lane)
    Path(args.output).write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n","utf-8")
    print("Crosswalk source records:",result["extracted_record_count"])
    print("Lemma ID conflicts:",len(result["lemma_source_conflicts"]))
    print("Module equation-source variants:",len(result["course_source_variants"]))
