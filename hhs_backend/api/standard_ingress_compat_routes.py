"""Standard/legacy frontend ingress compatibility routes.

These routes are a transport membrane only. They translate ordinary Linux/web
payload forms into the existing workspace ingress command and never create a
second runtime, VM81, receipt, or persistence authority.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from email import policy
from email.parser import BytesParser
import json
import os
from typing import Any, Mapping
from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Request

from hhs_backend.runtime.multimodal_workspace_ingress_v1 import (
    LEGACY_MODALITY_ALIASES,
    MIME_MODALITY_MAP,
    SUPPORTED_MODALITIES,
)

VERSION = "HHS_STANDARD_LEGACY_INGRESS_COMPAT_V1"
DEFAULT_MAX_INGRESS_BYTES = 64 * 1024 * 1024
MAX_CONFIGURED_INGRESS_BYTES = 256 * 1024 * 1024

LEGACY_ROUTE_ALIASES = (
    "/api/runtime/ingress",
    "/api/runtime/ingress/legacy",
    "/api/runtime/ingress/upload",
    "/api/ingress",
)

LINUX_COMPATIBILITY_SURFACES = (
    "HTTP_REQUEST_BODY",
    "JSON",
    "TEXT",
    "URLENCODED_FORM",
    "MULTIPART_FORM",
    "RAW_BYTES",
    "FILESYSTEM",
    "STDIN_STDOUT_PROCESS",
    "UNIX_DOMAIN_SOCKET",
    "HTTP_CLIENT",
)


def _configured_max_bytes() -> int:
    raw = os.environ.get("HHS_STANDARD_INGRESS_MAX_BYTES", "").strip()
    if not raw:
        return DEFAULT_MAX_INGRESS_BYTES
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError("HHS_STANDARD_INGRESS_MAX_BYTES_INVALID") from exc
    if value < 1 or value > MAX_CONFIGURED_INGRESS_BYTES:
        raise RuntimeError("HHS_STANDARD_INGRESS_MAX_BYTES_OUT_OF_RANGE")
    return value


def _base_media_type(content_type: str | None) -> str:
    return str(content_type or "").split(";", 1)[0].strip().lower()


def _charset(content_type: str | None, default: str = "utf-8") -> str:
    raw = str(content_type or "")
    for item in raw.split(";")[1:]:
        key, sep, value = item.strip().partition("=")
        if sep and key.lower() == "charset" and value.strip():
            return value.strip().strip('"')
    return default


async def _read_bounded_body(request: Request, limit: int) -> bytes:
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > limit:
                raise HTTPException(
                    status_code=413,
                    detail={
                        "classification": "HHS_STANDARD_INGRESS_BODY_TOO_LARGE",
                        "limit_bytes": limit,
                    },
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={"classification": "HHS_STANDARD_INGRESS_CONTENT_LENGTH_INVALID"},
            )

    chunks: list[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                status_code=413,
                detail={
                    "classification": "HHS_STANDARD_INGRESS_BODY_TOO_LARGE",
                    "limit_bytes": limit,
                },
            )
        chunks.append(bytes(chunk))
    return b"".join(chunks)


def _form_scalar(values: Mapping[str, list[str]], name: str) -> str | None:
    items = values.get(name) or []
    return items[-1] if items else None


def _parse_multipart(body: bytes, content_type: str) -> dict[str, Any]:
    synthetic = (
        f"Content-Type: {content_type}\r\n"
        "MIME-Version: 1.0\r\n"
        "\r\n"
    ).encode("utf-8") + body
    message = BytesParser(policy=policy.default).parsebytes(synthetic)
    if not message.is_multipart():
        return {
            "mode": "MULTIPART_RAW_FALLBACK",
            "payload": body,
            "source_name": "multipart-upload.bin",
            "declared_modality": "BINARY",
            "media_type": content_type,
            "fields": {},
            "part_count": 0,
        }

    fields: dict[str, str] = {}
    files: list[dict[str, Any]] = []
    part_records: list[dict[str, Any]] = []

    for index, part in enumerate(message.iter_parts()):
        disposition = part.get_content_disposition()
        name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        part_type = part.get_content_type() or "application/octet-stream"
        raw = part.get_payload(decode=True) or b""
        record = {
            "index": index,
            "name": name,
            "filename": filename,
            "content_type": part_type,
            "size_bytes": len(raw),
            "data_b64": b64encode(raw).decode("ascii"),
        }
        part_records.append(record)

        if disposition == "form-data" and filename:
            files.append(record)
            continue

        if disposition == "form-data" and name:
            charset = part.get_content_charset() or "utf-8"
            try:
                fields[str(name)] = raw.decode(charset)
            except (LookupError, UnicodeDecodeError):
                fields[str(name)] = raw.decode("utf-8", errors="replace")

    if len(files) == 1:
        file_record = files[0]
        return {
            "mode": "MULTIPART_SINGLE_FILE",
            "payload": b64decode(file_record["data_b64"]),
            "source_name": str(file_record.get("filename") or "upload.bin"),
            "declared_modality": fields.get("declared_modality") or fields.get("source_modality"),
            "media_type": str(file_record.get("content_type") or "application/octet-stream"),
            "fields": fields,
            "part_count": len(part_records),
        }

    return {
        "mode": "MULTIPART_BUNDLE",
        "payload": {
            "schema": "HHS_MULTIPART_SOURCE_BUNDLE_V1",
            "parts": part_records,
            "fields": fields,
            "part_count": len(part_records),
        },
        "source_name": fields.get("source_name") or "multipart-upload.bundle",
        "declared_modality": fields.get("declared_modality") or "DIRECTORY",
        "media_type": content_type,
        "fields": fields,
        "part_count": len(part_records),
    }


def _decode_standard_body(
    *,
    body: bytes,
    content_type: str,
    source_name: str,
    declared_modality: str | None,
) -> dict[str, Any]:
    media_type = _base_media_type(content_type)

    if media_type in {"application/json", "application/ld+json"}:
        try:
            return {
                "mode": "JSON",
                "payload": json.loads(body.decode(_charset(content_type))),
                "source_name": source_name or "payload.json",
                "declared_modality": declared_modality or "JSON",
                "media_type": content_type,
                "parse_error": None,
            }
        except (LookupError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return {
                "mode": "JSON_RAW_FALLBACK",
                "payload": body,
                "source_name": source_name or "malformed-json.bin",
                "declared_modality": declared_modality or "BINARY",
                "media_type": content_type,
                "parse_error": f"{type(exc).__name__}:{exc}",
            }

    if media_type == "application/x-www-form-urlencoded":
        try:
            text = body.decode(_charset(content_type))
            parsed = parse_qs(text, keep_blank_values=True, strict_parsing=False)
            return {
                "mode": "URLENCODED_FORM",
                "payload": parsed,
                "source_name": source_name or "form.json",
                "declared_modality": declared_modality or "JSON",
                "media_type": content_type,
                "parse_error": None,
            }
        except (LookupError, UnicodeDecodeError) as exc:
            return {
                "mode": "URLENCODED_RAW_FALLBACK",
                "payload": body,
                "source_name": source_name or "form.bin",
                "declared_modality": declared_modality or "BINARY",
                "media_type": content_type,
                "parse_error": f"{type(exc).__name__}:{exc}",
            }

    if media_type == "multipart/form-data":
        parsed = _parse_multipart(body, content_type)
        parsed["parse_error"] = None
        return parsed

    if media_type.startswith("text/") or media_type in {
        "application/javascript",
        "application/ecmascript",
        "application/xml",
    }:
        try:
            return {
                "mode": "TEXT",
                "payload": body.decode(_charset(content_type)),
                "source_name": source_name or "stdin.txt",
                "declared_modality": declared_modality,
                "media_type": content_type,
                "parse_error": None,
            }
        except (LookupError, UnicodeDecodeError) as exc:
            return {
                "mode": "TEXT_RAW_FALLBACK",
                "payload": body,
                "source_name": source_name or "stdin.bin",
                "declared_modality": declared_modality or "BINARY",
                "media_type": content_type,
                "parse_error": f"{type(exc).__name__}:{exc}",
            }

    return {
        "mode": "RAW_BYTES",
        "payload": body,
        "source_name": source_name or "stdin.bin",
        "declared_modality": declared_modality,
        "media_type": content_type or "application/octet-stream",
        "parse_error": None,
    }


def compatibility_status() -> dict[str, Any]:
    return {
        "schema": "HHS_STANDARD_LEGACY_INGRESS_COMPAT_STATUS_V1",
        "version": VERSION,
        "ok": True,
        "canonical_redirect_operation": "workspace:ingress.register",
        "legacy_route_aliases": list(LEGACY_ROUTE_ALIASES),
        "canonical_modalities": list(SUPPORTED_MODALITIES),
        "legacy_modality_aliases": dict(sorted(LEGACY_MODALITY_ALIASES.items())),
        "mime_translation_count": len(MIME_MODALITY_MAP),
        "linux_compatibility_surfaces": list(LINUX_COMPATIBILITY_SURFACES),
        "max_body_bytes": _configured_max_bytes(),
        "unknown_type_policy": "PRESERVE_AS_REVERSIBLE_BINARY",
        "frontend_authority": "REQUEST_ONLY_NO_CANONICAL_COMMIT_AUTHORITY",
        "native_backend_authority": "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1",
    }


def build_standard_ingress_router(authority_loop: Any) -> APIRouter:
    router = APIRouter(tags=["runtime", "ingress", "compatibility", "linux"])

    @router.get("/api/runtime/ingress/compatibility")
    async def standard_ingress_status() -> dict[str, Any]:
        return compatibility_status()

    async def handle(request: Request) -> dict[str, Any]:
        limit = _configured_max_bytes()
        body = await _read_bounded_body(request, limit)

        source_name = (
            request.headers.get("x-hhs-filename")
            or request.headers.get("x-filename")
            or request.query_params.get("source_name")
            or request.query_params.get("filename")
            or ""
        )
        declared_modality = (
            request.headers.get("x-hhs-modality")
            or request.query_params.get("declared_modality")
            or request.query_params.get("modality")
        )
        content_type = request.headers.get("content-type") or "application/octet-stream"

        decoded = _decode_standard_body(
            body=body,
            content_type=content_type,
            source_name=source_name,
            declared_modality=declared_modality,
        )
        fields = decoded.get("fields") if isinstance(decoded.get("fields"), dict) else {}

        project_id = (
            request.headers.get("x-hhs-project-id")
            or request.query_params.get("project_id")
            or fields.get("project_id")
            or "project:default"
        )
        source_name = str(fields.get("source_name") or decoded.get("source_name") or "ingress.bin")
        declared_modality = (
            fields.get("declared_modality")
            or fields.get("source_modality")
            or decoded.get("declared_modality")
        )
        media_type = str(decoded.get("media_type") or content_type)

        decision = authority_loop.submit(
            "ingress.register",
            {
                "project_id": str(project_id),
                "source_name": source_name,
                "source_payload": decoded.get("payload"),
                "declared_modality": declared_modality,
                "source_media_type": media_type,
                "compatibility_transport": decoded.get("mode"),
                "compatibility_parse_error": decoded.get("parse_error"),
            },
        )

        return {
            "schema": "HHS_STANDARD_LEGACY_INGRESS_COMPAT_RESULT_V1",
            "version": VERSION,
            "ok": bool(decision.get("ok")),
            "status": (
                "LEGACY_INGRESS_TRANSLATED_AND_REDIRECTED"
                if decision.get("ok")
                else "LEGACY_INGRESS_CANONICAL_ADMISSION_FAILED"
            ),
            "received_content_type": content_type,
            "transport_mode": decoded.get("mode"),
            "source_name": source_name,
            "requested_declared_modality": declared_modality,
            "redirected_operation": "workspace:ingress.register",
            "authority_decision": decision,
            "frontend_committed_runtime_truth": False,
        }

    for path in LEGACY_ROUTE_ALIASES:
        router.add_api_route(
            path,
            handle,
            methods=["POST"],
            include_in_schema=True,
            name="standard_legacy_ingress_" + path.strip("/").replace("/", "_"),
        )

    return router


__all__ = [
    "LEGACY_ROUTE_ALIASES",
    "LINUX_COMPATIBILITY_SURFACES",
    "VERSION",
    "build_standard_ingress_router",
    "compatibility_status",
]
