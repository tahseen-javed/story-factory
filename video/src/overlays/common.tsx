import React from "react";
import { staticFile } from "remotion";
import { INK, PAPER, PAPER_EDGE, easeOut, easeOutBack, clamp, GLOVE } from "../theme";

export type OvProps = {
  args: any[];
  frame: number; // frames since overlay start
  total: number; // overlay length in frames
  accent: string;
  fps: number;
  track: Record<string, any>;
  prevTrack: Record<string, any>;
};

export const prog = (frame: number, start: number, len: number) => clamp((frame - start) / Math.max(1, len), 0, 1);

// Pops in with a little overshoot, leaves with a quick shrink. Wraps every overlay.
export const OverlayFrame: React.FC<{ frame: number; total: number; rot?: number; x?: number; y?: number; children: React.ReactNode }> = ({ frame, total, rot = 0, x = 960, y = 540, children }) => {
  const inP = easeOutBack(prog(frame, 0, 12));
  const outP = prog(frame, total - 8, 8);
  const scale = (0.78 + 0.22 * inP) * (1 - 0.06 * outP);
  const opacity = clamp(frame / 5, 0, 1) * (1 - outP);
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%, -50%) rotate(${rot + (1 - inP) * -4}deg) scale(${scale})`, opacity, filter: "drop-shadow(0 18px 18px rgba(0,0,0,0.38))" }}>
      {children}
    </div>
  );
};

export const Tape: React.FC<{ x: number; y: number; rot?: number; w?: number }> = ({ x, y, rot = -8, w = 120 }) => (
  <div style={{ position: "absolute", left: x, top: y, width: w, height: 40, background: "rgba(240,224,150,0.82)", transform: `rotate(${rot}deg)`, borderLeft: "3px dotted rgba(0,0,0,0.12)", borderRight: "3px dotted rgba(0,0,0,0.12)" }} />
);

export const Paper: React.FC<{ w: number; h: number; color?: string; children?: React.ReactNode; style?: React.CSSProperties; tape?: boolean; radius?: number }> = ({ w, h, color = PAPER, children, style, tape = true, radius = 8 }) => (
  <div style={{ position: "relative", width: w, height: h, background: color, border: `6px solid ${INK}`, borderRadius: radius, boxShadow: "12px 14px 0 rgba(0,0,0,0.22)", overflow: "visible", ...style }}>
    <div style={{ position: "absolute", inset: 0, borderRadius: radius, backgroundImage: `url(${staticFile("grain.png")})`, backgroundSize: "256px", mixBlendMode: "multiply", opacity: 0.22 }} />
    {tape ? <><Tape x={-30} y={-18} rot={-24} /><Tape x={w - 100} y={-18} rot={20} /></> : null}
    {children}
  </div>
);

// Handwriting-style reveal: wipes text from left to right.
export const Reveal: React.FC<{ p: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ p, children, style }) => (
  <div style={{ clipPath: `inset(-10% ${100 - p * 100}% -10% 0)`, ...style }}>{children}</div>
);

export const Glove: React.FC<{ x: number; y: number; rot?: number; s?: number }> = ({ x, y, rot = 0, s = 1 }) => (
  <g transform={`translate(${x},${y}) rotate(${rot}) scale(${s})`}>
    <rect x={-60} y={40} width={120} height={150} rx={26} fill="#3e3a48" stroke={INK} strokeWidth={6} />
    <rect x={-56} y={20} width={112} height={40} rx={14} fill={GLOVE} stroke={INK} strokeWidth={6} />
    <rect x={-54} y={-72} width={108} height={100} rx={34} fill={GLOVE} stroke={INK} strokeWidth={6} />
  </g>
);

export const easeP = easeOut;
export { PAPER_EDGE };
