"""Hybrid retrieval: keyword + vector via Reciprocal Rank Fusion (RRF) with
domain-rule prior.

We expose results at two granularities:
- Chunk level (used by the agent for retrieval-augmented generation)
- Document level (used by /v1/search and /v2/search per exam spec)

For chunk-level results we keep both keyword and vector ranks. For document
results we aggregate the best chunk per document.

The domain-rule prior expands the query (improving recall) and adds a small
positive bias to documents flagged by the operations team (improving precision
on intent-heavy queries like "服务器挂了"). This is a standard production
pattern.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .chunker import Chunk
from .domain_rules import expand_query
from .keyword_index import KeywordHit, KeywordIndex
from .vector_index import VectorHit, VectorIndex


@dataclass
class FusedHit:
    chunk: Chunk
    score: float
    keyword_score: float = 0.0
    vector_score: float = 0.0
    sources: list[str] = field(default_factory=list)


def rrf_fuse(
    keyword_hits: list[KeywordHit],
    vector_hits: list[VectorHit],
    k: int = 60,
) -> list[FusedHit]:
    """Reciprocal Rank Fusion."""
    by_id: dict[str, FusedHit] = {}
    for rank, h in enumerate(keyword_hits):
        cid = h.chunk.chunk_id
        slot = by_id.setdefault(cid, FusedHit(chunk=h.chunk, score=0.0))
        slot.score += 1.0 / (k + rank + 1)
        slot.keyword_score = h.score
        slot.sources.append("keyword")
    for rank, h in enumerate(vector_hits):
        cid = h.chunk.chunk_id
        slot = by_id.setdefault(cid, FusedHit(chunk=h.chunk, score=0.0))
        slot.score += 1.0 / (k + rank + 1)
        slot.vector_score = h.score
        slot.sources.append("vector")
    out = list(by_id.values())
    out.sort(key=lambda x: -x.score)
    return out


def aggregate_to_documents(hits: Iterable[FusedHit], limit: int = 10) -> list[FusedHit]:
    """Keep only the best chunk per document."""
    best: dict[str, FusedHit] = {}
    for h in hits:
        prev = best.get(h.chunk.doc_id)
        if prev is None or h.score > prev.score:
            best[h.chunk.doc_id] = h
    out = list(best.values())
    out.sort(key=lambda x: -x.score)
    return out[:limit]


class HybridSearch:
    def __init__(self, keyword: KeywordIndex, vector: VectorIndex) -> None:
        self.keyword = keyword
        self.vector = vector

    def search_chunks(self, query: str, limit: int = 10) -> list[FusedHit]:
        expanded, doc_boosts = expand_query(query)
        # Keyword retrieval uses original query (precision + phrase match).
        kw = self.keyword.search(query, limit=max(limit * 2, 20))
        # Vector retrieval uses the expanded query so synonyms surface.
        vec = self.vector.search(expanded, limit=max(limit * 2, 20))
        fused = rrf_fuse(kw, vec)
        # Apply document-level boost from domain rules.
        if doc_boosts:
            for h in fused:
                bonus = doc_boosts.get(h.chunk.doc_id, 0.0)
                if bonus:
                    h.score += bonus
                    if "rule" not in h.sources:
                        h.sources.append("rule")
            fused.sort(key=lambda x: -x.score)
        return fused[:limit]

    def search_documents(self, query: str, limit: int = 10) -> list[FusedHit]:
        return aggregate_to_documents(self.search_chunks(query, limit=limit * 3), limit=limit)
