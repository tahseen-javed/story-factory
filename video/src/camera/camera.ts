import { CamSpec } from "../types";
import { W, H, OVERSCAN, easeInOut, easeOut, clamp, rand } from "../theme";

export type CamState = {
  z: number; // zoom
  tx: number; // px translation of the world (before parallax multipliers)
  ty: number;
  rot: number; // degrees
  blur: number; // px background blur from rack_focus / whip
  fx: number; // focus point (0..1)
  fy: number;
};

// Max sideways travel that never exposes the image edge: the image covers (1+OVERSCAN)*stage and is scaled by z.
export function slack(z: number) {
  const sx = ((1 + OVERSCAN) * z - 1) * W * 0.5;
  const sy = ((1 + OVERSCAN) * z - 1) * H * 0.5;
  return { sx: Math.max(0, sx), sy: Math.max(0, sy) };
}

export function cameraAt(cam: CamSpec, frame: number, dur: number): CamState {
  const t = dur <= 1 ? 1 : clamp(frame / (dur - 1), 0, 1);
  const e = easeInOut(t);
  const z = cam.z0 + (cam.z1 - cam.z0) * e;
  const base: CamState = { z, tx: 0, ty: 0, rot: 0, blur: 0, fx: cam.fx, fy: cam.fy };
  const { sx, sy } = slack(Math.min(cam.z0, cam.z1));
  const px = sx * 0.6;
  const py = sy * 0.5;
  switch (cam.preset) {
    case "pan_l":
      base.tx = px * (1 - 2 * e) * -1; // content moves right as the camera moves left
      base.tx = -px + 2 * px * e;
      break;
    case "pan_r":
      base.tx = px - 2 * px * e;
      break;
    case "tilt_up":
      base.ty = py - 2 * py * e;
      break;
    case "tilt_down":
      base.ty = -py + 2 * py * e;
      break;
    case "parallax_drift":
      base.tx = -px * 0.8 + 1.6 * px * e;
      base.ty = Math.sin(t * Math.PI) * py * 0.25;
      break;
    case "whip_to": {
      const k = easeOut(t);
      base.tx = px * (1 - k);
      base.blur = 10 * Math.sin(Math.min(1, t * 2) * Math.PI) * (1 - t);
      break;
    }
    case "rack_focus":
      base.blur = 9 * (1 - e);
      break;
    case "shake_light":
    case "shake_medium": {
      const a = cam.preset === "shake_light" ? 4 : 9;
      const f = frame * 0.9;
      base.tx = clamp(Math.sin(f * 2.3) * a + (rand(Math.floor(frame / 2)) - 0.5) * a, -px, px);
      base.ty = clamp(Math.cos(f * 2.9) * a * 0.7, -py, py);
      base.rot = Math.sin(f * 1.7) * (cam.preset === "shake_light" ? 0.25 : 0.55);
      break;
    }
    default:
      break; // push, pull, hold: zoom only
  }
  return base;
}

// Parallax multipliers per layer (far moves least, near most). Characters ride with the mid plane.
export const PARALLAX = { far: 0.75, mid: 0.95, near: 1.15, chars: 0.95 };
