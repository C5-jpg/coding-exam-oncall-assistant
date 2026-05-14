import type { Bounds, ParticleDrawState } from "./Particle";

export class Renderer {
  private context: CanvasRenderingContext2D;
  private dpr = 1;
  private backgroundCanvas = document.createElement("canvas");
  private backgroundContext: CanvasRenderingContext2D;
  bounds: Bounds = { width: 0, height: 0 };

  constructor(private readonly canvas: HTMLCanvasElement, private readonly dprCap: number) {
    const context = canvas.getContext("2d", { alpha: true });
    if (!context) {
      throw new Error("Canvas 2D context is not available.");
    }
    this.context = context;

    const backgroundContext = this.backgroundCanvas.getContext("2d", { alpha: false });
    if (!backgroundContext) {
      throw new Error("Background canvas context is not available.");
    }
    this.backgroundContext = backgroundContext;
  }

  resize(): Bounds {
    const width = window.innerWidth;
    const height = window.innerHeight;
    this.dpr = Math.min(window.devicePixelRatio || 1, this.dprCap);
    this.canvas.width = Math.floor(width * this.dpr);
    this.canvas.height = Math.floor(height * this.dpr);
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
    this.context.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.bounds = { width, height };
    this.renderStaticBackground();
    return this.bounds;
  }

  clear(): void {
    const ctx = this.context;
    const { width, height } = this.bounds;
    ctx.globalCompositeOperation = "source-over";
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    ctx.drawImage(this.backgroundCanvas, 0, 0, width, height);
  }

  private renderStaticBackground(): void {
    const { width, height } = this.bounds;
    this.backgroundCanvas.width = Math.max(1, Math.floor(width * this.dpr));
    this.backgroundCanvas.height = Math.max(1, Math.floor(height * this.dpr));
    const ctx = this.backgroundContext;
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    const base = ctx.createLinearGradient(0, 0, width, height);
    base.addColorStop(0, "#ffffff");
    base.addColorStop(0.42, "#fbfbfa");
    base.addColorStop(1, "#f4f6fb");
    ctx.fillStyle = base;
    ctx.fillRect(0, 0, width, height);

    const halo = ctx.createRadialGradient(width * 0.5, height * 0.43, 0, width * 0.5, height * 0.43, width * 0.48);
    halo.addColorStop(0, "rgba(255, 255, 255, 0.96)");
    halo.addColorStop(0.44, "rgba(255, 255, 255, 0.62)");
    halo.addColorStop(1, "rgba(229, 234, 247, 0.12)");
    ctx.fillStyle = halo;
    ctx.fillRect(0, 0, width, height);

    const vignette = ctx.createRadialGradient(width * 0.18, height * 0.5, 0, width * 0.18, height * 0.5, width * 0.74);
    vignette.addColorStop(0, "rgba(255, 255, 255, 0)");
    vignette.addColorStop(0.58, "rgba(255, 255, 255, 0)");
    vignette.addColorStop(1, "rgba(209, 216, 240, 0.25)");
    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, width, height);
  }

  drawParticles(particles: ParticleDrawState[]): void {
    const ctx = this.context;
    for (const particle of particles) {
      ctx.save();
      ctx.translate(particle.x, particle.y);
      ctx.rotate(particle.rotation);
      ctx.scale(particle.scaleX, particle.scaleY);
      ctx.globalAlpha = particle.opacity;
      ctx.globalCompositeOperation = "source-over";
      ctx.shadowColor = particle.color;
      ctx.shadowBlur = particle.blur;
      ctx.fillStyle = particle.color;

      if (particle.isCapsule) {
        this.roundedCapsule(ctx, particle.radius * 3.6, particle.radius * 1.28, particle.radius);
      } else {
        ctx.beginPath();
        ctx.ellipse(0, 0, particle.radius, particle.radius, 0, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
  }

  drawRipples(ripples: Array<{ x: number; y: number; age: number; strength: number }>): void {
    const ctx = this.context;
    ctx.save();
    ctx.globalCompositeOperation = "multiply";
    for (const ripple of ripples) {
      const progress = Math.min(1, ripple.age / 1.15);
      const radius = Math.pow(progress, 0.72) * 560;
      const alpha = (1 - progress) * 0.16 * ripple.strength;
      ctx.strokeStyle = `rgba(96, 95, 214, ${alpha})`;
      ctx.lineWidth = 1 + (1 - progress) * 2.2;
      ctx.beginPath();
      ctx.arc(ripple.x, ripple.y, radius, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();
  }

  private roundedCapsule(ctx: CanvasRenderingContext2D, width: number, height: number, radius: number): void {
    const x = -width / 2;
    const y = -height / 2;
    const r = Math.min(radius, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + width - r, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + r);
    ctx.lineTo(x + width, y + height - r);
    ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
    ctx.lineTo(x + r, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.fill();
  }
}
