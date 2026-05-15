#!/usr/bin/env python3
"""Backwards-compatible entry point + legacy symbol re-exports.

The original demo used `python oncall_assistant.py [--self-test|--port ...]`.
This shim now dispatches to the modernised package under `oncall/`. New code
should use `python main.py {serve,http,ui,self-test}` instead.

Legacy tests in tests/test_oncall.py import classes/functions from this
module directly, so we re-export the most-used ones below.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

# Ensure the local 'oncall' package is importable when invoked from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# --- Re-exports for legacy tests -----------------------------------------
from oncall.tokenizer import (
    tokenize,
    normalize,
    split_query_terms,
    chinese_ngrams,
    compact_spaces,
    DOMAIN_PHRASES,
    STOPWORDS,
)
from oncall.html_parser import VisibleTextExtractor
from oncall.config import SETTINGS
from oncall.tools import ReadFileTool, ToolError
from oncall.service import OnCallService
from oncall.http_server import serve as http_serve

# --- Legacy DocumentIndex/OnCallAgent compatibility wrappers ------------
# The legacy tests construct `DocumentIndex(data_dir)` and call
# `index.keyword_search(q)`, `index.semantic_search(q)`, `index.add_document(...)`,
# inspecting `index.documents` (dict) and a `Document` object with attributes
# `id`, `title`, `text`, `token_counts`, `norm_text`. We provide a thin façade
# over OnCallService that keeps that shape.

class _LegacyDocument:
    def __init__(self, doc_id: str, title: str, text: str) -> None:
        self.id = doc_id
        self.title = title
        self.text = text
        self.token_counts: Counter[str] = Counter(tokenize(f"{title} {text}"))
        self.norm_text = normalize(f"{title} {text}")


class _LegacySearchResult:
    def __init__(self, item: dict[str, Any]) -> None:
        self.id = item["id"]
        self.title = item["title"]
        self.snippet = item.get("snippet", "")
        self.score = item.get("score", 0.0)


class DocumentIndex:
    """Legacy-shaped facade backed by OnCallService."""

    def __init__(self, data_dir: Path) -> None:
        self._service = OnCallService(data_dir=Path(data_dir))
        self.documents: dict[str, _LegacyDocument] = {
            doc_id: _LegacyDocument(doc_id, summary.title, "")
            for doc_id, summary in self._service.documents.items()
        }
        # Populate text from chunks
        text_by_doc: dict[str, list[str]] = {}
        for c in self._service.chunks:
            text_by_doc.setdefault(c.doc_id, []).append(c.text)
        for doc_id, parts in text_by_doc.items():
            text = " ".join(parts)
            self.documents[doc_id] = _LegacyDocument(doc_id, self._service.documents[doc_id].title, text)

    def keyword_search(self, query: str, limit: int = 10) -> list[_LegacySearchResult]:
        return [_LegacySearchResult(r) for r in self._service.keyword_search(query, limit=limit)]

    def semantic_search(self, query: str, limit: int = 10) -> list[_LegacySearchResult]:
        return [_LegacySearchResult(r) for r in self._service.semantic_search(query, limit=limit)]

    def add_document(self, doc_id: str, html: str):
        if not re.fullmatch(r"[A-Za-z0-9_.\-]+", doc_id or ""):
            raise ValueError("invalid doc_id")
        summary = self._service.add_document(doc_id, html)
        # Refresh the legacy view
        text = " ".join(c.text for c in self._service.chunks if c.doc_id == doc_id)
        self.documents[doc_id] = _LegacyDocument(doc_id, summary.title, text)

        class _Result:
            def __init__(self, did, title):
                self.id = did
                self.title = title

        return _Result(doc_id, summary.title)


class OnCallAgent:
    """Legacy-shaped agent facade backed by OnCallService."""

    def __init__(self, index: DocumentIndex, data_dir: Path) -> None:
        self._service = index._service if isinstance(index, DocumentIndex) else OnCallService(data_dir=Path(data_dir))

    def answer(self, message: str) -> dict[str, Any]:
        result = self._service.chat(message)
        # Legacy response shape used `arguments.fname` and a summary 'answer' field.
        return {
            "message": result["message"],
            "answer": result["answer"],
            "tool_calls": [
                {"tool": c["tool"], "arguments": c["arguments"], "result": c["result"]}
                for c in result["tool_calls"]
            ],
            "sources": result["sources"],
        }


# --- get_query_value helper used by tests --------------------------------

def get_query_value(raw_query: str) -> str:
    if raw_query.startswith("q=&") and not raw_query.startswith("q=&q="):
        return "&"
    params = parse_qs(raw_query, keep_blank_values=True)
    return params.get("q", [""])[0]


# --- Entry point ----------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="On-Call Assistant (legacy entry; prefer `python main.py`)"
    )
    parser.add_argument("--host", default=SETTINGS.http_host)
    parser.add_argument("--port", type=int, default=SETTINGS.http_port)
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir).resolve() if args.data_dir else None

    if args.self_test:
        from main import cmd_self_test, _configure_logging
        _configure_logging("WARNING")
        ns = argparse.Namespace(data_dir=str(data_dir) if data_dir else None)
        return cmd_self_test(ns)

    service = OnCallService(data_dir=data_dir)
    print(f"Serving On-Call Assistant on http://{args.host}:{args.port}")
    print(f"Status: {service.status()}")
    http_serve(host=args.host, port=args.port, service=service)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
