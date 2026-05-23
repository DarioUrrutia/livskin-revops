"""Transcribe encuentro audio con faster-whisper modelo small + save SRT + TXT + JSON.

Fix v2: stdout UTF-8 + save incremental cada 20 segmentos para no perder progreso si crash.
"""
import sys
import io
# Force UTF-8 stdout to avoid cp1252 crash on rare chars (e.g. CJK false positives)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

from faster_whisper import WhisperModel
import json
import time

AUDIO_PATH = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/raw/audio-encuentro/encuentro-doctora-2026-05-23.m4a"
OUT_DIR = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/discovery-fill"
CHECKPOINT_EVERY = 20  # save every N segments

def fmt_srt_time(s):
    h = int(s // 3600); m = int((s % 3600) // 60); sec = s % 60
    return f"{h:02d}:{m:02d}:{int(sec):02d},{int((sec - int(sec))*1000):03d}"

def save_outputs(segments, info):
    with open(f"{OUT_DIR}/encuentro-transcripcion.txt", "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(seg["text"] + "\n")
    with open(f"{OUT_DIR}/encuentro-transcripcion.srt", "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{fmt_srt_time(seg['start'])} --> {fmt_srt_time(seg['end'])}\n{seg['text']}\n\n")
    with open(f"{OUT_DIR}/encuentro-transcripcion.json", "w", encoding="utf-8") as f:
        json.dump({
            "audio_path": AUDIO_PATH,
            "language": info.language,
            "language_probability": info.language_probability,
            "duration_seconds": info.duration,
            "segments": segments,
            "model": "small",
            "device": "cpu",
            "compute_type": "int8",
            "n_segments": len(segments),
        }, f, ensure_ascii=False, indent=2)

print("[1/3] Loading model small...")
t0 = time.time()
model = WhisperModel("small", device="cpu", compute_type="int8")
print(f"     loaded in {time.time()-t0:.1f}s")

print("[2/3] Transcribing 71min audio...")
t0 = time.time()
segments_iter, info = model.transcribe(
    AUDIO_PATH,
    language="es",
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
    word_timestamps=False,
)
print(f"     language={info.language} prob={info.language_probability:.2f} duration={info.duration:.0f}s")

segments = []
for i, seg in enumerate(segments_iter):
    segments.append({
        "start": seg.start,
        "end": seg.end,
        "text": seg.text.strip(),
    })
    elapsed = time.time() - t0
    pct = (seg.end / info.duration) * 100
    # Print with safe ascii fallback to avoid crashes on rare unicode
    safe_text = seg.text[:80].encode('ascii', errors='replace').decode('ascii')
    try:
        print(f"     [{pct:5.1f}%] {seg.start:7.1f}s -> {seg.end:7.1f}s | elapsed {elapsed/60:.1f}m | {safe_text}")
    except Exception:
        print(f"     [{pct:5.1f}%] [print failed]")

    # Incremental save every N segments
    if (i + 1) % CHECKPOINT_EVERY == 0:
        try:
            save_outputs(segments, info)
        except Exception as e:
            print(f"     [checkpoint save failed: {e}]")

total = time.time() - t0
print(f"\n[3/3] Done. Processed {info.duration/60:.1f}min in {total/60:.1f}min ({info.duration/total:.1f}x realtime)")

save_outputs(segments, info)

print(f"\nOutputs saved:")
print(f"  {OUT_DIR}/encuentro-transcripcion.txt ({sum(len(s['text']) for s in segments)} chars, {len(segments)} segments)")
print(f"  {OUT_DIR}/encuentro-transcripcion.srt")
print(f"  {OUT_DIR}/encuentro-transcripcion.json")
