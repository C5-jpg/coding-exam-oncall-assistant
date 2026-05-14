import { particlePalette, type LayerSettings, type QualityProfile, subtlePalette } from "./config";
import type { PointerState } from "./pointer";
import { clamp, distance, easeOutCubic, mapRange, TAU } from "../utils/math";
import { hash, pickSeeded, seededRange, signedNoise } from "../utils/random";

export interface Bounds {
  width: number;
  height: number;
}

export interface ParticleDrawState {
  x: number;
  y: number;
  radius: number;
  opacity: number;
  color: string;
  rotation: number;
  scaleX: number;
  scaleY: number;
  blur: number;
  layer: number;
  isCapsule: boolean;
}

export class Particle {
  baseX = 0;
  baseY = 0;
  x = 0;
  y = 0;
  vx = 0;
  vy = 0;
  ax = 0;
  ay = 0;
  radius = 1;
  scale = 1;
  opacity = 1;
  color = "#1a73e8";
  angularVelocity = 0;
  rotation = 0;
  phase = 0;
  noiseSeed = 0;
  targetX = 0;
  targetY = 0;
  interactionWeight = 1;
  lifetime = 1;
  loopProgress = 0;
  isCapsule = false;

  private orbitAngle = 0;
  private orbitRadiusX = 0;
  private orbitRadiusY = 0;
  private speed = 0.1;
  private layerIndex = 0;

  constructor(
    private readonly seed: number,
    private readonly layer: LayerSettings,
    layerIndex: number,
    bounds: Bounds,
    reducedMotion: boolean,
    private readonly profile: QualityProfile,
  ) {
    this.layerIndex = layerIndex;
    this.reset(bounds, reducedMotion);
  }

  reset(bounds: Bounds, reducedMotion: boolean): void {
    this.noiseSeed = this.seed * 1.381;
    this.phase = seededRange(this.seed + 4, 0, TAU);
    this.loopProgress = hash(this.seed + 9);
    this.radius = seededRange(this.seed + 10, this.layer.radius[0], this.layer.radius[1]);
    this.opacity = seededRange(this.seed + 20, this.layer.opacity[0], this.layer.opacity[1]);
    this.speed = seededRange(this.seed + 30, this.layer.speed[0], this.layer.speed[1]) * this.profile.motionScale;
    this.angularVelocity = seededRange(this.seed + 40, -0.32, 0.32);
    this.rotation = seededRange(this.seed + 50, 0, TAU);
    this.interactionWeight = seededRange(this.seed + 60, 0.6, 1.35) * this.layer.interaction;
    this.lifetime = seededRange(this.seed + 70, 8, 18);
    this.isCapsule = this.layer.name === "orbit" && hash(this.seed + 80) > 0.34;

    if (this.layer.name === "orbit") {
      this.assignOrbitPosition(bounds, reducedMotion);
      this.color = pickSeeded(particlePalette, this.seed + 100);
    } else if (this.layer.name === "signal") {
      this.assignSignalPosition(bounds);
      this.color = pickSeeded(particlePalette, this.seed + 200);
    } else {
      this.assignDustPosition(bounds);
      this.color = pickSeeded(subtlePalette, this.seed + 300);
    }

    this.x = this.baseX + seededRange(this.seed + 400, -8, 8);
    this.y = this.baseY + seededRange(this.seed + 410, -8, 8);
    this.targetX = this.baseX;
    this.targetY = this.baseY;
  }

  update(dt: number, elapsed: number, bounds: Bounds, pointer: PointerState, reducedMotion: boolean): void {
    this.loopProgress = (this.loopProgress + dt / this.lifetime) % 1;
    this.rotation += this.angularVelocity * dt;

    this.computeTarget(elapsed, bounds, reducedMotion);
    this.ax = (this.targetX - this.x) * this.layer.spring;
    this.ay = (this.targetY - this.y) * this.layer.spring;

    this.applyPointerForces(pointer);
    this.applyRipples(pointer);

    this.vx += this.ax * dt * 60;
    this.vy += this.ay * dt * 60;
    const damping = Math.pow(this.layer.damping, dt * 60);
    this.vx *= damping;
    this.vy *= damping;
    this.x += this.vx * dt * 60;
    this.y += this.vy * dt * 60;

    if (this.x < -80 || this.x > bounds.width + 80 || this.y < -80 || this.y > bounds.height + 80) {
      this.vx *= -0.22;
      this.vy *= -0.22;
      this.x = clamp(this.x, -80, bounds.width + 80);
      this.y = clamp(this.y, -80, bounds.height + 80);
    }
  }

  getDrawState(pointer: PointerState): ParticleDrawState {
    const velocity = Math.hypot(this.vx, this.vy);
    const stretch = clamp(velocity / 11, 0, this.isCapsule ? 2.8 : 1.4);
    const nearPointer =
      pointer.isActive && distance(this.x, this.y, pointer.smoothX, pointer.smoothY) < 180 ? 1 : 0;
    const hoverLift = pointer.isHovering ? 0.14 : 0;
    const opacity = clamp(this.opacity + nearPointer * 0.2 + hoverLift, 0.03, 1);

    return {
      x: this.x,
      y: this.y,
      radius: this.radius * (1 + nearPointer * 0.42),
      opacity,
      color: this.color,
      rotation: Math.atan2(this.vy, this.vx) || this.rotation,
      scaleX: this.isCapsule ? 2.2 + stretch : 1 + stretch * 0.36,
      scaleY: this.isCapsule ? 0.58 + stretch * 0.05 : 1 - stretch * 0.08,
      blur: this.layer.blur * this.profile.blurScale,
      layer: this.layerIndex,
      isCapsule: this.isCapsule,
    };
  }

  private assignOrbitPosition(bounds: Bounds, reducedMotion: boolean): void {
    const desktop = bounds.width >= 760;
    const centerX = desktop ? bounds.width * 0.33 : bounds.width * 0.52;
    const centerY = desktop ? bounds.height * 0.51 : bounds.height * 0.36;
    const radiusX = desktop ? bounds.width * 0.35 : bounds.width * 0.55;
    const radiusY = desktop ? bounds.height * 0.44 : bounds.height * 0.32;

    const arcStart = desktop ? Math.PI * 0.96 : Math.PI * 1.1;
    const arcEnd = desktop ? Math.PI * 1.54 : Math.PI * 1.82;
    this.orbitAngle = seededRange(this.seed + 500, arcStart, arcEnd);
    this.orbitRadiusX = radiusX * seededRange(this.seed + 510, 0.78, 1.05);
    this.orbitRadiusY = radiusY * seededRange(this.seed + 520, 0.72, 1.0);

    const jitter = reducedMotion ? 0 : seededRange(this.seed + 530, -18, 18);
    this.baseX = centerX + Math.cos(this.orbitAngle) * this.orbitRadiusX + jitter;
    this.baseY = centerY + Math.sin(this.orbitAngle) * this.orbitRadiusY + seededRange(this.seed + 540, -10, 10);
  }

  private assignDustPosition(bounds: Bounds): void {
    const bias = hash(this.seed + 600);
    if (bias < 0.58) {
      this.baseX = seededRange(this.seed + 610, 0, bounds.width);
      this.baseY = seededRange(this.seed + 620, 0, bounds.height);
    } else {
      this.baseX = seededRange(this.seed + 630, bounds.width * 0.05, bounds.width * 0.95);
      this.baseY = seededRange(this.seed + 640, bounds.height * 0.12, bounds.height * 0.88);
    }
  }

  private assignSignalPosition(bounds: Bounds): void {
    const desktop = bounds.width >= 760;
    const centerX = desktop ? bounds.width * 0.5 : bounds.width * 0.5;
    const centerY = desktop ? bounds.height * 0.55 : bounds.height * 0.42;
    const spreadX = desktop ? bounds.width * 0.5 : bounds.width * 0.72;
    const spreadY = desktop ? bounds.height * 0.5 : bounds.height * 0.42;
    const angle = seededRange(this.seed + 700, 0, TAU);
    const radius = Math.pow(hash(this.seed + 710), 0.48);
    this.baseX = centerX + Math.cos(angle) * spreadX * radius;
    this.baseY = centerY + Math.sin(angle) * spreadY * radius;
  }

  private computeTarget(elapsed: number, bounds: Bounds, reducedMotion: boolean): void {
    const drift = (reducedMotion ? this.layer.drift * 0.2 : this.layer.drift) * this.profile.motionScale;
    const noiseX = (signedNoise(this.noiseSeed, elapsed, this.speed) - 0.5) * drift;
    const noiseY = (signedNoise(this.noiseSeed + 17, elapsed, this.speed * 0.82) - 0.5) * drift;

    if (this.layer.name === "orbit") {
      const orbitShift = reducedMotion ? 0 : Math.sin(elapsed * this.speed + this.phase) * 0.024;
      const centerX = bounds.width >= 760 ? bounds.width * 0.33 : bounds.width * 0.52;
      const centerY = bounds.width >= 760 ? bounds.height * 0.51 : bounds.height * 0.36;
      const angle = this.orbitAngle + orbitShift;
      this.targetX = centerX + Math.cos(angle) * this.orbitRadiusX + noiseX;
      this.targetY = centerY + Math.sin(angle) * this.orbitRadiusY + noiseY;
    } else {
      const parallax = this.layer.name === "signal" ? 36 : 18;
      this.targetX = this.baseX + noiseX;
      this.targetY = this.baseY + noiseY - window.scrollY * 0.03 * parallax;
    }
  }

  private applyPointerForces(pointer: PointerState): void {
    if (!pointer.isActive) {
      return;
    }

    const dx = this.x - pointer.smoothX;
    const dy = this.y - pointer.smoothY;
    const dist = Math.max(1, Math.hypot(dx, dy));
    const radius = pointer.isHovering ? 285 : 230;
    if (dist > radius) {
      return;
    }

    const normalized = 1 - dist / radius;
    const falloff = normalized * normalized;
    const force = falloff * this.interactionWeight * (pointer.isHovering ? 1.55 : 1);
    const nx = dx / dist;
    const ny = dy / dist;
    const swirl = this.layer.name === "orbit" ? 0.62 : 0.34;
    this.ax += nx * force * 2.4 + -ny * force * swirl;
    this.ay += ny * force * 2.4 + nx * force * swirl;
    this.rotation += force * 0.07;
  }

  private applyRipples(pointer: PointerState): void {
    for (const ripple of pointer.ripples) {
      const progress = clamp(ripple.age / 1.15, 0, 1);
      const waveRadius = easeOutCubic(progress) * 560;
      const dist = distance(this.x, this.y, ripple.x, ripple.y);
      const band = mapRange(progress, 0, 1, 24, 56);
      const influence = Math.max(0, 1 - Math.abs(dist - waveRadius) / band) * (1 - progress);
      if (influence <= 0) {
        continue;
      }

      const nx = (this.x - ripple.x) / Math.max(dist, 1);
      const ny = (this.y - ripple.y) / Math.max(dist, 1);
      this.ax += nx * influence * ripple.strength * 4.3 * this.interactionWeight;
      this.ay += ny * influence * ripple.strength * 4.3 * this.interactionWeight;
      this.opacity = clamp(this.opacity + influence * 0.025, this.layer.opacity[0], 1);
      this.scale = 1 + influence * 0.4;
    }
  }
}
