"""Build a narrated demo video from a Playwright screen recording.

Usage: python make_video.py <narration.json>

narration.json: {"voice", "rec" (recording file), "out" (output .mp4), "segments": [{"id", "range": [start, end] seconds
in the recording, "text", optional "caption" (banner text) and "boxes" ([[x, y, w, h], ...] highlight
rectangles in recording pixels)}]}. Generates one voiceover clip per segment with edge-tts (Microsoft neural voices), then cuts
the recording into the segments, speeds up any segment much longer than its narration (for example the wait while
Copilot works), holds the last frame if the narration is longer, and joins them with the voiceover.
Needs edge-tts and imageio-ffmpeg.
"""
import asyncio
import json
import re
import subprocess
import sys

import edge_tts
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
FONT = "C\\:/Windows/Fonts/segoeuib.ttf"
LEAD = 0.35  # silence before each clip


def duration(path: str) -> float:
    err = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


async def voice(cfg: dict) -> dict:
    out = {}
    for seg in cfg["segments"]:
        path = f"vo_{cfg['out'][:-4]}_{seg['id']}.mp3"
        for attempt in range(4):
            try:
                await edge_tts.Communicate(seg["text"], cfg["voice"], rate=cfg.get("rate", "+4%")).save(path)
                break
            except edge_tts.exceptions.NoAudioReceived:
                if attempt == 3:
                    raise
                await asyncio.sleep(3)
        out[seg["id"]] = (path, duration(path))
    return out


def overlay(seg: dict) -> str:
    """ffmpeg filters for a segment's highlight boxes and caption banner (empty when it has neither)."""
    out = "".join(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=0xE8A400@0.95:t=4," for x, y, w, h in seg.get("boxes", []))
    if seg.get("caption"):
        text = seg["caption"].replace("\\", "").replace(":", "\\:").replace("'", "")
        out += (f"drawtext=fontfile='{FONT}':text='{text}':fontsize=26:fontcolor=white:box=1:boxcolor=0x0B6A0B@0.92:"
                "boxborderw=14:x=(w-text_w)/2:y=24,")
    return out


def main(path: str) -> None:
    cfg = json.load(open(path, encoding="utf-8"))
    vo = asyncio.run(voice(cfg))
    parts, inputs = [], ["-i", cfg["rec"]]
    for i, seg in enumerate(cfg["segments"], start=1):
        audio, vo_len = vo[seg["id"]]
        inputs += ["-i", audio]
        start, end = seg["range"]
        clip = max(end - start, 0.5)
        need = vo_len + LEAD + 0.5
        speed = clip / need if clip > need * 1.15 else 1.0
        dur = max(clip / speed, need)
        parts.append(
            f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=(PTS-STARTPTS)/{speed:.4f},{overlay(seg)}"
            f"tpad=stop_mode=clone:stop_duration={dur:.3f},trim=duration={dur:.3f},fps=30,format=yuv420p[v{i}];"
            f"[{i}:a]adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad,atrim=duration={dur:.3f},"
            f"aresample=48000,aformat=channel_layouts=stereo[a{i}];")
        print(f"{seg['id']:10s} clip {clip:6.1f}s  speed x{speed:4.1f}  -> {dur:5.1f}s")
    n = len(cfg["segments"])
    graph = "".join(parts) + "".join(f"[v{i}][a{i}]" for i in range(1, n + 1)) + f"concat=n={n}:v=1:a=1[v][a]"
    subprocess.run([FF, "-y", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                    cfg["out"]], check=True, capture_output=True)
    print(f"wrote {cfg['out']} ({duration(cfg['out']):.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
