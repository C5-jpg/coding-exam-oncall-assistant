import { particleConfig, qualityProfiles, type QualityLevel, type QualityProfile } from "./config";
import { Particle, type Bounds } from "./Particle";
import { PointerState } from "./pointer";
import { Renderer } from "./Renderer";

interface RuntimeStats {
  fps: number;
  particles: number;
  reducedMotion: boolean;
}

export class ParticleSystem {
  private readonly renderer: Renderer;
  private readonly pointer = new PointerState(window);
  private particles: Particle[] = [];
  private bounds: Bounds = { width: 0, height: 0 };
  private raf = 0;
  private elapsed = 0;
  private lastTime = performance.now();
  private frameCount = 0;
  private fpsTime = 0;
  private stats: RuntimeStats = { fps: 0, particles: 0, reducedMotion: false };
  private readonly reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  private readonly quality: QualityLevel;
  private readonly profile: QualityProfile;

  constructor(canvas: HTMLCanvasElement, private readonly debugNode?: HTMLElement | null) {
    this.quality = this.resolveQualityLevel();
    this.profile = qualityProfiles[this.quality];
    this.renderer = new Renderer(canvas, this.profile.dprCap);
  }

  start(): void {
    this.pointer.attach();
    this.bounds = this.renderer.resize();
    this.seedParticles();
    window.addEventListener("resize", this.onResize, { passive: true });
    this.reducedMotionQuery.addEventListener("change", this.onMotionPreferenceChange);
    this.raf = window.requestAnimationFrame(this.tick);
  }

  stop(): void {
    window.cancelAnimationFrame(this.raf);
    window.removeEventListener("resize", this.onResize);
    this.reducedMotionQuery.removeEventListener("change", this.onMotionPreferenceChange);
    this.pointer.detach();
  }

  getStats(): RuntimeStats {
    return { ...this.stats };
  }

  private readonly tick = (time: number): void => {
    const dt = Math.min((time - this.lastTime) / 1000, 0.034);
    this.lastTime = time;
    this.elapsed += dt;
    this.pointer.update(dt);

    const reducedMotion = this.reducedMotionQuery.matches;
    for (const particle of this.particles) {
      particle.update(dt, this.elapsed, this.bounds, this.pointer, reducedMotion);
    }

    this.renderer.clear();
    this.renderer.drawParticles(this.particles.map((particle) => particle.getDrawState(this.pointer)));
    this.renderer.drawRipples(this.pointer.ripples);
    this.updateStats(dt, reducedMotion);

    this.raf = window.requestAnimationFrame(this.tick);
  };

  private seedParticles(): void {
    this.particles = [];
    const reducedMotion = this.reducedMotionQuery.matches;
    let seed = 1;
    particleConfig.layers.forEach((layer, layerIndex) => {
      const qualityCount = Math.ceil(layer.count * this.profile.particleScale);
      const count = reducedMotion ? Math.ceil(qualityCount * 0.38) : qualityCount;
      for (let i = 0; i < count; i += 1) {
        this.particles.push(new Particle(seed, layer, layerIndex, this.bounds, reducedMotion, this.profile));
        seed += 1;
      }
    });
    this.stats.particles = this.particles.length;
  }

  private readonly onResize = (): void => {
    this.bounds = this.renderer.resize();
    this.seedParticles();
  };

  private readonly onMotionPreferenceChange = (): void => {
    this.seedParticles();
  };

  private updateStats(dt: number, reducedMotion: boolean): void {
    this.frameCount += 1;
    this.fpsTime += dt;
    if (this.fpsTime >= 0.5) {
      this.stats = {
        fps: Math.round(this.frameCount / this.fpsTime),
        particles: this.particles.length,
        reducedMotion,
      };
      this.frameCount = 0;
      this.fpsTime = 0;
      if (this.debugNode && !this.debugNode.hidden) {
        this.debugNode.textContent = `fps ${this.stats.fps} · particles ${this.stats.particles} · quality ${this.quality} · reduced ${this.stats.reducedMotion}`;
      }
    }
  }

  private resolveQualityLevel(): QualityLevel {
    const value = new URLSearchParams(window.location.search).get("quality");
    if (value === "low" || value === "balanced" || value === "high") {
      return value;
    }
    return "balanced";
  }
}
