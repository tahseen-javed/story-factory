import React from "react";
import { AbsoluteFill } from "remotion";
import { INK, PAPER, PAPER_SHADE, NOTE_YELLOW, ALERT_RED, GLOVE, FONT, ACCENT, W, H, clamp, easeOut, easeInOut, rand } from "../theme";
import { OvProps, OverlayFrame, Paper, Reveal, prog, Tape } from "./common";

const LABELS: Record<string, string> = { hours: "HOURS LEFT", water: "WATER", phone: "PHONE", cash: "CASH", power: "POWER", tank: "FUEL", food: "FOOD", days: "DAYS LEFT" };
const label = (k: string) => LABELS[k] || k.replace(/_/g, " ").toUpperCase();
const fmtVal = (k: string, v: any) => (k === "hours" ? (typeof v === "number" ? `${v} h` : `${v} h`) : String(v));

/* ---------------- NotepadTracker ---------------- */
export const NotepadTracker: React.FC<OvProps> = ({ args, frame, total, accent, track, prevTrack }) => {
  const title = String(args[0] ?? "SURVIVAL LOG");
  const keys = Object.keys(track).slice(0, 6);
  return (
    <OverlayFrame frame={frame} total={total} rot={-2.5}>
      <Paper w={840} h={150 + keys.length * 92 + 60} color={NOTE_YELLOW}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 74, background: ACCENT[accent] || ACCENT.amber, borderBottom: `6px solid ${INK}`, display: "flex", alignItems: "center", padding: "0 30px", fontFamily: FONT.marker, fontSize: 48, color: INK, letterSpacing: 2 }}>{title}</div>
        <div style={{ position: "absolute", left: 66, top: 74, bottom: 0, width: 4, background: "#d9534f", opacity: 0.7 }} />
        {keys.map((k, i) => {
          const rowP = prog(frame, 8 + i * 7, 10);
          const changed = prevTrack && k in prevTrack && String(prevTrack[k]) !== String(track[k]);
          const newP = prog(frame, 24 + i * 7, 14);
          return (
            <div key={k} style={{ position: "absolute", left: 92, right: 30, top: 100 + i * 92, height: 84, borderBottom: "3px solid rgba(60,90,160,0.45)", display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
              <Reveal p={rowP}><span style={{ fontFamily: FONT.hand, fontSize: 52, color: INK }}>{label(k)}</span></Reveal>
              <div style={{ display: "flex", gap: 22, alignItems: "flex-end", fontFamily: FONT.note, fontWeight: 700, fontSize: 70, color: INK }}>
                {changed ? <span style={{ position: "relative", opacity: 0.55 }}>{fmtVal(k, prevTrack[k])}<span style={{ position: "absolute", left: -6, right: -6, top: "52%", height: 7, background: "#d9534f", transform: "rotate(-4deg)", width: `${easeOut(newP) * 110}%` }} /></span> : null}
                <Reveal p={changed ? newP : rowP}><span style={{ color: changed ? "#1d6fb8" : INK }}>{fmtVal(k, track[k])}</span></Reveal>
              </div>
            </div>
          );
        })}
      </Paper>
    </OverlayFrame>
  );
};

/* ---------------- CalendarCountdown ---------------- */
export const CalendarCountdown: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const left = Number(args[0] ?? 6), tot = Math.max(left, Number(args[1] ?? 14)), elapsed = tot - left;
  const cells = Array.from({ length: tot });
  return (
    <OverlayFrame frame={frame} total={total} rot={2}>
      <Paper w={900} h={720} color="#fbf6ea">
        <div style={{ height: 90, background: ACCENT[accent] || ACCENT.crimson, borderBottom: `6px solid ${INK}`, fontFamily: FONT.marker, fontSize: 54, display: "flex", alignItems: "center", padding: "0 34px" }}>{String(args[2] ?? "COUNTDOWN")}</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 8, padding: 26 }}>
          {cells.map((_, i) => {
            const xp = prog(frame, 10 + i * 4, 10);
            return (
              <div key={i} style={{ height: 78, border: `3px solid ${INK}`, background: "#fff", position: "relative", fontFamily: FONT.hand, fontSize: 34, padding: 4 }}>{i + 1}
                {i < elapsed ? <svg width="100%" height="100%" viewBox="0 0 100 78" style={{ position: "absolute", inset: 0 }}><path d="M12,8 L88,70 M88,8 L12,70" stroke="#d9322e" strokeWidth={9} strokeLinecap="round" strokeDasharray={200} strokeDashoffset={200 * (1 - easeOut(xp))} /></svg> : null}
              </div>
            );
          })}
        </div>
        <div style={{ position: "absolute", right: 24, bottom: 20, transform: "rotate(-6deg)", border: "8px solid #d9322e", color: "#d9322e", fontFamily: FONT.display, fontSize: 84, padding: "4px 24px", opacity: prog(frame, 30, 8), letterSpacing: 2 }}>{left} DAYS LEFT</div>
      </Paper>
    </OverlayFrame>
  );
};

/* ---------------- StickyNote ---------------- */
export const StickyNote: React.FC<OvProps> = ({ args, frame, total }) => (
  <OverlayFrame frame={frame} total={total} rot={-4}>
    <Paper w={560} h={560} color={NOTE_YELLOW} radius={4}>
      <div style={{ padding: "70px 40px", textAlign: "center", fontFamily: FONT.note, fontWeight: 700, color: INK }}>
        <Reveal p={prog(frame, 6, 12)}><div style={{ fontSize: args[1] ? 170 : 150, lineHeight: 1 }}>{String(args[0])}</div></Reveal>
        {args[1] ? <Reveal p={prog(frame, 16, 14)}><div style={{ fontSize: 78, marginTop: 24, lineHeight: 1.05 }}>{String(args[1])}</div></Reveal> : null}
      </div>
    </Paper>
  </OverlayFrame>
);

/* ---------------- LabelTag ---------------- */
export const LabelTag: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const text = String(args[0]);
  const w = clamp(text.length * 52 + 150, 420, 1100);
  return (
    <OverlayFrame frame={frame} total={total} rot={-3}>
      <div style={{ position: "relative" }}>
        <svg width={w} height={260} viewBox={`0 0 ${w} 260`} style={{ overflow: "visible" }}>
          <path d={`M70,10 L${w - 20},10 L${w - 20},250 L70,250 L10,130 Z`} fill="#e3c58f" stroke={INK} strokeWidth={7} strokeLinejoin="round" />
          <circle cx={62} cy={130} r={16} fill="#3a2f26" stroke={INK} strokeWidth={5} />
          <path d={`M62,130 C-40,60 -60,-30 20,-70`} fill="none" stroke={INK} strokeWidth={5} />
          <rect x={90} y={22} width={w - 130} height={14} fill={ACCENT[accent] || ACCENT.amber} opacity={0.8} />
        </svg>
        <div style={{ position: "absolute", left: 100, right: 40, top: 0, height: 260, display: "flex", alignItems: "center", fontFamily: FONT.marker, fontSize: 84, color: INK }}>
          <Reveal p={prog(frame, 6, 16)}>{text}</Reveal>
        </div>
      </div>
    </OverlayFrame>
  );
};

/* ---------------- Receipt ---------------- */
export const Receipt: React.FC<OvProps> = ({ args, frame, total }) => {
  const title = String(args[0]);
  const lines = args.slice(1).map(String);
  const zig = (up: boolean) => Array.from({ length: 15 }).map((_, i) => `${(i / 14) * 100}% ${i % 2 ? (up ? "0" : "100%") : (up ? "14px" : "calc(100% - 14px)")}`);
  const clip = `polygon(${zig(true).join(",")}, ${zig(false).reverse().join(",")})`;
  return (
    <OverlayFrame frame={frame} total={total} rot={2.5}>
      <div style={{ width: 600, padding: "46px 40px 56px", background: "#fbf8ee", clipPath: clip, fontFamily: FONT.ui, color: INK, boxShadow: "inset 0 0 0 4px #00000010" }}>
        <div style={{ textAlign: "center", fontWeight: 800, fontSize: 52, letterSpacing: 3, marginBottom: 6 }}>{title}</div>
        <div style={{ textAlign: "center", fontSize: 24, opacity: 0.6, marginBottom: 18 }}>------ THANK YOU ------</div>
        {lines.map((ln, i) => {
          const last = i === lines.length - 1;
          const parts = ln.split(/\s{2,}/);
          return (
            <Reveal key={i} p={prog(frame, 8 + i * 8, 8)}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: last ? 46 : 38, fontWeight: last ? 800 : 500, padding: "8px 0", borderTop: last ? `4px dashed ${INK}` : "none", marginTop: last ? 14 : 0, fontVariantNumeric: "tabular-nums" }}>
                <span>{parts[0]}</span>
                <span>{parts[1] ?? ""}</span>
              </div>
            </Reveal>
          );
        })}
      </div>
    </OverlayFrame>
  );
};

/* ---------------- PaperDiagram ---------------- */
const Icon: React.FC<{ name: string; c: string }> = ({ name, c }) => {
  const n = name.toLowerCase();
  if (n.includes("sun")) return <g><circle cx={0} cy={0} r={34} fill="#f6b73c" stroke={INK} strokeWidth={5} />{Array.from({ length: 10 }).map((_, i) => <path key={i} d={`M${Math.cos(i * 0.628) * 46},${Math.sin(i * 0.628) * 46} L${Math.cos(i * 0.628) * 66},${Math.sin(i * 0.628) * 66}`} stroke={INK} strokeWidth={6} strokeLinecap="round" />)}</g>;
  if (n.includes("earth")) return <g><circle cx={0} cy={0} r={46} fill="#4f9fd6" stroke={INK} strokeWidth={5} /><path d="M-26,-14 q14,-18 28,-6 q-4,14 -14,14 q-8,10 -16,0 z M10,14 q18,-4 22,10 q-12,12 -22,2 z" fill="#79b86a" stroke={INK} strokeWidth={3} /></g>;
  if (n.includes("storm") || n.includes("cloud")) return <g><path d="M-48,16 q-14,-34 22,-34 q10,-34 46,-12 q36,-4 34,28 q0,18 -20,18 h-66 q-16,0 -16,0 z" fill="#d7d2e6" stroke={INK} strokeWidth={5} /><path d="M2,12 l-14,30 l16,-6 l-8,28" fill="none" stroke="#f2b632" strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" /></g>;
  if (n.includes("grid") || n.includes("power")) return <g><path d="M0,-60 V60 M-36,-30 H36 M-28,-6 H28 M-40,18 H40 M-44,60 L0,-60 L44,60" fill="none" stroke={INK} strokeWidth={6} strokeLinecap="round" /><path d="M-90,-30 Q0,-10 90,-30" fill="none" stroke={INK} strokeWidth={3} /></g>;
  return <rect x={-34} y={-34} width={68} height={68} rx={12} fill={c} stroke={INK} strokeWidth={5} />;
};
export const PaperDiagram: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const title = String(args[0]);
  const nodes = args.slice(1).map(String);
  const n = nodes.length;
  const w = 1480, step = (w - 220) / Math.max(1, n - 1);
  return (
    <OverlayFrame frame={frame} total={total} rot={-1.2}>
      <Paper w={w} h={560} color="#f6efdc">
        <div style={{ position: "absolute", left: 40, top: 26, fontFamily: FONT.marker, fontSize: 54, color: INK }}>{title}</div>
        <svg width={w} height={560} style={{ position: "absolute", inset: 0 }}>
          {nodes.map((nm, i) => {
            const x = 110 + i * step, y = 300;
            const ap = prog(frame, 8 + i * 14, 12);
            return (
              <g key={i} opacity={ap}>
                <g transform={`translate(${x},${y - 20}) scale(${1.05 + 0.1 * (1 - ap)})`}><Icon name={nm} c={ACCENT[accent] || ACCENT.amber} /></g>
                <text x={x} y={y + 110} textAnchor="middle" fontFamily={FONT.hand} fontSize={44} fill={INK}>{nm}</text>
                {i < n - 1 ? (() => {
                  const x0 = x + 82, x1 = x + step - 82, dp = prog(frame, 16 + i * 14, 12);
                  return <g><path d={`M${x0},${y - 22} Q${(x0 + x1) / 2},${y - 70} ${x1 - 10},${y - 22}`} fill="none" stroke={INK} strokeWidth={7} strokeLinecap="round" strokeDasharray={600} strokeDashoffset={600 * (1 - easeOut(dp))} /><path d={`M${x1 - 34},${y - 40} L${x1 - 6},${y - 20} L${x1 - 38},${y - 8}`} fill="none" stroke={INK} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" opacity={dp} /></g>;
                })() : null}
              </g>
            );
          })}
        </svg>
      </Paper>
    </OverlayFrame>
  );
};

/* ---------------- PhoneScreen (alert/web/video/call/search) ---------------- */
export const PhoneScreen: React.FC<OvProps & { mode: string }> = ({ args, frame, total, accent, mode }) => {
  const buzz = mode === "alert" ? Math.sin(frame * 1.9) * 3 * (frame < 50 ? 1 : 0.3) : 0;
  const pw = 520, ph = 960;
  const A = args.map(String);
  let screen: React.ReactNode = null;
  if (mode === "alert") {
    const pulse = 0.5 + 0.5 * Math.sin((frame / 30) * Math.PI * 2 * 1.5);
    screen = (
      <div style={{ position: "absolute", inset: 0, background: "#16181f", fontFamily: FONT.ui, color: "#fff", padding: 26 }}>
        <div style={{ height: 520, marginTop: 90, borderRadius: 26, background: `linear-gradient(180deg, ${ALERT_RED}, #8e1f27)`, padding: 34, boxShadow: `0 0 ${30 + pulse * 40}px ${ALERT_RED}` }}>
          <div style={{ fontSize: 30, fontWeight: 700, opacity: 0.85, marginBottom: 16 }}>! ALERT</div>
          <div style={{ fontSize: 58, fontWeight: 900, lineHeight: 1.05, letterSpacing: 1 }}>{A[0]}</div>
          <div style={{ fontSize: 38, fontWeight: 500, marginTop: 24, lineHeight: 1.2 }}>{A[1]}</div>
        </div>
        <div style={{ marginTop: 40, height: 64, borderRadius: 32, background: "#2a2d38", textAlign: "center", fontSize: 30, lineHeight: "64px" }}>Slide to dismiss</div>
      </div>
    );
  } else if (mode === "web") {
    screen = (
      <div style={{ position: "absolute", inset: 0, background: "#f4f4f1", fontFamily: FONT.ui, color: INK, padding: 22 }}>
        <div style={{ marginTop: 70, height: 56, borderRadius: 28, background: "#dedbd3", padding: "0 22px", fontSize: 26, lineHeight: "56px", overflow: "hidden", whiteSpace: "nowrap" }}>{A[0]}</div>
        <div style={{ marginTop: 28, height: 230, borderRadius: 14, background: `linear-gradient(135deg, ${ACCENT[accent] || ACCENT.cobalt}, #263a5e)` }} />
        <div style={{ marginTop: 22, fontSize: 44, fontWeight: 800, lineHeight: 1.1 }}>{A[1]}</div>
        <div style={{ marginTop: 14, fontSize: 28, lineHeight: 1.3, opacity: 0.75 }}>{A[2]}</div>
        {[0, 1, 2].map((i) => <div key={i} style={{ marginTop: 14, height: 18, borderRadius: 9, background: "#d8d5cc", width: `${92 - i * 14}%` }} />)}
      </div>
    );
  } else if (mode === "video") {
    screen = (
      <div style={{ position: "absolute", inset: 0, background: "#0f0f12", fontFamily: FONT.ui, color: "#fff", padding: 20 }}>
        <div style={{ marginTop: 70, height: 300, borderRadius: 12, background: "linear-gradient(135deg,#3a4d78,#14172a)", position: "relative" }}><div style={{ position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)", width: 110, height: 110, borderRadius: 55, background: "rgba(255,255,255,0.92)" }}><div style={{ position: "absolute", left: 42, top: 28, borderLeft: "42px solid #111", borderTop: "27px solid transparent", borderBottom: "27px solid transparent" }} /></div></div>
        <div style={{ height: 10, marginTop: 16, borderRadius: 5, background: "#444" }}><div style={{ width: `${20 + prog(frame, 0, total) * 60}%`, height: 10, borderRadius: 5, background: "#ff3b3b" }} /></div>
        <div style={{ marginTop: 22, fontSize: 38, fontWeight: 800 }}>{A[0]}</div>
        <div style={{ marginTop: 10, fontSize: 28, opacity: 0.7 }}>{A[1]}</div>
      </div>
    );
  } else if (mode === "call") {
    const pulse = prog(frame % 30, 0, 30);
    screen = (
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg,#25304a,#0e1220)", fontFamily: FONT.ui, color: "#fff", textAlign: "center" }}>
        <div style={{ marginTop: 130, margin: "130px auto 0", width: 200, height: 200, borderRadius: 100, background: "#7d93c6", boxShadow: `0 0 0 ${pulse * 60}px rgba(125,147,198,${0.4 * (1 - pulse)})`, fontSize: 110, lineHeight: "200px", fontWeight: 800 }}>{A[0].slice(0, 1)}</div>
        <div style={{ marginTop: 30, fontSize: 56, fontWeight: 800 }}>{A[0]}</div>
        <div style={{ marginTop: 10, fontSize: 32, opacity: 0.75 }}>{A[1]}</div>
        <div style={{ position: "absolute", left: 60, right: 60, bottom: 90, display: "flex", justifyContent: "space-between" }}>
          <div style={{ width: 130, height: 130, borderRadius: 65, background: "#e04646" }} /><div style={{ width: 130, height: 130, borderRadius: 65, background: "#38c172" }} />
        </div>
      </div>
    );
  } else {
    const rs = A.slice(1);
    screen = (
      <div style={{ position: "absolute", inset: 0, background: "#fff", fontFamily: FONT.ui, color: INK, padding: 22 }}>
        <div style={{ marginTop: 72, height: 66, borderRadius: 33, border: "3px solid #bbb", padding: "0 26px", fontSize: 32, lineHeight: "60px", overflow: "hidden", whiteSpace: "nowrap" }}>{A[0]}<span style={{ opacity: frame % 20 < 10 ? 1 : 0 }}>|</span></div>
        {rs.map((r, i) => (
          <div key={i} style={{ marginTop: 28, opacity: prog(frame, 10 + i * 10, 8) }}>
            <div style={{ fontSize: 22, color: "#2a6a3a" }}>www.news-site.example</div>
            <div style={{ fontSize: 34, fontWeight: 700, color: "#1a3fa0", marginTop: 4 }}>{r}</div>
            <div style={{ height: 14, marginTop: 8, borderRadius: 7, background: "#e4e2dc", width: "90%" }} />
          </div>
        ))}
      </div>
    );
  }
  return (
    <OverlayFrame frame={frame} total={total} rot={-6} x={1040 + buzz * 2} y={600 + buzz}>
      <svg width={760} height={1100} viewBox="-120 -60 760 1100" style={{ overflow: "visible", position: "absolute", left: -120, top: -60, pointerEvents: "none" }} />
      <div style={{ position: "relative", width: pw, height: ph }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: 60, background: "#1b1a20", border: `8px solid ${INK}`, boxShadow: "0 0 0 6px #4c4a55 inset" }} />
        <div style={{ position: "absolute", left: 18, top: 18, right: 18, bottom: 18, borderRadius: 44, overflow: "hidden" }}>{screen}</div>
        <div style={{ position: "absolute", left: "50%", top: 26, width: 150, height: 30, marginLeft: -75, borderRadius: 15, background: "#0b0b0e" }} />
        <svg width={pw} height={ph + 300} viewBox={`0 0 ${pw} ${ph + 300}`} style={{ position: "absolute", left: 0, top: 0, overflow: "visible", pointerEvents: "none" }}>
          {[0, 1, 2].map((i) => <rect key={i} x={-34} y={300 + i * 92} width={96} height={74} rx={36} fill={GLOVE} stroke={INK} strokeWidth={7} />)}
          <rect x={pw - 66} y={420} width={104} height={80} rx={38} fill={GLOVE} stroke={INK} strokeWidth={7} transform={`rotate(-16 ${pw} 460)`} />
          <rect x={150} y={ph - 40} width={230} height={300} rx={44} fill={GLOVE} stroke={INK} strokeWidth={7} />
          <rect x={140} y={ph + 130} width={250} height={64} rx={14} fill="#3e3a48" stroke={INK} strokeWidth={7} />
        </svg>
      </div>
    </OverlayFrame>
  );
};

/* ---------------- TVNews ---------------- */
export const TVNews: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const [headline, lower, ticker] = [String(args[0]), String(args[1] ?? ""), String(args[2] ?? "")];
  return (
    <OverlayFrame frame={frame} total={total} rot={-1.5}>
      <div style={{ width: 1280, height: 860, borderRadius: 60, background: "#2b2a31", border: `8px solid ${INK}`, padding: 46, boxShadow: "0 0 0 8px #0003 inset" }}>
        <div style={{ position: "relative", width: "100%", height: "100%", borderRadius: 34, overflow: "hidden", background: "linear-gradient(180deg,#27406e,#10192f)" }}>
          <svg width="1188" height="768" style={{ position: "absolute", inset: 0 }}>
            <rect x={0} y={560} width={1188} height={210} fill="#1b2340" />
            <ellipse cx={594} cy={310} rx={96} ry={110} fill="#e0a67a" stroke={INK} strokeWidth={7} />
            <path d="M280,768 Q300,470 594,450 Q890,470 910,768 Z" fill={ACCENT[accent] || "#3a6fb0"} stroke={INK} strokeWidth={7} />
            <path d="M498,250 Q594,170 690,250 Q650,210 594,210 Q540,210 498,250 Z" fill="#3a2b22" stroke={INK} strokeWidth={5} />
          </svg>
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 98, height: 112, background: "#f3f3f0", borderTop: `6px solid ${INK}`, display: "flex", alignItems: "center", fontFamily: FONT.ui }}>
            <div style={{ background: ALERT_RED, color: "#fff", fontWeight: 900, fontSize: 40, padding: "0 28px", height: "100%", display: "flex", alignItems: "center", letterSpacing: 2 }}>BREAKING</div>
            <div style={{ padding: "0 30px", fontSize: 50, fontWeight: 800, color: INK }}>{headline}</div>
          </div>
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 98, background: INK, color: "#fff", fontFamily: FONT.ui, fontSize: 38, lineHeight: "98px", whiteSpace: "nowrap", overflow: "hidden" }}>
            <div style={{ transform: `translateX(${1188 - ((frame * 7) % 2600)}px)` }}>{lower}   +++   {ticker}   +++   {lower}</div>
          </div>
          <div style={{ position: "absolute", inset: 0, backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.12) 0 2px, transparent 2px 5px)", pointerEvents: "none" }} />
        </div>
      </div>
    </OverlayFrame>
  );
};

/* ---------------- Timer ---------------- */
const parseHMS = (s: string) => {
  const p = s.split(":").map((x) => parseInt(x, 10) || 0);
  return p.length === 3 ? p[0] * 3600 + p[1] * 60 + p[2] : p.length === 2 ? p[0] * 60 + p[1] : p[0];
};
export const TimerOv: React.FC<OvProps> = ({ args, frame, total, fps }) => {
  const start = parseHMS(String(args[0]));
  const left = Math.max(0, start - Math.floor(frame / fps));
  const hh = String(Math.floor(left / 3600)).padStart(2, "0"), mm = String(Math.floor((left % 3600) / 60)).padStart(2, "0"), ss = String(left % 60).padStart(2, "0");
  return (
    <OverlayFrame frame={frame} total={total} rot={-1}>
      <div style={{ padding: "34px 54px 26px", background: "#101114", border: `8px solid ${INK}`, borderRadius: 26, boxShadow: "0 0 70px rgba(255,40,50,0.35)", textAlign: "center" }}>
        <div style={{ fontFamily: FONT.ui, fontWeight: 800, fontSize: 150, letterSpacing: 6, color: "#ff3b45", fontVariantNumeric: "tabular-nums", textShadow: "0 0 24px #ff3b45" }}>{hh}:{mm}:{ss}</div>
        {args[1] ? <div style={{ fontFamily: FONT.marker, fontSize: 50, color: "#ffd9d9", marginTop: 4, letterSpacing: 3 }}>{String(args[1])}</div> : null}
      </div>
    </OverlayFrame>
  );
};

/* ---------------- NumberedCircle ---------------- */
export const NumberedCircle: React.FC<OvProps> = ({ args, frame, total, accent }) => (
  <OverlayFrame frame={frame} total={total} rot={-4}>
    <div style={{ textAlign: "center" }}>
      <div style={{ width: 400, height: 400, margin: "0 auto", borderRadius: 200, background: ACCENT[accent] || ACCENT.amber, border: `10px solid ${INK}`, boxShadow: "14px 16px 0 rgba(0,0,0,0.25)", fontFamily: FONT.display, fontSize: 260, lineHeight: "380px", color: INK }}>{String(args[0])}</div>
      {args[1] ? <div style={{ display: "inline-block", marginTop: 28, background: PAPER, border: `6px solid ${INK}`, padding: "10px 34px", fontFamily: FONT.marker, fontSize: 56, color: INK, transform: "rotate(2deg)", opacity: prog(frame, 8, 10) }}>{String(args[1])}</div> : null}
    </div>
  </OverlayFrame>
);

/* ---------------- ArrowCallout ---------------- */
export const ArrowCallout: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const dir = String(args[1] ?? "right");
  const dp = easeOut(prog(frame, 8, 14));
  const rot = dir === "left" ? 180 : dir === "up" ? -90 : dir === "down" ? 90 : 0;
  return (
    <OverlayFrame frame={frame} total={total} rot={-2} x={dir === "right" ? 700 : dir === "left" ? 1220 : 960} y={dir === "up" ? 700 : dir === "down" ? 380 : 360}>
      <div style={{ display: "flex", alignItems: "center", gap: 20, flexDirection: dir === "left" ? "row-reverse" : "row" }}>
        <div style={{ background: PAPER, border: `7px solid ${INK}`, padding: "18px 38px", fontFamily: FONT.note, fontWeight: 700, fontSize: 84, color: INK, maxWidth: 900, boxShadow: "10px 12px 0 rgba(0,0,0,0.22)", transform: "rotate(-1.5deg)" }}><Reveal p={prog(frame, 4, 14)}>{String(args[0])}</Reveal></div>
        <svg width={260} height={160} viewBox="0 0 260 160" style={{ transform: `rotate(${rot}deg)` }}>
          <path d="M10,110 C70,10 150,10 230,76" fill="none" stroke={ACCENT[accent] || ACCENT.crimson} strokeWidth={14} strokeLinecap="round" strokeDasharray={420} strokeDashoffset={420 * (1 - dp)} />
          <path d="M190,36 L236,78 L178,100" fill="none" stroke={ACCENT[accent] || ACCENT.crimson} strokeWidth={14} strokeLinecap="round" strokeLinejoin="round" opacity={dp > 0.9 ? 1 : 0} />
        </svg>
      </div>
    </OverlayFrame>
  );
};

/* ---------------- DashedPath ---------------- */
export const DashedPath: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const a = String(args[0]), b = String(args[1]);
  const dp = easeInOut(prog(frame, 10, Math.max(20, total - 24)));
  const L = 1100;
  return (
    <OverlayFrame frame={frame} total={total} rot={1.5}>
      <Paper w={1420} h={640} color="#f4ecd6">
        <svg width={1420} height={640} style={{ position: "absolute", inset: 0 }}>
          {Array.from({ length: 9 }).map((_, i) => <path key={i} d={`M0,${70 + i * 70} H1420`} stroke="#b9ae92" strokeWidth={2} opacity={0.5} />)}
          {Array.from({ length: 12 }).map((_, i) => <path key={i} d={`M${70 + i * 118},0 V640`} stroke="#b9ae92" strokeWidth={2} opacity={0.5} />)}
          <path d="M250,480 C420,120 760,560 1120,200" fill="none" stroke={ACCENT[accent] || ACCENT.crimson} strokeWidth={13} strokeLinecap="round" strokeDasharray="30 22" pathLength={L} strokeDashoffset={L * (1 - dp)} opacity={0.95} />
          {[[250, 480, a], [1120, 200, b]].map(([x, y, t], i) => (
            <g key={i} transform={`translate(${x},${y})`}>
              <circle r={30} fill={i ? "#d9322e" : "#2b8a5a"} stroke={INK} strokeWidth={7} />
              <circle r={10} fill="#fff" />
              <text y={-52} textAnchor="middle" fontFamily={FONT.marker} fontSize={52} fill={INK}>{String(t)}</text>
            </g>
          ))}
        </svg>
      </Paper>
    </OverlayFrame>
  );
};

/* ---------------- GlitchText ---------------- */
export const GlitchText: React.FC<OvProps> = ({ args, frame, total }) => {
  const t = String(args[0]);
  const j = (rand(Math.floor(frame / 2) * 1.37) - 0.5) * 18;
  const style: React.CSSProperties = { position: "absolute", left: 0, right: 0, textAlign: "center", fontFamily: FONT.display, fontSize: 260, letterSpacing: 8, whiteSpace: "nowrap" };
  return (
    <OverlayFrame frame={frame} total={total}>
      <div style={{ position: "relative", width: 1300, height: 340, background: "#0a0b10", border: `8px solid ${INK}`, overflow: "hidden" }}>
        <div style={{ ...style, color: "#ff2d55", transform: `translateX(${j}px)`, mixBlendMode: "screen" }}>{t}</div>
        <div style={{ ...style, color: "#2de2ff", transform: `translateX(${-j}px)`, mixBlendMode: "screen" }}>{t}</div>
        <div style={{ ...style, color: "#f4f4f4", opacity: 0.9 }}>{t}</div>
        <div style={{ position: "absolute", inset: 0, backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0 3px, transparent 3px 7px)" }} />
        {rand(Math.floor(frame / 4)) > 0.7 ? <div style={{ position: "absolute", left: 0, right: 0, top: rand(frame) * 300, height: 30, background: "rgba(255,255,255,0.18)" }} /> : null}
      </div>
    </OverlayFrame>
  );
};

/* ---------------- PaperBarChart ---------------- */
export const PaperBarChart: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const title = String(args[0]);
  const bars = args.slice(1).map((s) => { const [k, v] = String(s).split("="); return { k, v: parseFloat(v) || 0 }; });
  const max = Math.max(...bars.map((b) => b.v), 1);
  const bw = clamp(820 / bars.length - 40, 120, 260);
  return (
    <OverlayFrame frame={frame} total={total} rot={1.4}>
      <Paper w={1280} h={760} color="#f8f1de">
        <div style={{ position: "absolute", left: 44, top: 28, fontFamily: FONT.marker, fontSize: 56, color: INK }}>{title}</div>
        <svg width={1280} height={760} style={{ position: "absolute", inset: 0 }}>
          <path d="M120,170 V640 H1190" fill="none" stroke={INK} strokeWidth={7} strokeLinecap="round" />
          {bars.map((b, i) => {
            const h = (b.v / max) * 400 * easeOut(prog(frame, 10 + i * 10, 18));
            const x = 220 + i * ((1000) / bars.length);
            return (
              <g key={i}>
                <rect x={x} y={640 - h} width={bw} height={h} fill={[ACCENT[accent] || ACCENT.amber, "#4f9fd6", "#79b86a", "#d9534f"][i % 4]} stroke={INK} strokeWidth={6} />
                <text x={x + bw / 2} y={632 - h} textAnchor="middle" fontFamily={FONT.display} fontSize={76} fill={INK}>{b.v} h</text>
                <text x={x + bw / 2} y={700} textAnchor="middle" fontFamily={FONT.hand} fontSize={44} fill={INK}>{b.k}</text>
              </g>
            );
          })}
        </svg>
      </Paper>
    </OverlayFrame>
  );
};

/* ---------------- HandWithPen ---------------- */
export const HandWithPen: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const text = String(args[0]);
  const p = easeInOut(prog(frame, 8, Math.max(24, total - 30)));
  const w = clamp(text.length * 78 + 160, 600, 1500);
  return (
    <OverlayFrame frame={frame} total={total} rot={-2}>
      <Paper w={w} h={300} color="#fbf6ea">
        <div style={{ position: "absolute", left: 60, top: 0, bottom: 0, display: "flex", alignItems: "center", fontFamily: FONT.note, fontWeight: 700, fontSize: 170, color: ACCENT[accent] ? "#1b2a5a" : INK }}>
          <Reveal p={p}>{text}</Reveal>
        </div>
        <svg width={w} height={300} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
          <g transform={`translate(${60 + p * (w - 160)},${190 + Math.sin(frame * 0.8) * 8}) rotate(-24)`}>
            <rect x={-6} y={-150} width={14} height={140} rx={5} fill="#2a5db0" stroke={INK} strokeWidth={4} />
            <path d="M-6,-10 L1,16 L8,-10 Z" fill="#222" />
            <rect x={-44} y={-250} width={92} height={110} rx={32} fill={GLOVE} stroke={INK} strokeWidth={6} />
            <rect x={-30} y={-210} width={62} height={190} rx={26} fill={GLOVE} stroke={INK} strokeWidth={6} opacity={0} />
          </g>
        </svg>
      </Paper>
    </OverlayFrame>
  );
};

/* ---------------- EndScreen ---------------- */
export const EndScreen: React.FC<OvProps> = ({ args, frame, total, accent }) => {
  const a = clamp(frame / 14, 0, 1);
  return (
    <AbsoluteFill style={{ background: `rgba(10,8,16,${0.72 * a})` }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 120, textAlign: "center", fontFamily: FONT.marker, fontSize: 92, color: "#fff", textShadow: `0 6px 0 ${INK}`, opacity: a, transform: `translateY(${(1 - easeOut(a)) * 30}px)` }}>{String(args[0])}</div>
      {[[220, 330], [1100, 330]].map(([x, y], i) => (
        <div key={i} style={{ position: "absolute", left: x, top: y, width: 600, height: 338, border: `6px dashed ${ACCENT[accent] || ACCENT.amber}`, borderRadius: 18, opacity: prog(frame, 10 + i * 6, 12), background: "rgba(255,255,255,0.05)" }} />
      ))}
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 150, textAlign: "center", opacity: prog(frame, 24, 12) }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 24, background: "#e0262f", border: `7px solid ${INK}`, borderRadius: 60, padding: "16px 54px", fontFamily: FONT.display, fontSize: 84, color: "#fff", boxShadow: "8px 10px 0 rgba(0,0,0,0.3)" }}>
          <span style={{ borderLeft: "40px solid #fff", borderTop: "26px solid transparent", borderBottom: "26px solid transparent" }} /> SUBSCRIBE
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- SubscribeSticker (cta) ---------------- */
export const SubscribeSticker: React.FC<{ frame: number; total: number }> = ({ frame, total }) => {
  const inP = easeOut(prog(frame, 0, 12)), outP = prog(frame, total - 10, 10);
  const wob = Math.sin(frame * 0.5) * 6;
  return (
    <div style={{ position: "absolute", left: 90, bottom: 110, transform: `scale(${(0.6 + 0.4 * inP) * (1 - 0.3 * outP)}) rotate(${-4 + wob * 0.2}deg)`, opacity: inP * (1 - outP), transformOrigin: "left bottom" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 22, background: "#e0262f", border: `7px solid ${INK}`, borderRadius: 60, padding: "14px 44px 14px 30px", boxShadow: "8px 10px 0 rgba(0,0,0,0.32)", fontFamily: FONT.display, fontSize: 74, color: "#fff", letterSpacing: 2 }}>
        <span style={{ width: 70, height: 70, borderRadius: 35, background: "#fff", display: "inline-block", position: "relative" }}><span style={{ position: "absolute", left: 27, top: 18, borderLeft: "28px solid #e0262f", borderTop: "17px solid transparent", borderBottom: "17px solid transparent" }} /></span>
        SUBSCRIBE
        <svg width={64} height={64} viewBox="0 0 64 64" style={{ transform: `rotate(${wob * 2}deg)` }}><path d="M32,6 C20,6 14,16 14,28 V40 L8,50 H56 L50,40 V28 C50,16 44,6 32,6 Z" fill="#ffd23f" stroke="#1c1a1f" strokeWidth={4} strokeLinejoin="round" /><circle cx={32} cy={56} r={6} fill="#ffd23f" stroke="#1c1a1f" strokeWidth={4} /></svg>
      </div>
    </div>
  );
};

/* ---------------- Time card + flash-forward banner (used by the shot view) ---------------- */
export const TimeCard: React.FC<{ text: string; frame: number; total: number; design: string; accent: string }> = ({ text, frame, total, design, accent }) => {
  const inP = easeOut(prog(frame, 0, 10)), outP = easeInOut(prog(frame, total - 10, 10));
  const slide = (1 - inP) * -700 + outP * -700;
  const acc = ACCENT[accent] || ACCENT.amber;
  if (design === "stamped_box" || design === "ticket") {
    return (
      <div style={{ position: "absolute", left: 110, top: 96, transform: `translateX(${slide}px) rotate(-3deg)`, border: `10px solid ${acc}`, color: acc, background: "rgba(10,10,14,0.78)", padding: "10px 40px", fontFamily: FONT.display, fontSize: 120, letterSpacing: 5, boxShadow: `8px 10px 0 rgba(0,0,0,0.35)` }}>{text}</div>
    );
  }
  if (design === "marker_scrawl" || design === "paper_tab") {
    return (
      <div style={{ position: "absolute", left: 100, top: 96, transform: `translateX(${slide}px) rotate(-2deg)`, background: PAPER, border: `7px solid ${INK}`, padding: "6px 40px", fontFamily: FONT.marker, fontSize: 104, color: INK, boxShadow: "10px 12px 0 rgba(0,0,0,0.28)" }}>{text}</div>
    );
  }
  return (
    <div style={{ position: "absolute", left: 0, top: 96, transform: `translateX(${slide}px)`, display: "flex", alignItems: "stretch", boxShadow: "0 12px 0 rgba(0,0,0,0.3)" }}>
      <div style={{ background: acc, width: 40, borderTop: `6px solid ${INK}`, borderBottom: `6px solid ${INK}` }} />
      <div style={{ background: "#0e0f14", color: "#fff", fontFamily: FONT.display, fontSize: 118, letterSpacing: 6, padding: "6px 60px 6px 40px", borderTop: `6px solid ${INK}`, borderBottom: `6px solid ${INK}` }}>
        <svg width={92} height={92} viewBox="0 0 92 92" style={{ marginRight: 26, verticalAlign: "-8px" }}><circle cx={46} cy={46} r={38} fill="none" stroke={acc} strokeWidth={9} /><path d="M46,22 V46 L64,58" fill="none" stroke={acc} strokeWidth={9} strokeLinecap="round" /></svg>{text}
      </div>
    </div>
  );
};

export const FlashForwardBanner: React.FC<{ text: string; frame: number; total: number }> = ({ text, frame, total }) => {
  const inP = easeOut(prog(frame, 0, 10)), outP = easeInOut(prog(frame, total - 10, 10));
  return (
    <div style={{ position: "absolute", left: -40, right: -40, top: 130, transform: `translateX(${(1 - inP) * 1400 + outP * 1400}px) rotate(-2.2deg)`, background: "repeating-linear-gradient(45deg, #f2b632 0 36px, #1b1a1f 36px 72px)", padding: 10, boxShadow: "0 14px 0 rgba(0,0,0,0.3)" }}>
      <div style={{ background: "#c6232c", border: `6px solid ${INK}`, padding: "10px 60px", display: "flex", alignItems: "baseline", gap: 40, color: "#fff" }}>
        <span style={{ fontFamily: FONT.ui, fontWeight: 900, fontSize: 44, letterSpacing: 8, opacity: 0.9 }}>{/EARLIER|AGO|BEFORE/i.test(text) ? "FLASHBACK" : "FLASH FORWARD"}</span>
        <span style={{ fontFamily: FONT.display, fontSize: 130, letterSpacing: 6 }}>{text}</span>
      </div>
    </div>
  );
};


// ---- survival meter insert (battery, water, cash, hours) ----
export const Meter: React.FC<OvProps> = ({ args, frame, total }) => {
  const kind = String(args[0]);
  const val = String(args[1]);
  const label = String(args[2] || kind).toUpperCase();
  const num = parseFloat(val.replace(/[^0-9.]/g, "")) || 0;
  const p = easeOut(prog(frame, 4, 22));
  const level = kind === "battery" ? clamp(num / 100, 0, 1) : kind === "water" ? clamp(num / 10, 0, 1) : kind === "cash" ? clamp(num / 100, 0, 1) : clamp(num / 12, 0, 1);
  const low = level < 0.2;
  const col = low ? "#ff5a5a" : "#7be08a";
  const lv = level * p;
  const icon =
    kind === "battery" ? (
      <g>
        <rect x={-170} y={-80} width={320} height={160} rx={22} fill="#1c1a1f" stroke="#f2e8d2" strokeWidth={12} />
        <rect x={150} y={-34} width={26} height={68} rx={8} fill="#f2e8d2" />
        <rect x={-150} y={-60} width={Math.max(8, 280 * lv)} height={120} rx={10} fill={col} />
      </g>
    ) : kind === "water" ? (
      <g>
        <path d="M-90,-110 L90,-110 L110,-70 L110,100 Q110,120 90,120 L-90,120 Q-110,120 -110,100 L-110,-70 Z" fill="#14233a" stroke="#f2e8d2" strokeWidth={12} strokeLinejoin="round" />
        <rect x={-96} y={110 - 200 * lv} width={192} height={Math.max(6, 200 * lv)} fill="#5fb4ff" />
        <rect x={-40} y={-140} width={80} height={32} rx={8} fill="#f2e8d2" />
      </g>
    ) : kind === "cash" ? (
      <g>
        {[0, 1, 2].map((i) => <rect key={i} x={-150 + i * 14} y={-70 + i * 22} width={270} height={130} rx={12} fill={i === 2 ? "#6fcf7f" : "#4f9f61"} stroke="#1c1a1f" strokeWidth={8} />)}
        <text x={-12} y={72} textAnchor="middle" fontFamily="Anton, Impact, sans-serif" fontSize={110} fill="#1c1a1f">$</text>
      </g>
    ) : (
      <g>
        <circle r={125} fill="#14233a" stroke="#f2e8d2" strokeWidth={12} />
        {Array.from({ length: 12 }).map((_, i) => <line key={i} x1={Math.cos(i * 0.5236) * 100} y1={Math.sin(i * 0.5236) * 100} x2={Math.cos(i * 0.5236) * 116} y2={Math.sin(i * 0.5236) * 116} stroke="#f2e8d2" strokeWidth={6} />)}
        <line x1={0} y1={0} x2={Math.sin(lv * Math.PI * 2) * 90} y2={-Math.cos(lv * Math.PI * 2) * 90} stroke={col} strokeWidth={14} strokeLinecap="round" />
      </g>
    );
  return (
    <OverlayFrame frame={frame} total={total} rot={0}>
      <div style={{ width: 760, textAlign: "center" }}>
        <div style={{ fontFamily: FONT.marker, fontSize: 64, color: "#f2e8d2", letterSpacing: 4, textShadow: "0 4px 0 #1c1a1f" }}>{label}</div>
        <svg width={420} height={300} viewBox="-210 -150 420 300" style={{ margin: "6px auto 0", display: "block" }}>{icon}</svg>
        <div style={{ fontFamily: FONT.display, fontSize: 190, lineHeight: 1, color: col, WebkitTextStroke: "10px #1c1a1f", paintOrder: "stroke fill" }}>{val}</div>
      </div>
    </OverlayFrame>
  );
};

export const OVERLAYS: Record<string, React.FC<any>> = {
  meter: Meter,
  notepad_tracker: NotepadTracker,
  calendar_countdown: CalendarCountdown,
  sticky_note: StickyNote,
  label_tag: LabelTag,
  receipt: Receipt,
  paper_diagram: PaperDiagram,
  phone_alert: (p: OvProps) => <PhoneScreen {...p} mode="alert" />,
  phone_web: (p: OvProps) => <PhoneScreen {...p} mode="web" />,
  phone_video: (p: OvProps) => <PhoneScreen {...p} mode="video" />,
  phone_call: (p: OvProps) => <PhoneScreen {...p} mode="call" />,
  phone_search: (p: OvProps) => <PhoneScreen {...p} mode="search" />,
  tv_news: TVNews,
  timer: TimerOv,
  numbered_circle: NumberedCircle,
  arrow_callout: ArrowCallout,
  dashed_path: DashedPath,
  glitch_text: GlitchText,
  paper_bar_chart: PaperBarChart,
  hand_pen: HandWithPen,
  end_screen: EndScreen,
};
