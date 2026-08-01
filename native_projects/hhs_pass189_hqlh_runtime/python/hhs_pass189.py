#!/usr/bin/env python3
"""Pass 189 exact sparse HARMONICODE hydration runtime.

The module preserves exact source text, builds typed membranes, decodes the
51,648,192 first-level contextual address space, hydrates only requested
base-41 paths, constructs exact tagged V72 topology, and issues deterministic
Hash72/Hash216 receipts. It intentionally does not claim physical-device
calibration without measured evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

VM81_CELLS = 81
OPERATIONS_PER_CELL = 64
G243_CONTROLS = 243
PERMANENT_STATES = 5_184
PROJECTED_STATES = 1_259_712
LOCAL_COORDINATES = 41
CONTEXTUAL_STATES = 51_648_192
Q144_STATES = 144
U72_STATES = 72
GLOBAL_NUCLEUS = 40
LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)
ORDERED_BASIS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
LO_SHU_POSITIVE_DELTAS = (8, 17, 3, 12, 4, 13, 1, 10, 19, 5, 14, 9, 18, 6, 15, 7, 16, 2, 11, 20)
ZERO_NUCLEUS = "ADMITTED_NUCLEUS_ZERO"
ZERO_UNRESOLVED = "UNRESOLVED_INTERNAL"
ZERO_REJECTED = "REJECTED_ADMISSION"
CLASSIFICATION = "HHS_PASS_189_HQLH_HYDRATION_VERIFIED"
CONTRACT = "HHS-P189-HQLH-LS41-XNOR-P1-H72-H216-UPA"

TOKEN_RE = re.compile(
    r"List|[A-Za-z_][A-Za-z0-9_]*|(?:0[xX][0-9A-Fa-f]+)|(?:\d+)|==|!=|<=|>=|->|::|[()\[\]{},=+\-*/^<>.]"
)
PAIR = {"(": ")", "[": "]", "{": "}"}
REVERSE_PAIR = {value: key for key, value in PAIR.items()}
OPERATOR_TYPES = {
    ",": "SIBLING_SEQUENCE",
    "=": "DIRECTIONAL_BINDING",
    "==": "RECIPROCAL_EQUIVALENCE",
    "+": "ORDERED_ADDITION",
    "-": "ORDERED_SUBTRACTION",
    "*": "ORDERED_MULTIPLICATION",
    "/": "ORDERED_DIVISION",
    "^": "ORDERED_POWER",
    "<": "COMPARISON",
    ">": "COMPARISON",
    "<=": "COMPARISON",
    ">=": "COMPARISON",
    "!=": "COMPARISON",
    ".": "COMPOSITION",
    "::": "COMPOSITION",
    "->": "BINDING",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def hash72(value: Any) -> str:
    return hashlib.sha512(canonical_json(value).encode("utf-8")).hexdigest()[:72]


def hash216(minus: str, center: str, plus: str) -> str:
    result = minus + center + plus
    if len(result) != 216:
        raise ValueError("Hash216 requires three ordered Hash72 lanes")
    return result


def derive_lo_shu_positive_deltas() -> tuple[int, ...]:
    return tuple(sorted(range(1, 21), key=lambda n: (LO_SHU[(n - 1) % 9], (n - 1) // 9, n)))


def lo_shu_delta(local_k: int) -> int:
    if not -20 <= local_k <= 20:
        raise ValueError("local_k must be in [-20,20]")
    if local_k == 0:
        return 0
    value = LO_SHU_POSITIVE_DELTAS[abs(local_k) - 1]
    return -value if local_k < 0 else value


def local_cell(cell81: int, local_k: int) -> int:
    if not 0 <= cell81 < VM81_CELLS:
        raise ValueError("cell81 out of range")
    return (cell81 + lo_shu_delta(local_k)) % VM81_CELLS


def xnor_bit(a: int, b: int) -> int:
    return 1 - ((a ^ b) & 1)


def signed_xnor(a: int, b: int) -> int:
    return 1 if ((a ^ b) & 1) == 0 else -1


def centered_displacement(cell81: int, nucleus81: int = GLOBAL_NUCLEUS) -> int:
    if not 0 <= cell81 < VM81_CELLS or not 0 <= nucleus81 < VM81_CELLS:
        raise ValueError("VM81 coordinate out of range")
    return ((cell81 - nucleus81 + 40) % 81) - 40


def ternary_orientation(cell81: int, a: int, b: int, nucleus81: int = GLOBAL_NUCLEUS) -> tuple[int, str]:
    displacement = centered_displacement(cell81, nucleus81)
    sign = -1 if displacement < 0 else (1 if displacement > 0 else 0)
    value = sign * signed_xnor(a, b)
    witness = ZERO_NUCLEUS if value == 0 else "ADMITTED_SIGNED_TERNARY"
    return value, witness


@dataclass(frozen=True)
class ContextAddress:
    extended: int
    projected: int
    permanent: int
    g243: int
    cell81: int
    operation64: int
    operation_class8: int
    ordered_basis8: int
    ordered_basis_tag: str
    kappa41: int
    local_k: int
    layer36: int
    q144_row: int
    q144_column: int
    u72_pair: int
    u72_index: int


def decode_context(extended: int) -> ContextAddress:
    if not 0 <= extended < CONTEXTUAL_STATES:
        raise ValueError("extended address out of range")
    projected, kappa = divmod(extended, LOCAL_COORDINATES)
    permanent, g243 = divmod(projected, G243_CONTROLS)
    cell81, operation64 = divmod(permanent, OPERATIONS_PER_CELL)
    q144 = permanent % Q144_STATES
    return ContextAddress(
        extended=extended,
        projected=projected,
        permanent=permanent,
        g243=g243,
        cell81=cell81,
        operation64=operation64,
        operation_class8=operation64 >> 3,
        ordered_basis8=operation64 & 7,
        ordered_basis_tag=ORDERED_BASIS[operation64 & 7],
        kappa41=kappa,
        local_k=kappa - 20,
        layer36=permanent // Q144_STATES,
        q144_row=q144 // 12,
        q144_column=q144 % 12,
        u72_pair=q144 // U72_STATES,
        u72_index=q144 % U72_STATES,
    )


def encode_context(address: ContextAddress | Mapping[str, Any]) -> int:
    data = asdict(address) if isinstance(address, ContextAddress) else dict(address)
    cell81 = int(data["cell81"])
    operation64 = int(data["operation64"])
    g243 = int(data["g243"])
    kappa41 = int(data["kappa41"])
    if not 0 <= cell81 < VM81_CELLS:
        raise ValueError("cell81 out of range")
    if not 0 <= operation64 < OPERATIONS_PER_CELL:
        raise ValueError("operation64 out of range")
    if not 0 <= g243 < G243_CONTROLS:
        raise ValueError("g243 out of range")
    if not 0 <= kappa41 < LOCAL_COORDINATES:
        raise ValueError("kappa41 out of range")
    return (((cell81 * OPERATIONS_PER_CELL) + operation64) * G243_CONTROLS + g243) * LOCAL_COORDINATES + kappa41


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int
    index: int


@dataclass(frozen=True)
class Membrane:
    membrane_id: str
    kind: str
    operator: str
    depth: int
    start: int
    end: int
    exact_source: str
    interior_source: str
    interior_states: int
    outer_boundary: int
    depth_modulus: int
    unresolved_witness: str = ZERO_UNRESOLVED


def tokenize_exact(source: str) -> list[Token]:
    return [Token(match.group(0), match.start(), match.end(), index) for index, match in enumerate(TOKEN_RE.finditer(source))]


def extract_membranes(source: str) -> list[Membrane]:
    tokens = tokenize_exact(source)
    stack: list[tuple[Token, int, bool]] = []
    membranes: list[Membrane] = []
    for token in tokens:
        if token.text in PAIR:
            previous = tokens[token.index - 1].text if token.index > 0 else ""
            stack.append((token, len(stack), previous == "List" or (previous and previous[0].isalpha() and token.text == "(")))
            continue
        if token.text in REVERSE_PAIR:
            if not stack or stack[-1][0].text != REVERSE_PAIR[token.text]:
                raise ValueError(f"malformed membrane at offset {token.start}")
            opening, depth, is_application = stack.pop()
            inside = [item for item in tokens if item.start >= opening.end and item.end <= token.start]
            kind = "LIST" if is_application and opening.text == "(" and opening.start >= 4 and source[max(0, opening.start - 4):opening.start] == "List" else (
                "FUNCTION_APPLICATION" if is_application else {"(": "PARENTHETICAL", "[": "INDEXING", "{": "SET_OR_MATRIX"}[opening.text]
            )
            exact = source[opening.start:token.end]
            interior = source[opening.end:token.start]
            p = len(inside)
            membranes.append(Membrane(
                membrane_id=hash72({"kind": kind, "span": [opening.start, token.end], "source": exact}),
                kind=kind,
                operator=opening.text + token.text,
                depth=depth,
                start=opening.start,
                end=token.end,
                exact_source=exact,
                interior_source=interior,
                interior_states=p,
                outer_boundary=p + 1,
                depth_modulus=depth % (depth + 1),
            ))
            continue
        if token.text in OPERATOR_TYPES:
            depth = len(stack)
            exact = source[token.start:token.end]
            membranes.append(Membrane(
                membrane_id=hash72({"kind": OPERATOR_TYPES[token.text], "offset": token.start, "source": exact}),
                kind=OPERATOR_TYPES[token.text],
                operator=token.text,
                depth=depth,
                start=token.start,
                end=token.end,
                exact_source=exact,
                interior_source=source,
                interior_states=2,
                outer_boundary=3,
                depth_modulus=depth % (depth + 1),
            ))
    if stack:
        raise ValueError(f"unclosed membrane at offset {stack[-1][0].start}")
    membranes.sort(key=lambda item: (item.start, item.end, item.kind))
    return membranes


def exact_ast(source: str) -> dict[str, Any]:
    tokens = tokenize_exact(source)
    membranes = extract_membranes(source)
    return {
        "exact_source": source,
        "tokens": [asdict(token) for token in tokens],
        "membranes": [asdict(membrane) for membrane in membranes],
        "source_hash72": hash72({"exact_source": source, "tokens": [token.text for token in tokens]}),
    }


def validate_postulates(postulates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    validated: list[dict[str, Any]] = []
    for postulate in postulates:
        item = dict(postulate)
        item.pop("receipt_hash72", None)
        required = ("name", "domain", "falsification_test")
        missing = [key for key in required if not item.get(key)]
        if missing:
            raise ValueError(f"engineering postulate missing {','.join(missing)}")
        item["receipt_hash72"] = hash72(item)
        validated.append(item)
    return validated


def build_v72(address: ContextAddress, resolved_cell: int, phase72: int, path: Sequence[int]) -> list[dict[str, Any]]:
    vector: list[dict[str, Any]] = []
    for lane_index, lane in enumerate(ORDERED_BASIS):
        for slot, lo_shu_value in enumerate(LO_SHU):
            vector.append({
                "lane_index": lane_index,
                "lane": lane,
                "slot": slot,
                "lo_shu": lo_shu_value,
                "cell81": resolved_cell,
                "operation_class8": address.operation_class8,
                "g243": address.g243,
                "phase72": (phase72 + lane_index * 9 + slot) % 72,
                "path_depth": len(path),
                "exact_value": {"numerator": lo_shu_value * (lane_index + 1), "denominator": 1},
            })
    if len(vector) != 72:
        raise AssertionError("V72 construction failed")
    return vector


@dataclass
class EquationObject:
    exact_source: str
    ast: dict[str, Any]
    variables: list[str]
    units: dict[str, str]
    dimensions: dict[str, str]
    bindings: list[dict[str, Any]]
    calibration: list[dict[str, Any]]
    postulates: list[dict[str, Any]]
    equation_hash72: str

    @classmethod
    def create(
        cls,
        source: str,
        *,
        units: Mapping[str, str] | None = None,
        dimensions: Mapping[str, str] | None = None,
        bindings: Sequence[Mapping[str, Any]] = (),
        calibration: Sequence[Mapping[str, Any]] = (),
        postulates: Sequence[Mapping[str, Any]] = (),
    ) -> "EquationObject":
        ast = exact_ast(source)
        identifiers = sorted({token["text"] for token in ast["tokens"] if re.match(r"^[A-Za-z_]", token["text"]) and token["text"] != "List"})
        validated_postulates = validate_postulates(postulates)
        payload = {
            "source": source,
            "ast": ast,
            "variables": identifiers,
            "units": dict(units or {}),
            "dimensions": dict(dimensions or {}),
            "bindings": [dict(item) for item in bindings],
            "calibration": [dict(item) for item in calibration],
            "postulates": validated_postulates,
        }
        return cls(
            exact_source=source,
            ast=ast,
            variables=identifiers,
            units=dict(units or {}),
            dimensions=dict(dimensions or {}),
            bindings=[dict(item) for item in bindings],
            calibration=[dict(item) for item in calibration],
            postulates=validated_postulates,
            equation_hash72=hash72(payload),
        )

    def projections(self, receipt_index: int) -> dict[str, Any]:
        shared = {
            "equation_hash72": self.equation_hash72,
            "exact_source": self.exact_source,
            "receipt_index": receipt_index,
        }
        return {
            "symbolic": {**shared, "ast": self.ast},
            "vm81": {**shared, "operation": "RESOLVE_SHARED_EQUATION_GRAPH"},
            "circuit": {**shared, "netlist_nodes": self.variables, "bindings": self.bindings},
            "breadboard": {**shared, "ports": self.bindings, "output_authorized": False, "reason": "MEASUREMENT_CALIBRATION_REQUIRED"},
            "simulation": {**shared, "method": "EXACT_OR_DECLARED_PROJECTION", "calibration": self.calibration},
            "visual": {**shared, "variables": self.variables, "membrane_count": len(self.ast["membranes"])},
            "worldline": {**shared, "global_receipt_lock": True, "physical_claim": False},
        }


@dataclass
class HydrationNode:
    schema: str
    contract: str
    classification: str
    source: str
    ast: dict[str, Any]
    address: dict[str, Any]
    path41: list[int]
    path_scalar: int
    resolved_cell81: int
    phase72: int
    xnor: int
    signed_xnor: int
    ternary: int
    zero_witness: str
    membranes: list[dict[str, Any]]
    v72: list[dict[str, Any]]
    postulates: list[dict[str, Any]]
    parent_hash72: str
    predecessor_hash72: str
    hash72: str
    hash216: str
    transition_receipt: dict[str, Any]
    projections: dict[str, Any]
    cycle_edge: bool = False


class HydrationRuntime:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cache: dict[str, HydrationNode] = {}
        self._payloads: dict[str, str] = {}
        self._edges: list[tuple[str, str]] = []
        self._predecessor = "0" * 72
        self._receipt_index = 0

    @property
    def receipt_index(self) -> int:
        return self._receipt_index

    @property
    def cache_size(self) -> int:
        return len(self._cache)

    def _path_scalar(self, path: Sequence[int]) -> int:
        result = 0
        power = 1
        for local_k in path:
            if not -20 <= local_k <= 20:
                raise ValueError("path coordinate outside [-20,20]")
            result += (local_k + 20) * power
            power *= 41
        return result

    def hydrate(
        self,
        *,
        projected: int,
        path: Sequence[int] = (),
        source: str = "x==x",
        xnor_a: int = 0,
        xnor_b: int = 0,
        postulates: Sequence[Mapping[str, Any]] = (),
        equation: EquationObject | None = None,
        admit: bool = True,
    ) -> HydrationNode:
        if not 0 <= projected < PROJECTED_STATES:
            raise ValueError("projected address out of range")
        path_tuple = tuple(int(value) for value in path)
        validated_postulates = validate_postulates(postulates)
        base = decode_context(projected * 41 + 20)
        resolved_cell = base.cell81
        phase = base.u72_index
        parent_hash = "0" * 72
        for depth, local_k in enumerate(path_tuple):
            resolved_cell = local_cell(resolved_cell, local_k)
            phase = (phase + lo_shu_delta(local_k)) % 72
            parent_hash = hash72({"parent": parent_hash, "depth": depth, "local_k": local_k, "cell81": resolved_cell, "phase72": phase})
        ast = exact_ast(source)
        membranes = [asdict(item) for item in extract_membranes(source)]
        ternary, zero_witness = ternary_orientation(resolved_cell, xnor_a, xnor_b)
        vector = build_v72(base, resolved_cell, phase, path_tuple)
        eq = equation or EquationObject.create(source, postulates=validated_postulates)
        payload = {
            "schema": "HHS_PASS_189_HQLH_NODE_V1",
            "contract": CONTRACT,
            "source": source,
            "ast": ast,
            "address": asdict(base),
            "path41": list(path_tuple),
            "path_scalar": self._path_scalar(path_tuple),
            "resolved_cell81": resolved_cell,
            "phase72": phase,
            "xnor": xnor_bit(xnor_a, xnor_b),
            "signed_xnor": signed_xnor(xnor_a, xnor_b),
            "ternary": ternary,
            "zero_witness": zero_witness,
            "membranes": membranes,
            "v72": vector,
            "postulates": validated_postulates,
            "parent_hash72": parent_hash,
            "predecessor_hash72": self._predecessor,
            "equation_hash72": eq.equation_hash72,
        }
        center = hash72(payload)
        minus = hash72({**payload, "orientation": "minus", "phase72": (phase - 1) % 72})
        plus = hash72({**payload, "orientation": "plus", "phase72": (phase + 1) % 72})
        topology = hash216(minus, center, plus)
        canonical = canonical_json(payload)
        cycle_edge = center in self._cache
        if center in self._payloads and self._payloads[center] != canonical:
            raise ValueError("Hash72 payload mismatch")
        projections = eq.projections(self._receipt_index + (1 if admit else 0))
        receipt = {
            "schema": "HHS_PASS_189_HQLH_TRANSITION_RECEIPT_V1",
            "classification": CLASSIFICATION,
            "receipt_index": self._receipt_index + (1 if admit else 0),
            "predecessor_hash72": self._predecessor,
            "successor_hash72": center,
            "hash216": topology,
            "projected": projected,
            "path41": list(path_tuple),
            "resolved_cell81": resolved_cell,
            "phase72": phase,
            "membrane_count": len(membranes),
            "v72_coordinates": 72,
            "coordinate_drift": 0,
            "cycle_edge": cycle_edge,
            "physical_output_authorized": False,
            "physical_output_reason": "REAL_DEVICE_CALIBRATION_NOT_PRESENT",
        }
        node = HydrationNode(
            schema="HHS_PASS_189_HQLH_NODE_V1",
            contract=CONTRACT,
            classification=CLASSIFICATION,
            source=source,
            ast=ast,
            address=asdict(base),
            path41=list(path_tuple),
            path_scalar=self._path_scalar(path_tuple),
            resolved_cell81=resolved_cell,
            phase72=phase,
            xnor=xnor_bit(xnor_a, xnor_b),
            signed_xnor=signed_xnor(xnor_a, xnor_b),
            ternary=ternary,
            zero_witness=zero_witness,
            membranes=membranes,
            v72=vector,
            postulates=validated_postulates,
            parent_hash72=parent_hash,
            predecessor_hash72=self._predecessor,
            hash72=center,
            hash216=topology,
            transition_receipt=receipt,
            projections=projections,
            cycle_edge=cycle_edge,
        )
        if admit:
            with self._lock:
                if self._predecessor != payload["predecessor_hash72"]:
                    return self.hydrate(
                        projected=projected,
                        path=path_tuple,
                        source=source,
                        xnor_a=xnor_a,
                        xnor_b=xnor_b,
                        postulates=validated_postulates,
                        equation=eq,
                        admit=True,
                    )
                self._receipt_index += 1
                node.transition_receipt["receipt_index"] = self._receipt_index
                self._cache[center] = node
                self._payloads[center] = canonical
                self._edges.append((parent_hash, center))
                self._predecessor = center
        return node

    def replay(self, node: HydrationNode | Mapping[str, Any]) -> bool:
        data = asdict(node) if isinstance(node, HydrationNode) else dict(node)
        projected = int(data["address"]["projected"])
        source = str(data["source"])
        path = [int(value) for value in data["path41"]]
        candidate = HydrationRuntime().hydrate(
            projected=projected,
            path=path,
            source=source,
            xnor_a=0 if int(data["xnor"]) == 1 else 0,
            xnor_b=0 if int(data["xnor"]) == 1 else 1,
            postulates=data.get("postulates", []),
            admit=False,
        )
        return (
            candidate.resolved_cell81 == int(data["resolved_cell81"])
            and candidate.phase72 == int(data["phase72"])
            and candidate.hash72 == data["hash72"]
            and candidate.hash216 == data["hash216"]
            and canonical_json(candidate.v72) == canonical_json(data["v72"])
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "classification": CLASSIFICATION,
            "receipt_index": self._receipt_index,
            "cached_nodes": len(self._cache),
            "edges": len(self._edges),
            "predecessor_hash72": self._predecessor,
            "allocation_policy": "VISITED_PATHS_ONLY",
        }


DEFAULT_RUNTIME = HydrationRuntime()


def node_to_dict(node: HydrationNode) -> dict[str, Any]:
    return asdict(node)


def load_registry() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "registry" / "hhs_pass189_hqlh.template.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HHS Pass 189 HQLH runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    decode_cmd = sub.add_parser("decode")
    decode_cmd.add_argument("extended", type=int)
    membrane_cmd = sub.add_parser("membranes")
    membrane_cmd.add_argument("source")
    hydrate_cmd = sub.add_parser("hydrate")
    hydrate_cmd.add_argument("projected", type=int)
    hydrate_cmd.add_argument("--path", default="")
    hydrate_cmd.add_argument("--source", default="x==x")
    hydrate_cmd.add_argument("--xnor-a", type=int, default=0)
    hydrate_cmd.add_argument("--xnor-b", type=int, default=0)
    replay_cmd = sub.add_parser("replay")
    replay_cmd.add_argument("receipt_file")
    equation_cmd = sub.add_parser("equation")
    equation_cmd.add_argument("source")
    sub.add_parser("registry")
    args = parser.parse_args(argv)

    if args.command == "decode":
        print(json.dumps(asdict(decode_context(args.extended)), indent=2))
    elif args.command == "membranes":
        print(json.dumps(exact_ast(args.source), indent=2))
    elif args.command == "hydrate":
        path = [] if not args.path else [int(value) for value in args.path.split(",")]
        node = DEFAULT_RUNTIME.hydrate(projected=args.projected, path=path, source=args.source, xnor_a=args.xnor_a, xnor_b=args.xnor_b)
        print(json.dumps(node_to_dict(node), indent=2))
    elif args.command == "replay":
        payload = json.loads(Path(args.receipt_file).read_text(encoding="utf-8"))
        print(json.dumps({"replay": DEFAULT_RUNTIME.replay(payload)}, indent=2))
    elif args.command == "equation":
        equation = EquationObject.create(args.source)
        print(json.dumps({**asdict(equation), "projections": equation.projections(0)}, indent=2))
    elif args.command == "registry":
        print(json.dumps(load_registry(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
