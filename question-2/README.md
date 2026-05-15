# Antigravity Frontend Recreation — Question 2

> 像素级复刻 [antigravity.google](https://antigravity.google/) 官网前端，包括导航层级、粒子动画、视频区域、产品展示、Use Cases 分层、Pricing、Blog、Resources 悬浮菜单、响应式布局和 Playwright 截图验证。

---

## 1. 项目目标

本项目不是简单的粒子背景 demo，而是对 antigravity.google 官网前端的**完整复刻**，包括：

- ✅ **官网导航结构** — Product / Use Cases / Pricing / Blog / Resources 五大导航项
- ✅ **Mega Menu** — Product、Use Cases、Resources 均有悬浮面板，左侧文案+右侧链接列表
- ✅ **Resources 面板** — 左侧 "Everything you need to stay up-to-date and get help"，右侧 Document / Changelog / Support / Press / Releases
- ✅ **Use Cases 分层** — Professional / Frontend / Fullstack 三个 tab 切换面板
- ✅ **Hero 首屏** — 大标题 + 副标题 + 双 CTA + 粒子背景 + 视频卡片
- ✅ **Product Section** — Agent-first 平台介绍 + 6 张能力卡片（Agent Manager / Editor / Browser / Terminal / Artifacts / Verification）
- ✅ **视频播放** — Hero video + Product demo video + 视频弹窗播放器（使用真实 .mp4 资源）
- ✅ **Pricing** — Free / Pro / Enterprise 三栏定价卡片
- ✅ **Blog** — 3 张文章卡片，含标签、日期、摘要
- ✅ **粒子系统** — 三层粒子（dust / orbit / signal），含鼠标交互、点击波纹、噪声漂移
- ✅ **移动端适配** — Hamburger 菜单 + 抽屉式导航 + accordion 子菜单
- ✅ **Footer** — 四列链接 + 品牌区 + 法律信息
- ✅ **Playwright 截图** — 自动化截图脚本

---

## 2. 目标站观察记录

> 以下为通过浏览器访问 https://antigravity.google/ 的观察总结（非源码复制）。

### 2.1 首页首屏

- **顶部导航**：左侧 Logo（Google Antigravity 文字 + 火箭 icon），右侧导航项 Product / Use Cases / Pricing / Blog / Resources，最右侧 Download CTA 按钮
- **Hero 区域**：居中大标题，白色文字，下方副标题，两个 CTA 按钮（主 CTA 实色背景，次 CTA 边框样式）
- **背景**：深色/近黑色背景，带有粒子动画（蓝紫色调粒子缓慢飘动）
- **视频卡片**：Hero 下方有圆角视频卡片，带发光边框效果
- **字体**：无衬线体，标题约 48-64px，正文约 16-18px
- **色彩**：主色调为深蓝黑背景 + 白色文字 + 蓝紫渐变装饰元素
- **留白**：大量垂直留白，section 之间间距明显

### 2.2 导航行为

- **Product**：hover 后出现 Mega Menu，包含产品能力子项（Editor / Browser / Terminal / Agent Manager 等）
- **Use Cases**：hover 后出现下拉面板，列出 Professional / Frontend / Fullstack 等子分类
- **Pricing**：点击跳转到独立 Pricing 页面或锚点
- **Blog**：点击跳转到 Blog 页面或锚点
- **Resources**：hover 后出现大型悬浮面板（左右分栏布局）

### 2.3 Resources 面板

- **布局**：左右分栏，左侧占约 35%（标题+描述文案），右侧占约 65%（链接列表）
- **左侧文案**："Everything you need to stay up-to-date and get help"
- **右侧链接**：Document / Changelog / Support / Press / Releases，每项含 icon + 标题 + 副标题 + 箭头
- **视觉**：玻璃拟态背景（半透明 + backdrop-filter blur），大圆角（约 16px），阴影
- **交互**：hover 链接项有背景高亮和轻微位移，面板平滑出现（opacity + translateY 过渡）
- **位置**：导航栏下方，宽度接近或略窄于页面宽度

### 2.4 Use Cases

- 有下拉菜单或独立页面
- Professional / Frontend / Fullstack 各有独立的标题、描述、特性列表
- Frontend：强调 browser-in-the-loop、visual feedback、responsive building
- Fullstack：强调 verification、testing、artifacts、trust
- Professional：强调 enterprise codebase、parallel agents、knowledge management
- 每个子页面/面板都有 CTA 按钮

### 2.5 视频

- Hero 区域有产品介绍视频
- Product section 有 demo 视频
- 视频带圆角边框和发光效果
- 有 poster/预览图
- 点击播放按钮可播放

### 2.6 响应式

- 桌面（1440px+）：完整导航栏 + 全部 Mega Menu
- 桌面（1024-1440px）：布局自适应，间距缩小
- 移动端（<768px）：导航变为 Hamburger 菜单，内容单列布局

---

## 3. 快速运行

```bash
# 进入项目目录
cd question-2/code

# 安装依赖
npm install

# 开发模式（http://127.0.0.1:5173）
npm run dev

# 生产构建
npm run build

# 预览构建产物
npm run preview
```

### 调试模式

在 URL 中添加 `?debug=1` 可在右下角显示粒子系统 FPS 和粒子数量：

```
http://127.0.0.1:5173/?debug=1
```

---

## 4. 官网结构复刻说明

### 4.1 导航层级

| 导航项 | 类型 | 内容 |
|--------|------|------|
| **Product** | Mega Menu | Overview / Agent Manager / Editor / Browser / Terminal |
| **Use Cases** | Mega Menu + Tab 面板 | Professional / Frontend / Fullstack |
| **Pricing** | 锚点跳转 | Free / Pro / Enterprise 三栏 |
| **Blog** | 锚点跳转 | 3 张文章卡片 |
| **Resources** | Mega Menu | Document / Changelog / Support / Press / Releases |

### 4.2 Resources 悬浮菜单

实现方式：**hover + click 触发的 Mega Menu**

- 左侧标题："Everything you need to stay up-to-date and get help"
- 右侧 5 个链接项，每项包含 emoji icon + 标题 + 副标题 + 箭头
- 链接列表：

| 项目 | href | 副标题 |
|------|------|--------|
| Documentation | `/docs/get-started` | Start building with Antigravity |
| Changelog | `/changelog` | See what changed recently |
| Support | `/support` | Get help and troubleshooting |
| Press | `/press` | Brand resources and announcements |
| Releases | `/releases` | Download and release notes |

交互特性：
- hover 触发打开（延迟关闭 250ms 避免闪烁）
- click 切换开关
- 点击外部关闭
- ESC 关闭
- 移动端降级为 accordion

### 4.3 Use Cases 分层

实现方式：**Tab 切换面板**

选择理由：原站 Use Cases 是独立页面或面板，使用 Tab 切换可以在单页内模拟页面切换体验，同时保持导航的即时响应。每个 tab 内容包含完整的文案、特性列表、CTA 和缩略图。

| Tab | 标题 | 核心场景 |
|-----|------|----------|
| **Professional** | Enterprise codebase & parallel agents | 大型代码库管理、并行 Agent 编排、知识管理、工作流自动化 |
| **Frontend** | Visual, responsive frontend development | Browser-in-the-loop、Visual feedback、响应式构建 |
| **Fullstack** | Verification-first fullstack development | 验证与测试、Artifact 通信、信任与透明 |

### 4.4 视频区域

实现方式：**真实 MP4 视频 + 自定义播放控件**

- Hero 区域：播放 `Welcome to Google Antigravity 🚀_2160p.mp4`
- Product 区域：播放 `an-agent-first-experience.mp4`
- Use Case 缩略图：点击打开视频弹窗播放对应视频
- 所有视频均使用项目 `resources/` 目录下的真实 .mp4 文件
- 视频控件：播放/暂停按钮、点击视频切换播放、键盘 Enter/Space 支持

---

## 5. 粒子系统

### 5.1 三层粒子

| 层级 | 粒子数 | 半径 | 透明度 | 特点 |
|------|--------|------|--------|------|
| **dust** | 220 | 0.8–2.4px | 0.22–0.58 | 背景星尘，缓慢漂移 |
| **orbit** | 120 | 1.6–4.8px | 0.55–0.95 | 中心环绕，响应鼠标，高亮 |
| **signal** | 55 | 1.4–3.5px | 0.35–0.72 | 信号粒子，模糊发光效果 |

### 5.2 物理模型

粒子更新遵循以下力学公式：

```
force =
    springK × (basePosition - currentPosition)
  + pointerForce(pointerPosition, currentPosition)
  + noiseForce(time, seed)
  + rippleForce(clickWaves)

velocity = (velocity + force × dt) × damping
position = position + velocity × dt
```

- **Spring 回归**：粒子倾向于回到初始位置
- **鼠标交互**：指针附近的粒子受排斥力 + 漩涡力影响
- **噪声漂移**：使用 Simplex-like 噪声生成有机运动
- **点击波纹**：点击产生向外扩散的冲击波
- **Damping**：速度衰减因子 0.86–0.89

### 5.3 渲染特性

- **DPR 自适应**：最大 DPR 限制为 1.5（balanced 配置）
- **颜色方案**：低饱和蓝、紫、青、白 + 灰色点缀
- **Additive Blending**：`globalCompositeOperation = "lighter"` 实现发光效果
- **形变拉伸**：粒子随速度方向拉伸（stretch factor）
- **页面隐藏暂停**：`document.visibilitychange` 时暂停动画
- **prefers-reduced-motion**：系统偏好减少动画时禁用动画

### 5.4 颜色配置

```typescript
const particlePalette = [
  "#1a73e8",  // Google Blue
  "#4c6fff",  // 鲜蓝
  "#6956d9",  // 紫色
  "#8e4eb8",  // 深紫
  "#c23886",  // 玫红
  "#e54f77",  // 珊瑚红
  "#202124",  // 深灰
  "#5f6368",  // 中灰
];
```

---

## 6. 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vite** | 6.4.x | 构建工具 |
| **TypeScript** | 5.x | 类型安全 |
| **Canvas 2D** | — | 粒子系统渲染 |
| **CSS** | — | 布局、动画、响应式 |
| **Playwright** | (dev) | 截图自动化 |

### 目录结构

```
question-2/
├── code/
│   ├── package.json
│   ├── index.html                  # 完整 HTML 结构
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── scripts/
│   │   └── capture-screenshots.mjs # Playwright 截图脚本
│   ├── public/
│   │   ├── images/                 # 站点图片资源
│   │   └── videos/                 # MP4 视频文件
│   └── src/
│       ├── main.ts                 # 入口：粒子系统 + 导航交互 + 视频播放
│       ├── style.css               # 完整样式（1400+ 行）
│       └── particles/
│           ├── ParticleSystem.ts   # 粒子系统主类
│           ├── Particle.ts         # 单粒子类
│           ├── config.ts           # 粒子配置参数
│           ├── math.ts             # 数学工具函数
│           └── palette.ts          # 颜色调色板
├── screenshot/                     # 自动截图输出目录
├── prompt/                         # 题目相关
└── README.md                       # 本文件
```

---

## 7. 截图验证

### 自动截图

```bash
# 先启动 dev server
npm run dev

# 在另一个终端运行截图脚本
cd question-2/code
npx playwright install chromium  # 首次需要安装
node scripts/capture-screenshots.mjs
```

截图输出到 `question-2/screenshot/`：

| 文件名 | 内容 |
|--------|------|
| `01-home-desktop.png` | 首页桌面首屏（1440×900） |
| `02-resources-menu.png` | Resources 悬浮菜单展开 |
| `03-use-cases-section.png` | Use Cases 面板 |
| `04-video-playing.png` | 视频播放状态 |
| `05-mobile.png` | 移动端布局（390×844） |
| `06-pricing.png` | Pricing 区域 |
| `07-blog.png` | Blog 区域 |

---

## 8. 已知差异

| 差异点 | 说明 |
|--------|------|
| **导航路由** | 原站使用 SPA 路由（/product, /pricing 等），本复刻使用锚点跳转 + Tab 切换模拟页面切换 |
| **Resources 链接** | Document/Changelog/Support/Press/Releases 为模拟 href，点击不会跳转到真实页面 |
| **视频资源** | 使用项目提供的真实 .mp4 文件，非原站 CDN 资源 |
| **图片资源** | 使用项目 resources/ 中的截图和图片，非原站原创素材 |
| **动画细节** | 原站可能使用 WebGL/Three.js，本复刻使用 Canvas 2D |
| **字体** | 使用 Inter + system fonts，非原站 Google Sans |
| **深色模式** | 原站有深色模式，本复刻暂未实现 |

---

## 9. 交互功能清单

- [x] Sticky 顶部导航栏（半透明 + backdrop-filter blur）
- [x] Product hover/click Mega Menu
- [x] Use Cases hover/click Mega Menu
- [x] Resources hover/click Mega Menu
- [x] ESC 关闭所有菜单和弹窗
- [x] 点击外部关闭菜单
- [x] 平滑滚动到锚点
- [x] Use Cases Tab 切换（Professional / Frontend / Fullstack）
- [x] Hero 视频播放/暂停
- [x] Product 视频播放/暂停
- [x] Use Case 缩略图点击打开视频弹窗
- [x] 视频弹窗关闭（ESC / 点击背景 / 关闭按钮）
- [x] 移动端 Hamburger 菜单
- [x] 移动端抽屉式导航
- [x] 移动端 Accordion 子菜单
- [x] 键盘可访问性（Enter/Space 触发按钮）
- [x] 粒子鼠标交互（排斥 + 漩涡）
- [x] 粒子点击波纹
- [x] prefers-reduced-motion 支持
- [x] 页面隐藏时粒子暂停

---

## 10. 运行效果

启动 `npm run dev` 后打开 http://127.0.0.1:5173：

1. **首屏**：看到粒子动画背景 + "Experience liftoff with the next-gen agent platform" 大标题 + 下载按钮 + 视频卡片
2. **导航**：hover Product / Use Cases / Resources 可看到 Mega Menu 展开动画
3. **视频**：点击播放按钮可播放真实 MP4 视频
4. **Use Cases**：滚动到 Use Cases 区域，点击 Tab 切换 Professional / Frontend / Fullstack
5. **Pricing**：三栏定价卡片，中间 Pro 卡片高亮
6. **Blog**：三张文章卡片，hover 有上浮效果
7. **Footer**：四列链接 + 版权信息
8. **移动端**：缩小浏览器窗口，导航变为 Hamburger 菜单