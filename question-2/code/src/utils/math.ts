export const TAU = Math.PI * 2;

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

export function lerp(start: number, end: number, amount: number): number {
  return start + (end - start) * amount;
}

export function mapRange(
  value: number,
  inputMin: number,
  inputMax: number,
  outputMin: number,
  outputMax: number,
): number {
  const t = clamp((value - inputMin) / (inputMax - inputMin), 0, 1);
  return lerp(outputMin, outputMax, t);
}

export function distance(x1: number, y1: number, x2: number, y2: number): number {
  return Math.hypot(x2 - x1, y2 - y1);
}

export function smoothstep(edge0: number, edge1: number, value: number): number {
  const t = clamp((value - edge0) / (edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
}

export function easeOutCubic(value: number): number {
  const t = clamp(value, 0, 1) - 1;
  return t * t * t + 1;
}

export function easeInOutSine(value: number): number {
  return -(Math.cos(Math.PI * clamp(value, 0, 1)) - 1) / 2;
}
