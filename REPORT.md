# On-Call 助手编程实战报告

## 1. 任务概述

本次编程实战来自 `oriengy/coding-exam`，两题任选其一。我完成的是题目一：构建一个基于 SOP 文档的 On-Call 助手 Web 应用。题目要求拆成三个阶段：

1. `/v1`：关键词搜索引擎。
2. `/v2`：语义搜索，查询词不需要精确出现在文档中。
3. `/v3`：On-Call 助手 Agent，通过对话回答值班问题，并展示工具调用过程。

交付目标包括 HTTP API、前端页面、运行说明、效果截图、prompt 记录、完整 Git 历史，以及后续可打包发送的仓库。

公开仓库地址：<https://github.com/C5-jpg/coding-exam-oncall-assistant>

## 2. 技术选型

### 2.1 语言与依赖

实现使用 Python 标准库完成，不引入第三方服务或依赖。主要考虑如下：

- 面试仓库没有预置工程框架，标准库实现可减少安装和环境不确定性。
- SOP 数据规模小，10 份 demo 或 100 份正式数据都可以在内存中快速索引。
- Phase 2 可以用轻量语义扩展和 TF-IDF 风格打分完成验收，不需要依赖外部 embedding API。
- Phase 3 的 Agent 工具约束非常明确，确定性实现更容易审计。

### 2.2 服务结构

核心文件是 `question-1/code/oncall_assistant.py`。服务启动后完成以下初始化：

1. 读取 `question-1/data/*.html`。
2. 使用 `VisibleTextExtractor` 解析标题和可见正文。
3. 构建 token 计数、document frequency 和 IDF。
4. 创建 `OnCallAgent`，注入索引和受限 `readFile` 工具。
5. 启动 `ThreadingHTTPServer` 提供 API 和前端页面。

## 3. 关键实现

### 3.1 HTML 解析

题目明确要求 `replication` 只出现在 `script` 标签内时不能被检索出来。因此解析器不能直接正则清洗 HTML，也不能简单抽取全文。

实现中使用 `HTMLParser`：

- `<title>` 单独抽取作为标题。
- 只把 `<body>` 内文本纳入正文。
- 忽略 `script`、`style`、`noscript`、`template`、`svg`、`canvas`。
- 通过 `HTMLParser(convert_charrefs=True)` 处理 HTML entity，例如 `&amp;`、`&#45;`、`&period;`。

这能同时覆盖普通 HTML、深层嵌套 HTML、实体编码 HTML 和带脚本样式的 HTML。

### 3.2 Phase 1 关键词搜索

关键词搜索由三部分组成：

- 归一化：统一小写、解码 HTML entity、压缩空白。
- token 化：英文数字按词切分，中文使用 2 到 4 字符 n-gram，并补充常见领域短语。
- 打分：完整 query 短语命中最高，其次是 term 命中和 token 频次。

这样可以保证：

- `OOM` 能命中后端 SOP。
- `故障` 能命中多份 SOP。
- `replication` 不会因为脚本变量 `replicationLag` 被命中。
- `CDN` 能命中前端和网络 CDN SOP。
- `&` 可以通过 `/v1/search?q=%26` 或题目给出的 `/v1/search?q=&` 形式检索。

### 3.3 Phase 2 语义搜索

语义搜索的实现目标是离线、可解释、可复现。它不是调用 LLM 或外部 embedding 服务，而是在关键词索引上增加 On-Call 领域语义层。

语义规则包含：

- backend/service down：服务器挂了、宕机、服务超时、OOM。
- database replication：数据库、主从、复制、延迟、慢查询。
- security attack：黑客、攻击、入侵、漏洞、泄露。
- ai model：机器学习、模型、推荐、质量下降、GPU、AB 实验。
- network/cdn、frontend、SRE、QA、移动端、数据平台等其他领域。

打分公式由三部分组成：

1. query + expansions 的 token 与文档 token 的 TF-IDF 风格相似度。
2. 原始 query 短语在文档中的直接命中。
3. 领域规则对目标 SOP 的 boost。

验收查询表现：

- `服务器挂了`：`sop-001`、`sop-004` 排前两位。
- `黑客攻击`：`sop-005` 排第一。
- `机器学习模型出问题`：`sop-008` 排第一。

### 3.4 Phase 3 Agent

Agent 只暴露一个工具：

```text
readFile(fname: string) -> string
```

工具安全限制：

- 只接受普通文件名。
- 拒绝 `/`、`\`、`*`、`?` 等路径分隔符或通配符。
- 使用 `resolve()` 校验目标文件父目录必须是 `question-1/data/`。
- 不提供列目录能力。

Agent 执行流程：

1. 根据用户问题做意图识别。
2. 选择 SOP 文件名。
3. 调用 `readFile(fname)`。
4. 解析文件可见文本。
5. 生成处置建议。
6. 返回 `answer`、`tool_calls`、`sources`。

典型行为：

- “数据库主从延迟超过30秒怎么处理？”读取 `sop-002.html`。
- “服务 OOM 了怎么办？”读取 `sop-001.html`。
- “P0 故障的响应流程是什么？”读取 `sop-001.html`、`sop-004.html`、`sop-005.html`、`sop-010.html` 做综合回答。
- “怀疑有人入侵了系统”读取 `sop-005.html`。
- “推荐结果质量下降了”读取 `sop-008.html`。

## 4. 前端实现

前端由服务端直接返回 HTML/CSS/JS，不需要构建工具。

- `/v1` 和 `/v2`：搜索框 + 结果列表。
- `/v3`：消息输入 + 对话历史 + 工具调用折叠区。
- 页面支持 URL 参数自动触发：
  - `/v1?q=CDN`
  - `/v2?q=机器学习模型出问题`
  - `/v3?message=数据库主从延迟超过30秒怎么处理？`

URL 参数支持方便截图、验收和复现。

## 5. 验证结果

### 5.1 静态检查

```bash
python -m py_compile question-1/code/oncall_assistant.py
```

结果：通过。

### 5.2 内置 smoke test

```bash
python question-1/code/oncall_assistant.py --self-test
```

结果：

```json
{
  "documents": 10,
  "checks": 10,
  "failures": []
}
```

### 5.3 HTTP 接口验证

| 请求 | 关键结果 |
| --- | --- |
| `GET /health` | `status=ok`，`documents=10` |
| `GET /v1/search?q=OOM` | `sop-001` 排第一 |
| `GET /v1/search?q=replication` | 空结果 |
| `GET /v1/search?q=CDN` | 返回 `sop-010`、`sop-003` |
| `GET /v1/search?q=%26` | 返回正文/标题包含 `&` 的文档 |
| `GET /v2/search?q=服务器挂了` | `sop-001`、`sop-004` 排前两位 |
| `GET /v2/search?q=黑客攻击` | `sop-005` 排第一 |
| `GET /v2/search?q=机器学习模型出问题` | `sop-008` 排第一 |
| `POST /v3/chat` DBA 问题 | 工具调用 `readFile(sop-002.html)` |

### 5.4 效果截图

截图已保存到：

- `screenshot/01-v1-search.png`
- `screenshot/02-v2-semantic.png`
- `screenshot/03-v3-agent.png`

## 6. 已知取舍

1. Phase 2 没有使用真实 embedding 模型。原因是题目没有要求必须使用外部模型，且离线可复现比依赖 API key 更稳定。
2. Agent 是确定性 Agent，不是开放式 LLM Agent。它更容易满足“只能通过 readFile 工具读取 SOP”的约束，也更容易被自动化验证。
3. 语义规则目前面向题目中的 10 类 SOP 构建。如果正式数据扩展到 100 份，可以把规则抽到配置文件，并在启动时从标题和章节自动生成领域词。
4. 前端以功能验收为主，没有引入复杂 UI 框架，减少构建步骤。

## 7. 后续优化方向

如果继续演进，我会优先做以下改进：

1. 把语义规则配置化，支持热更新。
2. 加入可选 embedding 后端，在有 API key 时使用向量检索，无 API key 时回退到当前离线实现。
3. 把 `readFile` 工具调用和回答生成拆成更细的 trace，便于审计 Agent 决策。
4. 增加 pytest 测试和 golden file，覆盖 HTML entity、脚本忽略、动态写入文档、Agent 安全边界。
5. 对正式 100 份 SOP 增加索引持久化，避免每次启动重复解析。

## 8. 提交说明

简历后续放入仓库根目录即可。最终提交时建议：

1. 确认 `python question-1/code/oncall_assistant.py --self-test` 通过。
2. 确认 `prompt/`、`screenshot/`、`README.md`、`REPORT.md` 存在。
3. 打包整个仓库，包含 `.git` 目录。
4. 创建公开 GitHub 仓库并推送完整提交历史。
5. 将 zip 发送到面试官邮箱。
