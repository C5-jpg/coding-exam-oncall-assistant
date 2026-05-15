# 审计与升级日志

> 工作副本：`E:\reps\26H1_kimi\coding-exam\question-1_kiro_audit_fix`
> 原始目录：`E:\reps\26H1_kimi\coding-exam\question-1`（只读，未修改）

## 第一阶段：只读审计（已完成）

详见上文审计报告。结论：原项目通过题目所有验证用例，但语义搜索是规则式、Agent 是硬编码模板，距离"工业化可用"还有差距。

## 第二阶段：运行验证（已完成）

- `python --self-test` → 10/10 通过
- HTTP 端点验证 → 15/15 通过
- 新增 pytest 测试 → 42/42 通过

## 第三阶段：工业化升级

### 3.1 升级目标

| 维度 | 现状 | 目标 |
|---|---|---|
| 嵌入检索 | 规则式语义扩展 | Qwen3-Embedding-8B 向量检索 |
| Agent | 硬编码意图 + 模板回答 | GLM-4.6 LLM Agent + 工具调用 + 多轮记忆 |
| 前端 | 简易 HTML | Gradio 三 Tab UI + 原 HTML 页面保留 |
| Chunking | 整文档索引 | 按 `<h2>/<h3>` 章节切分 |
| 缓存 | 无 | 嵌入向量本地 JSON 持久化（基于内容 hash） |
| 配置管理 | 无 | `.env` + `.env.example`，密钥不进代码 |
| 测试覆盖 | 42 项 | 增加嵌入、Agent 记忆、工具调用边界 |

### 3.2 API 配置

| 服务 | 端点 | 模型 | 用途 |
|---|---|---|---|
| 硅基流动 | `https://api.siliconflow.cn/v1/embeddings` | `Qwen/Qwen3-Embedding-8B` | 1024 维向量嵌入 |
| 智谱 GLM Coding | `https://open.bigmodel.cn/api/coding/paas/v4` | `glm-4.6` | LLM 推理 + tool calling |

### 3.3 API 连通性验证（已通过）

- `[EMBED] OK dim=1024` — Qwen3-Embedding-8B 返回 1024 维向量
- `[CHAT] OK model=glm-4.6 reply='Pong! 🏓'` — GLM-4.6 正常应答

### 3.4 依赖

新增：
- `gradio==6.14.0` — Web UI
- `python-dotenv` — 加载 `.env`

`numpy`、`requests` 已在系统中。

### 3.5 工作记录

逐步追加于本文件下方的"操作记录"小节。
