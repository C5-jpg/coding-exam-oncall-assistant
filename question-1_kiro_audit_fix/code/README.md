# On-Call 助手 - 实现代码

## 快速启动

```bash
# 需要 Python 3.10+，无第三方依赖
python oncall_assistant.py --host 127.0.0.1 --port 8000
```

启动后访问：
- Phase 1 关键词搜索：http://127.0.0.1:8000/v1
- Phase 2 语义搜索：http://127.0.0.1:8000/v2
- Phase 3 Agent 对话：http://127.0.0.1:8000/v3

## 自检

```bash
python oncall_assistant.py --self-test
```

## 运行测试

```bash
# 无需 pytest，直接运行：
python tests/test_oncall.py

# 或使用 pytest（如已安装）：
python -m pytest tests/ -v
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `oncall_assistant.py` | 主程序，包含 HTTP 服务、搜索引擎、Agent、前端页面 |
| `tests/test_oncall.py` | 42 项单元测试和集成测试 |

## 架构

```
oncall_assistant.py
├── VisibleTextExtractor   # HTML 解析，忽略 script/style
├── DocumentIndex          # 文档索引、关键词搜索、语义搜索
├── ReadFileTool           # Agent 唯一工具，受限文件读取
├── OnCallAgent            # Agent 逻辑：意图识别 → 文件选择 → 工具调用 → 答案生成
├── OnCallRequestHandler   # HTTP 路由处理
└── OnCallServer           # ThreadingHTTPServer 封装
```
