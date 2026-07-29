"""Deterministic Pass 166 archive, Word2Vec, projection, and index codecs."""
from __future__ import annotations

from base64 import b64decode, b64encode
from hashlib import sha256
from pathlib import Path
import io
import shutil
import tarfile
from typing import Sequence
import unicodedata
import zipfile

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

from .common import (
    COORDINATES,
    INDEX_VERSION,
    MAX_EXTRACTED_BYTES,
    PROJECTION_VERSION,
    QUANTIZATION_PROFILE,
    SNAPSHOT_BYTES,
    CanonicalVector,
    LanguageVectorObject,
    Word2VecError,
    Word2VecPackageManifest,
    decimal_fraction,
    float32_fraction,
    root,
    safe_member,
)


def extract_package(manifest: Word2VecPackageManifest, package_path: Path, operation_dir: Path) -> Path:
    if manifest.archive_type == "NONE":
        return package_path
    extraction = operation_dir / "extracted"
    extraction.mkdir(parents=True, exist_ok=True)
    candidates: list[Path] = []
    if manifest.archive_type == "ZIP":
        try:
            with zipfile.ZipFile(package_path) as archive:
                total = 0
                seen: set[str] = set()
                for info in archive.infolist():
                    relative = safe_member(info.filename)
                    if info.filename in seen:
                        raise Word2VecError("P166_DUPLICATE_ARCHIVE_ENTRY", info.filename)
                    seen.add(info.filename)
                    if info.is_dir():
                        continue
                    mode = (info.external_attr >> 16) & 0o170000
                    if mode == 0o120000:
                        raise Word2VecError("P166_ARCHIVE_SYMLINK_REJECTED")
                    total += info.file_size
                    if total > MAX_EXTRACTED_BYTES or (info.compress_size and info.file_size > max(64 * 1024 * 1024, info.compress_size * 200)):
                        raise Word2VecError("P166_DECOMPRESSION_BOMB")
                    target = extraction / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, target.open("wb") as destination:
                        shutil.copyfileobj(source, destination)
                    candidates.append(target)
        except Word2VecError:
            raise
        except Exception as exc:
            raise Word2VecError("P166_ARCHIVE_INTEGRITY_FAILED", str(exc)) from exc
    else:
        mode = "r:gz" if manifest.archive_type == "TAR_GZ" else "r:"
        try:
            with tarfile.open(package_path, mode) as archive:
                total = 0
                seen: set[str] = set()
                for info in archive.getmembers():
                    relative = safe_member(info.name)
                    if info.name in seen:
                        raise Word2VecError("P166_DUPLICATE_ARCHIVE_ENTRY", info.name)
                    seen.add(info.name)
                    if info.issym() or info.islnk() or info.isdev():
                        raise Word2VecError("P166_UNSAFE_ARCHIVE_MEMBER", info.name)
                    if not info.isfile():
                        continue
                    total += info.size
                    if total > MAX_EXTRACTED_BYTES:
                        raise Word2VecError("P166_DECOMPRESSION_BOMB")
                    source = archive.extractfile(info)
                    if source is None:
                        raise Word2VecError("P166_ARCHIVE_INTEGRITY_FAILED")
                    target = extraction / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with source, target.open("wb") as destination:
                        shutil.copyfileobj(source, destination)
                    candidates.append(target)
        except Word2VecError:
            raise
        except Exception as exc:
            raise Word2VecError("P166_ARCHIVE_INTEGRITY_FAILED", str(exc)) from exc
    if manifest.artifact_path:
        artifact = extraction / safe_member(manifest.artifact_path)
        if not artifact.is_file():
            raise Word2VecError("P166_DECLARED_ARTIFACT_MISSING")
        return artifact
    if len(candidates) != 1:
        raise Word2VecError("P166_AMBIGUOUS_ARCHIVE_ROOT", str(len(candidates)))
    return candidates[0]


def parse_text(raw: bytes, manifest: Word2VecPackageManifest) -> tuple[CanonicalVector, ...]:
    try:
        text = raw.decode(manifest.character_encoding)
    except UnicodeDecodeError as exc:
        raise Word2VecError("P166_INVALID_TOKEN_ENCODING") from exc
    lines = text.splitlines()
    if not lines:
        raise Word2VecError("P166_MALFORMED_WORD2VEC_HEADER")
    header = lines[0].split()
    if len(header) != 2:
        raise Word2VecError("P166_MALFORMED_WORD2VEC_HEADER")
    try:
        vocabulary, dimension = int(header[0]), int(header[1])
    except ValueError as exc:
        raise Word2VecError("P166_MALFORMED_WORD2VEC_HEADER") from exc
    if vocabulary != manifest.vocabulary_size or dimension != manifest.vector_dimension:
        raise Word2VecError("P166_MODEL_GEOMETRY_MISMATCH")
    vectors: list[CanonicalVector] = []
    seen: set[bytes] = set()
    for row, line in enumerate(lines[1:]):
        fields = line.split()
        if len(fields) != dimension + 1:
            raise Word2VecError("P166_MIXED_VECTOR_DIMENSIONS", str(row))
        token = fields[0].encode(manifest.character_encoding)
        if token in seen:
            raise Word2VecError("P166_DUPLICATE_TOKEN_CONFLICT", fields[0])
        seen.add(token)
        vectors.append(CanonicalVector.create(token, fields[0], row, [decimal_fraction(value) for value in fields[1:]], "DECIMAL_TEXT"))
    if len(vectors) != vocabulary:
        raise Word2VecError("P166_VOCABULARY_COUNT_MISMATCH")
    return tuple(vectors)


def parse_binary(raw: bytes, manifest: Word2VecPackageManifest) -> tuple[CanonicalVector, ...]:
    stream = io.BytesIO(raw)
    header = stream.readline().strip().split()
    if len(header) != 2:
        raise Word2VecError("P166_MALFORMED_WORD2VEC_HEADER")
    try:
        vocabulary, dimension = int(header[0]), int(header[1])
    except ValueError as exc:
        raise Word2VecError("P166_MALFORMED_WORD2VEC_HEADER") from exc
    if vocabulary != manifest.vocabulary_size or dimension != manifest.vector_dimension:
        raise Word2VecError("P166_MODEL_GEOMETRY_MISMATCH")
    vectors: list[CanonicalVector] = []
    seen: set[bytes] = set()
    for row in range(vocabulary):
        token = bytearray()
        while True:
            byte = stream.read(1)
            if not byte:
                raise Word2VecError("P166_TRUNCATED_WORD2VEC_BINARY", str(row))
            if byte == b" ":
                break
            if byte not in (b"\n", b"\r"):
                token.extend(byte)
        token_bytes = bytes(token)
        if not token_bytes or token_bytes in seen:
            raise Word2VecError("P166_DUPLICATE_TOKEN_CONFLICT" if token_bytes else "P166_INVALID_TOKEN_ENCODING")
        seen.add(token_bytes)
        try:
            decoded = token_bytes.decode(manifest.character_encoding)
        except UnicodeDecodeError as exc:
            raise Word2VecError("P166_INVALID_TOKEN_ENCODING") from exc
        vector_raw = stream.read(dimension * 4)
        if len(vector_raw) != dimension * 4:
            raise Word2VecError("P166_TRUNCATED_WORD2VEC_BINARY", str(row))
        values = [float32_fraction(vector_raw[index : index + 4]) for index in range(0, len(vector_raw), 4)]
        vectors.append(CanonicalVector.create(token_bytes, decoded, row, values, "IEEE754_BINARY32_BITS"))
        separator = stream.read(1)
        if separator not in (b"", b"\n", b"\r", b" "):
            stream.seek(-1, io.SEEK_CUR)
    return tuple(vectors)


def parse_vectors(path: Path, manifest: Word2VecPackageManifest) -> tuple[CanonicalVector, ...]:
    raw = path.read_bytes()
    return parse_text(raw, manifest) if manifest.vector_format == "WORD2VEC_TEXT" else parse_binary(raw, manifest)


def normalize(token: str, profile: str) -> tuple[str, ...]:
    aliases = {token}
    if profile == "UNICODE_NFC":
        aliases.add(unicodedata.normalize("NFC", token))
    elif profile == "UNICODE_NFKC":
        aliases.add(unicodedata.normalize("NFKC", token))
    elif profile == "CASE_FOLDED":
        aliases.add(unicodedata.normalize("NFKC", token).casefold())
    return tuple(sorted(aliases))


def projection(vector: CanonicalVector, model_root: str, aliases: Sequence[str]) -> bytes:
    raw = bytearray(SNAPSHOT_BYTES)
    identities = [f"MODEL:{model_root}", f"TOKEN:{vector.source_token_b64}", f"VECTOR:{vector.canonical_vector_digest}", *(f"ALIAS:{alias}" for alias in aliases)]
    identities.extend(f"COMPONENT:{index}:{value // 4096}:{-1 if value < 0 else 1}" for index, value in enumerate(vector.canonical_values))
    for identity in identities:
        digest = sha256(b"HHS-P166-PROJECTION-V1\0" + identity.encode()).digest()
        for offset in (0, 2, 4, 6):
            coordinate = int.from_bytes(digest[offset : offset + 2], "big") % COORDINATES
            byte_index, bit_index = divmod(coordinate, 8)
            raw[byte_index] |= 1 << (7 - bit_index)
    return bytes(raw)


def build_model(manifest: Word2VecPackageManifest, package_digest: str, vectors: tuple[CanonicalVector, ...]) -> tuple[str, str, tuple[LanguageVectorObject, ...], dict[str, tuple[str, ...]]]:
    model_root = root(b"HHS-P166-CANONICAL-MODEL-V1\0", {"manifest_root": manifest.manifest_root, "quantization_profile": QUANTIZATION_PROFILE, "vectors": [item.canonical_vector_digest for item in vectors]})
    alias_map: dict[str, list[str]] = {}
    pending: list[dict[str, object]] = []
    for vector in vectors:
        aliases = normalize(vector.decoded_token, manifest.normalization_profile)
        for alias in aliases:
            alias_map.setdefault(alias, []).append(vector.decoded_token)
        frame = projection(vector, model_root, aliases)
        pending.append({
            "lexical_object_id": root(b"HHS-P166-LEXICAL-OBJECT-V1\0", {"model_root": model_root, "token": vector.source_token_b64, "vector": vector.canonical_vector_digest}),
            "source_token_identity": sha256(b64decode(vector.source_token_b64)).hexdigest(),
            "decoded_token": vector.decoded_token,
            "normalized_aliases": aliases,
            "canonical_vector_identity": vector.canonical_vector_digest,
            "dimensionality": vector.dimension,
            "source_model_identity": model_root,
            "projection_5184_b64": b64encode(frame).decode("ascii"),
            "projection_5184_root": hash72_digest({"model_root": model_root, "vector": vector.canonical_vector_digest, "projection_version": PROJECTION_VERSION}, frame),
            "provenance_root": root(b"HHS-P166-PROVENANCE-V1\0", {"package_digest": package_digest, "manifest_root": manifest.manifest_root, "source_vector_digest": vector.source_vector_digest}),
        })
    aliases = {key: tuple(sorted(value)) for key, value in sorted(alias_map.items())}
    index_root = root(b"HHS-P166-INDEX-V1\0", {"index_version": INDEX_VERSION, "model_root": model_root, "exact_tokens": [item.decoded_token for item in vectors], "aliases": aliases, "vectors": [item.canonical_vector_digest for item in vectors]})
    objects = tuple(LanguageVectorObject(**{**item, "relation_index_root": index_root}) for item in pending)
    return model_root, index_root, objects, aliases
