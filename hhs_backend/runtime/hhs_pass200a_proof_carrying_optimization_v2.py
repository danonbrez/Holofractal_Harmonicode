"""Pass 200A V2 repair: independently executed, receipt-bound compiler shadows.

This module repair-forwards the accepted Pass 200A V1 contract without
expanding its authority.  Candidate execution remains compare-only and the
reference lane remains the only returned path.
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    evaluate_branch_candidate,
)
from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization_v1 import (
    BUNDLE_SCHEMA,
    CLASSIFICATION,
    CONTRACT,
    DEFAULT_HOLDOUTS,
    DEFAULT_SHADOW_CONFIG,
    ENVELOPE_SCHEMA,
    EVENT_SCHEMA,
    OPERATION_ID,
    PASS200A_OPTIMIZATION_AUTHORITY as PASS200A_V1_SINGLETON,
    SHADOW_PLAN_SCHEMA,
    SHADOW_RUN_SCHEMA,
    VERSION as V1_VERSION,
    Pass200AError,
    Pass200AProofCarryingOptimizationAuthority as Pass200AProofCarryingOptimizationAuthorityV1,
    _copy,
    _without_identifier,
)
from hhs_backend.runtime.pass197_exact_v1 import canonical_json, hash72
from hhs_runtime.hhs_vm81_receipt_provenance_v1 import require_runtime_receipt_hash72

VERSION = "HHS_PASS_200A_PROOF_CARRYING_SHADOW_OPTIMIZATION_V2"
REPAIR_CLASSIFICATION = "HHS_PASS_200A_PROOF_CARRYING_COMPILER_SHADOW_REPAIRED_VERIFIED"
NONPRODUCTION_CLASSIFICATION = "HHS_PASS_200A_NONPRODUCTION_SHADOW_PROFILE"
REPAIR_SCHEMA = "HHS_PASS_200A_POST_MERGE_REPAIR_V2"
QUALIFYING_PROOF_STATUS = "COMPILER_CANDIDATE"

PRODUCTION_TOTALS = {
    "evaluated_parameter_states": 290,
    "branch_job_count": 580,
    "admitted_parameter_states": 263,
    "domain_rejected_parameter_states": 27,
    "address_comparisons": 1_363_392,
    "negative_mutation_count": 24,
}


def _same_payload(left: Any, right: Any) -> bool:
    return canonical_json(left) == canonical_json(right)


class Pass200AProofCarryingOptimizationAuthority(
    Pass200AProofCarryingOptimizationAuthorityV1
):
    """Corrected canonical Pass 200A production authority.

    Repairs the seven post-merge findings recorded on PR #138:
    - canonical VM81 receipt-chain provenance is required for mutation;
    - compiled candidate and reference lanes are independently evaluated;
    - persisted shadow identities and event bindings are revalidated;
    - stale/revoked Pass 198 proof bindings are rejected;
    - production closure is gated by the exact production profile/totals;
    - the canonical singleton is upgraded in-place by the production wrapper;
    - partial holdout persistence remains a recoverable in-progress state.
    """

    @property
    def production_profile(self) -> bool:
        return _same_payload(tuple(self.holdouts), DEFAULT_HOLDOUTS)

    @staticmethod
    def _receipt(receipt_hash72: str | None) -> tuple[str, dict[str, Any]]:
        value = str(receipt_hash72 or "")
        evidence = require_runtime_receipt_hash72(value)
        return value, evidence

    @staticmethod
    def _assert_independence(
        envelopes: Sequence[Mapping[str, Any]],
        *,
        require_complete: bool = True,
    ) -> None:
        if require_complete and len(envelopes) < 4:
            raise Pass200AError("four independent holdout envelopes are required")
        for field in (
            "tree_hash72",
            "config_hash72",
            "report_hash72",
            "state_root_hash72",
            "pass198_run_id",
        ):
            values = [item[field] for item in envelopes]
            if len(values) != len(set(values)):
                raise Pass200AError(f"holdout evidence is not independent: {field}")
        if not all(
            mutation.get("detected") is True
            for envelope in envelopes
            for mutation in envelope.get("negative_mutations", [])
        ):
            raise Pass200AError("holdout negative mutation set is incomplete")

    def _current_proof(self, bundle: Mapping[str, Any]) -> dict[str, Any]:
        matches = [
            proof
            for proof in self.distributed.pass198.list_simplifications(OPERATION_ID)
            if proof.get("simplification_id") == bundle.get("simplification_id")
        ]
        if len(matches) != 1:
            raise Pass200AError("bundle source simplification is missing or ambiguous")
        current = matches[0]
        if current.get("status") != QUALIFYING_PROOF_STATUS:
            raise Pass200AError(
                "bundle source proof is no longer the current compiler candidate: "
                f"{current.get('status')}"
            )
        if current.get("proof_hash72") != bundle.get("proof_hash72"):
            raise Pass200AError("bundle source proof Hash72 no longer matches current proof")
        if current.get("source_operation_identity") != bundle.get("source_operation_identity"):
            raise Pass200AError("bundle source operation identity drift")
        if current.get("candidate_operation_identity") != bundle.get("candidate_operation_identity"):
            raise Pass200AError("bundle candidate operation identity drift")
        return _copy(current)

    @staticmethod
    def _verify_bundle_identity(document: Mapping[str, Any]) -> None:
        expected = hash72(
            "pass200a.bundle",
            _without_identifier(document, "bundle_hash72", "event_hash72"),
        )
        if expected != document.get("bundle_hash72"):
            raise Pass200AError("persisted optimization bundle was tampered")
        if document.get("compiler_mode") != "SHADOW":
            raise Pass200AError("non-shadow optimization bundle detected")
        if document.get("candidate_execution_is_authority") is not False:
            raise Pass200AError("candidate authority drift detected")

    def list_bundles(self) -> list[dict[str, Any]]:
        bundles = [
            json.loads(row[0])
            for row in self._db.execute(
                "SELECT payload_json FROM bundles ORDER BY simplification_id"
            )
        ]
        for document in bundles:
            self._verify_bundle_identity(document)
            self._current_proof(document)
        return bundles

    def get_bundle(self, bundle_id: str) -> dict[str, Any]:
        row = self._db.execute(
            "SELECT payload_json FROM bundles WHERE bundle_id=?",
            (str(bundle_id),),
        ).fetchone()
        if not row:
            raise Pass200AError("unknown optimization bundle")
        document = json.loads(row[0])
        self._verify_bundle_identity(document)
        self._current_proof(document)
        return document

    def compile_shadow_plan(
        self,
        bundle_id: str,
        invocation: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        plan = super().compile_shadow_plan(bundle_id, invocation)
        bundle = self.get_bundle(bundle_id)
        plan = _copy(plan)
        plan["version"] = VERSION
        plan["repair_schema"] = REPAIR_SCHEMA
        plan["bound_current_proof_hash72"] = bundle["proof_hash72"]
        plan["program_hash72"] = hash72(
            "pass200a.shadow.program.v2",
            {key: value for key, value in plan.items() if key != "program_hash72"},
        )
        return plan

    @staticmethod
    def _candidate_projection(candidate: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "ordinal": int(candidate["ordinal"]),
            "x": _copy(candidate["x"]),
            "y": _copy(candidate["y"]),
            "xy_symbol": candidate["xy_symbol"],
            "x_times_y": _copy(candidate["x_times_y"]),
            "status": candidate["status"],
            "address_count": int(candidate["address_count"]),
            "singular_count": int(candidate["singular_count"]),
            "cell_value_hashes": list(candidate["cell_value_hashes"]),
            "cell_root_hash72": candidate["cell_root_hash72"],
            "address_witness_root_hash72": candidate["address_witness_root_hash72"],
            "equivalence_root_hash72": candidate["equivalence_root_hash72"],
        }

    def _execute_compiled_lanes(
        self,
        bundle: Mapping[str, Any],
        plan: Mapping[str, Any],
    ) -> dict[str, Any]:
        config = _copy(plan["call"]["arguments"])
        tree = self.distributed.pass198.parameter_tree(OPERATION_ID, config)
        run_id = hash72(
            "pass200a.shadow.direct.run",
            {
                "bundle_id": bundle["bundle_id"],
                "program_hash72": plan["program_hash72"],
                "tree_hash72": tree["tree_hash72"],
            },
        )

        def execute(branch: str) -> list[dict[str, Any]]:
            records: list[dict[str, Any]] = []
            for state in tree["states"]:
                arguments = {
                    "run_id": run_id,
                    "operation_id": OPERATION_ID,
                    "operation_spec_hash72": tree["operation_spec_hash72"],
                    "tree_hash72": tree["tree_hash72"],
                    "ordinal": int(state["ordinal"]),
                    "branch": branch,
                    "x": _copy(state["x"]),
                    "y": _copy(state["y"]),
                    "xy_symbol": state["xy_symbol"],
                }
                records.append(
                    self._candidate_projection(evaluate_branch_candidate(arguments))
                )
            return records

        reference = execute("A")
        candidate = execute("B")
        reference_replay = execute("A")
        candidate_replay = execute("B")

        reference_semantic = hash72("pass200a.shadow.semantic", reference)
        candidate_semantic = hash72("pass200a.shadow.semantic", candidate)
        reference_replay_root = hash72("pass200a.shadow.semantic", reference_replay)
        candidate_replay_root = hash72("pass200a.shadow.semantic", candidate_replay)
        reference_witness = hash72(
            "pass200a.shadow.witness",
            [item["address_witness_root_hash72"] for item in reference],
        )
        candidate_witness = hash72(
            "pass200a.shadow.witness",
            [item["address_witness_root_hash72"] for item in candidate],
        )
        exact_match = reference_semantic == candidate_semantic
        witness_match = reference_witness == candidate_witness
        replay_match = (
            reference_semantic == reference_replay_root
            and candidate_semantic == candidate_replay_root
            and reference_replay_root == candidate_replay_root
        )
        return {
            "tree_hash72": tree["tree_hash72"],
            "state_count": len(tree["states"]),
            "reference_semantic_root_hash72": reference_semantic,
            "candidate_semantic_root_hash72": candidate_semantic,
            "reference_witness_root_hash72": reference_witness,
            "candidate_witness_root_hash72": candidate_witness,
            "reference_replay_root_hash72": reference_replay_root,
            "candidate_replay_root_hash72": candidate_replay_root,
            "exact_match": exact_match,
            "witness_match": witness_match,
            "replay_match": replay_match,
            "candidate_lane_executed": True,
            "reference_lane_executed": True,
            "candidate_execution_is_authority": False,
        }

    @staticmethod
    def _verify_shadow_identity(document: Mapping[str, Any]) -> None:
        expected = hash72(
            "pass200a.shadow.run",
            _without_identifier(document, "shadow_hash72", "event_hash72"),
        )
        if expected != document.get("shadow_hash72"):
            raise Pass200AError("persisted compiler shadow payload was tampered")
        if document.get("candidate_activated") is not False:
            raise Pass200AError("candidate activation is forbidden in Pass 200A")
        if document.get("returned_path") != "REFERENCE":
            raise Pass200AError("Pass 200A shadow must return the reference path")

    def _shadow_event_bound(self, document: Mapping[str, Any]) -> bool:
        row = self._db.execute(
            "SELECT e.payload_json FROM shadow_runs s JOIN events e ON e.seq=s.created_event WHERE s.shadow_run_id=?",
            (document["shadow_run_id"],),
        ).fetchone()
        if not row:
            return False
        event = json.loads(row[0])
        payload = event.get("payload") or {}
        return payload.get("shadow_hash72") == document.get("shadow_hash72")

    def _record_shadow(
        self,
        bundle: Mapping[str, Any],
        plan: Mapping[str, Any],
        report: Mapping[str, Any],
    ) -> dict[str, Any]:
        direct = self._execute_compiled_lanes(bundle, plan)
        status = (
            "MATCH"
            if direct["exact_match"] and direct["witness_match"] and direct["replay_match"]
            else "MISMATCH"
        )
        body = {
            "schema": SHADOW_RUN_SCHEMA,
            "version": VERSION,
            "repair_schema": REPAIR_SCHEMA,
            "contract": CONTRACT,
            "bundle_id": bundle["bundle_id"],
            "program_hash72": plan["program_hash72"],
            "report_hash72": report["report_hash72"],
            "report_state_root_hash72": report["state_root_hash72"],
            "report_replay_root_hash72": report["replay"]["replay_root_hash72"],
            **direct,
            "returned_path": "REFERENCE",
            "candidate_activated": False,
            "candidate_worker_is_authority": False,
            "status": status,
        }
        shadow_run_id = hash72("pass200a.shadow.run.identity.v2", body)
        row = self._db.execute(
            "SELECT payload_json FROM shadow_runs WHERE shadow_run_id=?",
            (shadow_run_id,),
        ).fetchone()
        if row:
            document = json.loads(row[0])
            self._verify_shadow_identity(document)
            if not self._shadow_event_bound(document):
                raise Pass200AError("persisted shadow lacks Hash72 event payload binding")
            return document

        document = {**body, "shadow_run_id": shadow_run_id}
        document["shadow_hash72"] = hash72("pass200a.shadow.run", document)
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "COMPILER_SHADOW_MATCH_RECORDED" if status == "MATCH" else "COMPILER_SHADOW_MISMATCH_RECORDED",
                    {
                        "shadow_run_id": shadow_run_id,
                        "bundle_id": bundle["bundle_id"],
                        "report_hash72": report["report_hash72"],
                        "shadow_hash72": document["shadow_hash72"],
                        "status": status,
                    },
                )
                document["event_hash72"] = event_hash
                self._db.execute(
                    "INSERT INTO shadow_runs(shadow_run_id,bundle_id,report_hash72,status,payload_json,created_event) VALUES(?,?,?,?,?,?)",
                    (
                        shadow_run_id,
                        bundle["bundle_id"],
                        report["report_hash72"],
                        status,
                        canonical_json(document),
                        event_id,
                    ),
                )
                self._db.commit()
                return _copy(document)
            except Exception:
                self._db.rollback()
                raise

    def _shadow_records(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        qualifying: list[dict[str, Any]] = []
        legacy_unbound: list[dict[str, Any]] = []
        rows = self._db.execute(
            "SELECT payload_json FROM shadow_runs ORDER BY rowid"
        )
        for row in rows:
            document = json.loads(row[0])
            self._verify_shadow_identity(document)
            if self._shadow_event_bound(document):
                qualifying.append(document)
            else:
                legacy_unbound.append(document)
        return qualifying, legacy_unbound

    def list_shadow_runs(self) -> list[dict[str, Any]]:
        qualifying, legacy_unbound = self._shadow_records()
        return [*_copy(legacy_unbound), *_copy(qualifying)]

    def _production_acceptance(self, envelopes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        totals = {
            "evaluated_parameter_states": sum(
                int(item.get("summary", {}).get("evaluated_parameter_states", 0))
                for item in envelopes
            ),
            "branch_job_count": sum(
                int(item.get("summary", {}).get("branch_job_count", 0))
                for item in envelopes
            ),
            "admitted_parameter_states": sum(
                int(item.get("summary", {}).get("admitted_parameter_states", 0))
                for item in envelopes
            ),
            "domain_rejected_parameter_states": sum(
                int(item.get("summary", {}).get("domain_rejected_parameter_states", 0))
                for item in envelopes
            ),
            "address_comparisons": sum(
                int(item.get("summary", {}).get("address_comparisons", 0))
                for item in envelopes
            ),
            "negative_mutation_count": sum(
                len(item.get("negative_mutations", [])) for item in envelopes
            ),
        }
        exact_holdout_ids = [item.get("envelope_id") for item in envelopes] == [
            item["envelope_id"] for item in DEFAULT_HOLDOUTS
        ]
        totals_match = totals == PRODUCTION_TOTALS
        return {
            "production_profile": self.production_profile,
            "exact_holdout_ids": exact_holdout_ids,
            "totals": totals,
            "expected_totals": dict(PRODUCTION_TOTALS),
            "totals_match": totals_match,
            "production_holdout_closed": bool(
                self.production_profile
                and exact_holdout_ids
                and totals_match
                and len(envelopes) == 4
            ),
        }

    def run_holdouts(
        self,
        *,
        worker_count: int = 8,
        vm81_receipt_hash72: str | None,
    ) -> dict[str, Any]:
        receipt, provenance = self._receipt(vm81_receipt_hash72)
        for envelope in self.holdouts:
            envelope_id = str(envelope["envelope_id"])
            if self._existing_envelope(envelope_id):
                continue
            config = self._config(envelope)
            report = self.distributed.run(
                OPERATION_ID,
                config,
                worker_count=worker_count,
                vm81_receipt_hash72=receipt,
                resume=True,
                full_replay=True,
            )
            self._validate_closed_report(report)
            tree = self.distributed.pass198.parameter_tree(OPERATION_ID, config)
            self._record_envelope(envelope, tree, report)

        envelopes = self.list_envelopes()
        self._assert_independence(envelopes, require_complete=True)
        evidence_run_ids = [item["pass198_run_id"] for item in envelopes]
        proofs = self.distributed.pass198.list_simplifications(OPERATION_ID)
        if len(proofs) != 4:
            raise Pass200AError("Pass 200A requires exactly four registered simplifications")
        promoted: list[dict[str, Any]] = []
        bundles: list[dict[str, Any]] = []
        for proof in proofs:
            promoted_proof = self._promote_proof(proof, evidence_run_ids, receipt)
            promoted.append(promoted_proof)
            bundles.append(self._record_bundle(promoted_proof, envelopes))

        acceptance = self._production_acceptance(envelopes)
        production_closed = acceptance["production_holdout_closed"] and len(bundles) == 4
        result = {
            "schema": "HHS_PASS_200A_HOLDOUT_QUALIFICATION_V2",
            "version": VERSION,
            "parent_version": V1_VERSION,
            "repair_schema": REPAIR_SCHEMA,
            "contract": CONTRACT,
            "classification": CLASSIFICATION if production_closed else NONPRODUCTION_CLASSIFICATION,
            "closed": production_closed,
            "profile_closed": len(envelopes) >= 4 and len(bundles) == 4,
            "production_closed": production_closed,
            "operation_id": OPERATION_ID,
            "independent_envelope_count": len(envelopes),
            "bundle_count": len(bundles),
            "compiler_candidate_count": sum(item["status"] == "COMPILER_CANDIDATE" for item in bundles),
            "automatic_promotion_count": 0,
            "compiler_mode": "SHADOW",
            "reference_result_remains_authoritative": True,
            "candidate_execution_is_authority": False,
            "vm81_receipt_provenance": provenance,
            "production_acceptance": acceptance,
            "envelopes": envelopes,
            "bundles": bundles,
            "promoted_proof_hash72s": [item["proof_hash72"] for item in promoted],
        }
        result["qualification_hash72"] = hash72("pass200a.holdout.qualification.v2", result)
        return result

    def execute_all_shadows(
        self,
        *,
        worker_count: int = 8,
        vm81_receipt_hash72: str | None,
        config_payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        receipt, provenance = self._receipt(vm81_receipt_hash72)
        bundles = self.list_bundles()
        if len(bundles) != 4:
            raise Pass200AError("four immutable bundles are required before shadow execution")
        config = _copy(dict(config_payload or DEFAULT_SHADOW_CONFIG))
        report = self.distributed.run(
            OPERATION_ID,
            config,
            worker_count=worker_count,
            vm81_receipt_hash72=receipt,
            resume=True,
            full_replay=True,
        )
        self._validate_closed_report(report)
        records = []
        for bundle in bundles:
            plan = self.compile_shadow_plan(bundle["bundle_id"], config)
            records.append(self._record_shadow(bundle, plan, report))

        profile_closed = all(item["status"] == "MATCH" for item in records)
        acceptance = self._production_acceptance(self.list_envelopes())
        production_closed = bool(
            acceptance["production_holdout_closed"]
            and profile_closed
            and len(records) == 4
            and all(item.get("candidate_lane_executed") is True for item in records)
            and not any(item.get("candidate_activated") for item in records)
        )
        result = {
            "schema": "HHS_PASS_200A_ALL_SHADOWS_V2",
            "version": VERSION,
            "parent_version": V1_VERSION,
            "repair_schema": REPAIR_SCHEMA,
            "contract": CONTRACT,
            "classification": REPAIR_CLASSIFICATION if production_closed else NONPRODUCTION_CLASSIFICATION,
            "closed": production_closed,
            "profile_closed": profile_closed,
            "production_closed": production_closed,
            "compiler_mode": "SHADOW",
            "bundle_count": len(bundles),
            "shadow_match_count": sum(item["status"] == "MATCH" for item in records),
            "reference_return_count": sum(item["returned_path"] == "REFERENCE" for item in records),
            "candidate_activation_count": sum(bool(item["candidate_activated"]) for item in records),
            "candidate_execution_count": sum(bool(item.get("candidate_lane_executed")) for item in records),
            "report_hash72": report["report_hash72"],
            "state_root_hash72": report["state_root_hash72"],
            "vm81_receipt_provenance": provenance,
            "production_acceptance": acceptance,
            "records": records,
        }
        result["shadow_suite_hash72"] = hash72("pass200a.shadow.suite.v2", result)
        return result

    def verify(self) -> dict[str, Any]:
        envelopes = self.list_envelopes()
        if envelopes:
            self._assert_independence(envelopes, require_complete=False)
        bundles = self.list_bundles()
        qualifying, legacy_unbound = self._shadow_records()
        event_chain = self.verify_event_chain()
        if not event_chain["ok"]:
            raise Pass200AError("Pass 200A event chain is invalid")
        if any(item["compiler_mode"] != "SHADOW" for item in bundles):
            raise Pass200AError("non-shadow compiler mode detected")
        if any(item.get("candidate_activated") for item in [*qualifying, *legacy_unbound]):
            raise Pass200AError("candidate activation is forbidden in Pass 200A")
        if any(
            item.get("status") == "MATCH"
            and not (
                item.get("exact_match") is True
                and item.get("witness_match") is True
                and item.get("replay_match") is True
                and item.get("candidate_lane_executed") is True
            )
            for item in qualifying
        ):
            raise Pass200AError("qualifying shadow match lacks exact executed comparison")
        acceptance = self._production_acceptance(envelopes)
        return {
            "schema": "HHS_PASS_200A_VERIFICATION_V2",
            "version": VERSION,
            "parent_version": V1_VERSION,
            "repair_schema": REPAIR_SCHEMA,
            "contract": CONTRACT,
            "ok": True,
            "independent_envelope_count": len(envelopes),
            "bundle_count": len(bundles),
            "shadow_run_count": len(qualifying) + len(legacy_unbound),
            "qualifying_shadow_run_count": len(qualifying),
            "legacy_unbound_shadow_run_count": len(legacy_unbound),
            "shadow_match_count": sum(item["status"] == "MATCH" for item in qualifying),
            "candidate_activation_count": 0,
            "production_acceptance": acceptance,
            "event_chain": event_chain,
            "compiler_auto_activation": False,
            "runtime_auto_admission": False,
            "reference_result_remains_authoritative": True,
            "candidate_execution_is_authority": False,
        }

    def status(self) -> dict[str, Any]:
        verification = self.verify()
        production_closed = bool(
            verification["production_acceptance"]["production_holdout_closed"]
            and verification["bundle_count"] == 4
            and verification["shadow_match_count"] >= 4
            and verification["qualifying_shadow_run_count"] >= 4
        )
        profile_complete = bool(
            verification["independent_envelope_count"] >= 4
            and verification["bundle_count"] == 4
            and verification["shadow_match_count"] >= 4
        )
        result = {
            "schema": "HHS_PASS_200A_STATUS_V2",
            "version": VERSION,
            "parent_version": V1_VERSION,
            "repair_schema": REPAIR_SCHEMA,
            "contract": CONTRACT,
            "classification": (
                REPAIR_CLASSIFICATION
                if production_closed
                else NONPRODUCTION_CLASSIFICATION
                if profile_complete
                else "HHS_PASS_200A_IN_PROGRESS"
            ),
            "closed": production_closed,
            "profile_closed": profile_complete,
            "production_closed": production_closed,
            "compiler_mode": "SHADOW",
            "reference_result_remains_authoritative": True,
            "candidate_execution_is_authority": False,
            "canary_enabled": False,
            "active_enabled": False,
            "frozen_constraint_enabled": False,
            **verification,
        }
        result["status_hash72"] = hash72("pass200a.status.v2", result)
        return result


# Export the V1 singleton only as the object to be upgraded by the canonical
# production wrapper.  Creating a second default-state authority is forbidden.
PASS200A_LEGACY_SINGLETON = PASS200A_V1_SINGLETON

__all__ = [
    "BUNDLE_SCHEMA",
    "CLASSIFICATION",
    "CONTRACT",
    "DEFAULT_HOLDOUTS",
    "DEFAULT_SHADOW_CONFIG",
    "ENVELOPE_SCHEMA",
    "EVENT_SCHEMA",
    "NONPRODUCTION_CLASSIFICATION",
    "OPERATION_ID",
    "PASS200A_LEGACY_SINGLETON",
    "PRODUCTION_TOTALS",
    "REPAIR_CLASSIFICATION",
    "REPAIR_SCHEMA",
    "SHADOW_PLAN_SCHEMA",
    "SHADOW_RUN_SCHEMA",
    "VERSION",
    "Pass200AError",
    "Pass200AProofCarryingOptimizationAuthority",
]
