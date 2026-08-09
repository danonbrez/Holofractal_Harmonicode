"""Pass 215 Iteration 10 exact authenticated text-to-token ingress.

Iteration 10 advances the frozen Iteration 9 token-ID ingress surface by deriving
one contracted four-token sequence from UTF-8 text using tokenizer metadata from
the same authenticated GGUF.  GGUF float32 tokenizer scores are decoded from
IEEE-754 storage bits to reduced exact rational pairs with integer operations;
Python float values are never used as canonical authority.

The tokenizer implements the LLaMA/SentencePiece score-ordered adjacent-pair
merge surface needed by the authenticated workload.  The contracted prompt must
produce exactly four model token IDs (including configured BOS/EOS behavior) so
those IDs can enter the already-frozen four-position Q4_0 embedding and causal
blk.0 symbolic forward path.  General arbitrary-text tokenizer conformance,
arbitrary sequence length, multi-block/full-model execution, logits/generation,
numeric transcendental approximation, dense-forward replacement, runtime
mutation, and canonical mutation remain outside Iteration 10 authority.
"""
from __future__ import annotations

from hashlib import sha256
from math import gcd
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration2_open_transformer_container_v1 as i2
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration6_authenticated_block_graph_v1 as i6
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v2 as i9

CONTRACT = "HHS-P215-I10-EXACT-AUTHENTICATED-TEXT-TO-TOKEN-INGRESS"
PASS_NUMBER = 215
ITERATION = 10
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_10_EXACT_TEXT_TOKEN_INGRESS_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_10_EXACT_TEXT_TOKEN_INGRESS_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_10_EXACT_TEXT_TOKEN_INGRESS_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_10_EXACT_AUTHENTICATED_TEXT_TOKEN_INGRESS_BENCHMARK"

ITERATION9_CLOSURE_HEAD = "8a9ca8907edb94d84ce828639145b94a119c2571"
ITERATION9_CLOSURE_TREE = "cc40fca257d1265882cdc3973205a6962117eb40"
ITERATION9_TOKENIZER_ROOT_HASH216 = "8837bcc9a03cbf7da2a6176761f9267fec282f253335a0aaba954a9bce8aae8e"
ITERATION9_SPECIAL_TOKEN_METADATA_ROOT_HASH216 = "98e9b41e37eca3c1b920accacdc27ee320566867448f066fd02d04d0ca3d3846"
ITERATION9_EMBEDDING_ROOT_HASH216 = "a2beeb9334bb36f604fa3e565e7dd57f82ee44954887c5911f945529449ab436"
ITERATION9_STAGE_SUITE_ROOT_HASH216 = "d13b42587d3519d1a68eab54551cee5adbc1438632ac85581fde0a13c4e97049"
ITERATION9_CAUSAL_ATTENTION_ROOT_HASH216 = "e8e5cc708fe28c5bd6d32f0eb06e55d858758f5b5aa406ebaffaf0c4eb44f020"
ITERATION9_FINAL_OUTPUT_ROOT_HASH216 = "956a155601e72adf7a5e72776eaafbac0c214b6730e5f9134b76e919827d36bd"
ITERATION9_SYMBOLIC_DAG_ROOT_HASH216 = "b9e80d1fa22fe8b56db471f74489733943a9856f88dfa9ffd8de3a69ddb065a3"
ITERATION9_SUITE_ROOT_HASH216 = "5f544e489fb05cf6675e6034a9acf552d53e1dd83801c6941384de868d9e4a94"
ITERATION9_EVIDENCE_ROOT_HASH216 = "71e36d07d2e5c016cfdae8356eb50abb5d750aefc796a2ad3f413d0391d06261"
ITERATION9_RECEIPT_HASH72 = "SF>Bd3yVELc5N4?z>34u6tM05-NirTF!PtssI5l3on*)3IzGzwj/4SC48Gtl>PGZ2EN7lKDH"
ITERATION9_CLOSURE_ARTIFACT_SHA256 = "dab1624efd702f44ed3480d1b9655be51f2f4794984144af6d76e9173e5e1ddc"

REAL_MODEL_SHA256 = i9.REAL_MODEL_SHA256
SEQUENCE_LENGTH = i9.SEQUENCE_LENGTH
EMBEDDING_WIDTH = i9.EMBEDDING_WIDTH
CONTRACTED_PROMPT = "Hello world!"
TOKEN_SCORE_KEY = "tokenizer.ggml.scores"
ADD_SPACE_PREFIX_KEY = "tokenizer.ggml.add_space_prefix"
REMOVE_EXTRA_WHITESPACES_KEY = "tokenizer.ggml.remove_extra_whitespaces"
PRECOMPILED_CHARMAP_KEY = "tokenizer.ggml.precompiled_charsmap"
BOS_KEY = "tokenizer.ggml.bos_token_id"
EOS_KEY = "tokenizer.ggml.eos_token_id"
UNK_KEY = "tokenizer.ggml.unknown_token_id"
BYTE_TOKEN_TYPE = 6
SPACE_MARKER = "\u2581"


class Pass215Iteration10Error(RuntimeError):
    pass


class Pass215Iteration10ValidationError(Pass215Iteration10Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration10ValidationError(f"PASS215_I10_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _reduce_pair(numerator: int, denominator: int) -> tuple[int, int]:
    if denominator == 0:
        raise Pass215Iteration10ValidationError("PASS215_I10_ZERO_DENOMINATOR")
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    if numerator == 0:
        return (0, 1)
    divisor = gcd(abs(numerator), denominator)
    return (numerator // divisor, denominator // divisor)


def decode_binary32_exact(raw: bytes) -> tuple[int, int]:
    """Decode one IEEE-754 binary32 storage value to an exact rational pair.

    No float conversion occurs. NaN and infinities fail closed.
    """
    if len(raw) != 4:
        raise Pass215Iteration10ValidationError("PASS215_I10_BINARY32_WIDTH_INVALID")
    bits = int.from_bytes(raw, "little", signed=False)
    sign = -1 if (bits >> 31) & 1 else 1
    exponent = (bits >> 23) & 0xFF
    fraction = bits & 0x7FFFFF
    if exponent == 0xFF:
        raise Pass215Iteration10ValidationError("PASS215_I10_BINARY32_NONFINITE_FORBIDDEN")
    if exponent == 0:
        if fraction == 0:
            return (0, 1)
        mantissa = fraction
        power = -149
    else:
        mantissa = (1 << 23) | fraction
        power = exponent - 127 - 23
    numerator = sign * mantissa
    denominator = 1
    if power >= 0:
        numerator <<= power
    else:
        denominator <<= -power
    return _reduce_pair(numerator, denominator)


def _compare_pairs(left: tuple[int, int], right: tuple[int, int]) -> int:
    lhs = int(left[0]) * int(right[1])
    rhs = int(right[0]) * int(left[1])
    return (lhs > rhs) - (lhs < rhs)


def _iteration9_bindings() -> Mapping[str, Any]:
    return {
        "iteration9_closure_head": ITERATION9_CLOSURE_HEAD,
        "iteration9_closure_tree": ITERATION9_CLOSURE_TREE,
        "iteration9_tokenizer_root_hash216": ITERATION9_TOKENIZER_ROOT_HASH216,
        "iteration9_special_token_metadata_root_hash216": ITERATION9_SPECIAL_TOKEN_METADATA_ROOT_HASH216,
        "iteration9_embedding_root_hash216": ITERATION9_EMBEDDING_ROOT_HASH216,
        "iteration9_stage_suite_root_hash216": ITERATION9_STAGE_SUITE_ROOT_HASH216,
        "iteration9_causal_attention_root_hash216": ITERATION9_CAUSAL_ATTENTION_ROOT_HASH216,
        "iteration9_final_output_root_hash216": ITERATION9_FINAL_OUTPUT_ROOT_HASH216,
        "iteration9_symbolic_dag_root_hash216": ITERATION9_SYMBOLIC_DAG_ROOT_HASH216,
        "iteration9_suite_root_hash216": ITERATION9_SUITE_ROOT_HASH216,
        "iteration9_evidence_root_hash216": ITERATION9_EVIDENCE_ROOT_HASH216,
        "iteration9_receipt_hash72": ITERATION9_RECEIPT_HASH72,
        "iteration9_closure_artifact_sha256": ITERATION9_CLOSURE_ARTIFACT_SHA256,
    }


def _validate_frozen_iteration9_evidence(evidence: Mapping[str, Any]) -> None:
    i9.validate_authenticated_token_ingress_evidence(evidence)
    tokenizer = evidence["authenticated_tokenizer"]
    ingress = evidence["authenticated_token_ingress"]
    execution = evidence["token_ingress_coordinate_forward"]
    checks = {
        "tokenizer": (tokenizer["vocabulary_root_hash216"], ITERATION9_TOKENIZER_ROOT_HASH216),
        "special": (tokenizer["special_token_metadata_root_hash216"], ITERATION9_SPECIAL_TOKEN_METADATA_ROOT_HASH216),
        "embedding": (ingress["embedding_suite_root_hash216"], ITERATION9_EMBEDDING_ROOT_HASH216),
        "stage": (execution["executed_stage_suite_root_hash216"], ITERATION9_STAGE_SUITE_ROOT_HASH216),
        "causal": (execution["causal_attention_root_hash216"], ITERATION9_CAUSAL_ATTENTION_ROOT_HASH216),
        "output": (execution["final_output_root_hash216"], ITERATION9_FINAL_OUTPUT_ROOT_HASH216),
        "dag": (execution["symbolic_dag"]["ordered_node_root_hash216"], ITERATION9_SYMBOLIC_DAG_ROOT_HASH216),
        "suite": (evidence["token_ingress_suite_root_hash216"], ITERATION9_SUITE_ROOT_HASH216),
        "evidence": (evidence["evidence_root_hash216"], ITERATION9_EVIDENCE_ROOT_HASH216),
        "receipt": (evidence["receipt_hash72"], ITERATION9_RECEIPT_HASH72),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise Pass215Iteration10ValidationError(f"PASS215_I10_ITERATION9_ROOT_MISMATCH:{name}")


def _read_exact_tokenizer_metadata(raw: bytes) -> Mapping[str, Any]:
    """Extend the frozen Iteration 9 reader with exact tokenizer score evidence."""
    base = dict(i9._read_tokenizer_metadata(raw))
    reader = i2._Reader(raw)
    if reader.read(4) != b"GGUF":
        raise Pass215Iteration10ValidationError("PASS215_I10_GGUF_MAGIC_INVALID")
    version = reader.u32()
    if version not in (2, 3):
        raise Pass215Iteration10ValidationError("PASS215_I10_GGUF_VERSION_UNSUPPORTED")
    tensor_count = reader.u64()
    metadata_count = reader.u64()
    if tensor_count <= 0 or metadata_count > 1_000_000:
        raise Pass215Iteration10ValidationError("PASS215_I10_GGUF_HEADER_INVALID")

    score_bits: tuple[str, ...] | None = None
    score_pairs: tuple[tuple[int, int], ...] | None = None
    normalization_bools: dict[str, bool] = {}
    precompiled_charsmap_present = False

    for _ in range(metadata_count):
        key = reader.string()
        value_type = reader.u32()
        if key == TOKEN_SCORE_KEY:
            if value_type != i2._GGUF_ARRAY:
                raise Pass215Iteration10ValidationError("PASS215_I10_SCORE_ARRAY_TYPE_INVALID")
            element_type = reader.u32()
            count = reader.u64()
            if element_type != i2._GGUF_FLOAT32:
                raise Pass215Iteration10ValidationError("PASS215_I10_SCORE_ELEMENT_TYPE_INVALID")
            if count != int(base["vocabulary_size"]):
                raise Pass215Iteration10ValidationError("PASS215_I10_SCORE_COUNT_MISMATCH")
            bits_out: list[str] = []
            pairs_out: list[tuple[int, int]] = []
            for _index in range(count):
                encoded = reader.read(4)
                bits_out.append(encoded.hex())
                pairs_out.append(decode_binary32_exact(encoded))
            score_bits = tuple(bits_out)
            score_pairs = tuple(pairs_out)
            continue
        if key in (ADD_SPACE_PREFIX_KEY, REMOVE_EXTRA_WHITESPACES_KEY):
            if value_type != i2._GGUF_BOOL:
                raise Pass215Iteration10ValidationError(f"PASS215_I10_NORMALIZATION_BOOL_TYPE_INVALID:{key}")
            normalization_bools[key] = bool(i2._read_gguf_value(reader, value_type, summarize_arrays=False))
            continue
        if key == PRECOMPILED_CHARMAP_KEY:
            precompiled_charsmap_present = True
        i2._read_gguf_value(reader, value_type, summarize_arrays=True)

    if score_bits is None or score_pairs is None:
        raise Pass215Iteration10ValidationError("PASS215_I10_TOKENIZER_SCORES_MISSING")
    score_bits_root = i4base.hash216(
        "pass215-i10-tokenizer-score-storage-bits",
        i4base.canonical_bytes(list(score_bits)),
    )
    exact_score_root = i4base.hash216(
        "pass215-i10-tokenizer-score-exact-rationals",
        i4base.canonical_bytes([[n, d] for n, d in score_pairs]),
    )
    base.update({
        "score_bits": score_bits,
        "score_pairs": score_pairs,
        "score_count": len(score_pairs),
        "score_storage_bits_root_hash216": score_bits_root,
        "exact_score_root_hash216": exact_score_root,
        "normalization_boolean_metadata": normalization_bools,
        "precompiled_charsmap_present": precompiled_charsmap_present,
        "score_float_interpretation_performed": False,
    })
    return base


def _normalization_policy(tokenizer: Mapping[str, Any]) -> Mapping[str, Any]:
    model = tokenizer.get("tokenizer_model")
    if model not in ("llama", "spm", "sentencepiece"):
        raise Pass215Iteration10ValidationError(f"PASS215_I10_TOKENIZER_MODEL_UNSUPPORTED:{model}")
    if tokenizer.get("precompiled_charsmap_present"):
        raise Pass215Iteration10ValidationError("PASS215_I10_PRECOMPILED_CHARMAP_UNSUPPORTED")
    booleans = dict(tokenizer.get("boolean_metadata", {}))
    normal = dict(tokenizer.get("normalization_boolean_metadata", {}))
    add_bos = bool(booleans[BOS_ADD_KEY]) if (BOS_ADD_KEY := "tokenizer.ggml.add_bos_token") in booleans else True
    add_eos = bool(booleans[EOS_ADD_KEY]) if (EOS_ADD_KEY := "tokenizer.ggml.add_eos_token") in booleans else False
    add_space_prefix = bool(normal[ADD_SPACE_PREFIX_KEY]) if ADD_SPACE_PREFIX_KEY in normal else True
    remove_extra = bool(normal[REMOVE_EXTRA_WHITESPACES_KEY]) if REMOVE_EXTRA_WHITESPACES_KEY in normal else False
    return {
        "tokenizer_model": model,
        "add_bos": add_bos,
        "add_eos": add_eos,
        "add_space_prefix": add_space_prefix,
        "remove_extra_whitespaces": remove_extra,
        "missing_add_bos_policy": "LEGACY_LLAMA_TRUE" if BOS_ADD_KEY not in booleans else "METADATA",
        "missing_add_eos_policy": "LEGACY_LLAMA_FALSE" if EOS_ADD_KEY not in booleans else "METADATA",
        "missing_add_space_prefix_policy": "LEGACY_LLAMA_TRUE" if ADD_SPACE_PREFIX_KEY not in normal else "METADATA",
        "precompiled_charsmap_present": False,
    }


def _normalize_contracted_text(text: str, policy: Mapping[str, Any], tokens: Sequence[str]) -> tuple[str, str]:
    if not isinstance(text, str):
        raise Pass215Iteration10ValidationError("PASS215_I10_TEXT_STRING_REQUIRED")
    text.encode("utf-8", errors="strict")
    normalized = text
    if policy.get("remove_extra_whitespaces"):
        # The contracted prompt contains only single ASCII spaces. Reject rather
        # than generalize the normalization claim to inputs whose semantics would
        # require a complete SentencePiece normalizer.
        if normalized.strip() != normalized or "  " in normalized or "\t" in normalized or "\n" in normalized or "\r" in normalized:
            raise Pass215Iteration10ValidationError("PASS215_I10_EXTRA_WHITESPACE_NORMALIZATION_OUT_OF_SCOPE")
    marker_mode = "U+2581" if any(piece.startswith(SPACE_MARKER) for piece in tokens) else "ASCII_SPACE"
    if policy.get("add_space_prefix") and normalized and not normalized.startswith((" ", SPACE_MARKER)):
        normalized = " " + normalized
    if marker_mode == "U+2581":
        normalized = normalized.replace(" ", SPACE_MARKER)
    return normalized, marker_mode


def _byte_token_map(tokens: Sequence[str], token_types: Sequence[int] | None) -> Mapping[int, int]:
    if token_types is None:
        return {}
    out: dict[int, int] = {}
    for token_id, (piece, token_type) in enumerate(zip(tokens, token_types)):
        if int(token_type) != BYTE_TOKEN_TYPE:
            continue
        if len(piece) == 6 and piece.startswith("<0x") and piece.endswith(">"):
            try:
                byte_value = int(piece[3:5], 16)
            except ValueError:
                continue
            out.setdefault(byte_value, token_id)
    return out


def _fallback_symbol_ids(symbol: str, tokenizer: Mapping[str, Any]) -> tuple[int, ...]:
    tokens = tokenizer["tokens"]
    token_types = tokenizer.get("token_types")
    byte_map = _byte_token_map(tokens, token_types)
    encoded = symbol.encode("utf-8")
    if byte_map and all(value in byte_map for value in encoded):
        return tuple(byte_map[value] for value in encoded)
    unknown = tokenizer.get("special_token_ids", {}).get(UNK_KEY)
    if unknown is None:
        raise Pass215Iteration10ValidationError("PASS215_I10_UNMATCHED_SYMBOL_WITHOUT_BYTE_OR_UNK")
    return (int(unknown),)


def _tokenize_sentencepiece_bpe(text: str, tokenizer: Mapping[str, Any]) -> Mapping[str, Any]:
    tokens = tuple(str(value) for value in tokenizer["tokens"])
    scores = tokenizer.get("score_pairs")
    bits = tokenizer.get("score_bits")
    if not isinstance(scores, tuple) or not isinstance(bits, tuple) or len(scores) != len(tokens) or len(bits) != len(tokens):
        raise Pass215Iteration10ValidationError("PASS215_I10_TOKENIZER_SCORE_SURFACE_INVALID")
    policy = _normalization_policy(tokenizer)
    normalized, marker_mode = _normalize_contracted_text(text, policy, tokens)

    piece_to_id: dict[str, int] = {}
    for token_id, piece in enumerate(tokens):
        piece_to_id.setdefault(piece, token_id)

    symbols = list(normalized)
    left_positions = list(range(len(symbols)))
    merge_trace: list[Mapping[str, Any]] = []
    while len(symbols) > 1:
        best: tuple[int, int, tuple[int, int], int, str] | None = None
        for index in range(len(symbols) - 1):
            merged_piece = symbols[index] + symbols[index + 1]
            token_id = piece_to_id.get(merged_piece)
            if token_id is None:
                continue
            score = scores[token_id]
            left_position = left_positions[index]
            candidate = (index, token_id, score, left_position, merged_piece)
            if best is None:
                best = candidate
                continue
            comparison = _compare_pairs(score, best[2])
            if comparison > 0 or (comparison == 0 and left_position < best[3]):
                best = candidate
        if best is None:
            break
        index, token_id, score, left_position, merged_piece = best
        merge_trace.append({
            "step": len(merge_trace),
            "left_position": left_position,
            "piece": merged_piece,
            "token_id": token_id,
            "score_bits_hex": bits[token_id],
            "score_numerator": int(score[0]),
            "score_denominator": int(score[1]),
        })
        symbols[index:index + 2] = [merged_piece]
        left_positions[index:index + 2] = [left_position]

    core_ids: list[int] = []
    core_records: list[Mapping[str, Any]] = []
    for position, symbol in enumerate(symbols):
        token_id = piece_to_id.get(symbol)
        if token_id is not None:
            ids = (token_id,)
            fallback = "NONE"
        else:
            ids = _fallback_symbol_ids(symbol, tokenizer)
            fallback = "BYTE_OR_UNK"
        for emitted in ids:
            core_ids.append(int(emitted))
            core_records.append({
                "core_position": len(core_records),
                "source_symbol_position": position,
                "symbol": symbol,
                "token_id": int(emitted),
                "token": tokens[int(emitted)],
                "fallback": fallback,
            })

    output_ids: list[int] = []
    special_ids = tokenizer.get("special_token_ids", {})
    if policy["add_bos"]:
        if BOS_KEY not in special_ids:
            raise Pass215Iteration10ValidationError("PASS215_I10_BOS_REQUIRED_BUT_MISSING")
        output_ids.append(int(special_ids[BOS_KEY]))
    output_ids.extend(core_ids)
    if policy["add_eos"]:
        if EOS_KEY not in special_ids:
            raise Pass215Iteration10ValidationError("PASS215_I10_EOS_REQUIRED_BUT_MISSING")
        output_ids.append(int(special_ids[EOS_KEY]))

    if any(not 0 <= token_id < len(tokens) for token_id in output_ids):
        raise Pass215Iteration10ValidationError("PASS215_I10_OUTPUT_TOKEN_ID_RANGE_INVALID")
    return {
        "input_text": text,
        "input_utf8_bytes": len(text.encode("utf-8")),
        "input_utf8_sha256": sha256(text.encode("utf-8")).hexdigest(),
        "normalized_text": normalized,
        "normalization_policy": policy,
        "space_marker_mode": marker_mode,
        "core_symbols": symbols,
        "core_token_records": core_records,
        "merge_trace": merge_trace,
        "merge_count": len(merge_trace),
        "token_ids": output_ids,
        "tokens": [tokens[token_id] for token_id in output_ids],
        "token_count": len(output_ids),
        "bos_added": bool(policy["add_bos"]),
        "eos_added": bool(policy["add_eos"]),
        "score_ordering": "EXACT_REDUCED_RATIONAL_FROM_BINARY32_STORAGE_BITS",
        "score_float_interpretation_performed": False,
    }


def build_exact_text_token_ingress_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration10ValidationError("PASS215_I10_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration10ValidationError("PASS215_I10_AUTHENTICATED_REAL_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT:
        raise Pass215Iteration10ValidationError("PASS215_I10_PROMPT_OUTSIDE_CONTRACT")

    # Re-execute and bind the entire frozen Iteration 9 ingress/forward before
    # replacing its deterministic token-ID selection with text-derived IDs.
    i9_evidence = i9.build_authenticated_token_ingress_evidence(
        raw, filename=filename, source=source, expected_sha256=expected_sha256
    )
    _validate_frozen_iteration9_evidence(i9_evidence)

    tokenizer = _read_exact_tokenizer_metadata(raw)
    tokenization = _tokenize_sentencepiece_bpe(prompt, tokenizer)
    if tokenization["token_count"] != SEQUENCE_LENGTH:
        raise Pass215Iteration10ValidationError(
            f"PASS215_I10_CONTRACTED_TOKEN_COUNT_MISMATCH:{tokenization['token_count']}!={SEQUENCE_LENGTH}"
        )
    token_ids = tuple(int(value) for value in tokenization["token_ids"])
    embeddings = i9._extract_authenticated_embeddings(raw, tokenizer, token_ids)
    i6_evidence = i6.build_block_graph_evidence(
        raw, filename=filename, source=source, expected_sha256=expected_sha256
    )
    i6.validate_block_graph_evidence(i6_evidence)
    execution = i9._execute_forward_from_embeddings(raw, i6_evidence, embeddings["rows"])
    linears = execution.pop("linears")
    q4_control = i7._q4_row_semantic_control(linears["blk.0.attn_q.weight"])
    if not q4_control["exact"]:
        raise Pass215Iteration10ValidationError("PASS215_I10_Q4_ROW_SEMANTIC_CONTROL_FAILED")

    tokenizer_record = {
        "tokenizer_model": tokenizer["tokenizer_model"],
        "vocabulary_size": tokenizer["vocabulary_size"],
        "vocabulary_root_hash216": tokenizer["vocabulary_root_hash216"],
        "token_type_root_hash216": tokenizer["token_type_root_hash216"],
        "special_token_metadata_root_hash216": tokenizer["special_token_metadata_root_hash216"],
        "active_special_token_ids": tokenizer["special_token_ids"],
        "inactive_special_token_ids": tokenizer["inactive_special_token_ids"],
        "boolean_metadata": tokenizer["boolean_metadata"],
        "normalization_boolean_metadata": tokenizer["normalization_boolean_metadata"],
        "precompiled_charsmap_present": tokenizer["precompiled_charsmap_present"],
        "tokenizer_score_count": tokenizer["score_count"],
        "score_storage_bits_root_hash216": tokenizer["score_storage_bits_root_hash216"],
        "exact_score_root_hash216": tokenizer["exact_score_root_hash216"],
        "score_float_interpretation_performed": False,
    }
    tokenization_record = dict(tokenization)
    tokenization_root = i4base.hash216(
        "pass215-i10-contracted-text-tokenization",
        i4base.canonical_bytes(tokenization_record),
    )
    source_record = {
        **dict(source),
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256,
    }
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "authority": {
            "pass215_benchmark_authority_active": True,
            "no_float_canonical_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "inherits": {
            **_iteration9_bindings(),
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "authenticated_tokenizer": tokenizer_record,
        "contracted_text_ingress": {
            **tokenization_record,
            "tokenization_root_hash216": tokenization_root,
            "contracted_prompt_match": True,
            "general_arbitrary_text_tokenizer_conformance_claimed": False,
        },
        "authenticated_embedding_ingress": {
            "selected_token_ids": list(token_ids),
            "selected_tokens": embeddings["selected_tokens"],
            "embedding_tensor": embeddings["tensor_binding"],
            "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
            "embedding_lookup_work": embeddings["embedding_lookup_work"],
        },
        "text_derived_coordinate_forward": execution,
        "exact_controls": {
            "iteration9_frozen_roots_reexecuted_and_bound": {"exact": True, **_iteration9_bindings()},
            "tokenizer_scores_decoded_without_python_float": {"exact": True, "score_count": tokenizer["score_count"]},
            "contracted_token_count_equals_forward_sequence_length": {"exact": len(token_ids) == SEQUENCE_LENGTH, "token_count": len(token_ids)},
            "inactive_special_ids_not_selected": {
                "exact": all(value not in token_ids for value in tokenizer["inactive_special_token_ids"].values()),
                "inactive_special_token_ids": tokenizer["inactive_special_token_ids"],
            },
            "embedding_rows_source_bound": {"exact": True, "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"]},
            "q4_0_factored_row_matches_iteration4_exact_execution": q4_control,
            "causal_edge_set_exact": {"exact": execution["causal_controls"]["edge_set_exact"], "future_edges_materialized": False},
        },
        "claims": {
            "authenticated_iteration9_roots_inherited_unchanged": True,
            "contracted_utf8_text_tokenization_executed": True,
            "authenticated_tokenizer_scores_bound": True,
            "exact_binary32_score_ordering_executed": True,
            "sentencepiece_bpe_pair_merge_executed": True,
            "text_derived_token_ids_feed_exact_q4_0_embedding_lookup": True,
            "contracted_text_to_blk0_forward_executed": True,
            "general_arbitrary_text_tokenizer_conformance_claimed": False,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
            "multi_block_transformer_forward_executed": False,
            "full_model_forward_executed": False,
            "output_logits_executed": False,
            "generation_or_sampling_executed": False,
            "numeric_transcendental_evaluation_performed": False,
            "approximate_transcendental_evaluation_performed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_performed": False,
            "canonical_mutation_performed": False,
        },
    }
    roots = {
        "iteration9_suite_root_hash216": ITERATION9_SUITE_ROOT_HASH216,
        "tokenizer_vocabulary_root_hash216": tokenizer["vocabulary_root_hash216"],
        "tokenizer_score_storage_root_hash216": tokenizer["score_storage_bits_root_hash216"],
        "tokenizer_exact_score_root_hash216": tokenizer["exact_score_root_hash216"],
        "text_tokenization_root_hash216": tokenization_root,
        "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
        "stage_suite_root_hash216": execution["executed_stage_suite_root_hash216"],
        "causal_attention_root_hash216": execution["causal_attention_root_hash216"],
        "final_output_root_hash216": execution["final_output_root_hash216"],
        "symbolic_dag_root_hash216": execution["symbolic_dag"]["ordered_node_root_hash216"],
    }
    suite_root = i4base.hash216("pass215-i10-exact-text-token-ingress-suite", i4base.canonical_bytes(roots))
    evidence["exact_text_token_ingress_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216("pass215-i10-exact-text-token-ingress-evidence", i4base.canonical_bytes(evidence))
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION10_EXACT_TEXT_TOKEN_INGRESS"},
        {"sequence": 10, "parent_hash72": ITERATION9_RECEIPT_HASH72, "evidence_root_hash216": evidence_root, "exact_text_token_ingress_suite_root_hash216": suite_root},
    )
    _reject_floats(evidence)
    return evidence


def build_exact_text_token_ingress_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_exact_text_token_ingress_evidence(
        target.read_bytes(), filename=target.name, source=source, prompt=prompt, expected_sha256=expected_sha256
    )


def validate_exact_text_token_ingress_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration10ValidationError("PASS215_I10_SCHEMA_OR_CONTRACT_INVALID")
    if evidence.get("inherits") is None:
        raise Pass215Iteration10ValidationError("PASS215_I10_INHERITANCE_MISSING")
    for key, expected in _iteration9_bindings().items():
        if evidence["inherits"].get(key) != expected:
            raise Pass215Iteration10ValidationError(f"PASS215_I10_FROZEN_BINDING_INVALID:{key}")
    tokenizer = evidence.get("authenticated_tokenizer")
    text = evidence.get("contracted_text_ingress")
    embedding = evidence.get("authenticated_embedding_ingress")
    execution = evidence.get("text_derived_coordinate_forward")
    claims = evidence.get("claims")
    if not all(isinstance(value, Mapping) for value in (tokenizer, text, embedding, execution, claims)):
        raise Pass215Iteration10ValidationError("PASS215_I10_REQUIRED_SECTION_MISSING")
    if text["input_text"] != CONTRACTED_PROMPT or text["contracted_prompt_match"] is not True:
        raise Pass215Iteration10ValidationError("PASS215_I10_CONTRACTED_PROMPT_INVALID")
    token_ids = [int(value) for value in text["token_ids"]]
    if len(token_ids) != SEQUENCE_LENGTH or int(text["token_count"]) != SEQUENCE_LENGTH:
        raise Pass215Iteration10ValidationError("PASS215_I10_TOKEN_COUNT_INVALID")
    if embedding["selected_token_ids"] != token_ids:
        raise Pass215Iteration10ValidationError("PASS215_I10_TEXT_EMBEDDING_TOKEN_ID_MISMATCH")
    if tokenizer["score_float_interpretation_performed"] is not False:
        raise Pass215Iteration10ValidationError("PASS215_I10_SCORE_FLOAT_AUTHORITY_INVALID")
    if int(tokenizer["tokenizer_score_count"]) != int(tokenizer["vocabulary_size"]):
        raise Pass215Iteration10ValidationError("PASS215_I10_SCORE_VOCAB_COUNT_INVALID")
    if embedding["embedding_lookup_work"] != {
        "selected_token_count": SEQUENCE_LENGTH,
        "q4_0_blocks_decoded": 36,
        "exact_embedding_coordinates_materialized": 1152,
        "source_row_bytes_read": 648,
    }:
        raise Pass215Iteration10ValidationError("PASS215_I10_EMBEDDING_WORK_INVALID")
    if execution["final_output_token_count"] != SEQUENCE_LENGTH or execution["final_output_coordinate_count"] != 1152:
        raise Pass215Iteration10ValidationError("PASS215_I10_OUTPUT_GEOMETRY_INVALID")
    if execution["causal_controls"]["future_edges_materialized"] is not False or execution["causal_controls"]["edge_set_exact"] is not True:
        raise Pass215Iteration10ValidationError("PASS215_I10_CAUSAL_CONTROL_INVALID")
    required_true = (
        "authenticated_iteration9_roots_inherited_unchanged",
        "contracted_utf8_text_tokenization_executed",
        "authenticated_tokenizer_scores_bound",
        "exact_binary32_score_ordering_executed",
        "sentencepiece_bpe_pair_merge_executed",
        "text_derived_token_ids_feed_exact_q4_0_embedding_lookup",
        "contracted_text_to_blk0_forward_executed",
    )
    required_false = (
        "general_arbitrary_text_tokenizer_conformance_claimed",
        "general_arbitrary_sequence_length_transformer_forward_executed",
        "multi_block_transformer_forward_executed",
        "full_model_forward_executed",
        "output_logits_executed",
        "generation_or_sampling_executed",
        "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_performed",
        "canonical_mutation_performed",
    )
    if any(claims.get(key) is not True for key in required_true):
        raise Pass215Iteration10ValidationError("PASS215_I10_REQUIRED_TRUE_CLAIM_INVALID")
    if any(claims.get(key) is not False for key in required_false):
        raise Pass215Iteration10ValidationError("PASS215_I10_REQUIRED_FALSE_CLAIM_INVALID")

    roots = {
        "iteration9_suite_root_hash216": ITERATION9_SUITE_ROOT_HASH216,
        "tokenizer_vocabulary_root_hash216": tokenizer["vocabulary_root_hash216"],
        "tokenizer_score_storage_root_hash216": tokenizer["score_storage_bits_root_hash216"],
        "tokenizer_exact_score_root_hash216": tokenizer["exact_score_root_hash216"],
        "text_tokenization_root_hash216": text["tokenization_root_hash216"],
        "embedding_suite_root_hash216": embedding["embedding_suite_root_hash216"],
        "stage_suite_root_hash216": execution["executed_stage_suite_root_hash216"],
        "causal_attention_root_hash216": execution["causal_attention_root_hash216"],
        "final_output_root_hash216": execution["final_output_root_hash216"],
        "symbolic_dag_root_hash216": execution["symbolic_dag"]["ordered_node_root_hash216"],
    }
    expected_suite = i4base.hash216("pass215-i10-exact-text-token-ingress-suite", i4base.canonical_bytes(roots))
    if evidence.get("exact_text_token_ingress_suite_root_hash216") != expected_suite:
        raise Pass215Iteration10ValidationError("PASS215_I10_SUITE_ROOT_INVALID")
    body = dict(evidence)
    evidence_root = body.pop("evidence_root_hash216", None)
    receipt = body.pop("receipt_hash72", None)
    expected_evidence = i4base.hash216("pass215-i10-exact-text-token-ingress-evidence", i4base.canonical_bytes(body))
    if evidence_root != expected_evidence:
        raise Pass215Iteration10ValidationError("PASS215_I10_EVIDENCE_ROOT_INVALID")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION10_EXACT_TEXT_TOKEN_INGRESS"},
        {"sequence": 10, "parent_hash72": ITERATION9_RECEIPT_HASH72, "evidence_root_hash216": evidence_root, "exact_text_token_ingress_suite_root_hash216": expected_suite},
    )
    if receipt != expected_receipt:
        raise Pass215Iteration10ValidationError("PASS215_I10_RECEIPT_INVALID")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_exact_text_token_ingress_evidence(left)
    validate_exact_text_token_ingress_evidence(right)
    left_text = left["contracted_text_ingress"]
    right_text = right["contracted_text_ingress"]
    left_embedding = left["authenticated_embedding_ingress"]
    right_embedding = right["authenticated_embedding_ingress"]
    left_execution = left["text_derived_coordinate_forward"]
    right_execution = right["text_derived_coordinate_forward"]
    identities = {
        "token_ids": left_text["token_ids"] == right_text["token_ids"],
        "tokenization_root_hash216": left_text["tokenization_root_hash216"] == right_text["tokenization_root_hash216"],
        "embedding_suite_root_hash216": left_embedding["embedding_suite_root_hash216"] == right_embedding["embedding_suite_root_hash216"],
        "stage_suite_root_hash216": left_execution["executed_stage_suite_root_hash216"] == right_execution["executed_stage_suite_root_hash216"],
        "causal_attention_root_hash216": left_execution["causal_attention_root_hash216"] == right_execution["causal_attention_root_hash216"],
        "final_output_root_hash216": left_execution["final_output_root_hash216"] == right_execution["final_output_root_hash216"],
        "symbolic_dag_root_hash216": left_execution["symbolic_dag"]["ordered_node_root_hash216"] == right_execution["symbolic_dag"]["ordered_node_root_hash216"],
        "suite_root_hash216": left["exact_text_token_ingress_suite_root_hash216"] == right["exact_text_token_ingress_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"] == right["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"] == right["receipt_hash72"],
    }
    return {
        "schema": REPLAY_SCHEMA,
        "cross_process_replay": all(identities.values()),
        "semantic_exactness": all(identities.values()),
        "identities": identities,
        "token_ids": list(left_text["token_ids"]),
        "text_tokenization_root_hash216": left_text["tokenization_root_hash216"],
        "embedding_suite_root_hash216": left_embedding["embedding_suite_root_hash216"],
        "final_output_root_hash216": left_execution["final_output_root_hash216"],
        "suite_root_hash216": left["exact_text_token_ingress_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT", "PASS_NUMBER", "ITERATION", "EVIDENCE_SCHEMA", "VALIDATION_SCHEMA", "REPLAY_SCHEMA",
    "REAL_MODEL_SHA256", "SEQUENCE_LENGTH", "EMBEDDING_WIDTH", "CONTRACTED_PROMPT",
    "Pass215Iteration10Error", "Pass215Iteration10ValidationError", "decode_binary32_exact",
    "_compare_pairs", "_read_exact_tokenizer_metadata", "_normalization_policy", "_normalize_contracted_text",
    "_tokenize_sentencepiece_bpe", "build_exact_text_token_ingress_evidence",
    "build_exact_text_token_ingress_evidence_from_path", "validate_exact_text_token_ingress_evidence", "compare_replay",
]
