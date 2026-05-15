#!/usr/bin/env python3
"""On-Call Assistant unified entry point.

Examples:
    # Run HTTP API + Gradio UI together (recommended)
    python main.py serve

    # Only HTTP API
    python main.py http

    # Only Gradio UI
    python main.py ui

    # Built-in smoke test (offline, no API key needed)
    python main.py self-test
"""
from __future__ import annotations

import argparse
import logging
import threading
import time
from pathlib import Path

from oncall import __version__
from oncall.config import SETTINGS
from oncall.http_server import OnCallHTTPServer, serve as http_serve
from oncall.gradio_app import launch as gradio_launch
from oncall.service import OnCallService


def _configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    # Force UTF-8 console output on Windows so emoji/CJK don't crash.
    import sys
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except Exception:
            pass
    # Also try to switch the Windows console code page to UTF-8 (65001).
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:
            pass


def cmd_serve(args: argparse.Namespace) -> int:
    service = OnCallService(data_dir=Path(args.data_dir).resolve() if args.data_dir else None)
    print("=" * 60)
    print(f"On-Call Assistant v{__version__}")
    print("=" * 60)
    for k, v in service.status().items():
        print(f"  {k:>26}: {v}")
    print("=" * 60)

    # Start HTTP API in a thread
    server = OnCallHTTPServer((args.host, args.http_port), service)
    http_thread = threading.Thread(
        target=server.serve_forever, name="http-server", daemon=True
    )
    http_thread.start()
    print(f"  HTTP API:   http://{args.host}:{args.http_port}")
    print(f"  Gradio UI:  http://{args.gradio_host}:{args.gradio_port}")
    print("=" * 60)

    # Run Gradio in main thread (Gradio likes the main thread)
    try:
        gradio_launch(host=args.gradio_host, port=args.gradio_port, service=service, share=args.share)
    finally:
        server.shutdown()
        server.server_close()
    return 0


def cmd_http(args: argparse.Namespace) -> int:
    service = OnCallService(data_dir=Path(args.data_dir).resolve() if args.data_dir else None)
    http_serve(host=args.host, port=args.http_port, service=service)
    return 0


def cmd_ui(args: argparse.Namespace) -> int:
    service = OnCallService(data_dir=Path(args.data_dir).resolve() if args.data_dir else None)
    gradio_launch(host=args.gradio_host, port=args.gradio_port, service=service, share=args.share)
    return 0


def cmd_self_test(args: argparse.Namespace) -> int:
    """Mirror the original exam validation table. Network APIs are exercised
    only if keys are configured; otherwise the deterministic fallback is used.
    """
    import json

    service = OnCallService(data_dir=Path(args.data_dir).resolve() if args.data_dir else None)
    failures = []

    def check(name: str, ok: bool) -> None:
        if ok:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            failures.append(name)

    print(f"On-Call Assistant v{__version__} - self test")
    print(f"Status: {service.status()}")

    # Phase 1
    print("\n=== Phase 1: keyword search ===")
    rs = service.keyword_search("OOM")
    check("v1 OOM -> sop-001 first", bool(rs) and rs[0]["id"] == "sop-001")
    check("v1 故障 -> >=5 results", len(service.keyword_search("故障")) >= 5)
    check("v1 replication -> empty", service.keyword_search("replication") == [])
    cdn_ids = {r["id"] for r in service.keyword_search("CDN")}
    check("v1 CDN -> sop-003 + sop-010", {"sop-003", "sop-010"}.issubset(cdn_ids))
    check("v1 & -> non-empty", bool(service.keyword_search("&")))

    # Phase 2
    print("\n=== Phase 2: semantic / hybrid search ===")
    sd = [r["id"] for r in service.semantic_search("服务器挂了")[:2]]
    check("v2 服务器挂了 -> sop-001 + sop-004 in top-2", {"sop-001", "sop-004"}.issubset(set(sd)))
    rs = service.semantic_search("黑客攻击")
    check("v2 黑客攻击 -> sop-005 first", bool(rs) and rs[0]["id"] == "sop-005")
    rs = service.semantic_search("机器学习模型出问题")
    check("v2 机器学习模型出问题 -> sop-008 first", bool(rs) and rs[0]["id"] == "sop-008")

    # Phase 3 (deterministic path used unless LLM key set; either way the
    # readFile target should match exam expectations)
    print("\n=== Phase 3: agent ===")
    r = service.chat("数据库主从延迟超过30秒怎么处理？", session_id="self-test-1")
    check(
        "v3 DBA -> readFile(sop-002.html)",
        any(c["arguments"].get("fname") == "sop-002.html" for c in r["tool_calls"]),
    )
    r = service.chat("服务 OOM 了怎么办？", session_id="self-test-2")
    check(
        "v3 OOM -> readFile(sop-001.html)",
        any(c["arguments"].get("fname") == "sop-001.html" for c in r["tool_calls"]),
    )
    r = service.chat("P0 故障的响应流程是什么？", session_id="self-test-3")
    check("v3 P0 -> >=3 SOPs read", len(r["tool_calls"]) >= 3)
    r = service.chat("怀疑有人入侵了系统", session_id="self-test-4")
    check(
        "v3 security -> readFile(sop-005.html)",
        any(c["arguments"].get("fname") == "sop-005.html" for c in r["tool_calls"]),
    )
    r = service.chat("推荐结果质量下降了", session_id="self-test-5")
    check(
        "v3 AI -> readFile(sop-008.html)",
        any(c["arguments"].get("fname") == "sop-008.html" for c in r["tool_calls"]),
    )

    print("\n=== Summary ===")
    summary = {"checks": 11, "failures": failures}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oncall", description="On-Call SOP Assistant")
    parser.add_argument("--log-level", default="INFO")
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--data-dir", default=None, help="path to SOP HTML directory")
    common.add_argument("--host", default=SETTINGS.http_host, help="HTTP host")
    common.add_argument("--http-port", type=int, default=SETTINGS.http_port, help="HTTP port")
    common.add_argument("--gradio-host", default=SETTINGS.gradio_host, help="Gradio host")
    common.add_argument("--gradio-port", type=int, default=SETTINGS.gradio_port, help="Gradio port")
    common.add_argument("--share", action="store_true", help="enable Gradio public share link")

    sub.add_parser("serve", parents=[common], help="run HTTP + Gradio together")
    sub.add_parser("http", parents=[common], help="run HTTP API only")
    sub.add_parser("ui", parents=[common], help="run Gradio UI only")
    sub.add_parser("self-test", parents=[common], help="run built-in validation checks")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.log_level)
    if args.cmd == "serve":
        return cmd_serve(args)
    if args.cmd == "http":
        return cmd_http(args)
    if args.cmd == "ui":
        return cmd_ui(args)
    if args.cmd == "self-test":
        return cmd_self_test(args)
    parser.error(f"unknown command: {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
