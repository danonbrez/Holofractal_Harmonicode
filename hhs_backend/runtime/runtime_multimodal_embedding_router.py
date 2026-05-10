# ============================================================================
# hhs_backend/runtime/runtime_multimodal_embedding_router.py
# HARMONICODE / HHS
# MULTIMODAL EMBEDDING ROUTER
#
# PURPOSE
# -------
# Canonical multimodal semantic transport layer for:
#
#   - cross-modal embeddings
#   - replay-aware semantic routing
#   - multimodal replay projection
#   - vector transport synchronization
#   - symbolic tensor embeddings
#   - modality-aware attractor routing
#   - distributed semantic replication
#   - adaptive multimodal retrieval
#
# Multimodal routing MUST remain replay-safe and append-only.
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
from typing import Dict, List, Optional, Any

from hhs_backend.runtime.runtime_semantic_memory_engine import (
    runtime_semantic_memory_engine,

    TYPE_MULTIMODAL,

    TYPE_SYMBOLIC
)

from hhs_backend.runtime.runtime_prediction_engine import (
    runtime_prediction_engine
)

from hhs_backend.runtime.runtime_replay_engine import (
    runtime_replay_engine
)

from hhs_storage.runtime_state_store_v1 import (
    runtime_state_store
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_MULTIMODAL_ROUTER"
)

# ============================================================================
# MODALITIES
# ============================================================================

MODALITY_TEXT = "text"

MODALITY_IMAGE = "image"

MODALITY_AUDIO = "audio"

MODALITY_VIDEO = "video"

MODALITY_SYMBOLIC = "symbolic"

MODALITY_REPLAY = "replay"

# ============================================================================
# EMBEDDING
# ============================================================================

@dataclass
class HHSMultimodalEmbedding:

    embedding_id: str

    created_at: float

    modality: str

    hash72: str

    vector: List[float]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# PROJECTION
# ============================================================================

@dataclass
class HHSMultimodalProjection:

    projection_id: str

    created_at: float

    source_modality: str

    target_modality: str

    source_hash72: str

    target_hash72: str

    similarity: float

# ============================================================================
# ATTRACTOR ROUTE
# ============================================================================

@dataclass
class HHSMultimodalAttractorRoute:

    route_id: str

    created_at: float

    attractor_hash72: str

    modality: str

    stability: float

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# ROUTER
# ============================================================================

class HHSRuntimeMultimodalEmbeddingRouter:

    """
    Canonical multimodal semantic transport layer.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.embeddings: Dict[
            str,
            HHSMultimodalEmbedding
        ] = {}

        self.projections: Dict[
            str,
            HHSMultimodalProjection
        ] = {}

        self.attractor_routes: Dict[
            str,
            HHSMultimodalAttractorRoute
        ] = {}

        self.total_embeddings = 0

        self.total_projections = 0

        self.total_routes = 0

    # =====================================================================
    # EMBEDDINGS
    # =====================================================================

    def generate_embedding(

        self,

        payload: str,

        dimensions: int = 72
    ) -> List[float]:

        digest = hashlib.sha256(

            payload.encode("utf-8")

        ).digest()

        vector = []

        for i in range(dimensions):

            byte = digest[
                i % len(digest)
            ]

            value = (
                (byte / 255.0) * 2.0
            ) - 1.0

            vector.append(value)

        return vector

    # =====================================================================
    # REGISTER
    # =====================================================================

    def register_embedding(

        self,

        modality: str,

        payload: str,

        hash72: Optional[str] = None,

        metadata: Optional[Dict] = None
    ) -> HHSMultimodalEmbedding:

        with self.lock:

            if hash72 is None:

                hash72 = hashlib.sha256(

                    payload.encode("utf-8")

                ).hexdigest()[:72]

            vector = self.generate_embedding(
                payload
            )

            embedding = HHSMultimodalEmbedding(

                embedding_id=str(uuid.uuid4()),

                created_at=time.time(),

                modality=modality,

                hash72=hash72,

                vector=vector,

                metadata=metadata or {}
            )

            self.embeddings[
                embedding.embedding_id
            ] = embedding

            runtime_state_store.store_vector_record(

                hash72=hash72,

                vector=vector
            )

            runtime_semantic_memory_engine.ingest_memory(

                memory_type=TYPE_MULTIMODAL,

                semantic_text=payload,

                hash72=hash72,

                metadata={

                    "modality":
                        modality
                }
            )

            self.total_embeddings += 1

            logger.info(
                f"Embedding registered: "
                f"{embedding.embedding_id}"
            )

            return embedding

    # =====================================================================
    # SIMILARITY
    # =====================================================================

    def cosine_similarity(

        self,

        a: List[float],

        b: List[float]
    ) -> float:

        dot = sum(x * y for x, y in zip(a, b))

        norm_a = math.sqrt(
            sum(x * x for x in a)
        )

        norm_b = math.sqrt(
            sum(y * y for y in b)
        )

        if norm_a == 0.0:
            return 0.0

        if norm_b == 0.0:
            return 0.0

        return dot / (norm_a * norm_b)

    # =====================================================================
    # PROJECTIONS
    # =====================================================================

    def create_projection(

        self,

        source_embedding_id: str,

        target_embedding_id: str
    ) -> HHSMultimodalProjection:

        with self.lock:

            source = self.embeddings[
                source_embedding_id
            ]

            target = self.embeddings[
                target_embedding_id
            ]

            similarity = self.cosine_similarity(

                source.vector,

                target.vector
            )

            projection = HHSMultimodalProjection(

                projection_id=str(uuid.uuid4()),

                created_at=time.time(),

                source_modality=
                    source.modality,

                target_modality=
                    target.modality,

                source_hash72=
                    source.hash72,

                target_hash72=
                    target.hash72,

                similarity=similarity
            )

            self.projections[
                projection.projection_id
            ] = projection

            self.total_projections += 1

            logger.info(
                f"Projection created: "
                f"{projection.projection_id}"
            )

            return projection

    # =====================================================================
    # MODALITY PROJECTIONS
    # =====================================================================

    def project_text_to_image(
        self,
        text_payload: str
    ):

        text_embedding = self.register_embedding(

            modality=MODALITY_TEXT,

            payload=text_payload
        )

        image_embedding = self.register_embedding(

            modality=MODALITY_IMAGE,

            payload=
                f"IMAGE::{text_payload}"
        )

        projection = self.create_projection(

            text_embedding.embedding_id,

            image_embedding.embedding_id
        )

        return {

            "source":
                text_embedding,

            "target":
                image_embedding,

            "projection":
                projection
        }

    # ---------------------------------------------------------------------

    def project_audio_to_symbolic(
        self,
        audio_payload: str
    ):

        audio_embedding = self.register_embedding(

            modality=MODALITY_AUDIO,

            payload=audio_payload
        )

        symbolic_embedding = self.register_embedding(

            modality=MODALITY_SYMBOLIC,

            payload=
                f"SYMBOLIC::{audio_payload}"
        )

        projection = self.create_projection(

            audio_embedding.embedding_id,

            symbolic_embedding.embedding_id
        )

        return {

            "source":
                audio_embedding,

            "target":
                symbolic_embedding,

            "projection":
                projection
        }

    # ---------------------------------------------------------------------

    def project_replay_to_multimodal(
        self,
        horizon: int = 5
    ):

        replay = (

            runtime_replay_engine
            .predictive_replay(
                horizon=horizon
            )
        )

        runtime_replay_engine.verify_replay_equivalence(
            replay
        )

        projections = []

        for frame in replay.frames:

            runtime = frame.runtime_packet.get(
                "runtime",
                {}
            )

            payload = json.dumps(
                runtime,
                sort_keys=True
            )

            replay_embedding = (
                self.register_embedding(

                    modality=MODALITY_REPLAY,

                    payload=payload,

                    hash72=runtime.get(
                        "state_hash72",
                        ""
                    )
                )
            )

            symbolic_embedding = (
                self.register_embedding(

                    modality=MODALITY_SYMBOLIC,

                    payload=
                        f"REPLAY::{payload}"
                )
            )

            projection = self.create_projection(

                replay_embedding.embedding_id,

                symbolic_embedding.embedding_id
            )

            projections.append(projection)

        return projections

    # =====================================================================
    # ATTRACTOR ROUTING
    # =====================================================================

    def route_multimodal_attractor(
        self,
        modality: str
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

        routes = []

        for attractor in attractors:

            route = HHSMultimodalAttractorRoute(

                route_id=str(uuid.uuid4()),

                created_at=time.time(),

                attractor_hash72=
                    attractor.dominant_hash72,

                modality=modality,

                stability=attractor.stability,

                metadata={

                    "frequency":
                        attractor.frequency
                }
            )

            self.attractor_routes[
                route.route_id
            ] = route

            self.total_routes += 1

            routes.append(route)

        logger.info(
            f"Attractor routing complete "
            f"for modality={modality}"
        )

        return routes

    # =====================================================================
    # DISTRIBUTED REPLICATION
    # =====================================================================

    def replicate_embedding_state(self):

        records = []

        for embedding in self.embeddings.values():

            runtime_state_store.store_vector_record(

                hash72=embedding.hash72,

                vector=embedding.vector
            )

            records.append({

                "embedding_id":
                    embedding.embedding_id,

                "hash72":
                    embedding.hash72,

                "modality":
                    embedding.modality
            })

        logger.info(
            "Embedding replication complete"
        )

        return records

    # =====================================================================
    # SEMANTIC ROUTING
    # =====================================================================

    def semantic_multimodal_search(
        self,
        query: str,
        limit: int = 10
    ):

        query_embedding = self.generate_embedding(
            query
        )

        results = []

        for embedding in self.embeddings.values():

            similarity = self.cosine_similarity(

                query_embedding,

                embedding.vector
            )

            results.append({

                "embedding_id":
                    embedding.embedding_id,

                "modality":
                    embedding.modality,

                "hash72":
                    embedding.hash72,

                "similarity":
                    similarity
            })

        results.sort(

            key=lambda x: x["similarity"],

            reverse=True
        )

        return results[:limit]

    # =====================================================================
    # GRAPH EXPORT
    # =====================================================================

    def export_multimodal_graph(self):

        return {

            "embeddings": [

                {

                    "embedding_id":
                        embedding.embedding_id,

                    "modality":
                        embedding.modality,

                    "hash72":
                        embedding.hash72

                }

                for embedding in self.embeddings.values()
            ],

            "projections": [

                {

                    "projection_id":
                        projection.projection_id,

                    "source_modality":
                        projection.source_modality,

                    "target_modality":
                        projection.target_modality,

                    "similarity":
                        projection.similarity

                }

                for projection in self.projections.values()
            ],

            "routes": [

                {

                    "route_id":
                        route.route_id,

                    "modality":
                        route.modality,

                    "stability":
                        route.stability

                }

                for route in self.attractor_routes.values()
            ]
        }

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        similarities = [

            projection.similarity

            for projection in self.projections.values()
        ]

        avg_similarity = 0.0

        if similarities:

            avg_similarity = statistics.mean(
                similarities
            )

        return {

            "embeddings":
                self.total_embeddings,

            "projections":
                self.total_projections,

            "routes":
                self.total_routes,

            "average_similarity":
                avg_similarity
        }

# ============================================================================
# GLOBAL ROUTER
# ============================================================================

runtime_multimodal_embedding_router = (
    HHSRuntimeMultimodalEmbeddingRouter()
)

# ============================================================================
# SELF TEST
# ============================================================================

def multimodal_router_self_test():

    text_projection = (

        runtime_multimodal_embedding_router
        .project_text_to_image(

            "runtime replay "
            "semantic attractor"
        )
    )

    audio_projection = (

        runtime_multimodal_embedding_router
        .project_audio_to_symbolic(

            "harmonic replay topology"
        )
    )

    replay_projection = (

        runtime_multimodal_embedding_router
        .project_replay_to_multimodal(
            horizon=3
        )
    )

    routes = (

        runtime_multimodal_embedding_router
        .route_multimodal_attractor(
            modality=MODALITY_IMAGE
        )
    )

    print()

    print("MULTIMODAL METRICS")

    print(

        runtime_multimodal_embedding_router
        .metrics()
    )

    print()

    print("GRAPH")

    print(

        runtime_multimodal_embedding_router
        .export_multimodal_graph()
    )

    print()

    print("SEARCH")

    print(

        runtime_multimodal_embedding_router
        .semantic_multimodal_search(
            "runtime attractor"
        )
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    multimodal_router_self_test()