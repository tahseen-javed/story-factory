import { Shot, Timeline, CharSpec } from "./types";

const HERO = { outfit: "teal", hat: "cap", hair: "short", headScale: 1.5, eyeScale: 1.25 };
const MARA = { outfit: "plum", hat: "none", hair: "bun", age: "old" };
const hero = (pose: string, expr: string, x = 0.5, facing: 1 | -1 = 1, prop?: string): CharSpec & { prop?: string } => ({ id: "hero", rig: "rig_hero", params: HERO, pose, expr, x, facing, ...(prop ? { prop } : {}) });
const mara = (pose: string, expr: string, x = 0.7, facing: 1 | -1 = -1, prop?: string): CharSpec & { prop?: string } => ({ id: "mara", rig: "rig_hero", params: MARA, pose, expr, x, facing, ...(prop ? { prop } : {}) });

type Def = Partial<Shot> & { loc: string; variant: string; camera: [string, number, number] };

const DEFS: Def[] = [
  { loc: "insert", variant: "night", camera: ["push", 1.0, 1.1], chars: [], overlay: { name: "meter", args: ["battery", "12%", "PHONE"], inFrame: 6, outFrame: 54 }, fx: ["dust"] },
  { loc: "insert", variant: "dusk", camera: ["push", 1.0, 1.1], chars: [], overlay: { name: "meter", args: ["cash", "$23", "CASH"], inFrame: 6, outFrame: 54 }, fx: ["dust"] },
  { loc: "street", variant: "dusk", camera: ["push", 1.0, 1.1], chars: [hero("look_up", "shocked", 0.3), mara("back_away", "scared", 0.7)], overlay: null, fx: ["rain"] },
  { loc: "apartment", variant: "night", camera: ["push", 1.0, 1.16], chars: [hero("sit_bed", "scared", 0.3)], overlay: { name: "phone_alert", args: ["EMERGENCY ALERT", "Severe space weather. Impact in 15 hours"], inFrame: 8, outFrame: 56 }, fx: ["flicker"], timeCard: { text: "FRIDAY 3:12 AM", frames: 56 } },
  { loc: "apartment", variant: "night", camera: ["push", 1.04, 1.18], chars: [hero("phone_hold", "shocked", 0.35)], overlay: { name: "timer", args: ["15:00:00", "UNTIL IMPACT"], inFrame: 4, outFrame: 56 } },
  { loc: "street", variant: "night", camera: ["pan_r", 1.12, 1.12], chars: [], overlay: { name: "paper_diagram", args: ["SOLAR STORM PATH", "Sun", "Storm cloud", "Earth", "Power grid"], inFrame: 4, outFrame: 58 }, fx: ["dust"] },
  { loc: "rooftop", variant: "blackout", camera: ["pull", 1.22, 1.06], chars: [hero("stand", "sad", 0.4)], banner: "SATURDAY 6:00 AM", overlay: null },
  { loc: "hallway", variant: "day", camera: ["push", 1.04, 1.16], chars: [hero("stand", "worried", 0.32, 1), mara("carry", "neutral", 0.7, -1, "radio")], overlay: { name: "sticky_note", args: ["3B", "Check on Mara"], inFrame: 4, outFrame: 56 } },
  { loc: "kitchen", variant: "day", camera: ["pull", 1.16, 1.05], chars: [hero("stand", "neutral", 0.3), mara("point", "determined", 0.72)], overlay: { name: "paper_bar_chart", args: ["HOW LONG FOOD STAYS COLD", "Fridge=4", "Full freezer=48"], inFrame: 4, outFrame: 58 } },
  { loc: "kitchen", variant: "day", camera: ["parallax_drift", 1.05, 1.12], chars: [hero("write", "determined", 0.4)], overlay: { name: "notepad_tracker", args: ["SURVIVAL LOG"], inFrame: 4, outFrame: 58 }, track: { hours: 3, water: "8 L", phone: "100%", cash: "$16" }, prevTrack: { hours: 9, water: "6 L", phone: "38%", cash: "$40" } },
  { loc: "gas_station", variant: "day", camera: ["push", 1.03, 1.14], chars: [hero("run", "determined", 0.5)], overlay: { name: "receipt", args: ["CORNER GAS", "Fuel   $20.00", "Water x2   $4.00", "TOTAL   $24.00"], inFrame: 4, outFrame: 58 } },
  { loc: "stairwell", variant: "blackout", camera: ["shake_medium", 1.12, 1.12], chars: [hero("stand", "scared", 0.3), mara("stand", "scared", 0.7)], overlay: { name: "glitch_text", args: ["SIGNAL LOST"], inFrame: 6, outFrame: 54 }, fx: ["flicker", "glitch"] },
  { loc: "hallway", variant: "alarm", camera: ["push", 1.05, 1.2], chars: [hero("hide", "scared", 0.5)], overlay: { name: "numbered_circle", args: [4, "G5 STORMS PER CYCLE"], inFrame: 4, outFrame: 56 }, fx: ["alarm_pulse"] },
  { loc: "apartment", variant: "dusk", camera: ["push", 1.06, 1.2], chars: [hero("phone_hold", "worried", 0.3)], overlay: { name: "phone_search", args: ["solar storm tonight", "One headline loads", "Page not responding"], inFrame: 4, outFrame: 56 } },
  { loc: "street", variant: "day", camera: ["pan_l", 1.12, 1.12], chars: [hero("walk", "worried", 0.5)], overlay: { name: "dashed_path", args: ["Home", "Gas station"], inFrame: 4, outFrame: 58 } },
  { loc: "kitchen", variant: "blackout", camera: ["push", 1.05, 1.18], chars: [hero("sit", "sad", 0.3), mara("sit", "sad", 0.7)], overlay: { name: "tv_news", args: ["GRID FAILURE", "Power out across the region", "Stay indoors"], inFrame: 4, outFrame: 56 } },
  { loc: "apartment", variant: "night", camera: ["push", 1.04, 1.16], chars: [hero("point", "determined", 0.35)], overlay: { name: "calendar_countdown", args: [6, 14, "COUNTDOWN"], inFrame: 4, outFrame: 58 } },
  { loc: "rooftop", variant: "dusk", camera: ["push", 1.05, 1.22], chars: [hero("stand", "shocked", 0.3), mara("stand", "sly", 0.7)], overlay: { name: "hand_pen", args: ["Someone had to wake up"], inFrame: 4, outFrame: 58 }, cta: true },
  { loc: "rooftop", variant: "dusk", camera: ["hold", 1.0, 1.0], chars: [hero("stand", "relieved", 0.3), mara("stand", "relieved", 0.7)], overlay: { name: "end_screen", args: ["Next story: the dam nobody was watching"], inFrame: 0, outFrame: 60 } },
];

export function testTimeline(): Timeline {
  const dur = 60;
  const shots: Shot[] = DEFS.map((d, i) => ({
    i,
    chapter: 1,
    start: i * dur,
    dur,
    location: d.loc,
    variant: d.variant,
    bg: null,
    layers: null,
    floorY: 0.9,
    chars: (d.chars as any) || [],
    overlay: (d.overlay as any) || null,
    camera: { preset: d.camera[0], z0: d.camera[1], z1: d.camera[2], fx: 0.5, fy: 0.55 },
    fx: d.fx || [],
    banner: (d.banner as any) || null,
    cta: !!d.cta,
    timeCard: (d.timeCard as any) || null,
    track: (d.track as any) || { hours: 15, water: "6 L" },
    prevTrack: (d.prevTrack as any) || {},
    text: "",
    framing: ["medium", "closeup", "wide", "ots", "low", "insert", "back", "silhouette", "profile", "xwide"][i % 10],
    trans: ["cut", "whip", "flash", "glitch", "punch", "smash"][i % 6],
    grade: ["warm", "cold", "alarm", "grey", "gold"][i % 5],
    crowd: i % 5 === 0,
  }));
  shots.forEach((sh) => sh.chars.forEach((c: any, k: number) => { c.speaks = k === 0; c.view = sh.framing === "back" || (sh.framing === "ots" && k === 0) ? "back" : k % 2 ? "front" : "three_quarter"; c.silhouette = sh.framing === "silhouette"; }));
  return {
    fps: 30,
    width: 1920,
    height: 1080,
    durationInFrames: dur * DEFS.length,
    style: { accent: "amber", lut: "cold_night", titlecard: "clock_strip", transition: "hard_cuts" },
    shots,
    endScreenFrames: 60,
    fadeOut: 20,
    voiceEnv: Array.from({ length: dur * DEFS.length }, (_, f) => Math.max(0, Math.sin(f * 0.55) * 0.5 + 0.55) * (Math.floor(f / 40) % 3 === 2 ? 0 : 1)),
    captions: [
      { s: 10, e: 100, lines: [[["Friday,", 10, 30], ["six", 30, 45], ["thirty-three", 45, 70]], [["p.m.", 70, 85], ["Your", 85, 100]]] },
      { s: 100, e: 200, lines: [[["Not", 100, 120], ["one", 120, 140], ["window", 140, 170], ["is", 170, 180], ["lit.", 180, 200]]] },
    ],
  };
}
