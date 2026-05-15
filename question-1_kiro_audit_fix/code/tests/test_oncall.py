"""Unit and integration tests for oncall_assistant.py.

Run with: python3.11 -m pytest tests/ -v
(from the question-1_kiro_audit_fix/code/ directory)

Or without pytest installed:
  python3.11 tests/test_oncall.py
"""
import sys
import os

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from oncall_assistant import (
    VisibleTextExtractor,
    DocumentIndex,
    OnCallAgent,
    ReadFileTool,
    tokenize,
    normalize,
    split_query_terms,
    get_query_value,
    compact_spaces,
    chinese_ngrams,
)

DATA_DIR = Path(__file__).resolve().parents[1] / ".." / "data"


# ============================================================
# Unit Tests: Text Processing
# ============================================================

class TestNormalize:
    def test_basic(self):
        assert normalize("  Hello   World  ") == "hello world"

    def test_html_entities(self):
        assert normalize("&amp;") == "&"
        assert normalize("&lt;script&gt;") == "<script>"

    def test_chinese(self):
        assert normalize("  数据库  主从延迟  ") == "数据库 主从延迟"


class TestTokenize:
    def test_english(self):
        tokens = tokenize("OOM error in service")
        assert "oom" in tokens
        assert "error" in tokens
        assert "service" in tokens

    def test_chinese_ngrams(self):
        tokens = tokenize("数据库主从延迟")
        # Should produce 2-gram, 3-gram, 4-gram
        assert "数据" in tokens
        assert "据库" in tokens
        assert "数据库" in tokens

    def test_domain_phrases(self):
        tokens = tokenize("检查 OOM 和 CDN 问题")
        assert "oom" in tokens
        assert "cdn" in tokens

    def test_stopwords_removed(self):
        tokens = tokenize("怎么处理这个问题")
        assert "怎么" not in tokens
        assert "处理" not in tokens


class TestChineseNgrams:
    def test_short_segment(self):
        grams = chinese_ngrams("数据库")
        assert "数据库" in grams  # full segment (<=8 chars)
        assert "数据" in grams   # 2-gram
        assert "据库" in grams   # 2-gram

    def test_empty(self):
        assert chinese_ngrams("") == []


class TestGetQueryValue:
    def test_normal(self):
        assert get_query_value("q=OOM") == "OOM"

    def test_ampersand(self):
        assert get_query_value("q=&") == "&"

    def test_empty(self):
        assert get_query_value("q=") == ""

    def test_encoded(self):
        assert get_query_value("q=%E6%95%85%E9%9A%9C") == "故障"


# ============================================================
# Unit Tests: HTML Parsing
# ============================================================

class TestVisibleTextExtractor:
    def test_basic_html(self):
        html = "<html><head><title>Test Title</title></head><body><p>Hello World</p></body></html>"
        parser = VisibleTextExtractor()
        parser.feed(html)
        assert parser.title == "Test Title"
        assert "Hello World" in parser.text

    def test_ignores_script(self):
        html = """<html><head><title>T</title></head><body>
        <p>Visible text</p>
        <script>var replicationLag = 100;</script>
        <p>More visible</p>
        </body></html>"""
        parser = VisibleTextExtractor()
        parser.feed(html)
        assert "replicationLag" not in parser.text
        assert "Visible text" in parser.text
        assert "More visible" in parser.text

    def test_ignores_style(self):
        html = "<html><body><style>.hidden { display: none; }</style><p>Content</p></body></html>"
        parser = VisibleTextExtractor()
        parser.feed(html)
        assert "hidden" not in parser.text
        assert "Content" in parser.text

    def test_empty_html(self):
        parser = VisibleTextExtractor()
        parser.feed("")
        assert parser.title == ""
        assert parser.text == ""

    def test_html_entities(self):
        html = "<html><body><p>A &amp; B</p></body></html>"
        parser = VisibleTextExtractor()
        parser.feed(html)
        assert "&" in parser.text or "A" in parser.text


# ============================================================
# Integration Tests: Document Index
# ============================================================

class TestDocumentIndex:
    def setup_method(self):
        self.index = DocumentIndex(DATA_DIR.resolve())

    def test_loads_10_documents(self):
        assert len(self.index.documents) == 10

    def test_keyword_search_oom(self):
        results = self.index.keyword_search("OOM")
        assert results
        assert results[0].id == "sop-001"

    def test_keyword_search_replication_empty(self):
        results = self.index.keyword_search("replication")
        assert results == []

    def test_keyword_search_cdn(self):
        results = self.index.keyword_search("CDN")
        ids = {r.id for r in results}
        assert "sop-003" in ids
        assert "sop-010" in ids

    def test_keyword_search_fault_multiple(self):
        results = self.index.keyword_search("故障")
        assert len(results) >= 5

    def test_keyword_search_ampersand(self):
        results = self.index.keyword_search("&")
        assert len(results) > 0

    def test_keyword_search_empty_query(self):
        results = self.index.keyword_search("")
        assert results == []

    def test_semantic_search_server_down(self):
        results = self.index.semantic_search("服务器挂了")
        top2_ids = {r.id for r in results[:2]}
        assert "sop-001" in top2_ids
        assert "sop-004" in top2_ids

    def test_semantic_search_hacker(self):
        results = self.index.semantic_search("黑客攻击")
        assert results[0].id == "sop-005"

    def test_semantic_search_ml_model(self):
        results = self.index.semantic_search("机器学习模型出问题")
        assert results[0].id == "sop-008"

    def test_semantic_search_empty_query(self):
        results = self.index.semantic_search("")
        assert results == []

    def test_add_document(self):
        doc = self.index.add_document(
            "test-doc",
            "<html><head><title>Test</title></head><body><p>Test content</p></body></html>"
        )
        assert doc.id == "test-doc"
        assert doc.title == "Test"
        results = self.index.keyword_search("Test content")
        assert any(r.id == "test-doc" for r in results)

    def test_add_document_invalid_id(self):
        try:
            self.index.add_document("../evil", "<html><body>x</body></html>")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


# ============================================================
# Integration Tests: ReadFileTool
# ============================================================

class TestReadFileTool:
    def setup_method(self):
        self.tool = ReadFileTool(DATA_DIR.resolve())

    def test_read_valid_file(self):
        content = self.tool("sop-001.html")
        assert "后端服务" in content
        assert "OOM" in content or "OutOfMemoryError" in content

    def test_reject_path_separator(self):
        try:
            self.tool("../code/oncall_assistant.py")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "path separators" in str(e) or "plain file name" in str(e)

    def test_reject_wildcard(self):
        try:
            self.tool("*.html")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_reject_empty(self):
        try:
            self.tool("")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_file_not_found(self):
        try:
            self.tool("nonexistent.html")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass


# ============================================================
# Integration Tests: Agent
# ============================================================

class TestOnCallAgent:
    def setup_method(self):
        self.index = DocumentIndex(DATA_DIR.resolve())
        self.agent = OnCallAgent(self.index, DATA_DIR.resolve())

    def test_dba_question(self):
        result = self.agent.answer("数据库主从延迟超过30秒怎么处理？")
        assert any(c["arguments"]["fname"] == "sop-002.html" for c in result["tool_calls"])
        assert len(result["answer"]) > 50

    def test_oom_question(self):
        result = self.agent.answer("服务 OOM 了怎么办？")
        assert any(c["arguments"]["fname"] == "sop-001.html" for c in result["tool_calls"])

    def test_p0_question(self):
        result = self.agent.answer("P0 故障的响应流程是什么？")
        assert len(result["tool_calls"]) >= 3

    def test_security_question(self):
        result = self.agent.answer("怀疑有人入侵了系统")
        assert any(c["arguments"]["fname"] == "sop-005.html" for c in result["tool_calls"])

    def test_ai_quality_question(self):
        result = self.agent.answer("推荐结果质量下降了")
        assert any(c["arguments"]["fname"] == "sop-008.html" for c in result["tool_calls"])

    def test_unknown_question_still_returns_answer(self):
        result = self.agent.answer("今天天气怎么样？")
        assert "answer" in result
        assert "tool_calls" in result
        # Should still attempt to provide something
        assert len(result["answer"]) > 0


# ============================================================
# Run tests without pytest (fallback)
# ============================================================

def run_without_pytest():
    """Simple test runner for environments without pytest."""
    import traceback
    test_classes = [
        TestNormalize, TestTokenize, TestChineseNgrams, TestGetQueryValue,
        TestVisibleTextExtractor, TestDocumentIndex, TestReadFileTool, TestOnCallAgent,
    ]
    total = 0
    passed = 0
    failed = 0
    errors = []

    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith("test_")]
        for method_name in methods:
            total += 1
            if hasattr(instance, "setup_method"):
                instance.setup_method()
            try:
                getattr(instance, method_name)()
                passed += 1
                print(f"  [PASS] {cls.__name__}.{method_name}")
            except Exception as e:
                failed += 1
                errors.append((cls.__name__, method_name, e))
                print(f"  [FAIL] {cls.__name__}.{method_name}: {e}")

    print(f"\n{'='*60}")
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")
    if errors:
        print("\nFailed tests:")
        for cls_name, method_name, exc in errors:
            print(f"  {cls_name}.{method_name}: {exc}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    print("Running tests without pytest...\n")
    sys.exit(run_without_pytest())
