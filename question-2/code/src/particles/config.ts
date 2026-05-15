export type ParticleLayerName = "dust" | "orbit" | "signal";

export interface LayerSettings {
  name: ParticleLayerName;
  count: number;
  radius: [number, number];
  opacity: [number, number];
  speed: [number, number];
  spring: number;
  damping: number;
  blur: number;
  drift: number;
  interaction: number;
}

export interface ParticleConfig {
  dprCap: number;
  background: {
    base: string;
    vignette: string;
    halo: string;
  };
  pointer: {
    radius: number;
    force: number;
    swirl: number;
    hoverBoost: number;
  };
  ripple: {
    duration: number;
    radius: number;
    force: number;
    band: number;
  };
  layers: LayerSettings[];
}

export type QualityLevel = "low" | "balanced" | "high";

export interface QualityProfile {
  dprCap: number;
  particleScale: number;
  blurScale: number;
  motionScale: number;
}

export const qualityProfiles: Record<QualityLevel, QualityProfile> = {
  low: {
    dprCap: 1,
    particleScale: 0.52,
    blurScale: 0,
    motionScale: 0.72,
  },
  balanced: {
    dprCap: 1.5,
    particleScale: 0.78,
    blurScale: 0.35,
    motionScale: 0.9,
  },
  high: {
    dprCap: 2,
    particleScale: 1,
    blurScale: 1,
    motionScale: 1,
  },
};

export const particleConfig: ParticleConfig = {
  dprCap: qualityProfiles.balanced.dprCap,
  background: {
    base: "#fbfbfa",
    vignette: "rgba(218, 225, 246, 0.32)",
    halo: "rgba(255, 255, 255, 0.86)",
  },
  pointer: {
    radius: 230,
    force: 62,
    swirl: 0.48,
    hoverBoost: 1.55,
  },
  ripple: {
    duration: 1.15,
    radius: 560,
    force: 148,
    band: 42,
  },
  layers: [
    {
      name: "dust",
      count: 220,
      radius: [0.8, 2.4],
      opacity: [0.22, 0.58],
      speed: [0.04, 0.18],
      spring: 0.038,
      damping: 0.88,
      blur: 0,
      drift: 18,
      interaction: 0.65,
    },
    {
      name: "orbit",
      count: 120,
      radius: [1.6, 4.8],
      opacity: [0.55, 0.95],
      speed: [0.07, 0.26],
      spring: 0.052,
      damping: 0.86,
      blur: 0.4,
      drift: 28,
      interaction: 1.2,
    },
    {
      name: "signal",
      count: 55,
      radius: [1.4, 3.5],
      opacity: [0.35, 0.72],
      speed: [0.05, 0.22],
      spring: 0.045,
      damping: 0.89,
      blur: 1.8,
      drift: 34,
      interaction: 0.85,
    },
  ],
};

export const particlePalette = [
  "#1a73e8",
  "#4c6fff",
  "#6956d9",
  "#8e4eb8",
  "#c23886",
  "#e54f77",
  "#202124",
  "#5f6368",
] as const;

export const subtlePalette = [
  "#174ea6",
  "#3c4043",
  "#5f6368",
  "#718096",
  "#b7468d",
] as const;
