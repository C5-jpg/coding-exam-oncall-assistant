import fs from 'node:fs/promises';
import path from 'node:path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

const root = path.resolve('..');
const referenceRoot = path.join(root, 'screenshots/reference');
const localRoot = path.join(root, 'screenshots/local');
const diffRoot = path.join(root, 'screenshots/diff');
const docsRoot = path.join(root, 'docs');
const states = ['initial.png', 'after-1s.png', 'after-3s.png'];

await fs.mkdir(diffRoot, { recursive: true });
await fs.mkdir(docsRoot, { recursive: true });

const viewports = await fs.readdir(referenceRoot);
const rows = [];

for (const viewport of viewports) {
  for (const state of states) {
    const refPath = path.join(referenceRoot, viewport, state);
    const localPath = path.join(localRoot, viewport, state);
    try {
      const ref = PNG.sync.read(await fs.readFile(refPath));
      const local = PNG.sync.read(await fs.readFile(localPath));
      const width = Math.min(ref.width, local.width);
      const height = Math.min(ref.height, local.height);
      const refCrop = crop(ref, width, height);
      const localCrop = crop(local, width, height);
      const diff = new PNG({ width, height });
      const mismatch = pixelmatch(refCrop.data, localCrop.data, diff.data, width, height, {
        threshold: 0.16,
        includeAA: false,
      });
      const ratio = mismatch / (width * height);
      const outDir = path.join(diffRoot, viewport);
      await fs.mkdir(outDir, { recursive: true });
      await fs.writeFile(path.join(outDir, state), PNG.sync.write(diff));
      rows.push({ viewport, state, mismatch, ratio });
    } catch (error) {
      rows.push({ viewport, state, error: String(error) });
    }
  }
}

const report = [
  '# 像素差异审计',
  '',
  '> 自动生成。差异比例用于指导迭代，不代表官方像素级认证。',
  '',
  '| Viewport | State | Mismatch pixels | Ratio |',
  '| --- | --- | ---: | ---: |',
  ...rows.map((row) =>
    'error' in row
      ? `| ${row.viewport} | ${row.state} | - | ${row.error.replaceAll('|', '\\|')} |`
      : `| ${row.viewport} | ${row.state} | ${row.mismatch} | ${(row.ratio * 100).toFixed(2)}% |`,
  ),
  '',
  '## 当前最不一致区域',
  '',
  '- 原站包含真实生产视频、动态图形和精确字体，当前本地复刻使用本地资源与自实现 Canvas，视频帧和字体渲染会产生较大差异。',
  '- 原站粒子为生产环境内置动画，本地版本按截图与 DOM 审计独立实现，运动规律接近但不复制内部源码。',
  '- full-page 差异通常受滚动 section 高度、媒体帧、图片裁剪影响更大。',
  '',
  '## 已修复项',
  '',
  '- 从暗色/竖向粒子改为白底稀疏点状与短划粒子。',
  '- 补齐 Header、Product、Use Cases、Resources、Pricing、Blog、Download、Footer 等结构。',
  '- 增加 Product 右侧大面积蓝色点阵 ribbon。',
  '- 增加本地资源引用、下拉菜单、卡片 hover、Cookie demo banner。',
  '',
  '## 未修复项',
  '',
  '- 未复制官方生产 JS/CSS，因此不能保证私有动画参数完全一致。',
  '- Google 字体在离线环境下由系统字体近似。',
  '- 官方下载/登录/追踪流程全部禁用，交互只保留本地占位。',
  '',
  '## 下一步建议',
  '',
  '- 按差异最高 viewport 逐项调节 hero 顶部偏移、标题字号、section 高度。',
  '- 使用截图 diff 重点校正 Header、Hero、Dropdown、Product ribbon、Pricing card。',
].join('\n');

await fs.writeFile(path.join(docsRoot, 'PIXEL_AUDIT.md'), report, 'utf8');

function crop(source, width, height) {
  if (source.width === width && source.height === height) return source;
  const out = new PNG({ width, height });
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const src = (source.width * y + x) << 2;
      const dst = (width * y + x) << 2;
      out.data[dst] = source.data[src];
      out.data[dst + 1] = source.data[src + 1];
      out.data[dst + 2] = source.data[src + 2];
      out.data[dst + 3] = source.data[src + 3];
    }
  }
  return out;
}
