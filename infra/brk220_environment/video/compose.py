"""Compose the Demo 1 video: cut the screen recording into narrated segments, speed up the wait, add voiceover.

Inputs (this folder): rec.webm, marks.json (seconds from recording start), vo_<id>.mp3, vo_durations.json.
Output: BRK220_Demo1_Contoso_renewal_brief.mp4
"""
import json
import subprocess
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
marks = json.load(open("marks.json"))
vo = json.load(open("vo_durations.json"))
LEAD = 0.35  # silence before each clip

# segment id -> [start, end] seconds in the recording
plan = [(k, *v) for k, v in marks.items()]

parts, inputs = [], ["-i", "rec.webm"]
for i, (sid, start, end) in enumerate(plan, start=1):
    inputs += ["-i", f"vo_{sid}.mp3"]
    clip = max(end - start, 0.5)
    need = vo[sid] + LEAD + 0.5
    speed = clip / need if clip > need * 1.15 else 1.0  # only speed up long waits
    dur = max(clip / speed, need)
    parts.append(
        f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=(PTS-STARTPTS)/{speed:.4f},"
        f"tpad=stop_mode=clone:stop_duration={dur:.3f},trim=duration={dur:.3f},fps=30,format=yuv420p[v{i}];"
        f"[{i}:a]adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad,atrim=duration={dur:.3f},"
        f"aresample=48000,aformat=channel_layouts=stereo[a{i}];"
    )
    print(f"{sid:10s} clip {clip:6.1f}s  speed x{speed:4.1f}  -> {dur:5.1f}s")

n = len(plan)
concat = "".join(f"[v{i}][a{i}]" for i in range(1, n + 1)) + f"concat=n={n}:v=1:a=1[v][a]"
cmd = [FF, "-y", *inputs, "-filter_complex", "".join(parts) + concat, "-map", "[v]", "-map", "[a]",
       "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
       "BRK220_Demo1_Contoso_renewal_brief.mp4"]
subprocess.run(cmd, check=True, capture_output=True)
print("wrote BRK220_Demo1_Contoso_renewal_brief.mp4")
