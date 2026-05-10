# ============================================================================
# hhs_backend/runtime/runtime_semantic_memory_engine.py
# HARMONICODE / HHS
# CANONICAL SEMANTIC MEMORY ENGINE
#
# PURPOSE
# -------
# Semantic cognition substrate for:
#
#   - semantic replay indexing
#   - multimodal embedding persistence
#   - symbolic attractor retrieval
#   - replay-memory association
#   - semantic graph traversal
#   - adaptive memory routing
#   - vectorized runtime cognition
#   - memory-linked prediction
#
# Semantic memory MUST remain replay-safe and append-only.
#
# ============================================================================

from __future__ import annotations

import hashlib
import json
import logging
import math
import statistics
import threading
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

from hhs_storage.runtime_state_store_v1 import (
    runtime_state_store
)

from hhs_backend.runtime.runtime_replay_engine import (
    runtime_replay_engine,
    HHSReplayResult
)

from hhs_backend.runtime.runtime_prediction_engine import (
    runtime_prediction_engine
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("HHS_SEMANTIC_MEMORY")

# ============================================================================
# MEMORY TYPES
# ============================================================================

TYPE_RUNTIME = "runtime"

TYPE_REPLAY = "replay"

TYPE_MULTIMODAL = "multimodal"

TYPE_SYMBOLIC = "symbolic"

TYPE_ATTRACTOR = "attractor"

TYPE_PREDICTIVE = "predictive"

# ============================================================================
# MEMORY RECORD
# ============================================================================

@dataclass
class HHSSemanticMemoryRecord:

    memory_id: str

    created_at: float

    memory_type: str

    hash72: str

    semantic_text: str

    embedding: List[float]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# MEMORY LINK
# ============================================================================

@dataclass
class HHSSemanticMemoryLink:

    link_id: str

    created_at: float

    source_memory_id: str

    target_memory_id: str

    weight: float

    relationship: str

# ============================================================================
# SEARCH RESULT
# ============================================================================

@dataclass
class HHSSemanticSearchResult:

    memory_id: str

    similarity: float

    semantic_text: str

    metadata: Dict[str, Any]

# ============================================================================
# SEMANTIC MEMORY ENGINE
# ============================================================================

class HHSSemanticMemoryEngine:

    """
    Canonical semantic cognition substrate.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.memories: Dict[
            str,
            HHSSemanticMemoryRecord
        ] = {}

        self.links: Dict[
            str,
            HHSSemanticMemoryLink
        ] = {}

        self.hash_index: Dict[
            str,
            List[str]
        ] = {}

        self.total_memories = 0

        self.total_links = 0

        self.total_queries = 0

    # =====================================================================
    # EMBEDDINGS
    # =====================================================================

    def generate_embedding(
        self,
        text: str,
        dimensions: int = 72
    ) -> List[float]:

        digest = hashlib.sha256(
            text.encode("utf-8")
        ).digest()

        values = []

        for i in range(dimensions):

            byte = digest[
                i % len(digest)
            ]

            value = (
                (byte / 255.0) * 2.0
            ) - 1.0

            values.append(value)

        return values

    # =====================================================================
    # MEMORY INGESTION
    # =====================================================================

    def ingest_memory(

        self,

        memory_type: str,

        semantic_text: str,

        hash72: Optional[str] = None,

        metadata: Optional[Dict] = None
    ) -> HHSSemanticMemoryRecord:

        with self.lock:

            if hash72 is None:

                hash72 = hashlib.sha256(

                    semantic_text.encode("utf-8")

                ).hexdigest()[:72]

            embedding = self.generate_embedding(
                semantic_text
            )

            record = HHSSemanticMemoryRecord(

                memory_id=str(uuid.uuid4()),

                created_at=time.time(),

                memory_type=memory_type,

                hash72=hash72,

                semantic_text=semantic_text,

                embedding=embedding,

                metadata=metadata or {}
            )

            self.memories[
                record.memory_id
            ] = record

            if hash72 not in self.hash_index:

                self.hash_index[hash72] = []

            self.hash_index[hash72].append(
                record.memory_id
            )

            runtime_state_store.store_vector_record(

                hash72=hash72,

                vector=embedding
            )

            self.total_memories += 1

            logger.info(
                f"Semantic memory ingested: "
                f"{record.memory_id}"
            )

            return record

    # =====================================================================
    # LINKING
    # =====================================================================

    def link_memories(

        self,

        source_memory_id: str,

        target_memory_id: str,

        relationship: str,

        weight: float = 1.0
    ) -> HHSSemanticMemoryLink:

        with self.lock:

            link = HHSSemanticMemoryLink(

                link_id=str(uuid.uuid4()),

                created_at=time.time(),

                source_memory_id=
                    source_memory_id,

                target_memory_id=
                    target_memory_id,

                weight=weight,

                relationship=relationship
            )

            self.links[
                link.link_id
            ] = link

            self.total_links += 1

            logger.info(
                f"Semantic link created: "
                f"{link.link_id}"
            )

            return link

    # =====================================================================
    # VECTOR SIMILARITY
    # =====================================================================

    def cosine_similarity(

        self,

        a: List[float],

        b: List[float]
    ) -> float:

        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))

        norm_a = math.sqrt(
            sum(x * x for x in a)
        )

        norm_b = math.sqrt(
            sum(y * y for y in b)
        )

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    # =====================================================================
    # SEARCH
    # =====================================================================

    def semantic_search(

        self,

        query: str,

        limit: int = 10
    ) -> List[HHSSemanticSearchResult]:

        with self.lock:

            self.total_queries += 1

            query_embedding = (
                self.generate_embedding(query)
            )

            results = []

            for memory in self.memories.values():

                similarity = (
                    self.cosine_similarity(

                        query_embedding,

                        memory.embedding
                    )
                )

                results.append(

                    HHSSemanticSearchResult(

                        memory_id=
                            memory.memory_id,

                        similarity=
                            similarity,

                        semantic_text=
                            memory.semantic_text,

                        metadata=
                            memory.metadata
                    )
                )

            results.sort(

                key=lambda x: x.similarity,

                reverse=True
            )

            return results[:limit]

    # =====================================================================
    # REPLAY INGESTION
    # =====================================================================

    def ingest_replay(
        self,
        replay: HHSReplayResult
    ):

        replay_memories = []

        for frame in replay.frames:

            runtime = frame.runtime_packet.get(
                "runtime",
                {}
            )

            semantic_text = json.dumps(
                runtime,
                sort_keys=True
            )

            memory = self.ingest_memory(

                memory_type=TYPE_REPLAY,

                semantic_text=semantic_text,

                hash72=runtime.get(
                    "state_hash72",
                    ""
                ),

                metadata={

                    "replay_id":
                        replay.replay_id,

                    "frame_index":
                        frame.frame_index
                }
            )

            replay_memories.append(memory)

        for i in range(
            len(replay_memories) - 1
        ):

            self.link_memories(

                replay_memories[i].memory_id,

                replay_memories[i + 1].memory_id,

                relationship="temporal"
            )

        logger.info(
            f"Replay ingested into semantic "
            f"memory: {replay.replay_id}"
        )

        return replay_memories

    # =====================================================================
    # ATTRACTOR MEMORY
    # =====================================================================

    def build_attractor_memory(
        self,
        replay: HHSReplayResult
    ):

        prediction = (

            runtime_prediction_engine
            .generate_predictive_replay(
                horizon=10
            )
        )

        attractors = prediction[
            "attractors"
        ]

        records = []

        for attractor in attractors:

            semantic_text = (

                f"ATTRACTOR "
                f"{attractor.dominant_hash72} "
                f"stability="
                f"{attractor.stability}"
            )

            memory = self.ingest_memory(

                memory_type=TYPE_ATTRACTOR,

                semantic_text=semantic_text,

                hash72=attractor.dominant_hash72,

                metadata={

                    "stability":
                        attractor.stability,

                    "frequency":
                        attractor.frequency
                }
            )

            records.append(memory)

        return records

    # =====================================================================
    # MEMORY ROUTING
    # =====================================================================

    def route_memory_context(
        self,
        query: str
    ):

        results = self.semantic_search(
            query,
            limit=5
        )

        replay = (
            runtime_replay_engine
            .predictive_replay(
                horizon=5
            )
        )

        runtime_replay_engine.verify_replay_equivalence(
            replay
        )

        trajectory = (

            runtime_prediction_engine
            .score_replay(replay)
        )

        return {

            "semantic_results":
                results,

            "trajectory":
                trajectory,

            "replay":
                replay
        }

    # =====================================================================
    # GRAPH EXPORT
    # =====================================================================

    def export_memory_graph(self):

        with self.lock:

            return {

                "nodes": [

                    {

                        "memory_id":
                            memory.memory_id,

                        "type":
                            memory.memory_type,

                        "hash72":
                            memory.hash72

                    }

                    for memory in self.memories.values()
                ],

                "edges": [

                    {

                        "source":
                            link.source_memory_id,

                        "target":
                            link.target_memory_id,

                        "relationship":
                            link.relationship,

                        "weight":
                            link.weight

                    }

                    for link in self.links.values()
                ]
            }

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        similarities = []

        memories = list(
            self.memories.values()
        )

        for i in range(min(len(memories), 10)):

            for j in range(i + 1, min(len(memories), 10)):

                sim = self.cosine_similarity(

                    memories[i].embedding,

                    memories[j].embedding
                )

                similarities.append(sim)

        avg_similarity = 0.0

        if similarities:

            avg_similarity = statistics.mean(
                similarities
            )

        return {

            "memories":
                self.total_memories,

            "links":
                self.total_links,

            "queries":
                self.total_queries,

            "average_similarity":
                avg_similarity
        }

# ============================================================================
# GLOBAL ENGINE
# ============================================================================

runtime_semantic_memory_engine = (
    HHSSemanticMemoryEngine()
)

# ============================================================================
# SELF TEST
# ============================================================================

def semantic_memory_self_test():

    memory_a = (

        runtime_semantic_memory_engine
        .ingest_memory(

            memory_type=TYPE_SYMBOLIC,

            semantic_text=
                "runtime convergence "
                "hash72 attractor manifold"
        )
    )

    memory_b = (

        runtime_semantic_memory_engine
        .ingest_memory(

            memory_type=TYPE_MULTIMODAL,

            semantic_text=
                "multimodal replay "
                "prediction topology"
        )
    )

    runtime_semantic_memory_engine.link_memories(

        memory_a.memory_id,

        memory_b.memory_id,

        relationship="semantic"
    )

    results = (

        runtime_semantic_memory_engine
        .semantic_search(
            "runtime attractor"
        )
    )

    print()

    print("SEMANTIC MEMORY METRICS")

    print(
        runtime_semantic_memory_engine.metrics()
    )

    print()

    print("SEARCH RESULTS")

    print(results)

    print()

    print("MEMORY GRAPH")

    print(

        runtime_semantic_memory_engine
        .export_memory_graph()
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    semantic_memory_self_test()