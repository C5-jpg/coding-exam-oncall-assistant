"""SOP chunking.

Strategy:
1. Use h2/h3 boundaries as natural section breaks (parsed by html_parser).
2. Combine paragraphs under the same (h2, h3) until reaching `target_chars`.
3. Maintain metadata: doc_id, doc_title, h2 (chapter), h3 (scenario).

Each chunk becomes one embedding row. This is the recommended granularity for
SOPs because the original documents are already organised by scenario.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .html_parser import parse_html
from .tokenizer import compact_spaces


@dataclass
class Chunk:
    chunk_id: str          # e.g. "sop-001#02"
    doc_id: str            # e.g. "sop-001"
    doc_title: str         # e.g. "后端服务 On-Call SOP"
    section_h2: str        # e.g. "三、常见故障处理"
    section_h3: str        # e.g. "场景二：单服务OOM崩溃"
    text: str              # combined paragraph text under this section

    @property
    def display_path(self) -> str:
        parts = [self.doc_title]
        if self.section_h2:
            parts.append(self.section_h2)
        if self.section_h3:
            parts.append(self.section_h3)
        return " / ".join(p for p in parts if p)


def chunk_html(doc_id: str, html: str, target_chars: int = 600) -> tuple[str, str, list[Chunk]]:
    """Return (title, full_text, chunks) for one HTML document."""
    title, full_text, records = parse_html(html)

    # Group paragraphs by (h2, h3)
    grouped: dict[tuple[str, str], list[str]] = {}
    order: list[tuple[str, str]] = []
    for h2, h3, para in records:
        key = (h2, h3)
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(para)

    chunks: list[Chunk] = []
    seq = 0

    def emit(h2: str, h3: str, text: str) -> None:
        nonlocal seq
        seq += 1
        chunks.append(
            Chunk(
                chunk_id=f"{doc_id}#{seq:02d}",
                doc_id=doc_id,
                doc_title=title or doc_id,
                section_h2=h2,
                section_h3=h3,
                text=text,
            )
        )

    for h2, h3 in order:
        paras = grouped[(h2, h3)]
        # Pack paragraphs into chunks ~target_chars
        buf: list[str] = []
        buf_len = 0
        for p in paras:
            p = compact_spaces(p)
            if not p:
                continue
            if buf and buf_len + len(p) > target_chars:
                emit(h2, h3, " ".join(buf))
                buf = [p]
                buf_len = len(p)
            else:
                buf.append(p)
                buf_len += len(p) + 1
        if buf:
            emit(h2, h3, " ".join(buf))

    # If no chunks produced (e.g. malformed HTML), fall back to whole-document chunk
    if not chunks and full_text:
        emit("", "", full_text[:2000])

    return title or doc_id, full_text, chunks
