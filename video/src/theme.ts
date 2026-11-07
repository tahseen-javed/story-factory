// Shared theme tokens (docs/STYLE_BIBLE.md). Every colour, font and size used by the video comes from here.
export const W = 1920;
export const H = 1080;
export const FPS = 30;
export const OVERSCAN = 0.12;

export const INK = "#1c1a1f";
export const INK_SOFT = "#3a3640";
export const PAPER = "#f2e8d2";
export const PAPER_SHADE = "#e2d2ae";
export const PAPER_EDGE = "#cdb88a";
export const NOTE_YELLOW = "#f7dc6f";
export const ALERT_RED = "#d8323a";
export const GLOVE = "#f2b632";

export const FONT = {
  marker: "'Permanent Marker', 'Patrick Hand', cursive",
  hand: "'Patrick Hand', cursive",
  note: "'Caveat', 'Patrick Hand', cursive",
  ui: "'Inter', Arial, sans-serif",
  display: "'Anton', Impact, sans-serif",
};

export const ACCENT: Record<string, string> = {
  amber: "#f2a33a",
  teal: "#2aa7a0",
  crimson: "#d63a3a",
  violet: "#7a5cd6",
  lime: "#9bcf3c",
  coral: "#ff6f59",
  cobalt: "#2f5fd0",
  gold: "#e6b422",
};

export const OUTFIT: Record<string, string> = {
  teal: "#2a9d9a",
  plum: "#7d416f",
  red: "#c8453b",
  navy: "#2d4a7a",
  olive: "#76803a",
  mustard: "#d9a22b",
  grey: "#7b7f86",
  coral: "#e86f5a",
  cobalt: "#2f5fd0",
};

export const SKIN: Record<string, string> = {
  light: "#f3c9a0",
  tan: "#e0a67a",
  brown: "#b97a52",
  dark: "#8d5a3b",
};

export const HAIR: Record<string, string> = {
  black: "#24201f",
  brown: "#5a3a26",
  grey: "#b9b6b0",
  ginger: "#b8582a",
  blond: "#d8b25a",
};

// Mood grading per location variant. tint = multiply/soft overlay; filter = css filter on the world.
export const MOODS: Record<string, { filter: string; tint: string; tintOpacity: number; blend: string }> = {
  day: { filter: "saturate(1.05) contrast(1.03) brightness(1.02)", tint: "#ffb85a", tintOpacity: 0.09, blend: "soft-light" },
  night: { filter: "saturate(0.88) contrast(1.05) brightness(0.8)", tint: "#1d2f66", tintOpacity: 0.34, blend: "multiply" },
  alarm: { filter: "saturate(1.1) contrast(1.08) brightness(0.84)", tint: "#ff1f2d", tintOpacity: 0.26, blend: "multiply" },
  dusk: { filter: "saturate(1.0) contrast(1.04) brightness(0.9)", tint: "#ff7a3d", tintOpacity: 0.22, blend: "soft-light" },
  blackout: { filter: "saturate(0.7) contrast(1.08) brightness(0.62)", tint: "#0b2a3a", tintOpacity: 0.45, blend: "multiply" },
};

export const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
export const easeOutBack = (t: number) => {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};

// Deterministic pseudo random in [0,1) from an integer seed (stable across chunk renders).
export const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453123;
  return x - Math.floor(x);
};
