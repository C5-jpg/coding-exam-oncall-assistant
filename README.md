<div align="center">

# 🚨 On-Call SOP Assistant — 值班工程师智能运维助手

**三阶段递进式 SOP 智能检索系统 · 关键词搜索 → 语义扩展 → Agent 对话**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-success.svg)]()
[![Self-Test](https://img.shields.io/badge/Self%20Test-10%2F10-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Coding Exam](https://img.shields.io/badge/Coding%20Exam-oriengy-blueviolet.svg)](https://github.com/oriengy/coding-exam)

**纯 Python 标准库实现 · 无需第三方依赖 · 离线可复现 · 10 项自检全通过**

[功能演示](#-功能演示) · [系统架构](#-系统架构) · [快速开始](#-快速开始) · [API文档](#-api-文档) · [技术方案](#-技术方案)

</div>

---

## 📋 项目概述

本项目是 [oriengy/coding-exam](https://github.com/oriengy/coding-exam) 编程面试题的完整解答，实现了一套面向**值班工程师（On-Call Engineer）**的 SOP 智能检索系统。系统从 10 个部门的标准运维流程文档中，通过三阶段递进式检索帮助工程师快速定位故障处理方案。

### 🔑 三阶段递进设计

| 阶段 | 路由 | 能力 | 核心技术 |
|:---:|:---:|------|------|
| **Phase 1** | `/v1` | 关键词全文检索 | TF-IDF + n-gram 分词 + 短语匹配 |
| **Phase 2** | `/v2` | 领域语义搜索 | 语义扩展规则(11组) + TF-IDF + 领域Boost |
| **Phase 3** | `/v3` | Agent 智能对话 | 意图识别 → 文档定位 → readFile 工具调用 → 结构化回答 |

---

## 🎯 功能演示

### Phase 1 — 关键词搜索

<p align="center">
  <img src="screenshot/01-v1-search.png" width="700" alt="Phase 1 关键词搜索界面">
</p>

> 全文关键词搜索，支持中英文混合查询、snippet 高亮、文档动态写入。
> 正确忽略 `<script>` 中的 `replicationLag`，仅返回可见文本结果。

### Phase 2 — 语义搜索

<p align="center">
  <img src="screenshot/02-v2-semantic.png" width="700" alt="Phase 2 语义搜索界面">
</p>

> 查询"服务器挂了"能匹配到"后端服务 OOM"、"K8s Pod NotReady"等相关 SOP，
> 而不要求精确关键词命中。覆盖后端、数据库、前端、SRE、安全、数据、移动、AI、QA、网络共 11 个领域。

### Phase 3 — Agent 对话

<p align="center">
  <img src="screenshot/03-v3-agent.png" width="700" alt="Phase 3 Agent 对话界面">
</p>

> Agent 自动识别意图 → 选择 SOP 文档 → 调用 `readFile()` 工具 → 生成结构化处理步骤。
> 前端实时展示工具调用轨迹（调用参数、读取标题、字符数）。

---

## 🧠 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户请求                                     │
│                  http://127.0.0.1:8000/{v1|v2|v3}                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
     │  Phase 1: v1 │ │ Phase 2: v2 │ │ Phase 3: v3  │
     │  关键词搜索   │ │  语义搜索    │ │ Agent 对话   │
     └──────┬───────┘ └──────┬──────┘ └──────┬───────┘
            │                │               │
            ▼                ▼               ▼
     ┌──────────────────────────────────────────────────┐
     │              DocumentIndex (文档索引)              │
     │  ┌────────────────────────────────────────────┐  │
     │  │  VisibleTextExtractor (HTMLParser)         │  │
     │  │  · 提取 <body> 可见文本 + <title>           │  │
     │  │  · 忽略 script/style/noscript/template/svg │  │
     │  └────────────────────────────────────────────┘  │
     │                                                  │
     │  ┌──────────────┐  ┌──────────────┐             │
     │  │ TF-IDF 关键词 │  │ 语义扩展规则  │             │
     │  │ · 中英文分词  │  │ · 11 组领域词 │             │
     │  │ · n-gram 切词 │  │ · 同义词扩展  │             │
     │  │ · 短语加权    │  │ · 意图 Boost  │             │
     │  └──────────────┘  └──────────────┘             │
     └──────────────────────────────────────────────────┘
                             │
                             ▼
     ┌──────────────────────────────────────────────────┐
     │              OnCallAgent (AI Agent)               │
     │  ┌──────────────┐  ┌──────────────────────────┐  │
     │  │ 意图分类器    │  │ ReadFileTool (唯一工具)   │  │
     │  │ · 关键词匹配  │  │ · 路径安全校验           │  │
     │  │ · 领域映射    │  │ · 沙箱文件读取           │  │
     │  └──────────────┘  │ · 限制 data/ 目录         │  │
     │                     └──────────────────────────┘  │
     └──────────────────────────────────────────────────┘
                             │
                             ▼
     ┌──────────────────────────────────────────────────┐
     │           10 份 SOP 文档 (HTML)                   │
     │  后端·数据库·前端·SRE·安全·数据·移动·AI·QA·网络   │
     └──────────────────────────────────────────────────┘
```

---

## 📊 10 份 SOP 文档覆盖

| 文件 | 部门 | 关键场景 | 边缘测试 |
|:---:|:---:|------|------|
| `sop-001` | 后端服务 | OOM、超时、降级、Kafka 积压 | — |
| `sop-002` | 数据库 DBA | 主从延迟、慢查询、连接池耗尽 | 含 `<script>` 排除测试 |
| `sop-003` | 前端 Web | 白屏、CDN 故障、JS 错误、CORS | HTML 实体编码测试 |
| `sop-004` | SRE 基础设施 | K8s NotReady、Etcd、Ingress | 缺少闭合标签健壮性测试 |
| `sop-005` | 信息安全 | DDoS、SQL 注入、数据泄露 | 深层嵌套 DOM 压力测试 |
| `sop-006` | 数据平台 | ETL 故障、Flink 异常、HDFS | 含分析脚本排除测试 |
| `sop-007` | 移动客户端 | App 崩溃、内存泄漏、推送 | — |
| `sop-008` | AI & 算法 | 模型推理延迟、质量退化、GPU | 含模型状态脚本 |
| `sop-009` | QA 质量 | 自动化失败、测试环境、性能 | 含内联样式排除测试 |
| `sop-010` | 网络 & CDN | CDN 节点、DNS 异常、跨域延迟 | 大量 HTML 实体编码 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+ （仅需标准库，零第三方依赖）

### 启动服务

```bash
python question-1/code/oncall_assistant.py --host 127.0.0.1 --port 8000
```

### 访问页面

| 阶段 | 地址 | 演示链接 |
|:---:|------|------|
| Phase 1 | http://127.0.0.1:8000/v1 | [?q=CDN](http://127.0.0.1:8000/v1?q=CDN) |
| Phase 2 | http://127.0.0.1:8000/v2 | [?q=机器学习模型出问题](http://127.0.0.1:8000/v2?q=机器学习模型出问题) |
| Phase 3 | http://127.0.0.1:8000/v3 | [?message=数据库主从延迟...](http://127.0.0.1:8000/v3?message=数据库主从延迟超过30秒怎么处理？) |

### 自检验证

```bash
python question-1/code/oncall_assistant.py --self-test
```

```json
{"documents": 10, "checks": 10, "failures": []}
```

---

## 📡 API 文档

### Phase 1 — 关键词搜索

| Method | Path | Description |
|:---:|------|------|
| `GET` | `/v1` | 搜索页面 |
| `GET` | `/v1/search?q={query}` | 关键词搜索 (JSON) |
| `POST` | `/v1/documents` | 动态写入文档 |

<details>
<summary>📝 请求/响应示例</summary>

```http
POST /v1/documents
Content-Type: application/json

{"id": "sop-custom", "html": "<html><head><title>自定义 SOP</title></head><body><h1>自定义 SOP</h1><p>故障处理...</p></body></html>"}
```

```json
// Response
{"id": "sop-custom", "title": "自定义 SOP"}
```

```http
GET /v1/search?q=CDN
```

```json
// Response: 返回 sop-003(前端) 和 sop-010(网络)
// GET /v1/search?q=replication → 空结果 (script 内容不参与索引)
```

</details>

### Phase 2 — 语义搜索

| Method | Path | Description |
|:---:|------|------|
| `GET` | `/v2` | 语义搜索页面 |
| `GET` | `/v2/search?q={query}` | 语义搜索 (JSON) |

<details>
<summary>📝 查询示例</summary>

| 查询 | 期望 Top 结果 | 说明 |
|------|:---:|------|
| `服务器挂了` | sop-001, sop-004 | 语义扩展到 OOM、K8s |
| `黑客攻击` | sop-005 | 领域 Boost 到安全 SOP |
| `机器学习模型出问题` | sop-008 | AI 领域匹配 |

</details>

### Phase 3 — Agent 对话

| Method | Path | Description |
|:---:|------|------|
| `GET` | `/v3` | Agent 对话页面 |
| `POST` | `/v3/chat` | Agent 对话 (JSON) |

<details>
<summary>📝 请求/响应示例</summary>

```http
POST /v3/chat
Content-Type: application/json

{"message": "数据库主从延迟超过30秒怎么处理？"}
```

```json
{
  "answer": "面向值班工程师的处理步骤...",
  "tool_calls": [
    {"tool": "readFile", "args": {"fname": "sop-002.html"}, "title": "数据库DBA SOP", "chars": 3847}
  ],
  "sources": ["sop-002.html"]
}
```

</details>

---

## 🔬 技术方案

### HTML 可见文本解析

```
┌─────────────────────────────────────────────────┐
│          VisibleTextExtractor (HTMLParser)       │
│                                                  │
│  ✅ 提取: <body> 可见文本 + <title>              │
│  ❌ 忽略: script · style · noscript · template   │
│          · svg · canvas                          │
│                                                  │
│  → "replicationLag" 在 <script> 中 → 不可检索    │
│  → "OOM" 在 <body> 中 → 可检索                   │
└─────────────────────────────────────────────────┘
```

### 分词策略

```
输入: "服务器OOM导致超时"
        │
        ▼
┌───────────────────────────────┐
│  中文: 2-4 字符 n-gram        │
│  "服务" "服务器" "务器O" ...  │
├───────────────────────────────┤
│  英文: 按词边界切分           │
│  "OOM" "导致" "超时"         │
├───────────────────────────────┤
│  加权: 短语命中 > 词元命中    │
│  TF-IDF 逆文档频率加权        │
└───────────────────────────────┘
```

### 语义扩展规则 (11 组)

| 领域 | 扩展示例 |
|:---:|------|
| 后端 | 服务器挂了 → OOM、超时、降级、Kafka 积压 |
| 数据库 | 主从延迟 → 复制、慢查询、连接池 |
| SRE | 节点异常 → K8s NotReady、Etcd、Ingress |
| 安全 | 黑客攻击 → DDoS、SQL注入、数据泄露 |
| AI | 模型问题 → 推理延迟、质量退化、GPU |
| ... | 共 11 组领域覆盖 |

### Agent 工具约束

```python
# Agent 唯一工具：沙箱文件读取
readFile(fname: str) -> str

# 安全约束:
# · 拒绝路径分隔符 / \
# · 拒绝通配符 * ?
# · 限制读取范围: question-1/data/
# · 路径规范化: os.path.resolve() 校验
```

---

## 📁 项目结构

```
coding-exam-oncall-assistant/
│
├── 🔧 核心实现
│   └── question-1/
│       ├── code/
│       │   └── oncall_assistant.py         # 1104 行单文件 Python 应用
│       │       ├── VisibleTextExtractor    # HTML 可见文本解析器
│       │       ├── Document / DocumentIndex# 文档索引 + TF-IDF + 语义搜索
│       │       ├── ReadFileTool            # 沙箱文件读取工具
│       │       ├── OnCallAgent             # 意图识别 + Agent 逻辑
│       │       └── OnCallServer            # HTTP 服务器 (ThreadingHTTPServer)
│       ├── data/
│       │   └── sop-001.html ... sop-010.html  # 10 份部门 SOP 文档
│       └── README.md                       # 题目规格说明
│
├── 📸 效果截图
│   └── screenshot/
│       ├── 01-v1-search.png               # Phase 1 关键词搜索
│       ├── 02-v2-semantic.png             # Phase 2 语义搜索
│       └── 03-v3-agent.png                # Phase 3 Agent 对话
│
├── 📄 文档
│   ├── REPORT.md                          # 详细技术报告
│   └── prompt/PROMPTS.md                  # AI 辅助记录
│
├── 🎨 Bonus: Antigravity 粒子动画复刻
│   └── question-2/
│       ├── code/                          # Vite + TS + Canvas 2D
│       │   ├── src/particles/             # 粒子物理引擎
│       │   │   ├── ParticleSystem.ts      # 三层粒子 (尘埃/轨道/信号)
│       │   │   ├── Particle.ts            # 弹簧-阻尼物理模型
│       │   │   └── Renderer.ts            # DPR 感知 Canvas 渲染
│       │   └── scripts/
│       │       └── compare-screenshot.mjs # 零依赖 PNG 像素对比
│       └── screenshot/                    # 多分辨率截图对比
│
└── 🌐 Bonus: Antigravity 全站复刻
    └── cline/
        ├── code/                          # Vite + React 18 + TS (14 组件)
        ├── docs/                          # 8 份设计/审计文档
        └── screenshots/                   # 6 视口 × reference/local/diff
```

---

## ✅ 验证记录

| 验证项 | 结果 |
|------|:---:|
| `py_compile` 语法检查 | ✅ |
| `--self-test` 10 项自检 | ✅ 10/10 |
| `GET /health` 健康检查 | ✅ `documents=10` |
| `GET /v1/search?q=OOM` → sop-001 排第一 | ✅ |
| `GET /v1/search?q=replication` → 空结果 (script 排除) | ✅ |
| `GET /v1/search?q=CDN` → sop-010, sop-003 | ✅ |
| `GET /v2/search?q=服务器挂了` → sop-001, sop-004 | ✅ |
| `GET /v2/search?q=黑客攻击` → sop-005 排第一 | ✅ |
| `GET /v2/search?q=机器学习模型出问题` → sop-008 排第一 | ✅ |
| `POST /v3/chat` DBA 主从延迟 → readFile(sop-002) | ✅ |
| 深度检查 (34/34 tests passed) | ✅ |

---

## 🛠️ 技术栈

<div align="center">

| 类别 | 技术 |
|:---:|:---:|
| 后端 | ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white) 标准库零依赖 |
| HTTP 服务 | `http.server.ThreadingHTTPServer` |
| HTML 解析 | `html.parser.HTMLParser` |
| 搜索引擎 | TF-IDF + n-gram + 语义扩展规则 |
| Agent | 意图分类 + 工具调用 (readFile) |
| 前端 | 服务端渲染 HTML/CSS/JS |
| 动画 (Bonus) | ![TypeScript](https://img.shields.io/badge/TypeScript-Canvas%202D-3178C6?style=flat&logo=typescript&logoColor=white) |
| 全站 (Bonus) | ![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black) + Vite |

</div>

---

## 🏆 项目亮点

- **零依赖**: 纯 Python 标准库，无需 `pip install`，开箱即用
- **离线可复现**: 不依赖外部 API 或 embedding 服务
- **渐进式设计**: 关键词 → 语义 → Agent，三阶段能力递进
- **安全沙箱**: Agent 工具严格路径校验，防止目录遍历攻击
- **边缘覆盖**: 10 份 SOP 精心设计覆盖 HTML 解析的各种边界情况
- **10 项自检**: 内置 smoke test，一键验证全部功能正确性
- **双 Bonus**: 额外完成粒子动画复刻 + Antigravity 全站复刻

---

## 📦 提交打包

```bash
zip -r your-name-exam.zip . -x "node_modules/*" "*.zip"
```

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个 Star 支持一下！**

</div>
