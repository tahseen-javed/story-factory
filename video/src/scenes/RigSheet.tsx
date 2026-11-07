import React from "react";
import { AbsoluteFill } from "remotion";
import { Rig } from "../characters/Rig";
import { POSES, EXPRS } from "../characters/poses";
import { useFonts } from "../fonts";
import { FONT, INK, PAPER } from "../theme";

// Contact sheet of every pose and expression of the rig (proof for docs/PROGRESS.md and a design regression image).
export const RigSheet: React.FC = () => {
  useFonts();
  const poses = Object.keys(POSES);
  const exprs = Object.keys(EXPRS);
  const hero = { outfit: "teal", hat: "cap", hair: "short" };
  const mara = { outfit: "plum", hat: "none", hair: "bun", age: "old" };
  return (
    <AbsoluteFill style={{ background: PAPER, fontFamily: FONT.hand }}>
      <svg width={2400} height={1500}>
        <text x={40} y={60} fontSize={46} fontFamily={FONT.marker} fill={INK}>POSES</text>
        {poses.map((p, i) => (
          <g key={p}>
            <Rig params={i % 2 ? mara : hero} pose={p} expr={exprs[i % exprs.length]} frame={20 + i * 3} seed={i + 1} x={150 + (i % 7) * 330} y={(i < 7 ? 520 : 1020)} scale={0.62} facing={1} progress={0.5} />
            <text x={150 + (i % 7) * 330} y={(i < 7 ? 560 : 1060)} textAnchor="middle" fontSize={34} fill={INK}>{p}</text>
          </g>
        ))}
        <text x={40} y={1140} fontSize={46} fontFamily={FONT.marker} fill={INK}>EXPRESSIONS</text>
        {exprs.map((e, i) => (
          <g key={e}>
            <Rig params={i % 3 === 0 ? mara : hero} pose="stand" expr={e} frame={40} seed={i + 3} x={130 + i * 230} y={1390} scale={0.4} facing={1} />
            <text x={130 + i * 230} y={1440} textAnchor="middle" fontSize={30} fill={INK}>{e}</text>
          </g>
        ))}
      </svg>
    </AbsoluteFill>
  );
};
