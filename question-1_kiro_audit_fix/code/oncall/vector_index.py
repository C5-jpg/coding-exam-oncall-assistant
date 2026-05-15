"""Phase 2 dense vector index using Qwen3-Embedding-8B.

In-memory matrix (numpy). For 100 docs with ~5 chunks each = 500 vectors of
1024 dim ~ 2MB. Plenty fast for cosine search without a real vector DB.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .chunker import Chunk
from .embedding import EmbeddingClient


@dataclass
class VectorHit:
    chunk: Chunk
    score: float          # cosine similarity in [-1, 1]


class VectorIndex:
    def __init__(self, embedder: EmbeddingClient) -> None:
        self.embedder = embedder
        self.chunks: list[Chunk] = []
        self._matrix: np.ndarray | None = None     # (n, dim) L2-normalised

    @property
    def size(self) -> int:
        return len(self.chunks)

    def build(self, chunks: Iterable[Chunk]) -> None:
        self.chunks = list(chunks)
        if not self.chunks:
            self._matrix = None
            return
        # Embed using "title -> section -> text" formatted strings to give the
        # encoder context about what the snippet is about.
        texts = [self._encode_text(c) for c in self.chunks]
        vectors = self.embedder.embed_many(texts)
        mat = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._matrix = mat / norms

    def add_chunks(self, new_chunks: Iterable[Chunk]) -> None:
        new_list = list(new_chunks)
        if not new_list:
            return
        new_texts = [self._encode_text(c) for c in new_list]
        new_vecs = np.asarray(self.embedder.embed_many(new_texts), dtype=np.float32)
        new_norms = np.linalg.norm(new_vecs, axis=1, keepdims=True)
        new_norms[new_norms == 0] = 1.0
        new_vecs = new_vecs / new_norms
        if self._matrix is None:
            self._matrix = new_vecs
        else:
            self._matrix = np.vstack([self._matrix, new_vecs])
        self.chunks.extend(new_list)

    def search(self, query: str, limit: int = 10) -> list[VectorHit]:
        if not query.strip() or self._matrix is None or self._matrix.shape[0] == 0:
            return []
        q_vec = np.asarray(self.embedder.embed(query), dtype=np.float32)
        q_norm = float(np.linalg.norm(q_vec))
        if q_norm == 0:
            return []
        q_vec = q_vec / q_norm
        scores = self._matrix @ q_vec               # cosine similarity
        order = np.argsort(-scores)[:limit]
        return [VectorHit(chunk=self.chunks[i], score=float(scores[i])) for i in order]

    @staticmethod
    def _encode_text(chunk: Chunk) -> str:
        prefix_parts = [chunk.doc_title]
        if chunk.section_h2:
            prefix_parts.append(chunk.section_h2)
        if chunk.section_h3:
            prefix_parts.append(chunk.section_h3)
        prefix = " > ".join(prefix_parts)
        return f"{prefix}\n{chunk.text}"
