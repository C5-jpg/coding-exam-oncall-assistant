"""On-Call SOP Assistant package.

Industrial-grade implementation:
- Phase 1: Keyword search (BM25-ish with Chinese n-grams)
- Phase 2: Hybrid semantic search (Qwen3-Embedding-8B + keyword fusion via RRF)
- Phase 3: GLM-4.6 LLM Agent with `readFile` tool and conversation memory
"""
__version__ = "2.0.0"
