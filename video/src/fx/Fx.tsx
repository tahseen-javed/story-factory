import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame } from "remotion";
import { W, H, MOODS, rand } from "../theme";

// Grain tile is generated once by factory/images.py (video/public/grain.png). Falls back to svg noise.
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.16 }) => {
  const frame = useCurrentFrame();
  const ox = Math.floor(rand(frame * 3 + 1) * 512);
  const oy = Math.floor(rand(frame * 5 + 2) * 512);
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `url(${staticFile("grain.png")})`,
        backgroundSize: "512px 512px",
        backgroundPosition: `${ox}px ${oy}px`,
        mixBlendMode: "overlay",
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};

export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.5 }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 52%, rgba(10,6,14,${strength}) 100%)`,
      pointerEvents: "none",
    }}
  />
);

export const MoodTint: React.FC<{ variant: string }> = ({ variant }) => {
  const m = MOODS[variant] || MOODS.day;
  return <AbsoluteFill style={{ background: m.tint, opacity: m.tintOpacity, mixBlendMode: m.blend as any, pointerEvents: "none" }} />;
};

const Particles: React.FC<{ n: number; color: string; size: [number, number]; speed: number; rise: boolean; seed: number; opacity: number }> = ({
  n, color, size, speed, rise, seed, opacity,
}) => {
  const frame = useCurrentFrame();
  const items = [];
  for (let i = 0; i < n; i++) {
    const r1 = rand(seed + i * 3.1), r2 = rand(seed + i * 7.7), r3 = rand(seed + i * 11.3);
    const s = size[0] + r1 * (size[1] - size[0]);
    const x = (r1 * W + Math.sin(frame * 0.02 * (0.5 + r3) + i) * 40 + W) % W;
    const yRaw = (r2 * H + frame * speed * (0.5 + r3) * (rise ? -1 : 1)) % H;
    const y = (yRaw + H) % H;
    items.push(<div key={i} style={{ position: "absolute", left: x, top: y, width: s, height: s, borderRadius: "50%", background: color, opacity: opacity * (0.4 + r3 * 0.6) }} />);
  }
  return <AbsoluteFill style={{ pointerEvents: "none" }}>{items}</AbsoluteFill>;
};

export const Rain: React.FC = () => {
  const frame = useCurrentFrame();
  const lines = [];
  for (let i = 0; i < 90; i++) {
    const r = rand(i * 9.3), r2 = rand(i * 4.1);
    const x = r * (W + 200) - 100;
    const y = ((r2 * H + frame * (38 + r * 22)) % (H + 120)) - 60;
    lines.push(<line key={i} x1={x} y1={y} x2={x - 14} y2={y + 46} stroke="#cfe3f2" strokeOpacity={0.35} strokeWidth={2} />);
  }
  return <svg width={W} height={H} style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>{lines}</svg>;
};

export const FxLayer: React.FC<{ fx: string[]; variant: string }> = ({ fx, variant }) => {
  const frame = useCurrentFrame();
  const out: React.ReactNode[] = [];
  if (fx.includes("flicker")) {
    const v = 0.5 + 0.5 * Math.sin(frame * 0.7) * Math.sin(frame * 0.23 + 1.3);
    out.push(<AbsoluteFill key="fl" style={{ background: "#000", opacity: 0.1 + 0.16 * Math.max(0, v), pointerEvents: "none" }} />);
  }
  if (fx.includes("alarm_pulse") || variant === "alarm") {
    // 1.2 Hz soft pulse, low contrast: well under 3 flashes per second
    const p = 0.5 + 0.5 * Math.sin((frame / 30) * Math.PI * 2 * 1.2);
    out.push(<AbsoluteFill key="al" style={{ background: "#ff1a2a", opacity: 0.05 + 0.1 * p, mixBlendMode: "multiply", pointerEvents: "none" }} />);
  }
  if (fx.includes("dust")) out.push(<Particles key="du" n={34} color="#f5e9c8" size={[2, 5]} speed={0.35} rise seed={11} opacity={0.5} />);
  if (fx.includes("embers")) out.push(<Particles key="em" n={40} color="#ffae42" size={[3, 7]} speed={1.4} rise seed={23} opacity={0.85} />);
  if (fx.includes("snow")) out.push(<Particles key="sn" n={70} color="#ffffff" size={[3, 7]} speed={1.1} rise={false} seed={31} opacity={0.8} />);
  if (fx.includes("smoke")) {
    const puffs = [];
    for (let i = 0; i < 7; i++) {
      const r = rand(i * 5.5 + 2);
      const x = ((r * W + frame * (0.4 + r)) % (W + 600)) - 300;
      const y = H * (0.45 + 0.4 * rand(i * 8.8)) - (frame * 0.25 * (0.4 + r)) % 120;
      puffs.push(<div key={i} style={{ position: "absolute", left: x, top: y, width: 520, height: 260, borderRadius: "50%", background: "radial-gradient(ellipse, rgba(210,205,200,0.34), rgba(210,205,200,0))", filter: "blur(18px)" }} />);
    }
    out.push(<AbsoluteFill key="sm" style={{ pointerEvents: "none" }}>{puffs}</AbsoluteFill>);
  }
  if (fx.includes("rain")) out.push(<Rain key="ra" />);
  if (fx.includes("glitch")) {
    const on = rand(Math.floor(frame / 3) * 1.7) > 0.8;
    if (on) {
      const y = rand(frame * 2.2) * H;
      out.push(<div key="gl" style={{ position: "absolute", left: 0, top: y, width: W, height: 26 + rand(frame) * 40, background: "rgba(255,255,255,0.12)", mixBlendMode: "difference", transform: `translateX(${(rand(frame * 4) - 0.5) * 60}px)` }} />);
    }
  }
  return <>{out}</>;
};
