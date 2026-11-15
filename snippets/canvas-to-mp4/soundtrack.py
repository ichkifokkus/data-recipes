"""Synthesise sound effects with numpy, place them on exact timestamps, and mux the result
into a video at -14 LUFS (two-pass ffmpeg loudnorm). No samples, no licences.

    pip install numpy
    python soundtrack.py demo.mp4 final.mp4
"""
import json
import re
import subprocess
import sys
import wave

import numpy as np

SR = 48_000


def env(n, attack=0.003, decay=0.2):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1)
    return a * np.exp(-t / decay)


def kick(f0=150, f1=45, dur=0.35):
    t = np.arange(int(dur * SR)) / SR
    freq = f1 + (f0 - f1) * np.exp(-t * 30)           # pitch drops fast: the "thump"
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * env(len(t), 0.002, 0.12)


def pluck(freq, dur=0.5):
    t = np.arange(int(dur * SR)) / SR
    tone = sum(np.sin(2 * np.pi * freq * k * t) / k ** 1.5 for k in range(1, 6))
    return tone * env(len(t), 0.002, 0.15)


def whoosh(dur=0.6):
    n = int(dur * SR)
    noise = np.random.default_rng(7).standard_normal(n)
    smooth = np.convolve(noise, np.ones(40) / 40, mode="same")   # crude low-pass
    shape = np.sin(np.pi * np.linspace(0, 1, n)) ** 2             # swell in, swell out
    return smooth * shape


def mix(events, duration):
    out = np.zeros((int(duration * SR), 2))
    for t, sound, gain, pan in events:
        i = int(t * SR)
        s = sound[: len(out) - i] * gain
        out[i:i + len(s), 0] += s * (1 - pan) / 2 * 2 ** 0.5
        out[i:i + len(s), 1] += s * (1 + pan) / 2 * 2 ** 0.5
    return out / max(1e-9, np.abs(out).max()) * 0.9               # peak-normalise before loudnorm


def write_wav(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def loudnorm_mux(video, audio, out, target=-14.0):
    base = f"loudnorm=I={target}:TP=-1.5:LRA=11"
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio, "-af", base + ":print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True)
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stderr, re.S).group(0))
    second = (f"{base}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-af", second + ",aresample=48000", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    return float(m["input_i"])


if __name__ == "__main__":
    video, out = sys.argv[1], sys.argv[2]
    duration = 4.0
    notes = [440.0, 493.9, 587.3, 659.3, 784.0]                    # one rising note per bar
    events = [(0.0, whoosh(), 0.6, 0.0)]                           # something audible on frame 0
    for i, f in enumerate(notes):                                  # bars start at 0.3 + i*0.25 s (see index.html)
        events.append((0.3 + i * 0.25, pluck(f), 0.5, -0.4 + 0.2 * i))
    events.append((1.5 + 4 * 0.25, kick(), 1.0, 0.0))             # last bar lands: hit
    write_wav("soundtrack.wav", mix(events, duration))
    before = loudnorm_mux(video, "soundtrack.wav", out)
    print(f"measured {before:.1f} LUFS before normalisation -> {out}")
