export type CharSpec = {
  id: string;
  rig: string;
  params: Record<string, any>;
  pose: string;
  expr: string;
  x: number; // 0..1 of stage width (centre of feet)
  facing: 1 | -1;
  view?: string; // front | three_quarter | back
  silhouette?: boolean;
  speaks?: boolean;
};

export type CamSpec = {
  preset: string;
  z0: number;
  z1: number;
  fx: number; // focus point 0..1
  fy: number;
  param?: string | null;
};

export type OverlaySpec = {
  name: string;
  args: any[];
  inFrame: number; // relative to shot start
  outFrame: number; // relative to shot start
};

export type Shot = {
  i: number;
  chapter: number;
  start: number; // absolute frame
  dur: number; // frames
  location: string;
  variant: string;
  bg: string | null; // staticFile path to the flattened background
  layers: { far?: string; mid?: string; near?: string } | null;
  floorY: number; // 0..1 of stage height where characters stand
  chars: CharSpec[];
  overlay: OverlaySpec | null;
  camera: CamSpec;
  fx: string[];
  banner: string | null;
  cta: boolean;
  timeCard: { text: string; frames: number } | null;
  track: Record<string, any>; // cumulative tracker state at this shot
  prevTrack: Record<string, any>;
  text: string;
  framing?: string;
  // Video Doctor face-overlap fixes (P-012): graphic placement overrides written by factory/doctor/visual.py
  ovShift?: [number, number] | null;
  ovScale?: number | null;
  hudRight?: boolean;
  bannerDy?: number;
  trans?: string;
  grade?: string;
  crowd?: boolean;
  tension?: number;
};

export type Caption = { s: number; e: number; lines: Array<Array<[string, number, number]>> };

export type Timeline = {
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
  style: { accent: string; lut: string; titlecard: string; transition: string };
  shots: Shot[];
  endScreenFrames: number;
  captions?: Caption[];
  voiceEnv?: number[];
  fadeOut?: number;
};
