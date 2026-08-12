"""Pass 218 cumulative relational-curriculum implementation surfaces."""

from importlib import import_module

from .curriculum import (
    CurriculumCursor,
    CurriculumManifest,
    CurriculumSource,
    CurriculumStage,
    Pass218CurriculumOrderError,
    build_curriculum_manifest,
)
from .genesis import (
    ExactDistributionalRelation,
    GenesisSeed,
    GenesisSeedBuilder,
    Pass166Word2VecAdapter,
    RelationStatus,
    repository_asset_manifest,
)
from .grammar import (
    GrammarRule,
    GrammarRuleSet,
    PASS218_GRAMMAR_COMPILER_VERSION,
    compile_grammar_rules,
)
from .hydration import (
    NarrativeBeat,
    NarrativeBeatHydrator,
    NarrativeHydrationCandidate,
    PASS218_NARRATIVE_HYDRATOR_VERSION,
)
from .transaction import (
    DeterministicStructuralStore,
    PASS218_SOURCE_TRANSACTION_VERSION,
    Pass218TransactionError,
    Pass218TransactionStateError,
    Pass218TransactionValidationError,
    SourceTransaction,
    StructuralStoreReceipt,
    TransactionPhase,
)

# Iteration 4 deliberately depends on the heavier inherited Pass 175 runtime.
# Keep these exports lazy so importing validated Iterations 1-3 does not acquire
# new optional dependencies merely because the cumulative package grew.
_STAGING_EXPORTS = frozenset({
    "ClosedTransactionVectorVM5184Adapter",
    "NonAuthoritativeVectorStageStore",
    "PASS218_VECTOR_VM5184_STAGER_VERSION",
    "Pass218VectorStageError",
    "Pass218VectorStageStateError",
    "Pass218VectorStageValidationError",
    "VectorVM5184StageCandidate",
})


def __getattr__(name: str):
    if name not in _STAGING_EXPORTS:
        raise AttributeError(name)
    module = import_module(".staging", __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | _STAGING_EXPORTS)


__all__ = [
    "CurriculumCursor",
    "CurriculumManifest",
    "CurriculumSource",
    "CurriculumStage",
    "Pass218CurriculumOrderError",
    "build_curriculum_manifest",
    "ExactDistributionalRelation",
    "GenesisSeed",
    "GenesisSeedBuilder",
    "Pass166Word2VecAdapter",
    "RelationStatus",
    "repository_asset_manifest",
    "GrammarRule",
    "GrammarRuleSet",
    "PASS218_GRAMMAR_COMPILER_VERSION",
    "compile_grammar_rules",
    "NarrativeBeat",
    "NarrativeBeatHydrator",
    "NarrativeHydrationCandidate",
    "PASS218_NARRATIVE_HYDRATOR_VERSION",
    "DeterministicStructuralStore",
    "PASS218_SOURCE_TRANSACTION_VERSION",
    "Pass218TransactionError",
    "Pass218TransactionStateError",
    "Pass218TransactionValidationError",
    "SourceTransaction",
    "StructuralStoreReceipt",
    "TransactionPhase",
    "ClosedTransactionVectorVM5184Adapter",
    "NonAuthoritativeVectorStageStore",
    "PASS218_VECTOR_VM5184_STAGER_VERSION",
    "Pass218VectorStageError",
    "Pass218VectorStageStateError",
    "Pass218VectorStageValidationError",
    "VectorVM5184StageCandidate",
]
