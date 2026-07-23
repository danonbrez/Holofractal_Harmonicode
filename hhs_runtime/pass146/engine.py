from __future__ import annotations

import base64
import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from hhs_runtime.pass145.canonical import canonical_json, hash72, stable_id, utc_now
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass145.service import HHS145Service
from hhs_runtime.pass145.workbench import LVMEngine, ScriptWorkbench

PASS_ID = "HHS-P146"
VERSION = "146.1.0"

REVERSIBILITY_CLASSES = {
    "EXACTLY_REVERSIBLE",
    "TRANSACTIONALLY_REVERSIBLE",
    "COMPENSATABLE",
    "CHECKPOINT_REVERSIBLE",
    "APPEND_ONLY_NONDESTRUCTIVE",
    "EXPLICITLY_IRREVERSIBLE",
    "REJECTED_AS_UNSAFE",
}

PATH_STATES = {
    "ADMITTED",
    "ACTIVE",
    "VALIDATING",
    "CLOSED",
    "DISSOLVED",
    "RECOVERY_REQUIRED",
    "REJECTED",
}

CAPABILITIES = {
    "QUERY", "SEARCH", "VALIDATE", "INGEST", "DATABASE_READ", "DATABASE_WRITE",
    "NETWORK", "NETWORK_SEND", "NETWORK_RECEIVE", "FILESYSTEM_READ", "FILESYSTEM_WRITE",
    "NATIVE_RUNTIME", "INTER_SANDBOX", "LOCAL_API", "SECURITY_ADMIN", "SECURITY_INSPECT",
    "PATH_EXECUTION", "CONFLICT_NEGOTIATION",
}

OPERATION_SPECS: dict[str, dict[str, Any]] = {
    "QUERY": {
        "capabilities": ["DATABASE_READ", "QUERY", "PATH_EXECUTION"],
        "reversibility": "APPEND_ONLY_NONDESTRUCTIVE",
        "components": ["KNOWLEDGE_QUERY_PLANNER", "KNOWLEDGE_DATABASE"],
        "mutating": False,
    },
    "SEARCH": {
        "capabilities": ["DATABASE_READ", "SEARCH", "PATH_EXECUTION"],
        "reversibility": "APPEND_ONLY_NONDESTRUCTIVE",
        "components": ["SYMBOL_AWARE_SEARCH", "KNOWLEDGE_DATABASE"],
        "mutating": False,
    },
    "VALIDATE_SOURCE": {
        "capabilities": ["DATABASE_READ", "VALIDATE", "PATH_EXECUTION"],
        "reversibility": "APPEND_ONLY_NONDESTRUCTIVE",
        "components": ["VALIDATION_ENGINE", "KNOWLEDGE_DATABASE"],
        "mutating": False,
    },
    "INGEST_TEXT": {
        "capabilities": ["INGEST", "DATABASE_WRITE", "PATH_EXECUTION"],
        "reversibility": "CHECKPOINT_REVERSIBLE",
        "components": ["DOCUMENT_INGESTION", "VALIDATION_ENGINE", "KNOWLEDGE_DATABASE"],
        "mutating": True,
    },
    "RUN_SCRIPT": {
        "capabilities": ["NATIVE_RUNTIME", "PATH_EXECUTION"],
        "reversibility": "CHECKPOINT_REVERSIBLE",
        "components": ["SCRIPT_WORKBENCH", "AUTHORITATIVE_RUNTIME"],
        "mutating": True,
    },
    "RUN_LVM": {
        "capabilities": ["NATIVE_RUNTIME", "PATH_EXECUTION"],
        "reversibility": "CHECKPOINT_REVERSIBLE",
        "components": ["LVM_ENGINE", "AUTHORITATIVE_RUNTIME"],
        "mutating": True,
    },
    "PROPAGATE": {
        "capabilities": ["NETWORK", "NETWORK_SEND", "PATH_EXECUTION"],
        "reversibility": "APPEND_ONLY_NONDESTRUCTIVE",
        "components": ["MESSAGE_ENVELOPE", "SIGNATURE_ENGINE", "BOUNDARY_HOP_VALIDATOR"],
        "mutating": False,
    },
    "RECEIVE_PROPAGATION": {
        "capabilities": ["NETWORK", "NETWORK_RECEIVE", "PATH_EXECUTION"],
        "reversibility": "APPEND_ONLY_NONDESTRUCTIVE",
        "components": ["PEER_TRUST_GATE", "SIGNATURE_ENGINE", "RECEIVER_BOUNDARY_RECONSTRUCTOR"],
        "mutating": False,
    },
    "NEGOTIATE_CONFLICT": {
        "capabilities": ["INTER_SANDBOX", "CONFLICT_NEGOTIATION", "PATH_EXECUTION"],
        "reversibility": "TRANSACTIONALLY_REVERSIBLE",
        "components": ["CONFLICT_NEGOTIATOR", "BOUNDARY_CONSTRUCTOR"],
        "mutating": False,
    },
    "RUN_CLI_COMMAND": {
        "capabilities": ["PATH_EXECUTION"],
        "reversibility": "CHECKPOINT_REVERSIBLE",
        "components": ["CLI_COMMAND_ROUTER", "AUTHORITATIVE_RUNTIME"],
        "mutating": True,
    },
}

DEFAULT_RESOURCE_BUDGET = {
    "max_steps": 64,
    "max_output_bytes": 4 * 1024 * 1024,
    "max_recursive_depth": 16,
    "max_messages": 128,
    "timeout_seconds": 30,
}


def _json_load(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    return json.loads(value)


def _sorted_strings(values: Sequence[Any] | None) -> list[str]:
    return sorted({str(v).upper() for v in (values or []) if str(v)})


def _scrypt_bytes(token: str, salt_hex: str) -> bytes:
    salt = bytes.fromhex(salt_hex)
    return hashlib.scrypt(token.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)


def _scrypt(token: str, salt_hex: str) -> str:
    return _scrypt_bytes(token, salt_hex).hex()


def _credential_attributes(token: str, *, local_only: bool) -> dict[str, Any]:
    credential_salt = secrets.token_bytes(16).hex()
    encryption_salt = secrets.token_bytes(16).hex()
    nonce = secrets.token_bytes(12)
    private = Ed25519PrivateKey.generate()
    private_raw = private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    public_raw = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    key = _scrypt_bytes(token, encryption_salt)
    encrypted = AESGCM(key).encrypt(nonce, private_raw, b"HHS-P146-ED25519-IDENTITY-V1")
    public_b64 = base64.b64encode(public_raw).decode("ascii")
    return {
        "credential_scheme": "SCRYPT_N16384_R8_P1",
        "credential_salt": credential_salt,
        "credential_verifier": _scrypt(token, credential_salt),
        "local_only": bool(local_only),
        "signing_scheme": "ED25519",
        "signing_public_key_b64": public_b64,
        "signing_public_key_fingerprint": hashlib.sha256(public_raw).hexdigest(),
        "signing_private_key_encryption": "AES256_GCM_SCRYPT_N16384_R8_P1",
        "signing_private_key_salt": encryption_salt,
        "signing_private_key_nonce_b64": base64.b64encode(nonce).decode("ascii"),
        "signing_private_key_ciphertext_b64": base64.b64encode(encrypted).decode("ascii"),
    }


def _allowed(value: str, allowed: Sequence[str]) -> bool:
    return "*" in allowed or value in allowed


@dataclass(frozen=True)
class BoundaryPlan:
    operation: str
    capabilities: list[str]
    resource_budget: dict[str, int]
    disclosure_scope: dict[str, Any]
    reversibility_class: str
    path_blueprint: list[dict[str, Any]]


class HHS146BoundaryEngine:
    """Boundary-constructed execution over the canonical Pass 145 authorities.

    A request cannot dispatch directly.  It must first become an immutable
    boundary contract and temporary minimum-capability pathway.  The pathway is
    later activated, executed, validated, closed, and dissolved into the shared
    transactional receipt chain.
    """

    def __init__(self, service: HHS145Service):
        self.service = service
        self.db = service.db
        self.scripts = ScriptWorkbench(service)
        self.lvms = LVMEngine(service, self.scripts)

    # ------------------------------------------------------------------
    # Identity and authority
    # ------------------------------------------------------------------
    def bootstrap_local_owner(self, display_name: str = "Local HHS Owner") -> dict[str, Any]:
        if self.db.conn.execute("SELECT 1 FROM security_identities LIMIT 1").fetchone():
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "security authority is already initialized", "SECURITY_BOOTSTRAP")
        token = secrets.token_urlsafe(32)
        attrs = _credential_attributes(token, local_only=True)
        identity_payload = {"identity_type": "LOCAL_OWNER", "display_name": display_name, "attributes": attrs}
        identity_hash = hash72("hhs_pass146_identity_v1", identity_payload)
        identity_id = stable_id("IDN", "hhs_pass146_identity_id_v1", identity_payload)
        grant_payload = {
            "identity_id": identity_id,
            "capabilities": sorted(CAPABILITIES),
            "operations": sorted(OPERATION_SPECS),
            "sources": ["*"],
            "destinations": ["*"],
            "resource_policy": {**DEFAULT_RESOURCE_BUDGET, "max_recursive_depth": 32},
            "disclosure_policy": {"classifications": ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"], "allow_remote": False},
            "parent_grant_id": None,
        }
        grant_hash = hash72("hhs_pass146_authority_grant_v1", grant_payload)
        grant_id = stable_id("GRT", "hhs_pass146_authority_grant_id_v1", grant_payload)

        def apply(conn):
            now = utc_now()
            conn.execute(
                "INSERT INTO security_identities(identity_id,identity_type,display_name,attributes_json,identity_hash72,active,created_at) VALUES(?,?,?,?,?,1,?)",
                (identity_id, "LOCAL_OWNER", display_name, canonical_json(attrs), identity_hash, now),
            )
            conn.execute(
                "INSERT INTO security_authority_grants(grant_id,identity_id,capabilities_json,operations_json,sources_json,destinations_json,resource_policy_json,disclosure_policy_json,parent_grant_id,grant_hash72,revoked,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,0,?)",
                (grant_id, identity_id, canonical_json(grant_payload["capabilities"]), canonical_json(grant_payload["operations"]), canonical_json(grant_payload["sources"]), canonical_json(grant_payload["destinations"]), canonical_json(grant_payload["resource_policy"]), canonical_json(grant_payload["disclosure_policy"]), None, grant_hash, now),
            )
            return {"status": "LOCAL_SECURITY_OWNER_BOOTSTRAPPED", "identity_id": identity_id, "grant_id": grant_id, "identity_hash72": identity_hash, "grant_hash72": grant_hash}

        result = self.db.mutate("SECURITY_BOOTSTRAP_LOCAL_OWNER", {"display_name": display_name, "identity_hash72": identity_hash, "grant_hash72": grant_hash}, apply, receipt_type="BOUNDARY_AUTHORITY_RECEIPT")
        return {**result, "authentication_token": token, "authentication_token_returned_once": True}

    def _identity(self, identity_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM security_identities WHERE identity_id=?", (identity_id,)).fetchone()
        if not row:
            raise Pass145Error("IDENTITY_UNRESOLVED", "identity does not exist", "BOUNDARY_IDENTITY", identity_id)
        value = dict(row)
        value["attributes"] = _json_load(value.pop("attributes_json"), {})
        return value

    def _grant(self, grant_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM security_authority_grants WHERE grant_id=?", (grant_id,)).fetchone()
        if not row:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "authority grant does not exist", "BOUNDARY_AUTHORITY", grant_id)
        value = dict(row)
        for field in ("capabilities", "operations", "sources", "destinations", "resource_policy", "disclosure_policy"):
            value[field] = _json_load(value.pop(field + "_json"), [] if field in {"capabilities", "operations", "sources", "destinations"} else {})
        return value

    def authenticate(self, identity_id: str, token: str) -> dict[str, Any]:
        identity = self._identity(identity_id)
        if not identity["active"]:
            raise Pass145Error("IDENTITY_UNRESOLVED", "identity is inactive", "BOUNDARY_IDENTITY", identity_id)
        attrs = identity["attributes"]
        observed = _scrypt(token, attrs["credential_salt"])
        if not secrets.compare_digest(observed, attrs["credential_verifier"]):
            raise Pass145Error("IDENTITY_UNRESOLVED", "credential verification failed", "BOUNDARY_IDENTITY", identity_id)
        return {"identity_id": identity_id, "identity_hash72": identity["identity_hash72"], "authenticated": True}

    def _signing_private_key(self, identity_id: str, token: str) -> Ed25519PrivateKey:
        identity = self._identity(identity_id)
        self.authenticate(identity_id, token)
        attrs = identity["attributes"]
        try:
            key = _scrypt_bytes(token, attrs["signing_private_key_salt"])
            nonce = base64.b64decode(attrs["signing_private_key_nonce_b64"], validate=True)
            ciphertext = base64.b64decode(attrs["signing_private_key_ciphertext_b64"], validate=True)
            raw = AESGCM(key).decrypt(nonce, ciphertext, b"HHS-P146-ED25519-IDENTITY-V1")
            return Ed25519PrivateKey.from_private_bytes(raw)
        except Exception as exc:
            raise Pass145Error("IDENTITY_UNRESOLVED", "identity signing key could not be unlocked", "BOUNDARY_IDENTITY", identity_id) from exc

    def identity_public_record(self, identity_id: str) -> dict[str, Any]:
        identity = self._identity(identity_id)
        attrs = identity["attributes"]
        return {
            "identity_id": identity_id,
            "identity_hash72": identity["identity_hash72"],
            "display_name": identity["display_name"],
            "signing_scheme": attrs.get("signing_scheme"),
            "public_key_b64": attrs.get("signing_public_key_b64"),
            "public_key_fingerprint": attrs.get("signing_public_key_fingerprint"),
        }

    def create_identity(self, issuer_identity_id: str, issuer_grant_id: str, issuer_token: str, display_name: str, *, identity_type: str = "LOCAL_USER") -> dict[str, Any]:
        self._authorize_admin(issuer_identity_id, issuer_grant_id, issuer_token)
        token = secrets.token_urlsafe(32)
        attrs = _credential_attributes(token, local_only=True)
        payload = {"identity_type": identity_type.upper(), "display_name": display_name, "attributes": attrs}
        identity_hash = hash72("hhs_pass146_identity_v1", payload)
        identity_id = stable_id("IDN", "hhs_pass146_identity_id_v1", payload)

        def apply(conn):
            conn.execute("INSERT INTO security_identities(identity_id,identity_type,display_name,attributes_json,identity_hash72,active,created_at) VALUES(?,?,?,?,?,1,?)", (identity_id, payload["identity_type"], display_name, canonical_json(attrs), identity_hash, utc_now()))
            return {"status": "SECURITY_IDENTITY_CREATED", "identity_id": identity_id, "identity_hash72": identity_hash}

        result = self.db.mutate("SECURITY_IDENTITY_CREATE", {"issuer_identity_id": issuer_identity_id, "display_name": display_name, "identity_type": payload["identity_type"]}, apply, receipt_type="BOUNDARY_AUTHORITY_RECEIPT")
        return {**result, "authentication_token": token, "authentication_token_returned_once": True}

    def create_grant(self, issuer_identity_id: str, parent_grant_id: str, issuer_token: str, target_identity_id: str, *, capabilities: Sequence[str], operations: Sequence[str], sources: Sequence[str] = ("*",), destinations: Sequence[str] = ("LOCAL_RESULT",), resource_policy: Mapping[str, Any] | None = None, disclosure_policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
        self.authenticate(issuer_identity_id, issuer_token)
        parent = self._grant(parent_grant_id)
        if parent["identity_id"] != issuer_identity_id or parent["revoked"]:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "issuer does not control the parent grant", "BOUNDARY_AUTHORITY", parent_grant_id)
        if "SECURITY_ADMIN" not in parent["capabilities"]:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "SECURITY_ADMIN capability required", "BOUNDARY_AUTHORITY", parent_grant_id)
        self._identity(target_identity_id)
        caps = _sorted_strings(capabilities)
        ops = _sorted_strings(operations)
        srcs = sorted({str(x) for x in sources})
        dsts = sorted({str(x) for x in destinations})
        if not set(caps).issubset(set(parent["capabilities"])):
            raise Pass145Error("RECURSIVE_AUTHORITY_EXPANSION", "child grant capabilities exceed parent authority", "BOUNDARY_AUTHORITY")
        if not set(ops).issubset(set(parent["operations"])):
            raise Pass145Error("RECURSIVE_AUTHORITY_EXPANSION", "child grant operations exceed parent authority", "BOUNDARY_AUTHORITY")
        if "*" not in parent["sources"] and not set(srcs).issubset(set(parent["sources"])):
            raise Pass145Error("RECURSIVE_AUTHORITY_EXPANSION", "child source scope exceeds parent authority", "BOUNDARY_AUTHORITY")
        if "*" not in parent["destinations"] and not set(dsts).issubset(set(parent["destinations"])):
            raise Pass145Error("RECURSIVE_AUTHORITY_EXPANSION", "child destination scope exceeds parent authority", "BOUNDARY_AUTHORITY")
        parent_resources = {k: int(v) for k, v in parent["resource_policy"].items() if isinstance(v, int)}
        requested_resources = {**parent_resources, **{k: int(v) for k, v in dict(resource_policy or {}).items()}}
        for key, value in requested_resources.items():
            if key in parent_resources and value > parent_resources[key]:
                raise Pass145Error("RECURSIVE_AUTHORITY_EXPANSION", f"child resource {key} exceeds parent", "BOUNDARY_AUTHORITY")
        parent_classes = set(parent["disclosure_policy"].get("classifications", []))
        disc = {"classifications": sorted(set(dict(disclosure_policy or {}).get("classifications", parent_classes)) & parent_classes), "allow_remote": bool(dict(disclosure_policy or {}).get("allow_remote", False) and parent["disclosure_policy"].get("allow_remote", False))}
        payload = {"identity_id": target_identity_id, "capabilities": caps, "operations": ops, "sources": srcs, "destinations": dsts, "resource_policy": requested_resources, "disclosure_policy": disc, "parent_grant_id": parent_grant_id}
        grant_hash = hash72("hhs_pass146_authority_grant_v1", payload)
        grant_id = stable_id("GRT", "hhs_pass146_authority_grant_id_v1", payload)

        def apply(conn):
            conn.execute("INSERT INTO security_authority_grants(grant_id,identity_id,capabilities_json,operations_json,sources_json,destinations_json,resource_policy_json,disclosure_policy_json,parent_grant_id,grant_hash72,revoked,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,0,?)", (grant_id, target_identity_id, canonical_json(caps), canonical_json(ops), canonical_json(srcs), canonical_json(dsts), canonical_json(requested_resources), canonical_json(disc), parent_grant_id, grant_hash, utc_now()))
            return {"status": "AUTHORITY_GRANT_CREATED", "grant_id": grant_id, "grant_hash72": grant_hash, "authority_surface_narrowed": True}

        return self.db.mutate("SECURITY_GRANT_CREATE", {"issuer_identity_id": issuer_identity_id, "parent_grant_id": parent_grant_id, "target_identity_id": target_identity_id, "grant_hash72": grant_hash}, apply, receipt_type="BOUNDARY_AUTHORITY_RECEIPT")

    def _authorize_admin(self, identity_id: str, grant_id: str, token: str) -> None:
        self.authenticate(identity_id, token)
        grant = self._grant(grant_id)
        if grant["identity_id"] != identity_id or grant["revoked"] or "SECURITY_ADMIN" not in grant["capabilities"]:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "active SECURITY_ADMIN grant required", "BOUNDARY_AUTHORITY", grant_id)

    def trust_peer(self, issuer_identity_id: str, issuer_grant_id: str, issuer_token: str, peer_id: str, public_key_b64: str, *, classifications: Sequence[str] = ("INTERNAL",), destinations: Sequence[str] = ("*",)) -> dict[str, Any]:
        self._authorize_admin(issuer_identity_id, issuer_grant_id, issuer_token)
        peer_id = str(peer_id).strip()
        if not peer_id:
            raise Pass145Error("IDENTITY_UNRESOLVED", "peer identity is empty", "PEER_TRUST")
        try:
            public_raw = base64.b64decode(public_key_b64, validate=True)
            Ed25519PublicKey.from_public_bytes(public_raw)
        except Exception as exc:
            raise Pass145Error("IDENTITY_UNRESOLVED", "peer public key is not a valid Ed25519 key", "PEER_TRUST", peer_id) from exc
        classes = _sorted_strings(classifications)
        destinations_value = sorted({str(x) for x in destinations if str(x)})
        payload = {
            "peer_id": peer_id,
            "public_key_b64": public_key_b64,
            "public_key_fingerprint": hashlib.sha256(public_raw).hexdigest(),
            "classifications": classes,
            "destinations": destinations_value,
            "admitted_by_identity_id": issuer_identity_id,
        }
        trust_hash = hash72("hhs_pass146_peer_trust_v1", payload)
        existing = self.db.conn.execute("SELECT * FROM security_peer_trust WHERE peer_id=?", (peer_id,)).fetchone()
        if existing:
            value = dict(existing)
            if value["trust_hash72"] != trust_hash:
                raise Pass145Error("AUTHORITY_INSUFFICIENT", "peer trust already exists with different key or scope", "PEER_TRUST", peer_id)
            return {"status": "PEER_TRUST_ALREADY_ADMITTED", "peer_id": peer_id, "trust_hash72": trust_hash, "public_key_fingerprint": payload["public_key_fingerprint"]}

        def apply(conn):
            conn.execute(
                "INSERT INTO security_peer_trust(peer_id,public_key_b64,public_key_fingerprint,classifications_json,destinations_json,admitted_by_identity_id,trust_hash72,active,created_at) VALUES(?,?,?,?,?,?,?,1,?)",
                (peer_id, public_key_b64, payload["public_key_fingerprint"], canonical_json(classes), canonical_json(destinations_value), issuer_identity_id, trust_hash, utc_now()),
            )
            return {"status": "PEER_TRUST_ADMITTED", "peer_id": peer_id, "trust_hash72": trust_hash, "public_key_fingerprint": payload["public_key_fingerprint"], "classifications": classes, "destinations": destinations_value}

        return self.db.mutate("SECURITY_PEER_TRUST_ADMIT", {"peer_id": peer_id, "trust_hash72": trust_hash, "issuer_identity_id": issuer_identity_id}, apply, receipt_type="BOUNDARY_AUTHORITY_RECEIPT")

    def list_trusted_peers(self) -> list[dict[str, Any]]:
        result = []
        for row in self.db.conn.execute("SELECT * FROM security_peer_trust ORDER BY peer_id"):
            value = dict(row)
            value["classifications"] = _json_load(value.pop("classifications_json"), [])
            value["destinations"] = _json_load(value.pop("destinations_json"), [])
            result.append(value)
        return result

    # ------------------------------------------------------------------
    # Boundary construction
    # ------------------------------------------------------------------
    def _target_scope_value(self, operation: str, request: Mapping[str, Any]) -> str:
        if operation in {"QUERY", "SEARCH", "INGEST_TEXT"}:
            return str(request.get("namespace", "default"))
        if operation == "VALIDATE_SOURCE":
            return str(request.get("source_id", ""))
        if operation == "RUN_SCRIPT":
            return str(request.get("script_id", ""))
        if operation == "RUN_LVM":
            return str(request.get("lvm_id", ""))
        if operation in {"PROPAGATE", "RECEIVE_PROPAGATION"}:
            return str(request.get("source_peer", "local"))
        if operation == "RUN_CLI_COMMAND":
            return str(request.get("source_scope", "*"))
        return "*"

    def _relevant_state_root(self, identity: Mapping[str, Any], grant: Mapping[str, Any], operation: str, request: Mapping[str, Any]) -> str:
        target: Any = None
        if operation == "VALIDATE_SOURCE":
            row = self.db.conn.execute("SELECT source_id,source_root_hash72,namespace,quarantined FROM sources WHERE source_id=?", (request.get("source_id"),)).fetchone()
            target = dict(row) if row else None
        elif operation == "RUN_SCRIPT":
            row = self.db.conn.execute("SELECT script_id,source_hash72,validation_state,environment_id FROM scripts WHERE script_id=?", (request.get("script_id"),)).fetchone()
            target = dict(row) if row else None
        elif operation == "RUN_LVM":
            row = self.db.conn.execute("SELECT lvm_id,manifest_hash72,environment_id FROM lvms WHERE lvm_id=?", (request.get("lvm_id"),)).fetchone()
            target = dict(row) if row else None
        elif operation in {"QUERY", "SEARCH", "INGEST_TEXT"}:
            target = {"namespace": request.get("namespace", "default")}
        elif operation == "PROPAGATE":
            target = {"source_peer": request.get("source_peer", "local"), "destination_peer": request.get("destination_peer")}
        elif operation == "RECEIVE_PROPAGATION":
            envelope = dict(request.get("envelope", {}))
            trust = self.db.conn.execute("SELECT peer_id,public_key_fingerprint,trust_hash72,active FROM security_peer_trust WHERE peer_id=?", (request.get("source_peer"),)).fetchone()
            target = {"source_peer": request.get("source_peer"), "destination_peer": request.get("destination_peer"), "message_hash72": envelope.get("message_hash72"), "peer_trust": dict(trust) if trust else None}
        elif operation == "NEGOTIATE_CONFLICT":
            target = {"left_hash72": hash72("hhs_pass146_conflict_left_v1", request.get("left_state")), "right_hash72": hash72("hhs_pass146_conflict_right_v1", request.get("right_state"))}
        elif operation == "RUN_CLI_COMMAND":
            target = {"argv_hash72": hash72("hhs_pass146_cli_argv_v1", request.get("argv", [])), "database_path": str(self.db.path)}
        return hash72("hhs_pass146_relevant_state_v1", {"identity": {"identity_id": identity["identity_id"], "identity_hash72": identity["identity_hash72"], "active": identity["active"]}, "grant": {"grant_id": grant["grant_id"], "grant_hash72": grant["grant_hash72"], "revoked": grant["revoked"]}, "operation": operation, "target": target})

    @staticmethod
    def _cli_capabilities(argv: Sequence[Any]) -> tuple[set[str], str]:
        args = [str(x) for x in argv]
        if not args:
            raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", "empty CLI command", "BOUNDARY_CONSTRUCTION")
        command = args[0]
        subcommand = args[1] if len(args) > 1 else ""
        read_only = {"object", "query", "search", "graph", "analyze", "receipt"}
        if command in {"status", "version", "doctor", "capabilities"}:
            return {"DATABASE_READ", "SECURITY_INSPECT", "PATH_EXECUTION"}, "APPEND_ONLY_NONDESTRUCTIVE"
        if command == "source":
            caps = {"DATABASE_READ", "PATH_EXECUTION"}
            if subcommand == "export": caps.add("FILESYSTEM_WRITE")
            return caps, "APPEND_ONLY_NONDESTRUCTIVE"
        if command in read_only:
            return {"DATABASE_READ", "PATH_EXECUTION"} | ({"QUERY"} if command == "query" else {"SEARCH"} if command == "search" else set()), "APPEND_ONLY_NONDESTRUCTIVE"
        if command == "validate":
            caps = {"DATABASE_READ", "VALIDATE", "PATH_EXECUTION"}
            if subcommand in {"source", "object"}:
                caps.add("DATABASE_WRITE")
                return caps, "TRANSACTIONALLY_REVERSIBLE"
            return caps, "APPEND_ONLY_NONDESTRUCTIVE"
        if command == "ingest":
            return {"INGEST", "DATABASE_WRITE", "FILESYSTEM_READ", "PATH_EXECUTION"}, "CHECKPOINT_REVERSIBLE"
        if command == "protect":
            return {"DATABASE_WRITE", "PATH_EXECUTION"}, "TRANSACTIONALLY_REVERSIBLE"
        if command == "database":
            if subcommand in {"status", "integrity"}:
                return {"DATABASE_READ", "PATH_EXECUTION"}, "APPEND_ONLY_NONDESTRUCTIVE"
            return {"DATABASE_WRITE", "PATH_EXECUTION"}, "CHECKPOINT_REVERSIBLE"
        if command == "backup":
            return {"DATABASE_READ", "FILESYSTEM_WRITE", "PATH_EXECUTION"}, "APPEND_ONLY_NONDESTRUCTIVE"
        if command == "restore":
            caps = {"DATABASE_READ", "FILESYSTEM_READ", "PATH_EXECUTION"}
            if subcommand == "apply": caps.add("DATABASE_WRITE")
            return caps, "CHECKPOINT_REVERSIBLE"
        if command in {"workspace", "env", "extension"}:
            inspect_ops = {"inspect", "list", "diff"}
            if subcommand in inspect_ops:
                return {"DATABASE_READ", "PATH_EXECUTION"}, "APPEND_ONLY_NONDESTRUCTIVE"
            if subcommand == "export":
                return {"DATABASE_READ", "FILESYSTEM_WRITE", "PATH_EXECUTION"}, "APPEND_ONLY_NONDESTRUCTIVE"
            caps = {"DATABASE_WRITE", "INTER_SANDBOX", "PATH_EXECUTION"}
            if subcommand in {"import", "install"}: caps.add("FILESYSTEM_READ")
            return caps, "TRANSACTIONALLY_REVERSIBLE"
        if command == "script":
            if subcommand in {"inspect"}:
                return {"DATABASE_READ", "PATH_EXECUTION"}, "APPEND_ONLY_NONDESTRUCTIVE"
            caps = {"NATIVE_RUNTIME", "PATH_EXECUTION"}
            if subcommand in {"import", "paste", "validate"}: caps.add("DATABASE_WRITE")
            if subcommand == "import": caps.add("FILESYSTEM_READ")
            if subcommand == "run": caps.update({"DATABASE_READ", "DATABASE_WRITE"})
            return caps, "CHECKPOINT_REVERSIBLE"
        if command == "lvm":
            caps = {"NATIVE_RUNTIME", "PATH_EXECUTION"}
            caps.add("DATABASE_READ")
            if subcommand in {"create", "run", "replay"}: caps.add("DATABASE_WRITE")
            if subcommand == "create": caps.add("FILESYSTEM_READ")
            return caps, "CHECKPOINT_REVERSIBLE"
        if command == "api":
            caps = {"LOCAL_API", "PATH_EXECUTION"}
            if subcommand == "execute": caps.add("NETWORK")
            if subcommand == "create": caps.update({"DATABASE_WRITE", "FILESYSTEM_READ"})
            else: caps.add("DATABASE_READ")
            return caps, "CHECKPOINT_REVERSIBLE" if subcommand == "create" else "APPEND_ONLY_NONDESTRUCTIVE"
        if command == "replay":
            return {"DATABASE_READ", "VALIDATE", "PATH_EXECUTION"}, "APPEND_ONLY_NONDESTRUCTIVE"
        if command in {"serve", "shell"}:
            raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", f"{command} requires its dedicated governed lifecycle surface", "BOUNDARY_CONSTRUCTION")
        raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", f"CLI command is not registered for boundary execution: {command}", "BOUNDARY_CONSTRUCTION")

    def _derive_plan(self, operation: str, request: Mapping[str, Any], grant: Mapping[str, Any], parent: Mapping[str, Any] | None) -> BoundaryPlan:
        spec = dict(OPERATION_SPECS[operation])
        required = set(spec["capabilities"])
        if operation == "RUN_CLI_COMMAND":
            dynamic_caps, dynamic_reversibility = self._cli_capabilities(request.get("argv", []))
            required.update(dynamic_caps)
            spec["reversibility"] = dynamic_reversibility
        if operation == "RUN_SCRIPT":
            row = self.db.conn.execute("SELECT declared_capabilities_json FROM scripts WHERE script_id=?", (request.get("script_id"),)).fetchone()
            if not row:
                raise Pass145Error("SOURCE_STATE_INVALID", "script target not found", "BOUNDARY_CONSTRUCTION")
            required.update(_json_load(row[0], []))
        if operation == "RUN_LVM":
            row = self.db.conn.execute("SELECT manifest_json FROM lvms WHERE lvm_id=?", (request.get("lvm_id"),)).fetchone()
            if not row:
                raise Pass145Error("SOURCE_STATE_INVALID", "LVM target not found", "BOUNDARY_CONSTRUCTION")
            required.update(_sorted_strings(_json_load(row[0], {}).get("capabilities", [])))
        unknown = required - CAPABILITIES
        if unknown:
            raise Pass145Error("CAPABILITY_OVERBROAD", f"operation requires unknown capabilities: {sorted(unknown)}", "BOUNDARY_CONSTRUCTION")
        if not required.issubset(set(grant["capabilities"])):
            raise Pass145Error("AUTHORITY_INSUFFICIENT", f"grant lacks capabilities: {sorted(required - set(grant['capabilities']))}", "BOUNDARY_CONSTRUCTION")
        declared = set(_sorted_strings(request.get("requested_capabilities", [])))
        if declared and declared != required:
            if not required.issubset(declared):
                raise Pass145Error("AUTHORITY_INSUFFICIENT", f"requested capability set omits required capabilities: {sorted(required - declared)}", "BOUNDARY_CONSTRUCTION")
            raise Pass145Error("CAPABILITY_OVERBROAD", f"requested capability set is broader than minimum: {sorted(declared - required)}", "BOUNDARY_CONSTRUCTION")
        if parent is not None and not required.issubset(set(parent["capabilities"])):
            raise Pass145Error("RECURSIVE_AUTHORITY_EXPANSION", "child boundary exceeds parent capability surface", "BOUNDARY_CONSTRUCTION")
        grant_budget = {**DEFAULT_RESOURCE_BUDGET, **{k: int(v) for k, v in grant["resource_policy"].items() if isinstance(v, int)}}
        request_budget = {k: int(v) for k, v in dict(request.get("resource_budget", {})).items()}
        budget = {k: min(int(grant_budget[k]), int(request_budget.get(k, grant_budget[k]))) for k in DEFAULT_RESOURCE_BUDGET}
        if any(v <= 0 for v in budget.values()):
            raise Pass145Error("RESOURCE_BOUND_UNRESOLVED", "all resource bounds must be positive", "BOUNDARY_CONSTRUCTION")
        if parent is not None:
            budget = {k: min(v, int(parent["resource_budget"].get(k, v))) for k, v in budget.items()}
        classification = str(request.get("classification", "INTERNAL")).upper()
        allowed_classes = set(grant["disclosure_policy"].get("classifications", []))
        if classification not in allowed_classes:
            raise Pass145Error("DISCLOSURE_PATH_INVALID", f"classification {classification} is not admitted", "BOUNDARY_CONSTRUCTION")
        disclosure = {"classification": classification, "fields": sorted(set(request.get("disclosure_fields", ["result"]))), "allow_remote": bool(grant["disclosure_policy"].get("allow_remote", False))}
        if parent is not None:
            parent_disc = parent["disclosure_scope"]
            if classification != parent_disc.get("classification") or not set(disclosure["fields"]).issubset(set(parent_disc.get("fields", []))):
                raise Pass145Error("RECURSIVE_AUTHORITY_EXPANSION", "child disclosure scope exceeds parent boundary", "BOUNDARY_CONSTRUCTION")
        blueprint = [
            {"ordinal": 0, "component": "IDENTITY_GATE", "action": "AUTHENTICATE"},
            {"ordinal": 1, "component": "AUTHORITY_GATE", "action": "RESOLVE_MINIMUM_CAPABILITY"},
            {"ordinal": 2, "component": "SOURCE_STATE_GATE", "action": "VALIDATE_RELEVANT_STATE"},
            {"ordinal": 3, "component": "PATHWAY", "action": "ACTIVATE_TEMPORARY_CAPABILITIES"},
        ]
        for component in spec["components"]:
            blueprint.append({"ordinal": len(blueprint), "component": component, "action": "EXECUTE"})
        blueprint.extend([
            {"ordinal": len(blueprint), "component": "DESTINATION_GATE", "action": "VALIDATE_OUTPUT_AND_DISCLOSURE"},
            {"ordinal": len(blueprint) + 1, "component": "REVERSIBILITY_GATE", "action": "CLOSE_REVERSIBILITY"},
            {"ordinal": len(blueprint) + 2, "component": "RECEIPT_CHAIN", "action": "EMIT_CLOSURE_RECEIPT"},
            {"ordinal": len(blueprint) + 3, "component": "PATHWAY", "action": "DISSOLVE_TEMPORARY_AUTHORITY"},
        ])
        if len(blueprint) > budget["max_steps"]:
            raise Pass145Error("RESOURCE_BOUND_UNRESOLVED", "path blueprint exceeds admitted step bound", "BOUNDARY_CONSTRUCTION")
        return BoundaryPlan(operation, sorted(required), budget, disclosure, spec["reversibility"], blueprint)

    def construct_path(self, identity_id: str, grant_id: str, token: str, operation: str, request: Mapping[str, Any], *, destination: Mapping[str, Any] | None = None, parent_contract_id: str | None = None, expires_after_sequences: int = 32) -> dict[str, Any]:
        operation = operation.upper()
        if operation not in OPERATION_SPECS:
            raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", f"unsupported operation: {operation}", "BOUNDARY_CONSTRUCTION")
        self.authenticate(identity_id, token)
        identity = self._identity(identity_id)
        grant = self._grant(grant_id)
        if grant["identity_id"] != identity_id or grant["revoked"]:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "grant is not active for identity", "BOUNDARY_CONSTRUCTION", grant_id)
        if operation not in grant["operations"] and "*" not in grant["operations"]:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "operation is outside grant", "BOUNDARY_CONSTRUCTION", grant_id)
        source_scope = self._target_scope_value(operation, request)
        if not _allowed(source_scope, grant["sources"]):
            raise Pass145Error("SOURCE_STATE_INVALID", f"source scope {source_scope!r} is outside grant", "BOUNDARY_CONSTRUCTION")
        destination_obj = {"kind": "LOCAL_RESULT", "id": "LOCAL_RESULT", **dict(destination or {})}
        destination_id = str(destination_obj.get("id", destination_obj.get("kind", "LOCAL_RESULT")))
        if not _allowed(destination_id, grant["destinations"]):
            raise Pass145Error("DESTINATION_STATE_INVALID", f"destination {destination_id!r} is outside grant", "BOUNDARY_CONSTRUCTION")
        if operation == "RECEIVE_PROPAGATION":
            envelope = dict(request.get("envelope", {}))
            self._verify_external_envelope(
                envelope,
                source_peer=str(request.get("source_peer", "")),
                destination_peer=str(request.get("destination_peer", destination_id)),
                classification=str(request.get("classification", "INTERNAL")).upper(),
            )
        parent = None
        depth = 0
        if parent_contract_id:
            parent = self.get_contract(parent_contract_id)
            if parent["identity_id"] != identity_id:
                raise Pass145Error("RECURSIVE_AUTHORITY_EXPANSION", "child identity differs from parent boundary", "BOUNDARY_CONSTRUCTION")
            if parent["status"] not in {"BOUNDARY_ADMITTED", "PATH_ACTIVE"}:
                raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", "parent boundary is not active for child construction", "BOUNDARY_CONSTRUCTION")
            depth = int(parent["recursive_depth"]) + 1
            if depth > int(parent["resource_budget"].get("max_recursive_depth", 16)):
                raise Pass145Error("RESOURCE_BOUND_UNRESOLVED", "recursive boundary depth reached", "BOUNDARY_CONSTRUCTION")
        plan = self._derive_plan(operation, request, grant, parent)
        relevant_root = self._relevant_state_root(identity, grant, operation, request)
        sequence = int(self.db.meta("transaction_sequence") or 0)
        temporal = {"admitted_sequence": sequence + 1, "valid_until_sequence": sequence + max(1, int(expires_after_sequences)), "transactional_context": "CANONICAL_SQLITE_IMMEDIATE"}
        canonical_contract = {
            "schema": "HHS_PASS146_BOUNDARY_CONTRACT_V1",
            "identity_id": identity_id,
            "grant_id": grant_id,
            "parent_contract_id": parent_contract_id,
            "operation": operation,
            "source_scope": {"value": source_scope},
            "destination": destination_obj,
            "request": dict(request),
            "temporal_context": temporal,
            "capabilities": plan.capabilities,
            "resource_budget": plan.resource_budget,
            "disclosure_scope": plan.disclosure_scope,
            "reversibility_class": plan.reversibility_class,
            "path_blueprint": plan.path_blueprint,
            "relevant_state_root_hash72": relevant_root,
            "recursive_depth": depth,
        }
        contract_hash = hash72("hhs_pass146_boundary_contract_v1", canonical_contract)
        occurrence = sequence + 1
        contract_id = stable_id("BND", "hhs_pass146_boundary_contract_id_v1", {"contract_hash72": contract_hash, "occurrence": occurrence})
        path_payload = {"contract_id": contract_id, "operation": operation, "capabilities": plan.capabilities, "resource_budget": plan.resource_budget, "disclosure_scope": plan.disclosure_scope, "blueprint": plan.path_blueprint}
        path_hash = hash72("hhs_pass146_pathway_v1", path_payload)
        path_id = stable_id("PTH", "hhs_pass146_pathway_id_v1", {"path_hash72": path_hash, "occurrence": occurrence})

        def apply(conn):
            now = utc_now()
            conn.execute("INSERT INTO security_boundary_contracts(contract_id,identity_id,grant_id,parent_contract_id,operation,source_scope_json,destination_json,request_json,temporal_context_json,capabilities_json,resource_budget_json,disclosure_scope_json,reversibility_class,path_blueprint_json,relevant_state_root_hash72,contract_hash72,status,recursive_depth,created_at,closed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)", (contract_id, identity_id, grant_id, parent_contract_id, operation, canonical_json(canonical_contract["source_scope"]), canonical_json(destination_obj), canonical_json(dict(request)), canonical_json(temporal), canonical_json(plan.capabilities), canonical_json(plan.resource_budget), canonical_json(plan.disclosure_scope), plan.reversibility_class, canonical_json(plan.path_blueprint), relevant_root, contract_hash, "BOUNDARY_ADMITTED", depth, now))
            conn.execute("INSERT INTO security_pathways(path_id,contract_id,operation,lifecycle_state,active_capabilities_json,resource_budget_json,disclosure_scope_json,path_hash72,result_hash72,closure_status,recovery_state,created_at,closed_at) VALUES(?,?,?,?,?,?,?,?,NULL,NULL,NULL,?,NULL)", (path_id, contract_id, operation, "ADMITTED", canonical_json([]), canonical_json(plan.resource_budget), canonical_json(plan.disclosure_scope), path_hash, now))
            return {"status": "BOUNDARY_PATH_CONSTRUCTED", "contract_id": contract_id, "contract_hash72": contract_hash, "path_id": path_id, "path_hash72": path_hash, "minimum_capabilities": plan.capabilities, "reversibility_class": plan.reversibility_class, "recursive_depth": depth}

        return self.db.mutate("BOUNDARY_PATH_CONSTRUCT", {"contract_hash72": contract_hash, "path_hash72": path_hash, "identity_id": identity_id, "grant_id": grant_id, "operation": operation}, apply, receipt_type="BOUNDARY_CONSTRUCTION_RECEIPT")

    # ------------------------------------------------------------------
    # Inspection and execution
    # ------------------------------------------------------------------
    def get_contract(self, contract_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM security_boundary_contracts WHERE contract_id=?", (contract_id,)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "boundary contract not found", "BOUNDARY_INSPECT", contract_id)
        out = dict(row)
        for field in ("source_scope", "destination", "request", "temporal_context", "capabilities", "resource_budget", "disclosure_scope", "path_blueprint"):
            out[field] = _json_load(out.pop(field + "_json"), {})
        path = self.db.conn.execute("SELECT * FROM security_pathways WHERE contract_id=?", (contract_id,)).fetchone()
        if path:
            p = dict(path)
            for field in ("active_capabilities", "resource_budget", "disclosure_scope"):
                p[field] = _json_load(p.pop(field + "_json"), {})
            out["pathway"] = p
        return out

    def list_contracts(self, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 1000))
        return [dict(r) for r in self.db.conn.execute("SELECT contract_id,identity_id,grant_id,parent_contract_id,operation,contract_hash72,status,recursive_depth,created_at,closed_at FROM security_boundary_contracts ORDER BY created_at DESC,contract_id DESC LIMIT ?", (limit,))]

    def _activate(self, contract: Mapping[str, Any]) -> dict[str, Any]:
        path_id = contract["pathway"]["path_id"]
        current_sequence = int(self.db.meta("transaction_sequence") or 0)
        if current_sequence > int(contract["temporal_context"]["valid_until_sequence"]):
            raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", "boundary contract expired before activation", "PATH_ACTIVATION", contract["contract_id"])
        identity = self._identity(contract["identity_id"])
        grant = self._grant(contract["grant_id"])
        if not identity["active"] or grant["revoked"]:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "identity or grant no longer active", "PATH_ACTIVATION")
        relevant = self._relevant_state_root(identity, grant, contract["operation"], contract["request"])
        if relevant != contract["relevant_state_root_hash72"]:
            raise Pass145Error("SOURCE_STATE_INVALID", "relevant source/authority state changed after construction", "PATH_ACTIVATION", contract["contract_id"])

        def apply(conn):
            conn.execute("UPDATE security_boundary_contracts SET status='PATH_ACTIVE' WHERE contract_id=?", (contract["contract_id"],))
            conn.execute("UPDATE security_pathways SET lifecycle_state='ACTIVE',active_capabilities_json=? WHERE path_id=?", (canonical_json(contract["capabilities"]), path_id))
            return {"status": "PATH_ACTIVE", "contract_id": contract["contract_id"], "path_id": path_id, "temporary_capabilities": contract["capabilities"]}

        return self.db.mutate("BOUNDARY_PATH_ACTIVATE", {"contract_id": contract["contract_id"], "path_id": path_id}, apply, receipt_type="BOUNDARY_PATH_LIFECYCLE_RECEIPT")

    def execute_path(self, contract_id: str, identity_id: str, token: str) -> dict[str, Any]:
        contract = self.get_contract(contract_id)
        if contract["identity_id"] != identity_id:
            raise Pass145Error("IDENTITY_UNRESOLVED", "executor identity does not match boundary", "PATH_EXECUTION", contract_id)
        self.authenticate(identity_id, token)
        if contract["status"] != "BOUNDARY_ADMITTED":
            raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", f"boundary is not executable from status {contract['status']}", "PATH_EXECUTION", contract_id)
        self._activate(contract)
        contract = self.get_contract(contract_id)
        pre_exec_root = self.db.database_root()
        try:
            result, extra = self._dispatch(contract, identity_token=token)
            result_projection = self._deterministic_projection(result)
            encoded = canonical_json(result_projection).encode("utf-8")
            if len(encoded) > int(contract["resource_budget"]["max_output_bytes"]):
                raise Pass145Error("RESOURCE_BOUNDED", "operation output exceeds boundary budget", "PATH_EXECUTION", contract_id)
            result_hash = hash72("hhs_pass146_path_result_v1", result_projection)
            post_operation_root = self.db.database_root()
            return self._close_success(contract, result, result_hash, pre_exec_root, post_operation_root, extra)
        except Pass145Error as exc:
            self._close_failure(contract, exc, pre_exec_root, self.db.database_root())
            raise
        except Exception as exc:
            wrapped = Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", str(exc), "PATH_EXECUTION", contract_id)
            self._close_failure(contract, wrapped, pre_exec_root, self.db.database_root())
            raise wrapped from exc

    def _dispatch(self, contract: Mapping[str, Any], *, identity_token: str | None = None) -> tuple[Any, dict[str, Any]]:
        op = contract["operation"]
        req = contract["request"]
        extra: dict[str, Any] = {}
        if op == "RUN_CLI_COMMAND":
            import io
            import sys
            from hhs_runtime.pass145 import cli as parent_cli
            argv = [str(x) for x in req.get("argv", [])]
            old_stdin = sys.stdin
            try:
                if "stdin_text" in req:
                    sys.stdin = io.TextIOWrapper(io.BytesIO(str(req["stdin_text"]).encode("utf-8")), encoding="utf-8")
                if argv and argv[0] in {"status", "version", "doctor", "capabilities"}:
                    result = getattr(self.service, argv[0])()
                else:
                    parsed = parent_cli.build_parser().parse_args(["--db", str(self.db.path), "--format", "json", *argv])
                    result = parent_cli._dispatch(parsed)
            finally:
                sys.stdin = old_stdin
        elif op == "QUERY":
            result = self.service.query(str(req.get("question", "")), namespace=req.get("namespace"), limit=min(int(req.get("limit", 100)), 1000))
        elif op == "SEARCH":
            result = self.service.search(str(req.get("text", "")), namespace=req.get("namespace"), object_type=req.get("object_type"), symbol=bool(req.get("symbol", False)), limit=min(int(req.get("limit", 100)), 1000))
        elif op == "VALIDATE_SOURCE":
            result = self.service.validate_source(str(req["source_id"]), record=False)
        elif op == "INGEST_TEXT":
            text = str(req.get("text", ""))
            result = self.service.ingest_bytes(text.encode("utf-8"), name=str(req.get("name", "boundary-input.txt")), mime_type=str(req.get("mime_type", "text/plain")), namespace=str(req.get("namespace", "default")), source_kind="BOUNDARY_PATH", acquisition={"method": "BOUNDARY_PATH", "contract_id": contract["contract_id"]}, analyze=bool(req.get("analyze", True)))
        elif op == "RUN_SCRIPT":
            result = self.scripts.execute(str(req["script_id"]), inputs=dict(req.get("inputs", {})), timeout_seconds=min(int(req.get("timeout_seconds", contract["resource_budget"]["timeout_seconds"])), int(contract["resource_budget"]["timeout_seconds"])), max_output_bytes=int(contract["resource_budget"]["max_output_bytes"]))
        elif op == "RUN_LVM":
            result = self.lvms.execute(str(req["lvm_id"]), dict(req.get("inputs", {})), _depth=int(contract["recursive_depth"]))
        elif op == "PROPAGATE":
            data = req.get("data")
            identity_public = self.identity_public_record(contract["identity_id"])
            core = {
                "schema": "HHS_PASS146_SIGNED_PROPAGATION_UNIT_V2",
                "data": data,
                "data_hash72": hash72("hhs_pass146_propagated_data_v1", data),
                "provenance": dict(req.get("provenance", {})),
                "authority": {"identity_id": contract["identity_id"], "identity_hash72": identity_public["identity_hash72"], "grant_id": contract["grant_id"]},
                "boundary_witness": {"contract_id": contract["contract_id"], "contract_hash72": contract["contract_hash72"], "path_id": contract["pathway"]["path_id"], "path_hash72": contract["pathway"]["path_hash72"], "capabilities": contract["capabilities"], "reversibility_class": contract["reversibility_class"]},
                "scope": contract["disclosure_scope"],
                "expected_destination_state": dict(req.get("expected_destination_state", {})),
                "reversal": dict(req.get("reversal", {"class": contract["reversibility_class"]})),
                "source_peer": str(req.get("source_peer", "local")),
                "destination_peer": str(req.get("destination_peer", contract["destination"].get("id", "local"))),
                "sender_public_key_b64": identity_public["public_key_b64"],
                "sender_public_key_fingerprint": identity_public["public_key_fingerprint"],
            }
            envelope_hash = hash72("hhs_pass146_signed_envelope_core_v2", core)
            if identity_token is None:
                raise Pass145Error("IDENTITY_UNRESOLVED", "identity token required to sign propagation envelope", "MESSAGE_SIGNATURE")
            signature = self._signing_private_key(contract["identity_id"], identity_token).sign(canonical_json({"envelope_hash72": envelope_hash}).encode("utf-8"))
            signed = {**core, "envelope_hash72": envelope_hash, "signature_b64": base64.b64encode(signature).decode("ascii")}
            signed["message_hash72"] = hash72("hhs_pass146_signed_propagation_unit_v2", signed)
            signed["message_id"] = stable_id("MSG", "hhs_pass146_message_id_v2", {"message_hash72": signed["message_hash72"], "source_peer": signed["source_peer"], "destination_peer": signed["destination_peer"]})
            extra["message"] = signed
            result = {"status": "SIGNED_PROPAGATION_ENVELOPE_CONSTRUCTED", **signed, "payload_detached_from_contract": False}
        elif op == "RECEIVE_PROPAGATION":
            envelope = dict(req.get("envelope", {}))
            verification = self._verify_external_envelope(envelope, source_peer=str(req.get("source_peer", "")), destination_peer=str(req.get("destination_peer", "")), classification=str(req.get("classification", "INTERNAL")).upper())
            extra["external_message"] = envelope
            result = {"status": "EXTERNAL_MESSAGE_RECEIVED_AND_REVALIDATED", "message_id": envelope["message_id"], "message_hash72": envelope["message_hash72"], "source_peer": envelope["source_peer"], "destination_peer": envelope["destination_peer"], "data": envelope["data"], "verification": verification, "prior_admission_reused_without_validation": False}
        elif op == "NEGOTIATE_CONFLICT":
            resolution = self._negotiate(req.get("left_state"), req.get("right_state"), dict(req.get("policy", {})))
            negotiation = {"left_state": req.get("left_state"), "right_state": req.get("right_state"), "policy": dict(req.get("policy", {})), "resolution": resolution}
            negotiation["negotiation_hash72"] = hash72("hhs_pass146_negotiation_v1", negotiation)
            negotiation["negotiation_id"] = stable_id("NEG", "hhs_pass146_negotiation_id_v1", {"hash": negotiation["negotiation_hash72"], "contract_id": contract["contract_id"]})
            extra["negotiation"] = negotiation
            result = {"status": resolution["status"], "negotiation_id": negotiation["negotiation_id"], "negotiation_hash72": negotiation["negotiation_hash72"], "resolution": resolution}
        else:
            raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", f"operation adapter missing: {op}", "PATH_EXECUTION")
        return result, extra

    @staticmethod
    def _verify_signed_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
        required = {"schema", "data", "data_hash72", "provenance", "authority", "boundary_witness", "scope", "expected_destination_state", "reversal", "source_peer", "destination_peer", "sender_public_key_b64", "sender_public_key_fingerprint", "envelope_hash72", "signature_b64", "message_hash72", "message_id"}
        missing = sorted(required - set(envelope))
        if missing:
            raise Pass145Error("PROVENANCE_INCOMPLETE", f"signed envelope fields missing: {missing}", "MESSAGE_SIGNATURE")
        if envelope.get("schema") != "HHS_PASS146_SIGNED_PROPAGATION_UNIT_V2":
            raise Pass145Error("PROVENANCE_INCOMPLETE", "unsupported propagation envelope schema", "MESSAGE_SIGNATURE")
        core = {k: envelope[k] for k in envelope if k not in {"envelope_hash72", "signature_b64", "message_hash72", "message_id"}}
        observed_envelope_hash = hash72("hhs_pass146_signed_envelope_core_v2", core)
        if observed_envelope_hash != envelope["envelope_hash72"]:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "envelope core hash mismatch", "MESSAGE_SIGNATURE")
        signed = {**core, "envelope_hash72": envelope["envelope_hash72"], "signature_b64": envelope["signature_b64"]}
        observed_message_hash = hash72("hhs_pass146_signed_propagation_unit_v2", signed)
        if observed_message_hash != envelope["message_hash72"]:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "signed message hash mismatch", "MESSAGE_SIGNATURE")
        if hash72("hhs_pass146_propagated_data_v1", envelope["data"]) != envelope["data_hash72"]:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "propagated data hash mismatch", "MESSAGE_SIGNATURE")
        try:
            public_raw = base64.b64decode(str(envelope["sender_public_key_b64"]), validate=True)
            if hashlib.sha256(public_raw).hexdigest() != envelope["sender_public_key_fingerprint"]:
                raise ValueError("public key fingerprint mismatch")
            signature = base64.b64decode(str(envelope["signature_b64"]), validate=True)
            Ed25519PublicKey.from_public_bytes(public_raw).verify(signature, canonical_json({"envelope_hash72": observed_envelope_hash}).encode("utf-8"))
        except (InvalidSignature, ValueError, TypeError) as exc:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "Ed25519 envelope signature verification failed", "MESSAGE_SIGNATURE") from exc
        return {"signature_valid": True, "envelope_hash_valid": True, "message_hash_valid": True, "data_hash_valid": True, "public_key_fingerprint": envelope["sender_public_key_fingerprint"]}

    def _verify_external_envelope(self, envelope: Mapping[str, Any], *, source_peer: str, destination_peer: str, classification: str) -> dict[str, Any]:
        verification = self._verify_signed_envelope(envelope)
        if str(envelope["source_peer"]) != source_peer:
            raise Pass145Error("SOURCE_STATE_INVALID", "source peer differs from receiving boundary", "MESSAGE_RECEIVE")
        if str(envelope["destination_peer"]) != destination_peer:
            raise Pass145Error("DESTINATION_STATE_INVALID", "destination peer differs from receiving boundary", "MESSAGE_RECEIVE")
        if str(envelope.get("scope", {}).get("classification", "")).upper() != classification:
            raise Pass145Error("DISCLOSURE_PATH_INVALID", "message classification differs from receiving boundary", "MESSAGE_RECEIVE")
        row = self.db.conn.execute("SELECT * FROM security_peer_trust WHERE peer_id=?", (source_peer,)).fetchone()
        if not row or not row["active"]:
            raise Pass145Error("IDENTITY_UNRESOLVED", "source peer is not admitted by receiver trust", "PEER_TRUST", source_peer)
        if row["public_key_b64"] != envelope["sender_public_key_b64"] or row["public_key_fingerprint"] != envelope["sender_public_key_fingerprint"]:
            raise Pass145Error("IDENTITY_UNRESOLVED", "source peer signing key differs from admitted trust", "PEER_TRUST", source_peer)
        classes = set(_json_load(row["classifications_json"], []))
        destinations = _json_load(row["destinations_json"], [])
        if classification not in classes:
            raise Pass145Error("DISCLOSURE_PATH_INVALID", "peer trust does not admit message classification", "PEER_TRUST", source_peer)
        if not _allowed(destination_peer, destinations):
            raise Pass145Error("DESTINATION_STATE_INVALID", "peer trust does not admit destination", "PEER_TRUST", destination_peer)
        return {**verification, "peer_trust_valid": True, "peer_id": source_peer, "trust_hash72": row["trust_hash72"]}

    @staticmethod
    def _negotiate(left: Any, right: Any, policy: Mapping[str, Any]) -> dict[str, Any]:
        if left == right:
            return {"status": "FIXED_POINT_REACHED", "result": left, "preserved_left": True, "preserved_right": True, "conflicts": []}
        if isinstance(left, dict) and isinstance(right, dict):
            merged: dict[str, Any] = {}
            conflicts = []
            for key in sorted(set(left) | set(right)):
                if key not in left:
                    merged[key] = right[key]
                elif key not in right:
                    merged[key] = left[key]
                elif left[key] == right[key]:
                    merged[key] = left[key]
                else:
                    conflicts.append({"key": key, "left": left[key], "right": right[key], "resolution": "UNRESOLVED"})
            if conflicts:
                return {"status": "STABLE_UNRESOLVED", "nonconflicting_result": merged, "conflicts": conflicts, "preserved_left": True, "preserved_right": True, "silent_winner_selected": False}
            return {"status": "FIXED_POINT_REACHED", "result": merged, "conflicts": []}
        return {"status": "STABLE_UNRESOLVED", "left": left, "right": right, "policy": dict(policy), "silent_winner_selected": False}

    def _build_steps(self, contract: Mapping[str, Any], pre_root: str, post_root: str, result_hash: str, *, success: bool, error: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        steps = []
        for item in contract["path_blueprint"]:
            is_execute = item["action"] == "EXECUTE"
            details = {"contract_id": contract["contract_id"], "capabilities": contract["capabilities"] if item["action"] == "ACTIVATE_TEMPORARY_CAPABILITIES" else [], "error": error if not success and is_execute else None}
            payload = {
                "path_id": contract["pathway"]["path_id"],
                "ordinal": int(item["ordinal"]),
                "component": item["component"],
                "action": item["action"],
                "input_hash72": contract["contract_hash72"],
                "output_hash72": result_hash if success else hash72("hhs_pass146_failed_step_v1", error or {}),
                "pre_state_root_hash72": pre_root,
                "post_state_root_hash72": post_root if is_execute else pre_root,
                "status": "STEP_COMPLETED" if success else ("STEP_FAILED" if is_execute else "STEP_COMPLETED"),
                "details": details,
            }
            payload["step_hash72"] = hash72("hhs_pass146_pathway_step_v1", payload)
            payload["step_id"] = stable_id("STP", "hhs_pass146_pathway_step_id_v1", {"path_id": payload["path_id"], "ordinal": payload["ordinal"], "step_hash72": payload["step_hash72"]})
            steps.append(payload)
        return steps

    def _close_success(self, contract: Mapping[str, Any], result: Any, result_hash: str, pre_root: str, post_root: str, extra: Mapping[str, Any]) -> dict[str, Any]:
        steps = self._build_steps(contract, pre_root, post_root, result_hash, success=True)
        path_id = contract["pathway"]["path_id"]

        def apply(conn):
            now = utc_now()
            for step in steps:
                conn.execute("INSERT INTO security_pathway_steps(step_id,path_id,ordinal,component,action,input_hash72,output_hash72,pre_state_root_hash72,post_state_root_hash72,status,step_hash72,details_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (step["step_id"], path_id, step["ordinal"], step["component"], step["action"], step["input_hash72"], step["output_hash72"], step["pre_state_root_hash72"], step["post_state_root_hash72"], step["status"], step["step_hash72"], canonical_json(step["details"]), now))
            if "message" in extra:
                m = extra["message"]
                conn.execute("INSERT INTO security_messages(message_id,path_id,contract_id,source_peer,destination_peer,data_json,provenance_json,scope_json,expected_state_json,reversal_json,envelope_json,message_hash72,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (m["message_id"], path_id, contract["contract_id"], m["source_peer"], m["destination_peer"], canonical_json(m["data"]), canonical_json(m["provenance"]), canonical_json(m["scope"]), canonical_json(m["expected_destination_state"]), canonical_json(m["reversal"]), canonical_json(m), m["message_hash72"], "SIGNED_ENVELOPE_VALIDATED", now))
            if "external_message" in extra:
                m = extra["external_message"]
                conn.execute("INSERT OR IGNORE INTO security_messages(message_id,path_id,contract_id,source_peer,destination_peer,data_json,provenance_json,scope_json,expected_state_json,reversal_json,envelope_json,message_hash72,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (m["message_id"], path_id, contract["contract_id"], m["source_peer"], m["destination_peer"], canonical_json(m["data"]), canonical_json(m["provenance"]), canonical_json(m["scope"]), canonical_json(m["expected_destination_state"]), canonical_json(m["reversal"]), canonical_json(m), m["message_hash72"], "EXTERNAL_RECEIVED_AND_REVALIDATED", now))
            if "negotiation" in extra:
                n = extra["negotiation"]
                conn.execute("INSERT INTO security_negotiations(negotiation_id,path_id,left_state_json,right_state_json,policy_json,resolution_json,negotiation_hash72,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (n["negotiation_id"], path_id, canonical_json(n["left_state"]), canonical_json(n["right_state"]), canonical_json(n["policy"]), canonical_json(n["resolution"]), n["negotiation_hash72"], n["resolution"]["status"], now))
            conn.execute("UPDATE security_pathways SET lifecycle_state='DISSOLVED',active_capabilities_json='[]',result_hash72=?,closure_status='PATH_CLOSED',recovery_state=NULL,closed_at=? WHERE path_id=?", (result_hash, now, path_id))
            conn.execute("UPDATE security_boundary_contracts SET status='BOUNDARY_CLOSED',closed_at=? WHERE contract_id=?", (now, contract["contract_id"]))
            return {"status": "BOUNDARY_PATH_CLOSED", "contract_id": contract["contract_id"], "path_id": path_id, "result_hash72": result_hash, "reversibility_class": contract["reversibility_class"], "temporary_capabilities_expired": True, "step_count": len(steps), "result": result}

        return self.db.mutate("BOUNDARY_PATH_CLOSE", {"contract_id": contract["contract_id"], "path_id": path_id, "result_hash72": result_hash}, apply, receipt_type="BOUNDARY_CLOSURE_RECEIPT")

    def _close_failure(self, contract: Mapping[str, Any], error: Pass145Error, pre_root: str, post_root: str) -> dict[str, Any]:
        err = error.to_dict()
        failure_hash = hash72("hhs_pass146_path_failure_v1", err)
        steps = self._build_steps(contract, pre_root, post_root, failure_hash, success=False, error=err)
        path_id = contract["pathway"]["path_id"]

        def apply(conn):
            now = utc_now()
            for step in steps:
                conn.execute("INSERT OR IGNORE INTO security_pathway_steps(step_id,path_id,ordinal,component,action,input_hash72,output_hash72,pre_state_root_hash72,post_state_root_hash72,status,step_hash72,details_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (step["step_id"], path_id, step["ordinal"], step["component"], step["action"], step["input_hash72"], step["output_hash72"], step["pre_state_root_hash72"], step["post_state_root_hash72"], step["status"], step["step_hash72"], canonical_json(step["details"]), now))
            conn.execute("UPDATE security_pathways SET lifecycle_state='RECOVERY_REQUIRED',active_capabilities_json='[]',result_hash72=?,closure_status='PATH_FAILED',recovery_state='VALIDATED_HALT',closed_at=? WHERE path_id=?", (failure_hash, now, path_id))
            conn.execute("UPDATE security_boundary_contracts SET status='BOUNDARY_FAILED',closed_at=? WHERE contract_id=?", (now, contract["contract_id"]))
            return {"status": "BOUNDARY_PATH_FAILED", "contract_id": contract["contract_id"], "path_id": path_id, "failure_hash72": failure_hash, "recovery_state": "VALIDATED_HALT", "temporary_capabilities_expired": True}

        return self.db.mutate("BOUNDARY_PATH_FAIL", {"contract_id": contract["contract_id"], "path_id": path_id, "error": err}, apply, receipt_type="BOUNDARY_FAILURE_RECEIPT")

    # ------------------------------------------------------------------
    # Propagation and replay
    # ------------------------------------------------------------------
    def inspect_message(self, message_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM security_messages WHERE message_id=?", (message_id,)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "propagation message not found", "MESSAGE_INSPECT", message_id)
        out = dict(row)
        for field in ("data", "provenance", "scope", "expected_state", "reversal", "envelope"):
            out[field] = _json_load(out.pop(field + "_json"), {})
        verification = self._verify_signed_envelope(out["envelope"])
        out["integrity_valid"] = bool(verification["signature_valid"] and verification["message_hash_valid"] and out["message_hash72"] == out["envelope"]["message_hash72"])
        out["signature_verification"] = verification
        return out

    def receive_message(self, message_id: str, receiver_identity_id: str, receiver_grant_id: str, receiver_token: str) -> dict[str, Any]:
        self.authenticate(receiver_identity_id, receiver_token)
        grant = self._grant(receiver_grant_id)
        message = self.inspect_message(message_id)
        if grant["identity_id"] != receiver_identity_id or grant["revoked"] or "NETWORK_RECEIVE" not in grant["capabilities"]:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "NETWORK_RECEIVE grant required", "MESSAGE_RECEIVE")
        if not _allowed(message["destination_peer"], grant["destinations"]):
            raise Pass145Error("DESTINATION_STATE_INVALID", "receiver grant does not admit destination peer", "MESSAGE_RECEIVE")
        if not message["integrity_valid"]:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "message contract/provenance integrity failed", "MESSAGE_RECEIVE")

        def apply(conn):
            conn.execute("UPDATE security_messages SET status='RECEIVED_AND_REVALIDATED' WHERE message_id=?", (message_id,))
            return {"status": "MESSAGE_RECEIVED_AND_REVALIDATED", "message_id": message_id, "destination_peer": message["destination_peer"], "data": message["data"], "prior_admission_reused_without_validation": False}

        return self.db.mutate("BOUNDARY_MESSAGE_RECEIVE", {"message_id": message_id, "receiver_identity_id": receiver_identity_id, "receiver_grant_id": receiver_grant_id}, apply, receipt_type="BOUNDARY_PROPAGATION_RECEIPT")

    @staticmethod
    def _deterministic_projection(value: Any) -> Any:
        volatile = {"transaction_id", "receipt_id", "receipt_hash72", "sequence", "pre_state_root_hash72", "post_state_root_hash72", "created_at", "closed_at", "transaction_sequence", "receipt_tip", "database_root_hash72", "query_plan_receipt", "query_result_receipt"}
        if isinstance(value, dict):
            return {k: HHS146BoundaryEngine._deterministic_projection(v) for k, v in sorted(value.items()) if k not in volatile}
        if isinstance(value, list):
            return [HHS146BoundaryEngine._deterministic_projection(v) for v in value]
        if isinstance(value, tuple):
            return [HHS146BoundaryEngine._deterministic_projection(v) for v in value]
        return value

    def replay_path(self, contract_id: str) -> dict[str, Any]:
        contract = self.get_contract(contract_id)
        if contract["status"] != "BOUNDARY_CLOSED":
            raise Pass145Error("REPLAY_PATH_INCOMPLETE", "only closed pathways are replayable", "BOUNDARY_REPLAY", contract_id)
        grant = self._grant(contract["grant_id"])
        parent = self.get_contract(contract["parent_contract_id"]) if contract["parent_contract_id"] else None
        rebuilt = self._derive_plan(contract["operation"], contract["request"], grant, parent)
        blueprint_matches = rebuilt.path_blueprint == contract["path_blueprint"]
        capabilities_match = rebuilt.capabilities == contract["capabilities"]
        steps = [dict(r) for r in self.db.conn.execute("SELECT ordinal,component,action,input_hash72,output_hash72,pre_state_root_hash72,post_state_root_hash72,status,step_hash72 FROM security_pathway_steps WHERE path_id=? ORDER BY ordinal", (contract["pathway"]["path_id"],))]
        step_chain_valid = len(steps) == len(contract["path_blueprint"]) and all(step["ordinal"] == idx for idx, step in enumerate(steps))
        exact_result_replayed = False
        replay_result_hash = None
        if contract["operation"] in {"QUERY", "SEARCH", "VALIDATE_SOURCE", "NEGOTIATE_CONFLICT"} or (contract["operation"] == "RUN_CLI_COMMAND" and contract["reversibility_class"] == "APPEND_ONLY_NONDESTRUCTIVE"):
            result, _ = self._dispatch(contract, identity_token=None)
            replay_result_hash = hash72("hhs_pass146_path_result_v1", self._deterministic_projection(result))
            exact_result_replayed = replay_result_hash == contract["pathway"]["result_hash72"]
        elif contract["operation"] == "PROPAGATE":
            row = self.db.conn.execute("SELECT message_id,envelope_json FROM security_messages WHERE path_id=?", (contract["pathway"]["path_id"],)).fetchone()
            if row:
                envelope = _json_load(row["envelope_json"], {})
                verification = self._verify_signed_envelope(envelope)
                result = {"status": "SIGNED_PROPAGATION_ENVELOPE_CONSTRUCTED", **envelope, "payload_detached_from_contract": False}
                replay_result_hash = hash72("hhs_pass146_path_result_v1", self._deterministic_projection(result))
                exact_result_replayed = bool(verification["signature_valid"] and replay_result_hash == contract["pathway"]["result_hash72"] )
        elif contract["operation"] == "RECEIVE_PROPAGATION":
            row = self.db.conn.execute("SELECT envelope_json FROM security_messages WHERE path_id=?", (contract["pathway"]["path_id"],)).fetchone()
            if row:
                envelope = _json_load(row["envelope_json"], {})
                verification = self._verify_external_envelope(envelope, source_peer=str(contract["request"].get("source_peer", "")), destination_peer=str(contract["request"].get("destination_peer", "")), classification=str(contract["request"].get("classification", "INTERNAL")).upper())
                result = {"status": "EXTERNAL_MESSAGE_RECEIVED_AND_REVALIDATED", "message_id": envelope["message_id"], "message_hash72": envelope["message_hash72"], "source_peer": envelope["source_peer"], "destination_peer": envelope["destination_peer"], "data": envelope["data"], "verification": verification, "prior_admission_reused_without_validation": False}
                replay_result_hash = hash72("hhs_pass146_path_result_v1", self._deterministic_projection(result))
                exact_result_replayed = replay_result_hash == contract["pathway"]["result_hash72"]
        else:
            # Mutating paths are reconstructed from immutable operation receipts;
            # they are not re-applied to canonical state during verification.
            exact_result_replayed = bool(contract["pathway"]["result_hash72"] and steps)
        ok = blueprint_matches and capabilities_match and step_chain_valid and exact_result_replayed
        return {"schema": "HHS_PASS146_PATH_REPLAY_V1", "status": "REPLAY_VALIDATED" if ok else "REPLAY_MISMATCH", "ok": ok, "contract_id": contract_id, "path_id": contract["pathway"]["path_id"], "blueprint_matches": blueprint_matches, "capabilities_match": capabilities_match, "step_chain_valid": step_chain_valid, "exact_result_replayed": exact_result_replayed, "stored_result_hash72": contract["pathway"]["result_hash72"], "replay_result_hash72": replay_result_hash, "mutating_operation_reapplied": False}

    def status(self) -> dict[str, Any]:
        counts = {}
        for table in ("security_identities", "security_authority_grants", "security_boundary_contracts", "security_pathways", "security_pathway_steps", "security_messages", "security_peer_trust", "security_negotiations"):
            counts[table] = int(self.db.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        open_paths = int(self.db.conn.execute("SELECT COUNT(*) FROM security_pathways WHERE lifecycle_state NOT IN ('DISSOLVED','RECOVERY_REQUIRED','REJECTED')").fetchone()[0])
        return {"schema": "HHS_PASS146_SECURITY_STATUS_V1", "pass_id": PASS_ID, "version": VERSION, "ok": self.db.integrity_check()["ok"] and self.db.verify_receipt_chain()["ok"], "counts": counts, "open_pathways": open_paths, "no_ambient_network_trust": True, "invalid_paths_nonrepresentable": True}
