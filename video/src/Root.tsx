import React from "react";
import { AbsoluteFill, Composition, Still } from "remotion";
import { Story } from "./scenes/Story";
import { RigSheet } from "./scenes/RigSheet";
import { testTimeline } from "./testTimeline";
import { Timeline } from "./types";
import { ThumbSet, ThumbSpec } from "./scenes/Thumb";

const DEMO_THUMB: ThumbSpec = {
  concept: "A", bg: null, location: "rooftop", variant: "blackout", accent: "amber", layout: "left", threat: "sun", text: "WHY ME?",
  hero: { params: { outfit: "teal", hat: "cap", hair: "short" }, pose: "stand", expr: "shocked" }, other: null, object: null,
};

const meta = ({ props }: { props: { timeline: Timeline } }) => ({
  durationInFrames: Math.max(1, props.timeline.durationInFrames),
  fps: props.timeline.fps,
  width: props.timeline.width,
  height: props.timeline.height,
});

export const RemotionRoot: React.FC = () => {
  const tl = testTimeline();
  return (
    <>
      {/* production composition: props = { timeline } written by factory.assemble */}
      <Composition id="Story" component={Story as any} durationInFrames={tl.durationInFrames} fps={30} width={1920} height={1080} defaultProps={{ timeline: tl }} calculateMetadata={meta as any} />
      {/* 30 s showcase of the rig, overlays, camera presets and FX (Phase 1 proof; first 20 s = CI smoke render) */}
      <Composition id="Showcase" component={Story as any} durationInFrames={tl.durationInFrames} fps={30} width={1920} height={1080} defaultProps={{ timeline: tl }} />
      <Still id="RigSheet" component={RigSheet as any} width={2400} height={1500} />
      {/* thumbnail candidates: one frame per candidate, render with --sequence (see factory/thumbnails.py) */}
      <Composition id="ThumbSet" component={ThumbSet as any} durationInFrames={8} fps={30} width={1280} height={720} defaultProps={{ thumbs: [DEMO_THUMB] }}
        calculateMetadata={(({ props }: any) => ({ durationInFrames: Math.max(1, props.thumbs.length) })) as any} />
    </>
  );
};
