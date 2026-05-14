import { useEffect, useRef } from 'react';
import { particleConfig } from './config';
import { ParticleField, type FieldMode } from './ParticleField';
import { createPointerState } from './pointer';

type CanvasLayerProps = {
  mode: FieldMode;
  className?: string;
  interactive?: boolean;
};

export function CanvasLayer({ mode, className = '', interactive = true }: CanvasLayerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    const field = new ParticleField(mode);
    const pointer = createPointerState();
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let frame = 0;
    let last = performance.now();
    let width = 0;
    let height = 0;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      width = Math.max(1, rect.width);
      height = Math.max(1, rect.height);
      const mobile = width < 700;
      const dpr = Math.min(window.devicePixelRatio || 1, mobile ? particleConfig.mobileDprCap : particleConfig.dprCap);
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      field.resize(width, height, mobile);
    };

    const animate = (now: number) => {
      const dt = Math.min(2.2, Math.max(0.35, (now - last) / 16.6667));
      last = now;
      ctx.clearRect(0, 0, width, height);
      field.draw(ctx, dt, now, pointer, reducedMotion);
      pointer.hoverBoost += (0 - pointer.hoverBoost) * 0.045;
      pointer.pulseAge += dt * 0.016;
      frame = requestAnimationFrame(animate);
    };

    const onMove = (event: PointerEvent) => {
      if (!interactive) return;
      const rect = canvas.getBoundingClientRect();
      pointer.x = event.clientX - rect.left;
      pointer.y = event.clientY - rect.top;
      pointer.active = true;
    };

    const onLeave = () => {
      pointer.active = false;
    };

    const onClick = (event: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      pointer.pulseX = event.clientX - rect.left;
      pointer.pulseY = event.clientY - rect.top;
      pointer.pulseAge = 0;
    };

    const onBoost = () => {
      pointer.hoverBoost = 1;
    };

    resize();
    frame = requestAnimationFrame(animate);
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);
    canvas.addEventListener('pointermove', onMove);
    canvas.addEventListener('pointerleave', onLeave);
    canvas.addEventListener('pointerdown', onClick);
    window.addEventListener('antigravity:hover-boost', onBoost);

    return () => {
      cancelAnimationFrame(frame);
      ro.disconnect();
      canvas.removeEventListener('pointermove', onMove);
      canvas.removeEventListener('pointerleave', onLeave);
      canvas.removeEventListener('pointerdown', onClick);
      window.removeEventListener('antigravity:hover-boost', onBoost);
    };
  }, [interactive, mode]);

  return <canvas ref={canvasRef} className={`canvas-layer ${className}`} aria-hidden="true" />;
}
