"""Pass 174 harmonic phase-gear, Hash216 retrieval, and Visual IDE runtime."""
from .inheritance import (
    LegacyAuthorityManifest,
    LegacyInheritanceError,
    LegacySpecification,
    build_legacy_manifest,
    verify_manifest,
)
from .runtime import (
    DIRECTED_PHASE_RELATIONSHIPS,
    HASH216_CHARACTERS,
    PHASE_LOCK_PERIOD,
    RUNTIME_VERSION,
    EfficiencyRecord,
    EncryptedVectorObject,
    EncryptedVectorStore,
    ExactCost,
    HarmonicGate,
    Hash216Array,
    Pass174Error,
    Pass174Runtime as CorePass174Runtime,
    Pass174VMRCAuthority,
    PhaseCoordinate,
)
from .pass175_adapter import (
    PASS175_AUTHORITY_OPERATIONS,
    Pass175AuthorityAdapter,
    Pass175AuthorityOperation,
)
from .storage import PersistentEncryptedVectorStore

# Package-level authority includes the additive, fail-closed Pass 175 mapping
# membrane.  The underlying Pass 174 implementation remains available as
# CorePass174Runtime for dependency-scoped verification and compatibility.
Pass174Runtime = Pass175AuthorityAdapter

__all__ = [
    "DIRECTED_PHASE_RELATIONSHIPS",
    "HASH216_CHARACTERS",
    "PASS175_AUTHORITY_OPERATIONS",
    "PHASE_LOCK_PERIOD",
    "RUNTIME_VERSION",
    "CorePass174Runtime",
    "EfficiencyRecord",
    "EncryptedVectorObject",
    "EncryptedVectorStore",
    "ExactCost",
    "HarmonicGate",
    "Hash216Array",
    "LegacyAuthorityManifest",
    "LegacyInheritanceError",
    "LegacySpecification",
    "Pass174Error",
    "Pass174Runtime",
    "Pass174VMRCAuthority",
    "Pass175AuthorityAdapter",
    "Pass175AuthorityOperation",
    "PersistentEncryptedVectorStore",
    "PhaseCoordinate",
    "build_legacy_manifest",
    "verify_manifest",
]
