# Tool Capability Map

当前会话中可用工具与用户描述能力的对应关系如下。

| 用户描述能力 | 当前可用工具 | 用途 | 备注 |
| --- | --- | --- | --- |
| Browser / Playwright / Puppeteer 类工具 | `mcp__node_repl__js` + Browser plugin runtime；`playwright screenshot` CLI | 打开网页、读取 DOM snapshot、控制本地/远程页面、保存截图 | 视觉审计优先使用该能力 |
| 智谱相关 MCP | 当前工具列表未暴露同名 MCP | 暂无 | 不因名称缺失停止；用 Browser 截图、DOM、计算样式和图片审阅替代 |
| 文件系统工具 | `apply_patch`、PowerShell `New-Item`/读取命令 | 只在 `D:\reps\26H1_kimi\coding-exam\cline` 写入审计产物 | 不写 `question-1` / `question-2` |
| 终端工具 | `functions.shell_command` | 运行 Playwright CLI、Node 脚本、构建/截图/后续 diff | 需要网络或 GUI 时按策略申请提升 |
| 视觉理解 | Browser 截图 + `functions.view_image` + DOM snapshot | 分析布局、粒子、响应式、section 结构 | 不依赖记忆 |

本阶段只做审计，不创建本地复刻页面代码。
