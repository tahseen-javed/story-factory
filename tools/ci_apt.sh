#!/usr/bin/env bash
# CI helper: apt with hard timeouts that never fails the job when the Ubuntu mirrors are unreachable
# (runner DNS outage on 2026-11-11 hung assemble/thumbs for 45 minutes). ffmpeg/ffprobe fall back to a static build.
# Usage: bash tools/ci_apt.sh pkg [pkg...]
OPT="-o Acquire::Retries=2 -o Acquire::http::Timeout=15 -o Acquire::https::Timeout=15"
need=()
for p in "$@"; do dpkg -s "$p" >/dev/null 2>&1 || need+=("$p"); done
if [ ${#need[@]} -gt 0 ]; then
  timeout 120 sudo apt-get $OPT update -qq 2>&1 | tee /tmp/apt-update.log
  if grep -q "Failed to fetch\|Temporary failure" /tmp/apt-update.log; then
    echo "[ci_apt] mirrors unreachable, skipping apt install of: ${need[*]}"
  else
    timeout 600 sudo apt-get $OPT install -y -qq "${need[@]}" || echo "[ci_apt] apt install failed for: ${need[*]}"
  fi
fi
if ! command -v ffmpeg >/dev/null || ! command -v ffprobe >/dev/null; then
  echo "[ci_apt] static ffmpeg fallback"
  mkdir -p /tmp/ffs && cd /tmp/ffs || exit 0
  if curl -fsSL --retry 3 --connect-timeout 20 -o ff.tar.xz https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz && tar -xJf ff.tar.xz; then
    sudo install -m 755 ffmpeg-master-latest-linux64-gpl/bin/ffmpeg ffmpeg-master-latest-linux64-gpl/bin/ffprobe /usr/local/bin/
  elif curl -fsSL --retry 3 --connect-timeout 20 -o ff2.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && tar -xJf ff2.tar.xz; then
    sudo install -m 755 ffmpeg-*-amd64-static/ffmpeg ffmpeg-*-amd64-static/ffprobe /usr/local/bin/
  fi
  cd - >/dev/null || true
fi
ffmpeg -version | head -1
exit 0
