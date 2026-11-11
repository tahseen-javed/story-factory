"""Post-encode true-peak safety (P-017 defect prevention). AAC can overshoot the limited master by up to 2 dB
(007 run 43000967103: -0.56 dBTP against the Doctor limit of -1.5). If the mp4 true peak is above the limit, the master is limited
a little harder (only the offending transients are clamped, loudness stays), the audio is re-encoded and the video stream is copied."""
import os
import re
import subprocess
import sys

LIMIT = -1.8   # Doctor limit is -1.5 dBTP, keep 0.3 dB margin
CEIL = -2.6    # dBFS ceiling of the master limiter (factory/mix.py alimiter 0.74)


def parse_peak(text: str):
    m = re.findall(r"True peak:\s+Peak:\s+(-?\d+(?:\.\d+)?) dBFS", text)
    return float(m[-1]) if m else None


def true_peak(path: str):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    return parse_peak(r.stderr)


def main(mp4: str, master: str, br: str = "192k") -> int:
    ceil = CEIL
    for i in range(4):
        tp = true_peak(mp4)
        print(f"[tpfix] pass {i} true peak {tp}", flush=True)
        if tp is None or tp <= LIMIT:
            return 0
        ceil -= (tp - LIMIT) + 0.2
        lim = 10 ** (ceil / 20)
        tmp = mp4 + ".tp.mp4"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", mp4, "-i", master, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-af", f"alimiter=limit={lim:.4f}:level=disabled", "-c:a", "aac", "-b:a", br, "-ar", "48000", "-movflags", "+faststart", "-shortest", tmp], check=True)
        os.replace(tmp, mp4)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
