"""Centralised configuration loaded from environment / .env file.

Secrets MUST come from environment variables. Never hard-code keys here.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Load .env if present (search project root)
try:
    from dotenv import load_dotenv

    _CODE_DIR = Path(__file__).resolve().parents[1]      # .../code
    _PROJECT_ROOT = _CODE_DIR.parent                      # .../question-1_kiro_audit_fix
    _ENV_FILE = _PROJECT_ROOT / ".env"
    if _ENV_FILE.exists():
        load_dotenv(_ENV_FILE)
except ImportError:  # python-dotenv optional
    _CODE_DIR = Path(__file__).resolve().parents[1]
    _PROJECT_ROOT = _CODE_DIR.parent


def _get(key: str, default: str = "") -> str:
    return (os.environ.get(key) or default).strip()


def _get_int(key: str, default: int) -> int:
    raw = _get(key)
    return int(raw) if raw else default


@dataclass
class Settings:
    project_root: Path = field(default_factory=lambda: _PROJECT_ROOT)
    code_dir: Path = field(default_factory=lambda: _CODE_DIR)
    data_dir: Path = field(
        default_factory=lambda: Path(_get("DATA_DIR") or _PROJECT_ROOT / "data")
    )
    cache_dir: Path = field(
        default_factory=lambda: Path(_get("CACHE_DIR") or _PROJECT_ROOT / ".cache")
    )

    # Embedding
    embedding_api_base: str = field(
        default_factory=lambda: _get("EMBEDDING_API_BASE", "https://api.siliconflow.cn/v1")
    )
    embedding_api_key: str = field(default_factory=lambda: _get("EMBEDDING_API_KEY"))
    embedding_model: str = field(
        default_factory=lambda: _get("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-8B")
    )
    embedding_dim: int = field(default_factory=lambda: _get_int("EMBEDDING_DIM", 1024))

    # LLM
    llm_api_base: str = field(
        default_factory=lambda: _get(
            "LLM_API_BASE", "https://open.bigmodel.cn/api/coding/paas/v4"
        )
    )
    llm_api_key: str = field(default_factory=lambda: _get("LLM_API_KEY"))
    llm_model: str = field(default_factory=lambda: _get("LLM_MODEL", "glm-4.6"))

    # Server
    http_host: str = field(default_factory=lambda: _get("HTTP_HOST", "127.0.0.1"))
    http_port: int = field(default_factory=lambda: _get_int("HTTP_PORT", 8000))
    gradio_host: str = field(default_factory=lambda: _get("GRADIO_HOST", "127.0.0.1"))
    gradio_port: int = field(default_factory=lambda: _get_int("GRADIO_PORT", 7860))

    def has_embedding_api(self) -> bool:
        return bool(self.embedding_api_key) and self.embedding_api_key != "sk-your-siliconflow-key"

    def has_llm_api(self) -> bool:
        return bool(self.llm_api_key) and self.llm_api_key != "your-zhipu-coding-key"

    def ensure_dirs(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)


SETTINGS = Settings()
SETTINGS.ensure_dirs()
