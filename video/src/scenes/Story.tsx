import React from "react";
import { AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { W, H, OVERSCAN, MOODS, GRADES, ACCENT, INK, FONT, easeOut, clamp, rand } from "../theme";
import { Shot, Timeline, Caption } from "../types";
import { cameraAt, PARALLAX } from "../camera/camera";
import { Rig } from "../characters/Rig";
import { POSES } from "../characters/poses";
import { ProceduralBackdrop } from "./Backdrop";
import { FxLayer, Grain, MoodTint, Vignette } from "../fx/Fx";
import { OVERLAYS, FlashForwardBanner, SubscribeSticker, TimeCard } from "../overlays/Overlays";
import { prog } from "../overlays/common";
import { useFonts } from "../fonts";

const bgBox: React.CSSProperties = {
  position: "absolute",
  left: -(W * OVERSCAN) / 2,
  top: -(H * OVERSCAN) / 2,
  width: W * (1 + OVERSCAN),
  height: H * (1 + OVERSCAN),
};

// One shared flat-colour pass for every backdrop so scenes generated at different times match (style bible: limited palette).
const PosterFilter: React.FC = () => {
  const t = "0 0.125 0.25 0.375 0.5 0.625 0.75 0.875 1";
  return (
    <svg width={0} height={0} style={{ position: "absolute" }}>
      <defs>
        <filter id="poster" colorInterpolationFilters="sRGB">
          <feComponentTransfer>
            <feFuncR type="discrete" tableValues={t} />
            <feFuncG type="discrete" tableValues={t} />
            <feFuncB type="discrete" tableValues={t} />
          </feComponentTransfer>
        </filter>
      </defs>
    </svg>
  );
};

const Backdrop: React.FC<{ shot: Shot; tx: number; ty: number }> = ({ shot, tx, ty }) => {
  if (shot.layers && shot.layers.far) {
    const L = shot.layers;
    return (
      <>
        <div style={{ ...bgBox, transform: `translate(${tx * PARALLAX.far}px, ${ty * PARALLAX.far}px)` }}><Img src={staticFile(L.far!)} style={{ width: "100%", height: "100%" }} /></div>
        {L.mid ? <div style={{ ...bgBox, transform: `translate(${tx * PARALLAX.mid}px, ${ty * PARALLAX.mid}px)` }}><Img src={staticFile(L.mid)} style={{ width: "100%", height: "100%" }} /></div> : null}
        {L.near ? <div style={{ ...bgBox, transform: `translate(${tx * PARALLAX.near}px, ${ty * PARALLAX.near}px)` }}><Img src={staticFile(L.near)} style={{ width: "100%", height: "100%" }} /></div> : null}
      </>
    );
  }
  if (shot.bg) {
    return <div style={{ ...bgBox, transform: `translate(${tx * PARALLAX.mid}px, ${ty * PARALLAX.mid}px)` }}><Img src={staticFile(shot.bg)} style={{ width: "100%", height: "100%" }} /></div>;
  }
  return <div style={{ position: "absolute", inset: 0, transform: `translate(${tx * PARALLAX.mid}px, ${ty * PARALLAX.mid}px)` }}><ProceduralBackdrop location={shot.location} variant={shot.variant} /></div>;
};

// Character size / position per framing (closeups anchor the head, inserts the torso and hands, wides shrink the hero against the world).
const FRAMING_MULT: Record<string, number> = { medium: 1, closeup: 2.3, insert: 1.8, wide: 0.82, xwide: 0.55, low: 1.45, back: 1.15, ots: 1.2, silhouette: 1.1, profile: 1.1 };

function placeChar(shot: Shot, idx: number, n: number, base: number) {
  const f = shot.framing || "medium";
  const c = shot.chars[idx];
  let mult = FRAMING_MULT[f] ?? 1;
  if (n >= 2 && f === "closeup") mult = 1.45;
  if (f === "ots") mult = idx === 0 ? 1.9 : 1.2;
  const sc = base * mult;
  const rootY = POSES[c.pose]?.rootY ?? 0;
  let y = shot.floorY * H;
  if (f === "closeup") y = 0.46 * H + (380 - rootY) * sc;
  else if (f === "insert") y = 0.52 * H + (200 - rootY) * sc;
  else if (f === "low") y = 1.02 * H;
  else if (f === "xwide") y = 0.84 * H;
  else if (f === "wide") y = 0.88 * H;
  else if (f === "ots" && idx === 0) y = 1.04 * H;
  return { sc, y };
}

const Crowd: React.FC<{ frame: number }> = ({ frame }) => (
  <g>
    {[0.1, 0.19, 0.33, 0.66, 0.8, 0.9].map((x, i) => (
      <g key={i} transform={`translate(${x * W},${0.8 * H + Math.sin(frame * 0.12 + i * 2) * 3}) scale(${0.46 + 0.07 * (i % 3)})`} fill="#14121a" opacity={0.82}>
        <circle cx={0} cy={-250} r={34} />
        <path d="M-46,-210 Q0,-232 46,-210 L58,0 L-58,0 Z" />
      </g>
    ))}
  </g>
);

const Hud: React.FC<{ track: Record<string, any>; prev: Record<string, any>; frame: number }> = ({ track, prev, frame }) => {
  const items: Array<{ k: string; label: string; v: string }> = [];
  if (track.hours !== undefined && Number(track.hours) > 0) items.push({ k: "hours", label: "HOURS LEFT", v: String(track.hours) });
  if (track.phone !== undefined) items.push({ k: "phone", label: "BATTERY", v: String(track.phone) });
  if (!items.length) return null;
  return (
    <div style={{ position: "absolute", left: "4%", top: "5%", display: "flex", gap: 14 }}>
      {items.map((it) => {
        const changed = prev[it.k] !== undefined && prev[it.k] !== track[it.k] && frame < 36;
        const low = it.k === "phone" && parseInt(it.v, 10) <= 10;
        return (
          <div key={it.k} style={{ background: "rgba(20,18,26,0.72)", border: `3px solid ${low || changed ? "#ff4d4d" : "#f2e8d2"}`, borderRadius: 12, padding: "6px 14px", transform: `scale(${changed ? 1 + 0.12 * Math.sin(frame * 0.5) : 1})` }}>
            <div style={{ fontFamily: FONT.ui, fontWeight: 700, fontSize: 15, letterSpacing: 2, color: "#f2e8d2", opacity: 0.8 }}>{it.label}</div>
            <div style={{ fontFamily: FONT.display, fontSize: 36, color: low || changed ? "#ff6b6b" : "#fff" }}>{it.v}</div>
          </div>
        );
      })}
    </div>
  );
};

const TransFx: React.FC<{ trans: string; frame: number }> = ({ trans, frame }) => {
  if (trans === "flash" && frame < 4) return <AbsoluteFill style={{ background: "#fff", opacity: 0.6 * (1 - frame / 4) }} />;
  if (trans === "smash" && frame < 5) return <AbsoluteFill style={{ background: "#000", opacity: 1 - frame / 5 }} />;
  if (trans === "glitch" && frame < 8) {
    const y = rand(frame * 3.1) * H;
    return (
      <>
        <div style={{ position: "absolute", left: 0, top: y, width: W, height: 34 + rand(frame) * 60, background: "rgba(255,255,255,0.16)", mixBlendMode: "difference", transform: `translateX(${(rand(frame * 4) - 0.5) * 90}px)` }} />
        <AbsoluteFill style={{ background: "#00e5ff", opacity: 0.08 * (frame % 2), mixBlendMode: "screen" }} />
      </>
    );
  }
  return null;
};

const Captions: React.FC<{ caps: Caption[] }> = ({ caps }) => {
  const frame = useCurrentFrame();
  const c = caps.find((x) => frame >= x.s && frame < x.e);
  if (!c) return null;
  return (
    <div style={{ position: "absolute", left: "5%", right: "5%", bottom: "6%", textAlign: "center" }}>
      {c.lines.map((ln, i) => (
        <div key={i} style={{ lineHeight: 1.12 }}>
          {ln.map(([w, a, b], k) => {
            const on = frame >= a && frame < b;
            return (
              <span key={k} style={{ display: "inline-block", marginRight: 14, fontFamily: FONT.ui, fontWeight: 900, fontSize: 58, color: on ? ACCENT.amber : frame >= b ? "#ffffff" : "rgba(255,255,255,0.72)",
                transform: `scale(${on ? 1.08 : 1})`, WebkitTextStroke: `9px ${INK}`, paintOrder: "stroke fill", textShadow: "0 4px 10px rgba(0,0,0,0.55)" }}>{w}</span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

export const ShotView: React.FC<{ shot: Shot; tl: Timeline }> = ({ shot, tl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cam = cameraAt(shot.camera, frame, shot.dur);
  const mood = MOODS[shot.variant] || MOODS.day;
  const grade = GRADES[shot.grade || ""] || null;
  const ov = shot.overlay;
  const ovOn = !!ov && frame >= ov.inFrame && frame < ov.outFrame;
  const isEnd = ov?.name === "end_screen";
  const blurIn = ov && !isEnd ? easeOut(prog(frame - ov.inFrame, 0, 8)) * (1 - prog(frame - (ov.outFrame - 8), 0, 8)) : 0;
  const trans = shot.trans || "cut";
  const k8 = clamp(frame / 8, 0, 1);
  const whip = trans === "whip" && frame < 8 ? 14 * (1 - k8) : 0;
  const blur = cam.blur + 8 * blurIn + whip;
  const Ov = ov ? OVERLAYS[ov.name] : null;
  const n = shot.chars.length;
  const charScale = n >= 3 ? 1.0 : n === 2 ? 1.12 : 1.28;
  const progress = shot.dur > 1 ? frame / (shot.dur - 1) : 0;
  const wrapX = trans === "whip" && frame < 8 ? -160 * (1 - easeOut(k8)) : 0;
  const punch = trans === "punch" && frame < 6 ? 1 + 0.07 * (1 - frame / 6) : 1;
  const worldFilter = `url(#poster) ${mood.filter}${grade ? " " + grade.filter : ""}`;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      <div style={{ position: "absolute", inset: 0, transform: `translateX(${wrapX}px) scale(${punch})`, filter: blur > 0.2 ? `blur(${blur.toFixed(2)}px)` : "none" }}>
        <div style={{ position: "absolute", inset: 0, transformOrigin: `${cam.fx * 100}% ${cam.fy * 100}%`, transform: `scale(${cam.z}) rotate(${cam.rot}deg)` }}>
          <div style={{ position: "absolute", inset: 0, filter: worldFilter }}>
            <Backdrop shot={shot} tx={cam.tx} ty={cam.ty} />
          </div>
          <svg width={W} height={H} style={{ position: "absolute", inset: 0, overflow: "visible", filter: grade ? `${mood.charFilter} ${grade.filter}` : mood.charFilter, transform: `translate(${cam.tx * PARALLAX.chars}px, ${cam.ty * PARALLAX.chars}px)` }}>
            {shot.crowd ? <Crowd frame={frame} /> : null}
            {shot.chars.map((c, i) => {
              const { sc, y } = placeChar(shot, i, n, charScale);
              const env = tl.voiceEnv ? tl.voiceEnv[shot.start + frame] : undefined;
              const mouth = c.speaks && env !== undefined ? env : undefined;
              return (
                <g key={c.id + i} style={c.silhouette ? { filter: "brightness(0)" } : undefined}>
                  <Rig params={c.params} pose={c.pose} expr={c.expr} frame={frame} fps={fps} seed={(c.id.charCodeAt(0) || 1) + i * 7} x={c.x * W} y={y} scale={sc} facing={c.facing} progress={progress} prop={(c as any).prop || null} mouth={mouth} view={c.view || "front"} />
                </g>
              );
            })}
          </svg>
        </div>
        <MoodTint variant={shot.variant} />
        {grade ? <AbsoluteFill style={{ background: grade.tint, opacity: grade.opacity, mixBlendMode: grade.blend as any, pointerEvents: "none" }} /> : null}
        <FxLayer fx={shot.fx} variant={shot.variant} />
      </div>
      <Vignette strength={mood.vignette} />
      <Grain />
      <TransFx trans={trans} frame={frame} />
      <Hud track={shot.track} prev={shot.prevTrack} frame={frame} />
      {ovOn && Ov ? (
        <Ov args={ov!.args} frame={frame - ov!.inFrame} total={ov!.outFrame - ov!.inFrame} accent={tl.style.accent} fps={fps} track={shot.track} prevTrack={shot.prevTrack} />
      ) : null}
      {shot.banner && frame < 96 ? <FlashForwardBanner text={shot.banner} frame={frame} total={Math.min(96, shot.dur)} /> : null}
      {shot.timeCard && frame < shot.timeCard.frames ? <TimeCard text={shot.timeCard.text} frame={frame} total={shot.timeCard.frames} design={tl.style.titlecard} accent={tl.style.accent} /> : null}
      {shot.cta && frame >= 6 ? <SubscribeSticker frame={frame - 6} total={Math.max(24, Math.min(90, shot.dur - 10))} /> : null}
    </AbsoluteFill>
  );
};

const FadeOut: React.FC<{ total: number; frames: number }> = ({ total, frames }) => {
  const frame = useCurrentFrame();
  const k = clamp((frame - (total - frames)) / frames, 0, 1);
  return k > 0 ? <AbsoluteFill style={{ background: "#000", opacity: k }} /> : null;
};

export const Story: React.FC<{ timeline: Timeline }> = ({ timeline }) => {
  useFonts();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <PosterFilter />
      {timeline.shots.map((s) => (
        <Sequence key={s.i} from={s.start} durationInFrames={s.dur} layout="none">
          <ShotView shot={s} tl={timeline} />
        </Sequence>
      ))}
      {timeline.captions && timeline.captions.length ? <Captions caps={timeline.captions} /> : null}
      <FadeOut total={timeline.durationInFrames} frames={timeline.fadeOut ?? 0} />
    </AbsoluteFill>
  );
};
