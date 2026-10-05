# -*- coding: utf-8 -*-
"""uji-mic-level.py — tes cepat mic: daftar mic yang ada, lalu rekam mic default
selama 6 detik dan tampilkan level (RMS) tiap detik.
Kalau RMS ~0.000 padahal Anda bicara → mic yang dipilih salah/hening."""
import sys, time
import numpy as np
import soundcard as sc

print("Daftar semua mic:", flush=True)
mics = sc.all_microphones(include_loopback=False)
for i, m in enumerate(mics):
    tanda = " <-- default" if (m.id == sc.default_microphone().id) else ""
    print(f"  [{i}] {m.name}{tanda}", flush=True)

mic = sc.default_microphone()
print(f"\nRekam mic '{mic.name}' selama 6 detik...")
print("TOLONG BICARA SEKARANG (hitung 1-10), jangan hening!", flush=True)
with mic.recorder(samplerate=16000) as rec:
    for dtk in range(6):
        data = rec.record(numframes=16000)
        if data.ndim == 2:
            data = data.mean(axis=1)
        rms = float(np.sqrt(np.mean(np.asarray(data, dtype=np.float32) ** 2)))
        puncak = float(np.max(np.abs(data)))
        print(f"  detik {dtk+1}: RMS={rms:.5f}  puncak={puncak:.5f}", flush=True)

print("\nKesimpulan: kalau RMS > 0.001 saat bicara → mic ketangkap (masalah di tempat lain).")
print("Kalau ~0.000 → mic salah device / dipaten Windows / perangkat lain yang default.")