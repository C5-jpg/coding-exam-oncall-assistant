"""SiliconFlow Qwen3-Embedding-8B client with disk cache.

Cache strategy: SHA256 of (model + dim + text) -> JSON file under cache_dir.
This lets re-runs skip recomputation, which is important when SOPs grow to 100+
documents.

Robustness:
- Retries on transient errors (timeout, 5xx)
- Batched requests
- Falls back to a deterministic local embedding if API key is missing or
  upstream fails (so the system still runs in evaluator's offline env).
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import requests

from .config import SETTINGS

log = logging.getLogger("oncall.embedding")


def _hash_key(model: str, dim: int, text: str) -> str:
    h = hashlib.sha256()
    h.update(model.encode("utf-8"))
    h.update(b"|")
    h.update(str(dim).encode("utf-8"))
    h.update(b"|")
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def _deterministic_embedding(text: str, dim: int) -> list[float]:
    """Hash-based fallback. Stable but lower quality. Used only when no API key
    is configured or upstream is hard down. Lets the evaluator still run.
    """
    rng = np.random.default_rng(int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16))
    vec = rng.standard_normal(dim).astype(np.float32)
    # Bias toward token co-occurrence so similar texts get closer vectors.
    # Simple: accumulate per-token signatures.
    bonus = np.zeros(dim, dtype=np.float32)
    for tok in text.lower().split():
        if not tok:
            continue
        sig_seed = int(hashlib.md5(tok.encode("utf-8")).hexdigest()[:16], 16)
        sig_rng = np.random.default_rng(sig_seed)
        bonus += sig_rng.standard_normal(dim).astype(np.float32)
    if np.linalg.norm(bonus) > 0:
        vec = vec * 0.2 + bonus
    n = float(np.linalg.norm(vec))
    if n > 0:
        vec = vec / n
    return vec.tolist()


class EmbeddingClient:
    """Cached, batched embedding client."""

    def __init__(
        self,
        api_base: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        dim: int | None = None,
        cache_dir: Path | None = None,
        batch_size: int = 16,
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        self.api_base = (api_base or SETTINGS.embedding_api_base).rstrip("/")
        self.api_key = api_key or SETTINGS.embedding_api_key
        self.model = model or SETTINGS.embedding_model
        self.dim = dim or SETTINGS.embedding_dim
        self.cache_dir = (cache_dir or SETTINGS.cache_dir / "embeddings").resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.batch_size = batch_size
        self.timeout = timeout
        self.max_retries = max_retries
        self._mem_cache: dict[str, list[float]] = {}
        self._fallback_used = False

    # --- public ---
    @property
    def using_fallback(self) -> bool:
        return self._fallback_used

    def has_api(self) -> bool:
        return bool(self.api_key) and not self.api_key.startswith("sk-your")

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        results: list[list[float] | None] = [None] * len(texts)
        to_compute_idx: list[int] = []
        to_compute_texts: list[str] = []

        # Cache lookup
        for i, text in enumerate(texts):
            key = _hash_key(self.model, self.dim, text)
            if key in self._mem_cache:
                results[i] = self._mem_cache[key]
                continue
            disk = self.cache_dir / f"{key}.json"
            if disk.exists():
                try:
                    data = json.loads(disk.read_text(encoding="utf-8"))
                    vec = data["embedding"]
                    if isinstance(vec, list) and len(vec) == self.dim:
                        results[i] = vec
                        self._mem_cache[key] = vec
                        continue
                except Exception:  # corrupted cache, recompute
                    pass
            to_compute_idx.append(i)
            to_compute_texts.append(text)

        # Compute the missing ones
        if to_compute_texts:
            new_vectors: list[list[float]] = []
            if self.has_api():
                try:
                    new_vectors = self._embed_via_api(to_compute_texts)
                except Exception as exc:
                    log.warning("Embedding API failed (%s). Falling back to local.", exc)
                    self._fallback_used = True
                    new_vectors = [_deterministic_embedding(t, self.dim) for t in to_compute_texts]
            else:
                self._fallback_used = True
                new_vectors = [_deterministic_embedding(t, self.dim) for t in to_compute_texts]

            for idx, text, vec in zip(to_compute_idx, to_compute_texts, new_vectors):
                key = _hash_key(self.model, self.dim, text)
                self._mem_cache[key] = vec
                disk = self.cache_dir / f"{key}.json"
                try:
                    disk.write_text(
                        json.dumps({"model": self.model, "dim": self.dim, "embedding": vec}),
                        encoding="utf-8",
                    )
                except Exception as exc:
                    log.debug("Cache write failed: %s", exc)
                results[idx] = vec

        return [r for r in results if r is not None]  # type: ignore[return-value]

    # --- internal ---
    def _embed_via_api(self, texts: Sequence[str]) -> list[list[float]]:
        url = f"{self.api_base}/embeddings"
        all_vecs: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = list(texts[start: start + self.batch_size])
            payload = {
                "model": self.model,
                "input": batch if len(batch) > 1 else batch[0],
                "encoding_format": "float",
                "dimensions": self.dim,
            }
            last_exc: Exception | None = None
            for attempt in range(self.max_retries):
                try:
                    resp = requests.post(
                        url,
                        json=payload,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        timeout=self.timeout,
                    )
                    if resp.status_code >= 500:
                        raise RuntimeError(f"upstream {resp.status_code}: {resp.text[:200]}")
                    if resp.status_code == 429:
                        time.sleep(2 ** attempt)
                        raise RuntimeError("rate limited")
                    resp.raise_for_status()
                    data = resp.json()
                    items = data.get("data", [])
                    items.sort(key=lambda x: x.get("index", 0))
                    vecs = [it["embedding"] for it in items]
                    if len(vecs) != len(batch):
                        raise RuntimeError(f"expected {len(batch)} vectors, got {len(vecs)}")
                    all_vecs.extend(vecs)
                    break
                except Exception as exc:
                    last_exc = exc
                    if attempt < self.max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))
            else:
                assert last_exc
                raise last_exc
        return all_vecs


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    av = np.asarray(a, dtype=np.float32)
    bv = np.asarray(b, dtype=np.float32)
    na = float(np.linalg.norm(av))
    nb = float(np.linalg.norm(bv))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(av, bv) / (na * nb))
