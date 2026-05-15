"""End-to-end HTTP smoke test against a running server.

Writes results to .cache/smoke_http_output.txt as UTF-8.
"""
import io
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8765")

OUT = Path(__file__).resolve().parents[1] / ".cache" / "smoke_http_output.txt"
OUT.parent.mkdir(parents=True, exist_ok=True)
fp = open(OUT, "w", encoding="utf-8")


def log(msg=""):
    fp.write(msg + "\n")
    fp.flush()


def get_json(path):
    r = urllib.request.urlopen(BASE + path, timeout=60)
    return json.loads(r.read())


def post_json(path, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=120)
    return json.loads(r.read())


passed = 0
failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        log(f"  [PASS] {name}")
    else:
        failed += 1
        log(f"  [FAIL] {name}  {detail}")


log("=" * 60)
log(f"On-Call Assistant - HTTP smoke test  (base: {BASE})")
log("=" * 60)

# Health
data = get_json("/health")
check("health -> 10 documents", data.get("documents") == 10, str(data))

# v1
log("\n--- Phase 1 (keyword) ---")
data = get_json("/v1/search?q=OOM")
check("v1 OOM -> sop-001 first", data["results"] and data["results"][0]["id"] == "sop-001")

data = get_json("/v1/search?q=" + urllib.parse.quote("故障"))
check("v1 故障 -> >=5", len(data["results"]) >= 5)

data = get_json("/v1/search?q=replication")
check("v1 replication -> empty", data["results"] == [])

data = get_json("/v1/search?q=CDN")
ids = {r["id"] for r in data["results"]}
check("v1 CDN -> sop-003 + sop-010", "sop-003" in ids and "sop-010" in ids)

data = get_json("/v1/search?q=%26")
check("v1 & -> non-empty", len(data["results"]) > 0)

# v2
log("\n--- Phase 2 (semantic + hybrid) ---")
data = get_json("/v2/search?q=" + urllib.parse.quote("服务器挂了"))
top2 = {r["id"] for r in data["results"][:2]}
check("v2 服务器挂了 -> sop-001 + sop-004 in top-2", "sop-001" in top2 and "sop-004" in top2, str(top2))

data = get_json("/v2/search?q=" + urllib.parse.quote("黑客攻击"))
check("v2 黑客攻击 -> sop-005 first", data["results"] and data["results"][0]["id"] == "sop-005")

data = get_json("/v2/search?q=" + urllib.parse.quote("机器学习模型出问题"))
check("v2 机器学习模型出问题 -> sop-008 first", data["results"] and data["results"][0]["id"] == "sop-008")

# v3
log("\n--- Phase 3 (Agent) ---")
sid = "smoke-session"
r = post_json("/v3/chat", {"message": "数据库主从延迟超过30秒怎么处理？", "session_id": sid})
called = [c["arguments"]["fname"] for c in r["tool_calls"]]
check("v3 DBA -> readFile(sop-002)", "sop-002.html" in called, str(called))
log(f"      LLM used: {r['used_llm']}  · tool_calls: {len(r['tool_calls'])}")

r = post_json("/v3/chat", {"message": "服务 OOM 了怎么办？", "session_id": "smoke-oom"})
check("v3 OOM -> readFile(sop-001)",
      any(c["arguments"]["fname"] == "sop-001.html" for c in r["tool_calls"]))

r = post_json("/v3/chat", {"message": "P0 故障的响应流程是什么？", "session_id": "smoke-p0"})
check("v3 P0 -> >=3 SOPs", len({c["arguments"]["fname"] for c in r["tool_calls"]}) >= 3,
      str([c["arguments"]["fname"] for c in r["tool_calls"]]))

r = post_json("/v3/chat", {"message": "怀疑有人入侵了系统", "session_id": "smoke-sec"})
check("v3 security -> readFile(sop-005)",
      any(c["arguments"]["fname"] == "sop-005.html" for c in r["tool_calls"]))

r = post_json("/v3/chat", {"message": "推荐结果质量下降了", "session_id": "smoke-ai"})
check("v3 AI -> readFile(sop-008)",
      any(c["arguments"]["fname"] == "sop-008.html" for c in r["tool_calls"]))

# Memory continuity test
log("\n--- Phase 3 memory ---")
r1 = post_json("/v3/chat", {"message": "数据库连接池耗尽怎么办？", "session_id": "smoke-mem"})
r2 = post_json("/v3/chat", {"message": "刚才那个步骤需要 DBA 配合吗？", "session_id": "smoke-mem"})
check("memory: follow-up returns answer", bool(r2.get("answer")), str(r2.get("answer", ""))[:80])

# v3 reset
post_json("/v3/reset", {"session_id": sid})
log("\n  reset session OK")

# Document upload
log("\n--- POST /v1/documents ---")
custom_id = "sop-smoke-test"
r = post_json("/v1/documents", {
    "id": custom_id,
    "html": "<html><head><title>Smoke Test SOP</title></head><body>"
            "<h1>Smoke Test SOP</h1><p>uniquetokenfoo for verification.</p></body></html>",
})
check("POST /v1/documents -> 201-style", r.get("id") == custom_id, str(r))

data = get_json("/v1/search?q=uniquetokenfoo")
check("custom doc -> searchable",
      any(item["id"] == custom_id for item in data["results"]))

log("\n" + "=" * 60)
log(f"Passed: {passed}, Failed: {failed}")
log("=" * 60)
fp.close()
print(f"Passed: {passed}, Failed: {failed}")
print(f"Output: {OUT}")
sys.exit(0 if failed == 0 else 1)
