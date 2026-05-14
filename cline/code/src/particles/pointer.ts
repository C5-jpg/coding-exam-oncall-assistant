export type PointerState = {
  x: number;
  y: number;
  active: boolean;
  hoverBoost: number;
  pulseX: number;
  pulseY: number;
  pulseAge: number;
};

export const createPointerState = (): PointerState => ({
  x: -9999,
  y: -9999,
  active: false,
  hoverBoost: 0,
  pulseX: -9999,
  pulseY: -9999,
  pulseAge: 999,
});
