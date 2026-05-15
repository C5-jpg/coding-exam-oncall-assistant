"""HTML to visible-text extraction.

Critical requirement from the exam: words appearing only inside <script> /
<style> tags must NOT be indexed (e.g. `replicationLag`).
"""
from __future__ import annotations

from html.parser import HTMLParser
from .tokenizer import compact_spaces


class VisibleTextExtractor(HTMLParser):
    """Extract <title> and visible <body> text. Skip script/style/etc."""

    _IGNORED_TAGS = {"script", "style", "noscript", "template", "svg", "canvas"}
    _BLOCK_TAGS = {"p", "br", "li", "tr", "h1", "h2", "h3", "h4", "section", "article"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self._in_title = False
        self._in_body = False
        self._title_parts: list[str] = []
        self._body_parts: list[str] = []
        # Track current heading hierarchy for chunker
        self._current_h2: str = ""
        self._current_h3: str = ""
        self._capturing_heading: str | None = None
        self._heading_buf: list[str] = []
        # Records of (h2, h3, paragraph_text) for chunker
        self.records: list[tuple[str, str, str]] = []
        self._para_buf: list[str] = []

    def _flush_paragraph(self) -> None:
        text = compact_spaces(" ".join(self._para_buf))
        self._para_buf.clear()
        if text:
            self.records.append((self._current_h2, self._current_h3, text))

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self._IGNORED_TAGS:
            self._ignored_depth += 1
            return
        if tag == "title":
            self._in_title = True
        elif tag == "body":
            self._in_body = True
        elif tag in {"h2", "h3"} and self._in_body:
            self._flush_paragraph()
            self._capturing_heading = tag
            self._heading_buf = []
        elif self._in_body and tag in self._BLOCK_TAGS:
            self._flush_paragraph()
            self._body_parts.append(" ")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self._IGNORED_TAGS and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        elif tag == "body":
            self._flush_paragraph()
            self._in_body = False
        elif tag in {"h2", "h3"} and self._capturing_heading == tag:
            heading = compact_spaces(" ".join(self._heading_buf))
            if tag == "h2":
                self._current_h2 = heading
                self._current_h3 = ""
            else:
                self._current_h3 = heading
            self._capturing_heading = None
            self._heading_buf = []
        elif self._in_body and tag in self._BLOCK_TAGS:
            self._flush_paragraph()
            self._body_parts.append(" ")

    def handle_data(self, data):
        if self._ignored_depth:
            return
        text = compact_spaces(data)
        if not text:
            return
        if self._in_title:
            self._title_parts.append(text)
        if self._capturing_heading:
            self._heading_buf.append(text)
        if self._in_body:
            self._body_parts.append(text)
            if self._capturing_heading is None:
                self._para_buf.append(text)

    @property
    def title(self) -> str:
        return compact_spaces(" ".join(self._title_parts))

    @property
    def text(self) -> str:
        return compact_spaces(" ".join(self._body_parts))


def parse_html(html: str) -> tuple[str, str, list[tuple[str, str, str]]]:
    """Return (title, full_visible_text, [(h2, h3, paragraph), ...])."""
    parser = VisibleTextExtractor()
    parser.feed(html)
    return parser.title, parser.text, parser.records
