# Demo videos

Narrated videos of the demos, built from Playwright screen recordings of Copilot Chat signed in as Megan.

| File | What |
|---|---|
| `make_video.py` | `python make_video.py <narration.json>`: generates one voiceover clip per segment (Microsoft neural TTS through `edge-tts`), cuts the recording into the segments, speeds up long waits, holds the last frame when the narration runs longer, and joins everything into an MP4 |
| `demo2_narration.json` | Demo 2 (close-out): recording file, output name, voice, and each segment's range in the recording and narration text |
| `narration.json`, `marks.json`, `compose.py` | Demo 1 (brief), built with the earlier version of the same approach |

Recordings (`*.webm`), audio and the output MP4s aren't committed. Needs `edge-tts` and `imageio-ffmpeg`.
