"""Text normalisation and tokenisation.

Same robust behavior as the original baseline:
- HTML entity decoding (`&amp;` -> `&`)
- Lowercasing
- English/digit word splitting
- Chinese 2-4 character n-grams
- Domain phrase recognition
"""
from __future__ import annotations

import re
from html import unescape
from typing import Iterable

DOMAIN_PHRASES = [
    "on-call", "oom", "outofmemoryerror", "p0", "p1", "p2", "qps", "p99", "p95",
    "cdn", "dns", "ddos", "waf", "ids", "siem", "sql", "redis", "mysql",
    "postgresql", "mongodb", "kafka", "kubernetes", "prometheus", "grafana",
    "alertmanager", "pagerduty", "gpu", "tensorflow", "pytorch", "triton",
    "特征服务", "推荐系统", "主从复制", "主从延迟", "慢查询", "连接池",
    "页面白屏", "资源加载", "故障响应", "升级流程", "数据泄露", "入侵检测",
    "模型推理", "模型效果", "质量下降", "自动化测试", "发版卡点",
]

STOPWORDS = {
    "the", "and", "or", "is", "are", "a", "an", "to", "of", "in", "on", "for",
    "了", "的", "怎么", "如何", "怎么办", "处理", "问题",
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
            grams.extend(segment[i: i + width] for i in range(0, len(segment) - width + 1))
    return grams


def tokenize(value: str) -> list[str]:
    value = normalize(value)
    tokens: list[str] = []
    for word in re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", value):
        if word not in STOPWORDS:
            tokens.append(word)
    for segment in re.findall(r"[\u4e00-\u9fff]+", value):
        tokens.extend(t for t in chinese_ngrams(segment) if t not in STOPWORDS)
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
