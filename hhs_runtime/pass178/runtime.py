from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.hash72_checkpoint import make_hash72_witness
from hhs_runtime.pass163.vmrc import VMRCRuntime, VMRCError
from hhs_runtime.pass165.ingestion import DEFAULT_MULTIMODAL_LEARNING_SERVICE

from .constraints import canonical_membrane, membrane_admitted, source_identity
from .exact import ComplexExact, ExactPhysicsError, ExactRational, reject_float
from .quantum import QuantumState, cayley_step
from .relativity import RelativisticParticle, relativistic_free_step
from .render import render_packet


class PhysicsAuthorityError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hash216(domain: str, payload: Mapping[str, Any]) -> str:
    lanes = [
        make_hash72_witness(f"{domain}:previous", payload, width=72).digest,
        make_hash72_witness(f"{domain}:change", payload, width=72).digest,
        make_hash72_witness(f"{domain}:receipt", payload, width=72).digest,
    ]
    value = "".join(lanes)
    if len(value) != 216:
        raise PhysicsAuthorityError("P178_HASH216_LENGTH")
    return value


@dataclass(frozen=True)
class ModelRecord:
    model_id: str
    model_kind: str
    source_sha256: str
    parameters: dict[str, Any]
    graph_root_sha256: str

    def payload(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_178_MODEL_RECORD_V1",
            "model_id": self.model_id,
            "model_kind": self.model_kind,
            "source_sha256": self.source_sha256,
            "parameters": self.parameters,
            "graph_root_sha256": self.graph_root_sha256,
        }


class PhysicsAuthority:
    MODEL_KINDS = {
        "RELATIVISTIC_FREE_PARTICLE",
        "QUANTUM_FINITE_CAYLEY_STEP",
        "HARMONICODE_CONSTRAINT_MEMBRANE",
    }

    def __init__(self, *, vm81: VMRCRuntime | None) -> None:
        self._vm81 = vm81
        self._sources: dict[str, bytes] = {}
        self._models: dict[str, ModelRecord] = {}
        self._states: dict[str, dict[str, Any]] = {}
        self._step_index: dict[str, int] = {}
        self._replay: dict[str, list[dict[str, Any]]] = {}

    def status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_178_RUNTIME_STATUS_V1",
            "contract": "HHS-P178-NEH-RQ-TJS-PSR",
            "implementation_stage": "P178_EXACT_PHYSICS_NUCLEUS_NONTERMINAL",
            "vm81_authority_bound": self._vm81 is not None,
            "singleton_vm81_authority": True,
            "independent_vm81_authority": False,
            "independent_hash72_commit_authority": False,
            "hash216_mutation_authority": False,
            "renderer_mutation_authority": False,
            "gpu_mutation_authority": False,
            "browser_mutation_authority": False,
            "floating_point_canonical_authority": False,
            "registered_model_count": len(self._models),
            "terminal_pass178_completion": False,
            "remaining_terminal_categories": [
                "COMPLETE_HARMONICODE_CONSTRAINT_CORPUS",
                "COMPLETE_TYPED_CST_AST_HIR_PIPELINE",
                "FULL_NATIVE_PUBLIC_ABI_PARITY",
                "THERMODYNAMIC_SYMBOLIC_KERNEL",
                "RELATIVISTIC_CHARGED_PARTICLE_LAB",
                "QUANTUM_DOUBLE_SLIT_LAB",
                "REGISTERED_MEASUREMENT_AUTHORITY",
                "SINGULAR_HASH72_COMMIT_INTEGRATION",
                "THREEJS_EXECUTING_VIEWPORT",
                "DETERMINISTIC_MP4_CAPTURE",
                "BROWSER_MOBILE_E2E_AND_PERFORMANCE",
                "AUTHORITATIVE_MAIN_INTEGRATION",
            ],
        }

    def ingest_source(self, source_id: str, source: bytes) -> dict[str, Any]:
        if not source_id or len(source) > 1048576:
            raise PhysicsAuthorityError("P178_SOURCE_ID_OR_SIZE")
        identity = source_identity(source)
        prior = self._sources.get(source_id)
        if prior is not None and prior != source:
            raise PhysicsAuthorityError("P178_SOURCE_ID_IMMUTABLE_CONFLICT")
        self._sources[source_id] = bytes(source)
        return {
            **identity,
            "source_id": source_id,
            "hash216": _hash216("pass178:source:archive", {
                "source_id": source_id,
                "sha256": identity["sha256"],
                "bytes": identity["bytes"],
            }),
            "canonical_mutation_authority": False,
        }

    def register_model(
        self,
        *,
        model_id: str,
        model_kind: str,
        source_id: str,
        parameters: Mapping[str, Any],
    ) -> dict[str, Any]:
        reject_float(parameters)
        if not model_id or model_kind not in self.MODEL_KINDS:
            raise PhysicsAuthorityError("P178_MODEL_KIND_OR_ID")
        source = self._sources.get(source_id)
        if source is None:
            raise PhysicsAuthorityError("P178_MODEL_SOURCE_NOT_INGESTED")
        source_sha = hashlib.sha256(source).hexdigest()
        if model_kind == "HARMONICODE_CONSTRAINT_MEMBRANE":
            graph = canonical_membrane(parameters)
            graph_root = graph.root_sha256()
        else:
            graph_root = hashlib.sha256(_canonical({
                "model_kind": model_kind,
                "parameters": parameters,
                "source_sha256": source_sha,
            })).hexdigest()
        record = ModelRecord(
            model_id=model_id,
            model_kind=model_kind,
            source_sha256=source_sha,
            parameters=dict(parameters),
            graph_root_sha256=graph_root,
        )
        prior = self._models.get(model_id)
        if prior is not None and prior != record:
            raise PhysicsAuthorityError("P178_MODEL_ID_IMMUTABLE_CONFLICT")
        self._models[model_id] = record
        self._step_index.setdefault(model_id, 0)
        self._replay.setdefault(model_id, [])
        return {
            "schema": "HHS_PASS_178_MODEL_REGISTER_RESULT_V1",
            "ok": True,
            "model": record.payload(),
            "registry_only": True,
            "vm81_state_mutation": False,
        }

    def _vm81_commit(self, transition: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self._vm81 is None:
            raise PhysicsAuthorityError("P178_VM81_ADMISSION_AUTHORITY_REQUIRED")
        material = _canonical({"transition": transition, "payload": payload})
        digest = hashlib.sha256(material).digest()
        writes: dict[int, int] = {}
        for byte in digest[:24]:
            writes[int(byte % 81)] = 1 if byte & 1 else -1
        try:
            candidate = self._vm81.submit_candidate(
                thread=58,
                writes=writes,
                operation="VMRC_COMMIT",
                expected_input_hash72=self._vm81.state_hash72,
                dependency_root=hashlib.sha256(
                    b"HHS-P178-PHYSICS-VM81\0" + material
                ).hexdigest(),
                capability_scope="P178_EXACT_PHYSICS_ADMISSION",
                source_architecture="P178_EXACT_PHYSICS_RUNTIME",
                target_architecture="VM81",
            )
            result = self._vm81.execute(candidate)
        except VMRCError as error:
            raise PhysicsAuthorityError(f"P178_VM81_ADMISSION_REJECTED:{error}") from error
        commit = result.get("commit") or {}
        receipt = commit.get("receipt") or {}
        validated = (result.get("validation") or {}).get("validated") or {}
        if commit.get("classification") != "HHS_PASS_163_COMMIT_ADMITTED":
            raise PhysicsAuthorityError("P178_VM81_ADMISSION_NOT_COMMITTED")
        if not receipt.get("receipt_hash72") or not receipt.get("operation_hash216"):
            raise PhysicsAuthorityError("P178_VM81_RECEIPT_INCOMPLETE")
        return {
            "classification": "HHS_PASS178_VM81_PHYSICS_ADMISSION_VERIFIED",
            "candidate_id": candidate.candidate_id,
            "receipt_hash72": str(receipt["receipt_hash72"]),
            "operation_hash216": str(receipt["operation_hash216"]),
            "output_hash72": str(receipt.get("output_hash72") or ""),
            "vm81_epoch": self._vm81.epoch,
            "singleton_authority": True,
            "independent_vm81_authority": False,
            "validation_mutation_authority": bool(validated.get("mutation_authority", False)),
        }

    def admit_initial_state(self, model_id: str, state: Mapping[str, Any]) -> dict[str, Any]:
        reject_float(state)
        model = self._models.get(model_id)
        if model is None:
            raise PhysicsAuthorityError("P178_MODEL_NOT_REGISTERED")
        canonical_state = self._validate_state(model, state, initial=True)
        candidate_sha = hashlib.sha256(_canonical(canonical_state)).hexdigest()
        admission = self._vm81_commit("INITIAL_STATE", {
            "model_id": model_id,
            "model_kind": model.model_kind,
            "candidate_state_sha256": candidate_sha,
            "graph_root_sha256": model.graph_root_sha256,
            "step_index": 0,
        })
        evidence = self._finalize_committed_state(
            model=model,
            canonical_state=canonical_state,
            step_index=0,
            prior_state_hash216="0" * 216,
            admission=admission,
            operation="INITIAL_STATE",
        )
        self._states[model_id] = evidence
        self._step_index[model_id] = 0
        self._replay[model_id] = [evidence]
        return evidence

    def step_candidate(self, model_id: str) -> dict[str, Any]:
        model = self._models.get(model_id)
        current = self._states.get(model_id)
        if model is None or current is None:
            raise PhysicsAuthorityError("P178_MODEL_OR_STATE_NOT_READY")
        next_index = self._step_index[model_id] + 1
        try:
            candidate_state = self._evolve(model, current["canonical_state"], next_index)
            validated = self._validate_state(model, candidate_state, initial=False)
        except (ExactPhysicsError, PhysicsAuthorityError) as error:
            return {
                "schema": "HHS_PASS_178_STEP_CANDIDATE_V1",
                "ok": False,
                "status": "REJECTED",
                "reason": str(error),
                "model_id": model_id,
                "candidate_step_index": next_index,
                "authoritative_clock_advanced": False,
                "vm81_admitted": False,
            }
        return {
            "schema": "HHS_PASS_178_STEP_CANDIDATE_V1",
            "ok": True,
            "status": "VALIDATED_CANDIDATE",
            "model_id": model_id,
            "candidate_step_index": next_index,
            "canonical_state": validated,
            "candidate_state_sha256": hashlib.sha256(_canonical(validated)).hexdigest(),
            "authoritative_clock_advanced": False,
            "vm81_admitted": False,
        }

    def commit_step(self, model_id: str, candidate: Mapping[str, Any]) -> dict[str, Any]:
        if candidate.get("ok") is not True or candidate.get("status") != "VALIDATED_CANDIDATE":
            raise PhysicsAuthorityError("P178_CANDIDATE_NOT_VALIDATED")
        model = self._models.get(model_id)
        current = self._states.get(model_id)
        if model is None or current is None:
            raise PhysicsAuthorityError("P178_MODEL_OR_STATE_NOT_READY")
        expected = self._step_index[model_id] + 1
        if candidate.get("candidate_step_index") != expected:
            raise PhysicsAuthorityError("P178_CANDIDATE_STEP_ORDER")
        canonical_state = candidate.get("canonical_state")
        if not isinstance(canonical_state, Mapping):
            raise PhysicsAuthorityError("P178_CANDIDATE_STATE_MISSING")
        admission = self._vm81_commit("STEP_COMMIT", {
            "model_id": model_id,
            "model_kind": model.model_kind,
            "candidate_step_index": expected,
            "candidate_state_sha256": candidate["candidate_state_sha256"],
            "prior_state_hash216": current["state_hash216"],
            "graph_root_sha256": model.graph_root_sha256,
        })
        evidence = self._finalize_committed_state(
            model=model,
            canonical_state=dict(canonical_state),
            step_index=expected,
            prior_state_hash216=current["state_hash216"],
            admission=admission,
            operation="STEP_COMMIT",
        )
        self._states[model_id] = evidence
        self._step_index[model_id] = expected
        self._replay[model_id].append(evidence)
        return evidence

    def replay(self, model_id: str) -> dict[str, Any]:
        records = self._replay.get(model_id)
        if not records:
            raise PhysicsAuthorityError("P178_REPLAY_EMPTY")
        valid = True
        prior = "0" * 216
        for index, record in enumerate(records):
            if record["step_index"] != index or record["prior_state_hash216"] != prior:
                valid = False
                break
            prior = record["state_hash216"]
        return {
            "schema": "HHS_PASS_178_REPLAY_RESULT_V1",
            "ok": valid,
            "model_id": model_id,
            "step_count": len(records),
            "final_state_hash216": records[-1]["state_hash216"],
            "deterministic_replay_chain": valid,
        }

    def project_render_packet(self, model_id: str) -> dict[str, Any]:
        current = self._states.get(model_id)
        model = self._models.get(model_id)
        if current is None or model is None:
            raise PhysicsAuthorityError("P178_MODEL_OR_STATE_NOT_READY")
        state = current["canonical_state"]
        if model.model_kind == "RELATIVISTIC_FREE_PARTICLE":
            position4 = [ExactRational(*pair) for pair in state["position4"]]
            position3 = position4[1:4]
            time = position4[0]
        else:
            position3 = (ExactRational(0), ExactRational(0), ExactRational(0))
            time = ExactRational(current["step_index"], 1)
        return render_packet(
            step_index=current["step_index"],
            world_time=time,
            position3=position3,
            phase_index_mod_72=current["step_index"] % 72,
            state_hash216=current["state_hash216"],
            transition_hash216=current["transition_hash216"],
        )

    def _validate_state(
        self,
        model: ModelRecord,
        state: Mapping[str, Any],
        *,
        initial: bool,
    ) -> dict[str, Any]:
        reject_float(state)
        if model.model_kind == "RELATIVISTIC_FREE_PARTICLE":
            particle = RelativisticParticle(
                particle_id=str(state.get("particle_id") or model.model_id),
                mass=ExactRational.coerce(state["mass"]),
                charge=ExactRational.coerce(state.get("charge", 0)),
                position4=tuple(ExactRational.coerce(v) for v in state["position4"]),  # type: ignore[arg-type]
                four_velocity=tuple(ExactRational.coerce(v) for v in state["four_velocity"]),  # type: ignore[arg-type]
                proper_step=ExactRational.coerce(state["proper_step"]),
            )
            return particle.payload()
        if model.model_kind == "QUANTUM_FINITE_CAYLEY_STEP":
            amplitudes = tuple(
                ComplexExact(
                    ExactRational(*pair[0]),
                    ExactRational(*pair[1]),
                )
                for pair in state["amplitudes"]
            )
            qstate = QuantumState(
                state_id=str(state.get("state_id") or model.model_id),
                amplitudes=amplitudes,
                step_index=int(state.get("step_index", 0)),
            )
            return qstate.payload()
        if model.model_kind == "HARMONICODE_CONSTRAINT_MEMBRANE":
            graph = canonical_membrane(state)
            if not membrane_admitted(graph):
                raise PhysicsAuthorityError("P178_HARMONICODE_MEMBRANE_REJECTED")
            return {
                "schema": "HHS_PASS_178_HARMONICODE_STATE_V1",
                "values": {
                    key: ExactRational.coerce(state[key]).as_pair()
                    for key in ("P", "A", "B", "p", "q")
                },
                "constraint_graph": graph.payload(),
            }
        raise PhysicsAuthorityError("P178_MODEL_KIND_UNSUPPORTED")

    def _evolve(
        self,
        model: ModelRecord,
        state: Mapping[str, Any],
        next_index: int,
    ) -> dict[str, Any]:
        if model.model_kind == "RELATIVISTIC_FREE_PARTICLE":
            particle = RelativisticParticle(
                particle_id=str(state["particle_id"]),
                mass=ExactRational(*state["mass"]),
                charge=ExactRational(*state["charge"]),
                position4=tuple(ExactRational(*pair) for pair in state["position4"]),  # type: ignore[arg-type]
                four_velocity=tuple(ExactRational(*pair) for pair in state["four_velocity"]),  # type: ignore[arg-type]
                proper_step=ExactRational(*state["proper_step"]),
            )
            return relativistic_free_step(particle).payload()
        if model.model_kind == "QUANTUM_FINITE_CAYLEY_STEP":
            qstate = QuantumState(
                state_id=str(state["state_id"]),
                amplitudes=tuple(
                    ComplexExact(ExactRational(*pair[0]), ExactRational(*pair[1]))
                    for pair in state["amplitudes"]
                ),
                step_index=int(state["step_index"]),
            )
            H = model.parameters.get("hamiltonian")
            dt = model.parameters.get("dt")
            hbar = model.parameters.get("hbar", 1)
            if H is None or dt is None:
                raise PhysicsAuthorityError("P178_QUANTUM_MODEL_PARAMETERS_MISSING")
            return cayley_step(qstate, H, dt, hbar).payload()
        if model.model_kind == "HARMONICODE_CONSTRAINT_MEMBRANE":
            return dict(state["values"])
        raise PhysicsAuthorityError("P178_MODEL_KIND_UNSUPPORTED")

    def _finalize_committed_state(
        self,
        *,
        model: ModelRecord,
        canonical_state: Mapping[str, Any],
        step_index: int,
        prior_state_hash216: str,
        admission: Mapping[str, Any],
        operation: str,
    ) -> dict[str, Any]:
        candidate_sha = hashlib.sha256(_canonical(canonical_state)).hexdigest()
        evidence_payload = {
            "model_id": model.model_id,
            "model_kind": model.model_kind,
            "step_index": step_index,
            "prior_state_hash216": prior_state_hash216,
            "candidate_state_sha256": candidate_sha,
            "graph_root_sha256": model.graph_root_sha256,
            "vm81_receipt_hash72": admission["receipt_hash72"],
            "vm81_output_hash72": admission["output_hash72"],
            "operation": operation,
        }
        hash72_evidence = make_hash72_witness(
            "pass178:post-vm81:state-evidence", evidence_payload, width=72
        ).digest
        transition_hash216 = _hash216("pass178:transition:archive", evidence_payload)
        state_payload = {**evidence_payload, "transition_hash216": transition_hash216}
        state_hash216 = _hash216("pass178:state:archive", state_payload)
        return {
            "schema": "HHS_PASS_178_COMMITTED_STATE_V1",
            "model_id": model.model_id,
            "model_kind": model.model_kind,
            "step_index": step_index,
            "prior_state_hash216": prior_state_hash216,
            "canonical_state": dict(canonical_state),
            "candidate_state_sha256": candidate_sha,
            "vm81_admission": dict(admission),
            "post_vm81_hash72_evidence": hash72_evidence,
            "transition_hash216": transition_hash216,
            "state_hash216": state_hash216,
            "hash72_commit_authority": False,
            "hash216_mutation_authority": False,
            "authoritative_clock_advanced": True,
        }


PASS178_PHYSICS = PhysicsAuthority(
    vm81=DEFAULT_MULTIMODAL_LEARNING_SERVICE._vm81,
)


def contract_corpus_identity() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    path = root / "contracts/pass178/HARMONICODE_PHYSICS_CONSTRAINT_CORPUS.hhs"
    source = path.read_bytes()
    ident = source_identity(source)
    return {
        **ident,
        "path": str(path.relative_to(root)),
        "classification": "CONTRACT_VISIBLE_CORPUS_NUCLEUS_NOT_COMPLETE_HISTORICAL_CORPUS",
        "hash216": _hash216("pass178:constraint-corpus:archive", {
            "sha256": ident["sha256"],
            "bytes": ident["bytes"],
        }),
    }
