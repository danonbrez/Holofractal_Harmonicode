from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile

from hhs_runtime.pass166.common import Word2VecPackageManifest
from hhs_runtime.pass166.service import Word2VecService
from hhs_runtime.pass218.model_activation_i20 import (
    Pass218I20ModelConfiguration,
    Pass218Pass166ModelBinding,
)


class _Target:
    def root_hash72(self) -> str:
        return "I" * 72


class _Lifecycle:
    def __init__(self, fence: int) -> None:
        self.fence = fence
        self.target = _Target()

    def status(self) -> dict:
        return {
            "authority_ready": True,
            "owner_id": "i20-local-writer",
            "ownership_fence_epoch": self.fence,
            "distributed_owner_id": "i20-distributed-writer",
            "distributed_host_id": "i20-host",
            "distributed_fence_epoch": self.fence,
            "split_brain_writer_permitted": False,
        }


class _Postcondition:
    def status(self) -> dict:
        return {
            "distributed_postcondition_configured": True,
            "successful_closure_pending_verification_count": 0,
        }


def _install_model(root: Path) -> tuple[Word2VecService, dict]:
    raw = (
        b"4 3\n"
        b"king 1 1 0\n"
        b"queen 1 0.9 0.1\n"
        b"man 0.9 0 0\n"
        b"woman 0.9 -0.1 0.1\n"
    )
    source = root / "vectors.txt"
    source.write_bytes(raw)
    manifest = Word2VecPackageManifest(
        package_id="pass218-i20-evidence",
        display_name="Pass 218 I20 evidence model",
        provider="HHS_PASS218_I20_EVIDENCE",
        source_uri=source.resolve().as_uri(),
        source_version="1",
        license_id="TEST-ONLY",
        license_uri="https://example.invalid/pass218-i20-test-license",
        expected_byte_length=len(raw),
        expected_sha256=sha256(raw).hexdigest(),
        archive_type="NONE",
        vector_format="WORD2VEC_TEXT",
        vector_dimension=3,
        vocabulary_size=4,
        normalization_profile="CASE_FOLDED",
    )
    service = Word2VecService(root / "pass166")
    service.register_manifest(manifest)
    installed = service.install(
        manifest.package_id,
        accept_license=True,
        activate=False,
        offline_ready=True,
    )
    return service, installed


def _binding(
    state_root: Path,
    service: Word2VecService,
    installed: dict,
    *,
    fence: int,
) -> Pass218Pass166ModelBinding:
    return Pass218Pass166ModelBinding(
        state_root=state_root,
        service=service,
        lifecycle=_Lifecycle(fence),
        postcondition_control=_Postcondition(),
        configuration=Pass218I20ModelConfiguration(
            model_id=installed["model_id"],
            expected_model_root=installed["canonical_model_root"],
            expected_index_root=installed["index_root"],
            activate_if_needed=True,
        ),
    )


def main() -> int:
    evidence_root = Path(".i20-evidence")
    if evidence_root.exists():
        shutil.rmtree(evidence_root)
    evidence_root.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="hhs-pass218-i20-") as temporary:
        runtime_root = Path(temporary)
        service, installed = _install_model(runtime_root)
        state_root = runtime_root / "pass218"

        first_binding = _binding(state_root, service, installed, fence=41)
        first = first_binding.synchronize()
        sealed = json.loads(first_binding.binding_path.read_text("utf-8"))
        activation_receipt = dict(sealed["pass166_activation_receipt"])
        verification_receipt = dict(sealed["pass166_verification_receipt"])
        first_operation_count = len(service._receipt_chain)

        restarted_binding = _binding(state_root, service, installed, fence=42)
        restarted = restarted_binding.synchronize()
        second_operation_count = len(service._receipt_chain)
        replayed = json.loads(restarted_binding.binding_path.read_text("utf-8"))

        provider = restarted_binding.exact_provider()
        relations = provider.exact_neighbors("king", top_k=2)

        assert first["relational_candidate_provider_ready"] is True
        assert first["activation_invocation_count"] == 1
        assert first["verification_invocation_count"] == 1
        assert first["binding_write_count"] == 1
        assert restarted["relational_candidate_provider_ready"] is True
        assert restarted["activation_invocation_count"] == 0
        assert restarted["verification_invocation_count"] == 0
        assert restarted["binding_write_count"] == 0
        assert second_operation_count == first_operation_count
        assert restarted["binding_hash72"] == first["binding_hash72"]
        assert replayed["pass166_activation_receipt"] == activation_receipt
        assert replayed["pass166_verification_receipt"] == verification_receipt
        assert replayed["binding_created_under_authority"]["distributed_fence_epoch"] == 41
        assert all(item.sign in (-1, 0, 1) for item in relations)
        for key in (
            "browser_model_activation_permitted",
            "canonical_learning_commit_invoked",
            "truth_promotion",
            "action_authority_minted",
            "pass165_source_retaining_learning_commit_invoked",
            "verbatim_corpus_source_retained",
            "authoritative_float_weights_created",
        ):
            assert restarted[key] is False

        evidence = {
            "schema": "HHS-P218-I20-GOVERNED-P166-MODEL-ACTIVATION-EVIDENCE-V1",
            "iteration": 20,
            "model_id": installed["model_id"],
            "canonical_model_root": installed["canonical_model_root"],
            "index_root": installed["index_root"],
            "binding_hash72": first["binding_hash72"],
            "activation_receipt": activation_receipt,
            "verification_receipt": verification_receipt,
            "first_writer_fence": 41,
            "restart_writer_fence": 42,
            "binding_creation_writer_fence": replayed["binding_created_under_authority"]["distributed_fence_epoch"],
            "pass166_operation_count_before_restart": first_operation_count,
            "pass166_operation_count_after_restart": second_operation_count,
            "restart_redispatch": False,
            "restart_reverification_receipt_emitted": False,
            "relational_candidates": [
                {
                    "token": item.token,
                    "rank": item.rank,
                    "sign": item.sign,
                    "evidence_hash72": item.evidence_hash72,
                }
                for item in relations
            ],
            "browser_model_activation_permitted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "pass165_source_retaining_learning_commit_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        target = evidence_root / "PASS218_I20_GOVERNED_PASS166_MODEL_ACTIVATION.json"
        target.write_text(
            json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n",
            "utf-8",
        )

    print("PASS218_I20_GOVERNED_PASS166_MODEL_ACTIVATION=1")
    print("PASS218_I20_STATUS_ONLY_BROWSER_SURFACE=1")
    print("PASS218_I20_RESTART_RECEIPT_IDEMPOTENT=1")
    print(f"PASS218_I20_BINDING_HASH72={evidence['binding_hash72']}")
    print(f"PASS218_I20_EVIDENCE={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
