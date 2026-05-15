"""Top-level service object wiring all components together."""
from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .agent import OnCallAgent
from .chunker import Chunk, chunk_html
from .config import SETTINGS
from .embedding import EmbeddingClient
from .hybrid_search import FusedHit, HybridSearch
from .keyword_index import KeywordIndex
from .llm import LLMClient
from .memory import MemoryStore
from .tools import ReadFileTool, WriteFileHelper
from .vector_index import VectorIndex

log = logging.getLogger("oncall.service")


@dataclass
class DocSummary:
    doc_id: str
    title: str
    filename: str


class OnCallService:
    """Holds indices, tools, and agent. Thread-safe for HTTP/Gradio concurrent use."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = (data_dir or SETTINGS.data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()

        # Tools
        self.read_tool = ReadFileTool(self.data_dir)
        self.write_helper = WriteFileHelper(self.data_dir)

        # Embedding + indices
        self.embedder = EmbeddingClient()
        self.documents: dict[str, DocSummary] = {}
        self.chunks: list[Chunk] = []
        self.keyword_index = KeywordIndex([])
        self.vector_index = VectorIndex(self.embedder)

        # Memory + LLM
        memory_dir = SETTINGS.cache_dir / "sessions"
        self.memory = MemoryStore(persist_dir=memory_dir)
        self.llm = LLMClient()

        # Bootstrap by indexing data dir
        self._bootstrap()

        self.search = HybridSearch(self.keyword_index, self.vector_index)
        self.agent = OnCallAgent(
            search=self.search,
            read_tool=self.read_tool,
            memory=self.memory,
            llm=self.llm,
        )

    # ------------------------------------------------------------------ status
    def status(self) -> dict[str, object]:
        return {
            "documents": len(self.documents),
            "chunks": len(self.chunks),
            "embedding_api": self.embedder.has_api(),
            "embedding_using_fallback": self.embedder.using_fallback,
            "embedding_model": self.embedder.model,
            "embedding_dim": self.embedder.dim,
            "llm_api": self.llm.has_api(),
            "llm_model": self.llm.model,
            "data_dir": str(self.data_dir),
        }

    # ----------------------------------------------------------------- indexing
    def _bootstrap(self) -> None:
        files = sorted(self.data_dir.glob("*.html"))
        all_chunks: list[Chunk] = []
        for path in files:
            doc_id = path.stem.lower()
            html = path.read_text(encoding="utf-8", errors="replace")
            title, _, doc_chunks = chunk_html(doc_id, html)
            self.documents[doc_id] = DocSummary(doc_id=doc_id, title=title, filename=path.name)
            all_chunks.extend(doc_chunks)
        self.chunks = all_chunks
        self.keyword_index = KeywordIndex(all_chunks)
        log.info("Embedding %d chunks from %d documents…", len(all_chunks), len(self.documents))
        self.vector_index.build(all_chunks)

    def add_document(self, doc_id: str, html: str) -> DocSummary:
        if not re.fullmatch(r"[A-Za-z0-9_.\-]+", doc_id or ""):
            raise ValueError("doc_id must contain only letters, digits, '.', '-', '_'")
        with self._lock:
            target = self.write_helper.write(f"{doc_id}.html", html)
            title, _, doc_chunks = chunk_html(doc_id, html)
            self.documents[doc_id] = DocSummary(doc_id=doc_id, title=title, filename=target.name)
            # Remove old chunks for this doc, if any.
            self.chunks = [c for c in self.chunks if c.doc_id != doc_id] + doc_chunks
            # Rebuild keyword index (cheap), incrementally update vector index.
            self.keyword_index = KeywordIndex(self.chunks)
            # Rebuild vector index from scratch is simplest and still fast (<100 docs).
            self.vector_index.build(self.chunks)
            self.search = HybridSearch(self.keyword_index, self.vector_index)
            self.agent.search = self.search
            return self.documents[doc_id]

    # ------------------------------------------------------------------ search
    def keyword_search(self, query: str, limit: int = 10) -> list[dict[str, object]]:
        hits = self.keyword_index.search(query, limit=limit * 3)
        # Aggregate to document level.
        best: dict[str, tuple[float, Chunk]] = {}
        for h in hits:
            cur = best.get(h.chunk.doc_id)
            if cur is None or h.score > cur[0]:
                best[h.chunk.doc_id] = (h.score, h.chunk)
        rows = sorted(best.items(), key=lambda kv: -kv[1][0])[:limit]
        out = []
        for doc_id, (score, chunk) in rows:
            doc = self.documents.get(doc_id)
            out.append(
                {
                    "id": doc_id,
                    "title": doc.title if doc else doc_id,
                    "snippet": _make_snippet(chunk.text, query),
                    "score": round(score, 4),
                }
            )
        return out

    def semantic_search(self, query: str, limit: int = 10) -> list[dict[str, object]]:
        hits = self.search.search_documents(query, limit=limit)
        out = []
        for h in hits:
            doc = self.documents.get(h.chunk.doc_id)
            out.append(
                {
                    "id": h.chunk.doc_id,
                    "title": doc.title if doc else h.chunk.doc_id,
                    "snippet": _make_snippet(h.chunk.text, query),
                    "score": round(h.score, 4),
                    "section": h.chunk.display_path,
                    "keyword_score": round(h.keyword_score, 4),
                    "vector_score": round(h.vector_score, 4),
                }
            )
        return out

    # ------------------------------------------------------------------ agent
    def chat(self, message: str, session_id: str | None = None) -> dict[str, object]:
        return self.agent.chat(message, session_id=session_id).to_dict()

    def reset_session(self, session_id: str) -> None:
        self.agent.reset(session_id)


def _make_snippet(text: str, query: str, radius: int = 90) -> str:
    text = text or ""
    if not text:
        return ""
    q = (query or "").strip().lower()
    if not q:
        return text[: radius * 2]
    norm = text.lower()
    pos = norm.find(q)
    if pos < 0:
        # try first token
        tok = q.split()[0] if q else ""
        if tok:
            pos = norm.find(tok)
    if pos < 0:
        return text[: radius * 2]
    start = max(0, pos - radius)
    end = min(len(text), pos + len(q) + radius)
    snippet = text[start:end]
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet
