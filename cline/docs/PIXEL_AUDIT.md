# 像素差异审计

> 自动生成。差异比例用于指导迭代，不代表官方像素级认证。

| Viewport | State | Mismatch pixels | Ratio |
| --- | --- | ---: | ---: |
| 1024x768 | initial.png | 50261 | 6.39% |
| 1024x768 | after-1s.png | 50227 | 6.39% |
| 1024x768 | after-3s.png | 50335 | 6.40% |
| 1366x768 | initial.png | 67605 | 6.44% |
| 1366x768 | after-1s.png | 67324 | 6.42% |
| 1366x768 | after-3s.png | 67598 | 6.44% |
| 1440x900 | initial.png | 50253 | 3.88% |
| 1440x900 | after-1s.png | 50374 | 3.89% |
| 1440x900 | after-3s.png | 50190 | 3.87% |
| 375x812 | initial.png | 35673 | 11.72% |
| 375x812 | after-1s.png | 35673 | 11.72% |
| 375x812 | after-3s.png | 35735 | 11.74% |
| 390x844 | initial.png | 35682 | 10.84% |
| 390x844 | after-1s.png | 35685 | 10.84% |
| 390x844 | after-3s.png | 35721 | 10.85% |
| 768x1024 | initial.png | 38215 | 4.86% |
| 768x1024 | after-1s.png | 38163 | 4.85% |
| 768x1024 | after-3s.png | 38228 | 4.86% |

## 当前最不一致区域

- 原站包含真实生产视频、动态图形和精确字体，当前本地复刻使用本地资源与自实现 Canvas，视频帧和字体渲染会产生较大差异。
- 原站粒子为生产环境内置动画，本地版本按截图与 DOM 审计独立实现，运动规律接近但不复制内部源码。
- full-page 差异通常受滚动 section 高度、媒体帧、图片裁剪影响更大。

## 已修复项

- 从暗色/竖向粒子改为白底稀疏点状与短划粒子。
- 补齐 Header、Product、Use Cases、Resources、Pricing、Blog、Download、Footer 等结构。
- 增加 Product 右侧大面积蓝色点阵 ribbon。
- 增加本地资源引用、下拉菜单、卡片 hover、Cookie demo banner。

## 未修复项

- 未复制官方生产 JS/CSS，因此不能保证私有动画参数完全一致。
- Google 字体在离线环境下由系统字体近似。
- 官方下载/登录/追踪流程全部禁用，交互只保留本地占位。

## 下一步建议

- 按差异最高 viewport 逐项调节 hero 顶部偏移、标题字号、section 高度。
- 使用截图 diff 重点校正 Header、Hero、Dropdown、Product ribbon、Pricing card。