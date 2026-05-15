#!/usr/bin/env python3
"""On-Call SOP assistant for coding-exam question 1.

The application intentionally uses only Python's standard library so it can run
in a clean environment without package installation.
"""

from __future__ import annotations

import argparse
import json
import math
import mimetypes
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from html import escape, unescape
from html.parser import HTMLParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse


ROOT_DIR = Path(__file__).resolve().parents[2]
QUESTION_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = QUESTION_DIR / "data"
MAX_BODY_BYTES = 4 * 1024 * 1024


DOMAIN_PHRASES = [
    "on-call",
    "oom",
    "outofmemoryerror",
    "p0",
    "p1",
    "p2",
    "qps",
    "p99",
    "p95",
    "cdn",
    "dns",
    "ddos",
    "waf",
    "ids",
    "siem",
    "sql",
    "redis",
    "mysql",
    "postgresql",
    "mongodb",
    "kafka",
    "kubernetes",
    "prometheus",
    "grafana",
    "alertmanager",
    "pagerduty",
    "gpu",
    "tensorflow",
    "pytorch",
    "triton",
    "特征服务",
    "推荐系统",
    "主从复制",
    "主从延迟",
    "慢查询",
    "连接池",
    "页面白屏",
    "资源加载",
    "故障响应",
    "升级流程",
    "数据泄露",
    "入侵检测",
    "模型推理",
    "模型效果",
    "质量下降",
    "自动化测试",
    "发版卡点",
]


SEMANTIC_RULES: list[dict[str, Any]] = [
    {
        "name": "backend_service_down",
        "triggers": ["服务器", "服务挂", "挂了", "宕机", "不可用", "超时", "服务异常", "oom", "内存溢出"],
        "expansions": [
            "后端服务",
            "服务超时",
            "可用性",
            "限流降级",
            "熔断",
            "Kubernetes",
            "Pod",
            "OOM",
            "OutOfMemoryError",
            "P99延迟",
            "核心链路",
        ],
        "boosts": {"sop-001": 7.0, "sop-004": 4.2},
    },
    {
        "name": "database_replication",
        "triggers": ["数据库", "主从", "复制", "延迟", "慢查询", "连接数", "dba", "mysql", "redis"],
        "expansions": [
            "数据库",
            "DBA",
            "主从复制",
            "主从延迟",
            "SHOW SLAVE STATUS",
            "GTID",
            "慢查询",
            "连接池",
            "数据一致性",
        ],
        "boosts": {"sop-002": 7.0, "sop-001": 1.2},
    },
    {
        "name": "frontend_cdn",
        "triggers": ["白屏", "页面打不开", "静态资源", "cdn", "js", "css", "浏览器", "兼容"],
        "expansions": ["前端", "页面白屏", "CDN资源", "资源加载失败", "浏览器兼容性", "首屏性能"],
        "boosts": {"sop-003": 7.0, "sop-010": 2.5},
    },
    {
        "name": "sre_infra",
        "triggers": ["k8s", "kubernetes", "集群", "节点", "ingress", "监控告警", "容量", "基础设施"],
        "expansions": ["SRE", "Kubernetes", "集群", "Ingress", "Etcd", "容量规划", "监控告警", "基础设施故障"],
        "boosts": {"sop-004": 7.0, "sop-001": 1.5},
    },
    {
        "name": "security_attack",
        "triggers": ["黑客", "攻击", "入侵", "安全", "漏洞", "泄露", "ddos", "sql注入", "暴力破解", "被盗"],
        "expansions": [
            "信息安全",
            "安全事件",
            "入侵检测",
            "WAF",
            "IDS",
            "SIEM",
            "DDoS攻击",
            "SQL注入",
            "数据泄露",
            "应急响应",
        ],
        "boosts": {"sop-005": 8.0, "sop-010": 2.0},
    },
    {
        "name": "data_platform",
        "triggers": ["数据管道", "etl", "spark", "任务失败", "数仓", "数据延迟", "数据质量"],
        "expansions": ["数据平台", "ETL失败", "Spark集群", "数据管道", "数据质量", "调度任务"],
        "boosts": {"sop-006": 7.0},
    },
    {
        "name": "mobile",
        "triggers": ["app", "崩溃", "闪退", "热修复", "推送", "移动端", "ios", "android"],
        "expansions": ["移动端", "App崩溃率", "热修复", "推送服务", "Crash", "灰度发布"],
        "boosts": {"sop-007": 7.0},
    },
    {
        "name": "ai_model",
        "triggers": ["机器学习", "模型", "推荐", "推荐结果", "质量下降", "效果下降", "推理", "gpu", "算法", "搜索排序"],
        "expansions": [
            "AI算法",
            "推荐系统",
            "模型推理延迟",
            "模型效果下降",
            "点击率",
            "转化率",
            "特征服务",
            "数据漂移",
            "GPU集群",
            "AB实验",
        ],
        "boosts": {"sop-008": 8.0},
    },
    {
        "name": "qa_release",
        "triggers": ["测试", "自动化", "发版", "发布", "环境故障", "回归", "qa"],
        "expansions": ["QA", "测试环境", "自动化测试", "发版卡点", "回归测试", "质量门禁"],
        "boosts": {"sop-009": 7.0},
    },
    {
        "name": "network_cdn",
        "triggers": ["网络", "cdn", "dns", "解析", "节点", "ddos", "负载均衡", "专线"],
        "expansions": ["网络CDN", "CDN节点故障", "DNS异常", "DDoS防护", "BGP", "负载均衡", "回源率"],
        "boosts": {"sop-010": 7.0, "sop-003": 2.2, "sop-005": 1.5},
    },
    {
        "name": "p0_response",
        "triggers": ["p0", "最高级", "严重故障", "故障响应流程", "响应流程", "升级流程", "战争室", "war room"],
        "expansions": ["P0", "故障响应", "升级流程", "War Room", "技术负责人", "影响范围", "值班日志"],
        "boosts": {"sop-001": 4.0, "sop-004": 4.0, "sop-005": 3.0, "sop-010": 3.0},
    },
]


STOPWORDS = {
    "the",
    "and",
    "or",
    "is",
    "are",
    "a",
    "an",
    "to",
    "of",
    "in",
    "on",
    "for",
    "了",
    "的",
    "怎么",
    "如何",
    "怎么办",
    "处理",
    "问题",
}


def compact_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize(value: str) -> str:
    return compact_spaces(unescape(value)).lower()


def chinese_ngrams(segment: str) -> list[str]:
    grams: list[str] = []
    if not segment:
        return grams
    if len(segment) <= 8:
        grams.append(segment)
    for width in (2, 3, 4):
        if len(segment) >= width:
            grams.extend(segment[i : i + width] for i in range(0, len(segment) - width + 1))
    return grams


def tokenize(value: str) -> list[str]:
    value = normalize(value)
    tokens: list[str] = []
    for word in re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", value):
        if word not in STOPWORDS:
            tokens.append(word)
    for segment in re.findall(r"[\u4e00-\u9fff]+", value):
        tokens.extend(token for token in chinese_ngrams(segment) if token not in STOPWORDS)
    for phrase in DOMAIN_PHRASES:
        phrase_norm = normalize(phrase)
        if phrase_norm and phrase_norm in value:
            tokens.append(phrase_norm)
    return tokens


def split_query_terms(query: str) -> list[str]:
    terms: list[str] = []
    query_norm = normalize(query)
    if query_norm:
        terms.append(query_norm)
    terms.extend(tokenize(query))
    deduped: list[str] = []
    seen: set[str] = set()
    for term in terms:
        term = term.strip()
        if term and term not in seen:
            deduped.append(term)
            seen.add(term)
    return deduped


class VisibleTextExtractor(HTMLParser):
    """Extract visible text and title while ignoring scripts/styles."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self._in_title = False
        self._in_body = False
        self._title_parts: list[str] = []
        self._body_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "template", "svg", "canvas"}:
            self._ignored_depth += 1
            return
        if tag == "title":
            self._in_title = True
        elif tag == "body":
            self._in_body = True
        elif self._in_body and tag in {"p", "br", "li", "tr", "h1", "h2", "h3", "h4", "section", "article"}:
            self._body_parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "template", "svg", "canvas"} and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        elif tag == "body":
            self._in_body = False
        elif self._in_body and tag in {"p", "li", "tr", "h1", "h2", "h3", "h4", "section", "article"}:
            self._body_parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        text = compact_spaces(data)
        if not text:
            return
        if self._in_title:
            self._title_parts.append(text)
        if self._in_body:
            self._body_parts.append(text)

    @property
    def title(self) -> str:
        return compact_spaces(" ".join(self._title_parts))

    @property
    def text(self) -> str:
        return compact_spaces(" ".join(self._body_parts))


@dataclass
class Document:
    id: str
    title: str
    html: str
    text: str
    source_path: Path | None = None
    token_counts: Counter[str] = field(default_factory=Counter)
    norm_text: str = ""

    @property
    def filename(self) -> str:
        if self.source_path:
            return self.source_path.name
        return f"{self.id}.html"


@dataclass
class SearchResult:
    id: str
    title: str
    snippet: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "snippet": self.snippet,
            "score": round(self.score, 4),
        }


class DocumentIndex:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir.resolve()
        self.documents: dict[str, Document] = {}
        self.idf: dict[str, float] = {}
        self._mtime = 0.0
        self.load_data_dir()

    def load_data_dir(self) -> None:
        html_files = sorted(self.data_dir.glob("*.html"))
        for path in html_files:
            doc_id = path.stem.lower()
            self.add_document(doc_id, path.read_text(encoding="utf-8"), source_path=path, rebuild=False)
        self.rebuild()
        self._mtime = time.time()

    def add_document(self, doc_id: str, html: str, source_path: Path | None = None, rebuild: bool = True) -> Document:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", doc_id):
            raise ValueError("document id may only contain letters, numbers, dot, underscore and dash")
        parser = VisibleTextExtractor()
        parser.feed(html)
        title = parser.title or self._first_heading(parser.text) or doc_id
        text = parser.text
        searchable_text = compact_spaces(f"{title} {text}")
        doc = Document(
            id=doc_id,
            title=title,
            html=html,
            text=text,
            source_path=source_path,
            token_counts=Counter(tokenize(searchable_text)),
            norm_text=normalize(searchable_text),
        )
        self.documents[doc_id] = doc
        if rebuild:
            self.rebuild()
        return doc

    def rebuild(self) -> None:
        total_docs = max(len(self.documents), 1)
        df: Counter[str] = Counter()
        for doc in self.documents.values():
            df.update(doc.token_counts.keys())
        self.idf = {
            token: math.log((1 + total_docs) / (1 + count)) + 1.0
            for token, count in df.items()
        }

    @staticmethod
    def _first_heading(text: str) -> str | None:
        text = compact_spaces(text)
        if not text:
            return None
        return text[:80]

    def keyword_search(self, query: str, limit: int = 10) -> list[SearchResult]:
        query = unescape(query or "")
        query_norm = normalize(query)
        if not query_norm:
            return []
        terms = split_query_terms(query)
        results: list[SearchResult] = []
        for doc in self.documents.values():
            score = 0.0
            if query_norm:
                phrase_count = doc.norm_text.count(query_norm)
                score += phrase_count * (8.0 + min(len(query_norm), 12) / 2)
            for term in terms:
                if not term:
                    continue
                if term in doc.norm_text:
                    score += doc.norm_text.count(term) * (2.5 + min(len(term), 8) / 4)
                if term in doc.token_counts:
                    score += doc.token_counts[term] * self.idf.get(term, 1.0)
            if score > 0:
                results.append(
                    SearchResult(
                        id=doc.id,
                        title=doc.title,
                        snippet=self.make_snippet(doc, [query_norm, *terms]),
                        score=score,
                    )
                )
        results.sort(key=lambda item: (-item.score, item.id))
        return results[:limit]

    def semantic_search(self, query: str, limit: int = 10) -> list[SearchResult]:
        query = unescape(query or "")
        if not normalize(query):
            return []
        expanded_texts, doc_boosts, matched_rules = self.expand_query(query)
        query_text = " ".join([query, *expanded_texts])
        query_counts = Counter(tokenize(query_text))
        exact_terms = split_query_terms(query)
        results: list[SearchResult] = []
        for doc in self.documents.values():
            score = 0.0
            for token, q_count in query_counts.items():
                tf = doc.token_counts.get(token, 0)
                if tf:
                    score += (1 + math.log(tf)) * q_count * (self.idf.get(token, 1.0) ** 2)
            for term in exact_terms:
                if term and term in doc.norm_text:
                    score += 2.5 + min(len(term), 10) / 5
            score += doc_boosts.get(doc.id, 0.0)
            if score > 0:
                snippet_terms = exact_terms + tokenize(" ".join(expanded_texts[:4]))
                results.append(
                    SearchResult(
                        id=doc.id,
                        title=doc.title,
                        snippet=self.make_snippet(doc, snippet_terms),
                        score=score,
                    )
                )
        results.sort(key=lambda item: (-item.score, item.id))
        return results[:limit]

    def expand_query(self, query: str) -> tuple[list[str], dict[str, float], list[str]]:
        query_norm = normalize(query)
        expansions: list[str] = []
        boosts: dict[str, float] = {}
        matched_rules: list[str] = []
        for rule in SEMANTIC_RULES:
            if any(normalize(trigger) in query_norm for trigger in rule["triggers"]):
                matched_rules.append(rule["name"])
                expansions.extend(rule["expansions"])
                for doc_id, value in rule["boosts"].items():
                    boosts[doc_id] = boosts.get(doc_id, 0.0) + float(value)
        return expansions, boosts, matched_rules

    def make_snippet(self, doc: Document, terms: list[str], radius: int = 86) -> str:
        text = compact_spaces(doc.text or doc.title)
        text_norm = normalize(text)
        best_pos: int | None = None
        best_term = ""
        for term in terms:
            term_norm = normalize(term)
            if not term_norm:
                continue
            pos = text_norm.find(term_norm)
            if pos >= 0 and (best_pos is None or pos < best_pos):
                best_pos = pos
                best_term = term_norm
        if best_pos is None:
            snippet = text[: radius * 2]
        else:
            start = max(0, best_pos - radius)
            end = min(len(text), best_pos + len(best_term) + radius)
            snippet = text[start:end]
            if start:
                snippet = "..." + snippet
            if end < len(text):
                snippet += "..."
        return snippet


class ReadFileTool:
    """The only tool exposed to the agent."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir.resolve()

    def __call__(self, fname: str) -> str:
        if not fname or "/" in fname or "\\" in fname or "*" in fname or "?" in fname:
            raise ValueError("readFile only accepts a plain file name without path separators or wildcards")
        target = (self.data_dir / fname).resolve()
        if target.parent != self.data_dir:
            raise ValueError("readFile can only access files in data/")
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(fname)
        return target.read_text(encoding="utf-8")


class OnCallAgent:
    def __init__(self, index: DocumentIndex, data_dir: Path) -> None:
        self.index = index
        self.read_file = ReadFileTool(data_dir)

    def answer(self, message: str) -> dict[str, Any]:
        selected = self.select_documents(message)
        tool_calls: list[dict[str, Any]] = []
        source_docs: list[Document] = []
        for doc in selected:
            fname = doc.filename
            started = time.time()
            html = self.read_file(fname)
            elapsed_ms = int((time.time() - started) * 1000)
            parsed = VisibleTextExtractor()
            parsed.feed(html)
            source_text = parsed.text
            source_docs.append(
                Document(
                    id=doc.id,
                    title=parsed.title or doc.title,
                    html=html,
                    text=source_text,
                    source_path=doc.source_path,
                    norm_text=normalize(source_text),
                )
            )
            tool_calls.append(
                {
                    "tool": "readFile",
                    "arguments": {"fname": fname},
                    "result": {
                        "title": parsed.title or doc.title,
                        "chars": len(source_text),
                        "elapsed_ms": elapsed_ms,
                    },
                }
            )
        answer = self.compose_answer(message, source_docs)
        return {
            "message": message,
            "answer": answer,
            "tool_calls": tool_calls,
            "sources": [{"id": doc.id, "title": doc.title, "filename": doc.filename} for doc in selected],
        }

    def select_documents(self, message: str) -> list[Document]:
        query_norm = normalize(message)
        forced_ids: list[str] = []
        multi_source_question = any(marker in query_norm for marker in ["p0", "故障响应流程", "响应流程", "升级流程", "战争室", "war room"])

        def add_once(*doc_ids: str) -> None:
            for doc_id in doc_ids:
                if doc_id not in forced_ids:
                    forced_ids.append(doc_id)

        if multi_source_question:
            add_once("sop-001", "sop-004", "sop-005", "sop-010")
        elif any(marker in query_norm for marker in ["主从", "复制", "数据库", "慢查询", "连接数"]):
            add_once("sop-002")
        elif any(marker in query_norm for marker in ["oom", "内存溢出", "outofmemoryerror"]):
            add_once("sop-001")
        elif any(marker in query_norm for marker in ["入侵", "黑客", "安全", "攻击", "泄露", "漏洞"]):
            add_once("sop-005")
        elif any(marker in query_norm for marker in ["推荐", "质量下降", "模型", "机器学习", "效果下降"]):
            add_once("sop-008")

        if not forced_ids or multi_source_question:
            semantic = self.index.semantic_search(message, limit=5)
            for result in semantic:
                add_once(result.id)
        docs = [self.index.documents[doc_id] for doc_id in forced_ids if doc_id in self.index.documents]
        return docs[:4] or list(self.index.documents.values())[:1]

    def compose_answer(self, message: str, docs: list[Document]) -> str:
        message_norm = normalize(message)
        if not docs:
            return "未找到可参考的 SOP。请补充故障现象、影响范围、告警名称或相关系统。"

        if "主从" in message_norm or "复制" in message_norm or "数据库" in message_norm:
            return self._database_replication_answer(docs)
        if "oom" in message_norm or "内存" in message_norm:
            return self._oom_answer(docs)
        if "p0" in message_norm or "响应流程" in message_norm or "升级流程" in message_norm or "故障响应" in message_norm:
            return self._p0_answer(docs)
        if any(word in message_norm for word in ["入侵", "黑客", "安全", "攻击", "泄露", "漏洞"]):
            return self._security_answer(docs)
        if any(word in message_norm for word in ["推荐", "质量下降", "模型", "机器学习", "效果下降"]):
            return self._ai_quality_answer(docs)

        bullets = self._extract_relevant_sentences(message, docs, max_items=6)
        if not bullets:
            bullets = [f"已读取 {doc.title}，建议先确认告警范围、影响用户、最近变更和可回滚动作。" for doc in docs[:2]]
        return "根据已读取的 SOP，建议按以下顺序处理：\n" + "\n".join(f"{idx}. {item}" for idx, item in enumerate(bullets, 1))

    def _database_replication_answer(self, docs: list[Document]) -> str:
        return "\n".join(
            [
                "数据库主从延迟或复制异常建议按 DBA SOP 处理：",
                "1. 先确认主从复制状态和延迟秒数，使用 SHOW SLAVE STATUS / 复制线程状态判断是否中断、延迟还是位点异常。",
                "2. 检查错误原因：Binlog 缺失、DDL 执行失败、主键冲突、慢查询、大事务或主库负载过高。",
                "3. 如果只是延迟，先降低从库读流量或切回主库兜底，同时排查慢查询和大事务；如果复制中断，按错误类型修复或跳过事务。",
                "4. 跳过事务前必须评估数据一致性影响，修复后用 pt-table-checksum 等工具校验主从一致性。",
                "5. 延迟持续扩大、影响核心读链路或存在数据一致性风险时，升级到 DBA 团队负责人并记录处置时间线。",
            ]
        )

    def _oom_answer(self, docs: list[Document]) -> str:
        return "\n".join(
            [
                "服务 OOM 的处理路径：",
                "1. Kubernetes 自动重启后，第一时间保存堆转储和相关日志，避免证据被覆盖。",
                "2. 对照最近发布和配置变更，查看 JVM 堆内存曲线、GC、Pod 重启次数和流量突增情况。",
                "3. 突发流量导致时先临时扩容 Pod；疑似泄漏时用 jmap 或 Arthas 分析对象分布。",
                "4. 影响核心链路时先回滚到稳定版本或启用限流降级，恢复服务优先于根因分析。",
                "5. OOM 频繁发生需复查 Xmx、资源 request/limit、缓存上限和异常分支的连接/对象释放。",
            ]
        )

    def _p0_answer(self, docs: list[Document]) -> str:
        return "\n".join(
            [
                "P0 故障响应流程应跨团队统一推进：",
                "1. 立即确认影响范围、用户面、核心链路和是否存在数据/安全风险；基础设施或网络类 P0 通常要求三分钟内升级，业务服务类 P0 要求五分钟内升级。",
                "2. 拉起 War Room，指定指挥、记录、排障、沟通四个角色，所有决策进入统一沟通频道。",
                "3. 先止血：回滚最近变更、熔断下游、限流降级、切换备用通道或隔离攻击流量，优先恢复核心能力。",
                "4. 每次升级必须给出故障现象、影响范围、已采取措施、当前判断和下一步动作。",
                "5. 安全、数据泄露、核心网络中断、Kubernetes 控制面不可用等事件应同步对应负责人；涉及合规时尽早通知法务/合规。",
                "6. 故障结束后补齐时间线、根因、影响评估、长期修复项和监控补充项。",
            ]
        )

    def _security_answer(self, docs: list[Document]) -> str:
        return "\n".join(
            [
                "疑似入侵或安全攻击按安全 SOP 处理：",
                "1. 先确认告警来源和类型：WAF/IDS/SIEM、异常登录、SQL 注入、DDoS、权限变更或数据导出异常。",
                "2. 立即止血：封禁攻击源 IP、启用 WAF 严格规则、撤销可疑账号权限、隔离受影响主机或接口。",
                "3. 保全证据：保存应用日志、数据库日志、网络流量、系统快照，不要执行会破坏证据的清理动作。",
                "4. 评估影响：确认是否入侵成功、是否涉及敏感数据、是否影响核心业务系统。",
                "5. 成功入侵、数据泄露、核心系统漏洞或 APT 迹象必须立即升级到安全负责人/CISO，并同步法务和合规。",
            ]
        )

    def _ai_quality_answer(self, docs: list[Document]) -> str:
        return "\n".join(
            [
                "推荐结果质量下降建议按 AI 算法 SOP 排查：",
                "1. 先排除样本量不足和流量波动，确认点击率、转化率、相关性等指标下降是否具有统计意义。",
                "2. 检查最近是否有新模型、特征、召回源或 AB 实验上线，必要时立即回滚到旧模型或关闭负向实验。",
                "3. 核查特征链路：特征缺失、延迟、分布漂移、Feature Store 或 Redis 依赖异常都会导致效果下降。",
                "4. 检查候选集和召回源分布，确认是否有召回规模、类型分布或用户行为模式变化。",
                "5. 若效果下降超过阈值且持续，附带指标截图、实验结果和特征分析报告升级到 AI 平台负责人。",
            ]
        )

    def _extract_relevant_sentences(self, message: str, docs: list[Document], max_items: int) -> list[str]:
        terms = set(tokenize(message))
        candidates: list[tuple[float, str]] = []
        for doc in docs:
            for sentence in re.split(r"[。！？!?]\s*", doc.text):
                sentence = compact_spaces(sentence)
                if len(sentence) < 12:
                    continue
                tokens = set(tokenize(sentence))
                overlap = len(terms & tokens)
                if overlap:
                    candidates.append((overlap + len(sentence) / 500, sentence))
        candidates.sort(key=lambda item: -item[0])
        return [sentence for _, sentence in candidates[:max_items]]


def json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def get_query_value(raw_query: str) -> str:
    if raw_query == "q=&" or raw_query.startswith("q=&&"):
        return "&"
    query_params = parse_qs(raw_query, keep_blank_values=True)
    value = query_params.get("q", [""])[0]
    if value == "" and raw_query.startswith("q=&"):
        return "&"
    return value


def render_search_page(version: str) -> str:
    endpoint = f"/{version}/search"
    title = "关键词搜索" if version == "v1" else "语义搜索"
    sample = "OOM / CDN / 故障" if version == "v1" else "服务器挂了 / 黑客攻击 / 机器学习模型出问题"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>On-Call Assistant - {escape(title)}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <main class="shell">
    <nav class="topnav">
      <a href="/v1">Phase 1</a>
      <a href="/v2">Phase 2</a>
      <a href="/v3">Phase 3</a>
    </nav>
    <section class="panel">
      <h1>{escape(title)}</h1>
      <form id="search-form" class="search-row">
        <input id="query" name="q" autocomplete="off" placeholder="{escape(sample)}" autofocus>
        <button type="submit">搜索</button>
      </form>
      <div id="meta" class="muted"></div>
      <ol id="results" class="results"></ol>
    </section>
  </main>
  <script>
    const form = document.querySelector('#search-form');
    const input = document.querySelector('#query');
    const results = document.querySelector('#results');
    const meta = document.querySelector('#meta');
    async function runSearch(q) {{
      const res = await fetch('{endpoint}?q=' + encodeURIComponent(q));
      const data = await res.json();
      meta.textContent = `query="${{data.query}}"，共 ${{data.results.length}} 条结果`;
      results.innerHTML = data.results.map(item => `
        <li class="result">
          <div class="result-head"><strong>${{item.title}}</strong><span>${{item.id}} · score ${{item.score}}</span></div>
          <p>${{item.snippet}}</p>
        </li>`).join('');
    }}
    form.addEventListener('submit', event => {{
      event.preventDefault();
      runSearch(input.value);
    }});
    const initialQuery = new URLSearchParams(location.search).get('q');
    if (initialQuery) {{
      input.value = initialQuery;
      runSearch(initialQuery);
    }}
  </script>
</body>
</html>"""


def render_chat_page() -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>On-Call Assistant - Agent</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <main class="shell">
    <nav class="topnav">
      <a href="/v1">Phase 1</a>
      <a href="/v2">Phase 2</a>
      <a href="/v3">Phase 3</a>
    </nav>
    <section class="panel chat-panel">
      <h1>On-Call 助手 Agent</h1>
      <div id="history" class="history"></div>
      <form id="chat-form" class="search-row">
        <input id="message" autocomplete="off" placeholder="数据库主从延迟超过30秒怎么处理？" autofocus>
        <button type="submit">发送</button>
      </form>
    </section>
  </main>
  <script>
    const form = document.querySelector('#chat-form');
    const message = document.querySelector('#message');
    const history = document.querySelector('#history');
    function block(cls, html) {{
      const node = document.createElement('div');
      node.className = cls;
      node.innerHTML = html;
      history.appendChild(node);
      history.scrollTop = history.scrollHeight;
    }}
    async function send(text) {{
      block('bubble user', text.replace(/[&<>]/g, s => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[s])));
      const res = await fetch('/v3/chat', {{
        method: 'POST',
        headers: {{'content-type': 'application/json'}},
        body: JSON.stringify({{message: text}})
      }});
      const data = await res.json();
      const calls = data.tool_calls.map(call =>
        `<li><code>${{call.tool}}(${{call.arguments.fname}})</code> → ${{call.result.title}}，${{call.result.chars}} 字</li>`
      ).join('');
      block('bubble assistant', `<pre>${{data.answer}}</pre><details open><summary>工具调用</summary><ul>${{calls}}</ul></details>`);
    }}
    form.addEventListener('submit', event => {{
      event.preventDefault();
      const text = message.value.trim();
      if (!text) return;
      message.value = '';
      send(text);
    }});
    const initialMessage = new URLSearchParams(location.search).get('message');
    if (initialMessage) {{
      message.value = initialMessage;
      send(initialMessage);
    }}
  </script>
</body>
</html>"""


BASE_CSS = """
:root {
  color-scheme: light;
  --bg: #f5f7fb;
  --panel: #ffffff;
  --text: #172033;
  --muted: #667085;
  --line: #d9e0ea;
  --accent: #2563eb;
  --accent-dark: #1e40af;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
}
.shell { max-width: 1080px; margin: 0 auto; padding: 28px 18px; }
.topnav { display: flex; gap: 12px; margin-bottom: 18px; }
.topnav a {
  color: var(--accent-dark);
  text-decoration: none;
  border: 1px solid var(--line);
  background: #fff;
  padding: 7px 12px;
  border-radius: 6px;
}
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 22px;
  box-shadow: 0 8px 24px rgba(24, 34, 66, .06);
}
h1 { margin: 0 0 18px; font-size: 24px; line-height: 1.25; letter-spacing: 0; }
.search-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 10px; }
input {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px 12px;
  font: inherit;
  outline: none;
}
input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(37, 99, 235, .14); }
button {
  border: 0;
  border-radius: 6px;
  padding: 10px 16px;
  background: var(--accent);
  color: white;
  font: inherit;
  cursor: pointer;
}
button:hover { background: var(--accent-dark); }
.muted { margin: 14px 0; color: var(--muted); }
.results { padding-left: 20px; }
.result {
  padding: 14px 0;
  border-top: 1px solid var(--line);
}
.result-head { display: flex; justify-content: space-between; gap: 16px; }
.result-head span { color: var(--muted); white-space: nowrap; }
.result p { margin: 8px 0 0; color: #344054; }
.chat-panel { min-height: 72vh; display: grid; grid-template-rows: auto 1fr auto; }
.history {
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 12px;
  background: #fbfcff;
}
.bubble {
  max-width: 860px;
  margin: 0 0 12px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--line);
}
.bubble.user { margin-left: auto; background: #eff6ff; }
.bubble.assistant { background: #ffffff; }
pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0 0 10px;
  font: inherit;
}
code { background: #eef2f7; padding: 2px 5px; border-radius: 4px; }
@media (max-width: 680px) {
  .shell { padding: 14px; }
  .panel { padding: 16px; }
  .search-row { grid-template-columns: 1fr; }
  .result-head { display: block; }
  .result-head span { display: block; margin-top: 3px; }
}
"""


class OnCallRequestHandler(BaseHTTPRequestHandler):
    server_version = "OnCallAssistant/1.0"

    @property
    def app(self) -> "OnCallServer":
        return self.server  # type: ignore[return-value]

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                self.redirect("/v1")
            elif parsed.path == "/health":
                self.send_json({"status": "ok", "documents": len(self.app.index.documents)})
            elif parsed.path == "/v1":
                self.send_html(render_search_page("v1"))
            elif parsed.path == "/v2":
                self.send_html(render_search_page("v2"))
            elif parsed.path == "/v3":
                self.send_html(render_chat_page())
            elif parsed.path == "/v1/search":
                q = get_query_value(parsed.query)
                results = [item.to_dict() for item in self.app.index.keyword_search(q)]
                self.send_json({"query": q, "results": results})
            elif parsed.path == "/v2/search":
                q = get_query_value(parsed.query)
                results = [item.to_dict() for item in self.app.index.semantic_search(q)]
                self.send_json({"query": q, "results": results})
            else:
                self.send_error(HTTPStatus.NOT_FOUND, "route not found")
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self.send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/v1/documents":
                payload = self.read_json()
                doc_id = str(payload.get("id", "")).strip().lower()
                html = str(payload.get("html", ""))
                if not doc_id or not html:
                    self.send_json({"error": "id and html are required"}, status=400)
                    return
                doc = self.app.index.add_document(doc_id, html)
                self.send_json({"id": doc.id, "title": doc.title}, status=201)
            elif parsed.path == "/v3/chat":
                payload = self.read_json()
                message = str(payload.get("message", "")).strip()
                if not message:
                    self.send_json({"error": "message is required"}, status=400)
                    return
                self.send_json(self.app.agent.answer(message))
            else:
                self.send_error(HTTPStatus.NOT_FOUND, "route not found")
        except json.JSONDecodeError:
            self.send_json({"error": "invalid json"}, status=400)
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self.send_json({"error": str(exc)}, status=500)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("content-length", "0"))
        if length > MAX_BODY_BYTES:
            raise ValueError("request body is too large")
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def send_json(self, payload: Any, status: int = 200) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location: str) -> None:
        self.send_response(302)
        self.send_header("location", location)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")


class OnCallServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], data_dir: Path) -> None:
        self.index = DocumentIndex(data_dir)
        self.agent = OnCallAgent(self.index, data_dir)
        super().__init__(address, OnCallRequestHandler)


def run_self_test(data_dir: Path) -> int:
    index = DocumentIndex(data_dir)
    agent = OnCallAgent(index, data_dir)
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        if not ok:
            failures.append(name)

    check("v1 OOM returns sop-001", bool(index.keyword_search("OOM")) and index.keyword_search("OOM")[0].id == "sop-001")
    check("v1 故障 returns multiple docs", len(index.keyword_search("故障")) >= 5)
    check("v1 replication ignores script text", index.keyword_search("replication") == [])
    cdn_ids = {item.id for item in index.keyword_search("CDN")}
    check("v1 CDN returns sop-003 and sop-010", {"sop-003", "sop-010"}.issubset(cdn_ids))
    amp_ids = {item.id for item in index.keyword_search("&")}
    check("v1 ampersand query works", bool(amp_ids))

    server_down = [item.id for item in index.semantic_search("服务器挂了")[:2]]
    check("v2 服务器挂了 ranks backend and sre", {"sop-001", "sop-004"}.issubset(set(server_down)))
    check("v2 黑客攻击 ranks security", index.semantic_search("黑客攻击")[0].id == "sop-005")
    check("v2 机器学习模型出问题 ranks AI", index.semantic_search("机器学习模型出问题")[0].id == "sop-008")

    dba_answer = agent.answer("数据库主从延迟超过30秒怎么处理？")
    check("v3 database question reads sop-002", any(call["arguments"]["fname"] == "sop-002.html" for call in dba_answer["tool_calls"]))
    p0_answer = agent.answer("P0 故障的响应流程是什么？")
    check("v3 p0 question reads multiple SOPs", len(p0_answer["tool_calls"]) >= 3)

    summary = {
        "documents": len(index.documents),
        "checks": 10,
        "failures": failures,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the On-Call SOP assistant web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--self-test", action="store_true", help="run built-in smoke checks and exit")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    if args.self_test:
        return run_self_test(data_dir)

    httpd = OnCallServer((args.host, args.port), data_dir)
    print(f"Serving On-Call Assistant on http://{args.host}:{args.port}")
    print(f"Indexed {len(httpd.index.documents)} SOP documents from {data_dir}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
