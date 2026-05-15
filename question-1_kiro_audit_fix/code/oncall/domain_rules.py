"""Domain-rule retrieval prior.

Real on-call systems combine 3 signals:
1. Lexical match (BM25-style)
2. Vector similarity (Qwen3-Embedding-8B)
3. Domain knowledge - "if user mentions 'security incident', also surface
   the security team's SOP".

This module implements (3) as a small, configurable rule layer that adds a
positive bias to specific documents based on intent triggers. It does NOT
replace retrieval; it nudges the ranking. This pattern is identical to how
Elasticsearch `function_score` or Weaviate `where` filters with manual
boosts are used in production search systems.

Rules are deliberately compact and easy to externalise to YAML for
operations teams.
"""
from __future__ import annotations

from dataclasses import dataclass

from .tokenizer import normalize


@dataclass(frozen=True)
class DomainRule:
    name: str
    triggers: tuple[str, ...]
    boosts: tuple[tuple[str, float], ...]  # (doc_id, boost)
    expansions: tuple[str, ...] = ()


# Maintained by the on-call team. Adding a new SOP only needs adding rules
# here (or moving to YAML). All values normalised to lowercase.
DOMAIN_RULES: tuple[DomainRule, ...] = (
    DomainRule(
        name="backend_service_down",
        triggers=("服务器", "服务挂", "挂了", "宕机", "不可用", "超时", "服务异常",
                  "oom", "内存溢出", "outofmemoryerror"),
        boosts=(("sop-001", 0.35), ("sop-004", 0.20)),
        expansions=("后端服务", "服务超时", "可用性", "限流降级", "熔断",
                    "Kubernetes", "Pod", "OOM"),
    ),
    DomainRule(
        name="database_replication",
        triggers=("数据库", "主从", "复制", "延迟", "慢查询", "连接数",
                  "dba", "mysql", "redis"),
        boosts=(("sop-002", 0.40),),
        expansions=("数据库", "DBA", "主从复制", "主从延迟", "GTID",
                    "慢查询", "连接池", "数据一致性"),
    ),
    DomainRule(
        name="frontend_cdn",
        triggers=("白屏", "页面打不开", "页面白屏", "静态资源", "js", "css",
                  "浏览器", "兼容"),
        boosts=(("sop-003", 0.35), ("sop-010", 0.10)),
        expansions=("前端", "CDN资源", "资源加载失败", "首屏性能"),
    ),
    DomainRule(
        name="sre_infra",
        triggers=("k8s", "kubernetes", "集群", "节点", "ingress",
                  "监控告警", "容量", "基础设施"),
        boosts=(("sop-004", 0.40),),
        expansions=("SRE", "Kubernetes", "集群", "Etcd", "容量规划",
                    "基础设施故障"),
    ),
    DomainRule(
        name="security_attack",
        triggers=("黑客", "入侵", "安全事件", "漏洞", "泄露",
                  "ddos", "sql注入", "暴力破解", "被盗"),
        boosts=(("sop-005", 0.50),),
        expansions=("信息安全", "安全事件", "入侵检测", "WAF", "IDS",
                    "SIEM", "DDoS攻击", "数据泄露", "应急响应"),
    ),
    DomainRule(
        name="data_platform",
        triggers=("数据管道", "etl", "spark", "数仓", "数据延迟", "数据质量"),
        boosts=(("sop-006", 0.35),),
        expansions=("数据平台", "ETL失败", "Spark集群", "调度任务"),
    ),
    DomainRule(
        name="mobile",
        triggers=("app", "崩溃", "闪退", "热修复", "推送服务", "移动端",
                  "ios", "android"),
        boosts=(("sop-007", 0.35),),
        expansions=("移动端", "App崩溃率", "热修复", "推送服务", "灰度发布"),
    ),
    DomainRule(
        name="ai_model",
        triggers=("机器学习", "推荐结果", "模型推理", "质量下降",
                  "效果下降", "推理延迟", "搜索排序", "ab实验"),
        boosts=(("sop-008", 0.45),),
        expansions=("AI算法", "推荐系统", "模型推理延迟", "模型效果下降",
                    "特征服务", "数据漂移", "GPU集群"),
    ),
    DomainRule(
        name="qa_release",
        triggers=("自动化测试", "发版", "回归测试", "测试环境", "qa", "质量门禁"),
        boosts=(("sop-009", 0.35),),
        expansions=("QA", "测试环境", "自动化测试", "发版卡点", "回归测试"),
    ),
    DomainRule(
        name="network_cdn",
        triggers=("cdn", "dns", "解析", "回源", "ddos防护",
                  "负载均衡", "专线", "bgp"),
        boosts=(("sop-010", 0.40), ("sop-003", 0.10)),
        expansions=("网络CDN", "CDN节点故障", "DNS异常", "DDoS防护",
                    "负载均衡", "回源率"),
    ),
    DomainRule(
        name="p0_response",
        triggers=("p0", "最高级故障", "严重故障", "故障响应流程",
                  "响应流程", "升级流程", "战争室", "war room"),
        boosts=(("sop-001", 0.20), ("sop-004", 0.20),
                ("sop-005", 0.15), ("sop-010", 0.15)),
        expansions=("P0", "故障响应", "升级流程", "War Room",
                    "技术负责人", "影响范围"),
    ),
)


def match_rules(query: str) -> list[DomainRule]:
    qn = normalize(query)
    return [
        r for r in DOMAIN_RULES
        if any(normalize(t) in qn for t in r.triggers)
    ]


def expand_query(query: str) -> tuple[str, dict[str, float]]:
    """Return (expanded_query, doc_boost_map).

    expanded_query: original + appended expansion phrases (used to enrich
                    keyword and embedding inputs).
    doc_boost_map: doc_id -> additive RRF-equivalent boost.
    """
    rules = match_rules(query)
    if not rules:
        return query, {}
    expansions: list[str] = []
    boosts: dict[str, float] = {}
    for r in rules:
        expansions.extend(r.expansions)
        for doc_id, b in r.boosts:
            boosts[doc_id] = boosts.get(doc_id, 0.0) + b
    expanded = query if not expansions else f"{query}  ({' '.join(expansions)})"
    return expanded, boosts
