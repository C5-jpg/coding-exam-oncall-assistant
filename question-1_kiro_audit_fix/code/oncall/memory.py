"""Conversation memory for the Agent.

Two layers:
1. Session message history (short-term): list of OpenAI-format messages,
   trimmed to N most recent turns.
2. Session facts (mid-term): compact bullet notes the Agent extracts after
   each turn (e.g. "user is debugging sop-002 main-replica lag"). These are
   prepended to the system prompt so context survives summarization.

Sessions are isolated by session_id so a real deployment can support multiple
on-call engineers concurrently.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Turn:
    role: str
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_call_id: str = ""
    name: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class Session:
    session_id: str
    turns: list[Turn] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_messages(self, include_tool_traffic: bool = True) -> list[dict[str, Any]]:
        """Render to OpenAI-format messages."""
        out: list[dict[str, Any]] = []
        for t in self.turns:
            msg: dict[str, Any] = {"role": t.role, "content": t.content}
            if t.role == "assistant" and t.tool_calls and include_tool_traffic:
                msg["tool_calls"] = t.tool_calls
            if t.role == "tool":
                msg["tool_call_id"] = t.tool_call_id
                if t.name:
                    msg["name"] = t.name
            out.append(msg)
        return out


class MemoryStore:
    def __init__(self, persist_dir: Path | None = None, max_turns: int = 24) -> None:
        self.persist_dir = persist_dir.resolve() if persist_dir else None
        if self.persist_dir:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.max_turns = max_turns
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> Session:
        with self._lock:
            sess = self._sessions.get(session_id)
            if sess is None:
                sess = self._load(session_id) or Session(session_id=session_id)
                self._sessions[session_id] = sess
            return sess

    def append_turn(self, session_id: str, turn: Turn) -> None:
        with self._lock:
            sess = self._sessions.setdefault(session_id, Session(session_id=session_id))
            sess.turns.append(turn)
            # Trim oldest, but always preserve at least the very first user turn for context.
            if len(sess.turns) > self.max_turns:
                # Keep first 1 + last (max_turns - 1)
                head = sess.turns[:1]
                tail = sess.turns[-(self.max_turns - 1):]
                sess.turns = head + tail
            sess.updated_at = time.time()
            self._save(sess)

    def add_fact(self, session_id: str, fact: str) -> None:
        if not fact.strip():
            return
        with self._lock:
            sess = self._sessions.setdefault(session_id, Session(session_id=session_id))
            if fact not in sess.facts:
                sess.facts.append(fact)
            sess.facts = sess.facts[-12:]  # cap
            sess.updated_at = time.time()
            self._save(sess)

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
            if self.persist_dir:
                f = self.persist_dir / f"{session_id}.json"
                if f.exists():
                    f.unlink()

    def list_sessions(self) -> list[Session]:
        with self._lock:
            return list(self._sessions.values())

    # --- persistence ---
    def _save(self, sess: Session) -> None:
        if not self.persist_dir:
            return
        f = self.persist_dir / f"{sess.session_id}.json"
        try:
            payload = {
                "session_id": sess.session_id,
                "facts": sess.facts,
                "created_at": sess.created_at,
                "updated_at": sess.updated_at,
                "turns": [
                    {
                        "role": t.role,
                        "content": t.content,
                        "tool_calls": t.tool_calls,
                        "tool_call_id": t.tool_call_id,
                        "name": t.name,
                        "timestamp": t.timestamp,
                    }
                    for t in sess.turns
                ],
            }
            f.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:  # pragma: no cover
            pass

    def _load(self, session_id: str) -> Session | None:
        if not self.persist_dir:
            return None
        f = self.persist_dir / f"{session_id}.json"
        if not f.exists():
            return None
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            return Session(
                session_id=data["session_id"],
                facts=list(data.get("facts", [])),
                created_at=float(data.get("created_at", time.time())),
                updated_at=float(data.get("updated_at", time.time())),
                turns=[
                    Turn(
                        role=t["role"],
                        content=t.get("content", "") or "",
                        tool_calls=t.get("tool_calls", []),
                        tool_call_id=t.get("tool_call_id", ""),
                        name=t.get("name", ""),
                        timestamp=float(t.get("timestamp", time.time())),
                    )
                    for t in data.get("turns", [])
                ],
            )
        except Exception:  # pragma: no cover
            return None
