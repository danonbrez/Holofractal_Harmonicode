from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash

PASS_ID = "PASS_122"
SNAPSHOT_SCHEMA = "HHS_READ_ONLY_SOURCE_SNAPSHOT_V1"
OBSERVATION_SCHEMA = "HHS_SELF_ANALYSIS_OBSERVATION_V1"
KNOWLEDGE_SCHEMA = "HHS_SELF_ANALYSIS_KNOWLEDGE_RECORD_V1"
CORPUS_SCHEMA = "HHS_SELF_ANALYSIS_KNOWLEDGE_CORPUS_V1"
QUERY_SCHEMA = "HHS_SELF_ANALYSIS_QUERY_RECEIPT_V1"
REPLAY_SCHEMA = "HHS_SELF_ANALYSIS_REPLAY_RECEIPT_V1"

REJECTION_CODES = {
    "REJECT_SOURCE_OUTSIDE_ANALYSIS_ROOT",
    "REJECT_UNSUPPORTED_SOURCE_TYPE",
    "REJECT_SOURCE_CHANGED_DURING_ANALYSIS",
    "REJECT_MALFORMED_SOURCE",
    "REJECT_OBSERVATION_WITHOUT_EVIDENCE",
    "REJECT_OBSERVATION_ROOT_MISMATCH",
    "REJECT_KNOWLEDGE_RECORD_MUTATION",
    "REJECT_EXECUTION_AUTHORITY_ESCALATION",
    "REJECT_MUTATION_AUTHORITY_ESCALATION",
    "REJECT_UNBOUNDED_ANALYSIS_REQUEST",
    "REJECT_QUERY_WITHOUT_CORPUS",
    "REJECT_REPLAY_MISMATCH",
}


class Pass122Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class SourceArtifact:
    relative_path: str
    source_type: str
    byte_length: int
    line_count: int
    content_root_hash72: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "relative_path": self.relative_path,
            "source_type": self.source_type,
            "byte_length": self.byte_length,
            "line_count": self.line_count,
            "content_root_hash72": self.content_root_hash72,
        }


class ReadOnlySelfAnalysisEngine:
    """Evidence-bound self-analysis with no execution or mutation authority."""

    ALLOWED_SUFFIXES = {".py": "PYTHON_SOURCE", ".json": "JSON_ARTIFACT", ".md": "MARKDOWN_ARTIFACT"}

    def __init__(self, repository_root: str | Path, *, max_files: int = 4096, max_bytes: int = 64 * 1024 * 1024):
        self.repository_root = Path(repository_root).resolve()
        self.max_files = int(max_files)
        self.max_bytes = int(max_bytes)
        if self.max_files <= 0 or self.max_bytes <= 0:
            raise Pass122Error("REJECT_UNBOUNDED_ANALYSIS_REQUEST", "positive bounds required")

    def snapshot(self, paths: Sequence[str | Path]) -> dict[str, Any]:
        if len(paths) > self.max_files:
            raise Pass122Error("REJECT_UNBOUNDED_ANALYSIS_REQUEST", "file count")
        artifacts: list[dict[str, Any]] = []
        total_bytes = 0
        for requested in sorted({str(p) for p in paths}):
            path = (self.repository_root / requested).resolve()
            try:
                rel = path.relative_to(self.repository_root).as_posix()
            except ValueError as exc:
                raise Pass122Error("REJECT_SOURCE_OUTSIDE_ANALYSIS_ROOT", requested) from exc
            source_type = self.ALLOWED_SUFFIXES.get(path.suffix.lower())
            if source_type is None:
                raise Pass122Error("REJECT_UNSUPPORTED_SOURCE_TYPE", rel)
            data = path.read_bytes()
            total_bytes += len(data)
            if total_bytes > self.max_bytes:
                raise Pass122Error("REJECT_UNBOUNDED_ANALYSIS_REQUEST", "byte budget")
            text = data.decode("utf-8")
            artifacts.append(SourceArtifact(rel, source_type, len(data), len(text.splitlines()), _hash("hhs_pass122_source_content_v1", data.hex())).to_dict())
        snapshot = {
            "schema": SNAPSHOT_SCHEMA,
            "pass_id": PASS_ID,
            "repository_root_identity": _hash("hhs_pass122_repository_root_v1", self.repository_root.name),
            "artifacts": artifacts,
            "artifact_count": len(artifacts),
            "total_bytes": total_bytes,
            "read_only": True,
            "execution_authority": False,
            "mutation_authority": False,
        }
        snapshot["snapshot_root_hash72"] = _hash("hhs_pass122_snapshot_v1", snapshot)
        return snapshot

    def analyze(self, snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
        self._verify_snapshot(snapshot)
        observations: list[dict[str, Any]] = []
        for artifact in snapshot["artifacts"]:
            rel = artifact["relative_path"]
            path = self.repository_root / rel
            text = path.read_text(encoding="utf-8")
            current = _hash("hhs_pass122_source_content_v1", text.encode("utf-8").hex())
            if current != artifact["content_root_hash72"]:
                raise Pass122Error("REJECT_SOURCE_CHANGED_DURING_ANALYSIS", rel)
            if artifact["source_type"] == "PYTHON_SOURCE":
                observations.extend(self._analyze_python(rel, text, artifact["content_root_hash72"]))
            elif artifact["source_type"] == "JSON_ARTIFACT":
                observations.append(self._observation(rel, "ARTIFACT_PRESENT", {"format": "JSON", "line_count": artifact["line_count"]}, artifact["content_root_hash72"], [1, artifact["line_count"]]))
            else:
                observations.append(self._observation(rel, "DOCUMENT_PRESENT", {"format": "MARKDOWN", "line_count": artifact["line_count"]}, artifact["content_root_hash72"], [1, artifact["line_count"]]))
        return observations

    def admit_knowledge(self, observations: Sequence[Mapping[str, Any]], *, corpus_parent_root_hash72: str | None = None) -> dict[str, Any]:
        records: list[dict[str, Any]] = []
        for obs in observations:
            self._verify_observation(obs)
            record = {
                "schema": KNOWLEDGE_SCHEMA,
                "observation_root_hash72": obs["observation_root_hash72"],
                "subject": obs["relative_path"],
                "predicate": obs["observation_type"],
                "object": deepcopy(obs["details"]),
                "evidence": deepcopy(obs["evidence"]),
                "epistemic_status": "OBSERVED_FROM_ROOTED_SOURCE",
                "execution_authority": False,
                "mutation_authority": False,
                "admission_effect": "KNOWLEDGE_ONLY",
            }
            record["knowledge_record_root_hash72"] = _hash("hhs_pass122_knowledge_record_v1", record)
            records.append(record)
        corpus = {
            "schema": CORPUS_SCHEMA,
            "pass_id": PASS_ID,
            "parent_corpus_root_hash72": corpus_parent_root_hash72,
            "records": records,
            "record_count": len(records),
            "execution_authority": False,
            "mutation_authority": False,
            "runtime_changes": [],
        }
        corpus["corpus_root_hash72"] = _hash("hhs_pass122_corpus_v1", corpus)
        return corpus

    def query(self, corpus: Mapping[str, Any], *, predicate: str | None = None, subject_contains: str | None = None) -> dict[str, Any]:
        self._verify_corpus(corpus)
        matches = []
        for record in corpus["records"]:
            if predicate is not None and record["predicate"] != predicate:
                continue
            if subject_contains is not None and subject_contains not in record["subject"]:
                continue
            matches.append(deepcopy(record))
        receipt = {
            "schema": QUERY_SCHEMA,
            "corpus_root_hash72": corpus["corpus_root_hash72"],
            "predicate": predicate,
            "subject_contains": subject_contains,
            "matches": matches,
            "match_count": len(matches),
            "authority_effect": "NONE",
        }
        receipt["query_receipt_root_hash72"] = _hash("hhs_pass122_query_v1", receipt)
        return receipt

    def replay(self, snapshot: Mapping[str, Any], expected_corpus: Mapping[str, Any]) -> dict[str, Any]:
        observations = self.analyze(snapshot)
        replayed = self.admit_knowledge(observations, corpus_parent_root_hash72=expected_corpus.get("parent_corpus_root_hash72"))
        if replayed["corpus_root_hash72"] != expected_corpus.get("corpus_root_hash72"):
            raise Pass122Error("REJECT_REPLAY_MISMATCH", "corpus root")
        receipt = {
            "schema": REPLAY_SCHEMA,
            "snapshot_root_hash72": snapshot["snapshot_root_hash72"],
            "corpus_root_hash72": replayed["corpus_root_hash72"],
            "replay_status": "DETERMINISTIC_SELF_ANALYSIS_REPLAY_VALIDATED",
            "execution_authority": False,
            "mutation_authority": False,
        }
        receipt["replay_receipt_root_hash72"] = _hash("hhs_pass122_replay_v1", receipt)
        return receipt

    def assert_no_authority_escalation(self, record: Mapping[str, Any]) -> None:
        if record.get("execution_authority") is not False:
            raise Pass122Error("REJECT_EXECUTION_AUTHORITY_ESCALATION", "knowledge cannot execute")
        if record.get("mutation_authority") is not False:
            raise Pass122Error("REJECT_MUTATION_AUTHORITY_ESCALATION", "knowledge cannot mutate")

    def _analyze_python(self, rel: str, text: str, content_root: str) -> list[dict[str, Any]]:
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError as exc:
            raise Pass122Error("REJECT_MALFORMED_SOURCE", f"{rel}:{exc.lineno}") from exc
        out: list[dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "CLASS_DECLARED" if isinstance(node, ast.ClassDef) else "CALLABLE_DECLARED"
                out.append(self._observation(rel, kind, {"name": node.name, "decorator_count": len(node.decorator_list)}, content_root, [node.lineno, getattr(node, "end_lineno", node.lineno)]))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.endswith(("SCHEMA", "PASS_ID", "REJECTION_CODES")):
                        out.append(self._observation(rel, "CONTRACT_CONSTANT_DECLARED", {"name": target.id}, content_root, [node.lineno, getattr(node, "end_lineno", node.lineno)]))
            elif isinstance(node, ast.Assert):
                out.append(self._observation(rel, "TEST_ASSERTION_DECLARED", {"expression": ast.unparse(node.test)}, content_root, [node.lineno, getattr(node, "end_lineno", node.lineno)]))
        return out

    @staticmethod
    def _observation(rel: str, kind: str, details: Mapping[str, Any], content_root: str, line_span: Sequence[int]) -> dict[str, Any]:
        obs = {
            "schema": OBSERVATION_SCHEMA,
            "relative_path": rel,
            "observation_type": kind,
            "details": deepcopy(dict(details)),
            "evidence": {"content_root_hash72": content_root, "line_span": list(line_span)},
            "interpretation_scope": "READ_ONLY_STRUCTURAL_ANALYSIS",
            "execution_authority": False,
            "mutation_authority": False,
        }
        obs["observation_root_hash72"] = _hash("hhs_pass122_observation_v1", obs)
        return obs

    def _verify_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        body = dict(snapshot); root = body.pop("snapshot_root_hash72", None)
        if root != _hash("hhs_pass122_snapshot_v1", body):
            raise Pass122Error("REJECT_SOURCE_CHANGED_DURING_ANALYSIS", "snapshot root")
        self.assert_no_authority_escalation(snapshot)

    def _verify_observation(self, obs: Mapping[str, Any]) -> None:
        if not obs.get("evidence", {}).get("content_root_hash72"):
            raise Pass122Error("REJECT_OBSERVATION_WITHOUT_EVIDENCE", str(obs.get("relative_path")))
        body = dict(obs); root = body.pop("observation_root_hash72", None)
        if root != _hash("hhs_pass122_observation_v1", body):
            raise Pass122Error("REJECT_OBSERVATION_ROOT_MISMATCH", str(obs.get("relative_path")))
        self.assert_no_authority_escalation(obs)

    def _verify_corpus(self, corpus: Mapping[str, Any]) -> None:
        body = dict(corpus); root = body.pop("corpus_root_hash72", None)
        if root != _hash("hhs_pass122_corpus_v1", body):
            raise Pass122Error("REJECT_KNOWLEDGE_RECORD_MUTATION", "corpus root")
        self.assert_no_authority_escalation(corpus)
        for record in corpus.get("records", []):
            item = dict(record); rr = item.pop("knowledge_record_root_hash72", None)
            if rr != _hash("hhs_pass122_knowledge_record_v1", item):
                raise Pass122Error("REJECT_KNOWLEDGE_RECORD_MUTATION", str(record.get("subject")))
            self.assert_no_authority_escalation(record)


def pass122_self_test() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    engine = ReadOnlySelfAnalysisEngine(root)
    snapshot = engine.snapshot([
        "hhs_runtime/hhs_pass121_harmonicode_core_library_v1.py",
        "tests/test_hhs_pass121_harmonicode_core_library_v1.py",
    ])
    observations = engine.analyze(snapshot)
    corpus = engine.admit_knowledge(observations)
    replay = engine.replay(snapshot, corpus)
    return {
        "ok": replay["replay_status"] == "DETERMINISTIC_SELF_ANALYSIS_REPLAY_VALIDATED",
        "snapshot_root_hash72": snapshot["snapshot_root_hash72"],
        "corpus_root_hash72": corpus["corpus_root_hash72"],
        "observation_count": len(observations),
        "execution_authority": corpus["execution_authority"],
        "mutation_authority": corpus["mutation_authority"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(pass122_self_test(), indent=2, sort_keys=True))
