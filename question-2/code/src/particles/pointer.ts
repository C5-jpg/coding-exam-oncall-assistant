import { clamp, lerp } from "../utils/math";

export interface Ripple {
  x: number;
  y: number;
  age: number;
  strength: number;
}

export class PointerState {
  x = 0;
  y = 0;
  smoothX = 0;
  smoothY = 0;
  lastX = 0;
  lastY = 0;
  velocityX = 0;
  velocityY = 0;
  isActive = false;
  isHovering = false;
  scroll = 0;
  ripples: Ripple[] = [];

  constructor(private readonly element: HTMLElement | Window = window) {}

  attach(): void {
    const target = this.element;

    target.addEventListener("pointermove", this.onPointerMove, { passive: true });
    target.addEventListener("pointerleave", this.onPointerLeave, { passive: true });
    target.addEventListener("pointerdown", this.onPointerDown, { passive: true });
    window.addEventListener("scroll", this.onScroll, { passive: true });

    document.querySelectorAll<HTMLElement>("[data-interactive]").forEach((node) => {
      node.addEventListener("pointerenter", this.onInteractiveEnter, { passive: true });
      node.addEventListener("pointerleave", this.onInteractiveLeave, { passive: true });
    });
  }

  detach(): void {
    const target = this.element;

    target.removeEventListener("pointermove", this.onPointerMove);
    target.removeEventListener("pointerleave", this.onPointerLeave);
    target.removeEventListener("pointerdown", this.onPointerDown);
    window.removeEventListener("scroll", this.onScroll);
  }

  update(dt: number): void {
    const smoothing = 1 - Math.pow(0.0006, dt);
    this.smoothX = lerp(this.smoothX, this.x, smoothing);
    this.smoothY = lerp(this.smoothY, this.y, smoothing);
    this.velocityX = (this.smoothX - this.lastX) / Math.max(dt, 0.001);
    this.velocityY = (this.smoothY - this.lastY) / Math.max(dt, 0.001);
    this.lastX = this.smoothX;
    this.lastY = this.smoothY;

    for (const ripple of this.ripples) {
      ripple.age += dt;
    }
    this.ripples = this.ripples.filter((ripple) => ripple.age < 1.25);
  }

  private readonly onPointerMove = (event: Event): void => {
    const pointerEvent = event as PointerEvent;
    this.x = pointerEvent.clientX;
    this.y = pointerEvent.clientY;
    if (!this.isActive) {
      this.smoothX = this.x;
      this.smoothY = this.y;
      this.lastX = this.x;
      this.lastY = this.y;
    }
    this.isActive = true;
  };

  private readonly onPointerLeave = (): void => {
    this.isActive = false;
    this.isHovering = false;
  };

  private readonly onPointerDown = (event: Event): void => {
    const pointerEvent = event as PointerEvent;
    this.ripples.push({
      x: pointerEvent.clientX,
      y: pointerEvent.clientY,
      age: 0,
      strength: clamp(0.78 + Math.hypot(this.velocityX, this.velocityY) / 1600, 0.78, 1.4),
    });
  };

  private readonly onScroll = (): void => {
    const maxScroll = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
    this.scroll = clamp(window.scrollY / maxScroll, 0, 1);
  };

  private readonly onInteractiveEnter = (): void => {
    this.isHovering = true;
  };

  private readonly onInteractiveLeave = (): void => {
    this.isHovering = false;
  };
}
