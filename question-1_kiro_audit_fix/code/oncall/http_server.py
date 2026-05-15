"""HTTP API server for /v1, /v2, /v3.

Conforms to the exam contract while delegating to the modern OnCallService
(hybrid search + LLM agent + memory).
"""
from __future__ import annotations

import json
import logging
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
from typing import Any
from urllib.parse import parse_qs, urlparse

from .config import SETTINGS
from .service import OnCallService

log = logging.getLogger("oncall.http")

MAX_BODY_BYTES = 8 * 1024 * 1024


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def _query_value(raw_query: str, key: str = "q") -> str:
    """Robust parse of `?q=...` while supporting bare-`&` as the value (per exam)."""
    if raw_query.startswith(f"{key}=&") and not raw_query.startswith(f"{key}=&{key}="):
        return "&"
    params = parse_qs(raw_query, keep_blank_values=True)
    return params.get(key, [""])[0]


def _render_search_page(version: str) -> str:
    endpoint = f"/{version}/search"
    title = "关键词搜索 (Phase 1)" if version == "v1" else "语义搜索 (Phase 2)"
    sample = "OOM / CDN / 故障" if version == "v1" else "服务器挂了 / 黑客攻击 / 机器学习模型出问题"
    return _PAGE_TEMPLATE.format(
        title=escape(title),
        endpoint=endpoint,
        sample=escape(sample),
        nav=_NAV_HTML,
        version=version,
    )


_NAV_HTML = """
<nav class="topnav">
  <a href="/v1">/v1 关键词</a>
  <a href="/v2">/v2 语义</a>
  <a href="/v3">/v3 Agent</a>
  <a href="/health">/health</a>
  <a href="/" target="_blank">Gradio UI</a>
</nav>
"""


_BASE_CSS = """
:root { color-scheme: light; --bg:#f5f7fb; --panel:#fff; --text:#172033; --muted:#667085; --line:#d9e0ea; --accent:#2563eb; --accent-dark:#1e40af; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:15px/1.6 -apple-system, BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; }
.shell { max-width:1080px; margin:0 auto; padding:28px 18px; }
.topnav { display:flex; gap:10px; margin-bottom:18px; flex-wrap:wrap; }
.topnav a { color:var(--accent-dark); text-decoration:none; border:1px solid var(--line); background:#fff; padding:7px 12px; border-radius:6px; font-size:14px; }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:22px; box-shadow:0 8px 24px rgba(24,34,66,.06); }
h1 { margin:0 0 18px; font-size:22px; }
.search-row { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:10px; }
input, textarea { width:100%; border:1px solid var(--line); border-radius:6px; padding:10px 12px; font:inherit; outline:none; }
input:focus, textarea:focus { border-color:var(--accent); box-shadow:0 0 0 3px rgba(37,99,235,.14); }
button { border:0; border-radius:6px; padding:10px 16px; background:var(--accent); color:#fff; font:inherit; cursor:pointer; }
button:hover { background:var(--accent-dark); }
.muted { margin:14px 0; color:var(--muted); font-size:13px; }
.results { padding-left:20px; margin-top:14px; }
.result { padding:14px 0; border-top:1px solid var(--line); }
.result-head { display:flex; justify-content:space-between; gap:16px; }
.result-head span { color:var(--muted); white-space:nowrap; font-size:13px; }
.result p { margin:8px 0 0; color:#344054; }
.chat-panel { min-height:72vh; display:grid; grid-template-rows:auto 1fr auto; gap:10px; }
.history { overflow:auto; border:1px solid var(--line); border-radius:8px; padding:14px; background:#fbfcff; min-height:300px; }
.bubble { max-width:880px; margin:0 0 12px; padding:12px; border-radius:8px; border:1px solid var(--line); }
.bubble.user { margin-left:auto; background:#eff6ff; }
.bubble.assistant { background:#fff; }
pre { white-space:pre-wrap; word-break:break-word; margin:0 0 10px; font:inherit; }
code { background:#eef2f7; padding:2px 5px; border-radius:4px; }
details { margin-top:8px; }
"""


_PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>On-Call Assistant - {title}</title><style>__BASE_CSS__</style></head>
<body>
<main class="shell">{nav}
<section class="panel">
  <h1>{title}</h1>
  <form id="search-form" class="search-row">
    <input id="query" name="q" autocomplete="off" placeholder="{sample}" autofocus>
    <button type="submit">搜索</button>
  </form>
  <div id="meta" class="muted"></div>
  <ol id="results" class="results"></ol>
</section></main>
<script>
const form=document.querySelector('#search-form'),input=document.querySelector('#query'),
results=document.querySelector('#results'),meta=document.querySelector('#meta');
async function runSearch(q){{
  const res=await fetch('{endpoint}?q='+encodeURIComponent(q));
  const data=await res.json();
  meta.textContent=`query="${{data.query}}", 共 ${{data.results.length}} 条结果`;
  results.innerHTML=data.results.map(item=>`
    <li class="result"><div class="result-head"><strong>${{item.title}}</strong>
    <span>${{item.id}} · score ${{item.score}}</span></div><p>${{item.snippet||''}}</p>
    ${{item.section?`<p class="muted">章节：${{item.section}}</p>`:''}}</li>`).join('');
}}
form.addEventListener('submit',e=>{{e.preventDefault();runSearch(input.value);}});
const init=new URLSearchParams(location.search).get('q');
if(init){{input.value=init;runSearch(init);}}
</script></body></html>"""


_CHAT_PAGE = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>On-Call Assistant - Agent</title><style>__BASE_CSS__</style></head>
<body>
<main class="shell">__NAV__
<section class="panel chat-panel">
  <h1>On-Call 助手 Agent (/v3)</h1>
  <div class="muted">提示：Agent 使用真实 LLM (GLM-4.6) 推理 + Qwen3-Embedding-8B 检索。<a href="javascript:resetSession()">清空会话</a></div>
  <div id="history" class="history"></div>
  <form id="chat-form" class="search-row">
    <input id="message" autocomplete="off" placeholder="数据库主从延迟超过30秒怎么处理？" autofocus>
    <button type="submit">发送</button>
  </form>
</section></main>
<script>
const form=document.querySelector('#chat-form'),message=document.querySelector('#message'),
history=document.querySelector('#history');
let sessionId=localStorage.getItem('oncall_session')||(crypto.randomUUID?crypto.randomUUID():String(Date.now()));
localStorage.setItem('oncall_session',sessionId);
function esc(s){{return s.replace(/[&<>]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;"}}[c]));}}
function block(cls,html){{const n=document.createElement('div');n.className=cls;n.innerHTML=html;history.appendChild(n);history.scrollTop=history.scrollHeight;}}
function resetSession(){{fetch('/v3/reset',{{method:'POST',headers:{{'content-type':'application/json'}},body:JSON.stringify({{session_id:sessionId}})}});history.innerHTML='';}}
async function send(text){{
  block('bubble user',esc(text));
  const res=await fetch('/v3/chat',{{method:'POST',headers:{{'content-type':'application/json'}},body:JSON.stringify({{message:text,session_id:sessionId}})}});
  const data=await res.json();
  const calls=data.tool_calls.map(c=>`<li><code>${{c.tool}}(${{c.arguments.fname||''}})</code> ${{c.result.ok?'OK':'<span style=color:#b91c1c>FAIL</span>'}} · ${{c.result.elapsed_ms}}ms ${{c.result.error?` · ${{esc(c.result.error)}}`:''}}</li>`).join('');
  const sources=data.sources.map(s=>`<li>${{s.filename}} · ${{esc(s.title||'')}}</li>`).join('');
  block('bubble assistant',`<pre>${{esc(data.answer)}}</pre>
    <details open><summary>工具调用 (${{data.tool_calls.length}}) ${{data.used_llm?' · LLM':' · 离线 fallback'}}</summary><ul>${{calls}}</ul></details>
    ${{sources?`<details><summary>来源 SOP</summary><ul>${{sources}}</ul></details>`:''}}`);
}}
form.addEventListener('submit',e=>{{e.preventDefault();const t=message.value.trim();if(!t)return;message.value='';send(t);}});
const init=new URLSearchParams(location.search).get('message');
if(init){{message.value=init;send(init);}}
</script></body></html>"""


def render_search_page(version: str) -> str:
    return _render_search_page(version).replace("__BASE_CSS__", _BASE_CSS)


def render_chat_page() -> str:
    return _CHAT_PAGE.replace("__BASE_CSS__", _BASE_CSS).replace("__NAV__", _NAV_HTML)


class OnCallRequestHandler(BaseHTTPRequestHandler):
    server_version = "OnCallAssistant/2.0"

    @property
    def service(self) -> OnCallService:
        return self.server.service  # type: ignore[attr-defined]

    # --- helpers ---
    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("content-length", "0") or "0")
        if length > MAX_BODY_BYTES:
            raise ValueError("request body too large")
        raw = self.rfile.read(length) if length > 0 else b""
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        log.info("%s - %s", self.address_string(), format % args)

    # --- routing ---
    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/":
                self._send_html(_redirect_page("/v1"))
            elif path == "/health":
                self._send_json({"status": "ok", **self.service.status()})
            elif path == "/v1":
                self._send_html(render_search_page("v1"))
            elif path == "/v2":
                self._send_html(render_search_page("v2"))
            elif path == "/v3":
                self._send_html(render_chat_page())
            elif path == "/v1/search":
                q = _query_value(parsed.query)
                self._send_json({"query": q, "results": self.service.keyword_search(q)})
            elif path == "/v2/search":
                q = _query_value(parsed.query)
                self._send_json({"query": q, "results": self.service.semantic_search(q)})
            elif path == "/v3/sessions":
                sessions = [
                    {
                        "session_id": s.session_id,
                        "turns": len(s.turns),
                        "facts": s.facts,
                        "updated_at": s.updated_at,
                    }
                    for s in self.service.memory.list_sessions()
                ]
                self._send_json({"sessions": sessions})
            else:
                self._send_json({"error": "not found", "path": path}, status=HTTPStatus.NOT_FOUND)
        except Exception as exc:
            log.exception("GET %s failed", self.path)
            self._send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/v1/documents":
                payload = self._read_json()
                doc_id = str(payload.get("id", "")).strip().lower()
                html = str(payload.get("html", ""))
                if not doc_id or not html:
                    self._send_json({"error": "id and html are required"}, status=400)
                    return
                doc = self.service.add_document(doc_id, html)
                self._send_json({"id": doc.doc_id, "title": doc.title}, status=201)
            elif path == "/v3/chat":
                payload = self._read_json()
                message = str(payload.get("message", "")).strip()
                session_id = payload.get("session_id") or None
                if not message:
                    self._send_json({"error": "message is required"}, status=400)
                    return
                self._send_json(self.service.chat(message, session_id=session_id))
            elif path == "/v3/reset":
                payload = self._read_json()
                session_id = payload.get("session_id")
                if session_id:
                    self.service.reset_session(session_id)
                self._send_json({"ok": True})
            else:
                self._send_json({"error": "not found", "path": path}, status=HTTPStatus.NOT_FOUND)
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, status=400)
        except Exception as exc:
            log.exception("POST %s failed", self.path)
            self._send_json({"error": str(exc)}, status=500)


def _redirect_page(target: str) -> str:
    return f"""<!doctype html><html><head><meta http-equiv="refresh" content="0;url={target}"></head>
<body><a href="{target}">{target}</a></body></html>"""


class OnCallHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], service: OnCallService) -> None:
        self.service = service
        super().__init__(address, OnCallRequestHandler)


def serve(host: str | None = None, port: int | None = None, service: OnCallService | None = None) -> None:
    host = host or SETTINGS.http_host
    port = port or SETTINGS.http_port
    service = service or OnCallService()
    server = OnCallHTTPServer((host, port), service)
    log.info("HTTP API listening on http://%s:%d", host, port)
    log.info("Status: %s", service.status())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
