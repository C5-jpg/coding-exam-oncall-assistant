"""Agent tools.

Per the exam spec the Agent has only ONE tool: `readFile(fname: string) -> str`.
- No directory listing
- No wildcards
- No path separators
- File must live directly in `data_dir`

We additionally expose `writeFile` as an internal helper because the spec says
"也可以往 data/ 目录添加任意文件" (the Agent may also add files), but we keep
the public LLM tool surface minimal: only `readFile` is exposed via the
OpenAI tool-calling schema.
"""
from __future__ import annotations

import re
from pathlib import Path

_SAFE_FNAME = re.compile(r"^[A-Za-z0-9_.\-\u4e00-\u9fff]+$")


class ToolError(ValueError):
    pass


class ReadFileTool:
    name = "readFile"
    description = (
        "Read the full content of a single SOP file from the data directory. "
        "Argument `fname` must be a plain file name like 'sop-001.html'. "
        "Path separators ('/', '\\\\'), wildcards ('*', '?') and parent traversal "
        "('..') are forbidden. The tool cannot list directories. Use this to "
        "fetch a SOP after deciding which one is relevant."
    )

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir.resolve()

    @property
    def openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fname": {
                            "type": "string",
                            "description": "Plain file name (e.g. 'sop-001.html'). No paths.",
                        }
                    },
                    "required": ["fname"],
                },
            },
        }

    def __call__(self, fname: str) -> str:
        if not isinstance(fname, str) or not fname.strip():
            raise ToolError("fname must be a non-empty string")
        fname = fname.strip()
        if any(sep in fname for sep in ("/", "\\")):
            raise ToolError("readFile rejects path separators")
        if any(ch in fname for ch in ("*", "?")):
            raise ToolError("readFile rejects wildcards")
        if ".." in fname:
            raise ToolError("readFile rejects parent traversal")
        if not _SAFE_FNAME.match(fname):
            raise ToolError("fname contains unsupported characters")
        target = (self.data_dir / fname).resolve()
        if target.parent != self.data_dir:
            raise ToolError("readFile is restricted to data/ directly")
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(fname)
        return target.read_text(encoding="utf-8", errors="replace")


class WriteFileHelper:
    """Internal helper. NOT exposed to the LLM. Used by /v1/documents."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir.resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def write(self, fname: str, content: str) -> Path:
        if not isinstance(fname, str) or not fname.strip():
            raise ToolError("fname must be a non-empty string")
        fname = fname.strip()
        if any(sep in fname for sep in ("/", "\\")) or ".." in fname or any(ch in fname for ch in ("*", "?")):
            raise ToolError("invalid fname")
        if not _SAFE_FNAME.match(fname):
            raise ToolError("fname contains unsupported characters")
        target = (self.data_dir / fname).resolve()
        if target.parent != self.data_dir:
            raise ToolError("write is restricted to data/")
        target.write_text(content, encoding="utf-8")
        return target
