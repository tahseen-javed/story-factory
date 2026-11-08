// Pose and expression tables for the puppet rig.
// Angles are in degrees measured from "straight down"; +90 points toward the facing direction, +180 straight up.
export type Joint = [number, number]; // [upper segment, lower segment] absolute angles

export type PoseDef = {
  torso: number; // lean (+ = forward)
  head: number; // tilt
  rootY: number; // hips lowered by this many px (sitting, crouching)
  armB: Joint;
  armF: Joint;
  legB: Joint;
  legF: Joint;
  holdF?: string;
  holdB?: string;
  cycle?: { speed: number; arm: number; leg: number; bob: number; bend: number };
  travel?: number; // px the character drifts across the shot while walking/running
};

export const POSES: Record<string, PoseDef> = {
  stand: { torso: 0, head: 0, rootY: 0, armB: [-5, -3], armF: [6, 12], legB: [-3, -3], legF: [3, 3] },
  walk: { torso: 3, head: 0, rootY: 0, armB: [0, 0], armF: [0, 0], legB: [0, 0], legF: [0, 0], cycle: { speed: 1.0, arm: 26, leg: 26, bob: 5, bend: 28 }, travel: 120 },
  run: { torso: 14, head: -4, rootY: 0, armB: [0, 0], armF: [0, 0], legB: [0, 0], legF: [0, 0], cycle: { speed: 1.9, arm: 48, leg: 48, bob: 12, bend: 62 }, travel: 260 },
  sit: { torso: 0, head: 0, rootY: 88, armB: [18, 70], armF: [26, 80], legB: [86, 2], legF: [92, 6] },
  sit_bed: { torso: -3, head: 8, rootY: 88, armB: [16, 66], armF: [24, 76], legB: [84, 4], legF: [90, 8] },
  carry: { torso: 4, head: 0, rootY: 0, armB: [58, 100], armF: [66, 104], legB: [-3, -3], legF: [3, 3], holdF: "crate" },
  push_cart: { torso: 10, head: 0, rootY: 0, armB: [72, 86], armF: [76, 90], legB: [-14, -14], legF: [16, 16], holdF: "cart" },
  phone_hold: { torso: 2, head: 6, rootY: 0, armB: [-6, -2], armF: [92, 158], legB: [-3, -3], legF: [3, 3], holdF: "phone" },
  point: { torso: 4, head: 0, rootY: 0, armB: [-6, -2], armF: [92, 92], legB: [-3, -3], legF: [3, 3] },
  write: { torso: 8, head: 14, rootY: 0, armB: [40, 96], armF: [58, 106], legB: [-3, -3], legF: [3, 3], holdF: "pen", holdB: "notepad" },
  hide: { torso: 20, head: 12, rootY: 104, armB: [150, 120], armF: [160, 128], legB: [96, -6], legF: [102, -2] },
  fight: { torso: 10, head: -2, rootY: 14, armB: [78, 150], armF: [92, 156], legB: [-24, -10], legF: [26, 8] },
  crouch: { torso: 12, head: 4, rootY: 92, armB: [30, 60], armF: [40, 70], legB: [98, -6], legF: [104, -2] },
  hands_up: { torso: -2, head: -4, rootY: 0, armB: [168, 176], armF: [170, 178], legB: [-3, -3], legF: [3, 3] },
  look_up: { torso: -4, head: -22, rootY: 0, armB: [-6, -3], armF: [150, 160], legB: [-3, -3], legF: [3, 3] },
  back_away: { torso: -12, head: 4, rootY: 0, armB: [60, 95], armF: [75, 100], legB: [-20, -10], legF: [18, 10] },
  reach: { torso: 12, head: 4, rootY: 0, armB: [24, 30], armF: [100, 104], legB: [-12, -12], legF: [14, 14] },
  shrug: { torso: 0, head: 5, rootY: 0, armB: [-42, 34], armF: [42, -34], legB: [-3, -3], legF: [3, 3] },
};

export type ExprDef = {
  eye: "open" | "wide" | "narrow" | "half" | "closed" | "happy";
  browInner: number; // + raises the inner end (worried), - lowers it (angry)
  browY: number;
  browR?: number; // right brow extra raise (sly)
  mouth: "line" | "smile" | "frown" | "o" | "open" | "grit" | "smirk" | "small_o";
  pupil: number; // pupil radius
};

export const EXPRS: Record<string, ExprDef> = {
  neutral: { eye: "open", browInner: 0, browY: 0, mouth: "line", pupil: 6 },
  worried: { eye: "open", browInner: 14, browY: -2, mouth: "frown", pupil: 5 },
  scared: { eye: "wide", browInner: 12, browY: -8, mouth: "small_o", pupil: 4 },
  shocked: { eye: "wide", browInner: 3, browY: -12, mouth: "o", pupil: 4 },
  determined: { eye: "narrow", browInner: -13, browY: 3, mouth: "line", pupil: 6 },
  relieved: { eye: "happy", browInner: 5, browY: -2, mouth: "smile", pupil: 6 },
  sad: { eye: "half", browInner: 15, browY: 1, mouth: "frown", pupil: 6 },
  angry: { eye: "narrow", browInner: -18, browY: 4, mouth: "grit", pupil: 5 },
  sleepy: { eye: "half", browInner: 2, browY: 4, mouth: "small_o", pupil: 6 },
  sly: { eye: "narrow", browInner: -6, browY: 0, browR: -10, mouth: "smirk", pupil: 6 },
};
