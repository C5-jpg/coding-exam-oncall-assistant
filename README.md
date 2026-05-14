# On-Call SOP Assistant

本仓库完成 [oriengy/coding-exam](https://github.com/oriengy/coding-exam) 的题目一：**On-Call 助手**。实现内容覆盖 `/v1` 关键词搜索、`/v2` 语义搜索、`/v3` Agent 对话三阶段，并提供前端页面、HTTP API、内置 smoke test、效果截图和详细报告。

公开仓库地址：<https://github.com/C5-jpg/coding-exam-oncall-assistant>

## 选题

我选择题目一，原因是它可以在离线环境中完整实现并可重复验证。题目二要求对外部站点动画做像素级复刻，评价强依赖运行时页面状态和视觉对比环境；题目一更适合用工程化方式证明解析、检索、Agent 工具约束和接口设计能力。

## 功能完成情况

| 阶段 | 路由 | 完成内容 |
| --- | --- | --- |
| Phase 1 | `/v1`、`/v1/search`、`/v1/documents` | HTML 可见正文解析、忽略 `script/style`、关键词检索、snippet 和分数、文档动态写入 |
| Phase 2 | `/v2`、`/v2/search` | TF-IDF 风格向量匹配 + On-Call 领域语义扩展 + 规则 boost，支持非精确命中查询 |
| Phase 3 | `/v3`、`/v3/chat` | Agent 对话、唯一工具 `readFile(fname)`、工具调用轨迹展示、多 SOP 综合回答 |

## 快速运行

环境要求：Python 3.10+。实现只使用 Python 标准库，不需要安装第三方依赖。

```bash
python question-1/code/oncall_assistant.py --host 127.0.0.1 --port 8000
```

打开页面：

- Phase 1：<http://127.0.0.1:8000/v1>
- Phase 2：<http://127.0.0.1:8000/v2>
- Phase 3：<http://127.0.0.1:8000/v3>

也可以直接打开带参数的演示页面：

- <http://127.0.0.1:8000/v1?q=CDN>
- <http://127.0.0.1:8000/v2?q=机器学习模型出问题>
- <http://127.0.0.1:8000/v3?message=数据库主从延迟超过30秒怎么处理？>

## 自检

```bash
python question-1/code/oncall_assistant.py --self-test
```

当前自检结果：

```json
{
  "documents": 10,
  "checks": 10,
  "failures": []
}
```

## API 示例

### Phase 1：写入文档

```http
POST /v1/documents
Content-Type: application/json

{
  "id": "sop-custom",
  "html": "<html><head><title>自定义 SOP</title></head><body><h1>自定义 SOP</h1><p>故障处理...</p></body></html>"
}
```

返回：

```json
{
  "id": "sop-custom",
  "title": "自定义 SOP"
}
```

### Phase 1：关键词搜索

```http
GET /v1/search?q=CDN
```

典型结果包含 `sop-003` 和 `sop-010`。`GET /v1/search?q=replication` 返回空，因为 `replicationLag` 只存在于脚本中，解析器不会把脚本内容加入索引。

### Phase 2：语义搜索

```http
GET /v2/search?q=服务器挂了
```

典型排序中 `sop-001` 和 `sop-004` 靠前。

```http
GET /v2/search?q=黑客攻击
```

典型排序中 `sop-005` 靠前。

### Phase 3：Agent 对话

```http
POST /v3/chat
Content-Type: application/json

{
  "message": "数据库主从延迟超过30秒怎么处理？"
}
```

返回中包含：

- `answer`：面向值班工程师的处理步骤
- `tool_calls`：Agent 调用 `readFile(fname)` 的完整轨迹
- `sources`：使用到的 SOP 文档

## 技术方案

### HTML 可见文本解析

`VisibleTextExtractor` 基于 `html.parser.HTMLParser` 实现。它只抽取 `<body>` 中的可见文本和 `<title>`，并显式忽略 `script`、`style`、`noscript`、`template`、`svg`、`canvas`。这样可以满足题目中 `replication` 不应被检索到的要求。

### 关键词检索

Phase 1 使用可解释的关键词检索：

- 英文、数字、下划线、短横线按词切分并统一小写
- 中文使用 2 到 4 字符 n-gram，兼顾短词和专有短语
- 对完整 query 短语命中、term 命中和 token 频次分别加权
- snippet 从可见正文中截取，不暴露脚本或样式内容

### 语义检索

Phase 2 在关键词索引上加入领域语义层：

- 基础分：TF-IDF 风格 token 匹配
- 语义扩展：把“服务器挂了”扩展到“后端服务、服务超时、Kubernetes、Pod、OOM”等领域词
- 领域 boost：对明显意图加入目标 SOP 的权重，例如“黑客攻击”提升 `sop-005`
- 结果按综合分排序并返回可解释 snippet

这种实现不依赖外部 embedding 服务，适合面试题的离线可复现环境。

### Agent 设计

Phase 3 的 Agent 遵守题目限制：对话过程中只有一个工具：

```text
readFile(fname: string) -> string
```

工具实现只接受普通文件名，拒绝路径分隔符和通配符，并把读取范围限制在 `question-1/data/`。Agent 先根据用户问题定位 SOP 文件，再调用 `readFile` 读取内容，最终给出面向 On-Call 场景的处理步骤。前端会展示每次工具调用、入参、读取标题和字符数。

## 验证记录

| 验证项 | 结果 |
| --- | --- |
| `python -m py_compile question-1/code/oncall_assistant.py` | 通过 |
| `python question-1/code/oncall_assistant.py --self-test` | 10 项通过 |
| `GET /health` | `status=ok`，`documents=10` |
| `GET /v1/search?q=OOM` | `sop-001` 排第一 |
| `GET /v1/search?q=replication` | 空结果 |
| `GET /v1/search?q=CDN` | 返回 `sop-010`、`sop-003` |
| `GET /v2/search?q=服务器挂了` | `sop-001`、`sop-004` 排前两位 |
| `GET /v2/search?q=黑客攻击` | `sop-005` 排第一 |
| `GET /v2/search?q=机器学习模型出问题` | `sop-008` 排第一 |
| `POST /v3/chat` DBA 主从延迟问题 | 调用 `readFile(sop-002.html)` |

## 目录结构

```text
.
├── question-1/
│   ├── code/
│   │   └── oncall_assistant.py
│   ├── data/
│   │   └── sop-001.html ... sop-010.html
│   └── README.md
├── prompt/
│   ├── PROMPTS.md
│   └── 01-user-task.png
├── screenshot/
│   ├── 01-v1-search.png
│   ├── 02-v2-semantic.png
│   └── 03-v3-agent.png
├── REPORT.md
└── README.md
```

## 打包提交

简历后续放到仓库根目录即可。打包时保留 `.git` 目录：

```bash
zip -r your-name-exam.zip . -x "node_modules/*" "*.zip"
```

如果使用 Windows PowerShell：

```powershell
Compress-Archive -Path .\* -DestinationPath your-name-exam.zip
```

注意：`Compress-Archive` 默认不会包含隐藏的 `.git` 目录；如果面试要求必须包含 `.git`，建议使用 Git Bash / WSL 的 `zip -r` 命令。
