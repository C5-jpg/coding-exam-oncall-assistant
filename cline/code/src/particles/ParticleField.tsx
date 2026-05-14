import { useEffect, useRef, useCallback } from 'react';
import { createSeededRandom } from './seededRandom';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
  opacity: number;
  isDash: boolean;
  dashLen: number;
  dashAngle: number;
}

interface ParticleFieldProps {
  width?: number;
  height?: number;
  density?: number; // particles per 10000 sq px
  className?: string;
  style?: React.CSSProperties;
}

const COLORS = [
  '#3f63ff', '#5c6ff0', // blue
  '#8a58d6',           // purple
  '#ea4335',           // red
  '#fbbc04',           // orange
  '#9aa0a6',           // gray
  '#c4c9d0',           // light gray
];

function buildParticles(
  w: number, h: number, count: number, seed: number
): Particle[] {
  const rng = createSeededRandom(seed);
  const particles: Particle[] = [];
  for (let i = 0; i < count; i++) {
    const isAccent = rng() < 0.15;
    const colorIdx = isAccent
      ? Math.floor(rng() * 4) // first 4 = colored
      : 4 + Math.floor(rng() * 3); // last 3 = gray
    const isDash = rng() < 0.25;
    particles.push({
      x: rng() * w,
      y: rng() * h,
      vx: (rng() - 0.5) * 0.3,
      vy: (rng() - 0.5) * 0.2,
      size: isDash ? 1.5 : (rng() < 0.7 ? 1.5 : 2.5),
      color: COLORS[colorIdx],
      opacity: 0.15 + rng() * 0.35,
      isDash,
      dashLen: isDash ? 3 + rng() * 6 : 0,
      dashAngle: rng() * Math.PI * 2,
    });
  }
  return particles;
}

export default function ParticleField({
  density = 0.5,
  className,
  style,
}: ParticleFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animRef = useRef<number>(0);
  const sizeRef = useRef({ w: 0, h: 0 });

  const getParticleCount = useCallback((w: number, h: number) => {
    const area = w * h;
    const isMobile = w < 768;
    const base = Math.floor((area / 10000) * density);
    if (isMobile) return Math.min(base, Math.floor(base * 0.4));
    if (w < 1024) return Math.floor(base * 0.7);
    return base;
  }, [density]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const parent = canvas.parentElement;
    if (!parent) return;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = parent.getBoundingClientRect();
      const w = rect.width;
      const h = rect.height;
      sizeRef.current = { w, h };
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;

      const ctx = canvas.getContext('2d');
      if (ctx) ctx.scale(dpr, dpr);

      const count = getParticleCount(w, h);
      particlesRef.current = buildParticles(w, h, count, 42);
    };

    resize();
    window.addEventListener('resize', resize);

    const animate = () => {
      const ctx = canvas?.getContext('2d');
      if (!ctx) return;
      const { w, h } = sizeRef.current;

      ctx.clearRect(0, 0, w, h);

      for (const p of particlesRef.current) {
        // Update position
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around
        if (p.x < -10) p.x = w + 10;
        if (p.x > w + 10) p.x = -10;
        if (p.y < -10) p.y = h + 10;
        if (p.y > h + 10) p.y = -10;

        // Slow rotation for dashes
        if (p.isDash) {
          p.dashAngle += 0.002;
        }

        ctx.globalAlpha = p.opacity;

        if (p.isDash) {
          // Short dash
          ctx.beginPath();
          ctx.strokeStyle = p.color;
          ctx.lineWidth = p.size * 0.7;
          ctx.lineCap = 'round';
          const dx = Math.cos(p.dashAngle) * p.dashLen * 0.5;
          const dy = Math.sin(p.dashAngle) * p.dashLen * 0.5;
          ctx.moveTo(p.x - dx, p.y - dy);
          ctx.lineTo(p.x + dx, p.y + dy);
          ctx.stroke();
        } else {
          // Dot
          ctx.beginPath();
          ctx.fillStyle = p.color;
          ctx.arc(p.x, p.y, p.size * 0.5, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      ctx.globalAlpha = 1;
      animRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animRef.current);
    };
  }, [density, getParticleCount]);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
        ...style,
      }}
    />
  );
}