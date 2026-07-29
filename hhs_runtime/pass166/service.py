"""Pass 166 governed acquisition, preinstallation, activation, and offline query service."""
from __future__ import annotations

from dataclasses import asdict, replace
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import tempfile
from threading import RLock
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass150.genome import Hash216Genome
from hhs_runtime.pass165.ingestion import MultimodalLearningService

from .codec import build_model, extract_package, parse_vectors
from .common import (
    CONTRACT_ID, IMPORT_PROFILE, INDEX_VERSION, MAX_PACKAGE_BYTES, PROJECTION_VERSION,
    QUANTIZATION_PROFILE, RUNTIME_VERSION, SCHEMA, SNAPSHOT_BYTES, ZERO_HASH216,
    InstalledModel, LanguageVectorObject, SimulatedInterruption, Word2VecError,
    Word2VecPackageManifest, atomic_write, canonical_bytes, root,
)


class Word2VecService:
    def __init__(self, root_path: str | Path | None = None, *, pass165: MultimodalLearningService | None = None) -> None:
        self.root = Path(root_path or os.environ.get("HHS_PASS166_STORAGE_DIR", ".hhs/pass166")).resolve()
        self.partial_dir = self.root / "downloads" / "partial"
        self.quarantine_dir = self.root / "downloads" / "quarantine"
        self.packages_dir = self.root / "models" / "word2vec" / "packages"
        self.active_dir = self.root / "models" / "word2vec" / "active"
        self.receipts_path = self.root / "receipts" / "operations.jsonl"
        self.registry_path = self.root / "models" / "word2vec" / "registry.json"
        self.active_path = self.active_dir / "active.json"
        for directory in (self.partial_dir, self.quarantine_dir, self.packages_dir, self.active_dir, self.receipts_path.parent):
            directory.mkdir(parents=True, exist_ok=True)
        self._pass165 = pass165 or MultimodalLearningService()
        self._manifests: dict[str, Word2VecPackageManifest] = {}
        self._models: dict[str, InstalledModel] = {}
        self._operations: dict[str, dict[str, Any]] = {}
        self._receipt_chain: list[dict[str, Any]] = []
        self._active_model_id: str | None = None
        self._lock = RLock()
        self._fault_after: str | None = None
        self._load()

    def _load(self) -> None:
        if self.registry_path.exists():
            raw = json.loads(self.registry_path.read_text("utf-8"))
            for item in raw.get("manifests", []):
                item["allowed_redirect_hosts"] = tuple(item.get("allowed_redirect_hosts", ()))
                item["compatibility_requirements"] = tuple(item.get("compatibility_requirements", ()))
                manifest = Word2VecPackageManifest(**item)
                self._manifests[manifest.package_id] = manifest
            self._models = {key: InstalledModel.from_serializable(value) for key, value in raw.get("models", {}).items()}
        if self.active_path.exists():
            self._active_model_id = json.loads(self.active_path.read_text("utf-8")).get("model_id")
        if self.receipts_path.exists():
            previous = ZERO_HASH216
            for line_number, line in enumerate(self.receipts_path.read_bytes().splitlines(), start=1):
                if not line:
                    continue
                envelope = json.loads(line)
                receipt = envelope["receipt"]
                if envelope.get("record_sha256") != sha256(canonical_bytes(receipt)).hexdigest() or receipt.get("previous_operation_hash216") != previous:
                    raise Word2VecError("P166_RECEIPT_CHAIN_TAMPER", str(line_number))
                previous = receipt["operation_hash216"]
                self._receipt_chain.append(receipt)
                self._operations[receipt["operation_id"]] = receipt

    def _persist_registry(self) -> None:
        body = {"schema": "P166_REGISTRY_V1", "manifests": [asdict(self._manifests[key]) for key in sorted(self._manifests)], "models": {key: self._models[key].serializable() for key in sorted(self._models)}}
        atomic_write(self.registry_path, canonical_bytes(body) + b"\n")

    def _persist_active(self, model_id: str | None) -> None:
        atomic_write(self.active_path, canonical_bytes({"schema": "P166_ACTIVE_MODEL_V1", "model_id": model_id}) + b"\n")
        self._active_model_id = model_id

    def _emit(self, stage: str, body: Mapping[str, Any], *, operation_id: str | None = None) -> dict[str, Any]:
        sequence = len(self._receipt_chain)
        previous = self._receipt_chain[-1]["operation_hash216"] if self._receipt_chain else ZERO_HASH216
        operation_id = operation_id or root(b"HHS-P166-OPERATION-ID-V1\0", {"stage": stage, "sequence": sequence, "body": body})
        operation = {"contract_id": CONTRACT_ID, "stage": stage, "sequence": sequence, "operation_id": operation_id, "body": dict(body), "previous_operation_hash216": previous}
        positions = Hash216Genome.positions(canonical_bytes(operation), previous_root=previous, sequence=sequence)
        receipt = {**operation, "operation_hash216": Hash216Genome.root(positions), "receipt_hash72": hash72_digest(operation, canonical_bytes(operation)), "classification": f"P166_{stage}_RECEIPT"}
        envelope = {"record_sha256": sha256(canonical_bytes(receipt)).hexdigest(), "receipt": receipt}
        with self.receipts_path.open("ab") as handle:
            handle.write(canonical_bytes(envelope) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._receipt_chain.append(receipt)
        self._operations[operation_id] = receipt
        return receipt

    def status(self) -> dict[str, Any]:
        return {"schema": SCHEMA, "classification": "HHS_PASS_166_WORD2VEC_PREINSTALLER_IMPLEMENTED", "registered_manifests": len(self._manifests), "installed_models": len(self._models), "active_model_id": self._active_model_id, "offline_ready": self._active_model_id in self._models, "worker_commit_authority": False, "vm81_commit_authority": True, "pass165_frontier": self._pass165.weight_root, "vm81_state_hash72": self._pass165._vm81.state_hash72}

    def register_manifest(self, manifest: Word2VecPackageManifest | Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(manifest, Word2VecPackageManifest):
            raw = dict(manifest)
            raw["allowed_redirect_hosts"] = tuple(raw.get("allowed_redirect_hosts", ()))
            raw["compatibility_requirements"] = tuple(raw.get("compatibility_requirements", ("PASS165", "VM81", "HASH72", "HASH216")))
            manifest = Word2VecPackageManifest(**raw)
        manifest.validate()
        existing = self._manifests.get(manifest.package_id)
        if existing and existing.manifest_root != manifest.manifest_root:
            raise Word2VecError("P166_MANIFEST_ID_CONFLICT", manifest.package_id)
        self._manifests[manifest.package_id] = manifest
        self._persist_registry()
        return {"package_id": manifest.package_id, "manifest_root": manifest.manifest_root, "registered": True}

    def list_models(self) -> list[dict[str, Any]]:
        values = []
        for model_id in sorted(set(self._manifests) | set(self._models)):
            manifest, model = self._manifests.get(model_id), self._models.get(model_id)
            values.append({"model_id": model_id, "manifest_root": manifest.manifest_root if manifest else model.manifest_root, "state": model.lifecycle_state if model else "RESOLVED", "active": model_id == self._active_model_id, "dimension": model.dimension if model else manifest.vector_dimension, "vocabulary_size": model.vocabulary_size if model else manifest.vocabulary_size})
        return values

    def inspect(self, model_id: str) -> dict[str, Any]:
        manifest, model = self._manifests.get(model_id), self._models.get(model_id)
        if manifest is None and model is None:
            raise Word2VecError("P166_MODEL_NOT_FOUND", model_id)
        return {"manifest": asdict(manifest) if manifest else None, "manifest_root": manifest.manifest_root if manifest else model.manifest_root, "model": model.serializable() if model else None, "active": model_id == self._active_model_id}

    def resolve(self, model_id: str, *, accept_license: bool) -> Word2VecPackageManifest:
        try:
            manifest = self._manifests[model_id]
        except KeyError as exc:
            raise Word2VecError("P166_UNREGISTERED_MODEL", model_id) from exc
        manifest.validate()
        if not accept_license:
            raise Word2VecError("P166_LICENSE_ACCEPTANCE_REQUIRED", manifest.license_id)
        self._emit("SOURCE_RESOLUTION", {"model_id": model_id, "manifest_root": manifest.manifest_root, "source_uri_identity": root(b"HHS-P166-SOURCE-URI-V1\0", manifest.source_uri)})
        self._emit("LICENSE_ACCEPTANCE", {"model_id": model_id, "license_id": manifest.license_id, "license_uri": manifest.license_uri, "accepted": True})
        return manifest

    def _copy_local(self, source: Path, target: Path, expected: int) -> None:
        if not source.is_file():
            raise Word2VecError("P166_SOURCE_NOT_FOUND", str(source))
        existing = target.stat().st_size if target.exists() else 0
        if existing > expected:
            target.unlink()
            existing = 0
        with source.open("rb") as incoming, target.open("ab") as outgoing:
            incoming.seek(existing)
            shutil.copyfileobj(incoming, outgoing, 1024 * 1024)
            outgoing.flush()
            os.fsync(outgoing.fileno())

    def _download_https(self, manifest: Word2VecPackageManifest, target: Path) -> None:
        parsed = urlparse(manifest.source_uri)
        allowed = {parsed.hostname, *manifest.allowed_redirect_hosts}
        existing = target.stat().st_size if target.exists() else 0
        request = Request(manifest.source_uri, headers={"Range": f"bytes={existing}-"} if existing else {}, method="GET")
        try:
            with urlopen(request, timeout=30) as response:
                final = urlparse(response.geturl())
                if final.scheme != "https" or final.hostname not in allowed:
                    raise Word2VecError("P166_REDIRECT_HOST_REJECTED", response.geturl())
                mode = "ab" if existing and getattr(response, "status", 200) == 206 else "wb"
                total = existing if mode == "ab" else 0
                with target.open(mode) as handle:
                    while True:
                        block = response.read(1024 * 1024)
                        if not block:
                            break
                        total += len(block)
                        if total > manifest.expected_byte_length or total > MAX_PACKAGE_BYTES:
                            raise Word2VecError("P166_PACKAGE_SIZE_BOUND")
                        handle.write(block)
                    handle.flush(); os.fsync(handle.fileno())
        except Word2VecError:
            raise
        except Exception as exc:
            raise Word2VecError("P166_NETWORK_TRANSFER_FAILED", str(exc)) from exc

    def download(self, manifest: Word2VecPackageManifest) -> Path:
        part = self.partial_dir / f"{manifest.package_id}.part"
        parsed = urlparse(manifest.source_uri)
        self._copy_local(Path(parsed.path), part, manifest.expected_byte_length) if parsed.scheme == "file" else self._download_https(manifest, part)
        size, digest = part.stat().st_size, sha256(part.read_bytes()).hexdigest()
        if size != manifest.expected_byte_length:
            raise Word2VecError("P166_BYTE_LENGTH_MISMATCH", f"{size}!={manifest.expected_byte_length}")
        if digest != manifest.expected_sha256:
            raise Word2VecError("P166_DIGEST_MISMATCH", digest)
        final = self.quarantine_dir / f"{manifest.package_id}.{digest}.package"
        os.replace(part, final)
        self._emit("DOWNLOAD", {"model_id": manifest.package_id, "bytes": size, "package_digest": digest, "resumable": True})
        self._emit("INTEGRITY_VERIFICATION", {"model_id": manifest.package_id, "byte_verified": True, "digest_verified": True, "package_digest": digest})
        return final

    def _admit(self, model_root: str, objects: Sequence[LanguageVectorObject], expected_frontier: str | None) -> dict[str, Any]:
        if expected_frontier is not None and expected_frontier != self._pass165.weight_root:
            raise Word2VecError("P166_STALE_PASS165_FRONTIER")
        vm81, incoming = self._pass165._vm81, self._pass165._vm81.state_hash72
        for item in objects:
            vm81.register_parameter(type="P166_WORD2VEC_DENSE_VECTOR_REFERENCE", value={"lexical_object_id": item.lexical_object_id, "canonical_vector_identity": item.canonical_vector_identity, "dimension": item.dimensionality}, domain="LANGUAGE_MODALITY_VECTOR_STORE", phase=int(item.lexical_object_id[:8], 16) % 72, operator="IMMUTABLE_VECTOR_REFERENCE", constraints=("P166_EXACT_QUANTIZATION", "P166_SOURCE_PRESERVED", "P165_5184_PROJECTION"), provenance=item.provenance_root)
        digest = sha256(bytes.fromhex(model_root)).digest()
        candidate = vm81.submit_candidate(thread=61, writes={digest[index] % 81: 1 for index in range(16)}, operation="VMRC_COMMIT", expected_input_hash72=incoming, dependency_root=model_root, capability_scope="P166_MODEL_ACTIVATION", source_architecture="P166_REFERENCE_CPU", target_architecture="VM81")
        result = vm81.execute(candidate)
        return {"incoming_hash72": incoming, "outgoing_hash72": vm81.state_hash72, "vm81_commit_receipt": result["commit"]["receipt"]}

    def install(self, model_id: str, *, accept_license: bool, activate: bool = True, offline_ready: bool = True, replace_existing: bool = False, expected_pass165_frontier: str | None = None) -> dict[str, Any]:
        with self._lock:
            manifest = self.resolve(model_id, accept_license=accept_license)
            idempotence = root(b"HHS-P166-IDEMPOTENCE-V1\0", {"package_digest": manifest.expected_sha256, "manifest_root": manifest.manifest_root, "runtime_version": RUNTIME_VERSION, "import_profile": manifest.import_profile, "quantization_profile": manifest.quantization_profile, "projection_version": manifest.projection_version, "index_version": manifest.index_version})
            existing = self._models.get(model_id)
            if existing and existing.idempotence_key == idempotence:
                return {**dict(existing.terminal_receipt), "classification": "P166_IDEMPOTENT_INSTALL_REUSED", "reused": True}
            if existing and not replace_existing:
                raise Word2VecError("P166_REPAIR_REQUIRED", model_id)
            operation_id = root(b"HHS-P166-INSTALL-V1\0", {"model_id": model_id, "idempotence_key": idempotence, "pass165_frontier": self._pass165.weight_root})
            operation_dir = self.quarantine_dir / operation_id
            operation_dir.mkdir(parents=True, exist_ok=True)
            package = self.download(manifest)
            artifact = extract_package(manifest, package, operation_dir)
            vectors = parse_vectors(artifact, manifest)
            self._emit("FORMAT_VERIFICATION", {"model_id": model_id, "format": manifest.vector_format, "dimension": manifest.vector_dimension, "vocabulary_size": manifest.vocabulary_size, "verified": True})
            self._emit("IMPORT", {"model_id": model_id, "rows": len(vectors), "source_vector_root": root(b"HHS-P166-SOURCE-VECTOR-SET-V1\0", [item.source_vector_digest for item in vectors])})
            model_root, index_root, objects, aliases = build_model(manifest, manifest.expected_sha256, vectors)
            self._emit("CANONICAL_CONVERSION", {"model_id": model_id, "canonical_model_root": model_root, "quantization_profile": QUANTIZATION_PROFILE, "cross_architecture_integer_identity": True})
            self._emit("INDEX_BUILD", {"model_id": model_id, "index_root": index_root, "index_version": INDEX_VERSION, "exact": True})
            replay_vectors = parse_vectors(artifact, manifest)
            replay_root, replay_index, replay_objects, replay_aliases = build_model(manifest, manifest.expected_sha256, replay_vectors)
            if (replay_root, replay_index, tuple(item.projection_5184_root for item in replay_objects), replay_aliases) != (model_root, index_root, tuple(item.projection_5184_root for item in objects), aliases):
                raise Word2VecError("P166_NONDETERMINISTIC_CONVERSION")
            self._emit("COMPATIBILITY_VALIDATION", {"model_id": model_id, "pass165_projection_bytes": SNAPSHOT_BYTES, "deterministic_reimport": True, "offline_ready": bool(offline_ready)}, operation_id=operation_id)
            prior_active = self._active_model_id
            prior_active_bytes = self.active_path.read_bytes() if self.active_path.exists() else None
            try:
                if activate and self._fault_after == "before_vm81_admission":
                    raise SimulatedInterruption("before_vm81_admission")
                admission = self._admit(model_root, objects, expected_pass165_frontier) if activate else {"incoming_hash72": self._pass165._vm81.state_hash72, "outgoing_hash72": self._pass165._vm81.state_hash72}
                package_target = self.packages_dir / model_id / manifest.expected_sha256
                package_target.mkdir(parents=True, exist_ok=True)
                shutil.copy2(package, package_target / "source.package")
                terminal_body = {"operation_id": operation_id, "package_id": manifest.package_id, "source_uri_identity": root(b"HHS-P166-SOURCE-URI-V1\0", manifest.source_uri), "package_digest": manifest.expected_sha256, "manifest_root": manifest.manifest_root, "license_identity": manifest.license_id, "runtime_version": RUNTIME_VERSION, "source_vector_format": manifest.vector_format, "source_dimension": manifest.vector_dimension, "source_vocabulary_size": manifest.vocabulary_size, "canonical_conversion_profile": QUANTIZATION_PROFILE, "canonical_model_root": model_root, "projection_registry_version": PROJECTION_VERSION, "index_root": index_root, "pass165_vector_store_frontier": self._pass165.weight_root, "incoming_hash72": admission["incoming_hash72"], "outgoing_hash72": admission["outgoing_hash72"], "hash216_installation_identity": self._receipt_chain[-1]["operation_hash216"], "activation_state": "ACTIVE" if activate else "INSTALLED", "offline_ready": bool(offline_ready), "replay_result": "DETERMINISTIC_REIMPORT_PASS"}
                terminal = self._emit("ACTIVATION" if activate else "INSTALLATION", terminal_body, operation_id=operation_id)
                self._models[model_id] = InstalledModel(model_id, manifest.package_id, manifest.manifest_root, manifest.expected_sha256, manifest.vector_format, manifest.vector_dimension, manifest.vocabulary_size, model_root, index_root, idempotence, "ACTIVE" if activate else "INSTALLED", activate, vectors, objects, aliases, terminal)
                self._persist_registry()
                if activate:
                    self._persist_active(model_id)
                return {**terminal, "model_id": model_id, "canonical_model_root": model_root, "index_root": index_root, "reused": False}
            except Exception:
                self._models.pop(model_id, None); self._persist_registry()
                if prior_active_bytes is None:
                    self.active_path.unlink(missing_ok=True); self._active_model_id = None
                else:
                    atomic_write(self.active_path, prior_active_bytes); self._active_model_id = prior_active
                self._emit("ROLLBACK", {"model_id": model_id, "restored_active_model": prior_active, "rollback_complete": True}, operation_id=operation_id)
                raise

    def _model(self, model_id: str | None = None) -> InstalledModel:
        selected = model_id or self._active_model_id
        if selected is None or selected not in self._models:
            raise Word2VecError("P166_MODEL_NOT_INSTALLED", str(selected))
        return self._models[selected]

    def verify(self, model_id: str) -> dict[str, Any]:
        model, manifest = self._model(model_id), self._manifests.get(model_id)
        if manifest is None or manifest.manifest_root != model.manifest_root:
            raise Word2VecError("P166_MANIFEST_MODEL_IDENTITY_MISMATCH")
        model_root, index_root, objects, aliases = build_model(manifest, model.package_digest, model.vectors)
        if model_root != model.canonical_model_root:
            raise Word2VecError("P166_CANONICAL_MODEL_ROOT_MISMATCH")
        if index_root != model.index_root or aliases != model.aliases or tuple(item.projection_5184_root for item in objects) != tuple(item.projection_5184_root for item in model.objects):
            raise Word2VecError("P166_INDEX_MODEL_IDENTITY_MISMATCH")
        receipt = self._emit("COMPATIBILITY_VALIDATION", {"model_id": model_id, "canonical_model_root": model_root, "index_root": index_root, "verified": True})
        return {"classification": "P166_MODEL_VERIFIED", "model_id": model_id, "verified": True, "receipt": receipt}

    def activate(self, model_id: str, *, expected_pass165_frontier: str | None = None) -> dict[str, Any]:
        with self._lock:
            model = self._model(model_id)
            admission = self._admit(model.canonical_model_root, model.objects, expected_pass165_frontier)
            self._persist_active(model_id); self._models[model_id] = replace(model, lifecycle_state="ACTIVE", active=True); self._persist_registry()
            return {"classification": "P166_MODEL_ACTIVATED", "model_id": model_id, "receipt": self._emit("ACTIVATION", {"model_id": model_id, **admission, "active": True})}

    def deactivate(self, model_id: str) -> dict[str, Any]:
        with self._lock:
            model = self._model(model_id)
            if self._active_model_id == model_id:
                self._persist_active(None)
            self._models[model_id] = replace(model, lifecycle_state="INSTALLED", active=False); self._persist_registry()
            return {"classification": "P166_MODEL_DEACTIVATED", "model_id": model_id, "receipt": self._emit("ACTIVATION", {"model_id": model_id, "active": False})}

    def remove(self, model_id: str, *, purge_package: bool = False) -> dict[str, Any]:
        with self._lock:
            if model_id == self._active_model_id:
                self._persist_active(None)
            model = self._models.pop(model_id, None)
            if model is None:
                raise Word2VecError("P166_MODEL_NOT_INSTALLED", model_id)
            if purge_package:
                shutil.rmtree(self.packages_dir / model_id, ignore_errors=True)
            self._persist_registry()
            return {"classification": "P166_MODEL_REMOVED", "model_id": model_id, "receipt": self._emit("REMOVAL", {"model_id": model_id, "purge_package": purge_package, "historical_receipts_preserved": True})}

    def repair(self, model_id: str) -> dict[str, Any]:
        try:
            return {"classification": "P166_REPAIR_NOT_REQUIRED", **self.verify(model_id)}
        except Word2VecError:
            manifest = self._manifests.get(model_id)
            if manifest is None:
                raise
            was_active = self._active_model_id == model_id
            self._models.pop(model_id, None); self._persist_registry()
            return {"classification": "P166_MODEL_REPAIRED", "result": self.install(model_id, accept_license=True, activate=was_active, offline_ready=True, replace_existing=True)}

    def get_operation(self, operation_id: str) -> dict[str, Any]:
        try:
            return json.loads(canonical_bytes(self._operations[operation_id]))
        except KeyError as exc:
            raise Word2VecError("P166_OPERATION_NOT_FOUND", operation_id) from exc

    def vector(self, token: str, *, model_id: str | None = None, include_projection_5184: bool = True, include_provenance: bool = True) -> dict[str, Any]:
        model = self._model(model_id)
        names = [token] if any(item.decoded_token == token for item in model.vectors) else list(model.aliases.get(token, ()))
        vector = next((item for item in model.vectors if item.decoded_token in names), None)
        if vector is None:
            raise Word2VecError("P166_TOKEN_NOT_FOUND", token)
        obj = next(item for item in model.objects if item.canonical_vector_identity == vector.canonical_vector_digest)
        result = {"model_id": model.model_id, "canonical_model_root": model.canonical_model_root, "import_profile": IMPORT_PROFILE, "quantization_profile": QUANTIZATION_PROFILE, "token": vector.decoded_token, "aliases": list(obj.normalized_aliases), "vector_identity": vector.canonical_vector_digest, "dimension": vector.dimension, "denominator": vector.denominator, "canonical_values": list(vector.canonical_values)}
        if include_projection_5184:
            result.update({"projection_5184_b64": obj.projection_5184_b64, "projection_5184_root": obj.projection_5184_root})
        if include_provenance:
            result["provenance_root"] = obj.provenance_root
        return result

    @staticmethod
    def _similarity_key(left: Sequence[int], right: Sequence[int]) -> tuple[int, Fraction]:
        dot, left_norm, right_norm = sum(a * b for a, b in zip(left, right)), sum(a * a for a in left), sum(b * b for b in right)
        if left_norm == 0 or right_norm == 0:
            return 0, Fraction(0, 1)
        return (-1 if dot < 0 else 1 if dot > 0 else 0), Fraction(dot * dot, left_norm * right_norm)

    def similarity(self, left: str, right: str, *, model_id: str | None = None) -> dict[str, Any]:
        l = self.vector(left, model_id=model_id, include_projection_5184=False, include_provenance=False); r = self.vector(right, model_id=model_id, include_projection_5184=False, include_provenance=False)
        sign, squared = self._similarity_key(l["canonical_values"], r["canonical_values"])
        return {"model_id": model_id or self._active_model_id, "left": l["token"], "right": r["token"], "cosine_sign": sign, "cosine_squared_exact": f"{squared.numerator}/{squared.denominator}", "exact_ranking": True}

    def nearest(self, token: str, *, model_id: str | None = None, top_k: int = 16) -> dict[str, Any]:
        if not 1 <= top_k <= 256:
            raise Word2VecError("P166_TOP_K_BOUND")
        model = self._model(model_id); target = self.vector(token, model_id=model.model_id, include_projection_5184=False, include_provenance=False)
        ranked = []
        for candidate in model.vectors:
            if candidate.decoded_token != target["token"]:
                sign, squared = self._similarity_key(target["canonical_values"], candidate.canonical_values); ranked.append((sign, squared, candidate.decoded_token, candidate.canonical_vector_digest))
        ranked.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        return {"model_id": model.model_id, "token": target["token"], "index_version": INDEX_VERSION, "approximate": False, "results": [{"token": item[2], "cosine_sign": item[0], "cosine_squared_exact": f"{item[1].numerator}/{item[1].denominator}", "vector_identity": item[3]} for item in ranked[:top_k]]}

    def analogy(self, positive: Sequence[str], negative: Sequence[str] = (), *, model_id: str | None = None, top_k: int = 16) -> dict[str, Any]:
        model = self._model(model_id)
        if not positive:
            raise Word2VecError("P166_ANALOGY_POSITIVE_REQUIRED")
        vectors = {item.decoded_token: item for item in model.vectors}; target = [0] * model.dimension
        try:
            for token in positive:
                target = [a + b for a, b in zip(target, vectors[token].canonical_values)]
            for token in negative:
                target = [a - b for a, b in zip(target, vectors[token].canonical_values)]
        except KeyError as exc:
            raise Word2VecError("P166_TOKEN_NOT_FOUND", str(exc)) from exc
        excluded, ranked = set(positive) | set(negative), []
        for candidate in model.vectors:
            if candidate.decoded_token not in excluded:
                sign, squared = self._similarity_key(target, candidate.canonical_values); ranked.append((sign, squared, candidate.decoded_token, candidate.canonical_vector_digest))
        ranked.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        return {"model_id": model.model_id, "positive": list(positive), "negative": list(negative), "results": [{"token": item[2], "cosine_sign": item[0], "cosine_squared_exact": f"{item[1].numerator}/{item[1].denominator}", "vector_identity": item[3]} for item in ranked[:top_k]]}

    def project(self, token: str, *, model_id: str | None = None) -> dict[str, Any]:
        result = self.vector(token, model_id=model_id, include_projection_5184=True, include_provenance=True)
        return {key: result[key] for key in ("model_id", "token", "vector_identity", "projection_5184_b64", "projection_5184_root", "provenance_root")}

    def replay(self, model_id: str) -> dict[str, Any]:
        model, manifest = self._model(model_id), self._manifests[model_id]
        package = self.packages_dir / model_id / model.package_digest / "source.package"
        if not package.is_file() or sha256(package.read_bytes()).hexdigest() != model.package_digest:
            raise Word2VecError("P166_OFFLINE_DEPENDENCY_OMISSION")
        with tempfile.TemporaryDirectory(prefix="p166-replay-") as temporary:
            artifact = extract_package(manifest, package, Path(temporary)); vectors = parse_vectors(artifact, manifest); model_root, index_root, objects, aliases = build_model(manifest, model.package_digest, vectors)
        if (model_root, index_root, tuple(item.projection_5184_root for item in objects), aliases) != (model.canonical_model_root, model.index_root, tuple(item.projection_5184_root for item in model.objects), model.aliases):
            raise Word2VecError("P166_REPLAY_DIVERGENCE")
        receipt = self._emit("COMPATIBILITY_VALIDATION", {"model_id": model_id, "replay": True, "canonical_model_root": model_root, "index_root": index_root})
        return {"classification": "P166_DETERMINISTIC_REPLAY_RECEIPT", "model_id": model_id, "canonical_model_root": model_root, "index_root": index_root, "records": model.vocabulary_size, "deterministic_replay": True, "receipt": receipt}


DEFAULT_WORD2VEC_SERVICE = Word2VecService()
