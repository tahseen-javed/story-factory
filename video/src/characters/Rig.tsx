import React from "react";
import { INK, OUTFIT, SKIN, HAIR, GLOVE, PAPER, rand } from "../theme";
import { POSES, EXPRS, Joint, PoseDef, ExprDef } from "./poses";

// Original puppet rig ("Paper Crew"): chunky ink-outlined cut-out people with 3/4 bodies and frontal faces.
// One rig renders every character; looks come from params (outfit, hat, hair, age, skin). The thumbnail uses the same rig.

const rad = (d: number) => (d * Math.PI) / 180;
const SW = 6; // ink outline width

const shade = (hex: string, k: number) => {
  const n = parseInt(hex.slice(1), 16);
  const r = Math.max(0, Math.min(255, Math.round(((n >> 16) & 255) * k)));
  const g = Math.max(0, Math.min(255, Math.round(((n >> 8) & 255) * k)));
  const b = Math.max(0, Math.min(255, Math.round((n & 255) * k)));
  return `#${((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1)}`;
};

type LimbOut = { node: React.ReactNode; end: [number, number]; mid: [number, number] };

function limb(x0: number, y0: number, j: Joint, l1: number, l2: number, w: number, color: string, key: string): LimbOut {
  const x1 = x0 + l1 * Math.sin(rad(j[0]));
  const y1 = y0 + l1 * Math.cos(rad(j[0]));
  const x2 = x1 + l2 * Math.sin(rad(j[1]));
  const y2 = y1 + l2 * Math.cos(rad(j[1]));
  const d = `M${x0},${y0} L${x1},${y1} L${x2},${y2}`;
  return {
    node: (
      <g key={key}>
        <path d={d} fill="none" stroke={INK} strokeWidth={w + SW * 2} strokeLinecap="round" strokeLinejoin="round" />
        <path d={d} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" />
      </g>
    ),
    end: [x2, y2],
    mid: [x1, y1],
  };
}

const Prop: React.FC<{ kind: string; x: number; y: number; angle: number }> = ({ kind, x, y, angle }) => {
  const ink = { stroke: INK, strokeWidth: 5, strokeLinejoin: "round" as const };
  switch (kind) {
    case "phone":
      return (
        <g transform={`translate(${x},${y}) rotate(${angle - 150})`}>
          <rect x={-24} y={-70} width={48} height={86} rx={9} fill="#26242b" {...ink} />
          <rect x={-18} y={-63} width={36} height={68} rx={4} fill="#8fd3ff" opacity={0.85} />
        </g>
      );
    case "notepad":
      return (
        <g transform={`translate(${x},${y}) rotate(${angle - 80})`}>
          <rect x={-30} y={-40} width={60} height={78} rx={4} fill="#f7dc6f" {...ink} />
          <path d="M-20,-20 H20 M-20,-4 H20 M-20,12 H12" stroke={INK} strokeWidth={3} opacity={0.55} />
        </g>
      );
    case "pen":
      return (
        <g transform={`translate(${x},${y}) rotate(${angle - 100})`}>
          <rect x={-3.5} y={-34} width={7} height={46} rx={2} fill="#2a5db0" {...ink} strokeWidth={3} />
        </g>
      );
    case "radio":
      return (
        <g transform={`translate(${x},${y}) rotate(0)`}>
          <line x1={14} y1={-30} x2={34} y2={-86} stroke={INK} strokeWidth={5} strokeLinecap="round" />
          <rect x={-44} y={-34} width={88} height={56} rx={9} fill="#7a8f62" {...ink} />
          <circle cx={-18} cy={-8} r={13} fill="#d6d1bf" {...ink} strokeWidth={4} />
          <rect x={8} y={-24} width={28} height={12} rx={3} fill="#2c2f26" />
          <path d="M44,-6 h22 v16" fill="none" stroke={INK} strokeWidth={5} strokeLinecap="round" />
        </g>
      );
    case "crate":
      return (
        <g transform={`translate(${x},${y})`}>
          <rect x={-58} y={-38} width={116} height={64} rx={6} fill="#c79a5a" {...ink} />
          {[-34, 0, 34].map((cx) => (
            <g key={cx}>
              <rect x={cx - 10} y={-72} width={20} height={36} rx={8} fill="#a9dbf2" {...ink} strokeWidth={4} />
              <rect x={cx - 6} y={-80} width={12} height={10} rx={3} fill="#2a5db0" />
            </g>
          ))}
        </g>
      );
    case "cart":
      return (
        <g transform={`translate(${x + 20},${y + 10})`}>
          <path d="M-70,-50 L70,-50 L50,30 L-50,30 Z" fill="#9aa3ad" {...ink} />
          <circle cx={-36} cy={46} r={16} fill="#33323a" {...ink} />
          <circle cx={36} cy={46} r={16} fill="#33323a" {...ink} />
        </g>
      );
    case "flashlight":
      return (
        <g transform={`translate(${x},${y}) rotate(${angle - 90})`}>
          <rect x={-9} y={-40} width={18} height={52} rx={5} fill="#d9a22b" {...ink} />
          <path d="M-14,-40 L14,-40 L22,-58 L-22,-58 Z" fill="#fff6c9" {...ink} strokeWidth={4} />
        </g>
      );
    default:
      return null;
  }
};

const Eye: React.FC<{ cx: number; cy: number; e: ExprDef; blink: boolean; look: number }> = ({ cx, cy, e, blink, look }) => {
  const stroke = { stroke: INK, strokeWidth: 5, strokeLinecap: "round" as const, fill: "none" };
  if (blink || e.eye === "closed") return <path d={`M${cx - 15},${cy} Q${cx},${cy + 7} ${cx + 15},${cy}`} {...stroke} />;
  if (e.eye === "happy") return <path d={`M${cx - 15},${cy + 5} Q${cx},${cy - 12} ${cx + 15},${cy + 5}`} {...stroke} />;
  const ry = e.eye === "wide" ? 24 : e.eye === "narrow" ? 11 : e.eye === "half" ? 17 : 18;
  const rx = e.eye === "wide" ? 18 : 15;
  return (
    <g>
      <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="#fffdf6" stroke={INK} strokeWidth={5} />
      <circle cx={cx + look} cy={cy + (e.eye === "half" ? 4 : 1)} r={e.pupil} fill={INK} />
      <circle cx={cx + look - 2} cy={cy - 2} r={1.8} fill="#fff" />
      {e.eye === "half" && <path d={`M${cx - rx - 2},${cy - 2} L${cx + rx + 2},${cy - 2}`} stroke={INK} strokeWidth={5} strokeLinecap="round" />}
      {e.eye === "narrow" && <path d={`M${cx - rx},${cy - 5} Q${cx},${cy - 12} ${cx + rx},${cy - 5}`} stroke={INK} strokeWidth={5} fill="none" strokeLinecap="round" />}
    </g>
  );
};

const Mouth: React.FC<{ kind: string }> = ({ kind }) => {
  const s = { stroke: INK, strokeWidth: 5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  switch (kind) {
    case "smile": return <path d="M-20,-2 Q0,20 20,-2" fill="none" {...s} />;
    case "frown": return <path d="M-18,9 Q0,-9 18,9" fill="none" {...s} />;
    case "o": return <ellipse cx={0} cy={4} rx={12} ry={15} fill="#5a1f24" {...s} />;
    case "small_o": return <ellipse cx={0} cy={4} rx={7} ry={9} fill="#5a1f24" {...s} />;
    case "open": return <ellipse cx={0} cy={4} rx={17} ry={12} fill="#5a1f24" {...s} />;
    case "grit":
      return (
        <g>
          <rect x={-20} y={-6} width={40} height={18} rx={5} fill="#fffdf6" {...s} />
          <path d="M-10,-6 V12 M0,-6 V12 M10,-6 V12" stroke={INK} strokeWidth={3} />
        </g>
      );
    case "smirk": return <path d="M-18,5 Q4,12 21,-7" fill="none" {...s} />;
    default: return <path d="M-16,2 L16,2" fill="none" {...s} />;
  }
};

export type RigProps = {
  params?: Record<string, any>;
  pose: string;
  expr: string;
  frame: number;
  fps?: number;
  seed?: number;
  x: number;
  y: number;
  scale?: number;
  facing?: 1 | -1;
  progress?: number; // 0..1 across the shot (for travel)
  prop?: string | null;
  mouth?: number; // 0..1 lip-sync opening from the voice (undefined = expression mouth)
  view?: string; // front | three_quarter | back
};

export const Rig: React.FC<RigProps> = ({ params = {}, pose, expr, frame, fps = 30, seed = 1, x, y, scale = 1, facing = 1, progress = 0, prop = null, mouth, view = "front" }) => {
  const P: PoseDef = POSES[pose] || POSES.stand;
  const E: ExprDef = EXPRS[expr] || EXPRS.neutral;
  const t = frame / fps;

  const outfitName = String(params.outfit || "teal");
  const outfit = OUTFIT[outfitName] || outfitName;
  const skin = SKIN[String(params.skin || "tan")] || SKIN.tan;
  const old = params.age === "old";
  const hairName = String(params.hair || "short");
  const hairCol = old ? HAIR.grey : HAIR[String(params.hairColor || "brown")] || HAIR.brown;
  const hat = String(params.hat || "none");
  const pants = params.pants || (old ? "#5a5160" : "#34384f");

  // ---- animation: cycle (walk/run) or idle ----
  let torso = P.torso + (old ? 5 : 0);
  let head = P.head;
  let armB = [...P.armB] as Joint, armF = [...P.armF] as Joint, legB = [...P.legB] as Joint, legF = [...P.legF] as Joint;
  let bob = 0;
  let dx = 0;
  if (P.cycle) {
    const ph = t * Math.PI * 2 * P.cycle.speed;
    const s = Math.sin(ph), c = Math.cos(ph);
    armF = [s * P.cycle.arm + 10, s * P.cycle.arm + 26 + (P.cycle.arm > 40 ? 30 : 0)];
    armB = [-s * P.cycle.arm - 4, -s * P.cycle.arm + 18 + (P.cycle.arm > 40 ? 30 : 0)];
    legF = [s * P.cycle.leg, s * P.cycle.leg - Math.max(0, c) * P.cycle.bend];
    legB = [-s * P.cycle.leg, -s * P.cycle.leg - Math.max(0, -c) * P.cycle.bend];
    bob = -Math.abs(c) * P.cycle.bob;
    dx = (progress - 0.5) * (P.travel || 0);
  }
  const hs = Number(params.headScale || 1);
  const es = Number(params.eyeScale || 1);
  const talking = mouth !== undefined && mouth > 0.06;
  if (talking && !P.cycle) { armF = [armF[0] + mouth! * 9, armF[1] + mouth! * 6]; head += mouth! * 2.2 * Math.sin(t * 7); }
  const gaze = 3 + 2.5 * Math.sin(t * 0.8 + seed);
  const faceX = view === "three_quarter" ? 21 : 5;
  const faceS = view === "three_quarter" ? 0.86 : 1;
  const breathe = 1 + 0.012 * Math.sin(t * Math.PI * 2 / 3.2 + seed);
  const sway = 0.9 * Math.sin(t * Math.PI * 2 / 5.5 + seed * 2);
  head += 1.2 * Math.sin(t * Math.PI * 2 / 4.1 + seed);
  const blinkPeriod = 2.4 + rand(seed * 3.3) * 2.4; // 2.4-4.8 s
  const blink = (t + rand(seed) * blinkPeriod) % blinkPeriod < 0.13;

  // ---- geometry ----
  const HIP_Y = -170 + P.rootY + bob;
  const SH_Y = HIP_Y - 128;
  const frontTone = outfit, backTone = shade(outfit, 0.82);
  const skinBack = shade(skin, 0.9);

  const armWidth = 26, legWidth = 30;
  const aB = limb(-30, SH_Y + 12, armB, 78, 74, armWidth, backTone, "armB");
  const aF = limb(30, SH_Y + 12, armF, 78, 74, armWidth, frontTone, "armF");
  const lB = limb(-14, HIP_Y, legB, 88, 82, legWidth, shade(pants, 0.85), "legB");
  const lF = limb(16, HIP_Y, legF, 88, 82, legWidth, pants, "legF");

  const glove = (p: [number, number], col: string, k: string) => (
    <g key={k}>
      <circle cx={p[0]} cy={p[1]} r={19} fill={col} stroke={INK} strokeWidth={SW} />
      <circle cx={p[0] + 6} cy={p[1] - 6} r={5} fill="#fff" opacity={0.35} />
    </g>
  );
  const shoe = (p: [number, number], col: string, k: string) => (
    <g key={k}>
      <path d={`M${p[0] - 24},${p[1] - 12} L${p[0] + 8},${p[1] - 12} Q${p[0] + 40},${p[1] - 10} ${p[0] + 44},${p[1] + 12} L${p[0] - 24},${p[1] + 12} Z`} fill={col} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
      <path d={`M${p[0] - 24},${p[1] + 6} L${p[0] + 44},${p[1] + 6}`} stroke="#f2ead6" strokeWidth={5} />
    </g>
  );

  const hf = P.holdF || (prop ? prop : undefined);
  const heldFront = prop || P.holdF;
  const heldBack = P.holdB;

  // torso / clothing
  const torsoPath = `M-52,${SH_Y} Q0,${SH_Y - 18} 52,${SH_Y} L60,${HIP_Y + 8} Q0,${HIP_Y + 24} -60,${HIP_Y + 8} Z`;

  const eyeY = -78;
  const browBase = eyeY - 30 + E.browY;

  return (
    <g transform={`translate(${x + dx},${y}) scale(${scale * facing},${scale})`}>
      {/* contact shadow */}
      <ellipse cx={0} cy={6} rx={92} ry={14} fill="#000" opacity={0.28} />
      <g transform={`rotate(${sway} 0 0)`}>
        {/* back limbs */}
        {lB.node}
        {shoe(lB.end, "#2c2a33", "shB")}
        <g transform={`rotate(${torso} 0 ${HIP_Y}) translate(0 ${HIP_Y * (1 - breathe)}) scale(1 ${breathe})`}>
          {aB.node}
          {glove(aB.end, shade(GLOVE, 0.85), "gB")}
          {heldBack ? <Prop kind={heldBack} x={aB.end[0]} y={aB.end[1]} angle={armB[1]} /> : null}
          {/* torso */}
          <path d={torsoPath} fill={frontTone} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
          {old ? (
            <g>
              <path d={`M0,${SH_Y + 6} L0,${HIP_Y + 18}`} stroke={INK} strokeWidth={4} />
              {[0, 1, 2].map((i) => <circle key={i} cx={-10} cy={SH_Y + 44 + i * 32} r={4} fill="#f2ead6" stroke={INK} strokeWidth={2} />)}
              <path d={`M-30,${SH_Y + 2} L0,${SH_Y + 38} L30,${SH_Y + 2}`} fill="#f2ead6" stroke={INK} strokeWidth={4} strokeLinejoin="round" />
            </g>
          ) : (
            <g>
              <path d={`M-34,${SH_Y + 4} Q0,${SH_Y + 30} 34,${SH_Y + 4}`} fill="none" stroke={INK} strokeWidth={4} />
              <rect x={-36} y={HIP_Y - 54} width={72} height={36} rx={12} fill={shade(outfit, 0.9)} stroke={INK} strokeWidth={4} />
            </g>
          )}
          {/* neck + head */}
          <g transform={`rotate(${head} 0 ${SH_Y})`}>
            <rect x={-14} y={SH_Y - 22} width={28} height={30} rx={8} fill={skinBack} stroke={INK} strokeWidth={SW} />
            <g transform={`translate(0 ${SH_Y - 82 - (hs - 1) * 22}) scale(${hs})`}>
              {/* hair behind head */}
              {hairName === "bun" ? <circle cx={-6} cy={-72} r={26} fill={hairCol} stroke={INK} strokeWidth={SW} /> : null}
              <ellipse cx={-64} cy={-4} rx={12} ry={17} fill={skin} stroke={INK} strokeWidth={SW} />
              <ellipse cx={64} cy={-4} rx={12} ry={17} fill={skin} stroke={INK} strokeWidth={SW} />
              <path d="M-62,-6 Q-62,-70 0,-70 Q62,-70 62,-6 Q62,52 0,56 Q-62,52 -62,-6 Z" fill={skin} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
              {/* hair */}
              {hairName === "short" && hat === "none" ? <path d="M-62,-14 Q-66,-72 0,-74 Q66,-72 62,-14 Q40,-40 0,-38 Q-40,-40 -62,-14 Z" fill={hairCol} stroke={INK} strokeWidth={SW} strokeLinejoin="round" /> : null}
              {hairName === "short" && hat !== "none" ? <path d="M-62,-14 Q-60,-30 -50,-34 L50,-34 Q60,-30 62,-14 Z" fill={hairCol} opacity={0.0} /> : null}
              {hairName === "bun" ? <path d="M-62,-4 Q-68,-72 0,-76 Q68,-72 62,-4 Q46,-44 0,-44 Q-46,-44 -62,-4 Z" fill={hairCol} stroke={INK} strokeWidth={SW} strokeLinejoin="round" /> : null}
              {hairName === "curly" ? [-48, -24, 0, 24, 48].map((cx, i) => <circle key={i} cx={cx} cy={-52 - (i % 2) * 6} r={20} fill={hairCol} stroke={INK} strokeWidth={SW} />) : null}
              {/* cap / beanie */}
              {hat === "cap" ? (
                <g>
                  <path d="M-64,-16 Q-66,-84 0,-86 Q66,-84 64,-16 Z" fill={frontTone} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
                  <path d="M-8,-20 Q50,-26 96,-12 Q92,-2 40,-6 Q10,-8 -8,-12 Z" fill={shade(outfit, 0.8)} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
                  <circle cx={0} cy={-84} r={7} fill={shade(outfit, 0.7)} stroke={INK} strokeWidth={4} />
                </g>
              ) : null}
              {hat === "beanie" ? (
                <g>
                  <path d="M-64,-18 Q-66,-92 0,-94 Q66,-92 64,-18 Z" fill={frontTone} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
                  <rect x={-66} y={-30} width={132} height={22} rx={8} fill={shade(outfit, 0.8)} stroke={INK} strokeWidth={SW} />
                </g>
              ) : null}
              {/* face (hidden from behind) */}
              {view === "back" ? (
                <g>
                  <path d="M-62,-6 Q-62,-70 0,-70 Q62,-70 62,-6 Q62,52 0,56 Q-62,52 -62,-6 Z" fill={hat !== "none" ? shade(outfit, 0.9) : hairCol} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
                  <path d="M-30,30 Q0,48 30,30" fill="none" stroke={INK} strokeWidth={4} opacity={0.5} />
                </g>
              ) : null}
              <g transform={`translate(${faceX} 0) scale(${faceS} 1)`} opacity={view === "back" ? 0 : 1}>
                {old ? <path d="M-46,4 q8,6 16,0 M30,4 q8,6 16,0" stroke={INK} strokeWidth={2.5} fill="none" opacity={0.45} /> : null}
                <g transform={`translate(-27 ${eyeY + 70}) scale(${es}) translate(27 ${-(eyeY + 70)})`}><Eye cx={-27} cy={eyeY + 70} e={E} blink={blink} look={gaze} /></g>
                <g transform={`translate(27 ${eyeY + 70}) scale(${es}) translate(-27 ${-(eyeY + 70)})`}><Eye cx={27} cy={eyeY + 70} e={E} blink={blink} look={gaze} /></g>
                <path d={`M-48,${browBase + 66 + 0} L-14,${browBase + 66 - E.browInner}`} stroke={hairName === "bun" || old ? shade(hairCol, 0.8) : INK} strokeWidth={7} strokeLinecap="round" />
                <path d={`M14,${browBase + 66 - E.browInner + (E.browR || 0)} L48,${browBase + 66 + (E.browR ? E.browR * 0.4 : 0)}`} stroke={hairName === "bun" || old ? shade(hairCol, 0.8) : INK} strokeWidth={7} strokeLinecap="round" />
                <g transform="translate(0 30)">{talking ? <ellipse cx={0} cy={5} rx={9 + 9 * mouth!} ry={3 + 17 * mouth!} fill="#5a1f24" stroke={INK} strokeWidth={5} /> : <Mouth kind={E.mouth} />}</g>
                <ellipse cx={-42} cy={16} rx={9} ry={5} fill="#e87a6e" opacity={0.28} />
                <ellipse cx={42} cy={16} rx={9} ry={5} fill="#e87a6e" opacity={0.28} />
              </g>
            </g>
          </g>
          {aF.node}
          {glove(aF.end, GLOVE, "gF")}
          {heldFront ? <Prop kind={heldFront} x={aF.end[0]} y={aF.end[1]} angle={armF[1]} /> : null}
        </g>
        {lF.node}
        {shoe(lF.end, "#34323c", "shF")}
      </g>
    </g>
  );
};
