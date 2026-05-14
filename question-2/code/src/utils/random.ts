export function hash(seed: number): number {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

export function seededRange(seed: number, min: number, max: number): number {
  return min + (max - min) * hash(seed);
}

export function pickSeeded<T>(items: readonly T[], seed: number): T {
  const index = Math.floor(hash(seed) * items.length) % items.length;
  return items[index];
}

export function signedNoise(seed: number, time: number, speed = 1): number {
  const a = Math.sin(time * speed + seed * 37.13);
  const b = Math.sin(time * speed * 0.37 + seed * 11.71);
  return (a * 0.68 + b * 0.32) * 0.5 + 0.5;
}
