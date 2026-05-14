# Antigravity 本地复刻交付报告

## 1. 本次完成内容

本次在 `D:\reps\26H1_kimi\coding-exam\cline` 下完成了 Antigravity 官网复刻的审计、资源整理、工程实现、截图检查和像素差异报告。

实现项目位置：

```text
D:\reps\26H1_kimi\coding-exam\cline\code
```

本地素材位置：

```text
D:\reps\26H1_kimi\coding-exam\resources
D:\reps\26H1_kimi\coding-exam\resources\antigravity-site
```

## 2. 使用的工具与 MCP

本轮使用了以下能力：

- Browser / Playwright：打开原站、读取 DOM、采集截图、验证本地页面。
- `zai-mcp-server`：对原站截图做视觉理解辅助分析，重点确认首屏布局、粒子形态、价格卡片层级。
- 文件系统工具：创建工程、写入中文文档、保存截图和审计数据。
- PowerShell / npm：安装依赖、构建项目、运行截图脚本、生成像素差异报告。

说明：当前可调用的 ZAI MCP 是视觉理解类工具，不是 Chrome DevTools 协议本身；页面 DOM、资源和截图细节主要通过 Browser/Playwright 获取。

## 3. 下载和整理的资源

已下载到 `resources\antigravity-site` 的公开静态资源包括：

- `antigravity-cursor.png`
- `landing-thumbnail-frontend.jpg`
- `landing-thumbnail-fullstack.jpg`
- `landing-thumbnail-enterprise.jpg`
- `blog-feature-introducing-google-antigravity.png`
- `blog-gemini-3-1-pro-square.png`
- `blog-gemini-3-flash-square.png`
- `individual.png`
- `cube.png`

用户已提供并被接入工程的本地视频包括：

- `Welcome to Google Antigravity 🚀_2160p.mp4`
- `an-agent-first-experience.mp4`
- `cross-surface-agents.mp4`
- `higher-level-abstractions.mp4`
- `pinball_optmized.mp4`
- `user-feedback.mp4`

这些资源被复制到：

```text
cline\code\public\assets\images
cline\code\public\assets\videos
```

这样项目运行时主体视觉不依赖远端资源。

## 4. 已实现的页面范围

当前本地复刻版本包括：

- Header / Navbar
- Google Antigravity 风格品牌区域
- Hero 首屏
- 白底稀疏点状 / 短划 Canvas 粒子
- Download for Windows CTA
- Explore use cases CTA
- Use Cases 全宽下拉菜单
- Resources 全宽下拉菜单
- Intro video 区域
- Agent-first 图标区
- Product section
- Product 蓝色点阵 ribbon Canvas
- Feature Explorer 视频切换
- Use Cases 卡片
- Pricing 卡片和卡片内 Canvas 粒子
- Blog 卡片
- Download section
- Footer
- Cookie demo banner
- 移动端折叠菜单

## 5. 交互和动画实现

Canvas 粒子系统位置：

```text
cline\code\src\particles
```

核心能力：

- `requestAnimationFrame` 主循环；
- `devicePixelRatio` 自适应；
- 移动端降低粒子数量；
- seeded random 保持刷新后视觉稳定；
- hero 模式：点状 / 短划粒子；
- product 模式：蓝色点阵 ribbon；
- card / download 模式：卡片内部低强度装饰粒子；
- pointermove 轻微扰动；
- pointerdown 波纹；
- hover boost；
- `prefers-reduced-motion` 降级。

这次重点修正了之前的问题：粒子不再是竖向长条，而是接近原站的点状和短划。

## 6. 如何运行检查

进入项目：

```bash
cd D:\reps\26H1_kimi\coding-exam\cline\code
```

安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev
```

浏览器打开：

```text
http://127.0.0.1:5173/
```

构建验证：

```bash
npm run build
```

生成本地截图：

```bash
npm run screenshot
```

生成像素差异报告：

```bash
npm run diff
```

## 7. 截图检查结果

本地截图输出：

```text
cline\screenshots\local
```

包含：

- `1440x900`
- `1366x768`
- `1024x768`
- `768x1024`
- `390x844`
- `375x812`
- `dropdown-use-cases.png`
- `dropdown-resources.png`

像素差异报告：

```text
cline\docs\PIXEL_AUDIT.md
```

当前桌面 1440x900 首屏差异约为 `3.87%`，移动端由于字体、折行和安全声明策略差异，差异约为 `10% - 12%`。

## 8. 已知差异

仍然存在以下差异：

- 未复制原站生产 JS/CSS，动画算法为独立实现；
- 字体使用系统近似，不能保证 Google Sans Flex 完全一致；
- 原站内部视频首帧、压缩和播放状态不可完全固定；
- 下载、登录、官方链接全部被替换为本地安全占位；
- Pixel diff 衡量的是截图像素差异，不代表官方认证。

## 9. 法务和品牌风险控制

本项目仅用于本地学习和 UI 复刻练习：

- 不得部署为误导用户的公开站点；
- 不得冒充 Google 官方；
- 不得提供真实软件下载；
- 不得接入真实登录、支付或用户数据收集；
- 不得接入 Google Analytics / GTM / 追踪脚本；
- 页面中保留了 `Demo only / Unofficial clone` 声明。

## 10. 建议下一轮优化

下一轮如果继续逼近像素级，建议按以下顺序调：

1. Hero 标题纵向位置和字体渲染；
2. Header 左右边距和导航间距；
3. 粒子左侧密度、颜色分布和短划旋转角；
4. Product 点阵 ribbon 的弧线曲率；
5. 移动端标题折行；
6. Pricing / Download section 的卡片尺寸和视频首帧。
