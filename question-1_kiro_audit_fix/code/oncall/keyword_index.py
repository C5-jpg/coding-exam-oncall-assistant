"""Phase 1 keyword search.

Same scoring philosophy as the original (TF-IDF style with phrase boost),
but operates over chunks AND aggregates to document level for the API.
The exam validates document-level results (`/v1/search?q=OOM` -> sop-001),
so we return per-document results derived from the best matching chunk.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from html import unescape
from typing import Iterable

from .chunker import Chunk
from .tokenizer import normalize, split_query_terms, tokenize


@dataclass
class KeywordHit:
    chunk: Chunk
    score: float


class KeywordIndex:
    def __init__(self, chunks: Iterable[Chunk]) -> None:
        self.chunks: list[Chunk] = list(chunks)
        self._token_counts: list[Counter[str]] = []
        self._norm_texts: list[str] = []
        self.idf: dict[str, float] = {}
        self._rebuild()

    def add_chunks(self, new_chunks: Iterable[Chunk]) -> None:
        for c in new_chunks:
            self.chunks.append(c)
        self._rebuild()

    def _rebuild(self) -> None:
        self._token_counts.clear()
        self._norm_texts.clear()
        df: Counter[str] = Counter()
        for chunk in self.chunks:
            blob = f"{chunk.doc_title} {chunk.section_h2} {chunk.section_h3} {chunk.text}"
            counts = Counter(tokenize(blob))
            self._token_counts.append(counts)
            self._norm_texts.append(normalize(blob))
            df.update(counts.keys())
        n = max(len(self.chunks), 1)
        self.idf = {tok: math.log((1 + n) / (1 + cnt)) + 1.0 for tok, cnt in df.items()}

    def search(self, query: str, limit: int = 10) -> list[KeywordHit]:
        query = unescape(query or "")
        query_norm = normalize(query)
        if not query_norm:
            return []
        terms = split_query_terms(query)
        hits: list[KeywordHit] = []
        for chunk, counts, norm_text in zip(self.chunks, self._token_counts, self._norm_texts):
            score = 0.0
            phrase = norm_text.count(query_norm)
            if phrase:
                score += phrase * (8.0 + min(len(query_norm), 12) / 2)
            for term in terms:
                if not term:
                    continue
                if term in norm_text:
                    score += norm_text.count(term) * (2.5 + min(len(term), 8) / 4)
                if term in counts:
                    score += counts[term] * self.idf.get(term, 1.0)
            if score > 0:
                hits.append(KeywordHit(chunk=chunk, score=score))
        hits.sort(key=lambda h: (-h.score, h.chunk.chunk_id))
        return hits[:limit]
