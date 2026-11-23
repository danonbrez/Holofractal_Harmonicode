"""Pass 215 certified exact-generation bridge for the unified HHS language service.

A callable projection of the *existing* I18 exact Q4_0 executor. This is not
a replacement for the inherited Pass 214/215 ROM/full-stack obligations or
general language generation. The authenticated profile admits one model,
one exact prompt, seven certified greedy tokens and a zero-mutation egress.
Production Transformers/PyTorch generation remains a distinct provider path.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass220_native_causal_lm_generation_v1 import (
    NativeCausalLMNotReady,
)

ENGINE_ID = "PASS215_EXACT_CERTIFIED"
MODEL_SHA256 = "6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04"
CONTRACTED_PROMPT = "Hello world!"
MAX_NEW_TOKENS = 7
EXPECTED_TOKEN_IDS = (450, 6575, 471, 528, 2827, 322, 278)
EXPECTED_TOKENS = ("▁The", "▁sun", "▁was", "▁sh", "ining", "▁and", "▁the")


class NativePass215ProfileError(NativeCausalLMNotReady):
    """The selected Pass 215 exact executor cannot admit this workload."""


def _exact_engine() -> Any:
    # The deep symbolic/interval executor is never imported by routine health.
    from hhs_backend.runtime import (
        hhs_pass215_iteration18_bounded_generation_control_v2 as i18,
    )
    return i18


class NativePass215CertifiedGenerator:
    """Execute and witness the frozen Pass 215 profile on real model bytes."""

    def __init__(self, model_path: str | Path | None = None) -> None:
        self.model_path = str(
            model_path if model_path is not None
            else os.getenv("HHS_PASS215_EXACT_MODEL_PATH", "")
        ).strip()

    def status(self) -> dict[str, Any]:
        path = Path(self.model_path) if self.model_path else None
        exists = bool(path and path.is_file())
        return {
            "schema": "HHS_PASS215_NATIVE_EXACT_PROVIDER_STATUS_V1",
            "engine_id": ENGINE_ID,
            "model_id": "ggml-org/tiny-llamas/stories15M-q4_0.gguf",
            "model_sha256": MODEL_SHA256,
            "configured": bool(self.model_path),
            "loaded": False,
            "ready": exists,
            "model_identity_verified_by_execution": False,
            "model_path": self.model_path or None,
            "prompt": CONTRACTED_PROMPT,
            "max_new_tokens": MAX_NEW_TOKENS,
            "arbitrary_prompt_generation_supported": False,
            "general_generation_authority_promoted": False,
            "pass213_rom_compilation_claimed": False,
            "natural_language_egress_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mutation_authority": False,
            "canonical_hash216_mutation_authority": False,
        }

    def generate(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        retrieval_context: str | None = None,
        max_new_tokens: int | None = None,
    ) -> dict[str, Any]:
        # Do not quietly drop conversation context or pretend the fixed
        # profile evaluated a multi-turn or RAG-conditioned input.
        users = [str(m.get("content") or "") for m in messages if m.get("role") == "user"]
        other = [
            str(m.get("role") or "") for m in messages
            if m.get("role") not in ("user", "system")
        ]
        if users != [CONTRACTED_PROMPT] or other or retrieval_context:
            raise NativePass215ProfileError(
                "PASS215_NATIVE_INPUT_OUTSIDE_CERTIFIED_PROFILE"
            )
        if max_new_tokens is not None and max_new_tokens != MAX_NEW_TOKENS:
            raise NativePass215ProfileError(
                "PASS215_NATIVE_GENERATION_BOUND_OUTSIDE_CERTIFIED_PROFILE"
            )
        if not self.model_path or not Path(self.model_path).is_file():
            raise NativePass215ProfileError("PASS215_NATIVE_MODEL_FILE_NOT_FOUND")

        engine = _exact_engine()
        evidence, _checkpoint = engine.execute_bounded_generation_with_resume_from_path(
            self.model_path,
            source={
                "kind": "public_open_transformer",
                "repo_id": "ggml-org/tiny-llamas",
                "revision": "main",
            },
            prompt=CONTRACTED_PROMPT,
            expected_sha256=MODEL_SHA256,
            certification_bits=256,
            max_new_tokens=MAX_NEW_TOKENS,
            resume_after_steps=4,
        )
        # The existing exact runtime is the authority; do not synthesize
        # proof roots, infer validity from filenames, or replace proof checks.
        engine.validate_bounded_generation_control_evidence(evidence)
        control = dict(evidence["bounded_generation_control"])
        token_ids = tuple(int(v) for v in control["selected_token_ids"])
        tokens = tuple(str(v) for v in control["selected_tokens"])
        if token_ids != EXPECTED_TOKEN_IDS or tokens != EXPECTED_TOKENS:
            raise NativePass215ProfileError("PASS215_NATIVE_CERTIFIED_CHAIN_MISMATCH")
        if control.get("termination_reason") != "MAX_NEW_TOKENS":
            raise NativePass215ProfileError("PASS215_NATIVE_TERMINATION_MISMATCH")
        if evidence.get("claims", {}).get("runtime_mutation_authority_promoted") is not False:
            raise NativePass215ProfileError("PASS215_NATIVE_MUTATION_AUTHORITY_MISMATCH")
        if evidence.get("claims", {}).get("canonical_mutation_authorized") is not False:
            raise NativePass215ProfileError("PASS215_NATIVE_CANONICAL_AUTHORITY_MISMATCH")
        receipt = {
            "schema": "HHS_PASS215_NATIVE_EXACT_EGRESS_RECEIPT_V1",
            "engine_id": ENGINE_ID,
            "model_sha256": MODEL_SHA256,
            "selected_token_ids": list(token_ids),
            "selected_tokens": list(tokens),
            "generation_control_root_hash216": control["generation_control_root_hash216"],
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "suite_root_hash216": evidence["bounded_generation_control_suite_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
            "per_token_proof_receipt_chain_terminal_hash72": control[
                "per_token_proof_receipt_chain_terminal_hash72"
            ],
            "checkpoint_root_hash216": evidence["resume_checkpoint"]["checkpoint_root_hash216"],
            "generated_token_count": len(tokens),
            "model_identity_verified_by_execution": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mutation_authority": False,
            "canonical_hash216_mutation_authority": False,
        }
        # A display projection only. The exact token spellings and positions
        # remain available in the witnessed receipt.
        return {
            "response": "".join(tokens).replace("▁", " "),
            "receipt": receipt,
            "status": self.status(),
            "finish_reason": "length",
        }
