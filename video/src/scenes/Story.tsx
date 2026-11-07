import React from "react";
import { AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { W, H, OVERSCAN, MOODS, easeOut, clamp } from "../theme";
import { Shot, Timeline } from "../types";
import { cameraAt, PARALLAX } from "../camera/camera";
import { Rig } from "../characters/Rig";
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

export const ShotView: React.FC<{ shot: Shot; tl: Timeline }> = ({ shot, tl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cam = cameraAt(shot.camera, frame, shot.dur);
  const mood = MOODS[shot.variant] || MOODS.day;
  const ov = shot.overlay;
  const ovOn = !!ov && frame >= ov.inFrame && frame < ov.outFrame;
  const isEnd = ov?.name === "end_screen";
  const blurIn = ov && !isEnd ? easeOut(prog(frame - ov.inFrame, 0, 8)) * (1 - prog(frame - (ov.outFrame - 8), 0, 8)) : 0;
  const blur = cam.blur + 8 * blurIn;
  const Ov = ov ? OVERLAYS[ov.name] : null;
  const n = shot.chars.length;
  const charScale = n >= 3 ? 1.0 : n === 2 ? 1.12 : 1.28;
  const progress = shot.dur > 1 ? frame / (shot.dur - 1) : 0;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      <div style={{ position: "absolute", inset: 0, filter: `${mood.filter}${blur > 0.2 ? ` blur(${blur.toFixed(2)}px)` : ""}` }}>
        <div style={{ position: "absolute", inset: 0, transformOrigin: `${cam.fx * 100}% ${cam.fy * 100}%`, transform: `scale(${cam.z}) rotate(${cam.rot}deg)` }}>
          <Backdrop shot={shot} tx={cam.tx} ty={cam.ty} />
          <svg width={W} height={H} style={{ position: "absolute", inset: 0, overflow: "visible", transform: `translate(${cam.tx * PARALLAX.chars}px, ${cam.ty * PARALLAX.chars}px)` }}>
            {shot.chars.map((c, i) => (
              <Rig key={c.id + i} params={c.params} pose={c.pose} expr={c.expr} frame={frame} fps={fps} seed={(c.id.charCodeAt(0) || 1) + i * 7} x={c.x * W} y={shot.floorY * H} scale={charScale} facing={c.facing} progress={progress} prop={(c as any).prop || null} />
            ))}
          </svg>
        </div>
        <MoodTint variant={shot.variant} />
        <FxLayer fx={shot.fx} variant={shot.variant} />
      </div>
      <Vignette strength={shot.variant === "day" ? 0.4 : 0.6} />
      <Grain />
      {ovOn && Ov ? (
        <Ov args={ov!.args} frame={frame - ov!.inFrame} total={ov!.outFrame - ov!.inFrame} accent={tl.style.accent} fps={fps} track={shot.track} prevTrack={shot.prevTrack} />
      ) : null}
      {shot.banner && frame < 96 ? <FlashForwardBanner text={shot.banner} frame={frame} total={Math.min(96, shot.dur)} /> : null}
      {shot.timeCard && frame < shot.timeCard.frames ? <TimeCard text={shot.timeCard.text} frame={frame} total={shot.timeCard.frames} design={tl.style.titlecard} accent={tl.style.accent} /> : null}
      {shot.cta && frame >= 6 && frame < 6 + 96 ? <SubscribeSticker frame={frame - 6} total={90} /> : null}
    </AbsoluteFill>
  );
};

export const Story: React.FC<{ timeline: Timeline }> = ({ timeline }) => {
  useFonts();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {timeline.shots.map((s) => (
        <Sequence key={s.i} from={s.start} durationInFrames={s.dur} layout="none">
          <ShotView shot={s} tl={timeline} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
