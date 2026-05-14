# Antigravity Animation Recreation

> 本项目是 `https://antigravity.google/` 的本地学习型 UI 复刻，不是 Google 官方网站，不提供真实下载、登录、购买、追踪或数据收集能力。

## 1. 项目概述

本项目基于第一阶段审计结果实现 Antigravity 官网首页的本地复刻版本，重点还原：

- 白色背景上的稀疏点状 / 短划粒子动画；
- 顶部 Header、导航、Download CTA；
- Product 页面状态中的蓝色点阵 ribbon；
- Use Cases / Resources 全宽下拉菜单；
- Hero、视频区、Agent-first、Feature Explorer、Use Cases、Pricing、Blog、Download、Footer；
- 卡片 hover、按钮 hover、点击粒子 pulse、移动端响应式；
- 本地资源化的视频、图片、缩略图，不依赖远端资源渲染页面主体。

## 2. 技术栈

| 类型 | 选择 |
| --- | --- |
| 构建工具 | Vite |
| UI | React + TypeScript |
| 动画 | Canvas 2D + requestAnimationFrame |
| 视觉资源 | `resources` 下载资源拷贝到 `public/assets` |
| 截图 | Playwright |
| 像素对比 | pixelmatch + pngjs |

选择 Canvas 2D 的原因：原站粒子主要是稀疏点阵、短划线、局部 ribbon 和卡片内装饰，Canvas 2D 足以实现高帧率和高可控性，且比 WebGL 更容易调参和解释。

## 3. 目录结构

```text
cline/code
├── index.html
├── package.json
├── vite.config.ts
├── src
│   ├── App.tsx
│   ├── components
│   │   ├── Header.tsx
│   │   ├── Hero.tsx
│   │   ├── ProductSection.tsx
│   │   ├── FeatureExplorer.tsx
│   │   ├── UseCases.tsx
│   │   ├── Pricing.tsx
│   │   ├── BlogGrid.tsx
│   │   ├── DownloadSection.tsx
│   │   ├── CookieBanner.tsx
│   │   └── Footer.tsx
│   ├── particles
│   │   ├── CanvasLayer.tsx
│   │   ├── ParticleField.ts
│   │   ├── config.ts
│   │   └── pointer.ts
│   ├── data
│   │   ├── nav.ts
│   │   └── sections.ts
│   ├── styles
│   │   ├── base.css
│   │   ├── layout.css
│   │   └── components.css
│   └── utils
│       ├── math.ts
│       └── seededRandom.ts
└── scripts
    ├── capture-reference.mjs
    ├── capture-local.mjs
    └── pixel-diff.mjs
```

## 4. 快速运行

```bash
cd D:\reps\26H1_kimi\coding-exam\cline\code
npm install
npm run dev
```

浏览器打开：

```text
http://127.0.0.1:5173/
```

构建与预览：

```bash
npm run build
npm run preview
```

## 5. 截图与像素对比

先启动本地开发服务器：

```bash
npm run dev
```

另开一个终端生成本地截图：

```bash
npm run screenshot
```

如果需要重新采集原站参考截图：

```bash
npm run screenshot:reference
```

生成像素差异报告：

```bash
npm run diff
```

输出位置：

```text
cline/screenshots/local
cline/screenshots/reference
cline/screenshots/diff
cline/docs/PIXEL_AUDIT.md
```

## 6. 粒子系统说明

粒子系统在 `src/particles/ParticleField.ts` 中实现，核心特性：

- `seededRandom` 固定随机分布，刷新后视觉稳定；
- Canvas DPR 自适应，移动端降低 DPR 和粒子数量；
- hero 模式：白底、稀疏蓝/灰/红/橙/紫点与短划粒子；
- product 模式：右侧大型蓝色点阵 ribbon，模拟原站 Product 页面；
- card/download 模式：卡片内部低强度装饰粒子；
- pointermove：轻微排斥和速度扰动；
- click：短暂波纹 pulse；
- hover：卡片/按钮悬停时增强局部粒子活性；
- `prefers-reduced-motion` 下显著降低运动。

## 7. 已知差异

- 未复制原站生产 JS/CSS，所有交互和 Canvas 均为独立实现。
- 字体使用系统字体近似 Google Sans Flex，离线环境会有渲染差异。
- 视频和图片来自本地学习素材，部分帧与原站首帧不完全一致。
- 官方下载、登录、购买、追踪均被禁用，只保留本地占位交互。
- 粒子运动基于截图和视觉审计近似，不声称完全复刻原站内部私有算法。

## 8. 法务与品牌说明

本项目仅用于本地学习、面试编程题和 UI 还原练习。页面中出现的 Antigravity / Google 风格元素仅作为复刻对象的视觉占位，不代表 Google 官方，不得部署为可误导用户的公开网站，不得用于分发软件、收集用户信息或冒充官方服务。
