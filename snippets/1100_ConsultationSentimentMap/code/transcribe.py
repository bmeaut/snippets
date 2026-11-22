"""Gépi átirat 10 perces WAV-darabokból faster-whisper modellel.

Használat:
    python code/transcribe.py <modell_mappa> <darabok_mappa> <kimeneti_mappa>

A darabok (c00.wav, c01.wav, …) 16 kHz-es, mono, 16 bites PCM WAV-fájlok, pl.:
    ffmpeg -i felvetel.mp3 -ar 16000 -ac 1 -f segment -segment_time 600 darabok/c%02d.wav

A kimenet darabonként egy TSV: kezdés (s) <TAB> vége (s) <TAB> szöveg, a teljes
felvételhez viszonyított időbélyegekkel. A már kész darabokat kihagyja, így a
futás megszakítás után folytatható.
"""
import glob
import os
import sys

import numpy as np
from faster_whisper import WhisperModel

CHUNK_S = 600

model_dir, chunk_dir, out_dir = sys.argv[1:4]
os.makedirs(out_dir, exist_ok=True)
# CPU-n, 8 bites kvantálással: a homokozóban nem volt GPU, és a teljes 2 órás
# felvétel egyben nem fért a memóriába, ezért dolgozunk 10 perces darabokkal.
model = WhisperModel(model_dir, device="cpu", compute_type="int8", cpu_threads=2)

for i, path in enumerate(sorted(glob.glob(os.path.join(chunk_dir, "c*.wav")))):
    out = os.path.join(out_dir, os.path.basename(path) + ".tsv")
    if os.path.exists(out):
        continue
    # A WAV-ot közvetlenül olvassuk (44 bájtos fejléc után nyers PCM), mert a
    # faster-whisper beépített (PyAV) dekódolója ebben a környezetben hibát adott.
    audio = np.frombuffer(open(path, "rb").read()[44:], np.int16).astype(np.float32) / 32768
    segs, _ = model.transcribe(audio, language="hu", beam_size=1, vad_filter=True,
                               condition_on_previous_text=False)
    lines = [f"{s.start + CHUNK_S * i:.1f}\t{s.end + CHUNK_S * i:.1f}\t{s.text.strip()}\n" for s in segs]
    with open(out + ".tmp", "w") as f:
        f.writelines(lines)
    os.rename(out + ".tmp", out)
    print("kész:", path, flush=True)
