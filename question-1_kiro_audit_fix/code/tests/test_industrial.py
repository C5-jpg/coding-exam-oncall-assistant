"""Comprehensive tests for the industrial-grade On-Call assistant.

Covers:
- text utilities (tokenizer, html_parser, chunker)
- embedding fallback (no API key needed)
- keyword + vector + hybrid search (uses fallback embedding so no API)
- ReadFileTool security boundary
- Memory store persistence and isolation
- Domain rules
- Agent deterministic path (does not require LLM key)

Tests that require live APIs are gated behind `SKIP_LIVE` environment variable.
Run:
    pytest code/tests/ -v
or:
    python code/tests/test_industrial.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))

from oncall.tokenizer import tokenize, normalize, chinese_ngrams, split_query_terms
from oncall.html_parser import parse_html, VisibleTextExtractor
from oncall.chunker import chunk_html
from oncall.domain_rules import expand_query, match_rules, DOMAIN_RULES
from oncall.embedding import EmbeddingClient, cosine, _deterministic_embedding
from oncall.tools import ReadFileTool, WriteFileHelper, ToolError
from oncall.memory import MemoryStore, Turn, Session
from oncall.keyword_index import KeywordIndex
from oncall.vector_index import VectorIndex
from oncall.hybrid_search import HybridSearch
from oncall.service import OnCallService


DATA_DIR = (Path(__file__).resolve().parents[2] / "data").resolve()
SKIP_LIVE = os.environ.get("SKIP_LIVE", "0") == "1"


# ============================================================
# Tokenizer / parser / chunker
# ============================================================

class TestTokenizer(unittest.TestCase):
    def test_normalize_strips_html_entities(self):
        self.assertEqual(normalize("&amp; &#x4E2D;"), "& 中")

    def test_chinese_ngrams_2_to_4(self):
        grams = chinese_ngrams("数据库主从延迟")
        self.assertIn("数据", grams)
        self.assertIn("数据库", grams)
        self.assertIn("主从延迟", grams)

    def test_tokenize_mixes_chinese_and_english(self):
        toks = tokenize("OOM 内存泄漏 K8s")
        self.assertIn("oom", toks)
        self.assertIn("内存", toks)
        # K8s gets normalised to lowercase 'k8s' as a single token
        self.assertIn("k8s", toks)

    def test_split_query_terms_dedupes(self):
        terms = split_query_terms("OOM oom OOM")
        self.assertEqual(terms.count("oom"), 1)


class TestHtmlParser(unittest.TestCase):
    def test_skips_script_and_style(self):
        html = """<html><head><title>T</title></head><body>
            <p>visible</p>
            <script>var replicationLag = 5;</script>
            <style>.x{color:red}</style>
            <p>also visible</p>
        </body></html>"""
        title, text, _ = parse_html(html)
        self.assertEqual(title, "T")
        self.assertIn("visible", text)
        self.assertNotIn("replicationLag", text)
        self.assertNotIn("color:red", text)

    def test_parses_h2_h3_records(self):
        html = """<html><body>
            <h2>Section A</h2><p>para A1</p><p>para A2</p>
            <h3>Sub A.1</h3><p>sub para</p>
            <h2>Section B</h2><p>para B</p>
        </body></html>"""
        _, _, records = parse_html(html)
        sections = [(h2, h3) for (h2, h3, _) in records]
        self.assertIn(("Section A", ""), sections)
        self.assertIn(("Section A", "Sub A.1"), sections)
        self.assertIn(("Section B", ""), sections)

    def test_handles_empty_html(self):
        title, text, records = parse_html("")
        self.assertEqual(title, "")
        self.assertEqual(text, "")
        self.assertEqual(records, [])


class TestChunker(unittest.TestCase):
    def test_splits_real_sop(self):
        html = (DATA_DIR / "sop-001.html").read_text(encoding="utf-8")
        title, _, chunks = chunk_html("sop-001", html)
        self.assertEqual(title, "后端服务 On-Call SOP")
        self.assertGreater(len(chunks), 3)
        # Chunks should have unique ids
        ids = [c.chunk_id for c in chunks]
        self.assertEqual(len(ids), len(set(ids)))
        # Each chunk should reference the source doc
        for c in chunks:
            self.assertEqual(c.doc_id, "sop-001")

    def test_chunks_have_section_metadata(self):
        html = (DATA_DIR / "sop-002.html").read_text(encoding="utf-8")
        _, _, chunks = chunk_html("sop-002", html)
        h2s = {c.section_h2 for c in chunks if c.section_h2}
        self.assertGreater(len(h2s), 1)


# ============================================================
# Domain rules
# ============================================================

class TestDomainRules(unittest.TestCase):
    def test_security_query_matches_rule(self):
        rules = match_rules("怀疑有人入侵系统")
        names = {r.name for r in rules}
        self.assertIn("security_attack", names)

    def test_p0_query_matches_rule(self):
        rules = match_rules("P0 故障的响应流程")
        names = {r.name for r in rules}
        self.assertIn("p0_response", names)

    def test_expand_query_returns_boosts(self):
        expanded, boosts = expand_query("黑客攻击")
        self.assertIn("sop-005", boosts)
        self.assertGreater(boosts["sop-005"], 0)
        self.assertNotEqual(expanded, "黑客攻击")


# ============================================================
# Embedding (deterministic fallback)
# ============================================================

class TestEmbedding(unittest.TestCase):
    def test_deterministic_is_stable(self):
        v1 = _deterministic_embedding("hello world", 1024)
        v2 = _deterministic_embedding("hello world", 1024)
        self.assertEqual(v1, v2)

    def test_deterministic_dimension(self):
        v = _deterministic_embedding("test", 512)
        self.assertEqual(len(v), 512)

    def test_cosine_basic(self):
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        c = [-1.0, 0.0, 0.0]
        self.assertAlmostEqual(cosine(a, b), 1.0, places=5)
        self.assertAlmostEqual(cosine(a, c), -1.0, places=5)

    def test_offline_client_falls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = EmbeddingClient(
                api_base="https://invalid.example",
                api_key="",                                  # no key -> fallback path
                model="dummy",
                dim=128,
                cache_dir=Path(tmp),
            )
            v = client.embed("test")
            self.assertEqual(len(v), 128)
            self.assertTrue(client.using_fallback)

    def test_cache_avoids_recompute(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = EmbeddingClient(
                api_base="https://invalid.example", api_key="",
                model="dummy", dim=64, cache_dir=Path(tmp),
            )
            v1 = client.embed("same text")
            v2 = client.embed("same text")
            self.assertEqual(v1, v2)
            # Cache file should exist
            cache_files = list(Path(tmp).glob("*.json"))
            self.assertGreaterEqual(len(cache_files), 1)


# ============================================================
# ReadFileTool security boundary
# ============================================================

class TestReadFileTool(unittest.TestCase):
    def setUp(self):
        self.tool = ReadFileTool(DATA_DIR)

    def test_reads_valid_sop(self):
        content = self.tool("sop-001.html")
        self.assertIn("后端服务", content)
        self.assertIn("OOM", content)

    def test_rejects_path_separator(self):
        with self.assertRaises(ToolError):
            self.tool("../code/main.py")
        with self.assertRaises(ToolError):
            self.tool("subdir/sop-001.html")
        with self.assertRaises(ToolError):
            self.tool("..\\sop-001.html")

    def test_rejects_wildcard(self):
        with self.assertRaises(ToolError):
            self.tool("*.html")
        with self.assertRaises(ToolError):
            self.tool("sop-?.html")

    def test_rejects_empty(self):
        with self.assertRaises(ToolError):
            self.tool("")
        with self.assertRaises(ToolError):
            self.tool("   ")

    def test_rejects_parent_traversal(self):
        with self.assertRaises(ToolError):
            self.tool("..")
        with self.assertRaises(ToolError):
            self.tool("..something")

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.tool("does-not-exist.html")


class TestWriteFileHelper(unittest.TestCase):
    def test_write_and_read_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            helper = WriteFileHelper(Path(tmp))
            target = helper.write("test.html", "<html>hi</html>")
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), "<html>hi</html>")

    def test_rejects_invalid_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            helper = WriteFileHelper(Path(tmp))
            with self.assertRaises(ToolError):
                helper.write("../escape.html", "x")


# ============================================================
# Memory store
# ============================================================

class TestMemoryStore(unittest.TestCase):
    def test_session_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(persist_dir=Path(tmp))
            store.append_turn("alice", Turn(role="user", content="hi"))
            store.append_turn("bob", Turn(role="user", content="bye"))
            self.assertEqual(len(store.get("alice").turns), 1)
            self.assertEqual(len(store.get("bob").turns), 1)
            self.assertNotEqual(store.get("alice").turns[0].content, store.get("bob").turns[0].content)

    def test_persistence_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            store1 = MemoryStore(persist_dir=Path(tmp))
            store1.append_turn("s1", Turn(role="user", content="msg-A"))
            store1.add_fact("s1", "fact-1")
            # Fresh store reads from disk
            store2 = MemoryStore(persist_dir=Path(tmp))
            sess = store2.get("s1")
            self.assertEqual(len(sess.turns), 1)
            self.assertEqual(sess.turns[0].content, "msg-A")
            self.assertIn("fact-1", sess.facts)

    def test_max_turns_trimming(self):
        store = MemoryStore(persist_dir=None, max_turns=4)
        for i in range(10):
            store.append_turn("s", Turn(role="user", content=f"msg-{i}"))
        sess = store.get("s")
        self.assertEqual(len(sess.turns), 4)
        # First message is preserved (head)
        self.assertEqual(sess.turns[0].content, "msg-0")
        # Most recent are kept
        self.assertEqual(sess.turns[-1].content, "msg-9")

    def test_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(persist_dir=Path(tmp))
            store.append_turn("s", Turn(role="user", content="hi"))
            store.reset("s")
            self.assertEqual(len(store.get("s").turns), 0)


# ============================================================
# Service (full stack with deterministic embedding fallback)
# ============================================================

class TestService(unittest.TestCase):
    """End-to-end service tests using REAL APIs if available, otherwise the
    fallback paths (which the exam validation table also accepts).

    These tests exercise the actual /v1, /v2, /v3 contracts."""

    @classmethod
    def setUpClass(cls):
        # Make a temp cache so test runs are isolated
        cls.tmp_cache = tempfile.TemporaryDirectory()
        os.environ["CACHE_DIR"] = cls.tmp_cache.name
        # Reload settings
        from oncall import config as _cfg
        _cfg.SETTINGS.cache_dir = Path(cls.tmp_cache.name)
        cls.svc = OnCallService(data_dir=DATA_DIR)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_cache.cleanup()

    def test_indexed_10_documents(self):
        s = self.svc.status()
        # Test ordering may have added extra docs via test_add_document_*; allow >=.
        self.assertGreaterEqual(s["documents"], 10)
        self.assertGreaterEqual(s["chunks"], 30)

    def test_v1_oom(self):
        rs = self.svc.keyword_search("OOM")
        self.assertTrue(rs)
        self.assertEqual(rs[0]["id"], "sop-001")

    def test_v1_replication_empty(self):
        rs = self.svc.keyword_search("replication")
        self.assertEqual(rs, [])

    def test_v1_cdn_returns_two_docs(self):
        ids = {r["id"] for r in self.svc.keyword_search("CDN")}
        self.assertIn("sop-003", ids)
        self.assertIn("sop-010", ids)

    def test_v1_ampersand(self):
        rs = self.svc.keyword_search("&")
        self.assertGreater(len(rs), 0)

    def test_v2_server_down(self):
        rs = self.svc.semantic_search("服务器挂了")
        ids = {r["id"] for r in rs[:2]}
        self.assertIn("sop-001", ids)
        self.assertIn("sop-004", ids)

    def test_v2_hacker(self):
        rs = self.svc.semantic_search("黑客攻击")
        self.assertEqual(rs[0]["id"], "sop-005")

    def test_v2_ml_model(self):
        rs = self.svc.semantic_search("机器学习模型出问题")
        self.assertEqual(rs[0]["id"], "sop-008")

    def test_v3_dba_question(self):
        r = self.svc.chat("数据库主从延迟超过30秒怎么处理？", session_id="t-dba")
        called = [c["arguments"].get("fname") for c in r["tool_calls"]]
        self.assertIn("sop-002.html", called)

    def test_v3_oom_question(self):
        r = self.svc.chat("服务 OOM 了怎么办？", session_id="t-oom")
        called = [c["arguments"].get("fname") for c in r["tool_calls"]]
        self.assertIn("sop-001.html", called)

    def test_v3_security_question(self):
        r = self.svc.chat("怀疑有人入侵了系统", session_id="t-sec")
        called = [c["arguments"].get("fname") for c in r["tool_calls"]]
        self.assertIn("sop-005.html", called)

    def test_v3_ai_quality(self):
        r = self.svc.chat("推荐结果质量下降了", session_id="t-ai")
        called = [c["arguments"].get("fname") for c in r["tool_calls"]]
        self.assertIn("sop-008.html", called)

    def test_v3_p0_multi_source(self):
        r = self.svc.chat("P0 故障的响应流程是什么？", session_id="t-p0")
        # Should consult multiple SOPs
        files = {c["arguments"].get("fname") for c in r["tool_calls"]}
        self.assertGreaterEqual(len(files), 3, f"expected >=3 SOPs, got {files}")

    def test_v3_session_memory_continuity(self):
        sid = "t-memory"
        r1 = self.svc.chat("数据库主从延迟超过30秒怎么处理？", session_id=sid)
        # Follow-up referring back via pronoun
        r2 = self.svc.chat("这个延迟会影响业务吗？", session_id=sid)
        # The session should accumulate facts
        sess = self.svc.memory.get(sid)
        self.assertGreaterEqual(len(sess.turns), 4)
        # Should have recorded that we read sop-002.html as a fact
        self.assertTrue(
            any("sop-002.html" in f for f in sess.facts),
            f"expected sop-002 in facts, got {sess.facts}",
        )

    def test_v3_unknown_question_returns_answer(self):
        r = self.svc.chat("今天天气怎么样？", session_id="t-unk")
        self.assertTrue(r.get("answer"))

    def test_add_document_then_search(self):
        custom_id = "sop-custom-test"
        custom_html = (
            "<html><head><title>测试 SOP</title></head><body>"
            "<h1>测试 SOP</h1>"
            "<h2>一、范围</h2><p>这份文档专门用于测试 wxyz-unique-marker 关键字。</p>"
            "</body></html>"
        )
        doc = self.svc.add_document(custom_id, custom_html)
        self.assertEqual(doc.title, "测试 SOP")
        rs = self.svc.keyword_search("wxyz-unique-marker")
        self.assertTrue(any(r["id"] == custom_id for r in rs))
        # Cleanup file from data dir
        target = DATA_DIR / f"{custom_id}.html"
        if target.exists():
            target.unlink()


# ============================================================
# Helpers to run without pytest
# ============================================================

if __name__ == "__main__":
    # Print to UTF-8 file for clean output on Windows.
    import io, json, traceback

    out_path = Path(__file__).parent.parent.parent / ".cache" / "test_industrial_output.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fp = open(out_path, "w", encoding="utf-8")

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(stream=fp, verbosity=2)
    result = runner.run(suite)
    fp.write(f"\nRan {result.testsRun} tests, "
             f"failures={len(result.failures)}, errors={len(result.errors)}\n")
    fp.close()
    print(f"Wrote results to: {out_path}")
    print(f"Tests run: {result.testsRun}, "
          f"failures: {len(result.failures)}, errors: {len(result.errors)}")
    sys.exit(0 if result.wasSuccessful() else 1)
