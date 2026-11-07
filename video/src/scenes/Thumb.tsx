import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { ACCENT, FONT, INK, W, H, MOODS } from "../theme";
import { Rig } from "../characters/Rig";
import { ProceduralBackdrop } from "./Backdrop";
import { OVERLAYS } from "../overlays/Overlays";
import { useFonts } from "../fonts";

export type ThumbSpec = {
  concept: "A" | "B";
  bg: string | null;
  location: string;
  variant: string;
  hero: { params: Record<string, any>; pose: string; expr: string };
  other?: { params: Record<string, any>; pose: string; expr: string } | null;
  text: string;
  accent: string;
  layout: "left" | "right";
  threat: string;
  object?: { name: string; args: any[] } | null;
};

const Threat: React.FC<{ kind: string; x: number; y: number; s: number; accent: string }> = ({ kind, x, y, s, accent }) => {
  const a = ACCENT[accent] || ACCENT.amber;
  const common = { transform: `translate(${x},${y}) scale(${s})` };
  if (kind === "sun")
    return (
      <g {...common}>
        <circle r={260} fill="#ff6a2b" opacity={0.22} />
        <circle r={190} fill="#ff8a30" stroke={INK} strokeWidth={10} />
        <circle r={140} fill="#ffc34d" />
        {Array.from({ length: 16 }).map((_, i) => <path key={i} d={`M${Math.cos(i * 0.3927) * 210},${Math.sin(i * 0.3927) * 210} L${Math.cos(i * 0.3927 + 0.1) * (290 + (i % 2) * 60)},${Math.sin(i * 0.3927 + 0.1) * (290 + (i % 2) * 60)} L${Math.cos(i * 0.3927 + 0.2) * 210},${Math.sin(i * 0.3927 + 0.2) * 210} Z`} fill="#ff8a30" stroke={INK} strokeWidth={6} strokeLinejoin="round" />)}
      </g>
    );
  if (kind === "alert")
    return (
      <g {...common}>
        <path d="M0,-230 L220,150 L-220,150 Z" fill="#d8323a" stroke={INK} strokeWidth={12} strokeLinejoin="round" />
        <rect x={-18} y={-110} width={36} height={150} rx={14} fill="#fff" /><circle cy={90} r={22} fill="#fff" />
      </g>
    );
  if (kind === "door")
    return (
      <g {...common}>
        <rect x={-150} y={-260} width={300} height={520} fill="#241c2b" stroke={INK} strokeWidth={12} />
        <path d="M-150,-260 L40,-230 L40,230 L-150,260 Z" fill="#6e4f3a" stroke={INK} strokeWidth={10} />
        <path d="M40,-230 L150,-260 L150,260 L40,230 Z" fill={a} opacity={0.9} />
      </g>
    );
  // clock
  return (
    <g {...common}>
      <circle r={230} fill="#f6efdc" stroke={INK} strokeWidth={14} />
      {Array.from({ length: 12 }).map((_, i) => <line key={i} x1={Math.cos(i * 0.5236) * 190} y1={Math.sin(i * 0.5236) * 190} x2={Math.cos(i * 0.5236) * 215} y2={Math.sin(i * 0.5236) * 215} stroke={INK} strokeWidth={10} />)}
      <path d="M0,0 L0,-150 M0,0 L100,50" stroke={"#d8323a"} strokeWidth={18} strokeLinecap="round" />
    </g>
  );
};

const Bg: React.FC<{ spec: ThumbSpec }> = ({ spec }) => {
  const tint = spec.concept === "A" ? "#10325a" : "#32193a";
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: -40, filter: "blur(7px) saturate(1.15) contrast(1.08)", transform: "scale(1.12)" }}>
        {spec.bg ? <Img src={staticFile(spec.bg)} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : <ProceduralBackdrop location={spec.location} variant={spec.variant} />}
      </div>
      <AbsoluteFill style={{ background: tint, opacity: 0.38, mixBlendMode: "multiply" }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at ${spec.layout === "left" ? "30%" : "70%"} 45%, rgba(255,190,90,0.38), rgba(0,0,0,0) 55%)`, mixBlendMode: "screen" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.62) 100%)" }} />
    </AbsoluteFill>
  );
};

const Headline: React.FC<{ text: string; x: number; y: number; accent: string; size?: number; rot?: number; width?: number }> = ({ text, x, y, accent, size = 230, rot = -3, width = 900 }) => {
  const words = text.split(" ");
  return (
    <div style={{ position: "absolute", left: x, top: y, width, transform: `rotate(${rot}deg)`, fontFamily: FONT.display, fontSize: size, lineHeight: 0.95, letterSpacing: 4, textTransform: "uppercase" }}>
      {words.map((w, i) => (
        <div key={i} style={{ color: i === 0 && /\d|^[A-Z]/.test(w) && words.length > 1 ? ACCENT[accent] : "#fff", WebkitTextStroke: "16px #0d0b10", paintOrder: "stroke fill", textShadow: "0 12px 0 rgba(0,0,0,0.55)" }}>{w}</div>
      ))}
    </div>
  );
};

export const ThumbFrame: React.FC<{ spec: ThumbSpec }> = ({ spec }) => {
  const left = spec.layout === "left";
  const isA = spec.concept === "A";
  const Obj = spec.object ? OVERLAYS[spec.object.name] : null;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: W, height: H, transform: "scale(0.6667)", transformOrigin: "0 0", overflow: "hidden", background: "#000" }}>
      <Bg spec={spec} />
      {isA ? (
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          <defs>
            <filter id="rim" x="-20%" y="-20%" width="140%" height="140%">
              <feMorphology in="SourceAlpha" operator="dilate" radius="7" result="d" />
              <feFlood floodColor="#ffd27a" result="c" />
              <feComposite in="c" in2="d" operator="in" result="rimc" />
              <feGaussianBlur in="rimc" stdDeviation="6" result="glow" />
              <feMerge><feMergeNode in="glow" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>
          <Threat kind={spec.threat} x={left ? 1330 : 560} y={430} s={1.15} accent={spec.accent} />
          <g filter="url(#rim)">
            <Rig params={spec.hero.params} pose={spec.hero.pose} expr={spec.hero.expr} frame={10} seed={3} x={left ? 520 : 1400} y={1600} scale={3.35} facing={left ? 1 : -1} />
          </g>
        </svg>
      ) : (
        <>
          {Obj ? (
            <div style={{ position: "absolute", left: left ? 860 : 120, top: 40, width: W, height: H, transform: "scale(0.82)", transformOrigin: "0 0" }}>
              <Obj args={spec.object!.args} frame={40} total={999} accent={spec.accent} fps={30} track={{}} prevTrack={{}} />
            </div>
          ) : null}
          <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
            <defs>
              <filter id="rim2" x="-20%" y="-20%" width="140%" height="140%">
                <feMorphology in="SourceAlpha" operator="dilate" radius="6" result="d" />
                <feFlood floodColor="#ffd27a" result="c" />
                <feComposite in="c" in2="d" operator="in" result="rimc" />
                <feGaussianBlur in="rimc" stdDeviation="5" result="glow" />
                <feMerge><feMergeNode in="glow" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>
            <g filter="url(#rim2)">
              <Rig params={spec.hero.params} pose={spec.hero.pose} expr={spec.hero.expr} frame={10} seed={5} x={left ? 330 : 1560} y={1090} scale={1.45} facing={left ? 1 : -1} />
            </g>
          </svg>
        </>
      )}
      {isA ? (
        <Headline text={spec.text} x={left ? 960 : 90} y={80} accent={spec.accent} size={250} width={900} />
      ) : (
        <Headline text={spec.text} x={left ? 70 : 860} y={60} accent={spec.accent} size={200} width={1000} />
      )}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5) 100%)" }} />
    </div>
  );
};

export const ThumbSet: React.FC<{ thumbs: ThumbSpec[] }> = ({ thumbs }) => {
  useFonts();
  const f = useCurrentFrame();
  const spec = thumbs[Math.min(f, thumbs.length - 1)];
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <ThumbFrame spec={spec} />
    </AbsoluteFill>
  );
};
