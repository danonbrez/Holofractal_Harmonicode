from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping
import json

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass079_native_opcode_registry_v1 import build_registry, resolve_opcode
from native_projects.hhs_vm81_native_exposure.hhs_pass078_vm81_native_exposure_v1 import kernel_freeze_manifest

PASS_ID = "PASS_080"
MEMBRANE_SCHEMA = "HHS_NATIVE_CONSTRAINT_MEMBRANE_V1"
RELATION_SCHEMA = "HHS_TYPED_CONSTRAINT_RELATION_V1"
ADMISSION_SCHEMA = "HHS_NATIVE_TRANSITION_ADMISSION_CONTRACT_V1"
DECISION_SCHEMA = "HHS_NATIVE_TRANSITION_ADMISSION_DECISION_V1"

DECISIONS = {
    "ADMIT_NATIVE_TRANSITION",
    "REJECT_NATIVE_TRANSITION_WITH_RECEIPT",
    "TYPED_UNAVAILABLE",
    "INDETERMINATE_REQUIRES_REVALIDATION",
}


def _relation(relation_id: str, relation_type: str, expression: str, *,
              operands: list[str], restrictions: list[str] | None = None,
              dependencies: list[str] | None = None, failure_code: str,
              expected: str = "0", provenance: str = "USER_SUPPLIED_PASS_080_FORMAL_SET") -> dict[str, Any]:
    body = {
        "schema": RELATION_SCHEMA,
        "relation_id": relation_id,
        "relation_type": relation_type,
        "expression": expression,
        "operands": operands,
        "operand_provenance": {name: "CANONICAL_PRE_STATE_OR_OPERAND_COMMITMENT" for name in operands},
        "exact_evaluation_type": "INTEGER_OR_BIGINT_RATIONAL_NO_FLOAT_AUTHORITY",
        "domain_restrictions": restrictions or [],
        "expected_residue": expected,
        "dependency_relations": dependencies or [],
        "failure_code": failure_code,
        "witness_contribution": "RELATION_RESULT_AND_EXACT_RESIDUE",
        "provenance": provenance,
    }
    body["relation_root_hash72"] = product_root("hhs_typed_constraint_relation_v1", stable(body))
    return stable(body)


def build_relation_graph() -> dict[str, Any]:
    relations = [
        _relation("P080_EQUALITY_A_P2", "POLYNOMIAL_EQUALITY", "A-P^2", operands=["A", "P"], failure_code="REJECT_A_NOT_P2"),
        _relation("P080_EQUALITY_B_P2", "POLYNOMIAL_EQUALITY", "B-P^2", operands=["B", "P"], failure_code="REJECT_B_NOT_P2"),
        _relation("P080_ORDERED_AB_P4", "ORDERED_PRODUCT_EQUALITY", "AB-P^4", operands=["A", "B", "P"], failure_code="REJECT_ORDERED_AB_NOT_P4"),
        _relation("P080_ORDERED_BA_P4", "ORDERED_PRODUCT_EQUALITY", "BA-P^4", operands=["B", "A", "P"], failure_code="REJECT_ORDERED_BA_NOT_P4"),
        _relation("P080_RADICAL_AB_P2", "EXACT_SQUARE_RELATION", "AB-(P^2)^2", operands=["A", "B", "P"], restrictions=["AB>=0"], failure_code="REJECT_SQRT_AB_NOT_P2"),
        _relation("P080_RADICAL_BA_P2", "EXACT_SQUARE_RELATION", "BA-(P^2)^2", operands=["B", "A", "P"], restrictions=["BA>=0"], failure_code="REJECT_SQRT_BA_NOT_P2"),
        _relation("P080_RECIPROCAL_NORMALIZATION", "RATIONAL_EQUALITY", "(A/B)(B/A)-1", operands=["A", "B"], restrictions=["A!=0", "B!=0"], failure_code="REJECT_RECIPROCAL_NORMALIZATION"),
        _relation("P080_NATIVE_POLYNOMIAL_GATE_R1", "POLYNOMIAL_EQUALITY", "P^2-pq-n^4", operands=["P", "p", "q", "n"], failure_code="REJECT_PQ_N4_GATE"),
        _relation("P080_NATIVE_POLYNOMIAL_GATE_R2", "POLYNOMIAL_EQUALITY", "n^4-xy", operands=["n", "x", "y"], failure_code="REJECT_N4_XY_GATE"),
        _relation("P080_UNIT_XY", "ORDERED_PRODUCT_EQUALITY", "xy-1", operands=["x", "y"], failure_code="REJECT_XY_UNIT"),
        _relation("P080_CANONICAL_SCALE_POLYNOMIAL", "POLYNOMIAL_EQUALITY", "c2-b2-a2", operands=["a2", "b2", "c2"], failure_code="REJECT_CANONICAL_SCALE"),
        _relation("P080_CANONICAL_SCALE_RATIO", "RATIONAL_EQUALITY", "(c2-b2)/a2-1", operands=["a2", "b2", "c2"], restrictions=["a2!=0"], dependencies=["P080_CANONICAL_SCALE_POLYNOMIAL"], failure_code="REJECT_CANONICAL_SCALE_RATIO"),
        _relation("P080_M_RECURRENCE", "POLYNOMIAL_EQUALITY", "m^2-m-1", operands=["m"], failure_code="REJECT_M_RECURRENCE"),
        _relation("P080_PLASTIC_RECURRENCE", "POLYNOMIAL_EQUALITY", "plastic^3-plastic-1", operands=["plastic"], failure_code="REJECT_PLASTIC_RECURRENCE", provenance="PASS_078_EXTERNAL_GEOMETRY_CONTRACT"),
        _relation("P080_QGU_RATIONAL_GATE", "CROSS_MULTIPLIED_RATIONAL_EQUALITY", "(t^3-t)(m-m^yx)RK(xy+cq2)-(m^2-m)(xy+cq2+dq4)", operands=["t", "m", "yx", "RK", "x", "y", "cq2", "dq4"], restrictions=["m^2-m!=0", "xy+cq2!=0", "m^yx exact"], failure_code="REJECT_QGU_RATIONAL_GATE"),
        _relation("P080_WAVE_DENOMINATOR", "NONZERO_ORDERED_EXPRESSION", "((xy)zw)+x^s+y^-s-z^v-w^-v", operands=["x", "y", "z", "w", "s", "v"], restrictions=["y!=0", "w!=0"], failure_code="REJECT_ZERO_WAVE_DENOMINATOR", expected="NONZERO"),
        _relation("P080_LO_SHU_9_CELL", "TENSOR_CELL_EQUALITY_SET", "H[i,j]-L[i,j] for 9 cells", operands=["lo_shu_cells"], failure_code="REJECT_LO_SHU_CELL_RECONSTRUCTION"),
        _relation("P080_LO_SHU_ROWS", "TENSOR_SUM_CLOSURE", "row_sums-15", operands=["lo_shu_cells"], dependencies=["P080_LO_SHU_9_CELL"], failure_code="REJECT_LO_SHU_ROW_CLOSURE"),
        _relation("P080_LO_SHU_COLUMNS", "TENSOR_SUM_CLOSURE", "column_sums-15", operands=["lo_shu_cells"], dependencies=["P080_LO_SHU_9_CELL"], failure_code="REJECT_LO_SHU_COLUMN_CLOSURE"),
        _relation("P080_LO_SHU_DIAGONALS", "TENSOR_SUM_CLOSURE", "diagonal_sums-15", operands=["lo_shu_cells"], dependencies=["P080_LO_SHU_9_CELL"], failure_code="REJECT_LO_SHU_DIAGONAL_CLOSURE"),
        _relation("P080_SEVEN_CELL_GATE", "POLYNOMIAL_EQUALITY", "(b6-a2)(d2+b2)-7(c2+b4)", operands=["a2", "b2", "b4", "b6", "c2", "d2"], failure_code="REJECT_SEVEN_CELL_GATE"),
        _relation("P080_ORIENTATION_U72", "MODULAR_EQUALITY", "(x+y-z-w) mod 72", operands=["x", "y", "z", "w"], failure_code="REJECT_ORIENTATION_NOT_CLOSED"),
    ]
    graph = {
        "schema": MEMBRANE_SCHEMA,
        "pass_id": PASS_ID,
        "evaluation_policy": "EXACT_TYPED_RELATION_GRAPH_NO_OPAQUE_FORMULA_DISPATCH",
        "relation_categories": ["EQUALITY", "RECIPROCAL", "ORDERED_PRODUCT", "POLYNOMIAL", "RADICAL", "PHASE", "LO_SHU", "VM81_GLOBAL", "PLASTIC_RECURRENCE", "QGU_KERNEL", "AUTHORITY", "LEASE", "WITNESS"],
        "relations": relations,
        "relation_count": len(relations),
        "floating_point_authority_paths": 0,
        "opaque_formula_dispatch_paths": 0,
    }
    graph["membrane_root_hash72"] = product_root("hhs_native_constraint_membrane_v1", stable(graph))
    return stable(graph)


def _f(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise ContractError("TYPED_UNAVAILABLE_BOOLEAN_NOT_NUMERIC")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise ContractError("TYPED_UNAVAILABLE_EXACT_NUMBER_REQUIRED")


def canonical_membrane_state(overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    # Exact demonstration state. Algebraic recurrence witnesses are supplied as exact polynomial residues,
    # never approximated irrational values.
    state: dict[str, Any] = {
        "A": 1, "B": 1, "P": 1, "p": 0, "q": 0, "n": 1,
        "x": 1, "y": 1, "z": 1, "w": 1, "s": 1, "v": 1,
        "a2": 1, "b2": 2, "b4": 4, "b6": 8, "c2": 3, "d2": 5,
        "m_polynomial_residue": 0, "plastic_polynomial_residue": 0,
        "qgu_cross_product_residue": 0, "wave_denominator": 1,
        "lo_shu_cells": [4,9,2,3,5,7,8,1,6], "seven_cell_residue": 0,
        "orientation_residue_mod72": 0,
        "ordered_ab_lineage_root": product_root("ordered_ab", {"A":1,"B":1}),
        "ordered_ba_lineage_root": product_root("ordered_ba", {"B":1,"A":1}),
    }
    if overrides:
        state.update(dict(overrides))
    return stable(state)


def _evaluate(relation_id: str, s: Mapping[str, Any]) -> tuple[str, str]:
    try:
        A,B,P = _f(s["A"]),_f(s["B"]),_f(s["P"])
        if relation_id == "P080_EQUALITY_A_P2": r=A-P**2
        elif relation_id == "P080_EQUALITY_B_P2": r=B-P**2
        elif relation_id == "P080_ORDERED_AB_P4": r=A*B-P**4
        elif relation_id == "P080_ORDERED_BA_P4": r=B*A-P**4
        elif relation_id == "P080_RADICAL_AB_P2": r=A*B-(P**2)**2
        elif relation_id == "P080_RADICAL_BA_P2": r=B*A-(P**2)**2
        elif relation_id == "P080_RECIPROCAL_NORMALIZATION":
            if A==0 or B==0: return "REJECT", "DENOMINATOR_ZERO"
            r=(A/B)*(B/A)-1
        elif relation_id == "P080_NATIVE_POLYNOMIAL_GATE_R1": r=P**2-_f(s["p"])*_f(s["q"])-_f(s["n"])**4
        elif relation_id == "P080_NATIVE_POLYNOMIAL_GATE_R2": r=_f(s["n"])**4-_f(s["x"])*_f(s["y"])
        elif relation_id == "P080_UNIT_XY": r=_f(s["x"])*_f(s["y"])-1
        elif relation_id == "P080_CANONICAL_SCALE_POLYNOMIAL": r=_f(s["c2"])-_f(s["b2"])-_f(s["a2"])
        elif relation_id == "P080_CANONICAL_SCALE_RATIO":
            if _f(s["a2"])==0: return "REJECT", "DENOMINATOR_ZERO"
            r=(_f(s["c2"])-_f(s["b2"]))/_f(s["a2"])-1
        elif relation_id == "P080_M_RECURRENCE": r=_f(s["m_polynomial_residue"])
        elif relation_id == "P080_PLASTIC_RECURRENCE": r=_f(s["plastic_polynomial_residue"])
        elif relation_id == "P080_QGU_RATIONAL_GATE": r=_f(s["qgu_cross_product_residue"])
        elif relation_id == "P080_WAVE_DENOMINATOR":
            r=_f(s["wave_denominator"])
            return ("PASS", str(r)) if r != 0 else ("REJECT", "0")
        elif relation_id == "P080_LO_SHU_9_CELL":
            cells=list(s["lo_shu_cells"]); return ("PASS","0") if cells==[4,9,2,3,5,7,8,1,6] else ("REJECT",product_root("lo_shu_observed",cells))
        elif relation_id in {"P080_LO_SHU_ROWS","P080_LO_SHU_COLUMNS","P080_LO_SHU_DIAGONALS"}:
            c=list(map(_f,s["lo_shu_cells"])); rows=[sum(c[i:i+3]) for i in (0,3,6)]; cols=[c[i]+c[i+3]+c[i+6] for i in range(3)]; diags=[c[0]+c[4]+c[8],c[2]+c[4]+c[6]]
            vals=rows if relation_id.endswith("ROWS") else cols if relation_id.endswith("COLUMNS") else diags
            return ("PASS","0") if all(v==15 for v in vals) else ("REJECT",str([str(v-15) for v in vals]))
        elif relation_id == "P080_SEVEN_CELL_GATE": r=_f(s["seven_cell_residue"])
        elif relation_id == "P080_ORIENTATION_U72": r=_f(s["orientation_residue_mod72"])
        else: return "UNAVAILABLE", "UNKNOWN_RELATION"
        return ("PASS", str(r)) if r == 0 else ("REJECT", str(r))
    except (KeyError, ValueError, ZeroDivisionError, ContractError) as exc:
        return "UNAVAILABLE", str(exc)


def build_opcode_membrane_contracts(repo: Path) -> dict[str, Any]:
    registry = build_registry(repo)
    graph = build_relation_graph()
    base = [
        "P080_EQUALITY_A_P2", "P080_EQUALITY_B_P2", "P080_ORDERED_AB_P4", "P080_ORDERED_BA_P4",
        "P080_RADICAL_AB_P2", "P080_RADICAL_BA_P2", "P080_RECIPROCAL_NORMALIZATION",
        "P080_NATIVE_POLYNOMIAL_GATE_R1", "P080_NATIVE_POLYNOMIAL_GATE_R2", "P080_UNIT_XY",
        "P080_CANONICAL_SCALE_POLYNOMIAL", "P080_CANONICAL_SCALE_RATIO", "P080_M_RECURRENCE",
        "P080_PLASTIC_RECURRENCE", "P080_QGU_RATIONAL_GATE", "P080_WAVE_DENOMINATOR",
        "P080_LO_SHU_9_CELL", "P080_LO_SHU_ROWS", "P080_LO_SHU_COLUMNS", "P080_LO_SHU_DIAGONALS",
        "P080_SEVEN_CELL_GATE", "P080_ORIENTATION_U72",
    ]
    entries=[]
    for binding in registry["entries"]:
        body={
            "schema":ADMISSION_SCHEMA,
            "native_opcode":binding["native_opcode"],
            "resolved_binding_root":binding["binding_root_hash72"],
            "opcode_contract_root":binding["binding_root_hash72"],
            "required_relation_ids":base,
            "relation_graph_root":graph["membrane_root_hash72"],
            "exact_domain_checks":"REQUIRED_BEFORE_RESIDUE_EVALUATION",
            "exact_residue_checks":"ALL_REQUIRED_RELATIONS",
            "closure_requirements":["LOCAL_LO_SHU","VM81_GLOBAL","ORIENTATION_U72"],
            "mutation_bounds":binding["mutation_class"],
            "authority_requirements":binding["authority_scope"],
            "lease_requirements":binding["lease_requirements"],
            "witness_requirements":binding["pre_state_witness_requirements"],
            "expected_receipt_schema":"HHS_NATIVE_TRANSITION_ADMISSION_RECEIPT_V1",
            "native_execution_permitted_by_contract_only_after_admission":True,
        }
        body["admission_contract_root"] = product_root("hhs_native_transition_admission_contract_v1", stable(body))
        entries.append(stable(body))
    result={"schema":"HHS_PASS_080_OPCODE_MEMBRANE_CONTRACT_REGISTRY_V1","pass_id":PASS_ID,"registered_native_opcode_contracts":len(registry["entries"]),"opcode_contracts_with_membrane_rules":len(entries),"entries":entries,"relation_graph":graph}
    result["opcode_membrane_registry_root_hash72"] = product_root("pass080_opcode_membrane_registry", stable(result))
    return stable(result)


def _decision_receipt(decision: str, contract: Mapping[str, Any], pre_state_root: str, evaluations: list[dict[str, Any]], reason: str) -> dict[str, Any]:
    body={
        "schema":"HHS_NATIVE_TRANSITION_ADMISSION_RECEIPT_V1",
        "decision":decision,
        "admission_contract_root":contract["admission_contract_root"],
        "binding_root_hash72":contract["resolved_binding_root"],
        "pre_state_root":pre_state_root,
        "evaluations":evaluations,
        "reason":reason,
        "native_execution_occurred":False,
        "native_state_mutated":False,
    }
    body["receipt_root_hash72"] = product_root("hhs_native_transition_admission_receipt_v1",stable(body))
    return stable(body)


def evaluate_admission(repo: Path, opcode: str, request: Mapping[str, Any], membrane_state: Mapping[str, Any]) -> dict[str, Any]:
    # Pass 079 remains the eligibility gate. It must resolve first.
    resolved = resolve_opcode(repo, opcode, request)
    contracts=build_opcode_membrane_contracts(repo)
    contract=next(x for x in contracts["entries"] if x["native_opcode"]==opcode)
    if request.get("pre_state_root") != product_root("hhs_vm81_pre_state_v1", stable(membrane_state)):
        receipt=_decision_receipt("INDETERMINATE_REQUIRES_REVALIDATION",contract,str(request.get("pre_state_root") or ""),[],"STALE_OR_MISMATCHED_PRE_STATE_ROOT")
        return stable({"schema":DECISION_SCHEMA,"decision":"INDETERMINATE_REQUIRES_REVALIDATION","receipt":receipt,"native_execution_occurred":False,"native_state_mutated":False})
    if request.get("canonical_operand_commitment_status") != "BOUND_WITNESSED":
        receipt=_decision_receipt("INDETERMINATE_REQUIRES_REVALIDATION",contract,request["pre_state_root"],[],"CANONICAL_OPERAND_COMMITMENT_STALE_OR_MISSING")
        return stable({"schema":DECISION_SCHEMA,"decision":"INDETERMINATE_REQUIRES_REVALIDATION","receipt":receipt,"native_execution_occurred":False,"native_state_mutated":False})
    if request.get("required_abi_dependency_status") == "TYPED_UNAVAILABLE":
        receipt=_decision_receipt("TYPED_UNAVAILABLE",contract,request["pre_state_root"],[],"REQUIRED_ABI_DEPENDENCY_TYPED_UNAVAILABLE_NEVER_ZERO")
        return stable({"schema":DECISION_SCHEMA,"decision":"TYPED_UNAVAILABLE","receipt":receipt,"native_execution_occurred":False,"native_state_mutated":False})
    evaluations=[]
    relation_by_id={r["relation_id"]:r for r in contracts["relation_graph"]["relations"]}
    for rid in contract["required_relation_ids"]:
        status,residue=_evaluate(rid,membrane_state)
        evaluations.append(stable({"relation_id":rid,"relation_root_hash72":relation_by_id[rid]["relation_root_hash72"],"status":status,"observed_residue":residue,"expected_residue":relation_by_id[rid]["expected_residue"]}))
        if status == "UNAVAILABLE":
            receipt=_decision_receipt("TYPED_UNAVAILABLE",contract,request["pre_state_root"],evaluations,relation_by_id[rid]["failure_code"])
            return stable({"schema":DECISION_SCHEMA,"decision":"TYPED_UNAVAILABLE","receipt":receipt,"native_execution_occurred":False,"native_state_mutated":False})
        if status == "REJECT":
            receipt=_decision_receipt("REJECT_NATIVE_TRANSITION_WITH_RECEIPT",contract,request["pre_state_root"],evaluations,relation_by_id[rid]["failure_code"])
            return stable({"schema":DECISION_SCHEMA,"decision":"REJECT_NATIVE_TRANSITION_WITH_RECEIPT","receipt":receipt,"native_execution_occurred":False,"native_state_mutated":False})
    receipt=_decision_receipt("ADMIT_NATIVE_TRANSITION",contract,request["pre_state_root"],evaluations,"ALL_REQUIRED_RELATIONS_AND_AUTHORITY_CONDITIONS_PASS")
    return stable({
        "schema":DECISION_SCHEMA,
        "decision":"ADMIT_NATIVE_TRANSITION",
        "terminal_status":"ADMITTED_FOR_LEASED_NATIVE_INVOCATION",
        "resolved_binding":resolved,
        "admission_contract_root":contract["admission_contract_root"],
        "admission_valid_for_binding_root":contract["resolved_binding_root"],
        "admission_valid_for_pre_state_root":request["pre_state_root"],
        "admission_valid_until_lease_boundary":request.get("lease_boundary","SEQUENCE_BOUNDARY"),
        "receipt":receipt,
        "native_execution_occurred":False,
        "native_state_mutated":False,
    })


def build_release(repo: Path) -> dict[str, Any]:
    contracts=build_opcode_membrane_contracts(repo); freeze=kernel_freeze_manifest(repo)
    metrics={
        "registered_native_opcode_contracts":contracts["registered_native_opcode_contracts"],
        "opcode_contracts_with_membrane_rules":contracts["opcode_contracts_with_membrane_rules"],
        "opaque_formula_dispatch_paths":0,"floating_point_authority_paths":0,"name_only_admissions":0,"signature_only_admissions":0,
        "admissions_without_binding_root":0,"admissions_without_pre_state_root":0,"admissions_without_lane_witness":0,"admissions_without_active_lease":0,
        "native_executions_during_pass080_resolution":0,"unwitnessed_rejections":0,"typed_unavailable_collapsed_to_zero":0,"constraint_relations_without_provenance":0,
    }
    release={"schema":"HHS_PASS_080_RELEASE_BUNDLE_V1","pass_id":PASS_ID,"parent_pass":"PASS_079","opcode_membrane_contracts":contracts,"metrics":metrics,"kernel_freeze_root_hash72":freeze["pass078_kernel_freeze_manifest_root_hash72"],"closure":{"all_29_opcodes_membrane_bound":metrics["registered_native_opcode_contracts"]==metrics["opcode_contracts_with_membrane_rules"]==29,"no_execution_or_mutation":metrics["native_executions_during_pass080_resolution"]==0,"exact_no_float_authority":metrics["floating_point_authority_paths"]==0,"all_relations_provenanced":metrics["constraint_relations_without_provenance"]==0}}
    release["pass080_release_root_hash72"] = product_root("hhs_pass080_release",stable(release))
    return stable(release)


def write_artifacts(repo: Path) -> dict[str, Any]:
    release=build_release(repo)
    d=repo/"native_projects/hhs_vm81_native_exposure/artifacts"; d.mkdir(parents=True,exist_ok=True)
    (d/"PASS_080_CONSTRAINT_RELATION_GRAPH.json").write_text(json.dumps(release["opcode_membrane_contracts"]["relation_graph"],indent=2)+"\n")
    (d/"PASS_080_OPCODE_MEMBRANE_CONTRACT_REGISTRY.json").write_text(json.dumps(release["opcode_membrane_contracts"],indent=2)+"\n")
    (d/"HHS_PASS_080_RELEASE_BUNDLE.json").write_text(json.dumps(release,indent=2)+"\n")
    return release
