import { clamp, distance } from '../utils/math';
import { createRandom, range } from '../utils/seededRandom';
import { particleColors, particleConfig } from './config';
import type { PointerState } from './pointer';

type ParticleMode = 'dot' | 'dash';

type Particle = {
  baseX: number;
  baseY: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  opacity: number;
  color: string;
  phase: number;
  rotation: number;
  angularVelocity: number;
  mode: ParticleMode;
  layer: number;
};

export type FieldMode = 'hero' | 'product' | 'card' | 'download';

const palette = [
  particleColors.blue,
  particleColors.softBlue,
  particleColors.purple,
  particleColors.red,
  particleColors.orange,
  particleColors.gray,
];

export class ParticleField {
  private particles: Particle[] = [];
  private width = 0;
  private height = 0;
  private random = createRandom(20261114);

  constructor(private readonly mode: FieldMode) {}

  resize(width: number, height: number, mobile: boolean) {
    this.width = width;
    this.height = height;
    this.random = createRandom(this.seedForMode());
    this.particles = [];
    const count = this.countForMode(mobile);
    for (let i = 0; i < count; i += 1) {
      this.particles.push(this.createParticle(i));
    }
  }

  draw(ctx: CanvasRenderingContext2D, dt: number, elapsed: number, pointer: PointerState, reducedMotion: boolean) {
    if (this.mode === 'product') {
      this.drawRibbon(ctx, dt, elapsed, pointer, reducedMotion);
      return;
    }

    ctx.save();
    ctx.globalCompositeOperation = 'source-over';
    for (const p of this.particles) {
      this.updateParticle(p, dt, elapsed, pointer, reducedMotion);
      this.drawParticle(ctx, p, pointer);
    }
    ctx.restore();
  }

  private seedForMode() {
    if (this.mode === 'product') return 93817;
    if (this.mode === 'card') return 51823;
    if (this.mode === 'download') return 76641;
    return 26031;
  }

  private countForMode(mobile: boolean) {
    if (this.mode === 'product') return mobile ? particleConfig.ribbonMobileCount : particleConfig.ribbonDesktopCount;
    if (this.mode === 'card') return mobile ? 120 : 220;
    if (this.mode === 'download') return mobile ? 180 : 420;
    return mobile ? particleConfig.heroMobileCount : particleConfig.heroDesktopCount;
  }

  private createParticle(index: number): Particle {
    if (this.mode === 'product') return this.createRibbonParticle(index);

    const leftCluster = this.mode === 'hero' && this.random() < 0.42;
    const x = leftCluster
      ? Math.pow(this.random(), 1.7) * this.width * 0.56
      : this.random() * this.width;
    const y = leftCluster
      ? range(this.random, this.height * -0.05, this.height * 0.84)
      : this.random() * this.height;
    const layer = this.random() < 0.18 ? 2 : this.random() < 0.55 ? 1 : 0;
    const accent = leftCluster && this.random() < 0.55;
    const color = accent ? palette[Math.floor(range(this.random, 1, 5))] : palette[this.random() < 0.72 ? 1 : 5];
    const mode: ParticleMode = this.random() < 0.22 ? 'dash' : 'dot';

    return {
      baseX: x,
      baseY: y,
      x,
      y,
      vx: range(this.random, -3, 3),
      vy: range(this.random, -3, 3),
      radius: range(this.random, 0.65, this.mode === 'hero' ? 1.55 : 2.2) * (1 + layer * 0.2),
      opacity: range(this.random, 0.08, this.mode === 'hero' ? 0.48 : 0.32),
      color,
      phase: range(this.random, 0, Math.PI * 2),
      rotation: range(this.random, 0, Math.PI * 2),
      angularVelocity: range(this.random, -0.28, 0.28),
      mode,
      layer,
    };
  }

  private createRibbonParticle(index: number): Particle {
    const columns = Math.max(34, Math.floor(Math.sqrt(this.countForMode(false)) * 1.18));
    const row = Math.floor(index / columns);
    const col = index % columns;
    const u = col / (columns - 1);
    const v = (row % columns) / (columns - 1);
    const angle = u * Math.PI * 1.42 - Math.PI * 0.2;
    const band = (v - 0.5) * 170;
    const centerX = this.width * 0.78 + Math.cos(angle) * this.width * 0.26;
    const centerY = this.height * 0.45 + Math.sin(angle) * this.height * 0.38;
    const x = centerX + Math.cos(angle + Math.PI / 2) * band;
    const y = centerY + Math.sin(angle + Math.PI / 2) * band;
    return {
      baseX: x,
      baseY: y,
      x,
      y,
      vx: 0,
      vy: 0,
      radius: range(this.random, 1.15, 1.9),
      opacity: range(this.random, 0.28, 0.78),
      color: particleColors.blue,
      phase: range(this.random, 0, Math.PI * 2),
      rotation: 0,
      angularVelocity: 0,
      mode: 'dot',
      layer: 1,
    };
  }

  private updateParticle(p: Particle, dt: number, elapsed: number, pointer: PointerState, reducedMotion: boolean) {
    const timeScale = reducedMotion ? 0.08 : 1;
    const noiseX = Math.sin(elapsed * 0.0012 + p.phase) * 0.018 * (p.layer + 1);
    const noiseY = Math.cos(elapsed * 0.001 + p.phase * 0.7) * 0.014 * (p.layer + 1);
    const targetX = p.baseX + Math.sin(elapsed * 0.00022 + p.phase) * (8 + p.layer * 4);
    const targetY = p.baseY + Math.cos(elapsed * 0.00018 + p.phase) * (7 + p.layer * 3);

    p.vx += (targetX - p.x) * particleConfig.spring * dt * timeScale + noiseX * dt;
    p.vy += (targetY - p.y) * particleConfig.spring * dt * timeScale + noiseY * dt;

    if (pointer.active) {
      const d = distance(p.x, p.y, pointer.x, pointer.y);
      const radius = particleConfig.pointerRadius * (1 + pointer.hoverBoost * 0.25);
      if (d < radius && d > 0.1) {
        const force = (1 - d / radius) ** 2 * particleConfig.pointerStrength;
        p.vx += ((p.x - pointer.x) / d) * force * dt * 3.2;
        p.vy += ((p.y - pointer.y) / d) * force * dt * 3.2;
      }
    }

    if (pointer.pulseAge < 0.9) {
      const d = distance(p.x, p.y, pointer.pulseX, pointer.pulseY);
      const wave = pointer.pulseAge * 360;
      const band = Math.abs(d - wave);
      if (band < 46 && d > 0.1) {
        const force = (1 - band / 46) * (1 - pointer.pulseAge) * 1.2;
        p.vx += ((p.x - pointer.pulseX) / d) * force * dt * 4;
        p.vy += ((p.y - pointer.pulseY) / d) * force * dt * 4;
      }
    }

    p.vx *= particleConfig.damping;
    p.vy *= particleConfig.damping;
    const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
    if (speed > particleConfig.maxVelocity) {
      p.vx = (p.vx / speed) * particleConfig.maxVelocity;
      p.vy = (p.vy / speed) * particleConfig.maxVelocity;
    }
    p.x += p.vx * dt * timeScale;
    p.y += p.vy * dt * timeScale;
    p.rotation += p.angularVelocity * dt * timeScale + Math.atan2(p.vy, p.vx) * 0.004;
  }

  private drawParticle(ctx: CanvasRenderingContext2D, p: Particle, pointer: PointerState) {
    const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
    const alpha = clamp(p.opacity + pointer.hoverBoost * 0.04 + Math.min(speed / 150, 0.18), 0.02, 0.82);
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.rotation);
    ctx.fillStyle = `rgba(${p.color}, ${alpha})`;
    if (p.mode === 'dash') {
      const length = clamp(p.radius * (2.4 + speed * 0.08), 2, 6);
      ctx.fillRect(-length / 2, -p.radius * 0.45, length, Math.max(1, p.radius * 0.8));
    } else {
      ctx.beginPath();
      ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  private drawRibbon(ctx: CanvasRenderingContext2D, dt: number, elapsed: number, pointer: PointerState, reducedMotion: boolean) {
    ctx.save();
    for (const p of this.particles) {
      const wave = reducedMotion ? 0 : Math.sin(elapsed * 0.001 + p.phase) * 3.4;
      p.x = p.baseX + wave;
      p.y = p.baseY + Math.cos(elapsed * 0.0008 + p.phase) * 2.6;
      if (pointer.active) {
        const d = distance(p.x, p.y, pointer.x, pointer.y);
        if (d < 170 && d > 0.1) {
          const push = (1 - d / 170) * 13;
          p.x += ((p.x - pointer.x) / d) * push;
          p.y += ((p.y - pointer.y) / d) * push;
        }
      }
      const edgeFade = clamp(p.x / this.width, 0.2, 1);
      ctx.fillStyle = `rgba(${p.color}, ${p.opacity * edgeFade})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fill();
    }
    if (!reducedMotion) pointer.pulseAge += dt * 0.016;
    ctx.restore();
  }
}
