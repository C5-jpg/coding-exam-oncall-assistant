"""Gradio UI with three tabs.

Tab 1 - Phase 1: Keyword search
Tab 2 - Phase 2: Semantic / hybrid search
Tab 3 - Phase 3: Agent chat (with conversation memory + tool-call inspector)

The UI talks directly to the in-process OnCallService (no HTTP roundtrip),
which keeps latency low and avoids race conditions when both servers run
in the same process.
"""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import gradio as gr

from .config import SETTINGS
from .service import OnCallService

log = logging.getLogger("oncall.gradio")


def _format_search_table(rows: list[dict[str, Any]]) -> list[list[Any]]:
    out = []
    for r in rows:
        out.append(
            [
                r.get("id", ""),
                r.get("title", ""),
                r.get("score", 0.0),
                r.get("section", "-"),
                r.get("snippet", ""),
            ]
        )
    return out


def _format_tool_calls_md(calls: list[dict[str, Any]]) -> str:
    if not calls:
        return "_(no tool calls)_"
    lines = []
    for i, c in enumerate(calls, 1):
        args = c.get("arguments", {}) or {}
        args_s = ", ".join(f"{k}={v!r}" for k, v in args.items())
        result = c.get("result", {}) or {}
        ok = result.get("ok", False)
        elapsed = result.get("elapsed_ms", 0)
        err = result.get("error", "")
        preview = result.get("preview", "")
        status = "✅" if ok else "❌"
        lines.append(
            f"**{i}. `{c.get('tool','?')}({args_s})`** · {status} · {elapsed} ms"
            + (f" · `{err}`" if err else "")
        )
        if preview:
            lines.append(f"\n> {preview}\n")
    return "\n".join(lines)


def _format_sources_md(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return ""
    rows = "\n".join(f"- `{s.get('filename','')}` — {s.get('title','')}" for s in sources)
    return f"### 来源 SOP\n{rows}"


def _format_status(status: dict[str, Any]) -> str:
    parts = [
        f"**SOPs**: {status.get('documents', 0)}  ·  **Chunks**: {status.get('chunks', 0)}",
        f"**Embedding**: `{status.get('embedding_model','?')}` (dim {status.get('embedding_dim','?')})"
        + ("  ·  ⚠️ fallback" if status.get("embedding_using_fallback") else ("  ·  ✅ API" if status.get("embedding_api") else "  ·  ⚠️ no key")),
        f"**LLM**: `{status.get('llm_model','?')}`"
        + ("  ·  ✅ API" if status.get("llm_api") else "  ·  ⚠️ no key (deterministic fallback)"),
    ]
    return "\n\n".join(parts)


def build_ui(service: OnCallService | None = None) -> gr.Blocks:
    service = service or OnCallService()

    def _do_keyword(q: str) -> tuple[list[list[Any]], str]:
        if not q or not q.strip():
            return [], ""
        rows = service.keyword_search(q.strip(), limit=10)
        return _format_search_table(rows), f"query=`{q}` · {len(rows)} hits"

    def _do_semantic(q: str) -> tuple[list[list[Any]], str]:
        if not q or not q.strip():
            return [], ""
        rows = service.semantic_search(q.strip(), limit=10)
        return _format_search_table(rows), f"query=`{q}` · {len(rows)} hits"

    def _do_chat(message: str, history: list, session_id: str):
        if not message or not message.strip():
            return history or [], "_请输入问题_", "", "", session_id

        history = list(history or [])
        result = service.chat(message.strip(), session_id=session_id)
        answer = result.get("answer", "(empty)")
        # gradio Chatbot legacy format: list of (user, assistant) pairs
        history.append((message, answer))

        meta_lines = [
            f"**LLM**: {'✅ glm-4.6' if result.get('used_llm') else '⚠️ deterministic fallback'}",
            f"**Session**: `{session_id}`",
        ]
        if result.get("candidate_hint"):
            meta_lines.append("\n<details><summary>候选 SOP (hybrid retrieval)</summary>\n\n```\n"
                              + result["candidate_hint"] + "\n```\n</details>")

        tool_md = _format_tool_calls_md(result.get("tool_calls", []))
        sources_md = _format_sources_md(result.get("sources", []))
        meta_md = "\n\n".join(meta_lines)
        return history, tool_md, sources_md, meta_md, session_id

    def _reset_session(_session_id: str):
        new_id = str(uuid.uuid4())
        return [], "", "", f"**Session**: `{new_id}` (new)", new_id

    def _new_session():
        return str(uuid.uuid4())

    def _add_document(doc_id: str, html: str) -> str:
        try:
            doc = service.add_document(doc_id.strip(), html)
            return f"✅ Added `{doc.filename}` — {doc.title}"
        except Exception as exc:
            return f"❌ {type(exc).__name__}: {exc}"

    def _refresh_status() -> str:
        return _format_status(service.status())

    with gr.Blocks(title="On-Call SOP Assistant") as demo:
        gr.Markdown(
            """
# 🛟 On-Call SOP Assistant
基于 **Qwen3-Embedding-8B** (硅基流动) 向量检索 + **GLM-4.6** (智谱 Coding Plan) Agent 的值班助手。

- Phase 1: 关键词搜索  ·  Phase 2: 语义/混合搜索  ·  Phase 3: 带记忆的 LLM Agent
- 也提供 HTTP API：`/v1/search`, `/v2/search`, `/v3/chat`（默认 `:8000`）
"""
        )
        status_md = gr.Markdown(_format_status(service.status()))
        gr.Button("🔄 刷新状态", size="sm").click(_refresh_status, outputs=status_md)

        with gr.Tabs():
            # ----- Tab 1: Keyword search -----
            with gr.Tab("🔎 Phase 1 · 关键词搜索"):
                gr.Markdown("基于 TF-IDF 风格的可解释关键词检索。中文使用 2-4 字 n-gram。")
                with gr.Row():
                    kw_input = gr.Textbox(
                        label="查询",
                        placeholder="OOM / CDN / 故障 / replication / &",
                        scale=4,
                    )
                    kw_btn = gr.Button("搜索", scale=1, variant="primary")
                kw_meta = gr.Markdown()
                kw_table = gr.Dataframe(
                    headers=["ID", "标题", "分数", "章节", "片段"],
                    datatype=["str", "str", "number", "str", "str"],
                    wrap=True,
                    interactive=False,
                )
                kw_btn.click(_do_keyword, inputs=kw_input, outputs=[kw_table, kw_meta])
                kw_input.submit(_do_keyword, inputs=kw_input, outputs=[kw_table, kw_meta])
                gr.Examples(
                    examples=["OOM", "故障", "replication", "CDN", "&"],
                    inputs=kw_input,
                )

            # ----- Tab 2: Semantic / hybrid -----
            with gr.Tab("🧠 Phase 2 · 语义搜索 (Hybrid + Embedding)"):
                gr.Markdown("Qwen3-Embedding-8B 向量检索 + 关键词召回 → RRF 融合排序。")
                with gr.Row():
                    sem_input = gr.Textbox(
                        label="查询",
                        placeholder="服务器挂了 / 黑客攻击 / 机器学习模型出问题",
                        scale=4,
                    )
                    sem_btn = gr.Button("搜索", scale=1, variant="primary")
                sem_meta = gr.Markdown()
                sem_table = gr.Dataframe(
                    headers=["ID", "标题", "RRF 分数", "章节", "片段"],
                    datatype=["str", "str", "number", "str", "str"],
                    wrap=True,
                    interactive=False,
                )
                sem_btn.click(_do_semantic, inputs=sem_input, outputs=[sem_table, sem_meta])
                sem_input.submit(_do_semantic, inputs=sem_input, outputs=[sem_table, sem_meta])
                gr.Examples(
                    examples=[
                        "服务器挂了",
                        "黑客攻击",
                        "机器学习模型出问题",
                        "页面打不开",
                        "Kafka 消费积压",
                    ],
                    inputs=sem_input,
                )

            # ----- Tab 3: Agent chat -----
            with gr.Tab("🤖 Phase 3 · On-Call Agent"):
                gr.Markdown(
                    "Agent 唯一工具：`readFile(fname)`. 先做 hybrid 检索给出候选 SOP，"
                    "然后由 GLM-4.6 决定调用哪个 SOP，并在多轮记忆下生成答案。"
                )
                session_state = gr.State(value=str(uuid.uuid4()))
                chatbot = gr.Chatbot(label="对话", height=420)
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="问题",
                        placeholder="数据库主从延迟超过30秒怎么处理？",
                        scale=5,
                    )
                    chat_btn = gr.Button("发送", scale=1, variant="primary")
                with gr.Row():
                    new_btn = gr.Button("🆕 新建会话")
                meta_md = gr.Markdown(value=f"**Session**: `(new)`")
                with gr.Accordion("🛠️ 工具调用过程", open=True):
                    tool_md = gr.Markdown()
                with gr.Accordion("📚 引用 SOP", open=False):
                    sources_md = gr.Markdown()

                chat_btn.click(
                    _do_chat,
                    inputs=[chat_input, chatbot, session_state],
                    outputs=[chatbot, tool_md, sources_md, meta_md, session_state],
                ).then(lambda: "", outputs=chat_input)
                chat_input.submit(
                    _do_chat,
                    inputs=[chat_input, chatbot, session_state],
                    outputs=[chatbot, tool_md, sources_md, meta_md, session_state],
                ).then(lambda: "", outputs=chat_input)
                new_btn.click(
                    _reset_session,
                    inputs=session_state,
                    outputs=[chatbot, tool_md, sources_md, meta_md, session_state],
                )
                gr.Examples(
                    examples=[
                        "数据库主从延迟超过30秒怎么处理？",
                        "服务 OOM 了怎么办？",
                        "P0 故障的响应流程是什么？",
                        "怀疑有人入侵了系统",
                        "推荐结果质量下降了",
                        "Kafka 消费积压如何处理",
                        "App 闪退率上升怎么办",
                    ],
                    inputs=chat_input,
                )

            # ----- Admin tab -----
            with gr.Tab("📥 文档管理 (Admin)"):
                gr.Markdown("写入新 SOP 后会自动重建关键词索引和向量索引。")
                with gr.Row():
                    add_id = gr.Textbox(label="文档 ID", placeholder="sop-100", scale=1)
                    add_btn = gr.Button("添加 / 替换", variant="primary", scale=1)
                add_html = gr.Textbox(
                    label="HTML 内容",
                    lines=10,
                    placeholder="<html><head><title>...</title></head><body>...</body></html>",
                )
                add_status = gr.Markdown()
                add_btn.click(_add_document, inputs=[add_id, add_html], outputs=add_status)

    return demo


def launch(
    host: str | None = None,
    port: int | None = None,
    service: OnCallService | None = None,
    share: bool = False,
) -> None:
    host = host or SETTINGS.gradio_host
    port = port or SETTINGS.gradio_port
    demo = build_ui(service)
    demo.queue()
    demo.launch(server_name=host, server_port=port, share=share)
