import React from "react";
import { W, H, INK, OVERSCAN, rand } from "../theme";

// Procedural illustrated backdrops: the guaranteed fallback when SDXL images are unavailable, and the source for smoke tests.
// Drawn in stage coordinates (0..1920 x 0..1080) on an overscanned canvas so cameras never reveal edges.

type Pal = { wall: string; wall2: string; floor: string; floor2: string; sky1: string; sky2: string; light: string; win: boolean; glow: number; dark: string; trim: string };

const PALS: Record<string, Pal> = {
  day: { wall: "#dccaa4", wall2: "#cdb78c", floor: "#a07a52", floor2: "#8a6844", sky1: "#bfe3f2", sky2: "#eaf4e6", light: "#fff3c4", win: false, glow: 0, dark: "#5b4a38", trim: "#f0e6cf" },
  night: { wall: "#47557a", wall2: "#3b4666", floor: "#3a3548", floor2: "#2c2938", sky1: "#0f1a3d", sky2: "#26376b", light: "#ffd27a", win: true, glow: 0.55, dark: "#1c2036", trim: "#8392b8" },
  alarm: { wall: "#6b3f4c", wall2: "#58303d", floor: "#3c2c36", floor2: "#2d2029", sky1: "#2a0f1e", sky2: "#5a1d2f", light: "#ff9a7a", win: true, glow: 0.5, dark: "#2a1822", trim: "#b8808c" },
  dusk: { wall: "#c79a74", wall2: "#b18564", floor: "#7d5a47", floor2: "#684a3a", sky1: "#f2b36b", sky2: "#7e5c9a", light: "#ffd49a", win: true, glow: 0.35, dark: "#4a3340", trim: "#e8cfa8" },
  blackout: { wall: "#3d5168", wall2: "#32445a", floor: "#2b3644", floor2: "#222b38", sky1: "#0a1a2c", sky2: "#1a3550", light: "#9fd7ff", win: false, glow: 0.0, dark: "#1a2735", trim: "#6a8299" },
};

const S = { stroke: INK, strokeWidth: 5, strokeLinejoin: "round" as const };

const Window: React.FC<{ x: number; y: number; w: number; h: number; p: Pal; id: string; city?: boolean }> = ({ x, y, w, h, p, id, city = true }) => (
  <g>
    <defs>
      <linearGradient id={`sky-${id}`} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor={p.sky1} />
        <stop offset="1" stopColor={p.sky2} />
      </linearGradient>
      <clipPath id={`wc-${id}`}><rect x={x} y={y} width={w} height={h} /></clipPath>
    </defs>
    <rect x={x} y={y} width={w} height={h} fill={`url(#sky-${id})`} {...S} />
    {city && (
      <g clipPath={`url(#wc-${id})`}>
        {Array.from({ length: 9 }).map((_, i) => {
          const bw = w / 8;
          const bh = h * (0.25 + rand(i * 3.7 + id.length) * 0.45);
          return (
            <g key={i}>
              <rect x={x + i * bw - 4} y={y + h - bh} width={bw} height={bh} fill={p.dark} opacity={0.85} />
              {p.win && Array.from({ length: 6 }).map((_, j) => rand(i * 17 + j * 5) > 0.55 ? <rect key={j} x={x + i * bw + 8 + (j % 2) * (bw / 2 - 4)} y={y + h - bh + 12 + Math.floor(j / 2) * 24} width={12} height={14} fill={p.light} opacity={0.9} /> : null)}
            </g>
          );
        })}
      </g>
    )}
    <path d={`M${x + w / 2},${y} V${y + h} M${x},${y + h / 2} H${x + w}`} stroke={INK} strokeWidth={6} />
  </g>
);

const Lamp: React.FC<{ x: number; y: number; p: Pal }> = ({ x, y, p }) => (
  <g>
    {p.glow > 0 && <ellipse cx={x} cy={y + 30} rx={260} ry={220} fill={p.light} opacity={p.glow * 0.35} />}
    <path d={`M${x - 40},${y} L${x + 40},${y} L${x + 26},${y - 56} L${x - 26},${y - 56} Z`} fill={p.glow > 0 ? p.light : "#8c8070"} {...S} />
    <rect x={x - 6} y={y} width={12} height={90} fill="#5b4a38" {...S} />
    <ellipse cx={x} cy={y + 94} rx={34} ry={9} fill="#5b4a38" {...S} />
  </g>
);

const Floor: React.FC<{ y: number; p: Pal }> = ({ y, p }) => (
  <g>
    <rect x={-150} y={y} width={W + 300} height={H - y + 150} fill={p.floor} />
    {Array.from({ length: 14 }).map((_, i) => <path key={i} d={`M${-150 + i * 190},${y} L${-250 + i * 220},${H + 150}`} stroke={p.floor2} strokeWidth={4} />)}
    <rect x={-150} y={y - 8} width={W + 300} height={16} fill={p.trim} {...S} />
  </g>
);

const Apartment: React.FC<{ p: Pal; v: string }> = ({ p, v }) => (
  <g>
    <rect x={-150} y={-100} width={W + 300} height={H} fill={p.wall} />
    {Array.from({ length: 10 }).map((_, i) => <rect key={i} x={-150 + i * 240} y={-100} width={120} height={H} fill={p.wall2} opacity={0.35} />)}
    <Floor y={760} p={p} />
    <Window x={1130} y={150} w={520} h={420} p={p} id={`ap-${v}`} />
    <path d="M1090,130 Q1130,300 1110,590 L1180,590 Q1180,300 1160,130 Z M1620,130 Q1600,300 1640,590 L1700,590 Q1690,300 1700,130 Z" fill={v === "day" ? "#e7b6a0" : "#6d4c68"} {...S} />
    {/* bed */}
    <rect x={90} y={620} width={620} height={190} rx={18} fill="#9a7a5f" {...S} />
    <rect x={110} y={560} width={580} height={110} rx={30} fill={v === "day" ? "#e9e2d0" : "#aab4cf"} {...S} />
    <rect x={110} y={600} width={580} height={150} rx={26} fill={v === "alarm" ? "#9d4a58" : "#4f8fa0"} {...S} />
    <ellipse cx={210} cy={590} rx={80} ry={34} fill="#f1ead8" {...S} />
    <rect x={90} y={520} width={40} height={300} fill="#6e5440" {...S} />
    {/* desk + laptop */}
    <rect x={1480} y={640} width={400} height={26} rx={6} fill="#7a5a40" {...S} />
    <path d="M1510,666 V810 M1850,666 V810" stroke={INK} strokeWidth={14} />
    <path d="M1580,640 L1620,560 L1760,560 L1790,640 Z" fill="#2b3040" {...S} />
    <rect x={1590} y={570} width={160} height={60} fill={p.win ? "#7fd0ff" : "#b9c5d0"} opacity={v === "blackout" ? 0.0 : 0.75} />
    <Lamp x={880} y={560} p={p} />
    <rect x={200} y={200} width={200} height={150} fill={p.trim} {...S} />
    <path d="M215,335 L270,260 L320,310 L355,270 L385,335 Z" fill="#7aa88a" opacity={0.7} />
    <ellipse cx={900} cy={880} rx={360} ry={50} fill={v === "day" ? "#c47a6a" : "#5a3a4e"} {...S} opacity={0.9} />
  </g>
);

const Street: React.FC<{ p: Pal; v: string }> = ({ p, v }) => (
  <g>
    <defs>
      <linearGradient id={`st-sky-${v}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={p.sky1} /><stop offset="1" stopColor={p.sky2} /></linearGradient>
    </defs>
    <rect x={-150} y={-150} width={W + 300} height={900} fill={`url(#st-sky-${v})`} />
    {[0, 1, 2, 3, 4].map((i) => {
      const bx = -100 + i * 440, bh = 420 + rand(i * 2.2) * 260, bw = 400;
      return (
        <g key={i}>
          <rect x={bx} y={760 - bh} width={bw} height={bh} fill={i % 2 ? "#8a5a4a" : "#a06a52"} {...S} opacity={v === "blackout" || v === "night" ? 0.92 : 1} />
          {Array.from({ length: 5 }).map((_, r) => Array.from({ length: 4 }).map((_, c) => (
            <rect key={`${r}${c}`} x={bx + 28 + c * 92} y={760 - bh + 34 + r * 88} width={54} height={60} fill={p.win && rand(i * 31 + r * 7 + c) > (v === "blackout" ? 2 : 0.6) ? p.light : p.dark} stroke={INK} strokeWidth={4} />
          )))}
        </g>
      );
    })}
    <rect x={-150} y={760} width={W + 300} height={30} fill="#7d7a80" {...S} />
    <rect x={-150} y={790} width={W + 300} height={400} fill="#3d3d47" />
    <path d={`M-150,930 H${W + 150}`} stroke="#d8cf9a" strokeWidth={8} strokeDasharray="70 60" />
    {[200, 1250].map((cx, k) => (
      <g key={cx}>
        <rect x={cx} y={820} width={380} height={96} rx={34} fill={k ? "#4f7f9a" : "#b8503f"} {...S} />
        <path d={`M${cx + 70},${822} Q${cx + 110},${760} ${cx + 190},${760} L${cx + 270},${760} Q${cx + 320},${790} ${cx + 330},${822} Z`} fill={k ? "#6fa0b8" : "#d06a55"} {...S} />
        <circle cx={cx + 90} cy={918} r={34} fill="#222" {...S} /><circle cx={cx + 292} cy={918} r={34} fill="#222" {...S} />
      </g>
    ))}
    <g>
      <rect x={1700} y={160} width={14} height={600} fill="#59555f" {...S} />
      <rect x={1620} y={110} width={170} height={110} rx={10} fill={p.win ? p.light : "#c9c2a8"} {...S} opacity={v === "blackout" ? 0.5 : 1} />
    </g>
    {p.glow > 0 && [330, 1020].map((lx) => <g key={lx}><rect x={lx} y={300} width={10} height={460} fill="#59555f" {...S} /><ellipse cx={lx + 5} cy={330} rx={170} ry={120} fill={p.light} opacity={p.glow * 0.3} /><circle cx={lx + 5} cy={300} r={22} fill={p.light} {...S} /></g>)}
  </g>
);

const GasStation: React.FC<{ p: Pal; v: string }> = ({ p, v }) => (
  <g>
    <defs><linearGradient id={`gs-sky-${v}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={p.sky1} /><stop offset="1" stopColor={p.sky2} /></linearGradient></defs>
    <rect x={-150} y={-150} width={W + 300} height={950} fill={`url(#gs-sky-${v})`} />
    <path d="M-150,640 Q300,560 700,620 T1500,600 T2100,620 V800 H-150 Z" fill={p.dark} opacity={0.55} />
    <rect x={-150} y={790} width={W + 300} height={400} fill="#5b5961" />
    <rect x={-150} y={790} width={W + 300} height={20} fill="#8c8a8f" {...S} />
    <rect x={150} y={150} width={1250} height={120} rx={8} fill="#e8e1cf" {...S} />
    <rect x={150} y={270} width={1250} height={30} fill={v === "day" ? "#d8553f" : "#a63c3a"} {...S} />
    {[250, 700, 1150].map((px) => <rect key={px} x={px} y={300} width={44} height={490} fill="#cfc7b2" {...S} />)}
    {[420, 900].map((px, k) => (
      <g key={px}>
        <rect x={px} y={560} width={150} height={230} rx={10} fill="#c8453b" {...S} />
        <rect x={px + 20} y={590} width={110} height={70} fill="#2f3b48" {...S} />
        <path d={`M${px + 150},${620} q60,10 60,70 v90`} fill="none" stroke={INK} strokeWidth={9} />
      </g>
    ))}
    <rect x={1460} y={380} width={560} height={410} fill="#cdbd9a" {...S} />
    <rect x={1500} y={430} width={300} height={220} fill={p.win ? p.light : "#8fb8c8"} {...S} opacity={v === "blackout" ? 0.35 : 1} />
    <rect x={1830} y={470} width={100} height={320} fill="#7a5a40" {...S} />
    <rect x={1520} y={110} width={420} height={230} rx={14} fill={p.win ? p.light : "#e7e0c8"} {...S} opacity={v === "blackout" ? 0.4 : 1} />
    <rect x={1700} y={340} width={16} height={200} fill="#59555f" />
  </g>
);

const Hallway: React.FC<{ p: Pal; v: string }> = ({ p, v }) => (
  <g>
    <rect x={-150} y={-150} width={W + 300} height={H + 300} fill={p.wall2} />
    <path d="M-150,-150 L560,260 L1360,260 L2070,-150 Z" fill={p.wall} {...S} />
    <path d="M-150,1230 L560,820 L1360,820 L2070,1230 Z" fill={p.floor} {...S} />
    <rect x={560} y={260} width={800} height={560} fill={p.dark} {...S} />
    <path d="M560,260 L-150,-150 M1360,260 L2070,-150 M560,820 L-150,1230 M1360,820 L2070,1230" stroke={INK} strokeWidth={5} />
    {[0, 1, 2].map((i) => {
      const x = 60 + i * 190, w = 150 - i * 30;
      return (<g key={`L${i}`}><path d={`M${x},${130 + i * 60} L${x + w},${200 + i * 60} V${760 - i * 20} L${x},${860 - i * 12} Z`} fill={i % 2 ? "#8a6c4c" : "#9a7a58"} {...S} /><circle cx={x + w - 20} cy={500} r={7} fill="#d8b24a" {...S} /></g>);
    })}
    {[0, 1, 2].map((i) => {
      const x = 1860 - i * 190, w = 150 - i * 30;
      return (<g key={`R${i}`}><path d={`M${x},${130 + i * 60} L${x - w},${200 + i * 60} V${760 - i * 20} L${x},${860 - i * 12} Z`} fill={i % 2 ? "#8a6c4c" : "#9a7a58"} {...S} /><circle cx={x - w + 20} cy={500} r={7} fill="#d8b24a" {...S} /></g>);
    })}
    <rect x={820} y={300} width={280} height={420} fill="#7a5a40" {...S} />
    <rect x={875} y={140} width={170} height={60} rx={8} fill={v === "blackout" ? "#25503a" : "#3fcf7a"} {...S} opacity={v === "blackout" ? 0.7 : 1} />
    {[300, 1620].map((lx) => <g key={lx}>{p.glow > 0 && <ellipse cx={lx} cy={260} rx={170} ry={130} fill={p.light} opacity={p.glow * 0.3} />}<rect x={lx - 22} y={210} width={44} height={70} rx={10} fill={p.glow > 0 ? p.light : "#8c8070"} {...S} /></g>)}
    <path d="M560,820 L1360,820 L1180,1100 L740,1100 Z" fill={p.floor2} opacity={0.5} />
  </g>
);

const Kitchen: React.FC<{ p: Pal; v: string }> = ({ p, v }) => (
  <g>
    <rect x={-150} y={-100} width={W + 300} height={900} fill={p.wall} />
    {Array.from({ length: 22 }).map((_, i) => Array.from({ length: 6 }).map((_, j) => <rect key={`${i}-${j}`} x={-150 + i * 110} y={420 + j * 70} width={106} height={66} fill={(i + j) % 2 ? p.wall2 : p.wall} opacity={0.65} />))}
    <Floor y={800} p={p} />
    <rect x={90} y={150} width={330} height={650} rx={22} fill="#dfe5e8" {...S} />
    <path d="M90,420 H420" stroke={INK} strokeWidth={6} /><rect x={380} y={230} width={14} height={110} rx={6} fill="#8d9aa3" {...S} /><rect x={380} y={470} width={14} height={160} rx={6} fill="#8d9aa3" {...S} />
    <Window x={760} y={170} w={380} h={300} p={p} id={`kt-${v}`} />
    <path d="M740,150 H1160 M750,150 Q760,330 740,480 M1150,150 Q1140,330 1160,480" fill="none" stroke={INK} strokeWidth={5} />
    <rect x={1300} y={150} width={420} height={320} fill="#e6dcc0" {...S} />
    {Array.from({ length: 6 }).map((_, i) => <path key={i} d={`M1300,${150 + i * 53} H1720 M${1300 + i * 70},150 V470`} stroke="#6aa6c8" strokeWidth={2.5} />)}
    <path d="M1360,220 L1450,300 L1560,260 L1650,380 M1450,300 L1470,420" stroke="#d8553f" strokeWidth={5} fill="none" />
    <circle cx={1360} cy={220} r={9} fill="#d8553f" /><circle cx={1650} cy={380} r={9} fill="#d8553f" />
    <rect x={1250} y={560} width={560} height={30} rx={8} fill="#8a6a4a" {...S} />
    <rect x={1330} y={590} width={30} height={220} fill="#6e5440" {...S} /><rect x={1700} y={590} width={30} height={220} fill="#6e5440" {...S} />
    <rect x={1400} y={500} width={90} height={60} rx={10} fill="#7a8f62" {...S} /><circle cx={1432} cy={530} r={13} fill="#d6d1bf" {...S} />
    <rect x={520} y={620} width={180} height={190} fill="#c9b690" {...S} />
    <Lamp x={620} y={470} p={p} />
  </g>
);

const Stairwell: React.FC<{ p: Pal; v: string }> = ({ p, v }) => (
  <g>
    <rect x={-150} y={-150} width={W + 300} height={H + 300} fill={p.wall2} />
    {Array.from({ length: 8 }).map((_, i) => <rect key={i} x={-150 + i * 300} y={-150} width={4} height={H + 300} fill={INK} opacity={0.35} />)}
    <Window x={1250} y={120} w={300} h={480} p={p} id={`sw-${v}`} city={false} />
    <Window x={1620} y={120} w={300} h={480} p={p} id={`sw2-${v}`} city={false} />
    {Array.from({ length: 9 }).map((_, i) => (
      <g key={i}>
        <path d={`M${-100 + i * 150},${1000 - i * 70} H${50 + i * 150} V${1030 - i * 70} H${-100 + i * 150} Z`} fill={p.floor} {...S} />
      </g>
    ))}
    <path d={`M-100,${900} L1250,${260}`} stroke={INK} strokeWidth={9} /><path d={`M-100,${820} L1250,${180}`} stroke={INK} strokeWidth={9} />
    {Array.from({ length: 10 }).map((_, i) => <path key={i} d={`M${-60 + i * 135},${885 - i * 62} V${805 - i * 62}`} stroke={INK} strokeWidth={6} />)}
    <rect x={1240} y={760} width={680} height={320} fill={p.floor} {...S} />
    <path d="M900,-150 V100" stroke={INK} strokeWidth={5} />
    {p.glow > 0 ? <ellipse cx={900} cy={150} rx={300} ry={240} fill={p.light} opacity={p.glow * 0.35} /> : null}
    <circle cx={900} cy={120} r={26} fill={p.glow > 0 ? p.light : "#8c8070"} {...S} />
  </g>
);

const Rooftop: React.FC<{ p: Pal; v: string }> = ({ p, v }) => (
  <g>
    <defs><linearGradient id={`rt-sky-${v}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={p.sky1} /><stop offset="1" stopColor={p.sky2} /></linearGradient></defs>
    <rect x={-150} y={-150} width={W + 300} height={1000} fill={`url(#rt-sky-${v})`} />
    {v !== "day" && Array.from({ length: 36 }).map((_, i) => <circle key={i} cx={rand(i * 3.3) * W} cy={rand(i * 7.1) * 330} r={1.5 + rand(i) * 2.5} fill="#f4f1e0" opacity={v === "dusk" ? 0.25 : 0.85} />)}
    {Array.from({ length: 14 }).map((_, i) => {
      const bw = 170 + rand(i * 2.9) * 90, bx = -120 + i * 150, bh = 220 + rand(i * 5.1) * 330;
      return (
        <g key={i}>
          <rect x={bx} y={780 - bh} width={bw} height={bh} fill={p.dark} stroke={INK} strokeWidth={4} opacity={0.96} />
          {p.win && Array.from({ length: 12 }).map((_, k) => rand(i * 19 + k * 3.3) > (v === "blackout" ? 5 : 0.62) ? <rect key={k} x={bx + 14 + (k % 3) * 46} y={780 - bh + 20 + Math.floor(k / 3) * 38} width={20} height={20} fill={p.light} opacity={0.9} /> : null)}
        </g>
      );
    })}
    <rect x={-150} y={760} width={W + 300} height={440} fill="#7c7a80" {...S} />
    <rect x={-150} y={700} width={W + 300} height={70} fill="#9a5a48" {...S} />
    {Array.from({ length: 24 }).map((_, i) => <path key={i} d={`M${-150 + i * 120},700 v70`} stroke={INK} strokeWidth={3} />)}
    {[1350, 1600].map((x, k) => (<g key={x}><rect x={x} y={420} width={190} height={250} rx={14} fill="#8d7155" {...S} />{[450, 520, 590].map((yy) => <path key={yy} d={`M${x},${yy} H${x + 190}`} stroke={INK} strokeWidth={4} />)}<path d={`M${x + 20},670 L${x - 6},760 M${x + 170},670 L${x + 196},760`} stroke={INK} strokeWidth={9} /><path d={`M${x - 8},420 Q${x + 95},350 ${x + 198},420 Z`} fill="#6e5a46" {...S} /></g>))}
    <path d="M200,700 V470 M200,520 H300 M200,580 H330 M200,640 H300" stroke={INK} strokeWidth={8} />
    <path d="M1000,700 V380 M960,430 H1040 M970,480 H1030" stroke={INK} strokeWidth={7} />
  </g>
);

const Generic: React.FC<{ p: Pal }> = ({ p }) => (
  <g>
    <rect x={-150} y={-150} width={W + 300} height={H + 300} fill={p.wall} />
    <Floor y={780} p={p} />
  </g>
);

export const ProceduralBackdrop: React.FC<{ location: string; variant: string }> = ({ location, variant }) => {
  const p = PALS[variant] || PALS.day;
  const Scene =
    location === "apartment" ? Apartment :
    location === "street" ? Street :
    location === "gas_station" ? GasStation :
    location === "hallway" ? Hallway :
    location === "kitchen" ? Kitchen :
    location === "stairwell" ? Stairwell :
    location === "rooftop" ? Rooftop : null;
  const mx = W * OVERSCAN / 2, my = H * OVERSCAN / 2;
  return (
    <svg
      width={W * (1 + OVERSCAN)}
      height={H * (1 + OVERSCAN)}
      viewBox={`${-mx} ${-my} ${W * (1 + OVERSCAN)} ${H * (1 + OVERSCAN)}`}
      style={{ position: "absolute", left: -mx, top: -my }}
    >
      {Scene ? <Scene p={p} v={variant} /> : <Generic p={p} />}
    </svg>
  );
};
