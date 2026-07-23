from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from collections import deque

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import _canon

PASS_ID = "PASS_128"
NODE_SCHEMA = "HHS_CANONICAL_KNOWLEDGE_NODE_V1"
EDGE_SCHEMA = "HHS_CANONICAL_KNOWLEDGE_EDGE_V1"
GRAPH_SCHEMA = "HHS_CANONICAL_KNOWLEDGE_GRAPH_V1"
QUERY_SCHEMA = "HHS_KNOWLEDGE_GRAPH_QUERY_V1"
RESULT_SCHEMA = "HHS_KNOWLEDGE_GRAPH_RETRIEVAL_RESULT_V1"
REPLAY_SCHEMA = "HHS_KNOWLEDGE_GRAPH_RETRIEVAL_REPLAY_V1"

REJECTION_CODES = {
    "REJECT_INVALID_KNOWLEDGE_RECORD", "REJECT_NODE_ROOT_MISMATCH", "REJECT_EDGE_ROOT_MISMATCH",
    "REJECT_GRAPH_ROOT_MISMATCH", "REJECT_QUERY_ROOT_MISMATCH", "REJECT_RESULT_ROOT_MISMATCH",
    "REJECT_UNBOUNDED_GRAPH", "REJECT_DUPLICATE_NODE", "REJECT_UNKNOWN_ENDPOINT",
    "REJECT_UNSUPPORTED_RELATION", "REJECT_MISSING_RELATION_EVIDENCE", "REJECT_SELF_CONTRADICTION_EDGE",
    "REJECT_QUERY_EMPTY", "REJECT_QUERY_NO_MATCH", "REJECT_UNGROUNDED_RESULT",
    "REJECT_AUTHORITY_ESCALATION", "REJECT_EXECUTABLE_RETRIEVAL_ESCALATION", "REJECT_REPLAY_MISMATCH",
}

class Pass128Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")

@dataclass(frozen=True)
class KnowledgeGraphBounds:
    max_nodes: int = 32768
    max_edges: int = 131072
    max_query_chars: int = 4096
    max_results: int = 128
    max_hops: int = 8
    max_path_expansions: int = 65536

class CanonicalKnowledgeGraphEngine:
    """Builds and queries an evidence-grounded, immutable, non-executable knowledge graph."""
    RELATIONS = {
        "SUPPORTS", "CONTRADICTS", "REFINES", "DEPENDS_ON", "EQUIVALENT_TO",
        "PART_OF", "CAUSES", "PRECEDES", "DEFINES", "INSTANCE_OF",
    }

    def __init__(self, bounds: KnowledgeGraphBounds | None = None):
        self.bounds = bounds or KnowledgeGraphBounds()
        if min(vars(self.bounds).values()) <= 0:
            raise Pass128Error("REJECT_UNBOUNDED_GRAPH", "positive bounds required")

    @staticmethod
    def _tokens(text: str) -> tuple[str, ...]:
        cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return tuple(sorted(set(part for part in cleaned.split() if part)))

    def node_from_record(self, record: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(record)
        claimed = obj.pop("knowledge_record_root_hash72", None)
        if obj.get("schema") != "HHS_ADMITTED_KNOWLEDGE_RECORD_V1":
            raise Pass128Error("REJECT_INVALID_KNOWLEDGE_RECORD", str(obj.get("schema")))
        if claimed != _hash("hhs_pass127_record_v1", obj):
            raise Pass128Error("REJECT_INVALID_KNOWLEDGE_RECORD", str(claimed))
        if obj.get("knowledge_authority") is not True or obj.get("execution_authority") is not False or obj.get("mutation_authority") is not False or obj.get("executable") is not False:
            raise Pass128Error("REJECT_AUTHORITY_ESCALATION", "record authority boundary")
        proposition = obj["normalized_proposition"]
        node = {
            "schema": NODE_SCHEMA, "pass_id": PASS_ID,
            "knowledge_record_root_hash72": claimed,
            "normalized_proposition": proposition,
            "semantic_tokens": list(self._tokens(proposition)),
            "decision_root_hash72": obj["decision_root_hash72"],
            "support_evidence_roots": list(obj["support_evidence_roots"]),
            "knowledge_status": obj["knowledge_status"],
            "knowledge_authority": True,
            "execution_authority": False, "mutation_authority": False, "executable": False,
        }
        node["knowledge_node_root_hash72"] = _hash("hhs_pass128_node_v1", node)
        return node

    def verify_node(self, node: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(node); claimed = obj.pop("knowledge_node_root_hash72", None)
        if obj.get("schema") != NODE_SCHEMA or claimed != _hash("hhs_pass128_node_v1", obj):
            raise Pass128Error("REJECT_NODE_ROOT_MISMATCH", str(claimed))
        if obj.get("execution_authority") is not False or obj.get("mutation_authority") is not False or obj.get("executable") is not False:
            raise Pass128Error("REJECT_AUTHORITY_ESCALATION", "node")
        obj["knowledge_node_root_hash72"] = claimed
        return obj

    def relate(self, source_node: Mapping[str, Any], target_node: Mapping[str, Any], *, relation_type: str,
               evidence_roots: Sequence[str], directed: bool = True, confidence_numerator: int = 1,
               confidence_denominator: int = 1) -> dict[str, Any]:
        source = self.verify_node(source_node); target = self.verify_node(target_node)
        if relation_type not in self.RELATIONS:
            raise Pass128Error("REJECT_UNSUPPORTED_RELATION", relation_type)
        if not evidence_roots or any(not root for root in evidence_roots):
            raise Pass128Error("REJECT_MISSING_RELATION_EVIDENCE", relation_type)
        if confidence_denominator <= 0 or confidence_numerator < 0 or confidence_numerator > confidence_denominator:
            raise Pass128Error("REJECT_MISSING_RELATION_EVIDENCE", "invalid exact confidence")
        if relation_type == "CONTRADICTS" and source["knowledge_node_root_hash72"] == target["knowledge_node_root_hash72"]:
            raise Pass128Error("REJECT_SELF_CONTRADICTION_EDGE", source["normalized_proposition"])
        edge = {
            "schema": EDGE_SCHEMA, "pass_id": PASS_ID,
            "source_node_root_hash72": source["knowledge_node_root_hash72"],
            "target_node_root_hash72": target["knowledge_node_root_hash72"],
            "relation_type": relation_type, "directed": bool(directed),
            "relation_evidence_roots": sorted(set(evidence_roots)),
            "confidence": {"numerator": confidence_numerator, "denominator": confidence_denominator},
            "execution_authority": False, "mutation_authority": False, "executable": False,
        }
        edge["knowledge_edge_root_hash72"] = _hash("hhs_pass128_edge_v1", edge)
        return edge

    def verify_edge(self, edge: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(edge); claimed = obj.pop("knowledge_edge_root_hash72", None)
        if obj.get("relation_type") not in self.RELATIONS or claimed != _hash("hhs_pass128_edge_v1", obj):
            raise Pass128Error("REJECT_EDGE_ROOT_MISMATCH", str(claimed))
        if not obj.get("relation_evidence_roots"):
            raise Pass128Error("REJECT_MISSING_RELATION_EVIDENCE", str(claimed))
        obj["knowledge_edge_root_hash72"] = claimed
        return obj

    def build_graph(self, nodes: Sequence[Mapping[str, Any]], edges: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        if not nodes or len(nodes) > self.bounds.max_nodes or len(edges) > self.bounds.max_edges:
            raise Pass128Error("REJECT_UNBOUNDED_GRAPH", "node/edge count")
        verified_nodes = [self.verify_node(n) for n in nodes]
        roots = [n["knowledge_node_root_hash72"] for n in verified_nodes]
        if len(set(roots)) != len(roots):
            raise Pass128Error("REJECT_DUPLICATE_NODE", "duplicate node root")
        root_set = set(roots)
        verified_edges = [self.verify_edge(e) for e in edges]
        for edge in verified_edges:
            if edge["source_node_root_hash72"] not in root_set or edge["target_node_root_hash72"] not in root_set:
                raise Pass128Error("REJECT_UNKNOWN_ENDPOINT", edge["knowledge_edge_root_hash72"])
        graph = {
            "schema": GRAPH_SCHEMA, "pass_id": PASS_ID,
            "node_roots": sorted(roots),
            "edge_roots": sorted(e["knowledge_edge_root_hash72"] for e in verified_edges),
            "nodes": sorted(verified_nodes, key=lambda n:n["knowledge_node_root_hash72"]),
            "edges": sorted(verified_edges, key=lambda e:e["knowledge_edge_root_hash72"]),
            "node_count": len(nodes), "edge_count": len(edges),
            "execution_authority": False, "mutation_authority": False, "executable": False,
        }
        graph["knowledge_graph_root_hash72"] = _hash("hhs_pass128_graph_v1", graph)
        return graph

    def verify_graph(self, graph: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(graph); claimed = obj.pop("knowledge_graph_root_hash72", None)
        if obj.get("schema") != GRAPH_SCHEMA or claimed != _hash("hhs_pass128_graph_v1", obj):
            raise Pass128Error("REJECT_GRAPH_ROOT_MISMATCH", str(claimed))
        obj["knowledge_graph_root_hash72"] = claimed
        return obj

    def make_query(self, text: str, *, relation_filter: Sequence[str] = (), max_results: int = 16, max_hops: int = 2) -> dict[str, Any]:
        text = text.strip()
        if not text:
            raise Pass128Error("REJECT_QUERY_EMPTY", "empty query")
        if len(text) > self.bounds.max_query_chars or max_results <= 0 or max_results > self.bounds.max_results or max_hops < 0 or max_hops > self.bounds.max_hops:
            raise Pass128Error("REJECT_UNBOUNDED_GRAPH", "query bounds")
        if any(r not in self.RELATIONS for r in relation_filter):
            raise Pass128Error("REJECT_UNSUPPORTED_RELATION", str(relation_filter))
        query = {
            "schema": QUERY_SCHEMA, "pass_id": PASS_ID, "query_text": text,
            "query_tokens": list(self._tokens(text)), "relation_filter": sorted(set(relation_filter)),
            "max_results": max_results, "max_hops": max_hops,
            "execution_authority": False, "mutation_authority": False,
        }
        query["query_root_hash72"] = _hash("hhs_pass128_query_v1", query)
        return query

    def retrieve(self, graph: Mapping[str, Any], query: Mapping[str, Any]) -> dict[str, Any]:
        g = self.verify_graph(graph)
        q = dict(query); qroot = q.pop("query_root_hash72", None)
        if q.get("schema") != QUERY_SCHEMA or qroot != _hash("hhs_pass128_query_v1", q):
            raise Pass128Error("REJECT_QUERY_ROOT_MISMATCH", str(qroot))
        q["query_root_hash72"] = qroot
        qtokens = set(q["query_tokens"])
        scored=[]
        nodes={n["knowledge_node_root_hash72"]:n for n in g["nodes"]}
        for node in nodes.values():
            overlap = len(qtokens.intersection(node["semantic_tokens"]))
            if overlap:
                scored.append((overlap, node["knowledge_node_root_hash72"]))
        if not scored:
            raise Pass128Error("REJECT_QUERY_NO_MATCH", q["query_text"])
        scored.sort(key=lambda x:(-x[0], x[1]))
        seeds=[root for _,root in scored[:q["max_results"]]]
        allowed=set(q["relation_filter"])
        adjacency={r:[] for r in nodes}
        for edge in g["edges"]:
            if allowed and edge["relation_type"] not in allowed: continue
            adjacency[edge["source_node_root_hash72"]].append(edge)
            if not edge["directed"]:
                reverse=dict(edge); reverse["source_node_root_hash72"],reverse["target_node_root_hash72"]=edge["target_node_root_hash72"],edge["source_node_root_hash72"]
                adjacency[reverse["source_node_root_hash72"]].append(reverse)
        paths=[]; expansions=0
        for seed in seeds:
            paths.append({"node_root_path":[seed],"edge_root_path":[],"hop_count":0})
            queue=deque([(seed,[seed],[])])
            seen={(seed,0)}
            while queue:
                current,npath,epath=queue.popleft()
                if len(epath)>=q["max_hops"]: continue
                for edge in adjacency.get(current,[]):
                    expansions += 1
                    if expansions > self.bounds.max_path_expansions:
                        raise Pass128Error("REJECT_UNBOUNDED_GRAPH", "path expansions")
                    nxt=edge["target_node_root_hash72"]
                    state=(nxt,len(epath)+1)
                    if state in seen: continue
                    seen.add(state)
                    np=npath+[nxt]; ep=epath+[edge["knowledge_edge_root_hash72"]]
                    paths.append({"node_root_path":np,"edge_root_path":ep,"hop_count":len(ep)})
                    queue.append((nxt,np,ep))
        selected_roots=[]
        for path in paths:
            for root in path["node_root_path"]:
                if root not in selected_roots and len(selected_roots)<q["max_results"]: selected_roots.append(root)
        if not selected_roots or any(root not in nodes for root in selected_roots):
            raise Pass128Error("REJECT_UNGROUNDED_RESULT", "missing selected node")
        result={
            "schema": RESULT_SCHEMA,"pass_id":PASS_ID,
            "knowledge_graph_root_hash72":g["knowledge_graph_root_hash72"],
            "query_root_hash72":qroot,
            "selected_node_roots":selected_roots,
            "selected_propositions":[nodes[r]["normalized_proposition"] for r in selected_roots],
            "proof_paths":paths[:self.bounds.max_results],
            "status":"EVIDENCE_GROUNDED_RETRIEVAL_VALIDATED",
            "knowledge_authority":True,"execution_authority":False,"mutation_authority":False,"executable":False,
        }
        result["retrieval_result_root_hash72"]=_hash("hhs_pass128_result_v1",result)
        return result

    def assert_no_execution_escalation(self, *objects: Mapping[str, Any]) -> None:
        for obj in objects:
            if obj.get("execution_authority") is not False or obj.get("mutation_authority") is not False:
                raise Pass128Error("REJECT_AUTHORITY_ESCALATION", obj.get("schema","object"))
            if obj.get("executable",False):
                raise Pass128Error("REJECT_EXECUTABLE_RETRIEVAL_ESCALATION", obj.get("schema","object"))

    def replay(self, graph: Mapping[str, Any], query: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any]:
        rebuilt=self.retrieve(graph,query)
        if _canon(rebuilt)!=_canon(result):
            raise Pass128Error("REJECT_REPLAY_MISMATCH","retrieval")
        receipt={"schema":REPLAY_SCHEMA,"pass_id":PASS_ID,
                 "knowledge_graph_root_hash72":graph["knowledge_graph_root_hash72"],
                 "query_root_hash72":query["query_root_hash72"],
                 "retrieval_result_root_hash72":rebuilt["retrieval_result_root_hash72"],
                 "status":"KNOWLEDGE_GRAPH_RETRIEVAL_REPLAY_VALIDATED"}
        receipt["replay_root_hash72"]=_hash("hhs_pass128_replay_v1",receipt)
        return receipt

def pass128_self_test() -> dict[str, Any]:
    from hhs_runtime.hhs_pass127_evidence_grounded_knowledge_admission_v1 import pass127_self_test
    # Build minimal valid Pass 127 records directly from their canonical schema.
    def record(prop: str, suffix: str) -> dict[str, Any]:
        obj={"schema":"HHS_ADMITTED_KNOWLEDGE_RECORD_V1","pass_id":"PASS_127","normalized_proposition":prop,
             "candidate_root_hash72":"candidate:"+suffix,"decision_root_hash72":"decision:"+suffix,
             "support_evidence_roots":["evidence:"+suffix],"knowledge_status":"ADMITTED_EVIDENCE_GROUNDED_KNOWLEDGE",
             "knowledge_authority":True,"execution_authority":False,"mutation_authority":False,"executable":False}
        obj["knowledge_record_root_hash72"]=_hash("hhs_pass127_record_v1",obj); return obj
    pass127_self_test()
    e=CanonicalKnowledgeGraphEngine(); n1=e.node_from_record(record("Mass is conserved.","a")); n2=e.node_from_record(record("Closed systems preserve mass.","b"))
    edge=e.relate(n2,n1,relation_type="SUPPORTS",evidence_roots=["proof:mass"])
    graph=e.build_graph([n1,n2],[edge]); query=e.make_query("mass conserved",max_hops=1)
    result=e.retrieve(graph,query); e.assert_no_execution_escalation(graph,result); replay=e.replay(graph,query,result)
    return {"schema":"HHS_PASS128_SELF_TEST_V1","status":"PASS","graph_root_hash72":graph["knowledge_graph_root_hash72"],"replay_root_hash72":replay["replay_root_hash72"]}
